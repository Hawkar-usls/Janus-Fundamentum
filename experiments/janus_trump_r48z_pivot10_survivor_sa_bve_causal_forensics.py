from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE="JANUS_TRUMP_R48Z_PIVOT10_SURVIVOR_SA_BVE_CAUSAL_FORENSICS"
PREFIX=[2,4,5,7,9]
PIVOT=10
SURVIVOR=(15,-20,-24,27,28)
SURVIVOR_SET=frozenset(SURVIVOR)
SURVIVOR_VARS=frozenset(abs(x) for x in SURVIVOR)
EXPECTED_ROOT="3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"


def canon(f): return r33.canonical_formula(f)
def clv(f): return r33.measure(canon(f))
def fhash(f): return r48o.formula_hash(canon(f))
def maxw(f): return max((len(c) for c in canon(f)),default=0)

def snapshot(f):
    x=canon(f)
    exact=SURVIVOR in x
    lit_overlap=max((len(set(c)&SURVIVOR_SET) for c in x),default=0)
    var_overlap=max((len({abs(l) for l in c}&SURVIVOR_VARS) for c in x),default=0)
    return {
        "formula_hash":fhash(x),"CLV":list(clv(x)),"max_width":maxw(x),
        "clauses_width_gt4":sum(1 for c in x if len(c)>4),
        "exact_survivor_present":bool(exact),
        "survivor_literal_overlap_max":int(lit_overlap),
        "survivor_variable_overlap_max":int(var_overlap),
    }

def reconstruct_predecessor():
    _,_,root=r48o.reconstruct_root(); root=canon(root)
    if fhash(root)!=EXPECTED_ROOT: raise AssertionError(("R48Z_ROOT_DRIFT",fhash(root)))
    current=root; path=[]
    for step,var in enumerate(PREFIX,1):
        c=r47m.macro_candidate_full_closure(current,int(var))
        if c is None: raise AssertionError(("R48Z_PREFIX_MISSING",step,var))
        rep=r47m.independent_replay(current,c)
        if not rep["pass"]: raise AssertionError(("R48Z_PREFIX_REPLAY_FAIL",step,var,rep))
        final=canon(c["normalization"]["final_formula"])
        if c["normalization"]["terminal"] is not None or maxw(final)>4:
            raise AssertionError(("R48Z_PREFIX_DRIFT",step,var,c["normalization"]["terminal"],maxw(final)))
        path.append({"step":step,"var":int(var),"before":snapshot(current),"after":snapshot(final)})
        current=final
    return root,current,path

