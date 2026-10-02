#!/usr/bin/env python3
"""Local-swap family: exact F2 coset and Exact-One witness classification.

The arbitrary-m proof is in the companion note. Small exhaustive checks are
OFFLINE_FALSIFIER_ONLY.
"""
from __future__ import annotations

from itertools import product
import json


def vid(r, a, m):
    return r * m + (a % m)


def build_edges(m):
    P = {}
    Q = {}
    for r in range(3):
        for a in range(m):
            P[(r, a)] = ((r + 1) % 3, a)
            if r == 0:
                Q[(r, a)] = (2, (a + 1) % m)
            elif r == 1:
                Q[(r, a)] = (0, a)
            else:
                Q[(r, a)] = (1, a)
    u = (0, 0)
    v = (2, 2)
    Q[u], Q[v] = Q[v], Q[u]

    edges = []
    for r in range(3):
        for a in range(m):
            edges.append((vid(r, a, m), vid(*P[(r, a)], m), vid(*Q[(r, a)], m)))
    return tuple(edges)


def parity_ok(edges, x):
    return all(sum(x[v] for v in e) % 2 == 1 for e in edges)


def exact_one(edges, x):
    return all(sum(x[v] for v in e) == 1 for e in edges)


def gf2_rank(edges, n):
    rows = []
    for e in edges:
        mask = 0
        for v in e:
            mask ^= 1 << v
        rows.append(mask)

    rank = 0
    for c in range(n):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> c) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> c) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def parameterized_parity_point(m, c, a_bits):
    # A_a=x_(0,a); A_2 is forced to 1. C_a is the global parity bit c.
    A = [None] * m
    it = iter(a_bits)
    for a in range(m):
        A[a] = 1 if a == 2 else next(it)
    C = [c] * m
    B = [1 ^ A[a] ^ c for a in range(m)]
    return tuple(A + B + C)


def parameterized_exact_witness(m, a_bits):
    # Exact-One classification: C=0, A_2=1, B_a=1-A_a.
    return parameterized_parity_point(m, 0, a_bits)


rows = []
for m in range(3, 21):
    edges = build_edges(m)
    n = 3 * m
    r = gf2_rank(edges, n)
    assert r == 2 * m
    nullity = n - r
    assert nullity == m

    zero_bits = (0,) * (m - 1)
    p0 = parameterized_parity_point(m, 0, zero_bits)
    p1 = parameterized_parity_point(m, 1, zero_bits)
    assert parity_ok(edges, p0)
    assert exact_one(edges, p0)
    assert parity_ok(edges, p1)
    assert not exact_one(edges, p1)

    # Enumerate the parameter space, not the 2^(3m) ambient cube.
    exact_count = 0
    parity_count = 0
    if m <= 12:
        for c in (0, 1):
            for a_bits in product((0, 1), repeat=m - 1):
                x = parameterized_parity_point(m, c, a_bits)
                assert parity_ok(edges, x)
                parity_count += 1
                if exact_one(edges, x):
                    exact_count += 1
                    assert c == 0
        assert parity_count == 2**m
        assert exact_count == 2 ** (m - 1)

    rows.append({
        "m": m,
        "n": n,
        "gf2_rank": r,
        "gf2_nullity": nullity,
        "expected_parity_coset_size": 2**m,
        "expected_exact_one_count": 2 ** (m - 1),
        "parameter_space_checked": m <= 12,
    })

# Tiny ambient exhaustive controls independently check completeness of the
# parametrization against every Boolean assignment.
for m in (3, 4, 5):
    edges = build_edges(m)
    n = 3 * m
    parity = []
    exact = []
    for x in product((0, 1), repeat=n):
        if parity_ok(edges, x):
            parity.append(x)
            if exact_one(edges, x):
                exact.append(x)

    assert len(parity) == 2**m
    assert len(exact) == 2 ** (m - 1)

    generated_parity = {
        parameterized_parity_point(m, c, a_bits)
        for c in (0, 1)
        for a_bits in product((0, 1), repeat=m - 1)
    }
    generated_exact = {
        parameterized_exact_witness(m, a_bits)
        for a_bits in product((0, 1), repeat=m - 1)
    }
    assert set(parity) == generated_parity
    assert set(exact) == generated_exact

out = {
    "status": "PASS_LOCAL_SWAP_BINARY_COSET_EXACTONE_CLASSIFICATION",
    "m_range_checked": [3, 20],
    "gf2_nullity_law": "m=n/3",
    "parity_coset_size": "2^m",
    "exact_one_solution_count": "2^(m-1)",
    "exact_one_classification": "C_a=0_FOR_ALL_a; A_2=1; B_a=1-A_a; A_a_FREE_FOR_a!=2",
    "direct_witness_construction": "O(n)",
    "ambient_exhaustive_controls": [3, 4, 5],
    "offline_exhaustive_role": "FALSIFIER_ONLY__NOT_E8_D1",
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}
print(json.dumps(out, sort_keys=True))
