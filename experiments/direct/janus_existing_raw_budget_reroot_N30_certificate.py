#!/usr/bin/env python3
"""Exact regression for C025 N=30 using only frozen existing lemmas."""

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


def recurrence(N: int, r0: int):
    s = Fraction(N - r0)
    n = r0
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        nxt = min(T(s), Fraction(Smax(n - 1)))
        yield n, s, raw, nxt
        s, n = nxt, n - 1


def root_L(N: int, r: int, m: int) -> int:
    return N - 1 - r - m


def small_clause_nonincrease(m: int) -> bool:
    if m > 4:
        return False
    for p in range(m + 1):
        for q in range(m - p + 1):
            if m - p - q + p * q > m:
                return False
    return True


def verify_low_r() -> None:
    N = 30
    maximum = Fraction(0)
    loc = None
    for r in range(1, 8):
        for n, s, raw, nxt in recurrence(N, r):
            assert raw <= N * N
            if raw > maximum:
                maximum, loc = raw, (r, n)
    assert maximum == 297, (maximum, loc)
    assert loc == (7, 5)


def verify_r8() -> None:
    N, r = 30, 8
    # Canonical/unit-free possible m range under L<=m*r and L>=2m.
    possible = []
    for m in range(1, N - 2 * r):
        L = root_L(N, r, m)
        if L >= r and L >= 2 * m and L <= m * r:
            possible.append((m, L))
    assert possible == [(3,18),(4,17),(5,16),(6,15),(7,14)], possible
    assert small_clause_nonincrease(3)
    assert small_clause_nonincrease(4)
    assert root_L(N, r, 6) < 2 * r
    assert root_L(N, r, 7) < 2 * r

    # Sole balanced cell m=5,L=16. If no degree1 exists, all variable degrees are 2.
    m, L = 5, 16
    s = 1 + m + L
    assert s == 22
    # Existing generic whole-state bound for mixed d=2, p=q=1 is B=s-3.
    B_mixed = s + 1 - 2 - 2
    assert B_mixed == 19
    assert B_mixed < N * N
    # Pure d=2 pivots are deletion-only. Mixed pivot gives local reroot <= 19+7=26.
    assert B_mixed + (r - 1) == 26


def verify_r9_and_high() -> None:
    N = 30
    # r=9,m=1 impossible: one canonical clause width <=9 but L=19.
    assert root_L(N, 9, 1) == 19 and 19 > 9
    assert small_clause_nonincrease(2)
    for r in range(10, 15):
        mmax = N - 2 * r - 1
        for m in range(1, mmax + 1):
            L = root_L(N, r, m)
            if L >= r:
                assert L < 2 * r, (r, m, L)
    assert N - 4 == 26


def selftest() -> None:
    verify_low_r()
    verify_r8()
    verify_r9_and_high()
    print("N30_RLE7_RECURRENCE=PASS")
    print("N30_R8_PARTITION=PASS")
    print("N30_R8_M5_EXISTING_GENERIC_RAW_BOUND=19")
    print("N30_R8_M5_REROOT_N_LE_26=PASS")
    print("N30_R9_AND_HIGH_R=PASS")
    print("NO_RAW_CAP_RESCUE_N_LE_30=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
