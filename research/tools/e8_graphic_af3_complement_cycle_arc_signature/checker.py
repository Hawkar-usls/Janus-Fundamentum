#!/usr/bin/env python3
from itertools import product
from math import comb

F3 = (0, 1, 2)  # 2 == -1 mod 3
NZ = (1, 2)


def feasible(k):
    return [s for s in product(NZ, repeat=k) if sum(s) % 3 == 0]


def main():
    tri = feasible(3)
    assert tri == [(1, 1, 1), (2, 2, 2)], tri

    c4 = feasible(4)
    assert len(c4) == comb(4, 2) == 6
    for s in c4:
        assert s.count(1) == 2 and s.count(2) == 2

    # Any affine GF(3) subspace/coset has size 3^d.
    affine_sizes = {3 ** d for d in range(10)}
    assert len(c4) not in affine_sizes

    # General count identity through a finite control range.
    for k in range(1, 13):
        states = feasible(k)
        expected = sum(comb(k, r) for r in range(k + 1) if (2 * r - k) % 3 == 0)
        assert len(states) == expected, (k, len(states), expected)

    # Triangle collapse: equality of first two nonzero arc sums plus telescoping
    # forces the third to the same value in GF(3).
    for a in NZ:
        b = a
        c = (-a - b) % 3
        assert c == a and c in NZ

    print("PASS: triangle one-sign signature; C4 EXACT2_4 six-state nonaffine boundary verified")


if __name__ == "__main__":
    main()
