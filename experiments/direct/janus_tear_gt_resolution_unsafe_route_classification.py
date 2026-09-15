#!/usr/bin/env python3
"""Exhaustively verify the exact abstract unsafe Resolution route.

On quotient digraphs with 3 and 4 vertices, enumerate all non-tautological
clauses, all parent pairs from the cycle-or-spanning safe family, and all legal
complementary pivots.  Every unsafe acyclic low-rank resolvent must come from:

- two component-spanning parents;
- a pivot that is a bridge in both; and
- identical undirected bridge cuts.

The proof of this classification is graph-theoretic and appears in
`GT_RESOLUTION_UNSAFE_ROUTE_CLASSIFICATION.md`; this program is an exhaustive
small-instance falsification gate and regression suite.
"""

from __future__ import annotations

from collections import Counter, deque

from janus_tear_gt_spanning_cycle_resolution_closure import (
    Clause,
    Edge,
    bridge_edges,
    clauses,
    resolve,
    safety_class,
)

SAFE_CLASSES = {
    "COMPONENT_SPANNING",
    "DIRECTED_CYCLE",
    "INTERNAL_ONLY",
}


def bridge_cut(vertex_count: int, clause: Clause, pivot: Edge) -> tuple[int, ...]:
    assert pivot in clause
    reduced = clause - {pivot}
    adjacency = [[] for _ in range(vertex_count)]
    for left, right in reduced:
        adjacency[left].append(right)
        adjacency[right].append(left)

    start = pivot[0]
    reached = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for neighbour in adjacency[vertex]:
            if neighbour not in reached:
                reached.add(neighbour)
                queue.append(neighbour)

    complement = set(range(vertex_count)) - reached
    assert complement
    left = tuple(sorted(reached))
    right = tuple(sorted(complement))
    return min(left, right)


def minimum_witness() -> None:
    left = frozenset({(0, 1), (2, 1)})
    right = frozenset({(1, 0), (2, 1)})
    pivot = (0, 1)
    resolvent = resolve(left, right, pivot)

    assert resolvent == frozenset({(2, 1)})
    assert safety_class(3, left) == "COMPONENT_SPANNING"
    assert safety_class(3, right) == "COMPONENT_SPANNING"
    assert safety_class(3, resolvent) == "UNSAFE_ACYCLIC_LOW_RANK"
    assert pivot in bridge_edges(3, left)
    opposite = (pivot[1], pivot[0])
    assert opposite in bridge_edges(3, right)
    assert bridge_cut(3, left, pivot) == bridge_cut(3, right, opposite)


