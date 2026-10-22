import unittest
from timing import measured_profile,timed_observation,measured_matrix,TimingError

class TimingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=measured_profile(samples=2,latency_ms=10,margin_ms=25)
    def run_timed(self,**kw):return timed_observation(drain_ms=self.p['drain_ms'],calibration=self.p,**kw)
    def test_profile_measured(self):self.assertEqual(self.p['source'],'MEASURED_LOCAL_MOCK_ONLY')
    def test_profile_positive(self):self.assertGreater(self.p['drain_ms'],0)
    def test_profile_clock(self):self.assertEqual(self.p['clock_id'],'s02-monotonic-process')
    def test_profile_samples(self):self.assertEqual(len(self.p['probe_observed_ms']),2)
    def test_profile_actual_durations(self):self.assertTrue(all(x>0 for x in self.p['probe_observed_ms']))
    def test_closed_observation_pass(self):self.assertEqual(self.run_timed()['outcome'],'PASS')
    def test_real_elapsed_not_shorter_than_drain(self):
        r=self.run_timed();self.assertGreaterEqual(r['elapsed_ms'],self.p['drain_ms'])
    def test_watermark_is_present(self):self.assertGreaterEqual(self.run_timed()['watermark'],1)
    def test_zero_drain_rejected(self):
        with self.assertRaises(TimingError):timed_observation(drain_ms=0,calibration=self.p)
    def test_negative_drain_rejected(self):
        with self.assertRaises(TimingError):timed_observation(drain_ms=-1,calibration=self.p)
    def test_missing_calibration_not_run(self):
        self.assertEqual(timed_observation(drain_ms=20)['outcome'],'NOT_RUN')
    def test_drain_below_calibration_not_run(self):
        self.assertEqual(timed_observation(drain_ms=1,calibration=self.p)['outcome'],'NOT_RUN')
    def test_insufficient_budget_not_run(self):
        self.assertEqual(self.run_timed(max_budget_ms=self.p['drain_ms']-1)['outcome'],'NOT_RUN')
    def test_unobserved_terminal_not_run(self):
        self.assertEqual(self.run_timed(terminal_observed=False)['outcome'],'NOT_RUN')
    def test_during_drain_unexpected_call_fails(self):
        r=self.run_timed(scheduled_ms=max(0,self.p['drain_ms']//3))
        self.assertEqual(r['outcome'],'FAIL',r);self.assertEqual(r['observed_calls'],1)
    def test_during_drain_expected_call_passes(self):
        r=self.run_timed(scheduled_ms=max(0,self.p['drain_ms']//3),expected_calls=1)
        self.assertEqual(r['outcome'],'PASS',r)
    def test_after_closure_late_fails(self):
        r=self.run_timed(post_close_call=True)
        self.assertEqual(r['outcome'],'FAIL',r);self.assertTrue(r['late'])
    def test_post_close_not_counted_as_ordinary_call(self):
        r=self.run_timed(post_close_call=True)
        self.assertEqual(r['observed_calls'],0);self.assertEqual(r['outcome'],'FAIL')
    def test_late_thread_after_close_fails(self):
        r=self.run_timed(scheduled_ms=self.p['drain_ms']+35)
        self.assertEqual(r['outcome'],'FAIL',r);self.assertTrue(r['late'])
    def test_distinct_sessions(self):
        self.assertNotEqual(self.run_timed()['session_id'],self.run_timed()['session_id'])
    def test_invalid_samples(self):
        with self.assertRaises(TimingError):measured_profile(samples=1)
    def test_invalid_delay(self):
        with self.assertRaises(TimingError):self.run_timed(scheduled_ms=-1)
    def test_matrix(self):
        m=measured_matrix()
        self.assertEqual([m[k]['outcome'] for k in ('correct','during_drain','after_closure','insufficient_budget','missing_terminal')],
                         ['PASS','FAIL','FAIL','NOT_RUN','NOT_RUN'])
if __name__=='__main__':unittest.main()
