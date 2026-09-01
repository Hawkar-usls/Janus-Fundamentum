#!/usr/bin/env python3
"""Execution-order optimization for frozen R7D.

The preregistered proof rules and frozen width k=4 are unchanged.  We first try
exact width-bounded elimination directly; only an OPEN width barrier proceeds to
fixed-width resolution saturation, after which exact width-bounded elimination
is retried.  This changes execution order/cost only, not theorem authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r7d_dense_3sat_polynomial_proof_attack as base


def fast_attack_component(part):
    f = base.canon(part)

    first = base.width_bounded_eliminate(f, base.WIDTH_K)
    ops = first.ops
    if first.status == "UNSAT":
        return {
            "status": "UNSAT",
            "class": "WIDTH4_EXACT_ELIMINATION",
            "assignment": None,
            "ops": ops,
            "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_REFUTATION", "phase": "PRE_SATURATION", "width": base.WIDTH_K, "records": first.records, "final_cnf": [list(c) for c in first.final_cnf]},
        }
    if first.status == "SAT":
        if first.witness is not None and base.r7b.verify_sat(f, first.witness):
            return {
                "status": "SAT",
                "class": "WIDTH4_EXACT_ELIMINATION",
                "assignment": first.witness,
                "ops": ops,
                "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_MODEL", "phase": "PRE_SATURATION", "width": base.WIDTH_K, "records": first.records},
            }
        return {"status": "OPEN", "class": "WIDTH4_RECONSTRUCTION_FAILURE", "assignment": None, "ops": ops, "certificate": {"type": "PRE_SATURATION_MODEL_REPLAY_FAILED"}}

    rr = base.fixed_width_resolution(f, base.WIDTH_K)
    ops += rr.ops
    if rr.status == "UNSAT":
        return {
            "status": "UNSAT",
            "class": "WIDTH4_RESOLUTION_REFUTATION",
            "assignment": None,
            "ops": ops,
            "certificate": {"type": "WIDTH4_RESOLUTION_REFUTATION", "width": base.WIDTH_K, "proof": rr.proof, "derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide, "clause_universe_bound": rr.universe_bound},
        }
    if rr.status != "SATURATION_COMPLETE_NO_REFUTATION":
        return {"status": "OPEN", "class": "WIDTH4_UNSUPPORTED", "assignment": None, "ops": ops, "certificate": {"type": rr.status}}

    second = base.width_bounded_eliminate(rr.saturated, base.WIDTH_K)
    ops += second.ops
    if second.status == "UNSAT":
        return {
            "status": "UNSAT",
            "class": "WIDTH4_EXACT_ELIMINATION",
            "assignment": None,
            "ops": ops,
            "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_REFUTATION", "phase": "POST_SATURATION", "width": base.WIDTH_K, "records": second.records, "final_cnf": [list(c) for c in second.final_cnf]},
        }
    if second.status == "SAT":
        if second.witness is not None and base.r7b.verify_sat(f, second.witness):
            return {
                "status": "SAT",
                "class": "WIDTH4_EXACT_ELIMINATION",
                "assignment": second.witness,
                "ops": ops,
                "certificate": {"type": "WIDTH4_EXACT_ELIMINATION_MODEL", "phase": "POST_SATURATION", "width": base.WIDTH_K, "records": second.records, "saturation_derived_clauses": rr.derived},
            }
        return {"status": "OPEN", "class": "WIDTH4_RECONSTRUCTION_FAILURE", "assignment": None, "ops": ops, "certificate": {"type": "POST_SATURATION_MODEL_REPLAY_FAILED"}}

    return {
        "status": "OPEN",
        "class": "WIDTH4_BARRIER",
        "assignment": None,
        "ops": ops,
        "certificate": {"type": second.status, "width": base.WIDTH_K, "pre_saturation_safe_steps": len(first.records), "post_saturation_safe_steps": len(second.records), "remaining_variables": len(base.variables(second.final_cnf)), "remaining_clauses": len(second.final_cnf), "blocked_pivot_witnesses": second.blocked_pivots[:32], "saturation_derived_clauses": rr.derived, "blocked_wide_resolvents": rr.blocked_wide},
    }


# Monkey-patch only the execution order of the already frozen candidate proof rules.
base.attack_component = fast_attack_component


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = base.run()
    result["execution_order"] = "WIDTH4_EXACT_ELIMINATION -> IF_OPEN WIDTH4_RESOLUTION_SATURATION -> WIDTH4_EXACT_ELIMINATION"
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "summary": result["summary"], "gates": result["gates"], "candidate_source_firewall": result["candidate_source_firewall"], "P_VS_NP": result["P_VS_NP"]}, indent=2))
    return 0 if all(result["gates"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
