#!/usr/bin/env python3
"""JANUS TIME-SAT-004D9 · fail-closed independently curated SAT model intake.

Research only, no solver/budgeted benchmark/prod changes. A signed original
source receipt must bind to a public key already anchored in a frozen separate
policy AND an exact precommitted candidate SHA. A self-described provider,
self-published signing key, or unsigned catalog SAT label has NO evidentiary
authority. The entire original CNF is model-replayed BEFORE any 004D6 rank.
A cryptographic signature is necessary but not sufficient to establish an
independent administrator (external 004C witness remains OPEN).
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import base64
import binascii
import json
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf
from janus_time_sat_004d8_sat_gate import certified_model
from janus_time_sat_004d7_rank_gate import source_rank_experiment

ROOT=Path("experiments/time_sat_004_external")
POLICY=ROOT/"PREREGISTERED_004D9_EXTERNAL_WITNESS_INTAKE_20261102.json"
POLICY_GIT_BLOB="83f17049fdcc663dd8acc8f878e0ca9bc73623cf"
MAX_SOURCE=134_217_728
MAX_MODEL=200_000
MAX_RECEIPT=16_384
MAX_BUDGET_AS=2_147_483_648
MAX_CPU=18
VALID_RECEIPT_KEYS=frozenset((
    "schema","candidate_id","external_issuer_id","source_sha256","model_sha256",
    "n_variables","n_clauses","n_literal_occurrences","signature_base64"
))
HEX="0123456789abcdef"

def is_sha(text):
    return (isinstance(text,str) and len(text)==64
            and all(c in HEX for c in text))

def b64dec(text,expected_len):
    if not isinstance(text,str):
        raise ValueError("Base64 field is missing or nonstring")
    try: b=base64.b64decode(text,validate=True)
    except (ValueError,binascii.Error) as ex:raise ValueError("Invalid Base64") from ex
    if len(b)!=expected_len:raise ValueError("Wrong Ed25519 key/signature length")
    return b

def canonical_receipt_bytes(receipt):
    if set(receipt)!=VALID_RECEIPT_KEYS:
        raise ValueError("Extra or missing signed receipt fields")
    value={k:receipt[k] for k in sorted(receipt) if k!="signature_base64"}
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")

def digest_file(path,limit):
    h=sha256()
    total=0
    with path.open("rb") as fd:
        while True:
            chunk=fd.read(min(65536,limit-total+1))
            if not chunk:break
            total+=len(chunk)
            if total>limit:raise ValueError("Evidence file over frozen byte budget")
            h.update(chunk)
    return h.hexdigest()

def load_json_bounded(path,limit):
    if path.stat().st_size>limit:raise ValueError("External JSON exceeds frozen bytes")
    return json.loads(path.read_text(encoding="utf-8"))

def policy_pending(policy):
    approved=policy.get("custodian",{}).get("trusted_ed25519_public_keys_base64",{})
    cases=policy.get("locked_candidate_cohort",[])
    if not approved or not cases:
        return {"status":"WAITING_FOR_EXTERNAL_WITNESS",
                "reason":"No external custodian public key and/or no precommitted sources",
                "actual_external_SAT_cases_admitted":0,
                "model_replay":"NOT_RUN","rank_experiment":"NOT_RUN",
                "admin_independence":"NOT_ESTABLISHED",
                "C023_main":"UNCHANGED"}
    return None

def check_external_evidence(policy,case,receipt,cnf,model_file):
    """Returns bound SAT replay receipt only, not a solver result or blind witness."""
    if policy_pending(policy):
        raise ValueError("No preapproved external public key and cohort")
    if not isinstance(receipt,dict):raise ValueError("Non-object external receipt")
    payload=canonical_receipt_bytes(receipt)
    if receipt["schema"]!="JANUS-TIME-SAT-004D9-INDEPENDENT-SAT-CUSTODIAN-RECEIPT-V1":
        raise ValueError("Unknown signed receipt protocol")
    if not isinstance(case,dict):
        raise ValueError("Missing frozen case")
    if case.get("candidate_id")!=receipt["candidate_id"]:
        raise ValueError("Source ID differs from PRE-registered cohort")
    if case.get("external_issuer_id")!=receipt["external_issuer_id"]:
        raise ValueError("Issuer differs from frozen source")
    if case.get("external_issuer_id") in ("Hawkar-usls","JANUS","self","synthetic"):
        raise ValueError("Source under owner control is NOT an outside witness")
    issuer=receipt["external_issuer_id"]
    if issuer not in policy["custodian"]["authorized_external_custodians"]:
        raise ValueError("No authorized custodian identity")
    pubtext=policy["custodian"]["trusted_ed25519_public_keys_base64"].get(issuer)
    if not pubtext:
        raise ValueError("Missing separately pinned public key for this exact custodian")
    frozen_fields=("source_sha256","model_sha256","n_variables","n_clauses","n_literal_occurrences")
    for k in frozen_fields:
        if receipt[k]!=case.get(k):raise ValueError("Signed receipt differs from frozen candidate "+k)
    if not is_sha(receipt["source_sha256"]) or not is_sha(receipt["model_sha256"]):
        raise ValueError("Original source/model sha must be lowercase 64-digit hex")
    for name in ("n_variables","n_clauses","n_literal_occurrences"):
        if type(receipt[name]) is not int or receipt[name]<0:
            raise ValueError("Invalid source dimension")
    n=receipt["n_variables"];m=receipt["n_clauses"];lits=receipt["n_literal_occurrences"]
    cap=policy["input_limits"]
    if not (1<=n<=cap["max_source_variables"]
            and 0<=m<=cap["max_source_clauses"]
            and 0<=lits<=cap["max_source_literals"]):
        raise ValueError("Candidate exceeds frozen bounded CNF dimensions")
    # Verify a pre-approved key, NOT a public key copied from untrusted receipt.
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.exceptions import InvalidSignature
    key=Ed25519PublicKey.from_public_bytes(b64dec(pubtext,32))
    try:key.verify(b64dec(receipt["signature_base64"],64),payload)
    except InvalidSignature as ex:raise ValueError("Signed external receipt FAIL") from ex
    if digest_file(cnf,cap["max_source_bytes"])!=receipt["source_sha256"]:
        raise ValueError("Downloaded original CNF SHA differs from signed preregistration")
    if digest_file(model_file,cap["max_model_bytes"])!=receipt["model_sha256"]:
        raise ValueError("Full original SAT model SHA differs from signed preregistration")
    shape=scan_dimacs(cnf)
    if any(shape[k]!=receipt[k] for k in frozen_fields if k in shape):
        raise ValueError("Malformed original CNF shape")
    for k in ("n_variables","n_clauses","n_literal_occurrences"):
        if shape[k]!=receipt[k]:raise ValueError("Declared DIMACS shape changed "+k)
    original_rows=read_cnf(cnf,n,m,max_literals=cap["max_source_literals"])
    model=load_json_bounded(model_file,cap["max_model_bytes"])
    if not isinstance(model,dict) or set(model)!={"signed_model"}:
        raise ValueError("Model JSON must have exactly one signed_model array")
    verify=certified_model(original_rows,n,model["signed_model"])
    if verify["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        raise ValueError("Original complete SAT model failed clause check: "+verify["status"])
    # No real SAT solver invoked: evaluate rank ONLY AFTER source/auth/model accepted.
    began=perf_counter()
    analysis=source_rank_experiment(original_rows,n)
    elapsed=perf_counter()-began
    if analysis["status"]!="SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
        raise ValueError("Original-resolution proof replay/rank failed: "+analysis["status"])
    values={abs(v):v>0 for v in model["signed_model"]}
    for x in analysis["additional_parity_keys"]:
        if (sum(int(values[v]) for v in x["variables"])&1)!=x["rhs"]:
            raise ValueError("Source derived XOR contradicts verified original SAT model")
    rk=analysis["independent_rank_analysis"]
    if rk["source_plus_derived_GF2_inconsistent"]:
        raise ValueError("Verified original SAT model conflicts with derived GF2")
    return {
       "status":"SIGNED_PRECOMMITTED_EXTERNAL_SOURCE_SAT_MODEL_AND_SOURCE_PROOF_VERIFIED",
       "source_sha256":receipt["source_sha256"],
       "model_sha256":receipt["model_sha256"],
       "signed_external_issuer_id":issuer,
       "cryptographic_signature_matches_separately_approved_policy_key":True,
       "trusted_key_external_administrative_independence":"REQUIRES_SEPARATE_REAL_WORLD_AUDIT",
       "original_verified_SAT_model":verify,
       "original_source_resolution_replayed":True,
       "new_source_XOR_forms":analysis["source_derived_new_syntactic_XOR_count"],
       "incremental_coefficient_rank":rk["independent_new_coefficient_rank"],
       "incremental_augmented_rank":rk["independent_new_augmented_rank"],
       "original_evidence_rank_DAG":analysis,
       "rank_scan_seconds_NOT_FULL_END_TO_END_BENCHMARK":elapsed,
       "original_CNF_kept_unmodified":True,
       "real_world_external_Witness":"OPEN_PENDING_INDEPENDENT_ADMINISTRATIVE_AUDIT",
       "performance_claim":"NONE",
       "C023_main":"UNCHANGED"
    }

def frozen_policy():
    # Policy is intentionally empty/untrusted until separate future precommit.
    digest=subprocess.run(["git","hash-object",str(POLICY)],text=True,
                          capture_output=True,check=True).stdout.strip()
    if digest!=POLICY_GIT_BLOB:
        raise ValueError("Frozen external source/custodian policy Git blob changed")
    return json.loads(POLICY.read_text(encoding="utf-8"))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--cnf",type=Path)
    p.add_argument("--model",type=Path)
    p.add_argument("--signed-receipt",type=Path)
    p.add_argument("--candidate-id")
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS,(MAX_BUDGET_AS,MAX_BUDGET_AS))
    resource.setrlimit(resource.RLIMIT_CPU,(MAX_CPU,MAX_CPU+1))
    policy=frozen_policy()
    pending=policy_pending(policy)
    if pending:
        result=pending
    elif args.preflight:
        result={"status":"PRECOMMIT_PRESENT_BUT_NO_EXTERNAL_INPUT_OPENED",
                "rank":"NOT_RUN","C023_main":"UNCHANGED"}
    else:
        if not (args.cnf and args.model and args.signed_receipt and args.candidate_id):
            raise SystemExit("Externally signed source/model evidence required")
        records=[x for x in policy["locked_candidate_cohort"]
                 if x.get("candidate_id")==args.candidate_id]
        if len(records)!=1:raise ValueError("Candidate is not uniquely preregistered")
        receipt=load_json_bounded(args.signed_receipt,MAX_RECEIPT)
        result=check_external_evidence(policy,records[0],receipt,args.cnf,args.model)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004D9_INTAKE",json.dumps({k:result[k] for k in ("status","C023_main")},sort_keys=True))
if __name__=="__main__":main()
