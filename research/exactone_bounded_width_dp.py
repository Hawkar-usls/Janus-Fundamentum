#!/usr/bin/env python3
"""Proof-carrying Exact-One SAT variable elimination at bounded primal width.

Unlike a cycle-cutset solver, this handles arbitrarily many cycles on
bounded-width instances. The width cap is explicit; if reached the result is
OPEN_WIDTH_CAP, never UNSAT. A polynomial independent checker validates
each local existential projection and any witness. P vs NP remains OPEN.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from exactone_parity_preprocessor import validate, digest, solution_set

SCHEMA = "janus.fundamentum.exactone_bounded_primal_width_v1"
MAX_WIDTH = 6


def _factor(scope, rows):
    return {
        "scope": tuple(scope),
        "rows": frozenset(tuple(x) for x in rows),
    }


def _initial_factors(case):
    n, clauses = validate(case)
    factors = []
    for clause in clauses:
        scope = sorted({abs(l) for l in clause})
        accepted = []
        for assignment in itertools.product((0, 1), repeat=len(scope)):
            values = dict(zip(scope, assignment))
            if sum(values[abs(lit)] ^ int(lit < 0) for lit in clause) == 1:
                accepted.append(assignment)
        factors.append(_factor(scope, accepted))
    return factors


def _neighbors(remaining, factors):
    graph = {v: set() for v in remaining}
    for fac in factors:
        s = fac["scope"]
        for x in s:
            graph[x].update(y for y in s if y != x)
    return graph


def _pick(remaining, factors):
    graph = _neighbors(remaining, factors)
    return min(remaining, key=lambda x:(len(graph[x]),x)), graph


def _accept(factor, values):
    return tuple(values[x] for x in factor["scope"]) in factor["rows"]


def _eliminate(factors, variable):
    """Compute an exact existential projection and one local lift choice."""
    bucket = [f for f in factors if variable in f["scope"]]
    untouched = [f for f in factors if variable not in f["scope"]]
    neighbors = sorted({v for f in bucket for v in f["scope"] if v != variable})
    accepted, choices = [], []
    for row in itertools.product((0, 1), repeat=len(neighbors)):
        values = dict(zip(neighbors, row))
        for bit in (0, 1):
            values[variable] = bit
            if all(_accept(f, values) for f in bucket):
                accepted.append(row)
                choices.append(bit)
                break
    result = _factor(neighbors, accepted)
    step = {
        "variable": variable,
        "scope": neighbors,
        "rows": [list(r) for r in accepted],
        "choices": choices,
        "bucket_size": len(bucket),
    }
    return untouched + [result], step


def _new_result(case, width_cap):
    return {
        "schema": SCHEMA,
        "input_sha256": digest(case),
        "width_cap": width_cap,
        "status": None,
        "steps": [],
        "eliminated_variables": 0,
        "maximum_realized_width": 0,
        "remaining_variables": [],
        "blocked_minimum_degree": None,
        "witness": None,
        "certificate_is_independently_replayable": True,
        "worst_case_time_claim": "O(poly(L)*2^(w+1)) for witnessed ordering width w",
        "all_graphs_polynomial_solver": False,
        "p_vs_np": "OPEN",
        "rowan_provider_calls": 0,
    }


def solve(case, width_cap=2):
    n, _ = validate(case)
    if type(width_cap) is not int or not 2 <= width_cap <= MAX_WIDTH:
        raise ValueError("WIDTH_CAP_OUT_OF_RESEARCH_BOUNDS")
    factors = _initial_factors(case)
    remaining = set(range(1,n+1))
    result = _new_result(case,width_cap)
    while remaining:
        if any(not f["rows"] for f in factors):
            result["status"] = "UNSAT"
            break
        variable, graph = _pick(remaining, factors)
        degree = len(graph[variable])
        if degree > width_cap:
            result["status"] = "OPEN_WIDTH_CAP"
            result["blocked_minimum_degree"] = degree
            break
        factors, step = _eliminate(factors,variable)
        result["steps"].append(step)
        result["maximum_realized_width"] = max(result["maximum_realized_width"],degree)
        remaining.remove(variable)
    result["eliminated_variables"] = len(result["steps"])
    result["remaining_variables"] = sorted(remaining)
    if result["status"] is None:
        if any(not f["rows"] for f in factors):
            result["status"] = "UNSAT"
        else:
            result["status"] = "SAT"
            witness={}
            for step in reversed(result["steps"]):
                row=tuple(witness[x] for x in step["scope"])
                idx=[tuple(r) for r in step["rows"]].index(row)
                witness[step["variable"]]=step["choices"][idx]
            if len(witness)!=n or any(
                sum(witness[abs(l)] ^ int(l<0) for l in c)!=1
                for c in case["clauses"]):
                raise AssertionError("BACKTRACK_WITNESS_INCORRECT")
            result["witness"]={str(x):witness[x] for x in sorted(witness)}
    result["result_sha256"]=digest(result)
    return result


def _oracle_projection(bucket,variable):
    """Verifier: independent exhaustive local table of <= w+1 variables.

    Intentionally does not call _eliminate or reuse solver's witness choices.
    """
    scope=sorted({x for f in bucket for x in f["scope"] if x!=variable})
    union=[variable]+scope
    options={}
    for full in itertools.product((0,1),repeat=len(union)):
        values=dict(zip(union,full))
        valid=True
        for fac in bucket:
            if tuple(values[v] for v in fac["scope"]) not in fac["rows"]:
                valid=False
                break
        if valid:
            key=tuple(values[v] for v in scope)
            options.setdefault(key,set()).add(values[variable])
    return scope, options


def verify(case,answer):
    try:
        n, clauses=validate(case)
        if not isinstance(answer,dict) or answer.get("schema")!=SCHEMA:
            return False
        x=dict(answer)
        h=x.pop("result_sha256",None)
        if h!=digest(x) or answer.get("input_sha256")!=digest(case):
            return False
        w=answer["width_cap"]
        if type(w) is not int or w<2 or w>MAX_WIDTH:
            return False
        if (answer["p_vs_np"]!="OPEN" or answer["all_graphs_polynomial_solver"] is not False
            or answer["rowan_provider_calls"]!=0
            or answer["certificate_is_independently_replayable"] is not True
            or answer["worst_case_time_claim"]!=_new_result(case,w)["worst_case_time_claim"]):
            return False
        factors=_initial_factors(case)
        remaining=set(range(1,n+1))
        max_width=0
        if not isinstance(answer["steps"],list) or len(answer["steps"])>n:
            return False
        for step in answer["steps"]:
            if any(not f["rows"] for f in factors) or not remaining:
                return False
            variable,graph=_pick(remaining,factors)
            d=len(graph[variable])
            if d>w or not isinstance(step,dict) or set(step)!={"variable","scope","rows","choices","bucket_size"}:
                return False
            if type(step["variable"]) is not int or step["variable"]!=variable:
                return False
            bucket=[f for f in factors if variable in f["scope"]]
            others=[f for f in factors if variable not in f["scope"]]
            scope,options=_oracle_projection(bucket,variable)
            if step["scope"]!=scope or step["bucket_size"]!=len(bucket):
                return False
            allowed=sorted(options)
            actual=[tuple(r) for r in step["rows"]]
            if actual!=allowed or len(step["choices"])!=len(actual):
                return False
            if any(type(b) is not int or b not in (0,1) or b not in options[r]
                   for r,b in zip(actual,step["choices"])):
                return False
            # Deterministic first witness is not necessary for mathematical
            # correctness, but makes the public packet byte-reproducible.
            if any(b!=min(options[r]) for r,b in zip(actual,step["choices"])):
                return False
            factors=others+[_factor(scope,actual)]
            max_width=max(max_width,d)
            remaining.remove(variable)
        if (answer["eliminated_variables"]!=len(answer["steps"])
            or answer["remaining_variables"]!=sorted(remaining)
            or answer["maximum_realized_width"]!=max_width):
            return False
        status=answer["status"]
        if any(not f["rows"] for f in factors):
            return (status=="UNSAT" and answer["blocked_minimum_degree"] is None
                    and answer["witness"] is None)
        if remaining:
            variable,graph=_pick(remaining,factors)
            return (status=="OPEN_WIDTH_CAP"
                    and answer["blocked_minimum_degree"]==len(graph[variable])
                    and len(graph[variable])>w and answer["witness"] is None)
        if status!="SAT" or answer["blocked_minimum_degree"] is not None:
            return False
        witness=answer["witness"]
        if (not isinstance(witness,dict)
            or set(witness)!={str(i) for i in range(1,n+1)}
            or any(type(b) is not int or b not in (0,1) for b in witness.values())):
            return False
        vals={int(k):v for k,v in witness.items()}
        if not all(sum(vals[abs(l)] ^ int(l<0) for l in c)==1 for c in clauses):
            return False
        for step in answer["steps"]:
            row=tuple(vals[x] for x in step["scope"])
            rows=[tuple(r) for r in step["rows"]]
            if row not in rows or vals[step["variable"]]!=step["choices"][rows.index(row)]:
                return False
        return True
    except (KeyError,ValueError,TypeError,OverflowError,AssertionError,IndexError):
        return False


def chain_family(n,unsat=False):
    """Arbitrarily many overlapping incidence 4-cycles, but primal width 2."""
    if type(n) is not int or n<4:
        raise ValueError("CHAIN_LENGTH")
    clauses=[[i,i+1,i+2] for i in range(1,n-1)]
    if unsat:
        clauses.append([-1,-2,-3])
    return {"n":n,"clauses":clauses}


def self_test():
    curated=[
        {"n":1,"clauses":[[1]]},
        {"n":1,"clauses":[[-1]]},
        {"n":2,"clauses":[]},
        {"n":3,"clauses":[[1,1,-2],[-1,2,3]]},
        {"n":3,"clauses":[[1],[ -1]]},
        {"n":4,"clauses":[[1,2,3],[2,3,4]]},
        {"n":7,"clauses":list([a,b,c] for a,b,c in itertools.combinations(range(1,8),3))},
    ]
    rng=random.Random(20261028)
    for _ in range(420):
        n=rng.randint(1,8)
        cs=[]
        for _ in range(rng.randint(0,10)):
            cs.append([ (v if rng.randrange(2) else -v)
                        for v in (rng.randint(1,n) for __ in range(rng.choice((1,3))))])
        curated.append({"n":n,"clauses":cs})
    counts={}
    for case in curated:
        answer=solve(case,width_cap=2)
        assert verify(case,answer),("REPLAY_INVALID",case,answer)
        actual=solution_set(case)
        if answer["status"]=="SAT":
            assert actual
            w={int(k):v for k,v in answer["witness"].items()}
            packed=sum(bit << (v-1) for v,bit in w.items())
            assert packed in actual
        elif answer["status"]=="UNSAT":
            assert not actual
        else:
            assert answer["status"]=="OPEN_WIDTH_CAP"
        counts[answer["status"]]=counts.get(answer["status"],0)+1
    long_sat=chain_family(83)
    long_unsat=chain_family(83,unsat=True)
    large=[]
    for case in (long_sat,long_unsat):
        answer=solve(case,width_cap=2)
        assert verify(case,answer)
        assert answer["maximum_realized_width"]<=2
        assert answer["eliminated_variables"]==83
        assert answer["status"]==("UNSAT" if case==long_unsat else "SAT")
        large.append(answer["status"])
    # 81 cubic constraints produce at least 80 distinct incidence 4-cycles.
    assert len(long_sat["clauses"])-1==80
    open_control=solve(curated[6],width_cap=2)
    assert open_control["status"]=="OPEN_WIDTH_CAP"
    assert verify(curated[6],open_control)
    false=json.loads(json.dumps(solve({"n":4,"clauses":[[1,2,3],[2,3,4]]})))
    first=false["steps"][0]
    first["rows"]=first["rows"][:-1]
    first["choices"]=first["choices"][:-1]
    false["result_sha256"]=digest({k:v for k,v in false.items() if k!="result_sha256"})
    assert not verify({"n":4,"clauses":[[1,2,3],[2,3,4]]},false)
    return {
        "schema":"janus.fundamentum.width_dp_test_receipt.v1",
        "status":"PASS",
        "small_reference_cases":len(curated),
        "small_test_statuses":counts,
        "large_sat_n":83,
        "large_sat_incidence_4cycles_lower_bound":80,
        "large_unsat_n":83,
        "large_test_statuses":large,
        "strong_open_width_gate":"PASS",
        "tampered_rehashed_projection":"REJECTED",
        "width_cap":2,
        "algorithmic_bound":"O(poly(L)*2^(w+1)) given witnessed elimination order",
        "universal_polynomial_sat_solver":False,
        "p_vs_np":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    arg=ap.add_mutually_exclusive_group(required=True)
    arg.add_argument("--self-test",action="store_true")
    arg.add_argument("--input",type=Path)
    ap.add_argument("--output",type=Path)
    ap.add_argument("--width-cap",type=int,default=2)
    args=ap.parse_args()
    if args.self_test:
        output=self_test()
    else:
        case=json.loads(args.input.read_text(encoding="utf-8"))
        output=solve(case,args.width_cap)
        if not verify(case,output):
            raise RuntimeError("INDEPENDENT_WIDTH_DP_CERTIFICATE_FAILED")
    s=json.dumps(output,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(s,encoding="utf-8")
    print(s)


if __name__=="__main__":
    main()
