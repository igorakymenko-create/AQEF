"""S4.0 mock-only CT-HRV-003 contract probe. Not evidence of actual SUT conformance.

No human participates in CI. We exercise and independently inspect the timeout
policy applied to a pending HumanReview Result. The injectable monotonic clock
is for unit fault injection; live_probe tests a real monotonic deadline.
"""
from __future__ import annotations
import copy
import time
import uuid

CAPABILITY = 'human_review'
CASE_ID = 'CT-HRV-003'

class ManualClock:
    def __init__(self, now=0.0): self.current=float(now)
    def __call__(self): return self.current
    def advance(self, seconds):
        if seconds < 0: raise ValueError('clock cannot move backward')
        self.current += seconds

class HumanReviewMock:
    """Deliberately tiny SUT stand-in exposing record and gate readback APIs."""
    def __init__(self, *, clock=time.monotonic, min_timeout_ms=20, mutation=None, claims=True):
        self.clock=clock
        self.min_timeout_ms=min_timeout_ms
        self.mutation=mutation
        self.claims=claims
        self.results={}
        self.events=[]
        self.last_gate=None

    def describe(self): return {'capabilities':[CAPABILITY] if self.claims else []}

    def create(self, *, timeout_ms=None, on_timeout=None):
        if not self.claims: raise ValueError('capability unclaimed')
        if timeout_ms is None: timeout_ms=self.min_timeout_ms
        if type(timeout_ms) is not int or timeout_ms < self.min_timeout_ms:
            raise ValueError('review_timeout below minimum supported')
        if on_timeout is not None and on_timeout not in ('block','escalate'):
            raise ValueError('unsupported on_timeout')
        if on_timeout=='escalate': raise ValueError('escalate requires named role; outside CT-HRV-003')
        xid='execution-'+uuid.uuid4().hex
        rid='result-'+uuid.uuid4().hex
        deadline=self.clock()+timeout_ms/1000
        record={'id':rid,'execution_id':xid,'clause':'expectation-1','oracle_type':'human_reviewer',
                'disposition':'awaiting_review','verdict':None,'confidence':'not_applicable'}
        self.results[xid]={'record':record,'deadline':deadline,'timeout_ms':timeout_ms,
                           'policy':on_timeout or 'block','timed_out':False}
        self.events.append({'event':'review_requested','execution_id':xid,'result_id':rid,
                            'at':self.clock()})
        return xid

    def poll(self, execution_id):
        item=self.results[execution_id]
        if not item['timed_out'] and self.clock() >= item['deadline']:
            item['timed_out']=True
            if self.mutation=='missing_timeout_event': pass
            else:
                self.events.append({'event':'review_timeout','execution_id':execution_id,
                                    'result_id':item['record']['id'],'policy':item['policy'],
                                    'at':self.clock()})
            if self.mutation=='silent_pass':
                item['record'].update({'disposition':'actionable','verdict':'pass'})
            elif self.mutation=='actionable_without_verdict':
                item['record']['disposition']='actionable'
            elif self.mutation=='fabricated_fail':
                item['record'].update({'disposition':'actionable','verdict':'fail'})
            elif self.mutation=='wrong_timeout_policy':
                self.events[-1]['policy']='allow'  # deliberately broken SUT
        return {'timed_out':item['timed_out']}

    def get_results(self, execution_id):
        return {'execution_id':execution_id,'results':[copy.deepcopy(self.results[execution_id]['record'])]}

    def evaluate_gates(self, execution_id):
        record=self.results[execution_id]['record']
        non_actionable=record['disposition']!='actionable'
        failing=record['verdict']=='fail'
        status='fail' if non_actionable or failing else 'pass'
        reasons=(['non_actionable_results'] if non_actionable else []) + (['aggregate_failed'] if failing else [])
        if self.mutation=='force_gate_pass': status='pass';reasons=[]
        if self.mutation=='omit_gate_reason': reasons=[]
        gate={'id':'gate-'+uuid.uuid4().hex,'execution_id':execution_id,'name':'semantic-gate',
              'status':status,'reasons':reasons}
        self.last_gate=gate
        return copy.deepcopy(gate)

    def get_events(self, execution_id):
        return copy.deepcopy([e for e in self.events if e['execution_id']==execution_id])


