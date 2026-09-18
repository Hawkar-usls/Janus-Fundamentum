#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

# Variables are represented by positive integers; sign encodes literal polarity.
# Internal vars: 1..n_internal.
# Boundary vars: n_internal+1 .. n_internal+n_boundary.
# Clauses are normalized: no repeated variable and no complementary literal pair.

def lit_value(lit:int, assignment:dict[int,bool]) -> bool:
    v=assignment[abs(lit)]
    return v if lit>0 else (not v)

def clause_value(clause, assignment):
    return any(lit_value(l,assignment) for l in clause)

def formula_value(clauses, assignment):
    return all(clause_value(c,assignment) for c in clauses)

def internal_projection(clause, internal_vars:set[int]):
    return tuple(l for l in clause if abs(l) in internal_vars)

def internal_cover_sat(clauses, n_internal):
    ivars=set(range(1,n_internal+1))
    for bits in itertools.product([False,True], repeat=n_internal):
        a={i+1:bits[i] for i in range(n_internal)}
        ok=True
        for c in clauses:
            proj=internal_projection(c,ivars)
            if not proj or not any(lit_value(l,a) for l in proj):
                ok=False; break
        if ok:
            return True,bits
    return False,None

def residual_truth_table(clauses,n_internal,n_boundary,alpha_bits):
    a={i+1:alpha_bits[i] for i in range(n_internal)}
    out={}
    for bbits in itertools.product([False,True], repeat=n_boundary):
        full=dict(a)
        for j,b in enumerate(bbits):
            full[n_internal+1+j]=b
        out[bbits]=formula_value(clauses,full)
    return out

def universal_branches(clauses,n_internal,n_boundary):
    out=[]
    for alpha in itertools.product([False,True], repeat=n_internal):
        tt=residual_truth_table(clauses,n_internal,n_boundary,alpha)
        if all(tt.values()):
            out.append(alpha)
    return out

def existential_relation(clauses,n_internal,n_boundary):
    out={}
    for bbits in itertools.product([False,True],repeat=n_boundary):
        sat=False
        for alpha in itertools.product([False,True],repeat=n_internal):
            full={i+1:alpha[i] for i in range(n_internal)}
            for j,b in enumerate(bbits):
                full[n_internal+1+j]=b
            if formula_value(clauses,full):
                sat=True; break
        out[bbits]=sat
    return out

def kappa_exact(clauses,n_internal,n_boundary):
    alphas=list(itertools.product([False,True],repeat=n_internal))
    tables={a:residual_truth_table(clauses,n_internal,n_boundary,a) for a in alphas}
    target=list(itertools.product([False,True],repeat=n_boundary))
    # If the full existential relation is not TRUE, define kappa=INFINITY.
    rel=existential_relation(clauses,n_internal,n_boundary)
    if not all(rel.values()):
        return None
    for k in range(1,len(alphas)+1):
        for subset in itertools.combinations(alphas,k):
            if all(any(tables[a][b] for a in subset) for b in target):
                return k
    raise AssertionError("finite TRUE relation must have a finite cover")

def verify_instance(clauses,n_internal,n_boundary):
    cover,witness=internal_cover_sat(clauses,n_internal)
    ub=universal_branches(clauses,n_internal,n_boundary)
    kappa=kappa_exact(clauses,n_internal,n_boundary)
    equivalence=(cover == bool(ub) == (kappa==1))
    return {
        "internal_cover_sat":cover,
        "internal_cover_witness":witness,
        "universal_branches":ub,
        "kappa_C":"INFINITY" if kappa is None else kappa,
        "R_C_truth_table":existential_relation(clauses,n_internal,n_boundary),
        "lemma_equivalence":equivalence
    }

def normalized_clauses(n_internal=2,n_boundary=2,max_width=3):
    n=n_internal+n_boundary
    vars_=list(range(1,n+1))
    clauses=[]
    for width in range(1,max_width+1):
        for subset in itertools.combinations(vars_,width):
            for signs in itertools.product([1,-1],repeat=width):
                clauses.append(tuple(v*s for v,s in zip(subset,signs)))
    return clauses

