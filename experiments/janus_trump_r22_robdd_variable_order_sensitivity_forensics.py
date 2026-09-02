#!/usr/bin/env python3
"""R22 exposed build-only ROBDD variable-order sensitivity forensics.

R22 imports the sealed R21 ROBDD machine and changes only the preregistered total
variable order.  It never quantifies variables and never imports/calls semantic
truth.  R19-W05 remains exposed discovery material, not unseen evidence.
"""
from __future__ import annotations

import argparse
import inspect
import json
import time
from collections import Counter
from pathlib import Path

import janus_trump_r19_fresh_unseen_dag_holdout as r19
import janus_trump_r21_canonical_robdd_function_dag_discovery as r21

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PREREG_PATH = REPO / "research" / "JANUS_TRUMP_R22_ROBDD_VARIABLE_ORDER_SENSITIVITY_FORENSICS_PREREGISTRATION_2026-09-02.json"
WORLD_ID = "R19-W05"
EXPECTED_FRAME_SHA = "cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384"
ORDER_IDS = (
    "R21_INTERNAL_FIRST_OCCURRENCE",
    "GLOBAL_OCCURRENCE",
    "GLOBAL_OCCURRENCE_REVERSED",
    "BRIDGE_FIRST_OCCURRENCE",
    "FREQUENCY_DESCENDING",
    "FREQUENCY_ASCENDING",
    "VARIABLE_ASCENDING",
    "VARIABLE_DESCENDING",
)


def load_prereg():
    d=json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    assert d["status"]=="FROZEN_BEFORE_R22_IMPLEMENTATION_AND_EXECUTION"
    assert d["parent_R21_result_summary_commit"]=="1ff91dbd10d2efb5672f52b7bbc0f4e689716a7c"
    assert tuple(x["id"] for x in d["frozen_order_family"])==ORDER_IDS
    assert d["truth_firewall"]["semantic_verifier_forbidden"] is True
    return d


def frame_variables(frame):
    return tuple(sorted({abs(int(l)) for c in frame for l in c}))


def normalize_order(seq, variables):
    allowed=set(variables); out=[]; seen=set()
    for raw in seq:
        v=int(raw)
        if v in allowed and v not in seen:
            out.append(v); seen.add(v)
    out.extend(v for v in variables if v not in seen)
    if len(out)!=len(variables) or set(out)!=allowed:
        raise r21.IntegrityFailure("ORDER_NORMALIZATION_COVERAGE_FAIL")
    return tuple(out)


def frozen_orders(frame, bridge):
    variables=frame_variables(frame)
    global_raw,_=r21.r18.direct.occurrence_order(frame)
    global_occ=normalize_order(global_raw,variables)
    bridge_set=set(int(v) for v in bridge)
    internal=tuple(r21.r18.elimination_order(frame,bridge))
    frequency=Counter(abs(int(l)) for c in frame for l in c)
    orders={
        "R21_INTERNAL_FIRST_OCCURRENCE": tuple(r21.frozen_variable_order(frame,bridge)),
        "GLOBAL_OCCURRENCE": global_occ,
        "GLOBAL_OCCURRENCE_REVERSED": tuple(reversed(global_occ)),
        "BRIDGE_FIRST_OCCURRENCE": tuple(v for v in global_occ if v in bridge_set)+internal,
        "FREQUENCY_DESCENDING": tuple(sorted(variables,key=lambda v:(-frequency[v],v))),
        "FREQUENCY_ASCENDING": tuple(sorted(variables,key=lambda v:(frequency[v],v))),
        "VARIABLE_ASCENDING": variables,
        "VARIABLE_DESCENDING": tuple(reversed(variables)),
    }
    for key,order in orders.items():
        if len(order)!=len(variables) or set(order)!=set(variables):
            raise r21.IntegrityFailure(f"ORDER_COVERAGE_FAIL:{key}")
    return orders


