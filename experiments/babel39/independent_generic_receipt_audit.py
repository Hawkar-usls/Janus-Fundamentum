#!/usr/bin/env python3
"""Independent BABEL39 proof audit: exhaustive Boolean DPLL vs Q tables.

Rebuilds each local SCL boundary relation using an independent unit-forcing
Boolean recursion (not the producer's Fraction elimination); independently
counts all Cartesian component states on small joined structures; checks the
actual emitted 2-CNF relation exhaustively; rejects semantically invalid
restoration metadata. This is a research-only finite verifier.
"""
import itertools
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from experiments.babel37.fourport_majority_falsifier import (
    U,PORTS,macros,independent_three_state_count,R4
)
from experiments.babel39.generic_scl_component_compiler import (
    affine9,complete_local_table,valid_square,join_certificate,solve,
    add_local_exact_2cnf,majority_relation
)
from experiments.babel36.u_macro_2sat_solver import Exact2SAT


def full_boolean_exact_one(rows,n):
    solutions=[]
    def dfs(known,true):
        while True:
            changed=False
            for clause in rows:
                selected=sum(true>>j&1 for j in clause)
                free=[j for j in clause if not(known>>j&1)]
                if selected>1 or selected+len(free)<1:return
                if selected==1 and free:
                    for j in free:known|=1<<j
                    changed=True
                elif selected==0 and len(free)==1:
                    v=free[0];known|=1<<v;true|=1<<v
                    changed=True
            if not changed:break
        if known==(1<<n)-1:
            assert all(sum(true>>j&1 for j in r)==1 for r in rows)
            solutions.append(true);return
        v=next(j for j in range(n) if not(known>>j&1))
        dfs(known|(1<<v),true)
        dfs(known|(1<<v),true|(1<<v))
    dfs(0,0)
    assert len(solutions)==len(set(solutions))
    return solutions


def independent_table(comp):
    rows=comp["rows"];ports=comp["ports"]
    kept=[r for i,r in enumerate(rows) if i not in {r for r,v in ports}]
    models=full_boolean_exact_one(kept,len(rows))
    relation=Counter()
    witnesses={}
    for x in models:
        a=tuple((x>>v)&1 for r,v in ports)
        b=tuple(1-sum(x>>j&1 for j in rows[r] if j!=v)
                for r,v in ports)
        if any(bit not in (0,1) for bit in b):continue
        key=a+b
        relation[key]+=1
        witnesses.setdefault(key,x)
        assert sum(a)-sum(b)==3*x.bit_count()-len(rows)
    return relation,witnesses,len(models)


def audit_local(comp):
    fromq=complete_local_table(comp)
    assert fromq["status"]=="COMPLETE"
    dpll,witnesses,total=independent_table(comp)
    assert len(dpll)==len(fromq["entries"])
    assert total==fromq["all_punctured_boolean_models"]
    assert {k:v["multiplicity"] for k,v in fromq["entries"].items()}==dpll
    for key,meta in fromq["entries"].items():
        # Multiple witnesses for a signature are allowed; accept any
        # EXACT physical local representative returned by the Q procedure.
        witness=meta["witness"]
        assert tuple((witness>>v)&1 for r,v in comp["ports"])==key[:len(comp["ports"])]
        assert all(sum(witness>>j&1 for j in row)==1 for i,row in enumerate(comp["rows"])
                   if i not in {r for r,v in comp["ports"]})
    return {"n":len(comp["rows"]),"ports":len(comp["ports"]),
            "Q_nullity":fromq["k"],
            "all_complete_DPLL_partial_models":total,
            "admissible_boundary_signature_counts":len(dpll),
            "independent_membership_and_multiplicity":"PASS"}


