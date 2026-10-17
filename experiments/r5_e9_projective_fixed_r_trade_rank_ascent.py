#!/usr/bin/env python3
"""Finite controls for the fixed-r projective trade rank-ascent router."""
from fractions import Fraction
from itertools import combinations, product
from collections import defaultdict

UNSAT=[
(1,10,11),(1,12,13),(1,14,15),(2,4,6),(2,5,7),(2,12,14),
(3,4,7),(3,8,11),(3,9,10),(4,11,15),(5,8,13),(5,9,12),
(6,8,14),(6,9,15),(7,10,13)]
SAT=[
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
(3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
(6,9,15),(7,8,15),(7,11,12)]


def matrix(E,n=15):
    return [[int(j+1 in L) for j in range(n)] for L in sorted(E)]


def gf2_rref(M):
    A=[r[:] for r in M]; piv=[]; rr=0
    for c in range(len(A[0])):
        p=next((i for i in range(rr,len(A)) if A[i][c]),None)
        if p is None: continue
        A[rr],A[p]=A[p],A[rr]
        for i in range(len(A)):
            if i!=rr and A[i][c]: A[i]=[x^y for x,y in zip(A[i],A[rr])]
        piv.append(c); rr+=1
    return A,piv


def gf2_rank(E): return len(gf2_rref(matrix(E))[1])


def q_rank(E):
    A=[[Fraction(x) for x in r] for r in matrix(E)]; rr=0
    for c in range(len(A[0])):
        p=next((i for i in range(rr,len(A)) if A[i][c]),None)
        if p is None: continue
        A[rr],A[p]=A[p],A[rr]
        f=A[rr][c]; A[rr]=[x/f for x in A[rr]]
        for i in range(len(A)):
            if i!=rr and A[i][c]:
                f=A[i][c]; A[i]=[x-f*y for x,y in zip(A[i],A[rr])]
        rr+=1
    return rr


def signatures(E):
    R,piv=gf2_rref(matrix(E)); n=15; free=[j for j in range(n) if j not in piv]
    B=[]
    for f in free:
        x=[0]*n; x[f]=1
        for i,p in enumerate(piv): x[p]=R[i][f]
        B.append(x)
    sig=[]
    for j in range(n):
        s=0
        for i,b in enumerate(B): s|=b[j]<<i
        sig.append(s)
    return sig


def projective_lines(sig):
    return [tuple(i+1 for i in C) for C in combinations(range(len(sig)),3)
            if sig[C[0]]^sig[C[1]]^sig[C[2]]==0]


def deg(E):
    d=[0]*15
    for L in E:
        for v in L:d[v-1]+=1
    return tuple(d)


def rank_safe_3trades(E, L):
    E=set(E); outside=sorted(set(L)-E); oldr=gf2_rank(E)
    bydeg=defaultdict(list)
    for rem in combinations(sorted(E),3): bydeg[deg(rem)].append(rem)
    out=[]
    for add in combinations(outside,3):
        for rem in bydeg.get(deg(add),[]):
            N=(E-set(rem))|set(add)
            if gf2_rank(N)==oldr: out.append((rem,add,N))
    return out


def all_cubic_decompositions(L):
    # Controls have 15 selected lines; SAT has only 19 total candidate lines.
    return [set(C) for C in combinations(L,15) if deg(C)==(3,)*15]


def main():
    U=set(UNSAT); sigU=signatures(U); LU=projective_lines(sigU)
    trades=rank_safe_3trades(U,LU)
    census=defaultdict(int)
    for _,_,N in trades:census[q_rank(N)]+=1
    assert len(LU)==35
    assert len(trades)==31
    assert dict(census)=={13:25,15:6}
    assert q_rank(U)==13 and gf2_rank(U)==11
    assert any(q_rank(N)==15 for _,_,N in trades)

    S=set(SAT); sigS=signatures(S); LS=projective_lines(sigS)
    assert len(LS)==19
    decomps=all_cubic_decompositions(LS)
    assert len(decomps)==1 and decomps[0]==S

    print({
      'status':'PASS_FIXED_R_PROJECTIVE_TRADE_RANK_ASCENT_CONTROLS',
      'unsat_projective_lines':len(LU),
      'unsat_rank_safe_3trades':len(trades),
      'unsat_qrank_census':dict(sorted(census.items())),
      'sat_projective_lines':len(LS),
      'sat_cubic_decompositions':len(decomps),
    })

if __name__=='__main__': main()
