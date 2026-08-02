#!/usr/bin/env python3
"""Build the standard clause-literal conflict graph for a DIMACS CNF.

A vertex represents one literal occurrence in one clause. Vertices are adjacent
when they belong to the same clause or carry complementary literals. A CNF with
m clauses is satisfiable iff the graph has an independent set of size m.

The optional exact-alpha diagnostic is exponential and intended only for tiny
fixtures. It must not be embedded in a canonical theta profile.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DimacsCNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


def parse_dimacs_text(text: str) -> DimacsCNF:
    header: tuple[int, int] | None = None
    clauses: list[tuple[int, ...]] = []
    current: list[int] = []

    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p"):
            if header is not None:
                raise ValueError(f"line {line_number}: duplicate DIMACS header")
            parts = line.split()
            if len(parts) != 4 or parts[0] != "p" or parts[1] != "cnf":
                raise ValueError(f"line {line_number}: expected 'p cnf <vars> <clauses>'")
            try:
                variable_count = int(parts[2])
                clause_count = int(parts[3])
            except ValueError as exc:
                raise ValueError(f"line {line_number}: non-integer DIMACS counts") from exc
            if variable_count < 0 or clause_count < 0:
                raise ValueError(f"line {line_number}: negative DIMACS count")
            header = (variable_count, clause_count)
            continue

        if header is None:
            raise ValueError(f"line {line_number}: clause data appears before DIMACS header")

        variable_count, declared_clause_count = header
        for token in line.split():
            try:
                lit = int(token)
            except ValueError as exc:
                raise ValueError(f"line {line_number}: invalid literal token {token!r}") from exc
            if lit == 0:
                clauses.append(tuple(current))
                current = []
                if len(clauses) > declared_clause_count:
                    raise ValueError(
                        f"line {line_number}: more clauses than declared "
                        f"({declared_clause_count})"
                    )
                continue
            if abs(lit) < 1 or abs(lit) > variable_count:
                raise ValueError(
                    f"line {line_number}: literal {lit} is outside 1..{variable_count}"
                )
            current.append(lit)

    if header is None:
        raise ValueError("missing DIMACS header")
    if current:
        raise ValueError("DIMACS clause missing terminating 0")

    variable_count, declared_clause_count = header
    if len(clauses) != declared_clause_count:
        raise ValueError(
            f"declared {declared_clause_count} clauses but parsed {len(clauses)}"
        )
    return DimacsCNF(variable_count=variable_count, clauses=tuple(clauses))


def parse_dimacs(path: Path) -> DimacsCNF:
    return parse_dimacs_text(path.read_text(encoding="utf-8"))


def build_graph(cnf: DimacsCNF | list[list[int]] | tuple[tuple[int, ...], ...]) -> dict:
    if isinstance(cnf, DimacsCNF):
        variable_count = cnf.variable_count
        clauses = cnf.clauses
    else:
        clauses = tuple(tuple(clause) for clause in cnf)
        variable_count = max((abs(lit) for clause in clauses for lit in clause), default=0)

    vertices = []
    for clause_index, clause in enumerate(clauses):
        for occurrence, literal in enumerate(clause):
            vertices.append(
                {
                    "id": len(vertices),
                    "clause": clause_index,
                    "occurrence": occurrence,
                    "literal": literal,
                }
            )

    edges: set[tuple[int, int]] = set()
    for i, left in enumerate(vertices):
        for j in range(i + 1, len(vertices)):
            right = vertices[j]
            if (
                left["clause"] == right["clause"]
                or left["literal"] == -right["literal"]
            ):
                edges.add((i, j))

    return {
        "variable_count": variable_count,
        "clause_count": len(clauses),
        "vertices": vertices,
        "edges": [list(edge) for edge in sorted(edges)],
    }


def exact_alpha(graph: dict) -> int:
    vertex_count = len(graph["vertices"])
    adjacency = [0] * vertex_count
    for left, right in graph["edges"]:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left

    best = 0

    def search(candidates: int, chosen: int) -> None:
        nonlocal best
        if chosen + candidates.bit_count() <= best:
            return
        if candidates == 0:
            best = max(best, chosen)
            return
        vertex = (candidates & -candidates).bit_length() - 1
        search(candidates & ~(1 << vertex) & ~adjacency[vertex], chosen + 1)
        search(candidates & ~(1 << vertex), chosen)

    search((1 << vertex_count) - 1, 0)
    return best


def self_test() -> None:
    sat = parse_dimacs_text("p cnf 2 2\n1 0\n-1 2 0\n")
    assert sat.variable_count == 2
    assert sat.clauses == ((1,), (-1, 2))
    sat_graph = build_graph(sat)
    assert exact_alpha(sat_graph) == sat_graph["clause_count"]

    empty = parse_dimacs_text("c empty clause is valid DIMACS\np cnf 1 1\n0\n")
    assert empty.clauses == ((),)
    empty_graph = build_graph(empty)
    assert exact_alpha(empty_graph) == 0
    assert exact_alpha(empty_graph) != empty_graph["clause_count"]

    spanning = parse_dimacs_text("p cnf 3 1\n1 -2\n3 0\n")
    assert spanning.clauses == ((1, -2, 3),)

    bad_inputs = [
        "1 0\n",
        "p cnf 1 1\n2 0\n",
        "p cnf 1 2\n1 0\n",
        "p cnf 1 1\n1\n",
        "p cnf 1 1\n1 0\np cnf 1 1\n",
    ]
    for payload in bad_inputs:
        try:
            parse_dimacs_text(payload)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid DIMACS accepted: {payload!r}")

    print("JANUS_DIMACS_CONFLICT_GRAPH_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", nargs="?", type=Path)
    parser.add_argument("--exact-alpha", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0
    if args.cnf is None:
        parser.error("cnf is required unless --self-test is used")

    cnf = parse_dimacs(args.cnf)
    graph = build_graph(cnf)
    if args.exact_alpha:
        graph["diagnostic_schema"] = "JANUS_TEST_ONLY_ALPHA_V1"
        graph["exact_alpha"] = exact_alpha(graph)
        graph["satisfiable_by_reduction"] = (
            graph["exact_alpha"] == graph["clause_count"]
        )
        graph["claim_boundary"] = (
            "Exact alpha is exponential, answer-dependent, and forbidden inside "
            "canonical theta profiles."
        )

    encoded = json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
