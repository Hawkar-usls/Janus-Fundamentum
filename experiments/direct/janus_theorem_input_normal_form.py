#!/usr/bin/env python3
"""Exact theorem-input normalization for JANUS.

The research engine historically measures a literal occurrence as one internal
unit.  That is polynomially equivalent to ordinary input length only after
variable identifiers are densely normalized.  This module performs the exact
SAT-isomorphism

    sorted original variables v_1 < ... < v_n  ->  1, ..., n

before theorem-mode resource accounting.  The inverse map is retained only for
optional witness presentation and has no decision authority.

This closes the hidden "huge variable id counted as O(1)" loophole without
changing any historical frozen run.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base


@dataclass(frozen=True)
class DenseInputNormalForm:
    source: base.CNF
    normalized: base.CNF
    forward: Dict[int, int]
    inverse: Dict[int, int]
    source_binary_units: int
    normalized_internal_N: int


def binary_encoding_units(cnf: base.CNF) -> int:
    """Deterministic binary-length surrogate including identifier magnitudes."""
    # Constant delimiters/sign bits plus magnitude bits.  Any standard sensible
    # binary CNF encoding differs only by a fixed polynomial/constant factor.
    return max(
        2,
        1 + len(cnf) + sum(2 + abs(lit).bit_length() for clause in cnf for lit in clause),
    )


def dense_normalize(raw_clauses: Iterable[Iterable[int]]) -> DenseInputNormalForm:
    source = base.canon_cnf(raw_clauses)
    variables = base.vars_of(source)
    forward = {variable: index + 1 for index, variable in enumerate(variables)}
    inverse = {dense: original for original, dense in forward.items()}

    rows = []
    for clause in source:
        rows.append(
            tuple(
                forward[abs(lit)] if lit > 0 else -forward[abs(lit)]
                for lit in clause
            )
        )
    normalized = base.canon_cnf(rows)

    if base.vars_of(normalized) != tuple(range(1, len(variables) + 1)):
        raise AssertionError("DENSE_VARIABLE_NORMALIZATION_FAILED")

    source_bits = binary_encoding_units(source)
    internal_N = base.input_size_units(normalized)
    # Every normalized variable id is <= number of source variables, and the
    # internal unit count is bounded by a constant multiple of literal count.
    if internal_N > 2 * source_bits + 2:
        raise AssertionError("INTERNAL_N_NOT_POLYNOMIALLY_DOMINATED_BY_SOURCE_ENCODING")

    return DenseInputNormalForm(
        source=source,
        normalized=normalized,
        forward=forward,
        inverse=inverse,
        source_binary_units=source_bits,
        normalized_internal_N=internal_N,
    )


def lift_normalized_assignment(normal_form: DenseInputNormalForm, assignment: Dict[int, int]) -> Dict[int, int]:
    return {
        normal_form.inverse[int(variable)]: int(bit)
        for variable, bit in assignment.items()
        if int(variable) in normal_form.inverse
    }


def verify_sat_isomorphism(normal_form: DenseInputNormalForm, normalized_assignment: Dict[int, int]) -> bool:
    if not base.verify_total_assignment(normal_form.normalized, normalized_assignment):
        return False
    source_assignment = lift_normalized_assignment(normal_form, normalized_assignment)
    return base.verify_total_assignment(normal_form.source, source_assignment)


def selftest() -> None:
    # Deliberately enormous sparse identifiers: the normalized theorem input must
    # still become variables 1..3 while preserving satisfaction exactly.
    raw = (
        (10**60 + 7, -(10**90 + 9), 10**120 + 11),
        (-(10**60 + 7), 10**90 + 9),
    )
    nf = dense_normalize(raw)
    assert base.vars_of(nf.normalized) == (1, 2, 3)

    # Exhaustive truth-table equivalence on this 3-variable smoke specimen.
    originals = base.vars_of(nf.source)
    for mask in range(1 << len(originals)):
        source_assignment = {
            variable: (mask >> index) & 1
            for index, variable in enumerate(originals)
        }
        normalized_assignment = {
            nf.forward[variable]: bit for variable, bit in source_assignment.items()
        }
        assert base.verify_total_assignment(nf.source, source_assignment) == base.verify_total_assignment(
            nf.normalized, normalized_assignment
        )

    print("JANUS_THEOREM_INPUT_NORMAL_FORM=PASS")
    print("DENSE_VARIABLE_ID_FIREWALL=PASS")
    print("P_VS_NP=OPEN")


if __name__ == "__main__":
    selftest()
