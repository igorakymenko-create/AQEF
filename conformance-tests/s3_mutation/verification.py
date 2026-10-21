"""Stage C S3.2 adversarial, mock-only Decision verification.
The independent assessor never trusts a SUT-supplied PASS. No production conformance claim.
"""
from __future__ import annotations
import copy
import hashlib
import json
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
for path in (ROOT / 's3_decision', ROOT / 's1_configuration', ROOT / 'harness' / 's02_harness'):
    sys.path.insert(0, str(path))
from foundation import evaluate, summarize, gate_signature
from decision_engine import MockDecision, run_dec006, run_dec012_variant, run_dec012, run_rel006
from harness import Harness


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def evidence_verdict(req, response, store):
    """Attests response metadata and stored bytes; incomplete evidence -> NOT_RUN."""
    try:
        if not isinstance(req, dict) or not isinstance(response, dict):
            return {'outcome': 'NOT_RUN', 'reason': 'EVIDENCE_UNAVAILABLE'}
        if response['contract_version'] != '0.4' or response['correlation_id'] != req['correlation_id']:
            return {'outcome': 'NOT_RUN', 'reason': 'EVIDENCE_IDENTITY_MISMATCH'}
        if response.get('success') is not True:
            return {'outcome': 'NOT_RUN', 'reason': 'ADAPTER_NOT_SUCCESSFUL'}
        info = response['data']['sut']
        ref = info['body_ref']
        if response['evidence_refs'] != [ref]:
            return {'outcome': 'NOT_RUN', 'reason': 'EVIDENCE_REFS_INVALID'}
        run, case, raw = store[ref]
        if (run, case) != (req['run_id'], req['case_id']) or not isinstance(raw, bytes):
            return {'outcome': 'NOT_RUN', 'reason': 'EVIDENCE_OWNER_MISMATCH'}
        if hashlib.sha256(raw).hexdigest() != info['body_sha256']:
            return {'outcome': 'NOT_RUN', 'reason': 'EVIDENCE_HASH_MISMATCH'}
        json.loads(raw)
        return {'outcome': 'PASS', 'reason': 'EVIDENCE_VALID'}
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, AttributeError):
        return {'outcome': 'NOT_RUN', 'reason': 'EVIDENCE_UNAVAILABLE'}


def evidence_probe(damage=None):
    req = {'run_id': 'run-1', 'case_id': 'CT-DEC-012.a', 'correlation_id': 'corr-1'}
    raw = canon({'results': [{'id': 'judge-1'}], 'terminal': 'completed'})
    ref = 'evidence://decision-1'
    rsp = {'contract_version': '0.4', 'correlation_id': 'corr-1', 'success': True,
           'data': {'sut': {'body_ref': ref, 'body_sha256': hashlib.sha256(raw).hexdigest()}},
           'evidence_refs': [ref]}
    store = {ref: ('run-1', 'CT-DEC-012.a', raw)}
    if damage == 'bytes': store[ref] = ('run-1', 'CT-DEC-012.a', raw + b'!')
    if damage == 'missing': store.pop(ref)
    if damage == 'wrong_case': store[ref] = ('run-1', 'CT-DEC-012.b', raw)
    if damage == 'wrong_run': store[ref] = ('run-2', 'CT-DEC-012.a', raw)
    if damage == 'correlation': rsp['correlation_id'] = 'other'
    if damage == 'refs': rsp['evidence_refs'] = []
    if damage == 'version': rsp['contract_version'] = '0.3'
    if damage == 'truncated': store[ref] = ('run-1', 'CT-DEC-012.a', raw[:-6])
    return evidence_verdict(req, rsp, store)


