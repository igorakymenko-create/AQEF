"""S3.5.3 mock-only measured Observation Timing for Stage C Q-05.

Time is measured via the real S0 Harness monotonic events. No fake clock,
no sleep-skipping mock, no claim about remote SUT timing or clock bounds.
"""
from __future__ import annotations
import pathlib, sys, time, threading, statistics, uuid
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'harness'/'s02_harness'))
from harness import Harness

class TimingError(ValueError): pass


def measured_profile(*, samples=3, latency_ms=20, margin_ms=20, clock=time.monotonic_ns):
    """Measure monotonic wakeup jitter, derive a positive conservative drain.

    latency_ms is a calibration probe, not the configured observation budget.
    Caller supplies a documented minimum margin, and actual measurements grow it.
    Results are a provisional environment-specific baseline, not an SUT SLA.
    """
    if type(samples) is not int or not 2 <= samples <= 12: raise TimingError('invalid samples')
    if type(latency_ms) is not int or not 1 <= latency_ms <= 100: raise TimingError('invalid latency_ms')
    if type(margin_ms) is not int or not 1 <= margin_ms <= 1000: raise TimingError('invalid margin_ms')
    durations=[]
    for _ in range(samples):
        t=clock();time.sleep(latency_ms/1000);elapsed=(clock()-t)/1e6
        if elapsed<=0:raise TimingError('nonmonotonic clock')
        durations.append(elapsed)
    overshoot=max(0,max(durations)-latency_ms)
    drain_ms=max(1,int(latency_ms+margin_ms+overshoot+0.9999))
    return {'clock_id':'s02-monotonic-process','sample_count':samples,
            'probe_target_ms':latency_ms,'probe_observed_ms':durations,
            'overshoot_ms':overshoot,'margin_ms':margin_ms,'drain_ms':drain_ms,
            'source':'MEASURED_LOCAL_MOCK_ONLY'}


def timed_observation(*,drain_ms,terminal_observed=True,scheduled_ms=None,
                      expected_calls=0,post_close_call=False,kind='judge',
                      max_budget_ms=2000,calibration=None):
    """One real Harness session; inspect independently recorded monotonic events.

    scheduled_ms starts a call during drain when < drain_ms; after when > drain_ms.
    No normative PASS is possible without a calibrated profile, a terminal state,
    and sufficient budget to cover the *measured* drain.
    """
    if type(drain_ms) is not int or drain_ms<=0:raise TimingError('drain must be positive')
    if type(max_budget_ms) is not int or max_budget_ms<1:raise TimingError('invalid budget')
    if scheduled_ms is not None and (type(scheduled_ms) is not int or scheduled_ms<0):raise TimingError('invalid scheduled delay')
    if type(expected_calls) is not int or expected_calls<0:raise TimingError('invalid expected calls')
    if calibration is None or calibration.get('source')!='MEASURED_LOCAL_MOCK_ONLY':
        return {'outcome':'NOT_RUN','reason':'CALIBRATION_MISSING'}
    if calibration.get('clock_id')!='s02-monotonic-process' or drain_ms<calibration.get('drain_ms',1):
        return {'outcome':'NOT_RUN','reason':'DRAIN_BELOW_MEASURED_BASELINE'}
    if drain_ms>max_budget_ms:
        return {'outcome':'NOT_RUN','reason':'OBSERVATION_BUDGET_INSUFFICIENT'}
    if not terminal_observed:
        return {'outcome':'NOT_RUN','reason':'TERMINAL_UNOBSERVED'}
    h=Harness();sid=h.begin('s353-'+uuid.uuid4().hex)
    h.configure(sid,kind,'J-PASS-90' if kind=='judge' else 'SR-OK')
    released=threading.Event()
    threads=[]
    def delayed_call(delay):
        released.wait()
        time.sleep(delay/1000)
        try:h.invoke(sid,kind,{'response':'Hello'},correlation_id='delayed')
        except RuntimeError:pass
    if scheduled_ms is not None:
        th=threading.Thread(target=delayed_call,args=(scheduled_ms,),daemon=False)
        th.start();threads.append(th)
    released.set()
    start=time.monotonic_ns()
    h.close_observation(sid,drain_ms=drain_ms,terminal_observed=True)
    elapsed_ms=(time.monotonic_ns()-start)/1e6
    if post_close_call:
        try:h.invoke(sid,kind,{'response':'Hello'},correlation_id='after-closure')
        except RuntimeError:pass
    for th in threads:th.join(timeout=2)
    if any(th.is_alive() for th in threads):
        return {'outcome':'NOT_RUN','reason':'CALL_THREAD_INCOMPLETE'}
    events=h.read_log(sid)
    try:
        watermark=next(e for e in events if e['type']=='observation_watermark')
        closed=next(e for e in events if e['type']=='observation_closed')
        # The last event before closure must carry a matching watermark sequence.
        stable=(watermark['clock_id']==closed['clock_id']==calibration['clock_id'] and
                closed['sequence']==watermark['sequence']+1 and
                closed['attributes']['watermark']==watermark['sequence'] and
                watermark['attributes']['highest_sequence']==watermark['sequence']-1 and
                elapsed_ms>=drain_ms and
                closed['observed_monotonic_ns']>=watermark['observed_monotonic_ns'])
    except (StopIteration,KeyError,TypeError):
        return {'outcome':'NOT_RUN','reason':'WATERMARK_UNAVAILABLE'}
    if not stable:return {'outcome':'NOT_RUN','reason':'OBSERVATION_TIMING_UNTRUSTWORTHY'}
    verdict=h.negative_assertion(sid,kind,expected_calls)
    return {'outcome':verdict['outcome'],'reason':('EXPECTED_MET' if verdict['outcome']=='PASS' else 'NEGATIVE_ASSERTION_VIOLATED'),
            'elapsed_ms':elapsed_ms,'configured_drain_ms':drain_ms,
            'watermark':watermark['attributes']['highest_sequence'],
            'observed_calls':verdict['observed'],'late':verdict['late'],
            'clock_id':calibration['clock_id'],'session_id':sid,
            'trace':events}


def measured_matrix():
    profile=measured_profile()
    d=profile['drain_ms']
    return {'scope':'S3.5.3_MEASURED_MOCK_ONLY','profile':profile,
            'correct':timed_observation(drain_ms=d,calibration=profile),
            'during_drain':timed_observation(drain_ms=d,calibration=profile,scheduled_ms=max(0,d//3)),
            'after_closure':timed_observation(drain_ms=d,calibration=profile,post_close_call=True),
            'insufficient_budget':timed_observation(drain_ms=d,calibration=profile,max_budget_ms=d-1),
            'missing_terminal':timed_observation(drain_ms=d,calibration=profile,terminal_observed=False)}
