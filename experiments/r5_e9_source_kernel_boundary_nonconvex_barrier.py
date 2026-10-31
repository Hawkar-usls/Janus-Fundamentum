#!/usr/bin/env python3
"""Exact PG15 countercontrol for convex/gated kernel-boundary shortcuts."""

from fractions import Fraction
from itertools import combinations

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

BOUNDARY = [
    ({1,5,7,9,14},      (-1,-1, 2,-1)),
    ({2,6,7,10,13},     (-1, 2,-1,-1)),
    ({3,8,9,10,12},     ( 2,-1,-1,-1)),
    ({3,11,13,14,15},   (-1, 2, 2, 2)),
]

Z_ALPHA=(-1,-1,2,-3)
Z_POS={1,5,7,9,10,14}


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


def dot(r,a):
    return sum(Fraction(x)*Fraction(y) for x,y in zip(r,a))


def signs(alpha):
    vals=[dot(r,alpha) for r in B]
    assert all(v != 0 for v in vals)
    return tuple(1 if v>0 else -1 for v in vals)


def positives(alpha):
    return {i+1 for i,s in enumerate(signs(alpha)) if s>0}


def class_signs(alpha,classes):
    s=signs(alpha); out=[]
    for cls in classes:
        ss={s[i-1] for i in cls}
        assert len(ss)==1
        out.append(next(iter(ss)))
    return tuple(out)


def dist(a,b,classes):
    x=class_signs(a,classes); y=class_signs(b,classes)
    return sum(u!=v for u,v in zip(x,y))


def separator_classes(a,b,classes):
    x=class_signs(a,classes); y=class_signs(b,classes)
    return {classes[i] for i,(u,v) in enumerate(zip(x,y)) if u!=v}


def exact_witnesses():
    out=[]
    for C in combinations(range(1,16),5):
        S=set(C)
        if all(len(S & set(row)) == 1 for row in ROWS):
            out.append(S)
    return out


def main():
    classes=projective_classes()
    assert len(classes)==11

    ws=exact_witnesses()
    assert len(ws)==4
    assert {frozenset(w) for w in ws} == {frozenset(w) for w,_ in BOUNDARY}

    for W,a in BOUNDARY:
        assert positives(a)==W
        assert len(W)==5

    # All four exact boundary topes are mutually distance six.
    pair_dist=[]
    for i in range(4):
        for j in range(i+1,4):
            dij=dist(BOUNDARY[i][1],BOUNDARY[j][1],classes)
            pair_dist.append(dij)
            assert dij==6
    assert pair_dist == [6]*6

    # Explicit nonboundary vertex in the interval between boundary topes 1,2.
    a=BOUNDARY[0][1]
    b=BOUNDARY[1][1]
    z=Z_ALPHA
    assert positives(z)==Z_POS
    assert len(Z_POS)==6
    assert dist(a,z,classes)==1
    assert dist(z,b,classes)==5
    assert dist(a,b,classes)==6
    assert dist(a,z,classes)+dist(z,b,classes)==dist(a,b,classes)

    assert separator_classes(a,z,classes)=={frozenset({10})}
    assert separator_classes(z,b,classes)=={
        frozenset({1,5}),frozenset({2,6}),frozenset({9}),
        frozenset({13}),frozenset({14}),
    }

    y_z=[dot(r,z) for r in B]
    assert y_z == [2,-1,-1,-3,2,-1,4,-1,4,1,-3,-1,-1,2,-3]

    print({
        'status':'PASS_PG15_BOUNDARY_NONCONVEX_NONGATED_COUNTERCONTROL',
        'boundary_topes':len(ws),
        'boundary_pair_distances':pair_dist,
        'interval_vertex_p':len(Z_POS),
        'dist_boundary1_to_Z':1,
        'dist_Z_to_boundary2':5,
        'dist_boundary1_to_boundary2':6,
        'boundary_convex':False,
        'boundary_gated':False,
        'route_selection':'OPEN',
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__ == '__main__':
    main()
