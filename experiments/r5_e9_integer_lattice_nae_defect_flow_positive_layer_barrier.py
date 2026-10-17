#!/usr/bin/env python3
"""Exact stdlib regression for the NAE defect-flow decomposition and p>0 barrier.

Finite checks are regression only. The theorem file contains the symbolic proof.
"""

from fractions import Fraction
from itertools import product

ROWS = [
    (0,14,11),(1,13,3),(2,1,7),(3,2,8),(4,3,5),
    (5,11,9),(6,0,2),(7,8,14),(8,6,4),(9,7,6),
    (10,4,1),(11,12,13),(12,10,0),(13,5,10),(14,9,12),
]

Z0 = [-1,1,0,1,-1,1,2,0,0,-1,1,1,1,-1,1]
V  = [-4,2,-1,2,-4,2,5,-1,-1,-4,2,2,2,-4,2]


def incidence(rows, n=15):
    A = [[0] * n for _ in range(n)]
    for i, row in enumerate(rows):
        assert len(set(row)) == 3
        for j in row:
            A[i][j] = 1
    return A


def mv(A, x):
    return [sum(a*b for a,b in zip(row,x)) for row in A]


def rank_q(M):
    M = [[Fraction(x) for x in row] for row in M]
    m = len(M); n = len(M[0]); r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if M[i][c]), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        pv = M[r][c]
        M[r] = [x/pv for x in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [M[i][j] - f*M[r][j] for j in range(n)]
        r += 1
    return r


def connected_levi(A):
    n = len(A)
    adj = [[] for _ in range(2*n)]
    for r in range(n):
        for c,a in enumerate(A[r]):
            if a:
                adj[r].append(n+c)
                adj[n+c].append(r)
    seen = {0}; stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen) == 2*n


def F(z):
    return sum(abs(2*t-1) for t in z)


def decomposition(A, z):
    n = len(A)
    b = [1 if t >= 1 else 0 for t in z]
    g = [z[i] - b[i] for i in range(n)]
    p = [g[i] if b[i] else 0 for i in range(n)]
    q = [0 if b[i] else -g[i] for i in range(n)]
    assert all(x >= 0 for x in p+q)
    rb = mv(A,b)
    assert all(t in (1,2) for t in rb)
    T = [r for r,t in enumerate(rb) if t == 2]
    lhs = [x-y for x,y in zip(mv(A,p), mv(A,q))]
    rhs = [-1 if r in T else 0 for r in range(n)]
    assert lhs == rhs
    ps = sum(p); qs = sum(q)
    assert len(T) == 3*(qs-ps)
    assert F(z)-n == 4*ps + 2*len(T)//3
    return b,p,q,T


def check_local_nae_lemma():
    # Exhaust a wide local scalar box: every integer triple summing to one
    # has threshold weight one or two.
    for a,b,c in product(range(-6,8), repeat=3):
        if a+b+c != 1:
            continue
        w = sum(t >= 1 for t in (a,b,c))
        assert w in (1,2)


def main():
    check_local_nae_lemma()
    A = incidence(ROWS)
    n = 15
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[r][c] for r in range(n)) == 3 for c in range(n))
    supports = [{c for c,a in enumerate(row) if a} for row in A]
    assert all(len(supports[i] & supports[j]) <= 1
               for i in range(n) for j in range(i))
    assert connected_levi(A)
    assert rank_q(A) == 14

    assert mv(A,Z0) == [1]*n
    assert mv(A,V) == [0]*n

    # rank=14 + nonzero kernel vector V => ker_Q(A)=span_Q(V).
    # Since Z0[2]=0 and V[2]=-1, any integer point Z0+lambda*V has
    # lambda=-z[2] integral. Thus all integer solutions are Z(k), k in Z.
    assert Z0[2] == 0 and V[2] == -1

    b,p,q,T = decomposition(A,Z0)
    assert sum(p) == 1
    assert sum(q) == 4
    assert len(T) == 9
    assert F(Z0) == 25

    # Exact piecewise objective law on representative integer k values.
    for k in range(-20,21):
        z = [Z0[i] + k*V[i] for i in range(n)]
        assert mv(A,z) == [1]*n
        explicit = 4*abs(-8*k-3) + 7*abs(4*k+1) + 3*abs(-2*k-1) + abs(10*k+3)
        assert F(z) == explicit
        if k >= 0:
            assert explicit == 76*k + 25
            assert z[6] >= 2
        else:
            assert explicit == -76*k - 25
            assert z[0] >= 3

    # Piecewise laws prove the exact global minimum over all k in Z.
    assert F(Z0) == 25
    assert 25 < (-76*(-1)-25)

    print("PASS: connected square linear-cubic rank-14 control")
    print("PASS: integer lattice -> NAE defect-flow identities")
    print("PASS: all integer solutions are Z0+kV, k in Z")
    print("PASS: exact F(k) piecewise law, global optimum=25 at k=0")
    print("PASS: every feasible integer point has positive overshoot p>0")
    print("OPEN: R5_E9_LINEAR_CUBIC_SOURCE_TRADE_AUGMENTATION_GATE_V1")
    print("P_VS_NP=OPEN; E8_D1=EMPTY")


if __name__ == "__main__":
    main()
