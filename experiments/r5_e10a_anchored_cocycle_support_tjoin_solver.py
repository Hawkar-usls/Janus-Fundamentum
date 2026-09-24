#!/usr/bin/env python3
"""
Finite controls for the PA-0008 child theorem:

1. anchored support-at-most-four cocycles spanning a rank-two graphic lift
   expose two quotient-independent small cocycles;
2. row operations / GF(2)^2 switching normalize the signature support to
   their union, hence at most seven elements when both contain f;
3. once all nonzero labels are confined to a constant set F, shortest-f
   equals a constant enumeration of ordinary minimum T-joins.

The checker is a finite regression control, not the theorem proof.
"""
from __future__ import annotations

import itertools
import json
import math
import random


INF = 10**18


def gf2_rank(rows):
    rows = [int(x) for x in rows if x]
    rank = 0
    while rows:
        rows = [r for r in rows if r]
        if not rows:
            break
        pivot = max(rows)
        bit = 1 << (pivot.bit_length() - 1)
        rank += 1
        nxt = []
        used = False
        for row in rows:
            if row == pivot and not used:
                used = True
                continue
            nxt.append(row ^ pivot if (row & bit) else row)
        rows = nxt
    return rank


def in_span(x, rows):
    return gf2_rank(list(rows) + [x]) == gf2_rank(rows)


def reduced_incidence_rows(n, edges):
    rows = []
    for v in range(n - 1):
        mask = 0
        for i, (a, b) in enumerate(edges):
            if a == v or b == v:
                mask |= 1 << i
        rows.append(mask)
    return rows


def popcount(x):
    return int(x).bit_count()


def combo2(rows, alpha):
    out = 0
    if alpha & 1:
        out ^= rows[0]
    if alpha & 2:
        out ^= rows[1]
    return out


def quotient_coordinate(d, cut_rows, sig_rows):
    hits = []
    for alpha in range(4):
        if in_span(d ^ combo2(sig_rows, alpha), cut_rows):
            hits.append(alpha)
    assert len(hits) == 1, (d, hits)
    return hits[0]


def enumerate_small_f_cocycles(m, f, rows):
    out = []
    other = [e for e in range(m) if e != f]
    for k in range(4):
        for extra in itertools.combinations(other, k):
            d = 1 << f
            for e in extra:
                d |= 1 << e
            if in_span(d, rows):
                out.append(d)
    return out


def anchored_normalization_control():
    # A fixed multigraph control found by deterministic finite search.
    edges = [
        (1, 2), (1, 3), (0, 3), (2, 3),
        (1, 3), (0, 1), (2, 3), (0, 1),
    ]
    n = 4
    m = len(edges)
    f = 0
    B = reduced_incidence_rows(n, edges)

    # Two small f-containing quotient-independent cocycles.
    D1 = 11   # edges {0,1,3}, size 3
    D2 = 45   # edges {0,2,3,5}, size 4
    assert popcount(D1) == 3 and popcount(D2) == 4
    assert (D1 >> f) & 1 and (D2 >> f) & 1
    assert gf2_rank(B + [D1, D2]) == gf2_rank(B) + 2

    # Hide them behind an invertible GL(2,2) signature basis plus cut rows.
    S_hidden = [
        D1 ^ D2 ^ B[0] ^ B[2],
        D2 ^ B[1],
    ]
    full_rows = B + S_hidden
    assert gf2_rank(full_rows) == gf2_rank(B) + 2

    small = enumerate_small_f_cocycles(m, f, full_rows)
    # This control satisfies the full anchored spanning promise.
    assert gf2_rank(small) == gf2_rank(full_rows)

    picked = None
    for a, b in itertools.combinations(small, 2):
        qa = quotient_coordinate(a, B, S_hidden)
        qb = quotient_coordinate(b, B, S_hidden)
        if qa and qb and qa != qb:  # distinct nonzero vectors in GF(2)^2 are independent
            picked = (a, b, qa, qb)
            break
    assert picked is not None
    A, C, qa, qc = picked

    # Replacing the two signature rows by A,C is an invertible quotient-basis
    # change plus addition of cut rows, hence preserves the represented matroid.
    assert gf2_rank(B + [A, C]) == gf2_rank(full_rows)
    assert gf2_rank(B + [A, C] + full_rows) == gf2_rank(full_rows)

    support = A | C
    assert popcount(support) <= 7
    assert (support >> f) & 1

    return {
        "vertices": n,
        "edges": m,
        "full_rank": gf2_rank(full_rows),
        "cut_rank": gf2_rank(B),
        "small_f_cocycles": len(small),
        "selected_sizes": [popcount(A), popcount(C)],
        "selected_quotient_coordinates": [qa, qc],
        "normalized_signature_support": popcount(support),
    }


