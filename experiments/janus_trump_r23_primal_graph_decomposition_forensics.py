#!/usr/bin/env python3
"""R23 truth-blind primal-graph decomposition forensics on frozen R19 worlds.

No SAT solver, assignment enumeration, truth table, candidate compiler, BDD, or
semantic witness is used.  The script regenerates the frozen CNF frames from the
R19 selector lineage, reads only variable co-occurrence structure, and replays two
preregistered internal-variable elimination heuristics while bridge variables are
kept as an interface.
"""
from __future__ import annotations

import argparse
import inspect
import itertools
import json
import random
from collections import Counter
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9
import janus_trump_r19_truth_blind_adversarial_world_selector as selector

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FREEZE_PATH = REPO / "research" / "JANUS_TRUMP_R19_FRESH_UNSEEN_DAG_WORLD_SET_AND_RESOURCE_FREEZE_2026-09-02.json"
WORLD_IDS = tuple(f"R19-W{i:02d}" for i in range(1,9))
PASS_IDS = set(WORLD_IDS[:4])
OPEN_IDS = set(WORLD_IDS[4:])
HEURISTICS = ("MIN_FILL_INTERNAL", "MIN_DEGREE_INTERNAL")


def load_frozen_specs():
    d = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
    assert d["status"] == "FROZEN_BEFORE_R19_CANDIDATE_HARNESS_IMPLEMENTATION_AND_EXECUTION"
    assert tuple(w["id"] for w in d["worlds"]) == WORLD_IDS
    return d["worlds"]


def regenerate_frame(spec):
    derived = selector.derive_spec(spec["suite"], int(spec["n"]), int(spec["rep"]))
    for key in ("seed","branch_value","derivation_string","m","k"):
        if derived[key] != spec[key]:
            raise AssertionError(f"R19 derivation drift {spec['id']}:{key}")
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
    bridge = tuple(int(v) for v in fd["active_bridge_vars"])
    checks = {
        "frame_sha256": fd["frame_sha256"] == spec["frame_sha256"],
        "delta_sha256": fd["delta_sha256"] == spec["delta_sha256"],
        "bridge_vars": list(bridge) == list(spec["bridge_vars"]),
        "frame_clause_count": len(frame) == int(spec["frame_clause_count"]),
        "frame_type": r9.classify_cnf(frame) == spec["frame_type"],
    }
    if not all(checks.values()):
        raise AssertionError(f"frozen frame drift {spec['id']} {checks}")
    return frame, bridge, checks


def primal_graph(frame):
    variables = sorted({abs(int(l)) for c in frame for l in c})
    adj = {v:set() for v in variables}
    for clause in frame:
        vs = sorted({abs(int(l)) for l in clause})
        for u,v in itertools.combinations(vs,2):
            adj[u].add(v); adj[v].add(u)
    return adj


def edge_count(adj):
    return sum(len(n) for n in adj.values()) // 2


def component_profile(adj, bridge):
    bridge = set(int(v) for v in bridge)
    internal = set(adj) - bridge
    seen = set(); rows=[]
    for start in sorted(internal):
        if start in seen: continue
        stack=[start]; comp=set(); seen.add(start)
        while stack:
            v=stack.pop(); comp.add(v)
            for n in adj[v]:
                if n in internal and n not in seen:
                    seen.add(n); stack.append(n)
        boundary = sorted({b for v in comp for b in adj[v] if b in bridge})
        rows.append({
            "internal_variables": sorted(comp),
            "internal_size": len(comp),
            "bridge_boundary": boundary,
            "bridge_boundary_size": len(boundary),
        })
    rows.sort(key=lambda r:(-r["internal_size"],-r["bridge_boundary_size"],r["internal_variables"]))
    return rows


def missing_fill_edges(adj, neighbors):
    ns = sorted(neighbors); missing=[]
    for u,v in itertools.combinations(ns,2):
        if v not in adj[u]: missing.append((u,v))
    return missing


