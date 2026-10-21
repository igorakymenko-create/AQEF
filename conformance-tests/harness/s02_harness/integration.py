"""Stage C S0.2 HTTP integration of the scripted harness (non-normative prototype).

Only harness-local operations are implemented; SUT/Adapter operations return a
schema-valid ADAPTER_SURFACE_UNSUPPORTED error. No external network calls occur.
"""
from __future__ import annotations
import json, hashlib, os, pathlib, threading, time, uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse
import sys

HERE=pathlib.Path(__file__).resolve().parent
SCHEMA_TOOL=HERE.parent/'tools'
if str(SCHEMA_TOOL) not in sys.path:sys.path.insert(0,str(SCHEMA_TOOL))
import validate as v
from harness import Harness,ENDPOINTS

MAX_BODY=1024*1024

def encode(obj):return json.dumps(obj, ensure_ascii=False, separators=(',',':'), allow_nan=False).encode('utf-8')
def sha(raw):return hashlib.sha256(raw).hexdigest()

class Evidence:
    def __init__(self,root):
        self.root=pathlib.Path(root);self.root.mkdir(parents=True,exist_ok=True)
        self.entries=[];self.lock=threading.RLock()
    def put(self,raw,run_id,case_id,kind):
        with self.lock:
            eid=uuid.uuid4().hex
            name=eid+'.bin'
            p=self.root/name
            # Exclusive creation; no overwriting captured evidence.
            with p.open('xb') as f:f.write(raw)
            entry={'evidence_id':eid,'case_id':case_id,'kind':kind,'raw_ref':'evidence://'+name,
                   'raw_sha256':sha(raw),'raw_size':len(raw),'redaction_policy':'none',
                   'collected_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z')}
            self.entries.append((run_id,entry))
            return entry['raw_ref'],entry['raw_sha256']
    def manifest(self,run_id):
        body={'schema_version':'0.4','run_id':run_id,
              'created_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
              'canonicalization':'RFC8785','entries':[e for rid,e in self.entries if rid==run_id]}
        body['manifest_sha256']=sha(v.jcs(body).encode())
        return body

