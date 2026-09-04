from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48g_targeted_unit_weight_pressure_counterexample_hunt as r48g
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE = "JANUS_TRUMP_R48Q_WIDTH4_FULL_FROZEN_FRONTIER_FALSIFIER"
MAX_ORDINAL = 64
EXPECTED_UNIQUE_ROOTS = 52
WIDTH_CAP = 4
R48O_ROOT_HASH = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
R48O_PIVOTS = [2,4,5,7,9,10]


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def formula_hash(f):
    return r47f.formula_hash(canon(f))


def max_width(f):
    x=canon(f)
    return max((len(c) for c in x),default=0)


def run_width4_root(root, provenance):
    root=canon(root)
    if max_width(root)>WIDTH_CAP:
        return {
            "covered":False,
            "root_hash":formula_hash(root),
            "root_CLV":list(clv(root)),
            "root_max_width":max_width(root),
            "provenance":provenance,
            "selected_path":[],
            "candidate_probe_count":0,
            "max_persisted_width":max_width(root),
            "obstruction":{
                "kind":"ROOT_ALREADY_EXCEEDS_WIDTH_CAP",
                "state_hash":formula_hash(root),
                "state_CLV":list(clv(root)),
                "state_max_width":max_width(root),
                "state_formula":[list(c) for c in root],
                "candidate_rows":None,
            },
            "terminal":None,
        }

    current=root
    V0=clv(root)[2]
    selected_path=[]
    selected_full=[]
    total_probes=0
    max_persisted=max_width(root)

    for state_index in range(V0+1):
        if state_index>=V0:
            raise AssertionError(("R48Q_STEP_CAP_EXHAUSTED",formula_hash(root),clv(current)))
        if max_width(current)>WIDTH_CAP:
            raise AssertionError(("R48Q_PERSISTED_WIDTH_DRIFT",formula_hash(root),state_index,max_width(current)))
        rows,candidates=r48o.scan(current,False)
        total_probes += len(rows)
        if total_probes>V0*V0:
            raise AssertionError(("R48Q_PROBE_CAP_EXCEEDED",formula_hash(root),total_probes,V0*V0))
        safe=[x for x in rows if x.get("width4_safe",False)]
        if not safe:
            replay_rows,_=r48o.scan(current,True)
            eligible=[x for x in replay_rows if x.get("eligible",False)]
            terminals=[x for x in eligible if x.get("terminal") is not None]
            width_safe=[x for x in eligible if x.get("terminal") is None and x.get("final_max_width",999)<=WIDTH_CAP]
            if terminals or width_safe:
                raise AssertionError(("R48Q_OBSTRUCTION_REPLAY_DRIFT",formula_hash(root),state_index))
            return {
                "covered":False,
                "root_hash":formula_hash(root),
                "root_CLV":list(clv(root)),
                "root_max_width":max_width(root),
                "provenance":provenance,
                "selected_path":selected_path,
                "candidate_probe_count":total_probes,
                "max_persisted_width":max_persisted,
                "obstruction":{
                    "kind":"NO_WIDTH4_SAFE_CERTIFIED_SUCCESSOR" if eligible else "NO_VARIABLE_DECREASING_CANDIDATE",
                    "state_index":int(state_index),
                    "state_hash":formula_hash(current),
                    "state_CLV":list(clv(current)),
                    "state_max_width":max_width(current),
                    "state_width_histogram":r48o.width_histogram(current),
                    "state_formula":[list(c) for c in current],
                    "candidate_rows":replay_rows,
                },
                "terminal":None,
            }

        chosen_row=min(safe,key=lambda x:int(x["var"]))
        chosen=candidates[int(chosen_row["var"])]
        replay=r48o.r47m.independent_replay(current,chosen)
        if not replay["pass"]:
            raise AssertionError(("R48Q_SELECTED_REPLAY_FAIL",formula_hash(root),chosen_row["var"],replay))
        row=r48o.candidate_row(current,chosen,True)
        final=canon(chosen["normalization"]["final_formula"])
        selected_full.append((current,chosen))
        selected_path.append({
            "step":len(selected_path)+1,
            "state_hash":formula_hash(current),
            "state_CLV":list(clv(current)),
            "state_max_width":max_width(current),
            "var":int(row["var"]),
            "final_CLV":row["final_CLV"],
            "final_max_width":int(row["final_max_width"]),
            "terminal":row["terminal"],
            "semantic_sat":row["semantic_sat"],
            "full_R47M_independent_replay_pass":True,
        })
        if row["terminal"] is not None:
            lift=r48g.lift_sat_root(root,selected_full,chosen)
            if not lift["pass"]:
                raise AssertionError(("R48Q_SAT_ROOT_LIFT_FAIL",formula_hash(root)))
            return {
                "covered":True,
                "root_hash":formula_hash(root),
                "root_CLV":list(clv(root)),
                "root_max_width":max_width(root),
                "provenance":provenance,
                "selected_path":selected_path,
                "selected_pivots":[int(x["var"]) for x in selected_path],
                "candidate_probe_count":total_probes,
                "max_persisted_width":max_persisted,
                "obstruction":None,
                "terminal":{
                    "kind":row["terminal"],
                    "semantic_sat":row["semantic_sat"],
                    "final_hash":formula_hash(final),
                    "final_CLV":list(clv(final)),
                    "SAT_root_reconstruction_pass":True,
                },
            }
        if row["final_max_width"]>WIDTH_CAP:
            raise AssertionError(("R48Q_SELECTED_WIDTH_FAIL",formula_hash(root),row))
        max_persisted=max(max_persisted,int(row["final_max_width"]))
        current=final
    raise AssertionError("R48Q_UNREACHABLE_ROOT_EXIT")


