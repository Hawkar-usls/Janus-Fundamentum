#!/usr/bin/env python3
"""Exhaust finite labelled instances of marked singleton-edge absorption.

For every labelled inward star and one-subdivision star on 2..8 vertices,
subdivide every directed edge once.  Mark either half of the new two-edge path,
simulate the falsifying branch by deleting the marked occurrence and identifying
its endpoints, and verify that the external directed graph is exactly the
source K-normal tree under the canonical contraction map.

The arbitrary-size theorem is proved separately in
`GT_MARKED_SINGLETON_EDGE_ABSORPTION.md`; this program is an independent finite
falsification gate for its graph/encoding operation.
"""

from __future__ import annotations

from collections import Counter

Edge = tuple[int, int]


def star(vertex_count: int) -> tuple[Edge, ...]:
    assert vertex_count >= 2
    return tuple((vertex, 0) for vertex in range(1, vertex_count))


def one_subdivision_stars(vertex_count: int):
    if vertex_count < 3:
        return ()
    result = []
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
            result.append(tuple(sorted(edges)))
    return tuple(sorted(set(result)))


def root(edges: tuple[Edge, ...]) -> int:
    vertices = {vertex for edge in edges for vertex in edge}
    tails = {tail for tail, _head in edges}
    sinks = vertices - tails
    assert len(sinks) == 1, (edges, sinks)
    return next(iter(sinks))


def shape(edges: tuple[Edge, ...]) -> tuple[int, int, bool]:
    sink = root(edges)
    parent = {tail: head for tail, head in edges}
    assert len(parent) == len(edges)
    vertices = {vertex for edge in edges for vertex in edge}
    heights = {}
    for vertex in vertices:
        current = vertex
        seen = set()
        distance = 0
        while current != sink:
            assert current not in seen, (edges, vertex)
            seen.add(current)
            current = parent[current]
            distance += 1
        heights[vertex] = distance
    maximum = max(heights.values())
    nonstar = sum(1 for _tail, head in edges if head != sink)
    return maximum, nonstar, maximum == 2 and nonstar == 1


def subdivide(edges: tuple[Edge, ...], edge: Edge, new_vertex: int):
    tail, head = edge
    result = [candidate for candidate in edges if candidate != edge]
    first = (tail, new_vertex)
    second = (new_vertex, head)
    result.extend((first, second))
    return tuple(sorted(result)), first, second


def contract_marked(
    transient: tuple[Edge, ...],
    marked: Edge,
    original_edge: Edge,
    new_vertex: int,
):
    tail, head = original_edge
    if marked == (tail, new_vertex):
        replacement = tail
    elif marked == (new_vertex, head):
        replacement = head
    else:
        raise AssertionError((marked, original_edge, new_vertex))

    def mapped(vertex: int):
        return replacement if vertex == new_vertex else vertex

    residual = []
    for edge in transient:
        if edge == marked:
            continue
        left, right = (mapped(vertex) for vertex in edge)
        if left == right:
            continue
        residual.append((left, right))
    return tuple(sorted(residual))


def self_test() -> None:
    counts: Counter[str] = Counter()
    source_shapes: Counter[tuple[int, int, bool]] = Counter()
    transient_shapes: Counter[tuple[int, int, bool]] = Counter()
    restored_shapes: Counter[tuple[int, int, bool]] = Counter()
    violations = []

    for vertex_count in range(2, 9):
        sources = [("STAR", star(vertex_count))]
        sources.extend(
            ("ONE_SUBDIVISION_STAR", edges)
            for edges in one_subdivision_stars(vertex_count)
        )
        for source_kind, source in sources:
            source_shape = shape(source)
            assert source_shape[0] <= 2 and source_shape[1] <= 1
            counts[f"source_{source_kind}"] += 1
            source_shapes[source_shape] += 1
            new_vertex = vertex_count
            for original_edge in source:
                transient, first, second = subdivide(
                    source, original_edge, new_vertex
                )
                transient_shape = shape(transient)
                transient_shapes[transient_shape] += 1
                counts["marked_extensions"] += 1
                for marked in (first, second):
                    counts["marked_half_edges"] += 1
                    restored = contract_marked(
                        transient,
                        marked,
                        original_edge,
                        new_vertex,
                    )
                    restored_shape = shape(restored)
                    restored_shapes[restored_shape] += 1
                    if restored != source or restored_shape != source_shape:
                        violations.append({
                            "vertex_count": vertex_count,
                            "source_kind": source_kind,
                            "source": source,
                            "source_shape": source_shape,
                            "original_edge": original_edge,
                            "transient": transient,
                            "transient_shape": transient_shape,
                            "marked": marked,
                            "restored": restored,
                            "restored_shape": restored_shape,
                        })

    assert counts["marked_half_edges"] > 0
    assert not violations, violations[:3]
    print("JANUS_MARKED_SINGLETON_EDGE_ABSORPTION = PASS")
    print(f"COUNTS = {tuple(sorted(counts.items()))}")
    print(f"SOURCE_SHAPES = {tuple(sorted(source_shapes.items(), key=repr))}")
    print(
        "TRANSIENT_SHAPES = "
        f"{tuple(sorted(transient_shapes.items(), key=repr))}"
    )
    print(
        "RESTORED_SHAPES = "
        f"{tuple(sorted(restored_shapes.items(), key=repr))}"
    )
    print(f"VIOLATIONS = {tuple(violations)}")
    print(
        "claim_boundary = finite labelled falsification gate through eight "
        "source vertices; arbitrary-size theorem proved separately under the "
        "explicit marked-extension and singleton-endpoint hypotheses"
    )


if __name__ == "__main__":
    self_test()
