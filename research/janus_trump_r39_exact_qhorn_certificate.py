#!/usr/bin/env python3
"""R39 exact q-Horn certificate checker for the sealed R38 fixpoint.

The q-Horn characterization used here is:
  for each clause C,
  sum_{positive x_j in C} alpha_j
  + sum_{negative ~x_j in C} (1-alpha_j) <= 1,
  with 0 <= alpha_j <= 1.

A NOT-q-Horn result is accepted only from an exact Farkas certificate:
nonnegative multipliers whose weighted LHS coefficient vector is exactly zero
and whose weighted RHS is strictly negative.

No floating-point status is authoritative.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path

EXPECTED_FORMULA_SHA256 = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
FARKAS_CLAUSE_INDICES = [8, 14, 17, 23, 27, 41]
FARKAS_WEIGHTS = [Fraction(1) for _ in FARKAS_CLAUSE_INDICES]


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def formula_hash(clauses):
    return hashlib.sha256(canonical_bytes(clauses)).hexdigest()


def qhorn_inequality(clause, variables):
    """Return exact A,b for A alpha <= b."""
    pos = {v: i for i, v in enumerate(variables)}
    row = [Fraction(0) for _ in variables]
    negative_count = 0
    for lit in clause:
        if lit > 0:
            row[pos[lit]] += 1
        else:
            row[pos[-lit]] -= 1
            negative_count += 1
    rhs = Fraction(1 - negative_count)
    return row, rhs


def add_scaled(acc, row, weight):
    for i, value in enumerate(row):
        acc[i] += weight * value


def verify_farkas(clauses):
    variables = sorted({abs(lit) for clause in clauses for lit in clause})
    lhs = [Fraction(0) for _ in variables]
    rhs = Fraction(0)
    expanded = []

    for one_based, weight in zip(FARKAS_CLAUSE_INDICES, FARKAS_WEIGHTS):
        if weight < 0:
            raise AssertionError("NEGATIVE_FARKAS_WEIGHT")
        clause = clauses[one_based - 1]
        row, bound = qhorn_inequality(clause, variables)
        add_scaled(lhs, row, weight)
        rhs += weight * bound
        expanded.append({
            "clause_index": one_based,
            "clause": clause,
            "weight": str(weight),
            "rhs": str(bound),
        })

    if any(value != 0 for value in lhs):
        raise AssertionError(f"FARKAS_LHS_NOT_ZERO: {lhs}")
    if not rhs < 0:
        raise AssertionError(f"FARKAS_RHS_NOT_NEGATIVE: {rhs}")

    return {
        "variables": variables,
        "certificate_clause_indices": FARKAS_CLAUSE_INDICES,
        "certificate": expanded,
        "weighted_lhs_coefficients": [str(v) for v in lhs],
        "weighted_rhs": str(rhs),
        "derived_contradiction": f"0 <= {rhs}",
        "recognized_q_horn": False,
        "verdict": "R39_QHORN_REJECTED_WITH_EXACT_FARKAS_CERTIFICATE",
    }


def main():
    root = Path(__file__).resolve().parents[1]
    input_path = root / "research" / "JANUS_TRUMP_R39_QHORN_SEALED_INPUT_2026-09-03.json"
    data = json.loads(input_path.read_text(encoding="utf-8"))
    clauses = data["clauses"]

    got = formula_hash(clauses)
    if got != EXPECTED_FORMULA_SHA256 or got != data["canonical_formula_sha256"]:
        raise AssertionError(f"FROZEN_FORMULA_HASH_MISMATCH: {got}")

    result = verify_farkas(clauses)
    result.update({
        "schema": "JANUS_TRUMP_R39_EXACT_QHORN_CERTIFICATE_CHECK_RESULT",
        "version": "1.0",
        "canonical_formula_sha256": got,
        "certificate_type": "EXACT_RATIONAL_FARKAS",
        "numeric_solver_authority": False,
        "assignment_enumeration_used": False,
        "external_sat_solver_used": False,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    })
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
