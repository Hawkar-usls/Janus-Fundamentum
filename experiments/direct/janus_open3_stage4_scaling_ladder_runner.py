#!/usr/bin/env python3
"""Execute the preregistered C025 OPEN3 Stage4 scaling ladder exactly as frozen.

The runner executes R1..R4 in order and stops only at the first finite Stage4
barrier, matching C025_OPEN3_STAGE4_SCALING_LADDER_PREREGISTRATION_2026-08-26.
It does not change the Stage4 grammar, cap exponent, Shannon depth, or rung
parameters after seeing results. Absence of a barrier remains finite evidence,
not a totality theorem.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

P_VS_NP = "OPEN"

RUNG_SPEC = (
    {"id": "R1", "nvars": 4, "clauses": 5, "min_width": 3, "max_width": 3, "limit": 5000},
    {"id": "R2", "nvars": 4, "clauses": 6, "min_width": 3, "max_width": 3, "limit": 10000},
    {"id": "R3", "nvars": 5, "clauses": 6, "min_width": 3, "max_width": 3, "limit": 10000},
    {"id": "R4", "nvars": 5, "clauses": 7, "min_width": 3, "max_width": 3, "limit": 20000},
)


def _run_rung(rung: dict) -> dict:
    command = [
        sys.executable,
        "-m",
        "experiments.direct.janus_open3_stage4_bounded_coverage_probe",
        "--nvars", str(rung["nvars"]),
        "--clauses", str(rung["clauses"]),
        "--min-width", str(rung["min_width"]),
        "--max-width", str(rung["max_width"]),
        "--cap-exponent", "2",
        "--limit", str(rung["limit"]),
    ]
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    report = json.loads(completed.stdout)
    boundary = report["scientific_boundary"]
    if boundary["bounded_finite_probe_only"] is not True:
        raise AssertionError("RUNG_LOST_FINITE_PROBE_BOUNDARY")
    if boundary["absence_of_counterexample_is_not_totality_proof"] is not True:
        raise AssertionError("RUNG_LOST_NO_TOTALITY_PROMOTION_BOUNDARY")
    if boundary["P_VS_NP"] != "OPEN":
        raise AssertionError("RUNG_PROMOTED_P_VS_NP")
    return report


def main() -> int:
    reports = []
    first_barrier = None

    for rung in RUNG_SPEC:
        report = _run_rung(rung)
        row = {
            "id": rung["id"],
            "frozen_parameters": rung,
            "status": report["status"],
            "totals": report["totals"],
            "first_open3": report["first_open3"],
            "first_barrier": report["first_barrier"],
            "search_space": report["search_space"],
        }
        reports.append(row)
        if report["first_barrier"] is not None:
            first_barrier = {"rung": rung["id"], **report["first_barrier"]}
            break

    aggregate = {
        "schema": "JANUS/C025/OPEN3-STAGE4-SCALING-LADDER-EXECUTION/v1",
        "status": (
            "FINITE_STAGE4_BARRIER_FOUND"
            if first_barrier is not None
            else "NO_BARRIER_IN_ALL_PREREGISTERED_RUNGS"
        ),
        "preregistration": "research/C025_OPEN3_STAGE4_SCALING_LADDER_PREREGISTRATION_2026-08-26.json",
        "grammar_changed_during_ladder": False,
        "cap_exponent": 2,
        "extension_exponent": 1,
        "rungs_executed": reports,
        "first_barrier": first_barrier,
        "scientific_boundary": {
            "bounded_finite_ladder_only": True,
            "absence_of_barrier_is_not_totality_proof": True,
            "presence_of_barrier_refutes_only_current_stage4_grammar_at_frozen_cap": True,
            "universal_OPEN3_move_availability": "OPEN",
            "universal_GPEI_preservation": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(aggregate, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
