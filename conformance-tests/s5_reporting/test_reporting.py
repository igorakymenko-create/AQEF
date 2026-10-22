import copy, json, pathlib, tempfile, unittest
from reporting import build, v, SELECTED

class S5Reporting(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='s5-reports-')
        self.addCleanup(self.temp.cleanup)
        self.path=pathlib.Path(self.temp.name)
    def report(self, **kwargs):
        return build(self.path/'run',cts_commit='abcdef1234567890',**kwargs)
    def test_all_selected_normative_cases_reported(self):
        r,m=self.report();self.assertEqual(set(x['test_id'] for x in r['tests']),set(SELECTED))
    def test_default_no_fake_sut_pass(self):
        r,m=self.report();self.assertEqual(r['summary']['cases']['PASS'],0)
        self.assertTrue(all(c['outcome'] in ('NOT_RUN','NOT_APPLICABLE') for c in r['cases']))
    def test_required_partial_scope(self):
        r,m=self.report();self.assertEqual(r['plan']['scope'],'partial')
        self.assertIn('real SUT',r['plan']['reason'])
    def test_manifest_and_report_pass_independent_validator(self):
        r,m=self.report();self.assertFalse(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_no_claim_has_na(self):
        r,m=self.report();d={c['case_id']:c for c in r['cases']}
        for case in ('CT-HRV-003','CT-PLG-003','CT-SDK-001'):
            self.assertEqual(d[case]['outcome'],'NOT_APPLICABLE')
    def test_claim_without_observation_not_run(self):
        r,m=self.report(claims=('cli','plugins:validator','human_review'))
        for cid in ('CT-HRV-003','CT-PLG-003','CT-SDK-001'):
            self.assertEqual(next(c['outcome'] for c in r['cases'] if c['case_id']==cid),'NOT_RUN')
    def test_claimed_mock_with_direct_evidence(self):
        r,m=self.report(claims=('cli',),observations={'CT-SDK-001':{'outcome':'PASS',
            'runner_observed':True,'evidence':{'scope':'MOCK_ONLY','proxy_calls':['load_config','execute','evaluate_gates']}}})
        self.assertEqual(next(c['outcome'] for c in r['cases'] if c['case_id']=='CT-SDK-001'),'PASS')
        self.assertFalse(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_reject_pass_without_evidence(self):
        with self.assertRaisesRegex(ValueError,'evidence'):
            self.report(claims=('cli',),observations={'CT-SDK-001':{'outcome':'PASS','runner_observed':True}})
    def test_reject_unattributed_success(self):
        with self.assertRaisesRegex(ValueError,'runner_observed'):
            self.report(claims=('cli',),observations={'CT-SDK-001':{'outcome':'PASS','evidence':{'x':1}}})
    def test_summary_lie_detected(self):
        r,m=self.report();r['summary']['cases']['PASS']+=1
        self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_hidden_not_run_detected(self):
        r,m=self.report(claims=('cli',));t=next(t for t in r['tests'] if t['test_id']=='CT-SDK-001')
        t['outcome']='PASS';self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_requirement_state_lie_detected(self):
        r,m=self.report();r['requirements'][0]['state']='violated' if r['requirements'][0]['state']!='violated' else 'verified'
        self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_manifest_hash_mutation_detected(self):
        r,m=self.report();m['entries'][0]['raw_sha256']='0'*64
        self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_missing_evidence_detected(self):
        r,m=self.report();(self.path/'run'/'evidence'/'conformance-statement.json').unlink()
        self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_evidence_byte_mutation_detected(self):
        r,m=self.report();with_file=self.path/'run'/'evidence'/'conformance-statement.json';with_file.write_bytes(with_file.read_bytes()+b'!')
        self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))
    def test_report_written_to_disk(self):
        self.report();self.assertTrue((self.path/'run'/'report.json').is_file());self.assertTrue((self.path/'run'/'manifest.json').is_file())
    def test_missing_commit_fails(self):
        with self.assertRaises(ValueError):build(self.path/'bad',cts_commit='')
    def test_duplicate_external_case_cannot_override_claim(self):
        with self.assertRaisesRegex(ValueError,'claimed capability'):
            self.report(claims=('cli',),observations={'CT-SDK-001':{'outcome':'NOT_APPLICABLE'}})
    def test_not_run_does_not_claim_verified(self):
        r,m=self.report(claims=('cli',));cid='CT-SDK-001'
        for q in r['requirements']:
            if cid in q['traced_to'] and all(next((c['outcome'] for c in r['cases'] if c['case_id']==x),'NOT_RUN') !='PASS' for x in q['traced_to']):
                self.assertNotEqual(q['state'],'verified')
    def test_plan_must_not_claim_full(self):
        r,m=self.report();r['plan']['scope']='full';r['plan'].pop('reason')
        self.assertTrue(v.check_report(r,v.load_inventory(),m,self.path/'run'/'evidence'))

if __name__=='__main__':unittest.main()
