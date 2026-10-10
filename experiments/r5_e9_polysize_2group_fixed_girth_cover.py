#!/usr/bin/env python3
"""Accounting and finite voltage controls for NM-0030.

The existence of the fixed finite 2-group K_{g,Delta} is source-bound to
residual-2 of free groups.  This checker validates the O(n) short-walk count,
the O(log n) repetition / polynomial-degree accounting, and a concrete
C2-voltage girth-raising toy cover.
"""
from __future__ import annotations
import math, json
from collections import deque

def short_walk_upper(n:int,delta:int,g:int)->int:
    if delta<=1:
        return 0
    # rooted directed nonbacktracking walks, an upper bound on closed ones
    return n*delta*sum((delta-1)**(ell-1) for ell in range(1,g))

def repetition_bound(M:int,K:int,g:int)->int:
    # Illustrative accounting for a fixed finite group order K.  NM-0030 does
    # NOT claim this K is the source-bound K_g.
    eps=K**(-(g-1))
    q=1.0-eps
    return max(1,math.ceil(math.log(M+1)/(-math.log(q))))

# Fixed g,Delta => M=O(n).
for n in (10,100,1000,10000):
    M=short_walk_upper(n,3,10)
    assert M==1533*n

# Any fixed K gives t=O(log n) and K^t=n^O(1).
K_demo=4
vals=[]
for n in (32,128,512,2048):
    M=short_walk_upper(n,3,6)
    t=repetition_bound(M,K_demo,6)
    degree=K_demo**t
    vals.append((n,t,degree))
# Doubling n only adds O(1) coordinates asymptotically.
assert vals[-1][1] < 4*vals[0][1]

def derived_cyclic_cover(vertices,edges,m,labels):
    # undirected voltage labels mod m; edge orientation is tuple order.
    adj=[[] for _ in range(vertices*m)]
    for ei,(u,v) in enumerate(edges):
        a=labels[ei]%m
        for t in range(m):
            x=u*m+t
            y=v*m+((t+a)%m)
            adj[x].append(y); adj[y].append(x)
    return adj

def girth(adj):
    best=10**9
    for s in range(len(adj)):
        dist=[-1]*len(adj); parent=[-1]*len(adj)
        dist[s]=0; q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if dist[v]<0:
                    dist[v]=dist[u]+1; parent[v]=u; q.append(v)
                elif parent[u]!=v:
                    best=min(best,dist[u]+dist[v]+1)
    return None if best==10**9 else best

# C4 with one nonzero C2 voltage lifts to C8.
adj=derived_cyclic_cover(4,[(0,1),(1,2),(2,3),(3,0)],2,[1,0,0,0])
assert girth(adj)==8

out={
 "status":"PASS_POLYSIZE_2GROUP_FIXED_GIRTH_ACCOUNTING",
 "source_bound_input":"FREE_GROUP_RESIDUALLY_FINITE_2GROUP_SUPPLIES_FIXED_K_g",
 "fixed_cubic_g10_short_walk_upper":"1533*n",
 "asymptotic":{
   "short_bad_walks":"O(n) for fixed g,Delta",
   "coordinates":"O(log n)",
   "cover_degree":"n^O(1)",
   "derandomization":"conditional expectation with fixed word length and fixed K_g",
 },
 "toy_voltage_control":{"base":"C4","deck":"C2","lift_girth":8},
 "boundary":{
   "ten_cycle_preservation":"OPEN",
   "superlog_phase_fail_base_family":"OPEN",
   "filtered_survivor":"OPEN",
   "P_VS_NP":"OPEN",
   "P_EQ_NP":"NOT_PROVED",
 }
}
print(json.dumps(out,sort_keys=True))
