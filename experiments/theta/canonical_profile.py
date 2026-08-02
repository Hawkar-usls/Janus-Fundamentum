#!/usr/bin/env python3
"""Build a finite answer-independent theta-profile interface for JANUS.

This tool does not solve an SDP. It freezes the encoding, exact small-instance
variable canonicalization, monomial coordinates, objectives, and certificate
fields used by H078 and H087. Exact-alpha diagnostics live in diagnostics.py.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

from conflict_graph import DimacsCNF, build_graph, parse_dimacs


MAX_EXACT_CANONICAL_VARIABLES = 8
MAX_EMITTED_MONOMIALS = 100_000


def literal_key(literal: int) -> tuple[int, int]:
    return (abs(literal), 0 if literal > 0 else 1)


def normalized_tuple(
    clauses: tuple[tuple[int, ...], ...], mapping: dict[int, int]
) -> tuple[tuple[int, ...], ...]:
    mapped = []
    for clause in clauses:
        transformed = [
            mapping[abs(literal)] if literal > 0 else -mapping[abs(literal)]
            for literal in clause
        ]
        mapped.append(tuple(sorted(transformed, key=literal_key)))
    return tuple(sorted(mapped, key=lambda clause: (len(clause), clause)))


def exact_variable_canonicalization(
    cnf: DimacsCNF, max_variables: int = MAX_EXACT_CANONICAL_VARIABLES
) -> tuple[tuple[int, ...], ...]:
    used = sorted({abs(literal) for clause in cnf.clauses for literal in clause})
    if len(used) > max_variables:
        raise ValueError(
            "exact variable canonicalization supports at most "
            f"{max_variables} used variables; got {len(used)}. "
            "Provide a separately verified canonical-label artifact instead "
            "of treating a heuristic relabeling as canonical."
        )
    if not used:
        return tuple(sorted(cnf.clauses, key=lambda clause: (len(clause), clause)))

    best: tuple[tuple[int, ...], ...] | None = None
    labels = range(1, len(used) + 1)
    for permutation in itertools.permutations(labels):
        mapping = dict(zip(used, permutation, strict=True))
        candidate = normalized_tuple(cnf.clauses, mapping)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best


def monomial_count(variable_count: int, maximum_degree: int) -> int:
    return sum(math.comb(variable_count, degree) for degree in range(maximum_degree + 1))


def monomial_basis(
    variable_count: int,
    maximum_degree: int,
    maximum_terms: int = MAX_EMITTED_MONOMIALS,
) -> list[list[int]]:
    count = monomial_count(variable_count, maximum_degree)
    if count > maximum_terms:
        raise ValueError(
            f"monomial basis would contain {count} terms; limit is {maximum_terms}"
        )
    basis: list[list[int]] = [[]]
    for degree in range(1, maximum_degree + 1):
        basis.extend(
            [list(term) for term in itertools.combinations(range(variable_count), degree)]
        )
    return basis


def canonical_profile(cnf: DimacsCNF, level: int) -> dict:
    if level < 1:
        raise ValueError("level must be at least one")

    canonical_clauses = exact_variable_canonicalization(cnf)
    used_variable_count = len(
        {abs(literal) for clause in canonical_clauses for literal in clause}
    )
    canonical_cnf = DimacsCNF(
        variable_count=used_variable_count,
        clauses=canonical_clauses,
    )
    graph = build_graph(canonical_cnf)
    adjacency_payload = json.dumps(
        {
            "vertices": graph["vertices"],
            "edges": graph["edges"],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return {
        "schema": "JANUS_THETA_PROFILE_V2",
        "encoding": "clause_literal_conflict_graph",
        "canonicalization": {
            "method": "exhaustive_variable_permutation",
            "maximum_supported_used_variables": MAX_EXACT_CANONICAL_VARIABLES,
            "answer_independent": True,
        },
        "level": level,
        "maximum_monomial_degree": 2 * level,
        "declared_variable_count": cnf.variable_count,
        "used_variable_count": used_variable_count,
        "canonical_clauses": [list(clause) for clause in canonical_clauses],
        "clause_count": graph["clause_count"],
        "vertex_count": len(graph["vertices"]),
        "edge_count": len(graph["edges"]),
        "graph_sha256": hashlib.sha256(adjacency_payload).hexdigest(),
        "monomial_basis": monomial_basis(len(graph["vertices"]), 2 * level),
        "registered_objectives": [
            "independent_set_target",
            "lovasz_theta_primal_value",
        ],
        "registered_dual_statistics": [
            "dual_objective_value",
            "minimum_reported_psd_slack",
            "rational_certificate_bit_length",
        ],
        "forbidden_answer_dependent_fields": [
            "exact_alpha",
            "satisfiable",
            "satisfiable_by_reduction",
            "sat_label",
        ],
        "claim_boundary": (
            "This profile defines answer-independent coordinates and permitted "
            "observables only. It contains no theta value unless a separate "
            "solver artifact supplies one, and it never contains exact alpha."
        ),
    }


def self_test() -> None:
    first = DimacsCNF(
        variable_count=3,
        clauses=((1, -2), (2, 3)),
    )
    renamed = DimacsCNF(
        variable_count=3,
        clauses=((2, -3), (3, 1)),
    )
    reordered = DimacsCNF(
        variable_count=3,
        clauses=((2, 3), (-2, 1)),
    )

    first_profile = canonical_profile(first, level=1)
    renamed_profile = canonical_profile(renamed, level=1)
    reordered_profile = canonical_profile(reordered, level=1)

    assert first_profile["canonical_clauses"] == renamed_profile["canonical_clauses"]
    assert first_profile["graph_sha256"] == renamed_profile["graph_sha256"]
    assert first_profile["graph_sha256"] == reordered_profile["graph_sha256"]
    assert first_profile["monomial_basis"][0] == []
    assert "exact_alpha" not in first_profile
    assert first_profile["canonicalization"]["answer_independent"] is True

    empty = DimacsCNF(variable_count=1, clauses=((),))
    empty_profile = canonical_profile(empty, level=1)
    assert empty_profile["canonical_clauses"] == [[]]
    assert empty_profile["clause_count"] == 1
    assert empty_profile["vertex_count"] == 0

    too_large = DimacsCNF(
        variable_count=9,
        clauses=tuple((index,) for index in range(1, 10)),
    )
    try:
        canonical_profile(too_large, level=1)
    except ValueError as exc:
        assert "at most 8" in str(exc)
    else:
        raise AssertionError("unsupported large exact canonicalization was accepted")

    print("JANUS_THETA_PROFILE_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", nargs="?", type=Path)
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.cnf is None:
        parser.error("cnf is required unless --self-test is used")

    profile = canonical_profile(parse_dimacs(args.cnf), args.level)
    encoded = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
