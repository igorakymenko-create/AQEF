"""CT-SDK-001 proxy-observed mock orchestration and independent CTS assessor.

Not a production CLI or real Appendix C server. All observed operations must come
through a separate subprocess hitting an actual localhost HTTP recording server.
"""
from __future__ import annotations
import copy, json, pathlib, subprocess, sys, tempfile, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from contextlib import contextmanager

ROOT=pathlib.Path(__file__).resolve().parent
EXPECTED={'load-config':'load_config','execute':'execute','evaluate-gates':'evaluate_gates'}
CAPABILITY='cli'

class MockREST:
    def __init__(self,mutation=None):
        self.mutation=mutation;self.config=None;self.execution=None;self.gate=None;self.calls=[]
    def handle(self,op,args):
        self.calls.append({'operation':op,'arguments':copy.deepcopy(args)})
        if op=='load_config':
            self.config=copy.deepcopy(args['config'])
            return {'status':'accepted','config_id':'cfg-base'}
        if op=='execute':
            if self.config is None:raise ValueError('CONFIG_NOT_LOADED')
            self.execution='execution-cts';return {'status':'completed','execution_ids':[self.execution],'batch_id':'batch-cts'}
        if op=='evaluate_gates':
            if self.execution is None:raise ValueError('NO_EXECUTION')
            self.gate={'status':'pass','execution_id':self.execution,'name':'semantic-gate'}
            return {'gate':copy.deepcopy(self.gate)}
        raise ValueError('UNKNOWN_OPERATION')

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_POST(self):
        if self.path!='/api/v0.4/operations':self.send_error(404);return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<1000000:raise ValueError('INVALID_SIZE')
            payload=json.loads(self.rfile.read(size))
            if set(payload)!={'operation','arguments'} or not isinstance(payload['arguments'],dict):raise ValueError('INVALID_ENVELOPE')
            with self.server.lock: reply=self.server.model.handle(payload['operation'],payload['arguments'])
            status=200;data={'success':True,'operation':payload['operation'],'data':reply}
        except (ValueError,KeyError,TypeError) as err:status=400;data={'success':False,'error':str(err)}
        b=json.dumps(data,sort_keys=True).encode();self.send_response(status)
        self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)))
        self.end_headers();self.wfile.write(b)

@contextmanager
def proxy(mutation=None):
    server=ThreadingHTTPServer(('127.0.0.1',0),ProxyHandler)
    server.model=MockREST(mutation);server.lock=threading.Lock()
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:yield server,'http://127.0.0.1:'+str(server.server_port)+'/api/v0.4/operations'
    finally:server.shutdown();server.server_close();t.join(timeout=3)

def inspect_documented_commands(commands):
    if not isinstance(commands,dict) or not commands:return {'outcome':'NOT_RUN','reason':'CLI_DOCUMENTATION_UNAVAILABLE'}
    if any(not isinstance(k,str) or not isinstance(v,str) or v not in {'load_config','execute','evaluate_gates','get_results','get_conversation','poll_execution','get_report','review_result','override_gate','record_release','describe','begin_case','end_case','cleanup','reset_harness','configure_behavior','read_call_log','inject_failure','clock_capabilities','self_test','close_observation','provision_principal','reassess_result','raw_request'} for k,v in commands.items()):
        return {'outcome':'FAIL','reason':'CLI_COMMAND_WITHOUT_REST_COUNTERPART'}
    if not all(commands.get(cmd)==op for cmd,op in EXPECTED.items()):
        return {'outcome':'FAIL','reason':'CLI_COMMAND_MAPPING_INVALID'}
    return {'outcome':'PASS','reason':'COMMANDS_MAPPED'}

