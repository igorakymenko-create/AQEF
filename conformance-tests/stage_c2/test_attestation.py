import base64,copy,hashlib,pathlib,tempfile,unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from attestation import canonical,sign_payload,verify
SHA="a"*40
class AttestationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name);(self.root/"report.json").write_text("real mock report")
  self.manifest={"cts_commit":SHA,"files":{"report.json":hashlib.sha256((self.root/"report.json").read_bytes()).hexdigest()}}
  self.private=Ed25519PrivateKey.generate()
  public=self.private.public_key().public_bytes(encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
  self.trust={"ci-key-1":{"status":"trusted","identity":"ci:aqef:stage-c2",
   "public_key":base64.b64encode(public).decode(),"not_before":"2026-01-01T00:00:00Z","not_after":"2027-01-01T00:00:00Z"}}
  payload={"version":"C2-ATTEST-1","commit":SHA,"run_id":"run-42","scope":"MOCK_ONLY",
   "key_id":"ci-key-1","signer":"ci:aqef:stage-c2",
   "manifest_sha256":hashlib.sha256(canonical(self.manifest)).hexdigest(),
   "issued_at":"2026-10-22T00:00:00Z","expires_at":"2026-10-24T00:00:00Z"}
  self.envelope=sign_payload(payload,self.private)
 def verify(self):
  return verify(self.envelope,self.manifest,self.root,self.trust,expected_commit=SHA,expected_run="run-42",now="2026-10-23T00:00:00Z")
 def test_valid_signature(self):self.assertEqual(self.verify(),[])
 def test_tampered_evidence(self):
  (self.root/"report.json").write_text("fake");self.assertTrue(self.verify())
 def test_tampered_manifest(self):
  self.manifest["extra"]="changed";self.assertTrue(self.verify())
 def test_wrong_run(self):
  self.envelope["run_id"]="run-43";self.assertTrue(self.verify())
 def test_wrong_commit(self):
  self.envelope["commit"]="b"*40;self.assertTrue(self.verify())
 def test_expired(self):
  self.envelope["expires_at"]="2026-10-22T01:00:00Z";self.assertTrue(self.verify())
 def test_revoked_key(self):
  self.trust["ci-key-1"]["status"]="revoked";self.assertTrue(self.verify())
 def test_unknown_key(self):
  self.envelope["key_id"]="other";self.assertTrue(self.verify())
 def test_wrong_signer(self):
  self.envelope["signer"]="evil";self.assertTrue(self.verify())
 def test_wrong_signature(self):
  other=Ed25519PrivateKey.generate()
  self.envelope["signature"]=sign_payload({k:v for k,v in self.envelope.items() if k!="signature"},other)["signature"]
  self.assertTrue(self.verify())
 def test_outside_authorized_rotation_window(self):
  self.trust["ci-key-1"]["not_after"]="2026-10-21T00:00:00Z";self.assertTrue(self.verify())
 def test_real_sut_claim_rejected(self):
  self.envelope["scope"]="REAL_SUT";self.assertTrue(self.verify())
 def test_path_traversal_rejected(self):
  self.manifest["files"]={"../report.json":"0"*64};self.assertTrue(self.verify())
if __name__=="__main__":unittest.main()
