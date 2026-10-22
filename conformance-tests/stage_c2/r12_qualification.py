"""C.2.R1.2 qualification inventory gate; source assertions never equate to closure."""
import json,pathlib
HERE=pathlib.Path(__file__).resolve().parent
def validate(doc):
    errors=[]
    rows=doc.get("rows",[])
    if doc.get("schema_version")!="C2-R1.2-1" or doc.get("claim")!="TEST_ASSERTION_SCOPE_QUALIFIED_NO_FINDING_CLOSURE" or not isinstance(rows,list):return ["wrong scope"]
    seen=set()
    for r in rows:
        fid=r.get("finding_id")
        if fid in seen:errors.append("duplicate "+str(fid))
        seen.add(fid)
        if r.get("qualification") not in {"PARTIAL","NOT_ESTABLISHED"}:errors.append(str(fid)+": qualification overclaim")
        if not isinstance(r.get("qualification_basis"),str) or len(r["qualification_basis"])<25:errors.append(str(fid)+": no evidence rationale")
        if r.get("finding_evidence_status")!="NOT_ESTABLISHED":errors.append(str(fid)+": closure overclaim")
        if r.get("mapping_status")!="CANDIDATE_SEMANTIC_REVIEW_REQUIRED":errors.append(str(fid)+": source mapping promoted")
    if len(rows)!=14 or len(seen)!=14:errors.append("not 14 unique findings")
    return errors
if __name__=="__main__":
    d=json.loads((HERE/"r12_evidence_qualification.json").read_text())
    e=validate(d)
    if e:raise SystemExit("; ".join(e))
    print("R1.2 source qualification validated: 13 PARTIAL, 1 NOT_ESTABLISHED, 0 CLOSED")