def observe_timeout(sut, execution_id, *, budget_ms=1000, poll_interval_ms=5,
                    clock=time.monotonic, sleep=time.sleep):
    """Runner-owned waiting budget, independent from contract review_timeout.

    Do not infer timeout from elapsed time alone: require an observable event.
    """
    if type(budget_ms) is not int or budget_ms<=0 or type(poll_interval_ms) is not int or poll_interval_ms<=0:
        return {'outcome':'NOT_RUN','reason':'WAIT_BUDGET_INVALID'}
    start=clock(); deadline=start+budget_ms/1000
    while True:
        try:
            sut.poll(execution_id)
            events=sut.get_events(execution_id)
        except (KeyError,TypeError,ValueError):
            return {'outcome':'NOT_RUN','reason':'TIMEOUT_OBSERVATION_UNAVAILABLE'}
        if any(e.get('event')=='review_timeout' for e in events):
            return {'outcome':'PASS','events':events,'elapsed_ms':(clock()-start)*1000}
        now=clock()
        if now >= deadline:
            return {'outcome':'NOT_RUN','reason':'TIMEOUT_NOT_OBSERVED','elapsed_ms':(now-start)*1000}
        sleep(min(poll_interval_ms/1000,deadline-now))


def assess_ct_hrv_003(*, claimed, pre, observed, results=None, gate=None, events=None, execution_id=None):
    """Independent oracle: rejects false PASS even with a legitimate timeout event.

    No human verdict is injected by this CTS. Strictly distinguishes an
    unavailable observation from a proven incorrect SUT response.
    """
    if not claimed:return {'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_UNCLAIMED'}
    if not isinstance(pre,dict) or pre.get('outcome')!='PASS':
        return {'outcome':'NOT_RUN','reason':'SETUP_OR_PRESTATE_UNAVAILABLE'}
    if pre.get('disposition')!='awaiting_review' or pre.get('verdict') is not None:
        return {'outcome':'FAIL','reason':'PRESTATE_NOT_AWAITING_REVIEW'}
    if observed.get('outcome')!='PASS':
        return {'outcome':'NOT_RUN','reason':observed.get('reason','TIMEOUT_NOT_OBSERVED')}
    if not isinstance(results,dict) or not isinstance(gate,dict) or not isinstance(events,list):
        return {'outcome':'NOT_RUN','reason':'READBACK_UNAVAILABLE'}
    rows=results.get('results')
    if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict):
        return {'outcome':'NOT_RUN','reason':'RESULT_READBACK_INVALID'}
    result=rows[0]
    if (results.get('execution_id')!=execution_id or gate.get('execution_id')!=execution_id or
        result.get('execution_id')!=execution_id or result.get('id')!=pre.get('id')):
        return {'outcome':'FAIL','reason':'ATTRIBUTION_OR_IDENTITY_VIOLATION'}
    timed=[e for e in events if isinstance(e,dict) and e.get('event')=='review_timeout'
           and e.get('execution_id')==execution_id and e.get('result_id')==result.get('id')]
    if len(timed)!=1:
        return {'outcome':'FAIL','reason':'TIMEOUT_EVENT_ATTRIBUTION_INVALID'}
    if timed[0].get('policy')!='block':
        return {'outcome':'FAIL','reason':'ON_TIMEOUT_BLOCK_NOT_APPLIED'}
    if result.get('verdict') is not None or result.get('disposition')=='actionable':
        return {'outcome':'FAIL','reason':'UNREVIEWED_RESULT_BECAME_ACTIONABLE'}
    if result.get('disposition') not in ('awaiting_review','timed_out','blocked','inconclusive'):
        return {'outcome':'FAIL','reason':'INVALID_TIMEOUT_DISPOSITION'}
    if (gate.get('name')!='semantic-gate' or gate.get('status')!='fail' or
        'non_actionable_results' not in gate.get('reasons',[])):
        return {'outcome':'FAIL','reason':'NON_ACTIONABLE_GATE_NOT_BLOCKED'}
    return {'outcome':'PASS','reason':'EXPECTED_MET'}


def run_ct_hrv_003(*, mutation=None, claims=True, budget_ms=1000, timeout_ms=None):
    """Live wall-clock integration, deliberately no review() operation exists."""
    sut=HumanReviewMock(mutation=mutation,claims=claims)
    if CAPABILITY not in sut.describe()['capabilities']:
        return assess_ct_hrv_003(claimed=False,pre={},observed={})
    try:ex=sut.create(timeout_ms=timeout_ms)
    except ValueError:return {'outcome':'NOT_RUN','reason':'FIXTURE_UNAVAILABLE'}
    prior=sut.get_results(ex)['results'][0]
    pre={'outcome':'PASS','id':prior['id'],'disposition':prior['disposition'],'verdict':prior['verdict']}
    obs=observe_timeout(sut,ex,budget_ms=budget_ms)
    if obs['outcome']!='PASS':return assess_ct_hrv_003(claimed=True,pre=pre,observed=obs)
    return assess_ct_hrv_003(claimed=True,pre=pre,observed=obs,execution_id=ex,
                            results=sut.get_results(ex),gate=sut.evaluate_gates(ex),events=sut.get_events(ex))
