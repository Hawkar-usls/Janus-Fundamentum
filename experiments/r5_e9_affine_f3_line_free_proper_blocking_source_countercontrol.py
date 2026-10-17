#!/usr/bin/env python3
"""Exact finite hostile control for the AF3 proper-blocking residual."""

from fractions import Fraction
from itertools import combinations, product

P = 3
ROWS = [
    (0,1,2),(0,9,10),(0,11,12),(1,8,10),(1,11,13),
    (2,3,6),(2,4,5),(3,8,12),(3,9,13),(4,7,8),
    (4,9,14),(5,7,13),(5,12,14),(6,7,14),(6,10,11),
]


def matrix_from_rows(rows, n):
    A = [[0] * n for _ in range(n)]
    for i, row in enumerate(rows):
        for j in row:
            A[i][j] = 1
    return A


def rank_q(M):
    A = [[Fraction(x) for x in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        z = A[r][c]
        A[r] = [x / z for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                z = A[i][c]
                A[i] = [A[i][j] - z * A[r][j] for j in range(n)]
        r += 1
    return r


def rref_mod(M, p=P):
    A = [[x % p for x in row] for row in M]
    m, n = len(A), len(A[0])
    r = 0
    pivots = []
    for c in range(n):
        pivot = next((i for i in range(r, m) if A[i][c]), None)
        if pivot is None:
            continue
        A[r], A[pivot] = A[pivot], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                z = A[i][c]
                A[i] = [(A[i][j] - z * A[r][j]) % p for j in range(n)]
        pivots.append(c)
        r += 1
    return A, pivots


def rank_mod(M, p=P):
    return len(rref_mod(M, p)[1])


def affine_parameterization(A):
    n = len(A)
    M = [[A[i][j] % P for j in range(n)] + [1] for i in range(n)]
    r = 0
    pivots = []
    for c in range(n):
        pivot = next((i for i in range(r, n) if M[i][c]), None)
        if pivot is None:
            continue
        M[r], M[pivot] = M[pivot], M[r]
        inv = pow(M[r][c], -1, P)
        M[r] = [(x * inv) % P for x in M[r]]
        for i in range(n):
            if i != r and M[i][c]:
                z = M[i][c]
                M[i] = [(M[i][j] - z * M[r][j]) % P for j in range(n + 1)]
        pivots.append(c)
        r += 1
    assert not any(all(M[i][j] == 0 for j in range(n)) and M[i][n] for i in range(r, n))
    free = [j for j in range(n) if j not in pivots]
    r0 = [0] * n
    for i, c in enumerate(pivots):
        r0[c] = M[i][n]
    basis = []
    for f in free:
        v = [0] * n
        v[f] = 1
        for i, c in enumerate(pivots):
            v[c] = (-M[i][f]) % P
        basis.append(v)
    rows = [[basis[k][i] for k in range(len(basis))] for i in range(n)]
    return r0, rows, len(pivots)


def canon(v):
    v = tuple(x % P for x in v)
    first = next((x for x in v if x), None)
    if first is None:
        return None
    inv = pow(first, -1, P)
    return tuple((inv * x) % P for x in v)


def projective_line(u, v):
    out = set()
    for a, b in product(range(P), repeat=2):
        if a == 0 and b == 0:
            continue
        w = tuple((a * u[i] + b * v[i]) % P for i in range(len(u)))
        out.add(canon(w))
    assert None not in out and len(out) == 4
    return frozenset(out)


def rank_columns(cols):
    M = [list(row) for row in zip(*cols)]
    return rank_mod(M)


def levi_connected(rows, n):
    adj = [[] for _ in range(2 * n)]
    for i, row in enumerate(rows):
        rr = n + i
        for v in row:
            adj[v].append(rr)
            adj[rr].append(v)
    stack = [0]
    seen = {0}
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == 2 * n


def exactone_count(A):
    n = len(A)
    count = 0
    for C in combinations(range(n), n // 3):
        S = set(C)
        if all(sum(row[j] for j in S) == 1 for row in A):
            count += 1
    return count


def affine_points(r0, brows):
    d = len(brows[0])
    out = []
    for alpha in product(range(P), repeat=d):
        vals = tuple((r0[i] + sum(brows[i][j] * alpha[j] for j in range(d))) % P
                     for i in range(len(r0)))
        out.append((alpha, vals))
    return out


def pcq_profile(r0, brows):
    groups = {}
    for a, b in zip(r0, brows):
        assert any(b), "countercontrol must have no zero normal"
        first = next(x for x in b if x)
        inv = pow(first, -1, P)
        v = tuple((inv * x) % P for x in b)
        # b = first * v, so v alpha = -a/first.
        c = (-a * inv) % P
        groups.setdefault(v, set()).add(c)
    return groups


def main():
    n = 15
    A = matrix_from_rows(ROWS, n)

    assert all(sum(row) == 3 for row in A)
    assert all(sum(A[i][j] for i in range(n)) == 3 for j in range(n))
    assert all(len(set(ROWS[i]) & set(ROWS[j])) <= 1 for i in range(n) for j in range(i))
    assert levi_connected(ROWS, n)
    assert rank_q(A) == 11
    assert rank_mod(A) == 11
    assert exactone_count(A) == 0

    r0, brows, rank = affine_parameterization(A)
    assert rank == 11
    d = len(brows[0])
    assert d == 4

    ap = affine_points(r0, brows)
    assert len(ap) == 81
    zero_sets = []
    for _, vals in ap:
        zeros = tuple(i for i, v in enumerate(vals) if v == 0)
        assert zeros
        zero_sets.append(zeros)

    groups = pcq_profile(r0, brows)
    assert len(groups) == 15
    assert all(len(C) == 1 for C in groups.values())

    pinf = (0,) * d + (1,)
    H = [tuple(brows[i]) + (r0[i],) for i in range(n)]
    points = {canon(h) for h in H}
    assert len(points) == 15
    B = set(points)
    B.add(pinf)
    assert len(B) == 16

    full_lines = set()
    for u, v in combinations(B, 2):
        L = projective_line(u, v)
        if L <= B:
            full_lines.add(L)
    assert not full_lines

    # Exact rooted dependency and nondegenerate four-circuit on every source row.
    for row in ROWS:
        hs = [H[j] for j in row]
        dep = tuple((hs[0][k] + hs[1][k] + hs[2][k] - pinf[k]) % P for k in range(d + 1))
        assert dep == (0,) * (d + 1)
        four = hs + [pinf]
        assert rank_columns(four) == 3
        for triple in combinations(four, 3):
            assert rank_columns(list(triple)) == 3

    # Bitset form of the 15 affine zero hyperplanes over the 81 parameter points.
    covers = []
    for i in range(n):
        mask = 0
        for q, (_, vals) in enumerate(ap):
            if vals[i] == 0:
                mask |= 1 << q
        assert mask.bit_count() == 27
        covers.append(mask)
    FULL = (1 << 81) - 1

    min_size = None
    min_covers = []
    for k in range(1, n + 1):
        for C in combinations(range(n), k):
            mask = 0
            for i in C:
                mask |= covers[i]
            if mask == FULL:
                min_covers.append(C)
        if min_covers:
            min_size = k
            break

    assert min_size == 11
    assert len(min_covers) == 36

    for C in min_covers:
        BC = {canon(H[i]) for i in C}
        BC.add(pinf)
        assert len(BC) == 12
        assert rank_columns(list(BC)) == 5
        for u, v in combinations(BC, 2):
            assert not (projective_line(u, v) <= BC)

    print({
        "status": "PASS_AFFINE_F3_LINE_FREE_PROPER_BLOCKING_SOURCE_COUNTERCONTROL",
        "n": n,
        "rank_Q": 11,
        "rank_F3": 11,
        "affine_dimension": 4,
        "affine_points_checked": 81,
        "exact_one_witnesses": 0,
        "pcq_projective_normal_classes": 15,
        "pcq_pin_classes": 0,
        "pcq_three_offset_classes": 0,
        "homogeneous_source_points": 15,
        "projective_lines_in_full_blocking_set": 0,
        "nondegenerate_rooted_four_circuits": 15,
        "minimum_affine_cover_size": min_size,
        "minimum_affine_covers": len(min_covers),
        "minimum_projective_blocking_size_with_pinf": 12,
        "minimum_cover_projective_rank": 5,
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    })


if __name__ == "__main__":
    main()
