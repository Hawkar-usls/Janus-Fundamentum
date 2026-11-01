#!/usr/bin/env python3
"""004D7 · exact GF(2) novelty gate on independently replayed source resolution.

This module never invokes a SAT solver; never asserts UNSAT from an augmented
rank inconsistency alone without a portable proof; never benchmarks a
redundant vector. All source CNF remains unchanged. Source-proven resolution
proof DAG saved by the caller when handling original competition CNFs.
"""
from __future__ import annotations
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d6_bounded_resolution import source_derived_xor
from janus_time_sat_004d6_replay import replay_all
from janus_time_sat_004d6_rank_audit import derive_keys

def vector(variables,rhs,n,*,augmented=True):
    if type(rhs) is not int or rhs not in (0,1):
        raise ValueError("malformed GF2 RHS")
    bits=0
    for v in variables:
        if type(v) is not int or not 1<=v<=n:
            raise ValueError("GF2 variable outside CNF")
        bits^=1<<(v-1)
    if augmented:bits|=rhs<<n
    return bits

def add_to_basis(v,basis):
    """Exact GF2 insert. Returns whether vector is independent of basis."""
    while v:
        pivot=v.bit_length()-1
        if pivot not in basis:
            basis[pivot]=v
            return True
        v^=basis[pivot]
    return False

def independence_record(known,new,n):
    """New vectors are ordered lexicographically and checked vs known basis."""
    base_coeff={};base_aug={}
    for variables,rhs in sorted(known):
        add_to_basis(vector(variables,rhs,n,augmented=False),base_coeff)
        add_to_basis(vector(variables,rhs,n,augmented=True),base_aug)
    before_coeff,before_aug=len(base_coeff),len(base_aug)
    # Keep separate bases to avoid mixing constant terms and coefficient rank.
    coeff=dict(base_coeff);aug=dict(base_aug)
    new_coeff=[];new_aug=[]
    for variables,rhs in sorted(new):
        vc=vector(variables,rhs,n,augmented=False)
        va=vector(variables,rhs,n,augmented=True)
        if add_to_basis(vc,coeff):
            new_coeff.append({"variables":list(variables),"rhs":rhs})
        if add_to_basis(va,aug):
            new_aug.append({"variables":list(variables),"rhs":rhs})
    return {
      "explicit_source_GF2_coefficient_rank":before_coeff,
      "explicit_source_GF2_augmented_rank":before_aug,
      "with_derived_GF2_coefficient_rank":len(coeff),
      "with_derived_GF2_augmented_rank":len(aug),
      "independent_new_coefficient_rank":len(coeff)-before_coeff,
      "independent_new_augmented_rank":len(aug)-before_aug,
      "new_coefficient_rank_witnesses":new_coeff,
      "new_augmented_rank_witnesses":new_aug,
      "known_GF2_source_inconsistent":before_aug>before_coeff,
      "source_plus_derived_GF2_inconsistent":len(aug)>len(coeff),
      "UNSAT_portable_proof":"NOT_PRODUCED",
      "speedup":"NOT_MEASURED"
    }

def source_rank_experiment(rows,n):
    prior=extract_paged_mixed_xor(rows,n)
    if prior.get("status")!="SOURCE_PARTITION_VERIFIED":
        return {"status":"ABSTAIN_ORIGINAL_SOURCE_EXPLICIT_XOR_GUARD",
                "raw_guard":prior.get("status")}
    result=source_derived_xor(rows,n)
    if result.get("status")!="SOURCE_RESOLUTION_BOUNDED_PASS":
        return {"status":"ABSTAIN_SOURCE_RESOLUTION",
                "raw_guard":result.get("status")}
    if not replay_all(rows,n,result):
        raise AssertionError("independently checked exact source resolution proof FAILED")
    known={(tuple(e["variables"]),e["rhs"]) for e in prior["equations"]}
    new=derive_keys(rows,n,result,known)
    if len(new)!=result["new_complete_xor_sign_mask_equations"]:
        raise AssertionError("independent derivation disagrees with original proof key count")
    rank=independence_record(known,new,n)
    if rank["independent_new_augmented_rank"]<rank["independent_new_coefficient_rank"]:
        raise AssertionError("GF2 augmented rank cannot be smaller than coefficient rank")
    return {
      "schema":"JANUS-TIME-SAT-004D7-EXACT-SOURCE-RESOLUTION-RANK-GATE-V1",
      "status":"SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS",
      "original_complete_mask_XOR_count":len(known),
      "source_derived_new_syntactic_XOR_count":len(new),
      "source_resolution_new_clause_count":result["total_new_resolvents"],
      "source_resolution_truncated":result["truncated_by_total_resolvent_cap"],
      "independent_rank_analysis":rank,
      "additional_parity_keys":[{"variables":list(k[0]),"rhs":k[1]}
                                for k in sorted(new)],
      "resolution_evidence":result,
      "verification":"EXACT_ORIGINAL_SOURCE_CLAUSE_DAG_REPLAY_PASS",
      "SAT_UNSAT_solver_calls":0,
      "original_CNF_retained":True,
      "independent_external_witness":"OPEN",
      "production_C023":"UNCHANGED"
    }
