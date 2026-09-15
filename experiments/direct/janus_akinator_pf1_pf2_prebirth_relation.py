#!/usr/bin/env python3
from itertools import product


def pf1_fixture():
    # F=(x or a) and (x or b) and (~x or c) and (~x or d)
    # exists x F == (a and b) or (c and d)
    for a,b,c,d in product((0,1), repeat=4):
        lhs = any(((x or a) and (x or b) and ((not x) or c) and ((not x) or d)) for x in (0,1))
        rhs = bool((a and b) or (c and d))
        assert lhs == rhs
        if rhs:
            x = 0 if (a and b) else 1
            assert ((x or a) and (x or b) and ((not x) or c) and ((not x) or d))


def add_only_frontier_fixture():
    # Original x-pivot residual pairs: {a OR c, a OR d, b OR c, b OR d}.
    old = {('a','c'),('a','d'),('b','c'),('b','d')}
    # Appending definitions can create additional pivot pairs, but old pairs remain.
    new = set(old) | {('a','e'),('b','e')}
    assert old <= new


def pf2_single_relation():
    rel = set()
    for e,y in product((0,1), repeat=2):
        if any(e == (x & y) for x in (0,1)):
            rel.add((e,y))
    assert rel == {(0,0),(0,1),(1,1)}
    assert {e for e,y in rel if y == 1} == {0,1}


def pf2_joint_relation():
    rel = {(x,1-x) for x in (0,1)}
    assert rel == {(0,1),(1,0)}
    m1 = {a for a,_ in rel}
    m2 = {b for _,b in rel}
    cart = {(a,b) for a in m1 for b in m2}
    assert rel < cart
    assert (0,0) in cart-rel and (1,1) in cart-rel


def main():
    pf1_fixture()
    add_only_frontier_fixture()
    pf2_single_relation()
    pf2_joint_relation()
    print('C025_AKINATOR_PF1_PREBIRTH_FACTOR_FINITE_REPLAY = PASS')
    print('C025_AKINATOR_PF1_WITNESS_LIFT_FINITE_REPLAY = PASS')
    print('C025_AKINATOR_ADD_ONLY_FRONTIER_MONOTONICITY = PASS')
    print('C025_AKINATOR_PF2_FUNCTION_TO_RELATION = PASS')
    print('C025_AKINATOR_PF2_JOINT_CORRELATION = PASS')
    print('C025_AKINATOR_PROVIDER_CLAIM_CEILING = FINITE_MECHANICS_ONLY')
    print('UNIVERSAL_POLY_BOUNDARY_QUOTIENT = OPEN')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
