#!/usr/bin/env python3
"""Build exact connected Lovasz-theta twins using seeded zero-entry arches.

The base SAT/UNSAT collision comes from complete_3cnf_collision.py.  For r
copies, the exact primal matrix is (1/r) J_r tensor X.  A cross-copy edge may
be added wherever the corresponding base entry X[u,v] is zero.  Such an edge
is an "arch": it connects two formerly disjoint components without changing
primal feasibility.  The old dual remains feasible by assigning multiplier
zero to every arch edge.

Seed 9379992 is used only to choose a canonical zero-entry arch from the finite
candidate set.  Correctness is then verified exactly and does not rely on
randomness, floating point, or a lucky search outcome.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from complete_3cnf_collision import (
    graph_payload,
    sat_formula,
    sat_primal_matrix,
    unsat_formula,
    unsat_primal_matrix,
)
from conflict_graph import exact_alpha
from lovasz_theta_certificate import verify_exact_theta
from rational_ldl import decompose_psd, encode_certificate, encode_matrix

SEED = 9_379_992
Matrix = list[list[Fraction]]


def seeded_score(side: str, left: int, right: int) -> str:
    payload = f"{SEED}:{side}:{left}:{right}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def choose_arch(
    matrix: Matrix,
    side: str,
    forbidden_vertices: set[int] | None = None,
) -> tuple[int, int, str]:
    forbidden = set() if forbidden_vertices is None else set(forbidden_vertices)
    candidates: list[tuple[str, int, int]] = []
    for left in range(len(matrix)):
        for right in range(len(matrix)):
            if left in forbidden or right in forbidden:
                continue
            if matrix[left][right] == 0:
                candidates.append((seeded_score(side, left, right), left, right))
    if not candidates:
        raise ValueError(f"no zero-entry arch candidate for {side}")
    score, left, right = min(candidates)
    return left, right, score


def repeated_graph(
    base_graph: dict[str, Any],
    copies: int,
    arch: tuple[int, int],
) -> tuple[dict[str, Any], list[list[int]]]:
    if copies < 1:
        raise ValueError("copies must be positive")
    size = base_graph["vertex_count"]
    edges: set[tuple[int, int]] = set()
    for copy in range(copies):
        offset = copy * size
        for left, right in base_graph["edges"]:
            edges.add((offset + left, offset + right))

    arches: list[list[int]] = []
    for copy in range(copies - 1):
        left = copy * size + arch[0]
        right = (copy + 1) * size + arch[1]
        edge = (left, right) if left < right else (right, left)
        if edge in edges:
            raise AssertionError("arch unexpectedly duplicates an internal edge")
        edges.add(edge)
        arches.append([edge[0], edge[1]])

    return {
        "vertex_count": copies * size,
        "edges": [list(edge) for edge in sorted(edges)],
    }, arches


def amplified_primal(base: Matrix, copies: int) -> Matrix:
    if copies < 1:
        raise ValueError("copies must be positive")
    size = len(base)
    scale = Fraction(1, copies)
    return [
        [
            scale * base[row % size][column % size]
            for column in range(copies * size)
        ]
        for row in range(copies * size)
    ]


def connected(graph: dict[str, Any]) -> bool:
    size = graph["vertex_count"]
    adjacency = [set() for _ in range(size)]
    for left, right in graph["edges"]:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == size


def dual_payload(
    graph: dict[str, Any],
    copies: int,
    base_vertex_count: int,
    clause_size: int,
) -> dict[str, Any]:
    target = 8 * copies
    size = graph["vertex_count"]
    slack = [[Fraction(-1) for _ in range(size)] for _ in range(size)]
    for index in range(size):
        slack[index][index] += target

    multipliers: dict[str, str] = {}
    for left, right in graph["edges"]:
        left_copy, left_local = divmod(left, base_vertex_count)
        right_copy, right_local = divmod(right, base_vertex_count)
        same_clause = (
            left_copy == right_copy
            and left_local // clause_size == right_local // clause_size
        )
        value = Fraction(target if same_clause else 0)
        multipliers[f"{left},{right}"] = str(value)
        slack[left][right] += value
        slack[right][left] += value

    return {
        "objective": str(target),
        "edge_multipliers": multipliers,
        "slack_ldl": encode_certificate(decompose_psd(slack)),
    }


def exact_certificate(
    base_graph: dict[str, Any],
    base_primal: Matrix,
    copies: int,
    arch: tuple[int, int],
    clause_size: int,
) -> tuple[dict[str, Any], list[list[int]]]:
    graph, arches = repeated_graph(base_graph, copies, arch)
    primal = amplified_primal(base_primal, copies)
    certificate = {
        "graph": graph,
        "primal": {
            "matrix": encode_matrix(primal),
            "ldl": encode_certificate(decompose_psd(primal)),
        },
        "dual": dual_payload(
            graph,
            copies,
            base_graph["vertex_count"],
            clause_size,
        ),
    }
    expected = Fraction(8 * copies)
    actual = verify_exact_theta(certificate)
    if actual != expected:
        raise AssertionError(f"theta mismatch: {actual} != {expected}")
    if not connected(graph):
        raise AssertionError("arched graph is not connected")
    return certificate, arches


def graph_for_alpha(graph: dict[str, Any]) -> dict[str, Any]:
    return {
        "vertices": [{"id": index} for index in range(graph["vertex_count"])],
        "edges": graph["edges"],
    }


def selected_sat_vertices(copies: int) -> list[int]:
    base_size = 32
    selected: list[int] = []
    for copy in range(copies):
        offset = copy * base_size
        selected.extend(offset + clause * 4 for clause in range(8))
    return selected


def assert_independent(graph: dict[str, Any], vertices: list[int]) -> None:
    selected = set(vertices)
    for left, right in graph["edges"]:
        if left in selected and right in selected:
            raise AssertionError(f"selected SAT witness contains edge {(left, right)}")


def build_family_member(copies: int) -> dict[str, Any]:
    unsat_base_graph = graph_payload(unsat_formula())
    sat_base_graph = graph_payload(sat_formula())
    unsat_base_primal = unsat_primal_matrix()
    sat_base_primal = sat_primal_matrix()

    sat_forbidden = {clause * 4 for clause in range(8)}
    unsat_left, unsat_right, unsat_score = choose_arch(
        unsat_base_primal, "UNSAT"
    )
    sat_left, sat_right, sat_score = choose_arch(
        sat_base_primal, "SAT", sat_forbidden
    )

    # Freeze the seed-derived choices so a changed candidate order cannot pass.
    if (unsat_left, unsat_right) != (22, 13):
        raise AssertionError("unexpected seed-derived UNSAT arch")
    if (sat_left, sat_right) != (31, 22):
        raise AssertionError("unexpected seed-derived SAT arch")

    unsat_certificate, unsat_arches = exact_certificate(
        unsat_base_graph,
        unsat_base_primal,
        copies,
        (unsat_left, unsat_right),
        clause_size=3,
    )
    sat_certificate, sat_arches = exact_certificate(
        sat_base_graph,
        sat_base_primal,
        copies,
        (sat_left, sat_right),
        clause_size=4,
    )

    sat_witness = selected_sat_vertices(copies)
    assert_independent(sat_certificate["graph"], sat_witness)

    base_unsat_alpha = exact_alpha(graph_for_alpha(unsat_base_graph))
    if base_unsat_alpha != 7:
        raise AssertionError("base UNSAT independence number changed")

    return {
        "schema": "JANUS_SEEDED_ARCH_THETA_FAMILY_V1",
        "seed": SEED,
        "copies": copies,
        "target": 8 * copies,
        "sat": {
            "arch_local_pair": [sat_left, sat_right],
            "arch_score_sha256": sat_score,
            "arches": sat_arches,
            "independent_set_witness": sat_witness,
            "alpha": 8 * copies,
            "theta_certificate": sat_certificate,
        },
        "unsat": {
            "arch_local_pair": [unsat_left, unsat_right],
            "arch_score_sha256": unsat_score,
            "arches": unsat_arches,
            "alpha_upper_bound": 7 * copies,
            "theta_certificate": unsat_certificate,
        },
        "claim_boundary": (
            "These are connected graph-level theta twins obtained from standard "
            "CNF conflict graphs by adding certified zero-entry arch edges. The "
            "arched graphs need not themselves be standard conflict graphs of "
            "the original CNFs."
        ),
    }


def self_test() -> dict[str, Any]:
    member = build_family_member(copies=2)
    if member["target"] != 16:
        raise AssertionError("unexpected target")
    if member["sat"]["alpha"] != 16:
        raise AssertionError("SAT alpha witness has wrong size")
    if not member["unsat"]["alpha_upper_bound"] < member["target"]:
        raise AssertionError("UNSAT alpha bound does not separate the target")
    print("JANUS_SEEDED_ARCH_THETA_FAMILY = PASS")
    print(f"SEED = {SEED}")
    print("SAT_ARCH = 31,22")
    print("UNSAT_ARCH = 22,13")
    print("CONNECTED_COPIES = 2")
    print("EXACT_THETA = 16")
    return member


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--copies", type=int, default=2)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    member = self_test() if args.self_test else build_family_member(args.copies)
    if args.output:
        args.output.write_text(
            json.dumps(member, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    elif not args.self_test:
        print(json.dumps(member, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
