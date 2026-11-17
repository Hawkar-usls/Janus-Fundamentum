#!/usr/bin/env python3
"""R5 E120: q15 full rational row-projection counterexample."""

from fractions import Fraction
from itertools import product
from math import gcd


P = [12,13,9,8,5,2,11,1,0,10,7,4,14,3,6]
Q = [3,4,14,10,7,13,5,0,2,12,6,9,8,11,1]
N = 15


def build_A():
    A=[[0]*N for _ in range(N)]
    for i in range(N):
        cols=(i,P[i],Q[i])
        assert len(set(cols))==3
        for j in cols:
            A[i][j]=1
    return A


def rank_q(M):
    A=[[Fraction(x) for x in row] for row in M]
    m=len(A)
    n=len(A[0]) if m else 0
    r=0
    piv=[]
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]),None)
        if p is None:
            continue
        A[r],A[p]=A[p],A[r]
        z=A[r][c]
        A[r]=[x/z for x in A[r]]
        for i in range(m):
            if i!=r and A[i][c]:
                f=A[i][c]
                A[i]=[A[i][j]-f*A[r][j] for j in range(n)]
        piv.append(c)
        r+=1
        if r==m:
            break
    return r,piv,A


def kernel_basis_q(M):
    rank,piv,R=rank_q(M)
    n=len(M[0])
    free=[c for c in range(n) if c not in piv]
    cols=[]
    for f in free:
        x=[Fraction(0) for _ in range(n)]
        x[f]=Fraction(1)
        for i,c in enumerate(piv):
            x[c]=-R[i][f]
        cols.append(x)
    B=[[cols[j][i] for j in range(len(cols))] for i in range(n)]
    return rank,B


def in_colspan(R,t):
    if not R or not R[0]:
        return False
    rank1=rank_q(R)[0]
    aug=[list(row)+[Fraction(t[i])] for i,row in enumerate(R)]
    rank2=rank_q(aug)[0]
    return rank1==rank2


def exact_count(A):
    count=0
    for bits in product((0,1),repeat=N):
        if all(sum(A[i][j]*bits[j] for j in range(N))==1 for i in range(N)):
            count+=1
    return count


def gf2_kernel_words(A):
    rows=[]
    for row in A:
        mask=0
        for j,v in enumerate(row):
            if v:
                mask |= 1<<j
        rows.append(mask)

    piv=[]
    r=0
    for c in range(N):
        p=next((i for i in range(r,N) if (rows[i]>>c)&1),None)
        if p is None:
            continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(N):
            if i!=r and ((rows[i]>>c)&1):
                rows[i]^=rows[r]
        piv.append(c)
        r+=1

    free=[c for c in range(N) if c not in piv]
    basis=[]
    for f in free:
        x=1<<f
        for i in range(r-1,-1,-1):
            c=piv[i]
            if (rows[i]&x).bit_count()&1:
                x |= 1<<c
        basis.append(x)

    words=[]
    for mask in range(1<<len(basis)):
        x=0
        for i,b in enumerate(basis):
            if (mask>>i)&1:
                x ^= b
        words.append(x)
    return basis,words


def inverse_perm(p):
    q=[0]*len(p)
    for i,v in enumerate(p):
        q[v]=i
    return q


def compose(a,b):
    return [a[b[i]] for i in range(len(a))]


def commutator_support(p,q):
    pinv=inverse_perm(p)
    qinv=inverse_perm(q)
    k=compose(compose(compose(p,q),pinv),qinv)
    return sum(k[i]!=i for i in range(len(k)))


def connected_tanner(A):
    adj=[set() for _ in range(2*N)]
    for i in range(N):
        for j in range(N):
            if A[i][j]:
                adj[i].add(N+j)
                adj[N+j].add(i)
    seen={0}
    stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen)==2*N


def main():
    A=build_A()
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(N))==3 for j in range(N))
    for a in range(N):
        for b in range(a+1,N):
            assert sum(A[i][a]*A[i][b] for i in range(N)) <= 1
    assert connected_tanner(A)
    assert N%3==0

    rank,B=kernel_basis_q(A)
    assert rank==13
    assert len(B[0])==2

    corners=((2,-1,-1),(-1,2,-1),(-1,-1,2))
    for c in range(N):
        inc=[j for j in range(N) if A[c][j]]
        R=[[B[j][k] for k in range(2)] for j in inc]
        assert rank_q(R)[0]==2
        assert all(in_colspan(R,t) for t in corners)

    assert exact_count(A)==0

    basis2,words=gf2_kernel_words(A)
    assert len(basis2)==2
    weights=sorted(x.bit_count() for x in words)
    assert weights==[0,4,8,8]
    assert max(weights)==8
    assert 2*N//3==10

    assert commutator_support(P,Q)==14

    print("R5 E120 full rational row-projection counterexample: PASS")
    print("n=15 connected square/cubic/linear; 3|n")
    print("rank_Q=13 nullity_Q=2")
    print("all 15 source-row projections have rank 2")
    print("all 15 rational three-port tables = 111")
    print("Exact-One solutions=0")
    print("GF2 kernel weights=[0,4,8,8], cap=10")
    print("commutator support=14")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
