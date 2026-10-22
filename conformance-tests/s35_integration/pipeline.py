"""S3.5.0 single-session unified *mock* pipeline: Execution -> Assessment -> Decision.
Uses existing S2.1 HTTP transport and S0 scripted harness; no real SUT conformance claim.
"""
from __future__ import annotations
import copy, json, pathlib, sys, threading, uuid
from contextlib import contextmanager
ROOT=pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT/'s2_execution',ROOT/'s3_decision',ROOT/'s1_configuration'):
    sys.path.insert(0,str(p))
from engine import Mock, Server, http, digest, validator
from mock import fixture_base

class MockValidator:
    def __init__(self):self.calls=[]
    def check(self,response,mode):
        self.calls.append((mode,response))
        if mode=='cts-crash':raise RuntimeError('injected validator failure')
        ok=isinstance(response,str) and bool(response)
        return {'oracle_type':'validator','disposition':'actionable',
                'verdict':'pass' if ok else 'fail','confidence':'not_applicable'}

class UnifiedMock(Mock):
    def __init__(self,mutation=None):
        super().__init__(mutation);self.modes={};self.judges={};self.validator=MockValidator()
    def prepare_pipeline(self,sid,config,subject='SR-OK',judge='J-PASS-90',mode='schema'):
        self.prepare(sid,config,subject);self.modes[sid]=mode;self.judges[sid]=judge
    def emit(self,sid,kind,**attrs):
        s=self.h.session(sid)
        with s.lock:self.h._emit(s,kind,**attrs)
    def execute(self,sid,case):
        config,behavior=self.fixtures[sid]
        self.h.begin(sid)
        self.h.configure(sid,'subject',behavior)
        self.h.configure(sid,'judge',self.judges[sid])
        prompt=config['project']['suites'][0]['scenarios'][0]['variables']['query']
        retry=config['project'].get('execution',{}).get('retry',{})
        limit=2 if retry.get('on')=='infrastructure_failure' and retry.get('max_attempts',0)>=2 else 1
        attempts=[]
        for _ in range(limit):
            a=self.h.invoke(sid,'subject',{'prompt':prompt},correlation_id=case)
            attempts.append(a)
            if a['outcome']=='completed' or a['outcome'] not in ('http_error','unreachable'):break
        executions=[]
        if attempts[-1]['outcome']=='completed':
            response=attempts[-1]['result']
            conversation={'messages':[{'role':'user','content':prompt},{'role':'assistant','content':response}]}
            if self.mutation=='alter_conversation':conversation['messages'][1]['content']='tampered'
            xid='execution-'+uuid.uuid4().hex
            self.emit(sid,'validator_started',execution_id=xid)
            try:vr=self.validator.check(response,self.modes[sid])
            except Exception:
                vr={'oracle_type':'validator','disposition':'oracle_unavailable',
                    'verdict':None,'confidence':'not_applicable'}
            if self.mutation=='crash_as_fail' and self.modes[sid]=='cts-crash':
                vr['disposition']='actionable';vr['verdict']='fail'
            self.emit(sid,'validator_finished',execution_id=xid,disposition=vr['disposition'])
            results=[{'id':'result-'+uuid.uuid4().hex,'execution_id':xid,'clause':'schema',**vr}]
            should_judge=vr['disposition']=='actionable' and vr['verdict']=='pass'
            if self.mutation=='judge_after_validation_failure':should_judge=True
            if should_judge:
                judge=self.h.invoke(sid,'judge',{'response':response},correlation_id=case)
                if judge['outcome']=='completed':
                    j=judge['result'];dis='actionable' if j['confidence']>=.8 else 'inconclusive'
                    results.append({'id':'result-'+uuid.uuid4().hex,'execution_id':xid,
                       'clause':'expectation-1','oracle_type':'judge','disposition':dis,
                       'verdict':j['verdict'],'confidence':j['confidence']})
                else:results.append({'id':'result-'+uuid.uuid4().hex,'execution_id':xid,
                    'clause':'expectation-1','oracle_type':'judge','disposition':'oracle_unavailable',
                    'verdict':None,'confidence':'not_applicable'})
            blocked=any(r['disposition']!='actionable' or r['verdict']!='pass' for r in results)
            reasons=[]
            if any(r['disposition']!='actionable' for r in results):reasons.append('non_actionable_results')
            if any(r['disposition']=='actionable' and r['verdict']=='fail' for r in results):reasons.append('aggregate_failed')
            if self.mutation=='allow_bad_gate':blocked=False;reasons=[]
            gate={'id':'gate-'+uuid.uuid4().hex,'execution_id':xid,
                  'status':'fail' if blocked else 'pass','reasons':reasons,
                  'basis':{'results':sum(r['disposition']=='actionable' for r in results),
                           'not_actionable':sum(r['disposition']!='actionable' for r in results)}}
            executions=[{'id':xid,'conversation':conversation,'results':results,'gate':gate}]
            if self.mutation=='record_failed_attempt' and len(attempts)>1:
                executions.insert(0,{'id':'failed-attempt','conversation':None,'results':[],'gate':None})
        self.saved[sid]={'executions':executions,'attempts':attempts,'validator_calls':len(self.validator.calls)}
        return {'terminal':'completed','execution_ids':[e['id'] for e in executions]}

