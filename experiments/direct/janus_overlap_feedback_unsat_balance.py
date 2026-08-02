#!/usr/bin/env python3
"""Balanced SAT/UNSAT companion for C021 feedback reduction."""

from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

import janus_overlap_feedback_barrier as c021


def planted_sat_3cnf(
    rng: random.Random,
    n_vars: int,
    n_clauses: int,
) -> tuple[c021.CNF, dict[int, bool]]:
    planted = {v: bool(rng.getrandbits(1)) for v in range(1, n_vars + 1)}
    clauses: list[c021.Clause] = []
    for _ in range(n_clauses):
        chosen = rng.sample(range(1, n_vars + 1), 3)
        lits = [v if rng.random() < 0.5 else -v for v in chosen]
        if not any(planted[abs(lit)] == (lit > 0) for lit in lits):
            v = chosen[0]
            lits[0] = v if planted[v] else -v
        clauses.append(c021.canonical_clause(lits))
    formula = c021.canonical_cnf(clauses)
    assert c021.satisfies(formula, planted)
    return formula, planted


def complete_unsat_3core() -> c021.CNF:
    clauses = []
    for bits in itertools.product([False, True], repeat=3):
        clauses.append(
            c021.canonical_clause(
                (i + 1) if not bits[i] else -(i + 1)
                for i in range(3)
            )
        )
    formula = c021.canonical_cnf(clauses)
    truth, _, _ = c021.brute_force(formula)
    assert not truth
    return formula


def run(seed: int = c021.DEFAULT_SEED, cases: int = 140) -> dict:
    rng = random.Random(seed ^ 0xC021)
    core = complete_unsat_3core()

    sat_count = 0
    unsat_count = 0
    structural_failures = 0
    witness_failures = 0
    equivalence_failures = 0

    for case_index in range(cases):
        n = rng.randint(3, 7)
        if case_index % 2 == 0:
            formula, planted = planted_sat_3cnf(rng, n, rng.randint(3, 10))
            expected_truth = True
            expected_witness = planted
        else:
            noise, _ = planted_sat_3cnf(rng, n, rng.randint(1, 5))
            formula = c021.canonical_cnf(noise + core)
            expected_truth = False
            expected_witness = None

        truth, exact_witness, _ = c021.brute_force(formula)
        assert truth == expected_truth

        circuit, metadata = c021.encode_feedback_circuit(formula)
        if not c021.verify_feedback_reduction_structure(formula, circuit, metadata):
            structural_failures += 1

        if truth:
            sat_count += 1
            witness = exact_witness or expected_witness
            assert witness is not None
            extended = c021.extend_circuit_witness(formula, metadata, witness)
            if extended is None or not c021.satisfies(circuit, extended):
                witness_failures += 1
        else:
            unsat_count += 1

        for bits in itertools.product([False, True], repeat=n):
            assignment = dict(zip(range(1, n + 1), bits))
            expected = c021.satisfies(formula, assignment)
            extended = c021.extend_circuit_witness(formula, metadata, assignment)
            obtained = extended is not None and c021.satisfies(circuit, extended)
            if expected != obtained:
                equivalence_failures += 1
                break

    assertions = {
        "balanced": sat_count == cases // 2 and unsat_count == cases // 2,
        "structure": structural_failures == 0,
        "witnesses": witness_failures == 0,
        "equivalence": equivalence_failures == 0,
    }
    return {
        "artifact_id": "C021-JANUS-FEEDBACK-BALANCED-COMPANION",
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "software_only": True,
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "structural_failures": structural_failures,
        "witness_failures": witness_failures,
        "assignment_equivalence_failures": equivalence_failures,
        "assertions": assertions,
        "verdict": (
            "The linear feedback encoding preserves SAT and UNSAT on a balanced "
            "suite. A general polynomial solver for this constrained nonlinear "
            "feedback class would solve arbitrary 3-SAT."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=c021.DEFAULT_SEED)
    parser.add_argument("--cases", type=int, default=140)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run(args.seed, args.cases)
    if args.output:
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
