#!/usr/bin/env python3
"""Exact rational LDL^T certificates for positive-semidefinite matrices.

The constructor uses symmetric rational elimination with diagonal pivoting. The
verifier checks a supplied permutation, unit-lower matrix, and nonnegative
rational diagonal. No floating-point arithmetic is used.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


Matrix = list[list[Fraction]]


def scalar(value: Any) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("boolean is not a rational scalar")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    raise ValueError(f"unsupported rational scalar: {value!r}")


def parse_matrix(payload: Any) -> Matrix:
    if not isinstance(payload, list) or not payload:
        raise ValueError("matrix must be a nonempty list")
    rows = []
    for row in payload:
        if not isinstance(row, list):
            raise ValueError("matrix row must be a list")
        rows.append([scalar(value) for value in row])
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("matrix must be rectangular and nonempty")
    return rows


def assert_symmetric(matrix: Matrix) -> None:
    if len(matrix) != len(matrix[0]):
        raise ValueError("matrix must be square")
    for i in range(len(matrix)):
        for j in range(i):
            if matrix[i][j] != matrix[j][i]:
                raise ValueError("matrix must be symmetric")


def identity(size: int) -> Matrix:
    return [
        [Fraction(1 if row == column else 0) for column in range(size)]
        for row in range(size)
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
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


def diagonal_matrix(diagonal: list[Fraction]) -> Matrix:
    return [
        [value if row == column else Fraction(0) for column, value in enumerate(diagonal)]
        for row in range(len(diagonal))
    ]


def permuted(matrix: Matrix, permutation: list[int]) -> Matrix:
    return [
        [matrix[permutation[row]][permutation[column]] for column in range(len(permutation))]
        for row in range(len(permutation))
    ]


def decompose_psd(matrix: Matrix) -> dict[str, Any]:
    """Return P A P^T = L D L^T or raise ValueError if A is not PSD."""

    assert_symmetric(matrix)
    size = len(matrix)
    work = [row[:] for row in matrix]
    permutation = list(range(size))
    lower = identity(size)
    diagonal = [Fraction(0) for _ in range(size)]

    for pivot_index in range(size):
        negative = [
            index
            for index in range(pivot_index, size)
            if work[index][index] < 0
        ]
        if negative:
            raise ValueError("matrix is not PSD: negative Schur-complement diagonal")

        pivot = next(
            (
                index
                for index in range(pivot_index, size)
                if work[index][index] > 0
            ),
            None,
        )

        if pivot is None:
            for row in range(pivot_index, size):
                for column in range(pivot_index, size):
                    if work[row][column] != 0:
                        raise ValueError(
                            "matrix is not PSD: zero diagonal block has nonzero entry"
                        )
            break

        if pivot != pivot_index:
            work[pivot_index], work[pivot] = work[pivot], work[pivot_index]
            for row in work:
                row[pivot_index], row[pivot] = row[pivot], row[pivot_index]
            permutation[pivot_index], permutation[pivot] = (
                permutation[pivot],
                permutation[pivot_index],
            )
            for column in range(pivot_index):
                lower[pivot_index][column], lower[pivot][column] = (
                    lower[pivot][column],
                    lower[pivot_index][column],
                )

        pivot_value = work[pivot_index][pivot_index]
        diagonal[pivot_index] = pivot_value

        for row in range(pivot_index + 1, size):
            lower[row][pivot_index] = work[row][pivot_index] / pivot_value

        for row in range(pivot_index + 1, size):
            for column in range(row, size):
                updated = (
                    work[row][column]
                    - lower[row][pivot_index]
                    * pivot_value
                    * lower[column][pivot_index]
                )
                work[row][column] = updated
                work[column][row] = updated

        for row in range(pivot_index + 1, size):
            work[row][pivot_index] = Fraction(0)
            work[pivot_index][row] = Fraction(0)

    certificate = {
        "permutation": permutation,
        "unit_lower": lower,
        "diagonal": diagonal,
    }
    verify_certificate(matrix, certificate)
    return certificate


def verify_certificate(matrix: Matrix, certificate: dict[str, Any]) -> None:
    assert_symmetric(matrix)
    size = len(matrix)
    permutation = certificate.get("permutation")
    if (
        not isinstance(permutation, list)
        or sorted(permutation) != list(range(size))
    ):
        raise ValueError("certificate permutation is invalid")

    lower = parse_matrix(certificate.get("unit_lower"))
    diagonal = [scalar(value) for value in certificate.get("diagonal", [])]
    if len(lower) != size or len(lower[0]) != size or len(diagonal) != size:
        raise ValueError("certificate dimensions do not match matrix")

    for row in range(size):
        for column in range(size):
            if column > row and lower[row][column] != 0:
                raise ValueError("unit_lower has a nonzero entry above the diagonal")
            if column == row and lower[row][column] != 1:
                raise ValueError("unit_lower diagonal must be one")

    if any(value < 0 for value in diagonal):
        raise ValueError("LDL diagonal contains a negative entry")

    reconstructed = multiply(
        multiply(lower, diagonal_matrix(diagonal)),
        transpose(lower),
    )
    if reconstructed != permuted(matrix, permutation):
        raise ValueError("LDL identity P A P^T = L D L^T failed")


def encode_fraction(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def encode_matrix(matrix: Matrix) -> list[list[str]]:
    return [[encode_fraction(value) for value in row] for row in matrix]


def encode_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    return {
        "permutation": certificate["permutation"],
        "unit_lower": encode_matrix(certificate["unit_lower"]),
        "diagonal": [encode_fraction(value) for value in certificate["diagonal"]],
    }


def self_test() -> None:
    fixtures = [
        [["1", "1/2"], ["1/2", "1/2"]],
        [["0", "0"], ["0", "1"]],
        [["0", "0"], ["0", "0"]],
        [["2", "-1", "0"], ["-1", "2", "-1"], ["0", "-1", "2"]],
    ]
    for payload in fixtures:
        matrix = parse_matrix(payload)
        certificate = decompose_psd(matrix)
        verify_certificate(matrix, certificate)
        encoded = encode_certificate(certificate)
        verify_certificate(matrix, encoded)

    invalid = [
        [["1", "2"], ["2", "1"]],
        [["-1"]],
        [["0", "1"], ["1", "0"]],
    ]
    for payload in invalid:
        try:
            decompose_psd(parse_matrix(payload))
        except ValueError:
            pass
        else:
            raise AssertionError(f"indefinite matrix accepted: {payload}")

    print("JANUS_RATIONAL_LDL_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("matrix", nargs="?", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.matrix is None:
        parser.error("matrix JSON is required unless --self-test is used")

    matrix = parse_matrix(json.loads(args.matrix.read_text(encoding="utf-8")))
    certificate = encode_certificate(decompose_psd(matrix))
    encoded = json.dumps(certificate, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
