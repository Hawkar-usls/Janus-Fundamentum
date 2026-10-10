#!/usr/bin/env python3
"""Finite regression for the U-PAIR-1F majority-projection proof.

This checks only finite instances of the two symbolic lemmas:
(1) majority true-points have full GF(2) affine hull;
(2) the number of maximal false assignments is binom(n,t-1), matching the
    clause lower-bound witness count.
The asymptotic theorem is mathematical, not inferred from these runs.
"""

from itertools import product
from math import comb


def affine_dim(points):
    points = [tuple(int(x) for x in p) for p in points]
    base = points[0]
    rows = [[a ^ b for a, b in zip(p, base)] for p in points[1:]]
    if not rows:
        return 0
    rank = 0
    width = len(base)
    for c in range(width):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i][c]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[rank])]
        rank += 1
    return rank


def run_case(n):
    t = (n + 1) // 2
    universe = list(product([0, 1], repeat=n))
    true_points = [a for a in universe if sum(a) >= t]
    maximal_false = [a for a in universe if sum(a) == t - 1]

    assert affine_dim(true_points) == n
    assert len(maximal_false) == comb(n, t - 1)

    # Distinct maximal-false assignments have distinct zero sets, so the proof
    # associates a distinct mandatory falsified clause to each one.
    zero_sets = {tuple(i for i, bit in enumerate(a) if bit == 0) for a in maximal_false}
    assert len(zero_sets) == len(maximal_false)
    return t, len(maximal_false)


if __name__ == "__main__":
    for n in range(4, 13):
        t, count = run_case(n)
        print(f"n={n:2d} threshold={t:2d} maximal_false={count:5d} affine_hull_dim={n}")
    print("PASS: finite majority-projection regression")
    print("CLAIM CEILING: finite regression only; GENERAL_SAT_IN_P remains NOT_PROVED; P_VS_NP remains OPEN")
