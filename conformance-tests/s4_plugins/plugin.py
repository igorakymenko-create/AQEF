"""AQEF S4.1 CT-PLG-003, mock-only. Python stdlib, no remote SUT.

Runner and plugin invocation records are deliberately separate. Plugin's only
injected capabilities are its logical input dictionary; no host APIs are passed.
This checks the logical input contract, NOT OS sandboxing or process isolation.
"""
from __future__ import annotations
import copy
import uuid

CAPABILITY = 'plugins:validator'
CASE_ID = 'CT-PLG-003'
PLUGIN = 'cts-probe'
VERSION = '1.0.0'
EXPECTED_KEYS = frozenset({'evidence', 'clause', 'configuration', 'execution_id', 'clause_id'})


class PluginProbe:
    def __init__(self):
        self.calls = []

    def invoke(self, logical_input):
        self.calls.append(copy.deepcopy(logical_input))
        if logical_input['configuration'].get('malformed') is True:
            return {'oracle': {'name': PLUGIN, 'version': VERSION}, 'disposition': 'actionable'}
        return {'oracle': {'name': PLUGIN, 'version': VERSION},
                'disposition': 'actionable', 'verdict': 'pass'}


class PluginMock:
    """A minimal mock of plugin invocation and assessment, with fault injection."""
    def __init__(self, *, claims=True, mutation=None):
        self.claims = claims
        self.mutation = mutation
        self.probe = PluginProbe()
        self.results = {}
        self.events = []

    def describe(self):
        return {'capabilities': [CAPABILITY] if self.claims else []}

    def execute(self, *, marker, malformed=False):
        if not self.claims:
            raise ValueError('capability not claimed')
        if type(marker) is not int:
            raise ValueError('marker must be an integer')
        execution_id = 'execution-' + uuid.uuid4().hex
        clause_id = 'constraint-1'
        response = 'Hello! How can I help?'
        logical_input = {
            'evidence': {'response': response},
            'clause': {'target': 'response', 'dimension': 'functional',
                       'expected': {'marker': marker}},
            'configuration': {'plugin': PLUGIN, 'version': VERSION,
                              'malformed': bool(malformed)},
            'execution_id': execution_id,
            'clause_id': clause_id,
        }
        if self.mutation == 'extra_input':
            logical_input['secret_token'] = 'mock-secret'
        elif self.mutation == 'missing_input':
            logical_input.pop('clause_id')
        elif self.mutation == 'wrong_expected':
            logical_input['clause']['expected'] = {'marker': 1 if marker == 2 else 2}
        elif self.mutation == 'wrong_response':
            logical_input['evidence']['response'] = 'WRONG RESPONSE'
        elif self.mutation == 'wrong_version_input':
            logical_input['configuration']['version'] = '0.0.0'
        try:
            response_from_plugin = self.probe.invoke(logical_input)
        except Exception:
            response_from_plugin = None
        # Validator Result validation occurs before assessment; malformed is not fail.
        valid = (isinstance(response_from_plugin, dict)
                 and response_from_plugin.get('verdict') in ('pass', 'fail')
                 and response_from_plugin.get('disposition') == 'actionable'
                 and response_from_plugin.get('oracle') == {'name': PLUGIN, 'version': VERSION})
        if valid:
            result = {'id': 'result-' + uuid.uuid4().hex, 'execution_id': execution_id,
                      'clause_id': clause_id, 'oracle': copy.deepcopy(response_from_plugin['oracle']),
                      'verdict': response_from_plugin['verdict'], 'disposition': 'actionable'}
        else:
            result = {'id': 'result-' + uuid.uuid4().hex, 'execution_id': execution_id,
                      'clause_id': clause_id, 'oracle': {'name': PLUGIN, 'version': VERSION},
                      'verdict': None, 'disposition': 'oracle_unavailable'}
        if self.mutation == 'malformed_as_fail' and malformed:
            result.update({'verdict': 'fail', 'disposition': 'actionable'})
        elif self.mutation == 'malformed_preserved' and malformed:
            result.pop('verdict')
        elif self.mutation == 'wrong_oracle':
            result['oracle']['version'] = '9.9.9'
        elif self.mutation == 'cross_execution':
            result['execution_id'] = 'execution-other'
        elif self.mutation == 'wrong_clause_id':
            result['clause_id'] = 'constraint-other'
        self.results[execution_id] = result
        self.events.append({'type': 'plugin_invoked', 'execution_id': execution_id,
                            'clause_id': clause_id})
        # Assessment must not call Judge when the validator is unavailable.
        if malformed and self.mutation == 'judge_on_malformed':
            self.events.append({'type': 'call_received', 'kind': 'judge',
                                'execution_id': execution_id})
        return execution_id

    def read(self, execution_id):
        return {'result': copy.deepcopy(self.results[execution_id]),
                'plugin_calls': copy.deepcopy(self.probe.calls),
                'events': copy.deepcopy(self.events)}


