#!/usr/bin/env python3
"""Audit MAJ3 as the next JANUS Tear lifting gadget.

The script verifies three finite facts:

1. MAJ3 is 1-stifling by exhaustive search over the definition;
2. neither output fibre of MAJ3 is affine over GF(2);
3. the concrete Policy-0A root affine extractor does not fire on MAJ3-lifted
   odd-charge Tseitin formulas, and the quadratic state envelope is exceeded on
   the K3,3 fixture.

The asymptotic lifting theorem is external mathematics. This file only verifies
that the chosen constant gadget and finite fixtures satisfy the local interface
required by the proposed bridge.
"""

from __future__ import annotations

import argparse
from itertools import product
from typing import Iterable, Sequence

from janus_tear_policy0a_masked_tseitin import (
    CNF,
    Edge,
    K33_EDGES,
    K4_EDGES,
    Policy0A,
    canonical_cnf,
    exact_relation_cnf,
    normalized_edges,
    visible_affine_root_decision,
)


def maj3(bits: Sequence[int]) -> int:
    if len(bits) != 3:
        raise ValueError("MAJ3 expects exactly three bits")
    return int(sum(bits) >= 2)


def stifling_witness(index: int, target: int) -> tuple[int, int, int] | None:
    for candidate in product((0, 1), repeat=3):
        valid = True
        for free_value in (0, 1):
            probe = list(candidate)
            probe[index] = free_value
            if maj3(probe) != target:
                valid = False
                break
        if valid:
            return candidate
    return None


def is_one_stifling() -> tuple[bool, dict[tuple[int, int], tuple[int, int, int]]]:
    witnesses: dict[tuple[int, int], tuple[int, int, int]] = {}
    for index in range(3):
        for target in (0, 1):
            witness = stifling_witness(index, target)
            if witness is None:
                return False, witnesses
            witnesses[(index, target)] = witness
    return True, witnesses


def is_affine_fibre(target: int) -> bool:
    allowed = {
        bits for bits in product((0, 1), repeat=3) if maj3(bits) == target
    }
    base = next(iter(allowed))
    translated = {
        tuple(left ^ right for left, right in zip(bits, base))
        for bits in allowed
    }
    zero = (0, 0, 0)
    if zero not in translated:
        return False
    return all(
        tuple(left ^ right for left, right in zip(first, second)) in translated
        for first in translated
        for second in translated
    )


def maj3_lifted_tseitin_cnf(
    vertex_count: int,
    edges: Iterable[Edge],
) -> tuple[CNF, int]:
    edge_list = normalized_edges(edges)
    blocks: dict[Edge, tuple[int, int, int]] = {}
    next_variable = 1

    for edge in edge_list:
        blocks[edge] = (next_variable, next_variable + 1, next_variable + 2)
        next_variable += 3

    charges = [1] + [0] * (vertex_count - 1)
    clauses = []

    for vertex in range(vertex_count):
        incident = [edge for edge in edge_list if vertex in edge]
        variables = [variable for edge in incident for variable in blocks[edge]]
        charge = charges[vertex]

        def relation(bits: tuple[int, ...], charge: int = charge) -> bool:
            parity = 0
            for offset in range(0, len(bits), 3):
                parity ^= maj3(bits[offset : offset + 3])
            return parity == charge

        clauses.extend(exact_relation_cnf(variables, relation))

    return canonical_cnf(clauses), next_variable - 1


def print_policy_case(
    name: str,
    vertex_count: int,
    edges: Sequence[Edge],
    state_cap: int | None,
):
    cnf, variable_count = maj3_lifted_tseitin_cnf(vertex_count, edges)
    affine_answer, affine_equations = visible_affine_root_decision(cnf, variable_count)
    result = Policy0A(state_cap=state_cap).solve(cnf, variable_count)

    print(f"CASE = {name}")
    print(f"  variables = {variable_count}")
    print(f"  clauses = {len(cnf)}")
    print(f"  maximum_width = {max(map(len, cnf))}")
    print(f"  root_affine_answer = {affine_answer}")
    print(f"  root_affine_equations = {affine_equations}")
    print(f"  answer = {result.answer}")
    print(f"  cap_exceeded = {str(result.cap_exceeded).lower()}")
    print(f"  residual_states = {result.residual_states}")
    return cnf, variable_count, result


def self_test() -> None:
    stifling, witnesses = is_one_stifling()
    assert stifling
    assert len(witnesses) == 6
    assert not is_affine_fibre(0)
    assert not is_affine_fibre(1)

    k4_cnf, k4_variables, k4_result = print_policy_case(
        "MAJ3_LIFTED_K4",
        4,
        K4_EDGES,
        None,
    )
    assert k4_variables == 18
    assert len(k4_cnf) == 1024
    assert k4_result.answer is False
    assert not k4_result.cap_exceeded
    assert k4_result.affine_equations == 0
    assert k4_result.residual_states == 2427

    k33_cnf, k33_variables, k33_result = print_policy_case(
        "MAJ3_LIFTED_K33_QUADRATIC_CAP",
        6,
        K33_EDGES,
        4 * 27 * 27,
    )
    assert k33_variables == 27
    assert len(k33_cnf) == 1536
    assert k33_result.answer is None
    assert k33_result.cap_exceeded
    assert k33_result.residual_states == 2917

    print("MAJ3_1_STIFLING = true")
    print("MAJ3_ZERO_FIBRE_AFFINE = false")
    print("MAJ3_ONE_FIBRE_AFFINE = false")
    print("JANUS_TEAR_MAJ3_STIFLING_SELF_TEST = PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--case",
        choices=("k4", "k33"),
        default="k4",
    )
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return

    stifling, witnesses = is_one_stifling()
    print(f"MAJ3_1_STIFLING = {str(stifling).lower()}")
    for key, witness in sorted(witnesses.items()):
        print(f"  free_index={key[0]} target={key[1]} witness={witness}")
    print(f"MAJ3_ZERO_FIBRE_AFFINE = {str(is_affine_fibre(0)).lower()}")
    print(f"MAJ3_ONE_FIBRE_AFFINE = {str(is_affine_fibre(1)).lower()}")

    if args.case == "k4":
        print_policy_case("MAJ3_LIFTED_K4", 4, K4_EDGES, None)
    else:
        print_policy_case(
            "MAJ3_LIFTED_K33_QUADRATIC_CAP",
            6,
            K33_EDGES,
            4 * 27 * 27,
        )


if __name__ == "__main__":
    main()
