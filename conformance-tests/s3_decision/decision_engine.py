"""S3.1 mock-only Decision Engine; not a production AQEF SUT or Appendix C adapter.
Mutations live solely in MockDecision; independent CTS assertions in foundation.py.
"""
from __future__ import annotations
import copy, pathlib, sys, uuid
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'harness'/'s02_harness'))
from harness import Harness
from foundation import evaluate, evaluate_fixture, summarize

class MockDecision:
    def __init__(self, mutation=None):
        self.mutation=mutation; self.results=[];self.gates=[];self.events=[]
        self.h=Harness();self.sid=self.h.begin('s31-'+uuid.uuid4().hex)
        self.evaluation_count=0;self.approvals={};self.release_decisions=[]

    def execute(self,judge_behavior):
        self.h.configure(self.sid,'subject','SR-OK')
        self.h.configure(self.sid,'judge',judge_behavior)
        s=self.h.invoke(self.sid,'subject',{'prompt':'Hello'},correlation_id='execute')
        if s['outcome']!='completed':raise RuntimeError('subject setup failed')
        j=self.h.invoke(self.sid,'judge',{'response':s['result']},correlation_id='evaluate')
        if j['outcome']!='completed':raise RuntimeError('judge setup failed')
        confidence=j['result']['confidence']
        disposition='actionable' if confidence>=.8 else 'inconclusive'
        result={'id':'result-'+uuid.uuid4().hex,'execution':'s-greeting', 'clause':'expectation-1',
                'oracle_type':'judge','disposition':disposition,'verdict':j['result']['verdict'],
                'confidence':confidence}
        self.results.append(result);self.events.append('execute');return copy.deepcopy(result)

    def effective(self):
        return copy.deepcopy(self.results[-1])

    def evaluate_gates(self):
        self.evaluation_count+=1
        effective=self.effective();non=effective['disposition']!='actionable'
        fail=non or effective['verdict']=='fail'
        reasons=['non_actionable_results'] if non else (['aggregate_failed'] if fail else [])
        if self.mutation=='gate_pass_nonactionable' and non:fail=False;reasons=[]
        if self.mutation=='omit_nonactionable_reason' and non:reasons=[]
        basis={'results':int(not non),'not_actionable':int(non)}
        if self.mutation=='count_nonactionable_as_result' and non:basis={'results':1,'not_actionable':0}
        value='not_computed' if non else (1.0 if not fail else 0.0)
        if self.mutation=='null_gate_value' and non:value=None
        g={'id':self.gates[0]['id'] if self.gates else 'gate-'+uuid.uuid4().hex,'evaluation_id':'evaluation-'+str(self.evaluation_count),
           'status':'fail' if fail else 'pass','reasons':reasons,'basis':basis,'value':value}
        self.gates=[g];self.events.append('evaluate_gates');return copy.deepcopy(g)

    def review(self,principal,target_id,verdict):
        current=self.results[-1]
        allowed=(principal=='P-REVIEWER' and current['id']==target_id and current['disposition']!='actionable')
        if self.mutation=='allow_repeat_review' and target_id==self.results[0]['id']:allowed=True
        if self.mutation=='allow_actionable_review' and current['disposition']=='actionable':allowed=True
        if self.mutation=='allow_unprivileged_review' and principal=='P-NOPERM':allowed=True
        if self.mutation=='reject_all_review':allowed=False
        if not allowed:
            self.events.append('review_rejected');return {'accepted':False,'code':'INVALID_RESOLUTION'}
        row={'id':'review-'+uuid.uuid4().hex,'execution':current['execution'],'clause':current['clause'],
             'oracle_type':'human_reviewer','disposition':'actionable','verdict':verdict,
             'resolves':target_id}
        self.results.append(row);self.events.append('review_accepted');return {'accepted':True,'result':copy.deepcopy(row)}

    def release(self,decision='overridden'):
        gate=self.gates[0]
        accepted=decision=='overridden' and gate['status']=='fail' and bool(gate.get('override'))
        if self.mutation=='release_without_override':accepted=True
        if self.mutation=='reject_after_override' and gate.get('override'):accepted=False
        self.events.append('release_attempt')
        if accepted:self.release_decisions.append({'decision':decision,'gate_id':gate['id']})
        return {'accepted':accepted}

    def override(self,person='P-APPROVER',justification='documented exception'):
        gate=self.gates[0]
        if gate['status']!='fail':return {'accepted':False}
        data={'record_id':'approval-'+uuid.uuid4().hex,'approved_by':person,'justification':justification}
        if self.mutation=='omit_approver':data['approved_by']=''
        if self.mutation=='omit_justification':data['justification']=''
        gate['override']=data
        if self.mutation=='override_as_pass':gate['status']='pass'
        if self.mutation=='re_evaluate_on_override':gate['evaluation_id']='evaluation-changed'
        self.events.append('override_approved');return {'accepted':True,'approval':copy.deepcopy(data)}


