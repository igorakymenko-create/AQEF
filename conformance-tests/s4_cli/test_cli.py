import pathlib,sys,unittest,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from cli import DOCUMENTED_COMMANDS
from probe import EXPECTED,run_ct_sdk_001,assess,inspect_documented_commands,trace_matrix

class CLIConformanceTests(unittest.TestCase):
    def test_healthy(self):self.assertEqual(run_ct_sdk_001()['outcome'],'PASS')
    def test_documented_cli_map(self):self.assertEqual(DOCUMENTED_COMMANDS,EXPECTED)
    def test_no_capability(self):self.assertEqual(run_ct_sdk_001(claimed=False)['outcome'],'NOT_APPLICABLE')
    def test_bypass_execute(self):self.assertEqual(run_ct_sdk_001(mutation='skip_rest_execute')['outcome'],'FAIL')
    def test_bypass_gate(self):self.assertEqual(run_ct_sdk_001(mutation='skip_rest_gate')['outcome'],'FAIL')
    def test_extra_call(self):self.assertEqual(run_ct_sdk_001(mutation='extra_rest_call')['outcome'],'FAIL')
    def test_wrong_args(self):self.assertEqual(run_ct_sdk_001(mutation='wrong_proxy_args')['outcome'],'FAIL')
    def test_missing_proxy(self):self.assertEqual(run_ct_sdk_001(mutation='missing_proxy_log')['outcome'],'NOT_RUN')
    def test_fabricated_output(self):self.assertEqual(run_ct_sdk_001(mutation='cli_output_fabricated')['outcome'],'FAIL')
    def test_extra_documented_command(self):self.assertEqual(run_ct_sdk_001(documented={**EXPECTED,'magic':'not_appendix_c'})['outcome'],'FAIL')
    def test_misdocumented_command(self):self.assertEqual(run_ct_sdk_001(documented={**EXPECTED,'execute':'get_results'})['outcome'],'FAIL')
    def test_missing_documented_command(self):self.assertEqual(run_ct_sdk_001(documented={'load-config':'load_config'})['outcome'],'FAIL')
    def test_missing_docs(self):self.assertEqual(inspect_documented_commands({})['outcome'],'NOT_RUN')
    def test_wrong_operation(self):self.assertEqual(run_ct_sdk_001(mutation='wrong_rest_operation')['outcome'],'FAIL')
    def test_missing_output(self):self.assertEqual(assess(claimed=True,documented=EXPECTED,records=[],outputs=[])['outcome'],'NOT_RUN')
    def test_invalid_output(self):self.assertEqual(assess(claimed=True,documented=EXPECTED,records=[{'operation':v,'arguments':dict.fromkeys(keys)} for v,keys in zip(EXPECTED.values(),[('project_id','config'),('project_id','suite','environment'),('project_id','batch_id')])],outputs=[{}, {}, {}])['outcome'],'FAIL')
    def test_empty_record_log(self):self.assertEqual(assess(claimed=True,documented=EXPECTED,records=[],outputs=[{}, {}, {}])['outcome'],'FAIL')
    def test_bad_record_type(self):self.assertEqual(assess(claimed=True,documented=EXPECTED,records='bad',outputs=[{}, {}, {}])['outcome'],'NOT_RUN')
    def test_trace_matrix(self):
        m=trace_matrix()['cases'];expected={'healthy':'PASS','bypass_execute':'FAIL','bypass_gate':'FAIL','extra_rest_call':'FAIL','wrong_proxy_args':'FAIL','missing_proxy_log':'NOT_RUN','unclaimed':'NOT_APPLICABLE','unmapped_command':'FAIL'}
        self.assertEqual({k:v['outcome'] for k,v in m.items()},expected)
if __name__=='__main__':unittest.main()
