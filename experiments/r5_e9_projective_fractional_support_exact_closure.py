#!/usr/bin/env python3
"""Exact finite controls for projective fractional-support closure.

This checker does not solve LPs. It verifies explicit positive fractional covers
and witness-based inactivity certificates on the frozen PG15 controls.
"""
from fractions import Fraction
from itertools import combinations

UNSAT=[
(1,10,11),(1,12,13),(1,14,15),(2,4,6),(2,5,7),(2,12,14),
(3,4,7),(3,8,11),(3,9,10),(4,11,15),(5,8,13),(5,9,12),
(6,8,14),(6,9,15),(7,10,13)]
SAT=[
(1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
(3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
(6,9,15),(7,8,15),(7,11,12)]


def matrix(E,n=15):
    return [[int(j+1 in L) for j in range(n)] for L in E]


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


def signatures(E,n=15):
    R,piv=gf2_rref(matrix(E,n)); free=[j for j in range(n) if j not in piv]
    B=[]
    for f in free:
        x=[0]*n; x[f]=1
        for i,p in enumerate(piv): x[p]=R[i][f]
        B.append(x)
    sig=[]
    for j in range(n):
        sig.append(sum(b[j]<<i for i,b in enumerate(B)))
    return sig,len(B)


def projective_lines(sig):
    return [tuple(i+1 for i in C) for C in combinations(range(len(sig)),3)
            if sig[C[0]]^sig[C[1]]^sig[C[2]]==0]


def rank_q(E,n=15):
    A=[[Fraction(x) for x in r] for r in matrix(E,n)]; rr=0
    for c in range(n):
        p=next((i for i in range(rr,len(A)) if A[i][c]),None)
        if p is None: continue
        A[rr],A[p]=A[p],A[rr]
        f=A[rr][c]; A[rr]=[x/f for x in A[rr]]
        for i in range(len(A)):
            if i!=rr and A[i][c]:
                f=A[i][c]; A[i]=[x-f*y for x,y in zip(A[i],A[rr])]
        rr+=1
    return rr


def exact_witnesses(E,sig,k):
    out=[]
    for t in range(1<<k):
        x=[1^(((s&t).bit_count())&1) for s in sig]
        if all(sum(x[j-1] for j in row)==1 for row in E):
            out.append(tuple(x))
    return out


def main():
    # UNSAT control: all 15 nonzero PG(3,2) points, hence all 35 lines.
    sigU,kU=signatures(UNSAT)
    LU=projective_lines(sigU)
    assert kU==4 and len(set(sigU))==15 and 0 not in sigU
    assert len(LU)==35
    # Every point of PG(3,2) is on 7 lines. lambda=3/7 is a strictly positive
    # fractional 3-factor on every projective line.
    for v in range(1,16):
        degree=sum(Fraction(3,7) for L in LU if v in L)
        assert degree==3
    assert rank_q(LU)==15
    assert not exact_witnesses(UNSAT,sigU,kU)

    # SAT control: 19 projective lines, 15 original active lines.
    sigS,kS=signatures(SAT)
    LS=projective_lines(sigS)
    assert kS==5 and len(set(sigS))==15 and 0 not in sigS
    assert len(LS)==19
    witnesses=exact_witnesses(SAT,sigS,kS)
    assert len(witnesses)==4
    extras=sorted(set(LS)-set(SAT))
    assert len(extras)==4

    # Original source indicator is a positive fractional 3-factor on all source
    # lines, so they are active.
    for v in range(1,16):
        assert sum(1 for L in SAT if v in L)==3

    # PFSC-1 says an active line must contain exactly one selected point for
    # every Exact-One witness. Each extra line has an explicit witness selecting
    # all three points, so none can be fractionally active.
    for L in extras:
        assert any(sum(w[j-1] for j in L)==3 for w in witnesses)
    activeS=SAT
    assert rank_q(activeS)==11

    # Closure preserves all witnesses on the SAT control.
    assert all(all(sum(w[j-1] for j in L)==1 for L in activeS) for w in witnesses)

    print({
        'status':'PASS_PROJECTIVE_FRACTIONAL_SUPPORT_EXACT_CLOSURE_CONTROLS',
        'unsat_projective_lines':len(LU),
        'unsat_active_lines':len(LU),
        'unsat_active_qrank':rank_q(LU),
        'sat_projective_lines':len(LS),
        'sat_active_lines':len(activeS),
        'sat_active_qrank':rank_q(activeS),
        'sat_exact_witnesses':len(witnesses),
        'sat_inactive_extra_lines':extras,
    })

if __name__=='__main__': main()
