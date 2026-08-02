#!/usr/bin/env python3
"""Exact SAT/UNSAT collision for a unit-propagation-enhanced marginal Tear."""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product
from typing import Iterable

Clause = tuple[int, ...]
Formula = tuple[Clause, ...]

UNSAT_FORMULA: Formula = (
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

SAT_FORMULA: Formula = (
    (-2, -3, -4),
    (-2, 3, 4),
    (-1, -2, -4),
    (-1, -2, 4),
    (-1, 2, -4),
    (1, -2, -4),
    (1, 3, -4),
    (1, 3, 4),
    (2, -3, -4),
    (2, -3, 4),
)

N_VARS = 4


def witnesses(formula: Formula) -> list[tuple[bool, ...]]:
    out: list[tuple[bool, ...]] = []
    for assignment in product((False, True), repeat=N_VARS):
        if all(
            any(
                (literal > 0 and assignment[literal - 1])
                or (literal < 0 and not assignment[-literal - 1])
                for literal in clause
            )
            for clause in formula
        ):
            out.append(assignment)
    return out


def primal_edges(formula: Formula) -> tuple[tuple[int, int], ...]:
    edges: set[tuple[int, int]] = set()
    for clause in formula:
        variables = sorted({abs(literal) for literal in clause})
        edges.update(combinations(variables, 2))
    return tuple(sorted(edges))


def component_sizes(edges: Iterable[tuple[int, int]]) -> tuple[int, ...]:
    adjacency = {variable: set() for variable in range(1, N_VARS + 1)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    unseen = set(adjacency)
    sizes: list[int] = []
    while unseen:
        root = unseen.pop()
        stack = [root]
        size = 0
        while stack:
            vertex = stack.pop()
            size += 1
            for neighbour in adjacency[vertex]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    stack.append(neighbour)
        sizes.append(size)
    return tuple(sorted(sizes))


def unit_propagation_profile(formula: Formula) -> tuple[object, ...]:
    clauses = [set(clause) for clause in formula]
    assignment: dict[int, bool] = {}

    while True:
        reduced: list[set[int]] = []
        for clause in clauses:
            residual: set[int] = set()
            satisfied = False
            for literal in clause:
                variable = abs(literal)
                if variable not in assignment:
                    residual.add(literal)
                    continue
                value = assignment[variable]
                if (literal > 0 and value) or (literal < 0 and not value):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not residual:
                return ("CONTRADICTION", tuple(sorted(assignment.items())))
            reduced.append(residual)

        units = [next(iter(clause)) for clause in reduced if len(clause) == 1]
        changed = False
        for literal in units:
            variable = abs(literal)
            value = literal > 0
            if variable in assignment and assignment[variable] != value:
                return ("CONTRADICTION", tuple(sorted(assignment.items())))
            if variable not in assignment:
                assignment[variable] = value
                changed = True

        clauses = reduced
        if not changed:
            break

    return (
        "OPEN",
        tuple(sorted(assignment.items())),
        tuple(sorted(Counter(len(clause) for clause in clauses).items())),
        len(clauses),
    )


def recognized_binary_xor_inventory(formula: Formula) -> tuple[tuple[str, int, int], ...]:
    clause_set = {frozenset(clause) for clause in formula}
    inventory: list[tuple[str, int, int]] = []
    for left, right in combinations(range(1, N_VARS + 1), 2):
        equality = {
            frozenset((-left, right)),
            frozenset((left, -right)),
        }
        inequality = {
            frozenset((left, right)),
            frozenset((-left, -right)),
        }
        if equality <= clause_set:
            inventory.append(("EQ", left, right))
        if inequality <= clause_set:
            inventory.append(("NEQ", left, right))
    return tuple(inventory)


def tear_signature(formula: Formula) -> tuple[object, ...]:
    edges = primal_edges(formula)
    return (
        N_VARS,
        len(formula),
        tuple(sorted(Counter(len(clause) for clause in formula).items())),
        tuple(
            sorted(
                Counter(
                    tuple(sorted(abs(literal) for literal in clause))
                    for clause in formula
                ).items()
            )
        ),
        tuple(
            sorted(
                Counter(
                    (
                        sum(literal > 0 for literal in clause),
                        sum(literal < 0 for literal in clause),
                    )
                    for clause in formula
                ).items()
            )
        ),
        tuple(
            (
                sum(variable in clause for clause in formula),
                sum(-variable in clause for clause in formula),
            )
            for variable in range(1, N_VARS + 1)
        ),
        edges,
        component_sizes(edges),
        recognized_binary_xor_inventory(formula),
        unit_propagation_profile(formula),
    )


def self_test() -> None:
    unsat_witnesses = witnesses(UNSAT_FORMULA)
    sat_witnesses = witnesses(SAT_FORMULA)
    unsat_signature = tear_signature(UNSAT_FORMULA)
    sat_signature = tear_signature(SAT_FORMULA)

    assert not unsat_witnesses
    assert sat_witnesses == [
        (False, True, True, False),
        (True, False, False, False),
    ]
    assert unsat_signature == sat_signature
    assert unsat_signature[-1] == ("OPEN", (), ((3, 10),), 10)

    print("JANUS_TEAR_UNIT_PROPAGATION_COLLISION = PASS")
    print(f"variables = {N_VARS}")
    print(f"clauses_per_formula = {len(SAT_FORMULA)}")
    print(f"sat_witnesses = {len(sat_witnesses)}")
    print(f"unsat_witnesses = {len(unsat_witnesses)}")
    print(f"unit_propagation_profile = {unsat_signature[-1]}")
    print("tear_signatures_equal = true")


if __name__ == "__main__":
    self_test()
