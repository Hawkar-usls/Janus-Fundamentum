#!/usr/bin/env python3
"""R19 fresh unseen holdout for the byte-frozen R18 shared Boolean DAG.

The R19 world identities and resource rules were frozen before this harness was
implemented.  For each world the candidate runs first with no semantic truth
access.  Only a terminal candidate permits the independent full bridge-domain
verifier.  OPEN resource states are preserved as OPEN, never as mismatches.
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
import janus_trump_r15f_incremental_independent_semantic_control as r15f
import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_truth_blind_adversarial_world_selector as selector

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FREEZE_PATH = REPO / "research" / "JANUS_TRUMP_R19_FRESH_UNSEEN_DAG_WORLD_SET_AND_RESOURCE_FREEZE_2026-09-02.json"
EXPECTED_CANDIDATE_BLOB = "afa95321ec6edbb33bef222d8ee7234fe631a599"
WORLD_IDS = tuple(f"R19-W{i:02d}" for i in range(1, 9))


def load_freeze():
    d = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    assert d["status"] == "FROZEN_BEFORE_R19_CANDIDATE_HARNESS_IMPLEMENTATION_AND_EXECUTION"
    assert d["frozen_candidate"]["git_blob_sha"] == EXPECTED_CANDIDATE_BLOB
    assert len(d["worlds"]) == 8
    assert tuple(w["id"] for w in d["worlds"]) == WORLD_IDS
    assert d["selector_receipt"]["truth_accessed"] is False
    assert d["selector_receipt"]["candidate_accessed"] is False
    return d


def generate_frozen_world(spec):
    derived = selector.derive_spec(spec["suite"], int(spec["n"]), int(spec["rep"]))
    for key in ("seed", "branch_value", "derivation_string", "m", "k"):
        if derived[key] != spec[key]:
            raise AssertionError(f"R19 selector derivation drift {spec['id']}:{key}")
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
        raise AssertionError(f"root hash drift {spec['id']}")
    order, _ = direct.occurrence_order(root)
    if not order or int(order[0]) != int(spec["pivot"]):
        raise AssertionError(f"pivot drift {spec['id']}")
    fd = r9.restriction_frame_delta(root, int(spec["pivot"]), bool(spec["branch_value"]))
    frame = tuple(fd["frame"])
    bridge = tuple(fd["active_bridge_vars"])
    frame_vars = len({abs(l) for c in frame for l in c})
    checks = {
        "frame_sha256": fd["frame_sha256"] == spec["frame_sha256"],
        "delta_sha256": fd["delta_sha256"] == spec["delta_sha256"],
        "bridge_vars": list(bridge) == list(spec["bridge_vars"]),
        "frame_clause_count": len(frame) == int(spec["frame_clause_count"]),
        "frame_variable_count": frame_vars == int(spec["frame_variable_count"]),
        "internal_variable_count": frame_vars - len(bridge) == int(spec["internal_variable_count"]),
        "frame_type": r9.classify_cnf(frame) == spec["frame_type"],
    }
    if not all(checks.values()):
        raise AssertionError(f"R19 world structural drift {spec['id']}: {checks}")
    return {"frame":frame,"bridge":bridge,"checks":checks}


def candidate_summary(candidate):
    return {k:v for k,v in candidate.items() if k not in ("dag","root")}


def candidate_allowed_with_deadline(candidate, bridge, deadline):
    dag = candidate["dag"]; root = candidate["root"]; allowed=[]; started=time.monotonic()
    domain = 1 << len(bridge)
    for mask in range(domain):
        if (mask & 255) == 0 and time.monotonic() >= deadline:
            return {"status":"OPEN_VERIFIER_RESOURCE_LIMIT","reason":"CANDIDATE_EVALUATION_DEADLINE","allowed_masks":allowed,"elapsed_seconds":time.monotonic()-started,"completed_masks":mask,"domain_size":domain}
        assignment={int(v):bool((mask>>i)&1) for i,v in enumerate(bridge)}
        if dag.evaluate(root,assignment):
            allowed.append(mask)
    return {"status":"COMPLETE","allowed_masks":allowed,"allowed_count":len(allowed),"elapsed_seconds":time.monotonic()-started,"completed_masks":domain,"domain_size":domain,"truth_table_sha256":mask_hash(allowed)}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks),separators=(",",":")).encode()).hexdigest()


def run_world(world_id):
    freeze = load_freeze()
    matches = [w for w in freeze["worlds"] if w["id"] == world_id]
    if len(matches) != 1:
        raise ValueError(f"world not frozen exactly once: {world_id}")
    spec = matches[0]
    generated = generate_frozen_world(spec)
    frame, bridge = generated["frame"], generated["bridge"]
    firewall = r18.candidate_firewall()
    base = {
        "schema":"JANUS/TRUMP/R19/FRESH_UNSEEN_DAG_HOLDOUT/WORLD_RESULT/v1.0",
        "created_date":"2026-09-02",
        "scientific_role":"FRESH_UNSEEN_PROSPECTIVE_HOLDOUT",
        "world_id":world_id,
        "source":{k:v for k,v in spec.items()},
        "world_regeneration_checks":generated["checks"],
        "frozen_candidate":{"git_blob_sha":EXPECTED_CANDIDATE_BLOB,"firewall":firewall,"logic_changes_allowed":False},
        "P_VS_NP":"OPEN",
    }
    if not firewall["pass"]:
        return {**base,"verdict":"R19_FAIL_INTEGRITY","candidate_ran":False,"verifier_ran":False,"reason":"FROZEN_CANDIDATE_FIREWALL_FAIL"}

    candidate_started=time.monotonic()
    candidate=r18.candidate_compile(frame,bridge)
    candidate_completed=time.monotonic()
    csum=candidate_summary(candidate)

    if candidate["status"] == "FAIL_INTEGRITY":
        return {**base,"verdict":"R19_FAIL_INTEGRITY","candidate_ran":True,"candidate":csum,"candidate_started_monotonic":candidate_started,"candidate_completed_monotonic":candidate_completed,"verifier_ran":False,"reason":candidate.get("reason","CANDIDATE_INTEGRITY_FAIL")}
    if candidate["status"] == "OPEN_RESOURCE_LIMIT":
        return {**base,"verdict":"R19_OPEN_CANDIDATE_RESOURCE_LIMIT","candidate_ran":True,"candidate":csum,"candidate_started_monotonic":candidate_started,"candidate_completed_monotonic":candidate_completed,"verifier_ran":False,"scientific_firewall":{"truth_not_accessed":True,"resource_limit_not_negative_evidence":True,"world_frozen_before_candidate":True}}
    if candidate["status"] != "COMPLETE_INTERFACE_DAG":
        return {**base,"verdict":"R19_FAIL_INTEGRITY","candidate_ran":True,"candidate":csum,"verifier_ran":False,"reason":"UNKNOWN_CANDIDATE_TERMINAL_STATUS"}
    if set(candidate.get("final_support",())) - set(bridge):
        return {**base,"verdict":"R19_FAIL_INTEGRITY","candidate_ran":True,"candidate":csum,"verifier_ran":False,"reason":"FINAL_SUPPORT_NOT_BRIDGE_ONLY"}

    verifier_started=time.monotonic()
    deadline=verifier_started + float(freeze["post_candidate_verifier"]["wall_seconds_total_after_candidate_per_world"])
    original=r15f.incremental_allowed_masks(frame,bridge,"m22",deadline,f"{world_id}_ORIGINAL")
    if original["status"] == "OPEN_VERIFIER_RESOURCE_LIMIT":
        return {**base,"verdict":"R19_OPEN_VERIFIER_RESOURCE_LIMIT","candidate_ran":True,"candidate":csum,"candidate_completed_monotonic":candidate_completed,"verifier_ran":True,"verifier_started_monotonic":verifier_started,"original_frame_verifier":original,"candidate_interface_verifier":{"not_run":True},"scientific_firewall":{"candidate_terminal_before_verifier":candidate_completed <= verifier_started,"verifier_limit_not_negative_evidence":True}}
    if original["status"] != "COMPLETE" or original.get("sat_model_replay_failures"):
        return {**base,"verdict":"R19_FAIL_INTEGRITY","candidate_ran":True,"candidate":csum,"verifier_ran":True,"reason":"ORIGINAL_VERIFIER_INTEGRITY_FAIL","original_frame_verifier":original}

    got=candidate_allowed_with_deadline(candidate,bridge,deadline)
    if got["status"] == "OPEN_VERIFIER_RESOURCE_LIMIT":
        return {**base,"verdict":"R19_OPEN_VERIFIER_RESOURCE_LIMIT","candidate_ran":True,"candidate":csum,"verifier_ran":True,"original_frame_verifier":{k:v for k,v in original.items() if k!="allowed_masks"},"candidate_interface_verifier":{k:v for k,v in got.items() if k!="allowed_masks"},"scientific_firewall":{"candidate_terminal_before_verifier":candidate_completed <= verifier_started,"verifier_limit_not_negative_evidence":True}}

    exact=set(original["allowed_masks"]); observed=set(got["allowed_masks"])
    fp=sorted(observed-exact); fn=sorted(exact-observed); match=not fp and not fn
    comparison={
        "full_domain":True,
        "domain_size":1<<len(bridge),
        "allowed_set_equal":match,
        "original_allowed_count":len(exact),
        "candidate_allowed_count":len(observed),
        "false_positive_count":len(fp),
        "false_negative_count":len(fn),
        "first_false_positive_masks":fp[:32],
        "first_false_negative_masks":fn[:32],
        "original_truth_table_sha256":original["truth_table_sha256"],
        "candidate_truth_table_sha256":got["truth_table_sha256"],
    }
    verdict="R19_PASS_EXACT_UNSEEN" if match else "R19_MISMATCH_UNSEEN"
    return {
        **base,
        "verdict":verdict,
        "candidate_ran":True,
        "candidate":csum,
        "candidate_started_monotonic":candidate_started,
        "candidate_completed_monotonic":candidate_completed,
        "verifier_ran":True,
        "verifier_started_monotonic":verifier_started,
        "original_frame_verifier":{k:v for k,v in original.items() if k!="allowed_masks"},
        "candidate_interface_verifier":{k:v for k,v in got.items() if k!="allowed_masks"},
        "comparison":comparison,
        "scientific_firewall":{
            "candidate_terminal_before_verifier":candidate_completed <= verifier_started,
            "world_selected_and_frozen_before_candidate":True,
            "candidate_byte_frozen_before_world_selection":True,
            "full_domain_compared":True,
            "all_original_sat_models_replayed":not original.get("sat_model_replay_failures"),
        },
        "claim_ceiling":"One fresh unseen world result only; no arbitrary-CNF or complexity-class conclusion.",
        "seal":"THE_FROZEN_SHARED_MACHINE_MET_A_WORLD_CHOSEN_BEHIND_A_CLOSED_DOOR",
        "P_VS_NP":"OPEN",
    }


def aggregate_directory(directory: Path):
    files=sorted(directory.glob("*.json"))
    results=[]
    for p in files:
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("schema")=="JANUS/TRUMP/R19/FRESH_UNSEEN_DAG_HOLDOUT/WORLD_RESULT/v1.0":
            results.append(d)
    by_id={r["world_id"]:r for r in results}
    missing=[wid for wid in WORLD_IDS if wid not in by_id]
    ordered=[by_id[wid] for wid in WORLD_IDS if wid in by_id]
    counts={}
    for r in ordered:
        counts[r["verdict"]]=counts.get(r["verdict"],0)+1
    if missing or counts.get("R19_FAIL_INTEGRITY",0):
        verdict="R19_FAIL_INTEGRITY__NO_SCIENTIFIC_CLAIM"
    elif counts.get("R19_MISMATCH_UNSEEN",0):
        verdict="R19_SEMANTIC_COUNTEREXAMPLE_UNSEEN__PRESERVE_AND_STOP"
    elif counts.get("R19_OPEN_CANDIDATE_RESOURCE_LIMIT",0) or counts.get("R19_OPEN_VERIFIER_RESOURCE_LIMIT",0):
        verdict="R19_OPEN_RESOURCE_LIMIT__PARTIAL_EXACT_SURVIVAL_ONLY"
    elif counts.get("R19_PASS_EXACT_UNSEEN",0)==8:
        verdict="R19_8_OF_8_PASS_EXACT_UNSEEN"
    else:
        verdict="R19_FAIL_INTEGRITY__NO_SCIENTIFIC_CLAIM"
    return {
        "schema":"JANUS/TRUMP/R19/FRESH_UNSEEN_DAG_HOLDOUT/AGGREGATE_RESULT/v1.0",
        "created_date":"2026-09-02",
        "verdict":verdict,
        "scientific_role":"FRESH_UNSEEN_PROSPECTIVE_HOLDOUT",
        "frozen_candidate_git_blob_sha":EXPECTED_CANDIDATE_BLOB,
        "world_count_expected":8,
        "world_count_present":len(ordered),
        "missing_worlds":missing,
        "verdict_counts":counts,
        "results":ordered,
        "claim_ceiling":"Even 8/8 exact unseen success is finite-family evidence only; it is not a proof of polynomial scaling, arbitrary-CNF totality, SAT-in-P, P=NP, or P!=NP.",
        "seal":"THE_EIGHT_NEW_DOORS_GRADED_THE_FROZEN_SHARED_MACHINE_WITHOUT_MOVING_AFTER_THE_KNOCK",
        "P_VS_NP":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--world")
    g.add_argument("--aggregate-dir")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    if args.world:
        out=run_world(args.world)
        code=2 if out["verdict"]=="R19_FAIL_INTEGRITY" else 0
        brief={"world_id":out["world_id"],"verdict":out["verdict"],"source":{k:out["source"][k] for k in ("suite","n","frame_clause_count","internal_variable_count","bridge_variable_count")},"candidate":out.get("candidate"),"comparison":out.get("comparison"),"P_VS_NP":"OPEN"}
    else:
        out=aggregate_directory(Path(args.aggregate_dir))
        code=2 if out["verdict"]=="R19_FAIL_INTEGRITY__NO_SCIENTIFIC_CLAIM" else 0
        brief={"verdict":out["verdict"],"verdict_counts":out["verdict_counts"],"missing_worlds":out["missing_worlds"],"P_VS_NP":"OPEN"}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(brief,indent=2,sort_keys=True))
    return code


if __name__=="__main__": raise SystemExit(main())
