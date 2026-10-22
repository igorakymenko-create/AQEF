import copy,json,pathlib,tempfile,unittest,hashlib
from closure import (BASELINES,FINDINGS,EXIT_NOTES,HISTORIC_RUNS,reconcile,
                     verify_regression,validate_bundle,dump,digest,is_commit)
SHA='a'*40

def fixture(root):
 root=pathlib.Path(root);(root/'logs').mkdir(parents=True,exist_ok=True)
 rows=[]
 for suite,n in BASELINES.items():
  p=root/'logs'/(suite+'.log');p.write_text(f'Ran {n} tests in 0.3s\n\nOK\n')
  rows.append({'suite':suite,'tests':n,'exit_code':0,'sha256':digest(p)})
 return {'cts_commit':SHA,'scope':'UNIT_TESTS_NOT_SUT_CONFORMANCE','suites':rows,'total_tests':423}

class EvidenceClosureTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name);self.reg=fixture(self.root)
 def test_baseline_exact(self):self.assertEqual(sum(BASELINES.values()),423)
 def test_valid_regression(self):self.assertEqual(verify_regression(self.reg,self.root/'logs',SHA),[])
 def test_wrong_sha_detected(self):self.assertTrue(verify_regression(self.reg,self.root/'logs','b'*40))
 def test_untrusted_scope_detected(self):
  x=copy.deepcopy(self.reg);x['scope']='SUT_CONFORMANCE';self.assertTrue(verify_regression(x,self.root/'logs',SHA))
 def test_wrong_count_detected(self):
  x=copy.deepcopy(self.reg);x['total_tests']=424;self.assertTrue(verify_regression(x,self.root/'logs',SHA))
 def test_missing_suite_detected(self):
  x=copy.deepcopy(self.reg);x['suites'].pop();self.assertTrue(verify_regression(x,self.root/'logs',SHA))
 def test_duplicate_suite_detected(self):
  x=copy.deepcopy(self.reg);x['suites'].append(x['suites'][0]);self.assertTrue(verify_regression(x,self.root/'logs',SHA))
 def test_missing_log_detected(self):
  (self.root/'logs'/'s5_reporting.log').unlink();self.assertTrue(verify_regression(self.reg,self.root/'logs',SHA))
 def test_mutated_log_detected(self):
  p=self.root/'logs'/'s4_plugins.log';p.write_text(p.read_text()+'edited');self.assertTrue(verify_regression(self.reg,self.root/'logs',SHA))
 def test_failed_exit_detected(self):
  x=copy.deepcopy(self.reg);x['suites'][0]['exit_code']=1;self.assertTrue(verify_regression(x,self.root/'logs',SHA))
 def test_false_summary_rejected(self):
  p=self.root/'logs'/'s1_configuration.log';p.write_text('Ran 78 tests in 0.2s\n\nFAILED\n');
  self.assertTrue(verify_regression(self.reg,self.root/'logs',SHA))
 def test_valid_commit(self):self.assertTrue(is_commit(SHA))
 def test_short_commit_invalid(self):self.assertFalse(is_commit('abc1234'))
 def test_uppercase_commit_invalid(self):self.assertFalse(is_commit('A'*40))
 def historical(self):return [{'id':id,'status':'PARTIAL'} for id in FINDINGS if id.startswith(('S2','S3','Q-'))]
 def test_reconciliation_count(self):self.assertEqual(len(reconcile(self.historical(),SHA,True)),len(FINDINGS))
 def test_no_success_without_regression(self):
  with self.assertRaises(ValueError):reconcile(self.historical(),SHA,False)
 def test_no_legacy_missing_findings(self):
  with self.assertRaises(ValueError):reconcile(self.historical()[:-1],SHA,True)
 def test_real_sut_never_claimed(self):self.assertTrue(all(x['real_sut_disposition']=='NOT_ESTABLISHED' for x in reconcile(self.historical(),SHA,True)))
 def test_findings_unresolved(self):self.assertGreater(sum(x[0]=='PARTIAL' for x in FINDINGS.values()),3)
 def test_ec02_not_false_pass(self):self.assertEqual(EXIT_NOTES['EC-02'][0],'PARTIAL')
 def test_ec09_not_false_pass(self):self.assertEqual(EXIT_NOTES['EC-09'][0],'CONDITIONAL_NOT_TRIGGERED')
 def test_historical_run_shas(self):self.assertTrue(all(is_commit(sha) for _,sha in HISTORIC_RUNS.values()))
 def test_manifest_tamper_detection(self):
  p=self.root/'note.txt';p.write_text('genuine');dump(self.root/'closure_manifest.json',{'cts_commit':SHA,'total_unit_tests':423,'files':{'note.txt':digest(p)}})
  self.assertEqual(validate_bundle(self.root,SHA),[])
  p.write_text('modified');self.assertTrue(validate_bundle(self.root,SHA))
 def test_manifest_traversal_rejected(self):
  dump(self.root/'closure_manifest.json',{'cts_commit':SHA,'total_unit_tests':423,'files':{'../escape.txt':'0'*64}})
  self.assertTrue(validate_bundle(self.root,SHA))
if __name__=='__main__':unittest.main()