@contextmanager
def service(mutation=None):
    mock=UnifiedMock(mutation);server=Server(mock)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield mock,server
    finally:server.shutdown();server.server_close();thread.join(timeout=2)

# Adapter Contract 0.4 requires a *normative* CTS case ID, not a custom S3.5 profile name.
# Profile remains separate in the execution fixture and diagnostic output.
CASE_IDS={
    'retry':'CT-EXE-003',
    'healthy':'CT-EXE-008',
    'validation_fail':'CT-ASM-001',
    'validator_crash':'CT-ASM-014',
    'inconclusive':'CT-DEC-006',
    'judge_fail':'CT-REL-006',
}

PROFILES={
    'retry':('SR-503-THEN-OK','J-PASS-90','schema'),
    'healthy':('SR-OK','J-PASS-90','schema'),
    'validation_fail':('SR-EMPTY','J-PASS-90','schema'),
    'validator_crash':('SR-OK','J-PASS-90','cts-crash'),
    'inconclusive':('SR-OK','J-PASS-60','schema'),
    'judge_fail':('SR-OK','J-FAIL-90','schema'),
}

def evaluate_independently(profile,config,records,events,validator_calls,observation):
    """CTS evaluator reads observed records/log and doesn't trust a mock-supplied verdict."""
    if observation['outcome']=='NOT_RUN':return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
    if observation['outcome']=='FAIL':return {'outcome':'FAIL','reason':'LATE_CALL'}
    subject=[e for e in events if e['type']=='call_received' and e['attributes'].get('kind')=='subject']
    judges=[e for e in events if e['type']=='call_received' and e['attributes'].get('kind')=='judge']
    finish=[e for e in events if e['type']=='validator_finished']
    if len(records)!=1:return {'outcome':'FAIL','reason':'EXECUTION_COUNT_INVALID'}
    ex=records[0];results=ex.get('results');gate=ex.get('gate');conv=ex.get('conversation')
    if not isinstance(results,list) or not isinstance(gate,dict) or not isinstance(conv,dict):
        return {'outcome':'FAIL','reason':'MISSING_EXECUTION_DATA'}
    messages=conv.get('messages')
    if not isinstance(messages,list) or len(messages)!=2:return {'outcome':'FAIL','reason':'CONVERSATION_INVALID'}
    if messages[0]!={'role':'user','content':'Hello'}:return {'outcome':'FAIL','reason':'PROMPT_CHANGED'}
    expected_response='' if profile=='validation_fail' else 'Hello! How can I help?'
    if messages[1]!={'role':'assistant','content':expected_response}:return {'outcome':'FAIL','reason':'RESPONSE_CHANGED'}
    expected_subject=2 if profile=='retry' else 1
    if len(subject)!=expected_subject:return {'outcome':'FAIL','reason':'SUBJECT_CALL_COUNT'}
    if len(finish)!=1 or validator_calls!=1:return {'outcome':'FAIL','reason':'VALIDATOR_COUNT'}
    if any(r.get('execution_id')!=ex['id'] for r in results) or gate.get('execution_id')!=ex['id']:
        return {'outcome':'FAIL','reason':'CROSS_EXECUTION_RECORDS'}
    vr=[r for r in results if r.get('oracle_type')=='validator']
    jr=[r for r in results if r.get('oracle_type')=='judge']
    if len(vr)!=1:return {'outcome':'FAIL','reason':'VALIDATOR_RESULT_MISSING'}
    v=vr[0]
    expected_v= ('oracle_unavailable',None) if profile=='validator_crash' else ('actionable','fail' if profile=='validation_fail' else 'pass')
    if (v.get('disposition'),v.get('verdict'))!=expected_v:return {'outcome':'FAIL','reason':'VALIDATOR_INCORRECT'}
    judge_expected=0 if profile in ('validator_crash','validation_fail') else 1
    if len(judges)!=judge_expected or len(jr)!=judge_expected:
        return {'outcome':'FAIL','reason':'JUDGE_COUNT'}
    if judges and (judges[0]['sequence']<=finish[0]['sequence']):return {'outcome':'FAIL','reason':'ORDERING'}
    if jr:
        expected_j='inconclusive' if profile=='inconclusive' else 'actionable'
        expected_verdict='fail' if profile=='judge_fail' else 'pass'
        if (jr[0].get('disposition'),jr[0].get('verdict'))!=(expected_j,expected_verdict):
            return {'outcome':'FAIL','reason':'JUDGE_RESULT_INVALID'}
    fail=profile in ('validator_crash','validation_fail','inconclusive','judge_fail')
    expected_reasons={'validator_crash':['non_actionable_results'],
                      'validation_fail':['aggregate_failed'],
                      'inconclusive':['non_actionable_results'],
                      'judge_fail':['aggregate_failed']}.get(profile,[])
    basis={'results':sum(r['disposition']=='actionable' for r in results),
           'not_actionable':sum(r['disposition']!='actionable' for r in results)}
    if (gate.get('status'),gate.get('reasons'),gate.get('basis')) != ('fail' if fail else 'pass',expected_reasons,basis):
        return {'outcome':'FAIL','reason':'GATE_INCORRECT'}
    return {'outcome':'PASS','reason':'EXPECTED_MET','subject_calls':len(subject),
            'judge_calls':len(judges),'execution_id':ex['id'],'result_count':len(results),
            'gate_status':gate['status']}

