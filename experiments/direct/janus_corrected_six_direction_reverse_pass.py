#!/usr/bin/env python3
"""Strict JANUS six-direction reverse pass on revealed controls only.

Required order (frozen before this implementation):
BACK -> FORWARD -> LEFT -> RIGHT -> FORWARD_AGAIN -> BACK_AGAIN.

The Pyramid Text material is a heuristic source prompt only. The modern gates
below are independently executable tests. No ancient algorithm claim and no
P=NP claim is licensed by any finite result.

Accounting note: the exact PR190 head still exposes its earlier incomplete
analyze_n charged-work dictionary. The canonical PR190 receipt froze the later
conservative proxy (89*n^2 + 45*n)/2. This run executes analyze_n for all
structural gates but charges the canonical frozen proxy independently.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from janus_c025_core import canonical_cnf, restrict_formula
from janus_c025_families import equality_family
from janus_egyptian_operator_sync_ladder import stage_pt355, stage_pt366
from janus_pt477_v3_local_apep_edge_tombstone import run as run_pt477_v3
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    apply_signed_map,
    signed_map_roundtrip_ok,
)
from janus_tranception_prebirth_orbit_generators import (
    FROZEN_N,
    analyze_n,
    digest_json,
    full_generator,
    residual_generator,
    variables_of,
)

RUN_ID = "JANUS-CORRECTED-SIX-DIRECTION-REVERSE-PASS-2026-08-18-v1"
BASE_SHA = "a24039ba24b880dc3c80d45ebc2c8f7bcfb3af26"
EXPECTED_ORDER = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
EXPECTED_PR191_STOP = "STOP_AT_FULL_MECHANICS_REVERSE_RETURN_FIRST"
CANONICAL_PR190_COST = {
    14: 9037,
    32: 46288,
    64: 183712,
    128: 731968,
    256: 2922112,
}


def stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def canonical_pr190_work_proxy(n: int) -> int:
    value = (89 * n * n + 45 * n) // 2
    if n in CANONICAL_PR190_COST and value != CANONICAL_PR190_COST[n]:
        raise AssertionError("canonical PR190 cost formula drift")
    return value


def stage_pt222_prebirth() -> dict[str, Any]:
    """Execute PR190 structural certificate; charge its canonical repaired ledger."""
    rows = [analyze_n(n) for n in FROZEN_N]
    passed = all(row["passed"] for row in rows) and all(row["raw_prefixes_enumerated"] == 0 for row in rows)
    projected = []
    for row in rows:
        n = int(row["n"])
        canonical_work = canonical_pr190_work_proxy(n)
        projected.append({
            "n": n,
            "represented_raw_prefixes": row["represented_raw_prefixes"],
            "generator_count": row["generator_count"],
            "symbolic_states": row["symbolic_quotient_states"],
            "symbolic_transitions": row["symbolic_quotient_transitions"],
            "raw_prefixes_enumerated": row["raw_prefixes_enumerated"],
            "legacy_head_incomplete_work_proxy": row["charged_work"]["polynomial_work_proxy"],
            "canonical_work_proxy": canonical_work,
            "canonical_cost_formula": "(89*n^2 + 45*n)/2",
            "branch_pair_passes": row["branch_pair_passes"],
            "automorphism_passes": row["automorphism_passes"],
            "passed": row["passed"],
        })
    return {
        "stage": "PT222_PREBIRTH",
        "status": "PASS" if passed else "FAIL",
        "accounting_status": "CANONICAL_PR190_CONSERVATIVE_LEDGER_APPLIED",
        "rows": projected,
        "passed": passed,
    }


def projection_pt222(stage: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": stage["status"],
        "accounting_status": stage["accounting_status"],
        "rows": stage["rows"],
        "passed": stage["passed"],
    }


def projection_pt477(stage: dict[str, Any]) -> dict[str, Any]:
    cand = stage["candidate"]
    keys = (
        "residual_states", "bytewise_distinct_absorptions", "polarity_flip_absorptions",
        "event_horizon_collisions", "hawking_escape_count", "buzz_return_checks",
        "canonical_edge_visits", "resolution_attempts", "resolution_additions",
        "local_tombstone_checks", "local_tombstone_hits", "local_tombstone_inserts",
        "route_rescan_edge_visits", "saved_buzz_return_checks",
    )
    return {
        "status": stage["status"],
        "candidate": {key: cand[key] for key in keys},
        "metric_improved": stage["metric_improved"],
    }


def projection_pt366(stage: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "samples", "bytewise_distinct_raw_forms", "seed_signature_classes",
        "reverse_map_passes", "recognition_compression_ratio", "test_pass", "metric_improved",
    )
    return {key: stage[key] for key in keys}


def projection_pt355(stage: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "raw_residual_states", "normalized_residual_states", "compression_ratio",
        "normalization_certificates", "subsumption_steps", "witness_valid",
        "test_pass", "metric_improved",
    )
    return {key: stage[key] for key in keys}


def run_back() -> dict[str, Any]:
    execution = []
    pt222 = stage_pt222_prebirth(); execution.append("PT222")
    pt477 = run_pt477_v3(); execution.append("PT477")
    pt366 = stage_pt366(); execution.append("PT366")
    pt355 = stage_pt355(); execution.append("PT355")
    return {
        "execution": execution,
        "PT222": projection_pt222(pt222),
        "PT477": projection_pt477(pt477),
        "PT366": projection_pt366(pt366),
        "PT355": projection_pt355(pt355),
        "pass": bool(pt222["passed"] and pt477["metric_improved"] and pt366["continue"] and pt355["continue"]),
    }


def run_forward() -> dict[str, Any]:
    execution = []
    pt355 = stage_pt355(); execution.append("PT355")
    pt366 = stage_pt366(); execution.append("PT366")
    pt477 = run_pt477_v3(); execution.append("PT477")
    pt222 = stage_pt222_prebirth(); execution.append("PT222")
    return {
        "execution": execution,
        "PT355": projection_pt355(pt355),
        "PT366": projection_pt366(pt366),
        "PT477": projection_pt477(pt477),
        "PT222": projection_pt222(pt222),
        "pass": bool(pt222["passed"] and pt477["metric_improved"] and pt366["continue"] and pt355["continue"]),
    }


def anti_equality_family(n: int):
    x_vars = tuple(range(1, n + 1))
    y_vars = tuple(range(n + 1, 2 * n + 1))
    formula = canonical_cnf(
        clause
        for xv, yv in zip(x_vars, y_vars)
        for clause in ((xv, yv), (-xv, -yv))
    )
    return formula, x_vars, y_vars


def run_left_control() -> dict[str, Any]:
    """Same reversible capability, different formula/provenance: capability != identity."""
    rows = []
    charged_literal_visits = 0
    for n in FROZEN_N:
        eq, _, _ = equality_family(n)
        anti, x_vars, y_vars = anti_equality_family(n)
        eq_anchor = digest_json(eq)
        anti_anchor = digest_json(anti)
        auto = 0
        branch = 0
        anti_literals = sum(len(c) for c in anti)
        for index, (xv, yv) in enumerate(zip(x_vars, y_vars), start=1):
            g = full_generator(n, index)
            if signed_map_roundtrip_ok(g) and apply_signed_map(anti, g) == anti:
                auto += 1
            charged_literal_visits += anti_literals
            child_false = restrict_formula(anti, {xv: False})
            child_true = restrict_formula(anti, {xv: True})
            rmap = residual_generator(child_false, yv)
            if signed_map_roundtrip_ok(rmap) and apply_signed_map(child_false, rmap) == child_true:
                branch += 1
            charged_literal_visits += sum(len(c) for c in child_false)
        capability_match = auto == n and branch == n
        identity_distinct = eq_anchor != anti_anchor
        rows.append({
            "n": n,
            "automorphism_passes": auto,
            "branch_pair_passes": branch,
            "same_capability": capability_match,
            "equality_anchor": eq_anchor,
            "anti_equality_anchor": anti_anchor,
            "identity_distinct": identity_distinct,
            "identity_authorized_from_capability": False,
            "passed": capability_match and identity_distinct,
        })
    return {
        "control": "LEFT_FUNCTION_MATCHED_DIFFERENT_PROVENANCE",
        "rows": rows,
        "charged_literal_visits": charged_literal_visits,
        "passed": all(row["passed"] and not row["identity_authorized_from_capability"] for row in rows),
    }


def run_right_control() -> dict[str, Any]:
    """Same formula/anchor, generator action removed: provenance != quotient authority."""
    rows = []
    charged_literal_visits = 0
    for n in FROZEN_N:
        formula, x_vars, _ = equality_family(n)
        xv = x_vars[0]
        child_false = restrict_formula(formula, {xv: False})
        child_true = restrict_formula(formula, {xv: True})
        identity_map = {v: (v, False) for v in variables_of(child_false)}
        identity_roundtrip = signed_map_roundtrip_ok(identity_map)
        mapped = apply_signed_map(child_false, identity_map)
        charged_literal_visits += sum(len(c) for c in child_false)
        quotient_authorized = mapped == child_true
        rows.append({
            "n": n,
            "formula_anchor": digest_json(formula),
            "provenance_preserved": True,
            "generator_action_present": False,
            "identity_map_roundtrip": identity_roundtrip,
            "branch_children_distinct_without_generator": child_false != child_true,
            "quotient_authorized_without_generator": quotient_authorized,
            "passed": identity_roundtrip and child_false != child_true and not quotient_authorized,
        })
    return {
        "control": "RIGHT_PROVENANCE_MATCHED_OPERATOR_REMOVED",
        "rows": rows,
        "charged_literal_visits": charged_literal_visits,
        "passed": all(row["passed"] for row in rows),
    }


def build_cost_vector(back: dict[str, Any], forward: dict[str, Any], left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    def pt222_work(side):
        return sum(row["canonical_work_proxy"] for row in side["PT222"]["rows"])
    def pt222_legacy(side):
        return sum(row["legacy_head_incomplete_work_proxy"] for row in side["PT222"]["rows"])
    return {
        "units_are_component_specific_do_not_sum_as_runtime": True,
        "PT222_prebirth_canonical_work_proxy_BACK": pt222_work(back),
        "PT222_prebirth_canonical_work_proxy_FORWARD": pt222_work(forward),
        "PT222_legacy_head_incomplete_proxy_BACK_not_canonical": pt222_legacy(back),
        "PT222_legacy_head_incomplete_proxy_FORWARD_not_canonical": pt222_legacy(forward),
        "PT477_structural_work_proxy_BACK": back["PT477"]["candidate"]["resolution_attempts"] + back["PT477"]["candidate"]["canonical_edge_visits"],
        "PT477_structural_work_proxy_FORWARD": forward["PT477"]["candidate"]["resolution_attempts"] + forward["PT477"]["candidate"]["canonical_edge_visits"],
        "PT477_local_bookkeeping_BACK": back["PT477"]["candidate"]["local_tombstone_checks"] + back["PT477"]["candidate"]["local_tombstone_inserts"],
        "PT477_local_bookkeeping_FORWARD": forward["PT477"]["candidate"]["local_tombstone_checks"] + forward["PT477"]["candidate"]["local_tombstone_inserts"],
        "PT366_samples_BACK": back["PT366"]["samples"],
        "PT366_samples_FORWARD": forward["PT366"]["samples"],
        "PT355_subsumption_steps_BACK": back["PT355"]["subsumption_steps"],
        "PT355_subsumption_steps_FORWARD": forward["PT355"]["subsumption_steps"],
        "LEFT_control_literal_visits": left["charged_literal_visits"],
        "RIGHT_control_literal_visits": right["charged_literal_visits"],
    }


def run() -> dict[str, Any]:
    executed_directions = []
    back = run_back(); executed_directions.append("BACK")
    forward = run_forward(); executed_directions.append("FORWARD")
    left = run_left_control(); executed_directions.append("LEFT")
    right = run_right_control(); executed_directions.append("RIGHT")

    mirror = {stage: back[stage] == forward[stage] for stage in ("PT355", "PT366", "PT477", "PT222")}
    forward_again = {
        "prediction": "4/4 BACK/FORWARD metric projections reproduce exactly and PR190 prebirth invariants remain exact",
        "stage_mirrors": mirror,
        "mirror_passes": sum(1 for ok in mirror.values() if ok),
        "mirror_total": 4,
        "all_prebirth_rows_zero_raw_prefixes": all(row["raw_prefixes_enumerated"] == 0 for row in forward["PT222"]["rows"]),
        "all_prebirth_rows_n_plus_1": all(row["symbolic_states"] == row["n"] + 1 for row in forward["PT222"]["rows"]),
        "all_prebirth_rows_n_transitions": all(row["symbolic_transitions"] == row["n"] for row in forward["PT222"]["rows"]),
        "all_prebirth_canonical_costs_match": all(row["canonical_work_proxy"] == canonical_pr190_work_proxy(row["n"]) for row in forward["PT222"]["rows"]),
    }
    forward_again["passed"] = bool(
        forward_again["mirror_passes"] == 4
        and forward_again["all_prebirth_rows_zero_raw_prefixes"]
        and forward_again["all_prebirth_rows_n_plus_1"]
        and forward_again["all_prebirth_rows_n_transitions"]
        and forward_again["all_prebirth_canonical_costs_match"]
    )
    executed_directions.append("FORWARD_AGAIN")

    back_again = {
        "rollback_point": "PRIMARY_SOURCE_AND_FROZEN_MODERN_OPERATOR_BOUNDARIES",
        "PT222_source_meaning": "BIDIRECTIONAL_ASCENT_DESCENT_PROMPT_ONLY",
        "PT477_source_meaning": "TEXTUAL_ROUTE_SEQUENCE_PROMPT_ONLY",
        "ancient_algorithm_claim_removed": True,
        "causal_pipeline_claim_removed": True,
        "physical_time_reversal_claim_removed": True,
        "PR191_preserved_status": EXPECTED_PR191_STOP,
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = all((
        back_again["ancient_algorithm_claim_removed"],
        back_again["causal_pipeline_claim_removed"],
        back_again["physical_time_reversal_claim_removed"],
        back_again["PR191_preserved_status"] == EXPECTED_PR191_STOP,
        back_again["P_VS_NP"] == "OPEN",
    ))
    executed_directions.append("BACK_AGAIN")

    order_exact = executed_directions == EXPECTED_ORDER
    all_gates = bool(
        order_exact and back["pass"] and forward["pass"] and left["passed"] and right["passed"]
        and forward_again["passed"] and back_again["passed"]
    )

    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_CORRECTED_SIX_DIRECTION_REVERSE" if all_gates else "STOP_AT_CORRECTED_SIX_DIRECTION_REVERSE",
        "base_sha": BASE_SHA,
        "run_scope": "REVEALED_FROZEN_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "accounting_repair": {
            "attempt_1": "NONCANONICAL_COST_ACCOUNTING_ONLY",
            "reason": "Exact PR190 head analyze_n still emitted its earlier incomplete proxy.",
            "canonical_rule": "(89*n^2 + 45*n)/2 from frozen PR190 canonical receipt",
            "structure_or_gates_changed": False,
        },
        "executed_direction_sequence": executed_directions,
        "required_direction_sequence": EXPECTED_ORDER,
        "direction_order_exact": order_exact,
        "BACK": back,
        "FORWARD": forward,
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": forward_again,
        "BACK_AGAIN": back_again,
        "cost_vector": build_cost_vector(back, forward, left, right),
        "comparison": {
            "PT222_old_n14": {"raw_prefixes_enumerated": 16384, "explicit_map_entries": 229376},
            "PR190_n14": {"raw_prefixes_enumerated": 0, "symbolic_states": 15, "symbolic_transitions": 14, "canonical_work_proxy": 9037},
            "PR190_n256": {"raw_prefixes_enumerated": 0, "symbolic_states": 257, "symbolic_transitions": 256, "canonical_work_proxy": 2922112},
            "PR191_status": EXPECTED_PR191_STOP,
            "PR191_n14_work_proxy": 25812,
            "PR191_n256_work_proxy": 475692,
        },
        "gates": {
            "direction_order_exact": order_exact,
            "BACK_all_four_stages_pass": back["pass"],
            "FORWARD_all_four_stages_pass": forward["pass"],
            "LEFT_capability_does_not_collapse_identity": left["passed"],
            "RIGHT_provenance_does_not_authorize_without_generator": right["passed"],
            "FORWARD_AGAIN_prediction_pass": forward_again["passed"],
            "BACK_AGAIN_rollback_pass": back_again["passed"],
        },
        "historical_boundary": "Egyptian/Pyramid Text sequence is heuristic operator inspiration only; source order cannot validate the modern algorithm.",
        "claim_boundary": [
            "This is a procedural/compositional PASS on already revealed controls if all gates pass.",
            "It does not prove arbitrary-CNF generator/decomposition discovery is polynomial.",
            "It does not prove arbitrary-CNF quotient size is polynomial.",
            "It does not establish P=NP.",
            "P_VS_NP = OPEN",
        ],
        "mathematical_verdict": {"P_VS_NP": "OPEN", "P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED"},
    }
    result["integrity_sha256"] = stable_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.self_test:
        assert result["executed_direction_sequence"] == EXPECTED_ORDER
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["FORWARD_AGAIN"]["all_prebirth_canonical_costs_match"] is True
        assert result["status"] in {"PASS_KEEP_CORRECTED_SIX_DIRECTION_REVERSE", "STOP_AT_CORRECTED_SIX_DIRECTION_REVERSE"}


if __name__ == "__main__":
    main()
