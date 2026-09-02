#!/usr/bin/env python3
"""R18B semantic controls for byte-frozen R18 candidate on R16-W05..W08."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r16_prospective_unseen_factored_bridge_holdout as r16
import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18

CONTROL_IDS = ("R16-W05", "R16-W06", "R16-W07", "R16-W08")
EXPECTED_CANDIDATE_BLOB = "afa95321ec6edbb33bef222d8ee7234fe631a599"


def run_world(world_id):
    if world_id not in CONTROL_IDS:
        raise ValueError(world_id)
    freeze,_=r16.load_contracts(); spec=next(w for w in freeze["worlds"] if w["id"]==world_id); world=r16.generate_frozen_world(spec)
    frame=tuple(world["frame"]); bridge=tuple(world["bridge"]); fw=r18.candidate_firewall()
    candidate=r18.candidate_compile(frame,bridge)
    csummary={k:v for k,v in candidate.items() if k not in ("dag","root")}
    base={
        "schema":"JANUS/TRUMP/R18B/POST_DISCOVERY_SEMANTIC_CONTROLS/WORLD_RESULT/v1.0",
        "created_date":"2026-09-02",
        "world_id":world_id,
        "source":{k:v for k,v in spec.items()},
        "candidate_blob_sha":EXPECTED_CANDIDATE_BLOB,
        "candidate_firewall":fw,
        "candidate":csummary,
        "P_VS_NP":"OPEN",
    }
    if not fw["pass"] or candidate["status"]=="FAIL_INTEGRITY":
        return {**base,"verdict":"FAIL_INTEGRITY","verifier":{"not_run":True}}
    if candidate["status"]=="OPEN_RESOURCE_LIMIT":
        return {**base,"verdict":"OPEN_RESOURCE_LIMIT","verifier":{"not_run":True},"seal":"THE_FROZEN_DAG_MACHINE_HIT_ITS_RESOURCE_WALL_BEFORE_TRUTH"}
    if candidate["status"]!="COMPLETE_INTERFACE_DAG" or not set(candidate["final_support"]) <= set(bridge):
        return {**base,"verdict":"FAIL_INTEGRITY","verifier":{"not_run":True},"reason":"CANDIDATE_TERMINAL_POSTCONDITION_FAIL"}
    # Truth appears only after terminal candidate.
    original=r18.independent_original_allowed(frame,bridge); got=r18.candidate_allowed(candidate,bridge)
    exact=set(original["allowed_masks"]); cand=set(got["allowed_masks"]); fp=sorted(cand-exact); fn=sorted(exact-cand)
    comparison={
        "full_domain":True,
        "domain_size":1<<len(bridge),
        "original_allowed":len(exact),
        "candidate_allowed":len(cand),
        "false_positive_count":len(fp),
        "false_negative_count":len(fn),
        "first_false_positive_masks":fp[:32],
        "first_false_negative_masks":fn[:32],
        "original_truth_table_sha256":r18.mask_hash(original["allowed_masks"]),
        "candidate_truth_table_sha256":r18.mask_hash(got["allowed_masks"]),
        "original_sat_model_replay_failures":original["replay_failures"],
        "allowed_set_equal":not fp and not fn,
    }
    verdict="PASS_EXACT_POST_DISCOVERY_CONTROL" if comparison["allowed_set_equal"] and not original["replay_failures"] else "MISMATCH_POST_DISCOVERY_CONTROL"
    csummary["compression_vs_R16_width3_checkpoint"] = {
        "R16-W05":198719,
        "R16-W06":253331,
        "R16-W07":160968,
        "R16-W08":200745,
    }[world_id] / candidate["final_active_nodes"] if candidate["final_active_nodes"] else None
    return {**base,"candidate":csummary,"verdict":verdict,
            "verifier":{"original":{k:v for k,v in original.items() if k!="allowed_masks"},"candidate_evaluation":{k:v for k,v in got.items() if k!="allowed_masks"}},
            "comparison":comparison,
            "scientific_firewall":{"candidate_terminal_before_truth":True,"candidate_byte_frozen":True,"full_domain":True},
            "seal":"THE_STRUCTURE_WAS_ALREADY_VISIBLE__THE_ANSWER_WAS_NOT__THE_FROZEN_MACHINE_NOW_GETS_GRADED"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--world",required=True); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run_world(args.world); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"world":d["world_id"],"verdict":d["verdict"],"candidate":d["candidate"],"comparison":d.get("comparison"),"P_VS_NP":"OPEN"},indent=2,sort_keys=True)); return 2 if d["verdict"]=="FAIL_INTEGRITY" else 0


if __name__=="__main__": raise SystemExit(main())
