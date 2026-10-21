"""S0.2 closure regression tests; must run with existing repo schema validator."""
import pathlib, tempfile, unittest, uuid
from closure import (PLUGIN_REQUIRED,DEFERRED,LocalPlugin,local_plugin_self_test,
                     summarize_s0,attribute_evidence_case)
from harness import Harness
from integration import Evidence
import selftest

class Closure(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.ev=Evidence(self.tmp.name)
        self.run='run-'+uuid.uuid4().hex
        self.case='CT-ASM-001'
        self.ref,_=self.ev.put(b'important',self.run,self.case,'harness_response')
    def tearDown(self):self.tmp.cleanup()
    def assess(self,outcome='PASS',refs=None):
        return attribute_evidence_case(self.ev,self.run,self.case,
                                       [self.ref] if refs is None else refs,outcome)
    def test_local_len(self):
        self.assertEqual(local_plugin_self_test('cts-len')['status'],'PASS')
        a=LocalPlugin('cts-len');self.assertEqual((a.evaluate('a'),a.evaluate('')),('pass','fail'))
    def test_local_flaky_reset(self):
        self.assertEqual(local_plugin_self_test('cts-flaky')['status'],'PASS')
        a=LocalPlugin('cts-flaky');self.assertEqual([a.evaluate('a') for _ in range(3)],['pass','fail','fail'])
        self.assertEqual(LocalPlugin('cts-flaky').evaluate('a'),'pass')
    def test_local_crash(self):
        self.assertEqual(local_plugin_self_test('cts-crash')['status'],'PASS')
        with self.assertRaises(RuntimeError):LocalPlugin('cts-crash').evaluate('test')
    def test_future_plugins_not_falsely_passed(self):
        for name in DEFERRED:
            self.assertEqual(local_plugin_self_test(name)['status'],'NOT_RUN')
    def test_unknown_plugin_rejected(self):
        with self.assertRaises(ValueError):local_plugin_self_test('cts-other')
    def test_required_s0_matrix(self):
        h=Harness();sid=h.begin('closure-'+uuid.uuid4().hex)
        summary=summarize_s0(selftest.run(h,sid))
        self.assertEqual(summary['status'],'PASS',summary)
        self.assertEqual(summary['required_count'],len(selftest.SUBJECTS)+len(selftest.JUDGES)+3)
        self.assertEqual(summary['required_count'],summary['required_passed'])
        self.assertEqual(summary['deferred'],list(DEFERRED))
        self.assertEqual(sum(r['status']=='NOT_RUN' for r in summary['results']),2)
    def test_broken_scripted_behavior_blocks_closure(self):
        h=Harness();sid=h.begin('closure-'+uuid.uuid4().hex)
        class Broken(Harness):
            def _answer(self,kind,code,payload,n):
                if code=='SR-OK': return 'WRONG'
                return super()._answer(kind,code,payload,n)
        summary=summarize_s0(selftest.run(h,sid,harness_type=Broken))
        self.assertEqual(summary['status'],'INCOMPLETE')
        self.assertIn('SR-OK',summary['blockers'])
    def test_evidence_healthy_preserves_pass(self):
        self.assertEqual(self.assess()['outcome'],'PASS')
    def test_evidence_healthy_preserves_fail(self):
        self.assertEqual(self.assess('FAIL')['outcome'],'FAIL')
    def test_evidence_single_byte_mutation_becomes_not_run(self):
        (pathlib.Path(self.tmp.name)/self.ref.split('://')[1]).write_bytes(b'ImportanT')
        self.assertEqual(self.assess()['outcome'],'NOT_RUN')
    def test_evidence_truncation_becomes_not_run(self):
        (pathlib.Path(self.tmp.name)/self.ref.split('://')[1]).write_bytes(b'imp')
        self.assertEqual(self.assess('FAIL')['outcome'],'NOT_RUN')
    def test_evidence_deleted_becomes_not_run(self):
        (pathlib.Path(self.tmp.name)/self.ref.split('://')[1]).unlink()
        self.assertEqual(self.assess()['reason'],'EVIDENCE_INTEGRITY_FAILED')
    def test_evidence_empty_ref_list_becomes_not_run(self):
        self.assertEqual(self.assess(refs=[])['reason'],'EVIDENCE_MISSING')
    def test_evidence_partial_refs_becomes_not_run(self):
        self.ev.put(b'other',self.run,self.case,'extra')
        self.assertEqual(self.assess()['reason'],'EVIDENCE_INCOMPLETE')
    def test_evidence_foreign_case_ref_rejected(self):
        foreign,_=self.ev.put(b'foreign',self.run,'CT-ASM-002','test')
        self.assertEqual(self.assess(refs=[foreign])['outcome'],'NOT_RUN')
    def test_evidence_foreign_run_ref_rejected(self):
        foreign,_=self.ev.put(b'foreign','other-run',self.case,'test')
        self.assertEqual(self.assess(refs=[foreign])['outcome'],'NOT_RUN')
    def test_evidence_duplicate_ref_rejected(self):
        self.assertEqual(self.assess(refs=[self.ref,self.ref])['outcome'],'NOT_RUN')
    def test_evidence_invalid_prior_outcome_rejected(self):
        with self.assertRaises(ValueError):self.assess('UNKNOWN')

if __name__=='__main__': unittest.main()
