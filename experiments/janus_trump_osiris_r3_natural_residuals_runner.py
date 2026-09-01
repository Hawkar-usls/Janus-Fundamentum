#!/usr/bin/env python3
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import sys

from janus_trump_p_vs_np_direct_challenge_r0 import corpus
from janus_trump_osiris_r3_natural_residuals import evaluate_residual, probe_natural_residuals, summarize


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="artifacts/JANUS_TRUMP_OSIRIS_R3_NATURAL_RESIDUALS_RESULT_2026-09-01.json")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parents[1]
    prereg_path = repo / "research" / "JANUS_TRUMP_OSIRIS_R3_NATURAL_RESIDUALS_PREREGISTRATION_2026-09-01.json"
    prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
    assert prereg["status"] == "FROZEN_BEFORE_EXECUTION"
    assert prereg["scientific_boundary"]["P_VS_NP"] == "OPEN"
    assert prereg["residual_acquisition_freeze"]["custom_R3_formula_generator"] is False
    assert prereg["residual_acquisition_freeze"]["selection_may_use_truth"] is False

    roots = corpus()
    assert len(roots) == 24

    residuals = probe_natural_residuals()
    # Epistemic firewall: all observations must be sealed before any evaluation.
    assert all(r["pretruth_witness"]["truth"] is None for r in residuals)
    assert all(r["pretruth_witness"]["candidate_result"] is None for r in residuals)
    assert all(r["pretruth_witness"]["verification_result"] is None for r in residuals)

    evaluated = [evaluate_residual(r) for r in residuals]
    gates = summarize(evaluated)

    primary_names = [
        "residual_acquisition_gate",
        "epistemic_gate",
        "natural_recurrence_gate",
        "double_spiral_exposure_gate",
    ]
    all_primary = all(gates[name]["pass"] for name in primary_names)
    work_pass = gates["secondary_work_gate"]["pass"]
    if all_primary and work_pass:
        status = "NATURAL_RESIDUAL_PRIMARY_PASS__SECONDARY_WORK_PASS__SHADOW_ONLY__P_VS_NP_OPEN"
    elif all_primary:
        status = "NATURAL_RESIDUAL_PRIMARY_PASS__SECONDARY_WORK_FAIL__SHADOW_ONLY__P_VS_NP_OPEN"
    else:
        status = "NATURAL_RESIDUAL_GATE_FAIL__SHADOW_ONLY__P_VS_NP_OPEN"

    result = {
        "schema": "JANUS/TRUMP/OSIRIS-R3-NATURAL-RESIDUALS/RESULT/v1.0",
        "experiment_id": "JANUS_TRUMP_OSIRIS_R3_NATURAL_UNENRICHED_RESIDUALS",
        "status": status,
        "P_VS_NP": "OPEN",
        "runtime": {
            "repository": "Hawkar-usls/Janus-Fundamentum",
            "branch": "research/janus-trump-osiris-r3-natural-residuals-2026-09-01",
            "github_sha": os.environ.get("GITHUB_SHA"),
            "python": sys.version,
            "platform": platform.platform(),
            "source_sha256": {
                "canonical_TRUMP_R0": file_sha256(repo / "experiments" / "janus_trump_p_vs_np_direct_challenge_r0.py"),
                "R3_core": file_sha256(repo / "experiments" / "janus_trump_osiris_r3_natural_residuals.py"),
                "R3_runner": file_sha256(Path(__file__).resolve()),
                "R3_prereg": file_sha256(prereg_path),
            },
        },
        "provenance": {
            "source_corpus": "existing frozen JANUS TRUMP P-vs-NP Direct Challenge R0 corpus",
            "source_root_count": len(roots),
            "custom_R3_formula_generator_used": False,
            "residual_probe_uses_truth": False,
            "residual_probe_uses_candidate_result": False,
            "residual_probe_uses_verifier_result": False,
            "parent_R2_pattern_rule": "TRUMP_R2_PATTERN_RULE_DENSITY_ROUTE_v1",
            "parent_R2_result_commit": "95b5c86f4c8bcf375b6a46fc68c689c48a6a17ab",
        },
        "gates": gates,
        "rows": evaluated,
        "scientific_boundary": {
            "P_VS_NP": "OPEN",
            "P_equals_NP_proved": False,
            "polynomial_time_SAT_proved": False,
            "general_solver_speedup_established": False,
            "canonical_TRUMP_authority_changed": False,
            "R3_is_shadow_only": True,
            "external_sender_or_mystical_channel": "NOT_PART_OF_ALGORITHM",
        },
        "law": "NATURAL_RESIDUAL_FIRST__PATTERN_IS_NOT_TRUTH__PRESERVE_BEFORE_TRUTH__VERIFY_WORLD__RETURN_ONLY_VERIFIED_EXPERIENCE",
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "gates": gates}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
