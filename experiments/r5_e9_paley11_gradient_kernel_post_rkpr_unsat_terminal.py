#!/usr/bin/env python3
"""Exact replay for the Paley(11) gradient-kernel post-RKPR UNSAT terminal."""

from itertools import combinations
from collections import deque
from fractions import Fraction

Q = 11
RES = {1, 3, 4, 5, 9}

PIVOT_COLS = [
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
    25,26,27,28,29,30,31,32,33,34,35,36,38,39,40,41,42,44,46,47,
]
PIVOT_ROWS = [
    0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,
    25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,45,46,
]


def is_arc(u, v):
    return u != v and ((v-u) % Q) in RES


def build_source():
    arcs = [(u, v) for u in range(Q) for v in range(Q) if is_arc(u, v)]
    arc_index = {e: i for i, e in enumerate(arcs)}

    triangles = []
    for a, b, c in combinations(range(Q), 3):
        verts = (a, b, c)
        outdeg = {v: 0 for v in verts}
        oriented = []
        for u, v in ((a,b), (a,c), (b,c)):
            e = (u,v) if is_arc(u,v) else (v,u)
            oriented.append(e)
            outdeg[e[0]] += 1
        if sorted(outdeg.values()) == [1,1,1]:
            triangles.append(tuple(oriented))

    A = [[0]*len(arcs) for _ in triangles]
    for i, tri in enumerate(triangles):
        for e in tri:
            A[i][arc_index[e]] = 1
    return arcs, triangles, A


def bareiss_det(M):
    a = [row[:] for row in M]
    n = len(a)
    if n == 0:
        return 1
    sign = 1
    prev = 1
    for k in range(n-1):
        if a[k][k] == 0:
            p = next((r for r in range(k+1, n) if a[r][k] != 0), None)
            if p is None:
                return 0
            a[k], a[p] = a[p], a[k]
            sign *= -1
        pivot = a[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                num = a[i][j]*pivot - a[i][k]*a[k][j]
                assert num % prev == 0
                a[i][j] = num // prev
        for i in range(k+1, n):
            a[i][k] = 0
        prev = pivot
    return sign*a[-1][-1]


def matmul(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))]
            for i in range(len(A))]


def gauge_gradient(arcs):
    # Columns are p_1,...,p_10, with p_0 fixed to 0.
    D = []
    for u, v in arcs:
        row = [0]*(Q-1)
        if u != 0:
            row[u-1] -= 1
        if v != 0:
            row[v-1] += 1
        D.append(row)
    return D


def proportional(a, b):
    ia = next((i for i,x in enumerate(a) if x), None)
    ib = next((i for i,x in enumerate(b) if x), None)
    if ia is None or ib is None:
        return ia is None and ib is None
    if {i for i,x in enumerate(a) if x} != {i for i,x in enumerate(b) if x}:
        return False
    lam = Fraction(a[ia], b[ia])
    return all(Fraction(a[i],1) == lam*Fraction(b[i],1) for i in range(len(a)))


def levi_connected(A):
    nr, nc = len(A), len(A[0])
    adj = [[] for _ in range(nr+nc)]
    for i,row in enumerate(A):
        for j,x in enumerate(row):
            if x:
                adj[i].append(nr+j)
                adj[nr+j].append(i)
    seen = {0}
    dq = deque([0])
    while dq:
        u = dq.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                dq.append(v)
    return len(seen) == nr+nc


def main():
    arcs, triangles, A = build_source()
    assert len(arcs) == 55
    assert len(triangles) == 55
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(55)) == 3 for j in range(55))

    supports = [{j for j,x in enumerate(row) if x} for row in A]
    assert all(len(supports[i] & supports[j]) <= 1
               for i in range(55) for j in range(i+1,55))
    assert levi_connected(A)

    D = gauge_gradient(arcs)
    AD = matmul(A, D)
    assert all(x == 0 for row in AD for x in row)

    # D has rank 10: for each v=1..10 the tournament edge on {0,v}
    # contributes one row +/- e_v.
    witness_rows = []
    for v in range(1,Q):
        e = (0,v) if is_arc(0,v) else (v,0)
        witness_rows.append(D[arcs.index(e)])
    det_D = bareiss_det(witness_rows)
    assert abs(det_D) == 1

    minor = [[A[i][j] for j in PIVOT_COLS] for i in PIVOT_ROWS]
    det_minor = bareiss_det(minor)
    assert det_minor == -3, det_minor

    # rank(A)<=45 from the 10-dimensional gradient kernel; the nonzero
    # 45-minor gives rank(A)>=45.
    rank_A = 45
    nullity_A = 55-rank_A
    assert nullity_A == 10

    assert all(any(x != 0 for x in row) for row in D)
    prop_pairs = []
    for i in range(55):
        for j in range(i+1,55):
            if proportional(D[i],D[j]):
                prop_pairs.append((i,j))
    assert prop_pairs == []

    # Symbolic UNSAT implication: if Ax=1, y=3x-1 lies in ker(A)=im(D).
    # Thus all vertex-potential pair distances belong to {1,2}.  Distinct
    # values with all pairwise distances in {1,2} number at most three.
    assert Q >= 4
    max_vertices_under_pairwise_gap = 3
    assert Q > max_vertices_under_pairwise_gap

    print("PALEY11_GRADIENT_KERNEL_POST_RKPR_UNSAT_TERMINAL: PASS")
    print("arcs=55 triangles=55 row_degree=3 col_degree=3 linear=True connected=True")
    print(f"gradient_rank=10 fixed_minor_det={det_minor} rank_Q(A)=45 nullity_Q(A)=10")
    print("RKPR zero_rows=0 proportional_pairs=0")
    print("Exact-One status=UNSAT by complete-gradient potential-range contradiction")


if __name__ == "__main__":
    main()
