import copy
import hashlib
import pathlib
import tempfile
import unittest
from inventory_binding import check_binding
from traceability import verify
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"s5_reporting"))
import reporting

SHA="a"*40

class BindingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.report,self.manifest=reporting.build(self.root,cts_commit=SHA,claims=("cli","plugins:validator","human_review"))
        self.inv=reporting.v.load_inventory()
        self.ledger={"schema_version":"C2-1","cts_commit":SHA,"scope":"MOCK_ONLY","executions":[]}
        self.cid=self.report["cases"][0]["case_id"]
        self.tid=self.report["cases"][0]["test_id"]
    def check(self):
        return check_binding(self.ledger,self.report,self.manifest,self.root/"evidence",SHA)
    def test_default_not_run_has_no_claim(self):
        self.assertEqual(self.check(),[])
    def test_unknown_case_rejected(self):
        self.ledger["executions"]=[self.record()]
        self.ledger["executions"][0]["case_id"]="CT-FAK-999"
        self.assertTrue(self.check())
    def record(self):
        return {"case_id":self.cid,"test_id":self.tid,"execution_id":"one","cts_commit":SHA,
                "cts_revision":self.inv["revision"],"scope":"MOCK_ONLY",
                "source_kind":"NONE","outcome":"NOT_RUN","assertions":[],"evidence":[]}
    def test_not_run_record_is_acceptable(self):
        self.ledger["executions"]=[self.record()]
        self.assertEqual(self.check(),[])
    def test_mismatched_test_owner_rejected(self):
        self.ledger["executions"]=[self.record()]
        self.ledger["executions"][0]["test_id"]="CT-EXE-999"
        self.assertTrue(self.check())
    def test_wrong_revision_rejected(self):
        self.ledger["executions"]=[self.record()]
        self.ledger["executions"][0]["cts_revision"]="WD0"
        self.assertTrue(self.check())
    def test_duplicate_case_across_execution_ids_rejected(self):
        a=self.record();b=copy.deepcopy(a);b["execution_id"]="two"
        self.ledger["executions"]=[a,b]
        self.assertTrue(self.check())
    def test_unattested_real_sut_rejected(self):
        self.ledger["scope"]="REAL_SUT"
        self.assertTrue(self.check())
    def test_report_false_pass_rejected(self):
        self.report["cases"][0]["outcome"]="PASS"
        self.assertTrue(self.check())
    def test_report_wrong_commit_rejected(self):
        self.report["provenance"]["cts_commit"]="b"*40
        self.assertTrue(self.check())
    def test_unplanned_case_rejected(self):
        self.ledger["executions"]=[self.record()]
        self.ledger["executions"][0]["case_id"]="CT-EXE-999"
        self.assertTrue(self.check())

if __name__=="__main__":
    unittest.main()
