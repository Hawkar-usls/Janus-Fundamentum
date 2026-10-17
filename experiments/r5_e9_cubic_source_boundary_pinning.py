#!/usr/bin/env python3
"""Exact controls for NM-0025 cubic source-valid boundary pinning."""
from __future__ import annotations
from itertools import product
import json

# Boundary vertices are 0,1,2. Internal vertices start at 3.
CANONICAL = {
    (0,0,0): (
        (0,1,3),
        (0,2,3),
        (1,2,3),
    ),
    (0,1,1): (
        (0,1,3),
        (0,2,4),
        (1,3,4),
        (2,3,4),
    ),
    (0,0,1): (
        (0,2,3),
        (0,4,5),
        (1,2,3),
        (1,4,5),
        (3,4,5),
    ),
    (1,1,1): (
        (0,3,4),
        (0,3,5),
        (1,3,6),
        (1,4,5),
        (2,4,6),
        (2,5,6),
    ),
}

def projected_relation(edges):
    n=1+max(max(e) for e in edges)
    out=set()
    for a in product((0,1), repeat=n):
        if all(sum(a[v] for v in e)==1 for e in edges):
            out.add(a[:3])
    return out

def degree_profile(edges):
    n=1+max(max(e) for e in edges)
    d=[0]*n
    for e in edges:
        assert len(e)==3 and len(set(e))==3
        for v in e:
            d[v]+=1
    return d

def gadget_for(target):
    target=tuple(target)
    w=sum(target)
    if w==0:
        canon=(0,0,0)
        perm=(0,1,2)
    elif w==3:
        canon=(1,1,1)
        perm=(0,1,2)
    elif w==1:
        canon=(0,0,1)
        one=target.index(1)
        zeros=[i for i,x in enumerate(target) if x==0]
        perm=(zeros[0],zeros[1],one)
    elif w==2:
        canon=(0,1,1)
        zero=target.index(0)
        ones=[i for i,x in enumerate(target) if x==1]
        perm=(zero,ones[0],ones[1])
    else:
        raise AssertionError
    edges=[]
    for e in CANONICAL[canon]:
        edges.append(tuple(perm[v] if v<3 else v for v in e))
    return tuple(edges)

controls={}
for target in product((0,1), repeat=3):
    edges=gadget_for(target)
    rel=projected_relation(edges)
    deg=degree_profile(edges)
    assert rel=={target}
    assert deg[:3]==[2,2,2]
    assert all(x==3 for x in deg[3:])
    assert len(edges)==len(set(tuple(sorted(e)) for e in edges))
    controls["".join(map(str,target))]={
        "clauses":[list(e) for e in edges],
        "internal_variables":len(deg)-3,
        "projected_relation":["".join(map(str,next(iter(rel))))],
        "boundary_degrees":deg[:3],
        "internal_degrees":deg[3:],
    }

# Composition bookkeeping: a full odd-hole boundary has 3k exposed variables,
# each already used once by the source block. Partition into triples. Each pin
# contributes exactly two more occurrences to every old boundary variable.
for k in (5,7,9):
    B=3*k
    for bits in (
        tuple(0 for _ in range(B)),
        tuple((i*7+3)%2 for i in range(B)),
        tuple(1 for _ in range(B)),
    ):
        boundary_deg=[0]*B
        internal_degs=[]
        for g in range(k):
            target=bits[3*g:3*g+3]
            edges=gadget_for(target)
            d=degree_profile(edges)
            for q in range(3):
                boundary_deg[3*g+q]+=d[q]
            internal_degs.extend(d[3:])
        assert boundary_deg==[2]*B
        assert all(d==3 for d in internal_degs)
        # After gluing to the odd-hole block, every exposed variable has total
        # source degree 1+2=3.
        assert all(1+d==3 for d in boundary_deg)

out={
  "status":"PASS_CUBIC_SOURCE_BOUNDARY_PINNING",
  "all_eight_three_bit_patterns":controls,
  "theorem":{
    "boundary_gadget_degree":2,
    "internal_degree":3,
    "clause_arity":3,
    "positive_exact_one_only":True,
    "all_8_singleton_patterns":True,
    "arbitrary_3k_boundary_assignment":"PIN_BY_DISJOINT_TRIPLE_COMPOSITION",
    "old_boundary_total_degree_after_gluing":"1+2=3",
  },
  "scope":{
    "source_valid_cubic_positive_exact_one_context":True,
    "preserves_every_current_residual_preprocessor_promise":False,
    "context_independent_hole_state_merge":"BLOCKED_AS_UNIVERSAL_SOURCE_REDUCTION",
    "instance_specific_contextual_dominance":"OPEN",
    "D1":"EMPTY",
    "P_VS_NP":"OPEN",
    "P_EQ_NP":"NOT_PROVED",
  }
}
print(json.dumps(out,sort_keys=True))
