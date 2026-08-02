#!/usr/bin/env python3
"""Exact rational certificates for the standard Lovasz-theta SDP.

Primal formulation for a graph G=(V,E):

    maximize <J, X>
    subject to Tr(X)=1,
               X_ij=0 for {i,j} in E,
               X positive semidefinite.

Dual certificates use

    S = t I + sum_e y_e A_e - J positive semidefinite,

where A_e has ones in the two symmetric off-diagonal edge positions. Exact
primal and dual objectives certify theta(G)=t. A dual objective below the
clause target certifies UNSAT for a clause-literal conflict graph.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from rational_ldl import (
    Matrix,
    encode_fraction,
    parse_matrix,
    scalar,
    verify_certificate as verify_ldl,
)


def validate_graph(graph: dict[str, Any]) -> tuple[int, list[tuple[int, int]]]:
    vertex_count = graph.get("vertex_count")
    if not isinstance(vertex_count, int) or vertex_count <= 0:
        raise ValueError("graph vertex_count must be a positive integer")
    raw_edges = graph.get("edges")
    if not isinstance(raw_edges, list):
        raise ValueError("graph edges must be a list")

    edges: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()
    for raw in raw_edges:
        if not isinstance(raw, list) or len(raw) != 2:
            raise ValueError("each edge must be a two-element list")
        left, right = raw
        if not isinstance(left, int) or not isinstance(right, int):
            raise ValueError("edge endpoints must be integers")
        if left == right or not (0 <= left < vertex_count) or not (0 <= right < vertex_count):
            raise ValueError(f"invalid edge: {raw}")
        edge = (left, right) if left < right else (right, left)
        if edge in seen:
            raise ValueError(f"duplicate edge: {edge}")
        seen.add(edge)
        edges.append(edge)
    edges.sort()
    return vertex_count, edges


def assert_square(matrix: Matrix, size: int, label: str) -> None:
    if len(matrix) != size or len(matrix[0]) != size:
        raise ValueError(f"{label} must be {size}x{size}")


def trace(matrix: Matrix) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), Fraction(0))


def sum_entries(matrix: Matrix) -> Fraction:
    return sum((value for row in matrix for value in row), Fraction(0))


def parse_edge_multipliers(
    payload: Any, edges: list[tuple[int, int]]
) -> dict[tuple[int, int], Fraction]:
    if not isinstance(payload, dict):
        raise ValueError("edge_multipliers must be an object")
    expected = {f"{left},{right}" for left, right in edges}
    if set(payload) != expected:
        raise ValueError(
            f"edge multiplier keys mismatch; expected={sorted(expected)}, "
            f"actual={sorted(payload)}"
        )
    return {
        tuple(int(part) for part in key.split(",")): scalar(value)
        for key, value in payload.items()
    }


def dual_slack(
    vertex_count: int,
    edges: list[tuple[int, int]],
    objective: Fraction,
    multipliers: dict[tuple[int, int], Fraction],
) -> Matrix:
    slack = [
        [
            objective * (1 if row == column else 0) - 1
            for column in range(vertex_count)
        ]
        for row in range(vertex_count)
    ]
    for left, right in edges:
        value = multipliers[(left, right)]
        slack[left][right] += value
        slack[right][left] += value
    return slack


def verify_primal(
    vertex_count: int,
    edges: list[tuple[int, int]],
    payload: dict[str, Any],
) -> Fraction:
    matrix = parse_matrix(payload.get("matrix"))
    assert_square(matrix, vertex_count, "primal matrix")
    if trace(matrix) != 1:
        raise ValueError("primal trace is not one")
    for left, right in edges:
        if matrix[left][right] != 0 or matrix[right][left] != 0:
            raise ValueError(f"primal edge entry is nonzero for {(left, right)}")
    verify_ldl(matrix, payload.get("ldl", {}))
    return sum_entries(matrix)


def verify_dual(
    vertex_count: int,
    edges: list[tuple[int, int]],
    payload: dict[str, Any],
) -> Fraction:
    objective = scalar(payload.get("objective"))
    multipliers = parse_edge_multipliers(payload.get("edge_multipliers"), edges)
    slack = dual_slack(vertex_count, edges, objective, multipliers)
    verify_ldl(slack, payload.get("slack_ldl", {}))
    return objective


def verify_exact_theta(certificate: dict[str, Any]) -> Fraction:
    vertex_count, edges = validate_graph(certificate.get("graph", {}))
    primal = certificate.get("primal")
    dual = certificate.get("dual")
    if not isinstance(primal, dict) or not isinstance(dual, dict):
        raise ValueError("exact certificate requires primal and dual objects")
    primal_objective = verify_primal(vertex_count, edges, primal)
    dual_objective = verify_dual(vertex_count, edges, dual)
    if primal_objective != dual_objective:
        raise ValueError(
            f"primal/dual objective mismatch: {primal_objective} != {dual_objective}"
        )
    return primal_objective


def verify_dual_unsat(certificate: dict[str, Any]) -> tuple[Fraction, int]:
    vertex_count, edges = validate_graph(certificate.get("graph", {}))
    clause_target = certificate.get("clause_target")
    if not isinstance(clause_target, int) or clause_target <= 0:
        raise ValueError("clause_target must be a positive integer")
    dual = certificate.get("dual")
    if not isinstance(dual, dict):
        raise ValueError("dual UNSAT certificate requires a dual object")
    upper_bound = verify_dual(vertex_count, edges, dual)
    if not upper_bound < clause_target:
        raise ValueError(
            f"theta upper bound {upper_bound} does not fall below target {clause_target}"
        )
    return upper_bound, clause_target


def certificate_for_matrix(matrix: list[list[str]]) -> dict[str, Any]:
    from rational_ldl import decompose_psd, encode_certificate

    parsed = parse_matrix(matrix)
    return encode_certificate(decompose_psd(parsed))


def self_test() -> None:
    complete_two = {
        "graph": {"vertex_count": 2, "edges": [[0, 1]]},
        "primal": {
            "matrix": [["1", "0"], ["0", "0"]],
            "ldl": certificate_for_matrix([["1", "0"], ["0", "0"]]),
        },
        "dual": {
            "objective": "1",
            "edge_multipliers": {"0,1": "1"},
            "slack_ldl": certificate_for_matrix([["0", "0"], ["0", "0"]]),
        },
    }
    assert verify_exact_theta(complete_two) == 1

    empty_two = {
        "graph": {"vertex_count": 2, "edges": []},
        "primal": {
            "matrix": [["1/2", "1/2"], ["1/2", "1/2"]],
            "ldl": certificate_for_matrix(
                [["1/2", "1/2"], ["1/2", "1/2"]]
            ),
        },
        "dual": {
            "objective": "2",
            "edge_multipliers": {},
            "slack_ldl": certificate_for_matrix([["1", "-1"], ["-1", "1"]]),
        },
    }
    assert verify_exact_theta(empty_two) == 2

    unsat = {
        "graph": complete_two["graph"],
        "clause_target": 2,
        "dual": complete_two["dual"],
    }
    upper, target = verify_dual_unsat(unsat)
    assert upper == 1 and target == 2

    bad = json.loads(json.dumps(complete_two))
    bad["dual"]["objective"] = "3/4"
    try:
        verify_exact_theta(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid theta certificate accepted")

    print("JANUS_LOVASZ_THETA_CERTIFICATE_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", type=Path)
    parser.add_argument("--mode", choices=["exact", "unsat"], default="exact")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.certificate is None:
        parser.error("certificate is required unless --self-test is used")

    certificate = json.loads(args.certificate.read_text(encoding="utf-8"))
    if args.mode == "exact":
        value = verify_exact_theta(certificate)
        print(f"JANUS_EXACT_THETA_CERTIFICATE = PASS\nTHETA = {encode_fraction(value)}")
    else:
        upper, target = verify_dual_unsat(certificate)
        print(
            "JANUS_DUAL_THETA_UNSAT_CERTIFICATE = PASS\n"
            f"THETA_UPPER_BOUND = {encode_fraction(upper)}\n"
            f"CLAUSE_TARGET = {target}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
