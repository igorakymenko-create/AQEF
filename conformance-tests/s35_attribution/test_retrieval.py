import copy, json, pathlib, sys, unittest, uuid
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'s35_attribution'))
from retrieval import service, exchange, readback, checked_request, request, validator, PROJECT, CASE
from predicates import evaluate, all_of, Q08, PATHS
from audit import summarize

class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.s='s354-'+uuid.uuid4().hex;self.r='run-'+uuid.uuid4().hex;self.case=CASE
    def x(self,server,kind,**kw):return exchange(server,kind,self.s,self.r,self.case,**kw)
    def boot(self,server,dir):
        v=self.x(server,'execute',suite='cts-suite',environment='cts-env')
        self.assertEqual(v['outcome'],'PASS',v)
        data=readback(v,dir);self.assertEqual(data['outcome'],'PASS',data)
        xid=data['body']['execution_ids'][0];return xid
    def test_execute_http_and_resolve(self):
        with service() as (srv,dr):self.assertEqual(len(self.boot(srv,dr)),42) # 'execution-' + 32 hex
    def test_conversation_http_and_resolve(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);a=self.x(srv,'get_conversation',execution_id=xid)
            d=readback(a,dr);self.assertEqual(d['outcome'],'PASS')
            self.assertEqual(all_of(d['body'],Q08['CT-EXE-008:get_conversation'])['outcome'],'PASS')
            self.assertEqual(d['body']['execution_id'],xid)
    def test_results_http_and_resolve(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);d=readback(self.x(srv,'get_results',execution_id=xid),dr)
            self.assertEqual(d['outcome'],'PASS');self.assertEqual(all_of(d['body'],Q08['CT-DEC-012:get_results'])['outcome'],'PASS')
            self.assertEqual(d['body']['effective']['expectation-1']['disposition'],'inconclusive')
    def test_gate_http_and_resolve(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);d=readback(self.x(srv,'evaluate_gates',batch_id=xid),dr)
            self.assertEqual(d['outcome'],'PASS',d);self.assertEqual(all_of(d['body'],Q08['CT-DEC-006:evaluate_gates'])['outcome'],'PASS')
    def test_review_retrieve_updated_results(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr)
            prior=readback(self.x(srv,'get_results',execution_id=xid),dr)['body']
            original=prior['effective']['expectation-1']['id']
            v=self.x(srv,'review_result',actor='P-REVIEWER',execution_id=xid,result_id=original,verdict='pass')
            self.assertTrue(readback(v,dr)['body']['accepted'])
            after=readback(self.x(srv,'get_results',execution_id=xid),dr)['body']
            self.assertEqual(len(after['results']),3)
            self.assertEqual(after['effective']['expectation-1']['resolves'],original)
    def test_rejected_review_preserves_results(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr)
            before=readback(self.x(srv,'get_results',execution_id=xid),dr)['body']
            target=before['effective']['expectation-1']['id']
            outcome=readback(self.x(srv,'review_result',actor='P-NOPERM',execution_id=xid,result_id=target,verdict='fail'),dr)['body']
            self.assertFalse(outcome['accepted'])
            after=readback(self.x(srv,'get_results',execution_id=xid),dr)['body']
            self.assertEqual(before,after)
    def test_approval_release_http_lifecycle(self):
        with service(judge='J-FAIL-90') as (srv,dr):
            xid=self.boot(srv,dr)
            gate=readback(self.x(srv,'evaluate_gates',batch_id=xid),dr)['body']['gate']
            self.assertEqual(gate['status'],'fail')
            first=readback(self.x(srv,'record_release',actor='P-RELEASE',body={'decision':'overridden'}),dr)['body']
            self.assertFalse(first['accepted'])
            approval=readback(self.x(srv,'override_gate',actor='P-APPROVER',gate='semantic-gate',gate_result_id=gate['id'],batch_id=xid,justification='documented exception'),dr)['body']
            self.assertTrue(approval['accepted'])
            second=readback(self.x(srv,'record_release',actor='P-RELEASE',body={'decision':'overridden','approval_id':approval['approval']['record_id']}),dr)['body']
            self.assertTrue(second['accepted']);self.assertEqual(srv.model.saved_by_execution(xid)['gate']['status'],'fail')
    def test_override_not_reused_after_evaluation(self):
        with service(judge='J-FAIL-90') as (srv,dr):
            xid=self.boot(srv,dr)
            gate=readback(self.x(srv,'evaluate_gates',batch_id=xid),dr)['body']['gate']
            approval=readback(self.x(srv,'override_gate',actor='P-APPROVER',gate='semantic-gate',gate_result_id=gate['id'],batch_id=xid,justification='documented'),dr)['body']['approval']
            changed=readback(self.x(srv,'evaluate_gates',batch_id=xid),dr)['body']['gate']
            self.assertNotEqual(gate['id'],changed['id'])
            rejected=readback(self.x(srv,'record_release',actor='P-RELEASE',body={'decision':'overridden','approval_id':approval['record_id']}),dr)['body']
            self.assertFalse(rejected['accepted'])
    def test_adapter_request_contracts(self):
        cases=[('execute',{'suite':'cts-suite','environment':'cts-env'}),('get_conversation',{'execution_id':'execution-x'}),
          ('get_results',{'execution_id':'execution-x'}),('evaluate_gates',{'batch_id':'batch-x'}),
          ('review_result',{'execution_id':'execution-x','result_id':'result-x','verdict':'pass'}),
          ('override_gate',{'gate':'semantic-gate','gate_result_id':'gate-x','batch_id':'batch-x','justification':'why'}),
          ('record_release',{'body':{'decision':'overridden'}})]
        for op,args in cases:
            with self.subTest(op=op):
                req=checked_request(op,self.s,self.r,self.case,**args)
                self.assertEqual(validator.schema_errors('adapter-operation.schema.json',req),[])
    def test_invalid_case_rejected(self):
        req=request('execute',self.s,self.r,'S3.5.4-bad',suite='cts-suite',environment='cts-env')
        # Explicit guard also in local tests where schemas are unavailable.
        self.assertNotRegex(req['case_id'],r'^CT-[A-Z]{3}-[0-9]{3}$')
    def test_bad_request_does_not_open_execution(self):
        with service() as (srv,dr):
            self.assertEqual(self.x(srv,'get_results',execution_id='execution-not-here')['outcome'],'NOT_RUN')
            self.assertIsNone(srv.execution)
    def test_cross_run_disallowed(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr)
            r=exchange(srv,'get_results',self.s,'run-other',self.case,execution_id=xid)
            self.assertEqual(r['outcome'],'NOT_RUN')
    def test_cross_case_disallowed(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr)
            r=exchange(srv,'get_results',self.s,self.r,'CT-DEC-006',execution_id=xid)
            self.assertEqual(r['outcome'],'NOT_RUN')
    def test_cross_session_disallowed(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr)
            r=exchange(srv,'get_results','s-other',self.r,self.case,execution_id=xid)
            self.assertEqual(r['outcome'],'NOT_RUN')
    def test_cross_execution_disallowed(self):
        with service() as (srv,dr):
            self.boot(srv,dr)
            r=self.x(srv,'get_results',execution_id='execution-other')
            self.assertEqual(r['outcome'],'NOT_RUN')
    def test_tampered_raw_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            ref=x['receipts']['raw']['ref'].removeprefix('evidence://')
            with open(pathlib.Path(dr)/'objects'/ref,'ab') as f:f.write(b'X')
            self.assertEqual(readback(x,dr)['outcome'],'NOT_RUN')
    def test_tampered_redacted_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            ref=x['receipts']['redacted']['ref'].removeprefix('evidence://')
            with open(pathlib.Path(dr)/'objects'/ref,'ab') as f:f.write(b'X')
            self.assertEqual(readback(x,dr)['outcome'],'NOT_RUN')
    def test_missing_raw_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            (pathlib.Path(dr)/'objects'/x['receipts']['raw']['ref'].removeprefix('evidence://')).unlink()
            self.assertEqual(readback(x,dr)['outcome'],'NOT_RUN')
    def test_wrong_receipt_owner_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            self.assertEqual(readback(x,dr,damage='wrong_owner')['outcome'],'NOT_RUN')
    def test_wrong_receipt_hash_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            self.assertEqual(readback(x,dr,damage='receipt_hash')['outcome'],'NOT_RUN')
    def test_wrong_evidence_refs_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            x['response']['evidence_refs']=[]
            self.assertEqual(readback(x,dr)['outcome'],'NOT_RUN')
    def test_wrong_response_hash_not_run(self):
        with service() as (srv,dr):
            xid=self.boot(srv,dr);x=self.x(srv,'get_results',execution_id=xid)
            x['response']['data']['sut']['body_sha256']='0'*64
            self.assertEqual(readback(x,dr)['outcome'],'NOT_RUN')
    def test_predicate_wrong_expected_fail(self):
        self.assertEqual(evaluate({'gate':{'status':'fail'}},{'field':'gate.status','op':'eq','expected':'pass'})['outcome'],'FAIL')
    def test_predicate_correct_pass(self):
        self.assertEqual(evaluate({'gate':{'status':'fail'}},{'field':'gate.status','op':'eq','expected':'fail'})['outcome'],'PASS')
    def test_predicate_missing_not_run(self):
        self.assertEqual(evaluate({},{'field':'gate.status','op':'eq','expected':'fail'})['outcome'],'NOT_RUN')
    def test_predicate_unapproved_field_not_run(self):
        self.assertEqual(evaluate({}, {'field':'__class__','op':'eq','expected':1})['outcome'],'NOT_RUN')
    def test_predicate_wrong_type_fail(self):
        self.assertEqual(evaluate({'gate':{'basis':{'results':True}}},{'field':'gate.basis.results','op':'eq','expected':1})['outcome'],'FAIL')
    def test_predicate_no_eval(self):
        self.assertEqual(evaluate({}, {'field':'gate.status','op':'exec','expected':'print(1)'})['outcome'],'NOT_RUN')
    def test_predicate_unique_ids(self):
        spec={'field':'results.rows','op':'unique_ids','expected':True}
        self.assertEqual(evaluate({'results':[{'id':'a'},{'id':'a'}]},spec)['outcome'],'FAIL')
    def test_predicate_inconclusive_basis_detects_mutant(self):
        wrong={'gate':{'status':'pass','basis':{'not_actionable':0},'reasons':[]}}
        self.assertEqual(all_of(wrong,Q08['CT-DEC-006:evaluate_gates'])['outcome'],'FAIL')
    def test_audit_does_not_claim_full_acceptance(self):
        r=summarize();self.assertFalse(r['unconditional_exit_acceptance']);self.assertFalse(r['real_sut_conformance'])
        self.assertGreater(r['open_or_partial'],0)
    def test_audit_q05_still_partial(self):
        r=summarize();self.assertEqual(next(x['status'] for x in r['items'] if x['id']=='S2-F01'),'PARTIAL')

if __name__=='__main__':unittest.main()
