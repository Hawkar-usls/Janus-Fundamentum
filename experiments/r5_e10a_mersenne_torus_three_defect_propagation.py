#!/usr/bin/env python3
"""Exact finite certificates for the three-defect torus propagation lemma.

The asymptotic proof has only one finite local part: classify connected unions
of at most three deleted plaquette-triangles in the infinite triangular
plaquette graph. L=7 is additionally replayed exhaustively as an independent
torus control.
"""
from __future__ import annotations

import json
from itertools import combinations
from collections import Counter

DIRS=((1,0),(-1,0),(0,1),(0,-1),(1,-1),(-1,1))

def neigh(p):
    x,y=p
    return {(x+dx,y+dy) for dx,dy in DIRS}

def D(s):
    x,y=s
    return {(x,y),(x-1,y),(x,y-1)}

def canon(shape):
    shape=set(shape)
    reps=[]
    for ox,oy in shape:
        reps.append(tuple(sorted((x-ox,y-oy) for x,y in shape)))
    return min(reps)

def components(nodes, adjacency=neigh):
    rem=set(nodes)
    out=[]
    while rem:
        s=next(iter(rem))
        rem.remove(s)
        c={s}
        stack=[s]
        while stack:
            u=stack.pop()
            for v in adjacency(u):
                if v in rem:
                    rem.remove(v)
                    c.add(v)
                    stack.append(v)
        out.append(c)
    return out

def triangles_touch(s,t):
    A,B=D(s),D(t)
    return bool(A&B) or any(v in neigh(u) for u in A for v in B)

TOUCH_OFFSETS=tuple(
    sorted(
        (x,y)
        for x in range(-3,4)
        for y in range(-3,4)
        if (x,y)!=(0,0) and triangles_touch((0,0),(x,y))
    )
)
assert len(TOUCH_OFFSETS)==18
assert max(max(abs(x),abs(y)) for x,y in TOUCH_OFFSETS)==2

def center_touch_neigh(p):
    x,y=p
    return {(x+dx,y+dy) for dx,dy in TOUCH_OFFSETS}

def connected_center_shapes(n):
    shapes={((0,0),)}
    for _ in range(1,n):
        nxt=set()
        for sh in shapes:
            S=set(sh)
            frontier=set().union(*(center_touch_neigh(s) for s in S))-S
            for q in frontier:
                nxt.add(canon(S|{q}))
        shapes=nxt
    return [set(s) for s in sorted(shapes)]

def bounded_holes(S, margin=6):
    R=set().union(*(D(s) for s in S))
    xs=[x for x,_ in R]; ys=[y for _,y in R]
    xmin,xmax=min(xs)-margin,max(xs)+margin
    ymin,ymax=min(ys)-margin,max(ys)+margin
    box={(x,y) for x in range(xmin,xmax+1) for y in range(ymin,ymax+1)}-R
    holes=[]
    for c in components(box):
        if not any(x in (xmin,xmax) or y in (ymin,ymax) for x,y in c):
            holes.append(c)
    return holes,R

local_counts={}
hole_examples=[]
for t in (1,2,3):
    shapes=connected_center_shapes(t)
    hist=Counter()
    for S in shapes:
        holes,R=bounded_holes(S)
        sig=tuple(sorted(len(c) for c in holes))
        hist[sig]+=1
        if sig:
            hole_examples.append({
                "defects":sorted(S),
                "hole_signature":sig,
                "holes":[sorted(c) for c in holes],
            })
    local_counts[t]={"shapes":len(shapes),"hole_signatures":{str(k):v for k,v in sorted(hist.items())}}

assert len(connected_center_shapes(1))==1
assert len(connected_center_shapes(2))==9
assert len(connected_center_shapes(3))==99
assert local_counts[1]["hole_signatures"]=={"()":1}
assert local_counts[2]["hole_signatures"]=={"()":9}
assert local_counts[3]["hole_signatures"]=={"()":98,"(1,)":1}
assert len(hole_examples)==1

hole=hole_examples[0]
hp=tuple(hole["holes"][0][0])
S0={(x-hp[0],y-hp[1]) for x,y in hole["defects"]}
assert S0=={(-1,1),(1,-1),(1,1)}
R0=set().union(*(D(s) for s in S0))
assert neigh((0,0)) <= R0

def possible_centers_covering_node(p):
    x,y=p
    return {(x,y),(x+1,y),(x,y+1)}

