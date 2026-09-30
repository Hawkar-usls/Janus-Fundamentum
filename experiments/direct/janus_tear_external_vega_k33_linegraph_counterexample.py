#!/usr/bin/env python3
from itertools import combinations

LEFT=(0,1,2)
RIGHT=(3,4,5)
U=LEFT+RIGHT
C=tuple((u,v) for u in LEFT for v in RIGHT)

def degree(u):
    return sum(u in e for e in C)

def adjacent(u,v):
    return (u,v) in C or (v,u) in C

def main():
    assert all(degree(u)==3 for u in U)
    assert all(len(set(a)&set(b))<=1 for a,b in combinations(C,2))
    center=0
    leaves=RIGHT
    assert all(adjacent(center,x) for x in leaves)
    assert all(not adjacent(a,b) for a,b in combinations(leaves,2))
    print('EXT_VEGA_2XHS_K33_LEGAL = PASS')
    print('EXT_VEGA_K33_INDUCED_CLAW = PASS')
    print('EXT_VEGA_THEOREM6_ALL_2XHS_ARE_LINE_GRAPHS = REFUTED_BY_K33')
    print('P_VS_NP = OPEN')

if __name__=='__main__':
    main()