def audit(vertex_count: int) -> dict[str, object]:
    family = clauses(vertex_count)
    safe = tuple(
        clause
        for clause in family
        if safety_class(vertex_count, clause) in SAFE_CLASSES
    )

    counts: Counter[str] = Counter()
    parent_pairs: Counter[tuple[str, str]] = Counter()
    unsafe_parent_pairs: Counter[tuple[str, str]] = Counter()
    unsafe_cut_relation: Counter[str] = Counter()
    result_classes: Counter[str] = Counter()
    violations = []

    for left in safe:
        left_class = safety_class(vertex_count, left)
        for right in safe:
            right_class = safety_class(vertex_count, right)
            pair = tuple(sorted((left_class, right_class)))
            parent_pairs[pair] += 1
            for pivot in left:
                opposite = (pivot[1], pivot[0])
                if opposite not in right:
                    continue
                counts["complementary_pivots"] += 1
                resolvent = resolve(left, right, pivot)
                if resolvent is None:
                    counts["tautological_or_rejected"] += 1
                    continue
                counts["legal_resolvents"] += 1
                result_class = safety_class(vertex_count, resolvent)
                result_classes[result_class] += 1

                if "DIRECTED_CYCLE" in pair:
                    counts["cycle_parent_legal_resolvents"] += 1
                    if result_class == "UNSAFE_ACYCLIC_LOW_RANK":
                        violations.append({
                            "kind": "CYCLE_PARENT_UNSAFE",
                            "left": tuple(sorted(left)),
                            "right": tuple(sorted(right)),
                            "pivot": pivot,
                            "resolvent": tuple(sorted(resolvent)),
                        })

                if result_class != "UNSAFE_ACYCLIC_LOW_RANK":
                    continue

                counts["unsafe_resolvents"] += 1
                unsafe_parent_pairs[pair] += 1
                left_bridge = pivot in bridge_edges(vertex_count, left)
                right_bridge = opposite in bridge_edges(vertex_count, right)
                same_cut = False
                if left_bridge and right_bridge:
                    same_cut = (
                        bridge_cut(vertex_count, left, pivot)
                        == bridge_cut(vertex_count, right, opposite)
                    )
                unsafe_cut_relation[
                    "SAME_CUT" if same_cut else "NOT_SAME_CUT"
                ] += 1

                if not (
                    pair
                    == ("COMPONENT_SPANNING", "COMPONENT_SPANNING")
                    and left_bridge
                    and right_bridge
                    and same_cut
                ):
                    violations.append({
                        "kind": "UNSAFE_OUTSIDE_EXACT_ROUTE",
                        "left_class": left_class,
                        "right_class": right_class,
                        "left": tuple(sorted(left)),
                        "right": tuple(sorted(right)),
                        "pivot": pivot,
                        "left_bridge": left_bridge,
                        "right_bridge": right_bridge,
                        "same_cut": same_cut,
                        "resolvent": tuple(sorted(resolvent)),
                    })

    return {
        "vertex_count": vertex_count,
        "clause_count": len(family),
        "safe_clause_count": len(safe),
        "counts": tuple(sorted(counts.items())),
        "parent_pairs": tuple(sorted(parent_pairs.items(), key=repr)),
        "unsafe_parent_pairs": tuple(sorted(unsafe_parent_pairs.items(), key=repr)),
        "unsafe_cut_relation": tuple(sorted(unsafe_cut_relation.items())),
        "result_classes": tuple(sorted(result_classes.items())),
        "violations": tuple(violations),
    }


def self_test() -> None:
    minimum_witness()
    aggregate_counts: Counter[str] = Counter()
    aggregate_unsafe_pairs: Counter[tuple[str, str]] = Counter()
    aggregate_cut: Counter[str] = Counter()
    rows = []

    for vertex_count in (3, 4):
        data = audit(vertex_count)
        assert not data["violations"]
        aggregate_counts.update(dict(data["counts"]))
        aggregate_unsafe_pairs.update(dict(data["unsafe_parent_pairs"]))
        aggregate_cut.update(dict(data["unsafe_cut_relation"]))
        rows.append(data)
        print(f"VERTEX_COUNT = {vertex_count}")
        print(f"  clause_count = {data['clause_count']}")
        print(f"  safe_clause_count = {data['safe_clause_count']}")
        print(f"  counts = {data['counts']}")
        print(f"  unsafe_parent_pairs = {data['unsafe_parent_pairs']}")
        print(f"  unsafe_cut_relation = {data['unsafe_cut_relation']}")
        print(f"  result_classes = {data['result_classes']}")
        print(f"  violations = {data['violations']}")

    assert aggregate_counts["unsafe_resolvents"] > 0
    assert aggregate_unsafe_pairs == Counter({
        ("COMPONENT_SPANNING", "COMPONENT_SPANNING"):
            aggregate_counts["unsafe_resolvents"]
    })
    assert aggregate_cut == Counter({
        "SAME_CUT": aggregate_counts["unsafe_resolvents"]
    })

    print("JANUS_GT_RESOLUTION_UNSAFE_ROUTE_CLASSIFICATION = PASS")
    print("MINIMUM_WITNESS = spanning_spanning_same_cut_double_bridge")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_UNSAFE_PARENT_PAIRS = {tuple(sorted(aggregate_unsafe_pairs.items(), key=repr))}")
    print(f"AGGREGATE_UNSAFE_CUT_RELATION = {tuple(sorted(aggregate_cut.items()))}")
    print(
        "claim_boundary = exhaustive abstract check on 3 and 4 quotient vertices; "
        "the exact route is proved separately by the graph classification theorem"
    )


if __name__ == "__main__":
    self_test()
