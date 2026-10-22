import copy,hashlib,pathlib,tempfile,unittest
from regression_accounting import count_log,verify_regression

def log(results, summary=None):
 text="".join(f"test_{i} (Suite.test_{i}) ... {result}\n" for i,result in enumerate(results))
 n=len(results)
 return text+f"\n----------------------------------------------------------------------\nRan {n} tests in 0.001s\n\n"+(summary if summary is not None else "OK")+"\n"

class AccountingTests(unittest.TestCase):
 def test_three_passes(self):
  c,e=count_log(log(["ok"]*3),exit_code=0)
  self.assertEqual(e,[]);self.assertEqual((c["executed"],c["passed"],c["skipped"]),(3,3,0))
 def test_one_skipped_fails_default(self):
  _,e=count_log(log(["ok","skipped 'reason'"],"OK (skipped=1)"),exit_code=0)
  self.assertIn("skip policy exceeded",e)
 def test_explicit_skip_allowance(self):
  c,e=count_log(log(["ok","skipped 'reason'"],"OK (skipped=1)"),exit_code=0,allowed_skips=1)
  self.assertEqual(e,[]);self.assertEqual(c["executed"],1)
 def test_forged_summary_rejected(self):
  _,e=count_log(log(["ok","skipped 'reason'"],"OK"),exit_code=0,allowed_skips=1)
  self.assertTrue(e)
 def test_failed_test_detected(self):
  _,e=count_log(log(["FAIL"],"FAILED (failures=1)"),exit_code=1)
  self.assertEqual(e,[])
 def test_error_and_exit_zero_rejected(self):
  _,e=count_log(log(["ERROR"],"OK"),exit_code=0)
  self.assertTrue(e)
 def test_missing_verbose_record_rejected(self):
  _,e=count_log("Ran 1 test in 0.01s\n\nOK\n",exit_code=0)
  self.assertTrue(e)
 def test_expected_failure_rejected(self):
  _,e=count_log(log(["expected failure"]),exit_code=0)
  self.assertTrue(e)
 def test_negative_skip_allowance_rejected(self):
  _,e=count_log(log(["ok"]),exit_code=0,allowed_skips=-1)
  self.assertTrue(e)
 def test_regression_integrity(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d);data=log(["ok","ok"]).encode();(p/"suite.log").write_bytes(data)
   reg={"scope":"UNIT_TESTS_NOT_SUT_CONFORMANCE","suites":[{"suite":"suite","tests":2,"exit_code":0,"sha256":hashlib.sha256(data).hexdigest()}],"total_tests":2}
   result,errors=verify_regression(reg,p,{"suite":2})
   self.assertEqual(errors,[]);self.assertEqual(result["summary"]["passed"],2)
   (p/"suite.log").write_bytes(data+b"tampered")
   self.assertTrue(verify_regression(reg,p,{"suite":2})[1])
if __name__=="__main__":unittest.main()