def run_dec006(mutation=None):
    mock=MockDecision(mutation);mock.execute('J-PASS-60');gate=mock.evaluate_gates()
    return evaluate('CT-DEC-006',{'gate':gate})


def run_dec012_variant(variant,mutation=None):
    if variant not in 'abcd' or len(variant)!=1:raise ValueError('variant must be a/b/c/d')
    mock=MockDecision(mutation)
    initial=mock.execute('J-PASS-90' if variant=='c' else 'J-PASS-60')
    if variant in ('a','b'):
        setup=mock.review('P-REVIEWER',initial['id'],'pass')
        if not setup['accepted']:return {'outcome':'NOT_RUN','reason':'SETUP_FAILED'}
        setup_obs={'review_result':setup['result'],'judge_result':initial,'effective_result':mock.effective()}
        check=evaluate_fixture('F-REVIEWED',setup_obs)
        if check['outcome']!='PASS':return {'outcome':'NOT_RUN','reason':'FIXTURE_CHECK_FAILED','fixture':check}
    mock.evaluate_gates()
    before={'results':copy.deepcopy(mock.results),'effective_result':mock.effective(),'gates':copy.deepcopy(mock.gates)}
    target=initial['id'] if variant in ('a','c','d') else mock.results[-1]['id']
    result=mock.review('P-NOPERM' if variant=='d' else 'P-REVIEWER',target,'fail')
    if mock.mutation=='mutate_rejected_results' and not result['accepted']:
        mock.results[0]['verdict']='fail'
    if mock.mutation=='mutate_rejected_gate' and not result['accepted']:
        mock.gates[0]['reasons']=['changed']
    # A second gate evaluation is required by the CTS; its ID may change, status/reasons must not.
    after_gate=mock.evaluate_gates()
    if mock.mutation=='mutate_rejected_gate' and not result['accepted']:
        after_gate['reasons']=['changed']
    after={'review_attempt':{'accepted':result['accepted']},'results':copy.deepcopy(mock.results),
           'effective_result':mock.effective(),'gates':[after_gate]}
    return evaluate('CT-DEC-012',{'before':before,'after':after},variant=variant)


def run_dec012(mutation=None,*,claimed_capabilities=('human_review',)):
    if 'human_review' not in claimed_capabilities:
        return {'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_NOT_CLAIMED'}
    variants={v:run_dec012_variant(v,mutation) for v in 'abcd'}
    return {'outcome':summarize(variants),'variants':variants}


def run_rel006(mutation=None):
    mock=MockDecision(mutation);mock.execute('J-FAIL-90');gate=mock.evaluate_gates()
    first=mock.release();prior={'release_attempt':first,'gate':copy.deepcopy(gate)}
    mock.override()
    second=mock.release()
    current=copy.deepcopy(mock.gates[0])
    return evaluate('CT-REL-006',{'before':prior,'after':{'release_attempt':second,'gate':current}})


def matrix():
    good={'CT-DEC-006':run_dec006(),'CT-DEC-012':run_dec012(),'CT-REL-006':run_rel006()}
    mutants={'nonactionable_pass':run_dec006('gate_pass_nonactionable'),
             'duplicate_review':run_dec012_variant('a','allow_repeat_review'),
             'unprivileged_review':run_dec012_variant('d','allow_unprivileged_review'),
             'release_without_override':run_rel006('release_without_override'),
             'override_as_pass':run_rel006('override_as_pass')}
    return {'scope':'S3.1_MOCK_ONLY','good':good,'mutants':mutants}
