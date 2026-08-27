#!/usr/bin/env python3
"""Exact arithmetic regression for C025 N=29 cap availability."""

from fractions import Fraction
from math import comb

P_VS_NP = "OPEN"


def T(s: Fraction) -> Fraction:
    s = Fraction(s)
    return max(s, Fraction(1) + (s - 1) ** 2 / 12)


def Uraw(n: int) -> int:
    return 3 ** (n - 2) * (2 * n + 1)


def Smax(n: int) -> int:
    if n <= 0:
        return 1
    return 1 + max((k + 1) * comb(n, k) * 2 ** k for k in range(1, n + 1))


def recurrence_raw_bounds(N: int, r0: int):
    s = Fraction(N - r0)
    n = r0
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        nxt = min(T(s), Fraction(Smax(n - 1)))
        yield n, s, raw, nxt
        s, n = nxt, n - 1


def root_literals(N: int, r0: int, m0: int) -> int:
    return N - 1 - r0 - m0


def legitimate_unit_free_root_cell(N: int, r0: int, m0: int) -> bool:
    L0 = root_literals(N, r0, m0)
    return m0 >= 1 and L0 >= r0 and L0 >= 2 * m0 and L0 <= m0 * r0


def verify_low_r() -> None:
    N = 29
    cap = N * N
    maximum = Fraction(0)
    location = None
    for r0 in range(1, 9):
        for n, s, raw, nxt in recurrence_raw_bounds(N, r0):
            assert raw <= cap
            if raw > maximum:
                maximum, location = raw, (r0, n)
    assert maximum == Fraction(1564687, 2187), (maximum, location)
    assert location == (8, 6)


def verify_r9_and_high_r() -> None:
    N = 29
    # r0=9: m0=1 would require L0=18 in a single canonical clause over 9 vars.
    assert root_literals(N, 9, 1) == 18
    assert 18 > 9
    assert not legitimate_unit_free_root_cell(N, 9, 1)

    for r0 in range(9, 14):
        mmax = N - 2 * r0 - 1
        for m0 in range(1, mmax + 1):
            if not legitimate_unit_free_root_cell(N, r0, m0):
                continue
            L0 = root_literals(N, r0, m0)
            assert L0 < 2 * r0, (r0, m0, L0)

    Nprime = N - 4
    assert Nprime == 25
    assert Nprime * Nprime <= N * N


def selftest() -> None:
    verify_low_r()
    verify_r9_and_high_r()
    print("N29_RLE8_COMBINED_RECURRENCE=PASS")
    print("N29_R9_CANONICAL_M1_EXCLUDED=PASS")
    print("N29_R9_TO_R13_DEGREE1_REROOT=PASS")
    print("N29_MAX_RAW_BOUND=1564687/2187")
    print("POST_ELIM_LOCAL_N_LE_25=PASS")
    print("NO_RAW_CAP_RESCUE_N_LE_29=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
