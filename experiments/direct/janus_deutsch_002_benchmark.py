#!/usr/bin/env python3
"""Deutsch-002 reproducible structural-vs-truth-table oracle and C023 comparison.

No quantum hardware. Honest staged accounting separates:
  compilation (old ANF requires 2^n table, D002 does not),
  classical gate/phase simulation (still evaluates 2^n amplitudes),
  direct brute-force SAT/Exact-One, and
  independent C023/UFR proof performance from a separately pinned large run.
MAJ3-K4 n=18 is *compiled and sampled*, not statevector-simulated.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
import statistics
import sys
import time
import tracemalloc

from janus_deutsch_001 import Circuit
from janus_deutsch_001_benchmark import experiments, classical_enumerate
from janus_deutsch_002 import DirectOracle, grover_statevector
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_ufr_001 import verify_model

REPEATS = 5


def measure(construct, repetitions=REPEATS):
    samples = []
    value = None
    for _ in range(repetitions):
        tracemalloc.start()
        begun = time.perf_counter()
        value = construct()
        elapsed = time.perf_counter() - begun
        _, allocated_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        samples.append((elapsed, allocated_peak))
    return value, {"median_seconds": statistics.median(t for t, _ in samples),
                   "maximum_python_allocations_bytes": max(p for _, p in samples),
                   "repetitions": repetitions}


def original_truth(rows, index, kind):
    assignment = {
        v: bool(index & (1 << (v - 1)))
        for v in range(1, max((abs(lit) for row in rows for lit in row),
                               default=0) + 1)
    }
    return verify_model(rows, assignment, kind)


def small_cases():
    outputs = []
    for name, rows, n, kind in experiments():
        structural, direct_cost = measure(
            lambda: DirectOracle.compile(rows, n, kind))
        old, prior_cost = measure(lambda: Circuit.build(rows, n, kind))
        if not all(structural.evaluate(x) == bool(old.table[x]) ==
                   original_truth(rows, x, kind)
                   for x in range(1 << n)):
            raise AssertionError(f"{name}: SAT/Exact-One oracle mismatch")
        old_valid = old.check_reversible()
        if not old_valid:
            raise AssertionError(f"{name}: old ANF reversibility error")
        brute, brute_cost = measure(lambda: classical_enumerate(rows, n, kind))
        sim, simulation_cost = measure(lambda: grover_statevector(structural))
        if bool(sim.solutions) != (brute[0] is not None):
            raise AssertionError(f"{name}: simulated and brute-force disagreement")
        if sim.candidate_verified and not original_truth(rows, sim.candidate, kind):
            raise AssertionError(f"{name}: invalid candidate")
        outputs.append({
            "name": name, "variables": n, "kind": kind,
            "answer": bool(sim.solutions),
            "solutions_counted_with_complete_classical_scan": sim.solutions,
            "original_truth_table_anf_compile": prior_cost,
            "direct_clause_compile": direct_cost,
            "direct_compile_over_anf_median_ratio": (
                direct_cost["median_seconds"] / prior_cost["median_seconds"]),
            "classical_bruteforce_with_early_exit": {
                **brute_cost, "evaluations_in_early_exit": brute[1]},
            "direct_oracle_plus_classical_grover": {
                **simulation_cost,
                "ideal_success_probability": sim.success_probability,
                "iterations": sim.iterations,
                "basis_predicate_evaluations": sim.basis_predicate_evaluations,
                "clause_gate_condition_evaluations": sim.gate_condition_evaluations,
                "candidate_verified": sim.candidate_verified,
            },
            "compiled_resource_counts": structural.resources(),
            "truth_agreement_checked_assignments": 1 << n,
        })
    return outputs


def maj3_case():
    rows, n = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    # Resource synthesis only: no 2^18-wide statevector, no exhaustive scan.
    oracle, compile_cost = measure(lambda: DirectOracle.compile(rows, n, "SAT"), 3)
    rng = random.Random(20261101)
    inputs = [0, (1 << n) - 1] + [rng.getrandbits(n) for _ in range(512)]
    start = time.perf_counter()
    hits = 0
    for index in inputs:
        actual = oracle.apply_basis(index, 0)[1]
        independently_expected = original_truth(rows, index, "SAT")
        if actual != int(independently_expected):
            raise AssertionError(f"MAJ3-K4 mismatch for x={index}")
        hits += 1
    sample_cost = time.perf_counter() - start
    return {
        "name": "MAJ3_K4", "variables": n, "input_cnf_clauses": len(rows),
        "direct_compilation": compile_cost,
        "resource_estimate": oracle.resources(),
        "checked_assignments": hits,
        "checked_truth_agreement": True,
        "sample_verification_seconds": sample_cost,
        "complete_truth_table_constructed": False,
        "classical_statevector_simulated": False,
        "unsat_status_from_samples": "NOT_PROVEN_BY_SAMPLING",
        "historical_independent_c023_unsat": {
            "source": "https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41292188688",
            "C023_states": 2427, "UFR_states": 2354,
            "UFR_isomorphic_cache_hits": 165, "gate": "NOT_READY",
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    small = small_cases()
    big = maj3_case()
    report = {
        "schema": "JANUS-DEUTSCH-002-STRUCTURAL-V1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": {"github_sha": os.getenv("GITHUB_SHA", "local"),
                   "github_run_id": os.getenv("GITHUB_RUN_ID", "local"),
                   "runner_name": os.getenv("RUNNER_NAME", "local")},
        "claim_status": "FINITE_BASIS_TESTS_AND_STRUCTURAL_RESOURCE_ESTIMATES_ONLY",
        "small_cases": small,
        "maj3_k4": big,
        "methodology": [
            "Direct clause compilation O(total encoded literals) after Exact-One O(sum row-width^2) pairwise encoding",
            "No truth table needed for D002 compilation, but the classical statevector simulator still uses 2^n input amplitudes",
            "Small cases compare direct compilation versus original fully enumerating ANF compilation on SAME input",
            "Five tiny repetitions timed sequentially; ratios noisy and not proof of speedup",
            "Large 18-input-variable MAJ3-K4 compiles without 2^18 truth table; 514 samples do NOT establish UNSAT",
            "High-control logical X gates require additional decomposition; resource-estimation gate counts are not physical execution costs",
            "Sampled SAT candidates require independent classical verification; no UNSAT oracle guarantee",
            "No legitimate claim of general polynomial-time SAT or P=NP",
            "Core C023 stays unchanged, UFR PR #574 remains draft pending separate 2-worker performance gate",
        ],
    }
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(payload)
    if args.out:
        file = Path(args.out)
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    main()
