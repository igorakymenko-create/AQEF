import ast
import pathlib
import sys
import threading
import time
import unittest
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'harness'/'s02_harness'))
sys.path.insert(0, str(ROOT/'s3_mutation'))
sys.path.insert(0, str(ROOT/'s35_integration'))
sys.path.insert(0, str(ROOT/'s2_assessment'))
from harness import Harness
from observation import local_profile, observe_closed
from apply_s355 import PATCHES


class S355Tests(unittest.TestCase):
    def session(self):
        h=Harness();sid=h.begin('s355-'+uuid.uuid4().hex)
        h.configure(sid,'judge','J-PASS-90')
        return h,sid

    def test_calibration_is_real_positive(self):
        profile=local_profile()
        self.assertEqual(profile['source'],'MEASURED_LOCAL_MOCK_ONLY')
        self.assertGreater(profile['drain_ms'],0)
        self.assertEqual(profile['clock_id'],'s02-monotonic-process')
        self.assertGreaterEqual(profile['sample_count'],2)

    def test_elapsed_and_watermark(self):
        h,sid=self.session()
        actual=observe_closed(h,sid,'judge',0)
        self.assertEqual(actual['outcome'],'PASS',actual)
        self.assertGreaterEqual(actual['elapsed_ms'],actual['drain_ms'])
        self.assertGreater(actual['watermark'],0)
        self.assertEqual(actual['clock_id'],h.clock_id)

    def test_unclosed_not_run(self):
        h,sid=self.session()
        actual=observe_closed(h,sid,'judge',terminal_observed=False)
        self.assertEqual(actual['outcome'],'NOT_RUN')
        self.assertEqual(h.session(sid).phase,'running')

    def test_insufficient_budget_not_run(self):
        h,sid=self.session()
        actual=observe_closed(h,sid,'judge',max_budget_ms=local_profile()['drain_ms']-1)
        self.assertEqual(actual['outcome'],'NOT_RUN',actual)
        self.assertEqual(h.session(sid).phase,'running')

    def test_untrusted_profile_not_run(self):
        h,sid=self.session()
        actual=observe_closed(h,sid,'judge',profile={'drain_ms':20,'source':'unknown'})
        self.assertEqual(actual['outcome'],'NOT_RUN')

    def test_zero_profile_not_run(self):
        h,sid=self.session()
        actual=observe_closed(h,sid,'judge',profile={'source':'MEASURED_LOCAL_MOCK_ONLY',
                                  'clock_id':h.clock_id,'drain_ms':0})
        self.assertEqual(actual['outcome'],'NOT_RUN')

    def test_mismatched_clock_not_run(self):
        h,sid=self.session()
        actual=observe_closed(h,sid,'judge',profile={'source':'MEASURED_LOCAL_MOCK_ONLY',
                                  'clock_id':'foreign-clock','drain_ms':30})
        self.assertEqual(actual['outcome'],'NOT_RUN')

    def test_unexpected_call_during_drain_fail(self):
        h,sid=self.session()
        th=threading.Thread(target=lambda: (time.sleep(.007),h.invoke(sid,'judge',{'response':'Hello'})))
        th.start()
        actual=observe_closed(h,sid,'judge',0)
        th.join()
        self.assertEqual(actual['outcome'],'FAIL',actual)
        self.assertGreaterEqual(actual['observed'],1)

    def test_post_close_late_call_fail(self):
        h,sid=self.session()
        self.assertEqual(observe_closed(h,sid,'judge',0)['outcome'],'PASS')
        with self.assertRaises(RuntimeError):h.invoke(sid,'judge',{'response':'Hello'})
        self.assertEqual(h.negative_assertion(sid,'judge',0)['outcome'],'FAIL')

    def test_legacy_source_is_patched(self):
        for name,(old,new) in PATCHES.items():
            with self.subTest(name=name):
                source=(ROOT.parent/name).read_text(encoding='utf-8')
                self.assertNotIn(old,source,'Run apply_s355.py before committing')
                self.assertIn(new,source)
                tree=ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='close_observation':
                        for kw in node.keywords:
                            if kw.arg=='drain_ms' and isinstance(kw.value,ast.Constant):
                                self.assertNotEqual(kw.value.value,0, 'No zero drain in patched source')

    def test_legacy_s32_contract(self):
        from verification import negative_observation
        self.assertEqual(negative_observation()['outcome'],'PASS')
        self.assertEqual(negative_observation(late=True)['outcome'],'FAIL')
        self.assertEqual(negative_observation(closed=False)['outcome'],'NOT_RUN')

    def test_legacy_s22_cases(self):
        from assessment import run_case
        for case in ('CT-ASM-001','CT-ASM-014'):
            with self.subTest(case=case):
                self.assertEqual(run_case(case)['outcome'],'PASS')

    def test_legacy_s350_profiles(self):
        from pipeline import run_case
        for p in ('validation_fail','validator_crash','retry'):
            with self.subTest(profile=p):
                self.assertEqual(run_case(p)['outcome'],'PASS')

    def test_negative_mutants_stay_negative(self):
        from pipeline import run_case
        self.assertEqual(run_case('validator_crash','crash_as_fail')['outcome'],'FAIL')
        from assessment import run_case as assessment_run
        self.assertEqual(assessment_run('CT-ASM-001','empty_as_pass')['outcome'],'FAIL')

if __name__=='__main__':unittest.main()
