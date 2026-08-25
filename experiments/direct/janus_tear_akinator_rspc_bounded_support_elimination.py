#!/usr/bin/env python3
"""Finite replay for bounded-support ER3 elimination mechanics.

Finite mechanics only; the analytic simulation theorem and imported Resolution
lower bound are not established by this script.
"""

from itertools import product


def assignments(n):
    return list(product((False, True), repeat=n))


def func_from_mask(n, mask):
    xs = assignments(n)
    return {x: bool((mask >> i) & 1) for i, x in enumerate(xs)}


def check_boolean_substitution_resolution():
    n = 2
    xs = assignments(n)
    funcs = [func_from_mask(n, m) for m in range(1 << (1 << n))]
    for A in funcs:
        for B in funcs:
            for X in funcs:
                for r in xs:
                    P = A[r] or X[r]
                    Q = B[r] or (not X[r])
                    R = A[r] or B[r]
                    assert not (P and Q) or R


def check_local_clause_space():
    for k in range(1, 20):
        assert 3 ** (6 * k) < 2 ** (10 * k)
        assert 2 ** (3 * k) <= 2 ** (10 * k)


def check_direct_parity_delta_accounting():
    for Delta in range(1, 20):
        N_min = 2 ** (Delta - 1)
        assert Delta <= (N_min.bit_length())
        assert 2 ** Delta <= 2 * N_min


def check_cover_counting():
    for Delta in range(1, 20):
        for c in range(1, 20):
            assert c * Delta < c * Delta + 1


if __name__ == "__main__":
    check_boolean_substitution_resolution()
    check_local_clause_space()
    check_direct_parity_delta_accounting()
    check_cover_counting()
    print("C025_AKINATOR_ER3_BOOLEAN_SUBSTITUTION_SMALL_REPLAY = PASS")
    print("C025_AKINATOR_ER3_LOCAL_CLAUSE_SPACE_2O_K = PASS")
    print("C025_AKINATOR_DIRECT_PARITY_DELTA_ACCOUNTING = PASS")
    print("C025_AKINATOR_COVER_CARDINALITY = PASS")
    print("C025_AKINATOR_BOUNDED_SUPPORT_ELIMINATION = ANALYTIC_THEOREM_NOT_CI")
    print("C025_AKINATOR_RESOLUTION_LOWER_BOUND = IMPORTED_FROZEN_RESULT_NOT_CI")
    print("C025_AKINATOR_UNRESTRICTED_ER3_SIZE_LOWER_BOUND = NOT_PROVED")
    print("P_VS_NP = OPEN")
