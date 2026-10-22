"""S3.5.1 unified-mock governance extension; not real SUT conformance.
Post-execution Result resolution is per (execution_id, clause).
Approval records are bound to a single, specific GateResult.
S3.5.4 will introduce HTTP retrieval and governance operation adapter surfaces.
"""
from __future__ import annotations
import copy, pathlib, sys, uuid
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'s35_integration'))
from pipeline import UnifiedMock
PERMISSIONS={'P-REVIEWER':{'review'}, 'P-APPROVER':{'approve_override'},
             'P-RELEASE':{'release'},'P-NOPERM':set()}

class GovernedPipeline(UnifiedMock):
    def __init__(self, mutation=None):
        super().__init__(mutation)
        self.resolutions={}
        self.approvals={}
        self.releases=[]
        self.audit=[]

    def execute(self,sid,case):
        receipt=super().execute(sid,case)
        for ex in self.saved[sid]['executions']:
            if not isinstance(ex.get('results'),list):continue
            for result in ex['results']:
                key=(ex['id'],result['clause'])
                self.resolutions.setdefault(key,[])
                self.resolutions[key].append(copy.deepcopy(result))
        return receipt

    def _records(self,execution_id,clause):
        key=(execution_id,clause)
        if key not in self.resolutions:raise KeyError('unknown execution/clause')
        return self.resolutions[key]

    def effective(self,execution_id,clause):
        records=self._records(execution_id,clause)
        by_id={r['id']:r for r in records}
        if len(by_id)!=len(records):raise ValueError('duplicate result IDs')
        targets={r['resolves'] for r in records if 'resolves' in r}
        heads=[r for r in records if r['id'] not in targets]
        if len(heads)!=1:raise ValueError('ambiguous resolution chain')
        seen=set();head=heads[0]
        while 'resolves' in head:
            if head['id'] in seen:raise ValueError('cycle')
            seen.add(head['id'])
            parent=by_id.get(head['resolves'])
            if parent is None:raise ValueError('broken resolves reference')
            head=parent
        if len(seen)+1!=len(records):raise ValueError('disconnected resolution chain')
        return copy.deepcopy(heads[0])

    def review(self,principal,execution_id,clause,target,verdict):
        records=self._records(execution_id,clause)
        effective=self.effective(execution_id,clause)
        authorized='review' in PERMISSIONS.get(principal,set())
        current=target==effective['id']
        inconclusive=effective['disposition']!='actionable'
        if self.mutation=='allow_stale_resolution':
            # Deliberately broken SUT: accepts a stale reference even when the
            # current effective Result is already actionable. Both guardrails
            # must be bypassed to make this mutation non-equivalent.
            current=True
            inconclusive=True
        if self.mutation=='allow_actionable_resolution':inconclusive=True
        if self.mutation=='allow_unprivileged_resolution':authorized=True
        if not (authorized and current and inconclusive):
            self.audit.append({'kind':'review_rejected','execution_id':execution_id,'clause':clause})
            return {'accepted':False,'code':'INVALID_RESOLUTION'}
        result={'id':'review-'+uuid.uuid4().hex,'execution_id':execution_id,'clause':clause,
                'oracle_type':'human_reviewer','disposition':'actionable',
                'verdict':verdict,'confidence':'not_applicable','resolves':target}
        if self.mutation=='wrong_review_execution':result['execution_id']='other-execution'
        records.append(result)
        self.saved_by_execution(execution_id)['results'].append(copy.deepcopy(result))
        self.audit.append({'kind':'review_accepted','result_id':result['id']})
        return {'accepted':True,'result':copy.deepcopy(result)}

    def saved_by_execution(self,execution_id):
        for data in self.saved.values():
            for ex in data.get('executions',[]):
                if ex['id']==execution_id:return ex
        raise KeyError('execution not found')

    def reevaluate(self,execution_id):
        ex=self.saved_by_execution(execution_id)
        effective=[self.effective(execution_id,clause) for eid,clause in self.resolutions if eid==execution_id]
        non=sum(r['disposition']!='actionable' for r in effective)
        failing=any(r['disposition']=='actionable' and r['verdict']=='fail' for r in effective)
        reasons=(['non_actionable_results'] if non else [])+(['aggregate_failed'] if failing else [])
        gate={'id':'gate-'+uuid.uuid4().hex,'execution_id':execution_id,'status':'fail' if non or failing else 'pass',
              'reasons':reasons,'basis':{'results':len(effective)-non,'not_actionable':non}}
        ex['gate']=gate
        return copy.deepcopy(gate)

    def approve_override(self,principal,execution_id,gate_id,justification):
        ex=self.saved_by_execution(execution_id);gate=ex['gate']
        allowed=('approve_override' in PERMISSIONS.get(principal,set()) and
                 gate['id']==gate_id and gate['status']=='fail' and
                 isinstance(justification,str) and bool(justification.strip()) and
                 'override' not in gate)
        if self.mutation=='allow_unprivileged_approval':allowed=gate['id']==gate_id and gate['status']=='fail'
        if not allowed:return {'accepted':False,'code':'APPROVAL_REJECTED'}
        approval={'record_id':'approval-'+uuid.uuid4().hex,'gate_id':gate_id,
                  'execution_id':execution_id,'approved_by':principal,'justification':justification}
        if self.mutation=='omit_approver':approval['approved_by']=''
        self.approvals[approval['record_id']]=copy.deepcopy(approval)
        gate['override']=copy.deepcopy(approval)
        if self.mutation=='override_as_pass':gate['status']='pass'
        self.audit.append({'kind':'override_approved','approval_id':approval['record_id']})
        return {'accepted':True,'approval':copy.deepcopy(approval)}

    def record_release(self,principal,execution_id,decision='overridden',approval_id=None):
        ex=self.saved_by_execution(execution_id);gate=ex['gate']
        approval=self.approvals.get(approval_id)
        allowed=('release' in PERMISSIONS.get(principal,set()) and decision=='overridden' and
                 gate['status']=='fail' and isinstance(approval,dict) and
                 approval['gate_id']==gate['id'] and approval['execution_id']==execution_id and
                 gate.get('override')==approval and approval['approved_by']=='P-APPROVER' and
                 bool(approval.get('justification','').strip()))
        if self.mutation=='reuse_override_any_gate' and approval is not None:allowed=True
        if self.mutation=='release_without_approval':allowed=True
        if not allowed:return {'accepted':False,'code':'RELEASE_REJECTED'}
        row={'id':'release-'+uuid.uuid4().hex,'gate_id':gate['id'],
             'execution_id':execution_id,'decision':decision,'approval_id':approval_id}
        self.releases.append(row)
        self.audit.append({'kind':'release_recorded','release_id':row['id']})
        return {'accepted':True,'release':copy.deepcopy(row)}


