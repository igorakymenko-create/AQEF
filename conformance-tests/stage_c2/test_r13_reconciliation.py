import copy,json,pathlib,unittest
from r13_reconciliation import build
HERE=pathlib.Path(__file__).resolve().parent
SHA="a"*40
class ReconciliationTests(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((HERE/"r12_evidence_qualification.json").read_text())
 def check(self):return build(self.data,evidence_root=HERE,commit=SHA)
 def test_register_not_closed(self):
  out,err=self.check();self.assertEqual(err,[])
  self.assertEqual(out["summary"],{"total":14,"partially_qualified":13,"not_established":1,"evidence_verified":0,"formally_closed":0})
  self.assertTrue(all(r["verification_state"]=="OPEN" for r in out["findings"]))
 def test_legacy_claim_not_promoted(self):
  out,err=self.check();self.assertEqual(err,[])
  self.assertEqual(next(x for x in out["findings"] if x["finding_id"]=="S2-F02")["historic_status"],"MOCK_VERIFIED")
  self.assertEqual(out["summary"]["formally_closed"],0)
 def test_run_substitution_rejected(self):
  self.data["rows"][0]["run_id"]="999999";self.assertTrue(self.check()[1])
 def test_promoted_qualification_rejected(self):
  self.data["rows"][0]["qualification"]="VERIFIED";self.assertTrue(self.check()[1])
 def test_missing_row_rejected(self):
  self.data["rows"].pop();self.assertTrue(self.check()[1])
 def test_duplicate_row_rejected(self):
  self.data["rows"].append(copy.deepcopy(self.data["rows"][0]));self.assertTrue(self.check()[1])
 def test_candidate_outcome_mutation_rejected(self):
  self.data["rows"][0]["recorded_result"]="FAIL";self.assertTrue(self.check()[1])
if __name__=="__main__":unittest.main()
