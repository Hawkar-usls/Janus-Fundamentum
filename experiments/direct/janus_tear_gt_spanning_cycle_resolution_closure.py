#!/usr/bin/env python3
"""Exhaustively sanity-check the spanning/cycle Resolution closure lemma.

For abstract quotient digraphs on 3 and 4 vertices, enumerate every
non-tautological clause (each comparison variable is absent or has one of its
two orientations), every mixed parent pair

    COMPONENT_SPANNING + DIRECTED_CYCLE,

and every legal complementary pivot.  Assert that the resolvent is always
component-spanning or contains a directed cycle.

The checker also preserves the minimal three-vertex regression witness showing
that a shared non-bridge may become a bridge even though the resolvent remains
component-spanning.  Thus it tests the proved safety theorem without silently
reintroducing the false binary-origin claim.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

Edge = tuple[int, int]
Clause = frozenset[Edge]


def variables(vertex_count: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(vertex_count)
        for right in range(left + 1, vertex_count)
    )


def clauses(vertex_count: int) -> tuple[Clause, ...]:
    result = []
    pairs = variables(vertex_count)
    for choices in product((0, 1, -1), repeat=len(pairs)):
        edges = []
        for (left, right), choice in zip(pairs, choices):
            if choice == 1:
                edges.append((left, right))
            elif choice == -1:
                edges.append((right, left))
        result.append(frozenset(edges))
    return tuple(result)


def has_directed_cycle(vertex_count: int, clause: Clause) -> bool:
    adjacency = [[] for _ in range(vertex_count)]
    for tail, head in clause:
        adjacency[tail].append(head)

    colour = [0] * vertex_count

    def visit(vertex: int) -> bool:
        colour[vertex] = 1
        for neighbour in adjacency[vertex]:
            if colour[neighbour] == 1:
                return True
            if colour[neighbour] == 0 and visit(neighbour):
                return True
        colour[vertex] = 2
        return False

    return any(colour[v] == 0 and visit(v) for v in range(vertex_count))


def component_count(vertex_count: int, clause: Clause) -> int:
    parent = list(range(vertex_count))

    def find(vertex: int) -> int:
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for tail, head in clause:
        union(tail, head)
    return len({find(vertex) for vertex in range(vertex_count)})


def is_component_spanning(vertex_count: int, clause: Clause) -> bool:
    return component_count(vertex_count, clause) == 1


def safety_class(vertex_count: int, clause: Clause) -> str:
    if has_directed_cycle(vertex_count, clause):
        return "DIRECTED_CYCLE"
    if is_component_spanning(vertex_count, clause):
        return "COMPONENT_SPANNING"
    if not clause:
        return "INTERNAL_ONLY"
    return "UNSAFE_ACYCLIC_LOW_RANK"


def is_tautological(clause: Clause) -> bool:
    return any((head, tail) in clause for tail, head in clause)


def bridge_edges(vertex_count: int, clause: Clause) -> frozenset[Edge]:
    baseline = component_count(vertex_count, clause)
    return frozenset(
        edge
        for edge in clause
        if component_count(vertex_count, clause - {edge}) > baseline
    )


def resolve(left: Clause, right: Clause, pivot: Edge) -> Clause | None:
    opposite = (pivot[1], pivot[0])
    if pivot not in left or opposite not in right:
        return None
    resolvent = frozenset((left - {pivot}) | (right - {opposite}))
    if is_tautological(resolvent):
        return None
    return resolvent


def regression_witness() -> None:
    left = frozenset({(0, 1), (0, 2), (1, 2)})
    right = frozenset({(0, 1), (1, 2), (2, 0)})
    pivot = (0, 2)
    bad = (0, 1)
    resolvent = resolve(left, right, pivot)

    assert resolvent == frozenset({(0, 1), (1, 2)})
    assert safety_class(3, left) == "COMPONENT_SPANNING"
    assert safety_class(3, right) == "DIRECTED_CYCLE"
    assert bad not in bridge_edges(3, left)
    assert bad not in bridge_edges(3, right)
    assert bad in bridge_edges(3, resolvent)
    assert safety_class(3, resolvent) == "COMPONENT_SPANNING"


def audit(vertex_count: int) -> dict[str, object]:
    family = clauses(vertex_count)
    spanning = tuple(
        clause
        for clause in family
        if safety_class(vertex_count, clause) == "COMPONENT_SPANNING"
    )
    cyclic = tuple(
        clause
        for clause in family
        if safety_class(vertex_count, clause) == "DIRECTED_CYCLE"
    )

    counts: Counter[str] = Counter()
    result_classes: Counter[str] = Counter()
    unsafe_examples = []

    for left in spanning:
        for right in cyclic:
            counts["mixed_parent_pairs"] += 1
            for pivot in left:
                opposite = (pivot[1], pivot[0])
                if opposite not in right:
                    continue
                counts["complementary_pivots"] += 1
                raw = frozenset((left - {pivot}) | (right - {opposite}))
                if is_tautological(raw):
                    counts["tautological_resolvents"] += 1
                    continue
                counts["legal_resolvents"] += 1
                classification = safety_class(vertex_count, raw)
                result_classes[classification] += 1
                if classification == "UNSAFE_ACYCLIC_LOW_RANK":
                    counts["unsafe_resolvents"] += 1
                    if len(unsafe_examples) < 20:
                        unsafe_examples.append(
                            {
                                "left": tuple(sorted(left)),
                                "right": tuple(sorted(right)),
                                "pivot": pivot,
                                "resolvent": tuple(sorted(raw)),
                            }
                        )

    return {
        "vertex_count": vertex_count,
        "clause_count": len(family),
        "spanning_parent_count": len(spanning),
        "cyclic_parent_count": len(cyclic),
        "counts": tuple(sorted(counts.items())),
        "result_classes": tuple(sorted(result_classes.items())),
        "unsafe_examples": tuple(unsafe_examples),
    }


def self_test() -> None:
    regression_witness()
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_classes: Counter[str] = Counter()

    for vertex_count in (3, 4):
        data = audit(vertex_count)
        aggregate.update(dict(data["counts"]))
        aggregate_classes.update(dict(data["result_classes"]))
        assert dict(data["counts"]).get("unsafe_resolvents", 0) == 0
        rows.append(data)
        print(f"VERTEX_COUNT = {vertex_count}")
        print(f"  clause_count = {data['clause_count']}")
        print(f"  spanning_parent_count = {data['spanning_parent_count']}")
        print(f"  cyclic_parent_count = {data['cyclic_parent_count']}")
        print(f"  counts = {data['counts']}")
        print(f"  result_classes = {data['result_classes']}")
        print(f"  unsafe_examples = {data['unsafe_examples']}")

    assert aggregate["legal_resolvents"] > 0
    assert aggregate_classes["UNSAFE_ACYCLIC_LOW_RANK"] == 0
    assert (
        aggregate_classes["COMPONENT_SPANNING"]
        + aggregate_classes["DIRECTED_CYCLE"]
        == aggregate["legal_resolvents"]
    )

    print("JANUS_GT_SPANNING_CYCLE_RESOLUTION_CLOSURE = PASS")
    print("REGRESSION_WITNESS = bridge_birth_but_component_spanning")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate.items()))}")
    print(f"AGGREGATE_RESULT_CLASSES = {tuple(sorted(aggregate_classes.items()))}")
    print(
        "claim_boundary = exhaustive abstract sanity check for 3 and 4 quotient "
        "vertices; theorem is established separately by the cut proof"
    )


if __name__ == "__main__":
    self_test()
