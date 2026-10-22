import base64,datetime as dt,hashlib,json,pathlib,tempfile,unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from operational_signing import sign
from attestation import verify
SHA="a"*40
class OperationalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=pathlib.Path(self.tmp.name)
  (self.root/"payload.txt").write_text("mock-only")
  self.manifest={"cts_commit":SHA,"files":{"payload.txt":hashlib.sha256(b"mock-only").hexdigest()}}
  (self.root/"closure_manifest.json").write_text(json.dumps(self.manifest))
  self.key=Ed25519PrivateKey.generate()
  pem=self.key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption())
  self.pem=pem
  public=self.key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
  self.trust={"key-1":{"status":"trusted","identity":"ci:aqef","public_key":base64.b64encode(public).decode(),
              "not_before":"2026-01-01T00:00:00Z","not_after":"2027-01-01T00:00:00Z"}}
 def envelope(self):
  return sign(self.root,SHA,"123",self.pem,"key-1","ci:aqef","2026-10-22T00:00:00Z","2026-10-23T00:00:00Z")
 def check(self,e):
  return verify(e,self.manifest,self.root,self.trust,expected_commit=SHA,expected_run="123",now="2026-10-22T12:00:00Z")
 def test_end_to_end_signature(self):self.assertEqual(self.check(self.envelope()),[])
 def test_wrong_run_rejected(self):self.assertTrue(verify(self.envelope(),self.manifest,self.root,self.trust,expected_commit=SHA,expected_run="other",now="2026-10-22T12:00:00Z"))
 def test_modified_evidence_rejected(self):
  envelope=self.envelope();(self.root/"payload.txt").write_text("modified")
  self.assertTrue(self.check(envelope))
 def test_other_anchor_rejected(self):
  envelope=self.envelope();self.trust={}
  self.assertTrue(self.check(envelope))
 def test_bad_commit_rejected(self):
  with self.assertRaises(ValueError):sign(self.root,"b"*40,"123",self.pem,"key-1","ci:aqef","2026-10-22T00:00:00Z","2026-10-23T00:00:00Z")
 def test_not_ed25519_rejected(self):
  with self.assertRaises((ValueError,TypeError)):
   sign(self.root,SHA,"123",b"invalid pem","key-1","ci:aqef","2026-10-22T00:00:00Z","2026-10-23T00:00:00Z")
if __name__=="__main__":unittest.main()
