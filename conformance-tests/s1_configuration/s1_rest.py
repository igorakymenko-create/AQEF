"""S1 non-normative reference HTTP bridge: runner -> adapter -> mock SUT.
No real AQEF conformance is claimed. Existing S1 mock.py/runner.py remain unchanged.
"""
from __future__ import annotations
import copy, hashlib, json, threading, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, unquote, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from contextlib import contextmanager
from mock import MockSUT, fixture_base
from runner import CASES, summarize
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent/'harness'/'tools'))
import validate as v


def encode(obj): return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf8')
def http(method, url, obj=None):
    raw=encode(obj) if obj is not None else None
    req=Request(url, data=raw, method=method, headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=8) as res:return res.status,json.loads(res.read())
    except HTTPError as err:return err.code,json.loads(err.read())


def fixture_seed_full():
    """CTS 13.1 F-SEED: F-BASE plus defect class and s-control.
    Conversation wire shape is a mock convention, not a normative REST schema.
    """
    c=fixture_base();p=c['project'];p['defect_classes']=[{'name':'greeting-missing'}]
    p['suites'][0]['scenarios'].append({
       'name':'s-control',
       'seeded_control':{'defect_class':'greeting-missing','planted_defect':'The response does not greet the user.','confirmed_by':'construction'},
       'evidence':{'conversation':[{'role':'user','content':'Hello'},{'role':'assistant','content':'Goodbye.'}]},
       'contract':{'expectations':[{'criteria':'The response greets the user.', 'defect_classes':['greeting-missing'],
                  'judge':{'model':'cts-scripted-judge@1','confidence_source':'self_rating'},'confidence_threshold':0.8}]}
    })
    return c


class RestMock(MockSUT):
    """Tiny mock that validates the F-SEED structural relationships used in S1."""
    def load(self, pid, cfg):
        p=cfg.get('project') if isinstance(cfg,dict) else None
        if isinstance(p,dict) and 'defect_classes' in p and 'seeded_controls' in self.capabilities:
            classes=p['defect_classes']
            if not isinstance(classes,list) or not classes:return 422,{'code':'INVALID_CONFIG','field':'defect_classes'}
            if any(not isinstance(c,dict) for c in classes):return 422,{'code':'INVALID_CONFIG','field':'defect_classes'}
            names={c.get('name') for c in classes if c.get('name')}
            try:scenarios=p['suites'][0]['scenarios']; control=next(x for x in scenarios if x['name']=='s-control')
            except (KeyError, IndexError, StopIteration, TypeError):return 422,{'code':'INVALID_CONFIG','field':'s-control'}
            if control['seeded_control'].get('defect_class') not in names:
                # Missing name explicitly diagnosed before the mock's basic validator.
                if self.mutation!='accept_missing_name':return 422,{'code':'INVALID_CONFIG','field':'defect_classes[0].name'}
            if not control.get('evidence',{}).get('conversation'):
                return 422,{'code':'INVALID_CONFIG','field':'s-control.evidence.conversation'}
        return super().load(pid,cfg)


class QuietHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,status,obj):
        raw=encode(obj);self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlsplit(self.path).path.split('/')
        if self.server.kind=='mock' and len(path)==3 and path[1]=='projects':
            pid=unquote(path[2]);s,b=self.server.sut.get(pid);return self.reply(s,b)
        return self.reply(404,{'code':'NOT_FOUND'})
    def do_POST(self):
        n=self.headers.get('Content-Length','')
        if not n.isdecimal() or int(n)>2_000_000:return self.reply(413,{'error':'BODY_TOO_LARGE'})
        try:obj=json.loads(self.rfile.read(int(n)))
        except (ValueError,UnicodeDecodeError):return self.reply(400,{'error':'INVALID_JSON'})
        if self.server.kind=='mock' and urlsplit(self.path).path=='/projects':
            if not isinstance(obj,dict) or 'project_id' not in obj or 'config' not in obj:return self.reply(400,{'error':'INVALID_ARGUMENTS'})
            pid=obj['project_id'];status,body=self.server.sut.load(pid,obj['config']);return self.reply(status,body)
        if self.server.kind=='adapter' and urlsplit(self.path).path=='/api/v0.4/operations':
            if not isinstance(obj,dict):return self.reply(400,{'error':'INVALID_ENVELOPE'})
            errs=v.schema_errors('adapter-operation.schema.json',obj)
            if errs:return self.reply(400,{'error':'SCHEMA_INVALID','details':errs[:5]})
            if obj['operation']!='load_config':
                rsp={'contract_version':'0.4','operation':obj['operation'],'correlation_id':obj['correlation_id'],'success':False,
                     'error':{'origin':'adapter','phase':'action','code':'ADAPTER_SURFACE_UNSUPPORTED','message':'Only load_config supported in S1','retryable':False}}
                return self.reply(200,rsp)
            args=obj['arguments'];status,body=http('POST',self.server.mock_url+'/projects',args)
            ref='evidence://s1-rest/'+uuid.uuid4().hex;raw=encode(body)
            with self.server.lock:self.server.evidence[ref]=(obj['run_id'],obj['case_id'],raw)
            response={'contract_version':'0.4','operation':'load_config','correlation_id':obj['correlation_id'],'success':True,
                'data':{'sut':{'outcome':'accepted' if status in (200,201,202) else 'rejected','status':status,
                 'body_ref':ref,'body_sha256':hashlib.sha256(raw).hexdigest(),'surface':'equivalent'}},'evidence_refs':[ref]}
            errs=v.schema_errors('adapter-response.schema.json',response)
            if errs:return self.reply(500,{'error':'ADAPTER_RESPONSE_SCHEMA','details':errs})
            return self.reply(200,response)
        return self.reply(404,{'error':'NOT_FOUND'})


