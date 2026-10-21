"""CTS §2.8 scripted-behavior checks, isolated from IUT and case observations.

A failing check is recorded in the caller's harness log and surfaced as unusable.
No successful S0 verdict is emitted for unimplemented SUT plugin validators.
"""
from __future__ import annotations
import time, uuid
from harness import Harness

SUBJECTS = ['SR-OK','SR-EMPTY','SR-ECHO','SR-503-THEN-OK','SR-SLOW-200','SR-BYE',
            'SR-CALL(https://cts-stub.example/x)',
            'SR-CALL(https://cts-trip.example/login)',
            'SR-CALL(https://cts-outside.example/x)', 'H-REL-035-SUBJECT']
JUDGES = ['J-PASS-90','J-PASS-60','J-FAIL-90','J-DOWN','J-DOWN-THEN-PASS-90',
          'J-FAIL-THEN-PASS-90','J-CATCH',
          'J-MAP(J-FAIL-90, J-PASS-60, J-PASS-90)']
PENDING_PLUGINS = ['cts-len','cts-flaky','cts-crash','cts-probe','cts-reach']
ALL = SUBJECTS+JUDGES+PENDING_PLUGINS


def check(code, harness_type=Harness):
    """Raise AssertionError on deviation. A new session is used per behavior."""
    h=harness_type()
    kind='subject' if code in SUBJECTS else 'judge'
    sid=h.begin('self-test-'+uuid.uuid4().hex)
    ep='self-test-endpoint'
    h.configure(sid,kind,code,endpoint_id=ep)
    def call(payload=None):
        return h.invoke(sid,kind,payload or {},endpoint_id=ep)
    def done(payload=None):
        r=call(payload)
        assert r['outcome']=='completed', f'expected completed: {r}'
        return r['result']
    if code=='SR-OK':assert done()=='Hello! How can I help?'
    elif code=='SR-EMPTY':assert done()==''
    elif code=='SR-ECHO':assert done({'prompt':'A\nB'})=='A\nB'
    elif code=='SR-BYE':assert done()=='Goodbye.'
    elif code=='SR-503-THEN-OK':
        a=call();assert (a['outcome'],a['status'])==('http_error',503)
        assert done()=='Hello! How can I help?'
        h.reset(sid);h.configure(sid,kind,code,endpoint_id=ep)
        assert call()['outcome']=='http_error', 'reset did not restore first-call behavior'
    elif code=='SR-SLOW-200':
        t=time.monotonic();assert done()=='Hello! How can I help?';assert time.monotonic()-t>=.2
    elif code.startswith('SR-CALL('):
        o=done();assert o=={'tool':'http_get','url':code[8:-1],'after_tool_response':'Done.','executed':False}
    elif code=='H-REL-035-SUBJECT':
        assert call({'scenario':'s-1','prompt':'First'})['outcome']=='http_error'
        assert done({'scenario':'s-1','prompt':'Second'})=='Second'
    elif code in ('J-PASS-90','J-PASS-60','J-FAIL-90'):
        expect={'verdict':'fail' if code=='J-FAIL-90' else 'pass','confidence':.6 if code=='J-PASS-60' else .9}
        assert done({'response':'Hello!'})==expect
    elif code=='J-DOWN':assert call()['outcome']=='unreachable' and call()['outcome']=='unreachable'
    elif code=='J-DOWN-THEN-PASS-90':
        assert call()['outcome']=='unreachable'
        assert done()=={'verdict':'pass','confidence':.9}
        h.reset(sid);h.configure(sid,kind,code,endpoint_id=ep)
        assert call()['outcome']=='unreachable'
    elif code=='J-FAIL-THEN-PASS-90':
        assert done()=={'verdict':'fail','confidence':.9}
        assert done()=={'verdict':'pass','confidence':.9}
        h.reset(sid);h.configure(sid,kind,code,endpoint_id=ep)
        assert done()=={'verdict':'fail','confidence':.9}
    elif code=='J-CATCH':
        for response in ('Goodbye.','Bye now.'):
            assert done({'response':response})=={'verdict':'fail','confidence':.9}
        assert done({'response':'Hello! How can I help?'})=={'verdict':'pass','confidence':.9}
    elif code.startswith('J-MAP('):
        expected=[('One','fail',.9),('Two','pass',.6),('Three','pass',.9)]
        for response,verdict,confidence in expected:
            assert done({'response':response})=={'verdict':verdict,'confidence':confidence}
    else:raise AssertionError('no self-test oracle for '+code)
    calls=[e for e in h.read_log(sid) if e['type']=='call_received']
    assert len(calls)>=1, 'missing call_received event'


def run(harness, sid, requested=None, harness_type=Harness):
    """Execute in fresh temporary sessions; record summary in owning session."""
    requested=ALL if requested is None else requested
    if len(requested)!=len(set(requested)):
        raise ValueError('duplicate self-test behavior')
    if any(code not in ALL for code in requested):
        raise ValueError('unknown self-test behavior')
    details=[]
    for code in requested:
        if code in PENDING_PLUGINS:
            result={'behavior':code,'status':'NOT_RUN','reason':'FIXTURE_UNAVAILABLE'}
        else:
            try:
                check(code,harness_type)
                result={'behavior':code,'status':'PASS'}
            except Exception as exc:
                result={'behavior':code,'status':'FAIL','reason':type(exc).__name__+': '+str(exc)}
        details.append(result)
        s=harness.session(sid)
        with s.lock:harness._emit(s,'self_test',**result)
    bad=[x['behavior'] for x in details if x['status']!='PASS']
    return {'results':details,'unusable_behaviors':bad,'status':'PASS' if not bad else 'INCOMPLETE'}
