#!/usr/bin/env python3
"""Full replay of the integrated PT350..PT222 braid plus source-boundary audit.

This file adds no operator. Historical source adjacency is heuristic only.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from janus_pt350_support_field_before_latent_binding import run as run_integrated_machine

RUN_ID = "JANUS-FULL-PICTURE-PT350-TO-PT222-SOURCE-COMPLETENESS-2026-08-18-v1"
FORWARD = ["PT350","PT351","PT352","PT353","PT354","PT355","PT366","PT477","PT222"]
BACK = list(reversed(FORWARD))
SIX = ["BACK","FORWARD","LEFT","RIGHT","FORWARD_AGAIN","BACK_AGAIN"]


def run() -> dict:
    machine = run_integrated_machine()

    inherited_gate_values = dict(machine["gates"])
    all_inherited = all(bool(v) for v in inherited_gate_values.values())
    forward_exact = machine["FORWARD"]["execution"] == FORWARD
    back_exact = machine["BACK"]["execution"] == BACK
    mirrors = machine["FORWARD_AGAIN"]["mirror_passes"] == 9 and machine["FORWARD_AGAIN"]["mirror_total"] == 9
    six_exact = machine["executed_direction_sequence"] == SIX

    source_tail = {
        "current_earliest_integrated": "PT350",
        "candidate_predecessor": "PT349",
        "sethe_numeric_adjacent": True,
        "mercer_editorial_boundary": "PT338-349 Offerings for the Deceased King -> PT350-374 Miscellaneous Utterances on the Hereafter",
        "teti_east_gable_object_id": "Y4ZYSDROK5CBFAAQBKMRF7HTLE",
        "same_object_contains_PT349_and_PT350": True,
        "PT349_status": "SOURCE_CONTINUATION_CANDIDATE_NOT_INTEGRATED",
        "tail_source_completeness": "OPEN_PENDING_PT349_SOURCE_OPERATOR_AUDIT"
    }
    source_head = {
        "current_terminal_integrated": "PT222",
        "unas_PT222_text_id": "USXOQHMRHJDX3LJKRIGZHHPSXI",
        "unas_east_wall_object_id": "NEYX37SSZBEEVKHKW2FBU4YEKM",
        "same_wall_sequence": ["PT220","PT221","PT222","PT223","PT224"],
        "PT223": {"text_id":"MGTSNHTSLBBBRMUUAVVSGBJRLY","status":"HIGH_CONFIDENCE_SAME_WALL_CONTINUATION_CANDIDATE_NOT_INTEGRATED"},
        "PT224": {"text_id":"AQXZDO2EIVCCBK24S5ICOLSXLE","status":"HIGH_CONFIDENCE_SAME_WALL_CONTINUATION_CANDIDATE_NOT_INTEGRATED"},
        "PT225": {"status":"LOWER_CONFIDENCE_EDITORIAL_SEQUENCE_CONTINUATION_NOT_ON_UNAS_EAST_WALL_OBJECT","note":"Mercer groups PT223-225; PT225 is described as a variant of PT224, while the cited Unas east-wall object lists through PT224."},
        "head_source_completeness": "OPEN_PENDING_PT223_PT224_AUDIT"
    }

    no_boundary_candidates_integrated = bool(
        machine["integration_discipline"]["integrated_now"] == "PT350"
        and machine["BACK_AGAIN"]["PT349_status"] == "BOUNDARY_AUDIT_ONLY_NOT_IN_CODE_NOT_IN_GATES"
        and "PT223" not in machine["FORWARD"]["execution"]
        and "PT224" not in machine["FORWARD"]["execution"]
        and "PT225" not in machine["FORWARD"]["execution"]
    )

    gates = {
        "integrated_machine_PASS": machine["status"] == "PASS_KEEP_PT350_SUPPORT_FIELD_BEFORE_LATENT_BINDING",
        "six_direction_order_exact": six_exact,
        "FORWARD_order_exact": forward_exact,
        "BACK_order_exact": back_exact,
        "FORWARD_AGAIN_9_of_9": mirrors,
        "all_inherited_fail_closed_gates_true": all_inherited,
        "boundary_candidates_not_integrated": no_boundary_candidates_integrated,
        "tail_source_completeness_OPEN": source_tail["tail_source_completeness"].startswith("OPEN"),
        "head_source_completeness_OPEN": source_head["head_source_completeness"].startswith("OPEN"),
        "P_VS_NP_OPEN": machine["mathematical_verdict"]["P_VS_NP"] == "OPEN",
    }
    passed = all(gates.values())

    result = {
        "artifact_id": RUN_ID,
        "status": "PASS_FULL_PICTURE_WITH_OPEN_HEAD_AND_TAIL_SOURCE_CONTINUATIONS" if passed else "STOP_FULL_PICTURE_SOURCE_COMPLETENESS_AUDIT",
        "run_type": "FULL_REPLAY_AND_SOURCE_BOUNDARY_AUDIT_NO_NEW_OPERATOR",
        "machine_snapshot": {
            "status": machine["status"],
            "FORWARD": machine["FORWARD"]["execution"],
            "BACK": machine["BACK"]["execution"],
            "six_direction": machine["executed_direction_sequence"],
            "mirrors": f"{machine['FORWARD_AGAIN']['mirror_passes']}/{machine['FORWARD_AGAIN']['mirror_total']}",
            "PT350": {
                "positive_field_manifests": machine["FORWARD"]["PT350"]["positive_field_manifests"],
                "positive_support_pairs_total": machine["FORWARD"]["PT350"]["positive_support_pairs_total"],
                "negative_field_controls_total": machine["FORWARD"]["PT350"]["negative_field_controls_total"],
                "negative_pt351_entries": machine["FORWARD"]["PT350"]["negative_pt351_entries"],
            },
            "PT351": {
                "positive_bindings": machine["FORWARD"]["PT351"]["positive_bindings"],
                "negative_controls_total": machine["FORWARD"]["PT351"]["negative_controls_total"],
                "negative_pt352_entries": machine["FORWARD"]["PT351"]["negative_pt352_entries"],
            },
            "PT352": {
                "formed": machine["FORWARD"]["PT352"]["formed"],
                "verified": machine["FORWARD"]["PT352"]["verified"],
            },
            "PT353": {
                "positive_live_passes": machine["FORWARD"]["PT353"]["positive_live_passes"],
                "negative_controls_total": machine["FORWARD"]["PT353"]["negative_controls_total"],
                "negative_pt354_entries": machine["FORWARD"]["PT353"]["negative_pt354_entries"],
            },
            "PT354": {
                "authorized": machine["FORWARD"]["PT354"]["authorized"],
                "total_generators": machine["FORWARD"]["PT354"]["total_generators"],
            },
            "PT355": {
                "raw_residual_states": machine["FORWARD"]["PT355"]["raw_residual_states"],
                "normalized_residual_states": machine["FORWARD"]["PT355"]["normalized_residual_states"],
            },
            "PT366": {
                "samples": machine["FORWARD"]["PT366"]["samples"],
                "reverse_map_passes": machine["FORWARD"]["PT366"]["reverse_map_passes"],
            },
            "PT477": {
                "residual_states": machine["FORWARD"]["PT477"]["candidate"]["residual_states"],
                "saved_buzz_return_checks": machine["FORWARD"]["PT477"]["candidate"]["saved_buzz_return_checks"],
                "route_rescan_edge_visits": machine["FORWARD"]["PT477"]["candidate"]["route_rescan_edge_visits"],
            },
            "PT222": {
                "raw_prefixes_enumerated_all_n": sum(row["raw_prefixes_enumerated"] for row in machine["FORWARD"]["PT222"]["rows"]),
                "canonical_work_proxy_sum": sum(row["canonical_work_proxy"] for row in machine["FORWARD"]["PT222"]["rows"]),
            },
            "LEFT_pass": machine["LEFT"]["passed"],
            "RIGHT_pass": machine["RIGHT"]["passed"],
            "BACK_AGAIN_pass": machine["BACK_AGAIN"]["passed"],
            "early_literal_visit_subtotal_PT350_to_PT353": machine["cost_vector"]["early_literal_visit_subtotal_PT350_to_PT353"],
            "legacy_PT353_literal_visits_each_direction": machine["cost_vector"]["legacy_PT353_literal_visits_each_direction"],
        },
        "source_tail_audit": source_tail,
        "source_head_audit": source_head,
        "completeness_verdict": {
            "current_machine_internal_completeness": "PASS_FOR_FROZEN_PT350_TO_PT222_SYNTHETIC_BRAID",
            "source_tail_completeness": "OPEN",
            "source_head_completeness": "OPEN",
            "next_tail_candidate": "PT349",
            "next_head_candidates": ["PT223", "PT224"],
            "PT225": "EDITORIAL_VARIANT_WATCHLIST",
        },
        "gates": gates,
        "historical_firewall": [
            "ANCIENT_TEXT != MODERN_ALGORITHM",
            "PT_NUMBER_ORDER != PHYSICAL_WALL_ORDER",
            "EDITORIAL_SEQUENCE != EXECUTION_PIPELINE",
            "SAME_WALL_ADJACENCY_CAN_SUGGEST_A_FALSIFIABLE_TEST_BUT_CANNOT_VALIDATE_IT"
        ],
        "mathematical_verdict": {"P_EQUALS_NP":"NOT_ESTABLISHED","P_NOT_EQUALS_NP":"NOT_ESTABLISHED","P_VS_NP":"OPEN"},
    }
    payload = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    result["integrity_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    return result


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--output"); a=p.parse_args()
    d=run(); text=json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)
    if a.output:
        q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True); q.write_text(text+"\n")
    print(text)
    return 0 if (not a.self_test or d["status"].startswith("PASS_")) else 1

if __name__=="__main__":
    raise SystemExit(main())
