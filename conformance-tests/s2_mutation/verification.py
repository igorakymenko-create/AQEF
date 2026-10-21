"""Stage C S2.3 adversarial verification for S2.1/S2.2 mock infrastructure.
This is a harness self-check, not evidence of real SUT conformance.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys, uuid
ROOT=pathlib.Path(__file__).resolve().parent.parent
for p in [ROOT/'s2_assessment',ROOT/'s2_execution',ROOT/'s1_configuration',ROOT/'harness'/'s02_harness']:
    sys.path.insert(0,str(p))
from assessment import assessment_service, assess_case, run_case as run_assessment
from engine import run_case as run_execution, http, binary, digest
from mock import fixture_base
from negative import aggregate
from harness import Harness


def evidence_outcome(req, rsp, evidence):
    """Fail closed on malformed, missing, unowned or modified transport evidence."""
    try:
        if rsp['contract_version']!='0.4' or rsp['correlation_id']!=req['correlation_id'] or rsp['success'] is not True:
            return 'NOT_RUN'
        surf=rsp['data']['sut'];ref=surf['body_ref']
        if rsp['evidence_refs'] != [ref]: return 'NOT_RUN'
        record=evidence[ref]
        if not isinstance(record,tuple) or len(record)!=3:return 'NOT_RUN'
        run,case,raw=record
        if (run,case)!=(req['run_id'],req['case_id']) or not isinstance(raw,bytes):return 'NOT_RUN'
        if hashlib.sha256(raw).hexdigest()!=surf['body_sha256']:return 'NOT_RUN'
        return 'PASS' if json.loads(raw).get('terminal')=='completed' else 'NOT_RUN'
    except (KeyError,TypeError,ValueError,UnicodeDecodeError,AttributeError):
        return 'NOT_RUN'


def scenario(case, mutation=None):
    if case in ('CT-EXE-003','CT-EXE-008'):
        return run_execution(case,mutation)
    if case in ('CT-ASM-001','CT-ASM-014'):
        return run_assessment(case,mutation)
    raise ValueError('unknown case')


def matrix():
    good={k:scenario(k) for k in ('CT-EXE-003','CT-EXE-008','CT-ASM-001','CT-ASM-014')}
    broken={
        'record_failed_attempt':scenario('CT-EXE-003','failed_attempt_record'),
        'change_conversation':scenario('CT-EXE-008','alter_response'),
        'judge_after_failed_validator':scenario('CT-ASM-001','judge_on_failed_validation'),
        'crash_misclassified':scenario('CT-ASM-014','crash_as_fail'),
    }
    return {'scope':'S2.3_MOCK_ONLY','good':good,'broken':broken,
            'good_aggregate':aggregate([v['outcome'] for v in good.values()]),
            'broken_aggregate':aggregate([v['outcome'] for v in broken.values()])}


def closed_absence(*, late=False, terminal=True, drain_ms=0):
    """Actual S0 harness watermark semantics; drain=0 only for fast unit tests."""
    h=Harness();sid=h.begin('s23-'+uuid.uuid4().hex)
    if not terminal:
        return h.negative_assertion(sid,'judge',0)
    h.close_observation(sid,drain_ms=drain_ms,terminal_observed=True)
    if late:
        try:h.invoke(sid,'judge',{'response':'Hello'},correlation_id='late')
        except RuntimeError:pass
    return h.negative_assertion(sid,'judge',0)


def assessment_probe(*, mutation=None, terminal_observed=True, damage=None):
    """Real S2.2 HTTP adapter, one session, independent read of its evidence and call log."""
    case='CT-ASM-001'
    with assessment_service(mutation) as (mock,server):
        sid='s23-'+uuid.uuid4().hex
        cfg=fixture_base();mock.prepare_assessment(sid,cfg,'SR-EMPTY','schema')
        req={'contract_version':'0.4','operation':'execute','run_id':'run-'+uuid.uuid4().hex,
             'case_id':case,'session_id':sid,'correlation_id':'corr-'+uuid.uuid4().hex,
             'timeout_ms':10000,'arguments':{'project_id':'project-'+uuid.uuid4().hex,
                'suite':'cts-suite','environment':'cts-env'}}
        status,rsp=http('POST',server.url+'/api/v0.4/operations',req)
        if status!=200 or not rsp.get('success'):return {'outcome':'NOT_RUN','reason':'ADAPTER_FAILURE'}
        ref=rsp['data']['sut']['body_ref']
        if damage=='bytes':
            run,owner,raw=server.evidence[ref];server.evidence[ref]=(run,owner,raw+b'!')
        if damage=='wrong_owner':
            run,owner,raw=server.evidence[ref];server.evidence[ref]=(run,'other-case',raw)
        if damage=='missing':server.evidence.pop(ref)
        if damage=='wrong_correlation':rsp['correlation_id']='other-correlation'
        if evidence_outcome(req,rsp,server.evidence)!='PASS':
            return {'outcome':'NOT_RUN','reason':'EVIDENCE_UNTRUSTWORTHY'}
        if not terminal_observed:
            return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
        mock.h.close_observation(sid,drain_ms=0,terminal_observed=True)
        obs=mock.h.negative_assertion(sid,'judge',0)
        events=mock.h.read_log(sid)
        rows=mock.saved[sid]['executions']
        if len(rows)!=1:return {'outcome':'FAIL','reason':'EXECUTION_COUNT_INVALID'}
        return assess_case(case,rows[0],events,obs)
