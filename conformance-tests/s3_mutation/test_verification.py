import unittest
from verification import evidence_probe, review_probe, override_probe, negative_observation, matrix


class S32Mutation(unittest.TestCase):
    def test_good_matrix(self):
        m = matrix()
        self.assertEqual(m['good_aggregate'], 'PASS')
        self.assertEqual({x['outcome'] for x in m['good'].values()}, {'PASS'})

    def test_broken_matrix(self):
        m = matrix()
        self.assertEqual(m['mutant_aggregate'], 'FAIL')
        self.assertEqual({x['outcome'] for x in m['mutants'].values()}, {'FAIL'}, m)

    def test_review_four_correct(self):
        for v in 'abcd':
            with self.subTest(v=v): self.assertEqual(review_probe(v)['outcome'], 'PASS')

    def test_repeated_resolution_detected(self):
        self.assertEqual(review_probe('a', 'allow_repeat_review')['outcome'], 'FAIL')

    def test_actionable_resolution_detected(self):
        self.assertEqual(review_probe('c', 'allow_actionable_review')['outcome'], 'FAIL')

    def test_permission_bypass_detected(self):
        self.assertEqual(review_probe('d', 'allow_unprivileged_review')['outcome'], 'FAIL')

    def test_mutated_results_detected(self):
        self.assertEqual(review_probe('b', 'mutate_rejected_results')['outcome'], 'FAIL')

    def test_mutated_gate_detected(self):
        self.assertEqual(review_probe('a', 'mutate_rejected_gate')['outcome'], 'FAIL')

    def test_review_setup_unavailable_not_run(self):
        self.assertEqual(review_probe('a', 'reject_all_review')['outcome'], 'NOT_RUN')

    def test_review_missing_before_not_run(self):
        self.assertEqual(review_probe('a', tamper='missing_before')['outcome'], 'NOT_RUN')

    def test_review_missing_after_not_run(self):
        self.assertEqual(review_probe('b', tamper='missing_after')['outcome'], 'NOT_RUN')

    def test_override_correct(self):
        self.assertEqual(override_probe()['outcome'], 'PASS')

    def test_override_mutations_fail(self):
        for m in ('release_without_override', 'reject_after_override', 'override_as_pass',
                  'omit_approver', 'omit_justification', 're_evaluate_on_override'):
            with self.subTest(m=m): self.assertEqual(override_probe(m)['outcome'], 'FAIL')

    def test_override_changed_gate_id_fail(self):
        self.assertEqual(override_probe(tamper='changed_gate_id')['outcome'], 'FAIL')

    def test_override_changed_evaluation_fail(self):
        self.assertEqual(override_probe(tamper='changed_evaluation')['outcome'], 'FAIL')

    def test_override_missing_evidence_not_run(self):
        for t in ('missing_approval', 'missing_after'):
            with self.subTest(t=t): self.assertEqual(override_probe(tamper=t)['outcome'], 'NOT_RUN')

    def test_evidence_good(self):
        self.assertEqual(evidence_probe()['outcome'], 'PASS')

    def test_evidence_corrupt_not_run(self):
        for d in ('bytes', 'missing', 'wrong_case', 'wrong_run', 'correlation', 'refs', 'version', 'truncated'):
            with self.subTest(d=d): self.assertEqual(evidence_probe(d)['outcome'], 'NOT_RUN')

    def test_observation_open_not_run(self):
        self.assertEqual(negative_observation(closed=False)['outcome'], 'NOT_RUN')

    def test_observation_closed_pass(self):
        self.assertEqual(negative_observation()['outcome'], 'PASS')

    def test_observation_late_fail(self):
        self.assertEqual(negative_observation(late=True)['outcome'], 'FAIL')

    def test_invalid_variant(self):
        with self.assertRaises(ValueError): review_probe('x')


if __name__ == '__main__':
    unittest.main()
