#!/usr/bin/env python3
"""Attack the strong JANUS Tear quotient conjecture.

For E_n(X,Y) = AND_i (x_i <-> y_i), assign every X bit. The 2^n
residual formulas over Y are pairwise distinguishable by continuations:
residual a accepts Y=a and rejects Y=b for every b != a.

Therefore any tear equivalence that preserves the complete continuation
language of every residual state requires at least 2^n classes, despite
|E_n| = O(n).

This does not prove P != NP. It refutes only the strong claim that every
formula's entire residual-state space admits a polynomial-size,
continuation-complete tear quotient.
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from typing import Iterable

Clause = tuple[int, ...]
Formula = tuple[Clause, ...]
Bits = tuple[int, ...]


def equality_formula(n: int) -> Formula:
    if n < 1:
        raise ValueError("n must be positive")
    clauses: list[Clause] = []
    for i in range(n):
        x = i + 1
        y = n + i + 1
        clauses.append((-x, y))
        clauses.append((x, -y))
    return tuple(clauses)


def simplify(formula: Formula, assignment: dict[int, bool]) -> Formula | None:
    residual: list[Clause] = []
    for clause in formula:
        new_clause: list[int] = []
        satisfied = False
        for literal in clause:
            variable = abs(literal)
            value = assignment.get(variable)
            if value is None:
                new_clause.append(literal)
                continue
            literal_value = value if literal > 0 else not value
            if literal_value:
                satisfied = True
                break
        if satisfied:
            continue
        if not new_clause:
            return None
        residual.append(tuple(sorted(new_clause, key=lambda lit: (abs(lit), lit < 0))))
    return tuple(sorted(residual))


def residual_for_x(n: int, bits: Bits) -> Formula:
    formula = equality_formula(n)
    assignment = {i + 1: bool(bits[i]) for i in range(n)}
    residual = simplify(formula, assignment)
    assert residual is not None
    return residual


def satisfies(formula: Formula | None, assignment: dict[int, bool]) -> bool:
    if formula is None:
        return False
    for clause in formula:
        if not any(
            assignment[abs(literal)] if literal > 0 else not assignment[abs(literal)]
            for literal in clause
        ):
            return False
    return True


def y_assignment(n: int, bits: Bits) -> dict[int, bool]:
    return {n + i + 1: bool(bits[i]) for i in range(n)}


def all_bits(n: int) -> Iterable[Bits]:
    return product((0, 1), repeat=n)


def run_case(n: int, exhaustive_pair_check: bool = True) -> dict[str, object]:
    states = list(all_bits(n))
    residuals = {bits: residual_for_x(n, bits) for bits in states}

    distinct_residuals = len(set(residuals.values()))
    unique_witness_ok = all(
        satisfies(residuals[bits], y_assignment(n, bits)) for bits in states
    )

    pairwise_distinguishable = True
    checked_pairs = 0
    if exhaustive_pair_check:
        for left in states:
            continuation = y_assignment(n, left)
            for right in states:
                if left == right:
                    continue
                checked_pairs += 1
                if satisfies(residuals[right], continuation):
                    pairwise_distinguishable = False
                    break
            if not pairwise_distinguishable:
                break

    formula = equality_formula(n)
    encoded_literal_count = sum(len(clause) for clause in formula)

    return {
        "n": n,
        "formula_clause_count": len(formula),
        "formula_literal_count": encoded_literal_count,
        "residual_state_count": len(states),
        "distinct_canonical_residuals": distinct_residuals,
        "expected_exponential_count": 2**n,
        "every_residual_is_sat": unique_witness_ok,
        "pairwise_continuation_distinguishable": pairwise_distinguishable,
        "checked_ordered_pairs": checked_pairs,
        "lower_bound": (
            "Any tear signature whose equality guarantees identical acceptance "
            "for every future Y-continuation needs at least 2^n classes."
        ),
        "falsified_statement": (
            "Every CNF has only polynomially many continuation-complete tear "
            "classes across all partial assignments."
        ),
        "surviving_weaker_statement": (
            "A particular polynomial-time solver may visit only polynomially many "
            "policy-selected states; proving such a solver exists remains open and "
            "is essentially a P=NP construction."
        ),
        "claim_boundary": (
            "This is not a P!=NP proof. It rejects one overly strong universal "
            "quotient formulation using an explicit formula family in P."
        ),
    }


def self_test() -> None:
    for n in range(1, 9):
        result = run_case(n, exhaustive_pair_check=True)
        assert result["distinct_canonical_residuals"] == 2**n
        assert result["residual_state_count"] == 2**n
        assert result["every_residual_is_sat"] is True
        assert result["pairwise_continuation_distinguishable"] is True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=6)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        print("JANUS_TEAR_CONGRUENCE_EXPLOSION_SELF_TEST = PASS")
        return 0
    print(json.dumps(run_case(args.n), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
