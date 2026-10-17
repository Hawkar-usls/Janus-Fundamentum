#!/usr/bin/env python3
"""Exact F3 regression for AF3 projective row/column invariance."""
from itertools import product

SAT_ROWS=[
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
(3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
(6,9,15),(7,8,15),(7,11,12)]

def source(): return [[int(j+1 in row) for j in range(15)] for row in SAT_ROWS]
def mv(M,x): return [sum(a*b for a,b in zip(row,x))%3 for row in M]
def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(len(B)))%3 for j in range(len(B[0]))] for i in range(len(A))]

def kernel_basis(M):
    A=[[v%3 for v in row] for row in M]
    m,n=len(A),len(A[0]); r=0; piv=[]
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        inv=pow(A[r][c],-1,3); A[r]=[(v*inv)%3 for v in A[r]]
        for i in range(m):
            if i!=r and A[i][c]:
                f=A[i][c]; A[i]=[(A[i][j]-f*A[r][j])%3 for j in range(n)]
        piv.append(c); r+=1
        if r==m: break
    free=[j for j in range(n) if j not in piv]
    B=[]
    for f in free:
        x=[0]*n; x[f]=1
        for i,c in enumerate(piv): x[c]=(-A[i][f])%3
        B.append(x)
    return B

def kernel_words(M):
    B=kernel_basis(M); n=len(M[0]); out=[]
    for coeff in product(range(3),repeat=len(B)):
        x=[0]*n
        for a,v in zip(coeff,B):
            for j in range(n): x[j]=(x[j]+a*v[j])%3
        out.append(tuple(x))
    return out

def main():
    A=source(); M=[row+[2] for row in A]
    m=len(M)
    U=[[int(i==j) for j in range(m)] for i in range(m)]
    for i in range(1,m): U[i][i-1]=1
    diag=[1 if j%2==0 else 2 for j in range(len(M[0]))]
    MD=[[M[i][j]*diag[j]%3 for j in range(len(M[0]))] for i in range(m)]
    N=mm(U,MD)

    words_M=kernel_words(M); words_N=kernel_words(N)
    assert len(words_M)==243 and len(words_N)==243
    full_M=[c for c in words_M if all(c)]
    full_N=[z for z in words_N if all(z)]
    assert len(full_M)==8 and len(full_N)==8

    mapped=set()
    for z in full_N:
        c=tuple(diag[j]*z[j]%3 for j in range(len(z)))
        assert mv(M,c)==[0]*m
        mapped.add(c)
    assert mapped==set(full_M)

    witnesses=set()
    for c in full_M:
        inv=pow(c[-1],-1,3); r=[inv*v%3 for v in c[:-1]]
        x=tuple(int(v==2) for v in r)
        assert all(sum(row[j]*x[j] for j in range(15))==1 for row in A)
        witnesses.add(x)
    assert len(witnesses)==4

    print({'status':'PASS_AF3_PROJECTIVE_SCALING_INVARIANCE','kernel_words':243,'full_support_words':8,'witnesses':4})
    print('E8_D1 = EMPTY')
    print('P_VS_NP = OPEN')

if __name__=='__main__': main()
