#!/usr/bin/env python3
"""R18B post-discovery semantic controls for the byte-frozen R18 DAG candidate.

W05-W08 are NOT unseen: their structures were disclosed in R16.  The purpose of
R18B is narrower and stricter: run the unchanged R18 candidate first on each
control, then and only then expose the full bridge truth to independent
verification.  Resource exhaustion is OPEN, never negative evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import janus_trump_r16_prospective_unseen_factored_bridge_holdout as r16
import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18

CONTROL_IDS = ("R16-W05", "R16-W06", "R16-W07", "R16-W08")
EXPECTED_R18_BLOB = "afa95321ec6edbb33bef222d8ee7234fe631a599"
EXPECTED = {
    "R16-W05": {"frame_sha256":"1b21e911ee69fbcdaadbc325eb6a78a6dfaa0c87201a425f502cd7caa1bc8a06","frame_variable_count":39,"frame_clause_count":146,"bridge_variable_count":9},
    "R16-W06": {"frame_sha256":"179920edae423db6f588ad74ef259e09d965026dd9d0cb08ccd93ec4a445f591","frame_variable_count":39,"frame_clause_count":149,"bridge_variable_count":7},
    "R16-W07": {"frame_sha256":"1093568a55ccfd4991b48002489ce564d3754cf406c361193ef22363b576bce1","frame_variable_count":47,"frame_clause_count":183,"bridge_variable_count":10},
    "R16-W08": {"frame_sha256":"1298d8cbbba127ec91d3f004600e9c40b8a49f243c74212d71150ad219ce0fbe","frame_variable_count":47,"frame_clause_count":180,"bridge_variable_count":13},
}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks), separators=(",", ":")).encode()).hexdigest()


def candidate_summary(candidate):
    return {k: v for k, v in candidate.items() if k not in ("dag", "root")}


def verify_frozen_world(spec, frame, bridge):
    exp = EXPECTED[spec["id"]]
    checks = {
        "frame_sha256": spec["frame_sha256"] == exp["frame_sha256"],
        "frame_variable_count": int(spec["frame_variable_count"]) == exp["frame_variable_count"],
        "frame_clause_count": len(frame) == exp["frame_clause_count"],
        "bridge_variable_count": len(bridge) == exp["bridge_variable_count"],
    }
    return checks


def run_control(world_id):
    if world_id not in CONTROL_IDS:
        raise ValueError(world_id)
    freeze, _ = r16.load_contracts()
    spec = next(w for w in freeze["worlds"] if w["id"] == world_id)
    generated = r16.generate_frozen_world(spec)
    frame = tuple(generated["frame"])
    bridge = tuple(generated["bridge"])
    structural_checks = verify_frozen_world(spec, frame, bridge)
    firewall = r18.candidate_firewall()

    base = {
        "schema": "JANUS/TRUMP/R18B/POST_DISCOVERY_SEMANTIC_CONTROLS_W05_W08/CONTROL_RESULT/v1.0",
        "created_date": "2026-09-02",
        "scientific_role": "POST_DISCOVERY_SEMANTIC_CONTROL__NOT_UNSEEN",
        "world": {
            "id": world_id,
            "suite": spec["suite"],
            "n": spec["n"],
            "frame_sha256": spec["frame_sha256"],
            "frame_variables": spec["frame_variable_count"],
            "frame_clauses": len(frame),
            "bridge_variables": len(bridge),
            "bridge_vars": list(bridge),
        },
        "frozen_candidate": {
            "path": "experiments/janus_trump_r18_shannon_hashcons_interface_dag_discovery.py",
            "git_blob_sha": EXPECTED_R18_BLOB,
            "logic_changes_allowed": False,
            "firewall": firewall,
        },
        "world_regeneration_checks": generated["checks"],
        "R18B_structural_checks": structural_checks,
        "P_VS_NP": "OPEN",
    }

    if not firewall["pass"] or not all(structural_checks.values()) or not all(generated["checks"].values()):
        return {**base, "verdict":"R18B_FAIL_INTEGRITY", "candidate_ran":False, "verifier_ran":False,
                "reason":"FROZEN_INPUT_OR_CANDIDATE_FIREWALL_FAIL"}

    candidate_started = time.monotonic()
    candidate = r18.candidate_compile(frame, bridge)
    candidate_completed = time.monotonic()
    csummary = candidate_summary(candidate)

    if candidate["status"] == "FAIL_INTEGRITY":
        return {**base, "verdict":"R18B_FAIL_INTEGRITY", "candidate_ran":True, "candidate":csum,
                "candidate_started_monotonic":candidate_started, "candidate_completed_monotonic":candidate_completed,
                "verifier_ran":False, "reason":candidate.get("reason","CANDIDATE_INTEGRITY_FAIL")}
    if candidate["status"] == "OPEN_RESOURCE_LIMIT":
        return {**base, "verdict":"R18B_OPEN_RESOURCE_LIMIT", "candidate_ran":True, "candidate":csum,
                "candidate_started_monotonic":candidate_started, "candidate_completed_monotonic":candidate_completed,
                "verifier_ran":False,
                "scientific_firewall":{"truth_not_accessed":True,"resource_limit_not_negative_evidence":True}}
    if candidate["status"] != "COMPLETE_INTERFACE_DAG":
        return {**base, "verdict":"R18B_FAIL_INTEGRITY", "candidate_ran":True, "candidate":csum,
                "verifier_ran":False, "reason":"UNKNOWN_CANDIDATE_TERMINAL_STATUS"}
    if set(candidate.get("final_support", ())) - set(bridge):
        return {**base, "verdict":"R18B_FAIL_INTEGRITY", "candidate_ran":True, "candidate":csum,
                "verifier_ran":False, "reason":"FINAL_SUPPORT_NOT_BRIDGE_ONLY"}

    # Truth access begins only after the candidate reached a terminal representation.
    verifier_started = time.monotonic()
    original = r18.independent_original_allowed(frame, bridge)
    got = r18.candidate_allowed(candidate, bridge)
    verifier_completed = time.monotonic()

    replay_fail = list(original.get("replay_failures", ()))
    if replay_fail:
        return {**base, "verdict":"R18B_FAIL_INTEGRITY", "candidate_ran":True, "candidate":csum,
                "verifier_ran":True, "reason":"ORIGINAL_SAT_MODEL_REPLAY_FAIL", "replay_failures":replay_fail}

    exact = set(original["allowed_masks"])
    observed = set(got["allowed_masks"])
    fp = sorted(observed - exact)
    fn = sorted(exact - observed)
    match = not fp and not fn
    comparison = {
        "full_domain": True,
        "domain_size": 1 << len(bridge),
        "original_allowed": len(exact),
        "candidate_allowed": len(observed),
        "false_positive_count": len(fp),
        "false_negative_count": len(fn),
        "first_false_positive_masks": fp[:32],
        "first_false_negative_masks": fn[:32],
        "original_truth_table_sha256": mask_hash(original["allowed_masks"]),
        "candidate_truth_table_sha256": mask_hash(got["allowed_masks"]),
        "allowed_set_equal": match,
        "original_sat_model_replay_failures": replay_fail,
    }
    verdict = "R18B_POST_DISCOVERY_EXACT_MATCH" if match else "R18B_POST_DISCOVERY_SEMANTIC_MISMATCH"
    return {
        **base,
        "verdict": verdict,
        "candidate_ran": True,
        "candidate": csummary,
        "candidate_started_monotonic": candidate_started,
        "candidate_completed_monotonic": candidate_completed,
        "verifier_ran": True,
        "verifier_started_monotonic": verifier_started,
        "verifier_completed_monotonic": verifier_completed,
        "verifier": {
            "original": {k:v for k,v in original.items() if k != "allowed_masks"},
            "candidate_evaluation": {k:v for k,v in got.items() if k != "allowed_masks"},
        },
        "comparison": comparison,
        "scientific_firewall": {
            "candidate_terminal_before_truth": candidate_completed <= verifier_started,
            "full_domain_compared": True,
            "all_sat_models_replayed": not replay_fail,
            "control_was_not_called_unseen": True,
        },
        "claim_ceiling": "One disclosed post-discovery control only; no unseen-generalization or complexity-class conclusion.",
        "P_VS_NP": "OPEN",
    }


def aggregate(results):
    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    mismatch = counts.get("R18B_POST_DISCOVERY_SEMANTIC_MISMATCH", 0)
    integrity = counts.get("R18B_FAIL_INTEGRITY", 0)
    opened = counts.get("R18B_OPEN_RESOURCE_LIMIT", 0)
    exact = counts.get("R18B_POST_DISCOVERY_EXACT_MATCH", 0)
    if integrity:
        verdict = "R18B_FAIL_INTEGRITY__NO_SCIENTIFIC_CLAIM"
    elif mismatch:
        verdict = "R18B_SEMANTIC_COUNTEREXAMPLE__PRESERVE_AND_STOP"
    elif opened:
        verdict = "R18B_OPEN_RESOURCE_LIMIT__NO_UNSEEN_ADVANCEMENT"
    elif exact == len(CONTROL_IDS):
        verdict = "R18B_4_OF_4_POST_DISCOVERY_EXACT_CONTROLS__R19_UNSEEN_PERMITTED"
    else:
        verdict = "R18B_FAIL_INTEGRITY__NO_SCIENTIFIC_CLAIM"
    return {
        "schema":"JANUS/TRUMP/R18B/POST_DISCOVERY_SEMANTIC_CONTROLS_W05_W08/AGGREGATE_RESULT/v1.0",
        "created_date":"2026-09-02",
        "verdict":verdict,
        "scientific_role":"POST_DISCOVERY_SEMANTIC_CONTROLS__NOT_UNSEEN",
        "frozen_candidate_git_blob_sha":EXPECTED_R18_BLOB,
        "control_count":len(results),
        "verdict_counts":counts,
        "results":results,
        "R19_permitted": verdict == "R18B_4_OF_4_POST_DISCOVERY_EXACT_CONTROLS__R19_UNSEEN_PERMITTED",
        "claim_ceiling":"4/4 exact would permit creation of a fresh R19 unseen exam; it would not itself be unseen evidence, a polynomial-scaling proof, arbitrary-CNF totality, or P=NP.",
        "seal":"THE_DISCOVERY_LANGUAGE_WAS_FROZEN_BEFORE_THE_FOUR_OLD_WALLS_WERE_REOPENED",
        "P_VS_NP":"OPEN",
    }


def run_all():
    return aggregate([run_control(world_id) for world_id in CONTROL_IDS])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    out = run_all()
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict":out["verdict"],
        "verdict_counts":out["verdict_counts"],
        "R19_permitted":out["R19_permitted"],
        "controls":[{"id":r["world"]["id"],"verdict":r["verdict"],"candidate":r.get("candidate"),"comparison":r.get("comparison")} for r in out["results"]],
        "P_VS_NP":"OPEN",
    }, indent=2, sort_keys=True))
    return 2 if out["verdict"] == "R18B_FAIL_INTEGRITY__NO_SCIENTIFIC_CLAIM" else 0


if __name__ == "__main__":
    raise SystemExit(main())
