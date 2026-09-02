#!/usr/bin/env python3
"""R24 truth-blind structural cutset-width profile on exposed R19-W05.

A cutset vertex is deleted only from the primal graph.  No Boolean value is
assigned, no clause is semantically simplified, and no SAT/truth/candidate code
is executed.  At each round the preregistered greedy lookahead evaluates every
remaining internal vertex with the exact R23 MIN_FILL_INTERNAL and
MIN_DEGREE_INTERNAL graph-elimination routines and freezes the lexicographic best
structural deletion.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
from collections import Counter
from pathlib import Path

import janus_trump_r23_primal_graph_decomposition_forensics as r23

WORLD_ID = "R19-W05"
EXPECTED_FRAME_SHA = "cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384"
MAX_CUTSET = 8
HEURISTICS = ("MIN_FILL_INTERNAL", "MIN_DEGREE_INTERNAL")


def delete_vertex(adj, vertex):
    vertex = int(vertex)
    if vertex not in adj:
        raise ValueError(vertex)
    out = {int(v): set(ns) for v, ns in adj.items() if int(v) != vertex}
    for ns in out.values():
        ns.discard(vertex)
    return out


def structural_profile(adj, frame, bridge, cutset_prefix):
    components = r23.component_profile(adj, bridge)
    hrs = {h: r23.eliminate_internal(adj, frame, bridge, h) for h in HEURISTICS}
    widths = {h: int(hrs[h]["induced_width_max_neighbor_count"]) for h in HEURISTICS}
    fills = {h: int(hrs[h]["total_fill_edges_added"]) for h in HEURISTICS}
    return {
        "cutset_size": len(cutset_prefix),
        "selected_cutset_prefix": list(cutset_prefix),
        "remaining_internal_variables": len(set(adj) - set(bridge)),
        "internal_component_count_after_cutset_and_bridge_removal": len(components),
        "largest_internal_component_size": max((x["internal_size"] for x in components), default=0),
        "largest_component_bridge_boundary_size": max((x["bridge_boundary_size"] for x in components), default=0),
        "heuristic_widths": widths,
        "heuristic_fill_edges": fills,
        "minimum_frozen_heuristic_width": min(widths.values()),
        "maximum_frozen_heuristic_width": max(widths.values()),
        "final_bridge_is_clique": {h: bool(hrs[h]["final_bridge_is_clique"]) for h in HEURISTICS},
        "peak_bag_normalized_position": {h: hrs[h]["peak_bag_normalized_position"] for h in HEURISTICS},
    }


def candidate_deletion_score(adj, frame, bridge, occurrence, vertex):
    reduced = delete_vertex(adj, vertex)
    hrs = {h: r23.eliminate_internal(reduced, frame, bridge, h) for h in HEURISTICS}
    widths = {h: int(hrs[h]["induced_width_max_neighbor_count"]) for h in HEURISTICS}
    fills = {h: int(hrs[h]["total_fill_edges_added"]) for h in HEURISTICS}
    degree = len(adj[int(vertex)])
    score = (
        min(widths.values()),
        max(widths.values()),
        min(fills.values()),
        -degree,
        -int(occurrence[int(vertex)]),
        int(vertex),
    )
    return {
        "variable": int(vertex),
        "score": list(score),
        "minimum_width_after_deletion": min(widths.values()),
        "maximum_width_after_deletion": max(widths.values()),
        "MIN_FILL_width": widths["MIN_FILL_INTERNAL"],
        "MIN_DEGREE_width": widths["MIN_DEGREE_INTERNAL"],
        "minimum_fill_edges_after_deletion": min(fills.values()),
        "current_degree": degree,
        "original_literal_occurrence": int(occurrence[int(vertex)]),
    }


def score_table_hash(rows):
    canonical = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def run():
    specs = r23.load_frozen_specs()
    spec = next(w for w in specs if w["id"] == WORLD_ID)
    frame, bridge, checks = r23.regenerate_frame(spec)
    if spec["frame_sha256"] != EXPECTED_FRAME_SHA:
        raise AssertionError("W05 frame hash drift")
    adj = r23.primal_graph(frame)
    occurrence = Counter(abs(int(l)) for clause in frame for l in clause)
    bridge_set = set(int(v) for v in bridge)
    cutset = []
    profiles = []
    rounds = []

    baseline = structural_profile(adj, frame, bridge, cutset)
    baseline["width_drop_from_k0"] = 0
    profiles.append(baseline)
    if baseline["minimum_frozen_heuristic_width"] != 48:
        raise AssertionError("R23 W05 baseline width not reproduced")

    for round_index in range(1, MAX_CUTSET + 1):
        eligible = sorted(set(adj) - bridge_set)
        if not eligible:
            break
        scored = [candidate_deletion_score(adj, frame, bridge, occurrence, v) for v in eligible]
        scored.sort(key=lambda row: tuple(row["score"]))
        chosen = scored[0]
        runner_up = scored[1] if len(scored) > 1 else None
        rounds.append({
            "round": round_index,
            "eligible_count": len(eligible),
            "selected_variable": chosen["variable"],
            "selected_score": chosen,
            "runner_up_score": runner_up,
            "candidate_score_table_sha256": score_table_hash(scored),
            "candidate_scores": scored,
        })
        cutset.append(chosen["variable"])
        adj = delete_vertex(adj, chosen["variable"])
        p = structural_profile(adj, frame, bridge, cutset)
        p["width_drop_from_k0"] = baseline["minimum_frozen_heuristic_width"] - p["minimum_frozen_heuristic_width"]
        profiles.append(p)

    final = profiles[-1]
    small = any(p["minimum_frozen_heuristic_width"] <= 20 for p in profiles if p["cutset_size"] <= 8)
    drop8 = int(final["width_drop_from_k0"])
    if small:
        verdict = "R24_SMALL_STRUCTURAL_CUTSET_PROMISING"
    elif drop8 >= 16:
        verdict = "R24_CONCENTRATED_STRUCTURAL_CORE_SIGNAL"
    elif drop8 <= 8:
        verdict = "R24_DISTRIBUTED_WIDTH_SIGNAL"
    else:
        verdict = "R24_MIXED_CUTSET_WIDTH_SIGNAL"

    fw = structural_firewall()
    if not fw["pass"] or not all(checks.values()) or len(profiles) != MAX_CUTSET + 1:
        verdict = "R24_FAIL_INTEGRITY"

    return {
        "schema": "JANUS/TRUMP/R24/TRUTH_BLIND_STRUCTURAL_CUTSET_WIDTH_PROFILE/RESULT/v1.0",
        "created_date": "2026-09-02",
        "scientific_role": "EXPOSED_STRUCTURAL_CUTSET_FORENSICS__NO_SEMANTIC_TRUTH__NO_BOOLEAN_BRANCHING",
        "world": {
            "id": WORLD_ID,
            "frame_sha256": spec["frame_sha256"],
            "frame_clauses": len(frame),
            "frame_variables": len(r23.primal_graph(frame)),
            "internal_variables": spec["internal_variable_count"],
            "bridge_variables": len(bridge),
        },
        "frame_regeneration_checks": checks,
        "structural_firewall": fw,
        "truth_accessed": False,
        "cutset_values_assigned": False,
        "semantic_candidate_ran": False,
        "verdict": verdict,
        "baseline_minimum_width": baseline["minimum_frozen_heuristic_width"],
        "selected_cutset": cutset,
        "profiles": profiles,
        "selection_rounds": rounds,
        "final_width_drop_at_k8": drop8,
        "small_cutset_width20_reached": small,
        "interpretation_firewall": "Graph vertex deletion only. No cutset assignment enumeration or semantic CNF simplification occurred. Widths are upper bounds for the frozen R23 heuristics only.",
        "claim_ceiling": "Exposed structural sensitivity on W05 only. No semantic verdict, exact treewidth theorem, polynomial scaling, SAT-in-P, P=NP, or P!=NP conclusion.",
        "seal": "R24_REMOVED_GRAPH_VERTICES_WITHOUT_ASSIGNING_FORMULA_BITS",
        "P_VS_NP": "OPEN",
    }


def structural_firewall():
    src = "\n".join(inspect.getsource(f) for f in (delete_vertex, structural_profile, candidate_deletion_score, run))
    forbidden = [
        "Solver(", "solve(", "allowed_masks", "truth_table", "candidate_compile",
        "candidate_allowed", "range(1 <<", "assumptions_for_mask", "exists_var(",
    ]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output", required=True); args = ap.parse_args()
    out = run()
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": out["verdict"],
        "selected_cutset": out["selected_cutset"],
        "width_profile": [{"k": p["cutset_size"], "width": p["minimum_frozen_heuristic_width"], "drop": p["width_drop_from_k0"], "components": p["internal_component_count_after_cutset_and_bridge_removal"], "largest_component": p["largest_internal_component_size"]} for p in out["profiles"]],
        "firewall": out["structural_firewall"],
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 2 if out["verdict"] == "R24_FAIL_INTEGRITY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
