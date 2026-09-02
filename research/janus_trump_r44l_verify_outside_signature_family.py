#!/usr/bin/env python3
import json

R={
    (0,0,1),(0,1,0),(0,1,1),
    (1,0,0),(1,0,1),(1,1,0)
}

and_w=((0,0,1),(0,1,0))
or_w=((1,0,1),(1,1,0))
maj_w=((0,0,1),(0,1,0),(1,0,0))
xor_w=((0,0,1),(0,1,0),(1,0,0))

bitand=lambda a,b: tuple(x&y for x,y in zip(a,b))
bitor=lambda a,b: tuple(x|y for x,y in zip(a,b))
majority=lambda a,b,c: tuple(1 if x+y+z>=2 else 0 for x,y,z in zip(a,b,c))
xor3=lambda a,b,c: tuple(x^y^z for x,y,z in zip(a,b,c))

assert and_w[0] in R and and_w[1] in R and bitand(*and_w) not in R
assert or_w[0] in R and or_w[1] in R and bitor(*or_w) not in R
assert all(x in R for x in maj_w) and majority(*maj_w) not in R
assert all(x in R for x in xor_w) and xor3(*xor_w) not in R

print(json.dumps({
  'gate_id':'R44L_OUTSIDE_COMPACT_SIGNATURE_FAMILY',
  'relation':'NAE3_BOUNDARY_RELATION',
  'horn_closed_under_and':False,
  'dual_horn_closed_under_or':False,
  'bijunctive_closed_under_majority':False,
  'affine_closed_under_xor3':False,
  'outside_current_R44K_portfolio':True,
  'hardness_claimed':False,
  'P_EQUALS_NP':'NOT_PROVED',
  'P_NE_NP':'NOT_PROVED',
  'P_VS_NP':'OPEN',
  'next_gate':'R44M_RELATION_LANGUAGE_DICHOTOMY_AND_REPRESENTATION_ESCAPE'
}, sort_keys=True))
