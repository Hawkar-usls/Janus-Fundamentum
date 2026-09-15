#!/usr/bin/env python3
"""External family harness for the generic JANUS finite-affine synthesizer.

Important separation rule:
- this file knows the test-family generator;
- janus_b_to_a_finite_affine_synthesizer.py does not.

The old toroidal SAT/UNSAT twins are especially useful because their complete
translation-normalized local signature multisets are equal at the tested
radius.  Therefore a local-pattern shortcut must not distinguish them.  The
new producer must instead recover an exact global algebraic obstruction.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_b_to_a_finite_affine_synthesizer as synth
from experiments.direct.toroidal_tseitin_twins import (
    build_formula,
    charge_patterns,
    formula_assignment,
    formula_satisfied,
    local_signature_multiset,
    torus_size,
)


def run_case(radius: int) -> dict:
    sat_charges, unsat_charges = charge_patterns(radius)
    sat_cnf, sat_ids = build_formula(radius, sat_charges)
    unsat_cnf, unsat_ids = build_formula(radius, unsat_charges)

    # Historical adversarial control: these two instances look identical to the
    # complete radius-local signature multiset used by the earlier test family.
    if local_signature_multiset(radius, sat_charges) != local_signature_multiset(radius, unsat_charges):
        raise AssertionError("LOCAL_TWIN_CONTROL_DRIFT")

    sat_external_witness = formula_assignment(radius, sat_charges, sat_ids)
    if sat_external_witness is None or not formula_satisfied(sat_cnf, sat_external_witness):
        raise AssertionError("EXTERNAL_SAT_CONTROL_FAILED")
    if formula_assignment(radius, unsat_charges, unsat_ids) is not None:
        raise AssertionError("EXTERNAL_UNSAT_CONTROL_FAILED")

    sat_certificate = synth.synthesize(sat_cnf.clauses)
    unsat_certificate = synth.synthesize(unsat_cnf.clauses)
    sat_verified = synth.verify_certificate(sat_cnf.clauses, sat_certificate)
    unsat_verified = synth.verify_certificate(unsat_cnf.clauses, unsat_certificate)
    if not sat_verified or not unsat_verified:
        raise AssertionError("INDEPENDENT_AFFINE_CERTIFICATE_VERIFIER_FAILED")
    if sat_certificate["decision"] != "SAT":
        raise AssertionError("SAT_TWIN_MISCLASSIFIED")
    if unsat_certificate["decision"] != "UNSAT":
        raise AssertionError("UNSAT_TWIN_MISCLASSIFIED")
    if sat_certificate["modulus"] != unsat_certificate["modulus"]:
        raise AssertionError("TWIN_ALGEBRA_CARRIER_MISMATCH")
    if sat_certificate["modulus"] != 2:
        raise AssertionError("TRAINING_DID_NOT_SELECT_EXPECTED_SMALLEST_EXACT_CARRIER")
    if not sat_certificate["incidence"]["all_variables_touch_exactly_two_scopes"]:
        raise AssertionError("SAT_INCIDENCE_NOT_EDGE_LIKE")
    if not unsat_certificate["incidence"]["all_variables_touch_exactly_two_scopes"]:
        raise AssertionError("UNSAT_INCIDENCE_NOT_EDGE_LIKE")

    return {
        "radius": radius,
        "torus_side": torus_size(radius),
        "raw_variables": sat_certificate["resource_ledger"]["raw_variables"],
        "raw_clauses": sat_certificate["resource_ledger"]["raw_clauses"],
        "discovered_scopes": sat_certificate["resource_ledger"]["discovered_scopes"],
        "max_scope_width": sat_certificate["resource_ledger"]["max_observed_scope_width"],
        "local_signature_multisets_equal": True,
        "family_labels_passed_to_synthesizer": False,
        "block_width_passed_to_synthesizer": False,
        "carrier_passed_to_synthesizer": False,
        "selected_modulus": sat_certificate["modulus"],
        "constraint_components": sat_certificate["incidence"]["constraint_component_count"],
        "sat": {
            "decision": sat_certificate["decision"],
            "rank": sat_certificate["global_rank"],
            "independent_verifier": sat_verified,
            "source_fingerprint": sat_certificate["source_fingerprint"],
        },
        "unsat": {
            "decision": unsat_certificate["decision"],
            "rank": unsat_certificate["global_rank"],
            "contradiction_rows": unsat_certificate["contradiction"]["row_count"],
            "independent_verifier": unsat_verified,
            "source_fingerprint": unsat_certificate["source_fingerprint"],
        },
        "resource_ledger": sat_certificate["resource_ledger"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--radii", default="0,1")
    args = parser.parse_args()
    radii = [int(token) for token in args.radii.split(",") if token.strip()]
    records = [run_case(radius) for radius in radii]
    report = {
        "schema": "JANUS/C025/B-TO-A/FINITE-AFFINE-TOROIDAL-TWINS-TRAINING/v1",
        "status": "PASS",
        "direction": "B_TO_A",
        "producer_received": "RAW_CNF_ONLY",
        "producer_exclusions": [
            "NO_FAMILY_NAME",
            "NO_GRAPH_COORDINATES",
            "NO_CHARGE_LABELS",
            "NO_BLOCK_WIDTH",
            "NO_MODULUS_HINT",
            "NO_SAT_ORACLE",
            "NO_LOCAL_PATTERN_PROMOTION"
        ],
        "records": records,
        "observed_meta_law_candidate": {
            "statement": "EXACT_LOCAL_RELATIONS_CAN_SELECT_A_FINITE_AFFINE_CARRIER_AND_GLOBAL_ELIMINATION_CAN_EXPOSE_A_CONSERVATION_OBSTRUCTION",
            "carrier_was_discovered_not_supplied": True,
            "exact_local_clause_replay_required": True,
            "global_certificate_required": True,
            "local_twin_control_prevents_local_pattern_SHORTCUT": True
        },
        "next_gate": "FREEZE_A_TOPOLOGY_AND_ARITY_HOLDOUT_PREDICTION_BEFORE_CREATING_THE_HOLDOUT_GENERATOR",
        "scientific_boundary": {
            "bounded_scope_truth_table_enumeration": True,
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_SAT_algorithm": "OPEN",
            "P_VS_NP": "OPEN"
        }
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
