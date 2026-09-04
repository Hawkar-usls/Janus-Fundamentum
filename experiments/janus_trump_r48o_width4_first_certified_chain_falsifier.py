from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48g_targeted_unit_weight_pressure_counterexample_hunt as r48g

GATE = "JANUS_TRUMP_R48O_WIDTH4_FIRST_CERTIFIED_CHAIN_FALSIFIER"
WIDTH_CAP = 4
EXPECTED_MUTATED_ORIGINAL_HASH = "720355b9542ddccc7bfe6ae1fcda35eb6879ad921aebb4a8b6f63998ecaadd0c"
EXPECTED_ROOT_HASH = "3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
EXPECTED_ROOT_CLV = (75, 199, 22)
R48G_SECOND_ORDINAL = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def formula_hash(f):
    return r47f.formula_hash(canon(f))


def max_width(f):
    x=canon(f)
    return max((len(c) for c in x), default=0)


def width_histogram(f):
    out={}
    for c in canon(f):
        k=str(len(c)); out[k]=out.get(k,0)+1
    return out


def reconstruct_root():
    first=r48g.reconstruct_r47x_first_mutation()
    for meta in r48g.targeted_second_mutations(first["mutated_original"]):
        if int(meta["targeted_ordinal"]) != R48G_SECOND_ORDINAL:
            continue
        if meta["mutated_original_hash"] != EXPECTED_MUTATED_ORIGINAL_HASH:
            raise AssertionError(("R48O_MUTATED_HASH_DRIFT",meta["mutated_original_hash"]))
        reached=r47f.reachable_fixpoint(meta["mutated_original"])
        if reached is None:
            raise AssertionError("R48O_NO_REACHABLE_ROOT")
        root=canon(reached["formula"])
        if formula_hash(root)!=EXPECTED_ROOT_HASH or clv(root)!=EXPECTED_ROOT_CLV:
            raise AssertionError(("R48O_ROOT_DRIFT",formula_hash(root),clv(root)))
        if max_width(root)>WIDTH_CAP:
            raise AssertionError(("R48O_ROOT_WIDTH_DRIFT",max_width(root)))
        return meta,reached,root
    raise AssertionError("R48O_SECOND_MUTATION_NOT_FOUND")


def candidate_row(current,candidate,replay_pass=None):
    final=canon(candidate["normalization"]["final_formula"])
    before_vars=set(r33.variables(current)); after_vars=set(r33.variables(final))
    terminal=candidate["normalization"]["terminal"]
    delta_v=len(before_vars)-len(after_vars)
    no_fresh=after_vars <= before_vars
    eligible=bool(terminal is not None or (delta_v>=1 and no_fresh))
    w=max_width(final)
    return {
        "var":int(candidate["var"]),
        "input_CLV":candidate["input_CLV"],
        "forced_DP_CLV":candidate["DP"]["measure_after_forced_DP"],
        "final_CLV":candidate["final_CLV"],
        "terminal":terminal,
        "semantic_sat":candidate["normalization"]["semantic_sat"],
        "delta_V_eliminated":int(delta_v),
        "no_fresh_variables":bool(no_fresh),
        "eligible":eligible,
        "final_max_width":int(w),
        "final_width_histogram":width_histogram(final),
        "width4_safe":bool(terminal is not None or (eligible and w<=WIDTH_CAP)),
        "DP_independent_replay_pass":bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass":bool(candidate["polynomial_intermediate_envelope_pass"]),
        "full_R47M_independent_replay_pass":replay_pass,
    }


def scan(current,replay_all=False):
    rows=[]; candidates={}
    for v in r33.variables(current):
        c=r47m.macro_candidate_full_closure(current,int(v))
        if c is None:
            rows.append({"var":int(v),"candidate":False,"eligible":False,"width4_safe":False})
            continue
        if not c["DP_independent_replay_pass"] or not c["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R48O_CANDIDATE_INTEGRITY_FAIL",v))
        candidates[int(v)]=c
        replay_pass=None
        if replay_all:
            replay=r47m.independent_replay(current,c)
            if not replay["pass"]:
                raise AssertionError(("R48O_FULL_REPLAY_FAIL",v,replay))
            replay_pass=True
        rows.append(candidate_row(current,c,replay_pass))
    return rows,candidates


