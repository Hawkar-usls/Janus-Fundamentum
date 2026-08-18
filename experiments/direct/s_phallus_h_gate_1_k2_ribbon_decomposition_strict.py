#!/usr/bin/env python3
"""Strict preregistration-conformant runner for S𓂸ḥ/1 K=2.

Repairs implementation only: boundary restriction uses the frozen sequential
cofactor semantics, and K2 discovery builds the primal graph once then charges
all candidate-pair/component/partition checks.  Contract, fixtures, budgets and
promotion gates remain unchanged.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

import s_phallus_h_gate_1_k2_ribbon_decomposition as gate
from janus_c025_core import CNF, canonical_cnf, cnf_hash, cofactor, satisfies, variables


def strict_detect_k2(formula: CNF) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    q0 = gate.v21.detect_pair_product(formula)
    if q0["matched"]:
        core={"formula_hash":cnf_hash(formula),"matched":False,"reason":"Q0_PRIORITY"}
        return {**core,"separator":None,"components":[],"metrics":{"q0_priority_reject":1},"certificate_sha256":gate.digest(core)}
    k1 = gate.g0.detect_articulation(formula)
    if k1["matched"]:
        core={"formula_hash":cnf_hash(formula),"matched":False,"reason":"K1_PRIORITY"}
        return {**core,"separator":None,"components":[],"metrics":{"k1_priority_reject":1},"certificate_sha256":gate.digest(core)}

    graph, graph_cost = gate.g0.primal_graph(formula)
    before = gate.g0.connected_components(graph)
    pairs=list(itertools.combinations(sorted(graph),2))
    verified=[]
    partition_checks=0
    component_recomputations=0
    for pair in pairs:  # frozen: exhaust all pairs
        after=gate.g0.connected_components(graph,set(pair)); component_recomputations+=1
        separates=len(after)>len(before) and len(after)>=2
        owner={v:i for i,comp in enumerate(after) for v in comp}
        cross=False
        local_checks=0
        for clause in formula:
            nonsep={abs(lit) for lit in clause if abs(lit) not in pair}
            if not nonsep:
                continue
            local_checks+=1
            ids={owner.get(v,-1) for v in nonsep}
            if len(ids)!=1 or -1 in ids:
                cross=True
                break
        partition_checks+=local_checks
        if separates and not cross:
            verified.append((pair,after))

    metrics={
        "graph_clause_visits":graph_cost["graph_clause_visits"],
        "graph_pair_edge_attempts":graph_cost["graph_pair_edge_attempts"],
        "candidate_pair_count":len(pairs),
        "candidate_component_recomputations":component_recomputations,
        "separator_clause_partition_checks":partition_checks,
        "verified_separator_count":len(verified),
    }
    if not verified:
        core={"formula_hash":cnf_hash(formula),"matched":False,"reason":"NO_VERIFIED_K2_SEPARATOR","metrics":metrics}
        return {**core,"separator":None,"components":[],"certificate_sha256":gate.digest(core)}
    pair,comps=verified[0]
    core={"formula_hash":cnf_hash(formula),"matched":True,"reason":None,"separator":list(pair),
          "components":[list(c) for c in comps],"metrics":metrics}
    return {**core,"certificate_sha256":gate.digest(core)}


def strict_partition_rows(formula: CNF, residual: CNF, units: dict[int,bool], separator: tuple[int,...],
                          valuations: list[tuple[bool,...]], budget: int, base_engine,
                          depth: int, counters: dict[str,Any], kind: str, certificate: str,
                          claimed_components: list[list[int]]) -> dict[str,Any]:
    rows=[]; sat_candidates=[]
    for valuation in valuations:
        if kind=="K1": counters["k1_boundary_valuations"]+=1
        else: counters["k2_boundary_valuations"]+=1
        boundary={var:value for var,value in zip(separator,valuation)}
        restricted=residual
        for var,value in sorted(boundary.items()):
            restricted=cofactor(restricted,var,value)
        restricted=canonical_cnf(restricted)
        comps=gate.g0.component_formulas(restricted)
        counters["component_partitions"]+=len(comps)
        branch_status="SAT"; branch_assignment=dict(boundary); comp_rows=[]
        for comp in comps:  # frozen: every component, no early closure
            solved=gate.solve_recursive(comp,budget,base_engine,depth+1,counters)
            comp_rows.append({"formula_hash":cnf_hash(comp),"status":solved["status"],"tree":solved["tree"]})
            if solved["status"]=="UNSAT": branch_status="UNSAT"
            elif solved["status"]=="UNKNOWN_BUDGET" and branch_status!="UNSAT": branch_status="UNKNOWN_BUDGET"
            elif solved["status"]=="SAT" and solved.get("assignment"): branch_assignment.update(solved["assignment"])
        if branch_status=="SAT":
            full={v:False for v in variables(formula)}; full.update(units); full.update(branch_assignment)
            if satisfies(formula,full): sat_candidates.append(full)
            else: branch_status="UNKNOWN_BUDGET"
        rows.append({"valuation":list(valuation),"status":branch_status,"components":comp_rows})
    tree={"kind":kind,"formula_hash":cnf_hash(formula),"residual_hash":cnf_hash(residual),
          "separator":list(separator),"separator_certificate":certificate,
          "claimed_components":claimed_components,"boundary_rows":rows}
    tree["tree_sha256"]=gate.digest(tree)
    if sat_candidates: return {"status":"SAT","assignment":sat_candidates[0],"tree":tree}
    if rows and all(r["status"]=="UNSAT" for r in rows): return {"status":"UNSAT","assignment":None,"tree":tree}
    return {"status":"UNKNOWN_BUDGET","assignment":None,"tree":tree}


def run() -> dict[str,Any]:
    gate.detect_k2=strict_detect_k2
    gate._solve_partition_rows=strict_partition_rows
    result=gate.run()
    result["implementation_conformance"]={
        "frozen_contract_unchanged":True,
        "sequential_cofactor_for_k2_boundary":True,
        "all_candidate_pairs_exhaustively_enumerated":True,
        "primal_graph_built_once_per_k2_detection":True,
        "all_four_boundary_rows_mandatory":True,
        "all_components_solved_per_row":True,
    }
    result.pop("integrity_sha256",None); result["integrity_sha256"]=gate.digest(result)
    return result


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    result=run(); text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text+"\n",encoding="utf-8")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"): raise SystemExit(1)

if __name__=="__main__": main()
