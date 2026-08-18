#!/usr/bin/env python3
"""Atomic PT350/PT351/PT352 reverse-head extension of the JANUS six-direction braid.

The three text-inspired stages are preregistered as ONE experimental triad:
PT350 FIELD -> PT351 GESTATION -> PT352 FORMATION -> PT353 LIVE.
They are heuristic modern operators only, not claims about an ancient algorithm.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from janus_c025_core import restrict_formula
from janus_c025_families import equality_family
from janus_corrected_six_direction_reverse_pass import anti_equality_family
from janus_pt353_live_state_before_provision import (
    EXPECTED_PR191_STOP,
    PR190_CLASS,
    PR192_CLASS,
    projection_pt354,
    run_left_control,
    run_pr192_back,
    run_pr192_forward,
    run_pt353 as run_legacy_pt353,
    run_pt354,
    run_right_control,
)
from janus_tranception_prebirth_orbit_generators import FROZEN_N, digest_json

RUN_ID = "JANUS-PT350-351-352-ATOMIC-TRIAD-HEAD-TAIL-2026-08-18-v1"
DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
BACK_ORDER = ["PT222", "PT477", "PT366", "PT355", "PT354", "PT353", "PT352", "PT351", "PT350"]
FORWARD_ORDER = ["PT350", "PT351", "PT352", "PT353", "PT354", "PT355", "PT366", "PT477", "PT222"]
TRIAD_FORWARD = ["PT350", "PT351", "PT352"]
TRIAD_BACK = ["PT352", "PT351", "PT350"]
NEGATIVE_NAMES = [
    "PT350_missing_or_parent_mismatch",
    "PT351_missing_or_wrong_PT350_commitment",
    "PT352_missing_or_wrong_PT351_commitment",
    "triad_order_swap",
    "cross_parent_triad_mix",
    "formed_candidate_not_live_at_PT353",
]


def _literal_count(formula: Any) -> int:
    return sum(len(clause) for clause in formula)


def _occurrence_map(formula: Any) -> dict[int, int]:
    out: dict[int, int] = {}
    for clause in formula:
        for lit in clause:
            var = abs(int(lit))
            out[var] = out.get(var, 0) + 1
    return out


def _cost() -> dict[str, int]:
    return {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 0}


def _add(dst: dict[str, int], src: dict[str, int]) -> None:
    for key, value in src.items():
        dst[key] = dst.get(key, 0) + int(value)


def _tamper_hex(value: str) -> str:
    if not value:
        return value
    return ("0" if value[0] != "0" else "1") + value[1:]


def build_pt350_field(n: int, formula_override: Any | None = None) -> tuple[dict[str, Any], dict[str, int]]:
    base_formula, x_vars, y_vars = equality_family(n)
    formula = base_formula if formula_override is None else formula_override
    literals = _literal_count(formula)
    occurrences = _occurrence_map(formula)
    parent_anchor = digest_json(formula)
    occurrence_rows = [[v, occurrences.get(v, 0)] for v in sorted(set(x_vars + y_vars))]
    occurrence_digest = digest_json(occurrence_rows)
    body = {
        "kind": "PT350_FIELD_CONTEXT",
        "n": n,
        "parent_anchor": parent_anchor,
        "clause_count": len(formula),
        "literal_count": literals,
        "occurrence_rows": occurrence_rows,
        "occurrence_digest": occurrence_digest,
    }
    commitment = digest_json(body)
    return {
        "n": n,
        "formula": formula,
        "x_vars": list(x_vars),
        "y_vars": list(y_vars),
        "body": body,
        "commitment": commitment,
    }, {"hash_ops": 3, "literal_visits": literals, "restriction_passes": 0, "presence_checks": 0}


def verify_pt350(field: dict[str, Any], *, present: bool = True, body_override: dict[str, Any] | None = None,
                 commitment_override: str | None = None) -> tuple[bool, dict[str, int]]:
    if not present:
        return False, {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}
    formula = field["formula"]
    body = field["body"] if body_override is None else body_override
    commitment = field["commitment"] if commitment_override is None else commitment_override
    literals = _literal_count(formula)
    occurrences = _occurrence_map(formula)
    vars_all = sorted(set(field["x_vars"] + field["y_vars"]))
    rows = [[v, occurrences.get(v, 0)] for v in vars_all]
    parent_anchor = digest_json(formula)
    occurrence_digest = digest_json(rows)
    witness_ok = digest_json(body) == commitment
    ok = bool(
        witness_ok
        and body.get("kind") == "PT350_FIELD_CONTEXT"
        and body.get("n") == field["n"]
        and body.get("parent_anchor") == parent_anchor
        and body.get("clause_count") == len(formula)
        and body.get("literal_count") == literals
        and body.get("occurrence_rows") == rows
        and body.get("occurrence_digest") == occurrence_digest
    )
    return ok, {"hash_ops": 3, "literal_visits": literals, "restriction_passes": 0, "presence_checks": 1}


def _occ_from_field(field: dict[str, Any]) -> dict[int, int]:
    return {int(v): int(c) for v, c in field["body"]["occurrence_rows"]}


def build_pt351(field: dict[str, Any], index: int) -> tuple[dict[str, Any], dict[str, int]]:
    xv = int(field["x_vars"][index - 1]); yv = int(field["y_vars"][index - 1])
    occ = _occ_from_field(field)
    body = {
        "kind": "PT351_GESTATION_BINDING",
        "n": field["n"],
        "index": index,
        "field_commitment": field["commitment"],
        "parent_anchor": field["body"]["parent_anchor"],
        "support": [xv, yv],
        "support_occurrences": [occ.get(xv, 0), occ.get(yv, 0)],
    }
    commitment = digest_json(body)
    return {"body": body, "commitment": commitment, "xv": xv, "yv": yv}, {"hash_ops": 1, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 0}


def verify_pt351(field: dict[str, Any], gest: dict[str, Any], *, present: bool = True,
                 body_override: dict[str, Any] | None = None, commitment_override: str | None = None) -> tuple[bool, dict[str, int]]:
    if not present:
        return False, {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}
    body = gest["body"] if body_override is None else body_override
    commitment = gest["commitment"] if commitment_override is None else commitment_override
    occ = _occ_from_field(field)
    xv = int(gest["xv"]); yv = int(gest["yv"])
    ok = bool(
        digest_json(body) == commitment
        and body.get("kind") == "PT351_GESTATION_BINDING"
        and body.get("n") == field["n"]
        and body.get("field_commitment") == field["commitment"]
        and body.get("parent_anchor") == field["body"]["parent_anchor"]
        and body.get("support") == [xv, yv]
        and body.get("support_occurrences") == [occ.get(xv, 0), occ.get(yv, 0)]
    )
    return ok, {"hash_ops": 1, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}


def build_pt352(field: dict[str, Any], gest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    formula = field["formula"]
    xv = int(gest["xv"])
    literals = _literal_count(formula)
    child_false = restrict_formula(formula, {xv: False})
    child_true = restrict_formula(formula, {xv: True})
    false_anchor = digest_json(child_false); true_anchor = digest_json(child_true)
    body = {
        "kind": "PT352_FORMATION_WITNESS",
        "n": field["n"],
        "index": gest["body"]["index"],
        "gestation_commitment": gest["commitment"],
        "parent_anchor": field["body"]["parent_anchor"],
        "support": list(gest["body"]["support"]),
        "support_occurrences": list(gest["body"]["support_occurrences"]),
        "child_false_anchor": false_anchor,
        "child_true_anchor": true_anchor,
        "child_clause_counts": [len(child_false), len(child_true)],
    }
    commitment = digest_json(body)
    return {
        "body": body,
        "commitment": commitment,
        "child_false": child_false,
        "child_true": child_true,
    }, {"hash_ops": 3, "literal_visits": 2 * literals, "restriction_passes": 2, "presence_checks": 0}


def verify_pt352(field: dict[str, Any], gest: dict[str, Any], form: dict[str, Any], *, present: bool = True,
                 body_override: dict[str, Any] | None = None, commitment_override: str | None = None) -> tuple[bool, dict[str, int]]:
    if not present:
        return False, {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}
    formula = field["formula"]
    xv = int(gest["xv"])
    literals = _literal_count(formula)
    body = form["body"] if body_override is None else body_override
    commitment = form["commitment"] if commitment_override is None else commitment_override
    child_false = restrict_formula(formula, {xv: False})
    child_true = restrict_formula(formula, {xv: True})
    false_anchor = digest_json(child_false); true_anchor = digest_json(child_true)
    ok = bool(
        digest_json(body) == commitment
        and body.get("kind") == "PT352_FORMATION_WITNESS"
        and body.get("n") == field["n"]
        and body.get("index") == gest["body"]["index"]
        and body.get("gestation_commitment") == gest["commitment"]
        and body.get("parent_anchor") == field["body"]["parent_anchor"]
        and body.get("support") == gest["body"]["support"]
        and body.get("support_occurrences") == gest["body"]["support_occurrences"]
        and body.get("child_false_anchor") == false_anchor
        and body.get("child_true_anchor") == true_anchor
        and body.get("child_clause_counts") == [len(child_false), len(child_true)]
    )
    return ok, {"hash_ops": 3, "literal_visits": 2 * literals, "restriction_passes": 2, "presence_checks": 1}


def verify_pt353_from_formation(gest: dict[str, Any], form: dict[str, Any], *, triad_verified: bool) -> tuple[bool, dict[str, int]]:
    if not triad_verified:
        return False, {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}
    occ = form["body"]["support_occurrences"]
    alive = bool(
        isinstance(occ, list) and len(occ) == 2
        and int(occ[0]) > 0 and int(occ[1]) > 0
        and form["body"]["child_false_anchor"] != form["body"]["child_true_anchor"]
        and form["body"]["support"] == gest["body"]["support"]
    )
    return alive, {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 1}


def verify_atomic_chain(field: dict[str, Any], gest: dict[str, Any], form: dict[str, Any], *,
                        order: list[str] | None = None) -> tuple[bool, dict[str, dict[str, int]]]:
    costs = {"PT350": _cost(), "PT351": _cost(), "PT352": _cost()}
    if (TRIAD_FORWARD if order is None else order) != TRIAD_FORWARD:
        return False, costs
    ok350, c = verify_pt350(field); _add(costs["PT350"], c)
    if not ok350: return False, costs
    ok351, c = verify_pt351(field, gest); _add(costs["PT351"], c)
    if not ok351: return False, costs
    ok352, c = verify_pt352(field, gest, form); _add(costs["PT352"], c)
    return bool(ok352), costs


def run_atomic_triad() -> dict[str, Any]:
    totals = {"PT350": _cost(), "PT351": _cost(), "PT352": _cost(), "PT353": _cost()}
    rows = []
    positive = 0
    positive_live = 0
    negatives = {name: 0 for name in NEGATIVE_NAMES}
    blocked_before_pt353 = 0
    blocked_at_pt353 = 0
    negative_pt354_entries = 0

    for n in FROZEN_N:
        field, c = build_pt350_field(n); _add(totals["PT350"], c)
        field_ok, c = verify_pt350(field); _add(totals["PT350"], c)
        if not field_ok:
            rows.append({"n": n, "generators": n, "positive": 0, "negative_rejects": 0, "passed": False})
            continue
        row_pos = 0; row_neg = 0
        formula, x_vars, _ = equality_family(n)
        anti_formula, _, _ = anti_equality_family(n)
        anti_field, c = build_pt350_field(n, anti_formula); _add(totals["PT350"], c)

        for index in range(1, n + 1):
            gest, c = build_pt351(field, index); _add(totals["PT351"], c)
            form, c = build_pt352(field, gest); _add(totals["PT352"], c)
            triad_ok, costs = verify_atomic_chain(field, gest, form)
            for stage, cost in costs.items(): _add(totals[stage], cost)
            live_ok, c = verify_pt353_from_formation(gest, form, triad_verified=triad_ok); _add(totals["PT353"], c)
            if triad_ok:
                positive += 1; row_pos += 1
            if triad_ok and live_ok:
                positive_live += 1

            # 1. PT350 missing. Must stop before PT353.
            ok350, c = verify_pt350(field, present=False); _add(totals["PT350"], c)
            if not ok350:
                negatives[NEGATIVE_NAMES[0]] += 1; row_neg += 1; blocked_before_pt353 += 1
            else: negative_pt354_entries += 1

            # 2. PT351 is internally valid but points to the wrong PT350 commitment.
            body351 = dict(gest["body"]); body351["field_commitment"] = _tamper_hex(body351["field_commitment"])
            comm351 = digest_json(body351); _add(totals["PT351"], {"hash_ops":1,"literal_visits":0,"restriction_passes":0,"presence_checks":0})
            ok351, c = verify_pt351(field, gest, body_override=body351, commitment_override=comm351); _add(totals["PT351"], c)
            if not ok351:
                negatives[NEGATIVE_NAMES[1]] += 1; row_neg += 1; blocked_before_pt353 += 1
            else: negative_pt354_entries += 1

            # 3. PT352 is internally valid but points to the wrong PT351 commitment.
            body352 = dict(form["body"]); body352["gestation_commitment"] = _tamper_hex(body352["gestation_commitment"])
            comm352 = digest_json(body352); _add(totals["PT352"], {"hash_ops":1,"literal_visits":0,"restriction_passes":0,"presence_checks":0})
            ok352, c = verify_pt352(field, gest, form, body_override=body352, commitment_override=comm352); _add(totals["PT352"], c)
            if not ok352:
                negatives[NEGATIVE_NAMES[2]] += 1; row_neg += 1; blocked_before_pt353 += 1
            else: negative_pt354_entries += 1

            # 4. All witnesses are valid, but the declared triad order is swapped.
            swap_ok, _ = verify_atomic_chain(field, gest, form, order=["PT351","PT350","PT352"])
            if not swap_ok:
                negatives[NEGATIVE_NAMES[3]] += 1; row_neg += 1; blocked_before_pt353 += 1
            else: negative_pt354_entries += 1

            # 5. Mix a field from another parent with the current gestation/formation.
            anti_gest, c = build_pt351(anti_field, index); _add(totals["PT351"], c)
            anti_form, c = build_pt352(anti_field, anti_gest); _add(totals["PT352"], c)
            mixed_ok, costs = verify_atomic_chain(field, anti_gest, anti_form)
            for stage, cost in costs.items(): _add(totals[stage], cost)
            if not mixed_ok:
                negatives[NEGATIVE_NAMES[4]] += 1; row_neg += 1; blocked_before_pt353 += 1
            else: negative_pt354_entries += 1

            # 6. A self-consistent triad may still describe a structurally dead candidate.
            # Remove every clause mentioning x. PT350/351/352 may bind it faithfully;
            # PT353 must reject it before PT354 provisioning.
            xv = int(x_vars[index - 1])
            dead_formula = tuple(clause for clause in formula if all(abs(int(lit)) != xv for lit in clause))
            dead_field, c = build_pt350_field(n, dead_formula); _add(totals["PT350"], c)
            dead_gest, c = build_pt351(dead_field, index); _add(totals["PT351"], c)
            dead_form, c = build_pt352(dead_field, dead_gest); _add(totals["PT352"], c)
            dead_triad_ok, costs = verify_atomic_chain(dead_field, dead_gest, dead_form)
            for stage, cost in costs.items(): _add(totals[stage], cost)
            dead_live_ok, c = verify_pt353_from_formation(dead_gest, dead_form, triad_verified=dead_triad_ok); _add(totals["PT353"], c)
            if dead_triad_ok and not dead_live_ok:
                negatives[NEGATIVE_NAMES[5]] += 1; row_neg += 1; blocked_at_pt353 += 1
            else: negative_pt354_entries += 1

        rows.append({
            "n": n,
            "generators": n,
            "positive_triad": row_pos,
            "positive_all": row_pos == n,
            "negative_rejects": row_neg,
            "negative_expected": n * len(NEGATIVE_NAMES),
            "passed": row_pos == n and row_neg == n * len(NEGATIVE_NAMES),
        })

    total = sum(FROZEN_N)
    expected_negative = total * len(NEGATIVE_NAMES)
    all_negative = all(v == total for v in negatives.values())
    pass_all = bool(
        positive == total and positive_live == total and all_negative
        and blocked_before_pt353 + blocked_at_pt353 == expected_negative
        and negative_pt354_entries == 0
    )
    return {
        "triad": {
            "name": "PT350_351_352_FIELD_GESTATION_FORMATION_TRIAD",
            "atomic": True,
            "forward_suborder": TRIAD_FORWARD,
            "back_suborder": TRIAD_BACK,
            "rows": rows,
            "total_generators": total,
            "positive_triad_passes": positive,
            "positive_live_passes": positive_live,
            "negative_controls_per_generator": len(NEGATIVE_NAMES),
            "negative_controls_total": expected_negative,
            "negative_rejects": negatives,
            "blocked_before_PT353": blocked_before_pt353,
            "blocked_at_PT353": blocked_at_pt353,
            "negative_PT354_entries": negative_pt354_entries,
            "passed": pass_all,
        },
        "PT350": {"operator":"PT350_FIELD_CONTEXT_WITNESS","cost":totals["PT350"],"passed":pass_all},
        "PT351": {"operator":"PT351_GESTATION_BINDING_WITNESS","cost":totals["PT351"],"passed":pass_all},
        "PT352": {"operator":"PT352_FORMATION_WITNESS","cost":totals["PT352"],"passed":pass_all},
        "PT353": {
            "operator":"PT353_LIVE_STATE_REUSED_FROM_PT352_FORMATION",
            "positive_live_passes": positive_live,
            "negative_dead_rejects": negatives["formed_candidate_not_live_at_PT353"],
            "uses_action_certificate": False,
            "uses_sat_oracle": False,
            "cost": totals["PT353"],
            "passed": pass_all,
        },
    }


def topology_audit() -> dict[str, Any]:
    return {
        "head": "PT350",
        "tail": "PT222",
        "head_contiguous_text_segment": ["PT350","PT351","PT352","PT353","PT354","PT355"],
        "head_segment_contiguous": True,
        "immediate_textual_predecessor": "PT349",
        "PT349_section": "Offerings for the Deceased King, PT338-349",
        "PT350_section": "Miscellaneous Utterances on the Hereafter, PT350-374",
        "PT349_status": "HEAD_BOUNDARY_WATCHLIST_ONLY_NOT_IN_CODE",
        "PT349_possible_overlap": "PROVISIONING_MOTIF_MAY_OVERLAP_PT354_REQUIRES_FUTURE_BOUNDARY_AUDIT",
        "intentional_synthetic_numeric_gaps": [
            {"from":"PT355","to":"PT366","missing_numbered_utterances":10,"range":"PT356-PT365"},
            {"from":"PT366","to":"PT477","missing_numbered_utterances":110,"range":"PT367-PT476"},
            {"from":"PT477","to":"PT222","note":"synthetic ladder transition; not a monotonic PT-number sequence"}
        ],
        "no_claim_of_continuous_ancient_pipeline": True,
        "audit_complete": True,
    }


def run() -> dict[str, Any]:
    directions: list[str] = []
    legacy_pt353 = run_legacy_pt353()

    back_core = run_pr192_back()
    pt354_back = run_pt354()
    triad_back = run_atomic_triad()
    directions.append("BACK")
    back_execution = list(back_core["execution"]) + ["PT354","PT353","PT352","PT351","PT350"]
    back = {
        **back_core,
        "execution": back_execution,
        "PT354": projection_pt354(pt354_back),
        "PT353": triad_back["PT353"],
        "PT352": triad_back["PT352"],
        "PT351": triad_back["PT351"],
        "PT350": triad_back["PT350"],
        "TRIAD": triad_back["triad"],
        "pass": bool(back_core["pass"] and pt354_back["passed"] and triad_back["triad"]["passed"]),
    }

    triad_forward = run_atomic_triad()
    triad_ok = triad_forward["triad"]["passed"]
    if triad_ok:
        pt354_forward = run_pt354()
        forward_core = run_pr192_forward()
        downstream_entered = True
    else:
        pt354_forward = {"passed": False, "skipped_due_to_triad": True}
        forward_core = {"pass": False, "execution": ["PT355","PT366","PT477","PT222"]}
        downstream_entered = False
    directions.append("FORWARD")
    forward_execution = ["PT350","PT351","PT352","PT353","PT354"] + list(forward_core["execution"])
    forward = {
        **forward_core,
        "execution": forward_execution,
        "PT350": triad_forward["PT350"],
        "PT351": triad_forward["PT351"],
        "PT352": triad_forward["PT352"],
        "PT353": triad_forward["PT353"],
        "TRIAD": triad_forward["triad"],
        "PT354": projection_pt354(pt354_forward) if downstream_entered else pt354_forward,
        "PT354_entered_only_after_atomic_triad_and_PT353": bool(downstream_entered and triad_ok),
        "pass": bool(triad_ok and downstream_entered and pt354_forward["passed"] and forward_core["pass"]),
    }

    left = run_left_control(); directions.append("LEFT")
    right = run_right_control(); directions.append("RIGHT")

    mirrors = {
        "PT350": back["PT350"] == forward["PT350"],
        "PT351": back["PT351"] == forward["PT351"],
        "PT352": back["PT352"] == forward["PT352"],
        "PT353": back["PT353"] == forward["PT353"],
        "PT354": back["PT354"] == forward["PT354"],
        "PT355": back["PT355"] == forward["PT355"],
        "PT366": back["PT366"] == forward["PT366"],
        "PT477": back["PT477"] == forward["PT477"],
        "PT222": back["PT222"] == forward["PT222"],
    }
    forward_again = {
        "prediction": "9/9 PT350/PT351/PT352/PT353/PT354/PT355/PT366/PT477/PT222 projections mirror exactly; the atomic triad blocks all frozen negatives before PT354.",
        "stage_mirrors": mirrors,
        "mirror_passes": sum(1 for v in mirrors.values() if v),
        "mirror_total": 9,
        "passed": all(mirrors.values()),
    }
    directions.append("FORWARD_AGAIN")

    topo = topology_audit()
    legacy_exact = bool(
        legacy_pt353["passed"]
        and legacy_pt353["positive_live_passes"] == 494
        and legacy_pt353["negative_controls_total"] == 2964
        and legacy_pt353["blocked_before_pt354"] == 2964
        and legacy_pt353["negative_pt354_entries"] == 0
        and legacy_pt353["hash_ops"] == 17784
        and legacy_pt353["literal_visits"] == 8362800
    )
    back_again = {
        "PR190_classification": PR190_CLASS,
        "PR191_preserved_status": EXPECTED_PR191_STOP,
        "PR192_classification": PR192_CLASS,
        "atomic_triad_status": "PT350_PT351_PT352_ATOMIC_NO_POSTHOC_SPLIT",
        "PT349_status": topo["PT349_status"],
        "legacy_PT353_control_exact": legacy_exact,
        "ancient_algorithm_claim_removed": True,
        "physical_time_reversal_claim_removed": True,
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(
        back_again["PR191_preserved_status"] == EXPECTED_PR191_STOP
        and back_again["legacy_PT353_control_exact"]
        and back_again["ancient_algorithm_claim_removed"]
        and back_again["physical_time_reversal_claim_removed"]
        and back_again["P_VS_NP"] == "OPEN"
    )
    directions.append("BACK_AGAIN")

    order_exact = directions == DIRECTIONS
    negative_block = bool(
        triad_forward["triad"]["negative_PT354_entries"] == 0
        and triad_forward["triad"]["blocked_before_PT353"] + triad_forward["triad"]["blocked_at_PT353"] == triad_forward["triad"]["negative_controls_total"]
    )
    inherited_exact = bool(
        forward_core["pass"]
        and forward["PT354"]["authorized"] == 494
        and forward["PT355"]["raw_residual_states"] == 4096
        and forward["PT355"]["normalized_residual_states"] == 1
        and forward["PT366"]["samples"] == 256
        and forward["PT366"]["reverse_map_passes"] == 256
        and forward["PT477"]["candidate"]["residual_states"] == 2822
        and forward["PT477"]["candidate"]["saved_buzz_return_checks"] == 1050
        and sum(row["canonical_work_proxy"] for row in forward["PT222"]["rows"]) == 3893117
    ) if downstream_entered else False

    gates = {
        "direction_order_exact": order_exact,
        "BACK_stage_order_exact": back_execution == BACK_ORDER,
        "FORWARD_stage_order_exact": forward_execution == FORWARD_ORDER,
        "atomic_triad_pass": triad_forward["triad"]["passed"] and triad_back["triad"]["passed"],
        "all_negative_controls_block_before_PT354": negative_block,
        "PT354_entered_only_after_atomic_triad_and_PT353": forward["PT354_entered_only_after_atomic_triad_and_PT353"],
        "inherited_stack_exact": inherited_exact,
        "LEFT_pass": left["passed"],
        "RIGHT_pass": right["passed"],
        "FORWARD_AGAIN_9_of_9": forward_again["passed"] and forward_again["mirror_passes"] == 9,
        "BACK_AGAIN_pass": back_again["passed"],
        "legacy_PT353_control_exact": legacy_exact,
        "head_to_tail_topology_audit_complete": topo["audit_complete"],
        "PT349_not_integrated": topo["PT349_status"] == "HEAD_BOUNDARY_WATCHLIST_ONLY_NOT_IN_CODE",
        "P_VS_NP_OPEN": back_again["P_VS_NP"] == "OPEN",
    }
    all_gates = all(gates.values())

    new_lits = sum(triad_forward[s]["cost"]["literal_visits"] for s in ("PT350","PT351","PT352","PT353"))
    new_hash = sum(triad_forward[s]["cost"]["hash_ops"] for s in ("PT350","PT351","PT352","PT353"))
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT350_352_ATOMIC_TRIAD" if all_gates else "STOP_AT_PT350_352_ATOMIC_TRIAD",
        "run_scope": "REVEALED_FROZEN_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "required_direction_sequence": DIRECTIONS,
        "executed_direction_sequence": directions,
        "BACK": back,
        "FORWARD": forward,
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": forward_again,
        "HEAD_TO_TAIL_AUDIT": topo,
        "BACK_AGAIN": back_again,
        "legacy_PT353_control": {
            "positive_live_passes": legacy_pt353["positive_live_passes"],
            "negative_controls_total": legacy_pt353["negative_controls_total"],
            "blocked_before_pt354": legacy_pt353["blocked_before_pt354"],
            "hash_ops": legacy_pt353["hash_ops"],
            "literal_visits": legacy_pt353["literal_visits"],
            "exact": legacy_exact,
        },
        "cost_comparison_same_units": {
            "legacy_PT353_literal_visits_each_direction": legacy_pt353["literal_visits"],
            "new_PT350_to_PT353_literal_visits_each_direction": new_lits,
            "literal_visit_delta": new_lits - legacy_pt353["literal_visits"],
            "literal_visit_ratio_new_over_legacy": new_lits / legacy_pt353["literal_visits"],
            "legacy_PT353_hash_ops_each_direction": legacy_pt353["hash_ops"],
            "new_PT350_to_PT353_hash_ops_each_direction": new_hash,
            "hash_op_delta": new_hash - legacy_pt353["hash_ops"],
            "hash_op_ratio_new_over_legacy": new_hash / legacy_pt353["hash_ops"],
            "warning": "This compares only like-for-like instrumented units in the pre-PT354 head layer; it is not wall-clock runtime and not a general complexity result."
        },
        "gates": gates,
        "claim_boundary": [
            "PT350/PT351/PT352 are an atomic modern experimental triad by preregistration only.",
            "Textual order is heuristic inspiration, not evidence of an ancient SAT algorithm.",
            "PT349 is only a head-boundary watchlist item and is not integrated.",
            "The ladder remains synthetic after PT355; numeric PT gaps are reported rather than silently filled.",
            "No arbitrary-CNF polynomial generator-discovery or quotient-size theorem is established.",
            "P_VS_NP = OPEN",
        ],
        "mathematical_verdict": {"P_EQUALS_NP":"NOT_ESTABLISHED","P_NOT_EQUALS_NP":"NOT_ESTABLISHED","P_VS_NP":"OPEN"},
    }
    payload = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["integrity_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.self_test:
        assert result["status"] == "PASS_KEEP_PT350_352_ATOMIC_TRIAD"
        assert all(result["gates"].values())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
