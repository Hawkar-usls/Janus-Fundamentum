#!/usr/bin/env python3
"""Exact control for NM-0028 high-girth odd-hole sparse attachments."""
from __future__ import annotations
from collections import deque
from fractions import Fraction
from itertools import combinations
import json

LCF = [-29,-19,-13,13,21,-27,27,33,-13,13,19,-21,-33,29]
N = 70

def harries_graph():
    adj=[set() for _ in range(N)]
    for i in range(N):
        j=(i+1)%N
        adj[i].add(j); adj[j].add(i)
    seq=LCF*5
    assert len(seq)==N
    for i,d in enumerate(seq):
        j=(i+d)%N
        adj[i].add(j); adj[j].add(i)
    return adj

def girth(adj):
    best=10**9
    for s in range(len(adj)):
        dist=[-1]*len(adj)
        parent=[-1]*len(adj)
        dist[s]=0
        q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if dist[v]<0:
                    dist[v]=dist[u]+1
                    parent[v]=u
                    q.append(v)
                elif parent[u]!=v:
                    best=min(best,dist[u]+dist[v]+1)
    return best

def bipartition(adj):
    color=[None]*len(adj)
    color[0]=0
    q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if color[v] is None:
                color[v]=1-color[u]
                q.append(v)
            else:
                assert color[v]!=color[u]
    return color

def rank_q(matrix):
    A=[[Fraction(x) for x in row] for row in matrix]
    m=len(A); n=len(A[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if A[i][c]),None)
        if p is None:
            continue
        A[r],A[p]=A[p],A[r]
        z=A[r][c]
        A[r]=[x/z for x in A[r]]
        for i in range(m):
            if i==r or not A[i][c]:
                continue
            z=A[i][c]
            A[i]=[A[i][j]-z*A[r][j] for j in range(n)]
        r+=1
    return r

B=harries_graph()
assert all(len(x)==3 for x in B)
assert sum(map(len,B))//2==105
assert girth(B)==10

color=bipartition(B)
V={i for i,c in enumerate(color) if c==0}
C=set(range(N))-V
assert len(V)==len(C)==35

# Explicit source-bound 10-cycle in the Sage/LCF Harries labeling.
cycle=[0,1,2,3,4,5,6,7,40,41]
assert len(set(cycle))==10
assert all(cycle[(i+1)%10] in B[cycle[i]] for i in range(10))
assert all(cycle[i] not in B[cycle[j]]
           for i in range(10) for j in range(i+1,10)
           if (j-i) not in (1,9) and not (i==0 and j==9))

if cycle[0] not in V:
    cycle=cycle[1:]+cycle[:1]
x=[cycle[2*i] for i in range(5)]
c=[cycle[2*i+1] for i in range(5)]
assert all(x[i] in V and c[i] in C for i in range(5))
assert all(c[i] in B[x[i]] and x[(i+1)%5] in B[c[i]] for i in range(5))

# Conflict graph on variable side.
CG={u:set() for u in V}
for clause in C:
    vs=sorted(B[clause])
    assert len(vs)==3 and all(v in V for v in vs)
    for u,v in combinations(vs,2):
        CG[u].add(v); CG[v].add(u)

# Girth >=10 implies the six co-clause neighbors are all distinct.
assert set(map(len,CG.values()))=={6}

# The variable-side projection of the 10-cycle is an induced C5.
for i in range(5):
    for j in range(i+1,5):
        edge=x[j] in CG[x[i]]
        diff=j-i
        should=diff in (1,4)
        assert edge==should

w=[]
D=[]
ab=[]
for i in range(5):
    wi=next(iter(B[c[i]]-{x[i],x[(i+1)%5]}))
    w.append(wi)
    Di=next(iter(B[x[i]]-{c[i],c[(i-1)%5]}))
    D.append(Di)
    pair=sorted(B[Di]-{x[i]})
    assert len(pair)==2
    ab.append(pair)

ports=w+[u for pair in ab for u in pair]
assert len(ports)==15
assert len(set(ports))==15
assert not (set(ports)&set(x))

# Every hole vertex is a literal conflict-claw center.
claw_leaves={}
for i in range(5):
    leaves=(w[(i-1)%5],w[i],ab[i][0])
    assert all(v in CG[x[i]] for v in leaves)
    assert all(v not in CG[u] for u,v in combinations(leaves,2))
    claw_leaves[str(x[i])]=list(leaves)

# Neighborhood domination is globally absent in this high-girth control.
dom=[]
for u in V:
    Nu=CG[u]|{u}
    for v in V:
        if u!=v and Nu <= (CG[v]|{v}):
            dom.append((u,v))
assert not dom

# Degree-2 folding cannot start on a 6-regular conflict graph.
assert all(len(CG[u])!=2 for u in V)

# Exact rational incidence rank.  This is an epistemic firewall:
# the finite Harries control is caught by the already-known low-nullity lane.
Vs=sorted(V); Cs=sorted(C)
vi={v:i for i,v in enumerate(Vs)}
matrix=[]
for clause in Cs:
    row=[0]*len(Vs)
    for v in B[clause]:
        row[vi[v]]=1
    matrix.append(row)
rq=rank_q(matrix)
assert rq==35

out={
  "status":"PASS_HIGH_GIRTH_ODD_HOLE_SPARSE_ATTACHMENT_CONTROL",
  "source_control":{
    "graph":"Harries (3,10)-cage",
    "order":70,
    "edges":105,
    "bipartition":[35,35],
    "girth":10,
    "lcf":LCF,
  },
  "odd_hole":{
    "incidence_cycle":cycle,
    "conflict_vertices":x,
    "edge_clauses":c,
    "w":w,
    "D":D,
    "ab":ab,
    "external_ports":ports,
    "external_ports_unique":15,
    "induced_C5":True,
    "every_hole_vertex_is_claw_center":True,
    "claw_leaves":claw_leaves,
  },
  "conflict_graph":{
    "vertices":35,
    "degree":6,
    "closed_neighborhood_domination_pairs":dom,
    "degree2_folding_vertices":[],
    "NM0027_two_expansion":"INHERITED_THEOREM_FOR_UNTOUCHED_CUBIC_SOURCE",
  },
  "epistemic_firewall":{
    "rational_incidence_rank":rq,
    "rational_nullity":35-rq,
    "low_nullity_lane":"CATCHES_THIS_FINITE_CONTROL",
    "full_PA0001_filtered_survivor":"NOT_CLAIMED",
  },
  "scope":{
    "two_expansion_forces_local_port_aliasing":"FALSIFIED",
    "two_expansion_forces_neighborhood_domination":"FALSIFIED",
    "long_range_or_extra_filtered_promises":"REQUIRED_FOR_NEXT_LEVERAGE",
    "D1":"EMPTY",
    "P_VS_NP":"OPEN",
    "P_EQ_NP":"NOT_PROVED",
  }
}
print(json.dumps(out,sort_keys=True))
