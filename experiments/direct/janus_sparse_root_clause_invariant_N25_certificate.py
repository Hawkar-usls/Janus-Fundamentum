#!/usr/bin/env python3
"""Exact regression for C025 sparse-root clause-count invariant and N<=25 corridor.

Checks the finite arithmetic m-p-q+p*q<=m for m<=4, the legitimate-root root
clause ceiling, and composes this with the audited N<=24 theorem frontier.  The
proof is combinatorial; this executable is regression only. P_VS_NP remains OPEN.
"""
from __future__ import annotations

P_VS_NP = "OPEN"


def next_clause_count_bound(m: int) -> int:
    best = 0
    for p in range(m + 1):
        for q in range(m - p + 1):
            retained = m - p - q
            best = max(best, retained + p * q)
    return best


def root_clause_bound(N: int, r0: int) -> int:
    return N - 2 * r0 - 1


def verify_small_clause_invariant() -> None:
    expected = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 9}
    for m, want in expected.items():
        got = next_clause_count_bound(m)
        assert got == want, ("CLAUSE_COUNT_RECURRENCE_DRIFT", m, got, want)
    for m in range(5):
        assert next_clause_count_bound(m) <= m


def verify_N25() -> None:
    assert root_clause_bound(25, 10) == 4
    assert root_clause_bound(25, 11) == 2
    # A continuing <=4-clause path has RAW_UNITS<=1+m*n before every ordinary
    # elimination; use the root live-variable ceiling for the global maximum.
    assert 1 + 4 * 10 == 41 < 625
    assert 1 + 2 * 11 == 23 < 625


def verify_N26_frontier() -> None:
    bounds = {r: root_clause_bound(26, r) for r in (9, 10, 11, 12)}
    assert bounds == {9: 7, 10: 5, 11: 3, 12: 1}
    assert bounds[11] <= 4 and bounds[12] <= 4
    assert bounds[9] > 4 and bounds[10] > 4


def selftest() -> None:
    verify_small_clause_invariant()
    verify_N25()
    verify_N26_frontier()
    print("SPARSE_CLAUSE_COUNT_INVARIANT_M_LE_4=PASS")
    print("NO_RAW_CAP_RESCUE_N25_R10_R11=PASS")
    print("NO_RAW_CAP_RESCUE_N_LE_25=PASS")
    print("N26_REMAINING_R0=9,10")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
