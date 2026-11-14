#!/usr/bin/env python3
"""Research-only 004D9B bridge for a *separately approved* external trust lock.

The old 004D9 verifier and frozen empty policy are NOT changed. Activation
requires a future reviewed CODE CHANGE to both literal constants below.
An untrusted receipt, CLI argument, or JSON file must NEVER select its own
trust root. Tests may call _check_lock_structure directly with synthetic data.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DIRECT = HERE.parent / "direct"
sys.path.insert(0, str(DIRECT))
from janus_time_sat_004d9_external_intake import (
    check_external_evidence, load_json_bounded, MAX_RECEIPT
)

# FROZEN BY DESIGN: no outside institution has authorized a key or cohort.
# Human approval must review a NEW immutable lockfile and commit the actual
# Git blob SHA here; never use a command-line --policy or --policy-sha input.
PINNED_TRUST_POLICY_RELATIVE_PATH = None
PINNED_TRUST_POLICY_BLOB_SHA = None
PINNED_REVIEW_ATTESTATION_SHA256 = None

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SCHEMA = "JANUS-TIME-SAT-004D9B-INDEPENDENT-CUSTODIAN-TRUST-LOCK-V1"

def _is_sha(value):
    return isinstance(value, str) and bool(HEX64.fullmatch(value))

def _check_lock_structure(policy):
    if not isinstance(policy, dict) or policy.get("schema") != SCHEMA:
        raise ValueError("Unknown/new external trust lock schema")
    review = policy.get("external_review")
    if not isinstance(review, dict) or review.get("status") != "APPROVED_OUT_OF_BAND":
        raise ValueError("External administrative identity review not approved")
    if not all(isinstance(review.get(k),str) and review[k] for k in (
            "reviewer_identity", "institution", "signed_review_reference")):
        raise ValueError("Missing independent authority chain")
    if not _is_sha(review.get("signed_review_sha256")):
        raise ValueError("Missing SHA-256 of separately verified external review")
    cust = policy.get("custodian")
    if not isinstance(cust,dict):
        raise ValueError("Missing custodian")
    approved=cust.get("authorized_external_custodians")
    trusted=cust.get("trusted_ed25519_public_keys_base64")
    if not isinstance(approved,list) or not isinstance(trusted,dict):
        raise ValueError("Incomplete trusted custodian identities and public keys")
    if not approved or set(approved)!=set(trusted) or len(approved)!=len(set(approved)):
        raise ValueError("Custodian identities not uniquely preapproved")
    for issuer,key in trusted.items():
        if not isinstance(issuer,str) or not issuer or issuer.lower() in ("janus","synthetic","self","hawkar-usls"):
            raise ValueError("Disallowed self-custodian")
        if not isinstance(key,str) or len(key)>128:
            raise ValueError("Unbounded/invalid public key")
    cases=policy.get("locked_candidate_cohort")
    if not isinstance(cases,list) or not 3<=len(cases)<=8:
        raise ValueError("Require frozen 3..8 candidate SAT cases")
    if len({c.get("candidate_id") for c in cases if isinstance(c,dict)})!=len(cases):
        raise ValueError("Duplicate frozen candidate identity")
    if len({c.get("source_sha256") for c in cases if isinstance(c,dict)})!=len(cases):
        raise ValueError("Duplicate original source")
    families=set()
    for c in cases:
        if not isinstance(c,dict) or c.get("external_issuer_id") not in trusted:
            raise ValueError("Candidate not bound to independently approved signer")
        families.add(c.get("family"))
        if not isinstance(c.get("candidate_id"),str) or not c["candidate_id"]:
            raise ValueError("Missing frozen case ID")
        if not all(_is_sha(c.get(k)) for k in ("source_sha256","model_sha256")):
            raise ValueError("Frozen source/model SHA missing")
        if not all(type(c.get(k)) is int and c[k]>=0 for k in (
                "n_variables","n_clauses","n_literal_occurrences")):
            raise ValueError("Missing frozen CNF shape")
    if len(families)<3 or None in families:
        raise ValueError("Require three externally chosen independent SAT families")
    inputs=policy.get("input_limits")
    if not isinstance(inputs,dict):
        raise ValueError("Missing frozen input budgets")
    reference={"max_source_bytes":134217728,"max_source_variables":5000,
               "max_source_clauses":30000,"max_source_literals":120000,
               "max_model_bytes":200000}
    if any(type(inputs.get(k)) is not int or not 0<inputs[k]<=v for k,v in reference.items()):
        raise ValueError("Unbounded input budget or wrong type")
    if policy.get("no_post_hoc_replacement") is not True or policy.get("negative_and_timeout_cases_retained") is not True:
        raise ValueError("Missing freeze/negative-result commitments")
    if not _is_sha(policy.get("algorithm_commit_sha256")):
        raise ValueError("Original algorithm commit not frozen")
    return policy

def approved_policy():
    """Only the code-reviewed, immutable code-pinned policy can ever be loaded."""
    pins=(PINNED_TRUST_POLICY_RELATIVE_PATH,PINNED_TRUST_POLICY_BLOB_SHA,
          PINNED_REVIEW_ATTESTATION_SHA256)
    if all(p is None for p in pins):
        return None
    if any(p is None for p in pins):
        raise ValueError("Incomplete code-reviewed trust root pins")
    path = (HERE / PINNED_TRUST_POLICY_RELATIVE_PATH).resolve()
    if not path.is_relative_to(HERE) or not path.is_file():
        raise ValueError("Untrusted or missing outside trust policy path")
    if not _is_sha(PINNED_TRUST_POLICY_BLOB_SHA) or not _is_sha(PINNED_REVIEW_ATTESTATION_SHA256):
        raise ValueError("Malformed code-pinned authority SHA")
    obj=_check_lock_structure(json.loads(path.read_text(encoding="utf-8")))
    if obj["external_review"]["signed_review_sha256"] != PINNED_REVIEW_ATTESTATION_SHA256:
        raise ValueError("External authority review SHA not code-pinned")
    blob=subprocess.run(["git","hash-object",str(path)],check=True,text=True,capture_output=True).stdout.strip()
    if blob!=PINNED_TRUST_POLICY_BLOB_SHA:
        raise ValueError("Immutable trust policy Git blob mismatch")
    return obj

def admit_case(policy, candidate_id, receipt_file, cnf_file, model_file):
    matches=[x for x in policy["locked_candidate_cohort"] if x["candidate_id"]==candidate_id]
    if len(matches)!=1:
        raise ValueError("Candidate absent from frozen approved cohort")
    receipt=load_json_bounded(receipt_file,MAX_RECEIPT)
    verified=check_external_evidence(policy,matches[0],receipt,cnf_file,model_file)
    # This result is cryptographic and mathematical replay, never third-party
    # endorsement merely because a signed data item passed.
    return {"schema":"JANUS-004D9B-VERIFIED-CANDIDATE-RESEARCH-RECEIPT-V1",
            "candidate_id":candidate_id,
            "cryptographic_and_source_model_replay":verified,
            "third_party_administrative_review":"SEPARATELY_RECORDED_NOT_PROVEN_BY_THIS_SOFTWARE",
            "blind_science_verdict":"NOT_YET_EVALUATED",
            "solver_performance_verdict":"NOT_EVALUATED",
            "production_C023":"UNCHANGED"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight", action="store_true")
    p.add_argument("--candidate-id")
    p.add_argument("--cnf", type=Path)
    p.add_argument("--model", type=Path)
    p.add_argument("--signed-receipt", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args=p.parse_args()
    policy=approved_policy()
    if policy is None:
        payload={"status":"WAITING_FOR_OUTSIDE_ADMIN_APPROVAL_AND_CODE_PINNED_LOCKFILE",
                 "actual_external_SAT_cases_admitted":0,"performance":"NOT_RUN",
                 "old_004D9_frozen_policy":"UNCHANGED","C023":"UNCHANGED"}
    elif args.preflight:
        payload={"status":"REVIEWED_LOCKFILE_PINNED_AWAITING_EXACT_CANDIDATE_RELEASE",
                 "locked_candidates":len(policy["locked_candidate_cohort"]),
                 "external_science":"NOT_YET_VERIFIED","C023":"UNCHANGED"}
    else:
        if not all((args.candidate_id,args.cnf,args.model,args.signed_receipt)):
            p.error("No source and signed receipt: choose --preflight")
        payload=admit_case(policy,args.candidate_id,args.signed_receipt,args.cnf,args.model)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(payload,sort_keys=True,indent=2)+"\n")
    print("004D9B_TRUST_GATE",json.dumps({"status":payload.get("status","SIGNED_REPLAY_ONLY")},sort_keys=True))
if __name__=="__main__":
    main()
