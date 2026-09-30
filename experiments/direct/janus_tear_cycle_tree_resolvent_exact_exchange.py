#!/usr/bin/env python3
"""Exhaust directed-cycle/tree resolvents through six vertices.

For every labelled tree on 3..6 vertices oriented toward root zero, every tree
pivot a->b, and every simple directed a-to-b path with at least one intermediate
vertex, treat the reverse pivot b->a plus that path as a directed cycle parent.
Every legal resolvent whose underlying graph is a tree must contain exactly one
new edge: the first path edge. It must be a same-root exact one-edge exchange.

The arbitrary-size theorem is proved separately in
`GT_CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE.md`; this program is an independent
finite falsification gate for the core cycle-path mechanism.
"""

from __future__ import annotations

from collections import Counter, deque
from itertools import permutations, product

Edge = tuple[int, int]


def undirected_trees(n: int):
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


def underlying(directed: frozenset[Edge]):
    return frozenset(tuple(sorted(edge)) for edge in directed)


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


def simple_paths(a: int, b: int, vertices: tuple[int, ...]):
    others = tuple(vertex for vertex in vertices if vertex not in (a, b))
    for length in range(1, len(others) + 1):
        for middle in permutations(others, length):
            yield (a,) + middle + (b,)


def path_edges(path: tuple[int, ...]):
    return frozenset(zip(path, path[1:]))


def self_test() -> None:
    counts: Counter[str] = Counter()
    by_n: Counter[tuple[int, str]] = Counter()
    path_lengths: Counter[int] = Counter()
    tree_path_lengths: Counter[int] = Counter()
    new_edge_positions: Counter[int] = Counter()
    violations = []
    examples = []

    for n in range(3, 7):
        vertices = tuple(range(n))
        for undirected_tree in undirected_trees(n):
            tree = orient_to_root(n, undirected_tree)
            counts["tree_parents"] += 1
            by_n[(n, "tree_parents")] += 1

            for pivot in tree:
                a, b = pivot
                forest = tree - {pivot}
                for path in simple_paths(a, b, vertices):
                    edges = path_edges(path)
                    counts["cycle_paths"] += 1
                    path_lengths[len(edges)] += 1
                    candidate = forest | edges

                    # A legal resolvent cannot contain opposite directed edges.
                    if any((head, tail) in candidate for tail, head in candidate):
                        counts["illegal_opposite_pair"] += 1
                        continue
                    counts["legal_resolvents"] += 1

                    if not is_tree(n, candidate):
                        counts["non_tree_resolvents"] += 1
                        continue

                    counts["tree_resolvents"] += 1
                    by_n[(n, "tree_resolvents")] += 1
                    tree_path_lengths[len(edges)] += 1
                    new_edges = tuple(edge for edge in edges if edge not in forest)
                    first = (path[0], path[1])
                    for index, edge in enumerate(zip(path, path[1:])):
                        if edge not in forest:
                            new_edge_positions[index] += 1

                    expected = forest | {first}
                    conditions = {
                        "exactly_one_new_path_edge": len(new_edges) == 1,
                        "first_path_edge_is_new": new_edges == (first,),
                        "all_later_path_edges_duplicate_tree": all(
                            edge in forest for edge in tuple(zip(path, path[1:]))[1:]
                        ),
                        "exact_edge_set": candidate == expected,
                        "same_root_arborescence": is_in_arborescence(n, candidate),
                    }
                    if not all(conditions.values()):
                        violations.append({
                            "n": n,
                            "tree": tuple(sorted(tree)),
                            "pivot": pivot,
                            "path": path,
                            "forest": tuple(sorted(forest)),
                            "candidate": tuple(sorted(candidate)),
                            "new_edges": new_edges,
                            "conditions": conditions,
                        })
                    elif len(examples) < 20:
                        examples.append({
                            "n": n,
                            "pivot": pivot,
                            "path": path,
                            "new_edge": first,
                            "resolvent": tuple(sorted(candidate)),
                        })

    assert counts["tree_resolvents"] > 0
    assert counts["non_tree_resolvents"] > 0
    assert set(new_edge_positions) == {0}
    assert not violations, violations[:3]

    print("JANUS_CYCLE_TREE_RESOLVENT_EXACT_EXCHANGE = PASS")
    print(f"COUNTS = {tuple(sorted(counts.items()))}")
    print(f"BY_N = {tuple(sorted(by_n.items()))}")
    print(f"PATH_LENGTHS = {tuple(sorted(path_lengths.items()))}")
    print(f"TREE_PATH_LENGTHS = {tuple(sorted(tree_path_lengths.items()))}")
    print(f"NEW_EDGE_POSITIONS = {tuple(sorted(new_edge_positions.items()))}")
    print(f"EXAMPLES = {tuple(examples)}")
    print(f"VIOLATIONS = {tuple(violations)}")
    print(
        "claim_boundary = exhaustive simple-cycle-path falsification gate through "
        "six vertices; arbitrary-size cycle/tree theorem proved separately; "
        "Policy-0A reachability of cycle/tree/tree-result hypotheses remains open"
    )


if __name__ == "__main__":
    self_test()
