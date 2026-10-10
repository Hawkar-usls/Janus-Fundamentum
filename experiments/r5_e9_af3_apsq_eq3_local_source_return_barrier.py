#!/usr/bin/env python3
"""Exact regression for the AF3/APSQ EQ3 local source-return barrier."""

from collections import defaultdict
from itertools import product

ROWS = [
    (2,5,6),
    (1,4,7),
    (5,7,9),
    (0,3,7),
    (4,6,9),
    (2,4,8),
    (3,8,9),
    (0,5,8),
    (1,3,6),
]


def incidence(rows, n):
    A = [[0]*n for _ in rows]
    for i,row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rank_mod(A, p=3):
    M = [[v % p for v in row] for row in A]
    m, n = len(M), len(M[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r,m) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [(v*inv) % p for v in M[r]]
        for i in range(m):
            if i != r and M[i][c]:
                f = M[i][c]
                M[i] = [(M[i][j]-f*M[r][j]) % p for j in range(n)]
        r += 1
    return r


def affine_solutions(A):
    n = len(A[0])
    return [
        r for r in product(range(3), repeat=n)
        if all(sum(A[i][j]*r[j] for j in range(n)) % 3 == 1 for i in range(len(A)))
    ]


def canon_normal(a):
    j = next(i for i,v in enumerate(a) if v)
    inv = pow(a[j], -1, 3)
    return tuple(v*inv % 3 for v in a), inv


def main():
    G = incidence(ROWS, 10)
    assert rank_mod(G) == 8

    sols = affine_solutions(G)
    assert len(sols) == 9

    # The exact two-parameter family recovered by elimination.
    for r in sols:
        q = r[9]
        p = r[8]
        assert r[0] == r[1] == r[2] == r[9] == q
        assert r[3] == r[4] == r[5] == (1-p-q) % 3
        assert r[6] == r[7] == r[8] == p

    full = [r for r in sols if all(v != 0 for v in r)]
    assert len(full) == 3
    assert {(r[8],r[9]) for r in full} == {(1,1),(2,1),(1,2)}
    assert {(r[0],r[1],r[2]) for r in full} == {(1,1,1),(2,2,2)}

    decoded = {
        tuple(1 if r[i] == 2 else 0 for i in range(3))
        for r in full
    }
    assert decoded == {(0,0,0),(1,1,1)}

    # APSQ local hyperplanes are precisely q!=0, p!=0, 1-p-q!=0.
    # Parameter order is (p,q).  For a coordinate affine function c+a.(p,q),
    # store the normalized normal and forbidden offset.
    funcs = [
        ((0,1), 0),  # q
        ((1,0), 0),  # p
        ((2,2), 1),  # 1-p-q
    ]
    classes = defaultdict(set)
    for a,c in funcs:
        an, inv = canon_normal(a)
        cn = c*inv % 3
        classes[an].add((-cn) % 3)
    assert len(classes) == 3
    assert all(len(v) == 1 for v in classes.values())

    # Exact source-return at an old source row: three shared nonzero q-values
    # satisfying qx+qy+qz=1 decode to exactly one Boolean 1.
    ternary_rows = []
    for qx,qy,qz in product((1,2), repeat=3):
        if (qx+qy+qz) % 3 == 1:
            bits = tuple(int(q == 2) for q in (qx,qy,qz))
            ternary_rows.append(((qx,qy,qz), bits))
    assert len(ternary_rows) == 3
    assert {bits for _,bits in ternary_rows} == {(1,0,0),(0,1,0),(0,0,1)}

    print({
        'status': 'PASS_AF3_APSQ_EQ3_LOCAL_SOURCE_RETURN',
        'rank_F3': 8,
        'affine_dimension': 2,
        'affine_solutions': 9,
        'nowhere_zero_solutions': 3,
        'apsq_parallel_classes': 3,
        'apsq_pins': 0,
        'terminal_projection_F3': ['111','222'],
        'terminal_projection_boolean': ['000','111'],
        'old_source_row_decoding': 'EXACT_POSITIVE_1IN3',
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
