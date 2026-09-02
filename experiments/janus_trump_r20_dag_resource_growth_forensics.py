#!/usr/bin/env python3
"""R20 observer-equivalent resource-growth forensics for the frozen R18 DAG.

This is not a stronger candidate.  It replays the exact frozen R18 primitives and
records the partial trajectory that R18 intentionally did not return when a
ResourceLimit interrupted a quantification step.  It never reads semantic truth.
"""
from __future__ import annotations

import argparse
import inspect
import json
import time
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19

WORLD_IDS = tuple(f"R19-W{i:02d}" for i in range(1, 9))
OPEN_IDS = set(WORLD_IDS[4:])
EXPECTED_BLOB = "afa95321ec6edbb33bef222d8ee7234fe631a599"

REFERENCE = {
    "R19-W01": {"final_active_nodes":960,"maximum_nodes_seen_before_gc":78951,"nodes_created_total":580271,"restrict_calls_total":1180827,"hashcons_hits":31067,"gc_calls":49,"gc_removed_total":579313,"elimination_steps":48},
    "R19-W02": {"final_active_nodes":1406,"maximum_nodes_seen_before_gc":51040,"nodes_created_total":411568,"restrict_calls_total":840370,"hashcons_hits":25336,"gc_calls":47,"gc_removed_total":410164,"elimination_steps":46},
    "R19-W03": {"final_active_nodes":2010,"maximum_nodes_seen_before_gc":76421,"nodes_created_total":857791,"restrict_calls_total":1740016,"hashcons_hits":35229,"gc_calls":55,"gc_removed_total":855783,"elimination_steps":54},
    "R19-W04": {"final_active_nodes":187,"maximum_nodes_seen_before_gc":104847,"nodes_created_total":701322,"restrict_calls_total":1421526,"hashcons_hits":9815,"gc_calls":54,"gc_removed_total":701137,"elimination_steps":53},
}


def observer_firewall():
    src = "\n".join(inspect.getsource(f) for f in (forensic_replay, forensic_landmarks, aggregate_directory))
    forbidden = ["Solver(", "solve(", "allowed_masks", "candidate_allowed", "independent_original_allowed", "range(1 <<", "truth_table"]
    hits = [x for x in forbidden if x in src]
    return {"pass": not hits, "forbidden_hits": hits}


def forensic_landmarks(trajectory, initial_active_nodes, total_steps):
    def earliest(pred):
        for row in trajectory:
            if pred(row):
                return {"step":row["step"],"normalized_progress":row["step"]/total_steps,"quantified_var":row["quantified_var"]}
        return None
    multiples = {}
    for m in (10, 50, 100):
        target = initial_active_nodes * m
        hit = earliest(lambda r, t=target: r["after_active_nodes"] >= t)
        multiples[str(m)] = {"target_nodes":target,"first_crossing":hit}
    after_abs = {}
    for t in (10000,50000,100000,250000,500000):
        after_abs[str(t)] = earliest(lambda r, t=t: r["after_active_nodes"] >= t)
    pre_abs = {}
    for t in (10000,50000,100000,250000,500000):
        pre_abs[str(t)] = earliest(lambda r, t=t: r["pre_gc_nodes"] >= t)
    created = {}
    for t in (100000,250000,500000,1000000):
        created[str(t)] = earliest(lambda r, t=t: r["cumulative_nodes_created"] >= t)
    restrict = {}
    for t in (250000,500000,1000000,2000000):
        restrict[str(t)] = earliest(lambda r, t=t: r["cumulative_restrict_calls"] >= t)
    peak_pre = max(trajectory, key=lambda r:r["pre_gc_nodes"], default=None)
    peak_after = max(trajectory, key=lambda r:r["after_active_nodes"], default=None)
    def peak_brief(row, field):
        if row is None: return None
        return {"step":row["step"],"normalized_progress":row["step"]/total_steps,"quantified_var":row["quantified_var"],field:row[field]}
    return {
        "initial_active_node_multiples":multiples,
        "after_active_node_thresholds":after_abs,
        "pre_gc_node_thresholds":pre_abs,
        "cumulative_nodes_created_thresholds":created,
        "cumulative_restrict_call_thresholds":restrict,
        "peak_completed_pre_gc":peak_brief(peak_pre,"pre_gc_nodes"),
        "peak_completed_after_gc":peak_brief(peak_after,"after_active_nodes"),
    }


