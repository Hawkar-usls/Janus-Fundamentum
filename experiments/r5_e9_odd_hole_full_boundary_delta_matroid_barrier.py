#!/usr/bin/env python3
"""Exact finite controls for NM-0024 full odd-hole boundary delta-matroid barrier."""
from __future__ import annotations
from itertools import product
import json

def boundary_from_internal(v):
    k=len(v)
    w=tuple(1-v[i]-v[(i+1)%k] for i in range(k))
    assert all(x in (0,1) for x in w)
    a=tuple(0 for _ in range(k))
    b=tuple(1-v[i] for i in range(k))
    return w+a+b

def feasible(boundary,k):
    w=boundary[:k]
    a=boundary[k:2*k]
    b=boundary[2*k:]
    for v in product((0,1),repeat=k):
        if all(v[i]+v[(i+1)%k]+w[i]==1 for i in range(k)) and \
           all(v[i]+a[i]+b[i]==1 for i in range(k)):
            return True
    return False

def support(bits):
    return frozenset(i for i,x in enumerate(bits) if x)

def toggle(X,e,f):
    z=set(X)
    if e==f:
        if e in z: z.remove(e)
        else: z.add(e)
    else:
        for t in (e,f):
            if t in z: z.remove(t)
            else: z.add(t)
    return frozenset(z)

def bits_from_support(S,n):
    return tuple(1 if i in S else 0 for i in range(n))

def witness(k):
    assert k>=5 and k%2==1
    j=k-1
    vx=(0,)*k
    vy=tuple(1 if i==j else 0 for i in range(k))
    Xbits=boundary_from_internal(vx)
    Ybits=boundary_from_internal(vy)
    X=support(Xbits); Y=support(Ybits)
    names=[f"w{i}" for i in range(k)]+[f"a{i}" for i in range(k)]+[f"b{i}" for i in range(k)]
    expected={j-1,j,2*k+j}
    D=X^Y
    assert D==expected
    assert feasible(Xbits,k) and feasible(Ybits,k)
    e=j-1
    exchange={}
    for f in sorted(D):
        Z=toggle(X,e,f)
        ok=feasible(bits_from_support(Z,3*k),k)
        exchange[names[f]]=ok
        assert not ok
    return {
        "j":j,
        "X_weight":len(X),
        "Y_weight":len(Y),
        "parity_X":len(X)%2,
        "parity_Y":len(Y)%2,
        "symmetric_difference":[names[t] for t in sorted(D)],
        "chosen_e":names[e],
        "exchange_candidates":exchange,
        "delta_matroid_exchange":"FAIL",
    }

controls={str(k):witness(k) for k in (5,7,9)}

out={
  "status":"PASS_FULL_ODD_HOLE_BOUNDARY_NOT_DELTA_MATROID",
  "uniform_theorem":{
    "scope":"all odd k>=5",
    "X":"v=0, w=1, a=0, b=1",
    "Y":"one v_j=1; remove w_(j-1), w_j, b_j from X",
    "symmetric_difference":"{w_(j-1),w_j,b_j}",
    "exchange_witness_e":"w_(j-1)",
    "result":"no f in symmetric difference gives a feasible X delta {e,f}",
    "matching_realizable":"IMPOSSIBLE",
  },
  "finite_controls":controls,
  "scope":{
    "ordinary_matching_grouped_quotient":"BLOCKED_FOR_FULL_BOUNDARY",
    "general_nonmatching_grouped_quotient":"OPEN_REQUIRES_REAUDIT",
    "D1":"EMPTY",
    "P_VS_NP":"OPEN",
    "P_EQ_NP":"NOT_PROVED",
  }
}
print(json.dumps(out,sort_keys=True))
