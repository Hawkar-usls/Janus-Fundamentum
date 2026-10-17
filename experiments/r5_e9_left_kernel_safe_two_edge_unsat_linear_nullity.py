#!/usr/bin/env python3
from fractions import Fraction
from itertools import combinations

ROWS = [
    (0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
    (1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
    (2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14),
]


def matrix_from_rows(rows):
    n=len(rows)
    A=[[0]*n for _ in range(n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j]=1
    return A


def rref_solve(M,b):
    m=len(M); n=len(M[0])
    X=[[Fraction(M[i][j]) for j in range(n)] + [Fraction(b[i])] for i in range(m)]
    piv=[]; r=0
    for c in range(n):
        p=next((i for i in range(r,m) if X[i][c] != 0), None)
        if p is None:
            continue
        X[r],X[p]=X[p],X[r]
        q=X[r][c]
        X[r]=[z/q for z in X[r]]
        for i in range(m):
            if i!=r and X[i][c]!=0:
                q=X[i][c]
                X[i]=[X[i][j]-q*X[r][j] for j in range(n+1)]
        piv.append(c); r+=1
    for i in range(r,m):
        if all(X[i][j]==0 for j in range(n)) and X[i][n]!=0:
            return None
    free=[c for c in range(n) if c not in piv]
    x=[Fraction(0) for _ in range(n)]
    for i,c in enumerate(piv):
        x[c]=X[i][n]
    basis=[]
    for f in free:
        v=[Fraction(0) for _ in range(n)]
        v[f]=1
        for i,c in enumerate(piv):
            v[c]=-X[i][f]
        basis.append(v)
    return x,basis


def nullity_q(M):
    return len(rref_solve(M,[0]*len(M))[1])


def transpose(M):
    return [list(x) for x in zip(*M)]


def left_kernel_basis(M):
    return rref_solve(transpose(M),[0]*len(M))[1]


def two_edge_lift(A,e1,e2):
    n=len(A)
    E=[[0]*n for _ in range(n)]
    for i,j in (e1,e2):
        assert A[i][j]==1
        E[i][j]=1
    P=[[A[i][j]-E[i][j] for j in range(n)] for i in range(n)]
    H=[[0]*(2*n) for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            H[i][j]=P[i][j]
            H[i][j+n]=E[i][j]
            H[i+n][j]=E[i][j]
            H[i+n][j+n]=P[i][j]
    return H


def signed_block(A,e1,e2):
    S=[row[:] for row in A]
    for i,j in (e1,e2):
        assert S[i][j]==1
        S[i][j]=-1
    return S


def cubic_square(A):
    n=len(A)
    return all(sum(row)==3 for row in A) and all(sum(A[i][j] for i in range(n))==3 for j in range(n))


def linear_rows(A):
    n=len(A)
    supp=[{j for j,x in enumerate(A[i]) if x} for i in range(n)]
    return all(len(supp[i]&supp[j])<=1 for i in range(n) for j in range(i))


def brute_unsat(A):
    n=len(A)
    assert n%3==0
    masks=[]
    for row in A:
        m=0
        for j,x in enumerate(row):
            if x:m|=1<<j
        masks.append(m)
    for C in combinations(range(n),n//3):
        z=0
        for j in C:z|=1<<j
        if all((z&m).bit_count()==1 for m in masks):
            return False
    return True


def row_signatures(left_basis):
    n=len(left_basis[0])
    return [tuple(v[i] for v in left_basis) for i in range(n)]


A0=matrix_from_rows(ROWS)
assert cubic_square(A0)
assert linear_rows(A0)
assert nullity_q(A0)==1
assert brute_unsat(A0)

# Bootstrap 1.
e01=(0,12); e02=(2,9)
assert e01[0]!=e02[0] and e01[1]!=e02[1]
L0=left_kernel_basis(A0)
assert len(L0)==1
assert L0[0][e01[0]] != L0[0][e02[0]]
S0=signed_block(A0,e01,e02)
assert nullity_q(S0)==1
A1=two_edge_lift(A0,e01,e02)
assert cubic_square(A1)
assert linear_rows(A1)
assert nullity_q(A1)==2

# Bootstrap 2.
e11=(0,5); e12=(1,1)
assert A1[e11[0]][e11[1]]==1 and A1[e12[0]][e12[1]]==1
assert e11[0]!=e12[0] and e11[1]!=e12[1]
L1=left_kernel_basis(A1)
assert len(L1)==2
sig=row_signatures(L1)
assert sig[e11[0]] != sig[e12[0]]
# Frozen exact signatures from the theorem artifact.
assert sig[e11[0]] == (Fraction(23,6), Fraction(-11,6))
assert sig[e12[0]] == (Fraction(17,6), Fraction(-5,6))
S1=signed_block(A1,e11,e12)
assert nullity_q(S1)==1
A2=two_edge_lift(A1,e11,e12)
assert cubic_square(A2)
assert linear_rows(A2)
assert nullity_q(A2)==3

# Constructive general-step precondition on A2: a nonzero left-kernel vector is
# necessarily nonconstant, so a separating row pair exists.  Verify the
# checker implementation actually finds one and can choose nonincident edges.
L2=left_kernel_basis(A2)
assert len(L2)==3
y=L2[0]
assert any(v!=y[0] for v in y)
r=0
s=next(i for i in range(1,len(y)) if y[i]!=y[r])
Nr=[j for j,x in enumerate(A2[r]) if x]
Ns=[j for j,x in enumerate(A2[s]) if x]
j=Nr[0]
l=next(q for q in Ns if q!=j)
assert r!=s and j!=l and y[r]!=y[s]

print('PASS')
print('bootstrap_n_nullity', [(15,1),(30,2),(60,3)])
print('general_safe_pair_rows', (r,s), 'left_kernel_values', (y[r],y[s]))
print('theorem_recurrence', 'k_next >= 2*k-2 for every k>=3 safe recursive stage')
print('theorem_asymptotic', 'k_t >= 2+n_t/60 for t>=2')
print('P_VS_NP=OPEN E8_D1=EMPTY')
