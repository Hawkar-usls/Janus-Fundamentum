#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

EXPECTED_IDS = [f"R16-W{i:02d}" for i in range(1, 9)]


def aggregate(input_dir: Path):
    rows = []
    for wid in EXPECTED_IDS:
        path = input_dir / f"JANUS_TRUMP_R16_WORLD_{wid}_RESULT_2026-09-02.json"
        if not path.exists():
            return {
                "schema": "JANUS/TRUMP/R16/PROSPECTIVE_UNSEEN_FACTORED_BRIDGE_HOLDOUT/AGGREGATE_RESULT/v1.0",
                "created_date": "2026-09-02",
                "overall_verdict": "FAIL_INTEGRITY",
                "reason": f"MISSING_WORLD_ARTIFACT:{wid}",
                "worlds": rows,
                "P_VS_NP": "OPEN",
            }
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("world_id") != wid or d.get("P_VS_NP") != "OPEN":
            return {
                "schema": "JANUS/TRUMP/R16/PROSPECTIVE_UNSEEN_FACTORED_BRIDGE_HOLDOUT/AGGREGATE_RESULT/v1.0",
                "created_date": "2026-09-02",
                "overall_verdict": "FAIL_INTEGRITY",
                "reason": f"WORLD_ID_OR_STATUS_DRIFT:{wid}",
                "worlds": rows,
                "P_VS_NP": "OPEN",
            }
        c = d.get("candidate", {})
        comp = d.get("comparison", {})
        rows.append({
            "id": wid,
            "suite": d["source"]["suite"],
            "n": d["source"]["n"],
            "m": d["source"]["m"],
            "bridge_variables": d["source"]["bridge_variable_count"],
            "frame_sha256": d["source"]["frame_sha256"],
            "verdict": d["verdict"],
            "candidate_status": c.get("status"),
            "candidate_elapsed_seconds": c.get("elapsed_seconds"),
            "active_clauses": c.get("active_clauses"),
            "auxiliary_variables": c.get("auxiliary_variables"),
            "shared_pair_atoms": c.get("shared_pair_atoms"),
            "atom_reuse_hits": c.get("atom_reuse_hits"),
            "pair_attempts": c.get("pair_attempts"),
            "max_clause_width": c.get("max_clause_width"),
            "original_allowed": comp.get("original_allowed_count"),
            "candidate_allowed": comp.get("candidate_allowed_count"),
            "false_positive": comp.get("false_positive_count"),
            "false_negative": comp.get("false_negative_count"),
            "original_truth_table_sha256": comp.get("original_truth_table_sha256"),
            "candidate_truth_table_sha256": comp.get("candidate_truth_table_sha256"),
        })

    counts = Counter(r["verdict"] for r in rows)
    if counts["FAIL_INTEGRITY"]:
        overall = "FAIL_INTEGRITY"
    elif counts["MISMATCH_UNSEEN"]:
        overall = "R16_UNSEEN_SEMANTIC_MISMATCH"
    elif counts["OPEN_CANDIDATE_RESOURCE_LIMIT"]:
        overall = "R16_OPEN_CANDIDATE_RESOURCE_LIMIT"
    elif counts["OPEN_VERIFIER_RESOURCE_LIMIT"]:
        overall = "R16_OPEN_VERIFIER_RESOURCE_LIMIT"
    elif counts["PASS_EXACT_UNSEEN"] == 8:
        overall = "R16_PASS_EXACT_UNSEEN_8_OF_8"
    else:
        overall = "FAIL_INTEGRITY"

    completed = [r for r in rows if r["candidate_status"] in ("COMPLETE_EXTENDED_INTERFACE", "COMPLETE_UNSAT_INTERFACE")]
    scaling = {
        "n_values": sorted({r["n"] for r in rows}),
        "candidate_terminal_worlds": len(completed),
        "max_candidate_elapsed_seconds": max((r["candidate_elapsed_seconds"] or 0 for r in completed), default=None),
        "max_active_clauses": max((r["active_clauses"] or 0 for r in completed), default=None),
        "max_auxiliary_variables": max((r["auxiliary_variables"] or 0 for r in completed), default=None),
        "max_pair_attempts": max((r["pair_attempts"] or 0 for r in completed), default=None),
        "interpretation": "Descriptive finite ladder only. No asymptotic polynomial fit or theorem is admitted from four n values and eight instances."
    }
    next_gate = {
        "R16_PASS_EXACT_UNSEEN_8_OF_8": "R17_FROZEN_SCALING_AND_ADVERSARIAL_GENERALIZATION",
        "R16_UNSEEN_SEMANTIC_MISMATCH": "R17_MISMATCH_FORENSICS__FREEZE_COUNTEREXAMPLE",
        "R16_OPEN_CANDIDATE_RESOURCE_LIMIT": "R17_RESOURCE_GROWTH_FORENSICS__NO_LOGIC_TUNING_IN_R16",
        "R16_OPEN_VERIFIER_RESOURCE_LIMIT": "R17_VERIFIER_RECOVERY_ONLY",
        "FAIL_INTEGRITY": "STOP_AND_REPAIR_INTEGRITY_BEFORE_SCIENTIFIC_INTERPRETATION",
    }[overall]
    return {
        "schema": "JANUS/TRUMP/R16/PROSPECTIVE_UNSEEN_FACTORED_BRIDGE_HOLDOUT/AGGREGATE_RESULT/v1.0",
        "created_date": "2026-09-02",
        "overall_verdict": overall,
        "verdict_counts": dict(sorted(counts.items())),
        "world_count": len(rows),
        "worlds": rows,
        "scaling_observation": scaling,
        "scientific_interpretation": "R16 is the first prospective holdout for the frozen shared-extension candidate after exposed W05 semantic calibration. A pass is scoped evidence; any mismatch is a preserved counterexample; any resource OPEN is not negative evidence.",
        "next_gate": next_gate,
        "claim_ceiling": "No arbitrary-CNF totality, global polynomial runtime, SAT-in-P, P=NP, or P!=NP conclusion follows from this finite holdout.",
        "seal": "CAPTAIN_OBVIOUS_SAYS__THE_SCORE_COUNTS_ONLY_AFTER_THE_EXAM_WAS_FROZEN",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--input-dir", required=True); ap.add_argument("--output", required=True); args = ap.parse_args()
    out = aggregate(Path(args.input_dir))
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"overall_verdict": out["overall_verdict"], "verdict_counts": out.get("verdict_counts"), "scaling": out.get("scaling_observation"), "P_VS_NP": "OPEN"}, indent=2, sort_keys=True))
    return 2 if out["overall_verdict"] == "FAIL_INTEGRITY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