def closure_centers(S):
    R=set().union(*(D(s) for s in S))
    cand=set().union(*(possible_centers_covering_node(p) for p in R))
    return {v for v in cand if D(v)<=R}

assert closure_centers(S0)==S0

target=D((0,0))
cand=set().union(*(possible_centers_covering_node(p) for p in target))
cand.discard((0,0))
iso_cover_counts={}
iso_triples=[]
for k in (1,2,3):
    sol=[]
    for C in combinations(sorted(cand),k):
        U=set().union(*(D(s) for s in C))
        if target<=U:
            sol.append(set(C))
    iso_cover_counts[k]=len(sol)
    if k==3:
        iso_triples=sol
assert iso_cover_counts=={1:0,2:0,3:8}
for S in iso_triples:
    assert closure_centers(S)-S=={(0,0)}
    holes,_=bounded_holes(S)
    assert not holes

def modp(p,L):
    return (p[0]%L,p[1]%L)

def torus_D(s,L):
    x,y=s
    return {modp((x,y),L),modp((x-1,y),L),modp((x,y-1),L)}

def torus_neigh(p,L):
    x,y=p
    return {modp((x+dx,y+dy),L) for dx,dy in DIRS}

def torus_components(nodes,L):
    rem=set(nodes); out=[]
    while rem:
        s=next(iter(rem)); rem.remove(s)
        c={s}; stack=[s]
        while stack:
            u=stack.pop()
            for v in torus_neigh(u,L):
                if v in rem:
                    rem.remove(v); c.add(v); stack.append(v)
        out.append(c)
    return out

def equality_tail_for_S(S,L):
    V={(i,j) for i in range(L) for j in range(L)}
    R=set().union(*(torus_D(s,L) for s in S)) if S else set()
    surv=V-R
    pcs=torus_components(surv,L)
    O=V-set(S)
    adj={v:set() for v in O}
    for i,j in surv:
        T={modp((i,j),L),modp((i+1,j),L),modp((i,j+1),L)}
        assert T.isdisjoint(S)
        a,b,c=tuple(T)
        adj[a].update((b,c)); adj[b].update((a,c)); adj[c].update((a,b))
    rem=set(O); ecs=[]
    while rem:
        s=next(iter(rem)); rem.remove(s)
        c={s}; stack=[s]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v in rem:
                    rem.remove(v); c.add(v); stack.append(v)
        ecs.append(c)
    sizes=sorted((len(c) for c in ecs),reverse=True)
    tail=tuple(sorted(sizes[1:], reverse=True))
    return tuple(sorted((len(c) for c in pcs),reverse=True)),tail

L=7
V7=[(i,j) for i in range(L) for j in range(L)]
tail_hist=Counter()
max_tail_mass=0
for k in range(4):
    for C in combinations(V7,k):
        _,tail=equality_tail_for_S(set(C),L)
        tail_hist[tail]+=1
        max_tail_mass=max(max_tail_mass,sum(tail))
assert max_tail_mass<=3
assert set(tail_hist)<={(),(1,),(3,)}

out={
    "status":"PASS_THREE_DEFECT_TORUS_PROPAGATION_LOCAL_CERTIFICATE",
    "infinite_local_deleted_cluster_classification":local_counts,
    "unique_singleton_plaquette_hole":{
        "normalized_defects":sorted(S0),
        "extra_isolated_ordinary_vertices":0,
    },
    "isolated_ordinary_coordinate":{
        "minimum_defects":3,
        "normalized_three_defect_cover_count":len(iso_triples),
        "maximum_extra_isolated_coordinates_with_three_defects":1,
        "coexists_with_singleton_plaquette_hole":False,
    },
    "L7_exhaustive":{
        "defect_subsets_checked":sum(1 for k in range(4) for _ in combinations(V7,k)),
        "equality_tail_histogram":{str(k):v for k,v in sorted(tail_hist.items())},
        "max_secondary_ordinary_mass":max_tail_mass,
    },
    "theorem_boundary":{
        "local_certificate":"EXACT_FINITE",
        "global_lifting_argument":"PROOF_ARTIFACT",
        "mersenne_L":"2^k-1, k>=3",
        "minority_ordinary_bound":"<=|S|+3<=6",
        "full_small_separation_side_bound":"<=7 including f",
    },
}
print(json.dumps(out,sort_keys=True))
