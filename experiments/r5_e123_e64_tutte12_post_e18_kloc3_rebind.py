#!/usr/bin/env python3
"""R5 E123: rebind the frozen E64 Tutte-12 q63 UNSAT through E18 and KLOC3."""

from fractions import Fraction
from itertools import combinations, product

from r5_e64_connected_postquotient_nullity_firewall import (
    rank_q,
    rref_q,
    tutte12_incidence,
    two_level_kernel_count,
    verify_square_cubic_linear,
)


def kernel_coordinate_rows(M):
    R, pivots = rref_q(M)
    n = len(M[0])
    free = [c for c in range(n) if c not in pivots]
    B = [[Fraction(0) for _ in free] for _ in range(n)]
    for k, f in enumerate(free):
        B[f][k] = Fraction(1)
        for rr, c in enumerate(pivots):
            B[c][k] = -R[rr][f]
    return B


def proportional(u, v):
    lam = None
    for a, b in zip(u, v):
        if a:
            q = b / a
            if lam is None:
                lam = q
            elif lam != q:
                return None
        elif b:
            return None
    return lam


def local_compatible(B, S):
    M = [B[i] for i in S]
    r = rank_q(M)
    for sig in product((-1, 2), repeat=len(S)):
        aug = [M[t] + [Fraction(sig[t])] for t in range(len(S))]
        if rank_q(aug) == r:
            return True
    return False


def main():
    M = tutte12_incidence()
    assert len(M) == 63
    verify_square_cubic_linear(M, expected_girth=12)

    assert rank_q(M) == 49
    d, count = two_level_kernel_count(M)
    assert d == 14
    assert count == 0
    assert len(M) % 3 == 0

    B = kernel_coordinate_rows(M)
    assert len(B) == 63
    assert all(any(x for x in row) for row in B)

    props = []
    for i, j in combinations(range(63), 2):
        q = proportional(B[i], B[j])
        if q is not None:
            props.append((i, j, q))
    assert props == []

    dependent_triples = 0
    checked = {1: 0, 2: 0, 3: 0}
    for s in (1, 2, 3):
        for S in combinations(range(63), s):
            checked[s] += 1
            if s == 3 and rank_q([B[i] for i in S]) < 3:
                dependent_triples += 1
            assert local_compatible(B, S)

    assert checked == {1: 63, 2: 1953, 3: 39711}
    assert dependent_triples == 63

    print("R5 E123 E64 Tutte-12 post-E18/KLOC3 rebind: PASS")
    print("q=63, rank_Q=49, nullity_Q=14, Exact-One UNSAT")
    print("E18 zero rows=0, proportional pairs=0")
    print("KLOC1/KLOC2/KLOC3: all coordinate subsets clean")
    print("dependent KLOC3 triples=63, all alphabet-compatible")
    print("finite benchmark only; scalable post-router UNSAT remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__ == "__main__":
    main()
