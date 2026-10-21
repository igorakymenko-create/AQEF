"""S1 Negative & Outcome Verification policy, mock-only; no AQEF SUT certification.

A fail-closed assessor operating on HTTP-adapter observations. This is deliberately
separate from the mock's behavior, so a broken mock cannot award itself PASS.
"""
from __future__ import annotations
import hashlib, json

ORDER=('FAIL','NOT_RUN','PASS','NOT_APPLICABLE')
ACCEPTED=(200,201,202)


def aggregate(outcomes):
    """CTS 1.2 outcome precedence. Never promote an unavailable case to PASS."""
    if not outcomes: raise ValueError('cannot aggregate zero cases')
    if any(x not in ORDER for x in outcomes): raise ValueError('unknown CTS outcome')
    return next(x for x in ORDER if x in outcomes)


def assess(req, rsp, evidence, *, expected_acceptance, missing_field=None, stored=None, source=None):
    """Assess a completed load_config HTTP observation.

    `evidence` is the Adapter's registered evidence map:
      evidence[ref] = (run_id, case_id, raw_response_bytes).
    It must never be replaced with unverified JSON from the SUT itself.
    PASS/FAIL concern SUT behavior; NOT_RUN concerns inability to trust observation.
    """
    if expected_acceptance and (source is None or not isinstance(source,dict)):
        return {'outcome':'NOT_RUN','reason':'SOURCE_FIXTURE_UNAVAILABLE'}
    if not isinstance(req,dict) or not isinstance(rsp,dict):
        return {'outcome':'NOT_RUN','reason':'ADAPTER_RESPONSE_UNAVAILABLE'}
    if (rsp.get('contract_version')!='0.4' or rsp.get('operation')!='load_config'
            or rsp.get('correlation_id')!=req.get('correlation_id')
            or rsp.get('success') is not True):
        return {'outcome':'NOT_RUN','reason':'ADAPTER_CONTRACT_INVALID'}
    data=rsp.get('data')
    sut=data.get('sut') if isinstance(data,dict) else None
    if not isinstance(sut,dict):return {'outcome':'NOT_RUN','reason':'ADAPTER_CONTRACT_INVALID'}
    status=sut.get('status');outcome=sut.get('outcome')
    ref=sut.get('body_ref');digest=sut.get('body_sha256')
    if not isinstance(status,int) or isinstance(status,bool) or not 100<=status<=599:
        return {'outcome':'NOT_RUN','reason':'ADAPTER_CONTRACT_INVALID'}
    if outcome not in ('accepted','rejected') or sut.get('surface') not in ('equivalent','appendix_c_rest'):
        return {'outcome':'NOT_RUN','reason':'ADAPTER_CONTRACT_INVALID'}
    if (outcome=='accepted') != (status in ACCEPTED):
        return {'outcome':'NOT_RUN','reason':'ADAPTER_STATUS_CONTRADICTION'}
    if not isinstance(ref,str) or not isinstance(digest,str) or rsp.get('evidence_refs')!=[ref]:
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_REFERENCE_INVALID'}
    record=evidence.get(ref) if hasattr(evidence,'get') else None
    if not isinstance(record,tuple) or len(record)!=3:
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_MISSING'}
    run,case,raw=record
    if (run,case)!=(req.get('run_id'),req.get('case_id')):
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_WRONG_OWNER'}
    if not isinstance(raw,bytes) or hashlib.sha256(raw).hexdigest()!=digest:
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_INTEGRITY_FAILED'}
    try:body=json.loads(raw)
    except (UnicodeDecodeError,ValueError):
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_INVALID_JSON'}
    accepted=outcome=='accepted'
    if expected_acceptance:
        if not accepted:return {'outcome':'FAIL','reason':'VALID_CONFIG_REJECTED'}
        if not isinstance(stored,dict) or stored.get('config')!=source:
            return {'outcome':'FAIL','reason':'CONFIG_NOT_PRESERVED'}
        return {'outcome':'PASS','reason':'VALID_CONFIG_PRESERVED'}
    if accepted:return {'outcome':'FAIL','reason':'INVALID_CONFIG_ACCEPTED'}
    if not isinstance(body,dict):return {'outcome':'FAIL','reason':'REJECTION_DIAGNOSTIC_MISSING'}
    diagnostic=' '.join(str(v) for v in body.values())
    if not missing_field or missing_field not in diagnostic:
        return {'outcome':'FAIL','reason':'REJECTION_DIAGNOSTIC_MISSING'}
    return {'outcome':'PASS','reason':'INVALID_CONFIG_REJECTED_WITH_DIAGNOSTIC'}
