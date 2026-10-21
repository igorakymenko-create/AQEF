import unittest
from pipeline import run_case,PROFILES,service,evaluate_independently
from mock import fixture_base

class UnifiedPipelineCTS(unittest.TestCase):
    def test_six_profiles(self):
        for profile in PROFILES:
            with self.subTest(profile=profile):
                result=run_case(profile)
                self.assertEqual(result['outcome'],'PASS',result)
    def test_retry_attempt_not_execution(self):
        v=run_case('retry');self.assertEqual(v['outcome'],'PASS',v)
        self.assertEqual(v['subject_calls'],2)
        self.assertEqual(v['result_count'],2)
    def test_actual_validator_crash(self):
        v=run_case('validator_crash');self.assertEqual(v['outcome'],'PASS',v)
        self.assertEqual(v['judge_calls'],0)
        self.assertEqual(v['gate_status'],'fail')
    def test_validator_short_circuit(self):
        v=run_case('validation_fail');self.assertEqual(v['outcome'],'PASS',v)
        self.assertEqual(v['judge_calls'],0)
    def test_inconclusive_blocks(self):
        v=run_case('inconclusive');self.assertEqual(v['outcome'],'PASS',v)
        self.assertEqual(v['gate_status'],'fail')
    def test_valid_success(self):
        self.assertEqual(run_case('healthy')['gate_status'],'pass')
    def test_mutants_fail(self):
        for profile,mutation in [('retry','record_failed_attempt'),('healthy','alter_conversation'),
             ('validation_fail','judge_after_validation_failure'),
             ('validator_crash','crash_as_fail'),('inconclusive','allow_bad_gate'),
             ('healthy','allow_bad_gate')]:
            # allow_bad_gate on already passing gate is equivalent, not a mutation case
            if profile=='healthy' and mutation=='allow_bad_gate':continue
            with self.subTest(profile=profile,mutation=mutation):
                result=run_case(profile,mutation)
                self.assertEqual(result['outcome'],'FAIL',result)
    def test_missing_terminal_not_run(self):
        self.assertEqual(run_case('healthy',terminal_observed=False)['outcome'],'NOT_RUN')
    def test_tampered_evidence_not_run(self):
        self.assertEqual(run_case('healthy',damage=True)['outcome'],'NOT_RUN')
    def test_unique_attribution(self):
        a=run_case('healthy');b=run_case('healthy')
        self.assertEqual(a['outcome'],'PASS');self.assertEqual(b['outcome'],'PASS')
        self.assertNotEqual(a['execution_id'],b['execution_id'])
    def test_one_shared_harness(self):
        with service() as (mock,server):
            self.assertIs(server.mock,mock)
            self.assertIs(mock.validator,mock.validator)
    def test_refuse_unknown_profile(self):
        with self.assertRaises(ValueError):run_case('unknown')

if __name__=='__main__':unittest.main()
