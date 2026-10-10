#!/usr/bin/env python3
"""Finite controls for NM-0022 conflict-graph obstruction theorem."""
from __future__ import annotations
from itertools import combinations, product
import json

def conflict_graph(clauses, n):
    adj=[set() for _ in range(n)]
    for C in clauses:
        assert len(C)==3
        for a,b in combinations(sorted(C),2):
            adj[a].add(b); adj[b].add(a)
    return adj

def alpha_bruteforce(adj):
    n=len(adj); best=()
    for mask in range(1<<n):
        if mask.bit_count()<=len(best): continue
        ok=True
        for i in range(n):
            if not (mask>>i)&1: continue
            if any((mask>>j)&1 for j in adj[i]):
                ok=False; break
        if ok: best=tuple(i for i in range(n) if (mask>>i)&1)
    return best

def sat_exact_one(clauses,n):
    out=[]
    for bits in product((0,1),repeat=n):
        if all(sum(bits[v] for v in C)==1 for C in clauses):
            out.append(bits)
    return out

def degrees_in_clauses(clauses,n):
    d=[0]*n
    for C in clauses:
        for v in C:d[v]+=1
    return d

# SAT cubic control: I + shift_1 + shift_2 on Z_6.
n=6
clauses6=[{i,(i+1)%n,(i+2)%n} for i in range(n)]
assert degrees_in_clauses(clauses6,n)==[3]*n
adj6=conflict_graph(clauses6,n)
assert max(map(len,adj6))<=6
sol6=sat_exact_one(clauses6,n)
a6=alpha_bruteforce(adj6)
assert len(a6)==n//3
assert len(sol6)==3

# Exact cubic UNSAT control whose conflict graph is the 9-antihole.
clauses9=[
    {0,3,7},{0,2,5},{1,5,7},{0,4,6},{2,4,7},
    {2,6,8},{1,3,6},{1,4,8},{3,5,8},
]
n=9
assert degrees_in_clauses(clauses9,n)==[3]*n
adj9=conflict_graph(clauses9,n)
for i in range(n):
    expected=set(range(n))-{i,(i-1)%n,(i+1)%n}
    assert adj9[i]==expected
assert all(len(x)==6 for x in adj9)
a9=alpha_bruteforce(adj9)
assert len(a9)==2
assert not sat_exact_one(clauses9,n)

# In an induced l-antihole every vertex has l-3 internal neighbors.
anti_degrees={l:l-3 for l in (5,7,9,11,13)}
assert [l for l,d in anti_degrees.items() if d<=6]==[5,7,9]

out={
 "status":"PASS_CUBIC_CONFLICT_GRAPH_OBSTRUCTION_CONTROLS",
 "sat_control":{"n":6,"alpha":len(a6),"target":2,"solutions":len(sol6)},
 "antihole9_control":{"n":9,"alpha":len(a9),"target":3,"exact_one_solutions":0},
 "max_conflict_degree":6,
 "odd_antihole_lengths_allowed_by_degree6":[5,7,9],
 "theorem_boundary":{
   "perfect_conflict_graph":"POLYNOMIAL_SOURCE_BOUND_ISLAND",
   "imperfect_obstruction":"ODD_HOLE_OR_ODD_ANTIHole",
   "unbounded_obstruction_type":"ODD_HOLE_ONLY",
   "general_solver":"OPEN",
   "P_VS_NP":"OPEN",
 }
}
print(json.dumps(out,sort_keys=True))
