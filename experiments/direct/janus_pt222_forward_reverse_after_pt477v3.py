#!/usr/bin/env python3
"""PT222 continuation after a passing PT477-v3 local replay de-duplication.

PT222 is used only as a historical prompt for mandatory forward/reverse replay.
The modern operator is an exact proof/witness audit on the frozen blocked-equality
n=14 control.  Reverse replay is a falsification/safety mechanism, not physical
retrocausality.  P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from janus_p_vs_np_dual_lane_tranception_c025_bhq2 import (
    audit_blocked_equality_signed_orbit,
)
from janus_pt477_v3_local_apep_edge_tombstone import run as run_pt477_v3

RUN_ID = "JANUS-PT222-FORWARD-REVERSE-AFTER-PT477V3-2026-08-18-v1"
EXPECTED = 1 << 14
EXPECTED_PARENT = {
    "residual_states": 2822,
    "bytewise_distinct_absorptions": 602,
    "polarity_flip_absorptions": 450,
    "event_horizon_collisions": 839,
    "canonical_edge_visits": 3488298,
    "resolution_attempts": 626489,
    "resolution_additions": 93638,
    "buzz_return_checks": 1844,
    "saved_buzz_return_checks": 1050,
    "route_rescan_edge_visits": 0,
}


def sha256_json(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run(n: int = 14) -> dict[str, Any]:
    if n != 14:
        raise ValueError("PT222 frozen continuation is preregistered only for n=14")

    parent = run_pt477_v3()
    parent_candidate = parent["candidate"]
    parent_reproduced = bool(
        parent["status"] == "PASS_KEEP_PT477_V3_LOCAL_REPLAY_DEDUP"
        and all(parent_candidate[name] == value for name, value in EXPECTED_PARENT.items())
    )

    audit = audit_blocked_equality_signed_orbit(n=n)

    gates = {
        "pt477_v3_parent_reproduced": parent_reproduced,
        "prefix_assignments_exact": audit["prefix_assignments"] == EXPECTED,
        "raw_fixed_coordinate_states_exact": audit["raw_fixed_coordinate_states"] == EXPECTED,
        "signed_orbit_singularities_exactly_one": audit["signed_orbit_singularities"] == 1,
        "normalization_certificate_passes_exact": audit["normalization_certificate_passes"] == EXPECTED,
        "forward_map_passes_exact": audit["forward_map_passes"] == EXPECTED,
        "inverse_map_passes_exact": audit["inverse_map_passes"] == EXPECTED,
        "residual_witness_passes_exact": audit["residual_witness_passes"] == EXPECTED,
        "full_formula_witness_passes_exact": audit["full_formula_witness_passes"] == EXPECTED,
        "enumerated_total_map_entries_exact": audit["enumerated_total_map_entries"] == 229376,
        "polarity_flips_total_exact": audit["polarity_flips_total"] == 114688,
        "all_absorptions_reversible": bool(audit["all_absorptions_reversible"]),
    }

    passed = all(gates.values())
    result: dict[str, Any] = {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_PT222_FORWARD_REVERSE_REPLAY" if passed else "STOP_AT_PT222_REPLAY_FAILURE",
        "operator": "TRANCEPTION_FORWARD_REVERSE_REPLAY",
        "run_scope": "REVEALED_FROZEN_CONTROLS_ONLY_NO_NEW_HOLDOUT",
        "historical_inspiration_boundary": {
            "PT222": "UP_DOWN_FORWARD_REVERSE_CYCLE_PROMPT_ONLY",
            "ancient_text_is_algorithmic_evidence": False,
            "physical_retrocausality_claim": False,
        },
        "parent_pt477_v3": {
            "status": parent["status"],
            "candidate": parent_candidate,
            "reproduced": parent_reproduced,
        },
        "pt222_audit": audit,
        "gates": gates,
        "ladder": {
            "PT355": "KEEP_FROM_PARENT",
            "PT366": "KEEP_FROM_PARENT",
            "PT477_v1": "REJECTED_FROM_PARENT",
            "PT477_v2": "REJECTED_FROM_PARENT",
            "PT477_v3": "KEEP_REPRODUCED" if parent_reproduced else "PARENT_REPRO_FAIL",
            "PT222": "KEEP" if passed else "REJECT",
        },
        "next_target": (
            "UNIVERSAL_CERTIFIED_RESIDUAL_ORBIT_AUTOMATON_COMPLEXITY"
            if passed
            else "NONE_STOP_AT_PT222"
        ),
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED",
        },
        "claim_boundary": [
            "Every accepted frozen n=14 signed route must replay forward, inverse, residual witness, and full-formula witness.",
            "The audit still enumerates 2^14 prefixes and therefore is not a universal polynomial construction.",
            "A finite PT222 pass cannot establish P=NP.",
            "A PT222 failure could reject this continuation but could not establish P!=NP.",
            "Reverse replay is verification, not physical retrocausality.",
        ],
    }
    result["integrity_sha256"] = sha256_json(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=14)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run(n=args.n)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.self_test:
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["status"] in {
            "PASS_KEEP_PT222_FORWARD_REVERSE_REPLAY",
            "STOP_AT_PT222_REPLAY_FAILURE",
        }


if __name__ == "__main__":
    main()
