#!/usr/bin/env python3
"""Exact SAT/UNSAT collision for marginal JANUS Tear signatures.

The two formulas have the same exact unsigned clause scopes, clause-width and
per-clause sign-count profiles, exact labelled variable sign counts, primal
graph, component sizes, and recognized equality/inequality XOR-gadget inventory.
Yet one has one witness and the other is UNSAT.
"""

from __future__ import annotations

import json
from collections import Counter
from itertools import product

Clause = tuple[int, ...]
Formula = tuple[Clause, ...]

SAT_FORMULA: Formula = (
    (1,),
    (2,),
    (1, -2),
    (-1, -3),
)

UNSAT_FORMULA: Formula = (
    (1,),
    (2,),
    (-1, -2),
    (1, -3),
)


def witness_count(formula: Formula, n: int) -> int:
    total = 0
    for bits in product((False, True), repeat=n):
        if all(
            any(
                bits[abs(literal) - 1]
                if literal > 0
                else not bits[abs(literal) - 1]
                for literal in clause
            )
            for clause in formula
        ):
            total += 1
    return total


def primal_graph(formula: Formula, n: int) -> tuple[tuple[int, ...], ...]:
    adjacency = [[0] * n for _ in range(n)]
    for clause in formula:
        variables = sorted({abs(literal) - 1 for literal in clause})
        for index, left in enumerate(variables):
            for right in variables[index + 1 :]:
                adjacency[left][right] = 1
                adjacency[right][left] = 1
    return tuple(tuple(row) for row in adjacency)


def component_sizes(adjacency: tuple[tuple[int, ...], ...]) -> tuple[int, ...]:
    seen: set[int] = set()
    sizes: list[int] = []
    for start in range(len(adjacency)):
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            for neighbor, linked in enumerate(adjacency[node]):
                if linked and neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        sizes.append(size)
    return tuple(sorted(sizes))


def recognized_xor_gadgets(formula: Formula) -> tuple[tuple[tuple[int, int], str], ...]:
    binary_by_scope: dict[tuple[int, int], set[Clause]] = {}
    for clause in formula:
        if len(clause) != 2:
            continue
        scope = tuple(sorted(abs(literal) for literal in clause))
        binary_by_scope.setdefault(scope, set()).add(clause)

    gadgets: list[tuple[tuple[int, int], str]] = []
    for (left, right), clauses in sorted(binary_by_scope.items()):
        equality = {(-left, right), (left, -right)}
        inequality = {(left, right), (-left, -right)}
        if equality.issubset(clauses):
            gadgets.append(((left, right), "EQ"))
        if inequality.issubset(clauses):
            gadgets.append(((left, right), "NEQ"))
    return tuple(gadgets)


def marginal_tear(formula: Formula, n: int) -> dict[str, object]:
    adjacency = primal_graph(formula, n)
    variable_profiles = []
    for variable in range(1, n + 1):
        positive = sum(variable in clause for clause in formula)
        negative = sum(-variable in clause for clause in formula)
        variable_profiles.append((positive, negative))

    return {
        "unsigned_scopes": tuple(
            sorted(
                tuple(sorted(abs(literal) for literal in clause))
                for clause in formula
            )
        ),
        "width_histogram": tuple(sorted(Counter(map(len, formula)).items())),
        "clause_sign_profiles": tuple(
            sorted(
                (
                    len(clause),
                    sum(literal > 0 for literal in clause),
                    sum(literal < 0 for literal in clause),
                )
                for clause in formula
            )
        ),
        "variable_signed_occurrences": tuple(variable_profiles),
        "primal_adjacency": adjacency,
        "component_sizes": component_sizes(adjacency),
        "recognized_xor_gadgets": recognized_xor_gadgets(formula),
    }


def run_case() -> dict[str, object]:
    sat_tear = marginal_tear(SAT_FORMULA, 3)
    unsat_tear = marginal_tear(UNSAT_FORMULA, 3)
    sat_witnesses = witness_count(SAT_FORMULA, 3)
    unsat_witnesses = witness_count(UNSAT_FORMULA, 3)
    return {
        "sat_formula": SAT_FORMULA,
        "unsat_formula": UNSAT_FORMULA,
        "tear_signatures_equal": sat_tear == unsat_tear,
        "shared_tear_signature": sat_tear,
        "sat_witness_count": sat_witnesses,
        "unsat_witness_count": unsat_witnesses,
        "opposite_sat_labels": (sat_witnesses > 0) != (unsat_witnesses > 0),
        "falsified_statement": (
            "Unsigned global structure plus the listed signed marginals is a "
            "sound complete Tear signature for SAT."
        ),
        "claim_boundary": (
            "The collision rejects this finite summary language only; it does "
            "not rule out every polynomial-time invariant language."
        ),
    }


def self_test() -> None:
    result = run_case()
    assert result["tear_signatures_equal"] is True
    assert result["sat_witness_count"] == 1
    assert result["unsat_witness_count"] == 0
    assert result["opposite_sat_labels"] is True


def main() -> int:
    self_test()
    print(json.dumps(run_case(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
