#!/usr/bin/env python3
"""Exact finite controls for NM-0026 contextual MIS-kernel transfer."""
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

def conflict_graph(clauses,n):
    adj=[set() for _ in range(n)]
    for C in clauses:
        for a,b in combinations(C,2):
            adj[a].add(b); adj[b].add(a)
    return adj

def independent(adj,S):
    S=set(S)
    return all(v not in adj[u] for u,v in combinations(S,2))

def alpha_witness(adj, keep=None):
    if keep is None: keep=tuple(range(len(adj)))
    keep=tuple(keep)
    best=()
    for bits in product((0,1), repeat=len(keep)):
        if sum(bits)<=len(best): continue
        S=tuple(keep[i] for i,b in enumerate(bits) if b)
        if independent(adj,S): best=S
    return best

def exact_one_solutions(clauses,n):
    out=[]
    for bits in product((0,1),repeat=n):
        if all(sum(bits[v] for v in C)==1 for C in clauses):
            out.append(tuple(i for i,b in enumerate(bits) if b))
    return out

def claws(adj):
    out=[]
    for c in range(len(adj)):
        for L in combinations(sorted(adj[c]),3):
            if independent(adj,L):
                out.append((c,L))
    return out

def induced_cycle5(adj,S):
    S=tuple(S)
    return all(sum(1 for w in S if w!=v and w in adj[v])==2 for v in S)

# Control A: literal cubic source with both a claw and a closed-neighborhood
# domination pair N[8] subset N[3].
P1=[1,2,0,5,6,8,7,4,3]
Q1=[5,3,4,6,2,1,8,0,7]
C1=clauses_from_pq(P1,Q1)
G1=conflict_graph(C1,9)
assert (G1[8]|{8}) <= (G1[3]|{3})
A1=alpha_witness(G1)
A1_del3=alpha_witness(G1,[v for v in range(9) if v!=3])
assert len(A1)==3==len(A1_del3)
S1=exact_one_solutions(C1,9)
assert S1 and all(len(S)==3 for S in S1)
assert independent(G1,(2,5,7))
assert (2,5,7) in [L for c,L in claws(G1) if c==0]

# Domination witness map: any independent set containing 3 can replace 3 by 8.
for bits in product((0,1),repeat=9):
    S={i for i,b in enumerate(bits) if b}
    if 3 in S and independent(G1,S):
        T=(S-{3})|{8}
        assert independent(G1,T)
        assert len(T)==len(S)

# Every claw at a cubic source center uses one leaf from each of its three
# center clauses, in the precise sense that the leaf-to-center-clause
# incidence sets are three disjoint singletons covering the 3 clauses.
def verify_claw_transversality(clauses,adj):
    for c,L in claws(adj):
        incident=[i for i,C in enumerate(clauses) if c in C]
        assert len(incident)==3
        leaf_inc=[]
        for x in L:
            s={i for i in incident if x in clauses[i]}
            assert s
            leaf_inc.append(s)
        for a,b in combinations(leaf_inc,2):
            assert not (a & b)
        assert set().union(*leaf_inc)==set(incident)
        assert all(len(s)==1 for s in leaf_inc)

verify_claw_transversality(C1,G1)

# Control B: cubic source whose conflict graph is claw-free but imperfect
# (contains an induced C5), proving the claw-free P-island is not merely the
# perfect-graph island.
P2=[3,8,5,6,7,2,1,0,4]
Q2=[2,5,6,0,1,3,8,4,7]
C2=clauses_from_pq(P2,Q2)
G2=conflict_graph(C2,9)
assert not claws(G2)
C5=(0,1,2,4,5)
assert induced_cycle5(G2,C5)
A2=alpha_witness(G2)
assert len(A2)==2 < 3
assert not exact_one_solutions(C2,9)

# General K1,4-free control on both sources: alpha(N(v))<=3.
for G in (G1,G2):
    for v in range(len(G)):
        N=sorted(G[v])
        for four in combinations(N,4):
            assert not independent(G,four)

out={
 "status":"PASS_CONTEXTUAL_MIS_KERNEL_TRANSFER_CONTROLS",
 "domination_control":{
   "n":9,
   "dominated_vertex":3,
   "replacement_vertex":8,
   "closed_neighborhood_inclusion":True,
   "alpha_before":len(A1),
   "alpha_after_delete":len(A1_del3),
   "target_n_over_3":3,
   "exact_one_solution_count":len(S1),
 },
 "claw_geometry":{
   "sample_center":0,
   "sample_leaves":[2,5,7],
   "one_leaf_per_center_clause":True,
   "K1_4_free":True,
 },
 "claw_free_imperfect_control":{
   "n":9,
   "claw_free":True,
   "induced_C5":list(C5),
   "alpha":len(A2),
   "target_n_over_3":3,
   "exact_one_solutions":0,
 },
 "theorem_boundary":{
   "alpha_offset_transfer":"EXACT",
   "known_MIS_reductions":"SOURCE_BOUND_DONORS",
   "claw_free_conflict_graph":"SOURCE_BOUND_POLY_ISLAND",
   "universal_kernelization":"NOT_PROVED",
   "next":"ODD_HOLE_CONTEXTUAL_MIS_REDUCTION_LEAN_DOMINANCE",
   "P_VS_NP":"OPEN",
 }
}
print(json.dumps(out,sort_keys=True))