def run():
    root,predecessor,prefix_trace=reconstruct_predecessor()
    claimed=r47m.macro_candidate_full_closure(predecessor,PIVOT)
    if claimed is None: raise AssertionError("R48Z_PIVOT10_MISSING")
    rep=r47m.independent_replay(predecessor,claimed)
    if not rep["pass"]: raise AssertionError(("R48Z_PIVOT10_REPLAY_FAIL",rep))
    if claimed["normalization"]["terminal"]!="DIRECT_EMPTY_CNF": raise AssertionError(("R48Z_TERMINAL_DRIFT",claimed["normalization"]["terminal"]))
    if int(claimed["normalization"]["SA_BVE_application_count"])!=8: raise AssertionError(("R48Z_BVE_COUNT_DRIFT",claimed["normalization"]["SA_BVE_application_count"]))
    forced=canon(claimed["DP"]["transformed"])
    state=forced
    trace=[]; bve_vars=[]; removal=None; prev_bve=None; saw_survivor=False; terminal=None
    bound=r47m.outer_height_bound(forced)
    total_bve=0
    for outer in range(bound+1):
        before=canon(state); before_snap=snapshot(before)
        norm=r47j.normalize_to_certified_fixpoint(before)
        after_norm=canon(norm["final_formula"]); norm_snap=snapshot(after_norm)
        if norm_snap["exact_survivor_present"]: saw_survivor=True
        row={
            "outer":int(outer),"before_R47J":before_snap,"after_R47J":norm_snap,
            "R47J_terminal":norm["terminal"],"R47J_round_count":int(norm["round_count"]),
            "R47J_restart_count":int(norm["restart_count"]),
        }
        if before_snap["exact_survivor_present"] and not norm_snap["exact_survivor_present"] and removal is None:
            if norm["terminal"] is not None:
                removal={"kind":"TERMINAL_R47J_COLLAPSE","outer":int(outer),"preceding_SA_BVE_var":prev_bve}
            elif prev_bve is not None and abs(int(prev_bve)) not in SURVIVOR_VARS:
                removal={"kind":"EXTERNAL_CONTEXT_SA_BVE_THEN_R47J","outer":int(outer),"preceding_SA_BVE_var":int(prev_bve)}
            else:
                removal={"kind":"SA_BVE_THEN_R47J","outer":int(outer),"preceding_SA_BVE_var":None if prev_bve is None else int(prev_bve)}
        if norm["terminal"] is not None:
            terminal=norm["terminal"]; row["stop"]=terminal; trace.append(row); state=after_norm; break
        bve,ledger=r47m.r42.best_sa_bve_candidate(after_norm)
        row["SA_BVE_variables_checked"]=int(ledger["variables_checked"])
        if bve is None:
            row["SA_BVE_applied"]=False; row["stop"]="CERTIFIED_FULL_EXISTING_STACK_FIXPOINT"; trace.append(row); state=after_norm; break
        brep=r47m.r42.independent_sa_bve_replay(after_norm,bve)
        if not brep["pass"]: raise AssertionError(("R48Z_BVE_REPLAY_FAIL",outer,brep))
        after_bve=canon(bve["transformed"]); bve_snap=snapshot(after_bve); v=int(bve["var"])
        if not clv(after_bve)<clv(after_norm): raise AssertionError(("R48Z_BVE_NOT_DESCENT",outer,v))
        if norm_snap["exact_survivor_present"] and not bve_snap["exact_survivor_present"] and removal is None:
            removal={
                "kind":"DIRECT_SURVIVOR_VARIABLE_SA_BVE" if abs(v) in SURVIVOR_VARS else "EXTERNAL_CONTEXT_DIRECT_SA_BVE",
                "outer":int(outer),"SA_BVE_var":v,
            }
        row.update({
            "SA_BVE_applied":True,"SA_BVE_var":v,"SA_BVE_var_in_survivor_support":abs(v) in SURVIVOR_VARS,
            "SA_BVE_replay_pass":True,"after_SA_BVE":bve_snap,"restart":True,
        })
        trace.append(row); bve_vars.append(v); total_bve+=1; prev_bve=v; state=after_bve
    else: raise AssertionError(("R48Z_BOUND_EXHAUSTED",bound))
    if not saw_survivor: raise AssertionError("R48Z_SEALED_SURVIVOR_NEVER_OBSERVED")
    final=canon(state)
    if fhash(final)!=claimed["normalization"]["final_formula_hash"]: raise AssertionError(("R48Z_FINAL_HASH_MISMATCH",fhash(final),claimed["normalization"]["final_formula_hash"]))
    if terminal!=claimed["normalization"]["terminal"]: raise AssertionError(("R48Z_FINAL_TERMINAL_MISMATCH",terminal,claimed["normalization"]["terminal"]))
    if total_bve!=8: raise AssertionError(("R48Z_MANUAL_BVE_COUNT_MISMATCH",total_bve))
    if removal is None:
        if any(x["before_R47J"]["exact_survivor_present"] and x["R47J_terminal"] is not None for x in trace):
            classification="SURVIVOR_PERSISTS_UNTIL_TERMINAL_COLLAPSE"
        else: classification="MIXED_SURVIVOR_DISCHARGE_MECHANISM"
    elif removal["kind"]=="DIRECT_SURVIVOR_VARIABLE_SA_BVE": classification="DIRECT_SURVIVOR_VARIABLE_SA_BVE_REMOVAL"
    elif removal["kind"]=="EXTERNAL_CONTEXT_SA_BVE_THEN_R47J": classification="EXTERNAL_CONTEXT_SA_BVE_UNLOCKS_SURVIVOR_DISCHARGE"
    elif removal["kind"]=="SA_BVE_THEN_R47J": classification="SA_BVE_THEN_R47J_INDIRECT_SURVIVOR_DISCHARGE"
    elif removal["kind"]=="TERMINAL_R47J_COLLAPSE": classification="SURVIVOR_PERSISTS_UNTIL_TERMINAL_COLLAPSE"
    else: classification="MIXED_SURVIVOR_DISCHARGE_MECHANISM"
    return {
        "gate":GATE,"classification":classification,
        "root":snapshot(root),"predecessor":snapshot(predecessor),"prefix_trace":prefix_trace,
        "pivot":PIVOT,"forced_DP":snapshot(forced),"survivor":list(SURVIVOR),
        "removal_event":removal,"SA_BVE_sequence":bve_vars,"SA_BVE_application_count":total_bve,
        "trace":trace,"terminal":terminal,"final":snapshot(final),
        "exact_match_to_frozen_R47M":True,
        "interpretation":{"finite_single_path_only":True,"universal_SA_BVE_reset_proved":False},
        "firewall":{"UNIVERSAL_WIDTH_RESET_LEMMA":"NOT_PROVED","UNIVERSAL_WIDTH_4_COVERAGE":"NOT_PROVED","UNIVERSAL_CONSTANT_WIDTH_COVERAGE":"NOT_PROVED","O4_UNIVERSAL_COVERAGE":"OPEN","SAT_IN_P":"NOT_PROVED","P_EQ_NP":"NOT_PROVED","P_NE_NP":"NOT_PROVED","P_VS_NP":"OPEN","TRUMP_finished":False},
    }

def main():
    p=argparse.ArgumentParser();p.add_argument("--output");a=p.parse_args();d=run()
    if a.output:
        path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"gate":d["gate"],"classification":d["classification"],"survivor":d["survivor"],"removal_event":d["removal_event"],"SA_BVE_sequence":d["SA_BVE_sequence"],"terminal":d["terminal"],"trace":[{"outer":x["outer"],"before_survivor":x["before_R47J"]["exact_survivor_present"],"after_r47j_survivor":x["after_R47J"]["exact_survivor_present"],"r47j_terminal":x["R47J_terminal"],"bve_var":x.get("SA_BVE_var"),"bve_in_support":x.get("SA_BVE_var_in_survivor_support"),"after_bve_survivor":None if "after_SA_BVE" not in x else x["after_SA_BVE"]["exact_survivor_present"],"max_width_after_r47j":x["after_R47J"]["max_width"]} for x in d["trace"]],"firewall":d["firewall"]},sort_keys=True))
if __name__=="__main__": main()
