#!/usr/bin/env python3
"""Exact F3 basis census for the PG15 augmented-ternary support-width barrier."""

from itertools import combinations
from collections import Counter

P = 3
SAT_ROWS = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),(3,4,7),
    (3,5,6),(4,9,13),(4,10,14),(5,8,13),(5,10,15),(6,8,14),
    (6,9,15),(7,8,15),(7,11,12),
]


def source():
    return [[int(j + 1 in row) for j in range(15)] for row in SAT_ROWS]


def rref(M):
    A = [[x % P for x in row] for row in M]
    m = len(A); n = len(A[0]); piv = []; r = 0
    for c in range(n):
        q = next((i for i in range(r, m) if A[i][c]), None)
        if q is None: continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, P)
        A[r] = [(x * inv) % P for x in A[r]]
        for i in range(m):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % P for j in range(n)]
        piv.append(c); r += 1
        if r == m: break
    return A, piv


def inverse(B):
    n = len(B)
    A = [[B[i][j] % P for j in range(n)] + [int(i == j) for j in range(n)]
         for i in range(n)]
    for c in range(n):
        q = next((i for i in range(c, n) if A[i][c]), None)
        if q is None: return None
        A[c], A[q] = A[q], A[c]
        inv = pow(A[c][c], -1, P)
        A[c] = [(x * inv) % P for x in A[c]]
        for i in range(n):
            if i != c and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[c][j]) % P for j in range(2 * n)]
    return [row[n:] for row in A]


def mm(X, Y):
    return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) % P
             for j in range(len(Y[0]))] for i in range(len(X))]


def cols(M, J):
    return [[row[j] for j in J] for row in M]


def main():
    A = source()
    M = [row + [2] for row in A]  # [A|-1]
    RR, piv = rref(M)
    rank = len(piv)
    assert rank == 11
    R = RR[:rank]

    total_bases = 0
    syndrome_bases = 0
    hist = Counter()
    hist_synd = Counter()
    sigma = 99
    sigma_synd = 99
    best = None
    best_synd = None

    for Jt in combinations(range(16), rank):
        J = list(Jt)
        inv = inverse(cols(R, J))
        if inv is None:
            continue
        total_bases += 1
        F = mm(inv, R)
        non = [j for j in range(16) if j not in J]
        supports = [(j, sum(F[i][j] != 0 for i in range(rank))) for j in non]
        width = max(s for _, s in supports)
        hist[width] += 1
        if width < sigma:
            sigma = width; best = (J, supports)
        if 15 in J:
            syndrome_bases += 1
            hist_synd[width] += 1
            if width < sigma_synd:
                sigma_synd = width; best_synd = (J, supports)

    assert total_bases == 1904
    assert syndrome_bases == 1220
    assert sigma == 7
    assert sigma_synd == 7
    assert best == (
        [0,1,2,3,4,5,6,7,8,10,12],
        [(9,5),(11,7),(13,5),(14,7),(15,7)],
    )
    assert best_synd == (
        [0,1,2,3,4,5,7,8,10,12,15],
        [(6,7),(9,5),(11,7),(13,5),(14,7)],
    )
    assert sum(hist[w] for w in hist if w <= 6) == 0
    assert sum(hist_synd[w] for w in hist_synd if w <= 6) == 0

    print({
        'status': 'PASS_PG15_AUGMENTED_TERNARY_FUNDAMENTAL_SUPPORT7',
        'rank_F3': rank,
        'bases': total_bases,
        'syndrome_bases': syndrome_bases,
        'sigma': sigma,
        'sigma_syndrome': sigma_synd,
        'width_histogram': dict(sorted(hist.items())),
        'syndrome_width_histogram': dict(sorted(hist_synd.items())),
        'E8_D1': 'EMPTY',
        'P_VS_NP': 'OPEN',
    })


if __name__ == '__main__':
    main()
