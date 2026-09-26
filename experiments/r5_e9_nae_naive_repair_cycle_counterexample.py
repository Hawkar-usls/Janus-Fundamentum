#!/usr/bin/env python3
"""Frozen counterexample for naive lexicographic NAE repair propagation."""

EDGES = (
    (3,5,7),(6,8,11),(1,4,10),(0,2,9),
    (2,6,10),(1,5,11),(0,3,8),(4,7,9),
    (1,3,6),(5,9,10),(2,7,8),(0,4,11),
    (2,3,11),(0,7,10),(4,5,6),(1,8,9),
)

START = (0,0,0,1,0,0,1,1,0,1,1,1)
ANCHOR = 0
PIVOT = 6

def nae_ok(a,e):
    return len({a[v] for v in e}) > 1

def model(a):
    return all(nae_ok(a,e) for e in EDGES)

def step_trace():
    assert model(START)
    a=list(START)
    assert a[ANCHOR]==0 and a[PIVOT]==1

    a[PIVOT]^=1
    s0=tuple(a)
    bad=[e for e in EDGES if not nae_ok(a,e)]
    assert bad==[(4,5,6)]

    a[4]^=1
    s1=tuple(a)
    bad=[e for e in EDGES if not nae_ok(a,e)]
    assert bad==[(4,7,9)]

    a[4]^=1
    s2=tuple(a)
    assert s2==s0
    bad=[e for e in EDGES if not nae_ok(a,e)]
    assert bad==[(4,5,6)]

    return s0,s1,s2

def main():
    s0,s1,s2=step_trace()
    print("NAIVE_LEX_REPAIR_CYCLE = PASS")
    print("cycle_length = 2")
    print("pivot = 6")
    print("anchor = 0")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
