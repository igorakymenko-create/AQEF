"""S5 honest partial CTS reporting. Green unittest runs are NOT SUT verdicts.
Uses the repository's normative inventory, algebra, manifest and report verifier.
"""
from __future__ import annotations
import copy, datetime, hashlib, json, os, pathlib, sys, uuid
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'harness'/'tools'))
import validate as v

SELECTED=('CT-EXE-003','CT-EXE-008','CT-ASM-001','CT-ASM-014',
          'CT-DEC-006','CT-DEC-012','CT-REL-006','CT-HRV-003','CT-PLG-003','CT-SDK-001')
REASONS={'PASS':'EXPECTED_MET','FAIL':'EXPECTED_VIOLATED',
         'NOT_RUN':'OBSERVATION_INCOMPLETE','NOT_APPLICABLE':'CAPABILITY_NOT_CLAIMED'}

def utc_now():return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z')
def encoded(obj):return v.jcs(obj).encode('utf-8')
def store_evidence(root, name, value, now, entries, case_id=None):
    root=pathlib.Path(root);root.mkdir(parents=True,exist_ok=True)
    data=encoded(value);ref='evidence://'+name+'.json';p=root/(name+'.json')
    p.write_bytes(data)
    entry={'evidence_id':name,'kind':'statement' if name=='conformance-statement' else 'probe',
           'raw_ref':ref,'raw_sha256':v.sha256_hex(data),'raw_size':len(data),
           'collected_at':now,'redaction_policy':'none-local-mock'}
    if case_id:entry['case_id']=case_id
    entries.append(entry)
    return ref

def build(output_dir,*,cts_commit, observations=None, claims=(), now=None):
    """Observations are explicit externally supplied CTS outcomes, NOT unittest results.
    PASS/FAIL require a written evidence payload and runner attribution. The default
    creates a truthful NOT_RUN report. No production conformance claims.
    """
    if not cts_commit or len(cts_commit)<7:raise ValueError('immutable CTS commit required')
    observations=observations or {}
    now=now or utc_now()
    inv=v.load_inventory()
    tests=[t for t in SELECTED if t in inv['tests']]
    if len(tests)!=len(SELECTED):raise ValueError('missing normative CTS IDs')
    out=pathlib.Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    root=out/'evidence';entries=[];run='s5-'+uuid.uuid4().hex
    statement={'scope':'MOCK_ONLY_CTS_HARNESS','not_real_sut_conformance':True,
               'limitations':['S4-F01','S4-F02','S4-F03','S4-F04','S4-F05'],
               'note':'This statement is generated for harness reporting, NOT a SUT claim.'}
    statement_ref=store_evidence(root,'conformance-statement',statement,now,entries)
    cases=[]
    for tid in tests:
        for cid in inv['tests'][tid]['cases']:
            caps=inv['tests'][tid]['case_caps'][cid];claim=v.is_claimed(caps,list(claims))
            o=observations.get(cid)
            if not claim:
                outcome='NOT_APPLICABLE';reason='CAPABILITY_NOT_CLAIMED';refs=[]
            elif o is None:
                outcome='NOT_RUN';reason='OBSERVATION_INCOMPLETE';refs=[]
            else:
                outcome=o.get('outcome')
                if outcome not in REASONS:raise ValueError('unknown outcome: '+str(cid))
                if outcome=='NOT_APPLICABLE':raise ValueError('claimed capability cannot be marked N/A')
                if outcome in ('PASS','FAIL') and not isinstance(o.get('evidence'),dict):
                    raise ValueError('PASS/FAIL require independent evidence: '+cid)
                if outcome in ('PASS','FAIL') and not o.get('runner_observed',False):
                    raise ValueError('PASS/FAIL require runner_observed=true: '+cid)
                reason=REASONS[outcome];refs=[]
                if isinstance(o.get('evidence'),dict):
                    refs=[store_evidence(root,'case-'+cid,o['evidence'],now,entries,cid)]
            case={'case_id':cid,'test_id':tid,'capability':' + '.join(caps),'outcome':outcome,
                  'reason_code':reason,'evidence_refs':refs,'evidence_grades':['observed'] if refs else [],
                  'setup_status':'not_needed' if outcome=='NOT_APPLICABLE' else ('failed' if outcome=='NOT_RUN' else 'ready'),
                  'cleanup_status':'skipped' if outcome in ('NOT_RUN','NOT_APPLICABLE') else 'complete'}
            if outcome=='NOT_RUN':case['reason']='No verified CTS observation was available for this case.'
            cases.append(case)
    case_map={x['case_id']:x['outcome'] for x in cases}
    test_rows=[{'test_id':t,'case_ids':inv['tests'][t]['cases'],
                'outcome':v.summarize([case_map[c] for c in inv['tests'][t]['cases']])} for t in tests]
    requirements=[]
    for rid,w in inv['requirements'].items():
        rec={'requirement_id':rid,'state':v.requirement_state(w['traced'],case_map),
             'traced_to':w['traced']}
        if w['derived_from'] is not None:rec['derived_from']=w['derived_from']
        requirements.append(rec)
    def count(xs,key,values):return {x:sum(i[key]==x for i in xs) for x in values}
    manifest={'schema_version':'0.4','run_id':run,'created_at':now,'canonicalization':'RFC8785','entries':entries}
    manifest['manifest_sha256']=v.sha256_hex(encoded(manifest))
    report={'schema_version':'0.4','run_id':run,
      'provenance':{'aqef_version':'working-draft','cts_revision':inv['revision'],'cts_commit':cts_commit,
                    'harness_contract_version':'0.4','harness_version':'s5-0.1',
                    'adapter_id':'s5-mock-harness','adapter_version':'0.1',
                    'sut_name':'Stage-C-Mock-Only','sut_version':'0.1',
                    'conformance_statement_ref':statement_ref,'capabilities_claimed':list(claims)},
      'plan':{'scope':'partial','test_ids':tests,
              'reason':'Stage C selected mock CTS cases only; not a full suite or real SUT conformance run.'},
      'started_at':now,'ended_at':now,'cases':cases,'tests':test_rows,'requirements':requirements,
      'summary':{'cases':count(cases,'outcome',v.ORDER),'tests':count(test_rows,'outcome',v.ORDER),
                 'requirements':count(requirements,'state',v.STATES)},
      'evidence_manifest_ref':'evidence://manifest.json','evidence_manifest_sha256':manifest['manifest_sha256'],
      'harness_findings':[]}
    errors=v.check_report(report,inv,manifest,root)
    if errors:raise ValueError('report rejected: '+str(errors[:12]))
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report,manifest

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--commit',required=True)
    p.add_argument('--observations',help='JSON mapping case IDs to runner observations (optional)')
    p.add_argument('--claims',default='',help='comma-separated capabilities')
    args=p.parse_args()
    observed=json.loads(pathlib.Path(args.observations).read_text()) if args.observations else None
    report,manifest=build(args.out,cts_commit=args.commit,observations=observed,
                         claims=[x for x in args.claims.split(',') if x])
    print(json.dumps({'cts_commit':args.commit,'scope':'S5_PARTIAL_MOCK_REPORT_ONLY',
      'summary':report['summary'],'manifest_sha256':manifest['manifest_sha256']},indent=2))
