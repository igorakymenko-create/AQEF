import concurrent.futures, time, unittest
from harness import Harness

class S02(unittest.TestCase):
 def setUp(self):
  self.h=Harness();self.s=self.h.begin('session-a')
 def test_default_and_reset(self):
  self.h.configure(self.s,'subject','SR-503-THEN-OK')
  self.assertEqual(self.h.invoke(self.s,'subject',{})['status'],503)
  self.assertEqual(self.h.invoke(self.s,'subject',{})['result'],'Hello! How can I help?')
  self.h.reset(self.s)
  self.assertEqual(self.h.invoke(self.s,'subject',{})['call_no'],1)
 def test_subject_registry(self):
  for code,expect in [('SR-EMPTY',''),('SR-ECHO','Testing'),('SR-BYE','Goodbye.'),('SR-OK','Hello! How can I help?')]:
   self.h.reset(self.s);self.h.configure(self.s,'subject',code)
   self.assertEqual(self.h.invoke(self.s,'subject',{'prompt':'Testing'})['result'],expect)
 def test_subject_delay(self):
  self.h.configure(self.s,'subject','SR-SLOW-200');t=time.monotonic();self.h.invoke(self.s,'subject',{});self.assertGreaterEqual(time.monotonic()-t,.2)
 def test_subject_tool_is_declarative_only(self):
  self.h.configure(self.s,'subject','SR-CALL(https://cts-outside.example/x)')
  o=self.h.invoke(self.s,'subject',{})['result'];self.assertFalse(o['executed']);self.assertEqual(o['tool'],'http_get')
 def test_judge_registry(self):
  for code,v,c in [('J-PASS-90','pass',.9),('J-PASS-60','pass',.6),('J-FAIL-90','fail',.9)]:
   self.h.reset(self.s);self.h.configure(self.s,'judge',code);o=self.h.invoke(self.s,'judge',{})['result'];self.assertEqual((o['verdict'],o['confidence']),(v,c))
 def test_judge_down_retry(self):
  self.h.configure(self.s,'judge','J-DOWN-THEN-PASS-90');self.assertEqual(self.h.invoke(self.s,'judge',{})['outcome'],'unreachable');self.assertEqual(self.h.invoke(self.s,'judge',{})['result']['verdict'],'pass')
 def test_judge_fail_retry(self):
  self.h.configure(self.s,'judge','J-FAIL-THEN-PASS-90');self.assertEqual(self.h.invoke(self.s,'judge',{})['result']['verdict'],'fail');self.assertEqual(self.h.invoke(self.s,'judge',{})['result']['verdict'],'pass')
 def test_judge_catch(self):
  self.h.configure(self.s,'judge','J-CATCH')
  for text,expected in [('Goodbye.','fail'),('Bye now.','fail'),('Hello! How can I help?','pass')]:self.assertEqual(self.h.invoke(self.s,'judge',{'response':text})['result']['verdict'],expected)
 def test_judge_map(self):
  self.h.configure(self.s,'judge','J-MAP(J-FAIL-90, J-PASS-60, J-PASS-90)')
  for text,verdict,confidence in [('One','fail',.9),('Two','pass',.6),('Three','pass',.9)]:
   x=self.h.invoke(self.s,'judge',{'response':text})['result'];self.assertEqual((x['verdict'],x['confidence']),(verdict,confidence))
 def test_phase_setup_excluded(self):
  self.h.invoke(self.s,'judge',{},phase='setup');self.h.close_observation(self.s)
  self.assertEqual(self.h.negative_assertion(self.s,'judge',0)['outcome'],'PASS')
 def test_negative_not_pass_before_closure(self):self.assertEqual(self.h.negative_assertion(self.s,'judge')['outcome'],'NOT_RUN')
 def test_close_requires_terminal(self):
  with self.assertRaises(ValueError):self.h.close_observation(self.s,terminal_observed=False)
 def test_closed_call_is_not_silently_discarded(self):
  self.h.close_observation(self.s)
  with self.assertRaises(RuntimeError):self.h.invoke(self.s,'judge',{})
  self.assertEqual(self.h.negative_assertion(self.s,'judge')['outcome'],'FAIL')
 def test_count_after_close(self):
  self.h.invoke(self.s,'judge',{});self.h.close_observation(self.s)
  self.assertEqual(self.h.negative_assertion(self.s,'judge',1)['outcome'],'PASS')
  self.assertEqual(self.h.negative_assertion(self.s,'judge',0)['outcome'],'FAIL')
 def test_monotonic_events(self):
  self.h.invoke(self.s,'subject',{});es=self.h.read_log(self.s)
  self.assertEqual([x['sequence'] for x in es],list(range(1,len(es)+1)))
  self.assertTrue(all(x['clock_id']==self.h.clock_id for x in es))
 def test_parallel_isolation(self):
  b=self.h.begin('session-b');self.h.configure(self.s,'judge','J-FAIL-90');self.h.configure(b,'judge','J-PASS-60')
  def call(s):return [self.h.invoke(s,'judge',{})['result'] for _ in range(20)]
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:aa,bb=list(ex.map(call,(self.s,b)))
  self.assertTrue(all(x['verdict']=='fail' for x in aa));self.assertTrue(all(x['confidence']==.6 for x in bb))
  self.assertEqual(self.h.session(self.s).counters[('judge','cts-scripted-judge@1')],20)
  self.assertEqual(self.h.session(b).counters[('judge','cts-scripted-judge@1')],20)
  self.h.reset(self.s);self.assertEqual(len(self.h.read_log(b)),41)
 def test_switch_preserves_counters(self):
  self.h.invoke(self.s,'judge',{});self.h.configure(self.s,'judge','J-FAIL-90',applies='next_call')
  x=self.h.invoke(self.s,'judge',{});self.assertEqual(x['call_no'],2);self.assertEqual(x['result']['verdict'],'fail')
 def test_endpoint_counter_scope(self):
  self.h.invoke(self.s,'judge',{},endpoint_id='j-1');self.h.invoke(self.s,'judge',{},endpoint_id='j-2')
  self.assertEqual(self.h.session(self.s).counters[('judge','j-1')],1)
  self.assertEqual(self.h.session(self.s).counters[('judge','j-2')],1)
 def test_invalid_behavior_rejected(self):
  with self.assertRaises(ValueError):self.h.configure(self.s,'judge','J-UNKNOWN')
 def test_repeated_reset_restores_first_call(self):
  for i in range(3):
   self.h.configure(self.s,'judge','J-DOWN-THEN-PASS-90');self.assertEqual(self.h.invoke(self.s,'judge',{})['outcome'],'unreachable');self.h.reset(self.s)

if __name__=='__main__':unittest.main(verbosity=2)