def exhaustive_small_model_sweep():
    atoms=normalized_clauses()
    checked=0
    failures=[]
    # Every normalized formula with 1, 2, or 3 DISTINCT clauses.
    for k in (1,2,3):
        for formula in itertools.combinations(atoms,k):
            checked+=1
            r=verify_instance(formula,2,2)
            if not r["lemma_equivalence"]:
                failures.append({"formula":formula,"result":r})
                break
        if failures:
            break
    return checked,failures

def named_controls():
    # n_internal=1, n_boundary=1 (boundary variable id=2)
    controls={
      "UNIVERSAL_BRANCH_SHIELDING":[(1,2),(1,-2)],
      "DISTRIBUTED_SHIELDING":[(1,2),(-1,-2)],
      "SEMANTIC_SIGNAL":[(1,2),(-1,2)],
      "TRIVIAL_FALSE":[(1,),(-1,)]
    }
    out={}
    for name,formula in controls.items():
        out[name]=verify_instance(formula,1,1)
    assert out["UNIVERSAL_BRANCH_SHIELDING"]["internal_cover_sat"] is True
    assert out["UNIVERSAL_BRANCH_SHIELDING"]["kappa_C"]==1
    assert out["DISTRIBUTED_SHIELDING"]["internal_cover_sat"] is False
    assert out["DISTRIBUTED_SHIELDING"]["kappa_C"]==2
    assert all(out["DISTRIBUTED_SHIELDING"]["R_C_truth_table"].values())
    assert out["SEMANTIC_SIGNAL"]["internal_cover_sat"] is False
    assert out["SEMANTIC_SIGNAL"]["kappa_C"]=="INFINITY"
    assert set(out["SEMANTIC_SIGNAL"]["R_C_truth_table"].values())=={False,True}
    assert out["TRIVIAL_FALSE"]["internal_cover_sat"] is False
    assert out["TRIVIAL_FALSE"]["kappa_C"]=="INFINITY"
    assert not any(out["TRIVIAL_FALSE"]["R_C_truth_table"].values())
    return out

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),default=list).encode()).hexdigest()

def main():
    checked,failures=exhaustive_small_model_sweep()
    controls=named_controls()
    result={
      "artifact_id":"JANUS-TRUMP-WALL-MANTEQUILLA-UNIVERSAL-BRANCH-SHIELDING-LEMMA-INDEPENDENT-CHECK-v1",
      "verdict":"PASS_INDEPENDENT_UNIVERSAL_BRANCH_SHIELDING_LEMMA_CHECK" if not failures else "FAIL_INDEPENDENT_UNIVERSAL_BRANCH_SHIELDING_LEMMA_CHECK",
      "general_claim_review":{
        "proof_dependency":"definition-level CNF reasoning; dataset-independent",
        "formal_proof_assistant_used":False,
        "checker_role":"independent executable validation and exact finite-instance decision procedure, not a proof-assistant certificate"
      },
      "exhaustive_small_model_sweep":{
        "n_internal":2,"n_boundary":2,"max_clause_width":3,
        "normalized_clause_count":len(normalized_clauses()),
        "formula_clause_counts":[1,2,3],
        "formulae_checked":checked,
        "failures":failures
      },
      "named_controls":controls,
      "checks":{
        "all_exhaustive_cases_satisfy_equivalence":not failures,
        "distributed_shielding_nonconverse_witness_verified":controls["DISTRIBUTED_SHIELDING"]["internal_cover_sat"] is False and controls["DISTRIBUTED_SHIELDING"]["kappa_C"]==2 and all(controls["DISTRIBUTED_SHIELDING"]["R_C_truth_table"].values()),
        "semantic_signal_control_verified":set(controls["SEMANTIC_SIGNAL"]["R_C_truth_table"].values())=={False,True},
        "universal_branch_control_verified":controls["UNIVERSAL_BRANCH_SHIELDING"]["kappa_C"]==1
      }
    }
    result["independent_semantic_digest_sha256"]=canonical_sha(result)
    if len(sys.argv)>1:
        Path(sys.argv[1]).write_text(json.dumps(result,indent=2,sort_keys=True,default=list)+"\n",encoding="utf-8")
    print(json.dumps({
      "verdict":result["verdict"],
      "formulae_checked":checked,
      "digest":result["independent_semantic_digest_sha256"]
    },sort_keys=True))
    if failures:
        raise SystemExit(1)

if __name__=="__main__":
    main()
