#!/usr/bin/env python3
"""TIME-SAT-004D8: independent source-CNF SAT model admissibility guard.

No trust in solver/catalog labels or unsatisfiable branch. A complete signed
assignment must satisfy EVERY clause of a SHA-pinned original source. Models
can be proposed externally (archived) or by verified exact-XOR algebra, but
this checker trusts ONLY the clauses and the exact full signed assignment.
"""
from __future__ import annotations
from hashlib import sha256
import json


def certified_model(rows,n,values):
    if type(n) is not int or n<1 or type(values) not in (list,tuple):
        return {"status":"BLOCK_INVALID_MODEL_FORMAT"}
    if len(values)!=n:
        return {"status":"BLOCK_INCOMPLETE_MODEL"}
    if any(type(x) is not int or x==0 or abs(x)>n for x in values):
        return {"status":"BLOCK_INVALID_MODEL_LITERAL"}
    if {abs(x) for x in values}!=set(range(1,n+1)):
        return {"status":"BLOCK_DUPLICATE_OR_MISSING_VARIABLE"}
    truth={abs(x):x>0 for x in values}
    for i,clause in enumerate(rows):
        if any(type(l) is not int or l==0 or abs(l)>n for l in clause):
            return {"status":"BLOCK_INVALID_ORIGINAL_CNF"}
        if not any(truth[abs(l)]==(l>0) for l in clause):
            return {"status":"BLOCK_MODEL_VIOLATES_ORIGINAL_CNF","first_failing_clause_index":i}
    payload=json.dumps(list(values),separators=(",",":")).encode("ascii")
    return {"status":"SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE",
            "verified_original_clause_count":len(rows),
            "model_variables":n,
            "signed_model_SHA256":sha256(payload).hexdigest()}


def gate_rank_for_sat(original_model_receipt,rank_diagnostic):
    if original_model_receipt.get("status")!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
        return "BLOCK_NO_VERIFIED_SAT_MODEL"
    if rank_diagnostic is None:
        return "BLOCK_NO_REPLAYED_RANK"
    if rank_diagnostic.get("status")!="SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
        return "BLOCK_SOURCE_PROOF_NOT_REPLAYED"
    rank=rank_diagnostic.get("independent_rank_analysis") or {}
    if rank.get("source_plus_derived_GF2_inconsistent"):
        return "BLOCK_DERIVED_GF2_CONFLICTS_WITH_VERIFIED_SAT_MODEL"
    if rank.get("independent_new_coefficient_rank",0)<=0:
        return "BLOCK_NO_NEW_INDEPENDENT_GF2_RANK"
    if rank.get("independent_new_augmented_rank",0)<=0:
        return "BLOCK_NO_NEW_AUGMENTED_GF2_RANK"
    return "POTENTIAL_RESEARCH_RANK_ONLY_FUTURE_BENCHMARK_REQUIRES_SEPARATE_APPROVAL"
