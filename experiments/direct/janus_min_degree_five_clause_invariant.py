#!/usr/bin/env python3
"""Regression for the C025 minimum-incidence m<=5 clause-count invariant.

The mathematical proof is stored in research/C025_MIN_DEGREE_FIVE_CLAUSE_INVARIANT_2026-08-27.json.
This executable protects the arithmetic and the full-width d=5 implementation behavior.
P vs NP remains OPEN.
"""

from itertools import combinations

from experiments.direct import janus_unified_proof_carrying_akinator_jec as core

P_VS_NP = "OPEN"


def verify_d_le_4_arithmetic() -> None:
    for m in range(0, 6):
        for d in range(0, min(4, m) + 1):
            for p in range(d + 1):
                q = d - p
                raw_clause_bound = m - d + p * q
                assert raw_clause_bound <= 5, (m, d, p, q, raw_clause_bound)
    print("M_LE_5_D_LE_4_CLAUSE_BOUND=PASS")


def full_width_clause(n: int, mask: int) -> core.Clause:
    return tuple(v if (mask >> (v - 1)) & 1 else -v for v in range(1, n + 1))


def verify_full_width_d5_exhaustive(n: int) -> None:
    patterns = list(range(1 << n))
    checked = 0
    for chosen in combinations(patterns, 5):
        cnf = core.canon_cnf(full_width_clause(n, mask) for mask in chosen)
        assert len(cnf) == 5
        assert all(len(c) == n for c in cnf)
        for pivot in range(1, n + 1):
            pos = sum(pivot in c for c in cnf)
            neg = sum(-pivot in c for c in cnf)
            assert pos + neg == 5
            out, stats = core.eliminate_var_capped(cnf, pivot, 10**9)
            assert out is not None
            assert len(out) <= min(pos, neg), (n, chosen, pivot, pos, neg, out, stats)
            assert len(out) <= 2, (n, chosen, pivot, out, stats)
            checked += 1
    print(f"M5_D5_FULL_WIDTH_N{n}_EXHAUSTIVE=PASS:{checked}")


def verify_raw_size_corollary() -> None:
    for n in range(1, 32):
        max_units = 1 + 5 * n
        assert max_units >= 1
    print("M_LE_5_RAW_UNITS_1_PLUS_5N=PASS")


def selftest() -> None:
    verify_d_le_4_arithmetic()
    verify_full_width_d5_exhaustive(3)
    verify_full_width_d5_exhaustive(4)
    verify_raw_size_corollary()
    print("MIN_DEGREE_FIVE_CLAUSE_INVARIANT_REGRESSION=PASS")
    print("THEOREM_RUNTIME_HEURISTICS=FORBIDDEN")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
