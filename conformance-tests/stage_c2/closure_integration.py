"""C.2.3.5: structured execution-backed finding reconciliation.

Evidence integrity and execution status are checked independently of historical
C.1 labels. This is MOCK evidence verification, not external attestation.
"""
import hashlib
import json
import pathlib
import re
from finding_closure import check as check_finding_metadata

COMMIT = re.compile(r"^[0-9a-f]{40}$")
CLOSED = {"MOCK_VERIFIED", "MOCK_VERIFIED_REAL_DEFERRED", "CLOSED"}

def _safe(root, relative):
    if not isinstance(relative, str) or not relative:
        return None
    base = pathlib.Path(root).resolve()
    path = (base / relative).resolve()
    return path if base in path.parents and path.is_file() else None

def reconcile_strict(findings, root, commit, *, allowed_ids, trusted_runs,
                     expected_tests, historic_statuses):
    """Return (dispositions, errors). Never mutate historical closure records.

    Structured JSON log: {source_run, source_commit, tests:[
      {test_id, outcome: PASS|FAIL|SKIPPED, finding_ids:[...]}]}.
    Verified evidence does not imply formal CLOSED or an authenticated signature.
    """
    errors = check_finding_metadata(findings, root, commit,
                                    allowed_ids=allowed_ids, trusted_runs=trusted_runs)
    results = []
    for row in findings:
        if not isinstance(row, dict) or row.get("finding_id") not in allowed_ids:
            continue
        fid = row["finding_id"]
        status = row.get("status")
        verdict = "OPEN"
        if fid not in historic_statuses:
            errors.append(fid + ": missing historical baseline")
        if status in CLOSED:
            if not isinstance(row.get("evidence"), list) or not row["evidence"]:
                errors.append(fid + ": closed without execution evidence")
            else:
                for e in row["evidence"]:
                    if not isinstance(e, dict):
                        errors.append(fid + ": malformed source evidence")
                        continue
                    path = _safe(root, e.get("path"))
                    if path is None:
                        errors.append(fid + ": missing structured log")
                        continue
                    try:
                        log = json.loads(path.read_text(encoding="utf-8"))
                    except (ValueError, UnicodeError):
                        errors.append(fid + ": invalid structured execution log")
                        continue
                    if not isinstance(log, dict) or not isinstance(log.get("tests"), list):
                        errors.append(fid + ": execution log schema invalid")
                        continue
                    if log.get("source_run") != e.get("source_run") or log.get("source_commit") != e.get("source_commit"):
                        errors.append(fid + ": execution provenance mismatch")
                    expected = expected_tests.get(fid, set())
                    if not expected or e.get("test_id") not in expected:
                        errors.append(fid + ": test is not mapped to finding")
                    matches = [t for t in log["tests"] if isinstance(t, dict) and t.get("test_id") == e.get("test_id")]
                    if len(matches) != 1:
                        errors.append(fid + ": test result missing/duplicated")
                        continue
                    actual = matches[0]
                    if actual.get("outcome") != "PASS":
                        errors.append(fid + ": source test did not PASS")
                    if fid not in actual.get("finding_ids", []):
                        errors.append(fid + ": source test does not attest finding")
                # Only give EVIDENCE_VERIFIED if no errors attributable to this finding.
                if not any(x.startswith(fid + ":") for x in errors):
                    verdict = "EVIDENCE_VERIFIED"
        elif status not in {"PARTIAL", "DEFERRED_REAL_SUT", "OPEN"}:
            errors.append(fid + ": unsupported status transition")
        results.append({"finding_id":fid, "historic_status":historic_statuses.get(fid),
                        "requested_status":status, "verification_state":verdict,
                        "formal_closure":"NOT_ATTESTED", "scope":row.get("scope")})
    if set(historic_statuses) != set(allowed_ids):
        errors.append("historical inventory mismatch")
    return results, errors
