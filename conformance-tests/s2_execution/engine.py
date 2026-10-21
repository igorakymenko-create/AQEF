"""S2.1 isolated execution mock and independent assessor. Not AQEF conformance."""
import copy, hashlib, json, pathlib, sys, threading, uuid
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
BASE=pathlib.Path(__file__).resolve().parent.parent
for p in [BASE/'harness'/'s02_harness', BASE/'harness'/'tools',BASE/'s1_configuration']:
    sys.path.insert(0,str(p))
from harness import Harness
from mock import fixture_base
import validate as validator

def binary(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def http(method,url,data):
    req=Request(url,data=binary(data),method=method,headers={'Content-Type':'application/json'})
    try:
        with urlopen(req,timeout=8) as r:return r.status,json.loads(r.read())
    except HTTPError as e:return e.code,json.loads(e.read())

class Mock:
    def __init__(self,mutation=None):
        self.mutation=mutation;self.h=Harness();self.saved={};self.fixtures={}
    def prepare(self,sid,config,behavior):
        self.fixtures[sid]=(copy.deepcopy(config),behavior)
    def execute(self,sid,case):
        config,behavior=self.fixtures[sid]
        self.h.begin(sid);self.h.configure(sid,'subject',behavior)
        project=config['project'];prompt=project['suites'][0]['scenarios'][0]['variables']['query']
        retry=project.get('execution',{}).get('retry',{})
        max_calls=2 if retry.get('on')=='infrastructure_failure' and retry.get('max_attempts',0)>=2 else 1
        attempts=[]
        for _ in range(max_calls):
            answer=self.h.invoke(sid,'subject',{'prompt':prompt},correlation_id=case)
            attempts.append(answer)
            if answer['outcome']=='completed':break
            if answer['outcome'] not in ('http_error','unreachable'):break
        executions=[]
        if attempts[-1]['outcome']=='completed':
            resp=attempts[-1]['result']
            conversation={'messages':[{'role':'user','content':prompt},{'role':'assistant','content':resp}]}
            if self.mutation=='alter_prompt':conversation['messages'][0]['content']='OTHER'
            if self.mutation=='alter_response':conversation['messages'][1]['content']='OTHER'
            if self.mutation=='duplicate_conversation':conversation=[conversation,copy.deepcopy(conversation)]
            executions=[{'id':'execution-'+uuid.uuid4().hex,'conversation':conversation,
                         'results':[{'oracle_type':'validator','verdict':'pass'}]}]
        if self.mutation=='failed_attempt_record' and len(attempts)>1:
            executions.insert(0,{'id':'bad-attempt','conversation':{'messages':[]},'results':[{'verdict':'fail'}]})
        if self.mutation=='missing_conversation' and executions:executions[-1]['conversation']=None
        if self.mutation=='missing_execution':executions=[]
        if self.mutation=='duplicate_subject_call' and behavior=='SR-OK':
            self.h.invoke(sid,'subject',{'prompt':prompt},correlation_id=case+'-extra')
        self.saved[sid]={'executions':executions,'attempts':attempts}
        return {'terminal':'completed','execution_ids':[e['id'] for e in executions]}

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,status,obj):
        raw=binary(obj);self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_POST(self):
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<0 or n>1000000:return self.reply(413,{'error':'body size'})
            req=json.loads(self.rfile.read(n))
        except (ValueError,UnicodeDecodeError):return self.reply(400,{'error':'invalid json'})
        if self.path!='/api/v0.4/operations':return self.reply(404,{'error':'not found'})
        issues=validator.schema_errors('adapter-operation.schema.json',req)
        if issues:return self.reply(400,{'error':'SCHEMA_INVALID','details':issues[:3]})
        if req['operation']!='execute':
            return self.reply(200,{'contract_version':'0.4','operation':req['operation'],
                   'correlation_id':req['correlation_id'],'success':False,'error':{
                   'origin':'adapter','phase':'action','code':'ADAPTER_SURFACE_UNSUPPORTED',
                   'message':'S2.1 execute only','retryable':False}})
        try:
            response=self.server.mock.execute(req['session_id'],req['case_id'],
                          )
        except (KeyError,ValueError,TypeError) as e:
            return self.reply(200,{'contract_version':'0.4','operation':'execute',
                 'correlation_id':req['correlation_id'],'success':False,
                 'error':{'origin':'adapter','phase':'setup','code':'HARNESS_SETUP_FAILED',
                          'message':str(e),'retryable':False}})
        ref='evidence://s21-'+uuid.uuid4().hex;raw=binary(response)
        self.server.evidence[ref]=(req['run_id'],req['case_id'],raw)
        result={'contract_version':'0.4','operation':'execute','correlation_id':req['correlation_id'],
                'success':True,'data':{'sut':{'outcome':'accepted','status':200,'body_ref':ref,
                'body_sha256':digest(raw),'surface':'equivalent'}},'evidence_refs':[ref]}
        issues=validator.schema_errors('adapter-response.schema.json',result)
        return self.reply(500,{'error':'RESPONSE_SCHEMA','details':issues}) if issues else self.reply(200,result)

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,mock):
        super().__init__(('127.0.0.1',0),Handler);self.mock=mock;self.evidence={}
    @property
    def url(self):return 'http://127.0.0.1:'+str(self.server_port)

