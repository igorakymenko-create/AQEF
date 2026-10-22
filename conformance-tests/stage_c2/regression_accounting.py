"""Stage C.2.5 strict unittest execution accounting.

Count executed/passed/failed/errors/skipped from verbose unittest output,
cross-check against summary, hashed logs and immutable regression baseline.
This is unit test accounting, not normative CTS case conformance.
"""
import hashlib,json,pathlib,re

RESULT=re.compile(r"^.+? \.\.\. (ok|FAIL|ERROR|skipped .+|expected failure|unexpected success)$",re.M)
RAN=re.compile(r"^Ran (\d+) tests? in ",re.M)
OK=re.compile(r"^OK(?: \(skipped=(\d+)\))?\s*$",re.M)
FAILED=re.compile(r"^FAILED \(([^\n]+)\)\s*$",re.M)

def count_log(log, *, exit_code, allowed_skips=0):
    errors=[]
    if not isinstance(allowed_skips,int) or isinstance(allowed_skips,bool) or allowed_skips<0:
        return None,["invalid skip policy"]
    matches=RESULT.findall(log)
    counts={"passed":sum(x=="ok" for x in matches),
            "failed":sum(x=="FAIL" for x in matches),
            "errors":sum(x=="ERROR" for x in matches),
            "skipped":sum(x.startswith("skipped ") for x in matches),
            "expected_failures":sum(x=="expected failure" for x in matches),
            "unexpected_successes":sum(x=="unexpected success" for x in matches)}
    counts["total"]=sum(counts.values())
    counts["executed"]=counts["total"]-counts["skipped"]
    found=RAN.findall(log)
    if len(found)!=1 or counts["total"]!=int(found[0]):
        errors.append("verbose results disagree with test summary")
    ok=OK.findall(log)
    if exit_code==0:
        if len(ok)!=1 or FAILED.search(log):
            errors.append("success exit disagrees with result summary")
        elif int(ok[0] or 0)!=counts["skipped"]:
            errors.append("skip count disagrees with OK summary")
        if counts["failed"] or counts["errors"] or counts["unexpected_successes"]:
            errors.append("successful exit with failures")
    else:
        if not FAILED.search(log):
            errors.append("failure exit without FAILED summary")
    if counts["skipped"]>allowed_skips:
        errors.append("skip policy exceeded")
    if counts["expected_failures"] or counts["unexpected_successes"]:
        errors.append("unapproved expected/unexpected failures")
    return counts,errors

def verify_regression(regression,logs_dir,baselines,*,skip_allowance=None):
    skip_allowance=skip_allowance or {}
    errors=[];rows=[];seen=set()
    if regression.get("scope")!="UNIT_TESTS_NOT_SUT_CONFORMANCE":
        errors.append("incorrect regression scope")
    for row in regression.get("suites",[]):
        suite=row.get("suite")
        if suite not in baselines or suite in seen:
            errors.append("unknown/duplicate suite: "+str(suite));continue
        seen.add(suite)
        path=(pathlib.Path(logs_dir)/(suite+".log"))
        if not path.is_file():
            errors.append("missing log: "+suite);continue
        data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=row.get("sha256"):
            errors.append("log digest mismatch: "+suite)
        tally,problems=count_log(data.decode("utf-8",errors="replace"),
                                  exit_code=row.get("exit_code"),
                                  allowed_skips=skip_allowance.get(suite,0))
        errors.extend(suite+": "+p for p in problems)
        if tally is None:continue
        if tally["total"]!=row.get("tests") or tally["total"]!=baselines[suite]:
            errors.append("baseline mismatch: "+suite)
        rows.append({"suite":suite,**tally})
    if seen!=set(baselines):
        errors.append("suite inventory mismatch")
    summary={k:sum(r[k] for r in rows) for k in ("total","executed","passed","failed","errors","skipped","expected_failures","unexpected_successes")}
    if summary["total"]!=regression.get("total_tests") or summary["total"]!=sum(baselines.values()):
        errors.append("regression total mismatch")
    return {"scope":"UNIT_TESTS_NOT_SUT_CONFORMANCE","suites":rows,"summary":summary},errors

def main():
    import argparse,sys
    p=argparse.ArgumentParser()
    p.add_argument("--regression",required=True);p.add_argument("--logs",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"stage_c_closure"))
    from closure import BASELINES
    document,errors=verify_regression(json.loads(pathlib.Path(a.regression).read_text()),a.logs,BASELINES)
    if errors:raise SystemExit("; ".join(errors))
    pathlib.Path(a.output).write_text(json.dumps(document,indent=2,sort_keys=True)+"\n")
    s=document["summary"]
    print(f'C2.5 ACCOUNTED total={s["total"]} executed={s["executed"]} passed={s["passed"]} skipped={s["skipped"]}; NO SUT CLAIM')
if __name__=="__main__":main()
