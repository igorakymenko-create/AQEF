"""C.2.3 fail-closed evidence-backed finding dispositions.

Artifact hashes prove integrity, not external provenance or semantic correctness.
C.1 historical statuses are never silently promoted into verified closure.
"""
import hashlib
import pathlib
import re

CLOSED = {"MOCK_VERIFIED", "MOCK_VERIFIED_REAL_DEFERRED", "CLOSED"}
OPEN = {"PARTIAL", "DEFERRED_REAL_SUT", "OPEN"}
COMMIT = re.compile(r"^[0-9a-f]{40}$")
HASH = re.compile(r"^[0-9a-f]{64}$")

def check(findings, evidence_root, expected_commit, *, allowed_ids, trusted_runs=None):
    errors = []
    root = pathlib.Path(evidence_root).resolve()
    trusted_runs = trusted_runs or {}
    if not COMMIT.fullmatch(str(expected_commit)):
        errors.append("invalid immutable commit")
    if not isinstance(findings, list):
        return errors + ["findings must be an array"]
    seen = set()
    for i, finding in enumerate(findings):
        p = f"finding[{i}]"
        if not isinstance(finding, dict):
            errors.append(p + ": invalid record")
            continue
        fid = finding.get("finding_id")
        if not isinstance(fid, str) or fid not in allowed_ids:
            errors.append(p + ": unknown finding")
            continue
        if fid in seen:
            errors.append(p + ": duplicate finding")
        seen.add(fid)
        status = finding.get("status")
        if status not in CLOSED | OPEN:
            errors.append(fid + ": invalid status")
            continue
        if finding.get("verification_commit") != expected_commit:
            errors.append(fid + ": wrong commit")
        if finding.get("scope") not in {"MOCK_ONLY", "REAL_SUT"}:
            errors.append(fid + ": invalid scope")
        evidence = finding.get("evidence", [])
        if not isinstance(evidence, list):
            errors.append(fid + ": evidence must be list")
            continue
        if status in CLOSED:
            if finding.get("scope") == "REAL_SUT":
                errors.append(fid + ": real SUT closure not authenticated")
            if not evidence:
                errors.append(fid + ": closure without evidence")
            if not finding.get("reviewer") or not finding.get("reviewed_at"):
                errors.append(fid + ": missing reviewer sign-off metadata")
            # Review metadata isn't independently authenticated until C.2.4.
            if finding.get("attestation_status") != "PENDING_EXTERNAL_ATTESTATION":
                errors.append(fid + ": unsupported attestation claim")
        seen_sources = set()
        for obj in evidence:
            if not isinstance(obj, dict):
                errors.append(fid + ": invalid evidence item")
                continue
            path, checksum = obj.get("path"), obj.get("sha256")
            if not isinstance(path, str) or not path:
                errors.append(fid + ": missing evidence path")
                continue
            target = (root / path).resolve()
            if root not in target.parents or not target.is_file() or not isinstance(checksum, str) or not HASH.fullmatch(checksum):
                errors.append(fid + ": unsafe/missing/unhashed evidence")
            elif hashlib.sha256(target.read_bytes()).hexdigest() != checksum:
                errors.append(fid + ": evidence digest mismatch")
            run, sha, test = obj.get("source_run"), obj.get("source_commit"), obj.get("test_id")
            if not all(isinstance(x, str) and x for x in (run, sha, test)):
                errors.append(fid + ": missing source run/commit/test")
            elif trusted_runs.get(run) != sha or not COMMIT.fullmatch(sha):
                errors.append(fid + ": untrusted source run/commit")
            key = (run, test, path)
            if key in seen_sources:
                errors.append(fid + ": duplicate source evidence")
            seen_sources.add(key)
    if seen != set(allowed_ids):
        errors.append("finding inventory mismatch: " + str(sorted(set(allowed_ids)-seen)))
    return errors
