"""S2.2 mock-only assessment proof. Reuses S2.1 HTTP adapter and S0 scripted Harness.
No production AQEF implementation or full CTS conformance is asserted.
"""
from __future__ import annotations
import copy, json, pathlib, sys, threading, uuid
from contextlib import contextmanager
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'s2_execution'))
from engine import Mock, Server, http, digest, binary, validator

CASES=('CT-ASM-001','CT-ASM-014')

class AssessmentMock(Mock):
    def __init__(self,mutation=None):
        super().__init__(mutation)
        self.modes={}

    def prepare_assessment(self,sid,config,subject_behavior,validator_mode='schema'):
        self.prepare(sid,config,subject_behavior)
        self.modes[sid]=validator_mode

    def event(self,sid,kind,**attrs):
        s=self.h.session(sid)
        with s.lock:self.h._emit(s,kind,**attrs)

    def execute(self,sid,case):
        config,behavior=self.fixtures[sid]
        self.h.begin(sid)
        self.h.configure(sid,'subject',behavior)
        self.h.configure(sid,'judge','J-PASS-90')
        prompt=config['project']['suites'][0]['scenarios'][0]['variables']['query']
        subject=self.h.invoke(sid,'subject',{'prompt':prompt},correlation_id=case)
        if subject['outcome']!='completed':
            self.saved[sid]={'executions':[],'subject':subject}
            return {'terminal':'completed','execution_ids':[]}
        response=subject['result']
        conversation={'messages':[{'role':'user','content':prompt},{'role':'assistant','content':response}]}
        mode=self.modes[sid]
        self.event(sid,'validator_started',validator=mode)
        if mode=='cts-crash':
            vr={'oracle_type':'validator','disposition':'oracle_unavailable','verdict':None,'confidence':'not_applicable'}
        else:
            passed=isinstance(response,str) and len(response)>0
            vr={'oracle_type':'validator','disposition':'actionable','verdict':'pass' if passed else 'fail','confidence':'not_applicable'}
        if self.mutation=='crash_as_fail' and mode=='cts-crash':
            vr['disposition']='actionable';vr['verdict']='fail'
        if self.mutation=='crash_no_result' and mode=='cts-crash':vr=None
        if self.mutation=='empty_as_pass' and mode=='schema':vr['verdict']='pass'
        self.event(sid,'validator_finished',validator=mode,disposition=vr['disposition'] if vr else None)
        results=[vr] if vr is not None else []
        should_judge=bool(vr and vr['disposition']=='actionable' and vr['verdict']=='pass')
        if self.mutation=='judge_on_failed_validation' and mode=='schema':should_judge=True
        if self.mutation=='judge_on_unavailable' and mode=='cts-crash':should_judge=True
        if self.mutation=='judge_before_validator':
            # Synthetic ordering violation, the judge is invoked before the completion event.
            s=self.h.session(sid)
            with s.lock:
                finish=next(e for e in s.events if e['type']=='validator_finished')
                s.events.remove(finish)
            self.h.invoke(sid,'judge',{'response':response},correlation_id=case)
            with s.lock:
                self.h._emit(s,'validator_finished',validator=mode,disposition=vr['disposition'] if vr else None)
            should_judge=False
        if should_judge:
            judge=self.h.invoke(sid,'judge',{'response':response},correlation_id=case)
            if judge['outcome']=='completed':
                results.append({'oracle_type':'judge','disposition':'actionable',**judge['result']})
        execution={'id':'execution-'+uuid.uuid4().hex,'conversation':conversation,'results':results}
        self.saved[sid]={'executions':[execution]}
        return {'terminal':'completed','execution_ids':[execution['id']]}

@contextmanager
def assessment_service(mutation=None):
    mock=AssessmentMock(mutation)
    server=Server(mock)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:yield mock,server
    finally:server.shutdown();server.server_close();thread.join(timeout=2)


