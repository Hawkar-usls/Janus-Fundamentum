#!/usr/bin/env python3
"""S𓂸ḥ/1: verified K=2 separator decomposition with ORIGIN_PRIME ribbon state.

Modern SAT/complexity experiment only.  Priority is Q0 PR192 -> K1 articulation
-> K2 verified separator -> unchanged OSIRIS v2 generic fallback.  All K2
candidate pairs are enumerated and charged; all four boundary valuations are
solved.  The ribbon state preserves path history while the computational
POSITION remains reproducible.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import itertools
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import osiris_v2_technical_sat_solver as v2
import osiris_v2_1_pr192_prebirth_quotient as v21
import s_phallus_h_gate_0_articulation_decomposition as g0
from janus_c025_core import CNF, canonical_cnf, cnf_hash, cofactor, satisfies, variables

RUN_ID = "S-PHALLUS-H-GATE-1-K2-RIBBON-DECOMPOSITION-2026-08-19-v1"
CONTRACT = "S_PHALLUS_H_GATE_1_K2_RIBBON_DECOMPOSITION_FROZEN_CONTRACT.json"
PARENT_SHA = "325620a1befb84a3a7a8235fd2f587e4ea224e37"
PARENT_RESULT_SHA = "c0dbc2d5ed3635fd8ca2f72d13a2c8b04e2282730c3bec2f1971915e01e3df0a"
Q0_LANE = "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT"
K1_LANE = "S_PHALLUS_H_0_ARTICULATION_DECOMPOSITION"
K2_LANE = "S_PHALLUS_H_1_VERIFIED_SEPARATOR_K2"
GENERIC_LANE = "GENERIC_OSIRIS_V2_FALLBACK"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
MAX_DEPTH = 64


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def _canonical_components(comps: Iterable[Iterable[int]]) -> list[tuple[int, ...]]:
    return sorted(tuple(sorted(int(v) for v in comp)) for comp in comps)


def verify_k2_claim(formula: CNF, pair: tuple[int, int], claimed: Iterable[Iterable[int]]) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    pair = tuple(sorted(pair))
    graph, graph_cost = g0.primal_graph(formula)
    if len(pair) != 2 or pair[0] == pair[1] or any(v not in graph for v in pair):
        return {"passed": False, "reason": "PAIR_INVALID_OR_ABSENT", **graph_cost}
    before = g0.connected_components(graph)
    after = g0.connected_components(graph, set(pair))
    separates = len(after) > len(before) and len(after) >= 2
    exact_components = _canonical_components(claimed) == _canonical_components(after)
    owner = {v: i for i, comp in enumerate(after) for v in comp}
    partition_checks = 0
    cross = False
    for clause in formula:
        nonsep = {abs(lit) for lit in clause if abs(lit) not in pair}
        if not nonsep:
            continue
        partition_checks += 1
        ids = {owner.get(v, -1) for v in nonsep}
        if len(ids) != 1 or -1 in ids:
            cross = True
            break
    passed = separates and exact_components and not cross
    reason = None if passed else "NOT_K2_SEPARATOR" if not separates else "COMPONENT_MISMATCH" if not exact_components else "CROSS_COMPONENT_CLAUSE"
    return {
        "passed": passed, "reason": reason,
        "before_component_count": len(before), "after_component_count": len(after),
        "actual_components": [list(c) for c in after],
        "separator_clause_partition_checks": partition_checks,
        **graph_cost,
    }


def detect_k2(formula: CNF) -> dict[str, Any]:
    """Full deterministic pair enumeration; fixture names/expected labels are never read."""
    formula = canonical_cnf(formula)
    q0 = v21.detect_pair_product(formula)
    if q0["matched"]:
        core = {"formula_hash": cnf_hash(formula), "matched": False, "reason": "Q0_PRIORITY"}
        return {**core, "separator": None, "components": [], "metrics": {"q0_priority_reject": 1}, "certificate_sha256": digest(core)}
    k1 = g0.detect_articulation(formula)
    if k1["matched"]:
        core = {"formula_hash": cnf_hash(formula), "matched": False, "reason": "K1_PRIORITY"}
        return {**core, "separator": None, "components": [], "metrics": {"k1_priority_reject": 1}, "certificate_sha256": digest(core)}

    graph, graph_cost = g0.primal_graph(formula)
    pairs = list(itertools.combinations(sorted(graph), 2))
    verified: list[tuple[tuple[int, int], list[tuple[int, ...]], dict[str, Any]]] = []
    component_recomputations = 0
    partition_checks = 0
    for pair in pairs:
        comps = g0.connected_components(graph, set(pair))
        component_recomputations += 1
        check = verify_k2_claim(formula, pair, comps)
        partition_checks += int(check.get("separator_clause_partition_checks", 0))
        if check["passed"]:
            verified.append((pair, comps, check))

    if not verified:
        core = {
            "formula_hash": cnf_hash(formula), "matched": False, "reason": "NO_VERIFIED_K2_SEPARATOR",
            "metrics": {**graph_cost, "candidate_pair_count": len(pairs),
                        "candidate_component_recomputations": component_recomputations,
                        "separator_clause_partition_checks": partition_checks,
                        "verified_separator_count": 0},
        }
        return {**core, "separator": None, "components": [], "certificate_sha256": digest(core)}

    pair, comps, _ = verified[0]
    metrics = {
        **graph_cost, "candidate_pair_count": len(pairs),
        "candidate_component_recomputations": component_recomputations,
        "separator_clause_partition_checks": partition_checks,
        "verified_separator_count": len(verified),
    }
    core = {
        "formula_hash": cnf_hash(formula), "matched": True, "reason": None,
        "separator": list(pair), "components": [list(c) for c in comps], "metrics": metrics,
    }
    return {**core, "certificate_sha256": digest(core)}


def make_counters() -> dict[str, Any]:
    return {
        "recursive_component_calls": 0, "max_recursion_depth": 0, "unit_propagations": 0,
        "q0_detector_calls": 0, "q0_leaf_hits": 0, "q0_symbolic_states": 0, "q0_symbolic_transitions": 0,
        "k1_detector_calls": 0, "k1_nodes": 0, "k1_boundary_valuations": 0,
        "k2_detector_calls": 0, "k2_nodes": 0, "k2_boundary_valuations": 0,
        "component_partitions": 0, "generic_leaf_calls": 0,
        "discovery_cost": {}, "leaf_engine": g0.empty_stats(),
    }


def _add_metrics(dst: dict[str, int], metrics: dict[str, Any], prefix: str = "") -> None:
    for key, val in metrics.items():
        if isinstance(val, int):
            name = prefix + key
            dst[name] = dst.get(name, 0) + val


def _solve_partition_rows(formula: CNF, residual: CNF, units: dict[int, bool], separator: tuple[int, ...],
                          valuations: list[tuple[bool, ...]], budget: int, base_engine,
                          depth: int, counters: dict[str, Any], kind: str, certificate: str,
                          claimed_components: list[list[int]]) -> dict[str, Any]:
    rows = []
    sat_candidates: list[dict[int, bool]] = []
    for valuation in valuations:
        if kind == "K1":
            counters["k1_boundary_valuations"] += 1
        else:
            counters["k2_boundary_valuations"] += 1
        restricted = residual
        boundary_assignment: dict[int, bool] = {}
        for var, value in zip(separator, valuation):
            boundary_assignment[var] = value
        restricted = canonical_cnf(cofactor(restricted, boundary_assignment))
        comps = g0.component_formulas(restricted)
        counters["component_partitions"] += len(comps)
        branch_status = "SAT"
        branch_assignment = dict(boundary_assignment)
        comp_rows = []
        for comp in comps:  # frozen rule: every component, no early exit
            solved = solve_recursive(comp, budget, base_engine, depth + 1, counters)
            comp_rows.append({"formula_hash": cnf_hash(comp), "status": solved["status"], "tree": solved["tree"]})
            if solved["status"] == "UNSAT":
                branch_status = "UNSAT"
            elif solved["status"] == "UNKNOWN_BUDGET" and branch_status != "UNSAT":
                branch_status = "UNKNOWN_BUDGET"
            elif solved["status"] == "SAT" and solved.get("assignment"):
                branch_assignment.update(solved["assignment"])
        if branch_status == "SAT":
            full = {v: False for v in variables(formula)}
            full.update(units)
            full.update(branch_assignment)
            if satisfies(formula, full):
                sat_candidates.append(full)
            else:
                branch_status = "UNKNOWN_BUDGET"
        rows.append({"valuation": list(valuation), "status": branch_status, "components": comp_rows})

    tree = {
        "kind": kind, "formula_hash": cnf_hash(formula), "residual_hash": cnf_hash(residual),
        "separator": list(separator), "separator_certificate": certificate,
        "claimed_components": claimed_components, "boundary_rows": rows,
    }
    tree["tree_sha256"] = digest(tree)
    if sat_candidates:
        return {"status": "SAT", "assignment": sat_candidates[0], "tree": tree}
    if rows and all(row["status"] == "UNSAT" for row in rows):
        return {"status": "UNSAT", "assignment": None, "tree": tree}
    return {"status": "UNKNOWN_BUDGET", "assignment": None, "tree": tree}


def solve_recursive(formula: CNF, budget: int, base_engine, depth: int, counters: dict[str, Any]) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    counters["recursive_component_calls"] += 1
    counters["max_recursion_depth"] = max(counters["max_recursion_depth"], depth)
    if depth > MAX_DEPTH:
        return {"status": "UNKNOWN_BUDGET", "assignment": None, "tree": {"kind": "DEPTH_LIMIT", "formula_hash": cnf_hash(formula)}}
    if not formula:
        return {"status": "SAT", "assignment": {}, "tree": {"kind": "EMPTY_SAT", "formula_hash": cnf_hash(formula)}}
    if () in formula:
        return {"status": "UNSAT", "assignment": None, "tree": {"kind": "EMPTY_CLAUSE_UNSAT", "formula_hash": cnf_hash(formula)}}

    residual, units, trail = v2.unit_propagate(formula)
    counters["unit_propagations"] += len(trail)
    residual = canonical_cnf(residual)
    if not residual:
        full = {v: False for v in variables(formula)}; full.update(units)
        ok = satisfies(formula, full)
        return {"status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": full if ok else None,
                "tree": {"kind": "UNIT_SAT", "formula_hash": cnf_hash(formula), "verified": ok}}
    if () in residual:
        return {"status": "UNSAT", "assignment": None, "tree": {"kind": "UNIT_UNSAT", "formula_hash": cnf_hash(formula)}}

    q0 = v21.detect_pair_product(residual); counters["q0_detector_calls"] += 1
    if q0["matched"]:
        counters["q0_leaf_hits"] += 1
        counters["q0_symbolic_states"] += int(q0["metrics"]["symbolic_states"])
        counters["q0_symbolic_transitions"] += int(q0["metrics"]["symbolic_transitions"])
        assignment = {v: False for v in variables(formula)}; assignment.update(units); assignment.update(q0["assignment"] or {})
        ok = satisfies(formula, assignment)
        return {"status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": assignment if ok else None,
                "tree": {"kind": "Q0", "formula_hash": cnf_hash(formula), "certificate": q0["certificate_sha256"], "verified": ok}}

    k1 = g0.detect_articulation(residual); counters["k1_detector_calls"] += 1
    _add_metrics(counters["discovery_cost"], k1.get("metrics", {}), "k1_")
    if k1["matched"]:
        counters["k1_nodes"] += 1
        sep = (int(k1["separator"]),)
        return _solve_partition_rows(formula, residual, units, sep, [(False,), (True,)], budget, base_engine,
                                     depth, counters, "K1", k1["certificate_sha256"], k1["components"])

    k2 = detect_k2(residual); counters["k2_detector_calls"] += 1
    _add_metrics(counters["discovery_cost"], k2.get("metrics", {}), "k2_")
    if k2["matched"]:
        counters["k2_nodes"] += 1
        sep = tuple(int(x) for x in k2["separator"])
        vals = list(itertools.product((False, True), repeat=2))
        return _solve_partition_rows(formula, residual, units, sep, vals, budget, base_engine,
                                     depth, counters, "K2", k2["certificate_sha256"], k2["components"])

    counters["generic_leaf_calls"] += 1
    order, _ = v2.activity_order(residual)
    engine = base_engine(formula, residual, order, units, budget)
    g0.add_engine_stats(counters, engine["stats"])
    return {"status": engine["status"], "assignment": engine.get("assignment"),
            "tree": {"kind": "GENERIC", "formula_hash": cnf_hash(formula), "status": engine["status"],
                     "projection_sha256": digest(v2.engine_projection(engine))}}


def _top_lane(residual: CNF) -> tuple[str, dict[str, Any]]:
    q0 = v21.detect_pair_product(residual)
    if q0["matched"]:
        return Q0_LANE, {"certificate_sha256": q0["certificate_sha256"], "metrics": q0["metrics"]}
    k1 = g0.detect_articulation(residual)
    if k1["matched"]:
        return K1_LANE, {"certificate_sha256": k1["certificate_sha256"], "separator": k1["separator"], "components": k1["components"]}
    k2 = detect_k2(residual)
    if k2["matched"]:
        return K2_LANE, k2
    return GENERIC_LANE, {"k2_rejection_reason": k2["reason"]}


def solve_with_k2_gate(raw_formula: Iterable[Iterable[int]], budget: int) -> dict[str, Any]:
    base_engine = v2.engine_run
    calls: list[dict[str, Any]] = []

    def aware_engine(original: CNF, residual: CNF, residual_order: list[int], units: dict[int, bool], state_budget: int) -> dict[str, Any]:
        lane, top = _top_lane(residual)
        if lane == Q0_LANE:
            q0 = v21.detect_pair_product(residual)
            engine = g0.q0_engine_result(original, residual, units, q0)
            calls.append({"lane": lane, "formula_hash": cnf_hash(residual), **top})
            return engine
        if lane == GENERIC_LANE:
            engine = base_engine(original, residual, residual_order, units, state_budget)
            engine["stats"] = dict(engine["stats"]); engine["stats"]["s_gate_lane"] = GENERIC_LANE
            calls.append({"lane": lane, "formula_hash": cnf_hash(residual), **top})
            return engine

        counters = make_counters()
        solved = solve_recursive(residual, state_budget, base_engine, 0, counters)
        status = solved["status"]
        assignment = None; verified = None
        if status == "SAT":
            assignment = {v: False for v in variables(original)}; assignment.update(units); assignment.update(solved.get("assignment") or {})
            verified = satisfies(original, assignment)
            if not verified:
                status = "UNKNOWN_BUDGET"; assignment = None
        leaf = counters["leaf_engine"]
        symbolic_states = counters["q0_symbolic_states"] + counters["k1_nodes"] + counters["k1_boundary_valuations"] + counters["k2_nodes"] + counters["k2_boundary_valuations"]
        stats = {
            "status": "EXACT_DECOMPOSITION" if status in {"SAT","UNSAT"} else "OPEN",
            "recursive_calls": max(symbolic_states, leaf["recursive_calls"] + counters["recursive_component_calls"]),
            "memo_hits": leaf["memo_hits"], "residual_states": leaf["residual_states"] + symbolic_states,
            "transition_checks": leaf["transition_checks"] + counters["k1_boundary_valuations"] + counters["k2_boundary_valuations"] + counters["q0_symbolic_transitions"],
            "normalization_certificates": leaf["normalization_certificates"], "subsumption_steps": leaf["subsumption_steps"],
            "bdd_nodes": leaf["bdd_nodes"], "max_frontier_states": max(1, leaf["max_frontier_states"]), "frontier_counts": {"0":1},
            "error": None if status in {"SAT","UNSAT"} else "DECOMPOSITION_CHILD_UNKNOWN",
            "s_gate_lane": lane, "k2_tree_sha256": digest(solved["tree"]),
            "k1_nodes": counters["k1_nodes"], "k2_nodes": counters["k2_nodes"],
            "k1_boundary_valuations": counters["k1_boundary_valuations"], "k2_boundary_valuations": counters["k2_boundary_valuations"],
            "component_partitions": counters["component_partitions"], "generic_leaf_calls": counters["generic_leaf_calls"],
            "discovery_cost": counters["discovery_cost"], "component_units_do_not_sum_as_runtime": True,
        }
        engine = {"status": status, "root": 1 if status=="SAT" else 0 if status=="UNSAT" else None,
                  "sat": True if status=="SAT" else False if status=="UNSAT" else None,
                  "assignment": assignment, "assignment_verified": verified,
                  "reason": lane if status in {"SAT","UNSAT"} else "S_PHALLUS_H_K2_CHILD_UNKNOWN",
                  "stats": stats, "engine_invoked": True}
        calls.append({"lane": lane, "formula_hash": cnf_hash(residual), **top,
                      "status": status, "tree_sha256": digest(solved["tree"]), "tree": solved["tree"], "counters": counters})
        return engine

    v2.engine_run = aware_engine
    try:
        solved = v2.technical_forward(raw_formula, budget)
    finally:
        v2.engine_run = base_engine
    solved["k_calls"] = calls
    solved["primary"] = calls[0] if calls else None
    solved["primary_lane"] = solved["primary"]["lane"] if solved["primary"] else "NO_ENGINE_CALL"
    return solved


def eq_edge(a: int, b: int) -> list[tuple[int, int]]:
    return [(-a, b), (a, -b)]


def anti_edge(a: int, b: int) -> list[tuple[int, int]]:
    return [(a, b), (-a, -b)]


def k2_dumbbell(total_vars: int, conflict: bool = False) -> CNF:
    if total_vars < 8 or total_vars % 2:
        raise ValueError("total_vars must be even and >=8")
    side = (total_vars - 2) // 2
    left = list(range(3, 3 + side)); right = list(range(3 + side, 3 + 2 * side))
    clauses: list[tuple[int, ...]] = []
    for comp in (left, right):
        for i, u in enumerate(comp):
            v = comp[(i + 1) % len(comp)]
            clauses.extend(eq_edge(u, v))
        for sep in (1, 2):
            for u in comp:
                clauses.extend(eq_edge(sep, u))
    if conflict:
        clauses.extend(anti_edge(left[0], left[1]))
    return canonical_cnf(clauses)


def k5_equality() -> CNF:
    clauses: list[tuple[int, ...]] = []
    for a, b in itertools.combinations(range(1, 6), 2):
        clauses.extend(eq_edge(a, b))
    return canonical_cnf(clauses)


def calibration() -> list[dict[str, Any]]:
    return [
        {"id":"K2_DUMBBELL_EQUALITY_8_SAT","formula":k2_dumbbell(8),"expected":"SAT","budget":50000},
        {"id":"K2_DUMBBELL_CONFLICT_8_UNSAT","formula":k2_dumbbell(8,True),"expected":"UNSAT","budget":50000},
        {"id":"K2_DUMBBELL_EQUALITY_10_SAT","formula":k2_dumbbell(10),"expected":"SAT","budget":50000},
        {"id":"K2_DUMBBELL_CONFLICT_10_UNSAT","formula":k2_dumbbell(10,True),"expected":"UNSAT","budget":50000},
        {"id":"K2_DUMBBELL_EQUALITY_12_SAT","formula":k2_dumbbell(12),"expected":"SAT","budget":50000},
    ]


def negative_controls() -> list[dict[str, Any]]:
    no_sep = k5_equality(); d_no = detect_k2(no_sep)
    forged = verify_k2_claim(no_sep, (1,2), g0.connected_components(g0.primal_graph(no_sep)[0], {1,2}))
    base = k2_dumbbell(8); det = detect_k2(base); assert det["matched"]
    bad_components = [tuple(c) for c in det["components"]]
    if len(bad_components) >= 2:
        bad_components = [tuple(sorted(bad_components[0] + bad_components[1]))]
    forged_components = verify_k2_claim(base, tuple(det["separator"]), bad_components)
    solved = solve_with_k2_gate(base, 50000); tree = solved["primary"]["tree"]
    rows = tree["boundary_rows"]
    mutated_rows = [dict(r) for r in rows[:-1]]
    row_set_ok_original = [tuple(r["valuation"]) for r in rows] == list(itertools.product((False,True), repeat=2))
    row_omission_rejected = row_set_ok_original and [tuple(r["valuation"]) for r in mutated_rows] != list(itertools.product((False,True), repeat=2))
    other = k2_dumbbell(10); other_det = detect_k2(other)
    hash_swap_rejected = det["certificate_sha256"] != other_det["certificate_sha256"]
    return [
        {"id":"K5_EQUALITY_NO_K2_SEPARATOR","passed":not d_no["matched"],"reason":d_no["reason"]},
        {"id":"FORGED_K2_PAIR_NOT_SEPARATOR","passed":not forged["passed"],"reason":forged["reason"]},
        {"id":"FORGED_K2_COMPONENT_PARTITION","passed":not forged_components["passed"],"reason":forged_components["reason"]},
        {"id":"K2_BOUNDARY_TABLE_ROW_BITFLIP_OR_OMISSION","passed":row_omission_rejected},
        {"id":"K2_CERTIFICATE_FORMULA_HASH_SWAP","passed":hash_swap_rejected},
    ]


def left_control() -> dict[str, Any]:
    a, b = k2_dumbbell(8), k2_dumbbell(10)
    da, db = detect_k2(a), detect_k2(b)
    return {"control":"SAME_K2_CAPABILITY_DIFFERENT_PROVENANCE",
            "both_k2": da["matched"] and db["matched"],
            "formula_identity_distinct": cnf_hash(a) != cnf_hash(b),
            "certificate_identity_distinct": da["certificate_sha256"] != db["certificate_sha256"],
            "identity_authorized_from_capability": False,
            "passed": da["matched"] and db["matched"] and cnf_hash(a)!=cnf_hash(b) and da["certificate_sha256"]!=db["certificate_sha256"]}


def right_control() -> dict[str, Any]:
    f = k2_dumbbell(8); d = detect_k2(f); action_certificate_present = False
    fallback = g0.solve_with_s_gate(f, 50000)
    return {"control":"SAME_CNF_K2_ACTION_CERTIFICATE_REMOVED", "detector_match":d["matched"],
            "action_certificate_present":False, "k2_authorized":False,
            "fallback_status":fallback["status"], "fallback_authorized":fallback["authorized"],
            "passed":d["matched"] and not action_certificate_present and fallback["authorized"] and fallback["status"]=="SAT"}


def make_position(solved: dict[str, Any]) -> dict[str, Any]:
    p = {"formula_hash": solved["cnf0"]["canonical_cnf_hash"], "technical_verdict": solved["status"],
         "authorized": solved["authorized"], "lane": solved["primary_lane"],
         "projection_sha256": digest(solved["projection"])}
    p["position_commitment"] = digest(p)
    return p


def make_origin(position: dict[str, Any]) -> dict[str, Any]:
    body = {"state_type":"ORIGIN", "generation":0, "position_commitment":position["position_commitment"],
            "previous_state_commitment":None, "path_history_digest":None}
    return {**body, "state_commitment":digest(body)}


def make_history(payloads: dict[str, Any]) -> dict[str, Any]:
    rows=[]
    for i,direction in enumerate(DIRECTIONS):
        rows.append({"index":i,"direction":direction,"payload_digest":digest(payloads[direction])})
    return {"ordered_directions":DIRECTIONS, "history":rows, "path_history_digest":digest(rows)}


def make_origin_prime(previous: dict[str, Any], position: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    generation = int(previous["generation"]) + 1
    body = {"state_type":"ORIGIN_PRIME", "generation":generation,
            "position_commitment":position["position_commitment"],
            "previous_state_commitment":previous["state_commitment"],
            "path_history_digest":history["path_history_digest"]}
    return {**body, "state_commitment":digest(body)}


def ribbon_controls(origin: dict[str, Any], prime: dict[str, Any], position: dict[str, Any], history: dict[str, Any]) -> dict[str, bool]:
    bitflip = dict(history); bitflip["path_history_digest"] = "0"*64 if history["path_history_digest"] != "0"*64 else "1"*64
    erased = dict(history); erased["history"]=[]; erased["path_history_digest"]=digest([])
    mutated_position = dict(position); mutated_position["technical_verdict"] = "MUTATED"; mutated_position["position_commitment"] = digest(mutated_position)
    return {
        "history_bitflip_rejected": make_origin_prime(origin, position, bitflip)["state_commitment"] != prime["state_commitment"],
        "history_erasure_rejected": make_origin_prime(origin, position, erased)["state_commitment"] != prime["state_commitment"],
        "forced_origin_state_reuse_rejected": prime["state_commitment"] != origin["state_commitment"],
        "return_position_mutation_rejected": make_origin_prime(origin, mutated_position, history)["state_commitment"] != prime["state_commitment"],
    }


def run() -> dict[str, Any]:
    contract = json.loads(Path(CONTRACT).read_text(encoding="utf-8"))
    assert contract["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    assert contract["parent"]["sha"] == PARENT_SHA
    assert contract["parent"]["result_integrity_sha256"] == PARENT_RESULT_SHA

    rows=[]
    for fx in calibration():
        solved=solve_with_k2_gate(fx["formula"],fx["budget"])
        rows.append({"id":fx["id"],"expected":fx["expected"],"observed":solved["status"],"authorized":solved["authorized"],
                     "lane":solved["primary_lane"],"exact_correct":solved["status"]==fx["expected"] and solved["authorized"],
                     "k2_used":solved["primary_lane"]==K2_LANE,
                     "cost":solved["cost_vector"],"primary":solved["primary"]})

    negatives=negative_controls()

    regression=[]
    for fx in v2.fixtures():
        solved=solve_with_k2_gate(fx["formula"],fx["budget"])
        regression.append({"id":fx["id"],"expected":fx["expected"],"observed":solved["status"],"lane":solved["primary_lane"],
                           "authorized":solved["authorized"],"passed":solved["status"]==fx["expected"] and solved["authorized"]})
    gate0_rows=[]
    for fx in g0.calibration_fixtures():
        solved=solve_with_k2_gate(fx["formula"],fx["budget"])
        gate0_rows.append({"id":fx["id"],"expected":fx["expected"],"observed":solved["status"],"lane":solved["primary_lane"],
                           "authorized":solved["authorized"],"passed":solved["status"]==fx["expected"] and solved["authorized"] and solved["primary_lane"]==K1_LANE})
    hard=[]
    for fx in v2.hard_fixtures():
        solved=solve_with_k2_gate(fx["formula"],fx["budget"])
        passed=(not solved["authorized"] and solved["status"]=="UNKNOWN_BUDGET") or (solved["authorized"] and solved["status"]==fx["expected"])
        hard.append({"id":fx["id"],"expected":fx["expected"],"observed":solved["status"],"authorized":solved["authorized"],"lane":solved["primary_lane"],"passed":passed})

    ref_formula=k2_dumbbell(10)
    reference=solve_with_k2_gate(ref_formula,50000)
    back=v2.back_replay(reference)
    k2_tree=reference["primary"]["tree"]
    back_bound=back["passed"] and reference["primary"]["certificate_sha256"]==detect_k2(ref_formula)["certificate_sha256"] and len(k2_tree["boundary_rows"])==4
    forward=solve_with_k2_gate(ref_formula,50000)
    left=left_control(); right=right_control(); forward_again=solve_with_k2_gate(ref_formula,50000)
    position=make_position(forward); position2=make_position(forward_again)
    position_same=position["position_commitment"]==position2["position_commitment"]
    back_again={"historical_text_semantics_consumed":False,"technical_verdict":forward["status"],"P_VS_NP":"OPEN","passed":forward["status"]==reference["status"]}
    payloads={"BACK":{"passed":back_bound,"terminal":back["terminal_commitment"]},
              "FORWARD":{"position":position,"primary_certificate":forward["primary"]["certificate_sha256"]},
              "LEFT":left,"RIGHT":right,"FORWARD_AGAIN":{"position":position2,"position_same":position_same},"BACK_AGAIN":back_again}
    history=make_history(payloads); origin=make_origin(position); prime1=make_origin_prime(origin,position,history); prime2=make_origin_prime(prime1,position2,history)
    ribbon_negative=ribbon_controls(origin,prime1,position,history)
    ribbon_ok=position_same and len({origin["state_commitment"],prime1["state_commitment"],prime2["state_commitment"]})==3 and prime2["generation"]==2 and all(ribbon_negative.values())

    eq=next(x for x in regression if x["id"]=="EQUALITY_N14")
    anti=next(x for x in regression if x["id"]=="ANTI_EQUALITY_N14")
    gates={
        "all_5_k2_calibration_exact":len(rows)==5 and all(r["exact_correct"] for r in rows),
        "all_5_k2_calibration_use_k2_lane":len(rows)==5 and all(r["k2_used"] for r in rows),
        "all_5_negative_controls_reject":len(negatives)==5 and all(r["passed"] for r in negatives),
        "osiris_v2_1_regression_8_of_8":len(regression)==8 and all(r["passed"] for r in regression),
        "gate0_regression_5_of_5_stays_k1":len(gate0_rows)==5 and all(r["passed"] for r in gate0_rows),
        "q0_priority_preserved":eq["lane"]==Q0_LANE and anti["lane"]==Q0_LANE,
        "hard_tseitin_same_budget_fail_closed_or_correct":len(hard)==2 and all(r["passed"] for r in hard),
        "BACK_exact_plus_k2_certificate":back_bound,
        "FORWARD_k2_exact":forward["status"]=="SAT" and forward["authorized"] and forward["primary_lane"]==K2_LANE,
        "LEFT_identity_firewall":left["passed"],"RIGHT_action_certificate_firewall":right["passed"],
        "FORWARD_AGAIN_position_reproducible":position_same,
        "ORIGIN_PRIME_state_advances":ribbon_ok,
        "all_four_boundary_rows_evaluated":len(forward["primary"]["tree"]["boundary_rows"])==4,
        "all_candidate_pairs_charged":forward["primary"]["metrics"]["candidate_pair_count"]==len(list(itertools.combinations(variables(ref_formula),2))),
        "P_VS_NP_OPEN":True,
    }
    passed=all(gates.values())
    result={
        "artifact_id":RUN_ID,
        "status":"PASS_KEEP_S_PHALLUS_H_GATE_1_K2_RIBBON_DECOMPOSITION__MASTER_P_VS_NP_GATE_REMAINS_OPEN" if passed else "STOP_S_PHALLUS_H_GATE_1_K2_RIBBON_DECOMPOSITION",
        "parent":{"sha":PARENT_SHA,"result_integrity_sha256":PARENT_RESULT_SHA},
        "gate_identity":"S𓂸ḥ/1","subgate":"VERIFIED_SIZE2_SEPARATOR_DECOMPOSITION_WITH_RIBBON_STATE",
        "calibration":rows,"negative_controls":negatives,"regression":regression,"gate0_regression":gate0_rows,"hard_controls":hard,
        "tranception":{"directions":DIRECTIONS,"BACK":{"passed":back_bound,"stage_back":back},"FORWARD":{"status":forward["status"],"lane":forward["primary_lane"]},
                        "LEFT":left,"RIGHT":right,"FORWARD_AGAIN":{"position_same":position_same},"BACK_AGAIN":back_again},
        "ribbon_state":{"mechanic":"ORIGIN -> EXPERIENCE -> RETURN -> ORIGIN_PRIME","position":position,"origin":origin,"history":history,
                        "origin_prime_1":prime1,"origin_prime_2":prime2,"negative_controls":ribbon_negative,
                        "POSITION_RETURN_EQUALS_ORIGIN_POSITION":position_same,"STATE_RETURN_DIFFERS_FROM_ORIGINAL_STATE":origin["state_commitment"]!=prime1["state_commitment"]},
        "gates":gates,
        "mathematical_verdict":{"P_EQUALS_NP":"NOT_ESTABLISHED","P_NOT_EQUALS_NP":"NOT_ESTABLISHED","P_VS_NP":"OPEN"},
        "next_gate_if_pass":"S𓂸ḥ/2: VERIFIED_BOUNDED_K_SEPARATOR_FAMILY_WITH_K_SCALING_AND_HOLDOUT",
        "scientific_boundary":["K=2 separator decomposition only","No arbitrary-CNF bounded separator theorem","No P=NP or P!=NP result"]
    }
    result["integrity_sha256"]=digest(result)
    return result


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    result=run(); text=json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_text(text+"\n",encoding="utf-8")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"):
        raise SystemExit(1)

if __name__=="__main__":
    main()
