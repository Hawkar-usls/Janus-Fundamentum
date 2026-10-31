#!/usr/bin/env python3
"""Exact finite controls for the rational-kernel sign / Tukey-depth quotient.

This checker validates the new sign-count identities on the frozen PG15 SAT
control and computes the exact chamber depth of the frozen one-dimensional
singular UNSAT countercontrol.  It is finite validation only; the arbitrary-size
theorem is proved in the companion research note.
"""

from fractions import Fraction
from itertools import combinations, product

SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
G = [1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1]


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def singular_unsat_matrix():
    n = 15
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, P[i], Q[i]):
            A[i][j] = 1
    return A


def rref_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m = len(A)
    n = len(A[0])
    pivots = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        f = A[r][c]
        A[r] = [z / f for z in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
    return A, pivots


def rank_q(M):
    return len(rref_q(M)[1])


def kernel_basis(M):
    R, pivots = rref_q(M)
    n = len(M[0])
    free = [j for j in range(n) if j not in pivots]
    basis = []
    for f in free:
        x = [Fraction(0) for _ in range(n)]
        x[f] = 1
        for i, p in enumerate(pivots):
            x[p] = -R[i][f]
        basis.append(x)
    return basis


def matvec(A, x):
    return [sum(Fraction(a) * b for a, b in zip(row, x)) for row in A]


def assert_cubic(A):
    n = len(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))


def witness_sets(A):
    n = len(A)
    if n % 3:
        return []
    out = []
    for C in combinations(range(n), n // 3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            out.append(S)
    return out


def sign_counts(y):
    assert all(v != 0 for v in y)
    p = sum(v > 0 for v in y)
    return p, len(y) - p


def row_sign_types(A, y):
    one = two = 0
    for row in A:
        vals = [y[j] for j, a in enumerate(row) if a]
        assert len(vals) == 3
        assert sum(vals) == 0
        q = sum(v > 0 for v in vals)
        assert q in (1, 2)
        if q == 1:
            one += 1
        else:
            two += 1
    return one, two


def check_identity(A, y):
    n = len(A)
    assert matvec(A, y) == [0] * n
    p, _ = sign_counts(y)
    m1, m2 = row_sign_types(A, y)
    assert m1 + m2 == n
    assert m2 == 3 * p - n
    assert m1 == 2 * n - 3 * p
    assert 3 * p >= n
    assert 3 * p <= 2 * n
    return p, m1, m2


def main():
    # Positive boundary control: frozen series-irreducible PG15 SAT source.
    A_sat = matrix_from_rows(SAT_ROWS, 15)
    assert_cubic(A_sat)
    assert rank_q(A_sat) == 11
    B_sat = kernel_basis(A_sat)
    assert len(B_sat) == 4

    # No coordinate is identically zero on the rational kernel.
    row_vectors = [tuple(B_sat[c][i] for c in range(len(B_sat)))
                   for i in range(15)]
    assert all(any(z != 0 for z in r) for r in row_vectors)

    witnesses = witness_sets(A_sat)
    assert len(witnesses) == 4
    for S in witnesses:
        y = [Fraction(2 if i in S else -1) for i in range(15)]
        p, m1, m2 = check_identity(A_sat, y)
        assert p == 5
        assert m1 == 15
        assert m2 == 0

    # Finite chamber sampling is only a regression: every sampled full-support
    # rational-kernel vector obeys the theorem's 1/3..2/3 sign bound, and the
    # explicit witness vectors attain the lower boundary.
    sampled = 0
    sampled_min_oriented = 15
    for coeff in product(range(-3, 4), repeat=len(B_sat)):
        if all(c == 0 for c in coeff):
            continue
        y = [sum(Fraction(coeff[t]) * B_sat[t][i]
                 for t in range(len(B_sat))) for i in range(15)]
        if any(v == 0 for v in y):
            continue
        p, m1, m2 = check_identity(A_sat, y)
        sampled += 1
        sampled_min_oriented = min(sampled_min_oriented, p, 15 - p)
        assert m1 >= 0 and m2 >= 0
    assert sampled > 0
    assert sampled_min_oriented == 5

    # Negative strict-depth control: frozen singular rank-14 UNSAT source.
    A_unsat = singular_unsat_matrix()
    assert_cubic(A_unsat)
    assert rank_q(A_unsat) == 14
    assert len(kernel_basis(A_unsat)) == 1
    g = [Fraction(v) for v in G]
    p_g, m1_g, m2_g = check_identity(A_unsat, g)
    assert p_g == 9
    assert m1_g == 3
    assert m2_g == 12

    # The only two chambers of a one-dimensional kernel are +/-g.
    p_minus, m1_minus, m2_minus = check_identity(A_unsat, [-v for v in g])
    assert p_minus == 6
    assert m1_minus == 12
    assert m2_minus == 3
    exact_unsat_depth = min(p_g, p_minus)
    assert exact_unsat_depth == 6
    assert exact_unsat_depth > 15 // 3
    assert 3 * exact_unsat_depth - 15 == 3
    assert witness_sets(A_unsat) == []

    print({
        'status': 'PASS_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_CONTROLS',
        'sat_rank_q': rank_q(A_sat),
        'sat_nullity_q': len(B_sat),
        'sat_exact_witnesses': len(witnesses),
        'sat_boundary_depth': 5,
        'sat_normalized_depth': '1/3',
        'sat_sampled_full_support_topes': sampled,
        'unsat_rank_q': rank_q(A_unsat),
        'unsat_nullity_q': 1,
        'unsat_exact_depth': exact_unsat_depth,
        'unsat_normalized_depth': '2/5',
        'unsat_depth_gap_3h_minus_n': 3,
        'P_VS_NP': 'OPEN',
        'E8_D1': 'EMPTY',
    })


if __name__ == '__main__':
    main()
