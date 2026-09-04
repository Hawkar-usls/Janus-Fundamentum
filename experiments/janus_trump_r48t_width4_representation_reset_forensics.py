from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE="JANUS_TRUMP_R48T_WIDTH4_REPRESENTATION_RESET_FORENSICS"
EXPECTED_ROOT="3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
EXPECTED_PIVOTS=[2,4,5,7,9,10]
WIDTH_CAP=4


def canon(f): return r33.canonical_formula(f)
def clv(f): return r33.measure(canon(f))
def maxw(f):
    x=canon(f); return max((len(c) for c in x),default=0)
def hist(f):
    out={}
    for c in canon(f): out[str(len(c))]=out.get(str(len(c)),0)+1
    return out


def run():
    sealed=r48o.run()
    if sealed["root"]["hash"]!=EXPECTED_ROOT or [x["var"] for x in sealed["selected_path"]]!=EXPECTED_PIVOTS or sealed["max_persisted_width"]!=4:
        raise AssertionError("R48T_R48O_REGRESSION_DRIFT")
    _,_,root=r48o.reconstruct_root()
    current=canon(root)
    rows=[]
    seen_categories=[]
    for step,var in enumerate(EXPECTED_PIVOTS,1):
        candidate=r48o.r47m.macro_candidate_full_closure(current,int(var))
        if candidate is None: raise AssertionError(("R48T_SELECTED_CANDIDATE_MISSING",step,var))
        replay=r48o.r47m.independent_replay(current,candidate)
        if not replay["pass"]: raise AssertionError(("R48T_SELECTED_REPLAY_FAIL",step,var,replay))
        forced=canon(candidate["DP"]["transformed"])
        r47j_only=r47j.normalize_to_certified_fixpoint(forced)
        r47j_final=canon(r47j_only["final_formula"])
        full_final=canon(candidate["normalization"]["final_formula"])
        cw=maxw(current); fw=maxw(forced); jw=maxw(r47j_final); uw=maxw(full_final)
        terminal=candidate["normalization"]["terminal"]
        if fw<=cw:
            category="NO_TRANSIENT_WIDTH_GROWTH"
        elif jw<=WIDTH_CAP:
            category="R47J_RESETS_WIDTH_TO_4"
        elif terminal is not None and uw<=WIDTH_CAP:
            category="TERMINAL_BEFORE_WIDTH_RESET"
        elif uw<=WIDTH_CAP:
            category="SA_BVE_OR_LATER_FULL_CLOSURE_RESETS_WIDTH_TO_4"
        else:
            raise AssertionError(("R48T_SELECTED_PATH_LOST_WIDTH4",step,var,cw,fw,jw,uw))
        seen_categories.append(category)
        rows.append({
            "step":int(step),"var":int(var),
            "current_CLV":list(clv(current)),"current_width":cw,"current_width_histogram":hist(current),
            "forced_DP_CLV":list(clv(forced)),"forced_DP_width":fw,"forced_DP_width_histogram":hist(forced),
            "R47J_only_final_CLV":list(clv(r47j_final)),"R47J_only_final_width":jw,"R47J_only_width_histogram":hist(r47j_final),"R47J_only_terminal":r47j_only["terminal"],"R47J_round_count":int(r47j_only["round_count"]),"R47J_restart_count":int(r47j_only["restart_count"]),
            "full_R47M_final_CLV":list(clv(full_final)),"full_R47M_final_width":uw,"full_R47M_width_histogram":hist(full_final),"full_terminal":terminal,"SA_BVE_application_count":int(candidate["normalization"]["SA_BVE_application_count"]),"segment_count":int(candidate["normalization"]["segment_count"]),
            "full_independent_replay_pass":True,"classification":category,
        })
        current=full_final
    unique=sorted(set(seen_categories))
    overall=unique[0] if len(unique)==1 else "MIXED_RESET_MECHANISM"
    return {
        "gate":GATE,"verdict":overall,
        "sealed_root_hash":EXPECTED_ROOT,"selected_pivots":EXPECTED_PIVOTS,
        "rows":rows,
        "summary":{
            "maximum_persisted_width":max(x["current_width"] for x in rows),
            "maximum_forced_DP_width":max(x["forced_DP_width"] for x in rows),
            "maximum_R47J_only_final_width":max(x["R47J_only_final_width"] for x in rows),
            "maximum_full_R47M_final_width":max(x["full_R47M_final_width"] for x in rows),
            "classification_histogram":{k:seen_categories.count(k) for k in sorted(set(seen_categories))},
            "transient_width_growth_steps":[x["step"] for x in rows if x["forced_DP_width"]>x["current_width"]],
            "R47J_reset_steps":[x["step"] for x in rows if x["classification"]=="R47J_RESETS_WIDTH_TO_4"],
            "full_closure_reset_steps":[x["step"] for x in rows if x["classification"]=="SA_BVE_OR_LATER_FULL_CLOSURE_RESETS_WIDTH_TO_4"],
        },
        "interpretation":{"finite_path_only":True,"transient_width_gt4_is_allowed_by_R48N":True,"universal_width_reset_proved":False},
        "firewall":{"UNIVERSAL_WIDTH_4_COVERAGE":"NOT_PROVED","UNIVERSAL_CONSTANT_WIDTH_COVERAGE":"NOT_PROVED","O4_UNIVERSAL_COVERAGE":"OPEN","SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN","TRUMP_finished":False},
    }


def main():
    p=argparse.ArgumentParser();p.add_argument("--output");a=p.parse_args();d=run()
    if a.output:
        path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"gate":d["gate"],"verdict":d["verdict"],"summary":d["summary"],"rows":[{"step":x["step"],"var":x["var"],"current_width":x["current_width"],"forced_DP_width":x["forced_DP_width"],"R47J_only_final_width":x["R47J_only_final_width"],"full_R47M_final_width":x["full_R47M_final_width"],"SA_BVE_application_count":x["SA_BVE_application_count"],"terminal":x["full_terminal"],"classification":x["classification"]} for x in d["rows"]],"firewall":d["firewall"]},sort_keys=True))

if __name__=="__main__":main()
