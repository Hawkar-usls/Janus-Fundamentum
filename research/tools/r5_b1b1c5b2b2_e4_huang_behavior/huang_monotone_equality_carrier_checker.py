#!/usr/bin/env python3
from itertools import product
import hashlib, json

C_POS=(0,2,4)
U_POS=(1,3,5,6)
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
    rel=set(); witness={}
    for cols,bi in FULL:
        if all(cols[p]==c for p,c in pre.items()):
            rel.add(bi); witness.setdefault(bi,cols)
    return rel,witness

def relation_independent(pre):
    rel=set(); witness={}
    for bi,b in enumerate(BOUNDARIES):
        dom=[]
        for p in range(7):
            if p in pre: dom.append((pre[p],))
            elif p in C_POS: dom.append((1,2,3,4))
            else: dom.append((3,4))
        a=[None]*7
        def dfs(p):
            if p==7:
                if a[6]==a[0]: return None
                for t,cp in enumerate(C_POS):
                    if a[cp] in (b[2*t],b[2*t+1]): return None
                return tuple(a)
            for c in dom[p]:
                if p>0 and a[p-1]==c: continue
                if p==6 and a[0]==c: continue
                a[p]=c
                if p in C_POS:
                    t=C_POS.index(p)
                    if c in (b[2*t],b[2*t+1]): continue
                got=dfs(p+1)
                if got is not None: return got
            a[p]=None
            return None
        got=dfs(0)
        if got is not None:
            rel.add(bi); witness[bi]=got
    return rel,witness

def factor(rel):
    S=[]
    for bi in rel:
        b=BOUNDARIES[bi]
        S.append(tuple(pair_code(b[2*t],b[2*t+1]) for t in range(3)))
    U=[set() for _ in range(3)]
    M=set()
    for s in S:
        for t in range(3): U[t].add(s[t])
        M.add(tuple(eqbit(s[t]) for t in range(3)))
    recon=set()
    for s in product(*(sorted(u) for u in U)):
        e=tuple(eqbit(s[t]) for t in range(3))
        if e in M:
            b=[]
            for q in s: b.extend(PAIR_STATES[q])
            recon.add(BOUNDARIES.index(tuple(b)))
    return U,M,recon

def upward(M):
    for e in M:
        for f in product((0,1),repeat=3):
            if all(f[i]>=e[i] for i in range(3)) and f not in M:
                return False
    return True

choices=[(None,1,2,3,4) if p in C_POS else (None,3,4) for p in range(7)]
extendable=0
rels={}
Ms=set()
for sel in product(*choices):
    pre={p:c for p,c in enumerate(sel) if c is not None}
    rc,wc=relation_candidate(pre)
    ri,wi=relation_independent(pre)
    assert rc==ri
    if not rc: continue
    extendable += 1
    U,M,recon=factor(rc)
    assert recon==rc
    assert upward(M)
    assert set(wc)==rc and set(wi)==ri
    rels.setdefault(tuple(sorted(rc)),(tuple(tuple(sorted(x)) for x in U),tuple(sorted(M))))
    Ms.add(tuple(sorted(M)))

root,_=relation_candidate({})
_,rootM,_=factor(root)
assert rootM == set(product((0,1),repeat=3)) - {(0,0,0)}

def carrier_feasible(keys):
    D=[set(range(4)) for _ in range(3)]
    MM=[]
    for key in keys:
        U,M,_=factor(set(key))
        for t in range(3): D[t] &= U[t]
        MM.append(M)
    if any(not d for d in D): return False
    emax=tuple(1 if any(eqbit(q) for q in d) else 0 for d in D)
    return all(emax in M for M in MM)

def brute_feasible(keys):
    Rs=[set(k) for k in keys]
    for s in product(range(4),repeat=3):
        b=[]
        for q in s: b.extend(PAIR_STATES[q])
        bi=BOUNDARIES.index(tuple(b))
        if all(bi in R for R in Rs): return True
    return False

keys=list(rels)
for a in keys:
    for b in keys:
        assert carrier_feasible((a,b)) == brute_feasible((a,b))

rows=[{"R":list(k),"U":[list(x) for x in v[0]],"M":[list(x) for x in v[1]]}
      for k,v in sorted(rels.items())]
digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()

print(json.dumps({
  "partial_precolorings_total":5**3*3**4,
  "extendable_partial_precolorings":extendable,
  "distinct_boundary_relations":len(rels),
  "distinct_upward_equality_relations":len(Ms),
  "all_relations_factor_unary_x_upward_eq":True,
  "candidate_vs_independent_relation_agreement":True,
  "root_relation":"e1 OR e2 OR e3",
  "two_relation_global_composition_exhaustive":"PASS",
  "catalog_sha256":digest,
  "status":"PASS_FINITE_LOCAL_CATALOG_AND_GLOBAL_SANITY"
},sort_keys=True,indent=2))
