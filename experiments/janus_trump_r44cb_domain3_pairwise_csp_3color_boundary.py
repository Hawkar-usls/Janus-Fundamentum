#!/usr/bin/env python3
from itertools import product, combinations


def is_proper_coloring(n, edges, colors):
    return all(colors[u] != colors[v] for u, v in edges)


def compatibility_assignments(n, edges):
    # R44CB transport view: each block/vertex has exactly three local candidates.
    # Every interacting pair/edge permits exactly unequal candidate labels.
    out = []
    for a in product(range(3), repeat=n):
        if all(a[u] != a[v] for u, v in edges):
            out.append(a)
    return out


def graph_3color_assignments(n, edges):
    return [a for a in product(range(3), repeat=n) if is_proper_coloring(n, edges, a)]


def all_graphs(n):
    possible = list(combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [e for i, e in enumerate(possible) if (mask >> i) & 1]


def audit(max_n=5):
    checked = 0
    for n in range(1, max_n + 1):
        for edges in all_graphs(n):
            lhs = compatibility_assignments(n, edges)
            rhs = graph_3color_assignments(n, edges)
            assert lhs == rhs
            checked += 1

    triangle = [(0, 1), (1, 2), (0, 2)]
    k4 = list(combinations(range(4), 2))
    triangle_count = len(compatibility_assignments(3, triangle))
    k4_count = len(compatibility_assignments(4, k4))
    assert triangle_count == 6
    assert k4_count == 0

    return {
        "gate": "R44CB_DOMAIN3_PAIRWISE_CSP_3COLOR_BOUNDARY",
        "graphs_checked": checked,
        "max_n": max_n,
        "triangle_assignment_count": triangle_count,
        "k4_assignment_count": k4_count,
        "exact_bijection_verified_on_enumerated_universe": True,
        "boundary_witness": "DOMAIN_3_ARBITRARY_PAIRWISE_COMPATIBILITY_REALIZES_GRAPH_3_COLORING",
        "R44CA_boolean_2sat_extension_universal": False,
        "full_transport_polynomiality_proven": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(audit(), indent=2, sort_keys=True))
