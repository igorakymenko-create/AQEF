"""C.2.2 bridge from immutable normative CTS inventory to case-level execution evidence.

This module validates identity, provenance, and report consistency. It does NOT
interpret free-text normative expected assertions, authenticate a runner, or
establish real-SUT conformance.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "harness" / "tools"))
import validate as normative
from traceability import verify as verify_evidence

def check_binding(ledger, report, manifest, evidence_root, commit, *, inventory=None):
    errors = verify_evidence(ledger, evidence_root, commit)
    inv = inventory if inventory is not None else normative.load_inventory()
    errors += ["report: " + e for e in normative.check_report(report, inv, manifest, evidence_root)]
    owner = normative.all_cases(inv)
    if report.get("provenance", {}).get("cts_commit") != commit:
        errors.append("report commit mismatch")
    if ledger.get("scope") == "MOCK_ONLY" and report.get("provenance", {}).get("sut_name") != "Stage-C-Mock-Only":
        errors.append("mock ledger cannot claim real SUT")
    if ledger.get("scope") == "REAL_SUT":
        errors.append("real SUT origin not attested by C.2.2; fail closed")
    if not isinstance(ledger.get("executions"), list):
        return errors
    report_cases = {row["case_id"]:row for row in report.get("cases", []) if isinstance(row, dict) and "case_id" in row}
    planned = {case for tid in report.get("plan", {}).get("test_ids", [])
               if tid in inv["tests"] for case in inv["tests"][tid]["cases"]}
    observed = {}
    for entry in ledger["executions"]:
        if not isinstance(entry, dict):
            continue
        cid = entry.get("case_id")
        if cid not in owner:
            errors.append("unknown normative case: " + str(cid))
            continue
        if cid not in planned:
            errors.append("execution outside report plan: " + cid)
        if entry.get("test_id") != owner[cid]:
            errors.append("incorrect normative test owner: " + cid)
        if entry.get("cts_revision") != inv["revision"]:
            errors.append("CTS revision mismatch: " + cid)
        if cid in observed:
            errors.append("ambiguous multiple executions for case: " + cid)
        observed[cid] = entry
        assertions = entry.get("assertions", [])
        if isinstance(assertions, list):
            ids = [a.get("predicate_id") for a in assertions if isinstance(a, dict)]
            if entry.get("outcome") in ("PASS", "FAIL") and (len(ids) != len(assertions) or not ids or any(not isinstance(a, str) or not a for a in ids)):
                errors.append("missing predicate identity: " + cid)
            if len(set(ids)) != len(ids):
                errors.append("duplicate predicate identity: " + cid)
            for a in assertions:
                if not isinstance(a, dict):
                    continue
                if a.get("normative_case") != cid:
                    errors.append("predicate not bound to normative case: " + cid)
                if a.get("source_ref") != cid:
                    errors.append("predicate source is not canonical case ref: " + cid)
        row = report_cases.get(cid)
        if row is None:
            errors.append("executed case absent from report: " + cid)
        elif row.get("outcome") != entry.get("outcome"):
            errors.append("execution/report outcome disagreement: " + cid)
        # A report PASS/FAIL must have evidence in the native CTS manifest too.
        if row and row.get("outcome") in ("PASS","FAIL") and not row.get("evidence_refs"):
            errors.append("report verdict lacks native evidence refs: " + cid)
    for cid in sorted(planned):
        row = report_cases.get(cid)
        if row and row.get("outcome") in ("PASS","FAIL") and cid not in observed:
            errors.append("report verdict has no execution record: " + cid)
        if row and row.get("outcome") == "NOT_RUN" and cid in observed and observed[cid].get("outcome") != "NOT_RUN":
            errors.append("unreported execution: " + cid)
    return errors
