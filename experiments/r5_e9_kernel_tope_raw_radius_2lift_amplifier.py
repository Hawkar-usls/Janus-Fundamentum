#!/usr/bin/env python3
"""Exact finite replay for the kernel-tope raw-radius 2-lift amplifier.

The arbitrary-size existence theorem is in the companion research note.
This checker validates PG15, two explicit nonsingular signings, connected
2-lifts through n=60, fixed rational nullity 4, and duplicated kernel/trap
geometry.  No numerical linear algebra is used.
"""

from fractions import Fraction
from itertools import combinations
from collections import deque

ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

B0 = [
    [-1,-1, 0, 0],[-1, 0,-1, 0],[ 2, 1, 1, 0],[-1,-1,-1, 1],
    [-1,-1, 0, 0],[-1, 0,-1, 0],[-1, 0, 0,-1],[ 1, 0, 0, 0],
    [ 1, 0, 1,-1],[ 1, 1, 0,-1],[ 0, 0, 0, 1],[ 1, 0, 0, 0],
    [ 0, 1, 0, 0],[ 0, 0, 1, 0],[ 0, 0, 0, 1],
]

TRAP = "--+---+-++--++-"
TRAP_POS = {i for i,c in enumerate(TRAP) if c == '+'}

# Explicit full-rank signing on A0, 0-based (row,column).
F0 = ((0,0),(1,9),(5,2),(7,3))
# Explicit full-rank signing on the resulting A1.
F1 = ((23,24),(15,0),(27,23),(5,6))


def incidence_matrix():
    return [[int(j + 1 in row) for j in range(15)] for row in ROWS]


def rank_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r],A[p] = A[p],A[r]
        pv = A[r][c]
        A[r] = [z/pv for z in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [A[i][j] - f*A[r][j] for j in range(n)]
        r += 1
        if r == m:
            break
    return r


def det_bareiss(M):
    A = [list(map(int,row)) for row in M]
    n = len(A)
    assert all(len(row) == n for row in A)
    if n == 0:
        return 1
    sign = 1
    prev = 1
    for k in range(n-1):
        p = next((i for i in range(k,n) if A[i][k] != 0), None)
        if p is None:
            return 0
        if p != k:
            A[k],A[p] = A[p],A[k]
            sign *= -1
        pivot = A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num = A[i][j]*pivot - A[i][k]*A[k][j]
                assert num % prev == 0
                A[i][j] = num // prev
        for i in range(k+1,n):
            A[i][k] = 0
        prev = pivot
    return sign*A[n-1][n-1]


def matmul(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def signed(A,neg):
    S = [row[:] for row in A]
    for i,j in neg:
        assert S[i][j] == 1
        S[i][j] = -1
    return S


def lift(A,neg):
    n = len(A)
    neg = set(neg)
    H = [[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            if not A[i][j]:
                continue
            if (i,j) in neg:
                H[i][j+n] = 1
                H[i+n][j] = 1
            else:
                H[i][j] = 1
                H[i+n][j+n] = 1
    return H


def connected_support(A):
    n = len(A)
    adj = [[] for _ in range(2*n)]
    for i,row in enumerate(A):
        for j,a in enumerate(row):
            if a:
                adj[i].append(n+j)
                adj[n+j].append(i)
    seen = {0}
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == 2*n


def repeat_rows(B,copies):
    return [row[:] for _ in range(copies) for row in B]


def exact_one_witnesses(A):
    n = len(A)
    assert n == 15
    out = []
    for C in combinations(range(n),n//3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            out.append(S)
    return out


def hamming(a,b):
    return sum(x != y for x,y in zip(a,b))


def boundary_from_support(S,n=15):
    return ''.join('+' if i in S else '-' for i in range(n))


def assert_cubic(A):
    n = len(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))


def main():
    A0 = incidence_matrix()
    assert_cubic(A0)
    assert connected_support(A0)
    assert rank_q(A0) == 11
    assert rank_q(B0) == 4
    assert matmul(A0,B0) == [[0]*4 for _ in range(15)]

    witnesses = exact_one_witnesses(A0)
    assert len(witnesses) == 4
    base_boundaries = [boundary_from_support(S) for S in witnesses]
    base_distances = [hamming(TRAP,w) for w in base_boundaries]
    assert base_distances == [5,5,5,5]
    assert TRAP.count('+') == 6
    assert all(w.count('+') == 5 for w in base_boundaries)

    S0 = signed(A0,F0)
    assert det_bareiss(S0) == -32
    assert rank_q(S0) == 15

    A1 = lift(A0,F0)
    assert_cubic(A1)
    assert connected_support(A1)
    assert rank_q(A1) == 26
    assert len(A1)-rank_q(A1) == 4

    B1 = repeat_rows(B0,2)
    assert rank_q(B1) == 4
    assert matmul(A1,B1) == [[0]*4 for _ in range(30)]
    # Since nullity(A1)=4, these four duplicated columns span the full kernel.

    trap1 = TRAP*2
    boundaries1 = [w*2 for w in base_boundaries]
    assert trap1.count('+') == 12
    assert all(w.count('+') == 10 for w in boundaries1)
    assert [hamming(trap1,w) for w in boundaries1] == [10]*4

    S1 = signed(A1,F1)
    assert det_bareiss(S1) == 64
    assert rank_q(S1) == 30

    A2 = lift(A1,F1)
    assert_cubic(A2)
    assert connected_support(A2)
    r2 = rank_q(A2)
    assert r2 == 56
    assert len(A2)-r2 == 4

    B2 = repeat_rows(B0,4)
    assert rank_q(B2) == 4
    assert matmul(A2,B2) == [[0]*4 for _ in range(60)]

    trap2 = TRAP*4
    boundaries2 = [w*4 for w in base_boundaries]
    assert trap2.count('+') == 24
    assert all(w.count('+') == 20 for w in boundaries2)
    assert [hamming(trap2,w) for w in boundaries2] == [20]*4

    # Multiplicity does not create new projective hyperplanes, so the geometric
    # arrangement is still the base PG15 arrangement.  Parent exact result: 4.

    print({
        'status': 'PASS_RAW_RADIUS_2LIFT_AMPLIFIER_CONTROLS',
        'base': {
            'n': 15,
            'rank_q': 11,
            'nullity_q': 4,
            'trap_p': 6,
            'boundary_p': 5,
            'min_raw_distance': 5,
            'geometric_distance_parent': 4,
        },
        'level1': {
            'n': 30,
            'signing_det': -32,
            'rank_q': 26,
            'nullity_q': 4,
            'connected': True,
            'trap_p': 12,
            'boundary_p': 10,
            'raw_distance': 10,
        },
        'level2': {
            'n': 60,
            'signing_det': 64,
            'rank_q': 56,
            'nullity_q': 4,
            'connected': True,
            'trap_p': 24,
            'boundary_p': 20,
            'raw_distance': 20,
        },
        'arbitrary_size_theorem': 'raw distance = 5*2^t = n_t/3',
        'fixed_or_sublinear_raw_radius': 'FALSIFIED',
        'bounded_geometric_radius': 'OPEN',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
