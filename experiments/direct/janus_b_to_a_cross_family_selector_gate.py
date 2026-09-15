#!/usr/bin/env python3
"""Cross-family gate for one exact JANUS algebra selector.

The harness knows which controls it generated only for post-selection scoring.
The selector itself receives raw clauses and no family label.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_b_to_a_exact_algebra_selector as selector
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct.janus_tseitin_b_to_a_petersen_holdout import build_formula as build_petersen


def check_case(name: str, raw, expected_status: str, expected_algebra: str | None) -> dict:
    result = selector.select_exact_algebra(raw)
    if result["status"] != expected_status:
        raise AssertionError(f"{name}_STATUS_MISMATCH:{result['status']}!={expected_status}")
    if expected_algebra is None:
        if result.get("selected_algebra") is not None:
            raise AssertionError(f"{name}_UNEXPECTED_ALGEBRA")
        if result["status"] != "OPEN":
            raise AssertionError(f"{name}_EXPECTED_OPEN")
        verified = None
    else:
        if result.get("selected_algebra") != expected_algebra:
            raise AssertionError(f"{name}_ALGEBRA_MISMATCH:{result.get('selected_algebra')}!={expected_algebra}")
        if not selector.verify_selector_result(raw, result):
            raise AssertionError(f"{name}_SELECTED_CERTIFICATE_VERIFIER_FAILED")
        admitted = [attempt for attempt in result["attempts"] if attempt["status"] == "ADMITTED"]
        if len(admitted) != 1:
            raise AssertionError(f"{name}_DID_NOT_HAVE_UNIQUE_ADMITTED_LANE")
        verified = True
    return {
        "case": name,
        "status": result["status"],
        "selected_algebra": result.get("selected_algebra"),
        "attempts": result["attempts"],
        "selected_certificate_verified": verified,
        "source_fingerprint": result["source_fingerprint"],
    }


def main() -> int:
    cases = [
        check_case("PHP_5_4_UNSAT", pigeonhole(5, 4), "UNSAT", "RELATION_PRODUCT_COUNTING"),
        check_case("PHP_4_5_SAT", pigeonhole(4, 5), "SAT", "RELATION_PRODUCT_COUNTING"),
        check_case("PETERSEN_EVEN_SAT", build_petersen(frozenset({0, 1})), "SAT", "FINITE_AFFINE_CONSERVATION"),
        check_case("PETERSEN_ODD_UNSAT", build_petersen(frozenset({0})), "UNSAT", "FINITE_AFFINE_CONSERVATION"),
        check_case("OUT_OF_PORTFOLIO_NEGATIVE_CONTROL", ((1, 2, 3), (-1, -2)), "OPEN", None),
    ]
    report = {
        "schema": "JANUS/C025/B-TO-A-CROSS-FAMILY-EXACT-ALGEBRA-SELECTOR/v1",
        "status": "PASS",
        "selector_input": "RAW_CNF_ONLY",
        "human_lane_choice": False,
        "heuristic_lane_score": False,
        "portfolio": ["RELATION_PRODUCT_COUNTING", "FINITE_AFFINE_CONSERVATION"],
        "cases": cases,
        "cross_family_result": {
            "same_selector_selected_counting_for_relation_product": True,
            "same_selector_selected_affine_conservation_for_petersen": True,
            "unknown_structure_failed_closed": True
        },
        "scientific_boundary": {
            "what_pass_would_show": "ONE_FAIL_CLOSED_SELECTOR_CAN_CHOOSE_BETWEEN_TWO_DISTINCT_EXACT_ALGEBRAIC_COORDINATE_SYSTEMS_FROM_RAW_CNF_WITHOUT_A_FAMILY_LABEL",
            "what_pass_would_not_show": "AUTONOMOUS_INVENTION_OF_ALL_POSSIBLE_ALGEBRAS_OR_ARBITRARY_CNF_POLYNOMIAL_SOLVABILITY",
            "current_portfolio_is_finite": True,
            "arbitrary_CNF_coverage": "OPEN",
            "P_VS_NP": "OPEN"
        }
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
