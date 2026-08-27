#!/usr/bin/env python3
"""Exact regression for C025 signed-LYM + unique raw-universe corridor through N=24.

The theorem authority is combinatorial.  This executable checks:
  1) exact Smax/Uraw arithmetic identities and published small values;
  2) frozen canon_cnf outputs satisfy the Smax bound on a broad small corpus;
  3) actual frozen eliminate_var_capped raw_units satisfy Uraw on unit-free states;
  4) exact-Fraction combined recurrence closes every allowed r0 for N<=24 and
     first becomes uncertified at N=25 exactly for r0 in {10,11} at live n=6.

Finite implementation checks are not a universal theorem. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from math import comb

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

P_VS_NP = "OPEN"


def Smax(n: int) -> int:
    if n <= 0:
        return 1
    return 1 + max((k + 1) * comb(n, k) * (2 ** k) for k in range(1, n + 1))


def Uraw(n: int) -> int:
    if n < 2:
        raise ValueError("ordinary raw-universe bound is used for n>=2")
    return (3 ** (n - 2)) * (2 * n + 1)


def Uraw_direct(n: int) -> int:
    m = n - 1
    return 1 + sum((k + 1) * comb(m, k) * (2 ** k) for k in range(1, m + 1))


def T(s: Fraction) -> Fraction:
    s = Fraction(s)
    return max(s, Fraction(1) + (s - 1) * (s - 1) / 12)


def run_combined(N: int, r0: int):
    n = r0
    s = Fraction(min(N - r0, Smax(r0)))
    rows = []
    while n > 2:
        raw = min(T(s), Fraction(Uraw(n)))
        rows.append((n, s, raw))
        if raw > N * N:
            return False, rows
        s = min(T(s), Fraction(Smax(n - 1)))
        n -= 1
    return True, rows


def verify_arithmetic() -> None:
    expected_smax = {1: 5, 2: 13, 3: 37, 4: 129, 5: 401, 6: 1201, 7: 4033, 8: 12545}
    expected_uraw = {3: 21, 4: 81, 5: 297, 6: 1053, 7: 3645, 8: 12393}
    for n, v in expected_smax.items():
        assert Smax(n) == v, ("SMAX_DRIFT", n, Smax(n), v)
    for n, v in expected_uraw.items():
        assert Uraw(n) == v, ("URAW_DRIFT", n, Uraw(n), v)
        assert Uraw_direct(n) == v, ("URAW_IDENTITY_DRIFT", n, Uraw_direct(n), v)


def signed_clause_universe(n: int, *, min_width: int = 1):
    rows = set()
    variables = tuple(range(1, n + 1))
    for k in range(min_width, n + 1):
        for support in combinations(variables, k):
            for mask in range(1 << k):
                c = tuple(v if ((mask >> i) & 1) else -v for i, v in enumerate(support))
                cc = base.canon_clause(c)
                assert cc is not None
                rows.add(cc)
    return tuple(sorted(rows, key=lambda c: (len(c), c)))


def verify_small_canonical_and_raw() -> tuple[int, int]:
    # n=3 is enough for a broad exact implementation cross-check while keeping
    # combinations compact. Canonicalization may subsume raw selected rows.
    U = signed_clause_universe(3, min_width=1)
    seen = set()
    states = 0
    pivots = 0
    for k in (1, 2, 3, 4):
        for rows in combinations(U, k):
            cnf = base.canon_cnf(rows)
            if not cnf or cnf in seen:
                continue
            seen.add(cnf)
            n = len(base.vars_of(cnf))
            assert base.state_units(cnf) <= Smax(n), ("SMAX_IMPLEMENTATION_FAILURE", cnf, n)
            states += 1
            if any(len(c) < 2 for c in cnf):
                continue
            cap = 100000
            for x in base.vars_of(cnf):
                out, stats = base.eliminate_var_capped(cnf, x, cap)
                assert out is not None
                raw = int(stats["raw_units"])
                assert raw <= Uraw(n), ("URAW_IMPLEMENTATION_FAILURE", cnf, x, raw, Uraw(n))
                assert base.verify_elimination_transition(cnf, x, out, cap)
                pivots += 1
    return states, pivots


def verify_range() -> tuple[dict[int, Fraction], dict[int, list]]:
    maxima = {}
    failures = {}
    for N in range(4, 26):
        max_raw = Fraction(0)
        bad = []
        for r0 in range(2, (N - 2) // 2 + 1):
            ok, rows = run_combined(N, r0)
            for _, _, raw in rows:
                max_raw = max(max_raw, raw)
            if not ok:
                bad.append((r0, rows[-1]))
        maxima[N] = max_raw
        failures[N] = bad

    for N in range(4, 25):
        assert failures[N] == [], ("UNEXPECTED_FAILURE_BELOW_25", N, failures[N])
    assert [r for r, _ in failures[25]] == [10, 11], failures[25]
    assert all(row[0] == 6 for _, row in failures[25])
    assert maxima[24] == 297
    return maxima, failures


def selftest() -> None:
    verify_arithmetic()
    states, pivots = verify_small_canonical_and_raw()
    maxima, failures = verify_range()

    r10 = next(row for r, row in failures[25] if r == 10)
    r11 = next(row for r, row in failures[25] if r == 11)
    assert r10[1] == Fraction(33468023061889, 235092492288)
    assert round(float(r10[1]), 6) == 142.361088
    assert round(float(r11[1]), 6) == 156.442097
    assert r10[2] == 1053 and r11[2] == 1053

    print(f"SIGNED_LYM_SMALL_CANONICAL_STATES={states}")
    print(f"RAW_UNIVERSE_SMALL_PIVOTS={pivots}")
    print("SMAX_ARITHMETIC=PASS")
    print("URAW_ARITHMETIC_AND_FROZEN_ACCOUNTING=PASS")
    print("COMBINED_CAP_CORRIDOR_N_LE_24=PASS")
    print("N25_UNCERTIFIED_R0=10,11")
    print("N25_IS_UNCERTIFIED_NOT_FAILED=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
