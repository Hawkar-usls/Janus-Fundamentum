#!/usr/bin/env python3
"""Exact finite regression for R5 E9 exact TU row-space router.

The theorem note supplies the symbolic equivalence and polynomial-recognition
argument. This checker uses exact Fraction arithmetic and exhaustive minors only
on tiny frozen controls; exhaustive minor enumeration is NOT the claimed
general recognition algorithm.
"""

from fractions import Fraction
from itertools import combinations, product


def rank_q(mat):
    if not mat:
        return 0
    a = [[Fraction(x) for x in row] for row in mat]
    m, n = len(a), len(a[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        z = a[r][c]
        a[r] = [v / z for v in a[r]]
        for i in range(m):
            if i != r and a[i][c] != 0:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def independent_rows(mat):
    out = []
    r = 0
    for row in mat:
        nr = rank_q(out + [row])
        if nr > r:
            out.append([Fraction(x) for x in row])
            r = nr
    return out


def independent_cols(rmat):
    r = len(rmat)
    n = len(rmat[0])
    cols = []
    rk = 0
    for j in range(n):
        trial = cols + [j]
        colmat = [[rmat[i][c] for c in trial] for i in range(r)]
        nr = rank_q(colmat)
        if nr > rk:
            cols.append(j)
            rk = nr
            if rk == r:
                break
    assert len(cols) == r
    return cols


def inverse_q(mat):
    n = len(mat)
    a = [
        [Fraction(x) for x in mat[i]]
        + [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]
    for c in range(n):
        pivot = next(i for i in range(c, n) if a[i][c] != 0)
        a[c], a[pivot] = a[pivot], a[c]
        z = a[c][c]
        a[c] = [v / z for v in a[c]]
        for i in range(n):
            if i != c and a[i][c] != 0:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[c][j] for j in range(2 * n)]
    return [row[n:] for row in a]


def matmul(a, b):
    return [
        [
            sum((a[i][k] * b[k][j] for k in range(len(b))), Fraction(0))
            for j in range(len(b[0]))
        ]
        for i in range(len(a))
    ]


def normalize_rowspace(a):
    rmat = independent_rows(a)
    pivots = independent_cols(rmat)
    basis = [[rmat[i][j] for j in pivots] for i in range(len(rmat))]
    f = matmul(inverse_q(basis), rmat)
    return pivots, f


def det_q(mat):
    n = len(mat)
    if n == 0:
        return Fraction(1)
    a = [[Fraction(x) for x in row] for row in mat]
    det = Fraction(1)
    for c in range(n):
        pivot = next((i for i in range(c, n) if a[i][c] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != c:
            a[c], a[pivot] = a[pivot], a[c]
            det = -det
        z = a[c][c]
        det *= z
        a[c] = [v / z for v in a[c]]
        for i in range(c + 1, n):
            if a[i][c] != 0:
                z = a[i][c]
                a[i] = [a[i][j] - z * a[c][j] for j in range(n)]
    return det


def exhaustive_tu_small(f):
    """Exact tiny-control TU replay, deliberately not a general recognizer."""
    m, n = len(f), len(f[0])
    for k in range(1, min(m, n) + 1):
        for rs in combinations(range(m), k):
            for cs in combinations(range(n), k):
                minor = [[f[i][j] for j in cs] for i in rs]
                d = det_q(minor)
                if d not in (Fraction(-1), Fraction(0), Fraction(1)):
                    return False, (rs, cs, d)
    return True, None


def matvec(a, x):
    return [
        sum((Fraction(a[i][j]) * x[j] for j in range(len(x))), Fraction(0))
        for i in range(len(a))
    ]


def exact_one(a, x):
    return all(v == 1 for v in matvec(a, x))


def normalized_rhs(f):
    return [sum(row, Fraction(0)) / 3 for row in f]


def normalized_feasible(f, b, x):
    return matvec(f, x) == b


def pointwise_equivalence(a, f):
    b = normalized_rhs(f)
    n = len(a[0])
    for bits in product((0, 1), repeat=n):
        x = [Fraction(v) for v in bits]
        assert exact_one(a, x) == normalized_feasible(f, b, x), bits


def k33_control():
    edges = [(u, v) for u in range(3) for v in range(3, 6)]
    a = [[int(v in e) for e in edges] for v in range(6)]
    assert all(sum(row) == 3 for row in a)

    pivots, f = normalize_rowspace(a)
    assert pivots == [0, 1, 2, 3, 6]
    ok, bad = exhaustive_tu_small(f)
    assert ok, bad
    pointwise_equivalence(a, f)

    # Diagonal perfect matching.
    x = [Fraction(0)] * len(edges)
    for e in ((0, 3), (1, 4), (2, 5)):
        x[edges.index(e)] = 1
    assert exact_one(a, x)
    assert normalized_feasible(f, normalized_rhs(f), x)
    return len(f), len(edges)


def network_unsat_control():
    a = [
        [1, 1, 1, 0, 0, 0],
        [1, 0, 0, 1, 1, 0],
        [1, 0, 0, 0, 1, 1],
        [0, 1, 0, 1, 1, 0],
        [0, 0, 1, 1, 1, 0],
    ]
    assert all(sum(row) == 3 for row in a)

    pivots, f = normalize_rowspace(a)
    assert pivots == [0, 1, 2, 3, 4]
    ok, bad = exhaustive_tu_small(f)
    assert ok, bad
    b = normalized_rhs(f)
    assert any(v.denominator != 1 for v in b)
    pointwise_equivalence(a, f)
    assert not any(exact_one(a, [Fraction(v) for v in bits])
                   for bits in product((0, 1), repeat=6))
    return b


def petersen_rejection_control():
    edges = []
    for i in range(5):
        edges.append(tuple(sorted((i, (i + 1) % 5))))
    for i in range(5):
        edges.append((i, 5 + i))
    inner = {
        tuple(sorted((5 + i, 5 + (i + 2) % 5)))
        for i in range(5)
    }
    edges += sorted(inner)
    assert len(edges) == 15 and len(set(edges)) == 15

    a = [[int(v in e) for e in edges] for v in range(10)]
    assert all(sum(row) == 3 for row in a)
    pivots, f = normalize_rowspace(a)
    assert pivots == list(range(10))

    # Fixed exact non-TU certificate under this deterministic edge/pivot ordering.
    rs = (0, 2, 9)
    cs = (11, 13, 14)
    minor = [[f[i][j] for j in cs] for i in rs]
    d = det_q(minor)
    assert d == -2, (minor, d)

    # The source itself is SAT (the five spokes form a perfect matching), so TU
    # rejection is not a SAT/UNSAT conclusion. The existing binet router handles it.
    x = [Fraction(0)] * len(edges)
    for i in range(5):
        x[edges.index((i, 5 + i))] = 1
    assert exact_one(a, x)
    return rs, cs, d


def main():
    kshape = k33_control()
    b = network_unsat_control()
    rs, cs, d = petersen_rejection_control()

    print("R5 E9 exact TU row-space router regression: PASS")
    print(f"K3,3 normalized shape = {kshape[0]} x {kshape[1]}; exhaustive tiny-control TU = PASS")
    print("network UNSAT normalized rhs =", [str(v) for v in b])
    print(f"Petersen non-TU witness: rows={rs} cols={cs} det={d}")
    print("scope: exhaustive minors are regression only; general theorem uses polynomial TU recognition")


if __name__ == "__main__":
    main()
