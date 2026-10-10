#!/usr/bin/env python3
"""Exact small-matrix checker for the Boben local semantic state barrier."""

from fractions import Fraction
from itertools import product


def rank_q(M):
    a = [[Fraction(v) for v in row] for row in M]
    m = len(a)
    n = len(a[0]) if m else 0
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, m) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [v / pv for v in a[r]]
        for i in range(m):
            if i != r and a[i][c]:
                f = a[i][c]
                a[i] = [a[i][j] - f * a[r][j] for j in range(n)]
        r += 1
    return r


def boolean_rank_isolated_support_lower_bound(M):
    """For the frozen matrices, prove Boolean rank by disjoint row supports.

    If every nonzero row has support disjoint from every other nonzero row,
    a Boolean rank-1 rectangle cannot cover 1s from two such rows without
    introducing a false 1. Hence Boolean rank equals # nonzero rows.
    """
    supports = [{j for j, v in enumerate(row) if v} for row in M]
    nz = [s for s in supports if s]
    for i in range(len(nz)):
        for j in range(i):
            assert nz[i].isdisjoint(nz[j])
    return len(nz)


def adjacent_matrix(pairing):
    tuples = []
    for a, b, c, d, s in product((0, 1), repeat=5):
        if a == b == s and c + d + s == 1:
            tuples.append((a, b, c, d))
    tuples = sorted(set(tuples))
    assert tuples == [(0, 0, 0, 1), (0, 0, 1, 0), (1, 1, 0, 0)]

    states = [(0, 0), (0, 1), (1, 0), (1, 1)]
    idx = {s: i for i, s in enumerate(states)}
    M = [[0] * 4 for _ in range(4)]
    left, right = pairing
    for t in tuples:
        u = (t[left[0]], t[left[1]])
        v = (t[right[0]], t[right[1]])
        M[idx[u]][idx[v]] = 1
    return M


def nonadjacent_matrix():
    states = [(0, 0), (0, 1), (1, 0), (1, 1)]
    idx = {s: i for i, s in enumerate(states)}
    pair_states = list(product(states, repeat=2))
    idx2 = {s: i for i, s in enumerate(pair_states)}

    allowed = []
    for triple in product(states, repeat=3):
        first = [s[0] for s in triple]
        second = [s[1] for s in triple]
        if len(set(first)) == 1 and sum(second) == 1:
            allowed.append(triple)
    assert len(allowed) == 6

    M = [[0] * 16 for _ in range(4)]
    for s1, s2, s3 in allowed:
        M[idx[s1]][idx2[(s2, s3)]] = 1
    return M, allowed


def main():
    expected_adj = [
        [0, 1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
    ]

    for pairing in [((0, 2), (1, 3)), ((0, 3), (1, 2))]:
        M = adjacent_matrix(pairing)
        assert M == expected_adj
        assert rank_q(M) == 3
        assert boolean_rank_isolated_support_lower_bound(M) == 3

    M, allowed = nonadjacent_matrix()
    assert rank_q(M) == 4
    assert boolean_rank_isolated_support_lower_bound(M) == 4
    assert allowed == [
        ((0, 0), (0, 0), (0, 1)),
        ((0, 0), (0, 1), (0, 0)),
        ((0, 1), (0, 0), (0, 0)),
        ((1, 0), (1, 0), (1, 1)),
        ((1, 0), (1, 1), (1, 0)),
        ((1, 1), (1, 0), (1, 0)),
    ]

    print('PASS R5_E9_BOBEN_LOCAL_BOND_DIMENSION_BARRIER')
    print('adjacent ordinary_rank = 3, boolean_rank = 3')
    print('nonadjacent 1|2 ordinary_rank = 4, boolean_rank = 4')
    print('TWO_STATE_EXACT_BOBEN_LIFT = FALSIFIED_LOCALLY')
    print('GLOBAL_SIGNATURE_CLOSURE = OPEN')
    print('P_VS_NP = OPEN')


if __name__ == '__main__':
    main()
