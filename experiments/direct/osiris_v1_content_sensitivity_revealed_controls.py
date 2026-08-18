#!/usr/bin/env python3
"""Frozen revealed-control content-sensitivity diagnostic for OSIRIS v1.0.

This does NOT test whether Pyramid Texts encode an algorithm. It asks a narrower
software question: does the current 31-stage linker inspect CNF content beyond an
externally supplied initial_anchor, or are stage decisions content-invariant?
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from janus_full_text_missing_link_assembly import FORWARD, BACK, link_forward, link_back
from janus_c025_families import equality_family
from toroidal_tseitin_twins import charge_patterns, build_formula
from connected_toroidal_tseitin_twins import add_neutral_bridge

EXPECTED_OSIRIS_RESULT_SHA = "0e03c64e38919b2022642786825fc43d52f60ac8d4acf36aa9150c0fa21989fa"
STATUS_LIMIT = "DIAGNOSTIC_PASS_OSIRIS_V1_INPUT_ANCHOR_ONLY_CONTENT_GENERALIZATION_NOT_ESTABLISHED"


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()


def cnf_payload(cnf: Any) -> dict[str, Any]:
    if hasattr(cnf, "clauses") and hasattr(cnf, "variable_count"):
        return {"variable_count": int(cnf.variable_count), "clauses": [list(c) for c in cnf.clauses]}
    return {"clauses": [list(c) for c in cnf]}


def run_chain(anchor: str) -> dict[str, Any]:
    fwd = link_forward(anchor)
    back = link_back(fwd)
    behavior = [
        {
            "stage": e.stage,
            "operator": e.operator,
            "requires": list(e.requires),
            "produces": list(e.produces),
        }
        for e in fwd
    ]
    return {
        "forward_order": [e.stage for e in fwd],
        "back_order": [e.stage for e in back],
        "forward_terminal_commitment": fwd[-1].commitment,
        "back_terminal_commitment": back[-1].commitment,
        "behavior_vector": behavior,
        "forward_envelopes": [asdict(e) for e in fwd],
        "back_envelopes": [asdict(e) for e in back],
    }


def controls() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for radius in (0, 1, 2):
        sat_charges, unsat_charges = charge_patterns(radius)
        for truth, charges in (("SAT", sat_charges), ("UNSAT", unsat_charges)):
            cnf, ids = build_formula(radius, charges)
            rows.append({
                "family": "TOROIDAL_TSEITIN_LOCAL_TWINS",
                "radius": radius,
                "truth": truth,
                "cnf": cnf,
            })
            connected, *_ = add_neutral_bridge(cnf, ids, radius)
            rows.append({
                "family": "CONNECTED_TOROIDAL_TSEITIN_TWINS",
                "radius": radius,
                "truth": truth,
                "cnf": connected,
            })
    eq, _, _ = equality_family(14)
    rows.append({"family": "EQUALITY_BASELINE", "radius": None, "truth": "SAT", "cnf": eq})
    return rows


def run() -> dict[str, Any]:
    results = []
    for row in controls():
        payload = cnf_payload(row["cnf"])
        anchor = digest(payload)
        chain = run_chain(anchor)
        results.append({
            "family": row["family"],
            "radius": row["radius"],
            "truth": row["truth"],
            "input_anchor": anchor,
            "variables": payload.get("variable_count"),
            "clauses": len(payload["clauses"]),
            "behavior_sha256": digest(chain["behavior_vector"]),
            "forward_terminal_commitment": chain["forward_terminal_commitment"],
            "back_terminal_commitment": chain["back_terminal_commitment"],
            "forward_order_exact": chain["forward_order"] == FORWARD,
            "back_order_exact": chain["back_order"] == BACK,
        })

    behavior_hashes = {r["behavior_sha256"] for r in results}
    anchors = {r["input_anchor"] for r in results}
    forward_terms = {r["forward_terminal_commitment"] for r in results}

    twin_pairs = []
    for family in ("TOROIDAL_TSEITIN_LOCAL_TWINS", "CONNECTED_TOROIDAL_TSEITIN_TWINS"):
        for radius in (0, 1, 2):
            sat = next(r for r in results if r["family"] == family and r["radius"] == radius and r["truth"] == "SAT")
            unsat = next(r for r in results if r["family"] == family and r["radius"] == radius and r["truth"] == "UNSAT")
            twin_pairs.append({
                "family": family,
                "radius": radius,
                "anchors_differ": sat["input_anchor"] != unsat["input_anchor"],
                "behavior_identical": sat["behavior_sha256"] == unsat["behavior_sha256"],
                "terminal_commitments_differ": sat["forward_terminal_commitment"] != unsat["forward_terminal_commitment"],
            })

    forced_anchor = "FORCED-SAME-ANCHOR-CONTENT-SENSITIVITY-CONTROL"
    a = run_chain(forced_anchor)
    b = run_chain(forced_anchor)
    forced_same_anchor_exact_chain_equality = digest(a) == digest(b)

    all_orders = all(r["forward_order_exact"] and r["back_order_exact"] for r in results)
    behavior_invariant = len(behavior_hashes) == 1
    commitments_anchor_sensitive = len(forward_terms) == len(results) and len(anchors) == len(results)
    twins_semantically_indistinguishable_to_stage_logic = all(p["behavior_identical"] for p in twin_pairs)
    no_semantic_verdict_emitted = True

    gates = {
        "all_revealed_controls_executed": len(results) == 13,
        "forward_back_orders_exact": all_orders,
        "behavior_vector_invariant_across_all_inputs": behavior_invariant,
        "terminal_commitments_change_with_distinct_input_anchor": commitments_anchor_sensitive,
        "sat_unsat_twins_have_identical_stage_behavior": twins_semantically_indistinguishable_to_stage_logic,
        "forced_same_anchor_exact_chain_equality": forced_same_anchor_exact_chain_equality,
        "no_unauthorized_sat_unsat_verdict": no_semantic_verdict_emitted,
        "P_VS_NP_OPEN": True,
    }
    status = STATUS_LIMIT if all(gates.values()) else "CONTENT_SENSITIVITY_DETECTED_OR_DIAGNOSTIC_DRIFT_REQUIRES_AUDIT"
    result = {
        "artifact_id": "OSIRIS-V1-CONTENT-SENSITIVITY-REVEALED-CONTROLS-2026-08-18-v1",
        "status": status,
        "scope": "REVEALED_CONTROLS_ONLY_NO_UNTOUCHED_HOLDOUT",
        "controls": results,
        "twin_pairs": twin_pairs,
        "summary": {
            "controls_total": len(results),
            "distinct_input_anchors": len(anchors),
            "distinct_behavior_vectors": len(behavior_hashes),
            "distinct_forward_terminal_commitments": len(forward_terms),
            "content_channel_observed": "INITIAL_ANCHOR_ONLY",
            "semantic_sat_unsat_discrimination": False,
            "solver_promotion": False,
        },
        "gates": gates,
        "interpretation": [
            "OSIRIS v1 preserves compositional/provenance integrity across these revealed inputs.",
            "Its current 31-stage linker does not inspect CNF structure beyond the externally supplied initial anchor.",
            "SAT and UNSAT Tseitin twins therefore receive the same stage-decision behavior.",
            "Different CNFs alter commitments via their anchors, but do not alter stage decisions.",
            "Content-generalization and solver advantage are NOT established by this version.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {"P_EQUALS_NP": "NOT_ESTABLISHED", "P_NOT_EQUALS_NP": "NOT_ESTABLISHED", "P_VS_NP": "OPEN"},
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = run()
    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
