"""Conformance of intentionally good/bad mock + real v0.4 schema validation."""
import unittest,sys,pathlib,hashlib,copy,uuid
from mock import MockSUT,fixture_base
from adapter import S1Adapter
from runner import run_suite,summarize
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'harness'/'tools'))
import validate as v

class S1(unittest.TestCase):
    def test_correct_mock(self):
        z=run_suite();self.assertEqual([r['outcome'] for r in z['cases'].values()],['PASS']*4);self.assertEqual(z['CT-CFG-025'],'PASS')
    def test_unclaimed_capability(self):
        z=run_suite(seeded_controls=False)
        self.assertEqual(z['cases']['CT-CFG-025.25']['outcome'],'NOT_APPLICABLE')
        self.assertEqual(z['CT-CFG-025'],'PASS')
    def test_missing_setup_not_run(self):
        z=run_suite(setup_available=False)
        self.assertEqual(set(r['outcome'] for r in z['cases'].values()),{'NOT_RUN'})
        self.assertEqual(z['CT-CFG-025'],'NOT_RUN')
    def test_broken_accepts_missing_name(self):
        self.assertEqual(run_suite('accept_missing_name')['cases']['CT-CFG-025.01']['outcome'],'FAIL')
    def test_broken_accepts_missing_tool_config(self):
        self.assertEqual(run_suite('accept_missing_tool_configuration')['cases']['CT-CFG-025.05']['outcome'],'FAIL')
    def test_broken_accepts_missing_defect_class_name(self):
        self.assertEqual(run_suite('accept_missing_name')['cases']['CT-CFG-025.25']['outcome'],'FAIL')
    def test_broken_silent_field_drop(self):
        self.assertEqual(run_suite('drop_tool_configuration')['cases']['CT-CFG-001']['outcome'],'FAIL')
    def test_broken_rejects_valid(self):
        self.assertEqual(run_suite('reject_valid')['cases']['CT-CFG-001']['outcome'],'FAIL')
    def test_rejected_without_field_diagnostic(self):
        self.assertEqual(run_suite('vague_error')['cases']['CT-CFG-025.05']['outcome'],'FAIL')
    def test_summary_priority(self):
        self.assertEqual(summarize({'a':{'outcome':'PASS'},'b':{'outcome':'NOT_RUN'}}),'NOT_RUN')
        self.assertEqual(summarize({'a':{'outcome':'FAIL'},'b':{'outcome':'NOT_RUN'}}),'FAIL')
        self.assertEqual(summarize({'a':{'outcome':'NOT_APPLICABLE'}}),'NOT_APPLICABLE')
    def test_adapter_v04_request_and_response(self):
        sut=MockSUT();ad=S1Adapter(sut);cid='cid-'+uuid.uuid4().hex
        req={'contract_version':'0.4','operation':'load_config','run_id':'run1','case_id':'CT-CFG-001',
        'session_id':'session1','correlation_id':cid,'timeout_ms':10000,
        'arguments':{'project_id':'cts-base','config':fixture_base()}}
        self.assertEqual(v.schema_errors('adapter-operation.schema.json',req),[])
        rsp=ad.operation(req)
        self.assertEqual(v.schema_errors('adapter-response.schema.json',rsp),[])
        self.assertEqual(rsp['correlation_id'],cid)
        self.assertEqual(ad.read_body(rsp)['project_id'],'cts-base')
    def test_reject_wrong_contract_version(self):
        req={'contract_version':'0.3','operation':'load_config','run_id':'run1','case_id':'CT-CFG-001',
        'session_id':'session1','correlation_id':'corr','timeout_ms':10000,
        'arguments':{'project_id':'cts-base','config':fixture_base()}}
        self.assertTrue(v.schema_errors('adapter-operation.schema.json',req))
    def test_reject_malformed_envelope(self):
        req={'contract_version':'0.4','operation':'load_config','arguments':{'config':fixture_base()}}
        self.assertTrue(v.schema_errors('adapter-operation.schema.json',req))
    def test_evidence_tampering_detected(self):
        ad=S1Adapter(MockSUT());req={'operation':'load_config','arguments':{'project_id':'x','config':fixture_base()},'correlation_id':'c'}
        out=ad.operation(req);ref=out['data']['sut']['body_ref'];ad.observations[ref]=b'altered'
        with self.assertRaises(ValueError):ad.read_body(out)

if __name__=='__main__':unittest.main()
