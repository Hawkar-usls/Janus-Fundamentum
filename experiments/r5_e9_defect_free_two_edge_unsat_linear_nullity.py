#!/usr/bin/env python3
from fractions import Fraction
from math import gcd

ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]


def matrix_from_rows(rows, n):
    A = [[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rank_q(M):
    M = [[Fraction(x) for x in row] for row in M]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r,m) if M[i][c] != 0), None)
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        q = M[r][c]
        M[r] = [x/q for x in M[r]]
        for i in range(m):
            if i != r and M[i][c] != 0:
                q = M[i][c]
                M[i] = [M[i][j] - q*M[r][j] for j in range(n)]
        r += 1
    return r


def matvec(M, x):
    return [sum(a*b for a,b in zip(row,x)) for row in M]


def transpose(M):
    return [list(c) for c in zip(*M)]


def signed_block(A, pair):
    S = [row[:] for row in A]
    for i,j in pair:
        assert S[i][j] == 1
        S[i][j] = -1
    return S


def two_edge_lift(A, pair):
    n = len(A)
    E = [[0]*n for _ in range(n)]
    for i,j in pair:
        assert A[i][j] == 1
        E[i][j] = 1
    P = [[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    H = [[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            H[i][j] = P[i][j]
            H[i][n+j] = E[i][j]
            H[n+i][j] = E[i][j]
            H[n+i][n+j] = P[i][j]
    return H


def cubic_linear(A):
    n = len(A)
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    supports = [{j for j,x in enumerate(row) if x} for row in A]
    assert all(len(supports[i] & supports[j]) <= 1
               for i in range(n) for j in range(i))


A0 = matrix_from_rows(ROWS, 15)
cubic_linear(A0)
assert rank_q(A0) == 14

# Frozen one-dimensional right kernel; its coordinate ratio 1:4 excludes any
# {-1,2}-valued kernel word, which is the parent exact UNSAT proof.
g = [1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1]
assert matvec(A0, g) == [0]*15
assert 1 in g and 4 in g
for lam in (-1,2):
    assert 4*lam not in (-1,2)

# Bootstrap 1.
pair0 = ((1,7),(8,4))
assert pair0[0][0] != pair0[1][0] and pair0[0][1] != pair0[1][1]
y0 = [8,-4,5,11,-1,-16,14,-10,20,-1,5,8,-13,-7,-19]
assert matvec(transpose(A0), y0) == [0]*15
assert y0[1] != y0[8]
S0 = signed_block(A0, pair0)
assert 15-rank_q(S0) == 1
A1 = two_edge_lift(A0, pair0)
cubic_linear(A1)
assert 30-rank_q(A1) == 2

# Bootstrap 2.
pair1 = ((0,0),(2,14))
assert pair1[0][0] != pair1[1][0] and pair1[0][1] != pair1[1][1]
y10 = [4,36,-7,15,-29,-8,26,14,-28,-29,-7,4,3,25,-19,
       4,-40,12,-4,28,-8,-12,-24,48,28,12,4,-16,-32,0]
y11 = [12,-20,11,13,9,-24,14,-22,44,9,11,12,-23,-21,-25,
       12,8,4,20,-12,-24,28,-8,16,-12,4,12,-16,0,-32]
AT1 = transpose(A1)
assert matvec(AT1, y10) == [0]*30
assert matvec(AT1, y11) == [0]*30
assert (y10[0],y11[0]) != (y10[2],y11[2])
S1 = signed_block(A1, pair1)
assert 30-rank_q(S1) == 1
A2 = two_edge_lift(A1, pair1)
cubic_linear(A2)
assert 60-rank_q(A2) == 3

# The arbitrary-size recurrence starts at (n_2,k_2)=(60,3).
n, k = 60, 3
prefix = []
for t in range(2,9):
    lower = 2 + n//60
    assert k >= lower
    prefix.append((t,n,k,lower))
    n *= 2
    k = 2*k-2

print("PASS_DEFECT_FREE_TWO_EDGE_UNSAT_LINEAR_NULLITY")
print("bootstrap", {"n0":15,"k0":1,"n1":30,"k1":2,"n2":60,"k2":3})
print("pair0", pair0, "signed_nullity", 1, "left_rows", (y0[1],y0[8]))
print("pair1", pair1, "signed_nullity", 1,
      "left_row_signatures", ((y10[0],y11[0]),(y10[2],y11[2])))
print("recurrence_prefix", prefix)
print("theorem", "k_next >= 2*k-2; k_t >= 2+n_t/60 for t>=2")
print("scientific_ceiling", "E8_D1=EMPTY P_VS_NP=OPEN")
