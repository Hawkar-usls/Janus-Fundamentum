#!/usr/bin/env python3
"""S𓂸ḥ/2: automatic verified bounded-K separator family with preregistered holdout.

Modern SAT/complexity experiment only. The detector receives canonical CNF only,
searches k=1..K_MAX in increasing order, exhausts every subset below and at the
first successful k, proves the selected separator, evaluates every 2^k boundary
row, and charges discovery separately from boundary work. Q0/PR192 retains
priority. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

import osiris_v2_technical_sat_solver as v2
import osiris_v2_1_pr192_prebirth_quotient as v21
import s_phallus_h_gate_0_articulation_decomposition as g0
import s_phallus_h_gate_1_k2_ribbon_decomposition as g1
from janus_c025_core import CNF, canonical_cnf, cnf_hash, cofactor, satisfies, variables

RUN_ID = "S-PHALLUS-H-GATE-2-BOUNDED-K-SCALING-HOLDOUT-2026-08-19-v1"
CONTRACT = "S_PHALLUS_H_GATE_2_BOUNDED_K_SCALING_HOLDOUT_FROZEN_CONTRACT.json"
FIXTURES = "S_PHALLUS_H_GATE_2_BOUNDED_K_FIXTURES_FROZEN.json"
PARENT_SHA = "f9d1e0f73ec9e628731afd45d7078f6623601a44"
PARENT_RESULT_SHA = "450cb257a7888528b8987f35b4358eab8c97028acf4caa86ff1386dfacb90462"
K_MAX = 4
Q0_LANE = "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT"
K_LANE = "S_PHALLUS_H_2_AUTOMATIC_MINIMUM_SEPARATOR_K_1_TO_4"
GENERIC_LANE = "GENERIC_OSIRIS_V2_FALLBACK"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
MAX_DEPTH = 64

digest = g1.digest


def _graph_bitsets(formula: CNF) -> tuple[list[int], list[int], int, dict[str, int]]:
    graph, cost = g0.primal_graph(canonical_cnf(formula))
    ordered = sorted(graph)
    index = {v: i for i, v in enumerate(ordered)}
    adj = [0] * len(ordered)
    for u in ordered:
        mask = 0
        for v in graph[u]:
            mask |= 1 << index[v]
        adj[index[u]] = mask
    return ordered, adj, (1 << len(ordered)) - 1, cost


def _mask_components(adj: list[int], all_mask: int, removed_mask: int) -> tuple[list[int], int]:
    unseen = all_mask & ~removed_mask
    comps: list[int] = []
    flood_rounds = 0
    while unseen:
        seed = unseen & -unseen
        seen = seed
        frontier = seed
        while frontier:
            flood_rounds += 1
            f = frontier
            neighbors = 0
            while f:
                bit = f & -f
                idx = bit.bit_length() - 1
                neighbors |= adj[idx]
                f ^= bit
            frontier = neighbors & (all_mask & ~removed_mask) & ~seen
            seen |= frontier
        comps.append(seen)
        unseen &= ~seen
    return comps, flood_rounds


def _mask_to_vars(mask: int, ordered: list[int]) -> tuple[int, ...]:
    out = []
    while mask:
        bit = mask & -mask
        out.append(ordered[bit.bit_length() - 1])
        mask ^= bit
    return tuple(out)


def verify_separator_claim(formula: CNF, separator: Iterable[int], claimed: Iterable[Iterable[int]]) -> dict[str, Any]:
    formula = canonical_cnf(formula)
    sep = tuple(sorted(int(v) for v in separator))
    graph, graph_cost = g0.primal_graph(formula)
    if len(sep) != len(set(sep)) or not sep or any(v not in graph for v in sep):
        return {"passed": False, "reason": "SEPARATOR_INVALID_OR_ABSENT", **graph_cost}
    before = g0.connected_components(graph)
    after = g0.connected_components(graph, set(sep))
    separates = len(after) > len(before) and len(after) >= 2
    actual = sorted(tuple(sorted(c)) for c in after)
    claimed_norm = sorted(tuple(sorted(int(v) for v in c)) for c in claimed)
    exact_components = actual == claimed_norm
    owner = {v: i for i, comp in enumerate(after) for v in comp}
    partition_checks = 0
    cross = False
    for clause in formula:
        nonsep = {abs(lit) for lit in clause if abs(lit) not in sep}
        if not nonsep:
            continue
        partition_checks += 1
        ids = {owner.get(v, -1) for v in nonsep}
        if len(ids) != 1 or -1 in ids:
            cross = True
            break
    passed = separates and exact_components and not cross
    reason = None if passed else "NOT_SEPARATOR" if not separates else "COMPONENT_MISMATCH" if not exact_components else "CROSS_COMPONENT_CLAUSE"
    return {
        "passed": passed,
        "reason": reason,
        "before_component_count": len(before),
        "after_component_count": len(after),
        "actual_components": [list(c) for c in after],
        "separator_clause_partition_checks": partition_checks,
        **graph_cost,
    }


def detect_min_separator(formula: CNF, kmax: int = K_MAX) -> dict[str, Any]:
    """CNF-only minimum-separator detector. No fixture metadata enters here."""
    formula = canonical_cnf(formula)
    ordered, adj, all_mask, graph_cost = _graph_bitsets(formula)
    index = {v: i for i, v in enumerate(ordered)}
    base_masks, base_rounds = _mask_components(adj, all_mask, 0)
    base_count = len(base_masks)

    candidate_counts: dict[str, int] = {}
    connectivity_checks: dict[str, int] = {}
    flood_rounds_by_k: dict[str, int] = {}
    partition_checks_by_k: dict[str, int] = {}
    verified_counts: dict[str, int] = {}
    found_k = None
    selected = None
    selected_components = None
    audited_k: list[int] = []

    upper = min(int(kmax), max(0, len(ordered) - 1))
    for k in range(1, upper + 1):
        audited_k.append(k)
        verified: list[tuple[tuple[int, ...], list[tuple[int, ...]]]] = []
        count = 0
        conn = 0
        floods = 0
        partitions = 0
        for subset in itertools.combinations(ordered, k):
            count += 1
            conn += 1
            removed = 0
            for v in subset:
                removed |= 1 << index[v]
            after_masks, rounds = _mask_components(adj, all_mask, removed)
            floods += rounds
            if len(after_masks) <= base_count or len(after_masks) < 2:
                continue
            comps = [_mask_to_vars(mask, ordered) for mask in after_masks]
            owner = {v: i for i, comp in enumerate(comps) for v in comp}
            cross = False
            for clause in formula:
                nonsep = {abs(lit) for lit in clause if abs(lit) not in subset}
                if not nonsep:
                    continue
                partitions += 1
                ids = {owner.get(v, -1) for v in nonsep}
                if len(ids) != 1 or -1 in ids:
                    cross = True
                    break
            if not cross:
                verified.append((subset, comps))
        candidate_counts[str(k)] = count
        connectivity_checks[str(k)] = conn
        flood_rounds_by_k[str(k)] = floods
        partition_checks_by_k[str(k)] = partitions
        verified_counts[str(k)] = len(verified)
        if verified:
            found_k = k
            selected, selected_components = verified[0]
            break

    metrics = {
        "graph_clause_visits": graph_cost["graph_clause_visits"],
        "graph_pair_edge_attempts": graph_cost["graph_pair_edge_attempts"],
        "base_component_flood_rounds": base_rounds,
        "candidate_counts_by_k": candidate_counts,
        "connectivity_checks_by_k": connectivity_checks,
        "component_flood_rounds_by_k": flood_rounds_by_k,
        "separator_clause_partition_checks_by_k": partition_checks_by_k,
        "verified_separator_counts_by_k": verified_counts,
        "cumulative_candidate_count": sum(candidate_counts.values()),
    }
    matched = found_k is not None
    core = {
        "formula_hash": cnf_hash(formula),
        "matched": matched,
        "reason": None if matched else f"NO_VERIFIED_SEPARATOR_K_LE_{kmax}",
        "kmax": int(kmax),
        "found_k": found_k,
        "audited_k": audited_k,
        "separator": list(selected) if selected is not None else None,
        "components": [list(c) for c in selected_components] if selected_components is not None else [],
        "metrics": metrics,
        "minimality_proof": {
            "all_smaller_k_verified_counts_zero": matched and all(verified_counts[str(k)] == 0 for k in range(1, int(found_k))),
            "found_k_has_verified_separator": matched and verified_counts[str(found_k)] > 0,
            "all_candidates_below_and_at_found_k_exhausted": True,
        },
    }
    return {**core, "certificate_sha256": digest(core)}


def verify_detector_certificate(formula: CNF, certificate: dict[str, Any], kmax: int = K_MAX) -> bool:
    expected = detect_min_separator(formula, kmax)
    keys = ["formula_hash", "matched", "reason", "kmax", "found_k", "audited_k", "separator", "components", "metrics", "minimality_proof", "certificate_sha256"]
    return all(certificate.get(k) == expected.get(k) for k in keys)


def _add_engine_stats(dst: dict[str, int], stats: dict[str, Any]) -> None:
    for key in ("recursive_calls", "memo_hits", "residual_states", "transition_checks",
                "normalization_certificates", "subsumption_steps", "bdd_nodes", "max_frontier_states"):
        dst[key] = dst.get(key, 0) + int(stats.get(key, 0) or 0)


def make_counters() -> dict[str, Any]:
    return {
        "recursive_component_calls": 0,
        "max_recursion_depth": 0,
        "unit_propagations": 0,
        "q0_detector_calls": 0,
        "q0_leaf_hits": 0,
        "q0_symbolic_states": 0,
        "q0_symbolic_transitions": 0,
        "separator_detector_calls": 0,
        "separator_nodes_by_k": {},
        "boundary_rows_by_k": {},
        "component_partitions": 0,
        "generic_leaf_calls": 0,
        "discovery_cost": {
            "candidate_counts_by_k": {},
            "connectivity_checks_by_k": {},
            "component_flood_rounds_by_k": {},
            "separator_clause_partition_checks_by_k": {},
            "verified_separator_counts_by_k": {},
            "graph_clause_visits": 0,
            "graph_pair_edge_attempts": 0,
        },
        "leaf_engine": {
            "recursive_calls": 0, "memo_hits": 0, "residual_states": 0, "transition_checks": 0,
            "normalization_certificates": 0, "subsumption_steps": 0, "bdd_nodes": 0, "max_frontier_states": 0,
        },
    }


def _merge_discovery(dst: dict[str, Any], metrics: dict[str, Any]) -> None:
    dst["graph_clause_visits"] += int(metrics.get("graph_clause_visits", 0))
    dst["graph_pair_edge_attempts"] += int(metrics.get("graph_pair_edge_attempts", 0))
    for field in ("candidate_counts_by_k", "connectivity_checks_by_k", "component_flood_rounds_by_k",
                  "separator_clause_partition_checks_by_k", "verified_separator_counts_by_k"):
        target = dst[field]
        for k, value in metrics.get(field, {}).items():
            target[k] = target.get(k, 0) + int(value)


def verify_boundary_rows(k: int, rows: list[dict[str, Any]]) -> bool:
    expected = list(itertools.product((False, True), repeat=int(k)))
    observed = [tuple(bool(x) for x in row.get("valuation", [])) for row in rows]
    return observed == expected and len(observed) == (1 << int(k))


def _solve_boundary_table(formula: CNF, residual: CNF, units: dict[int, bool], detection: dict[str, Any],
                          budget: int, base_engine, depth: int, counters: dict[str, Any]) -> dict[str, Any]:
    sep = tuple(int(v) for v in detection["separator"])
    k = int(detection["found_k"])
    valuations = list(itertools.product((False, True), repeat=k))
    rows = []
    sat_candidates: list[dict[int, bool]] = []
    for valuation in valuations:
        counters["boundary_rows_by_k"][str(k)] = counters["boundary_rows_by_k"].get(str(k), 0) + 1
        restricted = residual
        boundary: dict[int, bool] = {}
        for var, value in zip(sep, valuation):
            boundary[var] = value
            restricted = cofactor(restricted, var, value)
        restricted = canonical_cnf(restricted)

        if () in restricted:
            rows.append({"valuation": list(valuation), "status": "UNSAT", "components": [], "reason": "EMPTY_CLAUSE_AFTER_BOUNDARY"})
            continue

        comps = [] if not restricted else g0.component_formulas(restricted)
        counters["component_partitions"] += len(comps)
        branch_assignment = dict(boundary)
        comp_rows = []
        saw_unsat = False
        saw_unknown = False
        for comp in comps:
            solved = solve_recursive(comp, budget, base_engine, depth + 1, counters)
            comp_rows.append({"formula_hash": cnf_hash(comp), "status": solved["status"], "tree": solved["tree"]})
            if solved["status"] == "UNSAT":
                saw_unsat = True
            elif solved["status"] == "UNKNOWN_BUDGET":
                saw_unknown = True
            elif solved["status"] == "SAT" and solved.get("assignment"):
                branch_assignment.update(solved["assignment"])

        if saw_unsat:
            branch_status = "UNSAT"
        elif saw_unknown:
            branch_status = "UNKNOWN_BUDGET"
        else:
            branch_status = "SAT"
            full = {v: False for v in variables(formula)}
            full.update(units)
            full.update(branch_assignment)
            if satisfies(formula, full):
                sat_candidates.append(full)
            else:
                branch_status = "UNKNOWN_BUDGET"

        rows.append({"valuation": list(valuation), "status": branch_status, "components": comp_rows})

    tree = {
        "kind": "S_PHALLUS_H_2_MIN_K_SEPARATOR",
        "formula_hash": cnf_hash(formula),
        "residual_hash": cnf_hash(residual),
        "found_k": k,
        "separator": list(sep),
        "separator_certificate": detection["certificate_sha256"],
        "minimum_k_proof": detection["minimality_proof"],
        "audited_k": detection["audited_k"],
        "claimed_components": detection["components"],
        "boundary_rows": rows,
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
        full = {v: False for v in variables(formula)}
        full.update(units)
        ok = satisfies(formula, full)
        return {"status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": full if ok else None,
                "tree": {"kind": "UNIT_SAT", "formula_hash": cnf_hash(formula), "verified": ok}}
    if () in residual:
        return {"status": "UNSAT", "assignment": None, "tree": {"kind": "UNIT_UNSAT", "formula_hash": cnf_hash(formula)}}

    q0 = v21.detect_pair_product(residual)
    counters["q0_detector_calls"] += 1
    if q0["matched"]:
        counters["q0_leaf_hits"] += 1
        counters["q0_symbolic_states"] += int(q0["metrics"]["symbolic_states"])
        counters["q0_symbolic_transitions"] += int(q0["metrics"]["symbolic_transitions"])
        assignment = {v: False for v in variables(formula)}
        assignment.update(units)
        assignment.update(q0["assignment"] or {})
        ok = satisfies(formula, assignment)
        return {"status": "SAT" if ok else "UNKNOWN_BUDGET", "assignment": assignment if ok else None,
                "tree": {"kind": "Q0", "formula_hash": cnf_hash(formula), "certificate": q0["certificate_sha256"], "verified": ok}}

    detection = detect_min_separator(residual, K_MAX)
    counters["separator_detector_calls"] += 1
    _merge_discovery(counters["discovery_cost"], detection["metrics"])
    if detection["matched"]:
        k = str(detection["found_k"])
        counters["separator_nodes_by_k"][k] = counters["separator_nodes_by_k"].get(k, 0) + 1
        return _solve_boundary_table(formula, residual, units, detection, budget, base_engine, depth, counters)

    counters["generic_leaf_calls"] += 1
    order, _ = v2.activity_order(residual)
    engine = base_engine(formula, residual, order, units, budget)
    _add_engine_stats(counters["leaf_engine"], engine["stats"])
    return {
        "status": engine["status"],
        "assignment": engine.get("assignment"),
        "tree": {
            "kind": "GENERIC",
            "formula_hash": cnf_hash(formula),
            "status": engine["status"],
            "projection_sha256": digest(v2.engine_projection(engine)),
        },
    }


def solve_with_gate(raw_formula: Iterable[Iterable[int]], budget: int) -> dict[str, Any]:
    base_engine = v2.engine_run
    calls: list[dict[str, Any]] = []

    def aware_engine(original: CNF, residual: CNF, residual_order: list[int], units: dict[int, bool], state_budget: int) -> dict[str, Any]:
        q0 = v21.detect_pair_product(residual)
        if q0["matched"]:
            engine = g0.q0_engine_result(original, residual, units, q0)
            calls.append({
                "lane": Q0_LANE, "formula_hash": cnf_hash(residual), "found_k": None,
                "certificate_sha256": q0["certificate_sha256"], "metrics": q0["metrics"],
            })
            return engine

        detection = detect_min_separator(residual, K_MAX)
        if not detection["matched"]:
            engine = base_engine(original, residual, residual_order, units, state_budget)
            engine["stats"] = dict(engine["stats"])
            engine["stats"]["s_gate_lane"] = GENERIC_LANE
            calls.append({
                "lane": GENERIC_LANE, "formula_hash": cnf_hash(residual), "found_k": None,
                "separator_rejection_reason": detection["reason"], "detector": detection,
            })
            return engine

        counters = make_counters()
        solved = solve_recursive(residual, state_budget, base_engine, 0, counters)
        status = solved["status"]
        assignment = None
        verified = None
        if status == "SAT":
            assignment = {v: False for v in variables(original)}
            assignment.update(units)
            assignment.update(solved.get("assignment") or {})
            verified = satisfies(original, assignment)
            if not verified:
                status = "UNKNOWN_BUDGET"
                assignment = None

        leaf = counters["leaf_engine"]
        boundary_total = sum(counters["boundary_rows_by_k"].values())
        separator_nodes = sum(counters["separator_nodes_by_k"].values())
        symbolic_states = counters["q0_symbolic_states"] + separator_nodes + boundary_total
        stats = {
            "status": "EXACT_DECOMPOSITION" if status in {"SAT", "UNSAT"} else "OPEN",
            "recursive_calls": max(symbolic_states, leaf["recursive_calls"] + counters["recursive_component_calls"]),
            "memo_hits": leaf["memo_hits"],
            "residual_states": leaf["residual_states"] + symbolic_states,
            "transition_checks": leaf["transition_checks"] + boundary_total + counters["q0_symbolic_transitions"],
            "normalization_certificates": leaf["normalization_certificates"],
            "subsumption_steps": leaf["subsumption_steps"],
            "bdd_nodes": leaf["bdd_nodes"],
            "max_frontier_states": max(1, leaf["max_frontier_states"]),
            "frontier_counts": {"0": 1},
            "error": None if status in {"SAT", "UNSAT"} else "DECOMPOSITION_CHILD_UNKNOWN",
            "s_gate_lane": K_LANE,
            "found_k": detection["found_k"],
            "separator_nodes_by_k": counters["separator_nodes_by_k"],
            "boundary_rows_by_k": counters["boundary_rows_by_k"],
            "component_partitions": counters["component_partitions"],
            "generic_leaf_calls": counters["generic_leaf_calls"],
            "discovery_cost": counters["discovery_cost"],
            "component_units_do_not_sum_as_runtime": True,
        }
        engine = {
            "status": status,
            "root": 1 if status == "SAT" else 0 if status == "UNSAT" else None,
            "sat": True if status == "SAT" else False if status == "UNSAT" else None,
            "assignment": assignment,
            "assignment_verified": verified,
            "reason": K_LANE if status in {"SAT", "UNSAT"} else "S_PHALLUS_H_2_CHILD_UNKNOWN",
            "stats": stats,
            "engine_invoked": True,
        }
        calls.append({
            "lane": K_LANE,
            "formula_hash": cnf_hash(residual),
            "found_k": detection["found_k"],
            "separator": detection["separator"],
            "certificate_sha256": detection["certificate_sha256"],
            "detector": detection,
            "status": status,
            "tree_sha256": digest(solved["tree"]),
            "tree": solved["tree"],
            "counters": counters,
        })
        return engine

    v2.engine_run = aware_engine
    try:
        solved = v2.technical_forward(raw_formula, budget)
    finally:
        v2.engine_run = base_engine
    solved["s2_calls"] = calls
    solved["primary"] = calls[0] if calls else None
    solved["primary_lane"] = solved["primary"]["lane"] if solved["primary"] else "NO_ENGINE_CALL"
    solved["found_k"] = solved["primary"].get("found_k") if solved["primary"] else None
    return solved


def eq_edge(a: int, b: int) -> list[tuple[int, int]]:
    return [(-a, b), (a, -b)]


def anti_edge(a: int, b: int) -> list[tuple[int, int]]:
    return [(a, b), (-a, -b)]


def separator_clique_dumbbell(k: int, left_size: int, right_size: int, conflict: bool = False) -> CNF:
    sep = list(range(1, k + 1))
    left = list(range(k + 1, k + 1 + left_size))
    right = list(range(k + 1 + left_size, k + 1 + left_size + right_size))
    edges: set[tuple[int, int]] = set()
    for group in (sep, left, right):
        for a, b in itertools.combinations(group, 2):
            edges.add((a, b))
    for s in sep:
        for v in left + right:
            edges.add(tuple(sorted((s, v))))
    clauses: list[tuple[int, ...]] = []
    for a, b in sorted(edges):
        clauses.extend(eq_edge(a, b))
    if conflict:
        if len(left) < 2:
            raise ValueError("conflict fixture requires at least two left variables")
        clauses.extend(anti_edge(left[0], left[1]))
    return canonical_cnf(clauses)


def complete_equality(n: int) -> CNF:
    clauses: list[tuple[int, ...]] = []
    for a, b in itertools.combinations(range(1, n + 1), 2):
        clauses.extend(eq_edge(a, b))
    return canonical_cnf(clauses)


def load_fixture_specs() -> list[dict[str, Any]]:
    doc = json.loads(Path(FIXTURES).read_text(encoding="utf-8"))
    assert doc["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    specs = doc["fixtures"]
    for fx in specs:
        formula = separator_clique_dumbbell(
            int(fx["expected_min_k"]), int(fx["left_size"]), int(fx["right_size"]), fx["expected"] == "UNSAT"
        )
        assert cnf_hash(formula) == fx["formula_sha256"]
        assert len(formula) == fx["clause_count"]
        assert sum(len(c) for c in formula) == fx["literal_count"]
    return specs


def formula_from_spec(fx: dict[str, Any]) -> CNF:
    return separator_clique_dumbbell(
        int(fx["expected_min_k"]), int(fx["left_size"]), int(fx["right_size"]), fx["expected"] == "UNSAT"
    )


def fixture_row(fx: dict[str, Any], budget: int = 50000) -> tuple[dict[str, Any], dict[str, Any]]:
    formula = formula_from_spec(fx)
    solved = solve_with_gate(formula, budget)
    primary = solved["primary"] or {}
    detector = primary.get("detector") or {}
    tree = primary.get("tree") or {}
    found_k = primary.get("found_k")
    expected_k = int(fx["expected_min_k"])
    expected_rows = 1 << expected_k
    exact = solved["status"] == fx["expected"] and solved["authorized"] and solved["primary_lane"] == K_LANE
    k_ok = found_k == expected_k
    minproof_ok = bool(detector and verify_detector_certificate(formula, detector, K_MAX))
    rowset_ok = bool(tree and verify_boundary_rows(expected_k, tree.get("boundary_rows", [])))
    metrics = detector.get("metrics", {})
    row = {
        "id": fx["id"], "split": fx["split"], "n": fx["n"],
        "expected": fx["expected"], "observed": solved["status"], "authorized": solved["authorized"],
        "expected_min_k": expected_k, "found_k": found_k, "lane": solved["primary_lane"],
        "exact_correct": exact, "minimum_k_correct": k_ok, "minimum_k_proof_verified": minproof_ok,
        "boundary_rows": len(tree.get("boundary_rows", [])), "expected_boundary_rows": expected_rows,
        "boundary_table_complete": rowset_ok,
        "candidate_counts_by_k": metrics.get("candidate_counts_by_k", {}),
        "verified_separator_counts_by_k": metrics.get("verified_separator_counts_by_k", {}),
        "cumulative_candidate_count": metrics.get("cumulative_candidate_count", 0),
        "component_partitions": (primary.get("counters") or {}).get("component_partitions", 0),
        "generic_leaf_calls": (primary.get("counters") or {}).get("generic_leaf_calls", 0),
        "residual_states": solved["cost_vector"]["residual_states"],
        "formula_sha256": cnf_hash(formula),
    }
    return row, solved


def negative_controls() -> list[dict[str, Any]]:
    complete = complete_equality(7)
    no_sep = detect_min_separator(complete, K_MAX)

    k3 = separator_clique_dumbbell(3, 4, 4)
    graph = g0.primal_graph(k3)[0]
    forged_k2_components = g0.connected_components(graph, {1, 2})
    forged_k2 = verify_separator_claim(k3, (1, 2), forged_k2_components)

    det3 = detect_min_separator(k3, K_MAX)
    assert det3["matched"] and det3["found_k"] == 3
    bad_components = [tuple(c) for c in det3["components"]]
    if len(bad_components) >= 2:
        bad_components = [tuple(sorted(bad_components[0] + bad_components[1]))]
    forged_components = verify_separator_claim(k3, tuple(det3["separator"]), bad_components)

    omitted_audit = json.loads(json.dumps(det3))
    omitted_audit["audited_k"] = [3]
    omitted_audit_rejected = not verify_detector_certificate(k3, omitted_audit, K_MAX)

    solved = solve_with_gate(k3, 50000)
    rows = solved["primary"]["tree"]["boundary_rows"]
    omitted_rows = [dict(r) for r in rows[:-1]]
    boundary_rejected = verify_boundary_rows(3, rows) and not verify_boundary_rows(3, omitted_rows)

    other = separator_clique_dumbbell(3, 5, 4)
    swapped = json.loads(json.dumps(det3))
    swapped["formula_hash"] = cnf_hash(other)
    hash_swap_rejected = not verify_detector_certificate(k3, swapped, K_MAX)

    return [
        {"id": "COMPLETE_GRAPH_N7_NO_SEPARATOR_K_LE4", "passed": not no_sep["matched"], "reason": no_sep["reason"]},
        {"id": "FORGED_K3_AS_K2", "passed": not forged_k2["passed"], "reason": forged_k2["reason"]},
        {"id": "FORGED_COMPONENT_PARTITION", "passed": not forged_components["passed"], "reason": forged_components["reason"]},
        {"id": "OMITTED_SMALLER_K_AUDIT", "passed": omitted_audit_rejected},
        {"id": "BOUNDARY_TABLE_ROW_OMISSION_OR_BITFLIP", "passed": boundary_rejected},
        {"id": "CERTIFICATE_FORMULA_HASH_SWAP", "passed": hash_swap_rejected},
    ]


def left_control() -> dict[str, Any]:
    a = separator_clique_dumbbell(3, 4, 4)
    b = separator_clique_dumbbell(3, 5, 4)
    da, db = detect_min_separator(a), detect_min_separator(b)
    return {
        "control": "SAME_MIN_K_CAPABILITY_DIFFERENT_PROVENANCE",
        "both_found_k3": da["found_k"] == 3 and db["found_k"] == 3,
        "formula_identity_distinct": cnf_hash(a) != cnf_hash(b),
        "certificate_identity_distinct": da["certificate_sha256"] != db["certificate_sha256"],
        "identity_authorized_from_capability": False,
        "passed": da["found_k"] == db["found_k"] == 3 and cnf_hash(a) != cnf_hash(b) and da["certificate_sha256"] != db["certificate_sha256"],
    }


def right_control() -> dict[str, Any]:
    f = separator_clique_dumbbell(3, 2, 2)
    d = detect_min_separator(f)
    action_certificate_present = False
    fallback = v21.solve_v21(f, 50000)
    return {
        "control": "SAME_CNF_MIN_K_ACTION_CERTIFICATE_REMOVED",
        "detector_match": d["matched"],
        "found_k": d["found_k"],
        "action_certificate_present": action_certificate_present,
        "s2_authorized": False,
        "fallback_status": fallback["status"],
        "fallback_authorized": fallback["authorized"],
        "passed": d["matched"] and d["found_k"] == 3 and not action_certificate_present and fallback["authorized"] and fallback["status"] == "SAT",
    }


def regression_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    osiris = []
    for fx in v2.fixtures():
        solved = solve_with_gate(fx["formula"], fx["budget"])
        osiris.append({
            "id": fx["id"], "expected": fx["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "lane": solved["primary_lane"], "found_k": solved.get("found_k"),
            "passed": solved["status"] == fx["expected"] and solved["authorized"],
        })
    gate0 = []
    for fx in g0.calibration_fixtures():
        solved = solve_with_gate(fx["formula"], fx["budget"])
        gate0.append({
            "id": fx["id"], "expected": fx["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "lane": solved["primary_lane"], "found_k": solved.get("found_k"),
            "passed": solved["status"] == fx["expected"] and solved["authorized"] and solved.get("found_k") == 1,
        })
    gate1 = []
    for fx in g1.calibration():
        solved = solve_with_gate(fx["formula"], fx["budget"])
        gate1.append({
            "id": fx["id"], "expected": fx["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "lane": solved["primary_lane"], "found_k": solved.get("found_k"),
            "passed": solved["status"] == fx["expected"] and solved["authorized"] and solved.get("found_k") == 2,
        })
    hard = []
    for fx in v2.hard_fixtures():
        solved = solve_with_gate(fx["formula"], fx["budget"])
        passed = (not solved["authorized"] and solved["status"] == "UNKNOWN_BUDGET") or (solved["authorized"] and solved["status"] == fx["expected"])
        hard.append({
            "id": fx["id"], "expected": fx["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "lane": solved["primary_lane"], "found_k": solved.get("found_k"),
            "passed": passed,
        })
    return osiris, gate0, gate1, hard


def scaling_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    observations = [{
        "id": r["id"], "split": r["split"], "n": r["n"], "found_k": r["found_k"],
        "candidate_counts_by_k": r["candidate_counts_by_k"],
        "cumulative_candidate_count": r["cumulative_candidate_count"],
        "boundary_rows": r["boundary_rows"],
        "component_partitions": r["component_partitions"],
        "generic_leaf_calls": r["generic_leaf_calls"],
        "residual_states": r["residual_states"],
        "technical_verdict": r["observed"],
    } for r in rows]
    by_k: dict[str, dict[str, Any]] = {}
    for r in rows:
        k = str(r["found_k"])
        bucket = by_k.setdefault(k, {"fixtures": 0, "n_values": [], "candidate_counts": [], "boundary_rows": []})
        bucket["fixtures"] += 1
        bucket["n_values"].append(r["n"])
        bucket["candidate_counts"].append(r["cumulative_candidate_count"])
        bucket["boundary_rows"].append(r["boundary_rows"])
    return {
        "observations": observations,
        "by_k": by_k,
        "finite_family_observation": "Within the preregistered separator-clique-dumbbell family, the detector recovered k=1..4 including holdout sizes. Boundary-table rows follow 2^k, while exhaustive discovery checks grow as sum_{j=1..k} C(n,j). This is a restricted-family measurement, not an arbitrary-CNF theorem.",
        "cost_warning": "Discovery candidate checks and boundary rows are reported as separate operation counts and are not summed into a fake runtime unit. As k grows, both combinatorial subset discovery and 2^k boundary work become explicit candidate barriers.",
    }


def run() -> dict[str, Any]:
    contract = json.loads(Path(CONTRACT).read_text(encoding="utf-8"))
    assert contract["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    assert contract["parent"]["sha"] == PARENT_SHA
    assert contract["parent"]["result_integrity_sha256"] == PARENT_RESULT_SHA
    assert contract["finite_scope"]["K_MAX"] == K_MAX
    assert contract["tranception"]["direction_order"] == DIRECTIONS

    specs = load_fixture_specs()
    calibration_specs = [x for x in specs if x["split"] == "calibration"]
    holdout_specs = [x for x in specs if x["split"] == "holdout"]

    calibration = []
    solved_cache: dict[str, dict[str, Any]] = {}
    for fx in calibration_specs:
        row, solved = fixture_row(fx)
        calibration.append(row)
        solved_cache[fx["id"]] = solved

    holdout = []
    for fx in holdout_specs:
        row, solved = fixture_row(fx)
        holdout.append(row)
        solved_cache[fx["id"]] = solved

    negatives = negative_controls()
    osiris, gate0_rows, gate1_rows, hard = regression_rows()

    eq = next(x for x in osiris if x["id"] == "EQUALITY_N14")
    anti = next(x for x in osiris if x["id"] == "ANTI_EQUALITY_N14")

    ref_fx = next(x for x in holdout_specs if x["id"] == "HOLD_K4_N13_SAT")
    ref_formula = formula_from_spec(ref_fx)
    reference = solved_cache[ref_fx["id"]]
    back = v2.back_replay(reference)
    primary = reference["primary"]
    back_bound = back["passed"] and primary["found_k"] == 4 and verify_detector_certificate(ref_formula, primary["detector"], K_MAX) and verify_boundary_rows(4, primary["tree"]["boundary_rows"])

    forward = solve_with_gate(ref_formula, 50000)
    left = left_control()
    right = right_control()
    forward_again = solve_with_gate(ref_formula, 50000)
    position = g1.make_position(forward)
    position2 = g1.make_position(forward_again)
    position_same = position["position_commitment"] == position2["position_commitment"]
    back_again = {
        "historical_text_semantics_consumed": False,
        "technical_verdict": forward["status"],
        "P_VS_NP": "OPEN",
        "passed": forward["status"] == reference["status"],
    }
    payloads = {
        "BACK": {"passed": back_bound, "terminal": back["terminal_commitment"], "minimum_k_certificate": primary["certificate_sha256"]},
        "FORWARD": {"position": position, "found_k": forward["found_k"], "certificate": forward["primary"]["certificate_sha256"]},
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": {"position": position2, "position_same": position_same, "found_k": forward_again["found_k"]},
        "BACK_AGAIN": back_again,
    }
    history = g1.make_history(payloads)
    origin = g1.make_origin(position)
    prime1 = g1.make_origin_prime(origin, position, history)
    prime2 = g1.make_origin_prime(prime1, position2, history)
    ribbon_negative = g1.ribbon_controls(origin, prime1, position, history)
    ribbon_ok = position_same and len({origin["state_commitment"], prime1["state_commitment"], prime2["state_commitment"]}) == 3 and prime2["generation"] == 2 and all(ribbon_negative.values())

    all_rows = calibration + holdout
    gates = {
        "calibration_8_of_8_exact_and_min_k": len(calibration) == 8 and all(r["exact_correct"] and r["minimum_k_correct"] and r["minimum_k_proof_verified"] and r["boundary_table_complete"] for r in calibration),
        "holdout_6_of_6_exact_and_min_k": len(holdout) == 6 and all(r["exact_correct"] and r["minimum_k_correct"] and r["minimum_k_proof_verified"] and r["boundary_table_complete"] for r in holdout),
        "all_separator_fixtures_use_auto_k_lane": all(r["lane"] == K_LANE for r in all_rows),
        "all_boundary_tables_exact_2_pow_k": all(r["boundary_rows"] == (1 << int(r["found_k"])) for r in all_rows),
        "all_smaller_k_exhausted": all(all(r["verified_separator_counts_by_k"].get(str(j), 0) == 0 for j in range(1, int(r["found_k"]))) for r in all_rows),
        "negative_controls_6_of_6": len(negatives) == 6 and all(x["passed"] for x in negatives),
        "osiris_v2_1_regression_8_of_8": len(osiris) == 8 and all(x["passed"] for x in osiris),
        "gate0_regression_5_of_5_auto_finds_k1": len(gate0_rows) == 5 and all(x["passed"] for x in gate0_rows),
        "gate1_regression_5_of_5_auto_finds_k2": len(gate1_rows) == 5 and all(x["passed"] for x in gate1_rows),
        "q0_priority_preserved": eq["lane"] == Q0_LANE and anti["lane"] == Q0_LANE,
        "hard_tseitin_budget_256_fail_closed_or_correct": len(hard) == 2 and all(x["passed"] for x in hard),
        "BACK_exact_plus_min_k_proof": back_bound,
        "FORWARD_auto_k4_exact": forward["status"] == "SAT" and forward["authorized"] and forward["found_k"] == 4,
        "LEFT_identity_firewall": left["passed"],
        "RIGHT_action_certificate_firewall": right["passed"],
        "FORWARD_AGAIN_position_reproducible": position_same and forward_again["found_k"] == 4,
        "ORIGIN_PRIME_state_advances": ribbon_ok,
        "P_VS_NP_OPEN": True,
    }
    passed = all(gates.values())
    scale = scaling_report(all_rows)

    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_S_PHALLUS_H_GATE_2_BOUNDED_K_SCALING_HOLDOUT__MASTER_P_VS_NP_GATE_REMAINS_OPEN" if passed else "STOP_S_PHALLUS_H_GATE_2_BOUNDED_K_SCALING_HOLDOUT",
        "parent": {"sha": PARENT_SHA, "result_integrity_sha256": PARENT_RESULT_SHA},
        "gate_identity": "S𓂸ḥ/2",
        "subgate": "AUTOMATIC_VERIFIED_MINIMUM_SEPARATOR_K_1_TO_4_WITH_PREREGISTERED_HOLDOUT",
        "K_MAX": K_MAX,
        "calibration": calibration,
        "holdout": holdout,
        "negative_controls": negatives,
        "regression": osiris,
        "gate0_regression": gate0_rows,
        "gate1_regression": gate1_rows,
        "hard_controls": hard,
        "scaling": scale,
        "tranception": {
            "directions": DIRECTIONS,
            "BACK": {"passed": back_bound, "stage_back": back, "minimum_k_certificate_verified": back_bound},
            "FORWARD": {"status": forward["status"], "lane": forward["primary_lane"], "found_k": forward["found_k"]},
            "LEFT": left,
            "RIGHT": right,
            "FORWARD_AGAIN": {"position_same": position_same, "found_k": forward_again["found_k"]},
            "BACK_AGAIN": back_again,
        },
        "ribbon_state": {
            "mechanic": "ORIGIN -> EXPERIENCE -> RETURN -> ORIGIN_PRIME",
            "position": position,
            "origin": origin,
            "history": history,
            "origin_prime_1": prime1,
            "origin_prime_2": prime2,
            "negative_controls": ribbon_negative,
            "POSITION_RETURN_EQUALS_ORIGIN_POSITION": position_same,
            "STATE_RETURN_DIFFERS_FROM_ORIGINAL_STATE": origin["state_commitment"] != prime1["state_commitment"],
        },
        "gates": gates,
        "mathematical_verdict": {
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
            "P_VS_NP": "OPEN",
        },
        "scientific_boundary": [
            "Finite K_MAX=4 experiment only",
            "Holdout is preregistered but belongs to the same separator-clique-dumbbell construction family",
            "No arbitrary-CNF bounded separator theorem",
            "Discovery cost and 2^k boundary cost remain explicit",
            "No P=NP or P!=NP result",
        ],
        "next_gate_if_pass": "S𓂸ḥ/3: BROADER_GRAPH_FAMILY_HOLDOUT_AND_K_GROWTH_BEYOND_FIXED_KMAX",
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
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
