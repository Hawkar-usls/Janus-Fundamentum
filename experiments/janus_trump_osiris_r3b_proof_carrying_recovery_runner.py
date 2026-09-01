#!/usr/bin/env python3
from __future__ import annotations

from collections import defaultdict
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys

from janus_trump_osiris_r3b_proof_carrying_recovery import (
    R3B_MIN_FAMILIES,
    R3B_MIN_RESIDUALS,
    evaluate_r3b,
    probe_family_stratified_residuals,
)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/JANUS_TRUMP_OSIRIS_R3B_PROOF_CARRYING_RECOVERY_RESULT_2026-09-01.json")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[1]
    prereg_path = repo / "research" / "JANUS_TRUMP_OSIRIS_R3B_PROOF_CARRYING_RECOVERY_PREREGISTRATION_2026-09-01.json"
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    assert prereg["status"] == "FROZEN_BEFORE_R3B_EXECUTION"
    assert prereg["parent_R3A"]["immutable"] is True
    assert prereg["changes_allowed"]["R2_route_rule"] == "UNCHANGED"

    residuals = probe_family_stratified_residuals()
    assert all(r["pretruth_witness"]["truth"] is None for r in residuals)
    evaluated = [evaluate_r3b(r) for r in residuals]

    families = sorted({r["source"]["family"] for r in evaluated})
    unique_witnesses = len({r["pretruth_witness"]["witness_sha256"] for r in evaluated})
    all_pretruth = all(r["pretruth_witness"]["truth"] is None for r in evaluated)
    exact_verifier = sum(r["checks"]["baseline_exact"] for r in evaluated)
    matches = sum(r["checks"]["terminal_match"] for r in evaluated)
    replay_failures = sum(1 for r in evaluated if r["candidate"]["terminal"] == "SAT" and not r["checks"]["sat_witness_replay"])
    verified = sum(r["checks"]["verified_experience_eligible"] for r in evaluated)
    sat_fallbacks = [
        r for r in evaluated
        if "FALLBACK" in r["candidate"]["mode"] and r["candidate"]["terminal"] == "SAT"
    ]
    sat_fallbacks_with_witness = sum(r["candidate"]["witness"] is not None and r["checks"]["sat_witness_replay"] for r in sat_fallbacks)

    by_sig = defaultdict(list)
    for r in evaluated:
        by_sig[r["pretruth_witness"]["signature"]["structural_key"]].append(r)
    repeat_groups = []
    for key, members in by_sig.items():
        roots = {(m["source"]["root_index"], m["source"]["family"], m["source"]["size"], m["source"]["variant"]) for m in members}
        if len(roots) >= 2:
            repeat_groups.append({
                "structural_key": key,
                "members": len(members),
                "distinct_roots": len(roots),
                "families": sorted({m["source"]["family"] for m in members}),
                "all_verified": all(m["checks"]["verified_experience_eligible"] for m in members),
            })

    exact_meets = sum(r["candidate"]["mode"] == "R3B_EXACT_DOUBLE_SPIRAL_MEET" for r in evaluated)
    baseline_work = sum(int(r["independent_exact_verifier"]["work"]) for r in evaluated)
    candidate_work = sum(int(r["candidate"]["work"]["charged_abstract_ops"]) for r in evaluated)

    acquisition_pass = len(evaluated) >= R3B_MIN_RESIDUALS and len(families) >= R3B_MIN_FAMILIES
    proof_carrying_pass = replay_failures == 0 and sat_fallbacks_with_witness == len(sat_fallbacks)
    exactness_pass = exact_verifier == len(evaluated) and matches == len(evaluated) and verified == len(evaluated)
    pretruth_pass = all_pretruth and unique_witnesses == len(evaluated)
    recurrence_pass = len(repeat_groups) >= 1
    primary_pass = acquisition_pass and proof_carrying_pass and exactness_pass and pretruth_pass and recurrence_pass

    work_delta = baseline_work - candidate_work
    work_fraction = 0.0 if baseline_work == 0 else work_delta / baseline_work
    status = (
        "R3B_RECOVERY_PRIMARY_PASS__R3A_REMAINS_FAILED__P_VS_NP_OPEN"
        if primary_pass else
        "R3B_RECOVERY_GATE_FAIL__R3A_REMAINS_FAILED__P_VS_NP_OPEN"
    )

    result = {
        "schema": "JANUS/TRUMP/OSIRIS-R3B-PROOF-CARRYING-RECOVERY/RESULT/v1.0",
        "status": status,
        "P_VS_NP": "OPEN",
        "runtime": {
            "repository": "Hawkar-usls/Janus-Fundamentum",
            "branch": "research/janus-trump-osiris-r3b-proof-carrying-recovery-2026-09-01",
            "github_sha": os.environ.get("GITHUB_SHA"),
            "python": sys.version,
            "platform": platform.platform(),
            "source_sha256": {
                "R3A_core": file_sha256(repo / "experiments" / "janus_trump_osiris_r3_natural_residuals.py"),
                "R3B_core": file_sha256(repo / "experiments" / "janus_trump_osiris_r3b_proof_carrying_recovery.py"),
                "R3B_runner": file_sha256(Path(__file__).resolve()),
                "R3B_prereg": file_sha256(prereg_path),
            },
        },
        "primary_gates": {
            "acquisition": {
                "pass": acquisition_pass,
                "residuals": len(evaluated),
                "required": R3B_MIN_RESIDUALS,
                "source_families": families,
                "source_family_count": len(families),
                "required_families": R3B_MIN_FAMILIES,
            },
            "pretruth": {
                "pass": pretruth_pass,
                "unique_witnesses": unique_witnesses,
                "all_truth_null_before_execution": all_pretruth,
            },
            "proof_carrying": {
                "pass": proof_carrying_pass,
                "sat_replay_failures": replay_failures,
                "sat_fallbacks": len(sat_fallbacks),
                "sat_fallbacks_with_replaying_witness": sat_fallbacks_with_witness,
            },
            "exactness": {
                "pass": exactness_pass,
                "independent_exact_verifier_passes": exact_verifier,
                "terminal_matches": matches,
                "verified_experiences": verified,
            },
            "natural_recurrence": {
                "pass": recurrence_pass,
                "repeat_group_count": len(repeat_groups),
                "repeat_groups": repeat_groups,
            },
        },
        "observations": {
            "exact_double_spiral_meet_cases": exact_meets,
            "abstract_work": {
                "baseline_frozen_TRUMP_DPLL": baseline_work,
                "candidate_charged_ops": candidate_work,
                "delta": work_delta,
                "fraction": work_fraction,
                "promotion": "DESCRIPTIVE_ONLY_NOT_FRESH_SPEEDUP_CLAIM",
            },
        },
        "rows": evaluated,
        "scientific_boundary": {
            "R3A_status_rewritten": False,
            "R3A_remains_failed": True,
            "P_VS_NP": "OPEN",
            "P_equals_NP_proved": False,
            "general_solver_speedup_established": False,
            "canonical_TRUMP_authority_changed": False,
        },
        "next_gate_if_primary_pass": "R4_FRESH_NATURAL_RESIDUAL_POLICY_TEST_ON_UNEXPOSED_EXISTING_TRUMP_WORKLOADS",
        "law": "REPAIR_PROOF_CARRIER_WITHOUT_ERASING_NEGATIVE_EVIDENCE",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "primary_gates": result["primary_gates"], "observations": result["observations"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
