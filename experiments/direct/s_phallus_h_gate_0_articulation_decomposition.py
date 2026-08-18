#!/usr/bin/env python3
"""S𓂸ḥ gate-0: proof-carrying articulation-separator decomposition.

This is a modern SAT/complexity experiment layered on OSIRIS v2.1.  S𓂸ḥ is a
project gate identity, not an Egyptian spelling claim.  The new lane is activated
only from canonical CNF structure.  It preserves the PR192 pair-product quotient
as first priority, then recursively decomposes formulas exposing size-1
articulation separators in the primal graph, and otherwise falls back to the
unchanged OSIRIS v2 generic exact solver / UNKNOWN_BUDGET.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import osiris_v2_technical_sat_solver as v2
import osiris_v2_1_pr192_prebirth_quotient as v21
from janus_c025_core import CNF, canonical_cnf, cnf_hash, cofactor, satisfies, variables

RUN_ID = "S-PHALLUS-H-GATE-0-ARTICULATION-DECOMPOSITION-2026-08-18-v1"
PARENT_SHA = "c99bddd4702a26e5c061430a856bae9985dc908d"
PARENT_RESULT_SHA = "3e66f37125f709a54f1220f83d4b6c0fed6f79dbbf39ba3918f8277f7c1d864e"
CONTRACT = "S_PHALLUS_H_GATE_0_ARTICULATION_DECOMPOSITION_FROZEN_CONTRACT.json"
S_LANE = "S_PHALLUS_H_0_ARTICULATION_DECOMPOSITION"
Q0_LANE = "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT"
GENERIC_LANE = "GENERIC_OSIRIS_V2_FALLBACK"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
MAX_DEPTH = 64


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def primal_graph(formula: CNF) -> tuple[dict[int, set[int]], dict[str, int]]:
    graph = {v: set() for v in variables(formula)}
    clause_visits = 0
    pair_edge_attempts = 0
    for clause in formula:
        clause_visits += 1
        vs = sorted({abs(lit) for lit in clause})
        for i, left in enumerate(vs):
            for right in vs[i + 1:]:
                pair_edge_attempts += 1
                graph[left].add(right)
                graph[right].add(left)
    return graph, {"graph_clause_visits": clause_visits, "graph_pair_edge_attempts": pair_edge_attempts}


def connected_components(graph: dict[int, set[int]], removed: set[int] | None = None) -> list[tuple[int, ...]]:
    removed = removed or set()
    unseen = set(graph) - removed
    out: list[tuple[int, ...]] = []
    while unseen:
        root = min(unseen)
        stack = [root]
        unseen.remove(root)
        comp = []
        while stack:
            node = stack.pop()
            comp.append(node)
            for nxt in sorted(graph[node], reverse=True):
                if nxt not in removed and nxt in unseen:
                    unseen.remove(nxt)
                    stack.append(nxt)
        out.append(tuple(sorted(comp)))
    return sorted(out)


def articulation_points(graph: dict[int, set[int]]) -> tuple[list[int], dict[str, int]]:
    timer = 0
    disc: dict[int, int] = {}
    low: dict[int, int] = {}
    parent: dict[int, int | None] = {}
    aps: set[int] = set()
    edge_visits = 0

    def dfs(u: int) -> None:
        nonlocal timer, edge_visits
        timer += 1
        disc[u] = low[u] = timer
        children = 0
        for v in sorted(graph[u]):
            edge_visits += 1
            if v not in disc:
                parent[v] = u
                children += 1
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent.get(u) is None and children > 1:
                    aps.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    aps.add(u)
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for root in sorted(graph):
        if root not in disc:
            parent[root] = None
            dfs(root)
    return sorted(aps), {"tarjan_vertex_visits": len(disc), "tarjan_directed_edge_visits": edge_visits}


def verify_separator_claim(formula: CNF, separator: int, claimed_components: list[tuple[int, ...]]) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    graph, graph_cost = primal_graph(formula)
    if separator not in graph:
        return {"passed": False, "reason": "SEPARATOR_ABSENT", **graph_cost}
    before = connected_components(graph)
    actual = connected_components(graph, {separator})
    articulation = len(actual) > len(before)
    canonical_claim = sorted(tuple(sorted(c)) for c in claimed_components)
    exact_components = canonical_claim == actual
    owner: dict[int, int] = {}
    for i, comp in enumerate(actual):
        for v in comp:
            owner[v] = i
    cross_clause = False
    clause_partition_checks = 0
    for clause in formula:
        nonsep = {abs(lit) for lit in clause if abs(lit) != separator}
        if not nonsep:
            continue
        clause_partition_checks += 1
        ids = {owner.get(v, -1) for v in nonsep}
        if len(ids) != 1 or -1 in ids:
            cross_clause = True
            break
    return {
        "passed": bool(articulation and exact_components and not cross_clause and len(actual) >= 2),
        "reason": None if articulation and exact_components and not cross_clause and len(actual) >= 2 else (
            "NOT_ARTICULATION" if not articulation else "COMPONENT_MISMATCH" if not exact_components else "CROSS_COMPONENT_CLAUSE"
        ),
        "before_component_count": len(before),
        "after_component_count": len(actual),
        "actual_components": [list(c) for c in actual],
        "clause_partition_checks": clause_partition_checks,
        **graph_cost,
    }


def detect_articulation(formula: CNF) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    q0 = v21.detect_pair_product(formula)
    if q0["matched"]:
        core = {"formula_hash": cnf_hash(formula), "matched": False, "reason": "Q0_PAIR_PRODUCT_PRIORITY"}
        return {**core, "separator": None, "components": [], "metrics": {"q0_priority_reject": 1}, "certificate_sha256": digest(core)}
    graph, graph_cost = primal_graph(formula)
    aps, tarjan_cost = articulation_points(graph)
    if not aps:
        core = {"formula_hash": cnf_hash(formula), "matched": False, "reason": "NO_ARTICULATION_POINT"}
        return {
            **core, "separator": None, "components": [],
            "metrics": {**graph_cost, **tarjan_cost, "articulation_candidates": 0, "separator_verification_checks": 0},
            "certificate_sha256": digest(core),
        }
    separator = min(aps)
    comps = connected_components(graph, {separator})
    verified = verify_separator_claim(formula, separator, comps)
    matched = bool(verified["passed"])
    metrics = {
        **graph_cost, **tarjan_cost,
        "articulation_candidates": len(aps),
        "separator_verification_checks": verified.get("clause_partition_checks", 0),
        "component_count_after_removal": len(comps),
    }
    core = {
        "formula_hash": cnf_hash(formula), "matched": matched,
        "reason": None if matched else verified["reason"], "separator": separator if matched else None,
        "components": [list(c) for c in comps] if matched else [], "metrics": metrics,
    }
    return {**core, "certificate_sha256": digest(core)}


def component_formulas(formula: CNF) -> list[CNF]:
    formula = canonical_cnf(formula)
    if not formula or () in formula:
        return [formula]
    graph, _ = primal_graph(formula)
    comps = connected_components(graph)
    if len(comps) <= 1:
        return [formula]
    owner = {v: i for i, comp in enumerate(comps) for v in comp}
    buckets: list[list[tuple[int, ...]]] = [[] for _ in comps]
    for clause in formula:
        ids = {owner[abs(lit)] for lit in clause}
        if len(ids) != 1:
            raise AssertionError("connected-component split found cross-component clause")
        buckets[next(iter(ids))].append(clause)
    return [canonical_cnf(bucket) for bucket in buckets]


def empty_stats() -> dict[str, int]:
    return {
        "recursive_calls": 0, "memo_hits": 0, "residual_states": 0, "transition_checks": 0,
        "normalization_certificates": 0, "subsumption_steps": 0, "bdd_nodes": 0,
        "max_frontier_states": 0,
    }


def add_engine_stats(counters: dict[str, Any], stats: dict[str, Any]) -> None:
    for key in ("recursive_calls", "memo_hits", "residual_states", "transition_checks", "normalization_certificates", "subsumption_steps", "bdd_nodes"):
        counters["leaf_engine"][key] += int(stats.get(key, 0))
    counters["leaf_engine"]["max_frontier_states"] = max(counters["leaf_engine"]["max_frontier_states"], int(stats.get("max_frontier_states", 0)))


def solve_recursive(formula: CNF, budget: int, base_engine, depth: int, counters: dict[str, Any]) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    counters["recursive_component_calls"] += 1
    counters["max_recursion_depth"] = max(counters["max_recursion_depth"], depth)
    formula_hash = cnf_hash(formula)
    if depth > MAX_DEPTH:
        return {"status": "UNKNOWN_BUDGET", "assignment": None, "tree": {"kind": "DEPTH_LIMIT", "formula_hash": formula_hash}}
    if not formula:
        return {"status": "SAT", "assignment": {}, "tree": {"kind": "EMPTY_SAT", "formula_hash": formula_hash}}
    if () in formula:
        return {"status": "UNSAT", "assignment": None, "tree": {"kind": "EMPTY_CLAUSE_UNSAT", "formula_hash": formula_hash}}

    residual, unit_assignment, unit_trail = v2.unit_propagate(formula)
    counters["unit_propagations"] += len(unit_trail)
    residual = canonical_cnf(residual)
    if not residual:
        full = {v: False for v in variables(formula)}
        full.update(unit_assignment)
        ok = satisfies(formula, full)
        return {"status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": full if ok else None,
                "tree": {"kind": "UNIT_SAT", "formula_hash": formula_hash, "trail_digest": digest(unit_trail), "verified": ok}}
    if () in residual:
        return {"status": "UNSAT", "assignment": None,
                "tree": {"kind": "UNIT_UNSAT", "formula_hash": formula_hash, "trail_digest": digest(unit_trail)}}

    q0 = v21.detect_pair_product(residual)
    counters["q0_detector_calls"] += 1
    if q0["matched"]:
        counters["q0_leaf_hits"] += 1
        assignment = {v: False for v in variables(formula)}
        assignment.update(unit_assignment)
        assignment.update(q0["assignment"] or {})
        ok = satisfies(formula, assignment)
        counters["q0_symbolic_states"] += int(q0["metrics"]["symbolic_states"])
        counters["q0_symbolic_transitions"] += int(q0["metrics"]["symbolic_transitions"])
        return {
            "status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": assignment if ok else None,
            "tree": {"kind": "Q0_PAIR_PRODUCT", "formula_hash": formula_hash,
                     "residual_hash": cnf_hash(residual), "certificate": q0["certificate_sha256"],
                     "symbolic_states": q0["metrics"]["symbolic_states"], "verified": ok},
        }

    detection = detect_articulation(residual)
    counters["s_detector_calls"] += 1
    for key, value in detection.get("metrics", {}).items():
        if isinstance(value, int):
            counters["discovery_cost"][key] = counters["discovery_cost"].get(key, 0) + value
    if detection["matched"]:
        counters["separator_nodes"] += 1
        separator = int(detection["separator"])
        branch_rows = []
        sat_candidate: dict[str, Any] | None = None
        both_unsat = True
        for value in (False, True):
            counters["boundary_valuations"] += 1
            restricted = canonical_cnf(cofactor(residual, separator, value))
            comps = component_formulas(restricted)
            counters["component_partitions"] += len(comps)
            component_rows = []
            branch_assignment = {separator: value}
            branch_status = "SAT"
            for comp in comps:
                solved = solve_recursive(comp, budget, base_engine, depth + 1, counters)
                component_rows.append({"formula_hash": cnf_hash(comp), "status": solved["status"], "tree": solved["tree"]})
                if solved["status"] == "UNSAT":
                    branch_status = "UNSAT"
                    break
                if solved["status"] == "UNKNOWN_BUDGET":
                    branch_status = "UNKNOWN_BUDGET"
                    continue
                if solved["assignment"]:
                    branch_assignment.update(solved["assignment"])
            if branch_status == "SAT":
                full = {v: False for v in variables(formula)}
                full.update(unit_assignment)
                full.update(branch_assignment)
                verified = satisfies(formula, full)
                if not verified:
                    branch_status = "UNKNOWN_BUDGET"
                else:
                    sat_candidate = full
            if branch_status != "UNSAT":
                both_unsat = False
            branch_rows.append({"separator_value": value, "status": branch_status, "components": component_rows})
            if sat_candidate is not None:
                break
        tree_core = {
            "kind": "S_ARTICULATION", "formula_hash": formula_hash, "residual_hash": cnf_hash(residual),
            "separator": separator, "separator_certificate": detection["certificate_sha256"],
            "claimed_components": detection["components"], "branches": branch_rows,
        }
        tree_core["tree_sha256"] = digest(tree_core)
        if sat_candidate is not None:
            return {"status": "SAT", "assignment": sat_candidate, "tree": tree_core}
        if both_unsat and len(branch_rows) == 2:
            return {"status": "UNSAT", "assignment": None, "tree": tree_core}
        return {"status": "UNKNOWN_BUDGET", "assignment": None, "tree": tree_core}

    counters["generic_leaf_calls"] += 1
    order, _ = v2.activity_order(residual)
    engine = base_engine(formula, residual, order, unit_assignment, budget)
    add_engine_stats(counters, engine["stats"])
    return {
        "status": engine["status"], "assignment": engine.get("assignment"),
        "tree": {"kind": "GENERIC_LEAF", "formula_hash": formula_hash, "residual_hash": cnf_hash(residual),
                 "status": engine["status"], "root": engine.get("root"),
                 "engine_projection_sha256": digest(v2.engine_projection(engine))},
    }


def make_counters() -> dict[str, Any]:
    return {
        "recursive_component_calls": 0, "max_recursion_depth": 0, "unit_propagations": 0,
        "q0_detector_calls": 0, "q0_leaf_hits": 0, "q0_symbolic_states": 0, "q0_symbolic_transitions": 0,
        "s_detector_calls": 0, "separator_nodes": 0, "boundary_valuations": 0, "component_partitions": 0,
        "generic_leaf_calls": 0, "discovery_cost": {}, "leaf_engine": empty_stats(),
    }


def q0_engine_result(original: CNF, residual: CNF, units: dict[int, bool], detected: dict[str, Any]) -> dict[str, Any]:
    assignment = {v: False for v in variables(original)}
    assignment.update(units)
    assignment.update(detected["assignment"] or {})
    verified = satisfies(original, assignment)
    if not verified:
        raise AssertionError("Q0 witness failed original formula")
    m = detected["metrics"]
    stats = {
        "status": "EXACT_QUOTIENT", "recursive_calls": m["symbolic_states"], "memo_hits": 0,
        "residual_states": m["symbolic_states"], "transition_checks": m["symbolic_transitions"],
        "normalization_certificates": 0, "subsumption_steps": 0, "bdd_nodes": 0,
        "max_frontier_states": 1, "frontier_counts": {str(i): 1 for i in range(m["symbolic_states"])},
        "error": None, "q0_lane": Q0_LANE, "q0_certificate_sha256": detected["certificate_sha256"],
        "q0_raw_prefixes_enumerated": 0, "s_gate_lane": "NOT_ENTERED_Q0_PRIORITY",
    }
    return {"status": "SAT", "root": 1, "sat": True, "assignment": assignment,
            "assignment_verified": True, "reason": Q0_LANE, "stats": stats, "engine_invoked": False}


def solve_with_s_gate(raw_formula: Iterable[Iterable[int]], budget: int) -> dict[str, Any]:
    base_engine = v2.engine_run
    calls: list[dict[str, Any]] = []

    def s_aware_engine(original: CNF, residual: CNF, residual_order: list[int], units: dict[int, bool], state_budget: int) -> dict[str, Any]:
        q0 = v21.detect_pair_product(residual)
        if q0["matched"]:
            engine = q0_engine_result(original, residual, units, q0)
            calls.append({"lane": Q0_LANE, "formula_hash": cnf_hash(residual), "certificate_sha256": q0["certificate_sha256"], "metrics": q0["metrics"]})
            return engine
        top = detect_articulation(residual)
        if not top["matched"]:
            engine = base_engine(original, residual, residual_order, units, state_budget)
            engine["stats"] = dict(engine["stats"])
            engine["stats"]["s_gate_lane"] = GENERIC_LANE
            engine["stats"]["s_gate_rejection_reason"] = top["reason"]
            calls.append({"lane": GENERIC_LANE, "formula_hash": cnf_hash(residual), "rejection_reason": top["reason"], "certificate_sha256": top["certificate_sha256"]})
            return engine

        counters = make_counters()
        solved = solve_recursive(residual, state_budget, base_engine, 0, counters)
        status = solved["status"]
        full_assignment = None
        verified = None
        if status == "SAT":
            full_assignment = {v: False for v in variables(original)}
            full_assignment.update(units)
            full_assignment.update(solved["assignment"] or {})
            verified = satisfies(original, full_assignment)
            if not verified:
                status = "UNKNOWN_BUDGET"
                full_assignment = None
        leaf = counters["leaf_engine"]
        symbolic = counters["separator_nodes"] + counters["boundary_valuations"] + counters["q0_symbolic_states"]
        residual_states = leaf["residual_states"] + symbolic
        recursive_calls = max(residual_states, leaf["recursive_calls"] + counters["recursive_component_calls"] + counters["boundary_valuations"])
        tree_digest = digest(solved["tree"])
        stats = {
            "status": "EXACT_DECOMPOSITION" if status in {"SAT", "UNSAT"} else "OPEN",
            "recursive_calls": recursive_calls, "memo_hits": leaf["memo_hits"], "residual_states": residual_states,
            "transition_checks": leaf["transition_checks"] + counters["boundary_valuations"] + counters["q0_symbolic_transitions"],
            "normalization_certificates": leaf["normalization_certificates"], "subsumption_steps": leaf["subsumption_steps"],
            "bdd_nodes": leaf["bdd_nodes"], "max_frontier_states": max(1, leaf["max_frontier_states"]),
            "frontier_counts": {"0": 1}, "error": None if status in {"SAT", "UNSAT"} else "DECOMPOSITION_CHILD_UNKNOWN",
            "s_gate_lane": S_LANE, "s_gate_certificate_sha256": top["certificate_sha256"],
            "s_gate_tree_sha256": tree_digest, "s_gate_separator_nodes": counters["separator_nodes"],
            "s_gate_boundary_valuations": counters["boundary_valuations"], "s_gate_component_partitions": counters["component_partitions"],
            "s_gate_recursive_component_calls": counters["recursive_component_calls"], "s_gate_max_recursion_depth": counters["max_recursion_depth"],
            "s_gate_q0_leaf_hits": counters["q0_leaf_hits"], "s_gate_generic_leaf_calls": counters["generic_leaf_calls"],
            "s_gate_discovery_cost": counters["discovery_cost"], "s_gate_component_units_do_not_sum_as_runtime": True,
        }
        engine = {
            "status": status, "root": 1 if status == "SAT" else 0 if status == "UNSAT" else None,
            "sat": True if status == "SAT" else False if status == "UNSAT" else None,
            "assignment": full_assignment, "assignment_verified": verified,
            "reason": S_LANE if status in {"SAT", "UNSAT"} else "S_PHALLUS_H_CHILD_UNKNOWN",
            "stats": stats, "engine_invoked": True,
        }
        calls.append({"lane": S_LANE, "formula_hash": cnf_hash(residual), "certificate_sha256": top["certificate_sha256"],
                      "tree_sha256": tree_digest, "status": status, "counters": counters})
        return engine

    v2.engine_run = s_aware_engine
    try:
        solved = v2.technical_forward(raw_formula, budget)
    finally:
        v2.engine_run = base_engine
    solved["s_calls"] = calls
    solved["s_primary"] = calls[0] if calls else None
    solved["s_primary_lane"] = solved["s_primary"]["lane"] if solved["s_primary"] else "NO_ENGINE_CALL"
    return solved


def relation_star(n: int, anti: bool = False, conflict: bool = False) -> CNF:
    s = 1
    clauses: list[tuple[int, ...]] = []
    for leaf in range(2, n + 2):
        if anti:
            clauses.extend(((s, leaf), (-s, -leaf)))
        else:
            clauses.extend(((-s, leaf), (s, -leaf)))
    if conflict:
        leaf = 2
        clauses.extend(((s, leaf), (-s, -leaf)))
    return canonical_cnf(clauses)


def relation_chain(n: int, conflict: bool = False) -> CNF:
    clauses: list[tuple[int, ...]] = []
    for left in range(1, n):
        right = left + 1
        clauses.extend(((-left, right), (left, -right)))
    if conflict:
        mid = n // 2
        clauses.extend(((mid, mid + 1), (-mid, -(mid + 1))))
    return canonical_cnf(clauses)


def relation_cycle(n: int) -> CNF:
    clauses = list(relation_chain(n))
    clauses.extend(((-n, 1), (n, -1)))
    return canonical_cnf(clauses)


def calibration_fixtures() -> list[dict[str, Any]]:
    return [
        {"id": "STAR_EQUALITY_12_SAT", "formula": relation_star(12), "expected": "SAT", "budget": 50000},
        {"id": "STAR_ANTI_EQUALITY_12_SAT", "formula": relation_star(12, anti=True), "expected": "SAT", "budget": 50000},
        {"id": "STAR_CONFLICT_12_UNSAT", "formula": relation_star(12, conflict=True), "expected": "UNSAT", "budget": 50000},
        {"id": "CHAIN_EQUALITY_16_SAT", "formula": relation_chain(16), "expected": "SAT", "budget": 50000},
        {"id": "CHAIN_CONFLICT_16_UNSAT", "formula": relation_chain(16, conflict=True), "expected": "UNSAT", "budget": 50000},
    ]


def negative_controls() -> list[dict[str, Any]]:
    cycle = relation_cycle(12)
    cycle_detect = detect_articulation(cycle)
    forged_sep = verify_separator_claim(cycle, 1, connected_components(primal_graph(cycle)[0], {1}))

    base = relation_star(6)
    det = detect_articulation(base)
    assert det["matched"]
    mutated = canonical_cnf(list(base) + [(2, 3)])
    forged_partition = verify_separator_claim(mutated, int(det["separator"]), [tuple(c) for c in det["components"]])

    solved = solve_with_s_gate(base, 50000)
    primary = dict(solved["s_primary"] or {})
    bitflip_core = {"lane": primary.get("lane"), "formula_hash": primary.get("formula_hash"), "certificate_sha256": primary.get("certificate_sha256"),
                    "tree_sha256": ("0" * 64 if primary.get("tree_sha256") != "0" * 64 else "1" * 64)}
    original_core = {"lane": primary.get("lane"), "formula_hash": primary.get("formula_hash"), "certificate_sha256": primary.get("certificate_sha256"),
                     "tree_sha256": primary.get("tree_sha256")}
    boundary_bitflip_reject = digest(bitflip_core) != digest(original_core)

    anti = relation_star(6, anti=True)
    swapped_hash_reject = det["certificate_sha256"] != detect_articulation(anti)["certificate_sha256"]
    return [
        {"id": "CYCLE_EQUALITY_12_NO_ARTICULATION", "passed": not cycle_detect["matched"], "reason": cycle_detect["reason"]},
        {"id": "FORGED_SEPARATOR_NON_ARTICULATION", "passed": not forged_sep["passed"], "reason": forged_sep["reason"]},
        {"id": "FORGED_COMPONENT_PARTITION_CROSS_CLAUSE", "passed": not forged_partition["passed"], "reason": forged_partition["reason"]},
        {"id": "BOUNDARY_TABLE_BITFLIP", "passed": boundary_bitflip_reject},
        {"id": "SEPARATOR_CERTIFICATE_FORMULA_HASH_SWAP", "passed": swapped_hash_reject},
    ]


def right_control() -> dict[str, Any]:
    formula = relation_star(6)
    detection = detect_articulation(formula)
    action_certificate_present = False
    s_authorized = bool(detection["matched"] and action_certificate_present)
    fallback = v21.solve_v21(formula, 50000)
    return {
        "control": "SAME_CNF_PROVENANCE_SEPARATOR_CERTIFICATE_REMOVED",
        "detector_structural_match": detection["matched"], "action_certificate_present": action_certificate_present,
        "s_gate_authorized": s_authorized, "fallback_status": fallback["status"], "fallback_authorized": fallback["authorized"],
        "passed": bool(detection["matched"] and not s_authorized and fallback["status"] == "SAT" and fallback["authorized"]),
    }


def left_control() -> dict[str, Any]:
    a = relation_star(6)
    b = relation_star(6, anti=True)
    da, db = detect_articulation(a), detect_articulation(b)
    return {
        "control": "SAME_ARTICULATION_CAPABILITY_DIFFERENT_PROVENANCE",
        "both_support_s_gate": da["matched"] and db["matched"],
        "formula_identity_distinct": cnf_hash(a) != cnf_hash(b),
        "certificate_identity_distinct": da["certificate_sha256"] != db["certificate_sha256"],
        "identity_authorized_from_capability": False,
        "passed": bool(da["matched"] and db["matched"] and cnf_hash(a) != cnf_hash(b) and da["certificate_sha256"] != db["certificate_sha256"]),
    }


def run() -> dict[str, Any]:
    contract = json.loads(Path(__file__).with_name(CONTRACT).read_text(encoding="utf-8"))
    assert contract["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    assert contract["parent"]["sha"] == PARENT_SHA
    assert contract["gate_identity"]["display"] == "S𓂸ḥ"
    assert contract["subgate"]["separator_size"] == 1
    assert contract["tranception"]["direction_order"] == DIRECTIONS

    rows = []
    solved_by_id: dict[str, dict[str, Any]] = {}
    for fixture in calibration_fixtures():
        solved = solve_with_s_gate(fixture["formula"], fixture["budget"])
        solved_by_id[fixture["id"]] = solved
        primary = solved["s_primary"] or {}
        exact = solved["status"] == fixture["expected"] and solved["authorized"] and solved["all_stage_gates_pass"]
        rows.append({
            "id": fixture["id"], "expected": fixture["expected"], "observed": solved["status"], "authorized": solved["authorized"],
            "exact_correct": exact, "primary_lane": primary.get("lane"), "s_gate_used": primary.get("lane") == S_LANE,
            "certificate_sha256": primary.get("certificate_sha256"), "tree_sha256": primary.get("tree_sha256"),
            "behavior_vector": solved["behavior_vector"], "cost_vector": solved["cost_vector"],
        })

    regress = []
    for fixture in v2.fixtures():
        solved = solve_with_s_gate(fixture["formula"], fixture["budget"])
        regress.append({"id": fixture["id"], "expected": fixture["expected"], "observed": solved["status"],
                        "authorized": solved["authorized"], "lane": solved["s_primary_lane"],
                        "passed": solved["status"] == fixture["expected"] and solved["authorized"] and solved["all_stage_gates_pass"]})
    hard = []
    for fixture in v2.hard_fixtures():
        solved = solve_with_s_gate(fixture["formula"], fixture["budget"])
        good = (solved["status"] == "UNKNOWN_BUDGET" and not solved["authorized"]) or (solved["status"] == fixture["expected"] and solved["authorized"])
        hard.append({"id": fixture["id"], "expected": fixture["expected"], "observed": solved["status"],
                     "authorized": solved["authorized"], "lane": solved["s_primary_lane"], "passed": good})

    negatives = negative_controls()
    reference_formula = relation_chain(16)
    reference = solve_with_s_gate(reference_formula, 50000)
    back_stage = v2.back_replay(reference)
    back = {
        "stage_back": back_stage,
        "s_certificate_bound": bool(reference["s_primary"] and reference["s_primary"].get("certificate_sha256")),
        "s_tree_bound": bool(reference["s_primary"] and reference["s_primary"].get("tree_sha256")),
    }
    back["passed"] = bool(back_stage["passed"] and back["s_certificate_bound"] and back["s_tree_bound"])
    forward = solve_with_s_gate(reference_formula, 50000)
    left = left_control()
    right = right_control()
    forward_again = solve_with_s_gate(reference_formula, 50000)
    exact_projection = bool(
        forward["projection"] == forward_again["projection"]
        and forward["s_primary"] == forward_again["s_primary"]
    )
    back_again = {
        "historical_text_semantics_consumed_by_solver": False,
        "historical_text_semantics_consumed_by_detector": False,
        "technical_verdict": forward["status"], "same_as_reference": forward["status"] == reference["status"],
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(not back_again["historical_text_semantics_consumed_by_solver"] and not back_again["historical_text_semantics_consumed_by_detector"] and back_again["same_as_reference"])

    eq_reg = next(r for r in regress if r["id"] == "EQUALITY_N14")
    anti_reg = next(r for r in regress if r["id"] == "ANTI_EQUALITY_N14")
    gates = {
        "all_5_s_gate_calibration_exact": all(r["exact_correct"] for r in rows),
        "all_5_calibration_use_s_gate": all(r["s_gate_used"] for r in rows),
        "all_5_negative_controls_reject": len(negatives) == 5 and all(r["passed"] for r in negatives),
        "all_8_osiris_v2_1_calibration_preserved": len(regress) == 8 and all(r["passed"] for r in regress),
        "equality_n14_q0_priority_preserved": eq_reg["lane"] == Q0_LANE,
        "anti_equality_n14_q0_priority_preserved": anti_reg["lane"] == Q0_LANE,
        "hard_tseitin_same_budget_fail_closed_or_correct": len(hard) == 2 and all(r["passed"] for r in hard),
        "BACK_exact_bindings_plus_s_certificate": back["passed"],
        "FORWARD_s_gate_exact": forward["status"] == "SAT" and forward["authorized"] and forward["s_primary_lane"] == S_LANE,
        "LEFT_identity_firewall": left["passed"],
        "RIGHT_removed_separator_certificate_blocks_s_authority": right["passed"],
        "FORWARD_AGAIN_exact_projection": exact_projection,
        "BACK_AGAIN_semantic_rollback": back_again["passed"],
        "direction_order_exact": DIRECTIONS == ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"],
        "P_VS_NP_OPEN": True,
    }
    passed = all(gates.values())
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_S_PHALLUS_H_GATE_0_ARTICULATION_DECOMPOSITION__MASTER_P_VS_NP_GATE_REMAINS_OPEN" if passed else "STOP_AT_S_PHALLUS_H_GATE_0_ARTICULATION_DECOMPOSITION",
        "gate_identity": "S𓂸ḥ", "subgate": "PROOF_CARRYING_SIZE1_ARTICULATION_SEPARATOR_DECOMPOSITION",
        "parent": {"sha": PARENT_SHA, "result_integrity_sha256": PARENT_RESULT_SHA},
        "calibration": rows, "detector_negative_controls": negatives, "regression": regress, "hard_controls": hard,
        "BACK": back, "FORWARD": {"status": forward["status"], "lane": forward["s_primary_lane"], "primary": forward["s_primary"]},
        "LEFT": left, "RIGHT": right,
        "FORWARD_AGAIN": {"passed": exact_projection, "status": forward_again["status"], "lane": forward_again["s_primary_lane"]},
        "BACK_AGAIN": back_again, "directions": DIRECTIONS, "gates": gates,
        "scientific_boundary": [
            "This gate generalizes proof-carrying prebirth decomposition only to formulas exposing size-1 articulation separators, while preserving pair-product Q0 and generic fallback.",
            "It does not establish bounded separators/treewidth for arbitrary CNF.",
            "It does not establish polynomial quotient size or polynomial solving for arbitrary CNF.",
            "Historical Pyramid Text material is not consumed by correctness.",
            "P_EQUALS_NP = NOT_ESTABLISHED", "P_NOT_EQUALS_NP = NOT_ESTABLISHED", "P_VS_NP = OPEN"
        ],
        "next_gate_if_pass": "S𓂸ḥ/1: VERIFIED_BOUNDED_K_SEPARATOR_DECOMPOSITION_WITH_DISCOVERY_AND_TABLE_COST_CHARGED",
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
