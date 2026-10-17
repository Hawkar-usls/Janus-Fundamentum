#!/usr/bin/env python3
"""Exact PG15 regression for the source-kernel tope geodesic bound.

The arbitrary-size gallery-distance theorem is proved geometrically in the
companion research note.  This checker binds the frozen PG15 local-minimum
escape to the simplified projective arrangement and verifies that the known
6->8->7->6->5 cascade is a shortest gallery.
"""

from fractions import Fraction

B = [
    (-1,-1, 0, 0),(-1, 0,-1, 0),( 2, 1, 1, 0),(-1,-1,-1, 1),
    (-1,-1, 0, 0),(-1, 0,-1, 0),(-1, 0, 0,-1),( 1, 0, 0, 0),
    ( 1, 0, 1,-1),( 1, 1, 0,-1),( 0, 0, 0, 1),( 1, 0, 0, 0),
    ( 0, 1, 0, 0),( 0, 0, 1, 0),( 0, 0, 0, 1),
]

ALPHAS = [
    (-1,2,2,-2),
    (-2,4,4,1),
    (-1,4,4,2),
    (-1,4,2,2),
    (-1,2,2,2),
]

EXPECTED_P = [6,8,7,6,5]
EXPECTED_STEP_CLASSES = [
    frozenset({11,15}),
    frozenset({7}),
    frozenset({9}),
    frozenset({10}),
]


def dot(row, alpha):
    return sum(Fraction(a)*Fraction(b) for a,b in zip(row,alpha))


def proportional(r,s):
    pivot = next(i for i,x in enumerate(r) if x != 0)
    if s[pivot] == 0:
        return False
    k = Fraction(s[pivot], r[pivot])
    return all(Fraction(s[i]) == k*Fraction(r[i]) for i in range(len(r)))


def positive_proportional(r,s):
    pivot = next(i for i,x in enumerate(r) if x != 0)
    if s[pivot] == 0:
        return False
    k = Fraction(s[pivot], r[pivot])
    return k > 0 and all(Fraction(s[i]) == k*Fraction(r[i]) for i in range(len(r)))


def projective_classes():
    unused=set(range(15))
    out=[]
    while unused:
        i=min(unused)
        cls={j for j in unused if proportional(B[i],B[j])}
        # PG15 has only positive multiples inside each class, so a single
        # canonical sign represents the whole class without reorientation.
        assert all(positive_proportional(B[i],B[j]) for j in cls)
        out.append(frozenset(j+1 for j in cls))
        unused -= cls
    return out


def tope(alpha):
    vals=[dot(row,alpha) for row in B]
    assert all(v != 0 for v in vals)
    return tuple(1 if v>0 else -1 for v in vals)


def class_signs(alpha, classes):
    t=tope(alpha)
    signs={}
    for cls in classes:
        ss={t[i-1] for i in cls}
        assert len(ss)==1
        signs[cls]=next(iter(ss))
    return signs


def separators(alpha,beta,classes):
    a=class_signs(alpha,classes)
    b=class_signs(beta,classes)
    return {cls for cls in classes if a[cls] != b[cls]}


def positive_count(alpha):
    return sum(s>0 for s in tope(alpha))


def main():
    classes=projective_classes()
    assert len(classes)==11
    assert len(classes) <= len(B) == 15

    assert [positive_count(a) for a in ALPHAS] == EXPECTED_P

    # Each realized consecutive pair differs on exactly one distinct geometric
    # hyperplane class, hence is adjacent in the simplified tope graph.
    step_seps=[]
    for a,b in zip(ALPHAS,ALPHAS[1:]):
        s=separators(a,b,classes)
        assert len(s)==1
        step_seps.append(next(iter(s)))
    assert step_seps == EXPECTED_STEP_CLASSES

    # Endpoints differ on exactly four projective hyperplanes.  Every gallery
    # must cross each of these at least once, so distance >=4.  The explicit
    # four-step gallery above gives distance <=4.  Hence it is geodesic.
    endpoint_sep=separators(ALPHAS[0],ALPHAS[-1],classes)
    assert endpoint_sep == set(EXPECTED_STEP_CLASSES)
    lower_bound=len(endpoint_sep)
    explicit_length=len(ALPHAS)-1
    assert lower_bound == explicit_length == 4

    # No class is crossed twice: the gallery realizes exactly the endpoint
    # separator set.  This is the finite PG15 instance of the general
    # partial-cube/geodesic theorem.
    assert len(set(step_seps)) == len(step_seps)
    assert set(step_seps) == endpoint_sep

    print({
        'status':'PASS_SOURCE_KERNEL_TOPE_GEODESIC_PG15',
        'projective_hyperplanes':len(classes),
        'element_rows':len(B),
        'endpoint_separators':[sorted(c) for c in sorted(endpoint_sep,key=lambda x:min(x))],
        'gallery_length':explicit_length,
        'distance_lower_bound':lower_bound,
        'is_geodesic':True,
        'depth_profile':EXPECTED_P,
        'general_theorem':'DIST_EQUALS_SEPARATING_PROJECTIVE_HYPERPLANES',
        'route_selection':'OPEN',
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__ == '__main__':
    main()
