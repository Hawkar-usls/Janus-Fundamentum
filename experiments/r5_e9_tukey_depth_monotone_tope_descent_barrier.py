#!/usr/bin/env python3
"""Exact PG15 countercontrol for monotone source-kernel tope descent."""

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

ALPHAS = [
    (-1,2,2,-2),
    (-2,4,4,1),
    (-1,4,4,2),
    (-1,4,2,2),
    (-1,2,2,2),
]

EXPECTED_POS = [
    {3,7,9,10,13,14},
    {3,7,9,10,11,13,14,15},
    {3,9,10,11,13,14,15},
    {3,10,11,13,14,15},
    {3,11,13,14,15},
]

EXPECTED_SEPARATORS = [
    {11,15}, {7}, {9}, {10},
]

EXPECTED_CLASSES = [
    {1,5}, {2,6}, {3}, {4}, {7}, {8,12}, {9}, {10}, {11,15}, {13}, {14},
]

UNIQUE_POSITIVE_ROW = {
    3:  (1,2,3),
    7:  (7,8,15),
    9:  (2,9,11),
    10: (1,10,11),
    13: (1,12,13),
    14: (2,12,14),
}


def matrix():
    A = [[0]*15 for _ in range(15)]
    for i,row in enumerate(ROWS):
        for j in row:
            A[i][j-1] = 1
    return A


def matvec(A, x):
    return [sum(Fraction(a)*b for a,b in zip(row,x)) for row in A]


def kernel_vec(alpha):
    return [sum(Fraction(B[i][j])*alpha[j] for j in range(4)) for i in range(15)]


def positive_set(y):
    assert all(v != 0 for v in y)
    return {i+1 for i,v in enumerate(y) if v > 0}


def proportional(r,s):
    # Exact rank-one test for two nonzero rational rows.
    pivot = next(i for i,x in enumerate(r) if x != 0)
    if s[pivot] == 0:
        return False
    a = Fraction(s[pivot], r[pivot])
    return all(Fraction(s[i]) == a*Fraction(r[i]) for i in range(len(r)))


def projective_classes():
    unused = set(range(15))
    out = []
    while unused:
        i = min(unused)
        cls = {j for j in unused if proportional(B[i], B[j])}
        out.append({j+1 for j in cls})
        unused -= cls
    return out


def witness_sets(A):
    out=[]
    for C in combinations(range(15),5):
        S=set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            out.append({j+1 for j in C})
    return out


def row_positive_count(row, P):
    return sum(j in P for j in row)


def main():
    A = matrix()
    assert all(sum(r)==3 for r in A)
    assert all(sum(A[i][j] for i in range(15))==3 for j in range(15))

    classes = projective_classes()
    assert classes == EXPECTED_CLASSES, classes

    ys=[]
    for alpha,Pexp in zip(ALPHAS,EXPECTED_POS):
        y=kernel_vec(alpha)
        assert matvec(A,y) == [0]*15
        assert positive_set(y) == Pexp
        # Every source row of a full-support kernel vector is mixed.
        assert all(row_positive_count(row,Pexp) in (1,2) for row in ROWS)
        ys.append(y)

    # y0 is a p=6 full-support tope with exactly three ++- defects.
    P0=EXPECTED_POS[0]
    defects=[row for row in ROWS if row_positive_count(row,P0)==2]
    assert defects == [(3,4,7),(4,9,13),(4,10,14)]
    assert len(defects) == 3 == 3*len(P0)-15

    # Every positive class is singleton and cannot be flipped downward: doing
    # so makes an explicit source triple all-negative.
    for i,row in UNIQUE_POSITIVE_ROW.items():
        assert {i} in classes
        assert i in P0
        assert row_positive_count(row,P0)==1
        Pflip=set(P0); Pflip.remove(i)
        assert row_positive_count(row,Pflip)==0

    # The only negative singleton is 4; flipping it upward makes (3,4,7) +++.
    singletons={next(iter(c)) for c in classes if len(c)==1}
    negative_singletons=singletons-P0
    assert negative_singletons == {4}
    P4=set(P0); P4.add(4)
    assert row_positive_count((3,4,7),P4)==3

    # Every remaining class is a negative pair, so any feasible facet exit
    # through one of them raises p from 6 to 8.
    pair_classes=[c for c in classes if len(c)==2]
    assert pair_classes == [{1,5},{2,6},{8,12},{11,15}]
    assert all(not (c & P0) for c in pair_classes)

    # The explicit nonmonotone escape consists entirely of realized kernel
    # topes, and each step flips exactly one projective hyperplane class.
    for a,b,sep in zip(EXPECTED_POS,EXPECTED_POS[1:],EXPECTED_SEPARATORS):
        assert a.symmetric_difference(b) == sep
        assert sep in classes
    assert [len(P) for P in EXPECTED_POS] == [6,8,7,6,5]

    # Final p=5 sign set is an actual Exact-One witness, so the global depth is
    # exactly 5 once combined with the arbitrary-size source lower bound p>=n/3.
    Pstar=EXPECTED_POS[-1]
    assert all(row_positive_count(row,Pstar)==1 for row in ROWS)
    ws=witness_sets(A)
    assert len(ws)==4
    assert Pstar in ws

    print({
        'status':'PASS_PG15_MONOTONE_TOPE_DESCENT_COUNTERCONTROL',
        'projective_classes':[sorted(c) for c in classes],
        'local_min_positive_count':len(P0),
        'global_boundary_positive_count':len(Pstar),
        'local_defects':len(defects),
        'escape_profile':[len(P) for P in EXPECTED_POS],
        'escape_separators':[sorted(s) for s in EXPECTED_SEPARATORS],
        'exact_witnesses':len(ws),
        'monotone_adjacent_descent':'FALSIFIED',
        'augmenting_cascade':'OPEN',
        'E8_D1':'EMPTY',
        'P_VS_NP':'OPEN',
    })


if __name__ == '__main__':
    main()
