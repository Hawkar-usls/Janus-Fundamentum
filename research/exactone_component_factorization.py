#!/usr/bin/env python3
"""Exact-One component product + independent bounded-affine-local certificates.

Handles unbounded GLOBAL primal width and XOR nullity when each incidence
component admits a small affine nullity, by factorization of SAT over disjoint
variable sets. Explicitly does NOT solve connected high-width/high-nullity
irreducible instances. AIFC supplies evidence-grade/canonicalization tests in
the cross-repository workflow, not mathematical proof authority.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from exactone_parity_preprocessor import validate, digest, solution_set
from exactone_affine_nullity import solve as affine_solve, verify as affine_verify
from exactone_affine_nullity import full_pair_fan, MAX_FREE_DIMENSION

SCHEMA="janus.fundamentum.exactone_component_product_v1"


def decompose(case):
    """Canonical original-incidence components; no assertion-based partition."""
    n, clauses=validate(case)
    parent=list(range(n+1))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]]
            i=parent[i]
        return i
    def unite(a,b):
        a,b=root(a),root(b)
        if a!=b: parent[max(a,b)]=min(a,b)
    for clause in clauses:
        vs=sorted({abs(l) for l in clause})
        for v in vs[1:]:
            unite(vs[0],v)
    groups={}
    for v in range(1,n+1):
        groups.setdefault(root(v),[]).append(v)
    components=[]
    for variables in sorted(groups.values(),key=lambda v:v[0]):
        old_to_new={v:i+1 for i,v in enumerate(variables)}
        local_clauses=[
            [(1 if lit>0 else -1)*old_to_new[abs(lit)] for lit in clause]
            for clause in clauses if root(abs(clause[0]))==root(variables[0])
        ]
        components.append({
            "variables":variables,
            "input":{"n":len(variables),"clauses":local_clauses}
        })
    return components


def _template(case,cap):
    return {
        "schema":SCHEMA,"source_sha256":digest(case),
        "local_nullity_cap":cap,
        "status":None,
        "number_of_original_variables":case["n"],
        "number_of_components":None,
        "records":[],
        "witness":None,
        "composition":"EXACT_CONJUNCTION_OF_DISJOINT_VARIABLE_COMPONENTS",
        "complexity_claim":"O(poly(L)+sum_i 2^(k_i)*poly(L_i))",
        "certificate_claim":"O(poly(L)+sum_i 2^(k_i)*poly(L_i))",
        "general_connected_high_width_solver":False,
        "p_vs_np":"OPEN",
        "provider_calls":0,
    }


def solve(case,local_nullity_cap=3):
    validate(case)
    if (type(local_nullity_cap) is not int or not 0<=local_nullity_cap<=MAX_FREE_DIMENSION):
        raise ValueError("INVALID_LOCAL_NULLITY_CAP")
    components=decompose(case)
    output=_template(case,local_nullity_cap)
    output["number_of_components"]=len(components)
    all_witness={}
    pending=False
    for i,component in enumerate(components):
        local=affine_solve(component["input"],local_nullity_cap)
        if not affine_verify(component["input"],local):
            raise AssertionError("LOCAL_CERTIFICATE_FAIL")
        record={
            "component_index":i,
            "variables":component["variables"],
            "local_input_sha256":digest(component["input"]),
            "local_certificate":local,
        }
        output["records"].append(record)
        if local["status"].startswith("UNSAT"):
            output["status"]="UNSAT_COMPONENT"
            break
        if local["status"]=="OPEN_NULLITY_CAP":
            pending=True
        else:
            assert local["status"]=="SAT"
            for li,v in enumerate(component["variables"],start=1):
                assert v not in all_witness
                all_witness[v]=local["witness"][str(li)]
    if output["status"] is None:
        if pending:
            output["status"]="OPEN_COMPONENT_CAP"
        else:
            output["status"]="SAT_COMPONENTS"
            if len(all_witness)!=case["n"]:
                raise AssertionError("INCOMPLETE_COMPONENT_WITNESS")
            output["witness"]={str(v):b for v,b in sorted(all_witness.items())}
    output["result_sha256"]=digest(output)
    return output


def verify(case,receipt):
    """Recompute the exact partition and verify all local original certificates."""
    try:
        n,clauses=validate(case)
        if not isinstance(receipt,dict) or receipt.get("schema")!=SCHEMA:
            return False
        signed=dict(receipt)
        claimed=signed.pop("result_sha256",None)
        cap=receipt.get("local_nullity_cap")
        if type(cap) is not int or not 0<=cap<=MAX_FREE_DIMENSION:
            return False
        if claimed!=digest(signed) or receipt.get("source_sha256")!=digest(case):
            return False
        template=_template(case,cap)
        if any(receipt.get(k)!=template[k] for k in (
            "composition","complexity_claim","certificate_claim",
            "general_connected_high_width_solver","p_vs_np","provider_calls",
            "number_of_original_variables")):
            return False
        components=decompose(case)
        if receipt.get("number_of_components")!=len(components):
            return False
        records=receipt.get("records")
        if not isinstance(records,list) or not (1<=len(records)<=len(components)):
            return False
        all_witness={}
        any_open=False
        first_unsat=None
        for i,record in enumerate(records):
            if not isinstance(record,dict) or set(record)!={
                "component_index","variables","local_input_sha256","local_certificate"
            }:
                return False
            component=components[i]
            if (type(record["component_index"]) is not int
                or record["component_index"]!=i
                or record["variables"]!=component["variables"]
                or record["local_input_sha256"]!=digest(component["input"])):
                return False
            local=record["local_certificate"]
            if not affine_verify(component["input"],local):
                return False
            status=local["status"]
            if status.startswith("UNSAT"):
                first_unsat=i
                break
            if status=="OPEN_NULLITY_CAP":
                any_open=True
            elif status=="SAT":
                for li,v in enumerate(component["variables"],start=1):
                    all_witness[v]=local["witness"][str(li)]
            else:
                return False
        if first_unsat is not None:
            return (receipt["status"]=="UNSAT_COMPONENT"
                    and len(records)==first_unsat+1
                    and receipt["witness"] is None)
        if len(records)!=len(components):
            return False
        if any_open:
            return receipt["status"]=="OPEN_COMPONENT_CAP" and receipt["witness"] is None
        if receipt["status"]!="SAT_COMPONENTS" or len(all_witness)!=n:
            return False
        witness={str(v):b for v,b in sorted(all_witness.items())}
        if receipt["witness"]!=witness:
            return False
        return all(sum(all_witness[abs(l)] ^ int(l<0) for l in c)==1
                   for c in clauses)
    except (KeyError,ValueError,TypeError,OverflowError,IndexError,AssertionError):
        return False


def high_width_high_nullity(blocks=16,leaves=16,unsat=False):
    """Both parameters grow without bound but factors split exactly."""
    if type(blocks) is not int or type(leaves) is not int or blocks<2 or leaves<4:
        raise ValueError("INVALID_FAMILY_PARAMETERS")
    clauses=[]
    for b in range(blocks):
        local=full_pair_fan(leaves,unsat=bool(unsat and b==blocks-1))
        offset=b*(leaves+1)
        clauses.extend([[(1 if lit>0 else -1)*(abs(lit)+offset) for lit in c]
                        for c in local["clauses"]])
    return {"n":blocks*(leaves+1),"clauses":clauses}


def self_test():
    controls=[
        {"n":1,"clauses":[[1]]},
        {"n":1,"clauses":[]},
        {"n":4,"clauses":[[1,2,3],[4]]},
        {"n":4,"clauses":[[1],[2],[-1,3,4]]},
        {"n":6,"clauses":[[1,2,3],[4,5,6]]},
        {"n":6,"clauses":[[1,1,2],[3,4,5],[6]]},
    ]
    rng=random.Random(20261028)
    for _ in range(300):
        n=rng.randint(1,9)
        clauses=[]
        for __ in range(rng.randint(0,12)):
            vs=[rng.randint(1,n) for _ in range(rng.choice((1,3)))]
            clauses.append([v if rng.randrange(2) else -v for v in vs])
        controls.append({"n":n,"clauses":clauses})
    statuses={}
    for c in controls:
        result=solve(c,local_nullity_cap=3)
        assert verify(c,result),("INVALID_COMPONENT_CERT",c,result)
        ref=solution_set(c)
        if result["status"]=="SAT_COMPONENTS":
            assert ref
            bits=sum(b<<(int(v)-1) for v,b in result["witness"].items())
            assert bits in ref
        elif result["status"]=="UNSAT_COMPONENT":
            assert not ref
        else:
            assert result["status"]=="OPEN_COMPONENT_CAP"
        statuses[result["status"]]=statuses.get(result["status"],0)+1
    high=high_width_high_nullity(16,16,False)
    high_unsat=high_width_high_nullity(16,16,True)
    assert high["n"]==272 and len(high["clauses"])==1920
    assert len(decompose(high))==16
    yes=solve(high,local_nullity_cap=3)
    no=solve(high_unsat,local_nullity_cap=3)
    assert yes["status"]=="SAT_COMPONENTS" and verify(high,yes)
    assert no["status"]=="UNSAT_COMPONENT" and verify(high_unsat,no)
    assert len(yes["records"])==16
    assert all(r["local_certificate"]["nullity"]==1 for r in yes["records"])
    assert len(no["records"])==16 and no["records"][-1]["local_certificate"]["nullity"]==0
    # Each component induces a clique K17 (treewidth 16); independent
    # local free parameters yield global GF(2) nullity 16.
    assert len(high["clauses"])==16*16*15//2
    open_case={"n":12,"clauses":[]}
    pending=solve(open_case,local_nullity_cap=0)
    assert pending["status"]=="OPEN_COMPONENT_CAP" and verify(open_case,pending)
    forged=json.loads(json.dumps(yes))
    forged["records"][0]["variables"][0]=999
    forged["result_sha256"]=digest({k:v for k,v in forged.items() if k!="result_sha256"})
    assert not verify(high,forged)
    return {
        "schema":"janus.fundamentum.exactone_component_factorization_test_v1",
        "status":"PASS",
        "small_independent_reference_cases":len(controls),
        "small_classification_counts":statuses,
        "high_width_high_nullity_family":{
            "variables":272,"components":16,"primal_treewidth_lower_bound":16,
            "global_xor_nullity":16,
            "total_cubic_clauses":1920,
            "sat":"PASS","unsat":"PASS",
            "local_affine_nullity_per_sat_component":1,
            "global_2_to_k_enumeration_performed":False,
            "composed_sat_witness_verified_against_all_clauses":True
        },
        "tampered_rehashed_component":"REJECTED",
        "large_local_nullity_fail_closed":"PASS",
        "generic_connected_high_high_solved":False,
        "complexity":"O(poly(L)+sum_i 2^k_i*poly(L_i))",
        "p_vs_np":"OPEN",
    }


def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--self-test",action="store_true")
    g.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--local-nullity-cap",type=int,default=3)
    args=p.parse_args()
    if args.self_test:
        result=self_test()
    else:
        case=json.loads(args.input.read_text(encoding="utf-8"))
        result=solve(case,args.local_nullity_cap)
        if not verify(case,result):
            raise RuntimeError("INDEPENDENT_COMPONENT_CERTIFICATE_REJECTED")
    s=json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        args.output.write_text(s,encoding="utf-8")
    print(s)


if __name__=="__main__":
    main()
