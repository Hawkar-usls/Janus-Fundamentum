#!/usr/bin/env python3
"""TIME-SAT-004D1 research: independently checkable *exact* XOR-CNF recognition.

A complete CNF for a k-variable XOR equation contains all 2^(k-1)
clauses falsified by assignments with the opposite parity. Recognition
is allowed ONLY when EVERY original clause belongs to a complete block.
Otherwise ABSTAIN with original CNF untouched. Never infer from dimensions.

Gaussian elimination over GF(2) is classical polynomial-time algebra;
this is not a general SAT solver, new P=NP theorem or physical time reversal.
No GitHub/Rowan fees, no CDCL search, no production C023 changes.
"""
from __future__ import annotations

from hashlib import sha256
import json
from time import perf_counter

MAX_N=5000
MAX_ROWS=30000
MAX_LITERALS=120000
MAX_GROUPS=20000
MAX_WIDTH=6


def source_digest(rows, n):
    """Unambiguous logical rows checksum, not the original raw DIMACS SHA."""
    payload=json.dumps({"n":n,"rows":rows},separators=(",",":"))
    return sha256(payload.encode("ascii")).hexdigest()


def group_parity_equations(rows,n):
    """Return all exact equations only for complete exclusive-or CNF cover.

    For a clause, its negative-literal sign mask represents the unique
    falsifying assignment on its variable support. A full XOR block has
    exactly 2^(k-1) distinct sign masks with identical mask parity.
    """
    if type(n) is not int or n<1 or n>MAX_N:
        return {"status":"ABSTAIN_N_LIMIT","equations":[]}
    if len(rows)>MAX_ROWS:
        return {"status":"ABSTAIN_ROW_LIMIT","equations":[]}
    groups={}
    scanned=0
    for index,row in enumerate(rows):
        if len(row)==0 or len(row)>MAX_WIDTH:
            return {"status":"ABSTAIN_UNSUPPORTED_WIDTH","equations":[]}
        scanned+=len(row)
        if scanned>MAX_LITERALS:
            return {"status":"ABSTAIN_LITERAL_BUDGET","equations":[]}
        if any(type(v) is not int or v==0 or abs(v)>n for v in row):
            return {"status":"ABSTAIN_INVALID_LITERAL","equations":[]}
        variables=tuple(sorted(abs(x) for x in row))
        if len(set(variables))!=len(variables):
            return {"status":"ABSTAIN_REPEATED_VARIABLE","equations":[]}
        mask=sum(1<<i for i,var in enumerate(variables)
                 if -var in row)
        if variables not in groups and len(groups)>=MAX_GROUPS:
            return {"status":"ABSTAIN_GROUP_BUDGET","equations":[]}
        groups.setdefault(variables,{}).setdefault(mask,[]).append(index)
    equations=[]
    for variables,signs in sorted(groups.items()):
        width=len(variables)
        expected=1<<(width-1)
        parities={mask.bit_count()&1 for mask in signs}
        if len(signs)!=expected or len(parities)!=1:
            return {"status":"ABSTAIN_NOT_FULL_XOR_COVER",
                    "equations":[],"groups_inspected":len(groups),
                    "complete_equations":len(equations),
                    "first_incomplete_support":list(variables),
                    "first_support_unique_masks":len(signs),
                    "first_support_expected_masks":expected,
                    "literal_occurrences_scanned":scanned}
        blocked_parity=next(iter(parities))
        rhs=1^blocked_parity
        equations.append({"variables":variables,"rhs":rhs,
                          "original_clause_indices":tuple(
                              idx for positions in signs.values() for idx in positions)})
    return {"status":"EXACT_XOR_COVER_PASS","equations":equations,
            "groups_inspected":len(groups),
            "literal_occurrences_scanned":scanned,
            "n":n,"clauses":len(rows)}


