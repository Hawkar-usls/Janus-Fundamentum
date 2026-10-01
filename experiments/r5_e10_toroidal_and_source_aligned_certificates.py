#!/usr/bin/env python3
"""Exact finite controls for R5 E10.

Dependency-free checker for:
  * Q-rank/nullity of the frozen PG15 SAT/UNSAT controls;
  * the explicit source-aligned PG15_UNSAT clique certificate;
  * the square/cubic/linear toroidal family A_k;
  * its explicit SAT witness when 3|k;
  * the predicted Q-nullity 2 (3|k) / 0 (otherwise), on finite controls.

Finite controls do not replace the symbolic proofs in the companion note.
"""

from fractions import Fraction
from itertools import combinations

SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

PERM_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PERM_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]


def matrix_from_rows(rows, n):
    return [[int(j + 1 in row) for j in range(n)] for row in rows]


def singular_unsat_matrix():
    n = 15
    A = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in (i, PERM_P[i], PERM_Q[i]):
            A[i][j] = 1
    return A


def rank_q(M):
    """Exact Gaussian rank over Q."""
    A = [[Fraction(x) for x in row] for row in M]
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        q = A[r][c]
        A[r] = [v / q for v in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def matvec(A, x):
    return [sum(a * b for a, b in zip(row, x)) for row in A]


def transpose_matvec(A, c):
    return [sum(c[i] * A[i][j] for i in range(len(A)))
            for j in range(len(A[0]))]


def conflict_graph(A):
    n = len(A[0])
    adj = [set() for _ in range(n)]
    for row in A:
        vs = [j for j, v in enumerate(row) if v]
        for u, v in combinations(vs, 2):
            adj[u].add(v)
            adj[v].add(u)
    return adj


def is_clique(adj, vertices):
    return all(v in adj[u] for u, v in combinations(vertices, 2))


def check_pg15():
    A_sat = matrix_from_rows(SAT_ROWS, 15)
    A_unsat = singular_unsat_matrix()

    assert rank_q(A_sat) == 11
    assert rank_q(A_unsat) == 14

    # R5 E10 source-aligned certificate, all vertex labels below are 1-based.
    omitted = {2, 6, 11}
    U = {v for v in range(1, 16) if v not in omitted}
    c = (9,5,8,10,6,-18,11,3,13,6,8,9,2,4,0)

    rhs = transpose_matvec(A_unsat, c)
    assert rhs == [19 if j + 1 in U else 0 for j in range(15)]
    assert sum(c) == 76

    adj = conflict_graph(A_unsat)
    cover = [
        (1,7,9,13),
        (3,8,10,15),
        (4,5,12,14),
    ]
    assert set().union(*(set(C) for C in cover)) == U
    assert sum(len(C) for C in cover) == len(U)  # disjoint here
    for C in cover:
        assert is_clique(adj, [v - 1 for v in C])

    # Any Exact-One witness would have 19*x(U)=76, so x(U)=4,
    # while the three-clique cover gives x(U)<=3.
    assert Fraction(sum(c), 19) == 4
    assert len(cover) == 3

    return {
        "sat_rank": 11,
        "sat_nullity": 4,
        "unsat_rank": 14,
        "unsat_nullity": 1,
        "local_U_size": len(U),
        "clique_cover": len(cover),
    }


def toroidal_matrix(k):
    n = k * k
    A = [[0] * n for _ in range(n)]

    def vid(i, j):
        return (i % k) * k + (j % k)

    for i in range(k):
        for j in range(k):
            r = vid(i, j)
            for v in (vid(i, j), vid(i + 1, j), vid(i, j + 1)):
                A[r][v] = 1
    return A


def check_square_cubic_linear(A):
    m, n = len(A), len(A[0])
    assert m == n
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(m)) == 3 for j in range(n))
    supports = [{j for j, v in enumerate(row) if v} for row in A]
    assert all(len(supports[i] & supports[j]) <= 1
               for i in range(m) for j in range(i + 1, m))


def toroidal_witness(k):
    return [int((i - j) % 3 == 0) for i in range(k) for j in range(k)]


def check_torus_edges(A, k):
    adj = conflict_graph(A)

    def vid(i, j):
        return (i % k) * k + (j % k)

    for i in range(k):
        for j in range(k):
            v = vid(i, j)
            assert vid(i + 1, j) in adj[v]
            assert vid(i, j + 1) in adj[v]


def check_toroidal_family():
    rows = []
    # k<=9 keeps exact Fraction elimination fast in ordinary CI while
    # testing both residue classes and three SAT sizes.
    for k in range(3, 10):
        A = toroidal_matrix(k)
        check_square_cubic_linear(A)
        check_torus_edges(A, k)

        n = k * k
        rank = rank_q(A)
        nullity = n - rank
        expected_nullity = 2 if k % 3 == 0 else 0
        assert nullity == expected_nullity

        if k % 3 == 0:
            x = toroidal_witness(k)
            assert matvec(A, x) == [1] * n
            witness = "EXPLICIT_SAT"
        else:
            # Symbolic UNSAT is proved in the note by the row-sum recurrence
            # 2 R_i + R_{i+1}=k.  The full Q-rank check here independently
            # gives an even stronger finite-control conclusion: Ax=1 has the
            # unique rational solution x=(1/3)1, which is not Boolean.
            assert rank == n
            witness = "Q_UNIQUE_NONBOOLEAN"

        rows.append((k, n, rank, nullity, witness))
    return rows


def main():
    pg = check_pg15()
    torus = check_toroidal_family()

    print("R5 E10 exact controls: PASS")
    print(
        "PG15: "
        f"SAT rank/nullity={pg['sat_rank']}/{pg['sat_nullity']}; "
        f"UNSAT rank/nullity={pg['unsat_rank']}/{pg['unsat_nullity']}; "
        f"local certificate |U|={pg['local_U_size']} vs "
        f"clique-cover={pg['clique_cover']}"
    )
    print("toroidal controls:")
    for k, n, rank, nullity, verdict in torus:
        print(f"  k={k}: n={n}, rank_Q={rank}, nullity_Q={nullity}, {verdict}")


if __name__ == "__main__":
    main()
