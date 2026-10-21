import unittest
from engine import run_case, service, http

class ExecutionCTS(unittest.TestCase):
    def test_exe003_correct(self):
        x=run_case('CT-EXE-003');self.assertEqual(x['outcome'],'PASS',x)
        self.assertEqual((x['subject_calls'],x['executions']),(2,1))
    def test_exe008_correct(self):
        x=run_case('CT-EXE-008');self.assertEqual(x['outcome'],'PASS',x)
        self.assertEqual((x['subject_calls'],x['executions']),(1,1))
    def test_exe003_bad_failed_attempt_record(self):
        self.assertEqual(run_case('CT-EXE-003','failed_attempt_record')['outcome'],'FAIL')
    def test_exe003_missing_execution(self):
        self.assertEqual(run_case('CT-EXE-003','missing_execution')['outcome'],'FAIL')
    def test_exe003_missing_conversation(self):
        self.assertEqual(run_case('CT-EXE-003','missing_conversation')['outcome'],'FAIL')
    def test_exe008_missing_conversation(self):
        self.assertEqual(run_case('CT-EXE-008','missing_conversation')['outcome'],'FAIL')
    def test_exe008_duplicate_conversation(self):
        self.assertEqual(run_case('CT-EXE-008','duplicate_conversation')['outcome'],'FAIL')
    def test_exe008_altered_prompt(self):
        self.assertEqual(run_case('CT-EXE-008','alter_prompt')['outcome'],'FAIL')
    def test_exe008_altered_response(self):
        self.assertEqual(run_case('CT-EXE-008','alter_response')['outcome'],'FAIL')
    def test_exe008_spurious_subject_call(self):
        self.assertEqual(run_case('CT-EXE-008','duplicate_subject_call')['outcome'],'FAIL')
    def test_corrupted_evidence_not_run(self):
        self.assertEqual(run_case('CT-EXE-008',damage_evidence=True)['outcome'],'NOT_RUN')
    def test_retry_evidence_corrupted_not_run(self):
        self.assertEqual(run_case('CT-EXE-003',damage_evidence=True)['outcome'],'NOT_RUN')
    def test_unknown_case_rejected(self):
        with self.assertRaises(ValueError):run_case('CT-EXE-999')
    def test_adapter_bad_envelope(self):
        with service() as (_,srv):
            status,body=http('POST',srv.url+'/api/v0.4/operations',{'operation':'execute'})
            self.assertEqual(status,400);self.assertEqual(body['error'],'SCHEMA_INVALID')
    def test_adapter_wrong_contract_version(self):
        with service() as (_,srv):
            status,body=http('POST',srv.url+'/api/v0.4/operations',{'contract_version':'0.3','operation':'execute'})
            self.assertEqual(status,400);self.assertEqual(body['error'],'SCHEMA_INVALID')

if __name__=='__main__':unittest.main()
