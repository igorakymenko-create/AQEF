import unittest
from verification import matrix,scenario,closed_absence,assessment_probe,evidence_outcome
from negative import aggregate

class S23Mutation(unittest.TestCase):
    def test_matrix_correct_all_pass(self):
        m=matrix();self.assertEqual(m['good_aggregate'],'PASS',m)
        self.assertEqual({x['outcome'] for x in m['good'].values()},{'PASS'})
    def test_matrix_broken_all_fail(self):
        m=matrix();self.assertEqual(m['broken_aggregate'],'FAIL',m)
        self.assertEqual({x['outcome'] for x in m['broken'].values()},{'FAIL'})
    def test_retry_mutants_detected(self):
        for mutation in ('failed_attempt_record','missing_execution','missing_conversation'):
            with self.subTest(mutation=mutation):self.assertEqual(scenario('CT-EXE-003',mutation)['outcome'],'FAIL')
    def test_conversation_mutants_detected(self):
        for mutation in ('alter_prompt','alter_response','missing_conversation','duplicate_conversation','duplicate_subject_call'):
            with self.subTest(mutation=mutation):self.assertEqual(scenario('CT-EXE-008',mutation)['outcome'],'FAIL')
    def test_validator_mutants_detected(self):
        for mutation in ('judge_on_failed_validation','judge_before_validator','empty_as_pass'):
            with self.subTest(mutation=mutation):self.assertEqual(scenario('CT-ASM-001',mutation)['outcome'],'FAIL')
    def test_unavailable_mutants_detected(self):
        for mutation in ('crash_as_fail','crash_no_result','judge_on_unavailable'):
            with self.subTest(mutation=mutation):self.assertEqual(scenario('CT-ASM-014',mutation)['outcome'],'FAIL')
    def test_unclosed_absence_not_run(self):
        self.assertEqual(closed_absence(terminal=False)['outcome'],'NOT_RUN')
    def test_closed_absence_pass(self):
        self.assertEqual(closed_absence()['outcome'],'PASS')
    def test_late_call_revokes_absence_pass(self):
        self.assertEqual(closed_absence(late=True)['outcome'],'FAIL')
    def test_actual_http_correct(self):
        self.assertEqual(assessment_probe()['outcome'],'PASS')
    def test_actual_http_judge_mutation(self):
        self.assertEqual(assessment_probe(mutation='judge_on_failed_validation')['outcome'],'FAIL')
    def test_actual_http_incomplete(self):
        self.assertEqual(assessment_probe(terminal_observed=False)['outcome'],'NOT_RUN')
    def test_actual_http_tamper(self):
        for damage in ('bytes','wrong_owner','missing','wrong_correlation'):
            with self.subTest(damage=damage):self.assertEqual(assessment_probe(damage=damage)['outcome'],'NOT_RUN')
    def test_aggregate_not_run_over_pass(self):
        self.assertEqual(aggregate(['PASS','NOT_RUN']),'NOT_RUN')
    def test_aggregate_fail_over_not_run(self):
        self.assertEqual(aggregate(['FAIL','NOT_RUN','PASS']),'FAIL')
    def test_unknown_case(self):
        with self.assertRaises(ValueError):scenario('CT-UNKNOWN')

if __name__=='__main__':unittest.main()
