#!/usr/bin/env python3
"""Provider replay for C025-E2R-L1G-F1 finite expansion mechanics."""
from dataclasses import dataclass
from itertools import product
from math import factorial, log

Clause=frozenset[int]

@dataclass(frozen=True)
class Gate:
    var:int
    left:int
    right:int

def or_cnf(a:set[Clause],b:set[Clause])->set[Clause]:
    out=set()
    for x in a:
        for y in b:
            c=frozenset(x|y)
            if not any(-z in c for z in c): out.add(c)
    return out

def exact_expansions(local_atoms:set[int],gates:list[Gate]):
    pos={v:{frozenset({v})} for v in local_atoms}
    neg={v:{frozenset({-v})} for v in local_atoms}
    qe={v:frozenset() for v in local_atoms}; known=set(local_atoms)
    for g in gates:
        assert g.var not in known
        assert abs(g.left) in known and abs(g.right) in known
        E=lambda lit: pos[abs(lit)] if lit>0 else neg[abs(lit)]
        EN=lambda lit: neg[abs(lit)] if lit>0 else pos[abs(lit)]
        pos[g.var]=set(E(g.left))|set(E(g.right))
        neg[g.var]=or_cnf(set(EN(g.left)),set(EN(g.right)))
        edges=set()
        for lit in (g.left,g.right):
            u=abs(lit)
            if u not in local_atoms:
                edges.update(qe[u])
                if lit<0: edges.add((g.var,u))
        qe[g.var]=frozenset(edges); known.add(g.var)
    return pos,neg,qe

def within_factorial_bound(count:int,S:int,q:int)->bool:
    if count<=1: return True
    return log(count) <= factorial(q+2)*log(S) + 1e-12

def parity_b2(n):
    gates=[]; y=1; nxt=n+1
    for x in range(2,n+1):
        t1,t2,yp=nxt,nxt+1,nxt+2; nxt+=3
        gates += [Gate(t1,y,x),Gate(t2,-y,-x),Gate(yp,-t1,-t2)]
        y=yp
    return gates,y

def main():
    locals_={1,2,3,4}
    for s12,s23 in product((-1,1),repeat=2):
        gs=[Gate(5,1,-2),Gate(6,s12*5,3),Gate(7,s23*6,-4)]
        pos,neg,qe=exact_expansions(locals_,gs); S=len(locals_)+3*len(gs)
        for v in (5,6,7):
            q=len(qe[v]); assert within_factorial_bound(len(pos[v]),S,q); assert within_factorial_bound(len(neg[v]),S,q)
    gs=[Gate(6,1,-2),Gate(7,6,3),Gate(8,7,-4),Gate(9,8,5)]
    pos,neg,qe=exact_expansions({1,2,3,4,5},gs)
    assert len(qe[9])==0 and len(pos[9])==5 and len(neg[9])==1
    for n in range(2,8):
        gs,out=parity_b2(n); pos,neg,qe=exact_expansions(set(range(1,n+1)),gs)
        q=len(qe[out]); S=n+3*len(gs)
        assert q==3*n-4 and len(pos[out])==2**(n-1)
        assert within_factorial_bound(len(pos[out]),S,q)
        assert within_factorial_bound(len(neg[out]),S,q)
    print("C025_E2R_L1G_F1_NEGATIVE_EDGE_ACCOUNTING = PASS")
    print("C025_E2R_L1G_F1_Q0_MONOTONE_EXPANSION = PASS")
    print("C025_E2R_L1G_F1_FACTORIAL_EXPANSION_BOUND_FINITE = PASS")
    print("C025_E2R_L1G_F1_BOUND_MATERIALIZATION_AVOIDED = PASS")
    print("C025_E2R_L1G_F1_PARITY_NEGATIVE_EDGE_GROWTH = PASS")
    print("claim_boundary = formula-representation mechanics only; proof-level macro-cut elimination handled separately")

if __name__=="__main__": main()