def assess(*, claims, execution_id=None, readback=None, marker=1, malformed=False):
    """Independent runner-owned oracle; never trusts SUT's own PASS label."""
    if not claims:
        return {'outcome': 'NOT_APPLICABLE', 'reason': 'CAPABILITY_UNCLAIMED'}
    if not isinstance(readback, dict) or not isinstance(execution_id, str):
        return {'outcome': 'NOT_RUN', 'reason': 'READBACK_UNAVAILABLE'}
    calls, result, events = (readback.get(k) for k in ('plugin_calls', 'result', 'events'))
    if not isinstance(calls, list) or len(calls) != 1 or not isinstance(calls[0], dict):
        return {'outcome': 'NOT_RUN', 'reason': 'PLUGIN_INPUT_LOG_UNAVAILABLE'}
    if not isinstance(result, dict) or not isinstance(events, list):
        return {'outcome': 'NOT_RUN', 'reason': 'RESULT_OR_LOG_UNAVAILABLE'}
    inp = calls[0]
    if set(inp) != EXPECTED_KEYS:
        return {'outcome': 'FAIL', 'reason': 'PLUGIN_INPUT_SCOPE_VIOLATION'}
    if (inp['evidence'] != {'response': 'Hello! How can I help?'}
        or inp['clause'] != {'target': 'response', 'dimension': 'functional', 'expected': {'marker': marker}}
        or inp['configuration'] != {'plugin': PLUGIN, 'version': VERSION, 'malformed': malformed}
        or inp['execution_id'] != execution_id or inp['clause_id'] != 'constraint-1'):
        return {'outcome': 'FAIL', 'reason': 'PLUGIN_INPUT_CONTENT_VIOLATION'}
    if (result.get('execution_id') != execution_id or result.get('clause_id') != 'constraint-1'
        or result.get('oracle') != {'name': PLUGIN, 'version': VERSION}):
        return {'outcome': 'FAIL', 'reason': 'RESULT_ATTRIBUTION_VIOLATION'}
    judge_calls = [ev for ev in events if isinstance(ev, dict)
                   and ev.get('type') == 'call_received' and ev.get('kind') == 'judge']
    if malformed:
        if result.get('disposition') != 'oracle_unavailable' or 'verdict' not in result or result['verdict'] is not None:
            return {'outcome': 'FAIL', 'reason': 'MALFORMED_RESULT_NOT_ISOLATED'}
        if judge_calls:
            return {'outcome': 'FAIL', 'reason': 'JUDGE_CALLED_AFTER_MALFORMED_VALIDATOR'}
    else:
        if result.get('disposition') != 'actionable' or result.get('verdict') != 'pass':
            return {'outcome': 'FAIL', 'reason': 'VALID_PLUGIN_RESULT_NOT_PASS'}
    return {'outcome': 'PASS', 'reason': 'EXPECTED_MET'}


def run_ct_plg_003(*, marker=1, malformed=False, mutation=None, claims=True, readback_damage=None):
    sut = PluginMock(claims=claims, mutation=mutation)
    if CAPABILITY not in sut.describe()['capabilities']:
        return assess(claims=False)
    try:
        execution_id = sut.execute(marker=marker, malformed=malformed)
        observed = sut.read(execution_id)
    except (ValueError, KeyError, TypeError):
        return {'outcome': 'NOT_RUN', 'reason': 'FIXTURE_OR_READBACK_UNAVAILABLE'}
    if readback_damage == 'absent':
        observed = None
    elif readback_damage == 'calls':
        observed['plugin_calls'] = None
    elif readback_damage == 'result':
        observed['result'] = None
    elif readback_damage == 'events':
        observed['events'] = None
    return assess(claims=True, execution_id=execution_id, readback=observed,
                  marker=marker, malformed=malformed)


def trace_matrix():
    return {'scope': 'S4.1_CT_PLG_003_MOCK_ONLY',
            'healthy': run_ct_plg_003(marker=1),
            'malformed': run_ct_plg_003(marker=2, malformed=True),
            'extra_input_mutant': run_ct_plg_003(mutation='extra_input'),
            'malformed_as_fail_mutant': run_ct_plg_003(marker=2, malformed=True, mutation='malformed_as_fail'),
            'judge_after_malformed_mutant': run_ct_plg_003(marker=2, malformed=True, mutation='judge_on_malformed'),
            'no_log': run_ct_plg_003(readback_damage='calls'),
            'unclaimed': run_ct_plg_003(claims=False)}
