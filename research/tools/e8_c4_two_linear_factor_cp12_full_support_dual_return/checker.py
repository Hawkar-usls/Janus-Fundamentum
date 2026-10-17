#!/usr/bin/env python3
"""Exact v8.5.8 checker: two-linear factorization, CP-rank 12 certificate, and full-support dual return."""

from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations, product

D = range(3)
VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)
A = (1, 0, 0, 0, 2, 2)
B = (0, 1, 0, 1, 2, 1)


def h(t):
    return 2 if t % 3 == 0 else -1


def dot3(x, y):
    return sum(a * b for a, b in zip(x, y)) % 3


assert tuple((A[i] + B[i]) % 3 for i in range(6)) == VP
assert tuple((A[i] - B[i]) % 3 for i in range(6)) == VM

# Exact local two-linear identity on all 729 frequencies.
for k in product(D, repeat=6):
    lhs = h(dot3(k, VP)) + h(dot3(k, VM))
    rhs = h(dot3(k, A)) * h(dot3(k, B))
    assert lhs == rhs


def wire_state(c, s, q):
    # Port order L0,L2,L3,R0,R2,R3.
    return (
        (c + s) % 3,
        (c + s * q) % 3,
        c % 3,
        (c + s * q) % 3,
        (c - s * (1 + q)) % 3,
        (c + s * (q - 1)) % 3,
    )


WIRE = {
    wire_state(c, s, q)
    for c in D
    for s in (1, 2)
    for q in (1, 2)
}
CHAR_EXPONENTS = {
    tuple((c + alpha * A[i] + beta * B[i]) % 3 for i in range(6))
    for c in D
    for alpha in (1, 2)
    for beta in (1, 2)
}
assert len(WIRE) == 12
assert CHAR_EXPONENTS == WIRE


def f6(k):
    if sum(k) % 3:
        return 0
    return h(dot3(k, A)) * h(dot3(k, B))


def rank_q(mat):
    a = [[Fraction(x) for x in row] for row in mat]
    nr = len(a)
    nc = len(a[0]) if nr else 0
    r = 0
    for c in range(nc):
        pivot = next((i for i in range(r, nr) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [x / pv for x in a[r]]
        for i in range(nr):
            if i == r or a[i][c] == 0:
                continue
            q = a[i][c]
            a[i] = [a[i][j] - q * a[r][j] for j in range(nc)]
        r += 1
        if r == nr:
            break
    return r


def flattening_rank(left):
    left = tuple(left)
    right = tuple(i for i in range(6) if i not in left)
    rows = list(product(D, repeat=len(left)))
    cols = list(product(D, repeat=len(right)))
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


rank3_profile = Counter(flattening_rank(cut) for cut in combinations(range(6), 3))
assert rank3_profile == Counter({12: 8, 9: 8, 6: 4})
assert max(rank3_profile) == 12
# 12 explicit rank-one character terms + a flattening of rank 12 => CP-rank exactly 12.


def direct_closed_count(pi):
    total = 0
    for x in WIRE:
        for y in WIRE:
            if all(x[j] != y[pi[j]] for j in range(6)):
                total += 1
    return total


def full_support_N(pi):
    # Two-wire connected closure.  Six edge-sign rows are coordinate vectors.
    # Wire 0 contributes A,B.  Pulling wire 1 through the oriented matching gives
    # coefficients -A[pi[j]], -B[pi[j]] in edge coordinate j.
    rows = []
    for e in range(6):
        r = [0] * 6
        r[e] = 1
        rows.append(tuple(r))
    rows.append(A)
    rows.append(B)
    rows.append(tuple((-A[pi[j]]) % 3 for j in range(6)))
    rows.append(tuple((-B[pi[j]]) % 3 for j in range(6)))

    count = 0
    for signs in product((1, 2), repeat=10):
        y = [0] * 6
        for s, row in zip(signs, rows):
            for j in range(6):
                y[j] = (y[j] + s * row[j]) % 3
        # row(B_incidence) is span of the all-ones edge vector for two vertices.
        if len(set(y)) == 1:
            count += 1
    return count


direct_profile = Counter()
full_support_profile = Counter()
for pi in permutations(range(6)):
    direct = direct_closed_count(pi)
    n = full_support_N(pi)
    assert direct == 3 * n
    direct_profile[direct] += 1
    full_support_profile[n] += 1

assert direct_profile == Counter({
    0: 96,
    6: 180,
    12: 168,
    18: 168,
    24: 80,
    30: 20,
    36: 8,
})
assert full_support_profile == Counter({
    0: 96,
    2: 180,
    4: 168,
    6: 168,
    8: 80,
    10: 20,
    12: 8,
})

print("PASS: VP=A+B and VM=A-B over GF(3)")
print("PASS: h(k.VP)+h(k.VM)=h(k.A)h(k.B) on all 3^6=729 frequencies")
print("PASS: the 12 character exponent vectors c*1+alpha*A+beta*B are exactly the 12 quotient wire states")
print("PASS: exact 3|3 flattening-rank profile is rank6:4, rank9:8, rank12:8")
print("PASS: explicit 12-term character decomposition plus rank-12 flattening proves CP_RANK_F6=12")
print("PASS: all 6!=720 two-wire closures satisfy DIRECT_COUNT=3*FULL_SUPPORT_N")
print("DIRECT_PROFILE=0:96,6:180,12:168,18:168,24:80,30:20,36:8")
print("FULL_SUPPORT_PROFILE=0:96,2:180,4:168,6:168,8:80,10:20,12:8")
print("VERDICT: EXACT_TWO_LINEAR_FACTOR_CP12_AND_FULL_SUPPORT_DUAL_RETURN_ESTABLISHED")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
