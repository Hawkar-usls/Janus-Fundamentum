#!/usr/bin/env python3
"""R5 E129: invertible-base cover theorem seed and gauge-clean q12 2-lift."""

from fractions import Fraction

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q,
    two_level_kernel_count,
)

P=[4,6,11,2,5,7,8,1,9,0,3,10]
Q=[7,9,1,6,2,3,0,10,11,5,8,4]
N=12

NEG={
    (1,9),
    (2,11),
    (2,1),
    (5,5),
    (7,10),
    (8,9),
    (8,11),
}


def base_matrix():
    A=[[0]*N for _ in range(N)]
    for i in range(N):
        for j in (i,P[i],Q[i]):
            A[i][j]=1
    return A


def det_bareiss(M):
    A=[list(map(int,row)) for row in M]
    n=len(A)
    sign=1
    prev=1
    for k in range(n-1):
        p=next((i for i in range(k,n) if A[i][k]),None)
        if p is None:
            return 0
        if p!=k:
            A[k],A[p]=A[p],A[k]
            sign=-sign
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                A[i][j]=(A[i][j]*pivot-A[i][k]*A[k][j])//prev
        for i in range(k+1,n):
            A[i][k]=0
        prev=pivot
    return sign*A[n-1][n-1]


def rank_mod2(M):
    rows=[]
    n=len(M)
    for row in M:
        x=0
        for j,v in enumerate(row):
            if v&1:
                x|=1<<j
        rows.append(x)
    r=0
    for c in range(n):
        p=next((i for i in range(r,n) if (rows[i]>>c)&1),None)
        if p is None:
            continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(n):
            if i!=r and ((rows[i]>>c)&1):
                rows[i]^=rows[r]
        r+=1
    return r


def verify_base(A):
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(N))==3 for j in range(N))
    for i in range(N):
        for j in range(i+1,N):
            assert sum(A[i][c]*A[j][c] for c in range(N))<=1

    # Levi connectivity.
    adj=[[] for _ in range(2*N)]
    for i,row in enumerate(A):
        for j,v in enumerate(row):
            if v:
                adj[i].append(N+j)
                adj[N+j].append(i)
    seen={0}; q=[0]
    while q:
        u=q.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    assert len(seen)==2*N


def signed_matrix(A):
    S=[row[:] for row in A]
    for i,j in NEG:
        assert S[i][j]==1
        S[i][j]=-1
    return S


def build_2lift(A):
    L=[[0]*(2*N) for _ in range(2*N)]
    for i,row in enumerate(A):
        for j,v in enumerate(row):
            if not v:
                continue
            cross=(i,j) in NEG
            for s in (0,1):
                t=1-s if cross else s
                L[2*i+s][2*j+t]=1
    return L


def connected_matrix(M):
    n=len(M)
    adj=[[] for _ in range(2*n)]
    for i,row in enumerate(M):
        for j,v in enumerate(row):
            if v:
                adj[i].append(n+j)
                adj[n+j].append(i)
    seen={0}; q=[0]
    while q:
        u=q.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen)==2*n


def row_subset_sat_table():
    # sat[S]=True iff some Boolean assignment satisfies every row in S.
    sat=[False]*(1<<N)
    rows=[(i,P[i],Q[i]) for i in range(N)]
    for x in range(1<<N):
        good=0
        for i,(a,b,c) in enumerate(rows):
            if ((x>>a)&1)+((x>>b)&1)+((x>>c)&1)==1:
                good|=1<<i
        sub=good
        while True:
            sat[sub]=True
            if sub==0:
                break
            sub=(sub-1)&good
    return sat


def gauge_clean_check():
    sat=row_subset_sat_table()
    max_parallel=0
    min_affected=N

    # Variable-fibre sheet relabelings. Row-fibre flips can then make a row
    # wholly parallel iff its three transformed edge signs are equal.
    for cm in range(1<<N):
        U=0
        parallel=0
        for i in range(N):
            vals=[]
            for j in (i,P[i],Q[i]):
                signbit=1 if (i,j) in NEG else 0
                vals.append(signbit ^ ((cm>>j)&1))
            if vals[0]==vals[1]==vals[2]:
                U|=1<<i
                parallel+=1

        assert sat[U], (cm,U)
        max_parallel=max(max_parallel,parallel)
        min_affected=min(min_affected,N-parallel)

    assert max_parallel==7
    assert min_affected==5
    return max_parallel,min_affected


def main():
    A=base_matrix()
    verify_base(A)

    det=det_bareiss(A)
    assert det==36
    assert rank_q(A)==12
    assert rank_mod2(A)==10

    S=signed_matrix(A)
    assert rank_q(S)==10

    L=build_2lift(A)
    verify_base(L)
    assert connected_matrix(L)
    assert rank_q(L)==22

    d,count=two_level_kernel_count(L)
    assert d==2
    assert count==0

    max_parallel,min_affected=gauge_clean_check()

    print("R5 E129 invertible-base cover seed: PASS")
    print("q12 det=36 rank_Q=12 rank_F2=10")
    print("signed rank_Q=10 => signed nullity=2")
    print("connected q24 2-lift rank_Q=22 nullity_Q=2 Exact-One UNSAT")
    print("all 4096 fibre gauges: parallel-row subset SAT")
    print("max parallel rows=",max_parallel,"min affected rows=",min_affected)
    print("general theorem: any r-sheet cover is UNSAT when 3 does not divide r")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
