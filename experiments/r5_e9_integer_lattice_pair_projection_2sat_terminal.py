#!/usr/bin/env python3
"""Exact finite checker for the integer-lattice pair-projection 2-SAT terminal."""

from math import prod
from itertools import product

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


P = [5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q = [16,6,19,10,23,4,2,13,7,17,1,21,22,11,3,12,15,20,5,0,9,8,14,18]
EXPECTED_PROJECTIVE_CLASSES = {
    frozenset((9,16,18)),
    frozenset((1,17)),
    frozenset((2,11)),
    frozenset((6,15)),
    frozenset((8,14)),
    frozenset((12,21)),
}


def source_matrix():
    n = 24
    A = sp.zeros(n, n)
    for i in range(n):
        for j in (i, P[i], Q[i]):
            A[i, j] = 1
    return A


def rank_mod_p(M, p):
    a = [[int(M[i, j]) % p for j in range(M.cols)] for i in range(M.rows)]
    r = 0
    for c in range(M.cols):
        pivot = next((i for i in range(r, M.rows) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][c], -1, p)
        a[r] = [(x * inv) % p for x in a[r]]
        for i in range(M.rows):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [(a[i][j] - f * a[r][j]) % p for j in range(M.cols)]
        r += 1
        if r == M.rows:
            break
    return r


def smith_invariants(M):
    D = smith_normal_form(M, domain=ZZ)
    return [abs(int(D[i, i])) for i in range(min(D.rows, D.cols)) if D[i, i] != 0]


def integer_system_solvable(M, b):
    r = M.rank()
    if M.row_join(b).rank() != r:
        return False
    d = smith_invariants(M)
    da = smith_invariants(M.row_join(b))
    assert len(d) == len(da) == r
    return prod(d) == prod(da)


def projective_classes(A):
    ns = A.nullspace()
    K = sp.Matrix.hstack(*ns)
    assert K.cols == 3
    rows = [tuple(K[i, j] for j in range(K.cols)) for i in range(K.rows)]
    assert all(any(v != 0 for v in row) for row in rows)

    buckets = {}
    for i, row in enumerate(rows):
        first = next(v for v in row if v != 0)
        key = tuple(sp.cancel(v / first) for v in row)
        buckets.setdefault(key, []).append(i)

    nontrivial = set()
    for members in buckets.values():
        if len(members) <= 1:
            continue
        ref = rows[members[0]]
        idx = next(j for j, v in enumerate(ref) if v != 0)
        for i in members[1:]:
            lam = sp.cancel(rows[i][idx] / ref[idx])
            assert lam == 1  # no -2/-1/2 pins and no illegal ratios
            assert rows[i] == ref
        nontrivial.add(frozenset(members))
    return K, buckets, nontrivial


def pair_relation(A, i, j):
    n = A.cols
    allowed = []
    for a, b in product((0, 1), repeat=2):
        ei = [0] * n
        ej = [0] * n
        ei[i] = 1
        ej[j] = 1
        M = A.col_join(sp.Matrix([ei, ej]))
        rhs = sp.Matrix([1] * A.rows + [a, b])
        if integer_system_solvable(M, rhs):
            allowed.append((a, b))
    return allowed


def main():
    A = source_matrix()
    n = A.rows
    one = sp.ones(n, 1)

    # Cubic and connected source checks.
    assert all(sum(int(A[i, j]) for j in range(n)) == 3 for i in range(n))
    assert all(sum(int(A[i, j]) for i in range(n)) == 3 for j in range(n))

    # The control is deliberately not linear: exactly four row pairs overlap twice.
    supports = [{j for j in range(n) if A[i, j]} for i in range(n)]
    bad_overlaps = [
        (i, j, supports[i] & supports[j])
        for i in range(n) for j in range(i)
        if len(supports[i] & supports[j]) > 1
    ]
    assert len(bad_overlaps) == 4
    assert all(len(s) == 2 for _, _, s in bad_overlaps)

    # Levi connectivity.
    adj = [[] for _ in range(2 * n)]
    for i in range(n):
        for j in supports[i]:
            adj[i].append(n + j)
            adj[n + j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    assert len(seen) == 2 * n

    assert A.rank() == 21
    assert A.row_join(one).rank() == 21
    for p, expected in ((2, 21), (3, 20), (5, 21), (7, 21)):
        assert rank_mod_p(A, p) == expected
        assert rank_mod_p(A.row_join(one), p) == expected

    # Global integer-lattice membership passes.
    d = smith_invariants(A)
    da = smith_invariants(A.row_join(one))
    assert len(d) == len(da) == 21
    assert prod(d) == prod(da) == 3
    assert integer_system_solvable(A, one)

    # RKPR passes with equality classes only.
    K, buckets, nontrivial = projective_classes(A)
    assert nontrivial == EXPECTED_PROJECTIVE_CLASSES
    assert sum(len(v) == 1 for v in buckets.values()) == 11
    assert 5 in next(v for v in buckets.values() if 5 in v) and len(next(v for v in buckets.values() if 5 in v)) == 1
    assert 3 in next(v for v in buckets.values() if 3 in v) and len(next(v for v in buckets.values() if 3 in v)) == 1
    assert frozenset(next(v for v in buckets.values() if 12 in v)) == frozenset((12,21))

    # Strict pair-projection contradiction beyond global SNF + RKPR.
    r_5_12 = pair_relation(A, 5, 12)
    r_3_5 = pair_relation(A, 3, 5)
    assert r_5_12 == [(1, 0)]
    assert r_3_5 == [(1, 0)]

    # R_5,12 forces x5=1; R_3,5 forces x5=0.  No Boolean witness exists.
    assert {a for a, _ in r_5_12} == {1}
    assert {b for _, b in r_3_5} == {0}

    print("PASS R5_E9_INTEGER_LATTICE_PAIR_PROJECTION_2SAT_TERMINAL")
    print("control: n=24 rank_Q=21 nullity_Q=3 SNF=PASS RKPR=PASS")
    print("control scope: cubic connected, NONLINEAR (four double row intersections)")
    print("R_5_12={(1,0)} => x5=1")
    print("R_3_5={(1,0)}  => x5=0")
    print("pair-projection 2-CSP => UNSAT")
    print("linear-cubic sufficiency gate remains OPEN")
    print("P_VS_NP=OPEN E8_D1=EMPTY")


if __name__ == "__main__":
    main()
