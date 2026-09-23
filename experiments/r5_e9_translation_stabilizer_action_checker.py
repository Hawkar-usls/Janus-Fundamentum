#!/usr/bin/env python3
"""Exact checks for the JANUS translation-stabilizer repair-action calculus."""

from itertools import product

def xor(a,b):
    return tuple(x^y for x,y in zip(a,b))

def stabilizer(rel,k):
    R=set(rel)
    out=[]
    for h in product((0,1), repeat=k):
        if {xor(a,h) for a in R} == R:
            out.append(h)
    return set(out)

def span(basis):
    out={(0,)*len(basis[0])} if basis else {()}
    for b in basis:
        out |= {xor(x,b) for x in tuple(out)}
    return out

def nae3_rel():
    return [a for a in product((0,1), repeat=3) if len(set(a))>1]

def or3_rel():
    return [a for a in product((0,1), repeat=3) if any(a)]

def eq2_rel():
    return [(0,0),(1,1)]

def xor0_rel(k):
    return [a for a in product((0,1), repeat=k) if sum(a)%2==0]

def models_nae(n,edges):
    return {
        a for a in product((0,1), repeat=n)
        if all(len({a[i] for i in e})>1 for e in edges)
    }

def global_nae_masks(n,edges):
    H=[]
    local=stabilizer(nae3_rel(),3)
    for h in product((0,1), repeat=n):
        if all(tuple(h[i] for i in e) in local for e in edges):
            H.append(h)
    return set(H)

def main():
    assert stabilizer(or3_rel(),3)=={(0,0,0)}
    assert stabilizer(nae3_rel(),3)=={(0,0,0),(1,1,1)}
    assert stabilizer(eq2_rel(),2)=={(0,0),(1,1)}
    assert stabilizer(xor0_rel(3),3)=={
        (0,0,0),(0,1,1),(1,0,1),(1,1,0)
    }

    # Connected NAE hypergraph => only identity/global complement translations.
    edges=((0,1,2),(2,3,4),(1,4,5))
    H=global_nae_masks(6,edges)
    assert H=={(0,0,0,0,0,0),(1,1,1,1,1,1)}
    M=models_nae(6,edges)
    for a in M:
        for h in H:
            assert xor(a,h) in M

    # Canonical quotient: every model can be translated to x0=0.
    for a in M:
        if a[0]:
            a=xor(a,(1,1,1,1,1,1))
        assert a[0]==0 and a in M

    print("TRANSLATION_STABILIZER_LOCAL_RELATIONS = PASS")
    print("CONNECTED_NAE_GLOBAL_SPACE_DIMENSION = 1")
    print("CANONICAL_ORBIT_QUOTIENT = PASS")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
