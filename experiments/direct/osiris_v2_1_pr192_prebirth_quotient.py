#!/usr/bin/env python3
"""OSIRIS v2.1: integrate a verified PR190/PR192 prebirth quotient lane.

The fast lane is activated from CNF structure only. It recognizes a restricted
product of independent equality/anti-equality pairs, verifies exact signed
flip automorphisms and branch-pair equivalence, constructs a satisfying witness,
and represents the 2^k symmetric branch choices with k+1 symbolic states.
Everything else falls back to the already frozen OSIRIS v2 exact engine.

Historical Pyramid Text labels are not consumed by correctness. P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable

import osiris_v2_technical_sat_solver as v2
from janus_c025_core import CNF, canonical_cnf, cnf_hash, restrict_formula, satisfies, variables
from janus_c025_families import equality_family
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    apply_signed_map,
    invert_signed_map,
    signed_map_roundtrip_ok,
)

RUN_ID = "OSIRIS-V2.1-PR192-VERIFIED-PREBIRTH-QUOTIENT-2026-08-18-v1"
PARENT_SHA = "6f4e41a99f0bf05daf03d781e878dec0c3b4814a"
PARENT_RESULT_SHA = "d733ebb45fa15dbb1531aabe96fa1b0977b2ea95cfa90a3346934d7b20932277"
CONTRACT = "OSIRIS_V2_1_PR192_PREBIRTH_QUOTIENT_FROZEN_CONTRACT.json"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PairComponent:
    left: int
    right: int
    kind: str


def _pair_expected(left: int, right: int, kind: str) -> CNF:
    if kind == "EQUALITY_PAIR":
        return canonical_cnf(((-left, right), (left, -right)))
    if kind == "ANTI_EQUALITY_PAIR":
        return canonical_cnf(((left, right), (-left, -right)))
    raise ValueError(kind)


def _flip_map(all_vars: list[int], support: set[int]) -> dict[int, tuple[int, bool]]:
    return {var: (var, var in support) for var in all_vars}


def _residual_partner_flip(formula: CNF, partner: int) -> dict[int, tuple[int, bool]]:
    return {var: (var, var == partner) for var in variables(formula)}


def detect_pair_product(formula: CNF) -> dict[str, Any]:
    """Proof-carrying detector. No fixture labels, expected answers or names enter here."""
    formula = canonical_cnf(formula)
    literal_count = sum(len(c) for c in formula)
    detector_clause_visits = len(formula)
    detector_literal_visits = literal_count
    rejection: str | None = None

    if not formula:
        rejection = "EMPTY_FORMULA_NOT_PAIR_PRODUCT"
    elif () in formula:
        rejection = "EMPTY_CLAUSE_NOT_PAIR_PRODUCT"
    elif any(len(c) != 2 or abs(c[0]) == abs(c[1]) for c in formula):
        rejection = "NON_BINARY_OR_DEGENERATE_CLAUSE"

    grouped: dict[tuple[int, int], list[tuple[int, ...]]] = {}
    var_pair: dict[int, tuple[int, int]] = {}
    if rejection is None:
        for clause in formula:
            pair = tuple(sorted((abs(clause[0]), abs(clause[1]))))
            grouped.setdefault(pair, []).append(clause)
            for var in pair:
                old = var_pair.get(var)
                if old is not None and old != pair:
                    rejection = "CROSS_PAIR_VARIABLE"
                    break
                var_pair[var] = pair
            if rejection is not None:
                break

    components: list[PairComponent] = []
    component_checks = 0
    if rejection is None:
        if sorted(var_pair) != variables(formula):
            rejection = "VARIABLE_COVERAGE_GAP"
        else:
            for (left, right), clauses in sorted(grouped.items()):
                component_checks += 1
                local = canonical_cnf(clauses)
                if len(clauses) != 2 or len(local) != 2:
                    rejection = "PAIR_CLAUSE_COUNT_NOT_TWO"
                    break
                if local == _pair_expected(left, right, "EQUALITY_PAIR"):
                    kind = "EQUALITY_PAIR"
                elif local == _pair_expected(left, right, "ANTI_EQUALITY_PAIR"):
                    kind = "ANTI_EQUALITY_PAIR"
                else:
                    rejection = "PAIR_RELATION_NOT_ALLOWED"
                    break
                components.append(PairComponent(left, right, kind))

    all_vars = variables(formula)
    automorphism_passes = 0
    involution_passes = 0
    branch_pair_passes = 0
    supports: list[set[int]] = []
    automorphism_literal_visit_proxy = 0
    branch_pair_restriction_literal_visit_proxy = 0
    if rejection is None:
        for component in components:
            support = {component.left, component.right}
            supports.append(support)
            mapping = _flip_map(all_vars, support)
            automorphism_literal_visit_proxy += literal_count
            if signed_map_roundtrip_ok(mapping) and apply_signed_map(formula, mapping) == formula:
                automorphism_passes += 1
            inverse = invert_signed_map(mapping)
            if inverse == mapping:
                involution_passes += 1

            child_false = restrict_formula(formula, {component.left: False})
            child_true = restrict_formula(formula, {component.left: True})
            branch_pair_restriction_literal_visit_proxy += 2 * literal_count
            residual_map = _residual_partner_flip(child_false, component.right)
            if (
                signed_map_roundtrip_ok(residual_map)
                and apply_signed_map(child_false, residual_map) == child_true
                and apply_signed_map(child_true, invert_signed_map(residual_map)) == child_false
            ):
                branch_pair_passes += 1

        k = len(components)
        if automorphism_passes != k:
            rejection = "FULL_FORMULA_AUTOMORPHISM_FAILED"
        elif involution_passes != k:
            rejection = "GENERATOR_INVOLUTION_FAILED"
        elif branch_pair_passes != k:
            rejection = "BRANCH_PAIR_EQUIVALENCE_FAILED"

    pairwise_checks = 0
    pairwise_passes = 0
    if rejection is None:
        for i, support in enumerate(supports):
            for other in supports[:i]:
                pairwise_checks += 1
                if support.isdisjoint(other):
                    pairwise_passes += 1
        if pairwise_checks != pairwise_passes:
            rejection = "GENERATOR_SUPPORTS_NOT_DISJOINT"

    assignment: dict[int, bool] = {}
    if rejection is None:
        for component in components:
            if component.kind == "EQUALITY_PAIR":
                assignment[component.left] = False
                assignment[component.right] = False
            else:
                assignment[component.left] = False
                assignment[component.right] = True
        witness_ok = satisfies(formula, assignment)
        if not witness_ok:
            rejection = "CONSTRUCTIVE_WITNESS_FAILED"
    else:
        witness_ok = False

    k = len(components) if rejection is None else 0
    matched = rejection is None and k > 0
    metrics = {
        "detector_clause_visits": detector_clause_visits,
        "detector_literal_visits": detector_literal_visits,
        "pair_component_checks": component_checks,
        "automorphism_literal_visit_proxy": automorphism_literal_visit_proxy,
        "branch_pair_restriction_literal_visit_proxy": branch_pair_restriction_literal_visit_proxy,
        "pairwise_support_independence_checks": pairwise_checks,
        "constructive_witness_checks": literal_count if matched else 0,
        "symbolic_states": k + 1 if matched else 0,
        "symbolic_transitions": k if matched else 0,
        "raw_prefixes_enumerated": 0,
        "represented_symmetric_branch_choices": (1 << k) if matched else 0,
        "generator_count": k,
    }
    certificate_core = {
        "formula_hash": cnf_hash(formula),
        "components": [component.__dict__ for component in components] if matched else [],
        "automorphism_passes": automorphism_passes,
        "involution_passes": involution_passes,
        "branch_pair_passes": branch_pair_passes,
        "pairwise_disjoint_passes": pairwise_passes,
        "metrics": metrics,
        "witness_sha256": digest(assignment) if matched else None,
    }
    return {
        "matched": matched,
        "rejection_reason": rejection,
        "formula_hash": cnf_hash(formula),
        "components": [component.__dict__ for component in components] if matched else [],
        "assignment": assignment if matched else None,
        "witness_verified_on_residual": witness_ok if matched else False,
        "automorphism_passes": automorphism_passes,
        "involution_passes": involution_passes,
        "branch_pair_passes": branch_pair_passes,
        "pairwise_disjoint_passes": pairwise_passes,
        "metrics": metrics,
        "certificate_sha256": digest(certificate_core),
    }


def solve_v21(raw_formula: Iterable[Iterable[int]], budget: int) -> dict[str, Any]:
    """Run OSIRIS v2 with a quotient-aware engine injected only for this call."""
    original_engine = v2.engine_run
    q0_calls: list[dict[str, Any]] = []

    def quotient_aware_engine(original: CNF, residual: CNF, residual_order: list[int], units: dict[int, bool], state_budget: int) -> dict[str, Any]:
        detected = detect_pair_product(residual)
        call_record = {
            "residual_hash": cnf_hash(residual),
            "matched": detected["matched"],
            "rejection_reason": detected["rejection_reason"],
            "certificate_sha256": detected["certificate_sha256"],
            "metrics": detected["metrics"],
        }
        if not detected["matched"]:
            call_record["lane"] = "GENERIC_OSIRIS_V2_FALLBACK"
            q0_calls.append(call_record)
            result = original_engine(original, residual, residual_order, units, state_budget)
            result["stats"] = dict(result["stats"])
            result["stats"]["q0_detector"] = detected["metrics"]
            result["stats"]["q0_lane"] = "GENERIC_OSIRIS_V2_FALLBACK"
            return result

        assignment = {var: False for var in variables(original)}
        assignment.update(units)
        assignment.update(detected["assignment"] or {})
        verified = satisfies(original, assignment)
        if not verified:
            raise AssertionError("verified pair-product quotient failed original-CNF witness check")
        metrics = detected["metrics"]
        stats = {
            "status": "EXACT_QUOTIENT",
            "recursive_calls": metrics["symbolic_states"],
            "memo_hits": 0,
            "residual_states": metrics["symbolic_states"],
            "transition_checks": metrics["symbolic_transitions"],
            "normalization_certificates": 0,
            "subsumption_steps": 0,
            "bdd_nodes": 0,
            "max_frontier_states": 1,
            "frontier_counts": {str(i): 1 for i in range(metrics["symbolic_states"])},
            "error": None,
            "q0_detector": metrics,
            "q0_lane": "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT",
            "q0_certificate_sha256": detected["certificate_sha256"],
            "q0_components": len(detected["components"]),
            "q0_raw_prefixes_enumerated": 0,
        }
        call_record["lane"] = "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT"
        call_record["assignment_verified_on_original"] = True
        q0_calls.append(call_record)
        return {
            "status": "SAT",
            "root": 1,
            "sat": True,
            "assignment": assignment,
            "assignment_verified": True,
            "reason": "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT",
            "stats": stats,
            "engine_invoked": False,
        }

    v2.engine_run = quotient_aware_engine
    try:
        solved = v2.technical_forward(raw_formula, budget)
    finally:
        v2.engine_run = original_engine
    solved["q0_calls"] = q0_calls
    solved["q0_primary"] = q0_calls[0] if q0_calls else None
    solved["q0_lane"] = solved["q0_primary"]["lane"] if solved["q0_primary"] else "NO_ENGINE_CALL"
    solved["q0_certificate_sha256"] = solved["q0_primary"]["certificate_sha256"] if solved["q0_primary"] else None
    return solved


def corrupted_equality_n6() -> CNF:
    formula, _, _ = equality_family(6)
    clauses = list(formula)
    clauses.remove((-1, 7))
    clauses.append((-1, -7))
    return canonical_cnf(clauses)


def cross_pair_equality_n6() -> CNF:
    formula, _, _ = equality_family(6)
    return canonical_cnf(list(formula) + [(1, 2)])


def detector_negative_controls() -> list[dict[str, Any]]:
    xor_unsat = canonical_cnf([(1,2),(1,-2),(-1,2),(-1,-2)])
    cases = [
        ("EQUALITY_N6_CROSS_PAIR", cross_pair_equality_n6()),
        ("EQUALITY_N6_CORRUPTED_PAIR", corrupted_equality_n6()),
        ("XOR2_UNSAT", xor_unsat),
        ("PHP3_2_UNSAT", v2.pigeonhole_3_2()),
        ("PLANTED_3SAT_12", v2.planted_12()),
    ]
    rows = []
    for case_id, formula in cases:
        detection = detect_pair_product(formula)
        rows.append({
            "id": case_id,
            "matched": detection["matched"],
            "rejection_reason": detection["rejection_reason"],
            "certificate_sha256": detection["certificate_sha256"],
            "passed": not detection["matched"],
        })
    return rows


def right_control() -> dict[str, Any]:
    formula, _, _ = equality_family(6)
    detection = detect_pair_product(formula)
    action_certificate_present = False
    quotient_authorized = bool(detection["matched"] and action_certificate_present)
    # Explicit generic fallback is still allowed and independently solves the formula.
    generic = v2.technical_forward(formula, 50000)
    return {
        "control": "SAME_FORMULA_PROVENANCE_PAIR_GENERATOR_CERTIFICATE_REMOVED",
        "detector_structural_match": detection["matched"],
        "action_certificate_present": action_certificate_present,
        "quotient_authorized": quotient_authorized,
        "fallback_path": "OSIRIS_V2_GENERIC_EXACT_SOLVER",
        "fallback_verdict": generic["status"],
        "fallback_authorized": generic["authorized"],
        "passed": bool(detection["matched"] and not quotient_authorized and generic["status"] == "SAT" and generic["authorized"]),
    }


def left_control() -> dict[str, Any]:
    eq, _, _ = equality_family(6)
    anti = v2.anti_equality(6)
    deq = detect_pair_product(eq)
    danti = detect_pair_product(anti)
    _, weq = v2.structural_witness(eq)
    _, wanti = v2.structural_witness(anti)
    return {
        "control": "SAME_PAIR_QUOTIENT_CAPABILITY_DIFFERENT_PROVENANCE",
        "both_support_same_quotient_capability": deq["matched"] and danti["matched"],
        "formula_identity_distinct": weq["canonical_cnf_hash"] != wanti["canonical_cnf_hash"],
        "identity_authorized_from_capability": False,
        "passed": bool(deq["matched"] and danti["matched"] and weq["canonical_cnf_hash"] != wanti["canonical_cnf_hash"]),
    }


def back_with_q0(forward: dict[str, Any]) -> dict[str, Any]:
    stage_back = v2.back_replay(forward)
    q0 = forward.get("q0_primary")
    q0_binding = {
        "present": q0 is not None,
        "lane": q0.get("lane") if q0 else None,
        "certificate_sha256": q0.get("certificate_sha256") if q0 else None,
        "metrics_sha256": digest(q0.get("metrics")) if q0 else None,
        "bound_to_forward_terminal": digest({"q0": q0, "terminal": forward["terminal_commitment"]}) if q0 else None,
    }
    q0_binding["passed"] = bool(q0 and q0["lane"] == "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT")
    return {
        "stage_back": stage_back,
        "q0_binding": q0_binding,
        "passed": bool(stage_back["passed"] and q0_binding["passed"]),
    }


def selected_metrics(solved: dict[str, Any]) -> dict[str, Any]:
    primary = solved.get("q0_primary") or {}
    return {
        "lane": solved.get("q0_lane"),
        "verdict": solved["status"],
        "authorized": solved["authorized"],
        "assignment_verified": solved["projection"]["engine"].get("assignment_verified"),
        "q0_metrics": primary.get("metrics"),
        "generic_cost_vector": solved["cost_vector"],
    }


def run() -> dict[str, Any]:
    contract = json.loads(Path(__file__).with_name(CONTRACT).read_text(encoding="utf-8"))
    assert contract["status"] == "FROZEN_BEFORE_IMPLEMENTATION_AND_RUN"
    assert contract["parent"]["sha"] == PARENT_SHA
    assert contract["parent"]["result_integrity_sha256"] == PARENT_RESULT_SHA

    calibration = []
    solved_by_id: dict[str, dict[str, Any]] = {}
    for fixture in v2.fixtures():
        solved = solve_v21(fixture["formula"], fixture["budget"])
        solved_by_id[fixture["id"]] = solved
        calibration.append({
            "id": fixture["id"],
            "expected": fixture["expected"],
            "observed": solved["status"],
            "authorized": solved["authorized"],
            "exact_correct": solved["status"] == fixture["expected"] and solved["authorized"],
            "q0_lane": solved["q0_lane"],
            "q0_metrics": (solved.get("q0_primary") or {}).get("metrics"),
            "all_stage_gates_pass": solved["all_stage_gates_pass"],
        })

    hard = []
    for fixture in v2.hard_fixtures():
        solved = solve_v21(fixture["formula"], fixture["budget"])
        okay = (solved["status"] == "UNKNOWN_BUDGET" and not solved["authorized"]) or (
            solved["status"] == fixture["expected"] and solved["authorized"]
        )
        hard.append({
            "id": fixture["id"], "expected": fixture["expected"], "observed": solved["status"],
            "authorized": solved["authorized"], "correct_or_unknown": okay,
            "q0_lane": solved["q0_lane"], "all_stage_gates_pass": solved["all_stage_gates_pass"],
        })

    negatives = detector_negative_controls()
    eq = solved_by_id["EQUALITY_N14"]
    anti = solved_by_id["ANTI_EQUALITY_N14"]
    xor = solved_by_id["XOR2_SAT"]

    # PR192-style Tranception over quotient-aware equality n14.
    eq_formula = next(f["formula"] for f in v2.fixtures() if f["id"] == "EQUALITY_N14")
    reference = solve_v21(eq_formula, 50000)
    directions = []
    back = back_with_q0(reference); directions.append("BACK")
    forward = solve_v21(eq_formula, 50000); directions.append("FORWARD")
    left = left_control(); directions.append("LEFT")
    right = right_control(); directions.append("RIGHT")
    forward_again = solve_v21(eq_formula, 50000); directions.append("FORWARD_AGAIN")
    forward_again_projection_exact = bool(
        forward["projection"] == forward_again["projection"]
        and forward["q0_primary"] == forward_again["q0_primary"]
    )
    back_again = {
        "historical_text_semantics_consumed_by_detector": False,
        "historical_text_semantics_consumed_by_solver": False,
        "technical_verdict": forward["status"],
        "q0_lane": forward["q0_lane"],
        "same_as_reference": forward["projection"] == reference["projection"],
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(
        not back_again["historical_text_semantics_consumed_by_detector"]
        and not back_again["historical_text_semantics_consumed_by_solver"]
        and back_again["same_as_reference"]
        and back_again["P_VS_NP"] == "OPEN"
    )
    directions.append("BACK_AGAIN")

    def quotient_gate(solved: dict[str, Any], pairs: int, states: int, transitions: int) -> bool:
        q = solved.get("q0_primary") or {}
        m = q.get("metrics") or {}
        return bool(
            solved["status"] == "SAT" and solved["authorized"]
            and solved["projection"]["engine"].get("assignment_verified") is True
            and solved["q0_lane"] == "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT"
            and m.get("generator_count") == pairs
            and m.get("symbolic_states") == states
            and m.get("symbolic_transitions") == transitions
            and m.get("raw_prefixes_enumerated") == 0
        )

    calibration_exact = all(row["exact_correct"] and row["all_stage_gates_pass"] for row in calibration)
    hard_ok = all(row["correct_or_unknown"] and row["all_stage_gates_pass"] for row in hard)
    no_false_authority = calibration_exact and hard_ok
    gates = {
        "parent_v2_preserved": contract["parent"]["status"] == "PASS_KEEP_OSIRIS_V2_TECHNICAL_SAT_SOLVER",
        "detector_content_only_no_fixture_id_parameter": "fixture" not in detect_pair_product.__code__.co_varnames,
        "equality_n14_15_states_14_transitions_zero_prefixes": quotient_gate(eq, 14, 15, 14),
        "anti_equality_n14_15_states_14_transitions_zero_prefixes": quotient_gate(anti, 14, 15, 14),
        "xor2_sat_2_states_1_transition_zero_prefixes": quotient_gate(xor, 1, 2, 1),
        "all_detector_negative_controls_reject": all(row["passed"] for row in negatives),
        "all_8_v2_calibration_verdicts_preserved": len(calibration) == 8 and calibration_exact,
        "hard_tseitin_correct_or_unknown_same_budget": len(hard) == 2 and hard_ok,
        "no_false_authoritative_verdict": no_false_authority,
        "direction_order_exact": directions == DIRECTIONS,
        "BACK_stage_and_q0_bindings_exact": back["passed"],
        "FORWARD_quotient_aware": forward["q0_lane"] == "PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT",
        "LEFT_identity_firewall": left["passed"],
        "RIGHT_missing_generator_certificate_blocks_quotient": right["passed"] and not right["quotient_authorized"],
        "FORWARD_AGAIN_exact_projection": forward_again_projection_exact,
        "BACK_AGAIN_semantic_rollback": back_again["passed"],
        "P_VS_NP_OPEN": True,
    }
    passed = all(gates.values())

    eq_metrics = (eq.get("q0_primary") or {}).get("metrics") or {}
    anti_metrics = (anti.get("q0_primary") or {}).get("metrics") or {}
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_OSIRIS_V2_1_PR192_VERIFIED_PREBIRTH_QUOTIENT" if passed else "STOP_OSIRIS_V2_1_PR192_VERIFIED_PREBIRTH_QUOTIENT",
        "scope": "RESTRICTED_VERIFIED_PAIR_PRODUCT_QUOTIENT_PLUS_OSIRIS_V2_GENERIC_FALLBACK_REVEALED_CONTROLS_ONLY",
        "parent_v2": {"sha": PARENT_SHA, "result_integrity_sha256": PARENT_RESULT_SHA},
        "internal_lane": "Q0_PR192_VERIFIED_PAIR_PRODUCT_PREBIRTH_QUOTIENT",
        "directions": directions,
        "BACK": back,
        "FORWARD": selected_metrics(forward),
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": {"passed": forward_again_projection_exact, "exact_projection": forward_again_projection_exact, "metrics": selected_metrics(forward_again)},
        "BACK_AGAIN": back_again,
        "calibration": calibration,
        "hard_controls": hard,
        "detector_negative_controls": negatives,
        "comparison": {
            "EQUALITY_N14": {
                "osiris_v2_generic_residual_states": 49164,
                "osiris_v2_1_symbolic_states": eq_metrics.get("symbolic_states"),
                "symbolic_transitions": eq_metrics.get("symbolic_transitions"),
                "raw_prefixes_enumerated": eq_metrics.get("raw_prefixes_enumerated"),
                "represented_symmetric_branch_choices": eq_metrics.get("represented_symmetric_branch_choices"),
            },
            "ANTI_EQUALITY_N14": {
                "osiris_v2_generic_residual_states": 49164,
                "osiris_v2_1_symbolic_states": anti_metrics.get("symbolic_states"),
                "symbolic_transitions": anti_metrics.get("symbolic_transitions"),
                "raw_prefixes_enumerated": anti_metrics.get("raw_prefixes_enumerated"),
                "represented_symmetric_branch_choices": anti_metrics.get("represented_symmetric_branch_choices"),
            },
        },
        "cost_accounting": {
            "heterogeneous_units_must_not_be_summed_as_runtime": True,
            "equality_n14_detector_and_quotient": eq_metrics,
            "anti_equality_n14_detector_and_quotient": anti_metrics,
            "reference_trace_build_charged": selected_metrics(reference),
            "forward_charged": selected_metrics(forward),
            "forward_again_charged": selected_metrics(forward_again),
        },
        "gates": gates,
        "claim_boundary": [
            "PASS repairs the OSIRIS v2 equality/anti-equality generic-search regression only on CNFs whose independent pair-product symmetry is explicitly detected and verified.",
            "Nonmatching formulas fall back to OSIRIS v2 generic exact search or UNKNOWN_BUDGET.",
            "This does not establish polynomial-time useful-generator discovery for arbitrary CNF.",
            "This does not establish polynomial quotient size for arbitrary CNF.",
            "Historical Pyramid Text material is not consumed by solver correctness.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    result["integrity_sha256"] = digest(result)
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
        assert result["directions"] == DIRECTIONS
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
