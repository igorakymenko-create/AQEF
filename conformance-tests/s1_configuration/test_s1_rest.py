import unittest
from s1_rest import fixture_seed_full,run_rest,services,http,call

class S1Rest(unittest.TestCase):
    def test_full_seed_matches_normative_structure(self):
        p=fixture_seed_full()['project'];sc=p['suites'][0]['scenarios'];self.assertEqual(len(sc),2)
        self.assertEqual(sc[1]['seeded_control']['defect_class'],p['defect_classes'][0]['name'])
        self.assertEqual(sc[1]['evidence']['conversation'][1]['content'],'Goodbye.')
    def test_good_mock_passes(self):
        z=run_rest();self.assertEqual([v['outcome'] for v in z['cases'].values()],['PASS']*4);self.assertEqual(z['CT-CFG-025'],'PASS')
    def test_unclaimed_capability(self):
        z=run_rest(seeded_controls=False);self.assertEqual(z['cases']['CT-CFG-025.25']['outcome'],'NOT_APPLICABLE')
    def test_setup_failure(self):
        z=run_rest(setup_available=False);self.assertEqual(set(x['outcome'] for x in z['cases'].values()),{'NOT_RUN'})
    def test_missing_name_mutant(self):self.assertEqual(run_rest('accept_missing_name')['cases']['CT-CFG-025.01']['outcome'],'FAIL')
    def test_missing_tool_mutant(self):self.assertEqual(run_rest('accept_missing_tool_configuration')['cases']['CT-CFG-025.05']['outcome'],'FAIL')
    def test_missing_defect_name_mutant(self):self.assertEqual(run_rest('accept_missing_name')['cases']['CT-CFG-025.25']['outcome'],'FAIL')
    def test_drop_mutant(self):self.assertEqual(run_rest('drop_tool_configuration')['cases']['CT-CFG-001']['outcome'],'FAIL')
    def test_reject_valid_mutant(self):self.assertEqual(run_rest('reject_valid')['cases']['CT-CFG-001']['outcome'],'FAIL')
    def test_vague_error_mutant(self):self.assertEqual(run_rest('vague_error')['cases']['CT-CFG-025.05']['outcome'],'FAIL')
    def test_wrong_contract_version_http(self):
        with services() as (mock,adapter):
            st,body=http('POST',adapter.url+'/api/v0.4/operations',{'contract_version':'0.3','operation':'load_config'})
            self.assertEqual(st,400);self.assertEqual(body['error'],'SCHEMA_INVALID')
    def test_no_unsupported_operation_success(self):
        from mock import fixture_base
        with services() as (mock,adapter):
            req,rsp=call(adapter,'CT-CFG-001',fixture_base(),'test')
            self.assertEqual(rsp['data']['sut']['surface'],'rest')
    def test_seed_setup_is_rejected_if_broken(self):
        from s1_rest import RestMock
        x=fixture_seed_full();x['project']['suites'][0]['scenarios'][1]['evidence'].pop('conversation')
        status,body=RestMock(capabilities={'seeded_controls'}).load('x',x)
        self.assertEqual(status,422)

if __name__=='__main__':unittest.main()
