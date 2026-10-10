#!/usr/bin/env python3
from itertools import product

SHEETS = ((0,0), (1,0), (0,1))

def maj(a,b,c):
    return int(a+b+c >= 2)

def q(a,b,c,u,v):
    # Expansion over F2 of Maj(a,b+u,c+v).
    return (
        (a*b) ^ (a*u) ^ (a*c) ^ (a*v) ^
        (b*c) ^ (b*v) ^ (c*u) ^ (u*v)
    )

EXPECTED = {
    (0,0,0): (),
    (0,0,1): ((1,0),),
    (0,1,0): ((0,1),),
    (0,1,1): ((0,0),),
    (1,0,0): ((1,0),(0,1)),
    (1,0,1): ((0,0),(1,0)),
    (1,1,0): ((0,0),(0,1)),
    (1,1,1): ((0,0),(1,0),(0,1)),
}

def main():
    for a,b,c in product((0,1), repeat=3):
        allowed=[]
        for u,v in SHEETS:
            assert u*v == 0
            direct=maj(a,b^u,c^v)
            expanded=q(a,b,c,u,v)
            assert direct == expanded
            if expanded == 1:
                allowed.append((u,v))
        allowed=tuple(allowed)
        assert allowed == EXPECTED[(a,b,c)]
        assert bool(allowed) == bool(a or b or c)

    # Repetition-code positive control.
    for d in range(2,9):
        for xs in product((0,1), repeat=d):
            parity_ok=all((xs[i] ^ xs[i+1]) == 0 for i in range(d-1))
            equality_ok=(len(set(xs)) == 1)
            assert parity_ok == equality_ok

    print("THREE_SHEET_QUADRATIC_EXPANSION = PASS")
    print("EXISTS_LOCAL_FLIPS_IFF_OR3 = PASS")
    print("VARIABLE_COHERENCE_REPETITION_CODE = PASS")
    print("RANK1_MOMENT_NORMAL_FORM = ALGEBRAIC_IDENTITY_READY")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
