#!/usr/bin/env python3
"""Finite exact binding for the source-kernel polynomial navigation shell.

The companion note proves the arbitrary-size moment-curve start construction
and rational-LP neighbor oracle.  This checker binds those claims to PG15 and
certifies the exact four-neighbor p=6 local-minimum chamber without requiring
an external LP package.
"""

from fractions import Fraction

ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

B = [
    (-1,-1, 0, 0),(-1, 0,-1, 0),( 2, 1, 1, 0),(-1,-1,-1, 1),
    (-1,-1, 0, 0),(-1, 0,-1, 0),(-1, 0, 0,-1),( 1, 0, 0, 0),
    ( 1, 0, 1,-1),( 1, 1, 0,-1),( 0, 0, 0, 1),( 1, 0, 0, 0),
    ( 0, 1, 0, 0),( 0, 0, 1, 0),( 0, 0, 0, 1),
]

TRAP=(-1,2,2,-2)
EXPECTED_NEIGHBORS = {
    frozenset({1,5}):   (-2,1,4,-2),
    frozenset({2,6}):   (-2,4,1,-2),
    frozenset({8,12}):  (1,1,1,-2),
    frozenset({11,15}): (-2,4,4,1),
}

UNIQUE_POSITIVE_ROW = {
    3:  (1,2,3),
    7:  (7,8,15),
    9:  (2,9,11),
    10: (1,10,11),
    13: (1,12,13),
    14: (2,12,14),
}


def dot(r,a):
    return sum(Fraction(x)*Fraction(y) for x,y in zip(r,a))


def values(alpha):
    return [dot(r,alpha) for r in B]


def signs(alpha):
    v=values(alpha)
    assert all(x != 0 for x in v)
    return tuple(1 if x>0 else -1 for x in v)


def positives(alpha):
    return {i+1 for i,s in enumerate(signs(alpha)) if s>0}


def proportional(r,s):
    pivot=next(i for i,x in enumerate(r) if x != 0)
    if s[pivot] == 0:
        return False
    k=Fraction(s[pivot],r[pivot])
    return all(Fraction(s[i]) == k*Fraction(r[i]) for i in range(len(r)))


def projective_classes():
    unused=set(range(15)); out=[]
    while unused:
        i=min(unused)
        cls={j for j in unused if proportional(B[i],B[j])}
        out.append(frozenset(j+1 for j in cls))
        unused-=cls
    return out


def class_signs(alpha,classes):
    s=signs(alpha); out={}
    for cls in classes:
        ss={s[i-1] for i in cls}
        assert len(ss)==1
        out[cls]=next(iter(ss))
    return out


def class_separator(a,b,classes):
    sa=class_signs(a,classes); sb=class_signs(b,classes)
    return {c for c in classes if sa[c] != sb[c]}


def row_positive_count(row,P):
    return sum(i in P for i in row)


def moment(t,d=4):
    return tuple(t**k for k in range(d))


def main():
    n=15; d=4
    classes=projective_classes()
    assert len(classes)==11 <= n

    # General theorem searches t in 0..n(d-1).  On PG15 the first safe
    # candidate is already t=1.
    bound=n*(d-1)
    assert bound==45
    bad0=values(moment(0,d))
    assert any(v==0 for v in bad0)
    first_safe=None
    for t in range(bound+1):
        if all(v != 0 for v in values(moment(t,d))):
            first_safe=t
            break
    assert first_safe==1
    start=moment(first_safe,d)
    assert start==(1,1,1,1)
    assert len(positives(start))==9
    assert len(positives(tuple(-x for x in start)))==6

    # Bind the strict p=6 trap.
    P=positives(TRAP)
    assert P=={3,7,9,10,13,14}
    assert len(P)==6

    # Four pair-class flips are realized by explicit exact rational (integer)
    # chamber representatives and every one raises p to 8.
    realized=set()
    for cls,a in EXPECTED_NEIGHBORS.items():
        sep=class_separator(TRAP,a,classes)
        assert sep=={cls}
        assert len(positives(a))==8
        realized.add(cls)
    assert realized=={
        frozenset({1,5}),frozenset({2,6}),
        frozenset({8,12}),frozenset({11,15}),
    }

    # Every positive singleton flip is locally impossible: it would create an
    # all-negative source row.  The only negative singleton is 4; flipping it
    # would create an all-positive source row.  Hence the four realized pair
    # flips above are the complete exact neighborhood of this chamber.
    singleton_classes={next(iter(c)) for c in classes if len(c)==1}
    for i,row in UNIQUE_POSITIVE_ROW.items():
        assert i in singleton_classes and i in P
        assert row_positive_count(row,P)==1
        Q=set(P); Q.remove(i)
        assert row_positive_count(row,Q)==0

    neg_singletons=singleton_classes-P
    assert neg_singletons=={4}
    Q=set(P); Q.add(4)
    assert row_positive_count((3,4,7),Q)==3

    pair_classes={c for c in classes if len(c)==2}
    assert pair_classes==realized

    print({
        'status':'PASS_SOURCE_KERNEL_POLYNOMIAL_NAVIGATION_SHELL_PG15',
        'moment_curve_search_bound':bound+1,
        'first_safe_t':first_safe,
        'start_positive_count':9,
        'oriented_start_positive_count':6,
        'projective_classes':len(classes),
        'trap_positive_count':6,
        'trap_exact_neighbor_count':len(realized),
        'trap_neighbor_positive_counts':[8,8,8,8],
        'local_neighbor_generation':'BOUND_EXACTLY_ON_PG15',
        'global_boundary_direction':'OPEN',
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__ == '__main__':
    main()
