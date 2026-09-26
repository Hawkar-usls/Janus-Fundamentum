#!/usr/bin/env python3
"""Finite controls for NM-0027 regular-uniform conflict expansion."""
from __future__ import annotations
from itertools import combinations, product
import json

def clauses_from_pq(P,Q):
    n=len(P)
    out=[]
    for i in range(n):
        C={i,P[i],Q[i]}
        assert len(C)==3
        out.append(tuple(sorted(C)))
    deg=[0]*n
    for C in out:
        for v in C: deg[v]+=1
    assert deg==[3]*n
    return out

def conflict_graph(edges,n):
    adj=[set() for _ in range(n)]
    for e in edges:
        for a,b in combinations(e,2):
            adj[a].add(b); adj[b].add(a)
    return adj

def independent(adj,S):
    S=tuple(S)
    return all(v not in adj[u] for u,v in combinations(S,2))

def all_independent(adj):
    n=len(adj)
    out=[]
    for bits in product((0,1),repeat=n):
        S=tuple(i for i,b in enumerate(bits) if b)
        if independent(adj,S): out.append(S)
    return out

def neighborhood(adj,S):
    S=set(S)
    N=set()
    for v in S: N.update(adj[v])
    return N-S

# Cubic literal source control from NM-0026.
P=[1,2,0,5,6,8,7,4,3]
Q=[5,3,4,6,2,1,8,0,7]
E=clauses_from_pq(P,Q)
G=conflict_graph(E,9)
inds=all_independent(G)

nonempty=[I for I in inds if I]
assert nonempty
for I in nonempty:
    N=neighborhood(G,I)
    assert len(N)>=2*len(I)

# Empty set is the unique maximum-difference independent set.
diffs={I:len(I)-len(neighborhood(G,I)) for I in inds}
assert diffs[()]==0
assert max(diffs[I] for I in nonempty)<0

# No nonempty classical crown side can even satisfy |N(C)|<=|C|.
assert all(len(neighborhood(G,I))>len(I) for I in nonempty)

alpha=max(map(len,inds))
assert alpha==3
maxsets=[I for I in inds if len(I)==alpha]
for I in maxsets:
    assert len(neighborhood(G,I))==6
    # Equality alpha=n/3 means every source clause is hit exactly once.
    assert all(sum(1 for v in e if v in I)==1 for e in E)

# Generic r=4,d=2 regular-uniform control.
H=[
 (0,1,2,3),
 (4,5,6,7),
 (0,1,4,5),
 (2,3,6,7),
]
deg=[0]*8
for e in H:
    for v in e: deg[v]+=1
assert deg==[2]*8
GH=conflict_graph(H,8)
for I in all_independent(GH):
    if I:
        assert len(neighborhood(GH,I))>=3*len(I)

out={
 "status":"PASS_REGULAR_UNIFORM_CONFLICT_EXPANSION",
 "general_theorem":"r-uniform d-regular strong independent I => |N(I)| >= (r-1)|I|",
 "cubic":{
   "independent_sets_checked":len(inds),
   "nonempty_sets_checked":len(nonempty),
   "expansion_factor":2,
   "alpha":alpha,
   "n_over_3":3,
   "max_nonempty_critical_difference":max(diffs[I] for I in nonempty),
   "nonempty_critical_independent_set":False,
   "classical_crown_side":False,
 },
 "r4_d2_control":{"expansion_factor":3,"pass":True},
 "boundary":{
   "critical_set_crown_on_literal_source":"EXTINGUISHED",
   "after_representation_change":"MAY_REAPPEAR",
   "domination_and_other_contextual_reductions":"STILL_LIVE",
   "P_VS_NP":"OPEN",
   "P_EQ_NP":"NOT_PROVED",
 }
}
print(json.dumps(out,sort_keys=True))
