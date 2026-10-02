#!/usr/bin/env python3
"""Exact pin-activated XOR gadget for linear 3-uniform NAE."""

from collections import Counter
from itertools import product

NAMES=("x","y","a","b","c","d","q0","q1")
IDX={s:i for i,s in enumerate(NAMES)}

EDGES=(
    ("x","a","b"),
    ("y","c","d"),
    ("a","c","q0"),
    ("a","d","q1"),
    ("b","c","q1"),
    ("b","d","q0"),
)

def nae(vals):
    return len(set(vals))>1

def extensions(x,y,q0=None,q1=None):
    out=[]
    for a,b,c,d in product((0,1),repeat=4):
        for r0 in ((q0,) if q0 is not None else (0,1)):
            for r1 in ((q1,) if q1 is not None else (0,1)):
                val=dict(zip(NAMES,(x,y,a,b,c,d,r0,r1)))
                if all(nae(tuple(val[v] for v in e)) for e in EDGES):
                    out.append((a,b,c,d,r0,r1))
    return out

def main():
    pinned={
        (x,y)
        for x,y in product((0,1),repeat=2)
        if extensions(x,y,0,1)
    }
    assert pinned=={(0,1),(1,0)}

    pinned_reverse={
        (x,y)
        for x,y in product((0,1),repeat=2)
        if extensions(x,y,1,0)
    }
    assert pinned_reverse=={(0,1),(1,0)}

    free={
        (x,y)
        for x,y in product((0,1),repeat=2)
        if extensions(x,y)
    }
    assert free==set(product((0,1),repeat=2))

    # Internal pinned relation is exactly a=b=not c=not d.
    internal=set()
    for a,b,c,d in product((0,1),repeat=4):
        val={"a":a,"b":b,"c":c,"d":d,"q0":0,"q1":1}
        if all(
            nae(tuple(val[v] for v in e))
            for e in EDGES[2:]
        ):
            internal.add((a,b,c,d))
    assert internal=={(0,0,1,1),(1,1,0,0)}

    deg=Counter(v for e in EDGES for v in e)
    assert deg==Counter({
        "a":3,"b":3,"c":3,"d":3,
        "q0":2,"q1":2,"x":1,"y":1
    })

    for i,e in enumerate(EDGES):
        for f in EDGES[i+1:]:
            assert len(set(e)&set(f))<=1

    print("PIN_ACTIVATED_XOR_PROJECTION = PASS")
    print("FREE_PIN_PROJECTION_UNIVERSAL = PASS")
    print("LINEARITY = PASS")
    print("MAX_DEGREE = 3")
    print("EXTERNAL_GADGET_DEGREE = 1")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
