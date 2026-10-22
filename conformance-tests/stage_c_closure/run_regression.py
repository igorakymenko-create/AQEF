"""Runs EVERY previously accepted unittest suite once; captures attestable logs.
No attempt to equate unittest success with CTS case conformance.
"""
import argparse, datetime, hashlib, json, os, pathlib, re, subprocess, sys
from closure import BASELINES,dump,is_commit

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--sha',required=True);a=p.parse_args()
 if not is_commit(a.sha) or os.environ.get('GITHUB_SHA',a.sha)!=a.sha:raise SystemExit('untrusted/incorrect SHA')
 out=pathlib.Path(a.out);logs=out/'logs';logs.mkdir(parents=True,exist_ok=True)
 src=pathlib.Path(__file__).resolve().parents[1]
 rows=[];failed=[]
 for suite,want in BASELINES.items():
  cmd=[sys.executable,'-m','unittest','discover','-p','test_*.py','-v']
  p=subprocess.run(cmd,cwd=src/suite,capture_output=True,text=True,timeout=240)
  log=p.stdout+'\n'+p.stderr
  log_path=logs/(suite+'.log');log_path.write_text(log,encoding='utf8')
  match=re.search(r'Ran (\d+) tests? in',log)
  count=int(match.group(1)) if match else -1
  rows.append({'suite':suite,'tests':count,'exit_code':p.returncode,'sha256':hashlib.sha256(log_path.read_bytes()).hexdigest()})
  print(f'{suite}: {count}/{want} tests, exit={p.returncode}',flush=True)
  if p.returncode!=0 or count!=want or not re.search(r'^OK(?: \(skipped=\d+\))?\s*$',log,re.M):failed.append(suite)
 reg={'cts_commit':a.sha,'scope':'UNIT_TESTS_NOT_SUT_CONFORMANCE','total_tests':sum(r['tests'] for r in rows),'suites':rows,
      'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 dump(out/'regression.json',reg)
 if failed:raise SystemExit('regression failed: '+', '.join(failed))
 if reg['total_tests']!=423:raise SystemExit('expected 423 regression tests')
 print('REGRESSION VERIFIED 423/423 on immutable commit '+a.sha)
if __name__=='__main__':main()
