#!/usr/bin/env python3
"""R5 E61 exact controls: two-level real kernel vectors are the Exact-One object.

For a simple linear square-cubic carrier A, put

    G = A^T A - 3 I.

Then G is a simple 6-regular conflict graph and A^T A = G + 3I.  Exact-One
Ax=1 over the integers is equivalent to

    y = 3x-1 in ker_R(A),   y_i in {-1,2}.

For S={i:y_i=2}, the eigen-equation Gy=-3y forces

    vertices in S     : 0 neighbours in S,
    vertices outside S: 3 neighbours in S,

so S is a (0,3)-regular set / perfect 2-coloring with quotient matrix

    [[0,6],
     [3,3]].

The checker also implements the exact 2^d * poly(n) algorithm, where

d = dim_R ker(A) = multiplicity of -3 in G.

A row-reduced nullspace basis is parameterized by its free coordinates.  Any
wanted y must assign each free coordinate one of {-1,2}; after one of the 2^d
assignments is fixed, every pivot coordinate is forced linearly.  We accept iff
all forced coordinates are again in {-1,2}.

Controls:
  * SAT12: linear square-cubic, real nullity 1, exactly one two-level witness;
  * UNSAT12: the frozen R5 E57 carrier, real nullity 1 and a full-support
    real/integer kernel vector, but no {-1,2}-valued kernel vector.
"""

import itertools
from fractions import Fraction


P_SAT = [7, 6, 11, 10, 8, 4, 9, 5, 0, 3, 2, 1]
Q_SAT = [11, 8, 3, 4, 7, 9, 0, 10, 2, 1, 6, 5]

# Frozen R5 E57 negative control.
P_UNSAT = [6, 3, 7, 10, 11, 1, 4, 8, 9, 5, 2, 0]
Q_UNSAT = [3, 4, 5, 8, 7, 0, 9, 6, 2, 11, 1, 10]
Z_UNSAT = [-1, -1, 2, -1, 2, 2, 2, -4, 2, -4, -1, 2]


def build_A(p, q):
    n = len(p)
    assert sorted(p) == list(range(n))
    assert sorted(q) == list(range(n))
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        cols = (i, p[i], q[i])
        assert len(set(cols)) == 3
        for j in cols:
            A[i][j] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    return A


def transpose(A):
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    BT = transpose(B)
    return [[sum(a * b for a, b in zip(row, col)) for col in BT] for row in A]


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def conflict_graph(A):
    n = len(A)
    ATA = matmul(transpose(A), A)
    G = [[ATA[i][j] - (3 if i == j else 0) for j in range(n)] for i in range(n)]
    return ATA, G


def rref_nullspace(A):
    """Exact rational RREF; basis vectors are indexed by free coordinates."""
    M = [[Fraction(v) for v in row] for row in A]
    m = len(M)
    n = len(M[0])
    pivots = []
    r = 0

    for c in range(n):
        pivot = next((i for i in range(r, m) if M[i][c] != 0), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [M[i][j] - f * M[r][j] for j in range(n)]
        pivots.append(c)
        r += 1
        if r == m:
            break

    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0) for _ in range(n)]
        v[f] = Fraction(1)
        for ri, pc in enumerate(pivots):
            v[pc] = -M[ri][f]
        basis.append(v)

    # The chosen basis has identity coordinates on the free positions.
    for j, f in enumerate(free):
        assert basis[j][f] == 1
        assert all(basis[k][f] == (1 if k == j else 0) for k in range(len(free)))

    return pivots, free, basis


def two_level_kernel_vectors(A):
    """Exact O(2^d poly(n)) search with d=dim_R ker(A)."""
    _, free, basis = rref_nullspace(A)
    n = len(A)
    out = []

    for values in itertools.product((-1, 2), repeat=len(free)):
        y = [Fraction(0) for _ in range(n)]
        for value, b in zip(values, basis):
            for i in range(n):
                y[i] += value * b[i]

        if not all(v in (Fraction(-1), Fraction(2)) for v in y):
            continue

        yi = [int(v) for v in y]
        assert matvec(A, yi) == [0] * n
        out.append(yi)

    return len(free), out


def exact_one_from_y(A, y):
    assert all(v in (-1, 2) for v in y)
    x = [(v + 1) // 3 for v in y]
    assert all(v in (0, 1) for v in x)
    assert matvec(A, x) == [1] * len(A)
    return x


def verify_linear_conflict_structure(A):
    n = len(A)
    ATA, G = conflict_graph(A)

    assert all(ATA[i][i] == 3 for i in range(n))
    assert all(
        ATA[i][j] in (0, 1)
        for i in range(n)
        for j in range(n)
        if i != j
    )
    assert all(G[i][i] == 0 for i in range(n))
    assert all(G[i][j] in (0, 1) for i in range(n) for j in range(n) if i != j)
    assert all(sum(row) == 6 for row in G)
    return G


def verify_hoffman_tight_partition(G, y):
    n = len(G)
    S = {i for i, value in enumerate(y) if value == 2}
    assert len(S) * 3 == n

    # Gy=-3y follows from A^T A y=0 in the carrier.  Here replay the local
    # quotient consequences directly.
    for i in range(n):
        inside = sum(G[i][j] for j in S)
        if i in S:
            assert inside == 0
        else:
            assert inside == 3

    # Quotient matrix with color order (S, V\S): [[0,6],[3,3]].
    for i in S:
        assert sum(G[i][j] for j in S) == 0
        assert sum(G[i][j] for j in range(n) if j not in S) == 6
    for i in range(n):
        if i not in S:
            assert sum(G[i][j] for j in S) == 3
            assert sum(G[i][j] for j in range(n) if j not in S) == 3


def check_fixture(name, p, q, expect_sat, expected_nullity):
    A = build_A(p, q)
    G = verify_linear_conflict_structure(A)
    d, ys = two_level_kernel_vectors(A)

    assert d == expected_nullity
    assert bool(ys) == expect_sat

    for y in ys:
        # Kernel/eigenvalue bridge.
        assert matvec(A, y) == [0] * len(A)
        assert matvec(G, y) == [-3 * v for v in y]
        x = exact_one_from_y(A, y)
        verify_hoffman_tight_partition(G, y)
        assert sum(x) * 3 == len(A)

    print(f"{name}: n={len(A)} real_nullity={d} two_level_witnesses={len(ys)} sat={bool(ys)}")
    return A, ys


def main():
    A_sat, ys_sat = check_fixture("SAT12", P_SAT, Q_SAT, True, 1)
    assert len(ys_sat) == 1
    assert {i for i, v in enumerate(ys_sat[0]) if v == 2} == {8, 9, 10, 11}

    A_unsat, ys_unsat = check_fixture("UNSAT12_E57", P_UNSAT, Q_UNSAT, False, 1)
    assert ys_unsat == []

    # E57's stronger negative fact survives: singularity and even a full-support
    # integer kernel vector do not imply the required two-level kernel vector.
    assert all(v != 0 for v in Z_UNSAT)
    assert matvec(A_unsat, Z_UNSAT) == [0] * len(A_unsat)
    assert any(v not in (-1, 2) for v in Z_UNSAT)

    print("R5 E61 two-level kernel / Hoffman (0,3)-regular-set theorem: PASS")
    print("exact solver cost: 2^d nullspace assignments, d=dim_R ker(A)=mult_G(-3)")
    print("SAT12 has a {-1,2} kernel vector; E57 UNSAT12 has only non-two-level kernel directions")


if __name__ == "__main__":
    main()
