"""S1 selected CTS cases. Outcomes refer to the mock SUT, not AQEF certification."""
import copy,uuid
from mock import MockSUT,fixture_base,fixture_seed
from adapter import S1Adapter

CASES=('CT-CFG-001','CT-CFG-025.01','CT-CFG-025.05','CT-CFG-025.25')

def summarize(cases):
    statuses=[v['outcome'] for v in cases.values()]
    if 'FAIL' in statuses:return 'FAIL'
    if 'NOT_RUN' in statuses:return 'NOT_RUN'
    if 'PASS' in statuses:return 'PASS'
    return 'NOT_APPLICABLE'

def run_suite(mutation=None,seeded_controls=True,setup_available=True):
    sut=MockSUT(mutation,{'seeded_controls'} if seeded_controls else set());ad=S1Adapter(sut)
    observations={}
    for case in CASES:
        if case=='CT-CFG-025.25' and not seeded_controls:
            observations[case]={'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_NOT_CLAIMED'};continue
        if not setup_available:
            observations[case]={'outcome':'NOT_RUN','reason':'SETUP_FAILED'};continue
        source=fixture_seed() if case.endswith('.25') else fixture_base()
        if case.endswith('.01'):source['project'].pop('name')
        if case.endswith('.05'):source['project']['environments'][0].pop('tool_configuration')
        if case.endswith('.25'):source['project']['defect_classes'][0].pop('name')
        pid='cts-'+case.replace('.','-')+'-'+uuid.uuid4().hex[:8]
        req={'contract_version':'0.4','operation':'load_config','run_id':'s1-'+uuid.uuid4().hex,
             'case_id':case,'session_id':'session-'+uuid.uuid4().hex,
             'correlation_id':'corr-'+uuid.uuid4().hex,'timeout_ms':10000,
             'arguments':{'project_id':pid,'config':source}}
        resp=ad.operation(req);body=ad.read_body(resp);sutx=resp['data']['sut']
        accepted=sutx['outcome']=='accepted'
        if case=='CT-CFG-001':
            actual=sut.get(pid)[1].get('config') if accepted else None
            ok=accepted and actual==source
            expected='accepted and persisted byte-semantically unchanged'
        else:
            missing={'CT-CFG-025.01':'project.name','CT-CFG-025.05':'environments[0].tool_configuration','CT-CFG-025.25':'defect_classes[0].name'}[case]
            diagnostic=' '.join(str(v) for v in body.values()) if isinstance(body,dict) else ''
            ok=(not accepted and missing in diagnostic)
            expected='rejected with diagnostic naming '+missing
        observations[case]={'outcome':'PASS' if ok else 'FAIL','expected':expected,
                            'observed_sut_outcome':sutx['outcome'],'sut_status':sutx['status'],
                            'evidence_ref':sutx['body_ref'],'evidence_sha256':sutx['body_sha256']}
    return {'scope':'S1_MOCK_ONLY','cases':observations,
            'CT-CFG-025':summarize({k:v for k,v in observations.items() if k.startswith('CT-CFG-025.')})}
