#!/usr/bin/env python3
"""Exact finite-field checks for the frozen q=4 Morgenstern family constants."""
import json
from pathlib import Path

# F4 = F2[a]/(a^2+a+1), integer bits encode u+v*a.
def a4(x,y): return x ^ y
def m4(x,y):
    x0,x1=x&1,(x>>1)&1; y0,y1=y&1,(y>>1)&1
    return ((x0*y0)^(x1*y1)) | (((x0*y1)^(x1*y0)^(x1*y1))<<1)
def p4(x,n):
    r=1
    while n:
        if n&1: r=m4(r,x)
        x=m4(x,x); n//=2
    return r
def i4(x):
    assert x != 0
    return p4(x,2)

epsilon=2  # a
assert all(a4(a4(m4(x,x),x),epsilon) != 0 for x in range(4))

# F16 = F4[y]/(y^2+y+epsilon), integer encodes u+4*v*y.
def a16(x,y): return x ^ y
def m16(x,y):
    u,v=x&3,(x>>2)&3; s,t=y&3,(y>>2)&3
    vt=m4(v,t)
    c0=a4(m4(u,s),m4(vt,epsilon))
    c1=a4(a4(m4(u,t),m4(v,s)),vt)
    return c0 | (c1<<2)
def p16(x,n):
    r=1
    while n:
        if n&1: r=m16(r,x)
        x=m16(x,x); n//=2
    return r

alpha=4  # y
assert a16(a16(m16(alpha,alpha),alpha),epsilon)==0

valid=[]
for b1 in range(4):
    for b2 in range(1,4):
        inv=i4(b2)
        z1=m16(a16(alpha,b1),inv)
        z2=m16(a16(a16(alpha,b1),1),inv)
        if p16(z1,5)!=1 and p16(z2,5)!=1:
            valid.append((b1,b2,z1,z2))
assert valid
assert valid[0][:2] == (0,1)

pairs=[]
for gamma in range(4):
    for delta in range(4):
        lhs=a4(a4(m4(gamma,gamma),m4(gamma,delta)),m4(m4(delta,delta),epsilon))
        if lhs==1:
            pairs.append((gamma,delta))
assert pairs == [(0,2),(1,0),(1,3),(2,2),(2,3)]
assert len(set(pairs)) == 5
assert (0,0) not in pairs
result={
  "artifact_id":"C023R-Q4-MORGENSTERN-CONSTANT-BINDING-CHECK-v1.0",
  "field":"F4=F2[a]/(a^2+a+1)",
  "epsilon":"a",
  "b1":0,
  "b2":1,
  "alpha_and_alpha_plus_one_non_cubes":True,
  "all_valid_b1_b2_encoded":valid,
  "generator_pairs_encoded":pairs,
  "generator_pair_count":len(pairs),
  "method":"EXACT_FINITE_FIELD_ENUMERATION__NO_HEURISTICS",
  "asymptotic_claim":"NONE_FROM_FINITE_CHECK"
}
out=Path(__file__).with_name("EXPLICIT_EXPANDER_CONSTANT_CHECK_v1.0.json")
out.write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps(result,indent=2))
