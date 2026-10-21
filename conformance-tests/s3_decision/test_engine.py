import unittest
from decision_engine import MockDecision,run_dec006,run_dec012,run_dec012_variant,run_rel006,matrix

class DecisionEngineCTS(unittest.TestCase):
    def test_dec006(self):self.assertEqual(run_dec006()['outcome'],'PASS')
    def test_dec006_mutants(self):
        for m in ('gate_pass_nonactionable','omit_nonactionable_reason','count_nonactionable_as_result','null_gate_value'):
            with self.subTest(m=m):self.assertEqual(run_dec006(m)['outcome'],'FAIL')
    def test_dec012_all_variants(self):
        outcome=run_dec012();self.assertEqual(outcome['outcome'],'PASS',outcome)
        for v in 'abcd':self.assertEqual(outcome['variants'][v]['outcome'],'PASS')
    def test_dec012_duplicate_review(self):self.assertEqual(run_dec012_variant('a','allow_repeat_review')['outcome'],'FAIL')
    def test_dec012_actionable_review(self):self.assertEqual(run_dec012_variant('c','allow_actionable_review')['outcome'],'FAIL')
    def test_dec012_unprivileged_review(self):self.assertEqual(run_dec012_variant('d','allow_unprivileged_review')['outcome'],'FAIL')
    def test_dec012_mutates_rejected_result(self):self.assertEqual(run_dec012_variant('b','mutate_rejected_results')['outcome'],'FAIL')
    def test_dec012_mutates_rejected_gate(self):self.assertEqual(run_dec012_variant('a','mutate_rejected_gate')['outcome'],'FAIL')
    def test_dec012_setup_unavailable(self):self.assertEqual(run_dec012_variant('a','reject_all_review')['outcome'],'NOT_RUN')
    def test_dec012_unclaimed(self):self.assertEqual(run_dec012(claimed_capabilities=())['outcome'],'NOT_APPLICABLE')
    def test_dec012_bad_variant(self):
        with self.assertRaises(ValueError):run_dec012_variant('x')
    def test_rel006(self):self.assertEqual(run_rel006()['outcome'],'PASS')
    def test_rel006_mutants(self):
        for m in ('release_without_override','reject_after_override','omit_approver','omit_justification','override_as_pass','re_evaluate_on_override'):
            with self.subTest(m=m):self.assertEqual(run_rel006(m)['outcome'],'FAIL')
    def test_override_does_not_recompute_gate(self):
        m=MockDecision();m.execute('J-FAIL-90');m.evaluate_gates();n=m.evaluation_count;m.override()
        self.assertEqual(m.evaluation_count,n)
        self.assertEqual(m.gates[0]['status'],'fail')
    def test_reject_preserves_results(self):
        m=MockDecision();j=m.execute('J-PASS-90');m.evaluate_gates();before=list(m.results)
        self.assertFalse(m.review('P-REVIEWER',j['id'],'fail')['accepted']);self.assertEqual(before,m.results)
    def test_distinct_sessions(self):
        a=MockDecision();b=MockDecision();self.assertNotEqual(a.sid,b.sid)
    def test_matrix(self):
        out=matrix();self.assertEqual({v['outcome'] for v in out['good'].values()},{'PASS'})
        self.assertEqual({v['outcome'] for v in out['mutants'].values()},{'FAIL'})

if __name__=='__main__':unittest.main()
