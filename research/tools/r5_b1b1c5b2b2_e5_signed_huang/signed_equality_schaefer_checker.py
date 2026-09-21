#!/usr/bin/env python3
"""
E5 signed-Huang equality/Schaefer classification checker.

Rebuilds the E4 local C7 catalog, projects each local relation to its
3 equality bits q, applies every occurrence-polarity flip q=e xor sigma,
deduplicates the signed language, and classifies it under the six frozen
Boolean Schaefer predicates.

Also verifies the source identity:
- positive literal occurrence: q=e
- negative literal occurrence: q=1-e
because x_i and ~x_i are adjacent and permanently restricted to colors {1,2}.

Expected authoritative facts:
- 14 unsigned upward equality relations from E4;
- 70 distinct signed relations after all coordinate flips;
- the full signed language is in none of:
  0-valid, 1-valid, Horn, dual-Horn, bijunctive, affine;
- already the 8 signed variants of root OR3 are in none of the six classes.

This is a relation-classification checker only. Any NP-completeness
consequence is source-bound to Schaefer's dichotomy and does not prove P!=NP.
"""
from itertools import product
import hashlib, json

C_POS=(0,2,4)
PAIR_STATES=((1,1),(1,2),(2,1),(2,2))
BOUNDARIES=list(product((1,2), repeat=6))

def cycle_proper(cols):
    return all(cols[i] != cols[(i+1)%7] for i in range(7))

def boundary_ok(cols,b):
    return all(cols[p] not in (b[2*t],b[2*t+1]) for t,p in enumerate(C_POS))

FULL=[]
for cols in product((1,2,3,4),(3,4),(1,2,3,4),(3,4),(1,2,3,4),(3,4),(3,4)):
    if not cycle_proper(cols):
        continue
    for bi,b in enumerate(BOUNDARIES):
        if boundary_ok(cols,b):
            FULL.append((cols,bi))

def pair_code(x,d):
    return PAIR_STATES.index((x,d))

def eqbit(q):
    x,d=PAIR_STATES[q]
    return int(x==d)

def relation_candidate(pre):
    rel=set()
    for cols,bi in FULL:
        if all(cols[p]==c for p,c in pre.items()):
            rel.add(bi)
    return rel

def factor(rel):
    S=[]
    for bi in rel:
        b=BOUNDARIES[bi]
        S.append(tuple(pair_code(b[2*t],b[2*t+1]) for t in range(3)))
    U=[set() for _ in range(3)]
    M=set()
    for s in S:
        for t in range(3):
            U[t].add(s[t])
        M.add(tuple(eqbit(s[t]) for t in range(3)))
    return U,M

choices=[(None,1,2,3,4) if p in C_POS else (None,3,4) for p in range(7)]
Ms=set()
for sel in product(*choices):
    pre={p:c for p,c in enumerate(sel) if c is not None}
    rel=relation_candidate(pre)
    if not rel:
        continue
    _,M=factor(rel)
    Ms.add(tuple(sorted(M)))

def flip_relation(M,mask):
    M=set(M)
    out=set()
    for e in product((0,1),repeat=3):
        q=tuple(e[i]^((mask>>i)&1) for i in range(3))
        if q in M:
            out.add(e)
    return frozenset(out)

SIGNED=set()
for M in Ms:
    for mask in range(8):
        SIGNED.add(tuple(sorted(flip_relation(M,mask))))

def cb(a,b,f):
    return tuple(f(x,y) for x,y in zip(a,b))

def ct(a,b,c,f):
    return tuple(f(x,y,z) for x,y,z in zip(a,b,c))

def closed_binary(R,f):
    return all(cb(a,b,f) in R for a in R for b in R)

def closed_ternary(R,f):
    return all(ct(a,b,c,f) in R for a in R for b in R for c in R)

def maj(x,y,z):
    return (x&y)|(x&z)|(y&z)

def minority(x,y,z):
    return x^y^z

def classify(language):
    L=[set(r) for r in language]
    return {
      "0_valid": all((0,0,0) in R for R in L),
      "1_valid": all((1,1,1) in R for R in L),
      "horn": all(closed_binary(R,lambda x,y:x&y) for R in L),
      "dual_horn": all(closed_binary(R,lambda x,y:x|y) for R in L),
      "bijunctive": all(closed_ternary(R,maj) for R in L),
      "affine": all(closed_ternary(R,minority) for R in L),
    }

# Source polarity identity on binary pair states.
polarity_identity=[]
for x,d in PAIR_STATES:
    e=int(x==d)
    xbar=3-x  # on palette {1,2}
    q_pos=int(x==d)
    q_neg=int(xbar==d)
    assert q_pos==e
    assert q_neg==1-e
    polarity_identity.append((x,d,e,q_pos,q_neg))

root=set(product((0,1),repeat=3))-{(0,0,0)}
ROOT_SIGNED={tuple(sorted(flip_relation(root,m))) for m in range(8)}

full_class=classify(SIGNED)
root_class=classify(ROOT_SIGNED)
assert len(Ms)==14
assert len(SIGNED)==70
assert len(ROOT_SIGNED)==8
assert not any(full_class.values())
assert not any(root_class.values())

rows=[{"relation":["".join(map(str,t)) for t in r]} for r in sorted(SIGNED)]
digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()

print(json.dumps({
  "unsigned_E4_equality_relations":len(Ms),
  "distinct_signed_relations":len(SIGNED),
  "signed_root_OR3_relations":len(ROOT_SIGNED),
  "source_polarity_identity":"PASS",
  "full_signed_language_classification":full_class,
  "root_signed_OR3_classification":root_class,
  "no_common_schaefer_basis_full":not any(full_class.values()),
  "no_common_schaefer_basis_root_signed_OR3":not any(root_class.values()),
  "signed_catalog_sha256":digest,
  "status":"PASS_SIGNED_RELATION_CLASSIFICATION"
},sort_keys=True,indent=2))
