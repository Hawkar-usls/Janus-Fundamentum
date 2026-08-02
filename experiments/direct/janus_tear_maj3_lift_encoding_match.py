#!/usr/bin/env python3
"""Compare the JANUS MAJ3 local encoding with the lifting paper's clause-wise CNF."""

from __future__ import annotations

from itertools import product

from janus_tear_policy0a_masked_tseitin import (
    CNF,
    Clause,
    canonical_clause,
    canonical_cnf,
    exact_relation_cnf,
)


def maj3(bits: tuple[int, ...]) -> int:
    assert len(bits) == 3
    return int(sum(bits) >= 2)


def gadget_fibre_cnf(block: tuple[int, int, int], target: int) -> CNF:
    return exact_relation_cnf(block, lambda bits: maj3(bits) == target)


def standard_cnf_disjunction(factors: tuple[CNF, ...]) -> CNF:
    """Equation (1) of ECCC TR26-018: distribute OR over CNF factors."""

    clauses: list[Clause] = []
    for selection in product(*factors):
        merged = canonical_clause(literal for clause in selection for literal in clause)
        if merged is not None:
            clauses.append(merged)
    return canonical_cnf(clauses)


def base_parity_cnf(degree: int, charge: int) -> CNF:
    variables = tuple(range(1, degree + 1))
    return exact_relation_cnf(
        variables,
        lambda bits: (sum(bits) % 2) == charge,
    )


def clausewise_lift(degree: int, charge: int) -> CNF:
    blocks = tuple(
        (3 * index + 1, 3 * index + 2, 3 * index + 3)
        for index in range(degree)
    )
    lifted: list[Clause] = []

    for base_clause in base_parity_cnf(degree, charge):
        factors: list[CNF] = []
        for literal in base_clause:
            block = blocks[abs(literal) - 1]
            target = 1 if literal > 0 else 0
            factors.append(gadget_fibre_cnf(block, target))
        lifted.extend(standard_cnf_disjunction(tuple(factors)))

    return canonical_cnf(lifted)


def direct_local_relation_cnf(degree: int, charge: int) -> CNF:
    variables = tuple(range(1, 3 * degree + 1))

    def relation(bits: tuple[int, ...]) -> bool:
        parity = 0
        for offset in range(0, len(bits), 3):
            parity ^= maj3(bits[offset : offset + 3])
        return parity == charge

    return exact_relation_cnf(variables, relation)


def audit(degree: int, charge: int) -> None:
    clausewise = clausewise_lift(degree, charge)
    direct = direct_local_relation_cnf(degree, charge)

    assert clausewise == direct
    expected = 2 ** (3 * degree - 1)
    assert len(direct) == expected

    print(f"DEGREE = {degree}")
    print(f"  charge = {charge}")
    print(f"  clausewise_clauses = {len(clausewise)}")
    print(f"  direct_relation_clauses = {len(direct)}")
    print("  canonical_clause_sets_equal = true")


def self_test() -> None:
    for degree in range(1, 5):
        for charge in (0, 1):
            audit(degree, charge)

    print("JANUS_MAJ3_LIFT_ENCODING_MATCH = PASS")
    print("degrees_checked = 1..4")
    print("charges_checked = 0,1")
    print("paper_definition = clause-wise standard CNF disjunction")
    print("janus_definition = direct exact local relation CNF")
    print("result = identical canonical clause sets")


if __name__ == "__main__":
    self_test()