def review_probe(variant='a', mutation=None, tamper=None):
    """Run a real MockDecision sequence and independently compare pre/post state."""
    if variant not in 'abcd' or len(variant) != 1:
        raise ValueError('invalid variant')
    m = MockDecision(mutation)
    first = m.execute('J-PASS-90' if variant == 'c' else 'J-PASS-60')
    if variant in 'ab':
        setup = m.review('P-REVIEWER', first['id'], 'pass')
        if not setup['accepted']:
            return {'outcome': 'NOT_RUN', 'reason': 'FIXTURE_UNAVAILABLE'}
    m.evaluate_gates()
    before = {'results': copy.deepcopy(m.results), 'effective_result': m.effective(), 'gates': copy.deepcopy(m.gates)}
    target = m.results[-1]['id'] if variant == 'b' else first['id']
    attempt = m.review('P-NOPERM' if variant == 'd' else 'P-REVIEWER', target, 'fail')
    if mutation == 'mutate_rejected_results' and not attempt['accepted']:
        m.results[0]['verdict'] = 'fail'
    new_gate = m.evaluate_gates()
    if mutation == 'mutate_rejected_gate' and not attempt['accepted']:
        new_gate['reasons'] = ['changed']
    after = {'review_attempt': {'accepted': attempt['accepted']}, 'results': copy.deepcopy(m.results),
             'effective_result': m.effective(), 'gates': [new_gate]}
    if tamper == 'missing_after': after.pop('results')
    if tamper == 'missing_before': before.pop('results')
    return evaluate('CT-DEC-012', {'before': before, 'after': after}, variant=variant)


def override_probe(mutation=None, tamper=None):
    """Two attempts, same GateResult, no re-evaluation between attempts."""
    m = MockDecision(mutation)
    m.execute('J-FAIL-90')
    gate = m.evaluate_gates()
    count = m.evaluation_count
    first = m.release()
    approved = m.override()
    second = m.release()
    after = copy.deepcopy(m.gates[0])
    observation = {'before': {'release_attempt': first, 'gate': gate},
                   'after': {'release_attempt': second, 'gate': after}}
    if tamper == 'missing_approval': observation['after']['gate'].pop('override', None)
    if tamper == 'changed_gate_id': observation['after']['gate']['id'] = 'another-gate'
    if tamper == 'changed_evaluation': observation['after']['gate']['evaluation_id'] = 'new-evaluation'
    if tamper == 'missing_after': observation.pop('after')
    outcome = evaluate('CT-REL-006', observation)
    if outcome['outcome'] == 'PASS' and (not approved['accepted'] or m.evaluation_count != count):
        return {'outcome': 'FAIL', 'reason': 'OVERRIDE_LIFECYCLE_VIOLATION'}
    return outcome


def negative_observation(late=False, closed=True):
    """Zero-drain *unit* check only; not proof of Q-05 timing compliance."""
    h = Harness()
    sid = h.begin('s32-' + uuid.uuid4().hex)
    if not closed:
        return h.negative_assertion(sid, 'judge', 0)
    h.close_observation(sid, drain_ms=0, terminal_observed=True)
    if late:
        try:
            h.invoke(sid, 'judge', {'response': 'Hello'}, correlation_id='late')
        except RuntimeError:
            pass
    return h.negative_assertion(sid, 'judge', 0)


def matrix():
    good = {'CT-DEC-006': run_dec006(), 'CT-DEC-012': run_dec012(), 'CT-REL-006': run_rel006()}
    bad = {
        'non_actionable_pass': run_dec006('gate_pass_nonactionable'),
        'repeat_review': review_probe('a', 'allow_repeat_review'),
        'review_actionable': review_probe('c', 'allow_actionable_review'),
        'unprivileged_review': review_probe('d', 'allow_unprivileged_review'),
        'result_changed_on_reject': review_probe('b', 'mutate_rejected_results'),
        'gate_changed_on_reject': review_probe('a', 'mutate_rejected_gate'),
        'release_without_override': override_probe('release_without_override'),
        'override_changed_gate_status': override_probe('override_as_pass'),
        'override_missing_approver': override_probe('omit_approver'),
        'override_missing_justification': override_probe('omit_justification'),
        'override_changed_evaluation': override_probe('re_evaluate_on_override')}
    return {'scope': 'S3.2_MOCK_ONLY', 'good': good, 'mutants': bad,
            'good_aggregate': summarize(good), 'mutant_aggregate': summarize(bad)}
