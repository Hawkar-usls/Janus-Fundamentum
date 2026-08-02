#!/usr/bin/env python3
"""Independently verify a root Resolution refutation for the Policy-0T trace fixture.

The certificate is a finite positive control for H130. It proves the same
four-variable UNSAT formula used by the transition trace, but does not yet prove
that every Policy-0T execution can be translated with size O(W) and depth O(N).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

Clause = tuple[int, ...]

UNSAT_FORMULA: tuple[Clause, ...] = (
    (-2, -3, -4),
    (-2, 3, -4),
    (-1, -3, -4),
    (-1, -2, 4),
    (-1, 3, -4),
    (1, -2, -4),
    (1, -2, 4),
    (1, 2, -4),
    (2, -3, 4),
    (2, 3, 4),
)


def canonical_clause(clause: Iterable[int]) -> Clause | None:
    literals = set(clause)
    if any(-literal in literals for literal in literals):
        return None
    return tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))


@dataclass(frozen=True)
class Axiom:
    clause: Clause


@dataclass(frozen=True)
class Resolution:
    clause: Clause
    left: int
    right: int
    pivot: int


ProofLine = Axiom | Resolution


# Eight of the ten input clauses suffice. The proof uses seven legal
# Resolution inferences and ends with the empty clause.
PROOF: tuple[ProofLine, ...] = (
    Axiom((-1, -3, -4)),                    # 0
    Axiom((-1, -2, 4)),                     # 1
    Axiom((-1, 3, -4)),                     # 2
    Axiom((1, -2, -4)),                     # 3
    Axiom((1, -2, 4)),                      # 4
    Axiom((1, 2, -4)),                      # 5
    Axiom((2, -3, 4)),                      # 6
    Axiom((2, 3, 4)),                       # 7
    Resolution((-1, -4), 0, 2, 3),         # 8
    Resolution((-2, 4), 1, 4, 1),          # 9
    Resolution((1, -4), 3, 5, 2),          # 10
    Resolution((2, 4), 6, 7, 3),           # 11
    Resolution((-4,), 8, 10, 1),           # 12
    Resolution((4,), 9, 11, 2),            # 13
    Resolution((), 12, 13, 4),              # 14
)


def resolve(left: Clause, right: Clause, pivot: int) -> Clause | None:
    if pivot in left and -pivot in right:
        raw = (set(left) - {pivot}) | (set(right) - {-pivot})
    elif -pivot in left and pivot in right:
        raw = (set(left) - {-pivot}) | (set(right) - {pivot})
    else:
        raise AssertionError(f"pivot {pivot} is not complementary")
    return canonical_clause(raw)


def verify() -> tuple[int, int, int, int]:
    axioms = {canonical_clause(clause) for clause in UNSAT_FORMULA}
    assert None not in axioms

    clauses: list[Clause] = []
    depths: list[int] = []
    axiom_lines = 0
    resolution_lines = 0

    for index, line in enumerate(PROOF):
        if isinstance(line, Axiom):
            clause = canonical_clause(line.clause)
            assert clause is not None
            assert clause in axioms, f"line {index}: non-input axiom {clause}"
            depth = 0
            axiom_lines += 1
        else:
            assert 0 <= line.left < index
            assert 0 <= line.right < index
            assert line.left != line.right
            clause = resolve(clauses[line.left], clauses[line.right], line.pivot)
            assert clause == canonical_clause(line.clause), (
                f"line {index}: expected {line.clause}, derived {clause}"
            )
            assert clause is not None
            depth = 1 + max(depths[line.left], depths[line.right])
            resolution_lines += 1

        clauses.append(clause)
        depths.append(depth)

    assert clauses[-1] == ()
    maximum_width = max(len(clause) for clause in clauses)
    proof_depth = depths[-1]
    return axiom_lines, resolution_lines, maximum_width, proof_depth


def self_test() -> None:
    axiom_lines, resolution_lines, maximum_width, proof_depth = verify()
    assert axiom_lines == 8
    assert resolution_lines == 7
    assert maximum_width == 3
    assert proof_depth == 3

    print("JANUS_TEAR_POLICY0T_ROOT_RESOLUTION_CERTIFICATE = PASS")
    print(f"input_clauses = {len(UNSAT_FORMULA)}")
    print(f"used_axiom_lines = {axiom_lines}")
    print(f"resolution_lines = {resolution_lines}")
    print(f"proof_lines = {len(PROOF)}")
    print(f"maximum_width = {maximum_width}")
    print(f"proof_depth = {proof_depth}")
    print("final_clause = EMPTY")
    print("claim_boundary = finite root proof only; general Policy-0T simulation remains open")


if __name__ == "__main__":
    self_test()
