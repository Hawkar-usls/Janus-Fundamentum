#!/usr/bin/env python3
from __future__ import annotations
from itertools import product

BOUNDARY = tuple(product((0,1), repeat=2))
TRIPLES = tuple(product((0,1), repeat=3))

def relation(mask):
    return {TRIPLES[i] for i in range(8) if (mask>>i)&1}

def projection_to_boundary(R):
    return {(b0,b1) for b0,b1,y in R}

def global_extendable(R1,R2):
    out=set()
    for b0,b1 in BOUNDARY:
        ok1=any((b0,b1,y) in R1 for y in (0,1))
        ok2=any((b0,b1,z) in R2 for z in (0,1))
        if ok1 and ok2:
            out.add((b0,b1))
    return out

def main():
    cases=0
    for m1 in range(256):
        R1=relation(m1)
        P1=projection_to_boundary(R1)
        for m2 in range(256):
            R2=relation(m2)
            P2=projection_to_boundary(R2)
            assert global_extendable(R1,R2) == (P1 & P2)
            cases += 1

    assert len(BOUNDARY) == 4
    print(f"ADHESION2_RELATION_PAIR_CASES = {cases}")
    print("BOUNDARY_MESSAGE_STATES_MAX = 4")
    print("SEPARATOR_JOIN_EQUALS_RELATION_INTERSECTION = PASS")
    print("WITNESS_GLUE_CONDITION = SAME_BOUNDARY_ASSIGNMENT")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
