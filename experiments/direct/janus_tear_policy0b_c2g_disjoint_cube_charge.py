#!/usr/bin/env python3
"""Provider replay for C025-C2G disjoint proof-carrying cube charge mechanics."""
from itertools import product


def req(clause):
    out={}
    for lit in clause:
        var=abs(lit); value=0 if lit>0 else 1
        if var in out and out[var]!=value:
            raise ValueError('tautology')
        out[var]=value
    return out


def disjoint(c,d):
    rc,rd=req(c),req(d)
    return any(v in rd and rd[v]!=x for v,x in rc.items())


def cube_size(n,c):
    return 2**(n-len(req(c)))


def clause_for(bits):
    return tuple(i+1 if b==0 else -(i+1) for i,b in enumerate(bits))


def main():
    four=[(1,2),(-1,2),(1,-2),(-1,-2)]
    for i,c in enumerate(four):
        for d in four[i+1:]:
            assert disjoint(c,d)
    assert sum(cube_size(5,c) for c in four)==2**5
    assert not disjoint((1,2),(2,3))
    assert disjoint((1,2),(-1,3))

    for w in range(1,7):
        cs=[clause_for(bits) for bits in product((0,1),repeat=w)]
        assert len(cs)==2**w
        for i,c in enumerate(cs):
            for d in cs[i+1:]:
                assert disjoint(c,d)
        n=w+3
        assert sum(cube_size(n,c) for c in cs)==2**n

    print('C025_C2G_PAIRWISE_DISJOINTNESS_CRITERION = PASS')
    print('C025_C2G_WIDTH_TO_COUNT_TIGHT_FIXTURE = PASS')
    print('C025_C2G_OVERLAP_REJECTION = PASS')
    print('C025_C2G_BRANCH_BOUND_THEOREM = ANALYTICAL_SUFFICIENT_CONDITION')
    print('C025_C2G_UNIVERSAL_CHARGE_DISCOVERY = OPEN')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