def build_request(profile,sid=None):
    if profile not in PROFILES:raise ValueError('unknown profile')
    return {'contract_version':'0.4','operation':'execute','run_id':'run-'+uuid.uuid4().hex,
            'case_id':CASE_IDS[profile],'session_id':sid or 's350-'+uuid.uuid4().hex,
            'correlation_id':'corr-'+uuid.uuid4().hex,'timeout_ms':10000,
            'arguments':{'project_id':'s350-'+uuid.uuid4().hex,
                         'suite':'cts-suite','environment':'cts-env'}}

def run_case(profile,mutation=None,*,damage=False,terminal_observed=True):
    if profile not in PROFILES:raise ValueError('unknown profile')
    subject,judge,mode=PROFILES[profile]
    with service(mutation) as (mock,server):
        cfg=fixture_base()
        if profile=='retry':cfg['project']['execution']={'retry':{'max_attempts':2,'on':'infrastructure_failure'}}
        sid='s350-'+uuid.uuid4().hex;mock.prepare_pipeline(sid,cfg,subject,judge,mode)
        req=build_request(profile,sid)
        if validator.schema_errors('adapter-operation.schema.json',req):return {'outcome':'NOT_RUN','reason':'REQUEST_INVALID'}
        try:status,rsp=http('POST',server.url+'/api/v0.4/operations',req)
        except (OSError,ValueError):return {'outcome':'NOT_RUN','reason':'TRANSPORT_FAILED'}
        if status!=200 or validator.schema_errors('adapter-response.schema.json',rsp) or rsp.get('success') is not True:
            return {'outcome':'NOT_RUN','reason':'ADAPTER_INVALID'}
        info=rsp['data']['sut'];ref=info['body_ref']
        if damage:
            run,owner,raw=server.evidence[ref];server.evidence[ref]=(run,owner,raw+b'!')
        try:
            run,owner,raw=server.evidence[ref]
            if (run,owner)!=(req['run_id'],req['case_id']) or digest(raw)!=info['body_sha256'] or rsp['evidence_refs']!=[ref]:
                return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'}
            receipt=json.loads(raw)
            if receipt['terminal']!='completed':return {'outcome':'NOT_RUN','reason':'TERMINAL_UNOBSERVED'}
            if receipt['execution_ids']!=[e['id'] for e in mock.saved[sid]['executions']]:
                return {'outcome':'FAIL','reason':'EXECUTION_REFERENCE_MISMATCH'}
        except (KeyError,ValueError,TypeError):return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'}
        if not terminal_observed:return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
        # Q-05: observed terminal state with measured, positive drain.
        sys.path.insert(0,str(ROOT/'s355_closure'))
        from observation import observe_closed
        obs=observe_closed(mock.h,sid,'subject',expected_count=2 if profile=='retry' else 1)
        if obs['outcome']=='NOT_RUN':return obs
        return evaluate_independently(profile,cfg,mock.saved[sid]['executions'],mock.h.read_log(sid),
                                      mock.saved[sid]['validator_calls'],obs)
