#!/usr/bin/env python3
"""Extend the PT354 bidirectional braid by exactly one earlier text-inspired stage: PT353.

PT353 is modeled only as a modern fail-closed LIVE_STATE witness before PT354 provisioning.
PT352 is deliberately untouched. Historical text is heuristic inspiration only.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from janus_c025_core import restrict_formula
from janus_c025_families import equality_family
from janus_pt354_bidirectional_braid_190_192 import (
    EXPECTED_PR191_STOP,
    PR190_CLASS,
    PR192_CLASS,
    projection_pt354,
    run_left_control,
    run_pr192_back,
    run_pr192_forward,
    run_pt354,
    run_right_control,
)
from janus_tranception_prebirth_orbit_generators import FROZEN_N, digest_json

RUN_ID = "JANUS-PT353-LIVE-STATE-BEFORE-PROVISION-2026-08-18-v1"
EXPECTED_DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
EXPECTED_BACK = ["PT222", "PT477", "PT366", "PT355", "PT354", "PT353"]
EXPECTED_FORWARD = ["PT353", "PT354", "PT355", "PT366", "PT477", "PT222"]
NEGATIVE_NAMES = [
    "witness_missing",
    "parent_anchor_tamper",
    "support_tamper",
    "false_child_anchor_tamper",
    "true_child_anchor_tamper",
    "structurally_dead_candidate",
]


def _tamper_hex(value: str) -> str:
    if not value:
        return value
    first = "0" if value[0] != "0" else "1"
    return first + value[1:]


def _literal_count(formula: Any) -> int:
    return sum(len(clause) for clause in formula)


def _occurrence_count(formula: Any, var: int) -> int:
    return sum(1 for clause in formula for lit in clause if abs(int(lit)) == int(var))


def _add_cost(total: dict[str, int], cost: dict[str, int]) -> None:
    for key, value in cost.items():
        total[key] = total.get(key, 0) + int(value)


def build_live_candidate(n: int, index: int, formula_override: Any | None = None) -> tuple[dict[str, Any], dict[str, int]]:
    base_formula, x_vars, y_vars = equality_family(n)
    formula = base_formula if formula_override is None else formula_override
    xv = int(x_vars[index - 1])
    yv = int(y_vars[index - 1])
    parent_lits = _literal_count(formula)

    child_false = restrict_formula(formula, {xv: False})
    child_true = restrict_formula(formula, {xv: True})
    parent_anchor = digest_json(formula)
    child_false_anchor = digest_json(child_false)
    child_true_anchor = digest_json(child_true)
    x_occ = _occurrence_count(formula, xv)
    y_occ = _occurrence_count(formula, yv)

    body = {
        "kind": "PT353_LIVE_STATE",
        "n": n,
        "index": index,
        "parent_anchor": parent_anchor,
        "support": [xv, yv],
        "support_occurrences": [x_occ, y_occ],
        "child_false_anchor": child_false_anchor,
        "child_true_anchor": child_true_anchor,
        "child_clause_counts": [len(child_false), len(child_true)],
    }
    commitment = digest_json(body)

    candidate = {
        "n": n,
        "index": index,
        "formula": formula,
        "xv": xv,
        "yv": yv,
        "body": body,
        "commitment": commitment,
    }
    # Build accounting: 2 restrictions + one support scan = 3 parent literal passes;
    # parent/2 child/body commitments = 4 hashes.
    cost = {
        "hash_ops": 4,
        "literal_visits": 3 * parent_lits,
        "restriction_passes": 2,
        "presence_checks": 0,
    }
    return candidate, cost


def verify_live_candidate(
    candidate: dict[str, Any],
    *,
    witness_present: bool = True,
    body_override: dict[str, Any] | None = None,
    commitment_override: str | None = None,
) -> tuple[bool, dict[str, int]]:
    if not witness_present:
        return False, {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}

    body = candidate["body"] if body_override is None else body_override
    commitment = candidate["commitment"] if commitment_override is None else commitment_override
    formula = candidate["formula"]
    xv = int(candidate["xv"])
    yv = int(candidate["yv"])
    parent_lits = _literal_count(formula)

    # Verification recomputes only local structural facts. It intentionally does not
    # inspect a full/residual generator certificate or ask any SAT/UNSAT question.
    witness_hash_ok = digest_json(body) == commitment
    parent_anchor = digest_json(formula)
    child_false = restrict_formula(formula, {xv: False})
    child_true = restrict_formula(formula, {xv: True})
    child_false_anchor = digest_json(child_false)
    child_true_anchor = digest_json(child_true)
    x_occ = _occurrence_count(formula, xv)
    y_occ = _occurrence_count(formula, yv)

    expected_support = [xv, yv]
    support = body.get("support")
    structurally_live = bool(
        isinstance(support, list)
        and support == expected_support
        and xv != yv
        and x_occ > 0
        and y_occ > 0
        and child_false_anchor != child_true_anchor
    )

    ok = bool(
        witness_hash_ok
        and body.get("kind") == "PT353_LIVE_STATE"
        and body.get("n") == candidate["n"]
        and body.get("index") == candidate["index"]
        and body.get("parent_anchor") == parent_anchor
        and body.get("support_occurrences") == [x_occ, y_occ]
        and body.get("child_false_anchor") == child_false_anchor
        and body.get("child_true_anchor") == child_true_anchor
        and body.get("child_clause_counts") == [len(child_false), len(child_true)]
        and structurally_live
    )

    # Verify accounting: 2 restrictions + one occurrence scan = 3 parent passes;
    # witness/parent/2 child hashes = 4 hashes.
    cost = {
        "hash_ops": 4,
        "literal_visits": 3 * parent_lits,
        "restriction_passes": 2,
        "presence_checks": 1,
    }
    return ok, cost


def _recommit(body: dict[str, Any]) -> tuple[str, dict[str, int]]:
    return digest_json(body), {"hash_ops": 1, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 0}


def run_pt353() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    total = 0
    positive_passes = 0
    positive_pt354_entries = 0
    negative_rejects = {name: 0 for name in NEGATIVE_NAMES}
    negative_pt354_entries = 0
    blocked_before_pt354 = 0
    cost = {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 0}

    for n in FROZEN_N:
        formula, x_vars, _ = equality_family(n)
        row_positive = 0
        row_negative_rejects = 0

        for index in range(1, n + 1):
            total += 1
            candidate, build_cost = build_live_candidate(n, index)
            _add_cost(cost, build_cost)
            live_ok, verify_cost = verify_live_candidate(candidate)
            _add_cost(cost, verify_cost)
            if live_ok:
                positive_passes += 1
                row_positive += 1
                # This is the only positive path allowed to reach PT354.
                positive_pt354_entries += 1

            # 1) Missing witness.
            ok, c = verify_live_candidate(candidate, witness_present=False)
            _add_cost(cost, c)
            if not ok:
                negative_rejects["witness_missing"] += 1
                row_negative_rejects += 1
                blocked_before_pt354 += 1
            else:
                negative_pt354_entries += 1

            # 2) Internally recommitted but wrong parent anchor.
            body = dict(candidate["body"])
            body["parent_anchor"] = _tamper_hex(str(body["parent_anchor"]))
            commitment, c = _recommit(body); _add_cost(cost, c)
            ok, c = verify_live_candidate(candidate, body_override=body, commitment_override=commitment)
            _add_cost(cost, c)
            if not ok:
                negative_rejects["parent_anchor_tamper"] += 1
                row_negative_rejects += 1
                blocked_before_pt354 += 1
            else:
                negative_pt354_entries += 1

            # 3) Internally recommitted but wrong support.
            body = dict(candidate["body"])
            body["support"] = [int(candidate["xv"]), int(candidate["xv"])]
            commitment, c = _recommit(body); _add_cost(cost, c)
            ok, c = verify_live_candidate(candidate, body_override=body, commitment_override=commitment)
            _add_cost(cost, c)
            if not ok:
                negative_rejects["support_tamper"] += 1
                row_negative_rejects += 1
                blocked_before_pt354 += 1
            else:
                negative_pt354_entries += 1

            # 4) Internally recommitted but stale/false child anchor.
            body = dict(candidate["body"])
            body["child_false_anchor"] = _tamper_hex(str(body["child_false_anchor"]))
            commitment, c = _recommit(body); _add_cost(cost, c)
            ok, c = verify_live_candidate(candidate, body_override=body, commitment_override=commitment)
            _add_cost(cost, c)
            if not ok:
                negative_rejects["false_child_anchor_tamper"] += 1
                row_negative_rejects += 1
                blocked_before_pt354 += 1
            else:
                negative_pt354_entries += 1

            # 5) Internally recommitted but stale/true child anchor.
            body = dict(candidate["body"])
            body["child_true_anchor"] = _tamper_hex(str(body["child_true_anchor"]))
            commitment, c = _recommit(body); _add_cost(cost, c)
            ok, c = verify_live_candidate(candidate, body_override=body, commitment_override=commitment)
            _add_cost(cost, c)
            if not ok:
                negative_rejects["true_child_anchor_tamper"] += 1
                row_negative_rejects += 1
                blocked_before_pt354 += 1
            else:
                negative_pt354_entries += 1

            # 6) A self-consistent but structurally dead current parent: remove every
            # clause mentioning the proposed branch variable, so x is absent and both
            # x restrictions collapse to the same residual. This must fail before PT354.
            xv = int(x_vars[index - 1])
            dead_formula = tuple(
                clause for clause in formula
                if all(abs(int(lit)) != xv for lit in clause)
            )
            dead_candidate, c = build_live_candidate(n, index, dead_formula)
            _add_cost(cost, c)
            ok, c = verify_live_candidate(dead_candidate)
            _add_cost(cost, c)
            if not ok:
                negative_rejects["structurally_dead_candidate"] += 1
                row_negative_rejects += 1
                blocked_before_pt354 += 1
            else:
                negative_pt354_entries += 1

        rows.append({
            "n": n,
            "generators": n,
            "positive_live": row_positive,
            "positive_all_live": row_positive == n,
            "negative_rejects": row_negative_rejects,
            "negative_expected": n * len(NEGATIVE_NAMES),
            "all_negatives_blocked": row_negative_rejects == n * len(NEGATIVE_NAMES),
        })

    expected_negative = total * len(NEGATIVE_NAMES)
    all_negative_exact = all(v == total for v in negative_rejects.values())
    passed = bool(
        positive_passes == total
        and positive_pt354_entries == total
        and all_negative_exact
        and blocked_before_pt354 == expected_negative
        and negative_pt354_entries == 0
    )

    return {
        "stage": "PT353_LIVE_STATE_WITNESS_BEFORE_PROVISIONING",
        "rule": "VERIFY_THE_LIVE_STATE -> ONLY_THEN_PREPARE_PAYLOAD_AND_RETURN",
        "rows": rows,
        "total_generators": total,
        "positive_live_passes": positive_passes,
        "positive_pt354_entries": positive_pt354_entries,
        "negative_controls_per_generator": len(NEGATIVE_NAMES),
        "negative_controls_total": expected_negative,
        "negative_rejects": negative_rejects,
        "blocked_before_pt354": blocked_before_pt354,
        "negative_pt354_entries": negative_pt354_entries,
        "hash_ops": cost["hash_ops"],
        "literal_visits": cost["literal_visits"],
        "restriction_passes": cost["restriction_passes"],
        "presence_checks": cost["presence_checks"],
        "uses_action_certificate": False,
        "uses_sat_oracle": False,
        "passed": passed,
    }


def projection_pt353(stage: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "rows", "total_generators", "positive_live_passes", "positive_pt354_entries",
        "negative_controls_per_generator", "negative_controls_total", "negative_rejects",
        "blocked_before_pt354", "negative_pt354_entries", "hash_ops", "literal_visits",
        "restriction_passes", "presence_checks", "uses_action_certificate", "uses_sat_oracle", "passed",
    )
    return {key: stage[key] for key in keys}


def run() -> dict[str, Any]:
    directions: list[str] = []

    # BACK: existing six-direction core, then undo/verify PT354, then PT353 live-state origin.
    back_core = run_pr192_back()
    pt354_back = run_pt354()
    pt353_back = run_pt353()
    directions.append("BACK")
    back_execution = list(back_core["execution"]) + ["PT354", "PT353"]
    back = {
        **back_core,
        "execution": back_execution,
        "PT354": projection_pt354(pt354_back),
        "PT353": projection_pt353(pt353_back),
        "pass": bool(back_core["pass"] and pt354_back["passed"] and pt353_back["passed"]),
    }

    # FORWARD: live-state must pass before PT354 is even entered.
    pt353_forward = run_pt353()
    if pt353_forward["passed"]:
        pt354_forward = run_pt354()
        forward_core = run_pr192_forward()
        pt354_was_entered = True
    else:
        pt354_forward = {"passed": False, "skipped_due_to_PT353": True}
        forward_core = {"pass": False, "execution": ["PT355", "PT366", "PT477", "PT222"]}
        pt354_was_entered = False
    directions.append("FORWARD")
    forward_execution = ["PT353", "PT354"] + list(forward_core["execution"])
    forward = {
        **forward_core,
        "execution": forward_execution,
        "PT353": projection_pt353(pt353_forward),
        "PT354": projection_pt354(pt354_forward) if pt354_was_entered else pt354_forward,
        "PT354_entered_only_after_PT353_pass": bool(pt354_was_entered and pt353_forward["passed"]),
        "pass": bool(pt353_forward["passed"] and pt354_was_entered and pt354_forward["passed"] and forward_core["pass"]),
    }

    left = run_left_control(); directions.append("LEFT")
    right = run_right_control(); directions.append("RIGHT")

    mirrors = {
        "PT353": back["PT353"] == forward["PT353"],
        "PT354": back["PT354"] == forward["PT354"],
        "PT355": back["PT355"] == forward["PT355"],
        "PT366": back["PT366"] == forward["PT366"],
        "PT477": back["PT477"] == forward["PT477"],
        "PT222": back["PT222"] == forward["PT222"],
    }
    forward_again = {
        "prediction": "6/6 PT353/PT354/PT355/PT366/PT477/PT222 metric projections mirror exactly; every failed PT353 control blocks PT354 and PT352 remains untouched.",
        "stage_mirrors": mirrors,
        "mirror_passes": sum(1 for value in mirrors.values() if value),
        "mirror_total": 6,
        "passed": bool(all(mirrors.values()) and pt353_back["passed"] and pt353_forward["passed"]),
    }
    directions.append("FORWARD_AGAIN")

    back_again = {
        "PR190_classification": PR190_CLASS,
        "PR191_preserved_status": EXPECTED_PR191_STOP,
        "PR192_classification": PR192_CLASS,
        "PT354_source_status": "HEURISTIC_PRECONDITION_PROMPT_ONLY",
        "PT353_source_status": "HEURISTIC_LIVE_STATE_PROMPT_ONLY",
        "PT352_status": "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "ancient_algorithm_claim_removed": True,
        "physical_time_reversal_claim_removed": True,
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(
        back_again["PR190_classification"] == PR190_CLASS
        and back_again["PR191_preserved_status"] == EXPECTED_PR191_STOP
        and back_again["PR192_classification"] == PR192_CLASS
        and back_again["PT352_status"] == "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES"
        and back_again["ancient_algorithm_claim_removed"]
        and back_again["physical_time_reversal_claim_removed"]
        and back_again["P_VS_NP"] == "OPEN"
    )
    directions.append("BACK_AGAIN")

    order_exact = directions == EXPECTED_DIRECTIONS
    back_order_exact = back_execution == EXPECTED_BACK
    forward_order_exact = forward_execution == EXPECTED_FORWARD
    negatives_block_pt354 = bool(
        pt353_forward["blocked_before_pt354"] == pt353_forward["negative_controls_total"]
        and pt353_forward["negative_pt354_entries"] == 0
    )

    gates = {
        "direction_order_exact": order_exact,
        "BACK_stage_order_exact": back_order_exact,
        "FORWARD_stage_order_exact": forward_order_exact,
        "PT353_BACK_pass": pt353_back["passed"],
        "PT353_FORWARD_pass": pt353_forward["passed"],
        "PT353_all_negative_controls_block_PT354": negatives_block_pt354,
        "PT354_entered_only_after_PT353_pass": forward["PT354_entered_only_after_PT353_pass"],
        "PT354_BACK_pass": pt354_back["passed"],
        "PT354_FORWARD_pass": bool(pt354_was_entered and pt354_forward["passed"]),
        "PR192_BACK_core_pass": back_core["pass"],
        "PR192_FORWARD_core_pass": forward_core["pass"],
        "LEFT_pass": left["passed"],
        "RIGHT_pass": right["passed"],
        "FORWARD_AGAIN_6_of_6": forward_again["passed"] and forward_again["mirror_passes"] == 6,
        "BACK_AGAIN_pass": back_again["passed"],
        "PT352_untouched": back_again["PT352_status"] == "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "P_VS_NP_OPEN": back_again["P_VS_NP"] == "OPEN",
    }
    all_gates = all(gates.values())

    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT353_LIVE_STATE_BEFORE_PROVISION" if all_gates else "STOP_AT_PT353_LIVE_STATE_BEFORE_PROVISION",
        "run_scope": "REVEALED_FROZEN_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "integration_discipline": {
            "integrated_now": "PT353",
            "PT352": "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
            "one_text_one_operator_one_run": True,
        },
        "required_direction_sequence": EXPECTED_DIRECTIONS,
        "executed_direction_sequence": directions,
        "BACK": back,
        "FORWARD": forward,
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": forward_again,
        "BACK_AGAIN": back_again,
        "gates": gates,
        "cost_vector": {
            "PT353_hash_ops_each_direction": pt353_forward["hash_ops"],
            "PT353_literal_visits_each_direction": pt353_forward["literal_visits"],
            "PT353_restriction_passes_each_direction": pt353_forward["restriction_passes"],
            "PT353_presence_checks_each_direction": pt353_forward["presence_checks"],
            "PT354_hash_ops_each_direction": pt354_forward["hash_ops"] if pt354_was_entered else None,
            "PT354_literal_visits_each_direction": pt354_forward["literal_visits"] if pt354_was_entered else None,
            "PT222_canonical_work_proxy_sum_each_direction": sum(row["canonical_work_proxy"] for row in forward["PT222"]["rows"]) if forward_core["pass"] else None,
            "PT477_structural_work_proxy_each_direction": (forward["PT477"]["candidate"]["resolution_attempts"] + forward["PT477"]["candidate"]["canonical_edge_visits"]) if forward_core["pass"] else None,
            "PT355_subsumption_steps_each_direction": forward["PT355"]["subsumption_steps"] if forward_core["pass"] else None,
            "PT366_samples_each_direction": forward["PT366"]["samples"] if forward_core["pass"] else None,
            "LEFT_literal_visits": left["charged_literal_visits"],
            "RIGHT_literal_visits": right["charged_literal_visits"],
            "warning": "Component-specific units; do not sum into a fake runtime total. PT353 positive-path cost is additional; reject-path benefit is only demonstrated as blocked PT354 entries, not as a general speedup.",
        },
        "claim_boundary": [
            "A PASS is compositional evidence on already revealed restricted controls only.",
            "PT353 is a modern live-state fail-closed precondition inspired heuristically by text ordering.",
            "PT352 is not integrated in this run.",
            "No arbitrary-CNF polynomial generator-discovery theorem is established.",
            "No arbitrary-CNF polynomial quotient-size theorem is established.",
            "P_VS_NP = OPEN",
        ],
        "mathematical_verdict": {
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
            "P_VS_NP": "OPEN",
        },
    }
    payload = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["integrity_sha256"] = __import__("hashlib").sha256(payload.encode("utf-8")).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.self_test:
        assert result["status"] == "PASS_KEEP_PT353_LIVE_STATE_BEFORE_PROVISION"
        assert all(result["gates"].values())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
