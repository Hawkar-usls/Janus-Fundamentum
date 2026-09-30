#!/usr/bin/env python3
"""Mixed-algebra instance-specific escape gate.

Construct one RAW CNF as a disjoint conjunction of two components whose exact
coordinate systems are different. The global algebra selector must return
OPEN, while the generic component escape is allowed to discover and verify a
separate exact algebra for each component.

Family names live only in this test harness; the escape producer receives raw
clauses.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_b_to_a_exact_algebra_selector as selector
from experiments.direct import janus_instance_specific_algebraic_escape as escape
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct.janus_tseitin_b_to_a_petersen_holdout import build_formula as build_petersen


def shift_cnf(cnf, offset: int):
    rows = []
    for clause in cnf:
        rows.append(
            tuple(
                (abs(literal) + offset) if literal > 0 else -(abs(literal) + offset)
                for literal in clause
            )
        )
    return base.canon_cnf(rows)


def combine(left, right):
    return base.canon_cnf(tuple(left) + tuple(right))


def inspect(label: str, raw, expected: str) -> dict:
    global_result = selector.select_exact_algebra(raw)
    if global_result.get("status") != "OPEN":
        raise AssertionError(
            f"{label}_GLOBAL_SELECTOR_SHOULD_BE_OPEN:{global_result.get('status')}"
        )

    result = escape.solve_by_component_escape(raw)
    if result.get("status") != expected:
        raise AssertionError(f"{label}_ESCAPE_STATUS:{result.get('status')}!={expected}")
    if result.get("mode") != "EXACT_COMPONENT_DIRECT_SUM":
        raise AssertionError(f"{label}_NOT_DIRECT_SUM:{result.get('mode')}")
    if not escape.verify_escape_result(raw, result):
        raise AssertionError(f"{label}_ESCAPE_CERTIFICATE_VERIFIER_FAILED")
    if result["ledger"]["component_count"] != 2:
        raise AssertionError(f"{label}_COMPONENT_COUNT_DRIFT")

    algebras = {
        record.get("selected_algebra")
        for record in result["components"]
        if record.get("selected_algebra") is not None
    }
    expected_algebras = {
        "RELATION_PRODUCT_COUNTING",
        "FINITE_AFFINE_CONSERVATION",
    }
    if algebras != expected_algebras:
        raise AssertionError(f"{label}_MIXED_ALGEBRAS_NOT_RECOVERED:{algebras}")

    return {
        "label": label,
        "global_selector_status": global_result.get("status"),
        "escape_status": result["status"],
        "escape_mode": result["mode"],
        "component_count": result["ledger"]["component_count"],
        "selected_algebras": sorted(algebras),
        "selector_calls": result["ledger"]["selector_calls"],
        "certificate_bytes": result["ledger"]["certificate_bytes"],
        "verification_work": result["ledger"]["verification_work"],
        "source_fingerprint": result["source_fingerprint"],
        "independent_escape_verifier": True,
    }


def main() -> int:
    affine_sat = build_petersen(frozenset({0, 1}))
    offset = max(base.vars_of(affine_sat)) + 100

    counting_sat = shift_cnf(pigeonhole(3, 4), offset)
    counting_unsat = shift_cnf(pigeonhole(5, 4), offset)

    sat_raw = combine(affine_sat, counting_sat)
    unsat_raw = combine(affine_sat, counting_unsat)

    sat = inspect("MIXED_SAT", sat_raw, "SAT")
    unsat = inspect("MIXED_UNSAT", unsat_raw, "UNSAT")

    report = {
        "schema": "JANUS/C025/INSTANCE-SPECIFIC-MIXED-ALGEBRA-ESCAPE/v1",
        "status": "PASS",
        "producer_received": "RAW_CNF_ONLY",
        "global_exact_algebra": "OPEN_ON_BOTH_CONTROLS",
        "escape": "EXACT_COMPONENT_DIRECT_SUM",
        "sat": sat,
        "unsat": unsat,
        "what_pass_shows": (
            "ONE_INSTANCE_CAN_BE_EXACTLY_DECOMPOSED_INTO_COMPONENTS_THAT_REQUIRE_"
            "DIFFERENT_VERIFIED_COORDINATE_SYSTEMS_WHEN_NO_SINGLE_GLOBAL_LANE_APPLIES"
        ),
        "what_pass_does_not_show": (
            "CONNECTED_INSTANCE_ESCAPE_OR_UNIVERSAL_TOTALITY_OR_P_VS_NP"
        ),
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
