#!/usr/bin/env python3
from __future__ import annotations
from itertools import combinations

GROUND = frozenset(("x","y","p"))
FEASIBLE = {
    frozenset(),
    frozenset(("y",)),
    frozenset(("x",)),
    frozenset(("x","y","p")),
}

def toggle_pair(X, e, f):
    toggles = {e} if e == f else {e,f}
    return frozenset(set(X) ^ toggles)

def symmetric_exchange_failure(feasible):
    for X in feasible:
        for Y in feasible:
            D = X ^ Y
            for e in D:
                if not any(toggle_pair(X,e,f) in feasible for f in D):
                    return X,Y,e
    return None

def twist(feasible, A):
    return {frozenset(F ^ A) for F in feasible}

def main():
    fail=symmetric_exchange_failure(FEASIBLE)
    assert fail is not None
    X,Y,e=fail
    assert X == frozenset()
    assert Y == frozenset(("x","y","p"))
    assert e == "p"

    # Exhaust all 2^3 twists: none can turn a non-delta-matroid into one.
    elems=tuple(GROUND)
    for mask in range(1<<len(elems)):
        A=frozenset(elems[i] for i in range(len(elems)) if (mask>>i)&1)
        assert symmetric_exchange_failure(twist(FEASIBLE,A)) is not None

    print("AND_GRAPH_RELATION_DELTA_MATROID = FAIL")
    print("EXPLICIT_EXCHANGE_WITNESS = EMPTY vs {x,y,p}, e=p")
    print("ALL_8_TWISTS_DELTA_MATROID = FAIL")
    print("DIRECT_DELTA_MATROID_RANK1_DEFECT_ROUTE = BLOCKED")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
