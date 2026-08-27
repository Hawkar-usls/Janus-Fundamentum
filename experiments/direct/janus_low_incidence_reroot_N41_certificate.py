#!/usr/bin/env python3
"""Exact regression for the C025 low-incidence reroot induction through N=41.

This checks arithmetic/composition of already-frozen exact lemmas. It changes no
JANUS runtime grammar. P vs NP remains OPEN.
"""

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
    return 1 + max((k + 1) * comb(n, k) * (2 ** k) for k in range(1, n + 1))


def recurrence(N: int, r0: int):
    s = Fraction(N - r0)
    n = r0
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        nxt = min(T(s), Fraction(Smax(n - 1)))
        yield n, s, raw, nxt
        s, n = nxt, n - 1


def hard_r_max(N: int) -> int:
    # m>=5 and L>=3r => N=1+m+L+r >= 6+4r.
    return (N - 6) // 4


def verify_low_incidence_corollary() -> None:
    # L<3r => floor(L/r)<=2. A certified d<=2 pivot exists.
    for r in range(1, 50):
        for L in range(r, 3 * r):
            assert L // r <= 2

    # Existing generic raw lemma for mixed degree-2 p=q=1 gives B=s-3.
    for s in range(5, 100):
        B = s + 1 - 2 - 2
        assert B == s - 3
        # with one live variable removed: local N=s+r -> N'<=s-3+r-1=N-4
        for r in range(1, 20):
            assert B + (r - 1) == (s + r) - 4


def verify_N31_to_N41() -> None:
    expected = {
        31: Fraction(193),
        32: Fraction(392353, 1728),
        33: Fraction(28669, 108),
        34: Fraction(297),
        35: Fraction(19747, 64),
        36: Fraction(9631, 27),
        37: Fraction(709009, 1728),
        38: Fraction(1053),
        39: Fraction(1053),
        40: Fraction(1053),
        41: Fraction(1053),
    }
    for N in range(31, 42):
        rmax = hard_r_max(N)
        maximum = Fraction(0)
        for r0 in range(1, rmax + 1):
            for n, s, raw, nxt in recurrence(N, r0):
                assert raw <= N * N, ("RAW_CAP_FAILURE", N, r0, n, raw, N * N)
                maximum = max(maximum, raw)
        assert maximum == expected[N], (N, maximum, expected[N])
        # <=4-clause corridor raw-size corollary also fits trivially.
        assert 1 + 4 * N <= N * N


def verify_N42_frontier() -> None:
    N = 42
    # r<=8 still recurrence-safe.
    for r0 in range(1, 9):
        for n, s, raw, nxt in recurrence(N, r0):
            assert raw <= N * N

    # In hard region m>=5,L>=3r, the only r=9 root cell is m=5,L=27.
    cells = []
    r0 = 9
    for m0 in range(5, N):
        L0 = N - 1 - r0 - m0
        if L0 >= 3 * r0:
            cells.append((r0, m0, L0))
    assert cells == [(9, 5, 27)], cells

    path = list(recurrence(N, 9))
    stage_n7 = [row for row in path if row[0] == 7]
    assert len(stage_n7) == 1
    n, s, raw, nxt = stage_n7[0]
    assert s == Fraction(16411, 27), s
    assert raw == Fraction(3645), raw
    assert raw > N * N
    # This means only that the coarse sufficient bound loses its certificate.


def selftest() -> None:
    verify_low_incidence_corollary()
    verify_N31_to_N41()
    verify_N42_frontier()
    print("LOW_INCIDENCE_L_LT_3R_REROOT_N_MINUS_4=PASS")
    print("N31_TO_N41_HARD_REGION_RECURRENCE=PASS")
    print("NO_RAW_CAP_RESCUE_N_LE_41=PASS")
    print("N42_FIRST_RESIDUAL_ROOT_CELL=R9_M5_L27")
    print("N42_COARSE_BOUND_LOSES_CERTIFICATE_AT_LIVE_N7=PASS")
    print("N42_ACTUAL_FAILURE=NOT_CLAIMED")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
