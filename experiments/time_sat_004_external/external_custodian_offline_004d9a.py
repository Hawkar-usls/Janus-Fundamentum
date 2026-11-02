#!/usr/bin/env python3
"""TIME-SAT-004D9A: OFFLINE external SAT custodian precommit and receipt kit.

Requires only Python3 + cryptography. Runs on the independent custodian's
computer, never on JANUS infrastructure for real evidence. No network,
no SAT solver and no claims of third-party identity from a signature alone.

Precommit includes source/model SHA256, n/m/literals, signer public key and
Ed25519 signature. It deliberately does NOT include original CNF/model bytes.
After JANUS separately checks identity and freezes issuer public key and the
exact candidate SHA in its own NEW append-only policy, custodian may reveal
the unchanged CNF/model and receipt. Never release a private signing key.
"""
from __future__ import annotations
import argparse
import base64
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

MAX_SOURCE=134_217_728
MAX_MODEL=200_000
MAX_VARS=5000
MAX_CLAUSES=30000
MAX_LITERALS=120000
RECEIPT_SCHEMA="JANUS-TIME-SAT-004D9-INDEPENDENT-SAT-CUSTODIAN-RECEIPT-V1"
PRECOMMIT_SCHEMA="JANUS-TIME-SAT-004D9A-EXTERNAL-CUSTODIAN-PRECOMMIT-V1"
RECEIPT_KEYS=frozenset({
    "schema","candidate_id","external_issuer_id","source_sha256",
    "model_sha256","n_variables","n_clauses","n_literal_occurrences",
    "signature_base64"
})


def bounded_read(path,limit):
    if not path.is_file() or path.stat().st_size>limit:
        raise ValueError("Missing/oversized local evidence")
    return path.read_bytes()


def strict_dimacs(raw):
    """Independent small strict DIMACS check; no JANUS imports."""
    try:lines=raw.decode("ascii").splitlines()
    except UnicodeDecodeError as e:raise ValueError("Non-ASCII source") from e
    header=None
    clauses=[];current=[];literals=0
    for physical in lines:
        line=physical.strip()
        if not line or line.startswith("c"):continue
        if line.startswith("p"):
            parts=line.split()
            if header is not None or current or len(parts)!=4 or parts[:2]!=["p","cnf"]:
                raise ValueError("Malformed/repeated p cnf header")
            try:n,m=map(int,parts[2:])
            except ValueError as e:raise ValueError("Invalid source dimensions") from e
            if not 1<=n<=MAX_VARS or not 0<=m<=MAX_CLAUSES:
                raise ValueError("Source dimensions beyond limit")
            header=(n,m)
            continue
        if header is None:
            raise ValueError("DIMACS data before p cnf")
        n,m=header
        for token in line.split():
            try:lit=int(token)
            except ValueError as e:raise ValueError("Non-integer DIMACS literal") from e
            if lit==0:
                clauses.append(tuple(current));current=[]
                if len(clauses)>m:raise ValueError("Too many source clauses")
            else:
                if abs(lit)>n:raise ValueError("Literal variable out of bounds")
                current.append(lit);literals+=1
                if literals>MAX_LITERALS:raise ValueError("Source literal budget")
    if header is None or current or len(clauses)!=header[1]:
        raise ValueError("Missing header, incomplete clause or clause count mismatch")
    return header[0],header[1],literals,clauses


def verify_complete_model(rows,n,raw):
    try:d=json.loads(raw.decode("utf-8"))
    except (UnicodeError,ValueError) as e:raise ValueError("Malformed model JSON") from e
    if type(d) is not dict or set(d)!={"signed_model"} or type(d["signed_model"]) is not list:
        raise ValueError("Expected model JSON {signed_model:[...]}")
    signed=d["signed_model"]
    if (len(signed)!=n or any(type(v) is not int or v==0 or abs(v)>n for v in signed)
        or {abs(v) for v in signed}!=set(range(1,n+1))):
        raise ValueError("Model is not a complete unique signed assignment")
    assignment={abs(v):v>0 for v in signed}
    if not all(any(assignment[abs(v)]==(v>0) for v in clause) for clause in rows):
        raise ValueError("Claimed SAT model fails original source clause")
    return {"original_clauses_replayed":len(rows),"complete_model_verified":True}


def canonical_receipt(receipt):
    if set(receipt)!=RECEIPT_KEYS:
        raise ValueError("Receipt has extra/missing fields")
    return json.dumps({k:receipt[k] for k in sorted(receipt)
                      if k!="signature_base64"},sort_keys=True,
                      separators=(",",":"),ensure_ascii=True).encode("ascii")


def private_not_in_git_worktree(path):
    """Refuse to place unencrypted signing keys into a git checkout."""
    target=path.resolve()
    probe=target.parent
    found=subprocess.run(["git","-C",str(probe),"rev-parse","--show-toplevel"],
                         capture_output=True,text=True,check=False)
    if found.returncode==0 and found.stdout.strip():
        root=Path(found.stdout.strip()).resolve()
        if target.is_relative_to(root):
            raise ValueError("REFUSE_PRIVATE_KEY_INSIDE_GIT_WORKTREE")


def refuse_same_path(paths):
    names=[x.resolve() for x in paths]
    if len(set(names))!=len(names):
        raise ValueError("Evidence/key/output paths must be distinct")


