#!/usr/bin/env python3
"""Execute the frozen OPEN3 stage-4 scaling ladder without grammar changes.

The ladder configuration is read from the preregistration JSON committed before
this runner existed.  Each rung invokes the unchanged bounded probe with the
frozen stage-4 grammar.  The runner stops early only on the preregistered event:
a finite OPEN3 instance for which stage 4 has no exact strict-progress move.

No recursive Shannon-depth increase is permitted.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research" / "C025_OPEN3_STAGE4_SCALING_LADDER_PREREGISTRATION_2026-08-26.json"
PROBE = ROOT / "experiments" / "direct" / "janus_open3_stage4_bounded_coverage_probe.py"


def run_rung(rung: dict, cap_exponent: int) -> dict:
    command = [
        sys.executable,
        str(PROBE),
        "--nvars", str(int(rung["nvars"])),
        "--clauses", str(int(rung["clauses"])),
        "--min-width", str(int(rung["min_width"])),
        "--max-width", str(int(rung["max_width"])),
        "--cap-exponent", str(int(cap_exponent)),
        "--limit", str(int(rung["connected_limit"])),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    report = json.loads(completed.stdout)
    expected = {
        "nvars": int(rung["nvars"]),
        "clause_count": int(rung["clauses"]),
        "min_width": int(rung["min_width"]),
        "max_width": int(rung["max_width"]),
        "cap_exponent": int(cap_exponent),
        "limit": int(rung["connected_limit"]),
    }
    observed = report["search_space"]
    for key, value in expected.items():
        if observed.get(key) != value:
            raise AssertionError(f"PREREGISTRATION_DRIFT:{rung['id']}:{key}:{observed.get(key)}!={value}")
    return report


def main() -> int:
    prereg = json.loads(PREREG.read_text())
    if prereg.get("schema") != "JANUS/C025/OPEN3-STAGE4-SCALING-LADDER-PREREGISTRATION/v1":
        raise AssertionError("PREREGISTRATION_SCHEMA_DRIFT")
    if prereg.get("P_VS_NP") != "OPEN":
        raise AssertionError("ILLEGAL_P_VS_NP_PROMOTION_IN_PREREGISTRATION")
    frozen = prereg["frozen_stage4_grammar"]
    if frozen.get("grammar_change_during_ladder") is not False:
        raise AssertionError("STAGE4_GRAMMAR_NOT_FROZEN")
    if prereg.get("stopping_rule") != "STOP_ONLY_IF_FIRST_STAGE4_BARRIER_IS_FOUND; OTHERWISE_EXECUTE_ALL_PREREGISTERED_RUNGS":
        raise AssertionError("STOPPING_RULE_DRIFT")

    cap_exponent = int(frozen["cap_exponent"])
    rung_reports = []
    first_open3 = None
    first_barrier = None

    for rung in prereg["rungs"]:
        report = run_rung(rung, cap_exponent)
        record = {
            "id": rung["id"],
            "search_space": report["search_space"],
            "totals": report["totals"],
            "status": report["status"],
            "first_open3": report.get("first_open3"),
            "first_barrier": report.get("first_barrier"),
        }
        rung_reports.append(record)
        if first_open3 is None and report.get("first_open3") is not None:
            first_open3 = {"rung": rung["id"], **report["first_open3"]}
        if report.get("first_barrier") is not None:
            first_barrier = {"rung": rung["id"], **report["first_barrier"]}
            break

    total_open3 = sum(int(row["totals"]["open3"]) for row in rung_reports)
    total_stage4_progress = sum(int(row["totals"]["stage4_progress"]) for row in rung_reports)
    total_open_after_stage4 = sum(int(row["totals"]["open_after_stage4"]) for row in rung_reports)

    if first_barrier is not None:
        status = "FINITE_OPEN3_COUNTEREXAMPLE_TO_CURRENT_STAGE4_GRAMMAR_FOUND"
    elif total_open3 > 0:
        status = "NONVACUOUS_OPEN3_COVERAGE__NO_STAGE4_BARRIER_IN_EXECUTED_PREREGISTERED_RUNGS"
    else:
        status = "PREREGISTERED_LADDER_EXECUTED_WITH_ZERO_OPEN3"

    output = {
        "schema": "JANUS/C025/OPEN3-STAGE4-SCALING-LADDER-RESULT/v1",
        "status": status,
        "preregistration_path": str(PREREG.relative_to(ROOT)),
        "frozen_stage4_grammar": frozen,
        "executed_rungs": rung_reports,
        "aggregate": {
            "rungs_executed": len(rung_reports),
            "open3": total_open3,
            "stage4_progress": total_stage4_progress,
            "open_after_stage4": total_open_after_stage4,
        },
        "first_open3": first_open3,
        "first_barrier": first_barrier,
        "scientific_boundary": {
            "bounded_preregistered_probe_only": True,
            "absence_of_barrier_is_not_totality_proof": True,
            "stage4_grammar_changed_during_ladder": False,
            "recursive_shannon_depth_increased": False,
            "universal_stage4_totality": "OPEN",
            "arbitrary_CNF": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
