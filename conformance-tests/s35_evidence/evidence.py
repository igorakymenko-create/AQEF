"""S3.5.2 mock-only persistent raw/redacted Evidence Store and independent Resolver.

This is an example filesystem store, NOT a production trusted evidence service.
The signed/externally anchored manifest problem remains outside this slice: a
caller must preserve the receipt OUTSIDE the mutable store's trust boundary.
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import re
import tempfile
import uuid

_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$')
_SHA = re.compile(r'^[a-f0-9]{64}$')


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class EvidenceStore:
    """Writes immutable-named objects to disk. Receipts are NOT stored as authority."""
    def __init__(self, directory):
        self.directory = pathlib.Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory / 'objects').mkdir(exist_ok=True)

    def put(self, *, run_id, case_id, correlation_id, kind, body):
        if not all(isinstance(x,str) and _ID.fullmatch(x) for x in (run_id,case_id,correlation_id)):
            raise ValueError('invalid ownership identifier')
        if kind not in ('raw', 'redacted'):
            raise ValueError('invalid evidence kind')
        if not isinstance(body, bytes):
            raise TypeError('evidence must be bytes')
        # Self-contained opaque object name; no input-derived paths.
        object_id=uuid.uuid4().hex
        path=self.directory / 'objects' / object_id
        fd=os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            with os.fdopen(fd,'wb') as output:
                output.write(body)
                output.flush()
                os.fsync(output.fileno())
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return {'ref':'evidence://'+object_id,'run_id':run_id,'case_id':case_id,
                'correlation_id':correlation_id,'kind':kind,'size':len(body),
                'sha256':sha256(body)}


class EvidenceResolver:
    """Independent read-only verifier. Never accepts a stored hash as authority."""
    def __init__(self, directory):
        self.directory=pathlib.Path(directory)

    def resolve(self, expected, *, run_id, case_id, correlation_id, kind):
        if not isinstance(expected,dict):
            return self._fail('EVIDENCE_RECEIPT_MISSING')
        necessary={'ref','run_id','case_id','correlation_id','kind','size','sha256'}
        if set(expected)!=necessary:
            return self._fail('EVIDENCE_RECEIPT_INVALID')
        if any(expected.get(k)!=v for k,v in {'run_id':run_id,'case_id':case_id,
                    'correlation_id':correlation_id,'kind':kind}.items()):
            return self._fail('EVIDENCE_OWNER_MISMATCH')
        ref=expected['ref']
        if not isinstance(ref,str) or re.fullmatch(r'evidence://[a-f0-9]{32}',ref) is None:
            return self._fail('EVIDENCE_REF_INVALID')
        if not isinstance(expected['sha256'],str) or _SHA.fullmatch(expected['sha256']) is None:
            return self._fail('EVIDENCE_RECEIPT_INVALID')
        if type(expected['size']) is not int or expected['size']<0:
            return self._fail('EVIDENCE_RECEIPT_INVALID')
        path=self.directory/'objects'/ref[len('evidence://'):]
        try:
            if path.is_symlink() or not path.is_file():
                return self._fail('EVIDENCE_UNAVAILABLE')
            with path.open('rb') as handle:
                data=handle.read()
        except (OSError, ValueError):
            return self._fail('EVIDENCE_UNAVAILABLE')
        if len(data)!=expected['size'] or sha256(data)!=expected['sha256']:
            return self._fail('EVIDENCE_HASH_MISMATCH')
        return {'outcome':'PASS','reason':'EVIDENCE_VERIFIED','data':data}

    @staticmethod
    def _fail(reason):
        return {'outcome':'NOT_RUN','reason':reason}


def verify_bundle(resolver, receipts, *, run_id, case_id, correlation_id):
    """All-or-NOT_RUN: both raw and redacted required; no partial PASS leakage."""
    if not isinstance(receipts, dict) or set(receipts)!={'raw','redacted'}:
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_BUNDLE_INCOMPLETE'}
    if not isinstance(receipts['raw'],dict) or not isinstance(receipts['redacted'],dict):
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_RECEIPT_INVALID'}
    if receipts['raw'].get('ref')==receipts['redacted'].get('ref'):
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_ALIAS_INVALID'}
    resolved={}
    for kind in ('raw','redacted'):
        r=resolver.resolve(receipts[kind],run_id=run_id,case_id=case_id,
                           correlation_id=correlation_id,kind=kind)
        if r['outcome']!='PASS':
            return {'outcome':'NOT_RUN','reason':r['reason'],'failed_kind':kind}
        resolved[kind]=r['data']
    return {'outcome':'PASS','reason':'EVIDENCE_BUNDLE_VERIFIED','objects':resolved}


def assess_integrated_snapshot(snapshot, receipt, resolver, *, run_id, case_id, correlation_id):
    """Assess raw stored Execution snapshot after independent evidence read-back.

    The snapshots are deliberately simple mock output, not normative CTS reports.
    Every field used by this checker comes from verified raw evidence, not the
    caller's mutable in-memory SUT object. The redacted object is integrity-tested.
    """
    bundle=verify_bundle(resolver, receipt,run_id=run_id,case_id=case_id,correlation_id=correlation_id)
    if bundle['outcome']!='PASS':return bundle
    try:
        raw=json.loads(bundle['objects']['raw'])
        redacted=json.loads(bundle['objects']['redacted'])
        if not isinstance(raw,dict) or not isinstance(redacted,dict):
            return {'outcome':'NOT_RUN','reason':'EVIDENCE_PAYLOAD_INVALID'}
        if raw.get('terminal')!='completed' or not isinstance(raw.get('execution'),dict):
            return {'outcome':'NOT_RUN','reason':'EVIDENCE_PAYLOAD_INCOMPLETE'}
        if redacted.get('execution_id')!=raw['execution'].get('id'):
            return {'outcome':'NOT_RUN','reason':'REDACTED_IDENTITY_MISMATCH'}
        ex=raw['execution']
        if not isinstance(ex.get('results'),list) or not isinstance(ex.get('gate'),dict):
            return {'outcome':'NOT_RUN','reason':'EVIDENCE_PAYLOAD_INCOMPLETE'}
        if any(r.get('execution_id')!=ex['id'] for r in ex['results']) or ex['gate'].get('execution_id')!=ex['id']:
            return {'outcome':'FAIL','reason':'CROSS_EXECUTION_ATTRIBUTION'}
        if snapshot is not None and snapshot!=ex['id']:
            return {'outcome':'NOT_RUN','reason':'EVIDENCE_IDENTITY_MISMATCH'}
        return {'outcome':'PASS','reason':'INTEGRATED_EVIDENCE_CONFIRMED',
                'execution_id':ex['id'],'result_count':len(ex['results']),
                'gate_status':ex['gate'].get('status')}
    except (ValueError,TypeError,KeyError,AttributeError):
        return {'outcome':'NOT_RUN','reason':'EVIDENCE_PAYLOAD_INVALID'}


def produce_integrated_evidence(store, *, run_id, case_id, correlation_id, judge='J-PASS-60'):
    """Exercise the S3.5.1 GovernedPipeline and persist its *actual* records."""
    root=pathlib.Path(__file__).resolve().parent.parent
    import sys
    for p in (root/'s35_resolution',root/'s1_configuration'):
        if str(p) not in sys.path:sys.path.insert(0,str(p))
    from governance import GovernedPipeline
    from mock import fixture_base
    mock=GovernedPipeline()
    sid='s352-'+uuid.uuid4().hex
    mock.prepare_pipeline(sid,fixture_base(),'SR-OK',judge,'schema')
    completed=mock.execute(sid,case_id)
    if completed['terminal']!='completed' or len(completed['execution_ids'])!=1:
        raise RuntimeError('integration fixture unavailable')
    ex=mock.saved[sid]['executions'][0]
    raw=canonical({'terminal':'completed','execution':ex})
    redacted=canonical({'execution_id':ex['id'],'summary':{'results':len(ex['results']),
                                   'gate_status':ex['gate']['status']},'redacted':True})
    receipts={kind:store.put(run_id=run_id,case_id=case_id,correlation_id=correlation_id,
                             kind=kind,body=data) for kind,data in [('raw',raw),('redacted',redacted)]}
    return {'receipts':receipts,'execution_id':ex['id'],'gate_status':ex['gate']['status']}
