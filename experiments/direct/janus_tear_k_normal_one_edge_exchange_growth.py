#!/usr/bin/env python3
"""Exhaust labelled K-normal exact one-edge exchanges through eight vertices.

Generate every labelled inward star and one-subdivision star rooted at zero.
For every deleted tree edge and every possible added directed edge, retain only
updates which are simple in-arborescences with the same root.  Verify the
arbitrary-size graph theorem's conclusions:

- at most two non-star edges;
- height at most three;
- every non-K-normal result becomes K-normal after contracting any non-star
  edge.

The theorem is proved separately in
`GT_K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH.md`; this is an independent finite
falsification gate.
"""

from __future__ import annotations

from collections import Counter

Edge = tuple[int, int]


def source_trees(vertex_count: int):
    star = tuple((vertex, 0) for vertex in range(1, vertex_count))
    result = {star}
    if vertex_count >= 3:
        for intermediate in range(1, vertex_count):
            for leaf in range(1, vertex_count):
                if leaf == intermediate:
                    continue
                edges = [(leaf, intermediate), (intermediate, 0)]
                edges.extend(
                    (vertex, 0)
                    for vertex in range(1, vertex_count)
                    if vertex not in (leaf, intermediate)
                )
                result.add(tuple(sorted(edges)))
    return tuple(sorted(result))


def is_in_arborescence(
    vertex_count: int,
    edges: tuple[Edge, ...],
    root: int = 0,
) -> bool:
    if len(edges) != vertex_count - 1 or len(set(edges)) != len(edges):
        return False
    if any(left == right for left, right in edges):
        return False
    outgoing = Counter(left for left, _right in edges)
    if outgoing[root] != 0:
        return False
    if any(outgoing[vertex] != 1 for vertex in range(vertex_count) if vertex != root):
        return False
    parent = {left: right for left, right in edges}
    for vertex in range(vertex_count):
        current = vertex
        seen = set()
        while current != root:
            if current in seen or current not in parent:
                return False
            seen.add(current)
            current = parent[current]
    return True


def shape(vertex_count: int, edges: tuple[Edge, ...], root: int = 0):
    assert is_in_arborescence(vertex_count, edges, root)
    parent = {left: right for left, right in edges}
    maximum = 0
    for vertex in range(vertex_count):
        current = vertex
        distance = 0
        while current != root:
            current = parent[current]
            distance += 1
        maximum = max(maximum, distance)
    nonstar = sum(1 for _left, right in edges if right != root)
    return maximum, nonstar, maximum <= 2 and nonstar <= 1


def contract_edge(
    vertex_count: int,
    edges: tuple[Edge, ...],
    edge: Edge,
    root: int = 0,
):
    left, right = edge
    assert right != root
    assert edge in edges

    # Contract the tail into the head, then canonically relabel the remaining
    # vertices in increasing old-label order while keeping root at zero.
    def merged(vertex: int):
        return right if vertex == left else vertex

    raw = []
    remaining_vertices = set()
    for candidate in edges:
        if candidate == edge:
            continue
        tail, head = (merged(vertex) for vertex in candidate)
        if tail == head:
            continue
        raw.append((tail, head))
        remaining_vertices.update((tail, head))
    remaining_vertices.add(root)
    ordered = [root] + sorted(vertex for vertex in remaining_vertices if vertex != root)
    relabel = {vertex: index for index, vertex in enumerate(ordered)}
    contracted = tuple(sorted(
        (relabel[tail], relabel[head])
        for tail, head in raw
    ))
    return len(ordered), contracted


def self_test() -> None:
    counts: Counter[str] = Counter()
    source_shapes: Counter[tuple[int, int, bool]] = Counter()
    result_shapes: Counter[tuple[int, int, bool]] = Counter()
    contraction_shapes: Counter[tuple[int, int, bool]] = Counter()
    violations = []

    for vertex_count in range(2, 9):
        for source in source_trees(vertex_count):
            source_shape = shape(vertex_count, source)
            assert source_shape[2]
            source_shapes[source_shape] += 1
            counts["sources"] += 1

            for deleted in source:
                residual = tuple(edge for edge in source if edge != deleted)
                for tail in range(vertex_count):
                    for head in range(vertex_count):
                        added = (tail, head)
                        if tail == head or added in residual:
                            continue
                        result = tuple(sorted(residual + (added,)))
                        if not is_in_arborescence(vertex_count, result):
                            continue

                        counts["exact_one_edge_exchanges"] += 1
                        result_shape = shape(vertex_count, result)
                        result_shapes[result_shape] += 1
                        height, nonstar, k_normal = result_shape
                        if height > 3 or nonstar > 2:
                            violations.append({
                                "kind": "GROWTH_BOUND",
                                "vertex_count": vertex_count,
                                "source": source,
                                "deleted": deleted,
                                "added": added,
                                "result": result,
                                "shape": result_shape,
                            })
                            continue

                        if k_normal:
                            counts["k_normal_results"] += 1
                            continue

                        counts["non_k_normal_results"] += 1
                        nonstar_edges = tuple(
                            edge for edge in result if edge[1] != 0
                        )
                        if len(nonstar_edges) != 2:
                            violations.append({
                                "kind": "NONSTAR_COUNT",
                                "result": result,
                                "shape": result_shape,
                                "nonstar_edges": nonstar_edges,
                            })
                            continue

                        for marked in nonstar_edges:
                            child_vertex_count, contracted = contract_edge(
                                vertex_count, result, marked
                            )
                            if not is_in_arborescence(
                                child_vertex_count, contracted
                            ):
                                violations.append({
                                    "kind": "CONTRACTION_NOT_TREE",
                                    "result": result,
                                    "marked": marked,
                                    "contracted": contracted,
                                })
                                continue
                            contracted_shape = shape(
                                child_vertex_count, contracted
                            )
                            contraction_shapes[contracted_shape] += 1
                            counts["marked_contractions"] += 1
                            if not contracted_shape[2]:
                                violations.append({
                                    "kind": "CONTRACTION_NOT_K_NORMAL",
                                    "result": result,
                                    "result_shape": result_shape,
                                    "marked": marked,
                                    "contracted": contracted,
                                    "contracted_shape": contracted_shape,
                                })

    assert counts["exact_one_edge_exchanges"] > 0
    assert counts["non_k_normal_results"] > 0
    assert not violations, violations[:3]
    print("JANUS_K_NORMAL_ONE_EDGE_EXCHANGE_GROWTH = PASS")
    print(f"COUNTS = {tuple(sorted(counts.items()))}")
    print(f"SOURCE_SHAPES = {tuple(sorted(source_shapes.items(), key=repr))}")
    print(f"RESULT_SHAPES = {tuple(sorted(result_shapes.items(), key=repr))}")
    print(
        "CONTRACTION_SHAPES = "
        f"{tuple(sorted(contraction_shapes.items(), key=repr))}"
    )
    print(f"VIOLATIONS = {tuple(violations)}")
    print(
        "claim_boundary = finite labelled falsification gate through eight "
        "vertices; arbitrary-size rooted-tree theorem proved separately; "
        "Policy-0A reachability of the exact-exchange hypotheses remains open"
    )


if __name__ == "__main__":
    self_test()
