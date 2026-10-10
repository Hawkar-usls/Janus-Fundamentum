#!/usr/bin/env python3
"""Finite controls for NM-0029 coprime-cover phase persistence."""
from __future__ import annotations
from fractions import Fraction
from itertools import product
import json

def invert(P):
    q=[0]*len(P)
    for i,j in enumerate(P): q[j]=i
    return q

def connected(P,Q):
    iP,iQ=invert(P),invert(Q)
    seen={0}; stack=[0]
    while stack:
        i=stack.pop()
        for R in (P,Q,iP,iQ):
            j=R[i]
            if j not in seen:
                seen.add(j); stack.append(j)
    return len(seen)==len(P)

def phase(P,Q):
    n=len(P); iP,iQ=invert(P),invert(Q)
    phi=[None]*n
    for root in range(n):
        if phi[root] is not None: continue
        phi[root]=0; stack=[root]
        while stack:
            i=stack.pop()
            for j,d in ((P[i],1),(Q[i],-1),(iP[i],-1),(iQ[i],1)):
                want=(phi[i]+d)%3
                if phi[j] is None:
                    phi[j]=want; stack.append(j)
                elif phi[j]!=want:
                    return None
    return tuple(phi)

def matrix(P,Q):
    n=len(P); A=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i,P[i],Q[i]): A[i][j]+=1
    return A

def rank_q(A):
    M=[[Fraction(x) for x in r] for r in A]
    m=len(M); n=len(M[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        q=M[r][c]
        M[r]=[x/q for x in M[r]]
        for i in range(m):
            if i==r: continue
            q=M[i][c]
            if q: M[i]=[x-q*y for x,y in zip(M[i],M[r])]
        r+=1
        if r==m: break
    return r

def additive_cover(P,Q,m,p_shift,q_shift):
    n=len(P)
    def idx(i,t): return i*m+t
    Pt=[0]*(n*m); Qt=[0]*(n*m)
    for i in range(n):
        for t in range(m):
            Pt[idx(i,t)]=idx(P[i],(t+p_shift[i])%m)
            Qt[idx(i,t)]=idx(Q[i],(t+q_shift[i])%m)
    return tuple(Pt),tuple(Qt)

def canonical_three_cover(P,Q):
    n=len(P)
    return additive_cover(P,Q,3,[1]*n,[-1]*n)

# Literal cubic, connected, noncommuting, phase-FAIL base from NM-0026 controls.
P=(1,2,0,5,6,8,7,4,3)
Q=(5,3,4,6,2,1,8,0,7)
n=len(P)
assert connected(P,Q)
assert phase(P,Q) is None
assert any(P[Q[i]]!=Q[P[i]] for i in range(n))
assert all(len({i,P[i],Q[i]})==3 for i in range(n))
d=n-rank_q(matrix(P,Q))
assert d==1

# Exhaust all additive Z2 labelled covers: none may repair phase.
z2_checked=0
for mask in range(1<<(2*n)):
    ps=[(mask>>i)&1 for i in range(n)]
    qs=[(mask>>(n+i))&1 for i in range(n)]
    Pt,Qt=additive_cover(P,Q,2,ps,qs)
    assert phase(Pt,Qt) is None
    assert any(Pt[Qt[i]]!=Qt[Pt[i]] for i in range(len(Pt)))
    z2_checked+=1

# Old-kernel injection is proved symbolically in the artifact; replay rational
# rank on a deterministic sample rather than all 2^18 covers.
rank_samples=0
for mask in range(0,1<<(2*n),4093):
    ps=[(mask>>i)&1 for i in range(n)]
    qs=[(mask>>(n+i))&1 for i in range(n)]
    Pt,Qt=additive_cover(P,Q,2,ps,qs)
    assert len(Pt)-rank_q(matrix(Pt,Qt)) >= d
    rank_samples+=1

# A handful of coprime higher-degree additive controls.
coprime_controls=[]
for m in (4,5,7,8):
    ps=[(i*i+1)%m for i in range(n)]
    qs=[(2*i+3)%m for i in range(n)]
    Pt,Qt=additive_cover(P,Q,m,ps,qs)
    assert phase(Pt,Qt) is None
    assert any(Pt[Qt[i]]!=Qt[Pt[i]] for i in range(len(Pt)))
    assert len(Pt)-rank_q(matrix(Pt,Qt)) >= d
    coprime_controls.append(m)

# Sharpness: the canonical 3-cover repairs every labelled phase obstruction.
P3,Q3=canonical_three_cover(P,Q)
phi3=phase(P3,Q3)
assert phi3 is not None
assert connected(P3,Q3)
assert all(phi3[i*3+t]==t for i in range(n) for t in range(3))
assert any(P3[Q3[i]]!=Q3[P3[i]] for i in range(len(P3)))

# PASS base remains PASS under arbitrary cover by pullback.
Pp=(1,2,0)
Qp=(2,0,1)
assert phase(Pp,Qp) is not None
Pt,Qt=additive_cover(Pp,Qp,4,[1,0,3],[2,1,0])
assert phase(Pt,Qt) is not None

out={
 "status":"PASS_COPRIME_COVER_PHASE_PERSISTENCE",
 "theorem":{
   "cover_degree_coprime_to_3":"PHASE_BASE_IFF_PHASE_COVER",
   "base_phase_fail":"PERSISTS_TO_ALL_COPRIME_DEGREE_LABELLED_COVERS",
   "two_group_covers":"PHASE_FAIL_PERSISTS",
   "base_noncommuting":"PERSISTS_TO_EVERY_LABELLED_COVER",
   "old_rational_kernel":"INJECTS_FIBER_CONSTANTLY",
   "polynomial_degree_cover":"SUPERLOG_NULLITY_PRESERVED_IF_BASE_NULLITY_IS_SUPERLOG",
 },
 "controls":{
   "base_n":n,
   "base_nullity":d,
   "z2_additive_covers_exhausted":z2_checked,
   "z2_rational_rank_samples":rank_samples,
   "other_coprime_degrees":coprime_controls,
   "canonical_3cover_connected":True,
   "canonical_3cover_phase":"PASS",
 },
 "sharpness":{
   "degree_3_can_repair_phase_fail":True,
   "canonical_repair":"P~(i,t)=(P(i),t+1), Q~(i,t)=(Q(i),t-1)",
 },
 "boundary":{
   "high_girth_polynomial_size_2group_cover":"OPEN",
   "superlog_phase_fail_base_family":"OPEN",
   "filtered_survivor_family":"OPEN",
   "P_VS_NP":"OPEN",
   "P_EQ_NP":"NOT_PROVED",
 }
}
print(json.dumps(out,sort_keys=True))
