#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

def lit_value(lit:int, assignment:dict[int,bool]) -> bool:
    v=assignment[abs(lit)]
    return v if lit>0 else (not v)

def clause_value(clause, assignment):
    return any(lit_value(l,assignment) for l in clause)

def formula_value(clauses, assignment):
    return all(clause_value(c,assignment) for c in clauses)

def boundary_projection_tautology(clause, boundary_vars:set[int]) -> bool:
    lits={l for l in clause if abs(l) in boundary_vars}
    return any(-l in lits for l in lits)

def internal_projection(clause, internal_vars:set[int]):
    return tuple(l for l in clause if abs(l) in internal_vars)

def naive_internal_cover_sat(clauses, internal_vars):
    iv=sorted(internal_vars)
    for bits in itertools.product([False,True], repeat=len(iv)):
        a=dict(zip(iv,bits))
        ok=True
        for c in clauses:
            proj=internal_projection(c,internal_vars)
            if not proj or not any(lit_value(l,a) for l in proj):
                ok=False
                break
        if ok:
            return True,a
    return False,None

def tautology_safe_internal_cover_sat(clauses, internal_vars, boundary_vars):
    iv=sorted(internal_vars)
    for bits in itertools.product([False,True], repeat=len(iv)):
        a=dict(zip(iv,bits))
        ok=True
        for c in clauses:
            if boundary_projection_tautology(c,boundary_vars):
                continue
            proj=internal_projection(c,internal_vars)
            if not proj or not any(lit_value(l,a) for l in proj):
                ok=False
                break
        if ok:
            return True,a
    return False,None

def verify_internal_cover_witness(clauses, internal_vars, boundary_vars, alpha):
    checked=0
    for c in clauses:
        checked += len(c)
        if boundary_projection_tautology(c,boundary_vars):
            continue
        proj=internal_projection(c,internal_vars)
        if not proj or not any(lit_value(l,alpha) for l in proj):
            return False,checked
    return True,checked

def domain_truth_table(clauses, internal_vars, boundary_vars):
    iv=sorted(internal_vars); bv=sorted(boundary_vars)
    out={}
    for bbits in itertools.product([False,True], repeat=len(bv)):
        b=dict(zip(bv,bbits))
        sat=False
        for ibits in itertools.product([False,True], repeat=len(iv)):
            a=dict(b); a.update(dict(zip(iv,ibits)))
            if formula_value(clauses,a):
                sat=True; break
        out["".join("1" if x else "0" for x in bbits)]=sat
    return out

def constant_witness_valid_on_domain(clauses, internal_vars, boundary_vars, alpha, domain):
    bv=sorted(boundary_vars)
    for bbits in itertools.product([False,True],repeat=len(bv)):
        key="".join("1" if x else "0" for x in bbits)
        if not domain[key]:
            continue
        a=dict(zip(bv,bbits)); a.update(alpha)
        if not formula_value(clauses,a):
            return False
    return True

def verify_constant_leaf_under_path(clauses, internal_vars, boundary_vars, alpha, path_assignment):
    # Proof obligation: every clause must be TRUE for every completion of boundary vars
    # consistent with the path, without any generic SAT/tautology oracle.
    unresolved=sorted(boundary_vars-set(path_assignment))
    inspections=0
    for c in clauses:
        inspections += len(c)
        # Clause already forced true by a path-fixed boundary literal?
        forced=False
        for l in c:
            if abs(l) in path_assignment and lit_value(l,path_assignment):
                forced=True; break
        if forced:
            continue
        # Or by the constant internal assignment?
        internal=internal_projection(c,internal_vars)
        if internal and any(lit_value(l,alpha) for l in internal):
            continue
        # Otherwise residual boundary literals over unresolved vars must be
        # syntactically tautological; this is local, not a generic DAG tautology test.
        residual={l for l in c if abs(l) in unresolved}
        if any(-l in residual for l in residual):
            continue
        return False,inspections
    return True,inspections

def eval_guarded_tree(node, boundary_assignment, path=None):
    if path is None: path={}
    if node["type"]=="CONST_LEAF":
        return node["alpha"],path
    assert node["type"]=="GUARDED_ITE"
    var=node["guard_var"]
    branch=bool(boundary_assignment[var])
    newpath=dict(path); newpath[var]=branch
    return eval_guarded_tree(node["true"] if branch else node["false"], boundary_assignment,newpath)

