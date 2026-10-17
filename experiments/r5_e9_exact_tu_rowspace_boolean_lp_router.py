#!/usr/bin/env python3
"""Exact finite controls for the TU-rowspace Exact-One router."""

from fractions import Fraction
from itertools import combinations, product


def rref_basis(M):
    a = [[Fraction(v) for v in row] for row in M]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        z = a[r][c]
        a[r] = [x / z for x in a[r]]
        for i in range(m):
            if i == r or a[i][c] == 0:
                continue
            z = a[i][c]
            a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return a[:r]


def det_q(M):
    n = len(M)
    if n == 0:
        return Fraction(1)
    a = [[Fraction(v) for v in row] for row in M]
    det = Fraction(1)
    for c in range(n):
        p = next((i for i in range(c, n) if a[i][c]), None)
        if p is None:
            return Fraction(0)
        if p != c:
            a[c], a[p] = a[p], a[c]
            det = -det
        z = a[c][c]
        det *= z
        for j in range(c, n):
            a[c][j] /= z
        for i in range(c + 1, n):
            if a[i][c] == 0:
                continue
            z = a[i][c]
            for j in range(c, n):
                a[i][j] -= z * a[c][j]
    return det


def is_tu_exhaustive(F):
    m, n = len(F), len(F[0])
    for k in range(1, min(m, n) + 1):
        for rs in combinations(range(m), k):
            for cs in combinations(range(n), k):
                d = det_q([[F[i][j] for j in cs] for i in rs])
                if d not in (0, 1, -1):
                    return False, (k, rs, cs, d)
    return True, None


def first_bad_2minor(F):
    m, n = len(F), len(F[0])
    for i, j in combinations(range(m), 2):
        for a, b in combinations(range(n), 2):
            d = F[i][a] * F[j][b] - F[i][b] * F[j][a]
            if abs(d) > 1:
                return (i, j), (a, b), d
    return None


def unsigned_incidence(nv, edges):
    A = [[0] * len(edges) for _ in range(nv)]
    for j, (u, v) in enumerate(edges):
        A[u][j] = 1
        A[v][j] = 1
    return A


def exact_one(A, x):
    return all(sum(row[j] * x[j] for j in range(len(x))) == 1 for row in A)


def check_k33_sat():
    edges = [(u, v) for u in range(3) for v in range(3, 6)]
    A = unsigned_incidence(6, edges)
    assert all(sum(row) == 3 for row in A)
    F = rref_basis(A)
    assert len(F) == 5
    ok, bad = is_tu_exhaustive(F)
    assert ok, bad
    b = [sum(row, Fraction(0)) / 3 for row in F]
    assert all(v.denominator == 1 for v in b)

    x = [int(e in {(0, 3), (1, 4), (2, 5)}) for e in edges]
    assert exact_one(A, x)
    assert [sum(F[i][j] * x[j] for j in range(len(x))) for i in range(len(F))] == b
    return len(F), len(edges) - len(F), b


def check_tu_nonintegral_unsat():
    A = [
        [1, 1, 1, 0, 0, 0],
        [1, 0, 0, 1, 1, 0],
        [1, 0, 0, 0, 1, 1],
        [0, 1, 0, 1, 1, 0],
        [0, 0, 1, 1, 1, 0],
    ]
    assert all(sum(row) == 3 for row in A)
    F = rref_basis(A)
    assert len(F) == 5
    ok, bad = is_tu_exhaustive(F)
    assert ok, bad
    b = [sum(row, Fraction(0)) / 3 for row in F]
    assert any(v.denominator != 1 for v in b)
    assert not any(exact_one(A, bits) for bits in product((0, 1), repeat=6))
    return len(F), 6 - len(F), b


def check_pg15_reject():
    rows = [
        (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
        (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
        (6,9,15),(7,8,15),(7,11,12),
    ]
    A = [[int(j + 1 in row) for j in range(15)] for row in rows]
    F = rref_basis(A)
    assert len(F) == 11
    bad = first_bad_2minor(F)
    assert bad is not None and abs(bad[2]) == 2
    assert any(v == -2 for row in F for v in row)
    return bad


def main():
    sat_rank, sat_nullity, sat_b = check_k33_sat()
    uns_rank, uns_nullity, uns_b = check_tu_nonintegral_unsat()
    pg_bad = check_pg15_reject()
    print("Exact TU-rowspace Boolean LP router regression: PASS")
    print(f"K3,3 SAT: rank={sat_rank} nullity={sat_nullity} b={sat_b}")
    print(f"TU UNSAT: rank={uns_rank} nullity={uns_nullity} b={uns_b}")
    print(f"PG15 TU rejection: determinant-2 minor={pg_bad}")
    print("P_VS_NP=OPEN E8_D1=EMPTY")


if __name__ == "__main__":
    main()
