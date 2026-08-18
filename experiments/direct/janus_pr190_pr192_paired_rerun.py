#!/usr/bin/env python3
"""Fresh paired rerun of PR190 restricted repair and PR192 canonical six-direction pass.

This does not reinterpret PR190 as canonical pyramid FORWARD.  It reruns its
restricted equality-family kernel under the canonical conservative cost ledger,
then reruns PR192 in the same checkout/process and compares the shared PT222
kernel exactly.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from janus_tranception_prebirth_orbit_generators import FROZEN_N, analyze_n
from janus_corrected_six_direction_reverse_pass import run as run_pr192

RUN_ID = "JANUS-PR190-PR192-PAIRED-RERUN-2026-08-18-v1"
PR190_HEAD = "a24039ba24b880dc3c80d45ebc2c8f7bcfb3af26"
PR192_HEAD = "0f325335f270af9a0aa8a1a0ac1f32e3bfb88f13"


def digest(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def canonical_cost(n: int) -> int:
    return (89 * n * n + 45 * n) // 2


def project_row_from_analyze(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "n": row["n"],
        "represented_raw_prefixes": row["represented_raw_prefixes"],
        "generator_count": row["generator_count"],
        "symbolic_states": row["symbolic_quotient_states"],
        "symbolic_transitions": row["symbolic_quotient_transitions"],
        "raw_prefixes_enumerated": row["raw_prefixes_enumerated"],
        "automorphism_passes": row["automorphism_passes"],
        "branch_pair_passes": row["branch_pair_passes"],
        "canonical_work_proxy": canonical_cost(row["n"]),
        "legacy_head_incomplete_work_proxy": row["charged_work"]["polynomial_work_proxy"],
        "passed": row["passed"],
    }


def project_row_from_192(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "n": row["n"],
        "represented_raw_prefixes": row["represented_raw_prefixes"],
        "generator_count": row["generator_count"],
        "symbolic_states": row["symbolic_states"],
        "symbolic_transitions": row["symbolic_transitions"],
        "raw_prefixes_enumerated": row["raw_prefixes_enumerated"],
        "automorphism_passes": row["automorphism_passes"],
        "branch_pair_passes": row["branch_pair_passes"],
        "canonical_work_proxy": row["canonical_work_proxy"],
        "legacy_head_incomplete_work_proxy": row["legacy_head_incomplete_work_proxy"],
        "passed": row["passed"],
    }


def run_pr190_restricted() -> dict[str, Any]:
    rows_raw = [analyze_n(n) for n in FROZEN_N]
    rows = [project_row_from_analyze(row) for row in rows_raw]
    gates = {
        "all_rows_pass": all(row["passed"] for row in rows),
        "zero_raw_prefixes_all_n": all(row["raw_prefixes_enumerated"] == 0 for row in rows),
        "states_n_plus_1_all_n": all(row["symbolic_states"] == row["n"] + 1 for row in rows),
        "transitions_n_all_n": all(row["symbolic_transitions"] == row["n"] for row in rows),
        "canonical_cost_formula_all_n": all(row["canonical_work_proxy"] == canonical_cost(row["n"]) for row in rows),
    }
    return {
        "classification": "RESTRICTED_FAMILY_REPAIR_NOT_CANONICAL_PYRAMID_FORWARD",
        "head_sha": PR190_HEAD,
        "rows": rows,
        "canonical_work_proxy_sum": sum(row["canonical_work_proxy"] for row in rows),
        "legacy_head_incomplete_proxy_sum_not_canonical": sum(row["legacy_head_incomplete_work_proxy"] for row in rows),
        "gates": gates,
        "passed": all(gates.values()),
        "row_projection_sha256": digest(rows),
    }


def run() -> dict[str, Any]:
    pr190 = run_pr190_restricted()
    pr192 = run_pr192()

    rows192_back = [project_row_from_192(row) for row in pr192["BACK"]["PT222"]["rows"]]
    rows192_forward = [project_row_from_192(row) for row in pr192["FORWARD"]["PT222"]["rows"]]
    shared_back_exact = pr190["rows"] == rows192_back
    shared_forward_exact = pr190["rows"] == rows192_forward

    extra_192 = {
        "BACK_execution": pr192["BACK"]["execution"],
        "FORWARD_execution": pr192["FORWARD"]["execution"],
        "mirror_passes": pr192["FORWARD_AGAIN"]["mirror_passes"],
        "mirror_total": pr192["FORWARD_AGAIN"]["mirror_total"],
        "LEFT_pass": pr192["LEFT"]["passed"],
        "RIGHT_pass": pr192["RIGHT"]["passed"],
        "BACK_AGAIN_pass": pr192["BACK_AGAIN"]["passed"],
        "direction_order_exact": pr192["direction_order_exact"],
        "PT477_structural_work_proxy_each_direction": pr192["cost_vector"]["PT477_structural_work_proxy_BACK"],
        "PT477_local_bookkeeping_each_direction": pr192["cost_vector"]["PT477_local_bookkeeping_BACK"],
        "PT366_samples_each_direction": pr192["cost_vector"]["PT366_samples_BACK"],
        "PT355_subsumption_steps_each_direction": pr192["cost_vector"]["PT355_subsumption_steps_BACK"],
        "LEFT_control_literal_visits": pr192["cost_vector"]["LEFT_control_literal_visits"],
        "RIGHT_control_literal_visits": pr192["cost_vector"]["RIGHT_control_literal_visits"],
    }

    gates = {
        "PR190_restricted_rerun_pass": pr190["passed"],
        "PR192_six_direction_rerun_pass": pr192["status"] == "PASS_KEEP_CORRECTED_SIX_DIRECTION_REVERSE",
        "shared_PT222_kernel_exact_match_BACK": shared_back_exact,
        "shared_PT222_kernel_exact_match_FORWARD": shared_forward_exact,
        "PR190_zero_raw_prefixes_all_n": pr190["gates"]["zero_raw_prefixes_all_n"],
        "PR192_direction_order_exact": pr192["direction_order_exact"],
        "PR192_mirror_4_of_4": pr192["FORWARD_AGAIN"]["mirror_passes"] == 4 and pr192["FORWARD_AGAIN"]["mirror_total"] == 4,
        "PR192_LEFT_pass": pr192["LEFT"]["passed"],
        "PR192_RIGHT_pass": pr192["RIGHT"]["passed"],
        "PR192_BACK_AGAIN_pass": pr192["BACK_AGAIN"]["passed"],
        "classification_firewall_preserved": pr190["classification"] == "RESTRICTED_FAMILY_REPAIR_NOT_CANONICAL_PYRAMID_FORWARD",
        "P_VS_NP_OPEN": pr192["mathematical_verdict"]["P_VS_NP"] == "OPEN",
    }
    passed = all(gates.values())

    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PR190_PR192_PAIRED_REPRODUCIBILITY" if passed else "STOP_AT_PR190_PR192_PAIRED_REPRODUCIBILITY",
        "run_scope": "FRESH_SAME_CHECKOUT_PAIRED_RERUN_REVEALED_RESTRICTED_CONTROLS_ONLY",
        "PR190": pr190,
        "PR192": {
            "classification": "CANONICAL_STRICT_SIX_DIRECTION_TRANCEPTION",
            "head_sha": PR192_HEAD,
            "status": pr192["status"],
            "PT222_BACK_rows": rows192_back,
            "PT222_FORWARD_rows": rows192_forward,
            "PT222_canonical_work_proxy_sum_each_direction": sum(row["canonical_work_proxy"] for row in rows192_back),
            "extra_six_direction_evidence": extra_192,
            "result_integrity_sha256": pr192["integrity_sha256"],
        },
        "comparison": {
            "shared_kernel": "PR190 restricted prebirth kernel is exactly the PT222 kernel replayed in PR192 BACK and FORWARD.",
            "shared_kernel_BACK_exact": shared_back_exact,
            "shared_kernel_FORWARD_exact": shared_forward_exact,
            "shared_kernel_cost_delta": 0 if shared_back_exact and shared_forward_exact else None,
            "PR190_new_information": "Restricted prebirth quotient reproducibility only; not canonical pyramid FORWARD.",
            "PR192_new_information": "Literal six-direction composition, two opposite ladder traversals, 4/4 mirror prediction, LEFT/RIGHT authority controls, and BACK_AGAIN rollback/audit.",
            "optimization_interpretation": "PR192 is not a speedup over PR190 on the shared PT222 kernel; it pays additional independently charged audit/control work for stronger procedural evidence.",
            "component_units_warning": "Do not sum PT222 proxy, PT477 structural proxy, samples, subsumption steps, and literal visits into a single runtime number."
        },
        "gates": gates,
        "claim_boundary": [
            "This paired PASS, if obtained, is a reproducibility/comparison result on already revealed restricted controls.",
            "PR190 remains a restricted-family repair, not the canonical pyramid FORWARD.",
            "PR192 remains a procedural/compositional six-direction PASS, not a general SAT complexity result.",
            "No arbitrary-CNF polynomial generator discovery theorem is established.",
            "No arbitrary-CNF polynomial quotient-size theorem is established.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED"
        }
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    out = run()
    if args.self_test and out["status"] != "PASS_KEEP_PR190_PR192_PAIRED_REPRODUCIBILITY":
        raise SystemExit(json.dumps(out, ensure_ascii=False, indent=2))
    text = json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main()