class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,kind,sut=None,mock_url=None):
        super().__init__(('127.0.0.1',0),QuietHandler)
        self.kind=kind;self.sut=sut;self.mock_url=mock_url;self.evidence={};self.lock=threading.RLock()
    @property
    def url(self):return f'http://127.0.0.1:{self.server_port}'

@contextmanager
def services(mutation=None,capabilities=('seeded_controls',)):
    mock=Server('mock',RestMock(mutation,capabilities));adapter=Server('adapter',mock_url=mock.url)
    threads=[threading.Thread(target=s.serve_forever,daemon=True) for s in (mock,adapter)]
    for t in threads:t.start()
    try:yield mock,adapter
    finally:
        for s in (mock,adapter):s.shutdown();s.server_close()
        for t in threads:t.join(timeout=2)


def call(adapter, case, cfg, pid):
    req={'contract_version':'0.4','operation':'load_config','run_id':'s1-'+uuid.uuid4().hex,'case_id':case,
         'session_id':'s1-session-'+uuid.uuid4().hex,'correlation_id':'corr-'+uuid.uuid4().hex,
         'timeout_ms':10000,'arguments':{'project_id':pid,'config':cfg}}
    assert not v.schema_errors('adapter-operation.schema.json',req)
    st,rsp=http('POST',adapter.url+'/api/v0.4/operations',req)
    if st!=200 or v.schema_errors('adapter-response.schema.json',rsp):raise AssertionError(f'Invalid HTTP contract: {st}, {rsp}')
    if rsp['correlation_id']!=req['correlation_id']:raise AssertionError('correlation mismatch')
    return req,rsp


def run_rest(mutation=None,seeded_controls=True,setup_available=True):
    cases={}
    with services(mutation,('seeded_controls',) if seeded_controls else ()) as (mock,adapter):
        for case in CASES:
            if case.endswith('.25') and not seeded_controls:
                cases[case]={'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_NOT_CLAIMED'};continue
            if not setup_available:
                cases[case]={'outcome':'NOT_RUN','reason':'SETUP_FAILED'};continue
            source=fixture_seed_full() if case.endswith('.25') else fixture_base()
            # Mandatory pristine fixture setup for CT-CFG-025, isolated namespace.
            if case!='CT-CFG-001':
                setup_id='setup-'+uuid.uuid4().hex
                st,data=http('POST',mock.url+'/projects',{'project_id':setup_id,'config':source})
                if st not in (200,201,202) or data.get('config')!=source:
                    cases[case]={'outcome':'NOT_RUN','reason':'SETUP_FAILED','setup_status':st};continue
            cfg=copy.deepcopy(source)
            if case.endswith('.01'):del cfg['project']['name']
            if case.endswith('.05'):del cfg['project']['environments'][0]['tool_configuration']
            if case.endswith('.25'):del cfg['project']['defect_classes'][0]['name']
            pid='cts-'+uuid.uuid4().hex
            req,rsp=call(adapter,case,cfg,pid)
            surf=rsp['data']['sut'];ref=surf['body_ref']
            run,owner,raw=adapter.evidence[ref]
            if (run,owner)!=(req['run_id'],case) or hashlib.sha256(raw).hexdigest()!=surf['body_sha256']:
                cases[case]={'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'};continue
            body=json.loads(raw);accepted=surf['outcome']=='accepted'
            if case=='CT-CFG-001':
                s,stored=http('GET',mock.url+'/projects/'+quote(pid,safe=''))
                ok=accepted and s==200 and stored.get('config')==cfg
            else:
                field={'CT-CFG-025.01':'project.name','CT-CFG-025.05':'environments[0].tool_configuration',
                        'CT-CFG-025.25':'defect_classes[0].name'}[case]
                ok=not accepted and field in ' '.join(str(v) for v in body.values())
            cases[case]={'outcome':'PASS' if ok else 'FAIL','sut_outcome':surf['outcome'],'sut_status':surf['status'],
                         'evidence_ref':ref,'surface':'rest'}
    return {'scope':'S1_HTTP_MOCK_ONLY','cases':cases,'CT-CFG-025':summarize({k:v for k,v in cases.items() if k.startswith('CT-CFG-025.')})}
