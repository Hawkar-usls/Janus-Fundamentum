#!/usr/bin/env python3
"""Exact rational Gram-factor and threshold certificate verifier.

The verifier checks a supplied artifact. It does not search for a factor,
solve an SDP, or prove that short rational certificates always exist.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def rational(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("booleans are not rational scalars")
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise ValueError(f"unsupported rational scalar: {value!r}")


def matrix(payload: list[list[Any]]) -> list[list[Fraction]]:
    rows = [[rational(value) for value in row] for row in payload]
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("matrix must be nonempty and rectangular")
    return rows


def transpose(value: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*value, strict=True)]


def multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    if len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    return [
        [
            sum(
                (left[row][middle] * right[middle][column] for middle in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def verify(payload: dict[str, Any]) -> None:
    claimed = matrix(payload["claimed_psd_matrix"])
    factor = matrix(payload["gram_factor"])
    if len(claimed) != len(claimed[0]):
        raise ValueError("claimed PSD matrix must be square")
    reconstructed = multiply(transpose(factor), factor)
    if reconstructed != claimed:
        raise ValueError("Gram identity B^T B = Q failed")

    for residual in payload.get("linear_residuals", []):
        if rational(residual) != 0:
            raise ValueError("nonzero linear residual")

    objective = rational(payload["objective_value"])
    threshold = rational(payload["threshold"])
    margin = rational(payload["required_margin"])
    relation = payload["relation"]
    if margin < 0:
        raise ValueError("required margin must be nonnegative")
    if relation == "<=":
        if not objective <= threshold - margin:
            raise ValueError("objective does not satisfy certified <= margin")
    elif relation == ">=":
        if not objective >= threshold + margin:
            raise ValueError("objective does not satisfy certified >= margin")
    else:
        raise ValueError("relation must be <= or >=")


def self_test() -> None:
    good = {
        "claimed_psd_matrix": [["1", "1/2"], ["1/2", "1/2"]],
        "gram_factor": [["1", "1/2"], ["0", "1/2"]],
        "linear_residuals": ["0", "0/7"],
        "objective_value": "3/4",
        "threshold": "1",
        "required_margin": "1/4",
        "relation": "<=",
    }
    verify(good)

    bad_factor = dict(good)
    bad_factor["gram_factor"] = [["1", "0"], ["0", "1"]]
    try:
        verify(bad_factor)
    except ValueError as exc:
        assert "Gram identity" in str(exc)
    else:
        raise AssertionError("invalid Gram factor accepted")

    bad_margin = dict(good)
    bad_margin["objective_value"] = "7/8"
    try:
        verify(bad_margin)
    except ValueError as exc:
        assert "margin" in str(exc)
    else:
        raise AssertionError("invalid objective margin accepted")

    print("JANUS_RATIONAL_GRAM_VERIFIER_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.certificate is None:
        parser.error("certificate is required unless --self-test is used")

    payload = json.loads(args.certificate.read_text(encoding="utf-8"))
    verify(payload)
    print("JANUS_RATIONAL_GRAM_CERTIFICATE = PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
