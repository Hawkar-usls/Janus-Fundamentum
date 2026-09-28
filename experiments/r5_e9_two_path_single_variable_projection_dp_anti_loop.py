#!/usr/bin/env python3
"""Regression for the exact single-variable-path projection classification.

The checker treats P_i and N_j as truth values of the residual clause bodies.
It exhaustively verifies

    exists x [AND_i (x OR P_i) AND AND_j (!x OR N_j)]
    == AND_{i,j} (P_i OR N_j)

including pure-polarity cases, and verifies the explicit witness reconstruction.
It also checks the sharp clause-count inequality for current degree <= 3.
"""

from __future__ import annotations

from itertools import product
import json


def source_star(x: int, P: tuple[int, ...], N: tuple[int, ...]) -> bool:
    return all(bool(x or p) for p in P) and all(bool((not x) or n) for n in N)


def existential_projection(P: tuple[int, ...], N: tuple[int, ...]) -> bool:
    return source_star(0, P, N) or source_star(1, P, N)


def dp_projection(P: tuple[int, ...], N: tuple[int, ...]) -> bool:
    # Empty Cartesian product = True, exactly the pure-literal case.
    return all(bool(p or n) for p in P for n in N)


def reconstruct_x(P: tuple[int, ...], N: tuple[int, ...]) -> int:
    assert dp_projection(P, N)
    if not N:
        return 1
    if not P:
        return 0
    if all(P):
        return 0
    # Pick any false positive-side body.  Its resolvents force every N_j true.
    assert any(not p for p in P)
    assert all(N)
    return 1


def exhaustive_projection_check(max_p: int = 5, max_q: int = 5) -> int:
    cases = 0
    for p in range(max_p + 1):
        for q in range(max_q + 1):
            for P in product((0, 1), repeat=p):
                for N in product((0, 1), repeat=q):
                    lhs = existential_projection(P, N)
                    rhs = dp_projection(P, N)
                    assert lhs == rhs, (p, q, P, N, lhs, rhs)
                    if rhs:
                        x = reconstruct_x(P, N)
                        assert source_star(x, P, N), (p, q, P, N, x)
                    cases += 1
    return cases


def low_degree_clause_count_check():
    rows = []
    for d in range(0, 7):
        for p in range(d + 1):
            q = d - p
            added = p * q if p and q else 0
            strict_drop = added < d if d > 0 else False
            if 1 <= d <= 3:
                assert strict_drop, (d, p, q, added)
                if p and q:
                    assert added <= d - 1
            rows.append(
                {
                    "degree": d,
                    "p": p,
                    "q": q,
                    "removed": d,
                    "raw_added": added,
                    "strict_clause_drop": strict_drop,
                }
            )

    # Sharp boundary controls.
    assert 2 * 2 == 4  # degree 4, balanced polarity: no forced strict drop.
    assert 3 * 3 == 9 and 9 > 6  # degree 6: raw growth is possible.
    return rows


def main():
    cases = exhaustive_projection_check()
    census = low_degree_clause_count_check()
    out = {
        "status": "PASS_TWO_PATH_SINGLE_VARIABLE_PROJECTION_DP_ANTI_LOOP",
        "exhaustive_truth_cases": cases,
        "exact_projection": "exists x star == all cross-polarity DP resolvents",
        "witness_reconstruction": "PASS",
        "pure_literal_cases": "PASS",
        "low_current_degree_le_3": "STRICT_CLAUSE_COUNT_DROP",
        "degree4_balanced_boundary": "p=q=2 gives pq=d=4",
        "degree6_growth_control": "p=q=3 gives pq=9>d=6",
        "classification": "SINGLE_VARIABLE_PATH_PROJECTION_IS_DAVIS_PUTNAM",
        "next_gate": "R5_E9_TWO_PATH_MULTI_VARIABLE_ALTERNATING_OVERLAY_PIVOT_GATE_V1",
        "degree_census": census,
        "E8_D1": "EMPTY",
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
