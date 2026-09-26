#!/usr/bin/env python3
"""Exact finite controls for NM-0023 odd-hole coverage selector conservation."""
from __future__ import annotations
from itertools import product
import json

EX1={(1,0,0),(0,1,0),(0,0,1)}

# Canonical one-edge boundary relation after eliminating a hole variable in
# favor of the coverage bit d=1-v of its third occurrence clause.
R=set()
for d0,d1,c in product((0,1), repeat=3):
    if d0+d1 == 1+c:
        R.add((d0,d1,c))
assert R=={(0,1,0),(1,0,0),(1,1,1)}

# Complement the two d coordinates.  The relation is exactly EX1_3.
R_comp={(1-d0,1-d1,c) for d0,d1,c in R}
assert R_comp==EX1

def belt_projection(k:int):
    """Allowed (d,c) tuples after existentially eliminating v from an
    induced-hole clause belt plus equations d_i=1-v_i.
    """
    assert k>=5 and k%2==1
    out=set()
    for d in product((0,1), repeat=k):
        v=tuple(1-x for x in d)
        for c in product((0,1), repeat=k):
            if all(v[i]+v[(i+1)%k]+c[i]==1 for i in range(k)):
                out.add(d+c)
    return out

def ex1_belt(k:int):
    out=set()
    for d in product((0,1), repeat=k):
        u=tuple(1-x for x in d)
        for c in product((0,1), repeat=k):
            if all((u[i],u[(i+1)%k],c[i]) in EX1 for i in range(k)):
                out.add(d+c)
    return out

controls={}
for k in (5,7):
    a=belt_projection(k)
    b=ex1_belt(k)
    assert a==b
    controls[str(k)]={"boundary_tuples":len(a),"same_as_exact_one_belt":True}

# The map d <-> v is a coordinatewise bijection, hence this summary retains
# one Boolean degree of freedom per hole vertex before any extra aliasing /
# boundary constraints from the rest of the cubic instance are used.
for k in (5,7,9):
    assert len({tuple(1-x for x in d) for d in product((0,1),repeat=k)})==2**k

out={
  "status":"PASS_ODD_HOLE_COVERAGE_SELECTOR_CONSERVATION",
  "single_edge_relation":{
    "coverage_relation":sorted(R),
    "after_complement":sorted(R_comp),
    "equals_exact_one_3":True,
  },
  "odd_belt_controls":controls,
  "theorem":{
    "summary_map":"d_i=1-v_i",
    "state_count_before_extra_constraints":"2^k",
    "local_boundary_relation":"EXACT_ONE_3_AFTER_COMPLEMENT",
    "naive_one_coverage_bit_per_hole_vertex":"NO_BOOLEAN_DIMENSION_REDUCTION",
  },
  "scope":{
    "general_grouped_odd_hole_contraction":"OPEN",
    "P_VS_NP":"OPEN",
    "P_EQ_NP":"NOT_PROVED",
  },
}
print(json.dumps(out,sort_keys=True))
