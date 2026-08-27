#!/usr/bin/env python3
"""Full-trajectory bounded falsification probe on preregistered OPEN3 witnesses.

This does NOT promote the Stage4 grammar to a theorem.  It takes the first OPEN3
instance frozen by each already-preregistered scaling-ladder rung and runs the
existing fixed v3 exact-cap engine all the way to SAT/UNSAT/OPEN without changing
its grammar, cap exponents, or decision rules after seeing an instance.

Purpose: expose the first concrete multi-step barrier, if one exists, rather than
mistaking one-step Stage4 availability for reachable-corridor totality.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3

P_VS_NP = "OPEN"

# Frozen verbatim from the successful preregistered R1..R4 reverse-pass ladder.
FROZEN_OPEN3 = (
    {
        "id": "R1_FIRST_OPEN3",
        "fingerprint": "a9cdd17ae17e3fbd709e64a234bac739530f870a5998f30a9dfe6a10f2c54c00",
        "cnf": ((-2, -3, -4), (-2, -3, 4), (-2, 3, -4), (-1, -3, -4), (-1, -2, -4)),
    },
    {
        "id": "R2_FIRST_OPEN3",
        "fingerprint": "7056c5a0722b1a34653edbec523eaa372e6c9c4b51af1a4d8990af82d9155ab2",
        "cnf": ((-2, -3, -4), (-2, -3, 4), (-2, 3, -4), (-2, 3, 4), (-1, -3, -4), (1, 2, 3)),
    },
    {
        "id": "R3_FIRST_OPEN3",
        "fingerprint": "152358aabf7212eeb40bd609e476068fc321c47b8bcca91ac6d22abfacf76ed4",
        "cnf": ((-3, -4, -5), (-3, -4, 5), (-3, 4, -5), (-3, 4, 5), (-2, -4, -5), (-1, 2, -3)),
    },
    {
        "id": "R4_FIRST_OPEN3",
        "fingerprint": "d7facaf8ee977053faee0c7b7bb0484892e22380a22f6098d2e3308b50ead053",
        "cnf": ((-3, -4, -5), (-3, -4, 5), (-3, 4, -5), (-3, 4, 5), (-2, -4, -5), (-2, -4, 5), (-1, 2, -5)),
    },
)


def _event_counts(events: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for event in events:
        kind = str(event.get("kind", "UNKNOWN"))
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def run_one(spec: dict) -> dict:
    cnf = base.canon_cnf(spec["cnf"])
    fingerprint = base.fingerprint(cnf)
    if fingerprint != spec["fingerprint"]:
        raise AssertionError(f"FROZEN_OPEN3_FINGERPRINT_DRIFT:{spec['id']}")

    result = v3.solve_fail_closed_v3(
        cnf,
        cap_exponent=2,
        extension_exponent=1,
        bounded_resolution_width=3,
    )
    if result["scientific_boundary"]["P_VS_NP"] != "OPEN":
        raise AssertionError("FINITE_TRAJECTORY_PROMOTED_P_VS_NP")
    if result["scientific_boundary"]["heuristic_promotion"] is not False:
        raise AssertionError("HEURISTIC_PROMOTION_ENTERED_TRAJECTORY")
    if result["status"] == "SAT":
        witness = result.get("witness")
        if witness is None or not base.verify_total_assignment(cnf, {int(k): int(v) for k, v in witness.items()}):
            raise AssertionError("SAT_TRAJECTORY_WITNESS_FAILED_ROOT_REPLAY")

    ledger = result["ledger"]
    return {
        "id": spec["id"],
        "source_fingerprint": fingerprint,
        "N": result["N"],
        "status": result["status"],
        "reason": result["reason"],
        "residual_fingerprint": result["residual_fingerprint"],
        "residual_units": result["residual_units"],
        "progress_phi": result["progress_phi"],
        "state_cap": result["state_cap"],
        "extension_cap": result["extension_cap"],
        "ledger": ledger,
        "event_counts": _event_counts(result.get("events", [])),
        "missing_bridge": result.get("missing_bridge"),
    }


def main() -> int:
    rows = [run_one(spec) for spec in FROZEN_OPEN3]
    first_open = next((row for row in rows if row["status"] == "OPEN"), None)
    report = {
        "schema": "JANUS/C025/FULL-TRAJECTORY-FROZEN-OPEN3-PROBE/v1",
        "status": "FINITE_MULTI_STEP_BARRIER_FOUND" if first_open else "NO_OPEN_ON_FROZEN_OPEN3_TRAJECTORIES",
        "grammar": "EXISTING_FIXED_V3_EXACT_CAP_ENGINE",
        "cap_exponent": 2,
        "extension_exponent": 1,
        "cases": rows,
        "first_open": first_open,
        "scientific_boundary": {
            "bounded_finite_probe_only": True,
            "tests_full_engine_trajectory_not_only_one_stage4_move": True,
            "absence_of_open_is_not_totality_proof": True,
            "does_not_prove_input_relative_polynomial_envelope": True,
            "universal_GPEI_preservation": "OPEN",
            "arbitrary_CNF_totality": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