def inspect_resolution(mock,execution_id,clause,before,attempt,gate_before):
    """Independent evaluator compares observable before/after snapshots."""
    if attempt.get('accepted') is True:
        return {'outcome':'FAIL','reason':'REJECTED_REVIEW_ACCEPTED'}
    try:
        after=mock._records(execution_id,clause)
        gate=mock.saved_by_execution(execution_id)['gate']
        current=mock.effective(execution_id,clause)
    except (KeyError,ValueError):
        return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
    if attempt['accepted'] or before['records']!=after or before['effective']!=current or gate_before!=gate:
        return {'outcome':'FAIL','reason':'REJECTED_REVIEW_MUTATED_STATE'}
    return {'outcome':'PASS','reason':'EXPECTED_MET'}


def inspect_override(mock,execution_id,gate_before,first,approved,second):
    try:gate=mock.saved_by_execution(execution_id)['gate']
    except KeyError:return {'outcome':'NOT_RUN','reason':'GATE_MISSING'}
    a=approved.get('approval')
    correct=(not first['accepted'] and approved['accepted'] and second['accepted'] and
             a is not None and mock.approvals.get(a['record_id'])==a and
             gate['id']==gate_before['id'] and gate['status']=='fail' and
             gate['override']==a and a['approved_by']=='P-APPROVER' and
             isinstance(a['justification'],str) and bool(a['justification'].strip()))
    return {'outcome':'PASS' if correct else 'FAIL',
            'reason':'EXPECTED_MET' if correct else 'OVERRIDE_INVARIANT_VIOLATED'}
