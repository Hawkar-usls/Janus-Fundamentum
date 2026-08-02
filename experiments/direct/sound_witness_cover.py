#!/usr/bin/env python3
"""Audit the universal witness-cover circuit attacking H116.

Given a positive list (F_i, a_i), collect the distinct assignments A.  The
predicate

    C_A(G) = OR_{a in A} [a satisfies G]

is SAT-sound and accepts every listed formula.  A standard fixed-shape CNF
evaluator gives a circuit of size O(|A| * EvalCost).  Therefore a positive-only
sound-circuit anti-checker must explicitly exceed this witness-cover budget.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


Assignment = tuple[bool, ...]


def satisfies(cnf: CNF, assignment: Assignment) -> bool:
    if len(assignment) != cnf.variable_count:
        raise ValueError("assignment length mismatch")
    return all(
        any(assignment[abs(literal) - 1] == (literal > 0) for literal in clause)
        for clause in cnf.clauses
    )


def witness_cover_accepts(cnf: CNF, assignments: set[Assignment]) -> bool:
    return any(satisfies(cnf, assignment) for assignment in assignments)


def verify_positive_list(entries: list[tuple[CNF, Assignment]]) -> set[Assignment]:
    if not entries:
        raise ValueError("positive list must be nonempty")
    variable_count = entries[0][0].variable_count
    witnesses: set[Assignment] = set()
    for cnf, assignment in entries:
        if cnf.variable_count != variable_count:
            raise ValueError("all formulas must use the same padded input shape")
        if not satisfies(cnf, assignment):
            raise ValueError("listed witness does not satisfy its formula")
        witnesses.add(assignment)
    return witnesses


def straightforward_gate_bound(
    distinct_witnesses: int,
    clause_count: int,
    width: int,
) -> int:
    if min(distinct_witnesses, clause_count, width) < 1:
        raise ValueError("positive shape parameters required")
    # For each fixed assignment: one literal-selection gate per slot, OR inside
    # every clause, AND across clauses; then OR across witnesses.  Constants are
    # intentionally generous because only an explicit polynomial upper bound is
    # needed for the obstruction.
    evaluator = clause_count * (3 * width + 2) + clause_count
    return distinct_witnesses * evaluator + max(0, distinct_witnesses - 1)


def self_test() -> None:
    zero = (False, False, False)
    one = (True, True, True)
    entries = [
        (CNF(3, ((-1,), (-2, 3))), zero),
        (CNF(3, ((1,), (2, 3))), one),
        (CNF(3, ((-1, -2), (3, -3))), zero),
        (CNF(3, ((1, 2), (-3, 3))), one),
    ]
    witnesses = verify_positive_list(entries)
    assert len(witnesses) == 2
    assert all(witness_cover_accepts(cnf, witnesses) for cnf, _ in entries)

    contradiction = CNF(3, ((1,), (-1,)))
    assert not witness_cover_accepts(contradiction, witnesses)

    bound = straightforward_gate_bound(
        distinct_witnesses=len(witnesses), clause_count=2, width=2
    )
    assert bound > 0

    print("JANUS_SOUND_WITNESS_COVER = PASS")
    print(f"POSITIVE_FORMULAS = {len(entries)}")
    print(f"DISTINCT_WITNESSES = {len(witnesses)}")
    print("COVER_ACCEPTS_ALL_LISTED_FORMULAS = true")
    print("COVER_REJECTS_FIXED_CONTRADICTION = true")
    print(f"STRAIGHTFORWARD_GATE_BOUND = {bound}")
    print("CLAIM_BOUNDARY = finite audit; asymptotic theorem is in proof artifact")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    parser.error("only --self-test is supported")


if __name__ == "__main__":
    raise SystemExit(main())
