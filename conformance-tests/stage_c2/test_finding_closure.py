import copy,hashlib,pathlib,tempfile,unittest
from finding_closure import check

SHA="a"*40
SOURCE="b"*40
RUN="39718787849"
class FindingClosureTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name)
  (self.root/"execution.log").write_text("test_example ... ok\\n")
  self.row={"finding_id":"S2-F02","status":"MOCK_VERIFIED","scope":"MOCK_ONLY",
   "verification_commit":SHA,"reviewer":"reviewer-a","reviewed_at":"2026-10-22T00:00:00Z",
   "attestation_status":"PENDING_EXTERNAL_ATTESTATION",
   "evidence":[{"path":"execution.log","sha256":hashlib.sha256((self.root/"execution.log").read_bytes()).hexdigest(),
    "source_run":RUN,"source_commit":SOURCE,"test_id":"test_example"}]}
 def result(self, rows=None):
  return check([self.row] if rows is None else rows,self.root,SHA,allowed_ids={"S2-F02"},trusted_runs={RUN:SOURCE})
 def test_valid_scoped_closure_metadata(self):self.assertEqual(self.result(),[])
 def test_missing_evidence_rejected(self):
  self.row["evidence"]=[];self.assertTrue(self.result())
 def test_missing_reviewer_rejected(self):
  self.row.pop("reviewer");self.assertTrue(self.result())
 def test_untrusted_run_rejected(self):
  self.row["evidence"][0]["source_run"]="unknown";self.assertTrue(self.result())
 def test_wrong_sha_rejected(self):
  self.row["evidence"][0]["sha256"]="0"*64;self.assertTrue(self.result())
 def test_wrong_commit_rejected(self):
  self.row["verification_commit"]="c"*40;self.assertTrue(self.result())
 def test_real_sut_claim_rejected(self):
  self.row["scope"]="REAL_SUT";self.assertTrue(self.result())
 def test_false_attestation_rejected(self):
  self.row["attestation_status"]="SIGNED";self.assertTrue(self.result())
 def test_inventory_missing_rejected(self):
  self.assertTrue(self.result([]))
 def test_duplicate_finding_rejected(self):
  self.assertTrue(self.result([self.row,self.row]))
 def test_traversal_rejected(self):
  self.row["evidence"][0]["path"]="../execution.log";self.assertTrue(self.result())
 def test_partial_without_evidence_allowed(self):
  self.row.update(status="PARTIAL",evidence=[]);self.assertEqual(self.result(),[])
if __name__=="__main__":unittest.main()
