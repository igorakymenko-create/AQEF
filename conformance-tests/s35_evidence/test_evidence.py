import copy
import json
import pathlib
import tempfile
import unittest
from evidence import (EvidenceStore, EvidenceResolver, verify_bundle,
                      assess_integrated_snapshot, produce_integrated_evidence, canonical)

RUN='run-352';CASE='CT-DEC-006';CORR='corr-352'

class PersistentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store=EvidenceStore(self.tmp.name)
        self.resolver=EvidenceResolver(self.tmp.name)
        self.receipts={k:self.store.put(run_id=RUN,case_id=CASE,correlation_id=CORR,
                                       kind=k,body=canonical({'kind':k,'hello':'world'}))
                       for k in ('raw','redacted')}

    def path(self,kind):
        return pathlib.Path(self.tmp.name)/'objects'/self.receipts[kind]['ref'].split('://')[1]

    def check(self, receipts=None, resolver=None):
        return verify_bundle(resolver or self.resolver, receipts if receipts is not None else self.receipts,
                             run_id=RUN,case_id=CASE,correlation_id=CORR)

    def test_persistent_store_reopened(self):
        self.assertEqual(self.check(resolver=EvidenceResolver(self.tmp.name))['outcome'],'PASS')

    def test_two_kinds_required(self):
        r={'raw':self.receipts['raw']}
        self.assertEqual(self.check(r)['reason'],'EVIDENCE_BUNDLE_INCOMPLETE')

    def test_raw_mutation_not_run(self):
        self.path('raw').write_bytes(b'{"changed":true}')
        self.assertEqual(self.check()['outcome'],'NOT_RUN')

    def test_redacted_mutation_not_run(self):
        self.path('redacted').write_bytes(b'{"changed":true}')
        r=self.check();self.assertEqual(r['outcome'],'NOT_RUN');self.assertEqual(r['failed_kind'],'redacted')

    def test_truncation_both(self):
        for kind in ('raw','redacted'):
            with self.subTest(kind=kind):
                p=self.path(kind);original=p.read_bytes();p.write_bytes(original[:-1])
                self.assertEqual(self.check()['outcome'],'NOT_RUN');p.write_bytes(original)

    def test_delete_both(self):
        for kind in ('raw','redacted'):
            with self.subTest(kind=kind):
                p=self.path(kind);original=p.read_bytes();p.unlink()
                self.assertEqual(self.check()['outcome'],'NOT_RUN');p.write_bytes(original)

    def test_swap_raw_and_redacted(self):
        a,b=self.path('raw'),self.path('redacted')
        olda,oldb=a.read_bytes(),b.read_bytes()
        a.write_bytes(oldb);b.write_bytes(olda)
        self.assertEqual(self.check()['outcome'],'NOT_RUN')

    def test_wrong_run_case_correlation(self):
        for field,val in [('run_id','other-run'),('case_id','CT-DEC-012'),('correlation_id','other-corr')]:
            with self.subTest(field=field):
                receipts=copy.deepcopy(self.receipts);receipts['raw'][field]=val
                self.assertEqual(self.check(receipts)['reason'],'EVIDENCE_OWNER_MISMATCH')

    def test_wrong_read_scope(self):
        self.assertEqual(verify_bundle(self.resolver,self.receipts,run_id='other',case_id=CASE,correlation_id=CORR)['outcome'],'NOT_RUN')

    def test_invalid_and_traversal_refs(self):
        for bad in ['evidence://../../escape','file:///etc/passwd','evidence://','evidence://'+'x'*32]:
            with self.subTest(ref=bad):
                receipts=copy.deepcopy(self.receipts);receipts['raw']['ref']=bad
                self.assertEqual(self.check(receipts)['outcome'],'NOT_RUN')

    def test_symlink_refused(self):
        p=self.path('raw');p.unlink();p.symlink_to(self.path('redacted'))
        self.assertEqual(self.check()['outcome'],'NOT_RUN')

    def test_alias_refused(self):
        receipts=copy.deepcopy(self.receipts);receipts['redacted']['ref']=receipts['raw']['ref']
        self.assertEqual(self.check(receipts)['reason'],'EVIDENCE_ALIAS_INVALID')

    def test_forged_digest_rejected(self):
        receipts=copy.deepcopy(self.receipts);receipts['raw']['sha256']='0'*64
        self.assertEqual(self.check(receipts)['outcome'],'NOT_RUN')

    def test_bad_receipt_not_run(self):
        receipts=copy.deepcopy(self.receipts);receipts['raw']['size']=False
        self.assertEqual(self.check(receipts)['outcome'],'NOT_RUN')

    def test_extra_manifest_field_rejected(self):
        receipts=copy.deepcopy(self.receipts);receipts['raw']['extra']='sneaky'
        self.assertEqual(self.check(receipts)['outcome'],'NOT_RUN')

    def test_store_rejects_invalid_identifiers(self):
        with self.assertRaises(ValueError):
            self.store.put(run_id='../attack',case_id=CASE,correlation_id=CORR,kind='raw',body=b'hi')

    def test_store_rejects_unknown_kind(self):
        with self.assertRaises(ValueError):
            self.store.put(run_id=RUN,case_id=CASE,correlation_id=CORR,kind='other',body=b'hi')

    def test_store_uses_distinct_objects(self):
        self.assertNotEqual(self.receipts['raw']['ref'],self.receipts['redacted']['ref'])


class IntegratedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=EvidenceStore(self.tmp.name)
        self.fixture=produce_integrated_evidence(self.store,run_id=RUN,case_id=CASE,correlation_id=CORR)
        self.resolver=EvidenceResolver(self.tmp.name)

    def assess(self,receipts=None,identity=None):
        return assess_integrated_snapshot(identity if identity is not None else self.fixture['execution_id'],
               receipts if receipts is not None else self.fixture['receipts'],self.resolver,
               run_id=RUN,case_id=CASE,correlation_id=CORR)

    def test_real_governed_pipeline_persisted_and_reopened(self):
        result=self.assess();self.assertEqual(result['outcome'],'PASS',result)
        self.assertEqual(result['gate_status'],'fail')
        self.assertEqual(result['result_count'],2)

    def test_integrated_raw_corruption_not_run(self):
        p=pathlib.Path(self.tmp.name)/'objects'/self.fixture['receipts']['raw']['ref'].split('://')[1]
        p.write_bytes(p.read_bytes()+b'!')
        self.assertEqual(self.assess()['outcome'],'NOT_RUN')

    def test_integrated_redacted_deletion_not_run(self):
        p=pathlib.Path(self.tmp.name)/'objects'/self.fixture['receipts']['redacted']['ref'].split('://')[1]
        p.unlink()
        self.assertEqual(self.assess()['outcome'],'NOT_RUN')

    def test_integrated_expected_execution_identity(self):
        self.assertEqual(self.assess(identity='other-execution')['outcome'],'NOT_RUN')

    def test_two_isolated_runs(self):
        other=produce_integrated_evidence(self.store,run_id='run-second',case_id=CASE,correlation_id='second')
        self.assertNotEqual(other['receipts']['raw']['ref'],self.fixture['receipts']['raw']['ref'])
        self.assertEqual(verify_bundle(self.resolver,other['receipts'],run_id=RUN,case_id=CASE,correlation_id=CORR)['outcome'],'NOT_RUN')

    def test_authenticated_payload_mismatch_is_fail(self):
        # Internally consistent, externally anchored hash; violation in observed SUT payload => FAIL.
        original=self.fixture
        raw={'terminal':'completed','execution':{'id':'execution-a','results':[{'execution_id':'execution-other'}],
                                            'gate':{'execution_id':'execution-a','status':'pass'}}}
        redacted={'execution_id':'execution-a','redacted':True}
        receipts={kind:self.store.put(run_id=RUN,case_id=CASE,correlation_id=CORR,kind=kind,body=canonical(obj))
                  for kind,obj in [('raw',raw),('redacted',redacted)]}
        verdict=assess_integrated_snapshot('execution-a',receipts,self.resolver,run_id=RUN,case_id=CASE,correlation_id=CORR)
        self.assertEqual(verdict['outcome'],'FAIL')

if __name__=='__main__':unittest.main()
