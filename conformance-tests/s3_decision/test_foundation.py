import copy
import unittest
from foundation import catalog,read_path,validate_catalog,evaluate,evaluate_fixture,summarize


def dec006():
    return {'gate': {'status':'fail','reasons':['non_actionable_results'],'basis':{'results':0,'not_actionable':1},'value':'not_computed'}}


def reviewed():
    return {'review_result': {'oracle_type':'human_reviewer','verdict':'pass','resolves':'judge-1','id':'review-1'},
            'judge_result':{'id':'judge-1'},'effective_result':{'id':'review-1'}}


def dec012():
    gates=[{'id':'gate-1','status':'fail','reasons':['non_actionable_results']}]
    records=[{'id':'judge-1','verdict':'pass','disposition':'inconclusive'}]
    return {'before':{'results':copy.deepcopy(records),'effective_result':{'id':'judge-1'},'gates':copy.deepcopy(gates)},
            'after':{'review_attempt':{'accepted':False},'results':copy.deepcopy(records),
                     'effective_result':{'id':'judge-1'},'gates':copy.deepcopy(gates)}}


def rel006():
    gate={'id':'gate-1','evaluation_id':'evaluation-1','status':'fail','reasons':['aggregate_failed']}
    return {'before':{'release_attempt':{'accepted':False},'gate':copy.deepcopy(gate)},
            'after':{'release_attempt':{'accepted':True},'gate':{
                **gate,'override':{'record_id':'approval-1','approved_by':'P-APPROVER',
                                    'justification':'documented exception'}}}}


class DecisionFoundation(unittest.TestCase):
    def test_catalog(self):self.assertTrue(validate_catalog())
    def test_all_case_sources_present(self):
        self.assertEqual(set(catalog()['normative_sources']).issuperset({'CT-DEC-006','CT-DEC-012','CT-REL-006'}),True)
    def test_dec006_correct(self):self.assertEqual(evaluate('CT-DEC-006',dec006())['outcome'],'PASS')
    def test_dec006_rejects_gate_pass(self):
        obs=dec006();obs['gate']['status']='pass';self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'FAIL')
    def test_dec006_requires_reason(self):
        obs=dec006();obs['gate']['reasons']=[];self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'FAIL')
    def test_dec006_rejects_inconclusive_counted_as_actionable(self):
        obs=dec006();obs['gate']['basis']['results']=1;self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'FAIL')
    def test_dec006_rejects_null_value(self):
        obs=dec006();obs['gate']['value']=None;self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'FAIL')
    def test_dec006_accepts_finite_number(self):
        obs=dec006();obs['gate']['value']=0.4;self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'PASS')
    def test_dec006_rejects_nan(self):
        obs=dec006();obs['gate']['value']=float('nan');self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'FAIL')
    def test_dec006_missing_field_not_run(self):
        obs=dec006();del obs['gate']['basis'];self.assertEqual(evaluate('CT-DEC-006',obs)['outcome'],'NOT_RUN')
    def test_reviewed_setup_pass(self):self.assertEqual(evaluate_fixture('F-REVIEWED',reviewed())['outcome'],'PASS')
    def test_reviewed_setup_wrong_resolution_fails(self):
        obs=reviewed();obs['review_result']['resolves']='not-judge';self.assertEqual(evaluate_fixture('F-REVIEWED',obs)['outcome'],'FAIL')
    def test_reviewed_setup_missing_result_not_run(self):
        obs=reviewed();del obs['effective_result'];self.assertEqual(evaluate_fixture('F-REVIEWED',obs)['outcome'],'NOT_RUN')
    def test_dec012_all_four_variants(self):
        for v in 'abcd':
            with self.subTest(v=v):self.assertEqual(evaluate('CT-DEC-012',dec012(),variant=v)['outcome'],'PASS')
    def test_dec012_mutated_results_fails(self):
        obs=dec012();obs['after']['results'].append({'id':'unexpected'});self.assertEqual(evaluate('CT-DEC-012',obs,variant='a')['outcome'],'FAIL')
    def test_dec012_changed_effective_fails(self):
        obs=dec012();obs['after']['effective_result']['id']='review-2';self.assertEqual(evaluate('CT-DEC-012',obs,variant='b')['outcome'],'FAIL')
    def test_dec012_changed_gate_reasons_fails(self):
        obs=dec012();obs['after']['gates'][0]['reasons']=[];self.assertEqual(evaluate('CT-DEC-012',obs,variant='c')['outcome'],'FAIL')
    def test_dec012_rejected_attempt_required(self):
        obs=dec012();obs['after']['review_attempt']['accepted']=True;self.assertEqual(evaluate('CT-DEC-012',obs,variant='d')['outcome'],'FAIL')
    def test_dec012_not_claimed(self):
        self.assertEqual(evaluate('CT-DEC-012',None,claimed_capabilities=(),variant='a')['outcome'],'NOT_APPLICABLE')
    def test_dec012_setup_missing(self):
        self.assertEqual(evaluate('CT-DEC-012',None,setup_ready=False,variant='a')['outcome'],'NOT_RUN')
    def test_dec012_variant_required(self):
        with self.assertRaises(ValueError):evaluate('CT-DEC-012',dec012())
    def test_dec012_variant_aggregate(self):
        self.assertEqual(summarize({v:evaluate('CT-DEC-012',dec012(),variant=v) for v in 'abcd'}),'PASS')
    def test_dec012_aggregate_not_run_precedence(self):
        self.assertEqual(summarize({'a':{'outcome':'PASS'},'b':{'outcome':'NOT_RUN'}}),'NOT_RUN')
    def test_dec012_aggregate_fail_precedence(self):
        self.assertEqual(summarize({'a':{'outcome':'NOT_RUN'},'b':{'outcome':'FAIL'}}),'FAIL')
    def test_rel006_correct(self):self.assertEqual(evaluate('CT-REL-006',rel006())['outcome'],'PASS')
    def test_rel006_first_attempt_must_fail(self):
        obs=rel006();obs['before']['release_attempt']['accepted']=True;self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_second_attempt_must_pass(self):
        obs=rel006();obs['after']['release_attempt']['accepted']=False;self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_gate_must_remain_failed(self):
        obs=rel006();obs['after']['gate']['status']='pass';self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_must_name_approver(self):
        obs=rel006();obs['after']['gate']['override']['approved_by']='';self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_must_have_justification(self):
        obs=rel006();obs['after']['gate']['override']['justification']=' ';self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_same_gate_result(self):
        obs=rel006();obs['after']['gate']['id']='new-gate';self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_no_re_evaluation(self):
        obs=rel006();obs['after']['gate']['evaluation_id']='new-eval';self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'FAIL')
    def test_rel006_evidence_missing_not_run(self):
        obs=rel006();del obs['after']['gate']['override'];self.assertEqual(evaluate('CT-REL-006',obs)['outcome'],'NOT_RUN')
    def test_setup_for_core_not_run(self):self.assertEqual(evaluate('CT-DEC-006',None,setup_ready=False)['outcome'],'NOT_RUN')
    def test_non_mapping_not_run(self):self.assertEqual(evaluate('CT-DEC-006',None)['outcome'],'NOT_RUN')

if __name__=='__main__':unittest.main()