def run():
    # Independent regression of the separate R48O pressure root before the frontier.
    r48o_reg=r48o.run()
    if r48o_reg["verdict"]!="R48G_ROOT_REACHES_CERTIFIED_TERMINAL_UNDER_WIDTH4_CHAIN__FINITE_ONLY":
        raise AssertionError(("R48Q_R48O_REGRESSION_VERDICT_DRIFT",r48o_reg["verdict"]))
    if r48o_reg["root"]["hash"]!=R48O_ROOT_HASH:
        raise AssertionError("R48Q_R48O_ROOT_HASH_DRIFT")
    if [x["var"] for x in r48o_reg["selected_path"]]!=R48O_PIVOTS:
        raise AssertionError(("R48Q_R48O_PIVOT_DRIFT",[x["var"] for x in r48o_reg["selected_path"]]))
    if r48o_reg["max_persisted_width"]!=4:
        raise AssertionError("R48Q_R48O_WIDTH_DRIFT")

    center_original,_,center_fixpoint=r47x.load_center_original()
    records=[]
    seen=set()
    metrics={
        "frontier_positions_seen":0,
        "mutants_generated":0,
        "duplicate_mutations_skipped":0,
        "semantic_or_nonfixpoint":0,
        "reachable_fixpoints":0,
        "unique_reachable_roots_evaluated":0,
        "covered_roots":0,
        "width4_obstruction_roots":0,
        "total_candidate_probes":0,
        "total_selected_steps":0,
    }

    center_record=run_width4_root(center_fixpoint,{
        "kind":"CENTER_CONTROL","frontier_ordinal":0,"phase":"CENTER",
        "source_clause":None,"replacement_clause":None,"mutated_original_hash":None,
    })
    records.append(center_record); seen.add(center_record["root_hash"])
    if not center_record["covered"]:
        metrics["unique_reachable_roots_evaluated"]=1
        metrics["width4_obstruction_roots"]=1
        metrics["total_candidate_probes"]=center_record["candidate_probe_count"]
        return finish(records,metrics,r48o_reg)

    for ordinal,(phase,source,replacement,mutated) in enumerate(r47x.frontier(center_original),1):
        if ordinal>MAX_ORDINAL:
            break
        metrics["frontier_positions_seen"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue
        r47x.validate_exact_3cnf(mutated)
        metrics["mutants_generated"] += 1
        reached=r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root=canon(reached["formula"]); rh=formula_hash(root)
        if rh in seen:
            continue
        seen.add(rh)
        record=run_width4_root(root,{
            "kind":"ONE_SWAP_REACHABLE_FIXPOINT","frontier_ordinal":int(ordinal),"phase":phase,
            "source_clause":list(source),"replacement_clause":list(replacement),
            "mutated_original_hash":formula_hash(mutated),
        })
        records.append(record)
        if not record["covered"]:
            break

    metrics["unique_reachable_roots_evaluated"]=len(records)
    metrics["covered_roots"]=sum(1 for x in records if x["covered"])
    metrics["width4_obstruction_roots"]=sum(1 for x in records if not x["covered"])
    metrics["total_candidate_probes"]=sum(int(x["candidate_probe_count"]) for x in records)
    metrics["total_selected_steps"]=sum(len(x["selected_path"]) for x in records)
    return finish(records,metrics,r48o_reg)


def finish(records,metrics,r48o_reg):
    obstruction=next((x for x in records if not x["covered"]),None)
    if obstruction is None:
        if len(records)!=EXPECTED_UNIQUE_ROOTS:
            raise AssertionError(("R48Q_EXPECTED_52_ROOT_LINEAGE_DRIFT",len(records)))
        verdict="FULL_FROZEN_52_ROOT_FRONTIER_COVERED_BY_WIDTH4_CHAIN__FINITE_ONLY"
    elif obstruction["obstruction"]["kind"]=="NO_VARIABLE_DECREASING_CANDIDATE":
        verdict="STRONGER_NO_VARIABLE_DECREASING_CANDIDATE_FOUND"
    else:
        verdict="EXPLICIT_REACHABLE_WIDTH4_FRONTIER_OBSTRUCTION_FOUND"
    hardest=max((x for x in records if x["covered"]),key=lambda x:(int(x["candidate_probe_count"]),len(x["selected_path"]),tuple(x["root_CLV"]),x["root_hash"]),default=None)
    max_width_seen=max((int(x["max_persisted_width"]) for x in records),default=None)
    return {
        "gate":GATE,
        "verdict":verdict,
        "width_cap":WIDTH_CAP,
        "R48O_regression":{
            "root_hash":r48o_reg["root"]["hash"],
            "selected_pivots":[x["var"] for x in r48o_reg["selected_path"]],
            "max_persisted_width":r48o_reg["max_persisted_width"],
            "SAT_root_reconstruction_pass":r48o_reg["terminal"]["SAT_root_reconstruction"]["pass"],
        },
        "metrics":metrics,
        "maximum_observed_persisted_width":max_width_seen,
        "hardest_covered_root":None if hardest is None else {
            "root_hash":hardest["root_hash"],"root_CLV":hardest["root_CLV"],"provenance":hardest["provenance"],
            "candidate_probe_count":hardest["candidate_probe_count"],"selected_pivots":hardest["selected_pivots"],
            "selected_step_count":len(hardest["selected_path"]),"max_persisted_width":hardest["max_persisted_width"],
            "terminal":hardest["terminal"],
        },
        "first_obstruction":obstruction,
        "roots":records,
        "interpretation":{
            "finite_frontier_only":True,
            "full_52_root_success_proves_universal_W4":False,
            "one_reachable_obstruction_refutes_universal_W4_for_frozen_grammar":True,
            "no_sequence_enumeration":True,
        },
        "firewall":{
            "UNIVERSAL_WIDTH_4_COVERAGE":"NOT_PROVED_UNLESS_REFUTED_BY_THIS_GATE",
            "UNIVERSAL_CONSTANT_WIDTH_COVERAGE":"NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE":"OPEN",
            "O4_UNIVERSAL_COVERAGE":"OPEN",
            "SAT_IN_P":"NOT_PROVED",
            "P_EQ_NP":"NOT_PROVED",
            "P_NE_NP":"NOT_PROVED",
            "P_VS_NP":"OPEN",
            "TRUMP_finished":False,
        },
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--output"); a=p.parse_args()
    d=run()
    if a.output:
        path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    h=d["hardest_covered_root"]; o=d["first_obstruction"]
    print(json.dumps({
        "gate":d["gate"],"verdict":d["verdict"],"metrics":d["metrics"],
        "maximum_observed_persisted_width":d["maximum_observed_persisted_width"],
        "hardest_covered_root":h,
        "first_obstruction":None if o is None else {
            "root_hash":o["root_hash"],"root_CLV":o["root_CLV"],"provenance":o["provenance"],
            "selected_pivots":[x["var"] for x in o["selected_path"]],
            "obstruction_kind":o["obstruction"]["kind"],"state_hash":o["obstruction"]["state_hash"],
            "state_CLV":o["obstruction"]["state_CLV"],"state_max_width":o["obstruction"]["state_max_width"],
        },
        "R48O_regression":d["R48O_regression"],"firewall":d["firewall"],
    },sort_keys=True))


if __name__=="__main__":
    main()
