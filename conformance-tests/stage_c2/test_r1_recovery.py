import copy,json,pathlib,unittest
from r1_recovery import recover,validate_inventory
HERE=pathlib.Path(__file__).resolve().parent
class RecoveryTests(unittest.TestCase):
 def setUp(self):
  self.source=json.loads((HERE.parent/"s35_attribution"/"audit_register.json").read_text())
  self.matrix=recover(self.source)
 def test_inventory_exact(self):
  self.assertEqual(len(self.matrix["findings"]),14)
  self.assertEqual(validate_inventory(self.matrix),[])
 def test_missing_legacy_fails(self):
  with self.assertRaises(ValueError):recover(self.source[:-1])
 def test_no_false_closures(self):
  self.assertTrue(all(f["finding_evidence_status"]=="NOT_ESTABLISHED" for f in self.matrix["findings"]))
 def test_source_mutation_rejected(self):
  self.matrix["findings"][0]["source_commit"]="a"*40
  self.assertTrue(validate_inventory(self.matrix))
 def test_fabricated_mapping_rejected(self):
  self.matrix["findings"][0]["candidate_test_ids"]=["test_example"]
  self.assertTrue(validate_inventory(self.matrix))
 def test_fabricated_verified_rejected(self):
  self.matrix["findings"][0]["finding_evidence_status"]="EVIDENCE_VERIFIED"
  self.assertTrue(validate_inventory(self.matrix))
if __name__=="__main__":unittest.main()
