"""Stage C.1: evidence reconciliation, never translates unit PASS into CTS PASS."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, pathlib, re, sys
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[1]
HERE=pathlib.Path(__file__).resolve().parent
OUTCOMES={'PASS','FAIL','NOT_RUN','NOT_APPLICABLE'}
BASELINES={
 's1_configuration':78,'s2_execution':15,'s2_assessment':16,
 's2_mutation':16,'s3_decision':52,'s3_mutation':22,
 's35_integration':14,'s35_resolution':24,'s35_evidence':24,
 's35_timing':23,'s35_attribution':32,'s355_closure':14,
 's4_human_review':25,'s4_plugins':29,'s4_cli':19,'s5_reporting':20,
}
# Source runs VERIFIED in previous GitHub Actions logs. CI at final SHA is independent.
HISTORIC_RUNS={
 'S3.5.5':('39718787849','99d53c8003b89329e2f905647b214bdd68683c6d'),
 'S4.0':('39721203836','3b93390c6e751f82b12775b4311a765ae2a5b305'),
 'S4.1':('39722573831','4b5846d30d7023900421d1eb6914694cf4164b75'),
 'S4.2':('39724627184','755f4b45f1beca823d12a149ce8c26b2c95d6fcd'),
 'S5':('39727841995','7117698c7ffb59c57370b47a4877819d503a6c69'),
}
FINDINGS={
 'S2-F01':('MOCK_VERIFIED_REAL_DEFERRED','Positive drain in mock regression after S3.5.5; real-target calibration remains outstanding','S3.5.5'),
 'S2-F02':('MOCK_VERIFIED','Unified pipeline mock regression passed; real SUT not proven','S3.5.5'),
 'S2-F03':('MOCK_VERIFIED_REAL_DEFERRED','Filesystem evidence resolver tested; production custody/signatures not proven','S3.5.5'),
 'S2-F04':('MOCK_VERIFIED','Injected validator exception covered in mock','S3.5.5'),
 'S3-F01':('MOCK_VERIFIED','Execution-and-clause resolution mock regression passed','S3.5.5'),
 'S3-F02':('PARTIAL','Principal is mock identity, no external authorization or signature','S3.5.5'),
 'Q-02':('PARTIAL','Only scoped mock field paths, not all Appendix C response surfaces','S3.5.5'),
 'Q-08':('PARTIAL','Only selected machine-readable Expected predicates','S3.5.5'),
 'S3.5.4-REST':('PARTIAL','Mock HTTP facade is not real Appendix C SUT','S3.5.5'),
 'S4-F01':('PARTIAL','S4 CLI uses reduced envelope, not full adapter v0.4','S4.2'),
 'S4-F02':('PARTIAL','CLI mapping uses controlled expected dictionary rather than independent published CLI inventory','S4.2'),
 'S4-F03':('PARTIAL','Some HTTP mutants modify observation array after execution','S4.2'),
 'S4-F04':('PARTIAL','Plugin input capture is in-process mock log','S4.1'),
 'S4-F05':('DEFERRED_REAL_SUT','Human review not exercised against real reviewer authentication / service','S4.0'),
}
EXIT_NOTES={
 'EC-01':('PASS_MOCK','S0 self-test and parallel isolation are covered by regression'),
 'EC-02':('PARTIAL','Unique executed normative CTS cases require per-case runner evidence; unit test counts are not CTS case counts'),
 'EC-03':('PASS_MOCK','FAIL, NOT_RUN, NOT_APPLICABLE and mixed-case aggregation tested'),
 'EC-04':('PASS_MOCK','Closed/unclosed/late negative assertion tested with mock timing'),
 'EC-05':('PASS_EXAMPLE_ONLY','Filesystem evidence integrity tested on example store; not production custody'),
 'EC-06':('PASS_MOCK','Adapter contract and wrong envelope/version tests on mock'),
 'EC-07':('PASS_MOCK','Native validator recomputes report algebra and schema with evidence'),
 'EC-08':('PASS_FINAL_PACKAGE_ONLY','Final immutable-SHA report and ledger verified in one CI; historical runs remain separately attributed'),
 'EC-09':('CONDITIONAL_NOT_TRIGGERED','Real SUT availability not demonstrated; real E2E not performed'),
}

def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def utc():return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00','Z')
def dump(path,data):
 p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
def is_commit(s):return isinstance(s,str) and bool(re.fullmatch(r'[0-9a-f]{40}',s))

def verify_regression(reg,log_root,expected_commit):
 errors=[]
 if not is_commit(expected_commit):errors.append('invalid immutable commit')
 if reg.get('cts_commit')!=expected_commit:errors.append('regression SHA mismatch')
 seen=set();sum_tests=0
 for row in reg.get('suites',[]):
  name=row.get('suite');path=pathlib.Path(log_root)/(str(name)+'.log')
  if name in seen or name not in BASELINES:errors.append('unknown/duplicate suite '+str(name))
  seen.add(name)
  if not path.is_file():errors.append('missing log '+str(path));continue
  if digest(path)!=row.get('sha256'):errors.append('tampered log '+str(name))
  n=row.get('tests')
  if n!=BASELINES.get(name):errors.append('unexpected number of tests in '+str(name))
  if row.get('exit_code')!=0:errors.append('nonzero unit exit '+str(name))
  text=path.read_text(encoding='utf8',errors='replace')
  if not re.search(r'Ran '+str(n)+r' tests? in',text):errors.append('missing count in '+str(name))
  if not re.search(r'^OK(?: \(skipped=\d+\))?\s*$',text,re.M):errors.append('missing OK '+str(name))
  if isinstance(n,int):sum_tests+=n
 if seen!=set(BASELINES):errors.append('missing suite(s): '+str(sorted(set(BASELINES)-seen)))
 if sum_tests!=423 or reg.get('total_tests')!=423:errors.append('wrong regression count')
 if reg.get('scope')!='UNIT_TESTS_NOT_SUT_CONFORMANCE':errors.append('scope contamination')
 return errors

def reconcile(source,current_sha,regression_ok):
 if not regression_ok:raise ValueError('cannot mark historical fixes as verified before current CI regression')
 found={x['id']:x for x in source}
 if set(found)!=set(k for k in FINDINGS if k.startswith(('S2','S3','Q-'))):
  raise ValueError('historical finding inventory changed; reconcile manually')
 rows=[]
 for id,(status,reason,runk) in FINDINGS.items():
  run,sha=HISTORIC_RUNS[runk]
  rows.append({'finding_id':id,'status':status,'basis':reason,'scope':'MOCK_ONLY',
               'historical_status':found[id]['status'] if id in found else None,
               'verification_commit':current_sha,
               'source_run':f'https://github.com/igorakymenko-create/AQEF/actions/runs/{run}',
               'source_commit':sha,
               'real_sut_disposition':'NOT_ESTABLISHED'})
 return rows

def build(root,commit,regression,legacy,report,manifest,evidence_root,real_sut_available=False):
 """Final packet is not proof of SUT compliance, even when all unit tests pass."""
 if not is_commit(commit):raise ValueError('full immutable 40-hex SHA required')
 root=pathlib.Path(root);errors=verify_regression(regression,root/'logs',commit)
 if errors:raise ValueError('regression evidence invalid: '+str(errors))
 # Native tool verifies current normative inventory, evidence integrity, summary and traces.
 sys.path.insert(0,str(ROOT/'harness'/'tools'))
 import validate as v
 native=v.check_report(report,v.load_inventory(),manifest,evidence_root)
 if native:raise ValueError('native report verification failed: '+str(native[:8]))
 if report['provenance'].get('cts_commit')!=commit:raise ValueError('report provenance differs from immutable checkout')
 if report['provenance'].get('sut_name')!='Stage-C-Mock-Only':raise ValueError('real SUT claim is forbidden')
 if report['plan']['scope']!='partial':raise ValueError('S5 example report is partial')
 if report['summary']['cases']['PASS']!=0:raise ValueError('unexpected normative CTS PASS from unobserved mock')
 if report['summary']['cases']['NOT_RUN']<=0:raise ValueError('missing honest NOT_RUN')
 findings=reconcile(legacy,commit,True)
 # CI regression is not a CTS run, so coverage is clearly NOT_ESTABLISHED.
 try: inv=v.load_inventory()
 except Exception as exc: raise ValueError('inventory unavailable') from exc
 selected=report['plan']['test_ids']
 case_rows=[{'case_id':cid,'test_id':tid,'reported_outcome':next(c['outcome'] for c in report['cases'] if c['case_id']==cid),
             'independent_sut_evidence':'NOT_ESTABLISHED', 'evidence_source':'S5 checked mock report',
             'unit_test_pass_is_not_cts_verdict':True} for tid in selected for cid in inv['tests'][tid]['cases']]
 criteria=[{'id':key,'status':status,'reason':detail,'cts_commit':commit} for key,(status,detail) in EXIT_NOTES.items()]
 if real_sut_available:criteria[-1].update({'status':'NOT_RUN','reason':'Real SUT declared available but no complete E2E evidence supplied'})
 runref=f'https://github.com/igorakymenko-create/AQEF/actions/runs/'
 ledger={'schema_version':'C1-1','cts_commit':commit,'scope':'MOCK_HARNESS_REGRESSION_ONLY',
         'unit_test_total':423,'evidence_claim':'NO_REAL_SUT_CONFORMANCE',
         'historical_runs':[{'slice':k,'run_url':runref+rid,'commit':sha,'outcome':'CI_SUCCESS_ONLY'} for k,(rid,sha) in HISTORIC_RUNS.items()],
         'suites':regression['suites'],'normative_cases':case_rows,
         'report_sha256':digest(root/'report.json'),'manifest_sha256':digest(root/'manifest.json')}
 dump(root/'audit_register.json',findings);dump(root/'evidence_ledger.json',ledger)
 dump(root/'exit_criteria.json',criteria)
 summary={k:sum(1 for v in criteria if v['status']==k) for k in sorted({c['status'] for c in criteria})}
 md=['# AQEF Stage C.1 — Final Evidence Closure','',f'- Immutable commit: `{commit}`',
     '- Engineering decision: **MOCK-BASED HARNESS ACCEPTED, CONDITIONAL FORMAL EXIT**.',
     '- Real SUT conformance: **NOT ESTABLISHED**.',
     '- CI regression: **423/423 Python tests** (not normative CTS PASS).',
     '- Native CTS report: validated with manifest and evidence; selected unobserved CTS cases remain NOT_RUN.',
     '- Unique independently executed normative CTS cases: **NOT ESTABLISHED** (EC-02 partial).',
     '- Real SUT availability: '+('declared available; real E2E missing' if real_sut_available else 'not supplied'),
     '', '## Exit Criteria','','| ID | Status | Basis |','|---|---|---|']
 md += [f"| {c['id']} | {c['status']} | {c['reason']} |" for c in criteria]
 md += ['','## Open / deferred findings','','| ID | Status | Basis |','|---|---|---|']
 md += [f"| {f['finding_id']} | {f['status']} | {f['basis']} |" for f in findings]
 md += ['','## Decision','','S0–S5 engineering harness acceptance remains valid within mock scope.',
        'Do not advertise an unconditional Stage C EXIT PASS until EC-02 per-case evidence is linked and other conditional criteria are formally settled.',
        'If real SUT becomes available, run Appendix C E2E and issue a distinct conformance report.',
        'This is a package generated from one checked-out commit and an auditable set of regression logs.']
 (root/'final_exit_report.md').write_text('\n'.join(md)+'\n',encoding='utf8')
 files=['audit_register.json','evidence_ledger.json','exit_criteria.json','final_exit_report.md','regression.json','report.json','manifest.json']
 files += ['logs/'+x+'.log' for x in BASELINES]
 for p in pathlib.Path(evidence_root).rglob('*'):
  if p.is_file():files.append(str(p.relative_to(root)))
 index={'schema_version':'C1-1','cts_commit':commit,'files':{path:digest(root/path) for path in sorted(files)},
        'total_unit_tests':423,'report_scope':'PARTIAL_MOCK','decision':'CONDITIONAL_MOCK_EXIT'}
 dump(root/'closure_manifest.json',index)
 return index

def validate_bundle(root,expected_commit):
 root=pathlib.Path(root);m=json.loads((root/'closure_manifest.json').read_text())
 errors=[]
 if m.get('cts_commit')!=expected_commit:errors.append('closure SHA differs')
 if m.get('total_unit_tests')!=423:errors.append('unit baseline mismatch')
 for p,h in m.get('files',{}).items():
  target=(root/p).resolve()
  if root.resolve() not in target.parents or not target.is_file() or digest(target)!=h:errors.append('tampered/missing file '+p)
 return errors

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--sha',required=True);p.add_argument('--legacy',required=True);p.add_argument('--real-sut-available',action='store_true');a=p.parse_args()
 o=pathlib.Path(a.root)
 build(o,a.sha,json.loads((o/'regression.json').read_text()),json.loads(pathlib.Path(a.legacy).read_text()),
       json.loads((o/'report.json').read_text()),json.loads((o/'manifest.json').read_text()),o/'evidence',a.real_sut_available)
 errors=validate_bundle(o,a.sha)
 if errors:raise SystemExit('; '.join(errors))
 print('C1 VERIFIED: 423 unit tests; native report and evidence valid; no SUT conformance claim; conditional exit')
