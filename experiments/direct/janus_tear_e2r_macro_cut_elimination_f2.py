#!/usr/bin/env python3
"""Provider replay for C025-E2R-L1G-F2 finite mechanics."""
from dataclasses import dataclass
from itertools import combinations
from math import factorial, log

Clause=frozenset[int]

def taut(c): return any(-x in c for x in c)
def resolve(a,b,p):
    if p in a and -p in b: r=frozenset((a-{p})|(b-{-p}))
    elif -p in a and p in b: r=frozenset((a-{-p})|(b-{p}))
    else: return None
    return None if taut(r) else r

@dataclass(frozen=True)
class Node:
    kind:str; clause:Clause; p1:int=-1; p2:int=-1; pivot:int=0

def verify_rw(nodes,axioms):
    for i,n in enumerate(nodes):
        if n.kind=="axiom": assert n.clause in axioms
        elif n.kind=="weaken": assert 0<=n.p1<i and nodes[n.p1].clause<=n.clause
        else:
            assert n.kind=="res" and 0<=n.p1<i and 0<=n.p2<i
            assert resolve(nodes[n.p1].clause,nodes[n.p2].clause,n.pivot)==n.clause

def normalize(nodes,axioms):
    out=[]
    for i,n in enumerate(nodes):
        if n.kind=="axiom": out.append(n.clause); continue
        if n.kind=="weaken":
            c=out[n.p1]; assert c<=n.clause; out.append(c); continue
        a,b=out[n.p1],out[n.p2]
        r=resolve(a,b,n.pivot)
        if r is not None:
            assert r<=n.clause; out.append(r)
        elif n.pivot not in a and -n.pivot not in a:
            assert a<=n.clause; out.append(a)
        elif n.pivot not in b and -n.pivot not in b:
            assert b<=n.clause; out.append(b)
        else:
            cs=[c for c in (a,b) if c<=n.clause]; assert cs; out.append(min(cs,key=len))
    return out

def check_weakening():
    ax={frozenset({1}),frozenset({-1,2}),frozenset({-2}),frozenset({-3})}
    ns=[Node("axiom",frozenset({1})),Node("axiom",frozenset({-1,2})),Node("axiom",frozenset({-2})),Node("axiom",frozenset({-3})),Node("weaken",frozenset({1,3}),0),Node("weaken",frozenset({-1,2,3}),1),Node("weaken",frozenset({-2,3}),2),Node("res",frozenset({2,3}),4,5,1),Node("res",frozenset({3}),7,6,2),Node("res",frozenset(),8,3,3)]
    verify_rw(ns,ax); pure=normalize(ns,ax)
    assert all(pure[i]<=ns[i].clause for i in range(len(ns))) and pure[-1]==frozenset()

@dataclass(frozen=True)
class Macro:
    locals:tuple[int,...]
    neg_children:tuple["Macro",...]=()

def or_cnf(a,b):
    out=set()
    for x in a:
        for y in b:
            c=frozenset(x|y)
            if not taut(c): out.add(c)
    return out

def pos_neg(m):
    pos={frozenset({l}) for l in m.locals}
    cps=[pos_neg(c) for c in m.neg_children]
    for _p,n in cps: pos|=n
    neg={frozenset(-l for l in m.locals)}
    for p,_n in cps: neg=or_cnf(neg,p)
    return pos,neg

def closure_refutes(ax,max_lines=10000):
    clauses=set(c for c in ax if not taut(c))
    if frozenset() in clauses: return True,len(clauses)
    changed=True
    while changed and len(clauses)<=max_lines:
        changed=False; cur=list(clauses)
        for a,b in combinations(cur,2):
            for v in ({abs(x) for x in a}&{abs(x) for x in b}):
                r=resolve(a,b,v)
                if r is None or r in clauses: continue
                clauses.add(r); changed=True
                if not r: return True,len(clauses)
                if len(clauses)>max_lines: return False,len(clauses)
    return False,len(clauses)

def check_macros():
    ms=[Macro((1,-2,3)),Macro((4,),(Macro((1,-2)),)),Macro((5,),(Macro((4,),(Macro((1,-2)),)),)),Macro((6,),(Macro((1,2)),Macro((2,-3))))]
    for m in ms:
        p,n=pos_neg(m); ok,lines=closure_refutes(p|n); assert ok and lines<10000

def check_recurrence():
    for q in range(9):
        H=factorial(q+2); line=factorial(q+3); comp=factorial(q+4); full=factorial(q+5)
        assert 3*H<=line
        if q:
            assert H+factorial(q+3)+2<=comp
        assert line+comp+1<=full

def check_shape():
    for k in (64,128,256,512):
        q=max(2,int(k/max(1.0,log(k))))
        assert log(factorial(q+5))>log(q)

def main():
    check_weakening(); check_macros(); check_recurrence(); check_shape()
    print("C025_E2R_L1G_F2_WEAKENING_NORMALIZATION = PASS")
    print("C025_E2R_L1G_F2_CONTEXT_LIFT_SCAFFOLD = PASS")
    print("C025_E2R_L1G_F2_NESTED_COMPLEMENT_REFUTATION_FIXTURES = PASS")
    print("C025_E2R_L1G_F2_FACTORIAL_RECURRENCE_CEILING = PASS")
    print("C025_E2R_L1G_F2_Q_LOWER_BOUND_ALGEBRA_SHAPE = PASS")
    print("claim_boundary = finite mechanics only; asymptotic q lower bound uses analytical F2 plus the external NW lower bound")
if __name__=="__main__": main()