def run():
    meta,reached,root=reconstruct_root()
    current=root
    V0=clv(root)[2]
    selected_path=[]
    selected_full=[]
    total_probes=0
    max_persisted_width=max_width(root)

    for state_index in range(V0+1):
        if state_index>=V0:
            raise AssertionError(("R48O_STEP_CAP_EXHAUSTED",clv(current)))
        if max_width(current)>WIDTH_CAP:
            raise AssertionError(("R48O_PERSISTED_WIDTH_DRIFT",state_index,max_width(current)))
        rows,candidates=scan(current,False)
        total_probes += len(rows)
        if total_probes > V0*V0:
            raise AssertionError(("R48O_PROBE_CAP_EXCEEDED",total_probes,V0*V0))
        safe=[r for r in rows if r.get("width4_safe",False)]
        if not safe:
            replay_rows,_=scan(current,True)
            eligible=[r for r in replay_rows if r.get("eligible",False)]
            terminals=[r for r in eligible if r.get("terminal") is not None]
            if terminals:
                raise AssertionError("R48O_OBSTRUCTION_REPLAY_FOUND_TERMINAL")
            width_safe=[r for r in eligible if r.get("final_max_width",999)<=WIDTH_CAP]
            if width_safe:
                raise AssertionError("R48O_OBSTRUCTION_REPLAY_FOUND_WIDTH_SAFE")
            verdict=("STRONGER_NO_VARIABLE_DECREASING_CANDIDATE_FOUND" if not eligible else "EXPLICIT_REACHABLE_WIDTH4_CHAIN_OBSTRUCTION_FOUND")
            return {
                "gate":GATE,
                "verdict":verdict,
                "root":{"hash":formula_hash(root),"CLV":list(clv(root)),"max_width":max_width(root)},
                "selected_path":selected_path,
                "candidate_probe_count":total_probes,
                "max_persisted_width":max_persisted_width,
                "obstruction":{
                    "state_index":int(state_index),
                    "state_hash":formula_hash(current),
                    "state_CLV":list(clv(current)),
                    "state_max_width":max_width(current),
                    "state_width_histogram":width_histogram(current),
                    "state_formula":[list(c) for c in current],
                    "candidate_rows":replay_rows,
                },
                "terminal":None,
                "firewall":firewall(),
            }

        chosen_row=min(safe,key=lambda r:int(r["var"]))
        chosen=candidates[int(chosen_row["var"])]
        replay=r47m.independent_replay(current,chosen)
        if not replay["pass"]:
            raise AssertionError(("R48O_SELECTED_REPLAY_FAIL",chosen_row["var"],replay))
        chosen_row=candidate_row(current,chosen,True)
        final=canon(chosen["normalization"]["final_formula"])
        selected_full.append((current,chosen))
        selected_path.append({
            "step":len(selected_path)+1,
            "state_hash":formula_hash(current),
            "state_CLV":list(clv(current)),
            "state_max_width":max_width(current),
            **chosen_row,
        })
        if chosen_row["terminal"] is not None:
            sat_lift=r48g.lift_sat_root(root,selected_full,chosen)
            if not sat_lift["pass"]:
                raise AssertionError("R48O_SAT_ROOT_LIFT_FAIL")
            return {
                "gate":GATE,
                "verdict":"R48G_ROOT_REACHES_CERTIFIED_TERMINAL_UNDER_WIDTH4_CHAIN__FINITE_ONLY",
                "root":{"hash":formula_hash(root),"CLV":list(clv(root)),"max_width":max_width(root)},
                "selected_path":selected_path,
                "candidate_probe_count":total_probes,
                "max_persisted_width":max(max_persisted_width,max_width(current)),
                "obstruction":None,
                "terminal":{
                    "kind":chosen_row["terminal"],
                    "semantic_sat":chosen_row["semantic_sat"],
                    "final_hash":formula_hash(final),
                    "final_CLV":list(clv(final)),
                    "SAT_root_reconstruction":sat_lift,
                },
                "firewall":firewall(),
            }
        if chosen_row["final_max_width"]>WIDTH_CAP:
            raise AssertionError(("R48O_SELECTED_WIDTH_FAIL",chosen_row))
        max_persisted_width=max(max_persisted_width,chosen_row["final_max_width"])
        current=final
    raise AssertionError("R48O_UNREACHABLE_EXIT")


def firewall():
    return {
        "UNIVERSAL_WIDTH_4_COVERAGE":"NOT_PROVED_UNLESS_REFUTED_BY_THIS_GATE",
        "UNIVERSAL_CONSTANT_WIDTH_COVERAGE":"NOT_PROVED",
        "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE":"OPEN",
        "O4_UNIVERSAL_COVERAGE":"OPEN",
        "SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_NE_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN",
        "TRUMP_finished":False,
    }


def main():
    p=argparse.ArgumentParser(); p.add_argument("--output"); a=p.parse_args()
    d=run()
    if a.output:
        path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "gate":d["gate"],"verdict":d["verdict"],"root":d["root"],
        "selected_pivots":[x["var"] for x in d["selected_path"]],
        "persisted_widths":[x["state_max_width"] for x in d["selected_path"]],
        "max_persisted_width":d["max_persisted_width"],
        "candidate_probe_count":d["candidate_probe_count"],
        "obstruction":None if d["obstruction"] is None else {
            "state_hash":d["obstruction"]["state_hash"],"state_CLV":d["obstruction"]["state_CLV"],"state_max_width":d["obstruction"]["state_max_width"]},
        "terminal":d["terminal"],"firewall":d["firewall"],
    },sort_keys=True))


if __name__=="__main__":
    main()