def create_key(private_path,identity_path,issuer):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding,PrivateFormat,NoEncryption,PublicFormat
    if not issuer or issuer.strip()!=issuer:
        raise ValueError("Stable independently identified issuer ID is required")
    private_path.parent.mkdir(parents=True,exist_ok=True)
    private_not_in_git_worktree(private_path)
    refuse_same_path([private_path,identity_path])
    if private_path.exists() or identity_path.exists():
        raise ValueError("Do not overwrite existing keys or identity files")
    private_path.parent.mkdir(parents=True,exist_ok=True)
    key=Ed25519PrivateKey.generate()
    pem=key.private_bytes(Encoding.PEM,PrivateFormat.PKCS8,NoEncryption())
    fd=os.open(private_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        with os.fdopen(fd,"wb") as out:out.write(pem)
    except BaseException:
        private_path.unlink(missing_ok=True)
        raise
    pub=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    identity={"schema":"JANUS-EXTERNAL-CUSTODIAN-PUBLIC-IDENTITY-V1",
              "external_issuer_id":issuer,
              "ed25519_public_key_base64":base64.b64encode(pub).decode("ascii"),
              "private_key_never_upload":True,
              "cryptographic_key_proves_admin_independence":False}
    identity_path.parent.mkdir(parents=True,exist_ok=True)
    identity_path.write_text(json.dumps(identity,sort_keys=True,indent=2)+"\n")
    return identity


def build_precommit(private_path,issuer,candidate_id,cnf_path,model_path):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import load_pem_private_key,Encoding,PublicFormat
    if not issuer or not candidate_id or not issuer.strip() or not candidate_id.strip():
        raise ValueError("Stable custodian and candidate identifiers required")
    cnf=bounded_read(cnf_path,MAX_SOURCE)
    model=bounded_read(model_path,MAX_MODEL)
    n,m,lits,rows=strict_dimacs(cnf)
    check=verify_complete_model(rows,n,model)
    key=load_pem_private_key(bounded_read(private_path,8192),password=None)
    if not isinstance(key,Ed25519PrivateKey):
        raise ValueError("Ed25519 private key required")
    receipt={
        "schema":RECEIPT_SCHEMA,
        "candidate_id":candidate_id,
        "external_issuer_id":issuer,
        "source_sha256":sha256(cnf).hexdigest(),
        "model_sha256":sha256(model).hexdigest(),
        "n_variables":n,"n_clauses":m,"n_literal_occurrences":lits,
        "signature_base64":""
    }
    signed=key.sign(canonical_receipt(receipt))
    receipt["signature_base64"]=base64.b64encode(signed).decode("ascii")
    public_key=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    precommit={
        "schema":PRECOMMIT_SCHEMA,
        "purpose":"SOURCE_MODEL_HASH_COMMITMENT_BEFORE_CNFS_RELEASE_NOT_EVIDENCE_OF_ADMIN_INDEPENDENCE",
        "public_identity":{"external_issuer_id":issuer,
                           "ed25519_public_key_base64":base64.b64encode(public_key).decode("ascii")},
        "signed_receipt":receipt,
        "original_source_and_model_bytes_included":False,
        "original_model_local_full_clause_check":check,
        "separate_external_identity_verification_REQUIRED":True,
        "JANUS_004C_external_proof_witness":"NOT_CLAIMED",
        "JANUS_004D9_live_source_admission":"WAITING_FOR_NEW_PINNED_LOCKFILE_AND_RELEASE"
    }
    return precommit,receipt


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    cmd=p.add_subparsers(dest="cmd",required=True)
    create=cmd.add_parser("keygen")
    create.add_argument("--issuer",required=True)
    create.add_argument("--private-key",required=True,type=Path)
    create.add_argument("--public-identity",required=True,type=Path)
    sign=cmd.add_parser("precommit")
    sign.add_argument("--issuer",required=True)
    sign.add_argument("--candidate-id",required=True)
    sign.add_argument("--private-key",required=True,type=Path)
    sign.add_argument("--cnf",required=True,type=Path)
    sign.add_argument("--model",required=True,type=Path)
    sign.add_argument("--out-commitment",required=True,type=Path)
    sign.add_argument("--out-signed-receipt",required=True,type=Path)
    a=p.parse_args(argv)
    if a.cmd=="keygen":
        result=create_key(a.private_key,a.public_identity,a.issuer)
        print(json.dumps({"status":"OFFLINE_KEY_CREATED_DO_NOT_UPLOAD_PRIVATE",
                          "issuer":result["external_issuer_id"]}))
    else:
        refuse_same_path([a.private_key,a.cnf,a.model,a.out_commitment,a.out_signed_receipt])
        if a.out_commitment.exists() or a.out_signed_receipt.exists():
            raise ValueError("Do not overwrite signed public evidence")
        precommit,receipt=build_precommit(a.private_key,a.issuer,a.candidate_id,
                                          a.cnf,a.model)
        a.out_commitment.parent.mkdir(parents=True,exist_ok=True)
        a.out_signed_receipt.parent.mkdir(parents=True,exist_ok=True)
        a.out_commitment.write_text(json.dumps(precommit,sort_keys=True,indent=2)+"\n")
        a.out_signed_receipt.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
        print(json.dumps({"status":"HASH_AND_SIGNATURE_PRECOMMITTED_NO_SOURCE_REVEALED",
                          "candidate_id":a.candidate_id,
                          "signed_model_verified_on_exact_original_clauses":True}))


if __name__=="__main__":
    try:main()
    except (ValueError,OSError) as e:
        print("004D9A_REJECTED",str(e),file=sys.stderr)
        sys.exit(2)
