#!/usr/bin/env python3
"""AUTONOMOUS_ALGEBRA_INVENTION_GATE v2 calibration harness.

The producer under test receives only extensional Boolean relations and searches
all operation tables of arity 1..3.  This harness labels four known calibration
operations only AFTER discovery.  Their names never enter the producer.
"""
from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_autonomous_boolean_operation_discovery as discovery


def table(arity, fn):
    return tuple(fn(*args) for args in product((0, 1), repeat=arity))


CALIBRATION_TABLES = {
    "BINARY_MEET_REFERENCE": table(2, lambda x, y: x & y),
    "BINARY_JOIN_REFERENCE": table(2, lambda x, y: x | y),
    "TERNARY_THRESHOLD_REFERENCE": table(3, lambda x, y, z: int(x + y + z >= 2)),
    "TERNARY_PARITY_REFERENCE": table(3, lambda x, y, z: x ^ y ^ z),
}


def contains(report: dict, arity: int, expected: tuple[int, ...]) -> bool:
    return any(
        tuple(record["table"]) == expected
        for record in report["discovered_operations_by_arity"][str(arity)]
    )


def score_case(case_name: str, relation, expected_key: str) -> dict:
    report = discovery.discover([relation], max_arity=3)
    if not discovery.verify_discovery([relation], report):
        raise AssertionError(f"{case_name}_INDEPENDENT_DISCOVERY_VERIFIER_FAILED")
    presence = {
        key: contains(report, 2 if key.startswith("BINARY") else 3, op_table)
        for key, op_table in CALIBRATION_TABLES.items()
    }
    if not presence[expected_key]:
        raise AssertionError(f"{case_name}_EXPECTED_OPERATION_NOT_DISCOVERED")
    unexpected = [key for key, hit in presence.items() if key != expected_key and hit]
    if unexpected:
        raise AssertionError(f"{case_name}_CALIBRATION_NOT_SEPARATING:{unexpected}")
    return {
        "case": case_name,
        "relation": [list(row) for row in relation],
        "posthoc_calibration_presence": presence,
        "expected_posthoc_label": expected_key,
        "producer_nonprojection_count": report["nonprojection_operation_count"],
        "producer_preserving_count": report["preserving_operation_count"],
        "ledger": report["ledger"],
        "source_fingerprint": report["source_fingerprint"],
        "producer_used_family_label": report["family_label_used"],
        "producer_used_preselected_algebra_name": report["preselected_algebra_name_used"],
        "producer_used_heuristic_promotion": report["heuristic_promotion_used"],
    }


def main() -> int:
    cube = tuple(product((0, 1), repeat=3))

    # Four separating calibration relations.  The comments are human-side test
    # provenance only; the producer receives just the tuples.
    relation_a = tuple(bits for bits in cube if bits != (1, 1, 0))
    relation_b = tuple(bits for bits in cube if bits != (0, 0, 1))
    relation_c = ((0, 0, 1), (0, 1, 1), (1, 0, 0), (1, 0, 1))
    relation_d = tuple(bits for bits in cube if sum(bits) % 2 == 0)

    cases = [
        score_case("CALIBRATION_A", relation_a, "BINARY_MEET_REFERENCE"),
        score_case("CALIBRATION_B", relation_b, "BINARY_JOIN_REFERENCE"),
        score_case("CALIBRATION_C", relation_c, "TERNARY_THRESHOLD_REFERENCE"),
        score_case("CALIBRATION_D", relation_d, "TERNARY_PARITY_REFERENCE"),
    ]

    if any(
        row["producer_used_family_label"]
        or row["producer_used_preselected_algebra_name"]
        or row["producer_used_heuristic_promotion"]
        for row in cases
    ):
        raise AssertionError("DISCOVERY_FIREWALL_VIOLATION")

    report = {
        "schema": "JANUS/C025/AUTONOMOUS-ALGEBRA-INVENTION-GATE-v2",
        "status": "PASS",
        "producer_input": "EXTENSIONAL_BOOLEAN_RELATIONS_ONLY",
        "producer_operation_search": "ALL_BOOLEAN_TRUTH_TABLES_ARITY_1_TO_3",
        "posthoc_labels_not_visible_to_producer": True,
        "cases": cases,
        "what_pass_means": (
            "ONE_GENERIC_EXACT_PRODUCER_RECOVERS_FOUR_SEPARATING_BOOLEAN_"
            "POLYMORPHISM_PATTERNS_WITHOUT_FAMILY_LABELS_OR_PRESELECTED_TABLES"
        ),
        "what_pass_does_not_mean": (
            "GENERAL_CNF_POLYNOMIAL_SOLVABILITY_OR_AUTONOMOUS_DISCOVERY_"
            "BEYOND_THE_ENUMERATED_BOOLEAN_OPERATION_SPACE"
        ),
        "complexity_boundary": (
            "OPERATION_SPACE_IS_CONSTANT_FOR_BOOLEAN_ARITY_LE_3;_EXTENSIONAL_"
            "RELATION_CONSTRUCTION_FROM_UNBOUNDED_WIDE_CNF_REMAINS_A_DEBT"
        ),
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
