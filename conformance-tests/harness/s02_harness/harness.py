"""AQEF Stage C S0.2: stdlib-only, in-memory scripted-services proof of concept.
Not a conformant Engine or a full v0.4 adapter; never sends external tool requests.
"""
from __future__ import annotations
import hashlib, json, re, threading, time, uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SUBJECT_DEFAULT = 'SR-OK'
JUDGE_DEFAULT = 'J-PASS-90'
ENDPOINTS = {'subject': 'cts-scripted-subject@1', 'judge': 'cts-scripted-judge@1'}

def utc(): return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
def digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

@dataclass
class Session:
    sid: str
    lock: threading.RLock = field(default_factory=threading.RLock)
    behaviors: dict = field(default_factory=dict)
    counters: dict = field(default_factory=dict)
    events: list = field(default_factory=list)
    seq: int = 0
    phase: str = 'running'
    closed_at: int | None = None
    watermark: int | None = None

class Harness:
    def __init__(self):
        self.sessions: dict[str,Session] = {}
        self.global_lock=threading.RLock()
        self.clock_id='s02-monotonic-process'
    def begin(self,sid=None):
        sid=sid or uuid.uuid4().hex
        with self.global_lock:
            if sid in self.sessions: raise ValueError('session already exists')
            self.sessions[sid]=Session(sid)
        return sid
    def session(self,sid):
        with self.global_lock:
            if sid not in self.sessions: raise KeyError('unknown session')
            return self.sessions[sid]
    def _emit(self,s,typ,**attrs):
        s.seq+=1
        ev={'event_id':str(uuid.uuid4()),'session_id':s.sid,'sequence':s.seq,'type':typ,
            'clock_id':self.clock_id,'observed_monotonic_ns':time.monotonic_ns(),
            'observed_at':utc(),'attributes':attrs}
        s.events.append(ev)
        return ev
    def configure(self,sid,kind,behavior,applies='next_call',endpoint_id=None):
        if kind not in ('subject','judge'):raise ValueError('unknown kind')
        self._validate(kind,behavior)
        if applies not in ('now','next_call'):raise ValueError('unknown applies')
        s=self.session(sid)
        with s.lock:
            if s.phase!='running':raise ValueError('session closed')
            s.behaviors[(kind, endpoint_id or ENDPOINTS[kind])]=behavior
            self._emit(s,'behavior_configured',kind=kind,behavior=behavior,applies=applies)
    def _validate(self,kind,behavior):
        subj={'SR-OK','SR-EMPTY','SR-ECHO','SR-503-THEN-OK','SR-SLOW-200','SR-BYE','H-REL-035-SUBJECT'}
        judge={'J-PASS-90','J-PASS-60','J-FAIL-90','J-DOWN','J-DOWN-THEN-PASS-90','J-FAIL-THEN-PASS-90','J-CATCH'}
        if kind=='subject' and (behavior in subj or re.fullmatch(r'SR-CALL\(https://cts-(?:stub|trip|outside)\.example/[^)]*\)',behavior)):return
        if kind=='judge' and (behavior in judge or re.fullmatch(r'J-MAP\((J-(?:PASS-90|PASS-60|FAIL-90)), (J-(?:PASS-90|PASS-60|FAIL-90)), (J-(?:PASS-90|PASS-60|FAIL-90))\)',behavior)):return
        raise ValueError('unsupported behavior')
    def invoke(self,sid,kind,payload,endpoint_id=None,phase='action',correlation_id=None):
        s=self.session(sid)
        if kind not in ('subject','judge'):raise ValueError('unknown kind')
        endpoint_id=endpoint_id or ENDPOINTS[kind]
        with s.lock:
            if s.phase not in ('running','closed'):raise ValueError('unknown session phase')
            if s.phase=='closed':
                self._emit(s,'late_call',kind=kind,endpoint_id=endpoint_id,phase=phase,correlation_id=correlation_id)
                raise RuntimeError('late call after observation closure')
            code=s.behaviors.get((kind,endpoint_id),SUBJECT_DEFAULT if kind=='subject' else JUDGE_DEFAULT)
            self._validate(kind,code)
            key=(kind,endpoint_id)
            n=s.counters.get(key,0)+1;s.counters[key]=n
            corr=correlation_id or uuid.uuid4().hex
            self._emit(s,'call_received',kind=kind,endpoint_id=endpoint_id,behavior=code,call_no=n,phase=phase,correlation_id=corr,payload_sha256=digest(payload))
        t0=time.monotonic_ns()
        try:
            result=self._answer(kind,code,payload,n)
        except ConnectionError as e:
            with s.lock:self._emit(s,'call_failed',kind=kind,endpoint_id=endpoint_id,correlation_id=corr,reason=str(e),phase=phase)
            return {'outcome':'unreachable','error':str(e),'call_no':n}
        except RuntimeError as e:
            with s.lock:self._emit(s,'call_failed',kind=kind,endpoint_id=endpoint_id,correlation_id=corr,reason=str(e),phase=phase)
            return {'outcome':'http_error','status':503,'call_no':n}
        with s.lock:self._emit(s,'response_sent',kind=kind,endpoint_id=endpoint_id,correlation_id=corr,phase=phase,elapsed_ns=time.monotonic_ns()-t0,response_sha256=digest(result))
        return {'outcome':'completed','result':result,'call_no':n}
    def _answer(self,kind,code,payload,n):
        if kind=='subject':
            if code=='SR-EMPTY':return ''
            if code=='SR-ECHO':return str(payload.get('prompt',''))
            if code=='SR-BYE':return 'Goodbye.'
            if code=='SR-503-THEN-OK' and n==1:raise RuntimeError('scripted 503')
            if code=='SR-SLOW-200':time.sleep(.2)
            if code=='H-REL-035-SUBJECT':
                if payload.get('scenario')=='s-1' and n==1:raise RuntimeError('scripted 503')
                return str(payload.get('prompt',''))
            if code.startswith('SR-CALL('):return {'tool':'http_get','url':code[8:-1], 'after_tool_response':'Done.','executed':False}
            return 'Hello! How can I help?'
        if code=='J-DOWN' or (code=='J-DOWN-THEN-PASS-90' and n==1):raise ConnectionError('scripted refusal')
        if code=='J-FAIL-THEN-PASS-90':code='J-FAIL-90' if n==1 else 'J-PASS-90'
        if code=='J-DOWN-THEN-PASS-90':code='J-PASS-90'
        if code=='J-CATCH':code='J-FAIL-90' if payload.get('response') in ('Goodbye.','Bye now.') else 'J-PASS-90'
        if code.startswith('J-MAP('):
            vals=re.fullmatch(r'J-MAP\(([^,]+), ([^,]+), ([^)]+)\)',code).groups()
            resp=payload.get('response')
            if resp not in ('One','Two','Three'):raise ValueError('J-MAP requires One/Two/Three')
            code=vals[('One','Two','Three').index(resp)]
        return {'verdict':'fail' if code=='J-FAIL-90' else 'pass','confidence':.60 if code=='J-PASS-60' else .90}
    def read_log(self,sid,after_sequence=0):
        s=self.session(sid)
        with s.lock:return [dict(e) for e in s.events if e['sequence']>after_sequence]
    def reset(self,sid):
        s=self.session(sid)
        with s.lock:
            s.behaviors.clear();s.counters.clear();s.events.clear();s.seq=0;s.phase='running';s.closed_at=None;s.watermark=None
    def close_observation(self,sid,drain_ms=0,terminal_observed=True):
        if not terminal_observed:raise ValueError('SUT terminal state unobserved; cannot close')
        if drain_ms<0:raise ValueError('negative drain')
        s=self.session(sid)
        with s.lock:
            if s.phase!='running':raise ValueError('already closed')
            s.phase='draining'
        time.sleep(drain_ms/1000)
        with s.lock:
            self._emit(s,'observation_watermark',highest_sequence=s.seq)
            s.watermark=s.seq
            self._emit(s,'observation_closed',watermark=s.watermark)
            s.closed_at=time.monotonic_ns();s.phase='closed'
            return {'state':'observation_closed','watermark':s.watermark}
    def negative_assertion(self,sid,kind,expected_count=0):
        s=self.session(sid)
        with s.lock:
            if s.phase!='closed':return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
            calls=[e for e in s.events if e['type']=='call_received' and e['attributes']['kind']==kind and e['sequence']<=s.watermark and e['attributes']['phase']!='setup']
            late=any(e['type']=='late_call' for e in s.events)
            return {'outcome':'FAIL' if late or len(calls)!=expected_count else 'PASS','observed':len(calls),'late':late}
