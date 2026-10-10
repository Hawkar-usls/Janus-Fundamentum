#!/usr/bin/env python3
"""Exact controls for zero-sum cycle compression in GF(2)^2-labelled T-joins."""

from __future__ import annotations

import itertools
import json
import random

INF = 10**9


def boundary(n, edges, mask):
    odd = [0] * n
    for i, (a, b) in enumerate(edges):
        if (mask >> i) & 1:
            odd[a] ^= 1
            odd[b] ^= 1
    return tuple(i for i, bit in enumerate(odd) if bit)


def degrees(n, edges, mask):
    deg = [0] * n
    for i, (a, b) in enumerate(edges):
        if (mask >> i) & 1:
            deg[a] += 1
            deg[b] += 1
    return deg


def connected_support(n, edges, mask):
    vertices = set()
    adj = [[] for _ in range(n)]
    for i, (a, b) in enumerate(edges):
        if (mask >> i) & 1:
            vertices.update((a, b))
            adj[a].append(b)
            adj[b].append(a)

    if not vertices:
        return False

    root = next(iter(vertices))
    seen = {root}
    stack = [root]
    while stack:
        a = stack.pop()
        for b in adj[a]:
            if b not in seen:
                seen.add(b)
                stack.append(b)
    return seen == vertices


def is_simple_path(n, edges, mask, u, v):
    if boundary(n, edges, mask) != tuple(sorted((u, v))):
        return False
    deg = degrees(n, edges, mask)
    return (
        deg[u] == 1
        and deg[v] == 1
        and max(deg, default=0) <= 2
        and connected_support(n, edges, mask)
    )


def is_simple_cycle(n, edges, mask):
    if mask == 0 or boundary(n, edges, mask):
        return False
    deg = degrees(n, edges, mask)
    return (
        all(d in (0, 2) for d in deg)
        and connected_support(n, edges, mask)
    )


def label_sum(labels, mask):
    value = 0
    for i, label in enumerate(labels):
        if (mask >> i) & 1:
            value ^= label
    return value


def weight(weights, mask):
    return sum(
        w for i, w in enumerate(weights)
        if (mask >> i) & 1
    )


def gf2_rank(vectors, rank_bound):
    basis = [0] * rank_bound
    rank = 0
    for x in vectors:
        y = x
        while y:
            i = y.bit_length() - 1
            if basis[i]:
                y ^= basis[i]
            else:
                basis[i] = y
                rank += 1
                break
    return rank


def unrestricted_optimum(n, edges, labels, weights, u, v, target):
    best = INF
    for mask in range(1 << len(edges)):
        if boundary(n, edges, mask) != tuple(sorted((u, v))):
            continue
        if label_sum(labels, mask) != target:
            continue
        best = min(best, weight(weights, mask))
    return best


def compressed_optimum(n, edges, labels, weights, u, v, target):
    m = len(edges)
    paths = [
        mask for mask in range(1, 1 << m)
        if is_simple_path(n, edges, mask, u, v)
    ]
    cycles = [
        mask for mask in range(1, 1 << m)
        if is_simple_cycle(n, edges, mask)
    ]

    best = INF

    for path in paths:
        if label_sum(labels, path) == target:
            best = min(best, weight(weights, path))

        for cycle in cycles:
            if path & cycle:
                continue
            lab = label_sum(labels, cycle)
            if lab == 0:
                continue
            union = path | cycle
            if label_sum(labels, union) == target:
                best = min(best, weight(weights, union))

        for i, c1 in enumerate(cycles):
            if path & c1:
                continue
            l1 = label_sum(labels, c1)
            if l1 == 0:
                continue

            for c2 in cycles[i + 1:]:
                if path & c2 or c1 & c2:
                    continue
                l2 = label_sum(labels, c2)
                if l2 == 0:
                    continue
                if gf2_rank([l1, l2], 2) != 2:
                    continue

                union = path | c1 | c2
                if label_sum(labels, union) == target:
                    best = min(best, weight(weights, union))

    return best


def random_controls(seed=9379992, trials=300):
    rng = random.Random(seed)
    checked = 0

    for _ in range(trials):
        n = 5
        possible = list(itertools.combinations(range(n), 2))
        rng.shuffle(possible)
        m = rng.randint(4, 8)
        edges = possible[:m]

        labels = [rng.randrange(4) for _ in edges]
        # Include zero weights to test the cardinality tie-break regime.
        weights = [rng.randrange(4) for _ in edges]
        u, v = rng.sample(range(n), 2)
        target = rng.randrange(4)

        unrestricted = unrestricted_optimum(
            n, edges, labels, weights, u, v, target
        )
        compressed = compressed_optimum(
            n, edges, labels, weights, u, v, target
        )

        assert unrestricted == compressed, (
            edges,
            labels,
            weights,
            u,
            v,
            target,
            unrestricted,
            compressed,
        )
        checked += 1

    return checked


def seven_patterns():
    nonzero = [1, 2, 3]
    patterns = [()]
    patterns.extend((x,) for x in nonzero)
    patterns.extend(itertools.combinations(nonzero, 2))
    assert len(patterns) == 7
    assert all(
        len(p) < 2 or gf2_rank(list(p), 2) == len(p)
        for p in patterns
    )
    return [list(p) for p in patterns]


def main():
    checked = random_controls()
    patterns = seven_patterns()

    print(json.dumps({
        "status": "PASS",
        "group": "GF(2)^2",
        "random_exact_controls": checked,
        "unrestricted_equals_path_plus_at_most_two_cycles": True,
        "cycle_label_condition": "NONZERO_AND_LINEarly_INDEPENDENT",
        "correction_pattern_count": len(patterns),
        "correction_patterns": patterns,
        "claim_ceiling": (
            "STRUCTURAL_COMPRESSION_ONLY__"
            "NO_DETERMINISTIC_POLYNOMIAL_SOLVER_CLAIM"
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
