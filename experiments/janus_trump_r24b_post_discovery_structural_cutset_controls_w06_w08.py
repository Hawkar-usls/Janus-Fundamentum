#!/usr/bin/env python3
"""R24B structural controls: replay frozen R24 graph rule on R19-W06..W08.

No Boolean values, SAT solver, semantic verifier, or candidate representation are
used. The R24 helper implementation is imported unchanged; this harness only
changes the frozen R19 frame supplied to those graph-only functions.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r23_primal_graph_decomposition_forensics as r23
import janus_trump_r24_truth_blind_structural_cutset_width_profile as r24

WORLD_IDS = ("R19-W06","R19-W07","R19-W08")
EXPECTED = {
    "R19-W06": {"frame_sha256":"27a467b3da4b6797a68ef6805fae60121f017c7353937910590fd75a0c14581b","baseline_width":48},
    "R19-W07": {"frame_sha256":"01340774703f14342287dae2b8ffa84cf0549664ad8339d85e74e09d12b2a742","baseline_width":53},
    "R19-W08": {"frame_sha256":"dab5477c7699d3051d46e5228754ffdf7b2673cee58491bc01db64e3e0e90eb0","baseline_width":54},
}
PASS_BAND_MAX = 43


def run_world(world_id):
    if world_id not in WORLD_IDS: raise ValueError(world_id)
    spec = next(w for w in r23.load_frozen_specs() if w["id"] == world_id)
    frame, bridge, checks = r23.regenerate_frame(spec)
    exp = EXPECTED[world_id]
    if spec["frame_sha256"] != exp["frame_sha256"]: raise AssertionError("frame drift")
    adj = r23.primal_graph(frame)
    bridge_set = set(int(v) for v in bridge)
    occurrence = Counter(abs(int(l)) for c in frame for l in c)
    cutset=[]; profiles=[]; rounds=[]
    baseline=r24.structural_profile(adj,frame,bridge,cutset); baseline["width_drop_from_k0"]=0; profiles.append(baseline)
    if baseline["minimum_frozen_heuristic_width"] != exp["baseline_width"]:
        raise AssertionError(f"R23 baseline width drift {world_id}")
    for round_index in range(1,9):
        eligible=sorted(set(adj)-bridge_set)
        scored=[r24.candidate_deletion_score(adj,frame,bridge,occurrence,v) for v in eligible]
        scored.sort(key=lambda row:tuple(row["score"]))
        chosen=scored[0]
        rounds.append({"round":round_index,"eligible_count":len(eligible),"selected_variable":chosen["variable"],"selected_score":chosen,"candidate_score_table_sha256":r24.score_table_hash(scored)})
        cutset.append(chosen["variable"]); adj=r24.delete_vertex(adj,chosen["variable"])
        p=r24.structural_profile(adj,frame,bridge,cutset); p["width_drop_from_k0"]=baseline["minimum_frozen_heuristic_width"]-p["minimum_frozen_heuristic_width"]; profiles.append(p)
    final=profiles[-1]; enters=final["minimum_frozen_heuristic_width"] <= PASS_BAND_MAX
    return {
        "schema":"JANUS/TRUMP/R24B/POST_DISCOVERY_STRUCTURAL_CUTSET_CONTROLS_W06_W08/CONTROL_RESULT/v1.0",
        "created_date":"2026-09-02",
        "scientific_role":"POST_DISCOVERY_STRUCTURAL_CONTROL__NO_SEMANTIC_TRUTH__NOT_UNSEEN",
        "world_id":world_id,
        "frame_sha256":spec["frame_sha256"],
        "frame_regeneration_checks":checks,
        "frozen_R24_algorithm_blob":"2478c671dd3b3f87477de679af832e0ea9c88f8d",
        "truth_accessed":False,
        "cutset_values_assigned":False,
        "semantic_candidate_ran":False,
        "baseline_width":baseline["minimum_frozen_heuristic_width"],
        "selected_cutset":cutset,
        "profiles":profiles,
        "selection_rounds":rounds,
        "final_k8_width":final["minimum_frozen_heuristic_width"],
        "final_k8_drop":final["width_drop_from_k0"],
        "enters_R23_PASS_band_at_k8":enters,
        "small_cutset_width20_reached":any(p["minimum_frozen_heuristic_width"]<=20 for p in profiles),
        "verdict":"R24B_CONTROL_ENTERS_R23_PASS_BAND_AT_K8" if enters else "R24B_CONTROL_STAYS_ABOVE_R23_PASS_BAND_AT_K8",
        "claim_ceiling":"Graph-only post-discovery control; no semantic or complexity-class authority.",
        "P_VS_NP":"OPEN",
    }


def aggregate_directory(directory):
    rows=[]
    for p in sorted(Path(directory).glob("*.json")):
        d=json.loads(p.read_text())
        if d.get("schema")=="JANUS/TRUMP/R24B/POST_DISCOVERY_STRUCTURAL_CUTSET_CONTROLS_W06_W08/CONTROL_RESULT/v1.0": rows.append(d)
    by={r["world_id"]:r for r in rows}; missing=[w for w in WORLD_IDS if w not in by]; ordered=[by[w] for w in WORLD_IDS if w in by]
    count=sum(bool(r["enters_R23_PASS_band_at_k8"]) for r in ordered)
    integrity=(not missing and len(ordered)==3 and all(all(r["frame_regeneration_checks"].values()) for r in ordered) and all(r["truth_accessed"] is False for r in ordered))
    if not integrity: verdict="R24B_FAIL_INTEGRITY"
    elif count==3: verdict="R24B_3_OF_3_OPEN_STRUCTURAL_CONTROLS_ENTER_R23_PASS_BAND_AT_K8"
    elif count>0: verdict="R24B_PARTIAL_OPEN_STRUCTURAL_CONTROLS_ENTER_R23_PASS_BAND_AT_K8"
    else: verdict="R24B_NO_OPEN_STRUCTURAL_CONTROL_ENTERS_R23_PASS_BAND_AT_K8"
    return {
        "schema":"JANUS/TRUMP/R24B/POST_DISCOVERY_STRUCTURAL_CUTSET_CONTROLS_W06_W08/AGGREGATE_RESULT/v1.0",
        "created_date":"2026-09-02",
        "scientific_role":"POST_DISCOVERY_STRUCTURAL_CONTROLS__NO_SEMANTIC_TRUTH__NOT_UNSEEN",
        "verdict":verdict,
        "control_count":len(ordered),
        "missing_worlds":missing,
        "enter_pass_band_count":count,
        "frozen_R24_algorithm_blob":"2478c671dd3b3f87477de679af832e0ea9c88f8d",
        "truth_accessed":False,
        "controls":ordered,
        "claim_ceiling":"Post-discovery structural controls only; no semantic, treewidth, SAT-in-P, P=NP, or P!=NP conclusion.",
        "P_VS_NP":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--world"); g.add_argument("--aggregate-dir"); ap.add_argument("--output",required=True); args=ap.parse_args()
    out=run_world(args.world) if args.world else aggregate_directory(args.aggregate_dir)
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if args.world:
        brief={"world":out["world_id"],"verdict":out["verdict"],"cutset":out["selected_cutset"],"profile":[p["minimum_frozen_heuristic_width"] for p in out["profiles"]],"P_VS_NP":"OPEN"}
    else:
        brief={"verdict":out["verdict"],"enter_pass_band_count":out["enter_pass_band_count"],"controls":[{"world":r["world_id"],"final":r["final_k8_width"],"drop":r["final_k8_drop"],"cutset":r["selected_cutset"]} for r in out["controls"]],"P_VS_NP":"OPEN"}
    print(json.dumps(brief,indent=2,sort_keys=True)); return 2 if out["verdict"]=="R24B_FAIL_INTEGRITY" else 0

if __name__=="__main__": raise SystemExit(main())