def forensic_replay(world_id):
    if world_id not in WORLD_IDS:
        raise ValueError(world_id)
    freeze = r19.load_freeze()
    spec = next(w for w in freeze["worlds"] if w["id"] == world_id)
    generated = r19.generate_frozen_world(spec)
    frame, bridge = tuple(generated["frame"]), tuple(generated["bridge"])
    started = time.monotonic()
    budget = r18.Budget(deadline=started + r18.WALL_SECONDS)
    dag = r18.Dag(budget)
    trajectory = []
    current_partial = None
    phase = "COMPILE_CNF"
    initial_active_nodes = None
    order = ()
    root = None
    max_active = len(dag.nodes)
    try:
        root = r18.compile_cnf(dag, frame)
        dag.gc(root)
        initial_active_nodes = len(dag.nodes)
        max_active = max(max_active, initial_active_nodes, dag.max_nodes_seen)
        order = r18.elimination_order(frame, bridge)
        phase = "ELIMINATION"
        for step, var in enumerate(order, start=1):
            before_nodes = len(dag.nodes)
            before_support = dag.support[root].bit_count()
            created_before = budget.nodes_created_total
            calls_before = budget.restrict_calls
            hits_before = dag.hashcons_hits
            current_partial = {
                "step":step,
                "quantified_var":int(var),
                "before_active_nodes":before_nodes,
                "support_variables_before":before_support,
                "nodes_created_before_step":created_before,
                "restrict_calls_before_step":calls_before,
                "hashcons_hits_before_step":hits_before,
            }
            try:
                root, memo_entries = dag.exists(root, var)
            except r18.ResourceLimit as e:
                current_partial.update({
                    "elapsed_seconds_at_open":time.monotonic()-started,
                    "reason":e.reason,
                    "active_nodes_at_open":len(dag.nodes),
                    "partial_nodes_created_step":budget.nodes_created_total-created_before,
                    "partial_restrict_calls_step":budget.restrict_calls-calls_before,
                    "partial_hashcons_hits_step":dag.hashcons_hits-hits_before,
                    "cumulative_nodes_created":budget.nodes_created_total,
                    "cumulative_restrict_calls":budget.restrict_calls,
                    "cumulative_hashcons_hits":dag.hashcons_hits,
                })
                raise
            pre_gc_nodes = len(dag.nodes)
            removed = dag.gc(root)
            after_nodes = len(dag.nodes)
            max_active = max(max_active, pre_gc_nodes, after_nodes, dag.max_nodes_seen)
            trajectory.append({
                "step":step,
                "quantified_var":int(var),
                "elapsed_seconds_after_step":time.monotonic()-started,
                "before_active_nodes":before_nodes,
                "pre_gc_nodes":pre_gc_nodes,
                "after_active_nodes":after_nodes,
                "gc_removed_nodes":removed,
                "support_variables_before":before_support,
                "support_variables_after":dag.support[root].bit_count(),
                "new_nodes_created_step":budget.nodes_created_total-created_before,
                "restrict_calls_step":budget.restrict_calls-calls_before,
                "restrict_memo_entries_step":memo_entries,
                "hashcons_hits_step":dag.hashcons_hits-hits_before,
                "cumulative_nodes_created":budget.nodes_created_total,
                "cumulative_restrict_calls":budget.restrict_calls,
                "cumulative_hashcons_hits":dag.hashcons_hits,
                "cumulative_gc_removed":dag.gc_removed_total,
            })
            current_partial = None
        status = "COMPLETE_INTERFACE_DAG"
        reason = None
    except r18.ResourceLimit as e:
        status = "OPEN_RESOURCE_LIMIT"
        reason = e.reason

    total_steps = len(order)
    completed_steps = len(trajectory)
    landmarks = forensic_landmarks(trajectory, initial_active_nodes or len(dag.nodes), total_steps) if total_steps else {}
    result = {
        "schema":"JANUS/TRUMP/R20/DAG_RESOURCE_GROWTH_FORENSICS/WORLD_RESULT/v1.0",
        "created_date":"2026-09-02",
        "scientific_role":"RESOURCE_FORENSICS_ONLY__NO_SEMANTIC_RESCORING",
        "world_id":world_id,
        "source":{"n":spec["n"],"suite":spec["suite"],"frame_sha256":spec["frame_sha256"],"frame_clauses":len(frame),"internal_variables":spec["internal_variable_count"],"bridge_variables":len(bridge)},
        "frozen_candidate_git_blob_sha":EXPECTED_BLOB,
        "observer_firewall":observer_firewall(),
        "truth_accessed":False,
        "status":status,
        "reason":reason,
        "phase_at_terminal":phase,
        "elapsed_seconds":time.monotonic()-started,
        "initial_active_nodes":initial_active_nodes,
        "total_elimination_steps":total_steps,
        "completed_elimination_steps":completed_steps,
        "normalized_elimination_progress":completed_steps/total_steps if total_steps else 0.0,
        "trajectory":trajectory,
        "partial_open_step":current_partial,
        "final_or_open_counters":{
            "active_nodes":len(dag.nodes),
            "maximum_nodes_seen":max(max_active,dag.max_nodes_seen),
            "nodes_created_total":budget.nodes_created_total,
            "restrict_calls_total":budget.restrict_calls,
            "hashcons_hits":dag.hashcons_hits,
            "gc_calls":dag.gc_calls,
            "gc_removed_total":dag.gc_removed_total,
            "gc_removed_fraction_of_created":dag.gc_removed_total/budget.nodes_created_total if budget.nodes_created_total else 0.0,
        },
        "landmarks":landmarks,
        "P_VS_NP":"OPEN",
    }
    if status == "COMPLETE_INTERFACE_DAG":
        result["final_support_variables"] = dag.support[root].bit_count()
    ref = REFERENCE.get(world_id)
    if ref:
        observed = {
            "final_active_nodes":len(dag.nodes),
            "maximum_nodes_seen_before_gc":max(max_active,dag.max_nodes_seen),
            "nodes_created_total":budget.nodes_created_total,
            "restrict_calls_total":budget.restrict_calls,
            "hashcons_hits":dag.hashcons_hits,
            "gc_calls":dag.gc_calls,
            "gc_removed_total":dag.gc_removed_total,
            "elimination_steps":completed_steps,
        }
        checks = {k:observed[k] == ref[k] for k in ref}
        result["observer_equivalence"] = {"reference":ref,"observed":observed,"checks":checks,"pass":status=="COMPLETE_INTERFACE_DAG" and all(checks.values())}
    else:
        result["observer_equivalence"] = {"not_applicable_open_world":True}
    return result