def verify_guarded_tree(clauses, internal_vars, boundary_vars, node, path=None, seen=None):
    if path is None: path={}
    if seen is None: seen=set()
    node_key=json.dumps(node,sort_keys=True)
    seen.add(node_key)
    if node["type"]=="CONST_LEAF":
        ok,inspections=verify_constant_leaf_under_path(
            clauses,internal_vars,boundary_vars,
            {int(k):bool(v) for k,v in node["alpha"].items()},
            path
        )
        return ok,inspections,seen
    if node["type"]!="GUARDED_ITE":
        return False,0,seen
    var=int(node["guard_var"])
    if var not in boundary_vars:
        return False,0,seen
    if var in path:
        return False,0,seen
    total=0
    p1=dict(path); p1[var]=True
    p0=dict(path); p0[var]=False
    ok1,n1,seen=verify_guarded_tree(clauses,internal_vars,boundary_vars,node["true"],p1,seen)
    ok0,n0,seen=verify_guarded_tree(clauses,internal_vars,boundary_vars,node["false"],p0,seen)
    total=n1+n0
    return ok1 and ok0,total,seen

def verify_tree_semantics(clauses, internal_vars, boundary_vars, node):
    bv=sorted(boundary_vars)
    for bits in itertools.product([False,True],repeat=len(bv)):
        b=dict(zip(bv,bits))
        alpha,_=eval_guarded_tree(node,b)
        full=dict(b); full.update({int(k):bool(v) for k,v in alpha.items()})
        if not formula_value(clauses,full):
            return False
    return True