def check_direct_relation(comp,prune):
    table=complete_local_table(comp)
    relations={k for k in table["entries"]}
    if prune:
        relations={key for key in relations if table["entries"][key]["delta"]==0}
    # Finite independent ternary majority audit (small frozen controls ONLY).
    maj,invalid=majority_relation(relations)
    sat=Exact2SAT()
    coords=[sat.fresh() for _ in range(2*len(comp["ports"]))]
    ok,witness=add_local_exact_2cnf(sat,coords,relations)
    assert ok==maj
    if ok:
        assert witness["all_truth_tuples_checked"]==1<<(2*len(comp["ports"]))
    else:
        assert witness["failure"]=="EXACT_2CNF_NOT_EQUIVALENT"
    return {"majority_closed":maj,
            "compiler_accepts_exact_2CNF":ok,
            "explicit_failure_checked":not ok}


def main():
    from experiments.babel35.bipartite_macro_compression import PORTS as P3
    components=[
       {"rows":U,"ports":PORTS},
       {"rows":U,"ports":P3},
       {"rows":U,"ports":((0,0),)},
       {"rows":affine9(),"ports":((0,0),)}
    ]
    assert all(valid_square(c["rows"]) for c in components)
    audits=[audit_local(c) for c in components]
    raw_R4=check_direct_relation(components[0],False)
    pruned_R4=check_direct_relation(components[0],True)
    assert not raw_R4["majority_closed"]
    assert pruned_R4["majority_closed"]
    assert check_direct_relation(components[1],False)["majority_closed"]

    # Full independent global count from local tables for DIFFERENT SCL
    # components: U27 + affine9, not copied template rows.
    joined_cert={"components":[components[2],components[3]],
                 "edges":[(0,0,1,0)]}
    raw,_=join_certificate(joined_cert["components"],joined_cert["edges"])
    solved=solve(raw,joined_cert)
    assert solved["status"]=="SAT"
    counts=[]
    a,_,_=independent_table(components[2])
    b,_,_=independent_table(components[3])
    for left,number_left in a.items():
        for right,number_right in b.items():
            if left[0]==right[1] and right[0]==left[1]:
                counts.append(number_left*number_right)
    assert sum(counts)==2
    assert all(sum(solved["physical_witness"]>>v&1 for v in row)==1 for row in raw)

    # Independent completely exhaustive 3^5 original macro network cert,
    # check exact generic compiler UNSAT agrees with raw local assignment CSP.
    n,edges,adj,slots=macros("K5")
    c={"components":[{"rows":U,"ports":PORTS} for _ in range(n)],
       "edges":[(u,slots[(u,v)],v,slots[(v,u)]) for u,v in edges]}
    original,_=join_certificate(c["components"],c["edges"])
    status=solve(original,c)
    assert status["status"]=="UNSAT"
    dpll_R4,_,_=independent_table({"rows":U,"ports":PORTS})
    assert len(dpll_R4)==3
    choices=list(dpll_R4)
    valid=[]
    for states in itertools.product(choices,repeat=5):
        if all(states[u][slots[(u,v)]]==states[v][4+slots[(v,u)]] and
               states[v][slots[(v,u)]]==states[u][4+slots[(u,v)]]
               for u,v in edges):
            valid.append(states)
    assert len(valid)==0
    # Tampered original row must never be accepted as a valid certificate.
    broken=list(raw)
    row=list(broken[0]);row[0]=row[1];broken[0]=tuple(row)
    try:
        solve(broken,joined_cert)
    except AssertionError:
        rejected=True
    else:rejected=False
    assert rejected
    print(json.dumps({
      "gate":"BABEL39_INDEPENDENT_Q_VS_DPLL_AND_TRUE_2CNF_AUDIT",
      "independent_local_boolean_censuses":audits,
      "R4_unpruned_2CNF_rejected":raw_R4,
      "R4_sound_global_flux_pruning_makes_2CNF":pruned_R4,
      "independent_mixed_nonU_joined_model_count":2,
      "independent_connected_unsat_K5_3state_oracle":0,
      "untrusted_incorrect_original_certificate_rejected":True,
      "full_physical_witness_verified":True,
      "arbitrary_SCL_auto_partition":"OPEN",
      "P_vs_NP":"OPEN"
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
