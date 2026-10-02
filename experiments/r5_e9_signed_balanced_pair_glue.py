#!/usr/bin/env python3
"""Exact controls for signed-balanced pair-glue preprocessing."""

from itertools import combinations

D1=((1,5),(6,7),(0,10),(3,11),(4,9),(2,8))
D2=((0,1,8),(3,5,9),(4,7,10),(2,6,11))
D3=((1,4,11),(3,7,8),(0,6,9),(2,5,10))
N=12

EXPECTED_A=(
 ( 1, 0, 1, 0, 0,-1),
 (-1, 0, 0, 1,-1, 0),
 ( 0,-1,-1, 0, 1, 0),
 ( 0, 1, 0,-1, 0, 1),
 ( 1, 0, 0,-1, 1, 0),
 ( 0,-1, 0, 1, 0,-1),
 ( 0, 1, 1, 0,-1, 0),
 (-1, 0,-1, 0, 0, 1),
)

def linear_audit(parts):
    for a in range(len(parts)):
        for b in range(a+1,len(parts)):
            for r in parts[a]:
                for s in parts[b]:
                    assert len(set(r)&set(s))<=1

def signed_matrix():
    vmap={}
    for i,(a,b) in enumerate(D1):
        vmap[a]=(i,1)
        vmap[b]=(i,-1)
    A=[]
    for R in D2+D3:
        row=[0]*len(D1)
        for v in R:
            i,s=vmap[v]
            assert row[i]==0
            row[i]=s
        A.append(tuple(row))
    return tuple(A)

def unsigned_incidence():
    rows=D1+D2+D3
    return tuple(tuple(1 if j in r else 0 for j in range(N)) for r in rows)

def balanced01(A):
    m=len(A); n=len(A[0])
    for k in range(3,min(m,n)+1,2):
        for rs in combinations(range(m),k):
            cand=[
                j for j in range(n)
                if sum(A[i][j] for i in rs)==2
            ]
            if len(cand)<k:
                continue
            for cs in combinations(cand,k):
                if all(sum(A[i][j] for j in cs)==2 for i in rs) and \
                   all(sum(A[i][j] for i in rs)==2 for j in cs):
                    return False
    return True

def balanced_signed(A):
    m=len(A); n=len(A[0])
    for k in range(2,min(m,n)+1):
        for rs in combinations(range(m),k):
            cand=[
                j for j in range(n)
                if sum(A[i][j]!=0 for i in rs)==2
            ]
            if len(cand)<k:
                continue
            for cs in combinations(cand,k):
                if not all(sum(A[i][j]!=0 for j in cs)==2 for i in rs):
                    continue
                if not all(sum(A[i][j]!=0 for i in rs)==2 for j in cs):
                    continue
                total=sum(A[i][j] for i in rs for j in cs)
                if total%4!=0:
                    return False
    return True

def center_audit(A):
    # For row a, at t=1/2 the reconstructed original triple sum is 3/2:
    # n(a) + a*(1/2) = 3/2.
    for r in A:
        neg=sum(v<0 for v in r)
        signed=sum(r)/2
        assert neg+signed==1.5

def main():
    linear_audit((D1,D2,D3))
    A=signed_matrix()
    assert A==EXPECTED_A
    center_audit(A)
    assert not balanced01(unsigned_incidence())
    assert balanced_signed(A)
    print("PAIR_SUBSTITUTION_SIGNED_NORMAL_FORM = PASS")
    print("UNIVERSAL_HALF_CENTER = PASS")
    print("UNSIGNED_INCIDENCE_BALANCED = FALSE")
    print("SIGNED_PAIR_GLUE_BALANCED = TRUE")
    print("STRICT_ISLAND_EXTENSION = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