def assess_case(case,execution,events,negative_assertion):
    """Independent CTS evaluator, never trusts a SUT-supplied 'PASS'."""
    if not isinstance(execution,dict) or not isinstance(execution.get('results'),list):
        return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
    results=execution['results']
    validators=[r for r in results if isinstance(r,dict) and r.get('oracle_type')=='validator']
    judge_events=[e for e in events if e['type']=='call_received' and e['attributes'].get('kind')=='judge']
    if negative_assertion['outcome']=='NOT_RUN':
        return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
    if negative_assertion['outcome']=='FAIL':
        return {'outcome':'FAIL','reason':'EXPECTED_VIOLATED','judge_calls':len(judge_events)}
    if len(validators)!=1:
        return {'outcome':'FAIL','reason':'VALIDATOR_RESULT_MISSING','judge_calls':len(judge_events)}
    result=validators[0]
    if case=='CT-ASM-001':
        expected={'oracle_type':'validator','disposition':'actionable','verdict':'fail'}
    elif case=='CT-ASM-014':
        expected={'oracle_type':'validator','disposition':'oracle_unavailable','verdict':None,'confidence':'not_applicable'}
    else:raise ValueError('unknown CTS case')
    ok=all(result.get(k)==v for k,v in expected.items()) and not judge_events
    return {'outcome':'PASS' if ok else 'FAIL','reason':'EXPECTED_MET' if ok else 'EXPECTED_VIOLATED',
            'judge_calls':len(judge_events),'validator_result':result}


def run_case(case,mutation=None,*,fixture_available=True,tamper_evidence=False,terminal_observed=True):
    if case not in CASES:raise ValueError('unsupported CTS case')
    if not fixture_available:
        return {'outcome':'NOT_RUN','reason':'FIXTURE_UNAVAILABLE'}
    from engine import validator as validate
    sys.path.insert(0,str(ROOT/'s1_configuration'))
    from mock import fixture_base
    with assessment_service(mutation) as (mock,server):
        config=fixture_base()
        mode='cts-crash' if case=='CT-ASM-014' else 'schema'
        behavior='SR-OK' if mode=='cts-crash' else 'SR-EMPTY'
        if mode=='cts-crash':
            config['project']['suites'][0]['scenarios'][0]['contract']['constraints'].append(
                {'validator':'cts-crash','target':'response','expected':{}})
        sid='s22-'+uuid.uuid4().hex
        mock.prepare_assessment(sid,config,behavior,mode)
        req={'contract_version':'0.4','operation':'execute','run_id':'s22-'+uuid.uuid4().hex,
             'case_id':case,'session_id':sid,'correlation_id':'corr-'+uuid.uuid4().hex,
             'timeout_ms':10000,'arguments':{'project_id':'cts-assessment-'+uuid.uuid4().hex,
                                              'suite':'cts-suite','environment':'cts-env'}}
        if validate.schema_errors('adapter-operation.schema.json',req):
            return {'outcome':'NOT_RUN','reason':'ADAPTER_REQUEST_INVALID'}
        try:status,rsp=http('POST',server.url+'/api/v0.4/operations',req)
        except (OSError,ValueError):return {'outcome':'NOT_RUN','reason':'TRANSPORT_FAILED'}
        if status!=200 or validate.schema_errors('adapter-response.schema.json',rsp) or rsp.get('success') is not True:
            return {'outcome':'NOT_RUN','reason':'ADAPTER_CONTRACT_INVALID'}
        ref=rsp['data']['sut']['body_ref']
        if tamper_evidence:
            run,owner,raw=server.evidence[ref];server.evidence[ref]=(run,owner,raw+b'!')
        try:
            run,owner,raw=server.evidence[ref]
            if run!=req['run_id'] or owner!=case or digest(raw)!=rsp['data']['sut']['body_sha256']:
                return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'}
            if json.loads(raw).get('terminal')!='completed':
                return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
        except (ValueError,KeyError,TypeError):
            return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'}
        if not terminal_observed:
            return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
        # drain=0 is a deliberately FAST MOCK-SPECIFIC unit setting, NOT Q-05 closure readiness.
        # Negative assertions still require a closed observation with a watermark.
        mock.h.close_observation(sid,drain_ms=0,terminal_observed=True)
        no_judge=mock.h.negative_assertion(sid,'judge',expected_count=0)
        events=mock.h.read_log(sid)
        executions=mock.saved.get(sid,{}).get('executions',[])
        if len(executions)!=1:
            return {'outcome':'FAIL','reason':'EXECUTION_COUNT_INVALID'}
        return assess_case(case,executions[0],events,no_judge)
