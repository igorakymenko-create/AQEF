"""C.2.R1 recovery inventory: never promote historical CI success to finding closure."""
import json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"stage_c_closure"))
from closure import FINDINGS,HISTORIC_RUNS

def recover(source_audit):
    legacy={item["id"]:item for item in source_audit}
    expected={key for key in FINDINGS if key.startswith(("S2","S3","Q-"))}
    if set(legacy)!=expected:raise ValueError("historical legacy inventory mismatch")
    records=[]
    for fid,(claimed,basis,slice_name) in FINDINGS.items():
        rid,sha=HISTORIC_RUNS[slice_name]
        records.append({
            "finding_id":fid,"legacy_status":legacy.get(fid,{}).get("status"),
            "c1_claimed_status":claimed,"source_slice":slice_name,
            "source_run_id":rid,"source_commit":sha,
            "source_run_url":f"https://github.com/igorakymenko-create/AQEF/actions/runs/{rid}",
            "source_job_log_observed":"AVAILABLE_IN_GITHUB_ACTIONS",
            "source_job_status":"SUCCESS",
            "candidate_test_ids":[],
            "finding_to_test_mapping":"NOT_ESTABLISHED",
            "execution_provenance":"CI_RUN_METADATA_ONLY",
            "finding_evidence_status":"NOT_ESTABLISHED",
            "real_sut_disposition":"NOT_ESTABLISHED",
            "recovery_note":"A successful workflow and test log do not prove this individual finding. Requires explicit mapping, preserved test record and independent evidence checks."
        })
    return {"schema_version":"C2-R1-1","scope":"HISTORICAL_MOCK_RECOVERY_ONLY",
            "claim":"NO_FINDINGS_CLOSED_BY_THIS_INVENTORY",
            "findings":records}

def validate_inventory(doc):
    errors=[]
    if doc.get("scope")!="HISTORICAL_MOCK_RECOVERY_ONLY":errors.append("scope mismatch")
    rows=doc.get("findings",[])
    if not isinstance(rows,list):return errors+["invalid findings"]
    ids=[r.get("finding_id") for r in rows if isinstance(r,dict)]
    if len(ids)!=len(FINDINGS) or set(ids)!=set(FINDINGS):errors.append("finding inventory mismatch")
    for row in rows:
        if not isinstance(row,dict):errors.append("invalid row");continue
        fid=row.get("finding_id")
        if fid not in FINDINGS:continue
        want=HISTORIC_RUNS[FINDINGS[fid][2]]
        if row.get("source_run_id")!=want[0] or row.get("source_commit")!=want[1]:
            errors.append(f"{fid}: source identity mismatch")
        if row.get("finding_evidence_status")=="EVIDENCE_VERIFIED":
            errors.append(f"{fid}: evidence promotion without independently checked execution")
        if row.get("finding_to_test_mapping")!="NOT_ESTABLISHED" or row.get("candidate_test_ids")!=[]:
            errors.append(f"{fid}: mapping is not yet proven")
    return errors

if __name__=="__main__":
    source=json.loads((HERE.parent/"s35_attribution"/"audit_register.json").read_text())
    document=recover(source)
    errors=validate_inventory(document)
    if errors:raise SystemExit("; ".join(errors))
    (HERE/"r1_recovery_matrix.json").write_text(json.dumps(document,indent=2)+"\n")
    print("R1 historical inventory: 14 findings, 0 evidence-verified, no real SUT claims")
