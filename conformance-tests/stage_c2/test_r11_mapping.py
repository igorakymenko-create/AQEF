import copy,json,pathlib,unittest
from r11_mapping import validate
HERE=pathlib.Path(__file__).resolve().parent
class CandidateMappingTests(unittest.TestCase):
 def setUp(self):
  self.data=json.loads((HERE/"r11_historical_test_candidates.json").read_text())
  self.ids={r["finding_id"] for r in self.data["rows"]}
 def test_candidates_valid(self):self.assertEqual(validate(self.data,self.ids),[])
 def test_promoted_finding_rejected(self):
  self.data["rows"][0]["finding_evidence_status"]="EVIDENCE_VERIFIED"
  self.assertTrue(validate(self.data,self.ids))
 def test_missing_finding_rejected(self):
  self.data["rows"].pop()
  self.assertTrue(validate(self.data,self.ids))
 def test_unobserved_test_rejected(self):
  self.data["rows"][0]["recorded_result"]="NOT_OBSERVED"
  self.assertTrue(validate(self.data,self.ids))
if __name__=="__main__":unittest.main()
