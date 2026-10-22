import copy,json,pathlib,unittest
from r12_qualification import validate
HERE=pathlib.Path(__file__).resolve().parent
class QualificationTests(unittest.TestCase):
 def setUp(self):self.data=json.loads((HERE/"r12_evidence_qualification.json").read_text())
 def test_valid(self):self.assertEqual(validate(self.data),[])
 def test_false_verified_rejected(self):
  self.data["rows"][0]["qualification"]="VERIFIED";self.assertTrue(validate(self.data))
 def test_false_closure_rejected(self):
  self.data["rows"][0]["finding_evidence_status"]="EVIDENCE_VERIFIED";self.assertTrue(validate(self.data))
 def test_missing_rationale_rejected(self):
  self.data["rows"][0]["qualification_basis"]="";self.assertTrue(validate(self.data))
 def test_duplicate_rejected(self):
  self.data["rows"][0]["finding_id"]=self.data["rows"][1]["finding_id"];self.assertTrue(validate(self.data))
if __name__=="__main__":unittest.main()
