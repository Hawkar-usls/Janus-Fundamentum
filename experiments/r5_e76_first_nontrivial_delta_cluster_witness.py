#!/usr/bin/env python3
"""R5 E76: explicit nontrivial delta boundary cluster beyond the E75 radius.

E75 exhaustively proved that every connected C4-free Tanner cluster through
9 vertices is non-delta except the singleton ExactOne_3 check.

E76 gives an explicit positive witness beyond that radius.

A connected C4-free cluster with 7 check vertices and 6 variable vertices
(13 total) has exact projected boundary relation, on 7 boundary stubs,

    F = {117, 118}.

The two feasible masks differ by exactly the two lowest boundary bits:

    117 xor 118 = 3.

Twisting by feasible set 117 gives

    F * 117 = {0, 3},

which is the feasible-set family of a 2x2 skew-symmetric block embedded in
7 coordinates.  Hence this cluster boundary is a genuine linear even
delta-matroid, not merely a support that happens to pass exchange.

The same cluster occurs as an induced cluster in an explicit connected
9x9 square-cubic-linear carrier, frozen below.  The full carrier is Exact-One
UNSAT; thus local delta repair alone does not solve the global instance.

Scientific ceiling: E76 refutes a universal extension of the E75 finite-radius
barrier.  It does not yet provide a polynomial decomposition of arbitrary E12
hard targets.  P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import combinations, product

from r5_e75_c4free_cluster_delta_barrier import (
    boundary_relation,
    symmetric_exchange_failure,
)


# 13-vertex witness: 7 checks C0..C6, 6 variables V0..V5.
CLUSTER_EDGES = [
    (6,3), (2,1), (4,4), (0,3), (0,5), (3,4), (1,4), (3,1),
    (1,0), (1,3), (4,5), (0,1), (5,2), (6,2), (4,2), (5,0),
]

# A 9x9 square-cubic-linear completion containing the cluster on rows 0..6
# and columns 0..5.  Its induced edges there are exactly CLUSTER_EDGES.
A9 = [
    [0,1,0,1,0,1,0,0,0],
    [1,0,0,1,1,0,0,0,0],
    [0,1,0,0,0,0,1,1,0],
    [0,1,0,0,1,0,0,0,1],
    [0,0,1,0,1,1,0,0,0],
    [1,0,1,0,0,0,1,0,0],
    [0,0,1,1,0,0,0,1,0],
    [1,0,0,0,0,0,0,1,1],
    [0,0,0,0,0,1,1,0,1],
]


def determinant(M):
    n = len(M)
    if n == 0:
        return Fraction(1)
    A = [[Fraction(x) for x in row] for row in M]
    det = Fraction(1)
    for c in range(n):
        p = next((i for i in range(c, n) if A[i][c]), None)
        if p is None:
            return Fraction(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            det = -det
        z = A[c][c]
        det *= z
        for i in range(c + 1, n):
            if A[i][c]:
                f = A[i][c] / z
                for j in range(c, n):
                    A[i][j] -= f * A[c][j]
    return det


def skew_family_7():
    """Principal-nonsingularity family of one 2x2 skew block + five zero coords."""
    M = [[0] * 7 for _ in range(7)]
    M[0][1] = 1
    M[1][0] = -1
    F = set()
    for mask in range(1 << 7):
        idx = [i for i in range(7) if (mask >> i) & 1]
        P = [[M[i][j] for j in idx] for i in idx]
        if determinant(P) != 0:
            F.add(mask)
    return F


def verify_carrier(A):
    n = len(A)
    assert n == 9 and all(len(row) == n for row in A)
    assert all(v in (0,1) for row in A for v in row)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))

    # Linearity: no two columns meet in more than one row.
    for a, b in combinations(range(n), 2):
        assert sum(A[i][a] * A[i][b] for i in range(n)) <= 1

    # Connected Tanner graph.
    adj = [[] for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            if A[i][j]:
                adj[i].append(n+j)
                adj[n+j].append(i)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    assert len(seen) == 2*n


def induced_cluster_edges(A):
    return sorted(
        (i,j)
        for i in range(7)
        for j in range(6)
        if A[i][j]
    )


def exact_one_solutions(A):
    n = len(A)
    out = []
    for bits in product((0,1), repeat=n):
        if all(sum(A[i][j] * bits[j] for j in range(n)) == 1 for i in range(n)):
            out.append(bits)
    return out


def main():
    arity, family = boundary_relation(7, 6, CLUSTER_EDGES)
    assert arity == 7
    assert family == {117, 118}
    assert symmetric_exchange_failure(family, arity) is None

    # Twist by one feasible set.  The residual family is exactly one 2x2 skew
    # block: empty or both active coordinates.
    twisted = {x ^ 117 for x in family}
    assert twisted == {0, 3}
    assert skew_family_7() == twisted

    verify_carrier(A9)
    assert induced_cluster_edges(A9) == sorted(CLUSTER_EDGES)

    sols = exact_one_solutions(A9)
    assert sols == []

    print("R5 E76 first nontrivial delta-cluster witness: PASS")
    print("cluster: checks=7 variables=6 total=13 boundary_arity=7")
    print("boundary family = {117,118}; xor=3")
    print("twist by 117 -> {0,3}, exactly one embedded 2x2 skew-symmetric block")
    print("therefore boundary relation is a genuine linear even delta-matroid")
    print("explicit completion: connected 9x9 square-cubic-linear carrier")
    print("full completion Exact-One status: UNSAT")
    print("consequence: E75 finite-radius barrier does NOT extend to all bounded clusters")
    print("live question: can such delta clusters cover/compress the E12 hardness image with polynomial interfaces?")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
