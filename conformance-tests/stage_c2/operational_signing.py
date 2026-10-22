"""C.2.4.5 operational signing and independent verification command.

Production mode requires a provisioned private key and independent trust-store
file; no ephemeral or self-declared trust roots are accepted in production.
"""
import argparse,base64,datetime as dt,hashlib,json,os,pathlib,sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from attestation import canonical,load_manifest,sign_payload,verify

def dump(path,obj):
    pathlib.Path(path).write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")

def sign(root,commit,run,key_pem,key_id,identity,issued,expires):
    root=pathlib.Path(root)
    manifest=json.loads((root/"closure_manifest.json").read_text())
    if manifest.get("cts_commit")!=commit:raise ValueError("manifest/commit mismatch")
    digest=load_manifest(root,manifest)
    key=serialization.load_pem_private_key(key_pem,password=None)
    if not isinstance(key,Ed25519PrivateKey):raise ValueError("Ed25519 required")
    payload={"version":"C2-ATTEST-1","commit":commit,"run_id":run,"scope":"MOCK_ONLY",
             "key_id":key_id,"signer":identity,"manifest_sha256":digest,
             "issued_at":issued,"expires_at":expires}
    return sign_payload(payload,key)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["sign","verify"])
    p.add_argument("--root",required=True);p.add_argument("--sha",required=True)
    p.add_argument("--run",required=True);p.add_argument("--now",required=True)
    p.add_argument("--trust-store");p.add_argument("--key-id");p.add_argument("--identity")
    p.add_argument("--expires")
    a=p.parse_args()
    root=pathlib.Path(a.root)
    if a.mode=="sign":
        if not os.environ.get("AQEF_SIGNING_KEY_PEM"):raise SystemExit("external signing key required")
        if not a.key_id or not a.identity or not a.expires:raise SystemExit("key metadata required")
        envelope=sign(root,a.sha,a.run,os.environ["AQEF_SIGNING_KEY_PEM"].encode(),a.key_id,a.identity,a.now,a.expires)
        dump(root/"attestation.json",envelope)
        print("SIGNED: external key used; independent verification still required")
    else:
        if not a.trust_store:raise SystemExit("external trust-store required")
        envelope=json.loads((root/"attestation.json").read_text())
        manifest=json.loads((root/"closure_manifest.json").read_text())
        anchors=json.loads(pathlib.Path(a.trust_store).read_text())
        errors=verify(envelope,manifest,root,anchors,expected_commit=a.sha,expected_run=a.run,now=a.now)
        if errors:raise SystemExit("; ".join(errors))
        print("VERIFIED: independent trust-store")
if __name__=="__main__":main()