def eliminate_internal(adj0, frame, bridge, heuristic_id):
    if heuristic_id not in HEURISTICS: raise ValueError(heuristic_id)
    adj = {v:set(ns) for v,ns in adj0.items()}
    bridge = set(int(v) for v in bridge)
    remaining = set(adj)-bridge
    occurrence = Counter(abs(int(l)) for c in frame for l in c)
    trajectory=[]; total_fill=0; max_width=-1; peak=None; order=[]
    max_bridge_neighbors=0; max_internal_neighbors=0
    while remaining:
        candidates=[]
        for v in remaining:
            ns=set(adj[v]); fill=len(missing_fill_edges(adj,ns)); degree=len(ns)
            if heuristic_id=="MIN_FILL_INTERNAL":
                key=(fill,degree,-occurrence[v],v)
            else:
                key=(degree,fill,-occurrence[v],v)
            candidates.append((key,v,fill,degree))
        _,v,fill_count,degree=min(candidates,key=lambda x:x[0])
        ns=set(adj[v]); missing=missing_fill_edges(adj,ns)
        bridge_neighbors=len(ns & bridge); internal_neighbors=len(ns & remaining - {v})
        row={
            "step":len(order)+1,
            "variable":v,
            "current_degree":degree,
            "bag_size":degree+1,
            "fill_edges_added":len(missing),
            "bridge_neighbors":bridge_neighbors,
            "internal_neighbors":internal_neighbors,
            "remaining_internal_before":len(remaining),
        }
        trajectory.append(row); order.append(v); total_fill += len(missing)
        max_bridge_neighbors=max(max_bridge_neighbors,bridge_neighbors)
        max_internal_neighbors=max(max_internal_neighbors,internal_neighbors)
        if degree > max_width:
            max_width=degree; peak=dict(row)
        for a,b in missing:
            adj[a].add(b); adj[b].add(a)
        for n in list(ns):
            adj[n].discard(v)
        del adj[v]; remaining.remove(v)
    bridge_list=sorted(bridge)
    final_bridge_edges=sum(1 for u,v in itertools.combinations(bridge_list,2) if v in adj.get(u,set()))
    possible=len(bridge_list)*(len(bridge_list)-1)//2
    return {
        "heuristic_id":heuristic_id,
        "elimination_order":order,
        "induced_width_max_neighbor_count":max_width,
        "max_bag_size":max_width+1 if max_width>=0 else 0,
        "total_fill_edges_added":total_fill,
        "max_bridge_neighbors_in_any_bag":max_bridge_neighbors,
        "max_internal_neighbors_in_any_bag":max_internal_neighbors,
        "peak_bag_step":peak,
        "peak_bag_normalized_position":(peak["step"]/len(order)) if peak and order else None,
        "final_bridge_edge_count":final_bridge_edges,
        "final_bridge_possible_edge_count":possible,
        "final_bridge_is_clique":final_bridge_edges==possible,
        "trajectory":trajectory,
    }


def analyze_world(spec):
    frame,bridge,checks=regenerate_frame(spec)
    adj=primal_graph(frame); components=component_profile(adj,bridge)
    heuristics={h:eliminate_internal(adj,frame,bridge,h) for h in HEURISTICS}
    widths=[heuristics[h]["induced_width_max_neighbor_count"] for h in HEURISTICS]
    return {
        "world_id":spec["id"],
        "R19_group":"PASS_EXACT" if spec["id"] in PASS_IDS else "OPEN_CANDIDATE_RESOURCE",
        "suite":spec["suite"],
        "n":spec["n"],
        "frame_sha256":spec["frame_sha256"],
        "frame_variables":len(adj),
        "frame_clauses":len(frame),
        "internal_variables":len(adj)-len(bridge),
        "bridge_variables":len(bridge),
        "initial_primal_edges":edge_count(adj),
        "frame_regeneration_checks":checks,
        "internal_component_count_after_bridge_removal":len(components),
        "largest_internal_component_size":max((r["internal_size"] for r in components),default=0),
        "largest_component_bridge_boundary_size":max((r["bridge_boundary_size"] for r in components),default=0),
        "component_profile":components,
        "heuristics":heuristics,
        "minimum_frozen_heuristic_induced_width":min(widths),
        "maximum_frozen_heuristic_induced_width":max(widths),
        "local_table_landmarks":{
            "minimum_width_le_16":min(widths)<=16,
            "minimum_width_le_20":min(widths)<=20,
            "states_at_minimum_width":1 << min(widths) if min(widths) < 63 else None,
        },
    }


def structural_firewall():
    src="\n".join(inspect.getsource(f) for f in (regenerate_frame,primal_graph,component_profile,missing_fill_edges,eliminate_internal,analyze_world))
    forbidden=["Solver(","solve(","allowed_masks","truth_table","candidate_compile","candidate_allowed","range(1 <<","ROBDD","Dag("]
    hits=[x for x in forbidden if x in src]
    return {"pass":not hits,"forbidden_hits":hits}


