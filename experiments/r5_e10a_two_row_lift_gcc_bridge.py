#!/usr/bin/env python3
"""Exact brute-force controls for the row-lift T-join -> GCC bridge."""

from __future__ import annotations

import itertools
import json
import random

INF = 10**9


def boundary(n, edges, mask):
    d = [0] * n
    for i, (a, b) in enumerate(edges):
        if (mask >> i) & 1:
            d[a] ^= 1
            d[b] ^= 1
    return tuple(i for i, bit in enumerate(d) if bit)


def label_sum(labels, mask):
    s = 0
    for i, lab in enumerate(labels):
        if (mask >> i) & 1:
            s ^= lab
    return s


def brute_tjoin(n, edges, labels, weights, u, v, target):
    best = INF
    best_mask = None
    wanted = tuple(sorted((u, v)))
    for mask in range(1 << len(edges)):
        if tuple(sorted(boundary(n, edges, mask))) != wanted:
            continue
        if label_sum(labels, mask) != target:
            continue
        cost = sum(weights[i] for i in range(len(edges)) if (mask >> i) & 1)
        if cost < best:
            best = cost
            best_mask = mask
    return best, best_mask


def brute_gcc(n, edges, labels, weights, u, v, target):
    # Two directed arcs for each ordinary edge, plus one special v->u arc.
    m = len(edges)
    special = 2 * m
    target_aug = (target << 1) | 1
    best = INF
    best_mask = None

    for mask in range(1 << (2 * m + 1)):
        bal = [0] * n
        group = 0
        cost = 0

        for i, (a, b) in enumerate(edges):
            for side, (tail, head) in enumerate(((a, b), (b, a))):
                ai = 2 * i + side
                if (mask >> ai) & 1:
                    bal[tail] -= 1
                    bal[head] += 1
                    group ^= labels[i] << 1
                    cost += weights[i]

        if (mask >> special) & 1:
            bal[v] -= 1
            bal[u] += 1
            group ^= 1

        if any(bal):
            continue
        if group != target_aug:
            continue
        if cost < best:
            best = cost
            best_mask = mask

    return best, best_mask


def opposite_pair_free(mask, m):
    return all(
        not (((mask >> (2*i)) & 1) and ((mask >> (2*i+1)) & 1))
        for i in range(m)
    )


def random_controls(seed=9379992, trials=160):
    rng = random.Random(seed)
    checked = 0
    for _ in range(trials):
        n = 4
        possible = [(i, j) for i in range(n) for j in range(i+1, n)]
        rng.shuffle(possible)
        m = rng.randint(2, 5)
        edges = possible[:m]
        labels = [rng.randrange(4) for _ in edges]  # GF(2)^2
        weights = [rng.randint(1, 3) for _ in edges]
        u, v = rng.sample(range(n), 2)
        target = rng.randrange(4)

        tj_cost, _ = brute_tjoin(n, edges, labels, weights, u, v, target)
        gcc_cost, gcc_mask = brute_gcc(n, edges, labels, weights, u, v, target)

        assert tj_cost == gcc_cost, (
            edges, labels, weights, u, v, target, tj_cost, gcc_cost
        )
        if gcc_mask is not None:
            assert opposite_pair_free(gcc_mask, m)
        checked += 1
    return checked


def disconnected_cycle_control():
    # u=0, v=2.  The only u-v path has label 00.
    # The disjoint triangle contributes label 01.
    # Target 01 therefore requires path + disconnected cycle.
    n = 6
    edges = [(0,1), (1,2), (3,4), (4,5), (5,3)]
    labels = [0, 0, 1, 0, 0]
    weights = [1] * len(edges)
    target = 1

    tj_cost, tj_mask = brute_tjoin(n, edges, labels, weights, 0, 2, target)
    gcc_cost, gcc_mask = brute_gcc(n, edges, labels, weights, 0, 2, target)

    assert tj_cost == 5
    assert tj_mask == (1 << len(edges)) - 1
    assert gcc_cost == 5
    assert gcc_mask is not None
    assert opposite_pair_free(gcc_mask, len(edges))

    # Enumerate simple u-v paths by brute subsets with boundary {u,v}
    # and no cycle component: in this graph the unique path is edges 0,1.
    path_mask = (1 << 0) | (1 << 1)
    assert boundary(n, edges, path_mask) == (0, 2)
    assert label_sum(labels, path_mask) == 0

    return {
        "tjoin_cost": tj_cost,
        "gcc_cost": gcc_cost,
        "required_structure": "u-v path plus disconnected labelled cycle",
        "path_only_label": 0,
        "target_label": target,
    }


def main():
    checked = random_controls()
    cycle = disconnected_cycle_control()
    print(json.dumps({
        "status": "PASS",
        "random_exact_controls": checked,
        "label_group": "GF(2)^2",
        "tjoin_equals_gcc_optimum": True,
        "positive_weight_opposite_arc_cancellation": "VERIFIED",
        "path_only_shortcut": "FALSIFIED",
        "disconnected_cycle_control": cycle,
        "claim_ceiling": (
            "EXACT_BRIDGE_ONLY__RANDOMIZED_GCC_SOURCE_BOUND__"
            "DETERMINISTIC_SOLVER_NOT_CLAIMED"
        )
    }, indent=2))


if __name__ == "__main__":
    main()
