#!/usr/bin/env python3
"""Cubic Exact-One -> affine-coset minimum-weight normal form.

This checker validates finite controls only.  The arbitrary-size proof is in the
companion research note.  Exhaustive enumeration is OFFLINE_FALSIFIER_ONLY and
is not an admitted E8-D1 algorithmic primitive.
"""
from __future__ import annotations

from collections import deque
from itertools import product
import json


def degrees(edges, n):
    d = [0] * n
    for e in edges:
        assert len(e) == 3
        assert len(set(e)) == 3
        for v in e:
            d[v] += 1
    return d


def parity_ok(edges, x):
    return all(sum(x[v] for v in e) % 2 == 1 for e in edges)


def kernel_ok(edges, z):
    return all(sum(z[v] for v in e) % 2 == 0 for e in edges)


def exact_one(edges, x):
    return all(sum(x[v] for v in e) == 1 for e in edges)


def triple_defect(edges, x):
    return sum(sum(x[v] for v in e) == 3 for e in edges)


def incidence_girth(edges, n):
    # Variable nodes are 0..n-1 and edge nodes are n..n+m-1.
    N = n + len(edges)
    adj = [[] for _ in range(N)]
    for j, e in enumerate(edges):
        ej = n + j
        for v in e:
            adj[v].append(ej)
            adj[ej].append(v)

    inf = 10**9
    best = inf
    for s in range(N):
        dist = [-1] * N
        parent = [-1] * N
        q = deque([s])
        dist[s] = 0
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    parent[v] = u
                    q.append(v)
                elif parent[u] != v:
                    best = min(best, dist[u] + dist[v] + 1)
    return None if best == inf else best


def min_nonzero_kernel_weight(edges, n):
    best = None
    for z in product((0, 1), repeat=n):
        w = sum(z)
        if w and kernel_ok(edges, z):
            best = w if best is None else min(best, w)
    return best


def audit_control(name, edges, n):
    deg = degrees(edges, n)
    assert len(set(deg)) == 1
    d = deg[0]
    m = len(edges)
    assert d * n == 3 * m

    parity_weights = []
    exact_weights = []
    for x in product((0, 1), repeat=n):
        if not parity_ok(edges, x):
            continue

        w = sum(x)
        t = triple_defect(edges, x)

        # Arbitrary-size theorem identity specialized to this finite control.
        assert d * w == m + 2 * t

        # Exact-One iff the parity solution attains the universal lower bound.
        assert exact_one(edges, x) == (d * w == m)

        parity_weights.append(w)
        if exact_one(edges, x):
            exact_weights.append(w)

    assert parity_weights
    assert all(w * d >= m for w in parity_weights)

    g = incidence_girth(edges, n)
    dmin = min_nonzero_kernel_weight(edges, n)
    if g is not None and dmin is not None:
        assert 2 * dmin >= g

    return {
        "name": name,
        "n": n,
        "m": m,
        "regular_degree": d,
        "incidence_girth": g,
        "parity_solution_count": len(parity_weights),
        "parity_weights": sorted(set(parity_weights)),
        "exact_one_solution_count": len(exact_weights),
        "exact_one_weights": sorted(set(exact_weights)),
        "binary_kernel_min_nonzero_weight": dmin,
    }


# Fano plane: cubic/3-uniform but n is not divisible by 3, hence no Exact-One
# witness.  Its parity coset is nevertheless nonempty (the all-ones vector).
FANO = (
    (0, 1, 2),
    (0, 3, 4),
    (0, 5, 6),
    (1, 3, 5),
    (1, 4, 6),
    (2, 3, 6),
    (2, 4, 5),
)

# Z3 affine control: rows + columns + one diagonal parallel class.
# This is cubic, 3-uniform, linear, connected, and satisfiable.
AFFINE_3X3 = tuple(
    [(3 * r + 0, 3 * r + 1, 3 * r + 2) for r in range(3)]
    + [(0 + c, 3 + c, 6 + c) for c in range(3)]
    + [
        tuple(3 * r + ((r + b) % 3) for r in range(3))
        for b in range(3)
    ]
)

fano = audit_control("FANO_7", FANO, 7)
aff = audit_control("AFFINE_3X3", AFFINE_3X3, 9)

# Explicit descent witness on the satisfiable affine control.
one = (1,) * 9
assert parity_ok(AFFINE_3X3, one)
target = None
for x in product((0, 1), repeat=9):
    if exact_one(AFFINE_3X3, x):
        target = x
        break
assert target is not None
z = tuple(a ^ b for a, b in zip(one, target))
assert kernel_ok(AFFINE_3X3, z)
assert sum(one) == 9
assert sum(target) == 3
assert sum(z) == 6

out = {
    "status": "PASS_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM",
    "finite_controls": [fano, aff],
    "affine_control_descent": {
        "start_weight": sum(one),
        "target_weight": sum(target),
        "kernel_flip_support": sum(z),
        "target_is_exact_one": True,
    },
    "proved_in_companion_note": [
        "d*|x| = m + 2*t(x) for every odd-parity solution",
        "Exact-One iff parity plus minimum possible weight n/3",
        "nonzero kernel support >= incidence_girth/2",
        "fixed-k bounded-support kernel descent is not universal",
    ],
    "offline_exhaustive_role": "FALSIFIER_ONLY__NOT_E8_D1",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}
print(json.dumps(out, sort_keys=True))
