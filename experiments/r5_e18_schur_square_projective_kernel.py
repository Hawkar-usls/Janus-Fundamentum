#!/usr/bin/env python3
"""Exact controls for R5 E18.

Verifies the 42-variable Schur-square firewall:
  * construct all directed 3-cycles on K7;
  * remove two disjoint directed-triangle decompositions;
  * obtain a 42x42 square/cubic/linear Exact-One source;
  * exact rational rank = 36, hence nullity = 6;
  * the A6 root space y_ij=t_i-t_j is a 6-dimensional subspace of ker(A),
    therefore it is the whole kernel;
  * Q2/Schur-square passes because sum_c u_c^2 = 2*1;
  * nevertheless no {-1,2}-valued kernel vector exists because
    y_ji=-y_ij while {-1,2} contains no nonzero pair a,-a.

This is a negative control for promoting the degree-2 Schur-square
necessary condition to a universal algorithm.
"""

from fractions import Fraction
from itertools import combinations


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
    m = len(A)
    n = len(A[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def cycle_edges(c):
    a, b, d = c
    return ((a,b),(b,d),(d,a))


def all_directed_triangles(m=7):
    out = []
    for a,b,c in combinations(range(m),3):
        out.append((a,b,c))
        out.append((a,c,b))
    return out


def check_decomposition(D, arcs):
    seen = []
    for c in D:
        seen.extend(cycle_edges(c))
    assert len(D) == 14
    assert len(seen) == 42
    assert set(seen) == set(arcs)
    assert len(set(seen)) == 42


def build_firewall():
    m = 7
    arcs = [(i,j) for i in range(m) for j in range(m) if i != j]
    ai = {a:i for i,a in enumerate(arcs)}
    triangles = all_directed_triangles(m)

    check_decomposition(D1, arcs)
    check_decomposition(D2, arcs)

    s1 = {frozenset(cycle_edges(c)) for c in D1}
    s2 = {frozenset(cycle_edges(c)) for c in D2}
    assert s1.isdisjoint(s2)

    remain = [
        c for c in triangles
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

    supports = [{j for j,v in enumerate(row) if v} for row in A]
    assert all(
        len(supports[i] & supports[j]) <= 1
        for i in range(42) for j in range(i)
    )

    return arcs, remain, A


def root_vectors(arcs):
    # Seven coordinate functions u_c(i->j)=1_{i=c}-1_{j=c}.
    U = []
    for c in range(7):
        U.append([
            (1 if i == c else 0) - (1 if j == c else 0)
            for i,j in arcs
        ])
    return U


def matvec(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def check_root_kernel(arcs, A):
    U = root_vectors(arcs)

    for u in U:
        assert matvec(A, u) == [0]*42

    # The seven coordinate functions have exactly one relation sum_c u_c=0,
    # so their span has dimension six.
    Ut = [[U[c][j] for c in range(7)] for j in range(42)]
    assert rank_q(Ut) == 6

    rankA = rank_q(A)
    assert rankA == 36
    assert 42 - rankA == 6

    # Hence the root space is the entire kernel.

    # Q2 / Schur-square pass:
    # for every directed arc i->j, exactly two coordinate functions are
    # nonzero (+1 and -1), so sum_c u_c^2 = 2.
    schur_sum = [
        sum(U[c][j] * U[c][j] for c in range(7))
        for j in range(42)
    ]
    assert schur_sum == [2]*42

    # Exact UNSAT witness obstruction:
    # every kernel vector is y_ij=t_i-t_j, hence y_ji=-y_ij.
    # The alphabet {-1,2} contains no a with -a also in the alphabet.
    alphabet = {-1,2}
    assert not any((-a) in alphabet for a in alphabet)

    return rankA


def main():
    arcs, remain, A = build_firewall()
    rankA = check_root_kernel(arcs, A)
    print("R5 E18 exact controls: PASS")
    print("firewall: n=42, rows=42, row/col weight=3, linear=True")
    print(f"rank_Q(A)={rankA}, nullity_Q(A)={42-rankA}")
    print("Q2 Schur-square condition: PASS via A6 root norms")
    print("Exact-One verdict: UNSAT via y_ji=-y_ij alphabet obstruction")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