def aggregate_directory(directory: Path):
    rows=[]
    for p in sorted(directory.glob("*.json")):
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("schema")=="JANUS/TRUMP/R20/DAG_RESOURCE_GROWTH_FORENSICS/WORLD_RESULT/v1.0":
            rows.append(d)
    by={r["world_id"]:r for r in rows}; missing=[w for w in WORLD_IDS if w not in by]; ordered=[by[w] for w in WORLD_IDS if w in by]
    equivalence_ok = not missing and all(by[w].get("observer_equivalence",{}).get("pass") is True for w in WORLD_IDS[:4])
    fw_ok = all(r.get("observer_firewall",{}).get("pass") is True and r.get("truth_accessed") is False for r in ordered)
    open_rows=[by[w] for w in WORLD_IDS[4:] if w in by and by[w]["status"]=="OPEN_RESOURCE_LIMIT"]
    retained=[]; churn=[]; restrict=[]
    for r in open_rows:
        c=r["final_or_open_counters"]
        if c["active_nodes"] >= 500000: retained.append(r["world_id"])
        if c["nodes_created_total"] >= 1000000 and c["active_nodes"] < 500000 and c["gc_removed_fraction_of_created"] > 0.5: churn.append(r["world_id"])
        if c["restrict_calls_total"] >= 2000000 and c["active_nodes"] < 500000: restrict.append(r["world_id"])
    mechanisms={"retained_node_rule_worlds":retained,"temporary_churn_rule_worlds":churn,"restrict_rule_worlds":restrict}
    if not equivalence_ok:
        verdict="R20_FAIL_OBSERVER_EQUIVALENCE__NO_OPEN_WORLD_INTERPRETATION"
    elif not fw_ok or missing:
        verdict="R20_FAIL_INTEGRITY"
    else:
        dominant=[name for name,ws in mechanisms.items() if len(ws)>=3]
        if dominant:
            verdict="R20_DAG_GROWTH_WALL_LOCALIZED"
        elif sum(bool(ws) for ws in mechanisms.values()) >= 2:
            verdict="R20_MIXED_RESOURCE_WALL_LOCALIZED"
        else:
            verdict="R20_NO_SINGLE_WALL_LOCALIZED__FORENSICS_PRESERVED"
    return {
        "schema":"JANUS/TRUMP/R20/DAG_RESOURCE_GROWTH_FORENSICS/AGGREGATE_RESULT/v1.0",
        "created_date":"2026-09-02",
        "verdict":verdict,
        "world_count":len(ordered),
        "missing_worlds":missing,
        "observer_equivalence_pass":equivalence_ok,
        "observer_firewall_pass":fw_ok,
        "open_world_count":len(open_rows),
        "mechanism_coverage":mechanisms,
        "worlds":ordered,
        "interpretation_firewall":"R20 describes where frozen R18 consumes resources. It does not change R18, rescore R19 semantics, or infer an asymptotic complexity class.",
        "P_VS_NP":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--world"); g.add_argument("--aggregate-dir"); ap.add_argument("--output",required=True); args=ap.parse_args()
    if args.world:
        out=forensic_replay(args.world); code=2 if not out["observer_firewall"]["pass"] else 0
        brief={"world_id":out["world_id"],"status":out["status"],"reason":out["reason"],"completed_steps":out["completed_elimination_steps"],"total_steps":out["total_elimination_steps"],"progress":out["normalized_elimination_progress"],"counters":out["final_or_open_counters"],"partial_open_step":out["partial_open_step"],"observer_equivalence":out["observer_equivalence"],"P_VS_NP":"OPEN"}
    else:
        out=aggregate_directory(Path(args.aggregate_dir)); code=2 if out["verdict"] in ("R20_FAIL_OBSERVER_EQUIVALENCE__NO_OPEN_WORLD_INTERPRETATION","R20_FAIL_INTEGRITY") else 0
        brief={"verdict":out["verdict"],"observer_equivalence_pass":out["observer_equivalence_pass"],"open_world_count":out["open_world_count"],"mechanism_coverage":out["mechanism_coverage"],"P_VS_NP":"OPEN"}
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(brief,indent=2,sort_keys=True))
    return code


if __name__=="__main__": raise SystemExit(main())
