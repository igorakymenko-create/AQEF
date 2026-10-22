import json,pathlib,tempfile,unittest
from r2_bundle import prepare
SHA="a"*40
class BundleTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  p=pathlib.Path(self.temp.name)
  self.out=p/"out";self.reg=p/"finding.json";self.acc=p/"accounting.json"
  self.finding={"schema_version":"C2-R1.3-1","claim":"NO_FINDINGS_CLOSED","summary":{"total":14,"formally_closed":0,"evidence_verified":0}}
  self.counts={"scope":"UNIT_TESTS_NOT_SUT_CONFORMANCE","summary":{"total":423,"passed":423,"executed":423,"skipped":0,"failed":0,"errors":0}}
  self.write()
 def write(self):
  self.reg.write_text(json.dumps(self.finding));self.acc.write_text(json.dumps(self.counts))
 def check(self):return prepare(self.out,SHA,"42",self.reg,self.acc)
 def test_bundle(self):
  m=self.check();self.assertEqual(len(m["files"]),3);self.assertEqual(m["cts_commit"],SHA)
 def test_missing_file(self):
  self.reg.unlink()
  with self.assertRaises(ValueError):self.check()
 def test_false_finding_closure(self):
  self.finding["summary"]["formally_closed"]=1;self.write()
  with self.assertRaises(ValueError):self.check()
 def test_skipped_regression(self):
  self.counts["summary"]["skipped"]=1;self.write()
  with self.assertRaises(ValueError):self.check()
 def test_bad_commit(self):
  with self.assertRaises(ValueError):prepare(self.out,"wrong","42",self.reg,self.acc)
 def test_wrong_scope(self):
  self.counts["scope"]="REAL_SUT";self.write()
  with self.assertRaises(ValueError):self.check()
if __name__=="__main__":unittest.main()
