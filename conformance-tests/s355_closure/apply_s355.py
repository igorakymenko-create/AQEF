"""Idempotent exact-match patcher, meant to run ONCE inside a checked-out AQEF repo.
Refuses unknown versions and writes atomically, with no changes if checks fail.
"""
from __future__ import annotations
import json
import os
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]

PATCHES = {
    'conformance-tests/s2_assessment/assessment.py': (
        """        # drain=0 is a deliberately FAST MOCK-SPECIFIC unit setting, NOT Q-05 closure readiness.
        # Negative assertions still require a closed observation with a watermark.
        mock.h.close_observation(sid,drain_ms=0,terminal_observed=True)
        no_judge=mock.h.negative_assertion(sid,'judge',expected_count=0)""",
        """        # Q-05: shared calibrated closure, not a zero-drain unit shortcut.
        sys.path.insert(0,str(ROOT/'s355_closure'))
        from observation import observe_closed
        no_judge=observe_closed(mock.h,sid,'judge',expected_count=0)
        if no_judge['outcome']=='NOT_RUN':return no_judge""",
    ),
    'conformance-tests/s3_mutation/verification.py': (
        """    \"\"\"Zero-drain *unit* check only; not proof of Q-05 timing compliance.\"\"\"
    h = Harness()
    sid = h.begin('s32-' + uuid.uuid4().hex)
    if not closed:
        return h.negative_assertion(sid, 'judge', 0)
    h.close_observation(sid, drain_ms=0, terminal_observed=True)
    if late:""",
        """    \"\"\"Q-05 measured close; late events still evaluated after closure.\"\"\"
    h = Harness()
    sid = h.begin('s32-' + uuid.uuid4().hex)
    if not closed:
        return h.negative_assertion(sid, 'judge', 0)
    sys.path.insert(0, str(ROOT / 's355_closure'))
    from observation import observe_closed
    observed = observe_closed(h, sid, 'judge', expected_count=0)
    if observed['outcome'] == 'NOT_RUN':
        return observed
    if late:""",
    ),
    'conformance-tests/s35_integration/pipeline.py': (
        """        # Deliberately fast unit observation. Q-05 measured timing remains OPEN.
        mock.h.close_observation(sid,drain_ms=0,terminal_observed=True)
        obs=mock.h.negative_assertion(sid,'subject',expected_count=2 if profile=='retry' else 1)""",
        """        # Q-05: observed terminal state with measured, positive drain.
        sys.path.insert(0,str(ROOT/'s355_closure'))
        from observation import observe_closed
        obs=observe_closed(mock.h,sid,'subject',expected_count=2 if profile=='retry' else 1)
        if obs['outcome']=='NOT_RUN':return obs""",
    ),
}


def apply():
    changed = {}
    for name, (old, new) in PATCHES.items():
        path = ROOT / name
        data = path.read_text(encoding='utf-8')
        if data.count(old) == 1:
            changed[path] = data.replace(old, new, 1)
        elif data.count(new) == 1 and old not in data:
            continue  # idempotent
        else:
            raise RuntimeError('Source differs; refusing partial patch: ' + name)
    # Audit register intentionally remains PARTIAL until full CI verification,
    # then requires an explicit audit decision and commit-specific evidence.
    for path, content in changed.items():
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.s355-')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
            os.replace(tmp, path)
        finally:
            pathlib.Path(tmp).unlink(missing_ok=True)
    return list(map(str, changed))


if __name__ == '__main__':
    print('\n'.join(apply()) or 'Already patched')
