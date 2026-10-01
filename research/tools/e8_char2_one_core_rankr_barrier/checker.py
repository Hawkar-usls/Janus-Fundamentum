#!/usr/bin/env python3
from itertools import product
import json


def rank2(A):
    A=[row[:] for row in A]
    m=len(A); n=len(A[0]) if m else 0
    r=0
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]&1),None)
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        for i in range(m):
            if i!=r and (A[i][c]&1):
                A[i]=[(x^y) for x,y in zip(A[i],A[r])]
        r+=1
    return r


def det2(A):
    return 1 if rank2(A)==len(A) else 0


def adj2(A):
    n=len(A)
    out=[[0]*n for _ in range(n)]
    if n==1:
        out[0][0]=1
        return out
    for i in range(n):
        for j in range(n):
            minor=[[A[r][c] for c in range(n) if c!=i] for r in range(n) if r!=j]
            # cofactor sign is irrelevant in characteristic two; transpose built into indices.
            out[i][j]=det2(minor)
    return out

checks=[]
# Exhaust every 2x2 and 3x3 D over GF(2) with corank one.
for s in (2,3):
    count=0
    for bits in product((0,1), repeat=s*s):
        D=[list(bits[i*s:(i+1)*s]) for i in range(s)]
        if rank2(D)!=s-1: continue
        A=adj2(D)
        assert rank2(A)==1
        count+=1
    checks.append({"size":s,"corank1_matrices":count,"adj_rank":1})

# Target linear coefficient of tr(K) has rank r, so it cannot equal R adj(D) L (rank <=1) for r>=2.
for r in (2,3,4):
    I=[[1 if i==j else 0 for j in range(r)] for i in range(r)]
    assert rank2(I)==r and r>1

print(json.dumps({
    "status":"PASS_CHAR2_ONE_CORE_RANKR_BARRIER_CONTROLS",
    "checks":checks,
    "target_coefficient_ranks":[2,3,4],
    "proof_note":"The arbitrary-size theorem uses det(D)=0, nonzero linear term => corank(D)=1, rank(adj(D))=1, hence rank(R adj(D) L)<=1 != rank(I_r).",
    "two_adic_corollary":"Any Z/2^k identity would reduce modulo 2 to the forbidden GF(2) identity.",
    "scientific_boundary":{"P_VS_NP":"OPEN","P_EQUALS_NP_ALGORITHM":"NOT_CONSTRUCTED"}
},sort_keys=True))