def aggregate():
    specs=load_frozen_specs(); worlds=[analyze_world(s) for s in specs]
    by={w["world_id"]:w for w in worlds}; w05=by["R19-W05"]
    component_promising=(w05["internal_component_count_after_bridge_removal"]>=2 and w05["largest_internal_component_size"]<=32 and w05["largest_component_bridge_boundary_size"]<=16)
    low_width=(not component_promising and w05["minimum_frozen_heuristic_induced_width"]<=16)
    still_wide=(not component_promising and not low_width and w05["minimum_frozen_heuristic_induced_width"]>20)
    if component_promising:
        verdict="R23_COMPONENT_FACTORIZATION_STRUCTURALLY_PROMISING"
    elif low_width:
        verdict="R23_LOW_WIDTH_DECOMPOSITION_STRUCTURALLY_PROMISING"
    elif still_wide:
        verdict="R23_DECOMPOSITION_HEURISTICS_STILL_WIDE__PRESERVE_STRUCTURE"
    else:
        verdict="R23_MIXED_STRUCTURAL_SIGNAL__NO_SINGLE_DECOMPOSITION_STORY"
    def group_summary(ids):
        rows=[by[x] for x in ids]
        mins=[r["minimum_frozen_heuristic_induced_width"] for r in rows]
        comps=[r["largest_internal_component_size"] for r in rows]
        bounds=[r["largest_component_bridge_boundary_size"] for r in rows]
        return {
            "worlds":list(ids),
            "minimum_heuristic_widths":mins,
            "minimum_heuristic_width_range":[min(mins),max(mins)],
            "largest_internal_component_sizes":comps,
            "largest_internal_component_size_range":[min(comps),max(comps)],
            "largest_component_bridge_boundaries":bounds,
            "largest_component_bridge_boundary_range":[min(bounds),max(bounds)],
        }
    fw=structural_firewall()
    if not fw["pass"] or not all(all(w["frame_regeneration_checks"].values()) for w in worlds): verdict="R23_FAIL_INTEGRITY"
    return {
        "schema":"JANUS/TRUMP/R23/PRIMAL_GRAPH_DECOMPOSITION_FORENSICS/AGGREGATE_RESULT/v1.0",
        "created_date":"2026-09-02",
        "scientific_role":"STRUCTURAL_DECOMPOSITION_FORENSICS_ONLY__NO_SEMANTIC_TRUTH__NO_CANDIDATE_EXECUTION",
        "verdict":verdict,
        "structural_firewall":fw,
        "truth_accessed":False,
        "semantic_candidate_ran":False,
        "world_count":len(worlds),
        "worlds":worlds,
        "R19_PASS_group":group_summary(WORLD_IDS[:4]),
        "R19_OPEN_group":group_summary(WORLD_IDS[4:]),
        "R19_W05_verdict_inputs":{
            "component_promising":component_promising,
            "low_width_promising":low_width,
            "still_wide":still_wide,
            "internal_component_count":w05["internal_component_count_after_bridge_removal"],
            "largest_internal_component_size":w05["largest_internal_component_size"],
            "largest_component_bridge_boundary_size":w05["largest_component_bridge_boundary_size"],
            "minimum_frozen_heuristic_induced_width":w05["minimum_frozen_heuristic_induced_width"],
        },
        "interpretation_firewall":"Heuristic induced widths are upper bounds for those frozen orders only, not exact treewidth or lower bounds on all decompositions.",
        "claim_ceiling":"Graph-structural evidence on eight finite frozen worlds only. No exact treewidth theorem, semantic holdout claim, SAT-in-P, P=NP, or P!=NP conclusion.",
        "seal":"R23_READ_EDGES_NOT_ANSWERS",
        "P_VS_NP":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    out=aggregate(); Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    brief={
        "verdict":out["verdict"],
        "R19_W05_verdict_inputs":out["R19_W05_verdict_inputs"],
        "PASS_widths":out["R19_PASS_group"]["minimum_heuristic_widths"],
        "OPEN_widths":out["R19_OPEN_group"]["minimum_heuristic_widths"],
        "firewall":out["structural_firewall"],
        "P_VS_NP":"OPEN",
    }
    print(json.dumps(brief,indent=2,sort_keys=True))
    return 2 if out["verdict"]=="R23_FAIL_INTEGRITY" else 0

if __name__=="__main__": raise SystemExit(main())
