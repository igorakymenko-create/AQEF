"""Stage C S3.5.4: mock-only HTTP operation facade + independently resolved Evidence.

NOT a real AQEF SUT. HTTP responses carry opaque evidence refs, not direct trusted
SUT data. Expected receipts are captured on the runner side, outside the mutable
object directory. The authentication of that trust anchor is outside this slice.
"""
from __future__ import annotations
import copy, json, pathlib, sys, tempfile, threading, uuid
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=pathlib.Path(__file__).resolve().parent.parent
for p in ('s35_resolution','s35_evidence','s35_integration','s1_configuration','s2_execution'):
    sys.path.insert(0,str(ROOT/p))
from governance import GovernedPipeline
from evidence import EvidenceStore, EvidenceResolver, canonical, sha256
from mock import fixture_base
from engine import http, validator

OPERATIONS=('execute','get_conversation','get_results','evaluate_gates',
            'review_result','override_gate','record_release')
PROJECT='cts-project'
CASE='CT-DEC-012'


def request(op,session,run,case,correlation=None,actor=None,**arguments):
    item={'contract_version':'0.4','operation':op,'run_id':run,'case_id':case,
          'session_id':session,'correlation_id':correlation or 'corr-'+uuid.uuid4().hex,
          'timeout_ms':10000,'arguments':{'project_id':PROJECT,**arguments}}
    if actor is not None:item['actor_ref']=actor
    return item