def build_only(frame, order):
    started=time.monotonic(); budget=r21.Budget(deadline=started+r21.WALL_SECONDS); bdd=r21.ROBDD(order,budget)
    root=1; trajectory=[]
    try:
        for idx,clause in enumerate(frame,start=1):
            before=len(bdd.nodes); created_before=budget.nodes_created_total; calls_before=budget.apply_calls; hits_before=bdd.unique_hits
            clause_root=0
            for lit in clause:
                lit_root=bdd.literal(lit)
                clause_root,_=bdd.apply("OR",clause_root,lit_root)
            root,_=bdd.apply("AND",root,clause_root)
            pre_gc=len(bdd.nodes); removed=bdd.gc(root); after=len(bdd.nodes)
            trajectory.append({
                "clause_index":idx,
                "elapsed_seconds":time.monotonic()-started,
                "before_active_nodes":before,
                "pre_gc_nodes":pre_gc,
                "after_active_nodes":after,
                "gc_removed_nodes":removed,
                "new_nodes_created":budget.nodes_created_total-created_before,
                "apply_calls":budget.apply_calls-calls_before,
                "unique_hits":bdd.unique_hits-hits_before,
                "cumulative_nodes_created":budget.nodes_created_total,
                "cumulative_apply_calls":budget.apply_calls,
                "cumulative_unique_hits":bdd.unique_hits,
            })
        return {
            "status":"COMPLETE_BUILD_ROBDD",
            "reason":None,
            "phase":"BUILD_CNF",
            "elapsed_seconds":time.monotonic()-started,
            "completed_clause_steps":len(trajectory),
            "final_active_nodes":len(bdd.nodes),
            "active_nodes_at_terminal_or_open":len(bdd.nodes),
            "maximum_nodes_seen":bdd.max_nodes_seen,
            "nodes_created_total":budget.nodes_created_total,
            "apply_calls_total":budget.apply_calls,
            "unique_table_hits":bdd.unique_hits,
            "gc_calls":bdd.gc_calls,
            "gc_removed_total":bdd.gc_removed_total,
            "root":root,
            "trajectory":trajectory,
        }
    except r21.ResourceLimit as e:
        return {
            "status":"OPEN_RESOURCE_LIMIT",
            "reason":e.reason,
            "phase":"BUILD_CNF",
            "elapsed_seconds":time.monotonic()-started,
            "completed_clause_steps":len(trajectory),
            "final_active_nodes":None,
            "active_nodes_at_terminal_or_open":len(bdd.nodes),
            "maximum_nodes_seen":bdd.max_nodes_seen,
            "nodes_created_total":budget.nodes_created_total,
            "apply_calls_total":budget.apply_calls,
            "unique_table_hits":bdd.unique_hits,
            "gc_calls":bdd.gc_calls,
            "gc_removed_total":bdd.gc_removed_total,
            "trajectory":trajectory,
        }
    except r21.IntegrityFailure as e:
        return {"status":"FAIL_INTEGRITY","reason":str(e),"phase":"BUILD_CNF","trajectory":trajectory}


def forensic_firewall():
    src="\n".join(inspect.getsource(x) for x in (frame_variables,normalize_order,frozen_orders,build_only,run_order,aggregate_directory))
    forbidden=["Solver(","solve(","range(1 <<","allowed_masks","truth_table","candidate_allowed","independent_original_allowed","exists_var(","dpll(","resolve_on("]
    hits=[x for x in forbidden if x in src]
    return {"pass":not hits,"forbidden_hits":hits}


def landmarks(result, total_clauses):
    traj=list(result.get("trajectory",[]))
    crossings={}
    for threshold in (10000,100000,500000):
        hit=next((r for r in traj if int(r["after_active_nodes"])>=threshold),None)
        crossings[str(threshold)]=None if hit is None else {"clause_index":hit["clause_index"],"completion_fraction":hit["clause_index"]/total_clauses,"after_active_nodes":hit["after_active_nodes"]}
    return {
        "completion_fraction":int(result.get("completed_clause_steps",0))/total_clauses,
        "first_live_node_crossings":crossings,
        "last_completed_clause_trajectory_row":traj[-1] if traj else None,
    }


