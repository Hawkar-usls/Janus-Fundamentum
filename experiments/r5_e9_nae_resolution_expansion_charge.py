#!/usr/bin/env python3
"""Exact sanity for the linear NAE3 resolution-expansion charge theorem."""

from itertools import product

def local_star(d):
    x=1
    nxt=2
    clauses=[]
    for _ in range(d):
        a,b=nxt,nxt+1
        nxt+=2
        clauses.append(frozenset((x,a,b)))
        clauses.append(frozenset((-x,-a,-b)))
    return x,tuple(clauses)

def resolvent(c,d,l):
    r=(set(c)-{l}) | (set(d)-{-l})
    if any(-z in r for z in r):
        return None
    return frozenset(r)

def charge(d):
    x,F=local_star(d)
    P=[c for c in F if x in c]
    N=[c for c in F if -x in c]
    R=set()
    for c in P:
        for e in N:
            r=resolvent(c,e,x)
            if r is not None:
                R.add(r)
    return len(R)-len(P)-len(N),len(R)

def main():
    for d in range(1,13):
        chi,r=charge(d)
        assert r==d*(d-1)
        assert chi==d*(d-3)
    assert charge(3)[0]==0
    assert charge(4)[0]==4
    print("LINEAR_NAE3_RESOLUTION_EXPANSION_CHARGE = PASS")
    print("chi(d) = d(d-3)")
    print("chi(3)=0")
    print("chi(4)=4")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
