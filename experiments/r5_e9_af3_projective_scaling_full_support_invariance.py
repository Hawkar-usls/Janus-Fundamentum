#!/usr/bin/env python3
"""Exact F3 regression for AF3 projective row/column invariance."""
from itertools import product

SAT_ROWS=[
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
(3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
(6,9,15),(7,8,15),(7,11,12)]

def source():
    return [[int(j+1 in row) for j in range(15)] for row in SAT_ROWS]

def mv(M,x): return [sum(a*b for a,b in zip(row,x))%3 for row in M]

def mm(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(len(B)))%3
             for j in range(len(B[0]))] for i in range(len(A))]

def kernel_words(M):
    n=len(M[0])
    return [x for x in product(range(3),repeat=n) if mv(M,x)==[0]*len(M)]

def main():
    A=source()
    M=[row+[2] for row in A] # -1 = 2 mod 3

    # Explicit invertible row operation: add row i+1 to row i cyclically via
    # a unit lower-bidiagonal matrix chosen to be triangular/invertible.
    m=len(M)
    U=[[int(i==j) for j in range(m)] for i in range(m)]
    for i in range(1,m): U[i][i-1]=1

    # Nonzero projective column scaling.
    diag=[1 if j%2==0 else 2 for j in range(len(M[0]))]
    MD=[[M[i][j]*diag[j]%3 for j in range(len(M[0]))] for i in range(m)]
    N=mm(U,MD)

    full_M=[c for c in kernel_words(M) if all(c)]
    full_N=[z for z in kernel_words(N) if all(z)]
    assert len(full_M)==8
    assert len(full_N)==8

    mapped=set()
    for z in full_N:
        c=tuple(diag[j]*z[j]%3 for j in range(len(z)))
        assert all(c)
        assert mv(M,c)==[0]*m
        mapped.add(c)
    assert mapped==set(full_M)

    # Every normalized codeword reconstructs one of the four Exact-One models.
    witnesses=set()
    for c in full_M:
        t=c[-1]
        inv=pow(t,-1,3)
        r=[inv*v%3 for v in c[:-1]]
        x=tuple(int(v==2) for v in r)
        assert all(sum(row[j]*x[j] for j in range(15))==1 for row in A)
        witnesses.add(x)
    assert len(witnesses)==4

    print({'status':'PASS_AF3_PROJECTIVE_SCALING_INVARIANCE','full_support_words':8,'witnesses':4})
    print('E8_D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