def assess(*,claimed,documented,records,outputs,errors=None):
    if not claimed:return {'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_UNCLAIMED'}
    doc=inspect_documented_commands(documented)
    if doc['outcome']!='PASS':return doc
    if not isinstance(records,list):return {'outcome':'NOT_RUN','reason':'PROXY_LOG_UNAVAILABLE'}
    if records==[] and outputs==[]:return {'outcome':'NOT_RUN','reason':'CLI_AND_PROXY_OBSERVATION_MISSING'}
    if not isinstance(outputs,list):return {'outcome':'NOT_RUN','reason':'CLI_OUTPUT_UNAVAILABLE'}
    ops=[x.get('operation') for x in records if isinstance(x,dict)]
    if ops!=list(EXPECTED.values()):return {'outcome':'FAIL','reason':'REST_OPERATION_TRACE_MISMATCH','observed':ops}
    if errors:return {'outcome':'NOT_RUN','reason':'CLI_EXECUTION_UNAVAILABLE'}
    if len(outputs)!=3:return {'outcome':'NOT_RUN','reason':'CLI_OUTPUT_UNAVAILABLE'}
    expected_args=[{'project_id','config'},{'project_id','suite','environment'},{'project_id','batch_id'}]
    if any(set(x.get('arguments',{}))!=req for x,req in zip(records,expected_args)):
        return {'outcome':'FAIL','reason':'REST_OPERATION_ARGUMENTS_INVALID'}
    if not all(isinstance(o,dict) and o.get('success') is True for o in outputs):
        return {'outcome':'FAIL','reason':'CLI_OUTPUT_INVALID'}
    if outputs[0]['data'].get('config_id')!='cfg-base' or outputs[1]['data'].get('execution_ids')!=['execution-cts'] or outputs[2]['data'].get('gate',{}).get('execution_id')!='execution-cts':
        return {'outcome':'FAIL','reason':'REST_OUTPUT_MISMATCH'}
    return {'outcome':'PASS','reason':'EXPECTED_MET','observed_operations':ops}

def run_ct_sdk_001(*,claimed=True,mutation=None,documented=None):
    if not claimed:return assess(claimed=False,documented={},records=[],outputs=[])
    if documented is None: documented=dict(EXPECTED)
    from cli import DOCUMENTED_COMMANDS
    fixture={'project':{'name':'F-BASE','suites':[{'name':'cts-suite','scenarios':[{'name':'s-greeting','variables':{'query':'Hello'}}]}]}}
    outputs=[];errors=[]
    with tempfile.TemporaryDirectory(prefix='aqef-s42-') as folder:
        path=pathlib.Path(folder)/'f-base.json';path.write_text(json.dumps(fixture))
        with proxy() as (server,url):
            calls=[['load-config','--project-id','cts-project','--fixture',str(path)],
                   ['execute','--project-id','cts-project','--suite','cts-suite','--environment','cts-env'],
                   ['evaluate-gates','--project-id','cts-project','--batch-id','batch-cts']]
            for i,cmd in enumerate(calls):
                if mutation=='skip_rest_execute' and i==1:
                    outputs.append({'success':True,'data':{'execution_ids':['execution-cts']}});continue
                if mutation=='skip_rest_gate' and i==2:
                    outputs.append({'success':True,'data':{'gate':{'execution_id':'execution-cts'}}});continue
                if mutation=='wrong_rest_operation' and i==2:cmd[0]='execute';cmd=cmd[:1]+['--project-id','cts-project','--suite','cts-suite','--environment','cts-env']
                cp=subprocess.run([sys.executable,str(ROOT/'cli.py'),'--api',url,*cmd],capture_output=True,text=True,timeout=8)
                if cp.returncode!=0:errors.append(cp.stderr);break
                try:outputs.append(json.loads(cp.stdout))
                except json.JSONDecodeError:errors.append('JSON_INVALID');break
            records=copy.deepcopy(server.model.calls)
    if mutation=='extra_rest_call':records.append({'operation':'get_results','arguments':{'project_id':'cts-project'}})
    if mutation=='wrong_proxy_args' and records:records[0]['arguments']['unexpected']='secret'
    if mutation=='missing_proxy_log':records=None
    if mutation=='cli_output_fabricated' and len(outputs)==3:outputs[2]['data']['gate']['execution_id']='other-execution'
    return assess(claimed=claimed,documented=documented,records=records,outputs=outputs,errors=errors)

def trace_matrix():
    modes={'healthy':{},'bypass_execute':{'mutation':'skip_rest_execute'},'bypass_gate':{'mutation':'skip_rest_gate'},
           'extra_rest_call':{'mutation':'extra_rest_call'},'wrong_proxy_args':{'mutation':'wrong_proxy_args'},
           'missing_proxy_log':{'mutation':'missing_proxy_log'},'unclaimed':{'claimed':False},
           'unmapped_command':{'documented':{**EXPECTED,'mystery':'not_appendix_c'}}}
    return {'scope':'S4.2_CT_SDK_001_MOCK_ONLY','cases':{key:run_ct_sdk_001(**kwargs) for key,kwargs in modes.items()}}
