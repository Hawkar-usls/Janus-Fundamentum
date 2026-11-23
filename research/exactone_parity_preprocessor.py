#!/usr/bin/env python3
"""JANUS Fundamentum: proof-carrying polynomial Exact-One preprocessing.

Input: conjunction of one- or three-literal exactly-one clauses in DIMACS
signed variable notation. Both signs and repeated literals are supported.
This is NOT a complete polynomial SAT solver or a proof of P=NP.

Method: exact-one unit inference plus Gaussian elimination over GF(2) of
necessary parity equations. Every new forced assignment has a checkable
source-clause XOR or local clause certificate. No network/provider calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path

SCHEMA = "janus.fundamentum.exactone_parity_reduction.v1"


def canon(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(x):
    return hashlib.sha256(canon(x)).hexdigest()


def validate(case):
    if not isinstance(case, dict) or set(case) != {"n", "clauses"}:
        raise ValueError("INPUT_SCHEMA")
    n, clauses = case["n"], case["clauses"]
    if type(n) is not int or n < 1 or not isinstance(clauses, list):
        raise ValueError("INPUT_DIMENSIONS")
    for c in clauses:
        if not isinstance(c, list) or len(c) not in (1, 3):
            raise ValueError("EXACT_ONE_LINEAR_OR_CUBIC_ONLY")
        if any(type(x) is not int or x == 0 or abs(x) > n for x in c):
            raise ValueError("INVALID_LITERAL")
    return n, clauses


def lit_value(lit, assign):
    v = abs(lit)
    return (assign[v] ^ int(lit < 0)) if v in assign else None


def clause_state(clause, assign):
    ones = 0
    free = []
    for lit in clause:
        value = lit_value(lit, assign)
        if value is None:
            free.append(lit)
        else:
            ones += value
    return ones, free


def row_of_clause(clause, assign):
    """Necessary XOR relation; 3 true literals can pass parity, never promote."""
    mask, rhs = 0, 1
    for lit in clause:
        bit = 1 << (abs(lit) - 1)
        mask ^= bit
        if lit < 0:
            rhs ^= 1
    for var, val in assign.items():
        bit = 1 << (var - 1)
        if mask & bit:
            mask ^= bit
            rhs ^= val
    return mask, rhs


def sources_of(bits):
    out = []
    while bits:
        bit = bits & -bits
        out.append(bit.bit_length() - 1)
        bits ^= bit
    return out


def xor_sources(case, assignments, indices):
    mask = rhs = 0
    for index in indices:
        row_mask, row_rhs = row_of_clause(case["clauses"][index], assignments)
        mask ^= row_mask
        rhs ^= row_rhs
    return mask, rhs


def parity_consequence(case, assign):
    """One forced literal or a parity contradiction, with XOR lineage."""
    bases = {}
    for ci, clause in enumerate(case["clauses"]):
        mask, rhs = row_of_clause(clause, assign)
        lineage = 1 << ci
        while mask:
            pivot = (mask & -mask).bit_length() - 1
            if pivot in bases:
                bm, br, bs = bases[pivot]
                mask, rhs, lineage = mask ^ bm, rhs ^ br, lineage ^ bs
            else:
                bases[pivot] = (mask, rhs, lineage)
                break
        if mask == 0 and rhs == 1:
            return {"kind":"parity_conflict", "sources":sources_of(lineage)}
    # Gauss-Jordan backward elimination exposes singleton implied equations.
    for pivot in sorted(bases, reverse=True):
        bm, br, bs = bases[pivot]
        for other in sorted(bases):
            if other != pivot and (bases[other][0] >> pivot) & 1:
                a, b, c = bases[other]
                bases[other] = (a ^ bm, b ^ br, c ^ bs)
    singleton = []
    for mask, rhs, lineage in bases.values():
        if mask and mask.bit_count() == 1:
            var = mask.bit_length()
            if var not in assign:
                singleton.append((var, rhs, lineage))
    if not singleton:
        return None
    var, value, sources = min(singleton, key=lambda x:x[0])
    return {"kind":"parity_force", "variable":var,
            "value":value, "sources":sources_of(sources)}


def simplified_clauses(case, assign):
    out, seen = [], set()
    for clause in case["clauses"]:
        true_count, unassigned = clause_state(clause, assign)
        if true_count == 1:
            if unassigned:
                raise AssertionError("NOT_AT_FIXED_POINT")
            continue
        if true_count > 1 or not unassigned:
            raise AssertionError("CONFLICT_SHOULD_BE_REPORTED")
        key = tuple(unassigned)
        if key not in seen:
            out.append(list(unassigned))
            seen.add(key)
    return out


def make_result(case, assignments, certificate, status, conflict=None):
    residual = None if status == "UNSAT" else simplified_clauses(case, assignments)
    result = {
        "schema": SCHEMA,
        "input_sha256": digest(case),
        "status": status,
        "assignments": {str(k):v for k,v in sorted(assignments.items())},
        "residual_clauses": residual,
        "residual_used_variables": None if residual is None else len(
            {abs(lit) for c in residual for lit in c}),
        "certificate": certificate,
        "conflict": conflict,
        "preprocessing_is_polynomial": True,
        "preprocessing_is_complete_sat_solver": False,
        "universal_polynomial_solution_bound_proven": False,
        "p_vs_np": "OPEN",
        "provider_calls": 0,
    }
    result["result_sha256"] = digest(result)
    return result


def preprocess(case):
    n, clauses = validate(case)
    assign, certificate = {}, []
    while True:
        selected = None
        for i, clause in enumerate(clauses):
            ones, free = clause_state(clause, assign)
            if ones > 1 or (ones == 0 and not free):
                return make_result(case, assign, certificate, "UNSAT",
                                   {"kind":"clause_conflict", "clause_index":i})
            if free and (ones == 1 or (ones == 0 and len(free) == 1)):
                lit = free[0]
                # When 1 already true, all remaining literals must be false.
                value = int(lit < 0) if ones == 1 else int(lit > 0)
                selected = {"kind":"clause_force","clause_index":i,
                            "variable":abs(lit),"value":value}
                break
        if selected is None:
            selected = parity_consequence(case, assign)
        if selected is None:
            residual = simplified_clauses(case, assign)
            return make_result(case, assign, certificate,
                               "SAT" if not residual else "REDUCED")
        if selected["kind"] in ("parity_conflict",):
            return make_result(case, assign, certificate, "UNSAT", selected)
        var, value = selected["variable"], selected["value"]
        if var in assign:
            raise AssertionError("DUPLICATE_OR_CONTRADICTORY_FORCE")
        assign[var] = value
        certificate.append(selected)
        assert len(certificate) <= n


def verify(case, result):
    """Independent certificate checker: never calls the Gaussian solver."""
    try:
        validate(case)
        if not isinstance(result, dict) or result.get("schema") != SCHEMA:
            return False
        expected_hash = result.get("result_sha256")
        data = dict(result)
        data.pop("result_sha256", None)
        if digest(case) != result.get("input_sha256") or digest(data) != expected_hash:
            return False
        if (result.get("preprocessing_is_complete_sat_solver") is not False
            or result.get("universal_polynomial_solution_bound_proven") is not False
            or result.get("p_vs_np") != "OPEN" or result.get("provider_calls") != 0):
            return False
        assign = {}
        clauses = case["clauses"]
        for event in result["certificate"]:
            var, value = event["variable"], event["value"]
            if type(var) is not int or not 1 <= var <= case["n"] or var in assign or type(value) is not int or value not in (0,1):
                return False
            if event["kind"] == "clause_force":
                ci = event["clause_index"]
                if type(ci) is not int or not 0 <= ci < len(clauses):
                    return False
                ones, free = clause_state(clauses[ci], assign)
                if not free or abs(free[0]) != var or not (
                    ones == 1 or (ones == 0 and len(free) == 1)):
                    return False
                literal = free[0]
                expected_value = int(literal < 0) if ones == 1 else int(literal > 0)
                if expected_value != value:
                    return False
            elif event["kind"] == "parity_force":
                ids = event["sources"]
                if (not isinstance(ids,list) or not ids
                    or len(set(ids)) != len(ids)
                    or any(type(i) is not int or i < 0 or i >= len(clauses) for i in ids)):
                    return False
                mask, rhs = xor_sources(case, assign, ids)
                if mask != (1 << (var-1)) or rhs != value:
                    return False
            else:
                return False
            assign[var] = value
        if result["assignments"] != {str(k):v for k,v in sorted(assign.items())}:
            return False
        status = result["status"]
        if status == "UNSAT":
            conflict = result["conflict"]
            if not isinstance(conflict,dict):
                return False
            if conflict["kind"] == "clause_conflict":
                ci = conflict["clause_index"]
                if type(ci) is not int or not 0 <= ci < len(clauses):
                    return False
                ones, free = clause_state(clauses[ci], assign)
                if not (ones > 1 or (ones == 0 and not free)):
                    return False
            elif conflict["kind"] == "parity_conflict":
                ids = conflict["sources"]
                if not isinstance(ids,list) or not ids or len(set(ids))!=len(ids):
                    return False
                if any(type(i) is not int or i<0 or i>=len(clauses) for i in ids):
                    return False
                if xor_sources(case,assign,ids) != (0,1):
                    return False
            else:
                return False
            return result["residual_clauses"] is None
        if status not in ("REDUCED","SAT") or result["conflict"] is not None:
            return False
        expected = simplified_clauses(case,assign)
        return (result["residual_clauses"] == expected
                and result["residual_used_variables"] == len(
                    {abs(lit) for c in expected for lit in c})
                and (status == "SAT") == (not expected))
    except (KeyError, ValueError, TypeError, AssertionError, OverflowError):
        return False


def solution_set(case):
    """Independent exponential reference, only for small TEST fixtures."""
    n, clauses = validate(case)
    if n > 18:
        raise ValueError("REFERENCE_ENUMERATION_CAP")
    sol = set()
    for bits in range(1 << n):
        if all(sum(((bits >> (abs(l)-1)) & 1) ^ int(l<0) for l in c) == 1 for c in clauses):
            sol.add(bits)
    return sol


def reduced_solution_set(case, result):
    n = case["n"]
    if n > 18 or result["status"] == "UNSAT":
        return set()
    assign = {int(k):v for k,v in result["assignments"].items()}
    out = set()
    for bits in range(1 << n):
        if any(((bits>>(k-1))&1)!=v for k,v in assign.items()):
            continue
        if all(sum(((bits >> (abs(l)-1)) & 1) ^ int(l<0) for l in c)==1
               for c in result["residual_clauses"]):
            out.add(bits)
    return out


def gadget_family(blocks):
    """Cubic-only class with sound guaranteed 3/5 variable elimination."""
    if type(blocks) is not int or blocks < 1:
        raise ValueError("BLOCK_COUNT")
    clauses=[]
    for k in range(blocks):
        a=5*k
        clauses.extend([[a+1,a+2,a+3],
                        [a+1,a+2,a+4],
                        [a+3,a+4,a+5]])
    return {"n":5*blocks, "clauses":clauses}


def self_test():
    cases=[
        {"n":1, "clauses":[[1]]},
        {"n":1, "clauses":[[-1]]},
        {"n":3, "clauses":[[1,2,3],[1,2,-3]]},
        {"n":3, "clauses":[[1,1,2],[3,-2,1]]},
        {"n":3, "clauses":[[-1,-2,-3],[1,2,3]]},
        gadget_family(1),gadget_family(2),
    ]
    rng=random.Random(20261028)
    for _ in range(320):
        n=rng.randint(1,8)
        m=rng.randint(0,9)
        clauses=[]
        for _ in range(m):
            lits=[]
            for _ in range(rng.choice([1,3])):
                v=rng.randint(1,n)
                lits.append(v if rng.choice([0,1]) else -v)
            clauses.append(lits)
        cases.append({"n":n,"clauses":clauses})
    result_counter={}
    for case in cases:
        result=preprocess(case)
        assert verify(case,result), ("CERTIFICATE_FAIL",case,result)
        assert solution_set(case)==reduced_solution_set(case,result), ("TRUTH_FAIL",case,result)
        result_counter[result["status"]]=result_counter.get(result["status"],0)+1
    family=preprocess(gadget_family(2))
    assert len(family["assignments"])==6 and family["residual_used_variables"]==4
    assert all(e["kind"] in ("parity_force","clause_force") for e in family["certificate"])
    # A maliciously re-hashed but unjustified assignment must be rejected.
    bad=dict(family)
    bad["certificate"]=list(family["certificate"])
    bad["certificate"][0]=dict(bad["certificate"][0],value=1-bad["certificate"][0]["value"])
    bad["result_sha256"]=digest({k:v for k,v in bad.items() if k!="result_sha256"})
    assert not verify(gadget_family(2),bad)
    return {"status":"PASS","independent_reference_cases":len(cases),
            "statuses":result_counter,"gadget_variables_original":10,
            "gadget_variables_remaining":family["residual_used_variables"],
            "gadget_forced_assignments":len(family["assignments"]),
            "negative_certificate_control":"REJECTED",
            "complexity":"O((n+literal_occurrences)^5) conservative bit-operation upper bound",
            "p_vs_np":"OPEN"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test",action="store_true")
    g.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.self_test:
        answer=self_test()
    else:
        case=json.loads(a.input.read_text(encoding="utf-8"))
        answer=preprocess(case)
        if not verify(case,answer):
            raise RuntimeError("INDEPENDENT_CERTIFICATE_FAILED")
    content=json.dumps(answer,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if a.output:
        a.output.write_text(content,encoding="utf-8")
    print(content)


if __name__=="__main__":
    main()
