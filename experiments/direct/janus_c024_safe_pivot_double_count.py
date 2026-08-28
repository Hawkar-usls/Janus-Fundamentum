#!/usr/bin/env python3
"""Finite pair-type checker for C024 SAFE_PIVOT_DOUBLE_COUNT.

This script is a sanity checker for the local combinatorial identity used by the
C024 proof candidate. It is not the theorem authority by itself.
"""

from itertools import product
from math import comb

P_VS_NP = "OPEN"


def opposite_count(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return sum(1 for x, y in zip(a, b) if x and y and x == -y)


def direct_non_taut_pivot_incidences(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    out = 0
    for i, (x, y) in enumerate(zip(a, b)):
        if not (x and y and x == -y):
            continue
        other_opposite = any(
            j != i and aa and bb and aa == -bb
            for j, (aa, bb) in enumerate(zip(a, b))
        )
        if not other_opposite:
            out += 1
    return out


def pair_type_exhaustive_check(n: int = 7) -> dict:
    clauses = [c for c in product((-1, 0, 1), repeat=n) if any(c)]
    checked = 0
    type_counts = [0] * (n + 1)
    for i, a in enumerate(clauses):
        for b in clauses[i + 1 :]:
            checked += 1
            t = opposite_count(a, b)
            type_counts[t] += 1
            direct = direct_non_taut_pivot_incidences(a, b)
            expected = 1 if t == 1 else 0
            if direct != expected:
                raise AssertionError((a, b, t, direct, expected))
    return {
        "n": n,
        "signed_nonempty_clause_types": len(clauses),
        "unordered_clause_type_pairs_checked": checked,
        "opposite_count_histogram": type_counts,
        "pairwise_identity": "PASS",
    }


def arithmetic_gate() -> dict:
    n = 7
    m = 79
    L = 350
    d_min = 50
    N = 58

    assert L == n * d_min
    retained = m - d_min
    pair_cap = comb(m, 2)
    non_taut_pairs_for_some_pivot = pair_cap // n
    raw_clause_cap = retained + non_taut_pairs_for_some_pivot
    raw_units_cap = 1 + raw_clause_cap + (n - 1) * raw_clause_cap
    cap = N * N

    assert pair_cap == 3081
    assert non_taut_pairs_for_some_pivot == 440
    assert retained == 29
    assert raw_clause_cap == 469
    assert raw_units_cap == 3284
    assert raw_units_cap < cap == 3364

    return {
        "state": [n, m, L],
        "minimum_degree": d_min,
        "all_degrees_forced_equal": True,
        "retained_clause_count": retained,
        "unordered_clause_pair_cap": pair_cap,
        "pigeonhole_non_taut_parent_pair_cap": non_taut_pairs_for_some_pivot,
        "raw_clause_cap": raw_clause_cap,
        "raw_units_cap": raw_units_cap,
        "N": N,
        "N_squared_cap": cap,
        "margin": cap - raw_units_cap,
        "arithmetic_gate": "PASS",
    }


def main() -> None:
    finite = pair_type_exhaustive_check(7)
    arithmetic = arithmetic_gate()
    print(f"C024_PAIR_TYPE_IDENTITY={finite['pairwise_identity']}")
    print(f"C024_PAIR_TYPES={finite['signed_nonempty_clause_types']}")
    print(f"C024_UNORDERED_TYPE_PAIRS={finite['unordered_clause_type_pairs_checked']}")
    print(f"C024_RAW_UNITS_CAP={arithmetic['raw_units_cap']}")
    print(f"C024_N58_CAP={arithmetic['N_squared_cap']}")
    print(f"C024_MARGIN={arithmetic['margin']}")
    print("C024_STATUS=PROOF_CANDIDATE_NOT_ADMITTED")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
