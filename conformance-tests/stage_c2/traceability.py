"""C.2 normative case-level execution traceability verifier.

No claim of SUT conformance is inferred from mock/unit-test success.
All file paths are relative to the provided evidence root.
"""
import argparse
import hashlib
import json
import pathlib
import re

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
OUTCOMES = {"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_path(root, name):
    if not isinstance(name, str) or not name:
        return None
    root = root.resolve()
    candidate = (root / name).resolve()
    if root not in candidate.parents or not candidate.is_file():
        return None
    return candidate

def verify(ledger, evidence_root, expected_commit):
    errors = []
    root = pathlib.Path(evidence_root)
    if not isinstance(expected_commit, str) or not COMMIT_RE.fullmatch(expected_commit):
        errors.append("invalid expected commit")
    if ledger.get("schema_version") != "C2-1":
        errors.append("invalid schema version")
    if ledger.get("cts_commit") != expected_commit:
        errors.append("immutable commit mismatch")
    if ledger.get("scope") not in {"MOCK_ONLY", "REAL_SUT"}:
        errors.append("invalid execution scope")
    records = ledger.get("executions")
    if not isinstance(records, list):
        return errors + ["executions must be list"]
    keys = set()
    for n, row in enumerate(records):
        prefix = "execution[%d]: " % n
        if not isinstance(row, dict):
            errors.append(prefix + "invalid record")
            continue
        case_id, run_id = row.get("case_id"), row.get("execution_id")
        if not isinstance(case_id, str) or not case_id or not isinstance(run_id, str) or not run_id:
            errors.append(prefix + "missing case or execution id")
        elif (case_id, run_id) in keys:
            errors.append(prefix + "duplicate case/execution pair")
        else:
            keys.add((case_id, run_id))
        outcome, scope = row.get("outcome"), row.get("scope")
        if outcome not in OUTCOMES:
            errors.append(prefix + "invalid outcome")
            continue
        if scope != ledger.get("scope"):
            errors.append(prefix + "execution scope mismatch")
        if row.get("cts_commit") != expected_commit:
            errors.append(prefix + "record commit mismatch")
        if row.get("source_kind") not in {"MOCK_OBSERVATION", "REAL_SUT_OBSERVATION", "NONE"}:
            errors.append(prefix + "invalid source kind")
        if scope == "MOCK_ONLY" and row.get("source_kind") == "REAL_SUT_OBSERVATION":
            errors.append(prefix + "mock marked as real evidence")
        if outcome == "PASS" and row.get("source_kind") == "NONE":
            errors.append(prefix + "PASS without observation")
        if outcome == "PASS" and not row.get("assertions"):
            errors.append(prefix + "PASS without assertions")
        assertions = row.get("assertions", [])
        if not isinstance(assertions, list):
            errors.append(prefix + "invalid assertions")
            continue
        if outcome == "PASS" and any(a.get("result") != "PASS" for a in assertions if isinstance(a, dict)):
            errors.append(prefix + "PASS with unsuccessful assertion")
        for a in assertions:
            if not isinstance(a, dict) or not a.get("expected") or not a.get("observed") or a.get("result") not in {"PASS", "FAIL"}:
                errors.append(prefix + "invalid assertion")
        evidence = row.get("evidence", [])
        if not isinstance(evidence, list):
            errors.append(prefix + "evidence must be list")
            continue
        if outcome in {"PASS", "FAIL"} and not evidence:
            errors.append(prefix + "verdict without evidence")
        if outcome == "NOT_RUN" and (assertions or evidence):
            errors.append(prefix + "NOT_RUN must not claim observations")
        seen_paths = set()
        for entry in evidence:
            if not isinstance(entry, dict):
                errors.append(prefix + "invalid evidence entry")
                continue
            name, digest = entry.get("path"), entry.get("sha256")
            if name in seen_paths:
                errors.append(prefix + "duplicate evidence path")
            seen_paths.add(name)
            file = check_path(root, name)
            if file is None or not isinstance(digest, str) or not SHA_RE.fullmatch(digest):
                errors.append(prefix + "missing/unsafe/unhashed evidence")
            elif sha256(file) != digest:
                errors.append(prefix + "evidence hash mismatch")
    return errors

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ledger", required=True)
    p.add_argument("--evidence-root", required=True)
    p.add_argument("--sha", required=True)
    a = p.parse_args()
    result = verify(json.loads(pathlib.Path(a.ledger).read_text()), a.evidence_root, a.sha)
    if result:
        raise SystemExit("\n".join(result))
    print("C2 TRACEABILITY VERIFIED (record scope only; no inferred SUT conformance)")

if __name__ == "__main__":
    main()
