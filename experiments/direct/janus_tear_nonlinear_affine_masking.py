#!/usr/bin/env python3
"""Hide an explicit XOR contradiction behind a bijective nonlinear encoding."""

from __future__ import annotations

from itertools import product

Clause = tuple[int, ...]
Formula = tuple[Clause, ...]


def clause_forbidden_assignment(bits: tuple[int, ...]) -> Clause:
    return tuple(
        index + 1 if bit == 0 else -(index + 1)
        for index, bit in enumerate(bits)
    )


def nonlinear_value(a: int, b: int, c: int) -> int:
    return a ^ b ^ (a & c)


def relation_cnf(output: int) -> Formula:
    return tuple(
        clause_forbidden_assignment(bits)
        for bits in product((0, 1), repeat=3)
        if nonlinear_value(*bits) != output
    )


def satisfies(formula: Formula, bits: tuple[int, ...]) -> bool:
    return all(
        any(
            (literal > 0 and bits[literal - 1] == 1)
            or (literal < 0 and bits[-literal - 1] == 0)
            for literal in clause
        )
        for clause in formula
    )


def witnesses(formula: Formula, variables: int) -> list[tuple[int, ...]]:
    return [
        bits
        for bits in product((0, 1), repeat=variables)
        if satisfies(formula, bits)
    ]


def affine_truth_tables(variables: int) -> set[tuple[int, ...]]:
    inputs = tuple(product((0, 1), repeat=variables))
    tables: set[tuple[int, ...]] = set()
    for coefficients in product((0, 1), repeat=variables + 1):
        constant, linear = coefficients[0], coefficients[1:]
        tables.add(
            tuple(
                constant
                ^ (
                    sum(
                        coefficient & bit
                        for coefficient, bit in zip(linear, bits, strict=True)
                    )
                    % 2
                )
                for bits in inputs
            )
        )
    return tables


def truth_table() -> tuple[int, ...]:
    return tuple(
        nonlinear_value(*bits) for bits in product((0, 1), repeat=3)
    )


def self_test() -> None:
    zero_relation = relation_cnf(0)
    one_relation = relation_cnf(1)
    masked_contradiction = zero_relation + one_relation

    zero_witnesses = witnesses(zero_relation, 3)
    one_witnesses = witnesses(one_relation, 3)
    contradiction_witnesses = witnesses(masked_contradiction, 3)

    mapping_images = {
        (a, b ^ (a & c), c)
        for a, b, c in product((0, 1), repeat=3)
    }

    assert len(mapping_images) == 8
    assert len(zero_relation) == 4
    assert len(one_relation) == 4
    assert len(zero_witnesses) == 4
    assert len(one_witnesses) == 4
    assert not contradiction_witnesses
    assert truth_table() not in affine_truth_tables(3)

    print("JANUS_TEAR_NONLINEAR_AFFINE_MASKING = PASS")
    print("triangular_mapping_bijective = true")
    print("relation_zero_clauses = 4")
    print("relation_one_clauses = 4")
    print("masked_contradiction_clauses = 8")
    print("nonlinear_relation_is_affine = false")
    print("masked_contradiction_sat = false")


if __name__ == "__main__":
    self_test()
