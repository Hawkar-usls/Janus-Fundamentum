#!/usr/bin/env python3
"""Frozen replay for the fixed-point affine-closure / low-determinant firewall."""

from collections import defaultdict
from fractions import Fraction
from itertools import product

Q=30
COLS=[
(9,15,23),(1,2,22),(13,20,27),(4,24,25),(5,6,28),(0,7,19),
(11,17,29),(14,21,26),(3,10,18),(8,12,16),(2,11,19),(9,14,19),
(12,18,25),(4,15,22),(10,15,28),(1,17,24),(5,8,21),(1,16,29),
(0,5,17),(4,8,20),(6,18,27),(3,20,26),(2,6,10),(23,25,26),
(7,9,29),(14,22,28),(3,12,23),(7,11,13),(13,21,24),(0,16,27),
]
PLANTED=set(range(10))
SEED_CHECK=26
SEED_VAR=7

def matrix():
    A=[[0]*Q for _ in range(Q)]
    for j,C in enumerate(COLS):
        for i in C:A[i][j]=1
    return A

def verify_source(A):
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[i][j] for i in range(Q))==3 for j in range(Q))
    for a in range(Q):
        for b in range(a+1,Q):
            assert sum(A[i][a]*A[i][b] for i in range(Q))<=1
    adj=[set() for _ in range(2*Q)]
    for i in range(Q):
        for j in range(Q):
            if A[i][j]:
                adj[i].add(Q+j);adj[Q+j].add(i)
    seen={0};stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v);stack.append(v)
    assert len(seen)==2*Q
    assert all(sum(A[i][j] for j in PLANTED)==1 for i in range(Q))

def propagate(A,assigned):
    vals=[None]*Q
    for j,v in assigned.items():vals[j]=v
    clauses=[[j for j in range(Q) if A[i][j]] for i in range(Q)]
    changed=True
    while changed:
        changed=False
        for vs in clauses:
            ones=sum(vals[j]==1 for j in vs)
            unk=[j for j in vs if vals[j] is None]
            if ones>1 or (ones==0 and not unk):
                return None
            if ones==1:
                for j in unk:
                    vals[j]=0;changed=True
            elif len(unk)==1:
                vals[unk[0]]=1;changed=True
    return vals

def quotient(A,vals):
    clauses=[[j for j in range(Q) if A[i][j]] for i in range(Q)]
    unknown=[j for j,v in enumerate(vals) if v is None]
    xor=[]
    tern=[]
    for vs in clauses:
        u=[j for j in vs if vals[j] is None]
        if len(u)==2:xor.append(tuple(u))
        elif len(u)==3:tern.append(tuple(u))
        elif len(u)==1:raise AssertionError("propagation not closed")
    g=defaultdict(list)
    for a,b in xor:
        g[a].append((b,1));g[b].append((a,1))
    parity={};compid={};comps=[]
    for v in unknown:
        if v in parity:continue
        cid=len(comps);parity[v]=0;stack=[v];comp=[]
        while stack:
            u=stack.pop();compid[u]=cid;comp.append(u)
            for w,p in g[u]:
                want=parity[u]^p
                if w in parity:
                    assert parity[w]==want
                else:
                    parity[w]=want;stack.append(w)
        comps.append(comp)
    qtern=[tuple((compid[v],parity[v]) for v in tri) for tri in tern]
    return unknown,comps,parity,compid,qtern

def affine_closure(A,initial):
    assigned=dict(initial)
    while True:
        vals=propagate(A,assigned)
        assert vals is not None
        unknown,comps,parity,compid,qtern=quotient(A,vals)
        forced={}
        repeated=0
        for tri in qtern:
            ids=sorted(set(c for c,p in tri))
            if len(ids)==3:continue
            repeated+=1
            loc={c:i for i,c in enumerate(ids)}
            allowed=[]
            for av in product((0,1),repeat=len(ids)):
                lits=[av[loc[c]]^p for c,p in tri]
                if sum(lits)==1:allowed.append(av)
            assert allowed
            for k,c in enumerate(ids):
                s={a[k] for a in allowed}
                if len(s)==1:
                    v=next(iter(s))
                    assert c not in forced or forced[c]==v
                    forced[c]=v
        if not forced:
            assert repeated==0
            return vals,unknown,comps,parity,compid,qtern
        for c,t in forced.items():
            for v in comps[c]:
                assigned[v]=t^parity[v]

def det(M):
    n=len(M)
    A=[[Fraction(x) for x in row] for row in M]
    d=Fraction(1)
    for j in range(n):
        p=next((i for i in range(j,n) if A[i][j]),None)
        if p is None:return 0
        if p!=j:
            A[j],A[p]=A[p],A[j];d=-d
        z=A[j][j];d*=z
        for i in range(j+1,n):
            if A[i][j]:
                f=A[i][j]/z
                for k in range(j,n):A[i][k]-=f*A[j][k]
    assert d.denominator==1
    return int(d)

def main():
    A=matrix();verify_source(A)
    neigh=[j for j in range(Q) if A[SEED_CHECK][j]]
    assert neigh==[7,21,23]
    init={j:(1 if j==SEED_VAR else 0) for j in neigh}
    vals,unknown,comps,parity,compid,qtern=affine_closure(A,init)
    assert len(unknown)==23
    assert len(comps)==11
    assert len(qtern)==15
    assert all(len({c for c,p in tri})==3 for tri in qtern)

    rows=[]
    rhs=[]
    for tri in qtern:
        row=[0]*len(comps);ones=0
        for c,p in tri:
            if p:row[c]-=1;ones+=1
            else:row[c]+=1
        rows.append(row);rhs.append(1-ones)

    sub2=[[rows[i][j] for j in (4,9)] for i in (4,6)]
    assert sub2==[[1,1],[-1,1]]
    assert det(sub2)==2

    sub5=[[rows[i][j] for j in (0,2,3,5)] for i in (5,7,8,12)]
    assert sub5==[
        [-1,-1,0,1],
        [0,-1,0,-1],
        [-1,1,-1,0],
        [1,0,-1,0],
    ]
    assert det(sub5)==-5

    print("AFFINE_CLOSURE_Q30: PASS")
    print("unknown=23 quotient_components=11 proper_ternary=15")
    print("post-closure 2x2 determinant=2")
    print("post-closure 4x4 determinant=-5")
    print("TU/BIMODULAR quotient shortcut: REFUTED")
    print("P_VS_NP remains OPEN")

if __name__=="__main__":
    main()
