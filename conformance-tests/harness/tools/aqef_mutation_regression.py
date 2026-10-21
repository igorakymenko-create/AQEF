#!/usr/bin/env python3
"""Independent, read-only AQEF CTS Harness v0.4 mutation regression.
Run from any directory: python3 aqef_mutation_regression.py /path/to/AQEF
Requires jsonschema==4.23.0 and referencing.
No repository files are changed. All byte mutations are made in a temporary directory.
"""
import copy, hashlib, importlib.util, json, pathlib, shutil, sys, tempfile

if len(sys.argv) != 2:
    raise SystemExit('Usage: python3 aqef_mutation_regression.py /path/to/AQEF')
repo = pathlib.Path(sys.argv[1]).resolve()
here = repo / 'conformance-tests' / 'harness'
module_file = here / 'tools' / 'validate.py'
if not module_file.is_file():
    raise SystemExit(f'Not found: {module_file}')
spec = importlib.util.spec_from_file_location('aqef_validate_under_test', module_file)
v = importlib.util.module_from_spec(spec); sys.modules[spec.name] = v; spec.loader.exec_module(v)
ex = here / 'examples'
report0 = json.loads((ex / 'cts-report--algebra.json').read_text(encoding='utf-8'))
manifest0 = json.loads((ex / 'evidence-manifest--algebra.json').read_text(encoding='utf-8'))
inv = v.load_inventory()
results=[]

def record(name, expected, detected, errors):
    status='KILLED' if expected and detected else ('SURVIVED' if expected else ('BASELINE_OK' if not detected else 'BASELINE_FAILED'))
    results.append(dict(name=name,status=status,diagnostics=errors[:3]))
    print(f'{status:15s} {name}' + (f' | {str(errors[0])[:160]}' if errors else ''))

def mutate_report(name, mutation):
    r=copy.deepcopy(report0)
    mutation(r)
    try: e=v.check_report(r,inv,manifest0,ex/'evidence')
    except Exception as x: e=[f'EXCEPTION {type(x).__name__}: {x}']
    record(name,True,bool(e),e)

def case(r,cid):return next(c for c in r['cases'] if c['case_id']==cid)
def requirement(r,rid):return next(q for q in r['requirements'] if q['requirement_id']==rid)

def re_count(r):
    cnt=lambda xs,key,ks:{k:sum(1 for a in xs if a[key]==k) for k in ks}
    r['summary']={'cases':cnt(r['cases'],'outcome',v.ORDER),'tests':cnt(r['tests'],'outcome',v.ORDER),'requirements':cnt(r['requirements'],'state',v.STATES)}

try:errors=v.check_report(report0,inv,manifest0,ex/'evidence')
except Exception as x:errors=[f'EXCEPTION {type(x).__name__}: {x}']
record('baseline valid report + real evidence',False,bool(errors),errors)

mutate_report('duplicate case ID',lambda r:r['cases'].append(copy.deepcopy(r['cases'][0])))
mutate_report('missing planned case CT-CFG-025.05',lambda r:r.update(cases=[c for c in r['cases'] if c['case_id']!='CT-CFG-025.05']))
mutate_report('duplicate test ID',lambda r:r['tests'].append(copy.deepcopy(r['tests'][0])))
mutate_report('missing planned test CT-ASM-001',lambda r:r.update(tests=[t for t in r['tests'] if t['test_id']!='CT-ASM-001']))
mutate_report('missing requirement row',lambda r:r['requirements'].pop())
mutate_report('duplicate requirement row',lambda r:r['requirements'].append(copy.deepcopy(r['requirements'][0])))
mutate_report('false PASS hides NOT_RUN',lambda r:next(t for t in r['tests'] if t['test_id']=='CT-CFG-025').update(outcome='PASS'))
mutate_report('wrong CTS trace',lambda r:requirement(r,'R-0021').update(traced_to=['CT-ASM-001']))
mutate_report('wrong requirement state even with recomputed summary',lambda r:(requirement(r,'R-0021').update(state='verified'),re_count(r)))
mutate_report('partial plan misrepresented as full',lambda r:r['plan'].update(scope='full'))
mutate_report('wrong CTS revision',lambda r:r['provenance'].update(cts_revision='WD6'))
mutate_report('case attributed to wrong test',lambda r:case(r,'CT-ASM-001').update(test_id='CT-REL-023'))
mutate_report('evidence reference outside manifest',lambda r:case(r,'CT-ASM-001').update(evidence_refs=['evidence://does-not-exist']))
mutate_report('report references wrong manifest digest',lambda r:r.update(evidence_manifest_sha256='0'*64))
mutate_report('wrong capability on conditional case',lambda r:case(r,'CT-CFG-025.25').update(capability='core'))

