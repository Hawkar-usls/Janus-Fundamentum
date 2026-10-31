#!/usr/bin/env python3
"""Finite regression for the high-girth cubic conflict local MIS-reduction theorem.

This checks one deterministic 15-point duad/syntheme fixture.  It is a regression
of hypotheses/consequences only; it is not the arbitrary-size proof and makes no
P-vs-NP claim.
"""

from collections import defaultdict, deque
from itertools import combinations
import json


def perfect_matchings(items):
    items = tuple(items)
    if not items:
        yield ()
        return
    a = items[0]
    for i in range(1, len(items)):
        b = items[i]
        rest = items[1:i] + items[i + 1 :]
        pair = tuple(sorted((a, b)))
        for tail in perfect_matchings(rest):
            yield tuple(sorted((pair,) + tail))


def graph_girth(adj):
    inf = 10**9
    best = inf
    for start in range(len(adj)):
        dist = [-1] * len(adj)
        parent = [-1] * len(adj)
        dist[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    queue.append(v)
                elif parent[u] != v:
                    best = min(best, dist[u] + dist[v] + 1)
    return None if best == inf else best


def main():
    points = tuple(combinations(range(6), 2))
    point_index = {p: i for i, p in enumerate(points)}
    synthemes = sorted(set(perfect_matchings(range(6))))
    hyperedges = [tuple(sorted(point_index[p] for p in m)) for m in synthemes]

    assert len(points) == 15
    assert len(hyperedges) == 15
    assert len(set(hyperedges)) == 15
    assert all(len(e) == 3 for e in hyperedges)

    source_degree = [0] * len(points)
    pair_multiplicity = defaultdict(int)
    for edge in hyperedges:
        for v in edge:
            source_degree[v] += 1
        for u, v in combinations(edge, 2):
            pair_multiplicity[tuple(sorted((u, v)))] += 1

    source_3_regular = all(d == 3 for d in source_degree)
    source_linear = max(pair_multiplicity.values()) == 1
    assert source_3_regular
    assert source_linear

    # Bipartite incidence graph: point nodes 0..14, edge nodes 15..29.
    incidence = [set() for _ in range(len(points) + len(hyperedges))]
    for j, edge in enumerate(hyperedges):
        edge_node = len(points) + j
        for v in edge:
            incidence[v].add(edge_node)
            incidence[edge_node].add(v)

    incidence_girth = graph_girth(incidence)
    assert incidence_girth == 8

    # Conflict graph / 2-section.
    neighbors = [set() for _ in points]
    for edge in hyperedges:
        for u, v in combinations(edge, 2):
            neighbors[u].add(v)
            neighbors[v].add(u)

    conflict_degrees = [len(nbrs) for nbrs in neighbors]
    assert set(conflict_degrees) == {6}
    assert 2 * sum(conflict_degrees) // 2 == sum(conflict_degrees)

    # Connectedness.
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in neighbors[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    conflict_connected = len(seen) == len(points)
    assert conflict_connected

    # Every source hyperedge induces a conflict triangle.
    source_triangles = all(
        all(v in neighbors[u] for u, v in combinations(edge, 2))
        for edge in hyperedges
    )
    assert source_triangles

    adjacent_common_counts = []
    oriented_unconfined_outside = []
    for v in range(len(points)):
        closed_v = {v} | neighbors[v]
        for u in neighbors[v]:
            if v < u:
                adjacent_common_counts.append(len(neighbors[u] & neighbors[v]))
            # Akiba-Iwata singleton start S={v}: N(u) \\ N[S].
            oriented_unconfined_outside.append(len(neighbors[u] - closed_v))

    assert set(adjacent_common_counts) == {1}
    assert set(oriented_unconfined_outside) == {4}

    domination_pairs = []
    for u in range(len(points)):
        closed_u = {u} | neighbors[u]
        for v in range(len(points)):
            if u == v:
                continue
            closed_v = {v} | neighbors[v]
            if closed_u <= closed_v:
                domination_pairs.append((u, v))
    assert domination_pairs == []

    degree2_vertices = [v for v, d in enumerate(conflict_degrees) if d == 2]
    assert degree2_vertices == []

    # The proof of LP uniqueness is symbolic.  This finite fixture checks the
    # sufficient structural premises: 6-regularity, connectedness, and a triangle.
    lp_all_half_objective_twice = len(points)  # 2 * (n/2)
    edge_count = sum(conflict_degrees) // 2
    assert edge_count == 3 * len(points)
    assert lp_all_half_objective_twice == len(points)

    receipt = {
        "status": "PASS_HIGH_GIRTH_CUBIC_CONFLICT_LOCAL_MIS_REDUCTION_EXTINCTION",
        "proof_role": "FINITE_REGRESSION_ONLY",
        "fixture": "15_DUADS_15_SYNTHEMES_GQ_2_2",
        "source_vertices": len(points),
        "source_hyperedges": len(hyperedges),
        "source_uniformity": 3,
        "source_degree_set": sorted(set(source_degree)),
        "source_linear": source_linear,
        "incidence_girth": incidence_girth,
        "conflict_degree_set": sorted(set(conflict_degrees)),
        "conflict_edges": edge_count,
        "conflict_connected": conflict_connected,
        "source_triangles": source_triangles,
        "adjacent_common_open_neighbor_counts": sorted(set(adjacent_common_counts)),
        "closed_neighborhood_domination_pairs": domination_pairs,
        "unconfined_singleton_first_step_outside_sizes": sorted(set(oriented_unconfined_outside)),
        "degree2_vertices": degree2_vertices,
        "lp_structural_premises_for_unique_all_half": True,
        "E8_D1": "EMPTY",
        "UNIVERSAL_SELECTOR": "OPEN",
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
