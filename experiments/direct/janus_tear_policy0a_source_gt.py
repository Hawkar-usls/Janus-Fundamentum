#!/usr/bin/env python3
"""Source-family GT_n probe for C024 / Issue #211.

This generator keeps the directed variables x_(i,j), i != j, rather than
identifying opposite directions with one Boolean variable.  It follows the
GT_n description used by the Formula-Caching lower-bound route:

- directed order variables x_(i,j), i != j;
- totality for each unordered pair;
- antisymmetry for each unordered pair;
- transitivity for each ordered distinct triple;
- non-minimality for every vertex.

This file is an encoding-repair probe.  It does not transfer the historical
lower bound through Policy-0A's extra local Resolution step and does not prove
P=NP or P!=NP.
"""

from __future__ import annotations

from itertools import combinations, permutations, product

from janus_tear_policy0a_masked_tseitin import CNF, canonical_cnf


def source_graph_tautology_cnf(n: int) -> tuple[CNF, int]:
    if n < 2:
        raise ValueError("GT_n requires n >= 2")

    variable: dict[tuple[int, int], int] = {}
    next_variable = 1
    for left in range(n):
        for right in range(n):
            if left == right:
                continue
            variable[(left, right)] = next_variable
            next_variable += 1

    clauses: list[tuple[int, ...]] = []

    # Totality + antisymmetry for every unordered pair.
    for left, right in combinations(range(n), 2):
        lr = variable[(left, right)]
        rl = variable[(right, left)]
        clauses.append((lr, rl))
        clauses.append((-lr, -rl))

    # Transitivity: (i<j and j<k) -> i<k.
    for first, second, third in permutations(range(n), 3):
        clauses.append(
            (
                -variable[(first, second)],
                -variable[(second, third)],
                variable[(first, third)],
            )
        )

    # Negation of existence of a minimum: every vertex has a predecessor.
    for vertex in range(n):
        clauses.append(
            tuple(variable[(other, vertex)] for other in range(n) if other != vertex)
        )

    return canonical_cnf(clauses), next_variable - 1


def brute_satisfiable(cnf: CNF, variable_count: int) -> bool:
    for assignment in product((False, True), repeat=variable_count):
        if all(
            any(
                (literal > 0 and assignment[literal - 1])
                or (literal < 0 and not assignment[-literal - 1])
                for literal in clause
            )
            for clause in cnf
        ):
            return True
    return False


def self_test() -> None:
    for n in range(2, 5):
        cnf, variable_count = source_graph_tautology_cnf(n)
        assert variable_count == n * (n - 1)
        assert len(cnf) == n * ((n - 1) ** 2 + 1)
        assert not brute_satisfiable(cnf, variable_count)
        print(f"SOURCE_GT_{n} = UNSAT")
        print(f"  variables = {variable_count}")
        print(f"  clauses = {len(cnf)}")

    print("JANUS_SOURCE_GT_ENCODING_REPAIR = PASS")
    print("claim_boundary = source-family encoding probe only; local-Resolution robustness remains open")


if __name__ == "__main__":
    self_test()
