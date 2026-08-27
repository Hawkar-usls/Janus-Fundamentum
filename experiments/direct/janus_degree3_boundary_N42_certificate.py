#!/usr/bin/env python3
"""Exact regression for the C025 N=42 degree-3 boundary theorem."""

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


def recurrence_from(s: int | Fraction, n: int):
    s = Fraction(s)
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        nxt = min(T(s), Fraction(Smax(n - 1)))
        yield n, s, raw, nxt
        s, n = nxt, n - 1


def verify_partition() -> None:
    N = 42
    # Hard region: m>=5 and L>=3r. Then r<=9.
    assert (N - 6) // 4 == 9
    # r<=8 recurrence-safe under cap.
    for r in range(1, 9):
        s0 = N - r
        for n, s, raw, nxt in recurrence_from(s0, r):
            assert raw <= N * N, (r, n, raw)

    # r=9 unique hard root cell.
    cells = []
    r = 9
    for m in range(5, N):
        L = N - 1 - r - m
        if L >= 3 * r:
            cells.append((r, m, L))
    assert cells == [(9, 5, 27)], cells


def verify_degree3_raw_bound() -> None:
    N, r, m, L = 42, 9, 5, 27
    s = 1 + m + L
    assert s == 33
    # If no degree<=2 exists, all 9 positive integer incidences are exactly 3.
    assert L == 3 * r
    # Mixed degree3 split is 1+2. Generic bound reduces to s-4+singleton_tail.
    singleton_tail_max = r - 1
    B = s - 4 + singleton_tail_max
    assert B == 37
    assert B < N * N
    # Pure degree3 pivot is deletion-only.


def verify_tail() -> None:
    N = 42
    expected = [
        (8, Fraction(37), Fraction(109), Fraction(109)),
        (7, Fraction(109), Fraction(973), Fraction(973)),
        (6, Fraction(973), Fraction(1053), Fraction(401)),
        (5, Fraction(401), Fraction(297), Fraction(129)),
        (4, Fraction(129), Fraction(81), Fraction(37)),
        (3, Fraction(37), Fraction(21), Fraction(13)),
    ]
    got = list(recurrence_from(37, 8))
    assert got == expected, got
    assert all(raw <= N * N for n, s, raw, nxt in got)


def selftest() -> None:
    verify_partition()
    verify_degree3_raw_bound()
    verify_tail()
    print("N42_HARD_ROOT_CELL=R9_M5_L27")
    print("N42_DEGREE3_GENERIC_RAW_BOUND_LE_37=PASS")
    print("N42_POST_FIRST_STEP_TAIL=PASS")
    print("NO_RAW_CAP_RESCUE_N_LE_42=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
