#!/usr/bin/env python3
"""Exact-rational regression for the C025 iterated envelope corridor through N=19.

Uses fractions only.  Confirms that every allowed root-variable budget for each
N<=19 stays under N^2 for enough ordinary eliminations, and that the same
sufficient recurrence intentionally becomes uncertified at N=20,r0=4.

This validates the arithmetic boundary; it does not turn recurrence failure at
N=20 into an algorithm failure. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from fractions import Fraction

P_VS_NP = "OPEN"


def T(s: Fraction) -> Fraction:
    return max(s, Fraction(1) + (s - 1) * (s - 1) / 12)


def trajectory(N: int, r0: int) -> list[Fraction]:
    if r0 < 1:
        raise ValueError("r0 must be positive")
    s = Fraction(N - r0)
    out = [s]
    for _ in range(r0):
        s = T(s)
        out.append(s)
    return out


def allowed_r0(N: int) -> range:
    return range(2, (N - 2) // 2 + 1)


def verify_through_N19() -> dict[int, Fraction]:
    maxima: dict[int, Fraction] = {}
    for N in range(4, 20):
        cap = Fraction(N * N)
        max_seen = Fraction(0)
        for r0 in allowed_r0(N):
            seq = trajectory(N, r0)
            # For r0 eliminations, every next-state envelope must fit the same cap.
            for value in seq[1:]:
                if value > cap:
                    raise AssertionError(("UNEXPECTED_ENVELOPE_ESCAPE_BELOW_20", N, r0, value, cap))
                max_seen = max(max_seen, value)
        maxima[N] = max_seen
    return maxima


def verify_small_closed_form() -> None:
    for N in range(4, 16):
        for r0 in allowed_r0(N):
            s0 = Fraction(N - r0)
            assert s0 <= 13
            assert T(s0) == s0


def verify_N20_negative_control() -> tuple[list[Fraction], int]:
    N, r0 = 20, 4
    seq = trajectory(N, r0)
    cap = Fraction(N * N)
    first_escape = next((i for i, value in enumerate(seq[1:], start=1) if value > cap), None)
    if first_escape is None:
        raise AssertionError("N20_R4_WAS_EXPECTED_TO_ESCAPE_THE_SUFFICIENT_RECURRENCE")
    # This is only a certificate failure, never an actual CNF/solver failure.
    return seq, first_escape


def selftest() -> None:
    verify_small_closed_form()
    maxima = verify_through_N19()
    seq20, escape20 = verify_N20_negative_control()

    expected_rounded = {
        16: 17.528357,
        17: 23.765548,
        18: 44.189179,
        19: 156.442097,
    }
    for N, expected in expected_rounded.items():
        actual = round(float(maxima[N]), 6)
        if actual != expected:
            raise AssertionError(("PUBLISHED_MAXIMUM_DRIFT", N, actual, expected, maxima[N]))

    print("ITERATED_UNIT_FREE_ENVELOPE_N_LE_19=PASS")
    for N in (16, 17, 18, 19):
        print(f"N{N}_MAX_ENVELOPE={float(maxima[N]):.6f}")
        print(f"N{N}_CAP={N*N}")
    print(f"N20_R4_FIRST_UNCERTIFIED_STEP={escape20}")
    print(f"N20_R4_ESCAPE_ENVELOPE={float(seq20[escape20]):.6f}")
    print("N20_RECURRENCE_FAILURE_IS_NOT_SOLVER_FAILURE=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
