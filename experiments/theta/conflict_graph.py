#!/usr/bin/env python3
"""Build the standard clause-literal conflict graph for a DIMACS CNF.

A vertex represents one literal occurrence in one clause. Vertices are adjacent
when they belong to the same clause or carry complementary literals. A CNF with
m clauses is satisfiable iff the graph has an independent set of size m.

The optional exact alpha computation is exponential and intended only for small
reproducibility fixtures. This script does not compute the Lovasz theta number.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_dimacs(path: Path) -> list[list[int]]:
    clauses: list[list[int]] = []
    current: list[int] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c") or line.startswith("p"):
            continue
        for token in line.split():
            lit = int(token)
            if lit == 0:
                if not current:
                    raise ValueError("empty clause is not supported in this seed tool")
                clauses.append(current)
                current = []
            else:
                current.append(lit)
    if current:
        raise ValueError("DIMACS clause missing terminating 0")
    return clauses


def build_graph(clauses: list[list[int]]) -> dict:
    vertices = []
    for ci, clause in enumerate(clauses):
        for oi, lit in enumerate(clause):
            vertices.append({"id": len(vertices), "clause": ci, "occurrence": oi, "literal": lit})

    edges: set[tuple[int, int]] = set()
    for i, u in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            v = vertices[j]
            if u["clause"] == v["clause"] or u["literal"] == -v["literal"]:
                edges.add((i, j))
    return {
        "clause_count": len(clauses),
        "vertices": vertices,
        "edges": [list(edge) for edge in sorted(edges)],
    }


def exact_alpha(graph: dict) -> int:
    n = len(graph["vertices"])
    adjacency = [0] * n
    for u, v in graph["edges"]:
        adjacency[u] |= 1 << v
        adjacency[v] |= 1 << u

    best = 0

    def search(candidates: int, chosen: int) -> None:
        nonlocal best
        if chosen + candidates.bit_count() <= best:
            return
        if candidates == 0:
            best = max(best, chosen)
            return
        v = (candidates & -candidates).bit_length() - 1
        search(candidates & ~(1 << v) & ~adjacency[v], chosen + 1)
        search(candidates & ~(1 << v), chosen)

    search((1 << n) - 1, 0)
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--exact-alpha", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    clauses = parse_dimacs(args.cnf)
    graph = build_graph(clauses)
    if args.exact_alpha:
        graph["exact_alpha"] = exact_alpha(graph)
        graph["satisfiable_by_reduction"] = graph["exact_alpha"] == graph["clause_count"]

    encoded = json.dumps(graph, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
