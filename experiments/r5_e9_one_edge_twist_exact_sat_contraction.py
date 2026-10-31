#!/usr/bin/env python3
"""Finite regression for the one-edge-twist exact SAT contraction theorem.

Brute-force model enumeration is OFFLINE_FALSIFIER_ONLY.  The arbitrary-n proof
is in research/R5_E9_ONE_EDGE_TWIST_2LIFT_EXACT_SAT_CONTRACTION_2026-09-27_v1.0.md.
"""
from __future__ import annotations

from itertools import combinations, product
import json


def model(A, x):
    return all(sum(x[j] for j, a in enumerate(row) if a) == 1 for row in A)


def models(A):
    n = len(A[0])
    return [bits for bits in product((0, 1), repeat=n) if model(A, bits)]


def one_edge_twist(A, i, j):
    n = len(A)
    assert len(A[0]) == n and A[i][j] == 1
    H = [[0] * (2 * n) for _ in range(2 * n)]
    for r in range(n):
        for c in range(n):
            if not A[r][c]:
                continue
            if (r, c) == (i, j):
                H[r][n + c] = 1
                H[n + r][c] = 1
            else:
                H[r][c] = 1
                H[n + r][n + c] = 1
    return H


def verify_model_space(A, i, j):
    n = len(A)
    base = models(A)
    H = one_edge_twist(A, i, j)
    lifted = models(H)
    predicted = {(u + v) for u in base for v in base if u[j] == v[j]}
    actual = set(lifted)
    assert actual == predicted
    for uv in lifted:
        u, v = uv[:n], uv[n:]
        assert u[j] == v[j]
        assert model(A, u) and model(A, v)
    for x in base:
        assert model(H, x + x)
    return base, lifted


def tanner_edges(A):
    n = len(A)
    return [(('r', r), ('v', c)) for r in range(n) for c in range(n) if A[r][c]]


def components_after_cut(Ahat, cut):
    nrows, ncols = len(Ahat), len(Ahat[0])
    vertices = [('r', r) for r in range(nrows)] + [('v', c) for c in range(ncols)]
    removed = {frozenset(e) for e in cut}
    adj = {v: set() for v in vertices}
    for r in range(nrows):
        for c, a in enumerate(Ahat[r]):
            if not a:
                continue
            e = (('r', r), ('v', c))
            if frozenset(e) in removed:
                continue
            adj[e[0]].add(e[1]); adj[e[1]].add(e[0])
    comps = []
    unseen = set(vertices)
    while unseen:
        root = next(iter(unseen)); stack = [root]; seen = {root}; unseen.remove(root)
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); unseen.remove(v); stack.append(v)
        comps.append(seen)
    return comps


def verify_known_cut(A, i, j):
    n = len(A)
    H = one_edge_twist(A, i, j)
    cut = [(("r", i), ("v", n + j)), (("r", n + i), ("v", j))]
    comps = components_after_cut(H, cut)
    assert len(comps) == 2
    assert sorted(len(c) for c in comps) == [2 * n, 2 * n]
    for comp in comps:
        marked = [u for e in cut for u in e if u in comp]
        assert len(marked) == 2
        assert {t for t, _ in marked} == {'r', 'v'}
    return True


J3 = (
    (1, 1, 1),
    (1, 1, 1),
    (1, 1, 1),
)

FANO = (
    (1,1,1,0,0,0,0),
    (1,0,0,1,1,0,0),
    (1,0,0,0,0,1,1),
    (0,1,0,1,0,1,0),
    (0,1,0,0,1,0,1),
    (0,0,1,1,0,0,1),
    (0,0,1,0,1,1,0),
)

UNIQUE9 = (
    (0,0,0,0,0,0,1,1,1),
    (0,1,1,0,0,0,0,1,0),
    (0,0,1,0,1,0,1,0,0),
    (1,1,0,0,0,0,1,0,0),
    (0,0,1,1,0,1,0,0,0),
    (0,0,0,1,1,0,0,0,1),
    (1,0,0,0,1,1,0,0,0),
    (1,0,0,1,0,0,0,1,0),
    (0,1,0,0,0,1,0,0,1),
)

j3_base, j3_lift = verify_model_space(J3, 0, 0)
assert len(j3_base) == 3
assert len(j3_lift) == 5
assert verify_known_cut(J3, 0, 0)

fano_base, fano_lift = verify_model_space(FANO, 0, 0)
assert len(fano_base) == 0
assert len(fano_lift) == 0
assert verify_known_cut(FANO, 0, 0)

unique_base, unique_lift = verify_model_space(UNIQUE9, 0, 6)
assert len(unique_base) == 1
assert len(unique_lift) == 1
assert unique_lift[0] == unique_base[0] + unique_base[0]
assert verify_known_cut(UNIQUE9, 0, 6)

out = {
    "status": "PASS_ONE_EDGE_TWIST_EXACT_SAT_CONTRACTION_REGRESSION",
    "model_space_exact": True,
    "sat_equivalence": True,
    "j3": {"base_models": len(j3_base), "lift_models": len(j3_lift)},
    "fano_unsat_preserved": True,
    "unique9_model_count_base": len(unique_base),
    "unique9_model_count_lift": len(unique_lift),
    "known_twisted_pair_is_two_edge_cut": True,
    "recursive_dimension_factor": 2,
    "recognition_route": "TWO_EDGE_CUT_PLUS_BOUNDED_DEGREE_COLORED_GI",
    "bruteforce_role": "OFFLINE_FALSIFIER_ONLY",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}
print(json.dumps(out, sort_keys=True))
