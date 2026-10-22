"""C.2.4 externally verifiable Ed25519 attestation of closure artifacts.

Trust anchors are caller-supplied, NEVER read from the signed envelope. Signing
uses a separately provisioned private key; no production keys are generated here.
"""
import base64
import datetime as dt
import hashlib
import json
import pathlib
import re
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA64=re.compile(r"^[0-9a-f]{64}$")

def canonical(data):
    return json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")

def timestamp(value):
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC Z")
    date=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
    if date.utcoffset()!=dt.timedelta(0):
        raise ValueError("timestamp must be UTC")
    return date

def load_manifest(root,manifest):
    root=pathlib.Path(root).resolve()
    if not isinstance(manifest,dict) or not isinstance(manifest.get("files"),dict) or not manifest["files"]:
        raise ValueError("invalid closure manifest")
    for name,want in manifest["files"].items():
        if not isinstance(name,str) or not name or name.startswith("/") or name.startswith(".") or "\\" in name:
            raise ValueError("unsafe evidence path")
        target=(root/name).resolve()
        if root not in target.parents or not target.is_file() or not isinstance(want,str) or not SHA64.fullmatch(want):
            raise ValueError("missing evidence or invalid digest")
        if hashlib.sha256(target.read_bytes()).hexdigest()!=want:
            raise ValueError("evidence digest mismatch")
    return hashlib.sha256(canonical(manifest)).hexdigest()

def verify(envelope,manifest,evidence_root,trust_store,*,expected_commit,expected_run,now):
    errors=[]
    try:
        if envelope.get("version")!="C2-ATTEST-1":raise ValueError("wrong envelope version")
        if not SHA40.fullmatch(str(expected_commit)):raise ValueError("invalid expected commit")
        if envelope.get("commit")!=expected_commit or manifest.get("cts_commit")!=expected_commit:
            raise ValueError("commit mismatch")
        if not isinstance(expected_run,str) or not expected_run or envelope.get("run_id")!=expected_run:
            raise ValueError("run mismatch")
        if envelope.get("scope")!="MOCK_ONLY":raise ValueError("unsupported attestation scope")
        digest=load_manifest(evidence_root,manifest)
        if envelope.get("manifest_sha256")!=digest:raise ValueError("manifest digest mismatch")
        start=timestamp(envelope.get("issued_at"));end=timestamp(envelope.get("expires_at"));current=timestamp(now)
        if not start<end or not start<=current<end:raise ValueError("outside attestation validity")
        keyid=envelope.get("key_id")
        anchor=trust_store.get(keyid) if isinstance(trust_store,dict) else None
        if not isinstance(anchor,dict) or anchor.get("status")!="trusted":raise ValueError("untrusted/revoked key")
        if not timestamp(anchor["not_before"])<=start<timestamp(anchor["not_after"]):
            raise ValueError("signer outside authorized period")
        if envelope.get("signer")!=anchor.get("identity"):raise ValueError("signer identity mismatch")
        payload={k:v for k,v in envelope.items() if k!="signature"}
        sig=base64.b64decode(envelope["signature"],validate=True)
        pub=Ed25519PublicKey.from_public_bytes(base64.b64decode(anchor["public_key"],validate=True))
        pub.verify(sig,canonical(payload))
    except (ValueError,TypeError,KeyError,InvalidSignature,OverflowError) as exc:
        errors.append("attestation rejected: "+str(exc))
    return errors

def sign_payload(payload, private_key):
    """Construct unsigned fields outside this function; signing key must stay external."""
    return dict(payload,signature=base64.b64encode(private_key.sign(canonical(payload))).decode("ascii"))

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--envelope",required=True);p.add_argument("--manifest",required=True)
    p.add_argument("--evidence-root",required=True);p.add_argument("--trust-store",required=True)
    p.add_argument("--sha",required=True);p.add_argument("--run",required=True);p.add_argument("--now",required=True)
    a=p.parse_args()
    read=lambda x:json.loads(pathlib.Path(x).read_text())
    errs=verify(read(a.envelope),read(a.manifest),a.evidence_root,read(a.trust_store),
                expected_commit=a.sha,expected_run=a.run,now=a.now)
    if errs:raise SystemExit("; ".join(errs))
    print("C2 ATTESTATION VERIFIED (mock scope; no real SUT conformance)")
if __name__=="__main__":main()
