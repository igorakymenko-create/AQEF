import copy
import unittest
from human_review import (ManualClock,HumanReviewMock,observe_timeout,assess_ct_hrv_003,
                          run_ct_hrv_003,CAPABILITY)

class CT_HRV_003(unittest.TestCase):
    def setUp(self):
        self.clock=ManualClock()
        self.sut=HumanReviewMock(clock=self.clock)
        self.xid=self.sut.create()
        r=self.sut.get_results(self.xid)['results'][0]
        self.pre={'outcome':'PASS','id':r['id'],'disposition':r['disposition'],'verdict':r['verdict']}

    def check(self, sut=None, xid=None, pre=None, observed=None):
        sut=sut or self.sut; xid=xid or self.xid; pre=pre or self.pre
        if observed is None: observed={'outcome':'PASS'}
        return assess_ct_hrv_003(claimed=True,pre=pre,observed=observed,
            execution_id=xid,results=sut.get_results(xid),gate=sut.evaluate_gates(xid),events=sut.get_events(xid))

    def test_before_timeout_remains_pending(self):
        self.clock.advance(.019);self.sut.poll(self.xid)
        self.assertFalse(any(e['event']=='review_timeout' for e in self.sut.get_events(self.xid)))
        self.assertEqual(self.sut.get_results(self.xid)['results'][0]['disposition'],'awaiting_review')
    def test_at_deadline_block_pass(self):
        self.clock.advance(.020);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'PASS')
    def test_timeout_idempotent_single_event(self):
        self.clock.advance(.030);self.sut.poll(self.xid);self.sut.poll(self.xid)
        self.assertEqual(sum(e['event']=='review_timeout' for e in self.sut.get_events(self.xid)),1)
    def test_default_policy_block(self):
        self.clock.advance(.020);self.sut.poll(self.xid)
        self.assertEqual([e['policy'] for e in self.sut.get_events(self.xid) if e['event']=='review_timeout'],['block'])
    def test_shortest_accepted_timeout(self):
        with self.assertRaises(ValueError):self.sut.create(timeout_ms=19)
        self.assertIsInstance(self.sut.create(timeout_ms=20),str)
    def test_no_verdict_after_timeout(self):
        self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertIsNone(self.sut.get_results(self.xid)['results'][0]['verdict'])
    def test_gate_fail(self):
        self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.sut.evaluate_gates(self.xid)['status'],'fail')
    def test_gate_non_actionable_reason(self):
        self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertIn('non_actionable_results',self.sut.evaluate_gates(self.xid)['reasons'])
    def test_capability_unclaimed_not_applicable(self):
        self.assertEqual(run_ct_hrv_003(claims=False)['outcome'],'NOT_APPLICABLE')
    def test_mutant_silent_pass_detected(self):
        self.sut.mutation='silent_pass';self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'FAIL')
    def test_mutant_actionable_detected(self):
        self.sut.mutation='actionable_without_verdict';self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'FAIL')
    def test_mutant_fabricated_fail_detected(self):
        self.sut.mutation='fabricated_fail';self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'FAIL')
    def test_mutant_gate_pass_detected(self):
        self.sut.mutation='force_gate_pass';self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'FAIL')
    def test_mutant_gate_reason_detected(self):
        self.sut.mutation='omit_gate_reason';self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'FAIL')
    def test_mutant_wrong_policy_detected(self):
        self.sut.mutation='wrong_timeout_policy';self.clock.advance(.025);self.sut.poll(self.xid)
        self.assertEqual(self.check()['outcome'],'FAIL')
    def test_missing_timeout_event_not_run(self):
        self.sut.mutation='missing_timeout_event';self.clock.advance(.025);self.sut.poll(self.xid)
        obs=observe_timeout(self.sut,self.xid,budget_ms=2,poll_interval_ms=1)
        self.assertEqual(obs['outcome'],'NOT_RUN')
    def test_missing_prestate_not_run(self):
        self.assertEqual(assess_ct_hrv_003(claimed=True,pre={},observed={'outcome':'PASS'})['outcome'],'NOT_RUN')
    def test_unexpected_prestate_fail(self):
        self.assertEqual(assess_ct_hrv_003(claimed=True,pre={'outcome':'PASS','id':self.pre['id'],'disposition':'actionable','verdict':'pass'},observed={'outcome':'PASS'})['outcome'],'FAIL')
    def test_readback_unavailable_not_run(self):
        self.assertEqual(assess_ct_hrv_003(claimed=True,pre=self.pre,observed={'outcome':'PASS'})['outcome'],'NOT_RUN')
    def test_identity_substitution_detected(self):
        self.clock.advance(.025);self.sut.poll(self.xid)
        old=self.sut.results[self.xid]['record']['id'];self.sut.results[self.xid]['record']['id']='result-tampered'
        self.assertEqual(self.check()['outcome'],'FAIL')
        self.sut.results[self.xid]['record']['id']=old
    def test_budget_expiry_not_run(self):
        self.assertEqual(observe_timeout(self.sut,self.xid,budget_ms=2,poll_interval_ms=1)['outcome'],'NOT_RUN')
    def test_invalid_budget_not_run(self):
        self.assertEqual(observe_timeout(self.sut,self.xid,budget_ms=0)['outcome'],'NOT_RUN')
    def test_real_clock_healthy(self):
        self.assertEqual(run_ct_hrv_003()['outcome'],'PASS')
    def test_real_clock_false_pass(self):
        self.assertEqual(run_ct_hrv_003(mutation='silent_pass')['outcome'],'FAIL')
    def test_real_clock_missing_timeout_not_run(self):
        self.assertEqual(run_ct_hrv_003(mutation='missing_timeout_event',budget_ms=40)['outcome'],'NOT_RUN')

if __name__=='__main__':unittest.main()
