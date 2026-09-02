#!/usr/bin/env python3
"""R16 prospective unseen holdout for the byte-frozen R15D candidate.

The exact world set is frozen on disk.  For each world the frozen candidate runs
first.  Only after a terminal candidate representation may independent
incremental SAT witnesses inspect the original frame and candidate interface.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9
import janus_trump_r15d_bounded_observer_equivalent_refactor as r15d
import janus_trump_r15f_incremental_independent_semantic_control as r15f
import janus_trump_r16_truth_blind_world_selector as selector

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FREEZE_PATH = REPO / "research" / "JANUS_TRUMP_R16_PROSPECTIVE_UNSEEN_WORLD_SET_FREEZE_2026-09-02.json"
RESOURCE_PATH = REPO / "research" / "JANUS_TRUMP_R16_EXECUTION_RESOURCE_ENVELOPE_FREEZE_2026-09-02.json"
EXPECTED_CANDIDATE_BLOB = "e6def9fef656c8f1af1b9f245bc855081f13a586"


def load_contracts():
    freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    resources = json.loads(RESOURCE_PATH.read_text(encoding="utf-8"))
    assert freeze["status"] == "FROZEN_BEFORE_R16_CANDIDATE_EXECUTION"
    assert resources["status"] == "FROZEN_BEFORE_R16_HARNESS_IMPLEMENTATION_AND_EXECUTION"
    assert freeze["frozen_candidate"]["blob_sha"] == EXPECTED_CANDIDATE_BLOB
    assert resources["candidate"]["blob_sha"] == EXPECTED_CANDIDATE_BLOB
    assert len(freeze["worlds"]) == 8
    return freeze, resources


def generate_frozen_world(spec):
    derived = selector.derive_spec(spec["suite"], int(spec["n"]), int(spec["rep"]))
    for key in ("seed", "branch_value", "derivation_string", "m", "k"):
        if derived[key] != spec[key]:
            raise AssertionError(f"frozen selector derivation drift for {spec['id']}:{key}")
    sat_core = r8a.load_legacy_sat_core()
    rng = random.Random(int(spec["seed"]))
    if spec["suite"] == "PLANTED":
        inst = sat_core.gen_planted(int(spec["n"]), int(spec["m"]), int(spec["k"]), rng)
    elif spec["suite"] == "UNSAT_CORE":
        inst = sat_core.gen_unsat_core(int(spec["n"]), int(spec["m"]), int(spec["k"]), rng)
    else:
        raise ValueError(spec["suite"])
    root = direct.canon(inst.clauses)
    if r8a.digest(root) != spec["root_sha256"]:
        raise AssertionError(f"root hash drift for {spec['id']}")
    order, _ = direct.occurrence_order(root)
    if not order or int(order[0]) != int(spec["pivot"]):
        raise AssertionError(f"pivot drift for {spec['id']}")
    fd = r9.restriction_frame_delta(root, int(spec["pivot"]), bool(spec["branch_value"]))
    frame = tuple(fd["frame"])
    bridge = tuple(fd["active_bridge_vars"])
    checks = {
        "frame_sha256": fd["frame_sha256"] == spec["frame_sha256"],
        "delta_sha256": fd["delta_sha256"] == spec["delta_sha256"],
        "bridge_vars": list(bridge) == list(spec["bridge_vars"]),
        "frame_clause_count": len(frame) == int(spec["frame_clause_count"]),
        "frame_variable_count": len({abs(l) for c in frame for l in c}) == int(spec["frame_variable_count"]),
        "frame_type": r9.classify_cnf(frame) == spec["frame_type"],
    }
    if not all(checks.values()):
        raise AssertionError(f"frozen world structural drift for {spec['id']}: {checks}")
    return {"root": root, "frame": frame, "bridge": bridge, "checks": checks}


def formula_hash(formula):
    return hashlib.sha256(json.dumps([list(c) for c in formula], separators=(",", ":")).encode()).hexdigest()


def candidate_summary(candidate, frame, bridge):
    formula = tuple(tuple(c) for c in candidate.get("formula", []))
    original_vars = {abs(l) for c in frame for l in c}
    original_internal = original_vars - set(bridge)
    remaining_original_internal_in_formula = sorted(original_internal & {abs(l) for c in formula for l in c})
    checkpoint = candidate.get("checkpoint", {})
    return {
        "status": candidate.get("status"),
        "reason": candidate.get("reason"),
        "elapsed_seconds": candidate.get("elapsed_seconds"),
        "history_steps": len(candidate.get("history", [])),
        "active_clauses": len(formula),
        "formula_sha256": formula_hash(formula),
        "max_clause_width": max((len(c) for c in formula), default=0),
        "remaining_original_internal_in_formula": remaining_original_internal_in_formula,
        "checkpoint": checkpoint,
        "auxiliary_variables": checkpoint.get("auxiliary_variables"),
        "shared_pair_atoms": checkpoint.get("shared_pair_atoms"),
        "atom_reuse_hits": checkpoint.get("atom_reuse_hits"),
        "pair_attempts": checkpoint.get("pair_attempts"),
    }


def run_world(world_id):
    freeze, resources = load_contracts()
    matches = [w for w in freeze["worlds"] if w["id"] == world_id]
    if len(matches) != 1:
        raise ValueError(f"world not frozen exactly once: {world_id}")
    spec = matches[0]
    generated = generate_frozen_world(spec)
    frame, bridge = generated["frame"], generated["bridge"]
    firewall = r15d.candidate_firewall()

    base = {
        "schema": "JANUS/TRUMP/R16/PROSPECTIVE_UNSEEN_FACTORED_BRIDGE_HOLDOUT/WORLD_RESULT/v1.0",
        "created_date": "2026-09-02",
        "world_id": world_id,
        "source": {k: v for k, v in spec.items()},
        "world_regeneration_checks": generated["checks"],
        "frozen_candidate": {"blob_sha": EXPECTED_CANDIDATE_BLOB, "firewall": firewall},
        "P_VS_NP": "OPEN",
    }
    if not firewall["pass"]:
        return {**base, "verdict": "FAIL_INTEGRITY", "candidate_ran": False, "verifier_ran": False,
                "reason": "FROZEN_CANDIDATE_FIREWALL_FAIL"}

    candidate_started = time.monotonic()
    candidate = r15d.compile_observed(frame, bridge)
    candidate_completed = time.monotonic()
    csum = candidate_summary(candidate, frame, bridge)
    terminal = candidate.get("status") in ("COMPLETE_EXTENDED_INTERFACE", "COMPLETE_UNSAT_INTERFACE")
    if not terminal:
        if candidate.get("status") == "FAIL_INTEGRITY":
            verdict = "FAIL_INTEGRITY"
        else:
            verdict = "OPEN_CANDIDATE_RESOURCE_LIMIT"
        return {
            **base,
            "verdict": verdict,
            "candidate_ran": True,
            "candidate": csum,
            "candidate_started_monotonic": candidate_started,
            "candidate_completed_monotonic": candidate_completed,
            "verifier_ran": False,
            "scientific_firewall": {
                "no_truth_before_candidate_terminal": True,
                "resource_limit_not_negative_evidence": verdict == "OPEN_CANDIDATE_RESOURCE_LIMIT",
            },
        }

    if csum["max_clause_width"] > 3 or (candidate.get("status") == "COMPLETE_EXTENDED_INTERFACE" and csum["remaining_original_internal_in_formula"]):
        return {**base, "verdict": "FAIL_INTEGRITY", "candidate_ran": True, "candidate": csum,
                "verifier_ran": False, "reason": "CANDIDATE_TERMINAL_POSTCONDITION_FAIL"}

    verifier_started = time.monotonic()
    deadline = verifier_started + float(resources["verifier"]["wall_seconds_total_after_candidate_per_world"])
    original = r15f.incremental_allowed_masks(frame, bridge, "m22", deadline, f"{world_id}_ORIGINAL")
    if original["status"] == "OPEN_VERIFIER_RESOURCE_LIMIT":
        return {**base, "verdict": "OPEN_VERIFIER_RESOURCE_LIMIT", "candidate_ran": True, "candidate": csum,
                "verifier_ran": True, "original_frame_verifier": original,
                "candidate_interface_verifier": {"not_run": True},
                "scientific_firewall": {"candidate_terminal_before_verifier": candidate_completed <= verifier_started,
                                        "verifier_limit_not_negative_evidence": True}}
    if original["status"] != "COMPLETE" or original.get("sat_model_replay_failures"):
        return {**base, "verdict": "FAIL_INTEGRITY", "candidate_ran": True, "candidate": csum,
                "verifier_ran": True, "original_frame_verifier": original,
                "candidate_interface_verifier": {"not_run": True}, "reason": "ORIGINAL_VERIFIER_INTEGRITY_FAIL"}

    candidate_formula = tuple(tuple(c) for c in candidate.get("formula", []))
    candidate_scan = r15f.incremental_allowed_masks(candidate_formula, bridge, "g4", deadline, f"{world_id}_CANDIDATE")
    if candidate_scan["status"] == "OPEN_VERIFIER_RESOURCE_LIMIT":
        return {**base, "verdict": "OPEN_VERIFIER_RESOURCE_LIMIT", "candidate_ran": True, "candidate": csum,
                "verifier_ran": True, "original_frame_verifier": original,
                "candidate_interface_verifier": candidate_scan,
                "scientific_firewall": {"candidate_terminal_before_verifier": candidate_completed <= verifier_started,
                                        "verifier_limit_not_negative_evidence": True}}
    if candidate_scan["status"] != "COMPLETE" or candidate_scan.get("sat_model_replay_failures"):
        return {**base, "verdict": "FAIL_INTEGRITY", "candidate_ran": True, "candidate": csum,
                "verifier_ran": True, "original_frame_verifier": original,
                "candidate_interface_verifier": candidate_scan, "reason": "CANDIDATE_VERIFIER_INTEGRITY_FAIL"}

    exact = set(original["allowed_masks"])
    got = set(candidate_scan["allowed_masks"])
    fp = sorted(got - exact)
    fn = sorted(exact - got)
    match = not fp and not fn
    verdict = "PASS_EXACT_UNSEEN" if match else "MISMATCH_UNSEEN"
    comparison = {
        "full_domain": True,
        "allowed_set_equal": match,
        "original_allowed_count": len(exact),
        "candidate_allowed_count": len(got),
        "false_positive_count": len(fp),
        "false_negative_count": len(fn),
        "first_false_positive_masks": fp[:32],
        "first_false_negative_masks": fn[:32],
        "original_truth_table_sha256": original["truth_table_sha256"],
        "candidate_truth_table_sha256": candidate_scan["truth_table_sha256"],
    }
    return {
        **base,
        "verdict": verdict,
        "candidate_ran": True,
        "candidate": csum,
        "verifier_ran": True,
        "original_frame_verifier": {k: v for k, v in original.items() if k != "allowed_masks"},
        "candidate_interface_verifier": {k: v for k, v in candidate_scan.items() if k != "allowed_masks"},
        "comparison": comparison,
        "scientific_firewall": {
            "candidate_terminal_before_verifier": candidate_completed <= verifier_started,
            "world_selected_before_candidate": True,
            "no_candidate_logic_change_after_world_freeze": True,
            "full_domain_compared": True,
            "all_sat_models_replayed": not original.get("sat_model_replay_failures") and not candidate_scan.get("sat_model_replay_failures"),
            "all_pass": candidate_completed <= verifier_started and firewall["pass"],
        },
        "claim_ceiling": "One frozen unseen world result only; no arbitrary-CNF or complexity-class conclusion.",
        "seal": "THE_FROZEN_MACHINE_MET_AN_UNSEEN_WORLD_AND_THE_WORLD_WAS_ALLOWED_TO_SAY_YES_OR_NO",
        "P_VS_NP": "OPEN",
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--world", required=True); ap.add_argument("--output", required=True); args = ap.parse_args()
    result = run_world(args.world)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "world_id": result["world_id"],
        "verdict": result["verdict"],
        "n": result["source"]["n"],
        "suite": result["source"]["suite"],
        "bridge": result["source"]["bridge_variable_count"],
        "candidate": result.get("candidate"),
        "comparison": result.get("comparison"),
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 2 if result["verdict"] == "FAIL_INTEGRITY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
