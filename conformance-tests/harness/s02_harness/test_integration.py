"""HTTP, contract-envelope, concurrency, evidence and negative tests for S0.2."""
import copy, json, pathlib, tempfile, threading, time, unittest, urllib.request, urllib.error, uuid
from concurrent.futures import ThreadPoolExecutor
from integration import App,Server, v

class Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.app=App(cls.tmp.name)
        cls.http=Server(('127.0.0.1',0),cls.app)
        cls.base=f'http://127.0.0.1:{cls.http.server_port}'
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.thread.join();cls.tmp.cleanup()
    def request(self,method,path,obj=None,headers=None):
        data=json.dumps(obj).encode() if obj is not None else None
        req=urllib.request.Request(self.base+path,data=data,method=method,headers=headers or {})
        try:
            with urllib.request.urlopen(req,timeout=8) as resp:return resp.status,json.loads(resp.read())
        except urllib.error.HTTPError as e:return e.code,json.loads(e.read())
    def op(self,op,args=None,sid=None,run=None,case='CT-ASM-001',corr=None,**changes):
        q={'contract_version':'0.4','operation':op,'run_id':run or 'r-'+uuid.uuid4().hex,
           'case_id':case,'session_id':sid or 's-'+uuid.uuid4().hex,
           'correlation_id':corr or uuid.uuid4().hex,'timeout_ms':10000,'arguments':args or {}}
        q.update(changes);return q
    def begun(self,case='CT-ASM-001',run=None):
        run=run or 'r-'+uuid.uuid4().hex;sid='s-'+uuid.uuid4().hex
        r=self.op('begin_case',{'test_id':case.split('.')[0],'case_id':case},sid,run,case)
        st,out=self.request('POST','/api/v0.4/operations',r)
        self.assertEqual((st,out['success']),(200,True),out)
        self.assertFalse(v.schema_errors('adapter-response.schema.json',out))
        return sid,run,case
    def operate(self,op,args,sid,run,case='CT-ASM-001'):
        req=self.op(op,args,sid,run,case);st,out=self.request('POST','/api/v0.4/operations',req)
        self.assertEqual(st,200,out)
        self.assertFalse(v.schema_errors('adapter-response.schema.json',out),out)
        self.assertEqual(out['correlation_id'],req['correlation_id'])
        return out
    def scripted(self,sid,kind,endpoint,payload,correlation=None):
        return self.request('POST',f'/sessions/{sid}/{kind}/{endpoint}',payload,
            {'X-Correlation-ID':correlation or uuid.uuid4().hex})
    def test_health(self):
        self.assertEqual(self.request('GET','/health')[1]['contract_version'],'0.4')
    def test_begin_and_envelope(self):
        self.begun()
    def test_invalid_version_rejected(self):
        r=self.op('begin_case',{'test_id':'CT-ASM-001','case_id':'CT-ASM-001'},contract_version='0.3')
        st,out=self.request('POST','/api/v0.4/operations',r)
        self.assertEqual(st,400);self.assertEqual(out['error'],'SCHEMA_INVALID')
    def test_malformed_arguments_rejected(self):
        r=self.op('begin_case',{},case='CT-ASM-001');st,out=self.request('POST','/api/v0.4/operations',r)
        self.assertEqual(st,400)
    def test_invalid_json_rejected(self):
        req=urllib.request.Request(self.base+'/api/v0.4/operations',data=b'{',method='POST')
        with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(req)
        self.assertEqual(e.exception.code,400)
    def test_unknown_session_returns_contract_error(self):
        q=self.op('reset_harness',{},sid='missing')
        st,out=self.request('POST','/api/v0.4/operations',q)
        self.assertFalse(out['success']);self.assertEqual(out['error']['code'],'HARNESS_SETUP_FAILED')
    def test_wrong_ownership_rejected(self):
        sid,run,case=self.begun()
        out=self.operate('read_call_log',{},sid,run+'other',case)
        self.assertFalse(out['success']);self.assertEqual(out['error']['code'],'SCHEMA_INVALID')
    def test_unsupported_operation_fails_closed(self):
        sid,run,case=self.begun()
        out=self.operate('execute',{'project_id':'cts-test-project','suite':'cts-suite','environment':'cts-env'},sid,run,case)
        self.assertFalse(out['success']);self.assertEqual(out['error']['code'],'ADAPTER_SURFACE_UNSUPPORTED')
    def test_scripted_subject_and_log_correlation(self):
        sid,run,case=self.begun()
        corr='external-correlation-test'
        st,out=self.scripted(sid,'subject','cts-scripted-subject@1',{'prompt':'hi'},corr)
        self.assertEqual(st,200);self.assertEqual(out['correlation_id'],corr)
        self.assertEqual(out['result'],'Hello! How can I help?')
        events=self.operate('read_call_log',{},sid,run,case)['data']['events']
        calls=[e for e in events if e['type']=='call_received']
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0]['attributes']['correlation_id'],corr)
        self.assertEqual([e['sequence'] for e in events],list(range(1,len(events)+1)))
    def test_endpoint_scoped_behavior(self):
        sid,run,case=self.begun()
        self.assertTrue(self.operate('configure_behavior',{'endpoint_id':'subject-one','behavior':'SR-ECHO'},sid,run,case)['success'])
        st,a=self.scripted(sid,'subject','subject-one',{'prompt':'ONE'})
        st,b=self.scripted(sid,'subject','subject-two',{'prompt':'TWO'})
        self.assertEqual(a['result'],'ONE');self.assertEqual(b['result'],'Hello! How can I help?')
    def test_judge_scenario(self):
        sid,run,case=self.begun()
        out=self.operate('configure_behavior',{'endpoint_id':'cts-scripted-judge@1','behavior':'J-CATCH'},sid,run,case)
        self.assertTrue(out['success'])
        _,a=self.scripted(sid,'judge','cts-scripted-judge@1',{'response':'Goodbye.'})
        _,b=self.scripted(sid,'judge','cts-scripted-judge@1',{'response':'Hello!'})
        self.assertEqual((a['result']['verdict'],b['result']['verdict']),('fail','pass'))
    def test_per_session_isolation_parallel(self):
        a,ra,c=self.begun();b,rb,_=self.begun()
        self.operate('configure_behavior',{'endpoint_id':'sub','behavior':'SR-ECHO'},a,ra,c)
        def call(s,p):return self.scripted(s,'subject','sub',{'prompt':p})[1]
        with ThreadPoolExecutor(max_workers=2) as pool:
            fa=pool.submit(call,a,'A');fb=pool.submit(call,b,'B')
            xa,xb=fa.result(),fb.result()
        self.assertEqual(xa['result'],'A');self.assertNotEqual(xb['result'],'B')
        ea=self.operate('read_call_log',{},a,ra,c)['data']['events']
        eb=self.operate('read_call_log',{},b,rb,c)['data']['events']
        self.assertEqual(sum(x['type']=='call_received' for x in ea),1)
        self.assertEqual(sum(x['type']=='call_received' for x in eb),1)
    def test_reset_restores_behavior(self):
        sid,run,case=self.begun()
        self.operate('configure_behavior',{'endpoint_id':'sub','behavior':'SR-ECHO'},sid,run,case)
        self.assertEqual(self.scripted(sid,'subject','sub',{'prompt':'A'})[1]['result'],'A')
        self.assertTrue(self.operate('reset_harness',{},sid,run,case)['success'])
        self.assertNotEqual(self.scripted(sid,'subject','sub',{'prompt':'B'})[1]['result'],'B')
    def test_terminal_error_without_500(self):
        sid,run,case=self.begun()
        st,out=self.request('POST','/api/v0.4/operations',self.op('close_observation',{'drain_ms':-1},sid,run,case))
        self.assertEqual(st,400)
    def test_close_waits_and_late_call(self):
        sid,run,case=self.begun()
        begin=time.monotonic()
        out=self.operate('close_observation',{'drain_ms':35},sid,run,case)
        self.assertTrue(out['success']);self.assertGreaterEqual(time.monotonic()-begin,.03)
        self.assertEqual(out['data']['state'],'observation_closed')
        st,late=self.scripted(sid,'subject','sub',{'prompt':'late'})
        self.assertEqual(late['outcome'],'late_call')
        ev=self.operate('read_call_log',{},sid,run,case)['data']['events']
        self.assertTrue(any(x['type']=='late_call' for x in ev))
    def test_evidence_manifest_checks_actual_bytes(self):
        sid,run,case=self.begun()
        _,res=self.scripted(sid,'subject','sub',{'prompt':'x'})
        m=self.request('GET','/manifests/'+run)[1]
        self.assertEqual(len(m['entries']),2)
        self.assertEqual(v.check_manifest(m,self.app.evidence.root),[])
        self.assertEqual(len(res['evidence_refs']),2)
    def test_evidence_tamper_detected(self):
        sid,run,case=self.begun()
        self.scripted(sid,'subject','sub',{'prompt':'x'})
        m=self.request('GET','/manifests/'+run)[1]
        ref=m['entries'][0]['raw_ref'].split('://',1)[1]
        p=pathlib.Path(self.tmp.name)/ref
        p.write_bytes(p.read_bytes()+b'X')
        self.assertTrue(any('digest' in e or 'bytes' in e for e in v.check_manifest(m,self.app.evidence.root)))
    def test_no_external_requests_for_scripted_tools(self):
        sid,run,case=self.begun()
        self.operate('configure_behavior',{'endpoint_id':'sub','behavior':'SR-CALL(https://cts-outside.example/x)'},sid,run,case)
        out=self.scripted(sid,'subject','sub',{'prompt':'x'})[1]
        self.assertFalse(out['result']['executed'])
    def test_fault_503_then_ok(self):
        sid,run,case=self.begun()
        self.operate('configure_behavior',{'endpoint_id':'sub','behavior':'SR-503-THEN-OK'},sid,run,case)
        a=self.scripted(sid,'subject','sub',{})[1]
        b=self.scripted(sid,'subject','sub',{})[1]
        self.assertEqual((a['outcome'],b['outcome']),('http_error','completed'))
    def test_response_kind_and_correlations(self):
        sid,run,case=self.begun()
        for op,args in [('read_call_log',{}),('end_case',{}),('reset_harness',{})]:
            out=self.operate(op,args,sid,run,case)
            self.assertTrue(out['success'])

if __name__=='__main__':unittest.main()
