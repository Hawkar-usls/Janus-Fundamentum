#!/usr/bin/env python3
"""Verify a branch-aligned root Resolution refutation for a Policy-0T trace.

This finite certificate checks that the deterministic Policy-0T trace branches
on variable 4, that both child computations return UNSAT, that the root proof
derives the complementary conflict clauses (-4) and (4), and that resolving
those clauses yields the empty clause.

The artifact is a finite positive control for H130. It does not yet prove the
uniform size-O(W), depth-O(N) translation for every Policy-0T execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from janus_tear_policy0t_trace_certificate import (
    N_VARS,
    TracePolicy,
    UNSAT_FORMULA as TRACE_FORMULA,
    canonical_cnf,
    verify_trace,
)

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


# Eight of the ten input clauses suffice. Lines 12 and 13 are the conflict
# clauses for the true and false x4 branches, respectively. Line 14 combines
# the sibling conflicts at the root.
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
    Resolution((-4,), 8, 10, 1),           # 12: conflict for x4=True
    Resolution((4,), 9, 11, 2),            # 13: conflict for x4=False
    Resolution((), 12, 13, 4),             # 14: combine siblings
)


def resolve(left: Clause, right: Clause, pivot: int) -> Clause | None:
    if pivot in left and -pivot in right:
        raw = (set(left) - {pivot}) | (set(right) - {-pivot})
    elif -pivot in left and pivot in right:
        raw = (set(left) - {-pivot}) | (set(right) - {pivot})
    else:
        raise AssertionError(f"pivot {pivot} is not complementary")
    return canonical_clause(raw)


def restrict_clause(clause: Clause, variable: int, value: bool) -> Clause | None:
    """Return the restricted clause; None denotes a satisfied clause."""

    true_literal = variable if value else -variable
    false_literal = -true_literal
    if true_literal in clause:
        return None
    return tuple(literal for literal in clause if literal != false_literal)


def verify_resolution_proof() -> tuple[list[Clause], int, int, int, int]:
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
    return clauses, axiom_lines, resolution_lines, maximum_width, proof_depth


def verify_trace_alignment(clauses: list[Clause]) -> tuple[int, int]:
    assert canonical_cnf(TRACE_FORMULA) == canonical_cnf(UNSAT_FORMULA)
    assert N_VARS == 4

    policy = TracePolicy()
    answer, root_id = policy.search(canonical_cnf(TRACE_FORMULA))
    assert answer is False
    assert verify_trace(policy.nodes, root_id, canonical_cnf(TRACE_FORMULA)) is False

    root = policy.nodes[root_id]
    branch_variable = root["branch_var"]
    children = root["children"]
    assert branch_variable == 4
    assert isinstance(children, list)
    assert [child["value"] for child in children] == [False, True]
    assert [child["result"] for child in children] == [False, False]

    false_branch_conflict = clauses[13]  # (4), falsified by x4=False
    true_branch_conflict = clauses[12]   # (-4), falsified by x4=True

    assert restrict_clause(false_branch_conflict, 4, False) == ()
    assert restrict_clause(true_branch_conflict, 4, True) == ()
    assert restrict_clause(false_branch_conflict, 4, True) is None
    assert restrict_clause(true_branch_conflict, 4, False) is None

    final = PROOF[14]
    assert isinstance(final, Resolution)
    assert final.left == 12 and final.right == 13 and final.pivot == branch_variable
    assert clauses[14] == ()

    return branch_variable, len(policy.nodes)


def self_test() -> None:
    clauses, axiom_lines, resolution_lines, maximum_width, proof_depth = (
        verify_resolution_proof()
    )
    branch_variable, trace_nodes = verify_trace_alignment(clauses)

    assert axiom_lines == 8
    assert resolution_lines == 7
    assert maximum_width == 3
    assert proof_depth == 3
    assert branch_variable == 4
    assert trace_nodes == 3

    print("JANUS_TEAR_POLICY0T_TRACE_TO_PROOF_BRIDGE = PASS")
    print(f"input_clauses = {len(UNSAT_FORMULA)}")
    print(f"trace_nodes = {trace_nodes}")
    print(f"root_branch_variable = {branch_variable}")
    print("false_branch_conflict_clause = (4)")
    print("true_branch_conflict_clause = (-4)")
    print(f"used_axiom_lines = {axiom_lines}")
    print(f"resolution_lines = {resolution_lines}")
    print(f"proof_lines = {len(PROOF)}")
    print(f"maximum_width = {maximum_width}")
    print(f"proof_depth = {proof_depth}")
    print("final_clause = EMPTY")
    print("claim_boundary = finite aligned bridge only; uniform H130 simulation remains open")


if __name__ == "__main__":
    self_test()
