#!/usr/bin/env python3
"""Deutsch-003: measured reversible block-pebbling resources, not a quantum speedup.

Compare identical MAJ3-K4 CNF and predecessor Deutsch-002, including
end-to-end gate-schedule materialization and sampled clean-basis evaluation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import statistics
import time
import tracemalloc

from janus_deutsch_002 import DirectOracle
from janus_deutsch_003 import BlockOracle, choose_block_size
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_ufr_001 import verify_model


def measure(fn, repetitions=3):
    times, peaks = [], []
    result = None
    for _ in range(repetitions):
        tracemalloc.start()
        begin = time.perf_counter()
        result = fn()
        times.append(time.perf_counter() - begin)
        peaks.append(tracemalloc.get_traced_memory()[1])
        tracemalloc.stop()
    return result, {"median_seconds": statistics.median(times),
                    "max_python_tracemalloc_bytes": max(peaks),
                    "repetitions": repetitions}


def test_instance(rows, n, kind, samples):
    direct, compile002 = measure(lambda: DirectOracle.compile(rows, n, kind))
    optimized, select003 = measure(lambda: choose_block_size(direct))
    schedule, materialize003 = measure(lambda: tuple(optimized.iter_instructions()))
    if len(schedule) != optimized.logical_mcx_gates:
        raise AssertionError("emitted schedule length differs from resource count")
    controls = []
    for bs in (1, 2, 4, 8, 16, 24, 32, 40, 64, 128, 256, 512, 1024):
        if bs <= max(1, direct.work_qubits):
            cand = BlockOracle.from_direct(direct, block_size=bs)
            controls.append({
                "block_size": bs,
                "block_count": cand.blocks,
                "qubits": cand.qubit_estimate,
                "maximum_controls": cand.maximum_controls,
                "estimated_toffolis": cand.estimated_toffolis,
                "logical_mcx": cand.logical_mcx_gates,
            })
    rng = random.Random(20261101)
    indices = [0, (1 << n) - 1] + [rng.getrandbits(n) for _ in range(samples)]
    evaluations_original, orig_time = measure(
        lambda: [direct.evaluate(x) for x in indices], 2)
    evaluations_opt, opt_time = measure(
        lambda: [optimized.evaluate(x) for x in indices], 2)
    if evaluations_opt != evaluations_original:
        raise AssertionError("Deutsch-003 differs from direct CNF oracle")
    for x, answer in zip(indices, evaluations_opt):
        assign = {v: bool(x & (1 << (v - 1))) for v in range(1, n+1)}
        if answer != verify_model(rows, assign, kind):
            raise AssertionError("independent SAT/Exact-One predicate disagreed")
    return {
        "n": n, "kind": kind,
        "number_of_clauses": len(rows),
        "checked_assignments": len(indices),
        "independently_verified_all_samples": True,
        "deutsch_002_direct_compile": compile002,
        "deutsch_002_resource_model": direct.resources(),
        "deutsch_002_sample_evaluation": orig_time,
        "deutsch_003_optimizer_selection": select003,
        "deutsch_003_schedule_emission": materialize003,
        "deutsch_003_sample_evaluation": opt_time,
        "deutsch_003_resource_model": optimized.resources(),
        "qubit_reduction_fraction": 1.0 - optimized.qubit_estimate /
                                   direct.all_qubits_with_clean_decomposition,
        "max_control_reduction_fraction": 1.0 - optimized.maximum_controls /
                                          max(1, direct.work_qubits,
                                              direct.encoded_max_width),
        "toffoli_ratio": optimized.estimated_toffolis /
                         max(1, direct.estimated_toffoli_count),
        "schedule_gate_ratio": optimized.logical_mcx_gates /
                               max(1, direct.logical_mcx_gates),
        "sample_cpu_evaluation_ratio": opt_time["median_seconds"] /
                                       orig_time["median_seconds"],
        "architecture_variants": controls,
        "limits": [
            "Both methods are classical simulations of idealized reversible gates",
            "The work+summary registers must begin clean; all are returned to their original state",
            "Generated SAT schedule is not a physical gate compilation with connectivity/fault tolerance",
            "The C023 UNSAT certificate was NOT reproduced by sampling",
            "No quantum statevector simulated for n>8",
            "Synthetic sample throughput is not a quantum hardware runtime",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    rows, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    maj = test_instance(rows, n, "SAT", samples=512)
    exact = test_instance(((1, 2, 3), (1, -2), (-1, 3)), 3, "EXACT_ONE", samples=64)
    out = {
        "schema": "JANUS-DEUTSCH-003-BLOCK-PEBBLE-V1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"sha": os.getenv("GITHUB_SHA", "local"),
                   "run_id": os.getenv("GITHUB_RUN_ID", "local"),
                   "runner_name": os.getenv("RUNNER_NAME", "local")},
        "status": "FINITE_REVERSIBLE_RESOURCE_TRADEOFF_NOT_QUANTUM_SPEEDUP",
        "maJ3_k4": maj,
        "exact_one_control": exact,
        "prior_verified_baseline": {
            "deutsch_002_cloud_run": 41295480672,
            "deutsch_002_maj3_k4_compile_median_seconds": 0.02124068,
            "C023_unique_states": 2427,
            "UFR_unique_states": 2354,
            "UFR_iso_hits": 165,
            "C023_vs_UFR_promotion": "NOT_READY",
            "deutsch_003_changes_C023": False,
        },
        "scientific_claim_boundary": [
            "Uses clause-structured reversible circuit, not ANF full truth table",
            "Block pebbling lowers qubit and max-control estimates by recomputation",
            "Increasing logical gate count/Toffolis is an explicit counter-cost",
            "Time and memory are Python execution artifacts, not device execution",
            "No quantum advantage, no general SAT speedup, no P=NP claim",
            "Original C023 remains canonical; experiment PR stays draft",
        ],
    }
    report = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.out:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
