#!/usr/bin/env python3
"""Execute the frozen PHP_8_7 holdout against the unchanged relation-product law.

Temporal ordering is part of the evidence:
  law source commit: 336c03343c783ddb8450fd39f1807382b667d9c4
  frozen prediction commit: 1f6701c25382acf163ffdc6da736ab308b820f48
  this holdout harness was created only after both commits existed.

Any mismatch is a FAIL.  This harness may not repair the law and reclassify the
same observation as a pass.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct import janus_reverse_b_to_a_relation_product_counting_law as law

LAW_SOURCE_COMMIT = "336c03343c783ddb8450fd39f1807382b667d9c4"
PREDICTION_COMMIT = "1f6701c25382acf163ffdc6da736ab308b820f48"

FROZEN = {
    "p": 8,
    "h": 7,
    "w": 7,
    "k": 8,
    "q": 7,
    "template_count": 3,
    "template_program": ["ROW_ALO", "ROW_AMO", "COLUMN_AMO"],
    "row_adjacent_generator_count": 7,
    "column_adjacent_generator_count": 6,
    "raw_variable_count": 56,
    "raw_clause_count": 372,
    "raw_state_units": 1157,
    "input_size_units_N": 1213,
    "row_histogram_count_if_materialized": 3003,
    "decision": "UNSAT",
}


def main() -> None:
    raw = pigeonhole(8, 7)
    cnf = base.canon_cnf(raw)
    cert = law.infer_relation_product(raw)
    independent_ok = law.verify_relation_product_certificate(raw, cert)
    if not independent_ok:
        raise AssertionError("HOLDOUT_INDEPENDENT_CERTIFICATE_VERIFIER_FAILED")

    observed = {
        "p": cert["p"],
        "h": cert["h"],
        "w": cert["w"],
        "k": cert["k"],
        "q": cert["q"],
        "template_count": cert["template_count"],
        "template_program": cert["template_program"],
        "row_adjacent_generator_count": len(cert["symmetry_group_generators"]["row_generators"]),
        "column_adjacent_generator_count": len(cert["symmetry_group_generators"]["column_generators"]),
        "raw_variable_count": len(base.vars_of(cnf)),
        "raw_clause_count": len(cnf),
        "raw_state_units": base.state_units(cnf),
        "input_size_units_N": base.input_size_units(cnf),
        "row_histogram_count_if_materialized": cert["row_histogram_count_if_materialized"],
        "decision": cert["decision"],
    }

    mismatches = {
        key: {"predicted": FROZEN[key], "observed": observed[key]}
        for key in FROZEN
        if observed[key] != FROZEN[key]
    }
    if mismatches:
        raise AssertionError("FROZEN_HOLDOUT_PREDICTION_FAILED=" + json.dumps(mismatches, sort_keys=True))

    expected_breakdown = {
        "ROW_ALO": 8,
        "ROW_AMO": 168,
        "COLUMN_AMO": 196,
    }
    if sum(expected_breakdown.values()) != len(cnf):
        raise AssertionError("FROZEN_CLAUSE_BREAKDOWN_FAILED")

    if not all(x["preserves_cnf"] for x in cert["symmetry_group_generators"]["row_generators"]):
        raise AssertionError("ROW_SYMMETRY_HOLDOUT_FAILED")
    if not all(x["preserves_cnf"] for x in cert["symmetry_group_generators"]["column_generators"]):
        raise AssertionError("COLUMN_SYMMETRY_HOLDOUT_FAILED")
    if not cert["exact_clause_replay"]:
        raise AssertionError("EXACT_CLAUSE_REPLAY_HOLDOUT_FAILED")
    if cert["counting_invariant"]["observed_relation"] != "p > h":
        raise AssertionError("COUNTING_INVARIANT_HOLDOUT_FAILED")

    report = {
        "schema": "JANUS/C025/PHP8-7-RELATION-PRODUCT-HOLDOUT/v1",
        "status": "PASS_FROZEN_PREDICTION",
        "P_VS_NP": "OPEN",
        "temporal_precommit": {
            "law_source_commit": LAW_SOURCE_COMMIT,
            "frozen_prediction_commit": PREDICTION_COMMIT,
            "holdout_harness_created_after_prediction": True,
        },
        "holdout": "PHP_8_7_STANDARD_PAIRWISE_CNF",
        "frozen_prediction": FROZEN,
        "observed": observed,
        "mismatches": mismatches,
        "source_fingerprint_observed_only_after_prediction_freeze": cert["source_fingerprint"],
        "raw_clause_breakdown": expected_breakdown,
        "exact_clause_replay": cert["exact_clause_replay"],
        "independent_certificate_verifier": independent_ok,
        "symmetry": {
            "row_group": "S_8",
            "column_group": "S_7",
            "row_adjacent_generators_pass": 7,
            "column_adjacent_generators_pass": 6,
        },
        "decision": {
            "result": cert["decision"],
            "required_row_selections": 8,
            "capacity_one_columns": 7,
            "reason": "8_GREATER_THAN_7_COUNTING_CONTRADICTION",
            "assignment_enumeration_used": False,
            "histogram_enumeration_used": False,
        },
        "scientific_boundary": {
            "what_passed": "PREDECLARED_PARAMETRIC_LAW_ON_ONE_UNSEEN_STANDARD_PHP_INSTANCE",
            "recognized_class": "EXACT_RELATION_PRODUCT_CNF",
            "arbitrary_CNF_coverage": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
