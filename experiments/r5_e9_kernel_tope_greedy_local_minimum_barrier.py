#!/usr/bin/env python3
"""Exact regression for the PG15 rational-kernel chamber-greedy barrier.

No LP solver is used. The strict local-minimum claim handles coincident /
projectively parallel kernel hyperplanes explicitly. Boundary distances are
certified by exhaustive enumeration of the 15-choose-5 Exact-One witnesses.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd

ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]

B = [
    [-1,-1, 0, 0],[-1, 0,-1, 0],[ 2, 1, 1, 0],[-1,-1,-1, 1],
    [-1,-1, 0, 0],[-1, 0,-1, 0],[-1, 0, 0,-1],[ 1, 0, 0, 0],
    [ 1, 0, 1,-1],[ 1, 1, 0,-1],[ 0, 0, 0, 1],[ 1, 0, 0, 0],
    [ 0, 1, 0, 0],[ 0, 0, 1, 0],[ 0, 0, 0, 1],
]

ALPHA = [-7, 8, 8, -8]
EXPECTED_Y = [-1,-1,2,-17,-1,-1,15,-7,9,9,-8,-7,8,8,-8]
TOPE = "--+---+-++--++-"

CERTS = {
    2:  (0,1,2),
    6:  (6,7,10),
    8:  (1,8,10),
    9:  (0,9,10),
    12: (0,7,12),
    13: (1,7,13),
}


def incidence_matrix():
    return [[int(j + 1 in row) for j in range(15)] for row in ROWS]


def rank_q(M):
    A = [[Fraction(v) for v in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        f = A[r][c]
        A[r] = [z / f for z in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [A[i][j] - f * A[r][j] for j in range(n)]
        r += 1
    return r


def matmul(A, Bm):
    return [[sum(A[i][k] * Bm[k][j] for k in range(len(Bm)))
             for j in range(len(Bm[0]))] for i in range(len(A))]


def matvec(M, x):
    return [sum(row[j] * x[j] for j in range(len(x))) for row in M]


def signs_of(v):
    assert all(z != 0 for z in v)
    return ''.join('+' if z > 0 else '-' for z in v)


def signed_row(sign_char, row):
    s = 1 if sign_char == '+' else -1
    return [s * z for z in row]


def projective_key(row):
    g = 0
    for z in row:
        g = gcd(g, abs(z))
    assert g > 0
    q = [z // g for z in row]
    for z in q:
        if z != 0:
            if z < 0:
                q = [-w for w in q]
            break
    return tuple(q)


def exact_one_witnesses(A):
    out = []
    for C in combinations(range(15), 5):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            out.append(S)
    return out


def main():
    A = incidence_matrix()
    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(15)) == 3 for j in range(15))
    assert rank_q(A) == 11
    assert rank_q(B) == 4
    assert matmul(A, B) == [[0] * 4 for _ in range(15)]

    y = matvec(B, ALPHA)
    assert y == EXPECTED_Y
    assert matvec(A, y) == [0] * 15
    assert signs_of(y) == TOPE
    assert TOPE.count('+') == 6

    m1 = m2 = 0
    for row in A:
        vals = [y[j] for j, a in enumerate(row) if a]
        assert len(vals) == 3 and sum(vals) == 0
        q = sum(v > 0 for v in vals)
        assert q in (1, 2)
        if q == 1:
            m1 += 1
        else:
            m2 += 1
    assert (m1, m2) == (12, 3)
    assert m2 == 3 * TOPE.count('+') - 15

    positive = {i for i, s in enumerate(TOPE) if s == '+'}
    assert positive == set(CERTS)

    classes = {}
    for i, row in enumerate(B):
        classes.setdefault(projective_key(row), []).append(i)
    projective_classes = [set(v) for v in classes.values()]
    multi = sorted(tuple(sorted(C)) for C in projective_classes if len(C) > 1)
    assert multi == [(0,4), (1,5), (7,11), (10,14)]

    for C in projective_classes:
        pos_in_class = C & positive
        if pos_in_class:
            assert len(C) == 1
        else:
            assert all(TOPE[i] == '-' for i in C)

    for flip, support in CERTS.items():
        desired = list(TOPE)
        assert desired[flip] == '+'
        desired[flip] = '-'
        signed = [signed_row(desired[i], B[i]) for i in range(15)]
        zero = [sum(signed[i][j] for i in support) for j in range(4)]
        assert zero == [0, 0, 0, 0], (flip, support, zero)

    witnesses = exact_one_witnesses(A)
    assert len(witnesses) == 4
    assert {tuple(sorted(S)) for S in witnesses} == {
        (0,4,6,8,13),
        (1,5,6,9,12),
        (2,7,8,9,11),
        (2,10,12,13,14),
    }

    hamming_distances = []
    projective_separations = []
    for S in witnesses:
        x = [1 if i in S else 0 for i in range(15)]
        assert matvec(A, x) == [1] * 15
        y_star = [3 * z - 1 for z in x]
        assert matvec(A, y_star) == [0] * 15
        boundary = signs_of(y_star)
        assert boundary.count('+') == 5

        diff = {i for i in range(15) if boundary[i] != TOPE[i]}
        assert all(not (diff & C) or C <= diff for C in projective_classes)
        hamming_distances.append(len(diff))
        projective_separations.append(sum(1 for C in projective_classes if C <= diff))

    assert hamming_distances == [5,5,5,5]
    assert projective_separations == [4,4,4,4]

    # In a real hyperplane arrangement, chamber-graph distance equals the
    # number of separating geometric hyperplanes: a generic segment crosses
    # each separating hyperplane once and no nonseparating hyperplane.
    min_hamming_to_boundary = min(hamming_distances)
    min_chamber_distance_to_boundary = min(projective_separations)
    assert min_hamming_to_boundary == 5
    assert min_chamber_distance_to_boundary == 4

    print({
        'status': 'PASS_EXACT_NON_GLOBAL_GEOMETRIC_CHAMBER_LOCAL_MINIMUM',
        'source': 'PG15_SAT_R11',
        'rank_q': 11,
        'nullity_q': 4,
        'local_tope': TOPE,
        'local_positive_count': 6,
        'local_defect_3p_minus_n': 3,
        'projective_hyperplane_classes': len(projective_classes),
        'non_singleton_negative_classes': len(multi),
        'potentially_improving_singleton_classes': len(CERTS),
        'exact_blocking_certificates': len(CERTS),
        'boundary_chambers': len(witnesses),
        'min_hamming_distance_to_boundary': min_hamming_to_boundary,
        'min_chamber_graph_distance_to_boundary': min_chamber_distance_to_boundary,
        'adjacent_chamber_greedy_descent': 'FALSIFIED',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
