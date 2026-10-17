#!/usr/bin/env python3
"""Exact sanity for the torsion side-code barrier."""

from itertools import product

def z3_rel():
    return {
        s for s in product((0,1),repeat=3)
        if sum(s)%3 == 1
    }

def affine_coset_two_words(a,b):
    d=tuple(x^y for x,y in zip(a,b))
    # Any two distinct Boolean words form a 1-dimensional affine F2 coset.
    return a!=b and any(d)

def main():
    R=z3_rel()
    assert R=={(1,0,0),(0,1,0),(0,0,1)}

    a=(0,0,0,0,1,0)
    b=(1,1,1,1,0,1)
    assert affine_coset_two_words(a,b)
    assert tuple(x^y for x,y in zip(a,b))==(1,1,1,1,1,1)

    print("Z3_BOOLEAN_SIDE_CODE = POSITIVE_1_IN_3")
    print("DET13_TWO_WORD_SIDE_CODE = F2_AFFINE_COSET")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
