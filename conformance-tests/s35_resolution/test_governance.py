import copy, pathlib, sys, unittest, uuid
from governance import GovernedPipeline, inspect_resolution, inspect_override
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'s1_configuration'))
from mock import fixture_base

def prepared(judge='J-PASS-60',mutation=None):
    m=GovernedPipeline(mutation)
    sid='s351-'+uuid.uuid4().hex
    m.prepare_pipeline(sid,fixture_base(),'SR-OK',judge,'schema')
    receipt=m.execute(sid,'CT-DEC-006')
    assert len(receipt['execution_ids'])==1
    ex=m.saved[sid]['executions'][0]
    return m,ex

def judge_result(m,ex):
    return next(x for x in ex['results'] if x['oracle_type']=='judge')

class GovernanceTests(unittest.TestCase):
    def test_single_pipeline_execution(self):
        m,e=prepared()
        self.assertEqual(len(e['results']),2)
        self.assertEqual(e['gate']['execution_id'],e['id'])
        self.assertEqual(m.effective(e['id'],'expectation-1')['id'],judge_result(m,e)['id'])

    def test_resolution_current_inconclusive(self):
        m,e=prepared()
        first=judge_result(m,e)
        action=m.review('P-REVIEWER',e['id'],'expectation-1',first['id'],'pass')
        self.assertTrue(action['accepted'])
        self.assertEqual(m.effective(e['id'],'expectation-1')['id'],action['result']['id'])
        self.assertEqual(action['result']['resolves'],first['id'])
        self.assertEqual(len(e['results']),3)

    def test_resolution_is_scoped_to_clause(self):
        m,e=prepared()
        schema=m.effective(e['id'],'schema')
        target=judge_result(m,e)['id']
        m.review('P-REVIEWER',e['id'],'expectation-1',target,'pass')
        self.assertEqual(m.effective(e['id'],'schema'),schema)

    def test_resolution_is_scoped_to_execution(self):
        m,e=prepared()
        sid2='s351-'+uuid.uuid4().hex
        m.prepare_pipeline(sid2,fixture_base(),'SR-OK','J-PASS-60','schema')
        other=m.saved.get(sid2)
        m.execute(sid2,'CT-DEC-006')
        e2=m.saved[sid2]['executions'][0]
        target=judge_result(m,e)['id']
        self.assertFalse(m.review('P-REVIEWER',e2['id'],'expectation-1',target,'fail')['accepted'])
        self.assertEqual(m.effective(e2['id'],'expectation-1')['id'],judge_result(m,e2)['id'])

    def check_rejection(self,m,e,principal,target):
        before={'records':copy.deepcopy(m._records(e['id'],'expectation-1')),
                'effective':m.effective(e['id'],'expectation-1')}
        gate=copy.deepcopy(e['gate'])
        action=m.review(principal,e['id'],'expectation-1',target,'fail')
        self.assertEqual(inspect_resolution(m,e['id'],'expectation-1',before,action,gate)['outcome'],'PASS')
        return action

    def test_duplicate_resolution_rejected(self):
        m,e=prepared()
        initial=judge_result(m,e)['id']
        self.assertTrue(m.review('P-REVIEWER',e['id'],'expectation-1',initial,'pass')['accepted'])
        self.check_rejection(m,e,'P-REVIEWER',initial)

    def test_actionable_result_rejected(self):
        m,e=prepared('J-PASS-90')
        self.check_rejection(m,e,'P-REVIEWER',judge_result(m,e)['id'])

    def test_unprivileged_review_rejected(self):
        m,e=prepared()
        self.check_rejection(m,e,'P-NOPERM',judge_result(m,e)['id'])

    def test_second_review_of_actionable_resolution_rejected(self):
        m,e=prepared()
        first=judge_result(m,e)['id']
        resolved=m.review('P-REVIEWER',e['id'],'expectation-1',first,'pass')['result']
        self.check_rejection(m,e,'P-REVIEWER',resolved['id'])

    def test_stale_mutant_detected(self):
        m,e=prepared(mutation='allow_stale_resolution')
        original=judge_result(m,e)['id']
        m.review('P-REVIEWER',e['id'],'expectation-1',original,'pass')
        before={'records':copy.deepcopy(m._records(e['id'],'expectation-1')),
                'effective':m.effective(e['id'],'expectation-1')}
        gate=copy.deepcopy(e['gate'])
        attempt=m.review('P-REVIEWER',e['id'],'expectation-1',original,'fail')
        self.assertEqual(inspect_resolution(m,e['id'],'expectation-1',before,attempt,gate)['outcome'],'FAIL')
        # Accepted stale review is an observable SUT violation.

    def test_actionable_mutant_detected(self):
        m,e=prepared('J-PASS-90',mutation='allow_actionable_resolution')
        result=m.review('P-REVIEWER',e['id'],'expectation-1',judge_result(m,e)['id'],'fail')
        self.assertTrue(result['accepted']) # Deliberate broken SUT for CTS detection.

    def test_unprivileged_mutant_detected(self):
        m,e=prepared(mutation='allow_unprivileged_resolution')
        r=m.review('P-NOPERM',e['id'],'expectation-1',judge_result(m,e)['id'],'fail')
        self.assertTrue(r['accepted'])

    def test_review_recomputes_gate_only_on_explicit_evaluation(self):
        m,e=prepared()
        old=copy.deepcopy(e['gate'])
        m.review('P-REVIEWER',e['id'],'expectation-1',judge_result(m,e)['id'],'pass')
        self.assertEqual(e['gate'],old)
        new=m.reevaluate(e['id'])
        self.assertEqual(new['status'],'pass')
        self.assertNotEqual(new['id'],old['id'])

    def test_override_lifecycle(self):
        m,e=prepared('J-FAIL-90')
        original=copy.deepcopy(e['gate'])
        first=m.record_release('P-RELEASE',e['id'])
        approved=m.approve_override('P-APPROVER',e['id'],original['id'],'reviewed exception')
        second=m.record_release('P-RELEASE',e['id'],approval_id=approved['approval']['record_id'])
        self.assertEqual(inspect_override(m,e['id'],original,first,approved,second)['outcome'],'PASS')

    def test_override_not_pass_gate(self):
        m,e=prepared('J-FAIL-90')
        m.approve_override('P-APPROVER',e['id'],e['gate']['id'],'reason')
        self.assertEqual(e['gate']['status'],'fail')

    def test_wrong_approver_rejected(self):
        m,e=prepared('J-FAIL-90')
        self.assertFalse(m.approve_override('P-REVIEWER',e['id'],e['gate']['id'],'reason')['accepted'])
        self.assertNotIn('override',e['gate'])

    def test_empty_justification_rejected(self):
        m,e=prepared('J-FAIL-90')
        self.assertFalse(m.approve_override('P-APPROVER',e['id'],e['gate']['id'],'  ')['accepted'])

    def test_wrong_gate_rejected(self):
        m,e=prepared('J-FAIL-90')
        self.assertFalse(m.approve_override('P-APPROVER',e['id'],'gate-other','reason')['accepted'])

    def test_override_single_gate(self):
        m,e=prepared('J-FAIL-90')
        approval=m.approve_override('P-APPROVER',e['id'],e['gate']['id'],'reason')['approval']
        oldid=e['gate']['id']
        new=m.reevaluate(e['id'])
        self.assertNotEqual(oldid,new['id'])
        self.assertNotIn('override',new)
        self.assertFalse(m.record_release('P-RELEASE',e['id'],approval_id=approval['record_id'])['accepted'])

    def test_override_does_not_cross_execution(self):
        m,e=prepared('J-FAIL-90')
        a=m.approve_override('P-APPROVER',e['id'],e['gate']['id'],'reason')['approval']
        sid='s351-'+uuid.uuid4().hex
        m.prepare_pipeline(sid,fixture_base(),'SR-OK','J-FAIL-90','schema')
        m.execute(sid,'CT-REL-006')
        e2=m.saved[sid]['executions'][0]
        self.assertFalse(m.record_release('P-RELEASE',e2['id'],approval_id=a['record_id'])['accepted'])

    def test_release_principal_must_have_permission(self):
        m,e=prepared('J-FAIL-90')
        a=m.approve_override('P-APPROVER',e['id'],e['gate']['id'],'reason')['approval']
        self.assertFalse(m.record_release('P-NOPERM',e['id'],approval_id=a['record_id'])['accepted'])

    def test_bad_override_gate_mutant_detected(self):
        m,e=prepared('J-FAIL-90',mutation='override_as_pass')
        g=copy.deepcopy(e['gate'])
        first=m.record_release('P-RELEASE',e['id'])
        approved=m.approve_override('P-APPROVER',e['id'],g['id'],'reason')
        second=m.record_release('P-RELEASE',e['id'],approval_id=approved['approval']['record_id'])
        self.assertEqual(inspect_override(m,e['id'],g,first,approved,second)['outcome'],'FAIL')

    def test_missing_approver_mutant_detected(self):
        m,e=prepared('J-FAIL-90',mutation='omit_approver')
        g=copy.deepcopy(e['gate'])
        first=m.record_release('P-RELEASE',e['id'])
        approved=m.approve_override('P-APPROVER',e['id'],g['id'],'reason')
        second=m.record_release('P-RELEASE',e['id'],approval_id=approved['approval']['record_id'])
        self.assertEqual(inspect_override(m,e['id'],g,first,approved,second)['outcome'],'FAIL')

    def test_release_without_approval_mutant_detected(self):
        m,e=prepared('J-FAIL-90',mutation='release_without_approval')
        self.assertTrue(m.record_release('P-RELEASE',e['id'])['accepted'])

    def test_approval_must_match_stored_record(self):
        m,e=prepared('J-FAIL-90')
        a=m.approve_override('P-APPROVER',e['id'],e['gate']['id'],'reason')['approval']
        e['gate']['override']['justification']='tampered'
        self.assertFalse(m.record_release('P-RELEASE',e['id'],approval_id=a['record_id'])['accepted'])

if __name__=='__main__':unittest.main()