def _gauss_with_linear_combination(equations):
    """Return a satisfying bitset or a contradiction combination certificate."""
    basis={}
    for i,eq in enumerate(equations):
        bits=sum(1<<(v-1) for v in eq["variables"])
        rhs=eq["rhs"]
        witness=1<<i
        while bits:
            pivot=bits.bit_length()-1
            if pivot not in basis:
                basis[pivot]=(bits,rhs,witness)
                break
            old,old_rhs,old_witness=basis[pivot]
            bits^=old;rhs^=old_rhs;witness^=old_witness
        if not bits and rhs:
            return {"status":"EXACT_GF2_UNSAT_COMBINATION","combination_indices":
                    [v for v in range(len(equations)) if (witness>>v)&1],
                    "rank":len(basis)}
    solution=0
    for pivot in sorted(basis):
        bits,rhs,_=basis[pivot]
        old_parity=((bits ^ (1<<pivot)) & solution).bit_count()&1
        if rhs^old_parity:solution|=1<<pivot
    return {"status":"EXACT_GF2_SAT_CANDIDATE","bits":solution,
            "rank":len(basis)}


def check_original_cnf(rows,n,solution):
    if type(solution) is not int or solution<0 or solution.bit_length()>n:
        return False
    for clause in rows:
        if not any(bool(solution>>(abs(lit)-1)&1)==(lit>0)
                   for lit in clause):
            return False
    return True


def independently_replay_unsat_combination(rows,n,indices):
    """Rebuild source parity blocks and check a GF(2) sum of 0 = 1.

    This is separate logical replay from source, but same repo/admin: it
    does NOT qualify as an independent third-party proof verifier.
    """
    cover=group_parity_equations(rows,n)
    if cover["status"]!="EXACT_XOR_COVER_PASS":return False
    eq=cover["equations"]
    if type(indices) is not list or not indices or any(
            type(i) is not int or i<0 or i>=len(eq) for i in indices):
        return False
    if len(set(indices))!=len(indices):return False
    parity=0
    residual=set()
    for i in indices:
        parity^=eq[i]["rhs"]
        for variable in eq[i]["variables"]:
            if variable in residual:residual.remove(variable)
            else:residual.add(variable)
    return parity==1 and not residual


def solve_if_exact_xor(rows,n):
    start=perf_counter()
    cover=group_parity_equations(rows,n)
    result={
        "schema":"JANUS-TIME-SAT-004D1-EXACT-XOR-STRUCTURAL-V1",
        "scope":"PUBLIC_SOURCE_ONLY_STANDALONE_GF2_NOT_GENERAL_SAT",
        "source_logical_sha256":source_digest(rows,n),
        "source_n":n,"source_clauses":len(rows),
        "coverage_status":cover["status"],
        "group_count":cover.get("groups_inspected",0),
        "literal_occurrences_scanned":cover.get("literal_occurrences_scanned",0),
        "source_original_clauses_unmodified":True,
        "external_proof_admin":"NOT_INDEPENDENT",
        "production_C023":"UNCHANGED",
    }
    if cover["status"]!="EXACT_XOR_COVER_PASS":
        result["verdict"]="ABSTAIN_NO_SAT_CLAIM"
        result["reason"]=cover["status"]
        result["first_incomplete_support"]=cover.get("first_incomplete_support")
    else:
        equations=cover["equations"]
        eliminated=_gauss_with_linear_combination(equations)
        result["equation_count"]=len(equations)
        result["gf2_rank"]=eliminated["rank"]
        if eliminated["status"]=="EXACT_GF2_SAT_CANDIDATE":
            solution=eliminated["bits"]
            if not check_original_cnf(rows,n,solution):
                raise AssertionError("GF2 candidate fails ORIGINAL source CNF")
            result["verdict"]="SAT_ORIGINAL_MODEL_VERIFIED"
            result["model"]=tuple(i if (solution>>(i-1))&1 else -i
                                   for i in range(1,n+1))
        else:
            combination=eliminated["combination_indices"]
            if not independently_replay_unsat_combination(rows,n,combination):
                raise AssertionError("false GF2 contradiction certificate")
            result["verdict"]="GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY"
            result["xor_contradiction_equation_indices"]=combination
    result["gf2_and_verification_seconds"]=perf_counter()-start
    return result
