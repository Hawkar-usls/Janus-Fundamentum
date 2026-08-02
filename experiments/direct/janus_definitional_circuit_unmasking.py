#!/usr/bin/env python3
"""
JANUS C022 Definitional Circuit Unmasking

Extends C021's single OR-definition recovery to an exact acyclic library:
OR, AND, XOR, and equivalence/XNOR.

The experiment asks whether tractable heterogeneous modules hidden behind
fresh Tseitin-like extension variables can be recovered in polynomial work
when the definitions are explicit, functional, and structurally certified.

No swarm, device, model, Telegram backend, NAS, or physical system is used.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path
from typing import Any

from janus_cognitive_portfolio_search import (
    CNF, Clause, ProofDAG, SolverResult, brute_force, canonical_clause,
    canonical_formula, formula_hash, mixed_formula, primal_components,
    satisfies, solve_componentwise, split_by_components, vars_of,
)


def relation_clauses(a:int,b:int,z:int,gate:str)->list[Clause]:
    def value(x:bool,y:bool)->bool:
        if gate=="OR": return x or y
        if gate=="AND": return x and y
        if gate=="XOR": return x ^ y
        if gate=="EQUIV": return x == y
        raise ValueError(gate)
    out=[]
    for xa,xb,xz in itertools.product([False,True],repeat=3):
        if xz == value(xa,xb): continue
        out.append(canonical_clause([-a if xa else a,-b if xb else b,-z if xz else z]))
    return list(canonical_formula(out))


GATES=("OR","AND","XOR","EQUIV")


def detect_root_definition(remaining:list[Clause], comparisons:dict[str,int])->dict[str,Any]|None:
    f=canonical_formula(remaining); occurrence={v:[] for v in vars_of(f)}
    for i,c in enumerate(remaining):
        for l in c: occurrence[abs(l)].append(i)
    for z,idxs in sorted(occurrence.items()):
        clauses=[remaining[i] for i in idxs]
        other_vars=sorted({abs(l) for c in clauses for l in c if abs(l)!=z})
        if len(other_vars)!=2: continue
        a,b=other_vars; got=set(clauses)
        for gate in GATES:
            comparisons["gate_patterns"]+=1
            expected=set(relation_clauses(a,b,z,gate))
            if got==expected:
                return {"gate":gate,"a":a,"b":b,"z":z,"clause_indices":sorted(idxs)}
    return None


def strip_definitional_circuit(f:CNF)->tuple[CNF,list[dict[str,Any]],dict[str,int]]:
    remaining=list(f); eliminated=[]; comparisons={"rounds":0,"gate_patterns":0}
    while True:
        comparisons["rounds"]+=1; d=detect_root_definition(remaining,comparisons)
        if d is None: break
        drop=set(d.pop("clause_indices")); remaining=[c for i,c in enumerate(remaining) if i not in drop]
        eliminated.append(d)
    return canonical_formula(remaining),eliminated,comparisons


def eval_gate(gate:str,a:bool,b:bool)->bool:
    if gate=="OR": return a or b
    if gate=="AND": return a and b
    if gate=="XOR": return a ^ b
    if gate=="EQUIV": return a == b
    raise ValueError(gate)


def recover_extensions(base:dict[int,bool],defs:list[dict[str,Any]])->dict[int,bool]|None:
    out=dict(base); pending=list(reversed(defs)); progress=True
    while pending and progress:
        progress=False
        for d in list(pending):
            if d["a"] in out and d["b"] in out:
                out[d["z"]]=eval_gate(d["gate"],out[d["a"]],out[d["b"]]); pending.remove(d); progress=True
    return None if pending else out


def solve_unmasked(f:CNF,dag:ProofDAG)->SolverResult:
    core,defs,cost=strip_definitional_circuit(f)
    if not defs: return SolverResult("OPEN","CIRCUIT_UNMASK",reason="no_certified_definitions")
    transform=dag.add("TRANSFORM_STRIP_DEFINITIONAL_CIRCUIT",{"definitions":defs,"core_sha256":formula_hash(core),"recognizer_cost":cost})
    inner=solve_componentwise(core,dag)
    if inner.status=="SAT":
        w=recover_extensions(inner.witness or {},defs)
        if w is None or not satisfies(f,w): return SolverResult("OPEN","CIRCUIT_UNMASK",reason="witness_recovery_failed")
        root=dag.add("LAUGHTER_CIRCUIT_RECOVERED_WITNESS",{"witness":w},[transform,*([inner.dag_root] if inner.dag_root is not None else [])])
        return SolverResult("SAT","CIRCUIT_UNMASK",witness=w,certificate={"definitions":defs,"cost":cost},dag_root=root)
    if inner.status=="UNSAT":
        cert={"definitions":defs,"core":[list(c) for c in core],"inner":inner.certificate,"inner_language":inner.language,"cost":cost}
        root=dag.add("TEAR_CIRCUIT_EQSAT_REDUCTION",cert,[transform,*([inner.dag_root] if inner.dag_root is not None else [])])
        return SolverResult("UNSAT","CIRCUIT_UNMASK",certificate=cert,dag_root=root)
    return SolverResult("OPEN","CIRCUIT_UNMASK",reason="core_open")


def attach_random_circuit(f:CNF,rng:random.Random,gate_count:int)->tuple[CNF,list[dict[str,Any]],int]:
    reps=[min(c) for c in primal_components(f)]; pool=list(reps); cs=list(f); nextv=max(vars_of(f),default=0)+1; defs=[]
    while len(pool)>1:
        a=pool.pop(rng.randrange(len(pool))); b=pool.pop(rng.randrange(len(pool))); gate=rng.choice(GATES); z=nextv; nextv+=1
        cs.extend(relation_clauses(a,b,z,gate)); defs.append({"gate":gate,"a":a,"b":b,"z":z}); pool.append(z)
    root=pool[0]; available=reps+[d["z"] for d in defs]
    while len(defs)<gate_count:
        a=root; b=rng.choice(available)
        if a==b: b=rng.choice(reps)
        gate=rng.choice(GATES); z=nextv; nextv+=1
        cs.extend(relation_clauses(a,b,z,gate)); defs.append({"gate":gate,"a":a,"b":b,"z":z}); available.append(z); root=z
    return canonical_formula(cs),defs,root


def shuffle_formula(f:CNF,rng:random.Random)->CNF:
    clauses=[list(c) for c in f]; rng.shuffle(clauses)
    for c in clauses: rng.shuffle(c)
    return tuple(tuple(c) for c in clauses)


def run(seed:int=9379992,cases:int=180,gates:int=24)->dict[str,Any]:
    rng=random.Random(seed); solved=mismatch=naive_open=definitions=comparisons=rounds=max_nodes=0; gate_counts={g:0 for g in GATES}
    for _ in range(cases):
        core=mixed_formula(rng); truth=all(brute_force(comp)[0] for comp in split_by_components(core))
        masked,_,_=attach_random_circuit(core,rng,gates); masked=shuffle_formula(masked,rng); canonical=canonical_formula(masked)
        naive=solve_componentwise(canonical,ProofDAG())
        if naive.status=="OPEN": naive_open+=1
        dag=ProofDAG(); r=solve_unmasked(canonical,dag); max_nodes=max(max_nodes,len(dag.nodes))
        if r.status!="OPEN": solved+=1
        if r.status=="OPEN" or (r.status=="SAT")!=truth or (r.status=="SAT" and not satisfies(canonical,r.witness or {})): mismatch+=1
        cert=r.certificate or {}; detected=cert.get("definitions",[]); definitions+=len(detected); cost=cert.get("cost",{})
        comparisons+=cost.get("gate_patterns",0); rounds+=cost.get("rounds",0)
        for d in detected: gate_counts[d["gate"]]+=1

    core=mixed_formula(rng); masked,_,root=attach_random_circuit(core,rng,12); constrained=canonical_formula([*masked,(root,)])
    _,stripped_defs,safety_cost=strip_definitional_circuit(constrained); safety_result=solve_unmasked(constrained,ProofDAG())
    base=mixed_formula(rng); reps=[min(c) for c in primal_components(base)]; z=max(vars_of(base))+1
    nonfunctional=canonical_formula([*base,(-z,reps[0],reps[1])]); _,nf_defs,nf_cost=strip_definitional_circuit(nonfunctional)
    scale_core=mixed_formula(rng); scale_masked,_,_=attach_random_circuit(scale_core,rng,256); _,scale_defs,scale_cost=strip_definitional_circuit(scale_masked)
    assertions={
        "deep_masking_all_solved":solved==cases,
        "deep_masking_zero_mismatch":mismatch==0,
        "naive_policy_blinded":naive_open>0,
        "all_gate_types_exercised":all(v>0 for v in gate_counts.values()),
        "constrained_output_not_stripped":len(stripped_defs)==0 and safety_result.status=="OPEN",
        "nonfunctional_relation_rejected":len(nf_defs)==0,
        "long_chain_all_definitions_recovered":len(scale_defs)==256,
        "recognizer_cost_polynomial_fixture":scale_cost["gate_patterns"] < 100000,
    }
    return {
        "audit":"JANUS_C022_DEFINITIONAL_CIRCUIT_UNMASKING","status":"PASS" if all(assertions.values()) else "FAIL",
        "software_only":True,"swarm_touched":False,"devices_touched":False,"model_apis_called":False,
        "seed":seed,"cases":cases,"gates_per_case":gates,"naive_component_open":naive_open,
        "certified_unmasking_solved":solved,"mismatches":mismatch,"definitions_recovered":definitions,
        "gate_counts":gate_counts,"recognizer_gate_comparisons":comparisons,"recognizer_rounds":rounds,"max_proof_dag_nodes":max_nodes,
        "safety_attack":{"final_output_constrained":root,"definitions_stripped":len(stripped_defs),"solver_status":safety_result.status,"recognizer_cost":safety_cost},
        "nonfunctional_attack":{"definitions_stripped":len(nf_defs),"recognizer_cost":nf_cost},
        "scaling_fixture":{"definitions":len(scale_defs),"gate_comparisons":scale_cost["gate_patterns"],"rounds":scale_cost["rounds"]},
        "assertions":assertions,
        "positive_result":"Fresh acyclic OR/AND/XOR/EQUIV extension circuits can be removed and their witnesses reconstructed using an exact root-first recognizer. Therefore explicit Tseitin-like representation masking is not by itself a barrier for the tested structural portfolio.",
        "obstruction":"The method deliberately refuses outputs used in real core constraints and non-functional relations. General discovery of hidden or overlapping definitions, arbitrary substitutions, or semantic equivalence remains open.",
        "p_equals_np_progress":"REPRESENTATION_ROBUSTNESS_EXPANDED_NOT_GENERAL_SAT",
        "next_search_target":"Attack the selector with overlapping definitions, shared extension outputs, cyclic circuits, and constraints that require symbolic substitution rather than safe deletion."
    }


def main()->None:
    ap=argparse.ArgumentParser(); ap.add_argument("--seed",type=int,default=9379992); ap.add_argument("--cases",type=int,default=180); ap.add_argument("--gates",type=int,default=24); ap.add_argument("--output",type=Path); ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args(); r=run(a.seed,a.cases,a.gates)
    if a.output: a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(r,ensure_ascii=False,indent=2))
    if a.self_test and r["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__": main()
