#!/usr/bin/env python3
"""Preregistered topology/arity holdout for the unchanged generic producer.

The prediction was frozen in
research/C025_TSEITIN_PETERSEN_HOLDOUT_PREDICTION_2026-08-26.json before this
file existed.  This harness knows the graph and control labels; the producer
receives only the resulting raw clauses.
"""
from __future__ import annotations

import json
from itertools import product
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_b_to_a_finite_affine_synthesizer as synth
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base


def petersen_edges() -> tuple[tuple[int, int], ...]:
    raw = (
        (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
        (5, 7), (7, 9), (9, 6), (6, 8), (8, 5),
        (0, 5), (1, 6), (2, 7), (3, 8), (4, 9),
    )
    return tuple(sorted(tuple(sorted(edge)) for edge in raw))


def verify_graph(edges: tuple[tuple[int, int], ...]) -> None:
    if len(edges) != 15 or len(set(edges)) != 15:
        raise AssertionError("PETERSEN_EDGE_COUNT_DRIFT")
    adjacency = {vertex: set() for vertex in range(10)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    if any(len(adjacency[vertex]) != 3 for vertex in adjacency):
        raise AssertionError("PETERSEN_NOT_3_REGULAR")
    seen = {0}
    frontier = [0]
    while frontier:
        vertex = frontier.pop()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    if len(seen) != 10:
        raise AssertionError("PETERSEN_NOT_CONNECTED")


def build_formula(charged_vertices: frozenset[int]):
    edges = petersen_edges()
    verify_graph(edges)
    edge_id = {edge: index + 1 for index, edge in enumerate(edges)}
    incident: dict[int, list[int]] = {vertex: [] for vertex in range(10)}
    for edge, variable in edge_id.items():
        left, right = edge
        incident[left].append(variable)
        incident[right].append(variable)

    clauses = []
    for vertex in range(10):
        scope = tuple(sorted(incident[vertex]))
        if len(scope) != 3:
            raise AssertionError("HOLDOUT_SCOPE_WIDTH_DRIFT")
        local_bit = 1 if vertex in charged_vertices else 0
        for bits in product((0, 1), repeat=3):
            if sum(bits) % 2 == local_bit:
                continue
            clauses.append(tuple(variable if bit == 0 else -variable for variable, bit in zip(scope, bits)))
    return base.canon_cnf(clauses)


def inspect_certificate(certificate: dict) -> dict:
    scopes = certificate["scopes"]
    widths = sorted({len(scope["variables"]) for scope in scopes})
    allowed_counts = sorted({int(scope["allowed_boolean_tuple_count"]) for scope in scopes})
    equations_per_scope = sorted({len(scope["equations"]) for scope in scopes})
    return {
        "decision": certificate["decision"],
        "selected_modulus": certificate["modulus"],
        "resource_key": certificate["resource_key"],
        "raw_variables": certificate["resource_ledger"]["raw_variables"],
        "raw_clauses": certificate["resource_ledger"]["raw_clauses"],
        "discovered_scope_count": certificate["resource_ledger"]["discovered_scopes"],
        "scope_widths": widths,
        "allowed_boolean_tuple_counts": allowed_counts,
        "equations_per_scope": equations_per_scope,
        "local_truth_table_tuples_examined": certificate["resource_ledger"]["local_truth_table_tuples_examined"],
        "global_equation_count": certificate["global_equation_count"],
        "global_rank": certificate["global_rank"],
        "all_variables_touch_exactly_two_scopes": certificate["incidence"]["all_variables_touch_exactly_two_scopes"],
        "constraint_component_count": certificate["incidence"]["constraint_component_count"],
        "contradiction_row_count": None if certificate["contradiction"] is None else certificate["contradiction"]["row_count"],
        "has_witness": certificate["witness"] is not None,
        "source_fingerprint": certificate["source_fingerprint"],
    }


def main() -> int:
    sat_raw = build_formula(frozenset({0, 1}))
    unsat_raw = build_formula(frozenset({0}))
    if len(base.vars_of(sat_raw)) != 15 or len(sat_raw) != 40:
        raise AssertionError("SAT_RAW_SIZE_PREDICTION_MISMATCH")
    if len(base.vars_of(unsat_raw)) != 15 or len(unsat_raw) != 40:
        raise AssertionError("UNSAT_RAW_SIZE_PREDICTION_MISMATCH")

    sat_certificate = synth.synthesize(sat_raw)
    unsat_certificate = synth.synthesize(unsat_raw)
    sat_verified = synth.verify_certificate(sat_raw, sat_certificate)
    unsat_verified = synth.verify_certificate(unsat_raw, unsat_certificate)
    if not sat_verified or not unsat_verified:
        raise AssertionError("HOLDOUT_INDEPENDENT_VERIFIER_FAILED")

    sat = inspect_certificate(sat_certificate)
    unsat = inspect_certificate(unsat_certificate)
    expected_common = {
        "selected_modulus": 2,
        "resource_key": [10, 2],
        "raw_variables": 15,
        "raw_clauses": 40,
        "discovered_scope_count": 10,
        "scope_widths": [3],
        "allowed_boolean_tuple_counts": [4],
        "equations_per_scope": [1],
        "local_truth_table_tuples_examined": 80,
        "global_equation_count": 10,
        "global_rank": 9,
        "all_variables_touch_exactly_two_scopes": True,
        "constraint_component_count": 1,
    }
    for label, record in (("SAT", sat), ("UNSAT", unsat)):
        for key, expected in expected_common.items():
            if record[key] != expected:
                raise AssertionError(f"{label}_{key}_PREDICTION_MISMATCH:{record[key]}!={expected}")

    if sat["decision"] != "SAT" or not sat["has_witness"] or sat["contradiction_row_count"] is not None:
        raise AssertionError("SAT_CONTROL_PREDICTION_MISMATCH")
    if unsat["decision"] != "UNSAT" or unsat["has_witness"] or unsat["contradiction_row_count"] != 10:
        raise AssertionError("UNSAT_CONTROL_PREDICTION_MISMATCH")

    report = {
        "schema": "JANUS/C025/TSEITIN-PETERSEN-HOLDOUT-RESULT/v1",
        "status": "PASS",
        "prediction_commit": "21018b4c41dcffa67c556d7999486a4c3073d969",
        "producer_commit_frozen_before_holdout": "e827ede82785818cbbe550e99c2b08082c67d3e4",
        "producer_modified_for_holdout": False,
        "producer_received": "RAW_CNF_ONLY",
        "topology_transfer": "TOROIDAL_GRID_TO_PETERSEN_GRAPH",
        "arity_transfer": "4_TO_3",
        "sat": {**sat, "independent_verifier": sat_verified},
        "unsat": {**unsat, "independent_verifier": unsat_verified},
        "prediction_mismatches": 0,
        "scientific_boundary": {
            "bounded_scope_finite_affine_class": "EXACT_PASS",
            "arbitrary_CNF_coverage": "OPEN",
            "unbounded_scope_polynomiality": "NOT_ESTABLISHED",
            "universal_polynomial_SAT_algorithm": "OPEN",
            "P_VS_NP": "OPEN"
        }
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
