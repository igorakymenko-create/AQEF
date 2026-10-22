import copy,hashlib,json,pathlib,tempfile,unittest
from closure_integration import reconcile_strict
SHA="a"*40
SOURCE="b"*40
RUN="39718787849"
class StrictClosureTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name)
  self.log={"source_run":RUN,"source_commit":SOURCE,
            "tests":[{"test_id":"test_pipeline","outcome":"PASS","finding_ids":["S2-F02"]}]}
  self.write()
  self.row={"finding_id":"S2-F02","status":"MOCK_VERIFIED","scope":"MOCK_ONLY",
            "verification_commit":SHA,"reviewer":"reviewer-a","reviewed_at":"2026-10-22T00:00:00Z",
            "attestation_status":"PENDING_EXTERNAL_ATTESTATION","evidence":[self.ev()]}
 def write(self):
  (self.root/"execution.json").write_text(json.dumps(self.log))
 def ev(self):
  return {"path":"execution.json","sha256":hashlib.sha256((self.root/"execution.json").read_bytes()).hexdigest(),
          "source_run":RUN,"source_commit":SOURCE,"test_id":"test_pipeline"}
 def runcheck(self):
  return reconcile_strict([self.row],self.root,SHA,allowed_ids={"S2-F02"},
                          trusted_runs={RUN:SOURCE},expected_tests={"S2-F02":{"test_pipeline"}},
                          historic_statuses={"S2-F02":"MOCK_CLOSED_PENDING_CI"})
 def test_verified_not_formally_closed(self):
  rows,errors=self.runcheck()
  self.assertEqual(errors,[]);self.assertEqual(rows[0]["verification_state"],"EVIDENCE_VERIFIED")
  self.assertEqual(rows[0]["formal_closure"],"NOT_ATTESTED")
 def test_failed_test_rejected(self):
  self.log["tests"][0]["outcome"]="FAIL";self.write();self.row["evidence"]=[self.ev()]
  self.assertTrue(self.runcheck()[1])
 def test_skipped_test_rejected(self):
  self.log["tests"][0]["outcome"]="SKIPPED";self.write();self.row["evidence"]=[self.ev()]
  self.assertTrue(self.runcheck()[1])
 def test_unmapped_test_rejected(self):
  self.row["evidence"][0]["test_id"]="another"
  self.assertTrue(self.runcheck()[1])
 def test_untrusted_run_rejected(self):
  self.log["source_run"]="other";self.write();self.row["evidence"]=[self.ev()]
  self.assertTrue(self.runcheck()[1])
 def test_duplicate_test_rejected(self):
  self.log["tests"].append(copy.deepcopy(self.log["tests"][0]));self.write();self.row["evidence"]=[self.ev()]
  self.assertTrue(self.runcheck()[1])
 def test_missing_finding_claim_rejected(self):
  self.log["tests"][0]["finding_ids"]=[];self.write();self.row["evidence"]=[self.ev()]
  self.assertTrue(self.runcheck()[1])
 def test_tamper_rejected(self):
  (self.root/"execution.json").write_text("{}")
  self.assertTrue(self.runcheck()[1])
 def test_partial_preserved(self):
  self.row.update(status="PARTIAL",evidence=[])
  rows,errors=self.runcheck();self.assertEqual(errors,[])
  self.assertEqual(rows[0]["verification_state"],"OPEN")
 def test_missing_baseline_rejected(self):
  self.assertTrue(reconcile_strict([self.row],self.root,SHA,allowed_ids={"S2-F02"},
    trusted_runs={RUN:SOURCE},expected_tests={"S2-F02":{"test_pipeline"}},historic_statuses={})[1])
if __name__=="__main__":unittest.main()
