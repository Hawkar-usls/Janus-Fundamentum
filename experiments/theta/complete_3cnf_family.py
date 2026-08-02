#!/usr/bin/env python3
"""Generate exact theta certificates for the H099 amplified collision family."""

from __future__ import annotations

import argparse
from fractions import Fraction
from typing import Any

from complete_3cnf_collision import (
    graph_payload,
    sat_formula,
    sat_primal_matrix,
    unsat_formula,
    unsat_primal_matrix,
)
from conflict_graph import DimacsCNF
from lovasz_theta_certificate import verify_exact_theta
from rational_ldl import decompose_psd, encode_certificate, encode_matrix


Matrix = list[list[Fraction]]


def renamed_copies(base: DimacsCNF, copies: int) -> DimacsCNF:
    if copies < 1:
        raise ValueError("copies must be positive")
    clauses: list[tuple[int, ...]] = []
    width = base.variable_count
    for copy_index in range(copies):
        offset = copy_index * width
        for clause in base.clauses:
            clauses.append(
                tuple(
                    (abs(literal) + offset) if literal > 0 else -(abs(literal) + offset)
                    for literal in clause
                )
            )
    return DimacsCNF(variable_count=width * copies, clauses=tuple(clauses))


def kronecker_copy_primal(base: Matrix, copies: int) -> Matrix:
    size = len(base)
    result = [
        [Fraction(0) for _ in range(size * copies)]
        for _ in range(size * copies)
    ]
    scale = Fraction(1, copies)
    for left_copy in range(copies):
        for right_copy in range(copies):
            for left in range(size):
                for right in range(size):
                    result[left_copy * size + left][right_copy * size + right] = (
                        scale * base[left][right]
                    )
    return result


def amplified_dual(
    graph: dict[str, Any], clause_size: int, target: int
) -> dict[str, Any]:
    size = graph["vertex_count"]
    slack = [[Fraction(-1) for _ in range(size)] for _ in range(size)]
    for index in range(size):
        slack[index][index] += target

    multipliers: dict[str, str] = {}
    for left, right in graph["edges"]:
        same_clause = left // clause_size == right // clause_size
        value = Fraction(target if same_clause else 0)
        multipliers[f"{left},{right}"] = str(value)
        slack[left][right] += value
        slack[right][left] += value

    return {
        "objective": str(target),
        "edge_multipliers": multipliers,
        "slack_ldl": encode_certificate(decompose_psd(slack)),
    }


def certificate(
    base_formula: DimacsCNF,
    base_primal: Matrix,
    clause_size: int,
    copies: int,
) -> dict[str, Any]:
    formula = renamed_copies(base_formula, copies)
    graph = graph_payload(formula)
    primal = kronecker_copy_primal(base_primal, copies)
    target = 8 * copies
    payload = {
        "graph": graph,
        "primal": {
            "matrix": encode_matrix(primal),
            "ldl": encode_certificate(decompose_psd(primal)),
        },
        "dual": amplified_dual(graph, clause_size, target),
    }
    value = verify_exact_theta(payload)
    if value != target:
        raise AssertionError(f"theta {value} differs from target {target}")
    return payload


def assert_disjoint_graph_copies(graph: dict[str, Any], component_size: int) -> None:
    for left, right in graph["edges"]:
        if left // component_size != right // component_size:
            raise AssertionError("cross-copy conflict edge detected")


def self_test() -> None:
    for copies in (1, 2):
        sat = certificate(sat_formula(), sat_primal_matrix(), 4, copies)
        unsat = certificate(unsat_formula(), unsat_primal_matrix(), 3, copies)
        assert_disjoint_graph_copies(sat["graph"], 32)
        assert_disjoint_graph_copies(unsat["graph"], 24)
    print("JANUS_COMPLETE_3CNF_THETA_FAMILY = PASS")
    print("CERTIFIED_COPIES = 1,2")
    print("GENERAL_MATRIX = (1/r) J_r tensor X")


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
