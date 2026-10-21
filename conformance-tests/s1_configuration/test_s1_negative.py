"""Independent negative/outcome adversarial tests, plus actual HTTP S1 checks."""
import copy, hashlib, json, unittest, uuid
from negative import assess, aggregate
from s1_rest import services, call, http, fixture_seed_full
from mock import fixture_base


def observation(*,case='CT-CFG-025.05',accepted=False,body=None,source=None):
    body={'code':'INVALID_CONFIG','field':'environments[0].tool_configuration'} if body is None else body
    req={'contract_version':'0.4','operation':'load_config','run_id':'run-1','case_id':case,
         'correlation_id':'corr-1'}
    ref='evidence://s1-rest/test'
    raw=json.dumps(body,sort_keys=True).encode()
    rsp={'contract_version':'0.4','operation':'load_config','correlation_id':'corr-1','success':True,
         'data':{'sut':{'outcome':'accepted' if accepted else 'rejected','status':201 if accepted else 422,
                        'body_ref':ref,'body_sha256':hashlib.sha256(raw).hexdigest(),
                        'surface':'equivalent'}},'evidence_refs':[ref]}
    return req,rsp,{ref:('run-1',case,raw)}


def result(req,rsp,evidence,**kw):
    return assess(req,rsp,evidence,expected_acceptance=False,
                  missing_field='environments[0].tool_configuration',**kw)

