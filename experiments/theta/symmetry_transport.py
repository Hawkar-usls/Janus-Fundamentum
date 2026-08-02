#!/usr/bin/env python3
"""Exact monomial-basis transport for signed coordinate permutations.

For squarefree monomials of degree at most k, build the integer matrix T such
that z_k(phi(x)) = T^T z_k(x), where phi permutes coordinates and may replace
selected x_i by 1-x_j. The self-test checks exact inverse identities.
"""

from __future__ import annotations

import argparse
import itertools
from collections import defaultdict


Monomial = tuple[int, ...]
Matrix = list[list[int]]


def basis(variable_count: int, maximum_degree: int) -> list[Monomial]:
    result: list[Monomial] = [()]
    for degree in range(1, maximum_degree + 1):
        result.extend(itertools.combinations(range(variable_count), degree))
    return result


def multiply_polynomials(
    left: dict[Monomial, int], right: dict[Monomial, int]
) -> dict[Monomial, int]:
    output: defaultdict[Monomial, int] = defaultdict(int)
    for left_term, left_coefficient in left.items():
        for right_term, right_coefficient in right.items():
            merged = tuple(sorted(set(left_term) | set(right_term)))
            output[merged] += left_coefficient * right_coefficient
    return {term: coefficient for term, coefficient in output.items() if coefficient}


def expand_monomial(
    term: Monomial,
    permutation: tuple[int, ...],
    complemented: frozenset[int],
) -> dict[Monomial, int]:
    polynomial: dict[Monomial, int] = {(): 1}
    for source in term:
        target = permutation[source]
        if source in complemented:
            factor = {(): 1, (target,): -1}
        else:
            factor = {(target,): 1}
        polynomial = multiply_polynomials(polynomial, factor)
    return polynomial


def transport_matrix(
    variable_count: int,
    maximum_degree: int,
    permutation: tuple[int, ...],
    complemented: frozenset[int],
) -> Matrix:
    if sorted(permutation) != list(range(variable_count)):
        raise ValueError("permutation must contain each coordinate exactly once")
    if any(index < 0 or index >= variable_count for index in complemented):
        raise ValueError("complemented coordinate outside range")

    monomials = basis(variable_count, maximum_degree)
    index = {term: position for position, term in enumerate(monomials)}
    matrix = [[0 for _ in monomials] for _ in monomials]

    for column, term in enumerate(monomials):
        expansion = expand_monomial(term, permutation, complemented)
        for output_term, coefficient in expansion.items():
            if len(output_term) > maximum_degree:
                raise AssertionError("degree increased under signed permutation")
            matrix[index[output_term]][column] = coefficient
    return matrix


def inverse_parameters(
    permutation: tuple[int, ...], complemented: frozenset[int]
) -> tuple[tuple[int, ...], frozenset[int]]:
    inverse = [0] * len(permutation)
    for source, target in enumerate(permutation):
        inverse[target] = source
    inverse_complemented = frozenset(
        target
        for target in range(len(permutation))
        if inverse[target] in complemented
    )
    return tuple(inverse), inverse_complemented


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    rows = len(left)
    columns = len(right[0])
    inner = len(right)
    return [
        [
            sum(left[row][middle] * right[middle][column] for middle in range(inner))
            for column in range(columns)
        ]
        for row in range(rows)
    ]


def identity(size: int) -> Matrix:
    return [[1 if row == column else 0 for column in range(size)] for row in range(size)]


def self_test() -> None:
    for variable_count in range(1, 6):
        permutations = {
            tuple(range(variable_count)),
            tuple(reversed(range(variable_count))),
            tuple((index + 1) % variable_count for index in range(variable_count)),
        }
        complements = {
            frozenset(),
            frozenset(index for index in range(variable_count) if index % 2 == 0),
            frozenset(range(variable_count)),
        }
        for maximum_degree in range(0, min(3, variable_count) + 1):
            size = len(basis(variable_count, maximum_degree))
            expected = identity(size)
            for permutation in permutations:
                for complemented in complements:
                    forward = transport_matrix(
                        variable_count,
                        maximum_degree,
                        permutation,
                        complemented,
                    )
                    inverse_permutation, inverse_complemented = inverse_parameters(
                        permutation, complemented
                    )
                    backward = transport_matrix(
                        variable_count,
                        maximum_degree,
                        inverse_permutation,
                        inverse_complemented,
                    )
                    assert multiply(forward, backward) == expected
                    assert multiply(backward, forward) == expected
                    assert all(
                        coefficient in {-1, 0, 1}
                        for row in forward
                        for coefficient in row
                    )
    print("JANUS_SYMMETRY_TRANSPORT_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    parser.error("only --self-test is currently supported")


if __name__ == "__main__":
    raise SystemExit(main())
