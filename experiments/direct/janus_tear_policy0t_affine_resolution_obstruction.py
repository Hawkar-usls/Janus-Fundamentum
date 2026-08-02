#!/usr/bin/env python3
"""Audit the affine-shortcut obstruction to H130's ordinary-Resolution claim.

The executable part verifies that Policy-0T decides several visible odd-charge
bounded-degree Tseitin CNFs before entering its recursive search.  The
asymptotic contradiction uses the registered/classical theorem that Tseitin
CNFs on bounded-degree expanders require exponential ordinary Resolution size.
That theorem is literature, not re-proved by this finite script.
"""

from __future__ import annotations

from janus_tear_policy0a_masked_tseitin import visible_tseitin_cnf
from janus_tear_policy0t_no_cache import Policy0T

Edge = tuple[int, int]


def complete_bipartite(left: int, right: int) -> tuple[Edge, ...]:
    return tuple((u, left + v) for u in range(left) for v in range(right))


def cube_edges() -> tuple[Edge, ...]:
    edges: set[Edge] = set()
    for vertex in range(8):
        for bit in (1, 2, 4):
            neighbour = vertex ^ bit
            edges.add(tuple(sorted((vertex, neighbour))))
    return tuple(sorted(edges))


def petersen_edges() -> tuple[Edge, ...]:
    outer = [(i, (i + 1) % 5) for i in range(5)]
    spokes = [(i, i + 5) for i in range(5)]
    inner = [(i + 5, ((i + 2) % 5) + 5) for i in range(5)]
    return tuple(sorted({tuple(sorted(edge)) for edge in outer + spokes + inner}))


def audit_case(name: str, vertex_count: int, edges: tuple[Edge, ...]) -> None:
    cnf, variables = visible_tseitin_cnf(vertex_count, edges)
    result = Policy0T().solve(cnf, variables)

    assert result.answer is False
    assert not result.cap_exceeded
    assert result.recursive_calls == 0
    assert result.expanded_states == 0
    assert result.branch_edges == 0
    assert result.affine_equations >= vertex_count

    maximum_degree = max(
        sum(vertex in edge for edge in edges) for vertex in range(vertex_count)
    )
    print(f"CASE = {name}")
    print(f"  vertices = {vertex_count}")
    print(f"  edges_or_variables = {variables}")
    print(f"  clauses = {len(cnf)}")
    print(f"  maximum_degree = {maximum_degree}")
    print(f"  affine_equations = {result.affine_equations}")
    print(f"  recursive_calls = {result.recursive_calls}")
    print("  answer = UNSAT")


def self_test() -> None:
    audit_case("K3_3", 6, complete_bipartite(3, 3))
    audit_case("CUBE", 8, cube_edges())
    audit_case("PETERSEN", 10, petersen_edges())

    print("JANUS_POLICY0T_AFFINE_RESOLUTION_OBSTRUCTION = PASS")
    print("finite_policy_fact = visible bounded-degree Tseitin is decided before search")
    print("asymptotic_bridge = use expander-Tseitin ordinary Resolution lower bound")
    print("verdict = H130 ordinary-Resolution simulation is false as stated")
    print("salvage = restrict Resolution simulation to affine_answer=None search core")


if __name__ == "__main__":
    self_test()
