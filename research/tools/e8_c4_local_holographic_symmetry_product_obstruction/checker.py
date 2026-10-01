#!/usr/bin/env python3
"""Exact v8.5.6 checker: local C4 current signature symmetry/product obstruction."""

from fractions import Fraction
from itertools import combinations, permutations, product
from collections import Counter

PORTS = ("L0", "L2", "L3", "R0", "R2", "R3")
VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)


def h(t):
    return 2 if t % 3 == 0 else -1


def dot3(a, b):
    return sum(x * y for x, y in zip(a, b)) % 3


def local_signature(k):
    if sum(k) % 3:
        return 0
    return h(dot3(k, VP)) + h(dot3(k, VM))


ALL = list(product(range(3), repeat=6))
TABLE = {k: local_signature(k) for k in ALL}

profile = Counter(TABLE.values())
assert profile == Counter({0: 486, -2: 108, 1: 108, 4: 27})
assert sum(1 for k in ALL if sum(k) % 3 == 0) == 243
assert all(TABLE[k] != 0 for k in ALL if sum(k) % 3 == 0)
assert all(TABLE[k] == 0 for k in ALL if sum(k) % 3 != 0)

# Exhaust the full S6 leg-permutation stabilizer.
stabilizer = []
for p in permutations(range(6)):
    ok = True
    for k in ALL:
        kp = tuple(k[p[i]] for i in range(6))
        if TABLE[kp] != TABLE[k]:
            ok = False
            break
    if ok:
        stabilizer.append(p)

expected_stabilizer = {
    (0, 1, 2, 3, 4, 5),
    (0, 3, 2, 1, 4, 5),
    (4, 1, 5, 3, 0, 2),
    (4, 3, 5, 1, 0, 2),
}
assert set(stabilizer) == expected_stabilizer
assert len(stabilizer) == 4


def matrix_rank_q(mat):
    if not mat:
        return 0
    a = [[Fraction(x) for x in row] for row in mat]
    nrows = len(a)
    ncols = len(a[0])
    r = 0
    c = 0
    while r < nrows and c < ncols:
        pivot = None
        for i in range(r, nrows):
            if a[i][c] != 0:
                pivot = i
                break
        if pivot is None:
            c += 1
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [x / pv for x in a[r]]
        for i in range(nrows):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [a[i][j] - f * a[r][j] for j in range(ncols)]
        r += 1
        c += 1
    return r


def flattening_rank(left):
    left = tuple(left)
    right = tuple(i for i in range(6) if i not in left)
    row_words = list(product(range(3), repeat=len(left)))
    col_words = list(product(range(3), repeat=len(right)))
    mat = []
    for a in row_words:
        row = []
        for b in col_words:
            k = [0] * 6
            for i, x in zip(left, a):
                k[i] = x
            for i, x in zip(right, b):
                k[i] = x
            row.append(TABLE[tuple(k)])
        mat.append(row)
    return matrix_rank_q(mat)


rank_profiles = {}
for size in (1, 2, 3):
    rank_profiles[size] = Counter(
        flattening_rank(left)
        for left in combinations(range(6), size)
    )

assert rank_profiles[1] == Counter({3: 6})
assert rank_profiles[2] == Counter({9: 8, 6: 6, 3: 1})
assert rank_profiles[3] == Counter({12: 8, 9: 8, 6: 4})

for size in (1, 2, 3):
    assert min(rank_profiles[size]) > 1

print("PASS: local current tensor support is exactly the 5D conservation hyperplane (243/729 states)")
print("PASS: value profile is 27x4, 108x1, 108x(-2), 486x0")
print("PASS: exact S6 leg-permutation stabilizer has order 4 (Klein four)")
print("STABILIZER=(id),(1 3),(0 4)(2 5),(0 4)(1 3)(2 5)")
print("PASS: 1|5 flattening ranks = 3 on all 6 cuts")
print("PASS: 2|4 flattening ranks profile = rank3:1, rank6:6, rank9:8")
print("PASS: 3|3 flattening ranks profile = rank6:4, rank9:8, rank12:8")
print("VERDICT: UNIFORM_HOLOGRAPHIC_SYMMETRIZATION_AND_PORTWISE_PRODUCT_FACTORIZATION_ARE_EXACTLY_OBSTRUCTED")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
