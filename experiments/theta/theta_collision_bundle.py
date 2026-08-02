#!/usr/bin/env python3
"""Verify finite exact-theta collision bundles for H096.

A component contains a graph, a clause target, and an exact primal/dual theta
certificate. Exact alpha is recomputed exponentially and kept as a diagnostic.
A collision bundle is accepted only when one component is SAT by the standard
conflict-graph reduction, the other is UNSAT, the clause targets agree, and the
certified theta values are exactly equal.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from conflict_graph import exact_alpha
from lovasz_theta_certificate import validate_graph, verify_exact_theta
from rational_ldl import encode_fraction


def graph_for_alpha(graph: dict[str, Any]) -> dict[str, Any]:
    vertex_count, edges = validate_graph(graph)
    return {
        "vertices": [{"id": index} for index in range(vertex_count)],
        "edges": [list(edge) for edge in edges],
    }


def verify_component(component: dict[str, Any]) -> dict[str, Any]:
    target = component.get("clause_target")
    if not isinstance(target, int) or target <= 0:
        raise ValueError("component clause_target must be a positive integer")
    certificate = component.get("theta_certificate")
    if not isinstance(certificate, dict):
        raise ValueError("component lacks theta_certificate")
    theta = verify_exact_theta(certificate)
    graph = certificate.get("graph", {})
    alpha = exact_alpha(graph_for_alpha(graph))
    return {
        "clause_target": target,
        "theta": theta,
        "alpha": alpha,
        "satisfiable_by_conflict_graph_reduction": alpha == target,
    }


def verify_collision_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    left = verify_component(bundle.get("left", {}))
    right = verify_component(bundle.get("right", {}))
    if left["clause_target"] != right["clause_target"]:
        raise ValueError("collision components have different clause targets")
    if left["satisfiable_by_conflict_graph_reduction"] == right[
        "satisfiable_by_conflict_graph_reduction"
    ]:
        raise ValueError("collision components do not have opposite SAT labels")
    if left["theta"] != right["theta"]:
        raise ValueError(
            f"theta values differ: {left['theta']} != {right['theta']}"
        )
    return {
        "schema": "JANUS_EXACT_THETA_COLLISION_V1",
        "clause_target": left["clause_target"],
        "theta": encode_fraction(left["theta"]),
        "left_alpha": left["alpha"],
        "right_alpha": right["alpha"],
        "claim_boundary": (
            "A finite accepted bundle is a certified level-one collision seed. "
            "It becomes an infinite family only after the separate H095 "
            "disjoint-union amplification lemma is independently verified."
        ),
    }


def _ldl(matrix: list[list[str]]) -> dict[str, Any]:
    from rational_ldl import decompose_psd, encode_certificate, parse_matrix

    return encode_certificate(decompose_psd(parse_matrix(matrix)))


def self_test() -> None:
    sat_certificate = {
        "graph": {"vertex_count": 2, "edges": []},
        "primal": {
            "matrix": [["1/2", "1/2"], ["1/2", "1/2"]],
            "ldl": _ldl([["1/2", "1/2"], ["1/2", "1/2"]]),
        },
        "dual": {
            "objective": "2",
            "edge_multipliers": {},
            "slack_ldl": _ldl([["1", "-1"], ["-1", "1"]]),
        },
    }
    unsat_certificate = {
        "graph": {"vertex_count": 2, "edges": [[0, 1]]},
        "primal": {
            "matrix": [["1", "0"], ["0", "0"]],
            "ldl": _ldl([["1", "0"], ["0", "0"]]),
        },
        "dual": {
            "objective": "1",
            "edge_multipliers": {"0,1": "1"},
            "slack_ldl": _ldl([["0", "0"], ["0", "0"]]),
        },
    }
    sat = verify_component(
        {"clause_target": 2, "theta_certificate": sat_certificate}
    )
    unsat = verify_component(
        {"clause_target": 2, "theta_certificate": unsat_certificate}
    )
    assert sat["satisfiable_by_conflict_graph_reduction"] is True
    assert unsat["satisfiable_by_conflict_graph_reduction"] is False

    try:
        verify_collision_bundle(
            {
                "left": {"clause_target": 2, "theta_certificate": sat_certificate},
                "right": {
                    "clause_target": 2,
                    "theta_certificate": unsat_certificate,
                },
            }
        )
    except ValueError as exc:
        assert "theta values differ" in str(exc)
    else:
        raise AssertionError("non-collision bundle was accepted")

    print("JANUS_THETA_COLLISION_BUNDLE_SELF_TEST = PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.bundle is None:
        parser.error("bundle JSON is required unless --self-test is used")
    result = verify_collision_bundle(
        json.loads(args.bundle.read_text(encoding="utf-8"))
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
