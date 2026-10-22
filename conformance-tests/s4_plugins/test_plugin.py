import copy
import unittest
from plugin import run_ct_plg_003, trace_matrix, assess, PluginMock, CAPABILITY

class CTPLG003(unittest.TestCase):
    def test_healthy_a(self): self.assertEqual(run_ct_plg_003(marker=1)['outcome'], 'PASS')
    def test_malformed_b(self): self.assertEqual(run_ct_plg_003(marker=2,malformed=True)['outcome'], 'PASS')
    def test_two_cases_independent(self):
        x=PluginMock();a=x.execute(marker=1);b=x.execute(marker=2,malformed=True)
        self.assertNotEqual(a,b)
        self.assertEqual(x.results[a]['verdict'],'pass')
        self.assertIsNone(x.results[b]['verdict'])
    def test_raw_probe_receives_exact_input(self):
        x=PluginMock();e=x.execute(marker=1);arg=x.read(e)['plugin_calls'][0]
        self.assertEqual(set(arg),{'evidence','clause','configuration','execution_id','clause_id'})
    def test_expected_marker_one(self):
        x=PluginMock();e=x.execute(marker=1);self.assertEqual(x.read(e)['plugin_calls'][0]['clause']['expected'],{'marker':1})
    def test_expected_marker_two(self):
        x=PluginMock();e=x.execute(marker=2,malformed=True);self.assertEqual(x.read(e)['plugin_calls'][0]['clause']['expected'],{'marker':2})
    def test_version_valid_result(self):
        x=PluginMock();e=x.execute(marker=1);self.assertEqual(x.read(e)['result']['oracle'],{'name':'cts-probe','version':'1.0.0'})
    def test_missing_verdict_never_fail(self):
        x=PluginMock();e=x.execute(marker=2,malformed=True);r=x.read(e)['result'];self.assertEqual((r['disposition'],r['verdict']),('oracle_unavailable',None))
    def test_no_judge_on_malformed(self):
        x=PluginMock();e=x.execute(marker=2,malformed=True);self.assertFalse(any(ev.get('kind')=='judge' for ev in x.read(e)['events']))
    def test_extra_input_mutant(self):self.assertEqual(run_ct_plg_003(mutation='extra_input')['outcome'],'FAIL')
    def test_missing_input_mutant(self):self.assertEqual(run_ct_plg_003(mutation='missing_input')['outcome'],'FAIL')
    def test_wrong_expected_mutant(self):self.assertEqual(run_ct_plg_003(mutation='wrong_expected')['outcome'],'FAIL')
    def test_wrong_response_mutant(self):self.assertEqual(run_ct_plg_003(mutation='wrong_response')['outcome'],'FAIL')
    def test_wrong_config_version_mutant(self):self.assertEqual(run_ct_plg_003(mutation='wrong_version_input')['outcome'],'FAIL')
    def test_malformed_as_fail_mutant(self):self.assertEqual(run_ct_plg_003(marker=2,malformed=True,mutation='malformed_as_fail')['outcome'],'FAIL')
    def test_malformed_preserved_mutant(self):self.assertEqual(run_ct_plg_003(marker=2,malformed=True,mutation='malformed_preserved')['outcome'],'FAIL')
    def test_judge_on_malformed_mutant(self):self.assertEqual(run_ct_plg_003(marker=2,malformed=True,mutation='judge_on_malformed')['outcome'],'FAIL')
    def test_wrong_oracle_mutant(self):self.assertEqual(run_ct_plg_003(mutation='wrong_oracle')['outcome'],'FAIL')
    def test_cross_execution_mutant(self):self.assertEqual(run_ct_plg_003(mutation='cross_execution')['outcome'],'FAIL')
    def test_wrong_clause_id_mutant(self):self.assertEqual(run_ct_plg_003(mutation='wrong_clause_id')['outcome'],'FAIL')
    def test_unclaimed(self):self.assertEqual(run_ct_plg_003(claims=False),{'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_UNCLAIMED'})
    def test_missing_readback(self):self.assertEqual(run_ct_plg_003(readback_damage='absent')['outcome'],'NOT_RUN')
    def test_missing_calls_log(self):self.assertEqual(run_ct_plg_003(readback_damage='calls')['outcome'],'NOT_RUN')
    def test_missing_result(self):self.assertEqual(run_ct_plg_003(readback_damage='result')['outcome'],'NOT_RUN')
    def test_missing_events(self):self.assertEqual(run_ct_plg_003(readback_damage='events')['outcome'],'NOT_RUN')
    def test_bad_type_marker(self):self.assertEqual(run_ct_plg_003(marker='one')['outcome'],'NOT_RUN')
    def test_wrong_input_independent_evaluator(self):
        x=PluginMock();e=x.execute(marker=1);o=x.read(e);o['plugin_calls'][0]['clause']['expected']={'marker':99}
        self.assertEqual(assess(claims=True,execution_id=e,readback=o,marker=1)['outcome'],'FAIL')
    def test_mutate_result_copy_independent(self):
        x=PluginMock();e=x.execute(marker=1);o=x.read(e);o['result']['verdict']='fail'
        self.assertEqual(x.read(e)['result']['verdict'],'pass')
    def test_matrix(self):
        d=trace_matrix();self.assertEqual([d[k]['outcome'] for k in ('healthy','malformed','extra_input_mutant','malformed_as_fail_mutant','judge_after_malformed_mutant','no_log','unclaimed')],['PASS','PASS','FAIL','FAIL','FAIL','NOT_RUN','NOT_APPLICABLE'])

if __name__ == '__main__':unittest.main()
