#!/usr/bin/env python3
"""Exact controls for GF(2)^2 pairwise-parity path-cost collapse."""

from __future__ import annotations

import json
import math
import random

INF = math.inf


def dot2(k: int, x: int) -> int:
    return (k & x).bit_count() & 1


def all_simple_paths(n, edges, labels, weights, s, t):
    adj = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))

    out = []

    def dfs(u, visited, cost, label, path):
        if u == t:
            out.append((cost, label, tuple(path)))
            return
        for v, e in adj[u]:
            if v in visited:
                continue
            visited.add(v)
            dfs(
                v,
                visited,
                cost + weights[e],
                label ^ labels[e],
                path + [e],
            )
            visited.remove(v)

    dfs(s, {s}, 0, 0, [])
    return out


def exact_check(n, edges, labels, weights, s, t):
    paths = all_simple_paths(n, edges, labels, weights, s, t)

    m = [INF] * 4
    for cost, label, _ in paths:
        m[label] = min(m[label], cost)

    pair = {}

    for a in range(4):
        for b in range(a + 1, 4):
            h = a ^ b
            functionals = [
                k for k in (1, 2, 3)
                if dot2(k, h) == 0
            ]
            assert len(functionals) == 1
            k = functionals[0]

            bit = dot2(k, a)
            assert dot2(k, b) == bit

            fiber = {
                x for x in range(4)
                if dot2(k, x) == bit
            }
            assert fiber == {a, b}

            parity_best = min(
                (
                    cost
                    for cost, label, _ in paths
                    if dot2(k, label) == bit
                ),
                default=INF,
            )

            expected = min(m[a], m[b])
            assert parity_best == expected

            pair[(a, b)] = parity_best

    M = max(pair.values(), default=INF)

    exceptions = []

    for c in range(4):
        if m[c] == INF:
            continue

        Rc = max(
            pair[tuple(sorted((c, d)))]
            for d in range(4)
            if d != c
        )

        other_max = max(
            m[d] for d in range(4) if d != c
        )

        if m[c] <= other_max:
            assert Rc == m[c]
        else:
            assert Rc == other_max
            assert Rc < m[c]
            exceptions.append(c)

        if Rc < M:
            assert m[c] == Rc
        else:
            assert Rc == M
            assert m[c] >= M

    assert len(exceptions) <= 1

    return {
        "m": [None if x == INF else x for x in m],
        "global_pair_max": None if M == INF else M,
        "strict_unique_max_labels": exceptions,
    }


def explicit_strict_maximum_control():
    # Four internally disjoint s-t branches with exact costs 2,3,4,7
    # and labels 00,01,10,11.
    n = 6
    s, t = 0, 1
    edges = []
    labels = []
    weights = []

    for label, internal, total_cost in zip(
        range(4), range(2, 6), (2, 3, 4, 7)
    ):
        edges.extend([(s, internal), (internal, t)])
        labels.extend([label, 0])
        weights.extend([total_cost - 1, 1])

    receipt = exact_check(
        n, edges, labels, weights, s, t
    )
    assert receipt["m"] == [2, 3, 4, 7]
    assert receipt["global_pair_max"] == 4
    assert receipt["strict_unique_max_labels"] == [3]
    return receipt


def random_controls(seed=9379992, trials=250):
    rng = random.Random(seed)
    checked = 0
    exception_instances = 0

    for _ in range(trials):
        n = 6
        possible = [
            (i, j)
            for i in range(n)
            for j in range(i + 1, n)
        ]
        rng.shuffle(possible)

        m_edges = rng.randint(5, 10)
        edges = possible[:m_edges]
        labels = [rng.randrange(4) for _ in edges]
        weights = [rng.randrange(0, 5) for _ in edges]

        receipt = exact_check(
            n, edges, labels, weights, 0, n - 1
        )
        if receipt["strict_unique_max_labels"]:
            exception_instances += 1
        checked += 1

    return checked, exception_instances


def main():
    explicit = explicit_strict_maximum_control()
    checked, exception_instances = random_controls()

    print(json.dumps({
        "status": "PASS",
        "group": "GF(2)^2",
        "random_exact_instances": checked,
        "random_instances_with_strict_unique_max": exception_instances,
        "explicit_strict_max_control": explicit,
        "pairwise_affine_fibers": "VERIFIED",
        "pairwise_minimum_identity": "VERIFIED",
        "at_most_one_exceptional_unique_max": "VERIFIED",
        "claim_ceiling": (
            "VALUE_COLLAPSE_ONLY__"
            "NO_FULL_DETERMINISTIC_PRESCRIBED_LABEL_SOLVER__"
            "NO_GENERAL_WITNESS_RECONSTRUCTION"
        )
    }, indent=2))


if __name__ == "__main__":
    main()
