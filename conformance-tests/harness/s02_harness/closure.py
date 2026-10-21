"""S0.2 closure policy. NOT a SUT plugin implementation or a CTS runner.

Three CTS §2.5 plugin behaviors have deterministic local self-test oracles.
Future CTS plugin fixtures cts-probe/cts-reach are explicitly deferred.
Evidence attribution is fail-closed: missing/invalid dependent raw evidence -> NOT_RUN.
"""
from __future__ import annotations
from dataclasses import dataclass

PLUGIN_REQUIRED = ('cts-len', 'cts-flaky', 'cts-crash')
DEFERRED = ('cts-probe', 'cts-reach')


class LocalPlugin:
    """Harness-local simulated validator, not a plugin registered in any SUT."""
    def __init__(self, name):
        if name not in PLUGIN_REQUIRED:
            raise ValueError('unknown local validator')
        self.name = name
        self.calls = 0

    def evaluate(self, response):
        self.calls += 1
        if self.name == 'cts-len':
            return 'pass' if len(response) >= 1 else 'fail'
        if self.name == 'cts-flaky':
            return 'pass' if self.calls == 1 else 'fail'
        raise RuntimeError('cts-crash: scripted validator failure')


def local_plugin_self_test(name):
    """Check CTS 2.5 observations, including first-call reset in a fresh instance."""
    if name in DEFERRED:
        return {'behavior': name, 'status': 'NOT_RUN', 'reason': 'DEFERRED_TO_S4'}
    if name not in PLUGIN_REQUIRED:
        raise ValueError('unknown CTS plugin')
    try:
        obj = LocalPlugin(name)
        if name == 'cts-len':
            assert obj.evaluate('a') == 'pass'
            assert obj.evaluate('') == 'fail'
        elif name == 'cts-flaky':
            assert obj.evaluate('a') == 'pass'
            assert obj.evaluate('a') == 'fail'
            obj = LocalPlugin(name)
            assert obj.evaluate('a') == 'pass', 'fresh instance did not reset first-call behavior'
        else:
            try:
                obj.evaluate('a')
            except RuntimeError:
                pass
            else:
                raise AssertionError('cts-crash must raise')
        return {'behavior': name, 'status': 'PASS', 'scope': 'HARNESS_LOCAL_ONLY'}
    except Exception as ex:
        return {'behavior': name, 'status': 'FAIL', 'reason': repr(ex)}


def summarize_s0(scripted_result):
    """Separate S0 required behaviors from future extension fixtures.

    The existing selftest.run currently returns NOT_RUN for all five plugins.
    Replace ONLY the three CTS 2.5 entries with independently verified local
    self-test outcomes; the remaining two are deferred, never counted as PASS.
    """
    original = {x['behavior']: dict(x) for x in scripted_result['results']}
    if not set(PLUGIN_REQUIRED + DEFERRED).issubset(original):
        raise ValueError('expected full selftest result with known plugin fixtures')
    for code in PLUGIN_REQUIRED:
        original[code] = local_plugin_self_test(code)
    for code in DEFERRED:
        original[code] = local_plugin_self_test(code)
    required = [x for key, x in original.items() if key not in DEFERRED]
    blockers = [x for x in required if x['status'] != 'PASS']
    return {
        'status': 'PASS' if not blockers else 'INCOMPLETE',
        'scope': 'S0_HARNESS_LOCAL_ONLY',
        'results': list(original.values()),
        'required_count': len(required),
        'required_passed': len(required)-len(blockers),
        'blockers': [x['behavior'] for x in blockers],
        'deferred': list(DEFERRED),
        'limitations': ['SUT_PLUGIN_INTEGRATION_NOT_TESTED', 'CTS_RUNNER_NOT_IMPLEMENTED'],
    }


def attribute_evidence_case(evidence, run_id, case_id, evidence_refs, observed_outcome):
    """Reference decision rule for a future CTS runner, without altering source verdict.

    Resolver validates exact captured bytes and ownership of every evidence ref.
    Evidence errors produce NOT_RUN, not an ungrounded FAIL/PASS.
    """
    if observed_outcome not in ('PASS','FAIL','NOT_RUN','NOT_APPLICABLE'):
        raise ValueError('invalid outcome')
    if not evidence_refs:
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_MISSING','prior_outcome':observed_outcome}
    registered = [entry for rid,entry in evidence.entries if rid == run_id and entry['case_id'] == case_id]
    expected = {e['raw_ref'] for e in registered}
    if not expected or set(evidence_refs) != expected or len(set(evidence_refs)) != len(evidence_refs):
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_INCOMPLETE','prior_outcome':observed_outcome}
    try:
        for ref in evidence_refs:
            evidence.resolve_verified(ref,run_id)
    except (ValueError, FileNotFoundError, OSError) as ex:
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED',
                'prior_outcome':observed_outcome,'diagnostic':type(ex).__name__}
    return {'outcome':observed_outcome,'reason':'EVIDENCE_VERIFIED'}
