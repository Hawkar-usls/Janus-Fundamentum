#!/usr/bin/env python3
"""Classify abstract parent classes for fresh bridge births on 3/4 vertices.

A legal directed clause chooses for every unordered vertex pair exactly one of
absent / low->high / high->low.  For every pivot variable and both opposite
parent orientations, the script forms the legal Resolution union, removes the
pivot occurrences, and classifies result bridges which were not bridges in any
parent containing the same directed occurrence.

This is a discovery certificate.  It tests whether the finite GT observation

    fresh non-tail birth => DIRECTED_CYCLE x COMPONENT_SPANNING

is a pure graph consequence.  No such theorem is assumed.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

Edge = tuple[int, int]
Clause = tuple[Edge, ...]


def variables(n: int):
    return tuple((low, high) for low in range(n) for high in range(low + 1, n))


def clauses(n: int):
    pairs = variables(n)
    for choices in product((0, 1, -1), repeat=len(pairs)):
        edges = []
        for (low, high), choice in zip(pairs, choices):
            if choice > 0:
                edges.append((low, high))
            elif choice < 0:
                edges.append((high, low))
        yield tuple(edges)


def directed_cycle(n: int, clause: Clause) -> bool:
    adjacency = [[] for _ in range(n)]
    for tail, head in clause:
        adjacency[tail].append(head)
    colour = [0] * n

    def visit(vertex: int) -> bool:
        colour[vertex] = 1
        for neighbour in adjacency[vertex]:
            if colour[neighbour] == 1:
                return True
            if colour[neighbour] == 0 and visit(neighbour):
                return True
        colour[vertex] = 2
        return False

    return any(colour[v] == 0 and visit(v) for v in range(n))


def components(n: int, clause: Clause, removed: Edge | None = None):
    adjacency = [set() for _ in range(n)]
    for edge in clause:
        if edge == removed:
            continue
        left, right = edge
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(range(n))
    parts = []
    while unseen:
        start = min(unseen)
        stack = [start]
        unseen.remove(start)
        part = {start}
        while stack:
            current = stack.pop()
            for neighbour in adjacency[current]:
                if neighbour not in unseen:
                    continue
                unseen.remove(neighbour)
                part.add(neighbour)
                stack.append(neighbour)
        parts.append(frozenset(part))
    return tuple(sorted(parts, key=lambda p: (len(p), tuple(sorted(p)))))


def classification(n: int, clause: Clause) -> str:
    if directed_cycle(n, clause):
        return "DIRECTED_CYCLE"
    if len(components(n, clause)) == 1:
        return "COMPONENT_SPANNING"
    if not clause:
        return "INTERNAL_ONLY"
    return "UNSAFE_ACYCLIC_LOW_RANK"


def bridge_cut(n: int, clause: Clause, edge: Edge):
    if edge not in clause:
        return None
    parts = components(n, clause, removed=edge)
    if len(parts) != 2:
        return None
    return frozenset(parts)


def legal_union(left: Clause, right: Clause, pivot_forward: Edge, pivot_reverse: Edge):
    residual = set(left)
    residual.discard(pivot_forward)
    residual.update(edge for edge in right if edge != pivot_reverse)
    if any((head, tail) in residual for tail, head in residual):
        return None
    return tuple(sorted(residual))


def role(n: int, edge: Edge, cut) -> str:
    tail, _head = edge
    tail_side = next(part for part in cut if tail in part)
    return "TAIL_SINGLETON" if len(tail_side) == 1 else "NON_TAIL"


def audit(n: int):
    all_clauses = tuple(clauses(n))
    classes = {clause: classification(n, clause) for clause in all_clauses}
    safe = tuple(
        clause
        for clause in all_clauses
        if classes[clause] in {"DIRECTED_CYCLE", "COMPONENT_SPANNING", "INTERNAL_ONLY"}
    )
    by_edge = {edge: [] for pair in variables(n) for edge in (pair, pair[::-1])}
    for clause in safe:
        for edge in clause:
            by_edge[edge].append(clause)

    counts: Counter[str] = Counter()
    parent_pairs: Counter[tuple[str, str]] = Counter()
    non_tail_pairs: Counter[tuple[str, str]] = Counter()
    examples = []

    for low, high in variables(n):
        forward = (low, high)
        reverse = (high, low)
        for left in by_edge[forward]:
            for right in by_edge[reverse]:
                result = legal_union(left, right, forward, reverse)
                if result is None:
                    counts["illegal_resolvents"] += 1
                    continue
                if classification(n, result) != "COMPONENT_SPANNING":
                    continue
                counts["spanning_resolvents"] += 1
                pair_class = tuple(sorted((classes[left], classes[right])))
                for edge in result:
                    cut = bridge_cut(n, result, edge)
                    if cut is None:
                        continue
                    counts["result_bridge_occurrences"] += 1
                    source_bridges = []
                    if edge in left:
                        source_bridges.append(bridge_cut(n, left, edge) is not None)
                    if edge in right:
                        source_bridges.append(bridge_cut(n, right, edge) is not None)
                    assert source_bridges
                    if any(source_bridges):
                        counts["inherited_bridge_occurrences"] += 1
                        continue
                    counts["fresh_bridge_occurrences"] += 1
                    parent_pairs[pair_class] += 1
                    edge_role = role(n, edge, cut)
                    if edge_role == "NON_TAIL":
                        counts["fresh_non_tail_occurrences"] += 1
                        non_tail_pairs[pair_class] += 1
                    else:
                        counts["fresh_tail_singleton_occurrences"] += 1
                    if len(examples) < 80:
                        examples.append({
                            "n": n,
                            "pivot": (forward, reverse),
                            "left": left,
                            "right": right,
                            "left_class": classes[left],
                            "right_class": classes[right],
                            "result": result,
                            "fresh_bridge": edge,
                            "role": edge_role,
                            "cut": tuple(sorted(tuple(sorted(part)) for part in cut)),
                        })

    return {
        "n": n,
        "clause_count": len(all_clauses),
        "safe_clause_count": len(safe),
        "counts": tuple(sorted(counts.items())),
        "fresh_parent_pairs": tuple(sorted(parent_pairs.items(), key=repr)),
        "fresh_non_tail_parent_pairs": tuple(sorted(non_tail_pairs.items(), key=repr)),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_pairs: Counter[tuple[str, str]] = Counter()
    aggregate_non_tail: Counter[tuple[str, str]] = Counter()
    rows = []

    for n in (3, 4):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_pairs.update(dict(data["fresh_parent_pairs"]))
        aggregate_non_tail.update(dict(data["fresh_non_tail_parent_pairs"]))
        rows.append(data)
        print(f"VERTEX_COUNT = {n}")
        print(f"  clause_count = {data['clause_count']}")
        print(f"  safe_clause_count = {data['safe_clause_count']}")
        print(f"  counts = {data['counts']}")
        print(f"  fresh_parent_pairs = {data['fresh_parent_pairs']}")
        print(f"  fresh_non_tail_parent_pairs = {data['fresh_non_tail_parent_pairs']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["fresh_bridge_occurrences"] > 0
    assert aggregate_counts["fresh_non_tail_occurrences"] > 0
    print("JANUS_ABSTRACT_FRESH_BRIDGE_PARENT_CLASS = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_FRESH_PARENT_PAIRS = {tuple(sorted(aggregate_pairs.items(), key=repr))}")
    print(
        "AGGREGATE_FRESH_NON_TAIL_PARENT_PAIRS = "
        f"{tuple(sorted(aggregate_non_tail.items(), key=repr))}"
    )
    print(f"ROWS = {tuple(rows)}")
    print(
        "claim_boundary = exhaustive abstract legal-clause discovery on three "
        "and four singleton vertices; GT-specific reachability remains open"
    )


if __name__ == "__main__":
    self_test()
