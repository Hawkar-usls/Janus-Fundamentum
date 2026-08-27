#!/usr/bin/env python3
"""Hostile bounded totality probe for PIRC_DECISION_CORE_V0_3.

Generate a frozen deterministic corpus of graph 4-colorability CNFs.  Graph
colorability is used only as an adversarial source of arbitrary-looking CNF
structure; no family label is supplied to the decision core and no graph solver
participates in its verdict.

If the JANUS core returns OPEN, a tiny independent exponential backtracker is
allowed *afterward* in this research harness only to label the finite specimen.
That oracle result has zero theorem/runtime authority.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
import random

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_pirc_decision_core_v0_3 as core

P_VS_NP = "OPEN"


def color_var(vertex: int, color: int, colors: int) -> int:
    return 1 + vertex * colors + color


def color_cnf(nvertices: int, colors: int, edges: tuple[tuple[int, int], ...]):
    clauses = []
    # Exactly one color per vertex.
    for vertex in range(nvertices):
        row = tuple(color_var(vertex, color, colors) for color in range(colors))
        clauses.append(row)
        for left in range(colors):
            for right in range(left + 1, colors):
                clauses.append((-row[left], -row[right]))
    # Adjacent vertices cannot share a color.
    for u, v in edges:
        for color in range(colors):
            clauses.append((-color_var(u, color, colors), -color_var(v, color, colors)))
    return base.canon_cnf(clauses)


def seeded_graph(nvertices: int, numerator: int, denominator: int, seed: int):
    rng = random.Random(seed)
    edges = []
    for u in range(nvertices):
        for v in range(u + 1, nvertices):
            if rng.randrange(denominator) < numerator:
                edges.append((u, v))
    return tuple(edges)


def exact_backtracking_colorable(nvertices: int, colors: int, edges: tuple[tuple[int, int], ...]) -> bool:
    """Finite-specimen labeler only; forbidden from theorem runtime."""
    adjacency = [set() for _ in range(nvertices)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    order = sorted(range(nvertices), key=lambda v: (-len(adjacency[v]), v))
    assignment = [-1] * nvertices

    def visit(index: int) -> bool:
        if index == len(order):
            return True
        vertex = order[index]
        forbidden = {assignment[n] for n in adjacency[vertex] if assignment[n] >= 0}
        for color in range(colors):
            if color in forbidden:
                continue
            assignment[vertex] = color
            if visit(index + 1):
                return True
        assignment[vertex] = -1
        return False

    return visit(0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-per-rung", type=int, default=8)
    args = parser.parse_args()

    # Frozen before results: increasing vertex count and two deterministic densities.
    rungs = (
        ("C4_N6_P2_5", 6, 2, 5, 4100),
        ("C4_N7_P2_5", 7, 2, 5, 4200),
        ("C4_N8_P2_5", 8, 2, 5, 4300),
        ("C4_N8_P3_5", 8, 3, 5, 4400),
    )
    colors = 4
    totals = {"examined": 0, "SAT": 0, "UNSAT": 0, "OPEN": 0}
    first_open = None
    rows = []

    for rung_id, nvertices, num, den, base_seed in rungs:
        rung = {"id": rung_id, "examined": 0, "SAT": 0, "UNSAT": 0, "OPEN": 0}
        for offset in range(args.cases_per_rung):
            seed = base_seed + offset
            edges = seeded_graph(nvertices, num, den, seed)
            cnf = color_cnf(nvertices, colors, edges)
            result = core.solve_decision_core(cnf)
            status = result["status"]
            if status not in {"SAT", "UNSAT", "OPEN"}:
                raise AssertionError("UNEXPECTED_DECISION_CORE_STATUS")
            totals["examined"] += 1
            totals[status] += 1
            rung["examined"] += 1
            rung[status] += 1

            if status == "OPEN" and first_open is None:
                truth = exact_backtracking_colorable(nvertices, colors, edges)
                first_open = {
                    "rung": rung_id,
                    "seed": seed,
                    "nvertices": nvertices,
                    "colors": colors,
                    "edge_count": len(edges),
                    "edges": [list(edge) for edge in edges],
                    "cnf_fingerprint": base.fingerprint(cnf),
                    "N": result["N"],
                    "residual_fingerprint": result["residual_fingerprint"],
                    "residual_units": result["residual_units"],
                    "progress_phi": result["progress_phi"],
                    "reason": result["reason"],
                    "missing_bridge": result.get("missing_bridge"),
                    "independent_finite_truth_label": "SAT" if truth else "UNSAT",
                    "truth_label_method": "EXPONENTIAL_GRAPH_BACKTRACKING_RESEARCH_ONLY",
                    "ledger": result["ledger"],
                }
                break
        rows.append(rung)
        if first_open is not None:
            break

    report = {
        "schema": "JANUS/C025/COLORABILITY-TOTALITY-HOSTILE-PROBE/v1",
        "status": "FINITE_OPEN_COUNTEREXAMPLE_FOUND" if first_open else "NO_OPEN_IN_BOUNDED_COLORABILITY_CORPUS",
        "decision_core": "PIRC_DECISION_CORE_V0_3",
        "colors": colors,
        "rungs": rows,
        "totals": totals,
        "first_open": first_open,
        "scientific_boundary": {
            "bounded_finite_probe_only": True,
            "graph_family_label_not_supplied_to_decision_core": True,
            "independent_backtracking_used_only_after_OPEN_for_finite_label": True,
            "absence_of_open_is_not_totality_proof": True,
            "found_open_refutes_only_frozen_v0_3_totality": True,
            "REACHABLE_MOVE_OR_TERMINAL_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
