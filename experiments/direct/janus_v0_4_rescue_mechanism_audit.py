#!/usr/bin/env python3
"""Measurement-only audit of actual rescue mechanisms in the frozen v0.4 corpus.

Replays exactly the deterministic width-4 seeds from
janus_v0_4_high_volume_random_cnf_probe and classifies the emitted exact event
trace.  No grammar or decision semantics are changed.  The key question is
whether a high-volume run actually required v2/v3 rescue after ordinary capped
elimination failed, rather than merely having state_units > N.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_v0_4_high_volume_random_cnf_probe as source

P_VS_NP = "OPEN"

RUNG_SEEDS = (
    ("W4_N8_M20", 8, 20, 5100),
    ("W4_N10_M30", 10, 30, 5200),
    ("W4_N12_M42", 12, 42, 5300),
    ("W4_N14_M56", 14, 56, 5400),
    ("W4_N16_M64", 16, 64, 5500),
)


def event_count(events, kind: str) -> int:
    return sum(1 for event in events if event.get("kind") == kind)


def main() -> int:
    rows = []
    totals = {
        "examined": 0,
        "high_volume": 0,
        "v2_rescue_runs": 0,
        "v3_rescue_runs": 0,
        "any_macro_rescue_runs": 0,
        "OPEN": 0,
    }
    first_macro_rescue = None

    for rung_id, nvars, nclauses, seed0 in RUNG_SEEDS:
        for offset in range(2):
            seed = seed0 + offset
            cnf = source.random_width_cnf(nvars, nclauses, 4, seed)
            result = core.solve_decision_core(cnf)
            events = result.get("events", [])
            ordinary = event_count(events, "AKINATOR_EXACT_ELIMINATION")
            v2 = event_count(events, "JEC_MACRO_RESTORE_CAP")
            v3 = event_count(events, "JEC_EXTENSION_TAIL_DESCENT_V3")
            N = int(result["N"])
            max_units = int(result["ledger"]["max_state_units"])
            high = max_units >= 2 * N

            row = {
                "rung": rung_id,
                "seed": seed,
                "status": result["status"],
                "N": N,
                "max_state_units": max_units,
                "max_volume_ratio": max_units / max(1, N),
                "entered_proved_danger_region": high,
                "ordinary_elimination_events": ordinary,
                "v2_macro_rescue_events": v2,
                "v3_tail_rescue_events": v3,
                "extension_count": int(result["ledger"]["extension_count"]),
            }
            rows.append(row)
            totals["examined"] += 1
            totals["high_volume"] += int(high)
            totals["v2_rescue_runs"] += int(v2 > 0)
            totals["v3_rescue_runs"] += int(v3 > 0)
            totals["any_macro_rescue_runs"] += int((v2 + v3) > 0)
            totals["OPEN"] += int(result["status"] == "OPEN")

            if first_macro_rescue is None and (v2 + v3) > 0:
                first_macro_rescue = dict(row)

    report = {
        "schema": "JANUS/C025/V0.4-RESCUE-MECHANISM-AUDIT/v1",
        "status": "MACRO_RESCUE_EXERCISED" if first_macro_rescue else "NO_MACRO_RESCUE_EXERCISED_IN_CORPUS",
        "rows": rows,
        "totals": totals,
        "first_macro_rescue": first_macro_rescue,
        "scientific_boundary": {
            "measurement_only_replay": True,
            "same_frozen_seed_corpus": True,
            "event_presence_is_not_totality_proof": True,
            "HIGH_VOLUME_RESCUE_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
