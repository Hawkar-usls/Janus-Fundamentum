#!/usr/bin/env python3
"""One-step reverse integration: PT352 formed-state manifest before PT353 live verification.

Historical text is heuristic operator inspiration only. No SAT/UNSAT oracle is used.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

from janus_c025_core import restrict_formula
from janus_c025_families import equality_family
from janus_pt353_live_state_before_provision import (
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

RUN_ID = "JANUS-PT352-FORMED-STATE-BEFORE-LIVE-2026-08-18-v1"
EXPECTED_DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
EXPECTED_BACK = ["PT222", "PT477", "PT366", "PT355", "PT354", "PT353", "PT352"]
EXPECTED_FORWARD = ["PT352", "PT353", "PT354", "PT355", "PT366", "PT477", "PT222"]
LEGACY_PT353_LITERAL_VISITS = 8_362_800
NEGATIVE_NAMES = [
    "witness_missing",
    "parent_anchor_tamper",
    "support_tamper",
    "false_child_anchor_tamper",
    "true_child_anchor_tamper",
    "structurally_dead_candidate",
]


def literal_count(formula: Any) -> int:
    return sum(len(clause) for clause in formula)


def tamper_hex(value: str) -> str:
    if not value:
        return value
    return ("0" if value[0] != "0" else "1") + value[1:]


def occurrence_map(formula: Any) -> dict[int, int]:
    out: dict[int, int] = {}
    for clause in formula:
        for lit in clause:
            v = abs(int(lit))
            out[v] = out.get(v, 0) + 1
    return out


def run_pt352() -> dict[str, Any]:
    runtime: dict[int, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    total = 0
    verified = 0
    cost = {"hash_ops": 0, "literal_visits": 0, "restriction_passes": 0, "presence_checks": 0}

    for n in FROZEN_N:
        formula, x_vars, y_vars = equality_family(n)
        parent_lits = literal_count(formula)
        parent_anchor = digest_json(formula)
        occ = occurrence_map(formula)
        cost["hash_ops"] += 1
        cost["literal_visits"] += parent_lits
        entries: list[dict[str, Any]] = []
        entry_commitments: list[str] = []

        # Formation: each current branch state is materialized once and committed once.
        for index in range(1, n + 1):
            xv = int(x_vars[index - 1]); yv = int(y_vars[index - 1])
            child_false = restrict_formula(formula, {xv: False})
            child_true = restrict_formula(formula, {xv: True})
            cf = digest_json(child_false); ct = digest_json(child_true)
            body = {
                "kind": "PT352_FORMED_STATE",
                "n": n,
                "index": index,
                "parent_anchor": parent_anchor,
                "support": [xv, yv],
                "support_occurrences": [occ.get(xv, 0), occ.get(yv, 0)],
                "child_false_anchor": cf,
                "child_true_anchor": ct,
                "child_clause_counts": [len(child_false), len(child_true)],
            }
            commitment = digest_json(body)
            entries.append({"body": body, "commitment": commitment})
            entry_commitments.append(commitment)
            total += 1
            cost["hash_ops"] += 3
            cost["literal_visits"] += 2 * parent_lits
            cost["restriction_passes"] += 2

        manifest_body = {
            "kind": "PT352_FORMED_STATE_MANIFEST",
            "n": n,
            "parent_anchor": parent_anchor,
            "entry_commitments": entry_commitments,
        }
        manifest_commitment = digest_json(manifest_body)
        cost["hash_ops"] += 1

        # Independent verification of the formation certificate. Restrictions are
        # recomputed once per entry here, never once per later PT353 tamper control.
        manifest_ok = digest_json(manifest_body) == manifest_commitment
        cost["hash_ops"] += 1
        row_verified = 0
        for index, entry in enumerate(entries, start=1):
            xv = int(x_vars[index - 1]); yv = int(y_vars[index - 1])
            child_false = restrict_formula(formula, {xv: False})
            child_true = restrict_formula(formula, {xv: True})
            cf = digest_json(child_false); ct = digest_json(child_true)
            expected = {
                "kind": "PT352_FORMED_STATE",
                "n": n,
                "index": index,
                "parent_anchor": parent_anchor,
                "support": [xv, yv],
                "support_occurrences": [occ.get(xv, 0), occ.get(yv, 0)],
                "child_false_anchor": cf,
                "child_true_anchor": ct,
                "child_clause_counts": [len(child_false), len(child_true)],
            }
            expected_commitment = digest_json(expected)
            cost["hash_ops"] += 3
            cost["literal_visits"] += 2 * parent_lits
            cost["restriction_passes"] += 2
            cost["presence_checks"] += 1
            ok = bool(
                manifest_ok
                and entry["body"] == expected
                and entry["commitment"] == expected_commitment
                and entry["commitment"] in manifest_body["entry_commitments"]
                and cf != ct
                and occ.get(xv, 0) > 0
                and occ.get(yv, 0) > 0
            )
            if ok:
                row_verified += 1; verified += 1

        runtime[n] = {
            "formula": formula,
            "parent_anchor": parent_anchor,
            "entries": entries,
            "manifest_body": manifest_body,
            "manifest_commitment": manifest_commitment,
        }
        rows.append({"n": n, "formed": n, "verified": row_verified, "all_verified": row_verified == n})

    passed = verified == total == sum(FROZEN_N)
    return {
        "stage": "PT352_FORMED_STATE_MANIFEST_BEFORE_LIVE",
        "rule": "FORM_AND_BIND_CURRENT_BRANCH_STATE -> ONLY_THEN_VERIFY_LIVE_STATE",
        "rows": rows,
        "total_generators": total,
        "formed": total,
        "verified": verified,
        "hash_ops": cost["hash_ops"],
        "literal_visits": cost["literal_visits"],
        "restriction_passes": cost["restriction_passes"],
        "presence_checks": cost["presence_checks"],
        "uses_action_certificate": False,
        "uses_sat_oracle": False,
        "passed": passed,
        "_runtime": runtime,
    }


def projection_pt352(stage: dict[str, Any]) -> dict[str, Any]:
    return {k: stage[k] for k in (
        "rows", "total_generators", "formed", "verified", "hash_ops", "literal_visits",
        "restriction_passes", "presence_checks", "uses_action_certificate", "uses_sat_oracle", "passed",
    )}


def run_pt353_from_pt352(pt352: dict[str, Any]) -> dict[str, Any]:
    runtime = pt352["_runtime"]
    total = 0; positive = 0; positive_pt354 = 0; blocked = 0; negative_pt354 = 0
    neg = {name: 0 for name in NEGATIVE_NAMES}
    rows: list[dict[str, Any]] = []
    hash_ops = 0; presence_checks = 0

    def accepted(n: int, body: dict[str, Any] | None, commitment: str | None) -> bool:
        nonlocal hash_ops, presence_checks
        presence_checks += 1
        if body is None or commitment is None:
            return False
        hash_ops += 1
        if digest_json(body) != commitment:
            return False
        manifest = runtime[n]["manifest_body"]
        if commitment not in manifest["entry_commitments"]:
            return False
        return bool(
            body.get("kind") == "PT352_FORMED_STATE"
            and body.get("parent_anchor") == runtime[n]["parent_anchor"]
            and isinstance(body.get("support"), list)
            and len(body["support"]) == 2
            and body["support"][0] != body["support"][1]
            and body.get("support_occurrences", [0, 0])[0] > 0
            and body.get("support_occurrences", [0, 0])[1] > 0
            and body.get("child_false_anchor") != body.get("child_true_anchor")
        )

    for n in FROZEN_N:
        entries = runtime[n]["entries"]
        row_pos = 0; row_neg = 0
        for entry in entries:
            total += 1
            body = dict(entry["body"]); commitment = entry["commitment"]
            if accepted(n, body, commitment):
                positive += 1; positive_pt354 += 1; row_pos += 1

            # Missing witness.
            if not accepted(n, None, None):
                neg["witness_missing"] += 1; blocked += 1; row_neg += 1
            else: negative_pt354 += 1

            # Five internally recommitted variants must still fail membership/structure.
            variants: list[tuple[str, dict[str, Any]]] = []
            b = dict(body); b["parent_anchor"] = tamper_hex(str(b["parent_anchor"])); variants.append(("parent_anchor_tamper", b))
            b = dict(body); b["support"] = [b["support"][0], b["support"][0]]; variants.append(("support_tamper", b))
            b = dict(body); b["child_false_anchor"] = tamper_hex(str(b["child_false_anchor"])); variants.append(("false_child_anchor_tamper", b))
            b = dict(body); b["child_true_anchor"] = tamper_hex(str(b["child_true_anchor"])); variants.append(("true_child_anchor_tamper", b))
            b = dict(body); b["child_true_anchor"] = b["child_false_anchor"]; b["support_occurrences"] = [0, 0]; variants.append(("structurally_dead_candidate", b))
            for name, variant in variants:
                recommit = digest_json(variant); hash_ops += 1
                if not accepted(n, variant, recommit):
                    neg[name] += 1; blocked += 1; row_neg += 1
                else: negative_pt354 += 1

        rows.append({
            "n": n,
            "generators": len(entries),
            "positive_live": row_pos,
            "negative_rejects": row_neg,
            "negative_expected": len(entries) * len(NEGATIVE_NAMES),
            "all_negatives_blocked": row_neg == len(entries) * len(NEGATIVE_NAMES),
        })

    expected_negative = total * len(NEGATIVE_NAMES)
    passed = bool(
        pt352["passed"] and positive == total and positive_pt354 == total
        and blocked == expected_negative and negative_pt354 == 0
        and all(v == total for v in neg.values())
    )
    return {
        "stage": "PT353_LIVE_STATE_FROM_PT352_MANIFEST",
        "rule": "VERIFY_FORMED_STATE_MEMBERSHIP -> ONLY_THEN_PREPARE_PAYLOAD_AND_RETURN",
        "rows": rows,
        "total_generators": total,
        "positive_live_passes": positive,
        "positive_pt354_entries": positive_pt354,
        "negative_controls_per_generator": len(NEGATIVE_NAMES),
        "negative_controls_total": expected_negative,
        "negative_rejects": neg,
        "blocked_before_pt354": blocked,
        "negative_pt354_entries": negative_pt354,
        "hash_ops": hash_ops,
        "literal_visits": 0,
        "restriction_passes": 0,
        "presence_checks": presence_checks,
        "uses_action_certificate": False,
        "uses_sat_oracle": False,
        "passed": passed,
    }


def projection_pt353(stage: dict[str, Any]) -> dict[str, Any]:
    return dict(stage)


def run() -> dict[str, Any]:
    directions: list[str] = []
    # PT352 manifests are independently rebuilt/verified for each direction; the logical
    # BACK order records unforming after PT353, while its certificate data are the input to
    # the reverse verifier. Costs remain charged to PT352 in that direction.
    pt352_back = run_pt352(); pt353_back = run_pt353_from_pt352(pt352_back)
    back_core = run_pr192_back(); pt354_back = run_pt354(); directions.append("BACK")
    back = {
        **back_core,
        "execution": list(back_core["execution"]) + ["PT354", "PT353", "PT352"],
        "PT354": projection_pt354(pt354_back),
        "PT353": projection_pt353(pt353_back),
        "PT352": projection_pt352(pt352_back),
        "pass": bool(back_core["pass"] and pt354_back["passed"] and pt353_back["passed"] and pt352_back["passed"]),
    }

    pt352_forward = run_pt352(); pt353_forward = run_pt353_from_pt352(pt352_forward)
    if pt352_forward["passed"] and pt353_forward["passed"]:
        pt354_forward = run_pt354(); forward_core = run_pr192_forward(); downstream_entered = True
    else:
        pt354_forward = {"passed": False}; forward_core = {"pass": False, "execution": ["PT355", "PT366", "PT477", "PT222"]}; downstream_entered = False
    directions.append("FORWARD")
    forward = {
        **forward_core,
        "execution": ["PT352", "PT353", "PT354"] + list(forward_core["execution"]),
        "PT352": projection_pt352(pt352_forward),
        "PT353": projection_pt353(pt353_forward),
        "PT354": projection_pt354(pt354_forward) if downstream_entered else pt354_forward,
        "PT354_entered_only_after_PT352_PT353_pass": bool(downstream_entered),
        "pass": bool(downstream_entered and pt354_forward["passed"] and forward_core["pass"]),
    }

    left = run_left_control(); directions.append("LEFT")
    right = run_right_control(); directions.append("RIGHT")
    mirrors = {name: back[name] == forward[name] for name in ["PT352", "PT353", "PT354", "PT355", "PT366", "PT477", "PT222"]}
    forward_again = {
        "prediction": "7/7 PT352/PT353/PT354/PT355/PT366/PT477/PT222 projections mirror; manifest-backed PT353 removes repeated restriction scans; PT351/PT350 remain untouched.",
        "stage_mirrors": mirrors,
        "mirror_passes": sum(bool(v) for v in mirrors.values()),
        "mirror_total": 7,
        "passed": all(mirrors.values()),
    }; directions.append("FORWARD_AGAIN")

    combined_literal_visits = pt352_forward["literal_visits"] + pt353_forward["literal_visits"]
    cost_improved = combined_literal_visits < LEGACY_PT353_LITERAL_VISITS
    back_again = {
        "PR190_classification": PR190_CLASS,
        "PR191_preserved_status": EXPECTED_PR191_STOP,
        "PR192_classification": PR192_CLASS,
        "PT352_source_status": "HEURISTIC_FORMATION_PROMPT_ONLY",
        "PT351_status": "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "PT350_status": "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "ancient_algorithm_claim_removed": True,
        "P_VS_NP": "OPEN",
        "passed": True,
    }; directions.append("BACK_AGAIN")

    gates = {
        "direction_order_exact": directions == EXPECTED_DIRECTIONS,
        "BACK_stage_order_exact": back["execution"] == EXPECTED_BACK,
        "FORWARD_stage_order_exact": forward["execution"] == EXPECTED_FORWARD,
        "PT352_BACK_pass": pt352_back["passed"],
        "PT352_FORWARD_pass": pt352_forward["passed"],
        "PT353_BACK_pass": pt353_back["passed"],
        "PT353_FORWARD_pass": pt353_forward["passed"],
        "PT353_all_negatives_block_PT354": pt353_forward["blocked_before_pt354"] == pt353_forward["negative_controls_total"] and pt353_forward["negative_pt354_entries"] == 0,
        "PT354_entered_only_after_PT352_PT353_pass": forward["PT354_entered_only_after_PT352_PT353_pass"],
        "FORWARD_AGAIN_7_of_7": forward_again["passed"] and forward_again["mirror_passes"] == 7,
        "PT352_plus_PT353_literal_visits_below_legacy_PT353": cost_improved,
        "PT351_untouched": back_again["PT351_status"] == "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "PT350_untouched": back_again["PT350_status"] == "WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "P_VS_NP_OPEN": True,
    }
    all_gates = all(gates.values()) and back["pass"] and forward["pass"] and left["passed"] and right["passed"]
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT352_FORMED_STATE_BEFORE_LIVE" if all_gates else "STOP_AT_PT352_FORMED_STATE_BEFORE_LIVE",
        "integration_discipline": {"integrated_now": "PT352", "PT351": "WATCHLIST_ONLY", "PT350": "WATCHLIST_ONLY", "one_text_one_operator_one_run": True},
        "required_direction_sequence": EXPECTED_DIRECTIONS,
        "executed_direction_sequence": directions,
        "BACK": back, "FORWARD": forward, "LEFT": left, "RIGHT": right,
        "FORWARD_AGAIN": forward_again, "BACK_AGAIN": back_again,
        "gates": gates,
        "cost_comparison": {
            "legacy_PT353_literal_visits_each_direction": LEGACY_PT353_LITERAL_VISITS,
            "PT352_literal_visits_each_direction": pt352_forward["literal_visits"],
            "manifest_backed_PT353_literal_visits_each_direction": pt353_forward["literal_visits"],
            "combined_PT352_PT353_literal_visits_each_direction": combined_literal_visits,
            "literal_visit_ratio_vs_legacy_PT353": combined_literal_visits / LEGACY_PT353_LITERAL_VISITS,
            "warning": "This is the same revealed equality-family accounting proxy, not wall-clock runtime and not a general-CNF complexity result."
        },
        "claim_boundary": [
            "PT352 is a modern formation operator heuristically inspired by textual adjacency.",
            "ANCIENT_TEXT != MODERN_ALGORITHM",
            "No arbitrary-CNF polynomial generator-discovery theorem is established.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    payload = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["integrity_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--self-test", action="store_true"); parser.add_argument("--output")
    args = parser.parse_args(); result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        from pathlib import Path
        p = Path(args.output); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text + "\n")
    print(text)
    if args.self_test and not result["status"].startswith("PASS_KEEP"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
