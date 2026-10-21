"""S3.0 declarative fixture and expected-predicate foundation; no SUT conformance claim.

Inputs are pre/post observations supplied by a future S3 adapter; S3.0 does NOT
execute a Decision Engine. Only explicitly allowlisted comparisons are accepted.
"""
from __future__ import annotations
import copy
import json
import math
from pathlib import Path

CATALOG = Path(__file__).with_name('foundation.json')
OPS = frozenset({'eq','contains','equals_path','number_or_not_computed',
                  'nonempty_string','gate_status_reasons_equal'})
CASES = ('CT-DEC-006','CT-DEC-012','CT-REL-006')

class ObservationUnavailable(Exception):
    pass


def catalog():
    return json.loads(CATALOG.read_text(encoding='utf-8'))


def read_path(record, path):
    if not isinstance(path,str) or not path or any(not part for part in path.split('.')):
        raise ObservationUnavailable('invalid field path')
    obj=record
    for part in path.split('.'):
        if not isinstance(obj,dict) or part not in obj:
            raise ObservationUnavailable('missing field: '+path)
        obj=obj[part]
    return obj


def gate_signature(gates):
    if not isinstance(gates,list):raise ObservationUnavailable('gates not a list')
    out=[]
    for gate in gates:
        if not isinstance(gate,dict):raise ObservationUnavailable('gate not a record')
        # ID differentiates multiple gates even when statuses/reasons coincide.
        for key in ('id','status','reasons'):
            if key not in gate:raise ObservationUnavailable('gate field missing: '+key)
        if not isinstance(gate['reasons'],list):raise ObservationUnavailable('reasons not list')
        out.append((gate['id'],gate['status'],tuple(sorted(gate['reasons']))))
    return sorted(out)


def predicate(check, observation):
    left=read_path(observation,check['path'])
    op=check['op']
    if op=='eq':return type(left)==type(check['value']) and left==check['value']
    if op=='contains':return isinstance(left,list) and check['value'] in left
    if op=='equals_path':return left==read_path(observation,check['value'])
    if op=='number_or_not_computed':
        return left=='not_computed' or (isinstance(left,(float,int)) and not isinstance(left,bool) and math.isfinite(left))
    if op=='nonempty_string':return isinstance(left,str) and bool(left.strip())
    if op=='gate_status_reasons_equal':return gate_signature(left)==gate_signature(read_path(observation,check['value']))
    raise ValueError('unsupported predicate: '+str(op))


def evaluate_checks(checks,observation):
    if not isinstance(observation,dict):return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE'}
    outcomes=[]
    for check in checks:
        try:
            ok=predicate(check,observation)
        except ObservationUnavailable as exc:
            return {'outcome':'NOT_RUN','reason':'OBSERVATION_INCOMPLETE','check_id':check['id'],'detail':str(exc)}
        except (TypeError,KeyError,ValueError) as exc:
            return {'outcome':'NOT_RUN','reason':'PREDICATE_INPUT_INVALID','check_id':check.get('id'),'detail':str(exc)}
        outcomes.append({'check_id':check['id'],'passed':ok})
    failing=[x['check_id'] for x in outcomes if not x['passed']]
    return {'outcome':'FAIL' if failing else 'PASS',
            'reason':'EXPECTED_VIOLATED' if failing else 'EXPECTED_MET',
            'checks':outcomes,'failed_checks':failing}


def evaluate(case,observation=None,*,claimed_capabilities=('human_review',),setup_ready=True,variant=None):
    cfg=catalog();entry=cfg['cases'][case]
    if entry.get('capability') and entry['capability'] not in claimed_capabilities:
        return {'outcome':'NOT_APPLICABLE','reason':'CAPABILITY_NOT_CLAIMED'}
    if not setup_ready:return {'outcome':'NOT_RUN','reason':'SETUP_FAILED'}
    if case=='CT-DEC-012':
        if variant not in entry['variants']:raise ValueError('variant required: a/b/c/d')
    elif variant is not None:raise ValueError('variant not supported')
    return evaluate_checks(entry['checks'],observation)


def evaluate_fixture(name,observation):
    return evaluate_checks(catalog()['fixtures'][name]['checks'],observation)


def summarize(variants):
    if not variants:raise ValueError('empty variant set')
    observed=[v['outcome'] for v in variants.values()]
    if any(x not in ('PASS','FAIL','NOT_RUN','NOT_APPLICABLE') for x in observed):raise ValueError('unknown outcome')
    return next(x for x in ('FAIL','NOT_RUN','PASS','NOT_APPLICABLE') if x in observed)


def validate_catalog():
    c=catalog()
    assert c['version']=='s3.0' and c['scope']=='DECISION_FOUNDATION_ONLY'
    assert set(c['cases'])==set(CASES)
    assert set(c['capabilities'])==set(CASES)
    assert set(c['cases']['CT-DEC-012']['variants'])==set('abcd')
    for name,entry in [*c['cases'].items(),*c['fixtures'].items()]:
        assert isinstance(entry['steps'],list) and entry['steps']
        checks=entry['checks'];assert checks and len(set(x['id'] for x in checks))==len(checks)
        for x in checks:
            assert x['op'] in OPS and isinstance(x['path'],str)
            if x['op'] in ('eq','contains','equals_path','gate_status_reasons_equal'):assert 'value' in x
            if x['op'] in ('equals_path','gate_status_reasons_equal'):assert isinstance(x['value'],str)
    return True
