#!/usr/bin/env python3
"""Exhaust labelled triangle/tree resolvents through seven vertices.

For every labelled undirected tree on 3..7 vertices, orient it toward root zero.
For every tree pivot a->b and every third vertex c, resolve against the directed
triangle b->a, a->c, c->b. Legal resolvents whose underlying graph is a tree
must be the exact same-root exchange

    (D - {a->b}) union {a->c}

with the sibling edge c->b already present in D.

The arbitrary-size theorem is proved separately in
`GT_TRIANGLE_TREE_RESOLVENT_EXACT_EXCHANGE.md`; this program is an independent
finite falsification gate.
"""

from __future__ import annotations

from collections import Counter, deque
from itertools import product

Edge = tuple[int, int]


def undirected_trees(n: int):
    """Generate all labelled trees using Prüfer words."""
    if n == 2:
        yield frozenset({(0, 1)})
        return
    for word in product(range(n), repeat=n - 2):
        degree = [1] * n
        for vertex in word:
            degree[vertex] += 1
        edges = []
        for vertex in word:
            leaf = next(index for index, value in enumerate(degree) if value == 1)
            edges.append(tuple(sorted((leaf, vertex))))
            degree[leaf] -= 1
            degree[vertex] -= 1
        leaves = [index for index, value in enumerate(degree) if value == 1]
        assert len(leaves) == 2
        edges.append(tuple(sorted(leaves)))
        yield frozenset(edges)


def orient_to_root(n: int, edges: frozenset[tuple[int, int]], root: int = 0):
    adjacency = [set() for _ in range(n)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    parent = {root: None}
    queue = deque([root])
    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour in parent:
                continue
            parent[neighbour] = current
            queue.append(neighbour)
    assert len(parent) == n
    return frozenset(
        (vertex, int(parent[vertex]))
        for vertex in range(n)
        if vertex != root
    )


def connected(n: int, edges: frozenset[tuple[int, int]]):
    adjacency = [set() for _ in range(n)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = {0}
    queue = deque([0])
    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour in seen:
                continue
            seen.add(neighbour)
            queue.append(neighbour)
    return len(seen) == n


def underlying(directed: frozenset[Edge]):
    return frozenset(tuple(sorted(edge)) for edge in directed)


def is_tree(n: int, directed: frozenset[Edge]):
    edges = underlying(directed)
    return len(edges) == n - 1 and connected(n, edges)


def is_in_arborescence(n: int, directed: frozenset[Edge], root: int = 0):
    if len(directed) != n - 1 or not is_tree(n, directed):
        return False
    outgoing = Counter(tail for tail, _head in directed)
    if outgoing[root] != 0:
        return False
    if any(outgoing[vertex] != 1 for vertex in range(n) if vertex != root):
        return False
    parent = {tail: head for tail, head in directed}
    for vertex in range(n):
        current = vertex
        seen = set()
        while current != root:
            if current in seen or current not in parent:
                return False
            seen.add(current)
            current = parent[current]
    return True


def subtree_after_pivot(n: int, tree: frozenset[Edge], pivot: Edge):
    a, _b = pivot
    residual = underlying(tree - {pivot})
    adjacency = [set() for _ in range(n)]
    for left, right in residual:
        adjacency[left].add(right)
        adjacency[right].add(left)
    reached = {a}
    queue = deque([a])
    while queue:
        current = queue.popleft()
        for neighbour in adjacency[current]:
            if neighbour in reached:
                continue
            reached.add(neighbour)
            queue.append(neighbour)
    return frozenset(reached)


def self_test() -> None:
    counts: Counter[str] = Counter()
    by_n: Counter[tuple[int, str]] = Counter()
    violations = []
    examples = []

    for n in range(3, 8):
        for undirected_tree in undirected_trees(n):
            tree = orient_to_root(n, undirected_tree)
            counts["tree_parents"] += 1
            by_n[(n, "tree_parents")] += 1

            for pivot in tree:
                a, b = pivot
                pivot_side = subtree_after_pivot(n, tree, pivot)
                residual_tree = tree - {pivot}
                for c in range(n):
                    if c in (a, b):
                        continue
                    counts["triangle_instances"] += 1
                    by_n[(n, "triangle_instances")] += 1

                    path_edges = frozenset({(a, c), (c, b)})
                    candidate = residual_tree | path_edges

                    # Legal clause: no opposite pair survives in the resolvent.
                    if any((head, tail) in candidate for tail, head in candidate):
                        counts["illegal_opposite_pair"] += 1
                        continue
                    counts["legal_resolvents"] += 1

                    if not is_tree(n, candidate):
                        counts["non_tree_resolvents"] += 1
                        if c in pivot_side:
                            counts["non_tree_third_vertex_in_pivot_side"] += 1
                        else:
                            counts["non_tree_third_vertex_in_root_side"] += 1
                        continue

                    counts["tree_resolvents"] += 1
                    by_n[(n, "tree_resolvents")] += 1
                    expected = residual_tree | {(a, c)}
                    conditions = {
                        "third_vertex_on_root_side": c not in pivot_side,
                        "sibling_edge_present": (c, b) in tree,
                        "exact_edge_set": candidate == expected,
                        "same_root_arborescence": is_in_arborescence(n, candidate),
                    }
                    if not all(conditions.values()):
                        violations.append({
                            "n": n,
                            "tree": tuple(sorted(tree)),
                            "pivot": pivot,
                            "third": c,
                            "pivot_side": tuple(sorted(pivot_side)),
                            "candidate": tuple(sorted(candidate)),
                            "expected": tuple(sorted(expected)),
                            "conditions": conditions,
                        })
                    elif len(examples) < 20:
                        examples.append({
                            "n": n,
                            "tree": tuple(sorted(tree)),
                            "pivot": pivot,
                            "third": c,
                            "sibling_edge": (c, b),
                            "new_edge": (a, c),
                            "resolvent": tuple(sorted(candidate)),
                        })

    assert counts["tree_resolvents"] > 0
    assert counts["non_tree_resolvents"] > 0
    assert not violations, violations[:3]

    print("JANUS_TRIANGLE_TREE_RESOLVENT_EXACT_EXCHANGE = PASS")
    print(f"COUNTS = {tuple(sorted(counts.items()))}")
    print(f"BY_N = {tuple(sorted(by_n.items()))}")
    print(f"EXAMPLES = {tuple(examples)}")
    print(f"VIOLATIONS = {tuple(violations)}")
    print(
        "claim_boundary = exhaustive labelled falsification gate through seven "
        "vertices; arbitrary-size triangle/tree theorem proved separately; "
        "Policy-0A reachability of triangle/tree hypotheses remains open"
    )


if __name__ == "__main__":
    self_test()
