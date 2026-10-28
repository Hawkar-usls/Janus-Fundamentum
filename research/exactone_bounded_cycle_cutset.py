#!/usr/bin/env python3
"""Exact-One solver for instances with <=2-variable incidence cycle cutset.

Complete SAT/UNSAT on the explicitly recognized class; NOT a universal
polynomial SAT algorithm. Every branch is certified by the existing
preprocessor + forest-DP verifier; UNSAT requires all 2**k branches.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from exactone_parity_preprocessor import validate, digest, solution_set
from exactone_forest_dp import run as forest_run, verify as forest_verify, factor_ok

SCHEMA="janus.fundamentum.exactone_cycle_cutset_2.v1"
MAX_CUTSET=2


def incidence_is_forest_after_variable_deletion(case, eliminated):
    n, clauses=validate(case)
    eliminated=set(eliminated)
    parent={}

    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]
            x=parent[x]
        return x

    def union(a,b):
        if a not in parent: parent[a]=a
        if b not in parent: parent[b]=b
        ra,rb=find(a),find(b)
        if ra==rb: return False
        parent[ra]=rb
        return True

    for ci,c in enumerate(clauses):
        factor=("c",ci)
        for var in {abs(l) for l in c} - eliminated:
            if not union(factor,("v",var)):
                return False
    return True


def find_cutset(case, max_size=MAX_CUTSET):
    validate(case)
    # Exhaustive candidate search is polynomial only with constant k<=2.
    if type(max_size) is not int or not 0<=max_size<=MAX_CUTSET:
        raise ValueError("UNBOUNDED_CUTSET_SEARCH_DENIED")
    used=sorted({abs(lit) for c in case["clauses"] for lit in c})
    for k in range(max_size+1):
        for chosen in itertools.combinations(used,k):
            if incidence_is_forest_after_variable_deletion(case,chosen):
                return chosen
    return None


def branch_case(case,variables,bits):
    return {"n":case["n"],"clauses":case["clauses"]+[
        [var if bit else -var] for var,bit in zip(variables,bits)]}


def solve(case):
    validate(case)
    direct=forest_run(case)
    if not forest_verify(case,direct):
        raise RuntimeError("FOREST_PRECHECK_FAILED")
    payload={
        "schema":SCHEMA,
        "source_sha256":digest(case),
        "status":None,
        "cycle_cutset_variables":None,
        "branches":[],
        "witness":None,
        "max_cutset_size":MAX_CUTSET,
        "proven_complete_for_recognized_class":False,
        "universal_polynomial_sat_solver":False,
        "p_vs_np":"OPEN",
        "rowan_provider_calls":0,
    }
    if direct["status"]!="OPEN_CYCLIC":
        payload["status"]="SOLVED_WITHOUT_CUTSET"
        payload["cycle_cutset_variables"]=[]
        payload["branches"]=[{"values":[],"certificate":direct}]
        payload["witness"]=direct["witness"]
        payload["proven_complete_for_recognized_class"]=True
    else:
        cutset=find_cutset(case)
        if cutset is None:
            payload["status"]="OPEN_NO_SMALL_CUTSET"
        else:
            payload["cycle_cutset_variables"]=list(cutset)
            # Every possible assignment to the cutset must be considered for UNSAT.
            for bits in itertools.product((0,1),repeat=len(cutset)):
                sub=branch_case(case,cutset,bits)
                certificate=forest_run(sub)
                if not forest_verify(sub,certificate):
                    raise RuntimeError("BRANCH_CERT_INVALID")
                if certificate["status"]=="OPEN_CYCLIC":
                    raise RuntimeError("CUTSET_TO_FOREST_CONTRACT_BROKEN")
                payload["branches"].append({
                    "values":list(bits),"certificate":certificate})
                if certificate["status"].startswith("SAT"):
                    payload["status"]="SAT_CUTSET"
                    payload["witness"]=certificate["witness"]
                    payload["proven_complete_for_recognized_class"]=True
                    break
            if payload["status"] is None:
                payload["status"]="UNSAT_CUTSET"
                payload["proven_complete_for_recognized_class"]=True
    payload["result_sha256"]=digest(payload)
    return payload


def verify(case,payload):
    """Polynomial independent validation of branch coverage and certificates."""
    try:
        validate(case)
        if not isinstance(payload,dict) or payload.get("schema")!=SCHEMA:
            return False
        tmp=dict(payload)
        h=tmp.pop("result_sha256",None)
        if (h!=digest(tmp) or payload.get("source_sha256")!=digest(case)
            or payload.get("p_vs_np")!="OPEN"
            or payload.get("universal_polynomial_sat_solver") is not False
            or payload.get("rowan_provider_calls")!=0
            or payload.get("max_cutset_size")!=MAX_CUTSET):
            return False
        status=payload["status"]
        cutset=payload["cycle_cutset_variables"]
        branches=payload["branches"]
        if status=="OPEN_NO_SMALL_CUTSET":
            return (cutset is None and branches==[] and payload["witness"] is None
                    and payload["proven_complete_for_recognized_class"] is False
                    and find_cutset(case) is None)
        if not isinstance(cutset,list) or len(cutset)>MAX_CUTSET or len(set(cutset))!=len(cutset):
            return False
        if not all(type(v) is int and 1<=v<=case["n"] for v in cutset):
            return False
        if status=="SOLVED_WITHOUT_CUTSET":
            # Preprocessing can solve a cyclic original graph before any
            # graph-class recognition. Its original, independent certificate
            # suffices; the raw graph need not itself be a forest.
            if (cutset!=[] or not isinstance(branches,list) or len(branches)!=1
                or not isinstance(branches[0],dict)
                or branches[0].get("values")!=[]):
                return False
            direct=branches[0].get("certificate")
            if not forest_verify(case,direct) or direct["status"]=="OPEN_CYCLIC":
                return False
            return (payload["proven_complete_for_recognized_class"] is True
                    and payload["witness"]==direct["witness"])
        if not incidence_is_forest_after_variable_deletion(case,cutset):
            return False
        if not isinstance(branches,list) or not branches:
            return False
        if payload["proven_complete_for_recognized_class"] is not True:
            return False
        if status=="SOLVED_WITHOUT_CUTSET" and (cutset!=[] or len(branches)!=1):
            return False
        patterns=list(itertools.product((0,1),repeat=len(cutset)))
        if len(branches)>len(patterns):
            return False
        seen_solution=False
        for index,item in enumerate(branches):
            if not isinstance(item,dict) or set(item)!={"values","certificate"}:
                return False
            if item["values"]!=list(patterns[index]):
                return False
            sub=branch_case(case,cutset,patterns[index])
            if not forest_verify(sub,item["certificate"]):
                return False
            if item["certificate"]["status"]=="OPEN_CYCLIC":
                return False
            is_sat=item["certificate"]["status"].startswith("SAT")
            if is_sat and index!=len(branches)-1:
                return False
            seen_solution |= is_sat
        if status in ("SAT_CUTSET","SOLVED_WITHOUT_CUTSET") and seen_solution:
            witness=payload["witness"]
            if not isinstance(witness,dict) or set(witness)!={str(i) for i in range(1,case["n"]+1)}:
                return False
            if any(type(bit) is not int or bit not in (0,1) for bit in witness.values()):
                return False
            if not all(factor_ok(c,{int(k):v for k,v in witness.items()}) for c in case["clauses"]):
                return False
            return witness==branches[-1]["certificate"]["witness"]
        if status in ("UNSAT_CUTSET","SOLVED_WITHOUT_CUTSET") and not seen_solution:
            return len(branches)==len(patterns) and payload["witness"] is None
        return False
    except (ValueError,KeyError,TypeError,AssertionError,OverflowError):
        return False


def self_test():
    rng=random.Random(20261028)
    cases=[
        {"n":4,"clauses":[[1,2,3],[2,3,4]]},
        {"n":5,"clauses":[[1,2,3],[2,3,4],[3,4,5]]},
        {"n":5,"clauses":[[1,2,3],[2,3,4],[3,4,5],[1],[-5]]},
        {"n":6,"clauses":[[1,2,3],[2,3,4],[4,5,6],[1,6,2]]},
        {"n":3,"clauses":[[1],[1,2,3]]},
    ]
    for i in range(135):
        n=rng.randint(3,9)
        m=rng.randint(1,9)
        cs=[]
        for _ in range(m):
            vals=[rng.choice(range(1,n+1)) for _ in range(3)]
            cs.append([v if rng.randrange(2) else -v for v in vals])
        cases.append({"n":n,"clauses":cs})
    statuses={}
    for case in cases:
        answer=solve(case)
        assert verify(case,answer),("CYCLE_CUTSET_CERT_INVALID",case,answer)
        ref=solution_set(case)
        if answer["status"].startswith("SAT") or (
            answer["status"]=="SOLVED_WITHOUT_CUTSET" and answer["witness"] is not None):
            assert ref
        elif answer["status"].startswith("UNSAT") or (
            answer["status"]=="SOLVED_WITHOUT_CUTSET" and answer["witness"] is None):
            assert not ref
        else:
            assert answer["status"]=="OPEN_NO_SMALL_CUTSET"
        statuses[answer["status"]]=statuses.get(answer["status"],0)+1
    # Example cyclic input actually handled by deleting one variable.
    ex=solve(cases[0])
    assert ex["status"]=="SAT_CUTSET"
    assert len(ex["cycle_cutset_variables"])==1
    # Detect forged witness even after recomputing top-level SHA.
    forgery=json.loads(json.dumps(ex))
    v=next(iter(forgery["witness"]))
    forgery["witness"][v]=1-forgery["witness"][v]
    forgery.pop("result_sha256")
    forgery["result_sha256"]=digest(forgery)
    assert not verify(cases[0],forgery)
    return {"schema":"janus.fundamentum.cycle_cutset_2_self_test.v1",
            "status":"PASS","cases":len(cases),"statuses":statuses,
            "cyclic_example_cutset_size":len(ex["cycle_cutset_variables"]),
            "adversarial_witness_test":"REJECTED",
            "complexity_bound_fixed_k":"O(L^7) conservative for k<=2",
            "p_vs_np":"OPEN"}


def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test",action="store_true")
    g.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.self_test:
        out=self_test()
    else:
        case=json.loads(a.input.read_text(encoding="utf-8"))
        out=solve(case)
        if not verify(case,out):
            raise RuntimeError("CUTSET_CERTIFICATE_INVALID")
    payload=json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.output:a.output.write_text(payload,encoding="utf-8")
    print(payload)


if __name__=="__main__":
    main()
