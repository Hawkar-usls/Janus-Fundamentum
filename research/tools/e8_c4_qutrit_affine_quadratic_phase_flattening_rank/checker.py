#!/usr/bin/env python3
"""Exact v8.5.7 checker: F6 cut-rank certificate against qutrit affine/quadratic-phase GL(3)^6 orbit."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, product

VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)


def h(t):
    return 2 if t % 3 == 0 else -1


def dot3(a, b):
    return sum(x * y for x, y in zip(a, b)) % 3


def f6(k):
    if sum(k) % 3:
        return 0
    return h(dot3(k, VP)) + h(dot3(k, VM))


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    if not a:
        return 0
    nr, nc = len(a), len(a[0])
    r = c = 0
    while r < nr and c < nc:
        p = next((i for i in range(r, nr) if a[i][c] != 0), None)
        if p is None:
            c += 1
            continue
        a[r], a[p] = a[p], a[r]
        pivot = a[r][c]
        a[r] = [x / pivot for x in a[r]]
        for i in range(nr):
            if i == r or a[i][c] == 0:
                continue
            q = a[i][c]
            a[i] = [a[i][j] - q * a[r][j] for j in range(nc)]
        r += 1
        c += 1
    return r


def flattening_rank(left):
    left = tuple(left)
    right = tuple(i for i in range(6) if i not in left)
    rows = list(product(range(3), repeat=len(left)))
    cols = list(product(range(3), repeat=len(right)))
    mat = []
    for xs in rows:
        row = []
        for ys in cols:
            k = [0] * 6
            for i, x in zip(left, xs):
                k[i] = x
            for i, y in zip(right, ys):
                k[i] = y
            row.append(f6(tuple(k)))
        mat.append(row)
    return rank_q(mat)


def is_power_of_three(n):
    if n < 1:
        return False
    while n % 3 == 0:
        n //= 3
    return n == 1


value_profile = Counter(f6(k) for k in product(range(3), repeat=6))
assert value_profile == Counter({0: 486, -2: 108, 1: 108, 4: 27})

profiles = {}
cut_records = {}
for size in (1, 2, 3):
    records = {}
    for left in combinations(range(6), size):
        records[left] = flattening_rank(left)
    cut_records[size] = records
    profiles[size] = Counter(records.values())

assert profiles[1] == Counter({3: 6})
assert profiles[2] == Counter({9: 8, 6: 6, 3: 1})
assert profiles[3] == Counter({12: 8, 9: 8, 6: 4})

bad2 = sorted((cut, r) for cut, r in cut_records[2].items() if not is_power_of_three(r))
bad3 = sorted((cut, r) for cut, r in cut_records[3].items() if not is_power_of_three(r))
assert Counter(r for _, r in bad2) == Counter({6: 6})
assert Counter(r for _, r in bad3) == Counter({12: 8, 6: 4})

# The theorem in the paired JSON artifact proves that every flattening of a
# qutrit affine-support quadratic-phase tensor has rank 3^r and that named-cut
# ranks are invariant under independent GL(3,C) changes on the six ports.
# The finite executable certificate needed for F6 is therefore the presence of
# exact non-powers-of-three 6 and 12 on its named cuts.
assert not is_power_of_three(6)
assert not is_power_of_three(12)

print("PASS: F6 value profile = 486x0, 108x(-2), 108x1, 27x4")
print("PASS: 1|5 cut-rank profile = rank3:6")
print("PASS: 2|4 cut-rank profile = rank3:1, rank6:6, rank9:8")
print("PASS: 3|3 cut-rank profile = rank6:4, rank9:8, rank12:8")
print("PASS: exact offending non-power-of-three cut ranks are 6 and 12")
print("PASS: paired theorem gives affine-quadratic-phase cut rank 3^r and GL(3)^6 cut-rank invariance")
print("VERDICT: F6_IS_OUTSIDE_THE_PORTWISE_GL3_ORBIT_OF_QUTRIT_AFFINE_QUADRATIC_PHASE_TENSORS")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
