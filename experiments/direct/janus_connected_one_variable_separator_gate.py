#!/usr/bin/env python3
"""Connected one-variable separator escape gate.

Build a connected SAT/UNSAT pair by joining two previously exact but different
components through one fresh forced-true connector variable. The connector
clauses are satisfiability-neutral: for any endpoint values they are satisfied
when connector=1.

The global exact selector and plain component decomposition must both remain
OPEN because the raw primal graph is connected. The one-variable escape must
find a closing variable without being told which one.
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
from experiments.direct import janus_instance_specific_algebraic_escape as component_escape
from experiments.direct import janus_one_variable_separator_escape as separator_escape
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct.janus_tseitin_b_to_a_petersen_holdout import build_formula as build_petersen


def shift_cnf(cnf, offset: int):
    return base.canon_cnf(
        tuple(
            (abs(literal) + offset) if literal > 0 else -(abs(literal) + offset)
            for literal in clause
        )
        for clause in cnf
    )


def neutral_connect(left, right):
    left = base.canon_cnf(left)
    right = base.canon_cnf(right)
    all_vars = set(base.vars_of(left)) | set(base.vars_of(right))
    if not all_vars:
        raise AssertionError("EMPTY_CONNECT_INPUT")
    left_endpoint = min(base.vars_of(left))
    right_endpoint = min(base.vars_of(right))
    connector = max(all_vars) + 1
    bridge = (
        (left_endpoint, connector),
        (-left_endpoint, connector),
        (right_endpoint, connector),
        (-right_endpoint, connector),
    )
    raw = base.canon_cnf(tuple(left) + tuple(right) + bridge)
    return raw, connector


def inspect(label: str, raw, expected: str) -> dict:
    if len(component_escape.component_cnf_partition(raw)) != 1:
        raise AssertionError(f"{label}_RAW_NOT_CONNECTED")

    global_result = selector.select_exact_algebra(raw)
    if global_result.get("status") != "OPEN":
        raise AssertionError(f"{label}_GLOBAL_SELECTOR_NOT_OPEN")

    component_result = component_escape.solve_by_component_escape(raw)
    if component_result.get("status") != "OPEN":
        raise AssertionError(f"{label}_PLAIN_COMPONENT_ESCAPE_NOT_OPEN")
    if component_result.get("mode") != "CONNECTED_NO_CURRENT_ESCAPE":
        raise AssertionError(f"{label}_PLAIN_COMPONENT_MODE_DRIFT")

    result = separator_escape.solve_one_variable_escape(raw)
    if result.get("status") != expected:
        raise AssertionError(f"{label}_SEPARATOR_STATUS:{result.get('status')}!={expected}")
    if result.get("mode") != "ONE_VARIABLE_EXACT_SHANNON_ESCAPE":
        raise AssertionError(f"{label}_SEPARATOR_MODE:{result.get('mode')}")
    if result.get("selected_variable") is None:
        raise AssertionError(f"{label}_NO_SELECTED_VARIABLE")
    if not separator_escape.verify_one_variable_escape(raw, result):
        raise AssertionError(f"{label}_SEPARATOR_CERTIFICATE_VERIFIER_FAILED")
    if result["ledger"]["branch_attempts"] > 2 * len(base.vars_of(raw)):
        raise AssertionError(f"{label}_BRANCH_WORK_BOUND_DRIFT")
    return {
        "label": label,
        "status": result["status"],
        "mode": result["mode"],
        "selected_variable": result["selected_variable"],
        "variables_considered": result["ledger"]["variables_considered"],
        "branch_attempts": result["ledger"]["branch_attempts"],
        "unit_propagation_work": result["ledger"]["unit_propagation_work"],
        "certificate_bytes": result["ledger"]["certificate_bytes"],
        "source_fingerprint": result["source_fingerprint"],
        "independent_verifier": True,
    }


def main() -> int:
    affine_sat = build_petersen(frozenset({0, 1}))
    offset = max(base.vars_of(affine_sat)) + 100
    counting_sat = shift_cnf(pigeonhole(3, 4), offset)
    counting_unsat = shift_cnf(pigeonhole(5, 4), offset)

    sat_raw, sat_connector = neutral_connect(affine_sat, counting_sat)
    unsat_raw, unsat_connector = neutral_connect(affine_sat, counting_unsat)

    sat = inspect("CONNECTED_MIXED_SAT", sat_raw, "SAT")
    unsat = inspect("CONNECTED_MIXED_UNSAT", unsat_raw, "UNSAT")

    report = {
        "schema": "JANUS/C025/CONNECTED-ONE-VARIABLE-SEPARATOR-ESCAPE/v1",
        "status": "PASS",
        "producer_received": "RAW_CNF_ONLY",
        "bridge_connector_hints_supplied_to_producer": False,
        "test_only_connector_ids": {
            "sat": sat_connector,
            "unsat": unsat_connector,
        },
        "sat": sat,
        "unsat": unsat,
        "what_pass_shows": (
            "A_CONNECTED_RAW_CNF_OUTSIDE_THE_CURRENT_GLOBAL_AND_COMPONENT_SELECTORS_"
            "CAN_BE_CLOSED_BY_DETERMINISTIC_ONE_VARIABLE_EXACT_SHANNON_ESCAPE"
        ),
        "what_pass_does_not_show": (
            "EVERY_CONNECTED_CNF_HAS_A_ONE_VARIABLE_ESCAPE_OR_RECURSIVE_BACKDOOR_"
            "SIZE_IS_LOGARITHMIC_OR_P_VS_NP"
        ),
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