def kappa_exact(clauses, internal_vars, boundary_vars):
    iv=sorted(internal_vars); bv=sorted(boundary_vars)
    alphas=[dict(zip(iv,bits)) for bits in itertools.product([False,True],repeat=len(iv))]
    btables=[dict(zip(bv,bits)) for bits in itertools.product([False,True],repeat=len(bv))]
    # Require D_C=TRUE.
    for b in btables:
        if not any(formula_value(clauses,{**b,**a}) for a in alphas):
            return None
    for k in range(1,len(alphas)+1):
        for idxs in itertools.combinations(range(len(alphas)),k):
            if all(any(formula_value(clauses,{**b,**alphas[i]}) for i in idxs) for b in btables):
                return k
    raise AssertionError

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def main(out_path):
    results={}

    # Control 1: universal branch
    F1=[(1,2),(1,-2)]
    iv={1}; bv={2}
    cover1,w1=tautology_safe_internal_cover_sat(F1,iv,bv)
    leaf1={"type":"CONST_LEAF","alpha":{"1":True}}
    leaf1_ok,leaf1_inspections=verify_internal_cover_witness(F1,iv,bv,{1:True})
    D1=domain_truth_table(F1,iv,bv)
    results["universal_branch"]={
      "domain":D1,"U_C_star_sat":cover1,"U_C_star_witness":{str(k):v for k,v in w1.items()},
      "kappa_C":kappa_exact(F1,iv,bv),
      "internal_cover_witness_pass":leaf1_ok,
      "clause_literal_inspections":leaf1_inspections,
      "proof_DAG_nodes":1,
      "PCShieldSize_control":1
    }

    # Control 2: distributed shielding, f(b)=NOT b.
    F2=[(1,2),(-1,-2)]
    cover2,_=tautology_safe_internal_cover_sat(F2,iv,bv)
    D2=domain_truth_table(F2,iv,bv)
    tree2={
      "type":"GUARDED_ITE","guard_var":2,
      "true":{"type":"CONST_LEAF","alpha":{"1":False}},
      "false":{"type":"CONST_LEAF","alpha":{"1":True}}
    }
    tree2_ok,tree2_inspections,seen2=verify_guarded_tree(F2,iv,bv,tree2)
    tree2_sem=verify_tree_semantics(F2,iv,bv,tree2)
    c0,_=verify_internal_cover_witness(F2,iv,bv,{1:False})
    c1,_=verify_internal_cover_witness(F2,iv,bv,{1:True})
    results["distributed_shielding"]={
      "domain":D2,"U_C_star_sat":cover2,"kappa_C":kappa_exact(F2,iv,bv),
      "constant_internal_cover_witnesses_pass":[c0,c1],
      "guarded_ITE_pass":tree2_ok and tree2_sem,
      "coverage_proof":"BY_CONSTRUCTION_COMPLEMENTARY_SPLIT_b_NOT_b",
      "generic_guard_tautology_oracle_used":False,
      "clause_literal_inspections":tree2_inspections,
      "proof_DAG_nodes":len(seen2),
      "PCShieldSize_control":len(seen2)
    }

    # Control 3: semantic signal. D(b)=b, constant x=0 is conditionally valid.
    F3=[(1,2),(-1,2)]
    cover3,_=tautology_safe_internal_cover_sat(F3,iv,bv)
    D3=domain_truth_table(F3,iv,bv)
    conditional=constant_witness_valid_on_domain(F3,iv,bv,{1:False},D3)
    total_attempt,_=verify_internal_cover_witness(F3,iv,bv,{1:False})
    results["semantic_signal"]={
      "domain":D3,
      "expected_domain":{"0":False,"1":True},
      "U_C_star_sat":cover3,
      "conditional_witness_x0_valid_on_domain":conditional,
      "total_shielding_attempt_pass":total_attempt,
      "interface_class":"PARTIAL_DOMAIN_PLUS_CONDITIONAL_WITNESS"
    }

    # Control 4: boundary tautology, no internal vars.
    F4=[(1,-1)]
    iv4=set(); bv4={1}
    naive4,_=naive_internal_cover_sat(F4,iv4)
    safe4,_=tautology_safe_internal_cover_sat(F4,iv4,bv4)
    D4=domain_truth_table(F4,iv4,bv4)
    results["boundary_tautology"]={
      "naive_U_C_sat":naive4,
      "U_C_star_sat":safe4,
      "domain":D4,
      "naive_unqualified_converse_rejected":(not naive4 and safe4 and all(D4.values()))
    }

    checks={
      "universal_internal_cover_rule_pass":
        results["universal_branch"]["internal_cover_witness_pass"]
        and results["universal_branch"]["U_C_star_sat"]
        and results["universal_branch"]["kappa_C"]==1
        and all(results["universal_branch"]["domain"].values()),
      "distributed_requires_genuine_guarded_ITE":
        results["distributed_shielding"]["U_C_star_sat"] is False
        and results["distributed_shielding"]["kappa_C"]==2
        and results["distributed_shielding"]["constant_internal_cover_witnesses_pass"]==[False,False]
        and results["distributed_shielding"]["guarded_ITE_pass"]
        and all(results["distributed_shielding"]["domain"].values()),
      "semantic_signal_retains_exact_domain":
        results["semantic_signal"]["domain"]=={"0":False,"1":True}
        and results["semantic_signal"]["conditional_witness_x0_valid_on_domain"]
        and results["semantic_signal"]["total_shielding_attempt_pass"] is False,
      "tautology_safe_master_theorem_control":
        results["boundary_tautology"]["naive_unqualified_converse_rejected"]
    }
    verdict="PASS_U_PAIR_1J_MANTEQUILLA_BRIDGE_CONTROLS" if all(checks.values()) else "FAIL_U_PAIR_1J_MANTEQUILLA_BRIDGE_CONTROLS"
    out={
      "artifact_id":"JANUS-TRUMP-U-PAIR-1J-MANTEQUILLA-PROOF-CARRYING-SHIELDING-BRIDGE-CONTROL-CHECK-v1",
      "verdict":verdict,
      "results":results,
      "checks":checks,
      "resource_accounting":{
        "generic_SK0LEM_VALID_calls":0,
        "generic_DAG_tautology_calls":0,
        "SAT_solver_calls":0,
        "general_truth_table_enumeration_authority":False,
        "note":"Finite exhaustive evaluation is used only inside preregistered tiny controls as a test harness, not as a general calculus rule."
      },
      "claim_ceiling":{
        "controls_only":True,
        "hostile_scaling_not_yet_run":True,
        "polynomial_synthesis_not_proved":True,
        "GENERAL_SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN"
      }
    }
    out["semantic_digest_sha256"]=canonical_sha(out)
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":verdict,"digest":out["semantic_digest_sha256"],"checks":checks},sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: checker.py OUT.json")
    main(sys.argv[1])
