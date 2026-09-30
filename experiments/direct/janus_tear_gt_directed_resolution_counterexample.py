#!/usr/bin/env python3
"""Certify a minimal abstract failure of directed safety under Resolution.

Safe directed component clauses are provisionally classified as:
- containing a directed cycle; or
- having a root reachable from every component; or
- containing no external edge.

This class is not closed under arbitrary Resolution.  The explicit three-
component counterexample prevents C024 from silently replacing the required
GT-specific theorem by a false generic graph statement.
"""

from __future__ import annotations

from itertools import combinations, product

Edge = tuple[int, int]
Clause = frozenset[Edge]


def has_directed_cycle(vertex_count: int, edges: Clause) -> bool:
    adjacency = [[] for _ in range(vertex_count)]
    for tail, head in edges:
        adjacency[tail].append(head)
    state = [0] * vertex_count

    def visit(vertex: int) -> bool:
        state[vertex] = 1
        for other in adjacency[vertex]:
            if state[other] == 1:
                return True
            if state[other] == 0 and visit(other):
                return True
        state[vertex] = 2
        return False

    return any(
        state[vertex] == 0 and visit(vertex)
        for vertex in range(vertex_count)
    )


def reachable_roots(vertex_count: int, edges: Clause) -> tuple[int, ...]:
    reverse = [[] for _ in range(vertex_count)]
    for tail, head in edges:
        reverse[head].append(tail)
    roots = []
    for root in range(vertex_count):
        seen = {root}
        stack = [root]
        while stack:
            vertex = stack.pop()
            for other in reverse[vertex]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        if len(seen) == vertex_count:
            roots.append(root)
    return tuple(roots)


def safe(vertex_count: int, edges: Clause) -> bool:
    return (
        not edges
        or has_directed_cycle(vertex_count, edges)
        or bool(reachable_roots(vertex_count, edges))
    )


def tautological(edges: Clause) -> bool:
    return any((head, tail) in edges for tail, head in edges)


def resolve(left: Clause, right: Clause, pivot: Edge) -> Clause:
    reverse = (pivot[1], pivot[0])
    assert pivot in left and reverse in right
    resolvent = frozenset((set(left) - {pivot}) | (set(right) - {reverse}))
    assert not tautological(resolvent)
    return resolvent


def all_nontautological_clauses(vertex_count: int):
    unordered = tuple(combinations(range(vertex_count), 2))
    for choices in product((0, 1, 2), repeat=len(unordered)):
        edges = set()
        for (left, right), choice in zip(unordered, choices):
            if choice == 1:
                edges.add((left, right))
            elif choice == 2:
                edges.add((right, left))
        yield frozenset(edges)


def first_counterexample(vertex_count: int):
    clauses = tuple(all_nontautological_clauses(vertex_count))
    safe_clauses = tuple(clause for clause in clauses if safe(vertex_count, clause))
    for tail in range(vertex_count):
        for head in range(vertex_count):
            if tail == head:
                continue
            pivot = (tail, head)
            reverse = (head, tail)
            for left in safe_clauses:
                if pivot not in left or reverse in left:
                    continue
                for right in safe_clauses:
                    if reverse not in right or pivot in right:
                        continue
                    resolvent = frozenset(
                        (set(left) - {pivot}) | (set(right) - {reverse})
                    )
                    if tautological(resolvent):
                        continue
                    if not safe(vertex_count, resolvent):
                        return pivot, left, right, resolvent
    return None


def self_test() -> None:
    left: Clause = frozenset({(0, 1), (2, 1)})
    right: Clause = frozenset({(1, 0), (2, 1)})
    pivot = (0, 1)
    resolvent = resolve(left, right, pivot)

    assert safe(3, left)
    assert reachable_roots(3, left) == (1,)
    assert safe(3, right)
    assert reachable_roots(3, right) == (0,)
    assert resolvent == frozenset({(2, 1)})
    assert not safe(3, resolvent)
    assert first_counterexample(2) is None
    assert first_counterexample(3) == (pivot, left, right, resolvent)

    print("JANUS_GT_DIRECTED_RESOLUTION_COUNTEREXAMPLE = PASS")
    print("minimum_component_count = 3")
    print(f"left = {tuple(sorted(left))}")
    print(f"left_roots = {reachable_roots(3, left)}")
    print(f"right = {tuple(sorted(right))}")
    print(f"right_roots = {reachable_roots(3, right)}")
    print(f"pivot = {pivot}")
    print(f"resolvent = {tuple(sorted(resolvent))}")
    print("resolvent_class = UNSAFE_DIRECTED_FOREST")
    print("claim_boundary = abstract graph counterexample; realizability in smart-GT Policy-0A states remains open")


if __name__ == "__main__":
    self_test()
