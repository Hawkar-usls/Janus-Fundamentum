#!/usr/bin/env python3
"""Probe exact Policy-0A caching on the graph-tautology family.

The smart encoding uses one variable per unordered pair.  The ordered literal
lt(i,j) means i<j; lt(j,i) is its negation.  Non-minimality plus transitivity is
unsatisfiable because every finite total order has a minimum.

Basic Formula Caching has a known exponential lower bound on this family.  This
finite probe does not transfer that theorem to Policy-0A because Policy-0A also
performs bounded local Resolution at every state.
"""

from __future__ import annotations

from itertools import permutations, product
from math import comb

from janus_tear_policy0a_masked_tseitin import (
    CNF,
    Policy0A,
    canonical_cnf,
    visible_affine_root_decision,
)


def graph_tautology_cnf(n: int) -> tuple[CNF, int]:
    if n < 2:
        raise ValueError("graph tautology requires n>=2")

    pair_var: dict[tuple[int, int], int] = {}
    next_var = 1
    for left in range(n):
        for right in range(left + 1, n):
            pair_var[(left, right)] = next_var
            next_var += 1

    def less_literal(left: int, right: int) -> int:
        if left == right:
            raise ValueError("strict order literal requires distinct vertices")
        if left < right:
            return pair_var[(left, right)]
        return -pair_var[(right, left)]

    clauses: list[tuple[int, ...]] = []

    # Every element has a predecessor: there is no minimum.
    for vertex in range(n):
        clauses.append(
            tuple(less_literal(other, vertex) for other in range(n) if other != vertex)
        )

    # For every directed triple, forbid the cyclic orientation.
    for first, second, third in permutations(range(n), 3):
        clauses.append(
            (
                less_literal(first, second),
                less_literal(second, third),
                less_literal(third, first),
            )
        )

    return canonical_cnf(clauses), next_var - 1


def satisfies(cnf: CNF, assignment: tuple[bool, ...]) -> bool:
    return all(
        any(
            (literal > 0 and assignment[literal - 1])
            or (literal < 0 and not assignment[-literal - 1])
            for literal in clause
        )
        for clause in cnf
    )


def brute_unsat(cnf: CNF, variable_count: int) -> bool:
    return not any(
        satisfies(cnf, assignment)
        for assignment in product((False, True), repeat=variable_count)
    )


def self_test() -> None:
    rows = []
    state_cap = 4096

    for n in range(3, 9):
        cnf, variable_count = graph_tautology_cnf(n)
        assert variable_count == comb(n, 2)
        assert len(cnf) == n + 2 * comb(n, 3)

        affine_answer, affine_equations = visible_affine_root_decision(
            cnf, variable_count
        )
        assert affine_answer is None

        if n <= 4:
            assert brute_unsat(cnf, variable_count)

        result = Policy0A(state_cap=state_cap).solve(cnf, variable_count)
        assert result.answer in (False, None)
        assert result.cap_exceeded == (result.answer is None)
        rows.append(
            (
                n,
                variable_count,
                len(cnf),
                result.answer,
                result.cap_exceeded,
                result.residual_states,
                result.memo_entries,
                result.resolution_attempts,
                result.resolution_additions,
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  variables = {variable_count}")
        print(f"  clauses = {len(cnf)}")
        print(f"  affine_answer = {affine_answer}")
        print(f"  affine_equations = {affine_equations}")
        print(f"  answer = {result.answer}")
        print(f"  cap_exceeded = {str(result.cap_exceeded).lower()}")
        print(f"  residual_states = {result.residual_states}")
        print(f"  memo_entries = {result.memo_entries}")
        print(f"  resolution_attempts = {result.resolution_attempts}")
        print(f"  resolution_additions = {result.resolution_additions}")

    assert rows[0][3] is False
    print("JANUS_POLICY0A_GRAPH_TAUTOLOGY_PROBE = PASS")
    print(f"state_cap = {state_cap}")
    print(f"rows = {tuple(rows)}")
    print("known_external_fact = basic Formula Caching requires exponentially many nodes on graph tautologies")
    print("claim_boundary = finite Policy-0A probe; local Resolution prevents direct theorem transfer")


if __name__ == "__main__":
    self_test()
