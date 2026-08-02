#!/usr/bin/env python3
"""Tiny-instance answer-dependent diagnostics kept outside canonical profiles."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from conflict_graph import build_graph, exact_alpha, parse_dimacs


def diagnostics(path: Path) -> dict:
    raw = path.read_bytes()
    cnf = parse_dimacs(path)
    graph = build_graph(cnf)
    alpha = exact_alpha(graph)
    return {
        "schema": "JANUS_TEST_ONLY_DIAGNOSTICS_V1",
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "variable_count": cnf.variable_count,
        "clause_count": len(cnf.clauses),
        "vertex_count": len(graph["vertices"]),
        "exact_alpha": alpha,
        "satisfiable_by_conflict_graph_reduction": alpha == len(cnf.clauses),
        "claim_boundary": (
            "This artifact is exponential, answer-dependent, and test-only. "
            "It must never be merged into a canonical theta profile or used "
            "as a polynomial-time feature."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = diagnostics(args.cnf)
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
