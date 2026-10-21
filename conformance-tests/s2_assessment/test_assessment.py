import unittest
from assessment import run_case, assess_case

class AssessmentCTS(unittest.TestCase):
    def test_asm001_correct(self):self.assertEqual(run_case('CT-ASM-001')['outcome'],'PASS')
    def test_asm014_correct(self):
        r=run_case('CT-ASM-014')
        self.assertEqual(r['outcome'],'PASS',r)
        self.assertEqual(r['validator_result']['disposition'],'oracle_unavailable')
        self.assertIsNone(r['validator_result']['verdict'])
        self.assertEqual(r['validator_result']['confidence'],'not_applicable')
    def test_no_judge_after_validator_fail(self):self.assertEqual(run_case('CT-ASM-001')['judge_calls'],0)
    def test_no_judge_after_validator_unavailable(self):self.assertEqual(run_case('CT-ASM-014')['judge_calls'],0)
    def test_bad_judge_on_failed_validation(self):self.assertEqual(run_case('CT-ASM-001','judge_on_failed_validation')['outcome'],'FAIL')
    def test_bad_judge_before_validation_finished(self):self.assertEqual(run_case('CT-ASM-001','judge_before_validator')['outcome'],'FAIL')
    def test_bad_empty_accepted_as_valid(self):self.assertEqual(run_case('CT-ASM-001','empty_as_pass')['outcome'],'FAIL')
    def test_bad_validator_crash_marked_fail(self):self.assertEqual(run_case('CT-ASM-014','crash_as_fail')['outcome'],'FAIL')
    def test_bad_validator_result_absent(self):self.assertEqual(run_case('CT-ASM-014','crash_no_result')['outcome'],'FAIL')
    def test_bad_judge_on_validator_unavailable(self):self.assertEqual(run_case('CT-ASM-014','judge_on_unavailable')['outcome'],'FAIL')
    def test_fixture_unavailable_not_run(self):self.assertEqual(run_case('CT-ASM-014',fixture_available=False)['outcome'],'NOT_RUN')
    def test_no_terminal_confirmation_not_run(self):self.assertEqual(run_case('CT-ASM-001',terminal_observed=False)['outcome'],'NOT_RUN')
    def test_tampered_evidence_not_run(self):self.assertEqual(run_case('CT-ASM-014',tamper_evidence=True)['outcome'],'NOT_RUN')
    def test_unknown_case(self):
        with self.assertRaises(ValueError):run_case('CT-ASM-999')
    def test_negative_assertion_unclosed_not_run(self):
        self.assertEqual(assess_case('CT-ASM-001',{'results':[]},[],{'outcome':'NOT_RUN'})['outcome'],'NOT_RUN')
    def test_missing_validator_result_fails(self):
        self.assertEqual(assess_case('CT-ASM-014',{'results':[]},[],{'outcome':'PASS'})['outcome'],'FAIL')

if __name__=='__main__':unittest.main()