def boundary_vertices(edge_indices, edges):
    parity = {}
    for i in edge_indices:
        u, v = edges[i]
        parity[u] = parity.get(u, 0) ^ 1
        parity[v] = parity.get(v, 0) ^ 1
    return sorted(v for v, bit in parity.items() if bit)


def floyd_dist(n, edges, weights, allowed):
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for e in allowed:
        u, v = edges[e]
        w = weights[e]
        if w < d[u][v]:
            d[u][v] = d[v][u] = w
    for k in range(n):
        for i in range(n):
            dik = d[i][k]
            if dik >= INF:
                continue
            for j in range(n):
                z = dik + d[k][j]
                if z < d[i][j]:
                    d[i][j] = z
    return d


def min_pairing_cost(T, d):
    T = tuple(T)
    memo = {0: 0}
    full = (1 << len(T)) - 1

    def solve(mask):
        if mask in memo:
            return memo[mask]
        i = (mask & -mask).bit_length() - 1
        best = INF
        rest = mask ^ (1 << i)
        mm = rest
        while mm:
            j = (mm & -mm).bit_length() - 1
            dij = d[T[i]][T[j]]
            if dij < INF:
                best = min(best, dij + solve(rest ^ (1 << j)))
            mm ^= 1 << j
        memo[mask] = best
        return best

    return solve(full)


def xor_labels(indices, labels):
    out = 0
    for i in indices:
        out ^= labels[i]
    return out


def brute_min_cycle_through_f(n, edges, weights, labels, f):
    m = len(edges)
    best = INF
    for mask in range(1 << m):
        if not (mask >> f) & 1:
            continue
        chosen = [i for i in range(m) if (mask >> i) & 1]
        if xor_labels(chosen, labels) != 0:
            continue
        if boundary_vertices(chosen, edges):
            continue
        cost = sum(weights[i] for i in chosen)
        best = min(best, cost)
    return best


def constant_support_solver(n, edges, weights, labels, f):
    F = [i for i, g in enumerate(labels) if g != 0]
    assert f in F
    assert len(F) <= 7
    zero_edges = [i for i in range(len(edges)) if i not in set(F)]
    d = floyd_dist(n, edges, weights, zero_edges)

    best = INF
    cases = 0
    for mask in range(1 << len(F)):
        R = [F[j] for j in range(len(F)) if (mask >> j) & 1]
        if f not in R:
            continue
        if xor_labels(R, labels) != 0:
            continue
        T = boundary_vertices(R, edges)
        assert len(T) <= 14 and len(T) % 2 == 0
        pair_cost = min_pairing_cost(T, d)
        if pair_cost >= INF:
            continue
        cases += 1
        best = min(best, sum(weights[e] for e in R) + pair_cost)
    return best, len(F), cases


def random_solver_controls(trials=300, seed=130013):
    rng = random.Random(seed)
    compared = 0
    feasible = 0
    max_support = 0
    for _ in range(trials):
        n = 5
        all_pairs = list(itertools.combinations(range(n), 2))
        # Connected backbone plus random extra/parallel edges.
        edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        while len(edges) < 9:
            edges.append(rng.choice(all_pairs))
        m = len(edges)
        f = 0
        weights = [rng.randint(0, 5) for _ in range(m)]

        k = rng.randint(1, min(6, m))
        F = {f}
        while len(F) < k:
            F.add(rng.randrange(m))
        labels = [0] * m
        for e in F:
            labels[e] = rng.randint(1, 3)

        brute = brute_min_cycle_through_f(n, edges, weights, labels, f)
        fast, supp, _ = constant_support_solver(n, edges, weights, labels, f)
        assert brute == fast, {
            "edges": edges,
            "weights": weights,
            "labels": labels,
            "brute": brute,
            "solver": fast,
        }
        compared += 1
        feasible += int(brute < INF)
        max_support = max(max_support, supp)

    return {
        "instances": compared,
        "feasible_instances": feasible,
        "max_signature_support_tested": max_support,
    }


def main():
    out = {
        "status": "PASS_FINITE_ANCHORED_SUPPORT_AND_TJOIN_CONTROLS",
        "normalization": anchored_normalization_control(),
        "solver": random_solver_controls(),
        "theorem_scope": {
            "quotient_rank_two": True,
            "anchored_cocycle_support_bound": 4,
            "derived_signature_support_bound": 7,
            "solver": "CONSTANT_ENUMERATION_PLUS_ORDINARY_T_JOIN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