def r21_equivalence(result, prereg):
    ref=prereg["R21_observer_equivalence_gate"]["reference"]
    got={
        "order_id":"R21_INTERNAL_FIRST_OCCURRENCE",
        "status":result.get("status"),
        "reason":result.get("reason"),
        "phase":result.get("phase"),
        "completed_clause_steps":result.get("completed_clause_steps"),
        "active_nodes_at_open":result.get("active_nodes_at_terminal_or_open"),
        "maximum_nodes_seen":result.get("maximum_nodes_seen"),
        "nodes_created_total":result.get("nodes_created_total"),
        "apply_calls_total":result.get("apply_calls_total"),
        "unique_table_hits":result.get("unique_table_hits"),
        "gc_calls":result.get("gc_calls"),
        "gc_removed_total":result.get("gc_removed_total"),
        "quantify_calls_total":0,
    }
    checks={k:got.get(k)==v for k,v in ref.items()}
    return {"pass":all(checks.values()),"checks":checks,"expected":ref,"observed":got}


def run_order(order_id):
    prereg=load_prereg(); freeze=r19.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r19.generate_frozen_world(spec)
    if spec["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("R19-W05 frame drift")
    frame=tuple(world["frame"]); bridge=tuple(world["bridge"]); orders=frozen_orders(frame,bridge)
    if order_id not in orders: raise ValueError(order_id)
    fw=forensic_firewall()
    if not fw["pass"]:
        return {"schema":"JANUS/TRUMP/R22/ROBDD_VARIABLE_ORDER_SENSITIVITY_FORENSICS/ORDER_RESULT/v1.0","order_id":order_id,"verdict":"R22_FAIL_INTEGRITY","firewall":fw,"truth_accessed":False,"P_VS_NP":"OPEN"}
    result=build_only(frame,orders[order_id]); total=len(frame); marks=landmarks(result,total)
    summary={k:v for k,v in result.items() if k not in ("root","trajectory")}
    base={
        "schema":"JANUS/TRUMP/R22/ROBDD_VARIABLE_ORDER_SENSITIVITY_FORENSICS/ORDER_RESULT/v1.0",
        "created_date":"2026-09-02",
        "scientific_role":"EXPOSED_BUILD_PHASE_ORDER_SENSITIVITY_FORENSICS__NO_SEMANTIC_TRUTH",
        "world_id":WORLD_ID,
        "frame_sha256":EXPECTED_FRAME_SHA,
        "order_id":order_id,
        "variable_order":list(orders[order_id]),
        "firewall":fw,
        "result":summary,
        "landmarks":marks,
        "build_survivor":result.get("status")=="COMPLETE_BUILD_ROBDD" and result.get("completed_clause_steps")==total,
        "truth_accessed":False,
        "P_VS_NP":"OPEN",
    }
    if order_id=="R21_INTERNAL_FIRST_OCCURRENCE":
        equiv=r21_equivalence(result,prereg)
        return {**base,"verdict":"R22_R21_ORDER_OBSERVER_EQUIVALENT" if equiv["pass"] else "R22_FAIL_R21_OBSERVER_EQUIVALENCE__NO_ORDER_INTERPRETATION","R21_observer_equivalence":equiv}
    if result.get("status")=="FAIL_INTEGRITY": verdict="R22_FAIL_INTEGRITY"
    elif base["build_survivor"]: verdict="R22_BUILD_SURVIVOR"
    else: verdict="R22_ORDER_RESOURCE_OPEN"
    return {**base,"verdict":verdict}


def aggregate_directory(directory:Path):
    prereg=load_prereg(); rows=[]
    for p in sorted(directory.glob("*.json")):
        d=json.loads(p.read_text(encoding="utf-8"))
        if d.get("schema")=="JANUS/TRUMP/R22/ROBDD_VARIABLE_ORDER_SENSITIVITY_FORENSICS/ORDER_RESULT/v1.0": rows.append(d)
    by={r["order_id"]:r for r in rows}; missing=[x for x in ORDER_IDS if x not in by]; ordered=[by[x] for x in ORDER_IDS if x in by]
    r21row=by.get("R21_INTERNAL_FIRST_OCCURRENCE"); equiv=bool(r21row and r21row.get("R21_observer_equivalence",{}).get("pass"))
    integrity=(not missing and all(r.get("firewall",{}).get("pass") for r in ordered) and not any(r.get("verdict")=="R22_FAIL_INTEGRITY" for r in ordered))
    survivors=[r for r in ordered if r["order_id"]!="R21_INTERNAL_FIRST_OCCURRENCE" and r.get("build_survivor")]
    def rank_key(r):
        x=r["result"]
        return (int(x["maximum_nodes_seen"]),int(x["nodes_created_total"]),int(x["apply_calls_total"]),int(x["final_active_nodes"]),r["order_id"])
    ranked=sorted(survivors,key=rank_key)
    if not equiv: verdict="R22_FAIL_R21_OBSERVER_EQUIVALENCE__NO_ORDER_INTERPRETATION"
    elif not integrity: verdict="R22_FAIL_INTEGRITY"
    elif ranked: verdict="R22_ORDER_SENSITIVITY_CONFIRMED__BUILD_SURVIVOR_EXISTS"
    else: verdict="R22_NO_BUILD_SURVIVOR_IN_FROZEN_ORDER_FAMILY"
    compact=[]
    for r in ordered:
        x=r.get("result",{}); compact.append({
            "order_id":r["order_id"],"verdict":r["verdict"],"build_survivor":r.get("build_survivor"),"status":x.get("status"),"reason":x.get("reason"),
            "completed_clause_steps":x.get("completed_clause_steps"),"completion_fraction":r.get("landmarks",{}).get("completion_fraction"),
            "active_nodes_at_terminal_or_open":x.get("active_nodes_at_terminal_or_open"),"maximum_nodes_seen":x.get("maximum_nodes_seen"),
            "nodes_created_total":x.get("nodes_created_total"),"apply_calls_total":x.get("apply_calls_total"),"unique_table_hits":x.get("unique_table_hits"),
            "gc_removed_total":x.get("gc_removed_total")})
    return {
        "schema":"JANUS/TRUMP/R22/ROBDD_VARIABLE_ORDER_SENSITIVITY_FORENSICS/AGGREGATE_RESULT/v1.0",
        "created_date":"2026-09-02",
        "verdict":verdict,
        "order_count":len(ordered),
        "missing_orders":missing,
        "R21_observer_equivalence_pass":equiv,
        "integrity_pass":integrity,
        "build_survivor_count":len(ranked),
        "build_survivor_order_ids":[r["order_id"] for r in ranked],
        "resource_selected_best_build_order":ranked[0]["order_id"] if ranked else None,
        "orders":compact,
        "truth_accessed":False,
        "interpretation":"R22 changes only preregistered structure-derived total variable order and measures build-phase ROBDD resource behavior. It has no semantic authority.",
        "claim_ceiling":prereg["claim_ceiling"],
        "seal":"THE_ORDER_RACE_USED_EIGHT_PREWRITTEN_LANES__THE_TRUTH_WAS_NOT_IN_THE_STADIUM",
        "P_VS_NP":"OPEN",
    }


def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument("--order",choices=ORDER_IDS); g.add_argument("--aggregate-dir"); ap.add_argument("--output",required=True); args=ap.parse_args()
    out=run_order(args.order) if args.order else aggregate_directory(Path(args.aggregate_dir))
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:out.get(k) for k in ("order_id","verdict","build_survivor","build_survivor_count","build_survivor_order_ids","resource_selected_best_build_order","R21_observer_equivalence_pass","P_VS_NP") if k in out},indent=2,sort_keys=True))
    return 2 if str(out.get("verdict","")).startswith("R22_FAIL") else 0


if __name__=="__main__": raise SystemExit(main())
