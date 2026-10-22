"""S3.5.5 Q-05: reusable measured negative-observation closure (MOCK ONLY).

Reuses S3.5.3 calibration and real S0 Harness event clocks. All dependent
legacy negative assertions must consume this helper, not drain_ms=0.
"""
from __future__ import annotations
import functools
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 's35_timing'))
from timing import measured_profile


@functools.lru_cache(maxsize=1)
def local_profile():
    """Cache *local process* calibration; not a remote SUT timing guarantee."""
    return measured_profile()


def observe_closed(harness, session_id, kind, expected_count=0, *,
                   terminal_observed=True, max_budget_ms=2000, profile=None):
    """Return PASS / FAIL / NOT_RUN using real elapsed time and event log.

    Budget/terminal/calibration failures MUST NOT be turned into PASS by the
    underlying Harness. Existing harness phase stays open on preflight NOT_RUN.
    """
    if kind not in ('subject', 'judge') or type(expected_count) is not int or expected_count < 0:
        return {'outcome': 'NOT_RUN', 'reason': 'OBSERVATION_PARAMETERS_INVALID'}
    if not terminal_observed:
        return {'outcome': 'NOT_RUN', 'reason': 'TERMINAL_UNOBSERVED'}
    if type(max_budget_ms) is not int or max_budget_ms <= 0:
        return {'outcome': 'NOT_RUN', 'reason': 'OBSERVATION_BUDGET_INVALID'}
    if profile is None:
        try:
            profile = local_profile()
        except (ValueError, RuntimeError, OverflowError):
            return {'outcome': 'NOT_RUN', 'reason': 'CALIBRATION_UNAVAILABLE'}
    if not isinstance(profile, dict) or profile.get('source') != 'MEASURED_LOCAL_MOCK_ONLY':
        return {'outcome': 'NOT_RUN', 'reason': 'CALIBRATION_UNAVAILABLE'}
    drain_ms = profile.get('drain_ms')
    if (type(drain_ms) is not int or drain_ms <= 0 or
            profile.get('clock_id') != harness.clock_id):
        return {'outcome': 'NOT_RUN', 'reason': 'CALIBRATION_INVALID'}
    if drain_ms > max_budget_ms:
        return {'outcome': 'NOT_RUN', 'reason': 'OBSERVATION_BUDGET_INSUFFICIENT'}
    try:
        start = time.monotonic_ns()
        harness.close_observation(session_id, drain_ms=drain_ms, terminal_observed=True)
        elapsed_ms = (time.monotonic_ns() - start) / 1e6
        events = harness.read_log(session_id)
        marks = [e for e in events if e.get('type') == 'observation_watermark']
        closures = [e for e in events if e.get('type') == 'observation_closed']
        if len(marks) != 1 or len(closures) != 1:
            return {'outcome': 'NOT_RUN', 'reason': 'WATERMARK_UNAVAILABLE'}
        mark, closed = marks[0], closures[0]
        sequence_ok = (
            mark['clock_id'] == closed['clock_id'] == harness.clock_id and
            closed['sequence'] == mark['sequence'] + 1 and
            closed['attributes']['watermark'] == mark['sequence'] and
            mark['attributes']['highest_sequence'] == mark['sequence'] - 1 and
            closed['observed_monotonic_ns'] >= mark['observed_monotonic_ns']
        )
        if not sequence_ok or elapsed_ms < drain_ms:
            return {'outcome': 'NOT_RUN', 'reason': 'OBSERVATION_TIMING_UNTRUSTWORTHY'}
        raw = harness.negative_assertion(session_id, kind, expected_count=expected_count)
        if raw.get('outcome') not in ('PASS', 'FAIL'):
            return {'outcome': 'NOT_RUN', 'reason': 'OBSERVATION_INCOMPLETE'}
        return {**raw, 'reason': ('EXPECTED_MET' if raw['outcome'] == 'PASS'
                                  else 'NEGATIVE_ASSERTION_VIOLATED'),
                'drain_ms': drain_ms, 'elapsed_ms': elapsed_ms,
                'clock_id': harness.clock_id,
                'watermark': mark['attributes']['highest_sequence']}
    except (KeyError, AttributeError, TypeError, ValueError, RuntimeError):
        return {'outcome': 'NOT_RUN', 'reason': 'OBSERVATION_UNAVAILABLE'}
