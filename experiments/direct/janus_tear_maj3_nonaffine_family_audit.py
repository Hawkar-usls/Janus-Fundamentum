#!/usr/bin/env python3
"""Verify non-affinity of parity-of-MAJ3 local relations."""

from __future__ import annotations

from itertools import product

from janus_tear_policy0a_masked_tseitin import affine_equations


def maj3(bits: tuple[int, int, int]) -> int:
    return int(sum(bits) >= 2)


def parity_of_maj3(bits: tuple[int, ...], charge: int) -> bool:
    assert len(bits) % 3 == 0
    value = 0
    for offset in range(0, len(bits), 3):
        value ^= maj3(bits[offset : offset + 3])
    return value == charge


def allowed_relation(degree: int, charge: int) -> set[tuple[int, ...]]:
    return {
        bits
        for bits in product((0, 1), repeat=3 * degree)
        if parity_of_maj3(bits, charge)
    }


def has_affine_parallelogram_violation(allowed: set[tuple[int, ...]]) -> bool:
    """An affine subset is closed under x xor y xor z."""

    values = tuple(sorted(allowed))
    value_set = set(values)
    for x in values:
        for y in values:
            for z in values:
                candidate = tuple(a ^ b ^ c for a, b, c in zip(x, y, z, strict=True))
                if candidate not in value_set:
                    return True
    return False


def audit(degree: int, charge: int) -> None:
    scope = tuple(range(1, 3 * degree + 1))
    allowed = allowed_relation(degree, charge)
    equations = affine_equations(scope, allowed)

    assert equations is None
    # Exhaustive cubic closure is affordable only for the degree-one fibres.
    if degree == 1:
        assert has_affine_parallelogram_violation(allowed)

    print(f"DEGREE = {degree}")
    print(f"  charge = {charge}")
    print(f"  variables = {3 * degree}")
    print(f"  satisfying_rows = {len(allowed)}")
    print("  affine_relation = false")


def self_test() -> None:
    for degree in range(1, 5):
        for charge in (0, 1):
            audit(degree, charge)

    print("JANUS_MAJ3_PARITY_NONAFFINE_FAMILY_AUDIT = PASS")
    print("degrees_checked = 1..4")
    print("charges_checked = 0,1")
    print("consequence = exact-scope affine detector returns NONE per local block")
    print("claim_boundary = finite degrees; general proof uses a non-affine fibre slice")


if __name__ == "__main__":
    self_test()
