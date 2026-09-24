#!/usr/bin/env python3
"""Exact controls for GF(2)^2 labelled T-join separability."""

from __future__ import annotations
import itertools
import json
import random

INF = 10**9
PATTERNS = [(), (1,), (2,), (3,), (1,2), (1,3), (2,3)]


def boundary(n, edges, mask):
    odd = [0] * n
    for i, (a, b) in enumerate(edges):
        if (mask >> i) & 1:
            odd[a] ^= 1
            odd[b] ^= 1
    return tuple(i for i, bit in enumerate(odd) if bit)


def label_sum(labels, mask):
    out = 0
    for i, a in enumerate(labels):
        if (mask >> i) & 1:
            out ^= a
    return out


def weight(weights, mask):
    return sum(w for i, w in enumerate(weights) if (mask >> i) & 1)


def degrees(n, edges, mask):
    d = [0] * n
    for i, (a, b) in enumerate(edges):
        if (mask >> i) & 1:
            d[a] += 1
            d[b] += 1
    return d


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
    d = degrees(n, edges, mask)
    return d[u] == 1 and d[v] == 1 and max(d, default=0) <= 2 and connected_support(n, edges, mask)


def is_simple_cycle(n, edges, mask):
    if mask == 0 or boundary(n, edges, mask):
        return False
    d = degrees(n, edges, mask)
    return all(x in (0, 2) for x in d) and connected_support(n, edges, mask)


def path_cost(n, edges, labels, weights, u, v, target, forbidden=None):
    best = INF
    for mask in range(1, 1 << len(edges)):
        if forbidden is not None and ((mask >> forbidden) & 1):
            continue
        if is_simple_path(n, edges, mask, u, v) and label_sum(labels, mask) == target:
            best = min(best, weight(weights, mask))
    return best


def cycle_cost(n, edges, labels, weights, target):
    return min(
        [weight(weights, mask) for mask in range(1, 1 << len(edges))
         if is_simple_cycle(n, edges, mask) and label_sum(labels, mask) == target]
        or [INF]
    )


def unrestricted_tjoin(n, edges, labels, weights, u, v, target):
    wanted = tuple(sorted((u, v)))
    return min(
        [weight(weights, mask) for mask in range(1 << len(edges))
         if boundary(n, edges, mask) == wanted and label_sum(labels, mask) == target]
        or [INF]
    )


def separable_formula(n, edges, labels, weights, u, v, target):
    p = {h: path_cost(n, edges, labels, weights, u, v, h) for h in range(4)}
    c = {h: cycle_cost(n, edges, labels, weights, h) for h in (1,2,3)}
    best = INF
    for pattern in PATTERNS:
        correction = 0
        cost = 0
        for h in pattern:
            correction ^= h
            cost += c[h]
        best = min(best, p[target ^ correction] + cost)
    return best


def cycle_via_paths(n, edges, labels, weights, target):
    best = INF
    for i, (u, v) in enumerate(edges):
        pcost = path_cost(n, edges, labels, weights, u, v, target ^ labels[i], forbidden=i)
        best = min(best, weights[i] + pcost)
    return best


def random_controls(seed=9379992, trials=300):
    rng = random.Random(seed)
    tj = 0
    cy = 0
    for _ in range(trials):
        n = 5
        possible = list(itertools.combinations(range(n), 2))
        rng.shuffle(possible)
        m = rng.randint(3, 8)
        edges = possible[:m]
        labels = [rng.randrange(4) for _ in edges]
        weights = [rng.randrange(4) for _ in edges]
        u, v = rng.sample(range(n), 2)
        target = rng.randrange(4)

        exact = unrestricted_tjoin(n, edges, labels, weights, u, v, target)
        separated = separable_formula(n, edges, labels, weights, u, v, target)
        assert exact == separated, ("separability", edges, labels, weights, u, v, target, exact, separated)
        tj += 1

        for h in (1,2,3):
            direct = cycle_cost(n, edges, labels, weights, h)
            via = cycle_via_paths(n, edges, labels, weights, h)
            assert direct == via, ("cycle_to_path", h, edges, labels, weights, direct, via)
            cy += 1
    return tj, cy


def main():
    tj, cy = random_controls()
    print(json.dumps({
        "status":"PASS",
        "group":"GF(2)^2",
        "random_tjoin_separability_controls":tj,
        "cycle_to_path_controls":cy,
        "correction_patterns":[list(p) for p in PATTERNS],
        "claim_ceiling":"EXACT_ORACLE_REDUCTION_ONLY__NO_DETERMINISTIC_PRESCRIBED_LABEL_PATH_SOLVER_CLAIM"
    }, indent=2))


if __name__ == "__main__":
    main()
