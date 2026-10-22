"""C.2.R1.1 candidate mappings are observed tests, NEVER finding closure."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def validate(doc,known):
    errors=[]
    rows=doc.get("rows",[])
    if doc.get("claim")!="CANDIDATE_TEST_PASS_NOT_FINDING_CLOSURE" or not isinstance(rows,list):
        return ["invalid candidate document"]
    seen=set()
    for row in rows:
        fid=row.get("finding_id")
        if fid in seen or fid not in known:errors.append("unknown/duplicate finding")
        seen.add(fid)
        if row.get("recorded_result")!="PASS" or row.get("mapping_status")!="CANDIDATE_SEMANTIC_REVIEW_REQUIRED":
            errors.append(str(fid)+": unobserved or incorrectly promoted mapping")
        if row.get("finding_evidence_status")!="NOT_ESTABLISHED":
            errors.append(str(fid)+": false closure")
        if not isinstance(row.get("test_id"),str) or not row.get("test_id").startswith("test_"):
            errors.append(str(fid)+": invalid test identity")
    if seen!=set(known):errors.append("incomplete inventory")
    return errors
if __name__=="__main__":
    import sys
    sys.path.insert(0,str(HERE.parent/"stage_c_closure"))
    from closure import FINDINGS
    data=json.loads((HERE/"r11_historical_test_candidates.json").read_text())
    errors=validate(data,FINDINGS)
    if errors:raise SystemExit("; ".join(errors))
    print("R1.1 validated: 14 observed candidate test results, 0 finding closures")
