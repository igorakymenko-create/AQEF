import copy, hashlib, json, unittest
from s20_foundation import (spec,field,validate_contract,evaluate,summary,
                            make_time_profile,canonical_http_suite)
from mock import fixture_base
from test_s1_negative import observation

def run_observation(case,accepted=False,body=None):
    # Synthetic envelope uses validated reference format from existing S1 tests.
    req,rsp,ev=observation(case=case,accepted=accepted,body=body)
    return req,rsp,ev

class FoundationContract(unittest.TestCase):
    def test_q02_paths(self):
        x={'data':{'sut':{'status':422,'outcome':'rejected'}}}
        self.assertEqual(field(x,spec()['fields']['sut.status']),422)
    def test_q02_missing_fails_loudly(self):
        with self.assertRaises(KeyError):field({},'data.sut.status')
    def test_q08_catalog_complete(self):
        self.assertTrue(validate_contract())
    def test_q08_capabilities_are_explicit(self):
        self.assertEqual(spec()['predicates']['CT-CFG-025.25']['required_capability'],'seeded_controls')
    def test_q08_05_missing_key_not_null(self):
        self.assertEqual(spec()['predicates']['CT-CFG-025.05']['missing_field'],
                         'environments[0].tool_configuration')
    def test_single_assessor_rejects_bad_config(self):
        r,s,e=run_observation('CT-CFG-025.05')
        self.assertEqual(evaluate('CT-CFG-025.05',r,s,e)['outcome'],'PASS')
    def test_single_assessor_detects_mutation(self):
        r,s,e=run_observation('CT-CFG-025.05',accepted=True)
        self.assertEqual(evaluate('CT-CFG-025.05',r,s,e)['outcome'],'FAIL')
    def test_single_assessor_detects_vague_error(self):
        r,s,e=run_observation('CT-CFG-025.05',body={'error':'invalid'})
        self.assertEqual(evaluate('CT-CFG-025.05',r,s,e)['outcome'],'FAIL')
    def test_single_assessor_valid_config(self):
        cfg=fixture_base();r,s,e=run_observation('CT-CFG-001',accepted=True)
        self.assertEqual(evaluate('CT-CFG-001',r,s,e,source=cfg,stored={'config':copy.deepcopy(cfg)})['outcome'],'PASS')
    def test_single_assessor_missing_source(self):
        r,s,e=run_observation('CT-CFG-001',accepted=True)
        self.assertEqual(evaluate('CT-CFG-001',r,s,e,source=None)['outcome'],'NOT_RUN')
    def test_single_assessor_corrupt_evidence(self):
        r,s,e=run_observation('CT-CFG-025.05')
        ref=next(iter(e));e[ref]=(r['run_id'],r['case_id'],b'altered')
        self.assertEqual(evaluate('CT-CFG-025.05',r,s,e)['outcome'],'NOT_RUN')
    def test_capability_unclaimed(self):
        self.assertEqual(evaluate('CT-CFG-025.25',None,None,{},capabilities=())['outcome'],'NOT_APPLICABLE')
    def test_setup_failure(self):
        self.assertEqual(evaluate('CT-CFG-001',None,None,{},setup_ready=False)['outcome'],'NOT_RUN')
    def test_summary_not_run_not_pass(self):
        self.assertEqual(summary({'a':{'outcome':'PASS'},'b':{'outcome':'NOT_RUN'}}),'NOT_RUN')
    def test_summary_fail_priority(self):
        self.assertEqual(summary({'a':{'outcome':'FAIL'},'b':{'outcome':'NOT_RUN'}}),'FAIL')
    def test_q05_contract_default(self):
        z=make_time_profile();self.assertEqual(z['drain_ms'],5000)
        self.assertEqual(z['grace_ms'],5000)
        self.assertEqual(z['measurement_provenance'],'CONFIGURED_PLACEHOLDER_NOT_MEASURED')
    def test_q05_reject_drain_under_floor(self):
        with self.assertRaises(ValueError):make_time_profile(drain_ms=4999)
    def test_q05_reject_drain_under_twice_measured(self):
        with self.assertRaises(ValueError):make_time_profile(measured_max_delay_ms=4000,drain_ms=5000)
    def test_q05_reject_grace_under_floor(self):
        with self.assertRaises(ValueError):make_time_profile(grace_ms=4999)
    def test_q05_reject_grace_under_10pct(self):
        with self.assertRaises(ValueError):make_time_profile(wait_ms=100000,grace_ms=5000)
    def test_q05_reject_negative_budget(self):
        with self.assertRaises(ValueError):make_time_profile(wait_ms=-1)

class FoundationHTTP(unittest.TestCase):
    def test_correct_mock_canonical(self):
        z=canonical_http_suite()
        self.assertEqual([v['outcome'] for v in z['cases'].values()],['PASS']*4)
        self.assertEqual(z['CT-CFG-025'],'PASS')
    def test_broken_mock_canonical(self):
        z=canonical_http_suite('accept_missing_tool_configuration')
        self.assertEqual(z['cases']['CT-CFG-025.05']['outcome'],'FAIL')
        self.assertEqual(z['CT-CFG-025'],'FAIL')
    def test_unclaimed_canonical(self):
        z=canonical_http_suite(seeded_controls=False)
        self.assertEqual(z['cases']['CT-CFG-025.25']['outcome'],'NOT_APPLICABLE')
    def test_setup_unavailable_canonical(self):
        z=canonical_http_suite(setup_available=False)
        self.assertEqual(set(q['outcome'] for q in z['cases'].values()),{'NOT_RUN'})
    def test_legacy_consistency_good(self):
        from s1_rest import run_rest
        old=run_rest();new=canonical_http_suite()
        self.assertEqual({k:v['outcome'] for k,v in old['cases'].items()},
                         {k:v['outcome'] for k,v in new['cases'].items()})
    def test_legacy_consistency_mutant(self):
        from s1_rest import run_rest
        old=run_rest('accept_missing_name');new=canonical_http_suite('accept_missing_name')
        self.assertEqual({k:v['outcome'] for k,v in old['cases'].items()},
                         {k:v['outcome'] for k,v in new['cases'].items()})

if __name__=='__main__':unittest.main()
