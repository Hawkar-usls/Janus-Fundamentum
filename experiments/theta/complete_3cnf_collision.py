#!/usr/bin/env python3
"""Construct and verify an exact finite Lovasz-theta collision for H096.

UNSAT side: all eight width-three clauses over x1,x2,x3.
SAT side: the same eight sign patterns with a shared positive x4 literal.
Both clause-literal conflict graphs have clause target and exact theta value 8.

No floating-point arithmetic or external SDP solver is used.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from conflict_graph import DimacsCNF, build_graph
from lovasz_theta_certificate import verify_exact_theta
from rational_ldl import decompose_psd, encode_certificate, encode_matrix
from theta_collision_bundle import verify_collision_bundle


Sign = tuple[int, int, int]
Matrix = list[list[Fraction]]


def sign_patterns() -> list[Sign]:
    return list(itertools.product((1, -1), repeat=3))


def unsat_formula() -> DimacsCNF:
    clauses = tuple(
        tuple(pattern[index] * (index + 1) for index in range(3))
        for pattern in sign_patterns()
    )
    return DimacsCNF(variable_count=3, clauses=clauses)


def sat_formula() -> DimacsCNF:
    clauses = tuple(
        (4,) + tuple(pattern[index] * (index + 1) for index in range(3))
        for pattern in sign_patterns()
    )
    return DimacsCNF(variable_count=4, clauses=clauses)


def graph_payload(cnf: DimacsCNF) -> dict[str, Any]:
    graph = build_graph(cnf)
    return {
        "vertex_count": len(graph["vertices"]),
        "edges": graph["edges"],
    }


def automorphisms() -> list[tuple[int, ...]]:
    patterns = sign_patterns()
    pattern_index = {pattern: index for index, pattern in enumerate(patterns)}
    result: list[tuple[int, ...]] = []
    for coordinate_permutation in itertools.permutations(range(3)):
        for flips in itertools.product((1, -1), repeat=3):
            vertex_permutation: list[int] = []
            for pattern in patterns:
                transformed = [0, 0, 0]
                for source in range(3):
                    target = coordinate_permutation[source]
                    transformed[target] = flips[target] * pattern[source]
                clause_index = pattern_index[tuple(transformed)]
                for source in range(3):
                    vertex_permutation.append(
                        clause_index * 3 + coordinate_permutation[source]
                    )
            result.append(tuple(vertex_permutation))
    if len(set(result)) != 48:
        raise AssertionError("expected 48 signed-coordinate automorphisms")
    return result


def deterministic_pair_orbits() -> list[list[tuple[int, int]]]:
    permutations = automorphisms()
    unseen = {(left, right) for left in range(24) for right in range(left, 24)}
    orbits: list[list[tuple[int, int]]] = []
    while unseen:
        representative = min(unseen)
        orbit: set[tuple[int, int]] = set()
        for permutation in permutations:
            left = permutation[representative[0]]
            right = permutation[representative[1]]
            orbit.add((left, right) if left <= right else (right, left))
        unseen -= orbit
        orbits.append(sorted(orbit))
    representatives = [orbit[0] for orbit in orbits]
    expected = [
        (0, 0),
        (0, 1),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 9),
        (0, 10),
        (0, 12),
        (0, 15),
        (0, 17),
        (0, 21),
        (0, 22),
    ]
    if representatives != expected:
        raise AssertionError(f"unexpected orbit order: {representatives}")
    return orbits


def zero_matrix(size: int) -> Matrix:
    return [[Fraction(0) for _ in range(size)] for _ in range(size)]


def unsat_primal_matrix() -> Matrix:
    values = [
        Fraction(1, 24),
        Fraction(0),
        Fraction(1, 36),
        Fraction(-1, 144),
        Fraction(1, 48),
        Fraction(1, 72),
        Fraction(1, 72),
        Fraction(0),
        Fraction(0),
        Fraction(1, 36),
        Fraction(0),
        Fraction(1, 48),
    ]
    matrix = zero_matrix(24)
    for value, orbit in zip(values, deterministic_pair_orbits(), strict=True):
        for left, right in orbit:
            matrix[left][right] = value
            matrix[right][left] = value
    return matrix


def sat_primal_matrix() -> Matrix:
    matrix = zero_matrix(32)
    selected = [clause_index * 4 for clause_index in range(8)]
    for left in selected:
        for right in selected:
            matrix[left][right] = Fraction(1, 8)
    return matrix


def dual_payload(graph: dict[str, Any], clause_size: int) -> dict[str, Any]:
    size = graph["vertex_count"]
    edge_multipliers: dict[str, str] = {}
    slack = [[Fraction(-1) for _ in range(size)] for _ in range(size)]
    for index in range(size):
        slack[index][index] += 8

    for raw_left, raw_right in graph["edges"]:
        same_clause = raw_left // clause_size == raw_right // clause_size
        value = Fraction(8 if same_clause else 0)
        edge_multipliers[f"{raw_left},{raw_right}"] = str(value)
        slack[raw_left][raw_right] += value
        slack[raw_right][raw_left] += value

    return {
        "objective": "8",
        "edge_multipliers": edge_multipliers,
        "slack_ldl": encode_certificate(decompose_psd(slack)),
    }


def theta_certificate(cnf: DimacsCNF, primal: Matrix, clause_size: int) -> dict[str, Any]:
    graph = graph_payload(cnf)
    certificate = {
        "graph": graph,
        "primal": {
            "matrix": encode_matrix(primal),
            "ldl": encode_certificate(decompose_psd(primal)),
        },
        "dual": dual_payload(graph, clause_size),
    }
    if verify_exact_theta(certificate) != 8:
        raise AssertionError("exact theta verifier did not return eight")
    return certificate


def collision_bundle() -> dict[str, Any]:
    return {
        "left": {
            "name": "SAT_SHARED_X4",
            "clause_target": 8,
            "theta_certificate": theta_certificate(
                sat_formula(), sat_primal_matrix(), clause_size=4
            ),
        },
        "right": {
            "name": "UNSAT_COMPLETE_3CNF",
            "clause_target": 8,
            "theta_certificate": theta_certificate(
                unsat_formula(), unsat_primal_matrix(), clause_size=3
            ),
        },
    }


def self_test() -> dict[str, Any]:
    bundle = collision_bundle()
    result = verify_collision_bundle(bundle)
    if result["theta"] != "8":
        raise AssertionError("collision theta is not eight")
    if sorted((result["left_alpha"], result["right_alpha"])) != [7, 8]:
        raise AssertionError("expected exact alpha labels seven and eight")
    print("JANUS_COMPLETE_3CNF_THETA_COLLISION = PASS")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    bundle = collision_bundle()
    if args.output:
        args.output.write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.self_test or not args.output:
        self_test()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
