"""Independent hardening checks; run with repo's real validate.py in CI."""
import copy, pathlib, tempfile, threading, time, unittest, uuid
from concurrent.futures import ThreadPoolExecutor
from harness import Harness
from integration import App
import selftest

class Hardening(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.app=App(self.tmp.name)
        self.sid='s-'+uuid.uuid4().hex
        self.run='r-'+uuid.uuid4().hex
        self.case='CT-ASM-001'
        self.req=lambda op,args: {'contract_version':'0.4','operation':op,'run_id':self.run,'case_id':self.case,
            'session_id':self.sid,'correlation_id':uuid.uuid4().hex,'timeout_ms':10000,'arguments':args}
    def tearDown(self):self.tmp.cleanup()
    def begin(self):
        status,out=self.app.operation(self.req('begin_case',{'test_id':'CT-ASM-001','case_id':self.case}))
        self.assertEqual((status,out['success']),(200,True),out)
    def test_all_harness_behaviors_have_explicit_self_test_outcomes(self):
        self.begin();st,out=self.app.operation(self.req('self_test',{}));self.assertEqual(st,200)
        self.assertTrue(out['success']);data=out['data']
        actual={i['behavior']:i for i in data['results']}
        self.assertEqual(set(actual),set(selftest.ALL))
        for code in selftest.SUBJECTS+selftest.JUDGES:
            self.assertEqual(actual[code]['status'],'PASS',actual[code])
        for code in selftest.PENDING_PLUGINS:
            self.assertEqual(actual[code]['status'],'NOT_RUN')
            self.assertIn(code,data['unusable_behaviors'])
        self.assertEqual(data['status'],'INCOMPLETE')
        events=self.app.harness.read_log(self.sid)
        self.assertEqual(len([x for x in events if x['type']=='self_test']),len(selftest.ALL))
    def test_selected_self_test_is_complete(self):
        self.begin();_,out=self.app.operation(self.req('self_test',{'behaviors':['J-CATCH','SR-503-THEN-OK']}))
        self.assertEqual(out['data']['status'],'PASS');self.assertEqual(out['data']['unusable_behaviors'],[])
    def test_unknown_self_test_behavior_rejected(self):
        self.begin();_,out=self.app.operation(self.req('self_test',{'behaviors':['J-NONSENSE']}))
        self.assertFalse(out['success']);self.assertEqual(out['error']['code'],'HARNESS_SETUP_FAILED')
    def test_duplicate_self_test_behavior_rejected(self):
        self.begin();_,out=self.app.operation(self.req('self_test',{'behaviors':['SR-OK','SR-OK']}))
        self.assertFalse(out['success'])
    def test_broken_scripted_behavior_is_detected_not_passed(self):
        class Broken(Harness):
            def _answer(self,kind,code,payload,n):
                if code=='SR-OK':return 'WRONG'
                return super()._answer(kind,code,payload,n)
        h=Harness();sid=h.begin('test-'+uuid.uuid4().hex)
        result=selftest.run(h,sid,['SR-OK','J-PASS-90'],Broken)
        self.assertEqual(result['status'],'INCOMPLETE')
        self.assertEqual(result['unusable_behaviors'],['SR-OK'])
        self.assertEqual([x['status'] for x in result['results']],['FAIL','PASS'])
    def test_calls_arriving_during_drain_are_in_watermark(self):
        h=Harness();sid=h.begin();out={}
        def close():out.update(h.close_observation(sid,drain_ms=90))
        t=threading.Thread(target=close);t.start()
        until=time.monotonic()+1
        while h.session(sid).phase!='draining' and time.monotonic()<until:time.sleep(.001)
        self.assertEqual(h.session(sid).phase,'draining')
        self.assertEqual(h.invoke(sid,'judge',{})['outcome'],'completed')
        t.join()
        self.assertEqual(h.negative_assertion(sid,'judge',0)['outcome'],'FAIL')
        call=h.read_log(sid)
        received=[x for x in call if x['type']=='call_received']
        self.assertLessEqual(received[0]['sequence'],out['watermark'])
    def test_absent_call_negative_assertion_not_pass_before_close(self):
        h=Harness();sid=h.begin();self.assertEqual(h.negative_assertion(sid,'judge')['outcome'],'NOT_RUN')
        h.close_observation(sid,drain_ms=1)
        self.assertEqual(h.negative_assertion(sid,'judge')['outcome'],'PASS')
    def test_late_call_changes_negative_assertion_to_fail(self):
        h=Harness();sid=h.begin();h.close_observation(sid,drain_ms=1)
        self.assertEqual(h.negative_assertion(sid,'subject')['outcome'],'PASS')
        with self.assertRaises(RuntimeError):h.invoke(sid,'subject',{})
        self.assertEqual(h.negative_assertion(sid,'subject')['outcome'],'FAIL')
    def test_double_close_rejected(self):
        h=Harness();sid=h.begin();h.close_observation(sid,0)
        with self.assertRaises(ValueError):h.close_observation(sid,0)
    def test_evidence_resolver_detects_one_byte_change(self):
        self.begin();ref,_=self.app.evidence.put(b'hello',self.run,self.case,'test')
        self.assertEqual(self.app.evidence.resolve_verified(ref,self.run),b'hello')
        p=pathlib.Path(self.tmp.name)/ref.split('://')[1];p.write_bytes(b'hell0')
        with self.assertRaisesRegex(ValueError,'integrity'):self.app.evidence.resolve_verified(ref,self.run)
    def test_evidence_resolver_detects_truncation(self):
        ref,_=self.app.evidence.put(b'hello',self.run,self.case,'test')
        (pathlib.Path(self.tmp.name)/ref.split('://')[1]).write_bytes(b'hell')
        with self.assertRaisesRegex(ValueError,'integrity'):self.app.evidence.resolve_verified(ref,self.run)
    def test_evidence_resolver_detects_deletion(self):
        ref,_=self.app.evidence.put(b'hello',self.run,self.case,'test')
        (pathlib.Path(self.tmp.name)/ref.split('://')[1]).unlink()
        with self.assertRaises(FileNotFoundError):self.app.evidence.resolve_verified(ref,self.run)
    def test_evidence_resolver_refuses_foreign_run_and_traversal(self):
        ref,_=self.app.evidence.put(b'hello',self.run,self.case,'test')
        with self.assertRaises(ValueError):self.app.evidence.resolve_verified(ref,'another-run')
        with self.assertRaises(ValueError):self.app.evidence.resolve_verified('evidence://../secret',self.run)
    def test_evidence_resolver_cross_run_isolation(self):
        ref,_=self.app.evidence.put(b'hello',self.run,self.case,'test')
        self.assertEqual(self.app.evidence.resolve_verified(ref,self.run),b'hello')
        with self.assertRaises(ValueError):self.app.evidence.resolve_verified(ref,self.run+'x')

if __name__=='__main__':unittest.main()