@contextmanager
def service(mutation=None):
    mock=Mock(mutation);server=Server(mock)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield mock,server
    finally:server.shutdown();server.server_close();thread.join(timeout=2)

def run_case(case,mutation=None,damage_evidence=False):
    if case not in ('CT-EXE-003','CT-EXE-008'):raise ValueError('unsupported CTS case')
    with service(mutation) as (mock,server):
        cfg=fixture_base();behavior='SR-503-THEN-OK' if case=='CT-EXE-003' else 'SR-OK'
        if case=='CT-EXE-003':cfg['project']['execution']={'retry':{'max_attempts':2,'on':'infrastructure_failure'}}
        sid='session-'+uuid.uuid4().hex
        mock.prepare(sid,cfg,behavior)
        req={'contract_version':'0.4','operation':'execute','run_id':'run-'+uuid.uuid4().hex,
             'case_id':case,'session_id':sid,'correlation_id':'corr-'+uuid.uuid4().hex,
             'timeout_ms':10000,'arguments':{'project_id':'cts-execution-'+uuid.uuid4().hex,'suite':'cts-suite','environment':'cts-env'}}
        issues=validator.schema_errors('adapter-operation.schema.json',req)
        if issues:return {'outcome':'NOT_RUN','reason':'REQUEST_INVALID','diagnostic':issues}
        status,rsp=http('POST',server.url+'/api/v0.4/operations',req)
        if status!=200 or validator.schema_errors('adapter-response.schema.json',rsp):
            return {'outcome':'NOT_RUN','reason':'ADAPTER_CONTRACT_INVALID','status':status}
        if not rsp['success']:return {'outcome':'NOT_RUN','reason':'SETUP_FAILED'}
        data=rsp['data']['sut'];ref=data['body_ref']
        if damage_evidence:
            rid,cid,raw=server.evidence[ref];server.evidence[ref]=(rid,cid,raw+b'!')
        try:
            rid,cid,raw=server.evidence[ref]
            assert (rid,cid)==(req['run_id'],case) and digest(raw)==data['body_sha256']
            assert json.loads(raw)['terminal']=='completed'
        except (AssertionError,KeyError,ValueError):return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'}
        records=mock.saved[req['session_id']]['executions']
        events=mock.h.read_log(req['session_id'])
        calls=[ev for ev in events if ev['type']=='call_received' and ev['attributes']['kind']=='subject']
        if case=='CT-EXE-003':
            ok=(len(calls)==2 and len(records)==1 and isinstance(records[0]['conversation'],dict)
                and records[0]['conversation'].get('messages',[None,None])[-1]==
                {'role':'assistant','content':'Hello! How can I help?'} and len(records[0]['results'])>0)
        else:
            correct=[{'role':'user','content':'Hello'},
                     {'role':'assistant','content':'Hello! How can I help?'}]
            ok=(len(calls)==1 and len(records)==1 and isinstance(records[0]['conversation'],dict)
                and records[0]['conversation'].get('messages')==correct)
        return {'outcome':'PASS' if ok else 'FAIL','reason':'EXPECTED_MET' if ok else 'EXPECTED_VIOLATED',
                'subject_calls':len(calls),'executions':len(records)}
