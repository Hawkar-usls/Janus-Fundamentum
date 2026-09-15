#!/usr/bin/env python3
"""JANUS B->A exact algebra selector.

One RAW CNF enters.  The selector does not receive a family label and does not
ask a human which algebraic lane to use.

Current exact grammar portfolio:
  1. relation-product counting coordinates;
  2. finite-affine conservation coordinates.

Each lane must independently replay/verify its source semantics.  The selector
admits a decision only when exactly one lane recognizes the CNF.  Zero exact
lanes => OPEN/NOT_RECOGNIZED.  Multiple exact lanes => OPEN/AMBIGUOUS even when
they agree, because choosing between exact coordinate systems by a cosmetic or
heuristic score would violate the B->A epistemic firewall.

This is a finite portfolio of exact recognizers, not a universal algebra
inventor and not an arbitrary-CNF polynomial SAT algorithm.  P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_reverse_b_to_a_relation_product_counting_law as counting
from experiments.direct import janus_b_to_a_finite_affine_synthesizer as affine


def _try_counting(raw_clauses):
    try:
        certificate = counting.infer_relation_product(raw_clauses)
        if not counting.verify_relation_product_certificate(raw_clauses, certificate):
            return {"lane": "RELATION_PRODUCT_COUNTING", "status": "REJECT", "reason": "INDEPENDENT_VERIFIER_FAILED"}
        return {
            "lane": "RELATION_PRODUCT_COUNTING",
            "status": "ADMITTED",
            "decision": certificate["decision"],
            "certificate": certificate,
        }
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        return {"lane": "RELATION_PRODUCT_COUNTING", "status": "REJECT", "reason": str(error)}


def _try_affine(raw_clauses):
    try:
        certificate = affine.synthesize(raw_clauses)
        if certificate.get("decision") not in {"SAT", "UNSAT"}:
            return {
                "lane": "FINITE_AFFINE_CONSERVATION",
                "status": "REJECT",
                "reason": certificate.get("reason", "AFFINE_DECISION_NOT_CLOSED"),
            }
        if not affine.verify_certificate(raw_clauses, certificate):
            return {"lane": "FINITE_AFFINE_CONSERVATION", "status": "REJECT", "reason": "INDEPENDENT_VERIFIER_FAILED"}
        return {
            "lane": "FINITE_AFFINE_CONSERVATION",
            "status": "ADMITTED",
            "decision": certificate["decision"],
            "certificate": certificate,
        }
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        return {"lane": "FINITE_AFFINE_CONSERVATION", "status": "REJECT", "reason": str(error)}


def select_exact_algebra(raw_clauses) -> dict:
    cnf = base.canon_cnf(raw_clauses)
    attempts = [_try_counting(cnf), _try_affine(cnf)]
    admitted = [attempt for attempt in attempts if attempt["status"] == "ADMITTED"]

    public_attempts = [
        {key: value for key, value in attempt.items() if key != "certificate"}
        for attempt in attempts
    ]
    if not admitted:
        return {
            "kind": "JANUS_EXACT_ALGEBRA_SELECTOR_RESULT",
            "source_fingerprint": base.fingerprint(cnf),
            "status": "OPEN",
            "reason": "NO_EXACT_ALGEBRA_IN_CURRENT_PORTFOLIO",
            "attempts": public_attempts,
            "P_VS_NP": "OPEN",
        }
    if len(admitted) != 1:
        return {
            "kind": "JANUS_EXACT_ALGEBRA_SELECTOR_RESULT",
            "source_fingerprint": base.fingerprint(cnf),
            "status": "OPEN",
            "reason": "AMBIGUOUS_MULTIPLE_EXACT_ALGEBRAS_FAIL_CLOSED",
            "attempts": public_attempts,
            "admitted_lanes": [attempt["lane"] for attempt in admitted],
            "P_VS_NP": "OPEN",
        }

    winner = admitted[0]
    return {
        "kind": "JANUS_EXACT_ALGEBRA_SELECTOR_RESULT",
        "source_fingerprint": base.fingerprint(cnf),
        "status": winner["decision"],
        "selected_algebra": winner["lane"],
        "attempts": public_attempts,
        "certificate": winner["certificate"],
        "selection_rule": "EXACTLY_ONE_INDEPENDENTLY_VERIFIED_LANE_OR_FAIL_CLOSED",
        "human_family_label_required": False,
        "heuristic_score_used": False,
        "P_VS_NP": "OPEN",
    }


def verify_selector_result(raw_clauses, result: dict) -> bool:
    """Verify the selected certificate without re-running portfolio selection."""
    try:
        cnf = base.canon_cnf(raw_clauses)
        if result.get("kind") != "JANUS_EXACT_ALGEBRA_SELECTOR_RESULT":
            return False
        if result.get("source_fingerprint") != base.fingerprint(cnf):
            return False
        if result.get("status") not in {"SAT", "UNSAT"}:
            return False
        lane = result.get("selected_algebra")
        certificate = result.get("certificate")
        if lane == "RELATION_PRODUCT_COUNTING":
            return counting.verify_relation_product_certificate(cnf, certificate)
        if lane == "FINITE_AFFINE_CONSERVATION":
            return affine.verify_certificate(cnf, certificate)
        return False
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def main() -> int:
    # This file intentionally has no embedded family examples.  Cross-family
    # tests live in a separate harness so family labels never enter selection.
    print(json.dumps({
        "schema": "JANUS/C025/B-TO-A-EXACT-ALGEBRA-SELECTOR/v1",
        "portfolio": ["RELATION_PRODUCT_COUNTING", "FINITE_AFFINE_CONSERVATION"],
        "selection": "EXACTLY_ONE_ADMITTED_OR_OPEN",
        "arbitrary_CNF_coverage": "OPEN",
        "P_VS_NP": "OPEN"
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
