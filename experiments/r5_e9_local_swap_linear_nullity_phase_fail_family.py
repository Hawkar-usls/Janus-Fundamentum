#!/usr/bin/env python3
"""Controls for NM-0031 local-swap high-nullity phase-FAIL family."""
from __future__ import annotations
from fractions import Fraction
import json

def inv(P):
    q=[0]*len(P)
    for i,j in enumerate(P): q[j]=i
    return q

def phase(P,Q):
    n=len(P); iP,iQ=inv(P),inv(Q)
    phi=[None]*n
    for root in range(n):
        if phi[root] is not None: continue
        phi[root]=0; st=[root]
        while st:
            i=st.pop()
            for j,d in ((P[i],1),(Q[i],-1),(iP[i],-1),(iQ[i],1)):
                w=(phi[i]+d)%3
                if phi[j] is None:
                    phi[j]=w; st.append(j)
                elif phi[j]!=w:
                    return None
    return tuple(phi)

def connected(P,Q):
    iP,iQ=inv(P),inv(Q)
    seen={0}; st=[0]
    while st:
        i=st.pop()
        for R in (P,Q,iP,iQ):
            j=R[i]
            if j not in seen:
                seen.add(j); st.append(j)
    return len(seen)==len(P)

def matrix(P,Q):
    n=len(P); A=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i,P[i],Q[i]): A[i][j]+=1
    return A

def rank_q(A):
    M=[[Fraction(x) for x in r] for r in A]
    m=len(M); n=len(M[0]); rr=0
    for c in range(n):
        p=next((i for i in range(rr,m) if M[i][c]),None)
        if p is None: continue
        M[rr],M[p]=M[p],M[rr]
        q=M[rr][c]; M[rr]=[x/q for x in M[rr]]
        for i in range(m):
            if i==rr: continue
            q=M[i][c]
            if q: M[i]=[x-q*y for x,y in zip(M[i],M[rr])]
        rr+=1
        if rr==m: break
    return rr

def family(m):
    pts=[(r,a) for r in range(3) for a in range(m)]
    idx={p:i for i,p in enumerate(pts)}
    P=[];Q=[]
    for r,a in pts:
        P.append(idx[((r+1)%3,a)])
        if r==0: q=(2,(a+1)%m)
        elif r==1: q=(0,a)
        else: q=(1,a)
        Q.append(idx[q])
    u=idx[(0,0)]; v=idx[(2,2)]
    Qp=list(Q); Qp[u],Qp[v]=Qp[v],Qp[u]
    return pts,idx,tuple(P),tuple(Q),tuple(Qp),u,v

def exact_witness(pts,m):
    return tuple(1 if (r==0 and a==2) or (r==1 and a!=2) else 0 for r,a in pts)

samples=[]
for m in range(3,21):
    pts,idx,P,Q,Qp,u,v=family(m)
    n=3*m
    assert sorted(P)==list(range(n))
    assert sorted(Qp)==list(range(n))
    assert all(len({i,P[i],Qp[i]})==3 for i in range(n))
    assert connected(P,Qp)
    assert any(P[Qp[i]]!=Qp[P[i]] for i in range(n))
    assert P[Qp[u]]==v
    assert Qp[P[u]]==u
    assert phase(P,Qp) is None

    A=matrix(P,Q); Ap=matrix(P,Qp)
    d0=n-rank_q(A); d=n-rank_q(Ap)
    assert d0==m+1
    assert d>=m

    D=[[Ap[i][j]-A[i][j] for j in range(n)] for i in range(n)]
    assert rank_q(D)==1

    x=exact_witness(pts,m)
    assert sum(x)==m
    assert all(x[i]+x[P[i]]+x[Qp[i]]==1 for i in range(n))
    samples.append({"m":m,"n":n,"old_nullity":d0,"new_nullity":d})

out={
 "status":"PASS_LOCAL_SWAP_LINEAR_NULLITY_PHASE_FAIL_FAMILY",
 "family":{
   "m":"m>=3",
   "n":"3m",
   "swap":"Q-images at (0,0) and (2,2)",
   "connected":True,
   "noncommuting":True,
   "phase":"FAIL",
   "nullity_lower_bound":"m=n/3",
   "SAT":True,
   "explicit_witness":"S={(0,2)} union {(1,a): a!=2}",
 },
 "rank_update":"rank(Q'-Q)=1",
 "samples":samples,
 "composition":{
   "NM0029":"2-group polynomial covers preserve phase FAIL, noncommutativity, superlog nullity",
   "NM0030":"polynomial-degree 2-group covers achieve incidence girth>=10",
   "lifted_exact_one_witness":"fiber-constant",
 },
 "boundary":{
   "specified_10cycle_or_oddhole":"OPEN",
   "downstream_filter_replay":"REQUIRED",
   "P_VS_NP":"OPEN",
   "P_EQ_NP":"NOT_PROVED",
 }
}
print(json.dumps(out,sort_keys=True))
