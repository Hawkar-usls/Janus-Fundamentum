#!/usr/bin/env python3
"""Aggregate sharded ORIGINAL-v2 receipts for the frozen C025 L1 candidate.

A rescue in any exact shard is a complete positive existential witness that v2
rescues this candidate.  A full NO_RESCUE conclusion requires every canonical
pair index exactly covered by complete shard receipts. Missing/failed scope is
UNKNOWN, never NO_RESCUE.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

P_VS_NP = "OPEN"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True)
    ap.add_argument("--expected-shards", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    files = sorted(Path(args.input_dir).rglob("shard-*.json"))
    receipts = []
    parse_errors = []
    for p in files:
        try:
            receipts.append(json.loads(p.read_text()))
        except Exception as exc:
            parse_errors.append({"file": str(p), "error": f"{type(exc).__name__}: {exc}"})

    by_index = {}
    for r in receipts:
        s = r.get("shard", {})
        idx = s.get("index")
        cnt = s.get("count")
        if not isinstance(idx, int) or cnt != args.expected_shards:
            continue
        by_index[idx] = r

    candidate_fps = {
        (r.get("frozen_candidate", {}).get("source_fingerprint"),
         r.get("frozen_candidate", {}).get("product_fingerprint"))
        for r in by_index.values()
    }
    candidate_consistent = len(candidate_fps) <= 1
    if not candidate_consistent:
        raise AssertionError("SHARD_CANDIDATE_FINGERPRINT_DRIFT")

    rescues = [r for r in by_index.values() if r.get("rescue") is not None]
    rescues.sort(key=lambda r: int(r["rescue"]["pair_index_zero_based"]))

    present = sorted(by_index)
    missing = [i for i in range(args.expected_shards) if i not in by_index]
    candidate_count_values = {
        int(r["v2_scope"]["candidate_count_global"])
        for r in by_index.values()
        if "v2_scope" in r and "candidate_count_global" in r["v2_scope"]
    }
    candidate_count = next(iter(candidate_count_values)) if len(candidate_count_values) == 1 else None

    covered = set()
    complete_shards = []
    incomplete_shards = []
    for idx, r in sorted(by_index.items()):
        scope = r.get("v2_scope", {})
        if scope.get("complete_for_selected_indices") is True:
            complete_shards.append(idx)
            covered.update(int(x) for x in scope.get("selected_indices", []))
        elif r.get("rescue") is None:
            incomplete_shards.append(idx)

    exact_full_coverage = bool(
        not rescues
        and not missing
        and not parse_errors
        and candidate_count is not None
        and set(range(candidate_count)) == covered
        and len(complete_shards) == args.expected_shards
        and not incomplete_shards
    )

    if rescues:
        winner = rescues[0]
        status = "EXACT_ORIGINAL_V2_RESCUE_FOUND__L1_SURVIVES_THIS_WITNESS"
        l1 = "SURVIVES_THIS_FROZEN_WITNESS__NOT_PROVED"
        next_gate = "FREEZE_FIRST_EXACT_RESCUE_AND_ATTACK_ITS_CONFLICT_COLLISION_MECHANISM"
    elif exact_full_coverage:
        winner = None
        status = "L1_ROOT_GRAMMAR_COUNTEREXAMPLE_FOUND"
        l1 = "REFUTED_BY_REACHABLE_ALL_ORDINARY_OVERFLOW_FULL_V2_NO_RESCUE_WITNESS"
        next_gate = "FREEZE_L1_COUNTEREXAMPLE_AND_DESIGN_STRICT_SUCCESSOR_GRAMMAR"
    else:
        winner = None
        status = "UNKNOWN_INCOMPLETE_SHARDED_SCOPE"
        l1 = "OPEN__NO_FULL_SCOPE_VERDICT"
        next_gate = "COMPLETE_MISSING_OR_INCOMPLETE_SHARDS"

    candidate = None
    if by_index:
        candidate = next(iter(by_index.values())).get("frozen_candidate")

    report = {
        "schema": "JANUS/C025/L1-SHARDED-ORIGINAL-V2-KILL-GATE/AGGREGATE/v1",
        "status": status,
        "frozen_candidate": candidate,
        "shard_accounting": {
            "expected": args.expected_shards,
            "present": present,
            "missing": missing,
            "complete_no_rescue_shards": complete_shards,
            "incomplete_no_rescue_shards": incomplete_shards,
            "parse_errors": parse_errors,
        },
        "scope_accounting": {
            "candidate_count_global": candidate_count,
            "covered_candidate_indices_count": len(covered),
            "exact_full_coverage": exact_full_coverage,
        },
        "first_exact_rescue": winner.get("rescue") if winner else None,
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": l1,
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_PREVIOUSLY",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_PREVIOUSLY",
            "L1C_POLARITY_DRAINAGE_TOTALITY": "REFUTED_BY_M80_EXACT_BOUND_NEGATIVE_CERTIFICATE",
        },
        "next_gate": next_gate,
        "scientific_boundary": {
            "candidate_parameters_frozen_before_this_scan": True,
            "every_present_shard_uses_original_v2_apply_verify_and_original_elimination": True,
            "any_exact_rescue_suffices_to_show_this_witness_does_not_refute_L1": True,
            "no_rescue_requires_complete_canonical_pair_scope": True,
            "missing_scope_maps_to_UNKNOWN": True,
            "finite_counterexample_can_refute_L1_candidate_only": True,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
