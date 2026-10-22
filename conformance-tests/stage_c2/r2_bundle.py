"""C.2.R2: prepare an immutable mock-scoped signing package from real CI outputs.

Never substitute an invented CI statement for an evidence package. The full
manifest covers the C.2 finding register and C.2.5 accounting document, both
produced on the same immutable CI commit.
"""
import argparse,hashlib,json,pathlib,re
SHA=re.compile(r"^[0-9a-f]{40}$")
def prepare(out,commit,run,register,accounting):
    if not SHA.fullmatch(str(commit)) or not str(run).isdigit():raise ValueError("invalid provenance")
    out=pathlib.Path(out)
    out.mkdir(parents=True,exist_ok=True)
    sources={"c2_finding_register.json":pathlib.Path(register),"accounting.json":pathlib.Path(accounting)}
    for name,source in sources.items():
        if not source.is_file():raise ValueError("missing source "+name)
    finding=json.loads(sources["c2_finding_register.json"].read_text())
    counts=json.loads(sources["accounting.json"].read_text())
    if finding.get("schema_version")!="C2-R1.3-1" or finding.get("claim")!="NO_FINDINGS_CLOSED" or finding.get("summary",{}).get("total")!=14:
        raise ValueError("invalid historical register")
    if finding.get("summary",{}).get("formally_closed")!=0 or finding.get("summary",{}).get("evidence_verified")!=0:
        raise ValueError("unproven findings promoted")
    if counts.get("scope")!="UNIT_TESTS_NOT_SUT_CONFORMANCE":
        raise ValueError("accounting scope mismatch")
    c=counts.get("summary",{})
    if c.get("total")!=423 or c.get("passed")!=423 or c.get("executed")!=423 or c.get("skipped")!=0 or c.get("failed")!=0 or c.get("errors")!=0:
        raise ValueError("regression accounting inconsistent")
    filehash={}
    for name,source in sources.items():
        content=source.read_bytes()
        (out/name).write_bytes(content)
        filehash[name]=hashlib.sha256(content).hexdigest()
    provenance={"scope":"MOCK_ONLY","claim":"NO_REAL_SUT_CONFORMANCE","cts_commit":commit,"source_run_id":str(run),
                "finding_closure":"NOT_ESTABLISHED"}
    content=(json.dumps(provenance,indent=2,sort_keys=True)+"\n").encode()
    (out/"provenance.json").write_bytes(content)
    filehash["provenance.json"]=hashlib.sha256(content).hexdigest()
    manifest={"schema_version":"C2-R2-1","cts_commit":commit,"files":filehash}
    (out/"closure_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    return manifest

def main():
    p=argparse.ArgumentParser()
    for name in ("out","sha","run","register","accounting"):p.add_argument("--"+name,required=True)
    a=p.parse_args()
    prepare(a.out,a.sha,a.run,a.register,a.accounting)
    print("R2 BUNDLE PREPARED: real CI outputs, MOCK_ONLY, zero formally closed findings")
if __name__=="__main__":main()