class App:
    def __init__(self,root):
        self.harness=Harness();self.evidence=Evidence(root)
        self.owner={};self.lock=threading.RLock()
    @staticmethod
    def resp(req, success, data=None, error=None, evidence_refs=None):
        x={'contract_version':'0.4','operation':req['operation'],'correlation_id':req['correlation_id'],'success':success}
        if success:x['data']=data if data is not None else {}
        else:x['error']=error
        if evidence_refs:x['evidence_refs']=evidence_refs
        return x
    @staticmethod
    def err(req,code,message,phase='action',origin='harness'):
        return App.resp(req,False,error={'origin':origin,'phase':phase,'code':code,'message':message,'retryable':False})
    def operation(self,req):
        err=v.schema_errors('adapter-operation.schema.json',req)
        if err:
            # Even malformed requests receive an explicitly non-contract HTTP 400 error.
            return 400,{'error':'SCHEMA_INVALID','details':err[:8]}
        sid=req['session_id'];op=req['operation'];arg=req['arguments'];run=req['run_id'];case=req['case_id']
        if op=='begin_case':
            if arg['case_id']!=case or not case.startswith(arg['test_id']):
                return 200,self.err(req,'SCHEMA_INVALID','case_id differs from request',phase='setup')
            with self.lock:
                if sid in self.owner:return 200,self.err(req,'HARNESS_SETUP_FAILED','session already exists',phase='setup')
                self.harness.begin(sid)
                self.owner[sid]=(run,case)
            return 200,self.resp(req,True,{'session_id':sid,'project_id':'s02-project-'+uuid.uuid4().hex})
        with self.lock:bound=self.owner.get(sid)
        if not bound:return 200,self.err(req,'HARNESS_SETUP_FAILED','unknown session',phase='setup')
        if bound!=(run,case):return 200,self.err(req,'SCHEMA_INVALID','session ownership mismatch')
        try:
            if op=='reset_harness':
                self.harness.reset(sid);data={'reset':True}
            elif op=='configure_behavior':
                endpoint=arg['endpoint_id'];kind='judge' if 'judge' in endpoint else 'subject'
                self.harness.configure(sid,kind,arg['behavior'],arg.get('applies','next_call'),endpoint)
                data={'configured':True,'endpoint_id':endpoint}
            elif op=='read_call_log':
                events=self.harness.read_log(sid,arg.get('after_sequence',0))
                if 'endpoint_id' in arg:events=[e for e in events if e.get('attributes',{}).get('endpoint_id')==arg['endpoint_id']]
                data={'events':events}
            elif op=='close_observation':
                data=self.harness.close_observation(sid,arg['drain_ms'])
            elif op=='end_case':
                data={'session_id':sid,'ended':True}
            elif op=='self_test':
                # A real comprehensive self_test is run by the separate unittest suite.
                return 200,self.err(req,'ADAPTER_SURFACE_UNSUPPORTED','self_test contract operation pending full CTS 2.8 behavior matrix',origin='adapter')
            else:
                return 200,self.err(req,'ADAPTER_SURFACE_UNSUPPORTED','SUT operation out of scope in S0.2',origin='adapter')
            return 200,self.resp(req,True,data)
        except (ValueError,KeyError,RuntimeError) as exc:
            return 200,self.err(req,'HARNESS_SETUP_FAILED',str(exc),phase='setup')
    def scripted(self, sid,kind,endpoint,body,correlation):
        with self.lock:bound=self.owner.get(sid)
        if not bound:return 404,{'error':'unknown session'}
        if kind not in ('subject','judge'):return 404,{'error':'unknown service'}
        run,case=bound
        payload=body
        raw_req=encode(payload)
        req_ref,_=self.evidence.put(raw_req,run,case,'harness_call')
        try:
            out=self.harness.invoke(sid,kind,payload,endpoint_id=endpoint,correlation_id=correlation)
        except RuntimeError as e:
            out={'outcome':'late_call','error':str(e)}
        raw_rsp=encode(out)
        rsp_ref,_=self.evidence.put(raw_rsp,run,case,'harness_response')
        return 200,dict(out,correlation_id=correlation,evidence_refs=[req_ref,rsp_ref])

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,address,app):
        super().__init__(address,Handler);self.app=app

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send_json(self,status,body):
        raw=encode(body);self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/health':return self.send_json(200,{'status':'ready','contract_version':'0.4'})
        if path.startswith('/manifests/'):
            run=unquote(path[len('/manifests/'):]);
            if not run or '/' in run:return self.send_json(400,{'error':'invalid run'})
            return self.send_json(200,self.server.app.evidence.manifest(run))
        return self.send_json(404,{'error':'not found'})
    def do_POST(self):
        length=self.headers.get('Content-Length','')
        if not length.isdecimal() or int(length)>MAX_BODY:return self.send_json(413,{'error':'invalid body length'})
        raw=self.rfile.read(int(length))
        try:body=json.loads(raw)
        except (UnicodeDecodeError,ValueError):return self.send_json(400,{'error':'invalid JSON'})
        path=urlparse(self.path).path
        if path=='/api/v0.4/operations':
            if not isinstance(body,dict):return self.send_json(400,{'error':'request must be an object'})
            status,resp=self.server.app.operation(body)
            if status==200:
                violations=v.schema_errors('adapter-response.schema.json',resp)
                if violations:return self.send_json(500,{'error':'response failed contract','details':violations})
            return self.send_json(status,resp)
        parts=path.strip('/').split('/')
        if len(parts)==4 and parts[0]=='sessions' and parts[2] in ('subject','judge') and parts[1]:
            sid,kind,endpoint=unquote(parts[1]),parts[2],unquote(parts[3])
            if not isinstance(body,dict):return self.send_json(400,{'error':'scripted request must be object'})
            correlation=self.headers.get('X-Correlation-ID') or uuid.uuid4().hex
            status,resp=self.server.app.scripted(sid,kind,endpoint,body,correlation)
            return self.send_json(status,resp)
        return self.send_json(404,{'error':'not found'})
