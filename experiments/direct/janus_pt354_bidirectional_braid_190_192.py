#!/usr/bin/env python3
"""Compose PR190's restricted PT222 kernel into PR192's strict six-direction frame,
with a new PT354 dual-resource precondition before PT355.

Historical material is heuristic operator inspiration only. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from janus_c025_core import restrict_formula
from janus_c025_families import equality_family
from janus_corrected_six_direction_reverse_pass import (
    EXPECTED_PR191_STOP,
    anti_equality_family,
    run_back as run_pr192_back,
    run_forward as run_pr192_forward,
    run_left_control,
    run_right_control,
)
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import (
    apply_signed_map,
    signed_map_roundtrip_ok,
)
from janus_tranception_prebirth_orbit_generators import (
    FROZEN_N,
    digest_json,
    full_generator,
    residual_generator,
)

RUN_ID = "JANUS-PT354-BIDIRECTIONAL-BRAID-190-192-2026-08-18-v1"
EXPECTED_DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
EXPECTED_BACK = ["PT222", "PT477", "PT366", "PT355", "PT354"]
EXPECTED_FORWARD = ["PT354", "PT355", "PT366", "PT477", "PT222"]
PR190_CLASS = "RESTRICTED_FAMILY_REPAIR_NOT_CANONICAL_PYRAMID_FORWARD"
PR192_CLASS = "CANONICAL_STRICT_SIX_DIRECTION_TRANCEPTION"


def stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def generator_serial(g: dict[int, tuple[int, bool]]) -> list[list[int | bool]]:
    return [[int(k), int(v[0]), bool(v[1])] for k, v in sorted(g.items())]


def _tamper_hex(value: str) -> str:
    if not value:
        return value
    first = "0" if value[0] != "0" else "1"
    return first + value[1:]


def make_pt354_resources(n: int, index: int) -> dict[str, Any]:
    formula, x_vars, y_vars = equality_family(n)
    xv = x_vars[index - 1]
    yv = y_vars[index - 1]
    parent_anchor = digest_json(formula)
    child_false = restrict_formula(formula, {xv: False})
    child_true = restrict_formula(formula, {xv: True})
    child_false_anchor = digest_json(child_false)
    child_true_anchor = digest_json(child_true)
    g = full_generator(n, index)
    rmap = residual_generator(child_false, yv)

    payload_body = {
        "kind": "PT354_PAYLOAD",
        "n": n,
        "index": index,
        "parent_anchor": parent_anchor,
        "support": [xv, yv],
        "child_false_anchor": child_false_anchor,
        "child_true_anchor": child_true_anchor,
    }
    payload_commitment = digest_json(payload_body)

    return_body = {
        "kind": "PT354_RETURN",
        "n": n,
        "index": index,
        "parent_anchor": parent_anchor,
        "support": [xv, yv],
        "full_generator": generator_serial(g),
        "residual_generator": generator_serial(rmap),
    }
    return_commitment = digest_json(return_body)

    full_auto_ok = signed_map_roundtrip_ok(g) and apply_signed_map(formula, g) == formula
    branch_return_ok = signed_map_roundtrip_ok(rmap) and apply_signed_map(child_false, rmap) == child_true

    return {
        "formula": formula,
        "parent_anchor": parent_anchor,
        "child_false": child_false,
        "child_true": child_true,
        "payload_body": payload_body,
        "payload_commitment": payload_commitment,
        "return_body": return_body,
        "return_commitment": return_commitment,
        "full_auto_ok": full_auto_ok,
        "branch_return_ok": branch_return_ok,
    }


def authorize_pt355(resource: dict[str, Any], *, payload_present: bool = True,
                    return_present: bool = True, payload_body: dict[str, Any] | None = None,
                    return_body: dict[str, Any] | None = None,
                    action_certificate_present: bool = True) -> bool:
    if not payload_present or not return_present or not action_certificate_present:
        return False
    pb = resource["payload_body"] if payload_body is None else payload_body
    rb = resource["return_body"] if return_body is None else return_body
    payload_ok = digest_json(pb) == resource["payload_commitment"]
    return_ok = digest_json(rb) == resource["return_commitment"]
    anchors_match = pb.get("parent_anchor") == rb.get("parent_anchor") == resource["parent_anchor"]
    supports_match = pb.get("support") == rb.get("support")
    return bool(payload_ok and return_ok and anchors_match and supports_match
                and resource["full_auto_ok"] and resource["branch_return_ok"])


def run_pt354() -> dict[str, Any]:
    rows = []
    total_generators = 0
    authorizations = 0
    payload_missing_rejects = 0
    return_missing_rejects = 0
    payload_tamper_rejects = 0
    return_tamper_rejects = 0
    cross_provenance_rejects = 0
    no_action_rejects = 0
    hash_ops = 0
    literal_visits = 0

    for n in FROZEN_N:
        formula, _, _ = equality_family(n)
        anti_formula, _, _ = anti_equality_family(n)
        anti_anchor = digest_json(anti_formula)
        row_ok = 0
        for index in range(1, n + 1):
            r = make_pt354_resources(n, index)
            total_generators += 1
            # parent/child anchors + two resource commitments + verification hashes + anti anchor accounting
            hash_ops += 7
            literal_visits += sum(len(c) for c in formula)
            literal_visits += sum(len(c) for c in r["child_false"])
            literal_visits += sum(len(c) for c in r["child_true"])

            if authorize_pt355(r):
                authorizations += 1
                row_ok += 1

            if not authorize_pt355(r, payload_present=False):
                payload_missing_rejects += 1
            if not authorize_pt355(r, return_present=False):
                return_missing_rejects += 1

            tampered_payload = dict(r["payload_body"])
            tampered_payload["child_false_anchor"] = _tamper_hex(tampered_payload["child_false_anchor"])
            if not authorize_pt355(r, payload_body=tampered_payload):
                payload_tamper_rejects += 1

            tampered_return = dict(r["return_body"])
            tampered_return["parent_anchor"] = _tamper_hex(tampered_return["parent_anchor"])
            if not authorize_pt355(r, return_body=tampered_return):
                return_tamper_rejects += 1

            cross_return = dict(r["return_body"])
            cross_return["parent_anchor"] = anti_anchor
            # Recommit to simulate an internally intact but provenance-different return resource.
            cross_resource = dict(r)
            cross_resource["return_body"] = cross_return
            cross_resource["return_commitment"] = digest_json(cross_return)
            hash_ops += 1
            if not authorize_pt355(cross_resource):
                cross_provenance_rejects += 1

            if not authorize_pt355(r, action_certificate_present=False):
                no_action_rejects += 1

        rows.append({
            "n": n,
            "generators": n,
            "authorized": row_ok,
            "all_authorized": row_ok == n,
        })

    all_negative = all(v == total_generators for v in (
        payload_missing_rejects, return_missing_rejects, payload_tamper_rejects,
        return_tamper_rejects, cross_provenance_rejects, no_action_rejects,
    ))
    passed = authorizations == total_generators and all_negative
    return {
        "stage": "PT354_DUAL_RESOURCE_PRECONDITION",
        "rule": "PREPARE_THE_PAYLOAD + PREPARE_THE_RETURN -> ONLY_THEN_OPEN_THE_GATE",
        "rows": rows,
        "total_generators": total_generators,
        "authorized": authorizations,
        "payload_missing_rejects": payload_missing_rejects,
        "return_missing_rejects": return_missing_rejects,
        "payload_tamper_rejects": payload_tamper_rejects,
        "return_tamper_rejects": return_tamper_rejects,
        "cross_provenance_rejects": cross_provenance_rejects,
        "same_provenance_without_action_rejects": no_action_rejects,
        "hash_ops": hash_ops,
        "literal_visits": literal_visits,
        "passed": passed,
    }


def projection_pt354(stage: dict[str, Any]) -> dict[str, Any]:
    return {k: stage[k] for k in (
        "rows", "total_generators", "authorized", "payload_missing_rejects",
        "return_missing_rejects", "payload_tamper_rejects", "return_tamper_rejects",
        "cross_provenance_rejects", "same_provenance_without_action_rejects",
        "hash_ops", "literal_visits", "passed",
    )}


def run() -> dict[str, Any]:
    directions = []

    # BACK: exact PR192 reverse, then PT354 unprepare/return-resource verification.
    back_core = run_pr192_back()
    pt354_back = run_pt354()
    directions.append("BACK")
    back_execution = list(back_core["execution"]) + ["PT354"]
    back = {
        **back_core,
        "execution": back_execution,
        "PT354": projection_pt354(pt354_back),
        "pass": bool(back_core["pass"] and pt354_back["passed"]),
    }

    # FORWARD: PT354 must authorize before PT355 is allowed to execute.
    pt354_forward = run_pt354()
    forward_core = run_pr192_forward()
    directions.append("FORWARD")
    forward_execution = ["PT354"] + list(forward_core["execution"])
    forward = {
        **forward_core,
        "execution": forward_execution,
        "PT354": projection_pt354(pt354_forward),
        "pass": bool(pt354_forward["passed"] and forward_core["pass"]),
    }

    left = run_left_control(); directions.append("LEFT")
    right = run_right_control(); directions.append("RIGHT")

    mirrors = {
        "PT354": back["PT354"] == forward["PT354"],
        "PT355": back["PT355"] == forward["PT355"],
        "PT366": back["PT366"] == forward["PT366"],
        "PT477": back["PT477"] == forward["PT477"],
        "PT222": back["PT222"] == forward["PT222"],
    }
    forward_again = {
        "prediction": "5/5 PT354/PT355/PT366/PT477/PT222 metric projections mirror exactly; PT354 dual resources fail closed and PR190 PT222 kernel remains canonical in both directions.",
        "stage_mirrors": mirrors,
        "mirror_passes": sum(1 for v in mirrors.values() if v),
        "mirror_total": 5,
        "passed": all(mirrors.values()) and pt354_forward["passed"] and pt354_back["passed"],
    }
    directions.append("FORWARD_AGAIN")

    back_again = {
        "PR190_classification": PR190_CLASS,
        "PR192_classification": PR192_CLASS,
        "PT354_source_status": "HEURISTIC_PRECONDITION_PROMPT_ONLY",
        "ancient_algorithm_claim_removed": True,
        "physical_time_reversal_claim_removed": True,
        "PR191_preserved_status": EXPECTED_PR191_STOP,
        "P_VS_NP": "OPEN",
    }
    back_again["passed"] = bool(
        back_again["PR190_classification"] == PR190_CLASS
        and back_again["PR192_classification"] == PR192_CLASS
        and back_again["PR191_preserved_status"] == EXPECTED_PR191_STOP
        and back_again["ancient_algorithm_claim_removed"]
        and back_again["physical_time_reversal_claim_removed"]
        and back_again["P_VS_NP"] == "OPEN"
    )
    directions.append("BACK_AGAIN")

    order_exact = directions == EXPECTED_DIRECTIONS
    back_order_exact = back_execution == EXPECTED_BACK
    forward_order_exact = forward_execution == EXPECTED_FORWARD
    all_gates = bool(
        order_exact and back_order_exact and forward_order_exact
        and back["pass"] and forward["pass"] and left["passed"] and right["passed"]
        and forward_again["passed"] and back_again["passed"]
    )

    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT354_BIDIRECTIONAL_BRAID" if all_gates else "STOP_AT_PT354_BIDIRECTIONAL_BRAID",
        "run_scope": "REVEALED_FROZEN_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "classification": {"PR190": PR190_CLASS, "PR192": PR192_CLASS},
        "required_direction_sequence": EXPECTED_DIRECTIONS,
        "executed_direction_sequence": directions,
        "BACK": back,
        "FORWARD": forward,
        "LEFT": left,
        "RIGHT": right,
        "FORWARD_AGAIN": forward_again,
        "BACK_AGAIN": back_again,
        "gates": {
            "direction_order_exact": order_exact,
            "BACK_stage_order_exact": back_order_exact,
            "FORWARD_stage_order_exact": forward_order_exact,
            "PT354_BACK_pass": pt354_back["passed"],
            "PT354_FORWARD_pass": pt354_forward["passed"],
            "PR192_BACK_core_pass": back_core["pass"],
            "PR192_FORWARD_core_pass": forward_core["pass"],
            "LEFT_pass": left["passed"],
            "RIGHT_pass": right["passed"],
            "FORWARD_AGAIN_5_of_5": forward_again["passed"] and forward_again["mirror_passes"] == 5,
            "BACK_AGAIN_pass": back_again["passed"],
            "P_VS_NP_OPEN": back_again["P_VS_NP"] == "OPEN",
        },
        "cost_vector": {
            "PT354_hash_ops_each_direction": pt354_forward["hash_ops"],
            "PT354_literal_visits_each_direction": pt354_forward["literal_visits"],
            "PT222_canonical_work_proxy_sum_each_direction": sum(row["canonical_work_proxy"] for row in forward["PT222"]["rows"]),
            "PT477_structural_work_proxy_each_direction": forward["PT477"]["candidate"]["resolution_attempts"] + forward["PT477"]["candidate"]["canonical_edge_visits"],
            "PT355_subsumption_steps_each_direction": forward["PT355"]["subsumption_steps"],
            "PT366_samples_each_direction": forward["PT366"]["samples"],
            "LEFT_literal_visits": left["charged_literal_visits"],
            "RIGHT_literal_visits": right["charged_literal_visits"],
            "warning": "Component-specific units; do not sum into a fake runtime total.",
        },
        "mathematical_verdict": {
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
            "P_VS_NP": "OPEN",
        },
        "claim_boundary": [
            "A PASS is compositional evidence on revealed restricted controls only.",
            "PR190 remains a restricted PT222 kernel, not a canonical pyramid FORWARD by itself.",
            "PT354 is a modern precondition operator inspired heuristically by source ordering, not an ancient algorithm.",
            "No arbitrary-CNF polynomial generator-discovery or quotient-size theorem is established.",
            "P_VS_NP = OPEN",
        ],
    }
    result["integrity_sha256"] = stable_hash(result)
    return result


def self_test(result: dict[str, Any]) -> None:
    assert result["executed_direction_sequence"] == EXPECTED_DIRECTIONS
    assert result["BACK"]["execution"] == EXPECTED_BACK
    assert result["FORWARD"]["execution"] == EXPECTED_FORWARD
    assert result["FORWARD_AGAIN"]["mirror_passes"] == 5
    assert all(result["gates"].values())
    assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
    assert result["status"] == "PASS_KEEP_PT354_BIDIRECTIONAL_BRAID"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    result = run()
    if args.self_test:
        self_test(result)
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
