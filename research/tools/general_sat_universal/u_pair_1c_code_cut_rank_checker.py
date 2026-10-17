#!/usr/bin/env python3
# Regression checker for Lemma 1: code cut indicator rank = 2^sigma.
import itertools
import numpy as np

def gf2_rank(A):
    A=np.array(A,dtype=np.uint8).copy(); m,n=A.shape; r=0
    for c in range(n):
        p=next((i for i in range(r,m) if A[i,c]),None)
        if p is None: continue
        A[[r,p]]=A[[p,r]]
        for i in range(m):
            if i!=r and A[i,c]: A[i]^=A[r]
        r+=1
    return r

def span(G):
    k,n=G.shape; out=[]
    for bits in itertools.product([0,1],repeat=k):
        v=np.zeros(n,dtype=np.uint8)
        for i,b in enumerate(bits):
            if b: v^=G[i]
        out.append(tuple(int(x) for x in v))
    return out

def log2_card(xs):
    n=len(set(xs)); assert n and n&(n-1)==0
    return n.bit_length()-1

rng=np.random.default_rng(20260917)
count=0
for n in range(4,9):
    k=max(1,n//2)
    for _ in range(12):
        while True:
            G=rng.integers(0,2,size=(k,n),dtype=np.uint8)
            if gf2_rank(G)==k: break
        C=span(G); A=list(range(n//2)); B=list(range(n//2,n))
        CA=[w for w in C if all(w[j]==0 for j in B)]
        CB=[w for w in C if all(w[j]==0 for j in A)]
        sigma=log2_card(C)-log2_card(tuple(w[j] for j in A) for w in CA)-log2_card(tuple(w[j] for j in B) for w in CB)
        As=sorted(set(tuple(w[j] for j in A) for w in C))
        Bs=sorted(set(tuple(w[j] for j in B) for w in C))
        ai={a:i for i,a in enumerate(As)}; bi={b:i for i,b in enumerate(Bs)}
        M=np.zeros((len(As),len(Bs)))
        for w in C:
            M[ai[tuple(w[j] for j in A)],bi[tuple(w[j] for j in B)]]=1
        assert int(np.linalg.matrix_rank(M))==2**sigma
        count+=1
print(f"PASS: {count} random linear-code cuts satisfy rank(M)=2^sigma")
print("CLAIM CEILING: regression only; U-PAIR-1D remains OPEN; P vs NP remains OPEN.")
