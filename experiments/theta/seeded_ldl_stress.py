#!/usr/bin/env python3
"""Deterministic rational LDL stress fixtures for C014.

Seed 9379992 generates explicit rational PSD matrices as L D L^T.  The JANUS
constructor must rediscover some valid permuted LDL certificate and the exact
verifier must replay it.  This is a reproducibility stress test, not a proof of
the universal bit-complexity statement H108.
"""

from __future__ import annotations

import argparse
import random
from fractions import Fraction

from rational_ldl import (
    decompose_psd,
    diagonal_matrix,
    multiply,
    transpose,
    verify_certificate,
)

SEED = 9_379_992
Matrix = list[list[Fraction]]


def random_lower(rng: random.Random, size: int, magnitude: int) -> Matrix:
    matrix: Matrix = []
    for row in range(size):
        current: list[Fraction] = []
        for column in range(size):
            if column > row:
                current.append(Fraction(0))
            elif column == row:
                current.append(Fraction(1))
            else:
                numerator = rng.randint(-magnitude, magnitude)
                denominator = rng.randint(1, magnitude)
                current.append(Fraction(numerator, denominator))
        matrix.append(current)
    return matrix


def random_diagonal(rng: random.Random, size: int, magnitude: int) -> list[Fraction]:
    values: list[Fraction] = []
    for index in range(size):
        if index % 4 == 0:
            values.append(Fraction(0))
        else:
            values.append(
                Fraction(rng.randint(1, magnitude), rng.randint(1, magnitude))
            )
    rng.shuffle(values)
    return values


def matrix_bit_length(matrix: Matrix) -> int:
    return max(
        max(abs(value.numerator).bit_length(), value.denominator.bit_length())
        for row in matrix
        for value in row
    )


def certificate_bit_length(certificate: dict) -> int:
    values = [value for row in certificate["unit_lower"] for value in row]
    values.extend(certificate["diagonal"])
    return max(
        max(abs(value.numerator).bit_length(), value.denominator.bit_length())
        for value in values
    )


def fixture(rng: random.Random, size: int, magnitude: int) -> tuple[Matrix, dict]:
    lower = random_lower(rng, size, magnitude)
    diagonal = random_diagonal(rng, size, magnitude)
    matrix = multiply(multiply(lower, diagonal_matrix(diagonal)), transpose(lower))
    certificate = decompose_psd(matrix)
    verify_certificate(matrix, certificate)
    return matrix, certificate


def self_test() -> None:
    rng = random.Random(SEED)
    summaries = []
    for size in range(2, 9):
        for magnitude in (3, 17):
            matrix, certificate = fixture(rng, size, magnitude)
            summaries.append(
                (
                    size,
                    magnitude,
                    matrix_bit_length(matrix),
                    certificate_bit_length(certificate),
                )
            )
    if len(summaries) != 14:
        raise AssertionError("unexpected fixture count")
    print("JANUS_SEEDED_LDL_STRESS = PASS")
    print(f"SEED = {SEED}")
    print(f"FIXTURES = {len(summaries)}")
    print(f"MAX_MATRIX_BITS = {max(item[2] for item in summaries)}")
    print(f"MAX_CERTIFICATE_BITS = {max(item[3] for item in summaries)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    parser.error("only --self-test is supported")


if __name__ == "__main__":
    raise SystemExit(main())