with tempfile.TemporaryDirectory(prefix='aqef-regression-') as td:
    root=pathlib.Path(td)
    # Copy evidence so no repo data is modified
    shutil.copytree(ex/'evidence',root/'evidence')
    def evidence_mutation(name,fn):
        m=copy.deepcopy(manifest0);r=copy.deepcopy(report0)
        try:
            if (root/'evidence').exists():shutil.rmtree(root/'evidence')
            shutil.copytree(ex/'evidence',root/'evidence')
            fn(m,root/'evidence')
            errors=v.check_report(r,inv,m,root/'evidence')
        except Exception as x:errors=[f'EXCEPTION {type(x).__name__}: {x}']
        record(name,True,bool(errors),errors)
    def raw_path(m,root):return v.resolve(m['entries'][0]['raw_ref'],root)
    evidence_mutation('flip one byte in raw Evidence',lambda m,root:(lambda p:p.write_bytes(p.read_bytes()[:-1]+bytes([p.read_bytes()[-1]^1])))(raw_path(m,root)))
    evidence_mutation('remove raw Evidence',lambda m,root:raw_path(m,root).unlink())
    evidence_mutation('truncate raw Evidence',lambda m,root:(lambda p:p.write_bytes(p.read_bytes()[:max(0,len(p.read_bytes())//2)]))(raw_path(m,root)))
    evidence_mutation('alter manifest raw_size',lambda m,root:m['entries'][0].update(raw_size=m['entries'][0]['raw_size']+1))
    evidence_mutation('duplicate evidence_id',lambda m,root:m['entries'].append(copy.deepcopy(m['entries'][0])))
    evidence_mutation('path traversal in evidence ref',lambda m,root:m['entries'][0].update(raw_ref='evidence://../outside.json'))
    def redacted(m,root):
        e=next(x for x in m['entries'] if x.get('redacted_ref'))
        p=v.resolve(e['redacted_ref'],root);p.write_bytes(p.read_bytes()+b'!')
    evidence_mutation('modify redacted Evidence',redacted)

# Independent RFC 8785 known-order test: code point order != UTF-16 order.
try:
    serialized=v.jcs({'\ue000':1,'\U0001f600':2})
    record('RFC8785 UTF-16 key order',True,serialized.startswith('{"\U0001f600":2,') ,[] if serialized.startswith('{"\U0001f600":2,') else [serialized])
except Exception as x:record('RFC8785 UTF-16 key order',True,False,[str(x)])
try:
    record('RFC8785 negative zero',True,v.jcs(-0.0)=='0',[])
except Exception as x:record('RFC8785 negative zero',True,False,[str(x)])
try:
    try:v.jcs(2**60);refused=False
    except (ValueError,OverflowError):refused=True
    record('RFC8785 unsafe integer refused',True,refused,[])
except Exception as x:record('RFC8785 unsafe integer refused',True,False,[str(x)])

print('\nSUMMARY',json.dumps({k:sum(1 for x in results if x['status']==k) for k in ['BASELINE_OK','BASELINE_FAILED','KILLED','SURVIVED']}))
out=pathlib.Path('aqef_mutation_results.json').resolve()
out.write_text(json.dumps({'repository':str(repo),'contract_version':'0.4','cases':results},ensure_ascii=False,indent=2),encoding='utf-8')
print('Detailed results:',out)
raise SystemExit(1 if any(x['status'] in ('BASELINE_FAILED','SURVIVED') for x in results) else 0)
