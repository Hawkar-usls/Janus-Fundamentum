#!/usr/bin/env python3
"""Finite exact-rank replay for the EQ3 middle-nullity hardness slab theorem.

This checker validates the local gadget rank and the exact output-nullity identity
on frozen cubic controls.  It is an OFFLINE_FALSIFIER_ONLY and is not a SAT oracle.
"""
from __future__ import annotations

from fractions import Fraction
import json


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pivot = A[r][c]
        A[r] = [x / pivot for x in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                q = A[i][c]
                A[i] = [A[i][j] - q * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


GADGET = [
    (2, 5, 6),
    (1, 4, 7),
    (5, 7, 9),
    (0, 3, 7),
    (4, 6, 9),
    (2, 4, 8),
    (3, 8, 9),
    (0, 5, 8),
    (1, 3, 6),
]


def incidence(rows, n):
    A = [[0] * n for _ in rows]
    for i, row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


G = incidence(GADGET, 10)
assert rank_q(G) == 8

# Two exact homogeneous kernel modes used by the theorem.
R_MODE = [0, 0, 0, -1, -1, -1, 1, 1, 1, 0]
Q_MODE = [1, 1, 1, -1, -1, -1, 0, 0, 0, 1]
for mode in (R_MODE, Q_MODE):
    assert all(sum(G[i][j] * mode[j] for j in range(10)) == 0 for i in range(9))
assert rank_q([R_MODE, Q_MODE]) == 2


def assert_cubic_square(rows, m):
    assert len(rows) == m
    assert all(len(row) == 3 and len(set(row)) == 3 for row in rows)
    deg = [0] * m
    for row in rows:
        for v in row:
            deg[v] += 1
    assert deg == [3] * m


def eq3_regularize(source_rows, m):
    """Materialize the existing 10x-per-variable EQ3 regularization matrix."""
    assert_cubic_square(source_rows, m)

    # Assign occurrence numbers 0,1,2 to the three appearances of each source variable.
    occ = [[] for _ in range(m)]
    for ri, row in enumerate(source_rows):
        for v in row:
            occ[v].append(ri)
    assert all(len(x) == 3 for x in occ)
    occ_index = {}
    for v in range(m):
        for idx, ri in enumerate(sorted(occ[v])):
            occ_index[(ri, v)] = idx

    out_rows = []
    for v in range(m):
        base = 10 * v
        for g in GADGET:
            out_rows.append(tuple(base + x for x in g))

    for ri, row in enumerate(source_rows):
        out_rows.append(tuple(10 * v + occ_index[(ri, v)] for v in row))

    N = 10 * m
    assert len(out_rows) == N
    A = incidence(out_rows, N)
    assert all(sum(row) == 3 for row in A)
    coldeg = [sum(A[i][j] for i in range(N)) for j in range(N)]
    assert coldeg == [3] * N
    return A


FANO7 = [
    (0, 1, 2), (0, 3, 4), (0, 5, 6),
    (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5),
]

AFFINE3X3 = []
for rr in range(3):
    AFFINE3X3.append(tuple(3 * rr + c for c in range(3)))
for c in range(3):
    AFFINE3X3.append(tuple(3 * rr + c for rr in range(3)))
for d in range(3):
    AFFINE3X3.append(tuple(3 * rr + ((rr + d) % 3) for rr in range(3)))

UNSAT9 = [
    (3, 6, 7), (2, 3, 4), (0, 3, 8), (2, 5, 8), (0, 4, 7),
    (1, 4, 8), (1, 5, 7), (1, 2, 6), (0, 5, 6),
]

controls_in = [
    ("FANO7", FANO7, 7),
    ("AFFINE_3X3", AFFINE3X3, 9),
    ("CONNECTED_LINEAR_CUBIC_UNSAT9", UNSAT9, 9),
]

controls = []
for name, rows, m in controls_in:
    M = incidence(rows, m)
    source_rank = rank_q(M)
    kappa = m - source_rank
    assert 0 <= kappa <= 2 * m / 3

    Aout = eq3_regularize(rows, m)
    N = 10 * m
    output_rank = rank_q(Aout)
    K = N - output_rank
    Delta = 2 * N - 3 * K

    assert output_rank == 8 * m + source_rank
    assert output_rank == 9 * m - kappa
    assert K == m + kappa
    assert 10 * K >= N
    assert 6 * K <= N
    assert 2 * Delta >= 3 * N
    assert 10 * Delta <= 17 * N

    controls.append({
        "name": name,
        "m": m,
        "source_rank_Q": source_rank,
        "source_nullity_Q": kappa,
        "output_N": N,
        "output_rank_Q": output_rank,
        "output_nullity_Q": K,
        "output_delta": Delta,
        "identity_rank": f"{output_rank}=8m+rank(M)=9m-kappa",
        "identity_nullity": f"{K}=m+kappa",
    })

print(json.dumps({
    "status": "PASS_EQ3_MID_NULLITY_HARDNESS_SLAB_RANK_REPLAY",
    "role": "OFFLINE_FALSIFIER_ONLY",
    "gadget_rank_Q": 8,
    "gadget_nullity_Q": 2,
    "output_nullity_identity": "K=m+kappa",
    "output_delta_identity": "Delta=17m-3kappa",
    "hardness_slab": "N/10<=K<=N/6",
    "delta_slab": "3N/2<=Delta<=17N/10",
    "controls": controls,
    "E8_D1": "EMPTY",
    "P_VS_NP": "OPEN",
}, sort_keys=True))
