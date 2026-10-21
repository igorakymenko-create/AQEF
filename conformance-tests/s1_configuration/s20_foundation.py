"""S2.0: reviewed CTS field map, predicates and canonical outcome policy.
Mock-only. Does not certify a real AQEF implementation.
"""
from __future__ import annotations
import json
from pathlib import Path
from negative import assess, aggregate

SPEC_PATH=Path(__file__).with_name('s20_contract.json')
CASES=('CT-CFG-001','CT-CFG-025.01','CT-CFG-025.05','CT-CFG-025.25')

def spec():
    return json.loads(SPEC_PATH.read_text(encoding='utf8'))

def field(root, dotted):
    """Strict path resolution: no implicit defaults, no computed/evaluated paths."""
    obj=root
    for key in dotted.split('.'):
        if not isinstance(obj,dict) or key not in obj:
            raise KeyError(dotted)
        obj=obj[key]
    return obj

def validate_contract(s=None):
    s=spec() if s is None else s
    assert s['surface'] in ('equivalent','appendix_c_rest')
    assert set(s['predicates'])==set(CASES)
    assert s['outcomes']['precedence']==['FAIL','NOT_RUN','PASS','NOT_APPLICABLE']
    assert len(s['fields'])==len(set(s['fields'].values()))
    for k,rule in s['predicates'].items():
        assert rule['kind'] in ('accepted_and_preserved','rejected_with_diagnostic')
        assert rule['fixture'] in ('F-BASE','F-SEED')
        assert rule['required_capability'] in ('core','seeded_controls')
        if rule['kind']=='rejected_with_diagnostic':
            assert rule['missing_field'] in ('project.name','environments[0].tool_configuration','defect_classes[0].name')
        else:
            assert 'missing_field' not in rule
    return True

def evaluate(case,req,rsp,evidence,*,source=None,stored=None,capabilities=('seeded_controls',),setup_ready=True):
    """ONE shared scorer: CTS-specific declarative expectations -> negative.assess.
    Capability and setup are evaluated before observing a SUT.
    """
    cfg=spec()['predicates'][case]
    if cfg['required_capability']!='core' and cfg['required_capability'] not in capabilities:
        return {'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_NOT_CLAIMED'}
    if not setup_ready:
        return {'outcome':'NOT_RUN','reason':'SETUP_FAILED'}
    return assess(req,rsp,evidence,
                  expected_acceptance=cfg['kind']=='accepted_and_preserved',
                  missing_field=cfg.get('missing_field'),stored=stored,source=source)

def summary(cases):
    if not cases: raise ValueError('no cases')
    return aggregate([r['outcome'] for r in cases.values()])

def make_time_profile(*,measured_max_delay_ms=200,drain_ms=5000,wait_ms=10000,grace_ms=5000):
    """Harness Contract 9.2 and 11 recommendations; milliseconds and same-clock measurement.

    Measurement must be supplied from the real harness before production S2 exit.
    Defaults are proposed run-profile settings, not asserted measured values.
    """
    for value in (measured_max_delay_ms,drain_ms,wait_ms,grace_ms):
        if isinstance(value,bool) or not isinstance(value,int) or value<0:
            raise ValueError('time values must be nonnegative integer milliseconds')
    if wait_ms<=0: raise ValueError('waiting budget must be positive')
    if drain_ms<max(5000,2*measured_max_delay_ms):
        raise ValueError('drain below Harness Contract 11 SHOULD floor')
    if grace_ms<max(5000,(wait_ms+9)//10):
        raise ValueError('grace below Harness Contract 9.2 SHOULD floor')
    return {'clock_id':'runner-monotonic','clock_profile':'real_monotonic',
            'measured_max_sut_to_harness_delay_ms':measured_max_delay_ms,
            'measurement_provenance':'CONFIGURED_PLACEHOLDER_NOT_MEASURED',
            'drain_ms':drain_ms,'wait_ms':wait_ms,'grace_ms':grace_ms,
            'negative_assertions_require_observation_closed':True}

def canonical_http_suite(mutation=None,seeded_controls=True,setup_available=True):
    """Reuse actual two-hop HTTP S1 services, but decide with the canonical assessor.
    Maintains separate case projects, setup checks, evidence ownership, and GET checks.
    """
    import copy,uuid
    from urllib.parse import quote
    from s1_rest import services,http,call,fixture_seed_full
    from mock import fixture_base
    cases={}
    with services(mutation,('seeded_controls',) if seeded_controls else ()) as (mock,adapter):
        for case in CASES:
            capabilities=('seeded_controls',) if seeded_controls else ()
            if case=='CT-CFG-025.25' and not seeded_controls:
                cases[case]=evaluate(case,None,None,{},capabilities=capabilities)
                continue
            if not setup_available:
                cases[case]=evaluate(case,None,None,{},setup_ready=False)
                continue
            source=fixture_seed_full() if case.endswith('.25') else fixture_base()
            if case!='CT-CFG-001':
                st,data=http('POST',mock.url+'/projects',
                             {'project_id':'setup-'+uuid.uuid4().hex,'config':source})
                if st not in (200,201,202) or data.get('config')!=source:
                    cases[case]=evaluate(case,None,None,{},setup_ready=False)
                    continue
            cfg=copy.deepcopy(source)
            key=spec()['predicates'][case].get('missing_field')
            if key=='project.name': cfg['project'].pop('name')
            elif key=='environments[0].tool_configuration':
                cfg['project']['environments'][0].pop('tool_configuration')
            elif key=='defect_classes[0].name':
                cfg['project']['defect_classes'][0].pop('name')
            pid='s20-'+uuid.uuid4().hex
            try:
                req,rsp=call(adapter,case,cfg,pid)
                stored=None
                if case=='CT-CFG-001':
                    status,stored=http('GET',mock.url+'/projects/'+quote(pid,safe=''))
                    if status!=200:stored=None
                cases[case]=evaluate(case,req,rsp,adapter.evidence,source=cfg,stored=stored,
                                     capabilities=capabilities)
            except (OSError,ValueError,AssertionError,KeyError) as exc:
                cases[case]={'outcome':'NOT_RUN','reason':'HARNESS_FAILURE','diagnostic':type(exc).__name__}
    return {'scope':'S1_HTTP_MOCK_ONLY','cases':cases,
            'CT-CFG-025':summary({k:v for k,v in cases.items() if k.startswith('CT-CFG-025.')})}
