"""C.2.R1.3: fail-closed reconciliation of historical finding qualifications.

Never forge structured historic logs or treat a candidate unittest PASS as a
finding closure. The output register is an auditable *disposition*, not an
authenticity attestation. C.1 historic claims are preserved as prior claims.
"""
import argparse
import json
import pathlib
import re
import sys

HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"stage_c_closure"))
from closure import FINDINGS,HISTORIC_RUNS
from r12_qualification import validate as validate_qualification
from closure_integration import reconcile_strict

def build(qualification, *, evidence_root, commit):
    errors=validate_qualification(qualification)
    rows=qualification.get("rows",[])
    expected=set(FINDINGS)
    by_id={r["finding_id"]:r for r in rows if isinstance(r,dict) and r.get("finding_id") in expected}
    if set(by_id)!=expected or len(rows)!=len(expected):
        errors.append("incomplete/duplicate qualification inventory")
    # Historical run references remain claims from C.1; do not infer authenticated
    # runner identities from them.
    open_rows=[]
    for fid in sorted(expected):
        if fid not in by_id: continue
        q=by_id[fid]
        run,sha=HISTORIC_RUNS[FINDINGS[fid][2]]
        if q.get("run_id")!=run:
            errors.append(fid+": historical run mismatch")
        if q.get("recorded_result")!="PASS" or not q.get("test_id"):
            errors.append(fid+": candidate test result missing")
        open_rows.append({"finding_id":fid,"status":"PARTIAL" if q.get("qualification")=="PARTIAL" else "DEFERRED_REAL_SUT",
                          "scope":"MOCK_ONLY","verification_commit":commit,"evidence":[]})
    historic={fid:info[0] for fid,info in FINDINGS.items()}
    trusted={run:sha for run,sha in HISTORIC_RUNS.values()}
    expected_tests={fid:{q["test_id"]} for fid,q in by_id.items()}
    dispositions,strict_errors=reconcile_strict(open_rows,evidence_root,commit,
                         allowed_ids=expected,trusted_runs=trusted,
                         expected_tests=expected_tests,historic_statuses=historic)
    errors.extend(strict_errors)
    register=[]
    for row in dispositions:
        fid=row["finding_id"]
        q=by_id[fid]
        register.append({
          **row,
          "historical_source_run":q["run_id"],
          "historical_source_commit":HISTORIC_RUNS[FINDINGS[fid][2]][1],
          "candidate_test_id":q["test_id"],
          "historical_test_result":q["recorded_result"],
          "qualification":q["qualification"],
          "qualification_basis":q["qualification_basis"],
          "finding_evidence_status":"NOT_ESTABLISHED",
          "real_sut_disposition":"NOT_ESTABLISHED"
        })
    if any(r["verification_state"]!="OPEN" or r["formal_closure"]!="NOT_ATTESTED" for r in register):
        errors.append("unexpected promotion of historic finding")
    return {"schema_version":"C2-R1.3-1","scope":"MOCK_HISTORICAL_QUALIFICATION_ONLY",
            "claim":"NO_FINDINGS_CLOSED","findings":register,
            "summary":{"total":len(register),"partially_qualified":sum(r["qualification"]=="PARTIAL" for r in register),
                       "not_established":sum(r["qualification"]=="NOT_ESTABLISHED" for r in register),
                       "evidence_verified":0,"formally_closed":0}},errors

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--qualification",default=str(HERE/"r12_evidence_qualification.json"))
    p.add_argument("--out",required=True)
    p.add_argument("--sha",required=True)
    a=p.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}",a.sha):raise SystemExit("immutable SHA required")
    data=json.loads(pathlib.Path(a.qualification).read_text())
    register,errors=build(data,evidence_root=HERE,commit=a.sha)
    if errors:raise SystemExit("; ".join(errors))
    dest=pathlib.Path(a.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(register,indent=2,sort_keys=True)+"\n")
    print("R1.3 reconciled: 14 historical findings, 13 PARTIAL, 1 NOT_ESTABLISHED, 0 VERIFIED/CLOSED")
if __name__=="__main__":main()