class S1Negative(unittest.TestCase):
    def test_rejection_pass(self):
        self.assertEqual(result(*observation())['outcome'],'PASS')
    def test_acceptance_of_invalid_fails(self):
        self.assertEqual(result(*observation(accepted=True))['outcome'],'FAIL')
    def test_vague_rejection_fails(self):
        self.assertEqual(result(*observation(body={'error':'bad'}))['outcome'],'FAIL')
    def test_correct_valid_acceptance_pass(self):
        cfg=fixture_base();r,s,e=observation(accepted=True,case='CT-CFG-001')
        self.assertEqual(assess(r,s,e,expected_acceptance=True,stored={'config':copy.deepcopy(cfg)},source=cfg)['outcome'],'PASS')
    def test_silent_data_loss_fails(self):
        cfg=fixture_base();r,s,e=observation(accepted=True,case='CT-CFG-001');stored=copy.deepcopy(cfg)
        stored['project']['environments'][0].pop('tool_configuration')
        self.assertEqual(assess(r,s,e,expected_acceptance=True,stored={'config':stored},source=cfg)['outcome'],'FAIL')
    def test_missing_source_not_run(self):
        r,s,e=observation(accepted=True,case='CT-CFG-001')
        self.assertEqual(assess(r,s,e,expected_acceptance=True,stored={'config':{}},source=None)['outcome'],'NOT_RUN')
    def test_missing_evidence_not_run(self):
        r,s,e=observation();self.assertEqual(result(r,s,{})['outcome'],'NOT_RUN')
    def test_modified_evidence_not_run(self):
        r,s,e=observation();ref=next(iter(e));e[ref]=(r['run_id'],r['case_id'],b'{"field":"altered"}')
        self.assertEqual(result(r,s,e)['reason'],'EVIDENCE_INTEGRITY_FAILED')
    def test_wrong_case_evidence_not_run(self):
        r,s,e=observation();ref=next(iter(e));e[ref]=(r['run_id'],'CT-CFG-001',e[ref][2])
        self.assertEqual(result(r,s,e)['reason'],'EVIDENCE_WRONG_OWNER')
    def test_wrong_run_evidence_not_run(self):
        r,s,e=observation();ref=next(iter(e));e[ref]=('another-run',r['case_id'],e[ref][2])
        self.assertEqual(result(r,s,e)['reason'],'EVIDENCE_WRONG_OWNER')
    def test_wrong_correlation_not_run(self):
        r,s,e=observation();s['correlation_id']='other'
        self.assertEqual(result(r,s,e)['reason'],'ADAPTER_CONTRACT_INVALID')
    def test_wrong_contract_version_not_run(self):
        r,s,e=observation();s['contract_version']='0.3'
        self.assertEqual(result(r,s,e)['reason'],'ADAPTER_CONTRACT_INVALID')
    def test_status_body_contradiction_not_run(self):
        r,s,e=observation();s['data']['sut']['status']=201
        self.assertEqual(result(r,s,e)['reason'],'ADAPTER_STATUS_CONTRADICTION')
    def test_unknown_surface_not_run(self):
        r,s,e=observation();s['data']['sut']['surface']='rest'
        self.assertEqual(result(r,s,e)['reason'],'ADAPTER_CONTRACT_INVALID')
    def test_missing_evidence_ref_not_run(self):
        r,s,e=observation();s['evidence_refs']=[]
        self.assertEqual(result(r,s,e)['reason'],'EVIDENCE_REFERENCE_INVALID')
    def test_invalid_json_with_valid_digest_not_run(self):
        r,s,e=observation();ref=next(iter(e));raw=b'not-json';e[ref]=(r['run_id'],r['case_id'],raw)
        s['data']['sut']['body_sha256']=hashlib.sha256(raw).hexdigest()
        self.assertEqual(result(r,s,e)['reason'],'EVIDENCE_INVALID_JSON')
    def test_priority_fail_over_not_run(self):
        self.assertEqual(aggregate(['PASS','NOT_RUN','FAIL','NOT_APPLICABLE']),'FAIL')
    def test_priority_not_run_over_pass(self):
        self.assertEqual(aggregate(['PASS','NOT_RUN','NOT_APPLICABLE']),'NOT_RUN')
    def test_unclaimed_all_not_applicable(self):
        self.assertEqual(aggregate(['NOT_APPLICABLE']),'NOT_APPLICABLE')
    def test_unsupported_status_rejected(self):
        with self.assertRaises(ValueError):aggregate(['PASS','UNKNOWN'])
    def test_empty_aggregation_rejected(self):
        with self.assertRaises(ValueError):aggregate([])
    def test_real_http_accepted_config_and_evidence_owner(self):
        with services() as (mock,adapter):
            cfg=fixture_base();pid='s1-negative-'+uuid.uuid4().hex
            req,rsp=call(adapter,'CT-CFG-001',cfg,pid)
            _,stored=http('GET',mock.url+'/projects/'+pid)
            self.assertEqual(assess(req,rsp,adapter.evidence,expected_acceptance=True,stored=stored,source=cfg)['outcome'],'PASS')
    def test_real_http_case_isolation_and_ownership(self):
        with services() as (mock,adapter):
            cfg=fixture_base()
            r1,s1=call(adapter,'CT-CFG-001',cfg,'first-'+uuid.uuid4().hex)
            r2,s2=call(adapter,'CT-CFG-001',cfg,'second-'+uuid.uuid4().hex)
            self.assertNotEqual(s1['data']['sut']['body_ref'],s2['data']['sut']['body_ref'])
            ref=s1['data']['sut']['body_ref'];foreign=copy.deepcopy(s2)
            foreign['data']['sut']['body_ref']=ref
            foreign['data']['sut']['body_sha256']=s1['data']['sut']['body_sha256']
            foreign['evidence_refs']=[ref]
            self.assertEqual(assess(r2,foreign,adapter.evidence,expected_acceptance=True,source=cfg,stored={'config':cfg})['reason'],'EVIDENCE_WRONG_OWNER')
    def test_real_http_seed_defect_diagnosed(self):
        with services() as (mock,adapter):
            cfg=fixture_seed_full();cfg['project']['defect_classes'][0].pop('name')
            req,rsp=call(adapter,'CT-CFG-025.25',cfg,'seed-'+uuid.uuid4().hex)
            self.assertEqual(assess(req,rsp,adapter.evidence,expected_acceptance=False,
                missing_field='defect_classes[0].name')['outcome'],'PASS')

if __name__=='__main__':unittest.main()
