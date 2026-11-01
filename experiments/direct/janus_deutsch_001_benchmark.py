#!/usr/bin/env python3
"""JANUS-DEUTSCH-001 finite benchmark versus classical brute force and C023/UFR.

No hardware. Classical statevector and ANF synthesis are charged in full.
Use exactly the same SAT/Exact-One logical constraints on both paths.
Small timing samples are *illustrative*, not a statistical speedup claim.
"""
from __future__ import annotations

from itertools import combinations
import argparse
import os
import json
import math
from pathlib import Path
import random
import statistics
import sys
import time
import tracemalloc

from janus_deutsch_001 import Circuit, evaluate, grover_simulate
from janus_tear_policy0a_masked_tseitin import canonical_cnf
from janus_ufr_001_adversarial import run_case

REPEATS = 5


def experiments():
    yield "SAT_UNIQUE_3", ((1,), (-2,), (3,)), 3, "SAT"
    yield "SAT_UNSAT_3", ((1,), (-1,)), 3, "SAT"
    yield "SAT_BALANCED_3", ((1,),), 3, "SAT"
    yield "EXACT_ONE_3", ((1, 2, 3),), 3, "EXACT_ONE"
    rng = random.Random(173)
    rows = []
    for _ in range(20):
        choices = rng.sample(range(1, 7), 3)
        rows.append(tuple(v if rng.randrange(2) else -v for v in choices))
    yield "INDEPENDENT_3SAT_6_SEED173", tuple(rows), 6, "SAT"
    rng = random.Random(271)
    rows = []
    for _ in range(8):
        vs = rng.sample(range(1, 6), 3)
        rows.append(tuple(v if rng.randrange(2) else -v for v in vs))
    yield "INDEPENDENT_EXACT_ONE_5_SEED271", tuple(rows), 5, "EXACT_ONE"


def exact_one_to_cnf(rows):
    clauses = []
    for row in rows:
        # Exactly one = at least one AND all pairwise at most one.
        # Duplicate literals are intentionally retained in source semantics.
        clauses.append(row)
        clauses.extend((-a, -b) for a, b in combinations(row, 2))
    return canonical_cnf(clauses)


def classical_enumerate(rows, n, kind):
    calls = 0
    candidate = None
    for x in range(1 << n):
        calls += 1
        if evaluate(rows, x, kind):
            candidate = x
            break
    return candidate, calls


def measure_classical(rows, n, kind):
    times = []
    calls = []
    candidates = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        candidate, checked = classical_enumerate(rows, n, kind)
        times.append(time.perf_counter() - start)
        calls.append(checked)
        candidates.append(candidate)
    assert len(set(calls)) == len(set(candidates)) == 1
    return {"candidate": candidates[0], "evaluations": calls[0],
            "median_wall_seconds": statistics.median(times),
            "timing_repeats": REPEATS}


def measure_quantum(rows, n, kind):
    measurements = []
    for _ in range(REPEATS):
        tracemalloc.start()
        start = time.perf_counter()
        circuit = Circuit.build(rows, n, kind)
        good = circuit.check_reversible()
        grover = grover_simulate(circuit)
        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        assert good
        measurements.append((elapsed, peak))
    return {
        "median_wall_seconds": statistics.median(x[0] for x in measurements),
        "peak_tracemalloc_bytes": max(x[1] for x in measurements),
        "oracle_basis_evaluations": grover.oracle_basis_evaluations,
        "multi_controlled_x_gate_count": len(circuit.gates),
        "total_gate_controls": circuit.total_controls,
        "synthesized_gate_applications": grover.synthesized_gate_applications,
        "statevector_amplitudes": grover.statevector_amplitudes,
        "classical_bits_per_statevector_lower_bound": 16 * (1 << n),
        "iterations": grover.iterations,
        "solution_count_known_by_full_classical_scan": grover.solutions,
        "ideal_success_probability": grover.success_probability,
        "best_candidate": grover.best_candidate,
        "best_candidate_classically_verified": grover.best_candidate_validated,
        "timing_repeats": REPEATS,
        "hardware": False,
    }


def run():
    records = []
    for name, rows, n, kind in experiments():
        classic = measure_classical(rows, n, kind)
        simulator = measure_quantum(rows, n, kind)
        cnf = canonical_cnf(rows) if kind == "SAT" else exact_one_to_cnf(rows)
        old = run_case(cnf, n, "EXACT_C023", 3000)
        ufr = run_case(cnf, n, "CERTIFIED_UFR_C023", 3000)
        truth = classic["candidate"] is not None
        assert old["answer"] is truth and ufr["answer"] is truth
        assert (simulator["solution_count_known_by_full_classical_scan"] > 0) is truth
        if simulator["best_candidate_classically_verified"]:
            assert simulator["best_candidate"] is not None
            assert evaluate(rows, simulator["best_candidate"], kind)
        records.append({
            "name": name, "n": n, "kind": kind,
            "classical_exhaustive": classic,
            "deutsch_classical_simulator": simulator,
            "c023": old, "ufr_c023": ufr,
            "classical_simulator_over_bruteforce_time_ratio": (
                simulator["median_wall_seconds"] / classic["median_wall_seconds"]),
            "logical_answers_match": True,
        })
    out = {
        "schema": "JANUS-DEUTSCH-001-FINITE-V1",
        "source": {"git_sha": os.getenv("GITHUB_SHA", "local"), "run_id": os.getenv("GITHUB_RUN_ID", "local"), "runner": os.getenv("RUNNER_NAME", "local")},
        "status": "FINITE_CLASSICAL_SIMULATOR_NO_QUANTUM_SPEEDUP_CLAIM",
        "comparison": "Same six tiny instances, baseline classical enumeration, C023, UFR-C023, and classical statevector simulator",
        "previous_large_instance": {
            "benchmark": "MAJ3-K4 (n=18)",
            "prior_ufr_iso_hits": 165,
            "prior_ufr_unique_states": 2354,
            "prior_c023_unique_states": 2427,
            "last_independent_gate": "NOT_READY",
            "source_url": "https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/41292188688",
            "direct_quantum_comparison": "NOT_RUN: capped classical statevector simulator n<=8, different workloads",
        },
        "limitations": [
            "Oracle is ANF synthesized from a complete classical truth table",
            "Classical simulator pays full memory and full lookup/evaluation costs",
            "Grover iteration count assumes M known from complete classical enumeration",
            "Multi-controlled-X gate count is not decomposed fault-tolerant hardware cost",
            "Deutsch-Jozsa tests only constant/balanced promise functions",
            "Tiny timing differences are noisy; no statistical significance implied",
            "Quantum SAT superposition does not certify UNSAT",
            "C023 root-affine cases may lack a serialized decision replay",
            "P vs NP unaffected",
        ],
        "fixtures": records,
    }
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="")
    args = parser.parse_args()
    report = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.out:
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    run()
