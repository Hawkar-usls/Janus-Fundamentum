#!/usr/bin/env python3
"""Audit the certificate asymmetry behind one-sided SAT anti-checkers.

A false negative made by a purported SAT circuit has an ordinary NP witness: a
satisfying assignment.  A false positive does not have such a witness; proving
that the formula is unsatisfiable needs a separately specified refutation
system.  The brute-force routine here is test-only and never appears in the
hypothesis statement or certificate verifier.
"""

from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


def evaluates(cnf: CNF, assignment: tuple[bool, ...]) -> bool:
    if len(assignment) != cnf.variable_count:
        raise ValueError("assignment length mismatch")
    return all(
        any(
            assignment[abs(literal) - 1] if literal > 0
            else not assignment[abs(literal) - 1]
            for literal in clause
        )
        for clause in cnf.clauses
    )


def verify_false_negative(
    cnf: CNF,
    circuit_answer: bool,
    assignment: tuple[bool, ...],
) -> None:
    if circuit_answer:
        raise ValueError("false-negative certificate requires circuit answer 0")
    if not evaluates(cnf, assignment):
        raise ValueError("assignment does not satisfy formula")


def brute_force_sat(cnf: CNF) -> tuple[bool, tuple[bool, ...] | None]:
    for assignment in itertools.product((False, True), repeat=cnf.variable_count):
        if evaluates(cnf, assignment):
            return True, assignment
    return False, None


def self_test() -> None:
    satisfiable = CNF(2, ((1, 2), (-1, 2)))
    unsatisfiable = CNF(1, ((1,), (-1,)))

    truth, witness = brute_force_sat(satisfiable)
    assert truth and witness is not None
    verify_false_negative(satisfiable, False, witness)

    try:
        verify_false_negative(unsatisfiable, False, (True,))
    except ValueError as exc:
        assert "does not satisfy" in str(exc)
    else:
        raise AssertionError("accepted assignment for an unsatisfiable formula")

    false_positive_truth, false_positive_witness = brute_force_sat(unsatisfiable)
    assert false_positive_truth is False
    assert false_positive_witness is None

    print("JANUS_ONE_SIDED_SAT_ERROR_AUDIT = PASS")
    print("FALSE_NEGATIVE_CERTIFICATE = SAT_ASSIGNMENT")
    print("FALSE_POSITIVE_CERTIFICATE = NOT_PROVIDED_BY_NP_WITNESS")


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
