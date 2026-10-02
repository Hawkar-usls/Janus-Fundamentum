#!/usr/bin/env python3
"""Executable algebraic regression for the Exact-One linear-autarky theorem.

This is a theorem-identity checker, not a SAT solver and not a P=NP claim.
"""
from __future__ import annotations

import json


def det3(m: list[list[int]]) -> int:
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
        - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
        + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


def main() -> None:
    positive = [1, 1, 1]
    pair_rows = [
        [-1, -1, 0],
        [-1, 0, -1],
        [0, -1, -1],
    ]

    certificate_identity = [
        2 * positive[j] + sum(row[j] for row in pair_rows)
        for j in range(3)
    ]
    determinant = det3(pair_rows)

    assert certificate_identity == [0, 0, 0]
    assert determinant != 0

    out = {
        "status": "PASS_EXACT_ONE_SIMPLE_LINEAR_AUTARKY_LEAN_THEOREM",
        "standard_exact_one_clause_rows": [positive, *pair_rows],
        "nonnegative_zero_sum_certificate_weights": [2, 1, 1, 1],
        "certificate_identity": certificate_identity,
        "pair_row_determinant": determinant,
        "conclusion": "ONLY_ZERO_SIMPLE_LINEAR_AUTARKY_VECTOR_ON_EVERY_COVERED_VARIABLE",
        "scope": "ARBITRARY_CONJUNCTION_OF_STANDARD_EXACT_ONE_TRIPLES_WITH_NO_ISOLATED_VARIABLES",
        "boundary": {
            "GENERAL_AUTARKY": "NOT_CLOSED_BY_THIS_RESULT",
            "UNIVERSAL_SELECTOR": "OPEN",
            "E8_D1": "EMPTY",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
