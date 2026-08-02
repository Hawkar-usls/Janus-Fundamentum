#!/usr/bin/env python3
"""Build a finite canonical theta-profile interface for JANUS C009.

This tool does not solve an SDP. It freezes the exact observable interface used
by H078 so that future solvers cannot add answer-dependent "statistics".
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

from conflict_graph import build_graph, exact_alpha, parse_dimacs


def normalize_clauses(clauses: list[list[int]]) -> list[list[int]]:
    def lit_key(lit: int) -> tuple[int, int]:
        return (abs(lit), 0 if lit > 0 else 1)

    normalized = [sorted(dict.fromkeys(clause), key=lit_key) for clause in clauses]
    normalized.sort(key=lambda clause: (len(clause), tuple(clause)))
    return normalized


def monomial_basis(vertex_count: int, max_degree: int) -> list[list[int]]:
    basis: list[list[int]] = [[]]
    for degree in range(1, max_degree + 1):
        basis.extend([list(term) for term in itertools.combinations(range(vertex_count), degree)])
    return basis


def canonical_profile(clauses: list[list[int]], level: int, include_exact_alpha: bool = False) -> dict:
    if level < 1:
        raise ValueError("level must be at least one")
    normalized = normalize_clauses(clauses)
    graph = build_graph(normalized)
    adjacency_payload = json.dumps(
        {"vertices": graph["vertices"], "edges": graph["edges"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    profile = {
        "schema": "JANUS_THETA_PROFILE_V1",
        "encoding": "clause_literal_conflict_graph",
        "level": level,
        "maximum_monomial_degree": 2 * level,
        "normalized_clauses": normalized,
        "clause_count": graph["clause_count"],
        "vertex_count": len(graph["vertices"]),
        "edge_count": len(graph["edges"]),
        "graph_sha256": hashlib.sha256(adjacency_payload).hexdigest(),
        "monomial_basis": monomial_basis(len(graph["vertices"]), 2 * level),
        "registered_objectives": ["independent_set_target", "lovasz_theta_primal_value"],
        "registered_dual_statistics": [
            "dual_objective_value",
            "minimum_reported_psd_slack",
            "rational_certificate_bit_length",
        ],
        "claim_boundary": (
            "This file defines coordinates and permitted observables only. "
            "It contains no theta value unless a separate solver artifact supplies one."
        ),
    }
    if include_exact_alpha:
        profile["exact_alpha"] = exact_alpha(graph)
        profile["satisfiable_by_exact_reduction"] = profile["exact_alpha"] == graph["clause_count"]
    return profile


def self_test() -> None:
    sat = canonical_profile([[1], [-1, 2]], level=1, include_exact_alpha=True)
    unsat = canonical_profile([[1], [-1]], level=1, include_exact_alpha=True)
    assert sat["satisfiable_by_exact_reduction"] is True
    assert unsat["satisfiable_by_exact_reduction"] is False
    assert sat["schema"] == "JANUS_THETA_PROFILE_V1"
    assert sat["monomial_basis"][0] == []
    assert sat["graph_sha256"] != unsat["graph_sha256"]
    reordered = canonical_profile([[-1, 2], [1]], level=1, include_exact_alpha=True)
    assert reordered["graph_sha256"] == sat["graph_sha256"]
    print("JANUS_THETA_PROFILE_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", nargs="?", type=Path)
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--exact-alpha", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.cnf is None:
        parser.error("cnf is required unless --self-test is used")

    profile = canonical_profile(parse_dimacs(args.cnf), args.level, args.exact_alpha)
    encoded = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
