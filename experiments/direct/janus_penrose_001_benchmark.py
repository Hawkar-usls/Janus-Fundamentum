#!/usr/bin/env python3
"""JANUS-PENROSE-001: reproducible global schedule consistency witness.

No impossible geometry implies a SAT speedup. We use a deliberately
contradictory positive-ascent cycle as a negative control on the separate
strict event-dependency graph for Deutsch-003 reversible operations.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import time

from janus_deutsch_002 import DirectOracle
from janus_deutsch_003 import choose_block_size
from janus_penrose_001 import audit_reversible_schedule, penrose_staircase_negative_control
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES


def build_report():
    cnf, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    direct = DirectOracle.compile(cnf, n, "SAT")
    blocked = choose_block_size(direct)
    started = time.perf_counter()
    audit = audit_reversible_schedule(blocked)
    seconds = time.perf_counter() - started
    if not audit.passed:
        raise AssertionError("real reversible schedule rejected")
    negative = penrose_staircase_negative_control()
    if negative.consistent:
        raise AssertionError("Penrose-style positive cycle incorrectly accepted")
    extra = ((f"event:{audit.events - 1}", "event:0"),)
    injected = audit_reversible_schedule(
        blocked, hostile_extra_dependencies=extra)
    if injected.passed or injected.strict_event_schedule.consistent:
        raise AssertionError("hostile loop incorrectly accepted")
    rng = random.Random(1958)
    samples = [0, (1 << n)-1] + [rng.getrandbits(n) for _ in range(128)]
    if any(direct.evaluate(x) != blocked.evaluate(x) for x in samples):
        raise AssertionError("block pebbling changed SAT evaluations")
    base = direct.resources()
    new = blocked.resources()
    return {
        "schema": "JANUS-PENROSE-001-GLOBAL-CONSISTENCY-V1",
        "utc": datetime.now(timezone.utc).isoformat(),
        "source": {"run_id": os.getenv("GITHUB_RUN_ID", "local"),
                   "sha": os.getenv("GITHUB_SHA", "local")},
        "status": "NEGATIVE_CYCLE_REJECTED_REVERSIBLE_SCHEDULE_ACCEPTED",
        "conceptual_source": {
            "work": "Penrose and Penrose, Impossible Objects, 1958",
            "doi": "10.1111/j.2044-8295.1958.tb00634.x",
            "interpretation": "Analogy only: local +1 rises around a closed strict precedence graph are globally impossible"
        },
        "strict_staircase": negative.as_dict(),
        "real_maj3_event_schedule": {
            "accepted": audit.passed,
            "logical_event_count": audit.events,
            "strict_dependency_count": audit.strict_event_schedule.constraint_count,
            "rank_end": max(level for _, level in audit.strict_event_schedule.ranks),
            "forward_uncompute_symmetry_pass": audit.forward_reverse_equal,
            "schedule_audit_wall_seconds": seconds,
            "injected_impossible_dependency_rejected": not injected.passed,
            "injected_cycle_witness_length":
                len(injected.strict_event_schedule.cycle_witness),
        },
        "resource_comparison": {
            "deutsch_002_ancillas_and_decomposition_qubits":
                base["qubit_count_with_clean_decomposition_estimate"],
            "deutsch_003_ancillas_and_decomposition_qubits":
                new["qubit_count_with_clean_decomposition_estimate"],
            "original_max_controls": base["max_controlled_x_controls"],
            "blocked_max_controls": new["max_controlled_x_controls"],
            "original_toffolis": base["toffoli_count_clean_decomposition_estimate"],
            "blocked_toffolis": new["toffoli_count_clean_decomposition_estimate"],
        },
        "sampled_sat_agreement": {
            "checked": len(samples),
            "all_matched": True,
            "not_exhaustive_and_no_unsat_proof": True,
        },
        "scientific_limits": [
            "Impossible visual staircases are an analogy for inconsistency, not quantum hardware",
            "Legitimate compute/uncompute reuses register values; only strict event dependencies must be acyclic",
            "Schedule potential is linear-time validation, not a new SAT-solving method",
            "No physical quantum advantage or P=NP conclusion",
            "Core C023 main remains unchanged; research branch PR #574 stays draft"
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    report = build_report()
    payload = json.dumps(report, indent=2) + "\n"
    if args.out:
        file = Path(args.out)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(payload, encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
