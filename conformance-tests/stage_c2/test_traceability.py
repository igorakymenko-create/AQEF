import copy
import hashlib
import pathlib
import tempfile
import unittest
from traceability import verify

COMMIT = "a" * 40

class TraceabilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        data = b"observed response"
        (self.root / "obs.json").write_bytes(data)
        self.entry = {"schema_version": "C2-1", "cts_commit": COMMIT, "scope": "MOCK_ONLY", "executions": [{
            "case_id": "CT-001-C01", "execution_id": "run-001", "cts_commit": COMMIT,
            "scope": "MOCK_ONLY", "source_kind": "MOCK_OBSERVATION", "outcome": "PASS",
            "assertions": [{"expected": "ok", "observed": "ok", "result": "PASS"}],
            "evidence": [{"path": "obs.json", "sha256": hashlib.sha256(data).hexdigest()}]
        }]}

    def validate(self, x=None):
        return verify(self.entry if x is None else x, self.root, COMMIT)

    def test_valid_mock_execution(self):
        self.assertEqual(self.validate(), [])
    def test_tampering_rejected(self):
        (self.root / "obs.json").write_text("tampered")
        self.assertTrue(self.validate())
    def test_untrusted_scope_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0]["source_kind"] = "REAL_SUT_OBSERVATION"
        self.assertTrue(self.validate(x))
    def test_missing_case_link_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0].pop("case_id")
        self.assertTrue(self.validate(x))
    def test_false_pass_without_evidence_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0]["evidence"] = []
        self.assertTrue(self.validate(x))
    def test_failed_assertion_with_pass_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0]["assertions"][0]["result"] = "FAIL"
        self.assertTrue(self.validate(x))
    def test_duplicate_execution_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"].append(copy.deepcopy(x["executions"][0]))
        self.assertTrue(self.validate(x))
    def test_path_traversal_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0]["evidence"][0]["path"] = "../outside.json"
        self.assertTrue(self.validate(x))
    def test_not_run_with_evidence_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0]["outcome"] = "NOT_RUN"
        self.assertTrue(self.validate(x))
    def test_sha_mismatch_rejected(self):
        x = copy.deepcopy(self.entry)
        x["executions"][0]["cts_commit"] = "b" * 40
        self.assertTrue(self.validate(x))

if __name__ == "__main__":
    unittest.main()
