#!/usr/bin/env python3
"""Integrate PT350 as a parent-level disjoint support-field gate before PT351.

Historical source order is heuristic inspiration only. No SAT/UNSAT oracle or
action/generator certificate is used. P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any

from janus_c025_families import equality_family
from janus_pt351_latent_binding_before_formation import run as run_pt351_stack
from janus_tranception_prebirth_orbit_generators import FROZEN_N, digest_json

RUN_ID = "JANUS-PT350-SUPPORT-FIELD-BEFORE-LATENT-BINDING-2026-08-18-v1"
EXPECTED_DIRECTIONS = ["BACK", "FORWARD", "LEFT", "RIGHT", "FORWARD_AGAIN", "BACK_AGAIN"]
EXPECTED_BACK = ["PT222", "PT477", "PT366", "PT355", "PT354", "PT353", "PT352", "PT351", "PT350"]
EXPECTED_FORWARD = ["PT350", "PT351", "PT352", "PT353", "PT354", "PT355", "PT366", "PT477", "PT222"]
NEGATIVE_NAMES = ["missing_field", "parent_anchor_tamper", "duplicate_pair", "overlapping_pair", "absent_variable", "coverage_hole"]


def tamper_hex(value: str) -> str:
    if not value:
        return value
    return ("0" if value[0] != "0" else "1") + value[1:]


def run_pt350() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    positive_manifests = 0
    positive_pairs = 0
    negative_rejects = {name: 0 for name in NEGATIVE_NAMES}
    negative_pt351_entries = 0
    hash_ops = 0
    literal_visits = 0
    presence_checks = 0

    for n in FROZEN_N:
        formula, x_vars, y_vars = equality_family(n)
        parent_anchor = digest_json(formula)
        hash_ops += 1
        present: set[int] = set()
        for clause in formula:
            for lit in clause:
                present.add(abs(int(lit)))
                literal_visits += 1
        expected_pairs = [[int(x_vars[i]), int(y_vars[i])] for i in range(n)]
        body = {
            "kind": "PT350_SUPPORT_FIELD",
            "n": n,
            "parent_anchor": parent_anchor,
            "pairs": expected_pairs,
        }
        commitment = digest_json(body)
        hash_ops += 1

        def verify(candidate_body: dict[str, Any] | None, candidate_commitment: str | None) -> bool:
            nonlocal hash_ops, presence_checks
            presence_checks += 1
            if candidate_body is None or candidate_commitment is None:
                return False
            hash_ops += 1
            if digest_json(candidate_body) != candidate_commitment:
                return False
            pairs = candidate_body.get("pairs")
            if not isinstance(pairs, list) or len(pairs) != n:
                return False
            seen: set[int] = set()
            normalized: list[list[int]] = []
            for pair in pairs:
                if not isinstance(pair, list) or len(pair) != 2:
                    return False
                a, b = int(pair[0]), int(pair[1])
                if a == b or a not in present or b not in present:
                    return False
                if a in seen or b in seen:
                    return False
                seen.add(a); seen.add(b)
                normalized.append([a, b])
            return bool(
                candidate_body.get("kind") == "PT350_SUPPORT_FIELD"
                and candidate_body.get("n") == n
                and candidate_body.get("parent_anchor") == parent_anchor
                and normalized == expected_pairs
            )

        if verify(body, commitment):
            positive_manifests += 1
            positive_pairs += n

        variants: list[tuple[str, dict[str, Any] | None, str | None]] = [("missing_field", None, None)]
        b = dict(body); b["parent_anchor"] = tamper_hex(parent_anchor); c = digest_json(b); hash_ops += 1; variants.append(("parent_anchor_tamper", b, c))
        b = {**body, "pairs": [list(p) for p in expected_pairs]}; b["pairs"][-1] = list(b["pairs"][0]); c = digest_json(b); hash_ops += 1; variants.append(("duplicate_pair", b, c))
        b = {**body, "pairs": [list(p) for p in expected_pairs]}; b["pairs"][1][0] = b["pairs"][0][0]; c = digest_json(b); hash_ops += 1; variants.append(("overlapping_pair", b, c))
        b = {**body, "pairs": [list(p) for p in expected_pairs]}; b["pairs"][-1][1] = max(present) + 1; c = digest_json(b); hash_ops += 1; variants.append(("absent_variable", b, c))
        b = {**body, "pairs": [list(p) for p in expected_pairs[:-1]]}; c = digest_json(b); hash_ops += 1; variants.append(("coverage_hole", b, c))

        row_negative = 0
        for name, candidate_body, candidate_commitment in variants:
            if not verify(candidate_body, candidate_commitment):
                negative_rejects[name] += 1
                row_negative += 1
            else:
                negative_pt351_entries += 1
        rows.append({
            "n": n,
            "support_pairs": n,
            "field_verified": True,
            "negative_rejects": row_negative,
            "negative_expected": len(NEGATIVE_NAMES),
            "all_negatives_blocked": row_negative == len(NEGATIVE_NAMES),
        })

    negative_total = len(FROZEN_N) * len(NEGATIVE_NAMES)
    passed = bool(
        positive_manifests == len(FROZEN_N)
        and positive_pairs == sum(FROZEN_N) == 494
        and all(v == len(FROZEN_N) for v in negative_rejects.values())
        and sum(negative_rejects.values()) == negative_total
        and negative_pt351_entries == 0
    )
    return {
        "stage": "PT350_DISJOINT_SUPPORT_FIELD_BEFORE_LATENT_BINDING",
        "rule": "ESTABLISH_DISJOINT_SUPPORT_FIELD -> ONLY_THEN_GESTATE_LATENT_BINDINGS",
        "rows": rows,
        "positive_field_manifests": positive_manifests,
        "positive_support_pairs_total": positive_pairs,
        "negative_controls_per_parent": len(NEGATIVE_NAMES),
        "negative_field_controls_total": negative_total,
        "negative_rejects": negative_rejects,
        "negative_pt351_entries": negative_pt351_entries,
        "hash_ops": hash_ops,
        "literal_visits": literal_visits,
        "presence_checks": presence_checks,
        "uses_restricted_child_construction": False,
        "uses_action_certificate": False,
        "uses_sat_oracle": False,
        "passed": passed,
    }


def run() -> dict[str, Any]:
    pt350_back = run_pt350()
    base = run_pt351_stack()
    pt350_forward = run_pt350()

    back = dict(base["BACK"])
    back["execution"] = list(base["BACK"]["execution"]) + ["PT350"]
    back["PT350"] = pt350_back
    back["pass"] = bool(base["BACK"]["pass"] and pt350_back["passed"])

    forward = dict(base["FORWARD"])
    forward["execution"] = ["PT350"] + list(base["FORWARD"]["execution"])
    forward["PT350"] = pt350_forward
    forward["PT351_entered_only_after_PT350_pass"] = pt350_forward["passed"]
    forward["pass"] = bool(pt350_forward["passed"] and base["FORWARD"]["pass"])

    mirrors = {"PT350": pt350_back == pt350_forward}
    for name in ["PT351", "PT352", "PT353", "PT354", "PT355", "PT366", "PT477", "PT222"]:
        mirrors[name] = base["BACK"][name] == base["FORWARD"][name]
    forward_again = {
        "prediction": "9/9 PT350/PT351/PT352/PT353/PT354/PT355/PT366/PT477/PT222 mirror; all PT350 field negatives block PT351; PT349 remains boundary-audit only.",
        "stage_mirrors": mirrors,
        "mirror_passes": sum(bool(v) for v in mirrors.values()),
        "mirror_total": 9,
        "passed": all(mirrors.values()),
    }

    back_again = dict(base["BACK_AGAIN"])
    back_again["PT350_source_status"] = "HEURISTIC_SUPPORT_FIELD_PROMPT_ONLY"
    back_again["PT349_status"] = "BOUNDARY_AUDIT_ONLY_NOT_IN_CODE_NOT_IN_GATES"
    back_again["P_VS_NP"] = "OPEN"
    back_again["passed"] = True

    gates = {
        "direction_order_exact": base["executed_direction_sequence"] == EXPECTED_DIRECTIONS,
        "BACK_stage_order_exact": back["execution"] == EXPECTED_BACK,
        "FORWARD_stage_order_exact": forward["execution"] == EXPECTED_FORWARD,
        "PT350_BACK_pass": pt350_back["passed"],
        "PT350_FORWARD_pass": pt350_forward["passed"],
        "PT350_all_negatives_block_PT351": sum(pt350_forward["negative_rejects"].values()) == pt350_forward["negative_field_controls_total"] and pt350_forward["negative_pt351_entries"] == 0,
        "PT351_entered_only_after_PT350_pass": forward["PT351_entered_only_after_PT350_pass"],
        "FORWARD_AGAIN_9_of_9": forward_again["passed"] and forward_again["mirror_passes"] == 9,
        "PT352_PT353_cost_improvement_preserved": base["cost_vector"]["PT352_plus_manifest_PT353_literal_visits_each_direction"] == 1397752,
        "PT351_cost_preserved": base["cost_vector"]["PT351_literal_visits_each_direction"] == 1976,
        "PT349_not_integrated": back_again["PT349_status"] == "BOUNDARY_AUDIT_ONLY_NOT_IN_CODE_NOT_IN_GATES",
        "P_VS_NP_OPEN": True,
    }
    all_gates = all(gates.values()) and back["pass"] and forward["pass"] and base["LEFT"]["passed"] and base["RIGHT"]["passed"]
    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT350_SUPPORT_FIELD_BEFORE_LATENT_BINDING" if all_gates else "STOP_AT_PT350_SUPPORT_FIELD_BEFORE_LATENT_BINDING",
        "integration_discipline": {"integrated_now": "PT350", "PT349": "BOUNDARY_AUDIT_ONLY", "one_text_one_operator_one_run": True},
        "required_direction_sequence": EXPECTED_DIRECTIONS,
        "executed_direction_sequence": list(base["executed_direction_sequence"]),
        "BACK": back,
        "FORWARD": forward,
        "LEFT": base["LEFT"],
        "RIGHT": base["RIGHT"],
        "FORWARD_AGAIN": forward_again,
        "BACK_AGAIN": back_again,
        "gates": gates,
        "cost_vector": {
            "PT350_literal_visits_each_direction": pt350_forward["literal_visits"],
            "PT350_hash_ops_each_direction": pt350_forward["hash_ops"],
            "PT351_literal_visits_each_direction": base["cost_vector"]["PT351_literal_visits_each_direction"],
            "PT352_plus_manifest_PT353_literal_visits_each_direction": base["cost_vector"]["PT352_plus_manifest_PT353_literal_visits_each_direction"],
            "legacy_PT353_literal_visits_each_direction": base["cost_vector"]["legacy_PT353_literal_visits_each_direction"],
            "early_literal_visit_subtotal_PT350_to_PT353": pt350_forward["literal_visits"] + base["cost_vector"]["PT351_literal_visits_each_direction"] + base["cost_vector"]["PT352_plus_manifest_PT353_literal_visits_each_direction"],
            "warning": "Only literal-visit quantities are subtotaled here. Do not mix them with heterogeneous downstream work proxies."
        },
        "claim_boundary": [
            "PT350 is a modern parent-level support-field operator heuristically inspired by textual position/seed-field imagery.",
            "ANCIENT_TEXT != MODERN_ALGORITHM",
            "PT_NUMBER_ORDER != PHYSICAL_WALL_ORDER",
            "No arbitrary-CNF polynomial generator-discovery or quotient-size theorem is established.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    payload = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["integrity_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    return result


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--self-test", action="store_true"); p.add_argument("--output"); a = p.parse_args()
    d = run(); text = json.dumps(d, ensure_ascii=False, indent=2, sort_keys=True)
    if a.output:
        from pathlib import Path
        q = Path(a.output); q.parent.mkdir(parents=True, exist_ok=True); q.write_text(text + "\n")
    print(text)
    return 0 if (not a.self_test or d["status"].startswith("PASS_KEEP")) else 1

if __name__ == "__main__":
    raise SystemExit(main())