def checked_request(op,session,run,case,**kwargs):
    x=request(op,session,run,case,**kwargs)
    errors=validator.schema_errors('adapter-operation.schema.json',x)
    if errors:raise ValueError('INVALID_ADAPTER_REQUEST: '+str(errors[:2]))
    return x

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def respond(self,code,obj):
        data=canonical(obj)
        self.send_response(code);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!='/api/v0.4/operations':return self.respond(404,{'error':'not found'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n<0 or n>1000000:return self.respond(413,{'error':'too large'})
            req=json.loads(self.rfile.read(n))
        except (ValueError,UnicodeDecodeError):return self.respond(400,{'error':'bad json'})
        issues=validator.schema_errors('adapter-operation.schema.json',req)
        if issues:return self.respond(400,{'error':'SCHEMA_INVALID','issues':issues[:2]})
        op=req['operation']
        if op not in OPERATIONS:return self.respond(400,{'error':'UNSUPPORTED_OPERATION'})
        try:
            owner=(req['run_id'],req['case_id'],req['session_id'])
            with self.server.state_lock:
                if self.server.owner is None:
                    if op!='execute':return self.respond(409,{'error':'EXECUTE_FIRST'})
                    self.server.owner=owner
                elif owner!=self.server.owner:
                    return self.respond(403,{'error':'OWNER_MISMATCH'})
                model=self.server.model
                sid=req['session_id'];args=req['arguments']
                if op=='execute':
                    if self.server.execution is not None:return self.respond(409,{'error':'ALREADY_EXECUTED'})
                    model.prepare_pipeline(sid,fixture_base(),'SR-OK',self.server.judge,'schema')
                    terminal=model.execute(sid,req['case_id'])
                    if terminal.get('terminal')!='completed' or len(terminal['execution_ids'])!=1:
                        return self.respond(409,{'error':'EXECUTION_NOT_COMPLETED'})
                    ex=model.saved[sid]['executions'][0]
                    self.server.execution=ex['id']
                    body={'terminal':terminal['terminal'],'execution_ids':terminal['execution_ids']}
                else:
                    xid=args.get('execution_id',self.server.execution)
                    if xid!=self.server.execution:return self.respond(404,{'error':'EXECUTION_NOT_FOUND'})
                    ex=model.saved_by_execution(xid)
                    if op=='get_conversation':body={'execution_id':xid,'conversation':copy.deepcopy(ex['conversation'])}
                    elif op=='get_results':
                        keys=sorted((clause for eid,clause in model.resolutions if eid==xid))
                        body={'execution_id':xid,'results':copy.deepcopy(ex['results']),
                              'effective':{clause:model.effective(xid,clause) for clause in keys}}
                    elif op=='evaluate_gates':
                        # Evaluate only when explicitly requested, producing a fresh GateResult.
                        body={'execution_id':xid,'gate':model.reevaluate(xid)}
                    elif op=='review_result':
                        target=args['result_id']
                        clause=next((r['clause'] for r in ex['results'] if r['id']==target),None)
                        if clause is None:return self.respond(404,{'error':'RESULT_NOT_FOUND'})
                        body=model.review(req.get('actor_ref',''),xid,clause,target,args['verdict'])
                    elif op=='override_gate':
                        body=model.approve_override(req.get('actor_ref',''),xid,args['gate_result_id'],args['justification'])
                    elif op=='record_release':
                        body=model.record_release(req.get('actor_ref',''),xid,
                             args['body'].get('decision','overridden'),args['body'].get('approval_id'))
                # Keep all operation readbacks as raw + redacted for independent resolution.
                raw=canonical(body)
                redacted=canonical({'operation':op,'execution_id':self.server.execution,
                                    'payload_sha256':sha256(raw),'redacted':True})
                receipts={kind:self.server.store.put(run_id=req['run_id'],case_id=req['case_id'],
                    correlation_id=req['correlation_id'],kind=kind,body=data)
                    for kind,data in (('raw',raw),('redacted',redacted))}
                self.server.receipts[req['correlation_id']]=copy.deepcopy(receipts)
                receipt=receipts['raw']
                result={'contract_version':'0.4','operation':op,'correlation_id':req['correlation_id'],
                        'success':True,'data':{'sut':{'outcome':'accepted','status':200,
                            'body_ref':receipt['ref'],'body_sha256':receipt['sha256'],
                            'surface':'equivalent'}},'evidence_refs':[receipts['raw']['ref'],receipts['redacted']['ref']]}
                errors=validator.schema_errors('adapter-response.schema.json',result)
                if errors:return self.respond(500,{'error':'ADAPTER_RESPONSE_SCHEMA','issues':errors[:2]})
                return self.respond(200,result)
        except (KeyError,TypeError,ValueError) as err:
            return self.respond(409,{'error':'OPERATION_FAILED','detail':str(err)})

class Server(ThreadingHTTPServer):
    daemon_threads=True
    def __init__(self,model,store,judge):
        super().__init__(('127.0.0.1',0),Handler)
        self.model=model;self.store=store;self.judge=judge
        self.owner=None;self.execution=None;self.receipts={}
        self.state_lock=threading.RLock()
    @property
    def url(self):return 'http://127.0.0.1:'+str(self.server_port)+'/api/v0.4/operations'

@contextmanager
def service(*,judge='J-PASS-60',mutation=None):
    with tempfile.TemporaryDirectory(prefix='aqef-s354-') as tmp:
        server=Server(GovernedPipeline(mutation),EvidenceStore(tmp),judge)
        t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
        try:yield server,tmp
        finally:server.shutdown();server.server_close();t.join(timeout=3)


def exchange(server,op,session,run,case,**kwargs):
    """Independent client receives an adapter envelope and resolves *disk* evidence."""
    try:req=checked_request(op,session,run,case,**kwargs)
    except ValueError:return {'outcome':'NOT_RUN','reason':'ADAPTER_REQUEST_INVALID'}
    try:status,rsp=http('POST',server.url,req)
    except (OSError,ValueError):return {'outcome':'NOT_RUN','reason':'ADAPTER_UNAVAILABLE'}
    if status!=200 or validator.schema_errors('adapter-response.schema.json',rsp) or not rsp.get('success'):
        return {'outcome':'NOT_RUN','reason':'ADAPTER_RESPONSE_INVALID','status':status}
    # Trust assumption: capture an independent immutable copy of receipts as the
    # runner-side manifest. NEVER treat the SUT response's own hash as sole authority.
    receipts=copy.deepcopy(server.receipts.get(req['correlation_id']))
    return {'outcome':'PASS','request':req,'response':rsp,'receipts':receipts}


def readback(exchange_result,store_dir,*,damage=None,owner_override=None):
    """Separate resolver object, reads file bytes; mutation of snapshots => NOT_RUN."""
    if exchange_result['outcome']!='PASS':return exchange_result
    req=exchange_result['request'];rsp=exchange_result['response']
    receipts=copy.deepcopy(exchange_result['receipts'])
    if damage=='receipt_hash':receipts['raw']['sha256']='0'*64
    if damage=='wrong_owner':receipts['raw']['run_id']='other-run'
    if owner_override is not None:receipts=owner_override
    from evidence import verify_bundle
    verified=verify_bundle(EvidenceResolver(store_dir),receipts,run_id=req['run_id'],
                           case_id=req['case_id'],correlation_id=req['correlation_id'])
    if verified['outcome']!='PASS':return {'outcome':'NOT_RUN','reason':verified['reason']}
    raw=verified['objects']['raw'];red=verified['objects']['redacted']
    if rsp['data']['sut']['body_ref']!=receipts['raw']['ref'] or rsp['data']['sut']['body_sha256']!=sha256(raw):
        return {'outcome':'NOT_RUN','reason':'ADAPTER_EVIDENCE_MISMATCH'}
    if rsp.get('evidence_refs')!=[receipts['raw']['ref'],receipts['redacted']['ref']]:
        return {'outcome':'NOT_RUN','reason':'ADAPTER_EVIDENCE_REFS_MISMATCH'}
    try:
        decoded=json.loads(raw);summary=json.loads(red)
        if not isinstance(decoded,dict) or summary['payload_sha256']!=sha256(raw) or summary['operation']!=req['operation']:
            return {'outcome':'NOT_RUN','reason':'REDACTED_PAYLOAD_MISMATCH'}
    except (ValueError,TypeError,KeyError):return {'outcome':'NOT_RUN','reason':'EVIDENCE_PAYLOAD_INVALID'}
    return {'outcome':'PASS','body':decoded,'request':req,'response':rsp}
