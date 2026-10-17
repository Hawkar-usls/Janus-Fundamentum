#!/usr/bin/env python3
from fractions import Fraction
from math import gcd
import json


def build(m):
    pts=[(r,a) for r in range(3) for a in range(m)]
    idx={p:i for i,p in enumerate(pts)}
    n=3*m
    P=list(range(n)); Q=list(range(n))
    for p in pts:
        r,a=p
        P[idx[p]]=idx[((r+1)%3,a)]
        if p==(0,0): q=(1,2)
        elif p==(2,2): q=(2,1)
        elif r==0: q=(2,(a+1)%m)
        elif r==1: q=(0,a)
        else: q=(1,a)
        Q[idx[p]]=idx[q]
    A=[[0]*n for _ in range(n)]
    for i in range(n):
        for j in (i,P[i],Q[i]): A[i][j]=1
    T=[P[Q[i]] for i in range(n)]
    return pts,idx,P,Q,T,A


def rank_rref(A):
    M=[[Fraction(x) for x in row] for row in A]
    rows=len(M); cols=len(M[0]); piv=[]; r=0
    for c in range(cols):
        p=next((i for i in range(r,rows) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        z=M[r][c]; M[r]=[x/z for x in M[r]]
        for i in range(rows):
            if i==r or M[i][c]==0: continue
            z=M[i][c]
            M[i]=[M[i][j]-z*M[r][j] for j in range(cols)]
        piv.append(c); r+=1
    return r,M,piv


def nullspace_rows(A):
    rank,M,piv=rank_rref(A)
    n=len(A); free=[c for c in range(n) if c not in piv]
    basis=[]
    for f in free:
        v=[Fraction(0) for _ in range(n)]; v[f]=1
        for rr,p in enumerate(piv): v[p]=-M[rr][f]
        basis.append(v)
    rows=[[basis[j][i] for j in range(len(basis))] for i in range(n)]
    return rank,rows


def ratio(u,v):
    # u=lambda*v, return lambda; None if not proportional
    k=next((i for i,x in enumerate(v) if x),None)
    if k is None: return None
    lam=u[k]/v[k]
    return lam if all(u[i]==lam*v[i] for i in range(len(u))) else None


def cycle_from(T,start):
    out=[]; x=start
    while x not in out:
        out.append(x); x=T[x]
    assert x==start
    return out

controls=[]
for m in range(3,13):
    pts,idx,P,Q,T,A=build(m); n=3*m
    # cubic source and explicit parent witness
    assert all(sum(row)==3 for row in A)
    assert all(sum(A[i][j] for i in range(n))==3 for j in range(n))
    S={(0,2)}|{(1,a) for a in range(m) if a!=2}
    x=[1 if p in S else 0 for p in pts]
    assert all(sum(A[i][j]*x[j] for j in range(n))==1 for i in range(n))

    # exact T orbit structure used by the arbitrary-size primitivity proof
    C=cycle_from(T,idx[(0,0)])
    expected=[(0,0),(2,2)]+[(0,a) for a in range(1,m)]
    assert [pts[i] for i in C]==expected
    fixed=[i for i in range(n) if T[i]==i]
    assert len(C)==m+1 and len(fixed)==2*m-1
    assert set(C).isdisjoint(fixed) and len(set(C)|set(fixed))==n
    assert gcd(m+1,2*m-1)==gcd(m+1,3)
    s=idx[(2,2)]
    assert P[s]==idx[(0,2)] and P[s] in C
    assert all(P[idx[(0,a)]] in fixed for a in range(m))

    rank,rows=nullspace_rows(A)
    nullity=n-rank
    assert nullity>=m

    # finite RKPR scope diagnostic: a nontrivial -1/2 proportional class exists.
    has_minus_half=False
    for i in range(n):
        if not any(rows[i]): continue
        for j in range(i+1,n):
            if not any(rows[j]): continue
            lam=ratio(rows[j],rows[i])
            if lam in (Fraction(-2),Fraction(-1,2)):
                has_minus_half=True; break
        if has_minus_half: break
    assert has_minus_half

    controls.append({"m":m,"n":n,"rank_Q":rank,"nullity_Q":nullity,
                     "T_long_cycle":m+1,"T_fixed":2*m-1,
                     "gcd_block_bound":gcd(m+1,2*m-1),
                     "rkpr_minus_half_pair":has_minus_half})

print(json.dumps({
  "status":"PASS_LOCAL_SWAP_PRIMITIVE_LINEAR_NULLITY_BARRIER",
  "theorem":{
    "m_range":"all m>=3",
    "primitive":"proved by block argument in research note",
    "nullity_lower":"nu_Q >= m = n/3",
    "forbidden_shortcut":"high rational nullity => nontrivial permutation block system",
    "scope":"pre-RKPR general cubic two-permutation carrier"
  },
  "finite_exact_controls":controls,
  "boundary":{
    "post_RKPR_hostile_family":"NOT_CLAIMED",
    "linear_hypergraph_hostile_family":"NOT_CLAIMED",
    "D1":"EMPTY",
    "P_VS_NP":"OPEN"
  }
},sort_keys=True))
