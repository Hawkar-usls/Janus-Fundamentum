#!/usr/bin/env python3
"""Executable finite regression for the Exact-One BIG/ELS theorem.

The proof is structural and lives in the companion theorem note. This checker
verifies the local implication orientation and several finite hypergraph unions.
"""
from __future__ import annotations

import json


def exact_one_binary_clauses(edge: tuple[int, int, int]):
    a, b, c = edge
    return [(-a, -b), (-a, -c), (-b, -c)]


def big_edges(edges: list[tuple[int, int, int]]):
    arcs: set[tuple[int, int]] = set()
    for edge in edges:
        for p, q in exact_one_binary_clauses(edge):
            # Clause (p or q) contributes (-p -> q) and (-q -> p).
            arcs.add((-p, q))
            arcs.add((-q, p))
    return arcs


def assert_positive_to_negative_only(edges: list[tuple[int, int, int]]) -> None:
    arcs = big_edges(edges)
    assert all(u > 0 and v < 0 for u, v in arcs)
    outgoing = {u for u, _ in arcs}
    negative_vertices = {-abs(x) for e in edges for x in e}
    assert outgoing.isdisjoint(negative_vertices)

    # Therefore every directed path has length at most one and every SCC is singleton.
    adjacency: dict[int, set[int]] = {}
    for u, v in arcs:
        adjacency.setdefault(u, set()).add(v)
    for _, v in arcs:
        assert not adjacency.get(v)


def main() -> None:
    fixtures = {
        "single": [(1, 2, 3)],
        "chain": [(1, 2, 3), (3, 4, 5), (5, 6, 7)],
        "overlapping": [(1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 5, 6)],
        "z3_rows": [(1, 2, 3), (4, 5, 6), (7, 8, 9)],
    }
    for edges in fixtures.values():
        assert_positive_to_negative_only(edges)

    out = {
        "status": "PASS_EXACT_ONE_BIG_ELS_LEAN_REGRESSION",
        "local_binary_clause_type": "NEGATIVE_NEGATIVE_ONLY",
        "big_arc_type": "POSITIVE_TO_NEGATIVE_ONLY",
        "negative_literal_outdegree": 0,
        "nontrivial_scc_possible": False,
        "fixtures": sorted(fixtures),
        "theorem_scope": "UNTOUCHED_STANDARD_EXACT_ONE_CNF",
        "boundary": {
            "BROADER_CERTIFIED_EQUIVALENCE": "OPEN",
            "UNIVERSAL_SELECTOR": "OPEN",
            "E8_D1": "EMPTY",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
