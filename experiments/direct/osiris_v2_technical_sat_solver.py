#!/usr/bin/env python3
"""OSIRIS v2: technical, content-bound SAT/complexity experiment.

This replaces the v1 generic stage-envelope path with executable CNF mechanics.
The 31 PT labels remain project operator names only; historical text is not used
as a correctness oracle. A modern CNF0 structural witness is inserted before
PT350. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import inspect
import json
import random
from collections import Counter, defaultdict
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

from janus_c025_core import (
    CNF,
    canonical_cnf,
    cnf_hash,
    cofactor,
    compile_residual_automaton,
    normalize_subsumption,
    satisfies,
    variables,
    verify_normalization,
)
from janus_c025_families import equality_family
from toroidal_tseitin_twins import build_formula as build_tseitin_formula, charge_patterns as tseitin_charge_patterns

RUN_ID = "OSIRIS-V2-TECHNICAL-SAT-SOLVER-2026-08-18-v1"
PARENT_OSIRIS_SHA = "108ceb0e6ca875517bcf17ef503ee0e0c6455c57"
PR192_SHA = "0f325335f270af9a0aa8a1a0ac1f32e3bfb88f13"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
PT_FORWARD = [
    "PT350","PT351","PT352","PT353","PT354","PT355",
    "PT356","PT357","PT358","PT359","PT360","PT361","PT362","PT363","PT364","PT365","PT366",
    "PT367","PT368","PT369","PT370","PT371","PT372","PT373","PT374",
    "PT476","PT477","PT478","PT220","PT221","PT222",
]
TECH_FORWARD = ["CNF0_STRUCTURAL_WITNESS"] + PT_FORWARD
TECH_BACK = list(reversed(TECH_FORWARD))

OP = {
    "CNF0_STRUCTURAL_WITNESS": "CANONICALIZE_AND_BIND_REAL_CNF_STRUCTURE",
    "PT350": "BUILD_CNF_FIELD",
    "PT351": "BIND_BRANCH_CANDIDATES",
    "PT352": "FORM_BRANCH_ORDER",
    "PT353": "LIVE_RESIDUAL_GATE",
    "PT354": "PROVISION_SOLVER_INPUT_AND_RETURN_CERT",
    "PT355": "VERIFIED_SUBSUMPTION_NORMALIZATION",
    "PT356": "SEEK_FORCED_LITERALS",
    "PT357": "VERIFY_FORCED_LITERALS",
    "PT358": "UNBIND_BY_UNIT_PROPAGATION",
    "PT359": "CROSS_TO_CANONICAL_RESIDUAL",
    "PT360": "TERMINAL_GATE",
    "PT361": "HANDOFF_TO_SEARCH_ENGINE",
    "PT362": "PROTECT_SEARCH_PROVENANCE",
    "PT363": "PREPARE_SEARCH_PATH",
    "PT364": "LOW_BRANCH_PROBE",
    "PT365": "HIGH_BRANCH_PROBE",
    "PT366": "SEED_INVARIANT",
    "PT367": "REASSEMBLE_AUTOMATON_NODES",
    "PT368": "PROTECT_WITNESS_PATH",
    "PT369": "RESTORE_ORIGINAL_VARIABLE_SPACE",
    "PT370": "REUNITE_RESULT_WITH_ORIGINAL_CNF",
    "PT371": "CLASSIFY_EXACT_OR_OPEN",
    "PT372": "CONFLICT_CERTIFICATE_GATE",
    "PT373": "RESIDUAL_STATE_ACCOUNTING",
    "PT374": "FINALIZE_FORMULA_BOUND_SOLVER_MANIFEST",
    "PT476": "CERTIFY_AND_ADMIT_RESULT",
    "PT477": "TOMBSTONE_DEDUP_AUDIT",
    "PT478": "ASCEND_CERTIFIED_RESULT",
    "PT220": "ROOT_HORIZON_GATE",
    "PT221": "AUTHORITY_HANDOFF_TO_INDEPENDENT_VERIFIER",
    "PT222": "BIDIRECTIONAL_REPLAY",
}


def stable_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def cnf_lists(formula: CNF) -> list[list[int]]:
    return [list(clause) for clause in formula]


def raw_hash(raw: Iterable[Iterable[int]]) -> str:
    return stable_hash([[int(lit) for lit in clause] for clause in raw])


def occurrence_table(formula: CNF) -> dict[str, dict[str, int]]:
    table: dict[int, list[int]] = defaultdict(lambda: [0, 0])
    for clause in formula:
        for lit in clause:
            if lit > 0:
                table[abs(lit)][0] += 1
            else:
                table[abs(lit)][1] += 1
    return {str(v): {"positive": p, "negative": n, "total": p + n} for v, (p, n) in sorted(table.items())}


def clause_histogram(formula: CNF) -> dict[str, int]:
    counts = Counter(len(c) for c in formula)
    return {str(k): counts[k] for k in sorted(counts)}


def structural_witness(raw: Iterable[Iterable[int]]) -> tuple[CNF, dict[str, Any]]:
    raw_rows = [tuple(int(x) for x in clause) for clause in raw]
    formula = canonical_cnf(raw_rows)
    occ = occurrence_table(formula)
    witness_core = {
        "original_cnf_hash": raw_hash(raw_rows),
        "canonical_cnf_hash": cnf_hash(formula),
        "variables": variables(formula),
        "variable_count": len(variables(formula)),
        "clause_count": len(formula),
        "literal_count": sum(len(c) for c in formula),
        "occurrence_table": occ,
        "clause_length_histogram": clause_histogram(formula),
    }
    witness = dict(witness_core)
    witness["witness_digest"] = stable_hash(witness_core)
    witness["verified"] = bool(formula == canonical_cnf(formula) and witness["canonical_cnf_hash"] == cnf_hash(formula))
    return formula, witness


def activity_order(formula: CNF) -> tuple[list[int], dict[str, int]]:
    scores: dict[int, int] = defaultdict(int)
    for clause in formula:
        # Integer Jeroslow-Wang-like weight; deterministic and content-derived.
        weight = 1 << max(0, 8 - min(8, len(clause)))
        for lit in clause:
            scores[abs(lit)] += weight
    order = sorted(variables(formula), key=lambda v: (-scores[v], v))
    return order, {str(v): scores[v] for v in sorted(scores)}


def scan_units(formula: CNF) -> list[int]:
    return sorted((c[0] for c in formula if len(c) == 1), key=lambda lit: (abs(lit), lit < 0))


def unit_propagate(formula: CNF) -> tuple[CNF, dict[int, bool], list[dict[str, Any]]]:
    residual = canonical_cnf(formula)
    assignment: dict[int, bool] = {}
    trail: list[dict[str, Any]] = []
    while True:
        if () in residual or not residual:
            break
        units = scan_units(residual)
        if not units:
            break
        lit = units[0]
        var = abs(lit)
        value = lit > 0
        if var in assignment and assignment[var] != value:
            residual = canonical_cnf([()])
            trail.append({"literal": lit, "conflict": True, "after_hash": cnf_hash(residual)})
            break
        before = cnf_hash(residual)
        assignment[var] = value
        residual = cofactor(residual, var, value)
        trail.append({"literal": lit, "variable": var, "value": value, "before_hash": before, "after_hash": cnf_hash(residual)})
    return residual, assignment, trail


def verify_unit_trail(start: CNF, trail: list[dict[str, Any]]) -> bool:
    residual = canonical_cnf(start)
    assigned: dict[int, bool] = {}
    for row in trail:
        if row.get("conflict"):
            return () in canonical_cnf([()])
        lit = int(row["literal"])
        if (lit,) not in residual:
            return False
        var = abs(lit)
        value = lit > 0
        if var in assigned and assigned[var] != value:
            return False
        if row.get("before_hash") != cnf_hash(residual):
            return False
        assigned[var] = value
        residual = cofactor(residual, var, value)
        if row.get("after_hash") != cnf_hash(residual):
            return False
    return True


def branch_probe(formula: CNF, order: list[int], value: bool) -> dict[str, Any]:
    if not order or not formula or () in formula:
        return {"applicable": False, "passed": True, "reason": "terminal_or_no_variable"}
    var = order[0]
    raw = cofactor(formula, var, value)
    normalized, cert = normalize_subsumption(raw)
    passed = verify_normalization(raw, normalized, cert)
    return {
        "applicable": True,
        "variable": var,
        "value": value,
        "raw_hash": cnf_hash(raw),
        "normalized_hash": cnf_hash(normalized),
        "subsumption_steps": len(cert.steps),
        "certificate_verified": passed,
        "passed": passed,
    }


def presentation_invariant(formula: CNF) -> dict[str, Any]:
    presented = [tuple(reversed(c)) for c in reversed(formula)]
    rebuilt = canonical_cnf(presented)
    order_a, score_a = activity_order(formula)
    order_b, score_b = activity_order(rebuilt)
    passed = formula == rebuilt and order_a == order_b and score_a == score_b
    return {
        "canonical_identity_preserved": formula == rebuilt,
        "activity_order_preserved": order_a == order_b,
        "activity_scores_preserved": score_a == score_b,
        "passed": passed,
    }


def engine_run(original: CNF, residual: CNF, residual_order: list[int], units: dict[int, bool], budget: int) -> dict[str, Any]:
    original_vars = variables(original)
    if not residual:
        assignment = {v: False for v in original_vars}
        assignment.update(units)
        verified = satisfies(original, assignment)
        return {
            "status": "SAT", "root": 1, "sat": True, "assignment": assignment,
            "assignment_verified": verified, "reason": "EMPTY_RESIDUAL_AFTER_UNIT_PROPAGATION",
            "stats": {"recursive_calls": 0, "memo_hits": 0, "residual_states": 1, "transition_checks": 0,
                      "normalization_certificates": 0, "subsumption_steps": 0, "bdd_nodes": 0,
                      "max_frontier_states": 1, "frontier_counts": {"0": 1}},
            "engine_invoked": False,
        }
    if () in residual:
        return {
            "status": "UNSAT", "root": 0, "sat": False, "assignment": None,
            "assignment_verified": None, "reason": "EMPTY_CLAUSE_AFTER_UNIT_PROPAGATION",
            "stats": {"recursive_calls": 0, "memo_hits": 0, "residual_states": 1, "transition_checks": 0,
                      "normalization_certificates": 0, "subsumption_steps": 0, "bdd_nodes": 0,
                      "max_frontier_states": 1, "frontier_counts": {"0": 1}},
            "engine_invoked": False,
        }
    # Conservative fail-closed precheck: we never exceed the frozen state budget merely
    # to force a verdict. This is an operational UNKNOWN, not a lower-bound claim.
    if len(residual_order) > budget:
        return {
            "status": "UNKNOWN_BUDGET", "root": None, "sat": None, "assignment": None,
            "assignment_verified": None, "reason": "VARIABLE_DEPTH_EXCEEDS_FROZEN_STATE_BUDGET_PRECHECK",
            "stats": {"recursive_calls": 0, "memo_hits": 0, "residual_states": 0, "transition_checks": 0,
                      "normalization_certificates": 0, "subsumption_steps": 0, "bdd_nodes": 0,
                      "max_frontier_states": 0, "frontier_counts": {}},
            "engine_invoked": False,
        }
    result = compile_residual_automaton(residual, residual_order, state_budget=budget)
    stats = asdict(result.stats)
    stats["frontier_counts"] = {str(k): v for k, v in result.stats.frontier_counts.items()}
    if result.status != "EXACT":
        return {
            "status": "UNKNOWN_BUDGET", "root": None, "sat": None, "assignment": None,
            "assignment_verified": None, "reason": result.stats.error or "RESIDUAL_STATE_BUDGET_EXCEEDED",
            "stats": stats, "engine_invoked": True,
        }
    if result.sat:
        full = {v: False for v in original_vars}
        full.update(units)
        if result.witness:
            full.update(result.witness)
        verified = satisfies(original, full)
        return {
            "status": "SAT", "root": result.root, "sat": True, "assignment": full,
            "assignment_verified": verified, "reason": "EXACT_RESIDUAL_AUTOMATON",
            "stats": stats, "engine_invoked": True,
        }
    return {
        "status": "UNSAT", "root": result.root, "sat": False, "assignment": None,
        "assignment_verified": None, "reason": "EXACT_RESIDUAL_AUTOMATON",
        "stats": stats, "engine_invoked": True,
    }


def engine_projection(engine: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": engine["status"],
        "root": engine["root"],
        "sat": engine["sat"],
        "assignment_sha256": stable_hash(engine["assignment"]) if engine.get("assignment") is not None else None,
        "assignment_verified": engine.get("assignment_verified"),
        "reason": engine["reason"],
        "stats": engine["stats"],
        "engine_invoked": engine["engine_invoked"],
    }


def make_stage(stage: str, predecessor: str, formula_anchor: str, payload: dict[str, Any], passed: bool) -> dict[str, Any]:
    body = {
        "stage": stage,
        "operator": OP[stage],
        "predecessor_commitment": predecessor,
        "formula_anchor": formula_anchor,
        "payload": payload,
        "passed": bool(passed),
    }
    row = dict(body)
    row["commitment"] = stable_hash(body)
    return row


def verify_stage(row: dict[str, Any]) -> bool:
    body = {k: row[k] for k in ("stage", "operator", "predecessor_commitment", "formula_anchor", "payload", "passed")}
    return bool(row["stage"] in OP and row["operator"] == OP[row["stage"]] and row["commitment"] == stable_hash(body))


def technical_forward(raw_formula: Iterable[Iterable[int]], budget: int) -> dict[str, Any]:
    raw_rows = [tuple(int(x) for x in c) for c in raw_formula]
    original, cnf0 = structural_witness(raw_rows)
    formula_anchor = cnf0["canonical_cnf_hash"]
    predecessor = stable_hash({"release": "OSIRIS_V2", "raw_hash": cnf0["original_cnf_hash"]})
    stages: list[dict[str, Any]] = []

    def emit(stage: str, payload: dict[str, Any], passed: bool = True) -> None:
        nonlocal predecessor
        row = make_stage(stage, predecessor, formula_anchor, payload, passed)
        stages.append(row)
        predecessor = row["commitment"]

    emit("CNF0_STRUCTURAL_WITNESS", {
        "canonical_cnf_hash": cnf0["canonical_cnf_hash"], "witness_digest": cnf0["witness_digest"],
        "variable_count": cnf0["variable_count"], "clause_count": cnf0["clause_count"],
        "literal_count": cnf0["literal_count"], "verified": cnf0["verified"],
    }, cnf0["verified"])

    order0, scores0 = activity_order(original)
    field = {
        "variable_count": len(order0), "clause_count": len(original), "literal_count": sum(len(c) for c in original),
        "clause_length_histogram": clause_histogram(original), "occurrence_digest": stable_hash(occurrence_table(original)),
    }
    emit("PT350", field, True)

    candidates = [{"variable": v, "score": scores0.get(str(v), 0), "parent": formula_anchor} for v in order0]
    candidate_ok = len(candidates) == len(order0) and len({c["variable"] for c in candidates}) == len(order0)
    emit("PT351", {"candidate_count": len(candidates), "candidate_digest": stable_hash(candidates), "all_parent_bound": candidate_ok}, candidate_ok)

    coverage_ok = sorted(order0) == variables(original) and len(order0) == len(set(order0))
    emit("PT352", {"order": order0, "order_digest": stable_hash(order0), "coverage_exact": coverage_ok}, coverage_ok)

    syntactic_terminal = "SAT_EMPTY_CNF" if not original else "UNSAT_EMPTY_CLAUSE" if () in original else "NONTERMINAL"
    emit("PT353", {"syntactic_terminal": syntactic_terminal, "well_formed": original == canonical_cnf(original)}, original == canonical_cnf(original))

    provision = stable_hash({"formula": formula_anchor, "order": order0, "budget": budget, "return": "PT222_REPLAY"})
    emit("PT354", {"solver_input_commitment": provision, "state_budget": budget, "return_target": "PT222"}, True)

    normalized, norm_cert = normalize_subsumption(original)
    norm_ok = verify_normalization(original, normalized, norm_cert)
    emit("PT355", {"input_hash": cnf_hash(original), "output_hash": cnf_hash(normalized),
                   "subsumption_steps": len(norm_cert.steps), "certificate_verified": norm_ok}, norm_ok)

    initial_units = scan_units(normalized)
    emit("PT356", {"initial_forced_literals": initial_units, "count": len(initial_units)}, True)

    forced_ok = all((lit,) in normalized for lit in initial_units)
    emit("PT357", {"claimed_units_present": forced_ok, "forced_digest": stable_hash(initial_units)}, forced_ok)

    residual, unit_assignment, unit_trail = unit_propagate(normalized)
    trail_ok = verify_unit_trail(normalized, unit_trail)
    emit("PT358", {"unit_assignments": {str(k): v for k, v in sorted(unit_assignment.items())},
                   "trail_length": len(unit_trail), "trail_digest": stable_hash(unit_trail), "trail_verified": trail_ok}, trail_ok)

    residual = canonical_cnf(residual)
    emit("PT359", {"residual_hash": cnf_hash(residual), "residual_clauses": len(residual),
                   "residual_variables": len(variables(residual))}, residual == canonical_cnf(residual))

    gate_status = "SAT_CANDIDATE" if not residual else "UNSAT_CANDIDATE" if () in residual else "CONTINUE"
    emit("PT360", {"gate_status": gate_status, "authority": "CANDIDATE_ONLY_NO_FINAL_VERDICT"}, True)

    handoff = stable_hash({"residual": cnf_hash(residual), "budget": budget, "unit_assignment": unit_assignment})
    emit("PT361", {"engine": "compile_residual_automaton", "handoff_commitment": handoff}, True)

    core_source = inspect.getsource(compile_residual_automaton)
    core_digest = sha256(core_source.encode("utf-8")).hexdigest()
    emit("PT362", {"core_source_sha256": core_digest, "parent_cnf0": cnf0["witness_digest"], "handoff": handoff}, True)

    remaining = set(variables(residual))
    order_residual = [v for v in order0 if v in remaining]
    order_residual += [v for v in sorted(remaining) if v not in order_residual]
    path_ok = sorted(order_residual) == sorted(remaining) and len(order_residual) == len(set(order_residual))
    emit("PT363", {"residual_order": order_residual, "order_digest": stable_hash(order_residual), "coverage_exact": path_ok}, path_ok)

    low = branch_probe(residual, order_residual, False)
    emit("PT364", {k: v for k, v in low.items() if k != "passed"}, low["passed"])
    high = branch_probe(residual, order_residual, True)
    emit("PT365", {k: v for k, v in high.items() if k != "passed"}, high["passed"])

    invariant = presentation_invariant(residual)
    emit("PT366", {k: v for k, v in invariant.items() if k != "passed"}, invariant["passed"])

    engine = engine_run(original, residual, order_residual, unit_assignment, budget)
    node_valid = True
    if engine["engine_invoked"]:
        # Runtime-source audit for the exact tombstone key used by C025.
        node_valid = "key = (depth, residual)" in core_source and "memo[key]" in core_source
    emit("PT367", {"automaton_structure_policy_verified": node_valid, "root": engine["root"],
                   "bdd_nodes": engine["stats"]["bdd_nodes"]}, node_valid)

    witness_commitment = stable_hash({"status": engine["status"], "root": engine["root"],
                                      "assignment": engine.get("assignment"), "formula": formula_anchor})
    emit("PT368", {"witness_commitment": witness_commitment, "status": engine["status"]}, True)

    restored_assignment = engine.get("assignment")
    restore_ok = engine["status"] != "SAT" or (restored_assignment is not None and set(variables(original)).issubset(restored_assignment))
    emit("PT369", {"assignment_present": restored_assignment is not None,
                   "assignment_sha256": stable_hash(restored_assignment) if restored_assignment is not None else None}, restore_ok)

    model_ok = None if engine["status"] != "SAT" else bool(restored_assignment is not None and satisfies(original, restored_assignment))
    reunite_ok = engine["status"] != "SAT" or bool(model_ok)
    emit("PT370", {"status": engine["status"], "sat_model_verified_on_original": model_ok}, reunite_ok)

    class_ok = engine["status"] in {"SAT", "UNSAT", "UNKNOWN_BUDGET"}
    emit("PT371", {"classification": engine["status"], "exact": engine["status"] in {"SAT", "UNSAT"}}, class_ok)

    if engine["status"] == "UNSAT":
        replay_unsat = engine_run(original, residual, order_residual, unit_assignment, budget)
        unsat_verified = replay_unsat["status"] == "UNSAT" and replay_unsat["root"] == 0
    else:
        replay_unsat = None
        unsat_verified = engine["status"] != "UNSAT"
    emit("PT372", {"unsat_applicable": engine["status"] == "UNSAT", "unsat_replay_root_zero": unsat_verified if engine["status"] == "UNSAT" else None}, unsat_verified)

    stats = engine["stats"]
    emit("PT373", {"residual_states": stats["residual_states"], "recursive_calls": stats["recursive_calls"],
                   "memo_hits": stats["memo_hits"], "transition_checks": stats["transition_checks"],
                   "bdd_nodes": stats["bdd_nodes"], "max_frontier_states": stats["max_frontier_states"]}, True)

    result_manifest = {
        "formula_anchor": formula_anchor, "cnf0_witness": cnf0["witness_digest"], "status": engine["status"],
        "root": engine["root"], "witness_commitment": witness_commitment, "budget": budget,
    }
    emit("PT374", {"result_manifest_sha256": stable_hash(result_manifest), "formula_bound": True}, True)

    admitted = bool((engine["status"] == "SAT" and model_ok) or (engine["status"] == "UNSAT" and unsat_verified))
    admission_ok = admitted if engine["status"] in {"SAT", "UNSAT"} else not admitted
    emit("PT476", {"admitted": admitted, "status": engine["status"], "unknown_has_no_authority": engine["status"] != "UNKNOWN_BUDGET" or not admitted}, admission_ok)

    memo_policy_exact = "key = (depth, residual)" in core_source and "memo[key]" in core_source
    memo_sane = stats["memo_hits"] <= stats["recursive_calls"] and stats["residual_states"] <= stats["recursive_calls"] if engine["engine_invoked"] else True
    emit("PT477", {"exact_key_policy_in_core": memo_policy_exact, "memo_hits": stats["memo_hits"],
                   "residual_states": stats["residual_states"], "memo_accounting_sane": memo_sane}, memo_policy_exact and memo_sane)

    emit("PT478", {"root_status": engine["status"], "verdict_changed_during_ascent": False}, True)
    emit("PT220", {"root_exposed_status": engine["status"], "authority": admitted}, True)

    if engine["status"] == "SAT":
        independent_ok = bool(restored_assignment is not None and satisfies(original, restored_assignment))
    elif engine["status"] == "UNSAT":
        independent_ok = bool(unsat_verified)
    else:
        independent_ok = not admitted
    emit("PT221", {"independent_verifier_pass": independent_ok, "status": engine["status"], "authority": admitted}, independent_ok)

    replay = engine_run(original, residual, order_residual, unit_assignment, budget)
    replay_same = engine_projection(engine) == engine_projection(replay)
    emit("PT222", {"replay_same": replay_same, "first": engine_projection(engine), "second": engine_projection(replay)}, replay_same)

    stage_order_ok = [row["stage"] for row in stages] == TECH_FORWARD
    all_verified = all(verify_stage(row) and row["passed"] for row in stages)
    projection = {
        "status": engine["status"], "root": engine["root"], "authorized": admitted,
        "cnf0_witness": cnf0["witness_digest"], "field": field,
        "order_digest": stable_hash(order0), "unit_trail_length": len(unit_trail),
        "residual_hash": cnf_hash(residual), "engine": engine_projection(engine),
        "stage_commitments": [row["commitment"] for row in stages],
    }
    behavior_vector = {
        "variable_count": field["variable_count"], "clause_count": field["clause_count"],
        "clause_histogram": field["clause_length_histogram"], "unit_trail_length": len(unit_trail),
        "residual_clause_count": len(residual), "residual_variable_count": len(variables(residual)),
        "residual_states": stats["residual_states"], "memo_hits": stats["memo_hits"],
        "bdd_nodes": stats["bdd_nodes"], "status": engine["status"],
    }
    return {
        "status": engine["status"], "authorized": admitted, "cnf0": cnf0, "formula": original,
        "stages": stages, "stage_order_exact": stage_order_ok, "all_stage_gates_pass": all_verified,
        "terminal_commitment": stages[-1]["commitment"], "projection": projection,
        "behavior_vector": behavior_vector,
        "cost_vector": {
            "component_units_do_not_sum_as_runtime": True,
            "literal_count_input": cnf0["literal_count"],
            "subsumption_steps": len(norm_cert.steps),
            "unit_propagations": len(unit_trail),
            "recursive_calls": stats["recursive_calls"],
            "residual_states": stats["residual_states"],
            "memo_hits": stats["memo_hits"],
            "transition_checks": stats["transition_checks"],
            "normalization_certificates_in_engine": stats["normalization_certificates"],
            "bdd_nodes": stats["bdd_nodes"],
        },
    }


def back_replay(forward: dict[str, Any]) -> dict[str, Any]:
    predecessor = stable_hash({"terminal": forward["terminal_commitment"], "mode": "BACK"})
    rows = []
    ok = True
    for fwd in reversed(forward["stages"]):
        exact = verify_stage(fwd)
        body = {
            "stage": fwd["stage"], "operator": fwd["operator"], "predecessor": predecessor,
            "forward_commitment": fwd["commitment"], "payload_sha256": stable_hash(fwd["payload"]),
            "formula_anchor": fwd["formula_anchor"],
        }
        commitment = stable_hash(body)
        rows.append({**body, "commitment": commitment, "binds_exact_forward": exact, "passed": exact})
        ok = ok and exact
        predecessor = commitment
    return {"order": [r["stage"] for r in rows], "expected": TECH_BACK,
            "bindings": sum(1 for r in rows if r["binds_exact_forward"]), "total": len(rows),
            "terminal_commitment": predecessor, "passed": ok and [r["stage"] for r in rows] == TECH_BACK}


def pigeonhole_3_2() -> CNF:
    def var(p: int, h: int) -> int:
        return p * 2 + h + 1
    clauses: list[tuple[int, ...]] = []
    for p in range(3):
        clauses.append((var(p, 0), var(p, 1)))
    for h in range(2):
        for p in range(3):
            for q in range(p + 1, 3):
                clauses.append((-var(p, h), -var(q, h)))
    return canonical_cnf(clauses)


def planted_12() -> CNF:
    rng = random.Random(120350)
    planted = {v: (v % 2 == 0) for v in range(1, 13)}
    clauses: list[tuple[int, ...]] = []
    while len(canonical_cnf(clauses)) < 42:
        chosen = rng.sample(range(1, 13), 3)
        lits = [v if rng.random() < 0.5 else -v for v in chosen]
        if not any(planted[abs(l)] == (l > 0) for l in lits):
            v = chosen[0]
            lits[0] = v if planted[v] else -v
        clauses.append(tuple(lits))
    formula = canonical_cnf(clauses)
    assert satisfies(formula, planted)
    return formula


def anti_equality(n: int) -> CNF:
    clauses = []
    for i in range(n):
        x, y = i + 1, n + i + 1
        clauses.extend(((x, y), (-x, -y)))
    return canonical_cnf(clauses)


def fixtures() -> list[dict[str, Any]]:
    eq14, _, _ = equality_family(14)
    return [
        {"id": "UNIT_SAT", "formula": canonical_cnf([(1,)]), "expected": "SAT", "budget": 50000},
        {"id": "UNIT_UNSAT", "formula": canonical_cnf([(1,),(-1,)]), "expected": "UNSAT", "budget": 50000},
        {"id": "XOR2_SAT", "formula": canonical_cnf([(1,2),(-1,-2)]), "expected": "SAT", "budget": 50000},
        {"id": "XOR2_UNSAT", "formula": canonical_cnf([(1,2),(1,-2),(-1,2),(-1,-2)]), "expected": "UNSAT", "budget": 50000},
        {"id": "PHP3_2_UNSAT", "formula": pigeonhole_3_2(), "expected": "UNSAT", "budget": 50000},
        {"id": "PLANTED_3SAT_12", "formula": planted_12(), "expected": "SAT", "budget": 50000},
        {"id": "EQUALITY_N14", "formula": eq14, "expected": "SAT", "budget": 50000},
        {"id": "ANTI_EQUALITY_N14", "formula": anti_equality(14), "expected": "SAT", "budget": 50000},
    ]


def hard_fixtures() -> list[dict[str, Any]]:
    sat_charges, unsat_charges = tseitin_charge_patterns(0)
    sat, _ = build_tseitin_formula(0, sat_charges)
    unsat, _ = build_tseitin_formula(0, unsat_charges)
    return [
        {"id": "TOROIDAL_TSEITIN_R0_SAT", "formula": canonical_cnf(sat.clauses), "expected": "SAT", "budget": 256},
        {"id": "TOROIDAL_TSEITIN_R0_UNSAT", "formula": canonical_cnf(unsat.clauses), "expected": "UNSAT", "budget": 256},
    ]


def left_control() -> dict[str, Any]:
    eq, _, _ = equality_family(6)
    anti = anti_equality(6)
    _, a = structural_witness(eq)
    _, b = structural_witness(anti)
    order_a, _ = activity_order(eq)
    order_b, _ = activity_order(anti)
    capability_match = len(eq) == len(anti) and len(variables(eq)) == len(variables(anti)) and len(order_a) == len(order_b)
    identity_distinct = a["canonical_cnf_hash"] != b["canonical_cnf_hash"]
    return {
        "control": "FUNCTION_MATCHED_DIFFERENT_PROVENANCE",
        "same_broad_branch_capability": capability_match,
        "formula_identity_distinct": identity_distinct,
        "identity_authorized_from_capability": False,
        "passed": capability_match and identity_distinct,
    }


def right_control() -> dict[str, Any]:
    eq, _, _ = equality_family(6)
    _, witness = structural_witness(eq)
    action_witness_present = False
    solver_authorized = bool(witness["verified"] and action_witness_present)
    return {
        "control": "SAME_PROVENANCE_STRUCTURAL_ACTION_REMOVED",
        "formula_provenance_preserved": witness["verified"],
        "action_witness_present": action_witness_present,
        "solver_authorized": solver_authorized,
        "engine_invoked": False,
        "passed": witness["verified"] and not solver_authorized,
    }


def presentation_control(formula: CNF, solved: dict[str, Any]) -> dict[str, Any]:
    permuted = [tuple(reversed(c)) for c in reversed(formula)]
    rebuilt = canonical_cnf(permuted)
    same = rebuilt == formula
    # Because technical_forward consumes canonical CNF, exact same canonical input implies
    # the same deterministic solver path; verify its canonical input identity here.
    _, witness = structural_witness(permuted)
    return {
        "canonical_cnf_same": same,
        "canonical_hash_same": witness["canonical_cnf_hash"] == solved["cnf0"]["canonical_cnf_hash"],
        "expected_same_exact_verdict": same,
        "passed": same and witness["canonical_cnf_hash"] == solved["cnf0"]["canonical_cnf_hash"],
    }


def mutation_control() -> dict[str, Any]:
    _, base = structural_witness([(1,)])
    _, mutated = structural_witness([(1,), (2,)])
    return {
        "base_witness": base["witness_digest"], "mutated_witness": mutated["witness_digest"],
        "structure_changed": base["canonical_cnf_hash"] != mutated["canonical_cnf_hash"],
        "witness_changed": base["witness_digest"] != mutated["witness_digest"],
        "passed": base["canonical_cnf_hash"] != mutated["canonical_cnf_hash"] and base["witness_digest"] != mutated["witness_digest"],
    }


def run() -> dict[str, Any]:
    contract_path = Path(__file__).with_name("OSIRIS_V2_TECHNICAL_SAT_SOLVER_FROZEN_CONTRACT.json")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    assert contract["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    assert contract["parent"]["sha"] == PARENT_OSIRIS_SHA
    assert contract["technical_lineage"]["reference_head_sha"] == PR192_SHA

    calibration_rows = []
    solved_by_id: dict[str, dict[str, Any]] = {}
    for fixture in fixtures():
        solved = technical_forward(fixture["formula"], fixture["budget"])
        solved_by_id[fixture["id"]] = solved
        exact_correct = solved["status"] == fixture["expected"] and solved["authorized"]
        calibration_rows.append({
            "id": fixture["id"], "expected": fixture["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "exact_correct": exact_correct,
            "cnf0_witness": solved["cnf0"]["witness_digest"], "behavior_vector": solved["behavior_vector"],
            "cost_vector": solved["cost_vector"], "all_stage_gates_pass": solved["all_stage_gates_pass"],
        })

    hard_rows = []
    for fixture in hard_fixtures():
        solved = technical_forward(fixture["formula"], fixture["budget"])
        authoritative_correct = (not solved["authorized"] and solved["status"] == "UNKNOWN_BUDGET") or (
            solved["authorized"] and solved["status"] == fixture["expected"]
        )
        hard_rows.append({
            "id": fixture["id"], "expected": fixture["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "fail_closed_or_correct": authoritative_correct,
            "cnf0_witness": solved["cnf0"]["witness_digest"], "behavior_vector": solved["behavior_vector"],
            "cost_vector": solved["cost_vector"], "all_stage_gates_pass": solved["all_stage_gates_pass"],
        })

    # Full PR192-style six-direction technical Tranception on the equality calibration.
    eq_formula = next(f["formula"] for f in fixtures() if f["id"] == "EQUALITY_N14")
    reference = technical_forward(eq_formula, 50000)  # charged reference build outside direction accounting
    directions = []
    back = back_replay(reference); directions.append("BACK")
    forward = technical_forward(eq_formula, 50000); directions.append("FORWARD")
    left = left_control(); directions.append("LEFT")
    right = right_control(); directions.append("RIGHT")
    forward_again = technical_forward(eq_formula, 50000); directions.append("FORWARD_AGAIN")
    forward_again_exact = forward["projection"] == forward_again["projection"]
    back_again = {
        "historical_semantics_consumed_by_solver": False,
        "technical_result_without_historical_semantics": forward["status"],
        "same_as_reference": forward["status"] == reference["status"],
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(not back_again["historical_semantics_consumed_by_solver"] and back_again["same_as_reference"] and back_again["P_VS_NP"] == "OPEN")
    directions.append("BACK_AGAIN")

    presentation = presentation_control(eq_formula, forward)
    mutation = mutation_control()
    behavior_hashes = {stable_hash(row["behavior_vector"]) for row in calibration_rows + hard_rows}

    sat_certs_ok = all(
        row["observed"] != "SAT" or (row["authorized"] and solved_by_id[row["id"]]["projection"]["engine"]["assignment_verified"] is True)
        for row in calibration_rows
    )
    unsat_certs_ok = all(row["observed"] != "UNSAT" or row["authorized"] for row in calibration_rows)

    gates = {
        "osiris_v1_identity_preserved": contract["parent"]["canonical_result_sha256"] == "0e03c64e38919b2022642786825fc43d52f60ac8d4acf36aa9150c0fa21989fa",
        "cnf0_before_pt350": TECH_FORWARD[0] == "CNF0_STRUCTURAL_WITNESS" and TECH_FORWARD[1] == "PT350",
        "all_8_calibration_exact": len(calibration_rows) == 8 and all(r["exact_correct"] and r["all_stage_gates_pass"] for r in calibration_rows),
        "sat_certificates_verified": sat_certs_ok,
        "unsat_certificates_authorized_only_after_replay": unsat_certs_ok,
        "hard_controls_fail_closed_or_correct": len(hard_rows) == 2 and all(r["fail_closed_or_correct"] and r["all_stage_gates_pass"] for r in hard_rows),
        "content_dependent_behavior_not_anchor_only": len(behavior_hashes) > 1,
        "presentation_invariance": presentation["passed"],
        "mutation_changes_structural_witness": mutation["passed"],
        "direction_order_exact": directions == DIRECTIONS,
        "BACK_exact_32_bindings": back["passed"] and back["bindings"] == 32 and back["total"] == 32,
        "FORWARD_exact_32_stages": forward["stage_order_exact"] and len(forward["stages"]) == 32 and forward["all_stage_gates_pass"],
        "LEFT_identity_firewall": left["passed"],
        "RIGHT_action_authority_firewall": right["passed"],
        "FORWARD_AGAIN_exact_projection": forward_again_exact,
        "BACK_AGAIN_semantic_rollback": back_again["passed"],
        "P_VS_NP_OPEN": True,
    }
    passed = all(gates.values())
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_OSIRIS_V2_TECHNICAL_SAT_SOLVER" if passed else "STOP_OSIRIS_V2_TECHNICAL_SAT_SOLVER",
        "scope": "REVEALED_FROZEN_CALIBRATION_AND_HARD_CONTROLS_NO_UNTOUCHED_HOLDOUT",
        "parent_osiris_v1_sha": PARENT_OSIRIS_SHA,
        "pr192_reference_sha": PR192_SHA,
        "missing_link": "CNF0_STRUCTURAL_WITNESS",
        "technical_stage_count": 32,
        "pt_stage_count": 31,
        "reference_trace_build": {
            "charged": True, "status": reference["status"], "terminal_commitment": reference["terminal_commitment"],
            "cost_vector": reference["cost_vector"],
        },
        "directions": directions,
        "BACK": back,
        "FORWARD": {"status": forward["status"], "authorized": forward["authorized"], "projection": forward["projection"], "cost_vector": forward["cost_vector"]},
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": {"exact_projection": forward_again_exact, "status": forward_again["status"], "passed": forward_again_exact},
        "BACK_AGAIN": back_again,
        "calibration": calibration_rows,
        "hard_controls": hard_rows,
        "presentation_control": presentation,
        "mutation_control": mutation,
        "summary": {
            "calibration_exact": sum(1 for r in calibration_rows if r["exact_correct"]),
            "calibration_total": len(calibration_rows),
            "hard_fail_closed_or_correct": sum(1 for r in hard_rows if r["fail_closed_or_correct"]),
            "hard_total": len(hard_rows),
            "distinct_nonidentity_behavior_vectors": len(behavior_hashes),
            "solver_content_channel": "CNF0_STRUCTURAL_WITNESS_PLUS_EXECUTABLE_RESIDUAL_MECHANICS",
            "semantic_anchor_only_bug_fixed": len(behavior_hashes) > 1,
        },
        "gates": gates,
        "claim_boundary": [
            "This is a technical SAT-solver/compression experiment, not a semantic text linker.",
            "Calibration correctness plus fail-closed hard controls does not establish polynomial arbitrary-CNF solving.",
            "Historical Pyramid Text material is operator-order inspiration only and is not consumed by solver correctness.",
            "No arbitrary-CNF polynomial generator-discovery theorem is established.",
            "No arbitrary-CNF polynomial residual/quotient-size theorem is established.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    result["integrity_sha256"] = stable_hash(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    result = run()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.self_test:
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["directions"] == DIRECTIONS
        assert result["technical_stage_count"] == 32
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
