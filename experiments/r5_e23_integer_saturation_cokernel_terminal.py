#!/usr/bin/env python3
"""Exact finite controls for R5 E23.

Checks two complementary frozen controls for the integer-saturation terminal:

1. The R5 E18 42-variable Q2 firewall is already integer-infeasible.  For an
   opposite arc pair (i->j),(j->i), the integer vector c=e_ij+e_ji lies in the
   rational row space of A and has sum(c)=2, not divisible by 3.  Hence Ax=1
   has no integer solution.

2. PG15_UNSAT is a firewall against promoting integer feasibility to SAT.  Its
   primitive kernel vector z gives the explicit integral non-Boolean solution

       x = (1 + 2 z)/3,

   so Ax=1 is integer-feasible although the frozen instance is Exact-One UNSAT.

Dependency-free exact Fraction arithmetic only.
P_VS_NP remains OPEN.
"""

from fractions import Fraction
from itertools import combinations


PG15_P = [5,7,9,10,3,1,14,2,4,6,12,13,8,0,11]
PG15_Q = [12,9,14,11,13,10,7,3,1,0,2,5,6,8,4]
PG15_KERNEL = (1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1)

D1 = [
    (0,1,2),(0,3,1),(0,4,3),(0,5,4),(0,6,5),(0,2,6),(1,5,2),
    (1,6,4),(2,4,6),(1,4,5),(1,3,6),(2,3,4),(2,5,3),(3,5,6),
]
D2 = [
    (0,1,5),(0,2,4),(0,3,2),(0,4,6),(1,3,4),(4,5,6),(0,5,3),
    (0,6,1),(2,6,5),(3,5,4),(1,4,2),(1,6,3),(1,2,5),(2,3,6),
]


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    if not A:
        return 0
    m, n = len(A), len(A[0])
    r = 0
    for col in range(n):
        pivot = next((i for i in range(r, m) if A[i][col]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][col]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][col]:
                f = A[i][col]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def matvec(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def pg15_unsat_matrix():
    n = 15
    A = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i, PG15_P[i], PG15_Q[i]):
            A[i][j] = 1
    return A


def cycle_edges(c):
    a,b,d = c
    return ((a,b),(b,d),(d,a))


def all_directed_triangles(m=7):
    out = []
    for a,b,c in combinations(range(m),3):
        out.append((a,b,c))
        out.append((a,c,b))
    return out


def build_a42():
    arcs = [(i,j) for i in range(7) for j in range(7) if i != j]
    ai = {a:i for i,a in enumerate(arcs)}
    s1 = {frozenset(cycle_edges(c)) for c in D1}
    s2 = {frozenset(cycle_edges(c)) for c in D2}
    remain = [
        c for c in all_directed_triangles(7)
        if frozenset(cycle_edges(c)) not in s1
        and frozenset(cycle_edges(c)) not in s2
    ]
    assert len(remain) == 42
    A = [[0]*42 for _ in range(42)]
    for r,c in enumerate(remain):
        for e in cycle_edges(c):
            A[r][ai[e]] = 1
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(42)) == 3 for j in range(42))
    return arcs, ai, A


def check_a42_integer_obstruction():
    arcs, ai, A = build_a42()
    assert rank_q(A) == 36

    # Pick one opposite pair.  c is orthogonal to the A6 root kernel because
    # r_ji=-r_ij.  Since that root space is the entire six-dimensional kernel,
    # c lies in row_Q(A).  We verify row-space membership independently by rank.
    c = [0]*42
    c[ai[(0,1)]] = 1
    c[ai[(1,0)]] = 1
    assert sum(c) == 2
    assert rank_q(A + [c]) == rank_q(A)
    assert sum(c) % 3 != 0

    # Therefore no integral x can solve Ax=1: if c=A^T lambda, then
    # c.x=lambda.1=sum(c)/3=2/3, impossible for integral c.x.
    return 42, 36, tuple(i for i,v in enumerate(c) if v)


def check_pg15_integer_firewall():
    A = pg15_unsat_matrix()
    z = list(PG15_KERNEL)
    assert matvec(A, z) == [0]*15

    # x=(1+2z)/3 is integral coordinatewise because z is 1 mod 3 everywhere.
    numer = [1 + 2*v for v in z]
    assert all(v % 3 == 0 for v in numer)
    x = [v//3 for v in numer]
    assert matvec(A, x) == [1]*15
    assert any(v not in (0,1) for v in x)
    return x


def main():
    n, rank, pair = check_a42_integer_obstruction()
    x = check_pg15_integer_firewall()
    print("R5 E23 integer-saturation controls: PASS")
    print(f"A42: n={n}, rank_Q={rank}, integer-rowspace certificate support={pair}, sum(c)=2 -> INTEGER_UNSAT")
    print(f"PG15_UNSAT: explicit integer non-Boolean solution x={x}")
    print("Conclusion: integer infeasibility is a sound polynomial UNSAT terminal, not a complete Exact-One solver")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
