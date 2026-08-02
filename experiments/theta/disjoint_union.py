#!/usr/bin/env python3
"""Disjoint-variable CNF union and conflict-graph amplification checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from conflict_graph import DimacsCNF, build_graph, exact_alpha, parse_dimacs


def disjoint_union(cnfs: list[DimacsCNF]) -> DimacsCNF:
    offset = 0
    clauses: list[tuple[int, ...]] = []
    for cnf in cnfs:
        for clause in cnf.clauses:
            clauses.append(
                tuple(
                    literal + offset if literal > 0 else literal - offset
                    for literal in clause
                )
            )
        offset += cnf.variable_count
    return DimacsCNF(variable_count=offset, clauses=tuple(clauses))


def verify_graph_disjointness(cnfs: list[DimacsCNF]) -> dict:
    combined = disjoint_union(cnfs)
    combined_graph = build_graph(combined)
    component_graphs = [build_graph(cnf) for cnf in cnfs]

    expected_vertices = sum(len(graph["vertices"]) for graph in component_graphs)
    expected_edges = sum(len(graph["edges"]) for graph in component_graphs)
    if len(combined_graph["vertices"]) != expected_vertices:
        raise ValueError("combined graph has an unexpected vertex count")
    if len(combined_graph["edges"]) != expected_edges:
        raise ValueError("cross-component conflict edges were introduced")

    component_alpha = [exact_alpha(graph) for graph in component_graphs]
    combined_alpha = exact_alpha(combined_graph)
    if combined_alpha != sum(component_alpha):
        raise ValueError("independence number was not additive")

    return {
        "component_count": len(cnfs),
        "variable_count": combined.variable_count,
        "clause_count": len(combined.clauses),
        "vertex_count": len(combined_graph["vertices"]),
        "edge_count": len(combined_graph["edges"]),
        "component_alpha": component_alpha,
        "combined_alpha": combined_alpha,
        "claim_boundary": (
            "This executable check proves graph disjointness and alpha additivity "
            "for the supplied finite fixtures. Theta additivity is a separate "
            "mathematical lemma recorded by H095."
        ),
    }


def self_test() -> None:
    sat = DimacsCNF(variable_count=2, clauses=((1,), (2,)))
    unsat = DimacsCNF(variable_count=1, clauses=((1,), (-1,)))
    report = verify_graph_disjointness([sat, unsat, sat])
    assert report["component_alpha"] == [2, 1, 2]
    assert report["combined_alpha"] == 5
    assert report["clause_count"] == 6
    print("JANUS_DISJOINT_UNION_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not args.cnf:
        parser.error("provide at least one CNF or use --self-test")
    report = verify_graph_disjointness([parse_dimacs(path) for path in args.cnf])
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
