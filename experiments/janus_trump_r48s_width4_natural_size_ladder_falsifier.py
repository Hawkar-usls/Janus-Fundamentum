from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r48g_targeted_unit_weight_pressure_counterexample_hunt as r48g
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE="JANUS_TRUMP_R48S_WIDTH4_NATURAL_SIZE_LADDER_FALSIFIER"
WIDTH_CAP=4
CASES=(
    (30,3.8,483038),(30,4.2,483042),
    (36,3.8,483638),(36,4.2,483642),
    (42,3.8,484238),(42,4.2,484242),
    (48,3.8,484838),(48,4.2,484842),
    (60,3.8,486038),(60,4.2,486042),
)
R48O_ROOT_HASH="3f05812b68eec1a2c16b099d5542dcc53fce66a0cb47679a1594134a0a553750"
R48O_PIVOTS=[2,4,5,7,9,10]


def canon(f): return r33.canonical_formula(f)
def clv(f): return r33.measure(canon(f))
def formula_hash(f): return r47f.formula_hash(canon(f))
def max_width(f):
    x=canon(f); return max((len(c) for c in x),default=0)

def validate_exact3(f):
    x=canon(f)
    if not x: raise AssertionError("R48S_EMPTY_INPUT")
    for c in x:
        if len(c)!=3 or r33.is_tautology(c):
            raise AssertionError(("R48S_NOT_EXACT3",c))


def run_root(root,case):
    root=canon(root)
    root_w=max_width(root)
    if root_w>WIDTH_CAP:
        return {
            "covered":False,"case":case,"root_hash":formula_hash(root),"root_CLV":list(clv(root)),"root_max_width":root_w,
            "selected_path":[],"candidate_probe_count":0,"max_persisted_width":root_w,"terminal":None,
            "obstruction":{"kind":"ROOT_ALREADY_EXCEEDS_WIDTH_CAP","state_index":0,"state_hash":formula_hash(root),"state_CLV":list(clv(root)),"state_max_width":root_w,"state_formula":[list(c) for c in root],"candidate_rows":None},
        }
    current=root; V0=clv(root)[2]; selected=[]; selected_full=[]; probes=0; maxw=root_w
    for state_index in range(V0+1):
        if state_index>=V0: raise AssertionError(("R48S_STEP_CAP",case,clv(current)))
        rows,candidates=r48o.scan(current,False)
        probes += len(rows)
        if probes>V0*V0: raise AssertionError(("R48S_PROBE_CAP",case,probes,V0*V0))
        safe=[x for x in rows if x.get("width4_safe",False)]
        if not safe:
            replay_rows,_=r48o.scan(current,True)
            eligible=[x for x in replay_rows if x.get("eligible",False)]
            terminals=[x for x in eligible if x.get("terminal") is not None]
            widthsafe=[x for x in eligible if x.get("terminal") is None and x.get("final_max_width",999)<=WIDTH_CAP]
            if terminals or widthsafe: raise AssertionError(("R48S_OBSTRUCTION_REPLAY_DRIFT",case,state_index))
            return {
                "covered":False,"case":case,"root_hash":formula_hash(root),"root_CLV":list(clv(root)),"root_max_width":root_w,
                "selected_path":selected,"candidate_probe_count":probes,"max_persisted_width":maxw,"terminal":None,
                "obstruction":{"kind":"NO_WIDTH4_SAFE_CERTIFIED_SUCCESSOR" if eligible else "NO_VARIABLE_DECREASING_CANDIDATE","state_index":int(state_index),"state_hash":formula_hash(current),"state_CLV":list(clv(current)),"state_max_width":max_width(current),"state_width_histogram":r48o.width_histogram(current),"state_formula":[list(c) for c in current],"candidate_rows":replay_rows},
            }
        row=min(safe,key=lambda x:int(x["var"])); candidate=candidates[int(row["var"])]
        replay=r48o.r47m.independent_replay(current,candidate)
        if not replay["pass"]: raise AssertionError(("R48S_SELECTED_REPLAY_FAIL",case,row["var"],replay))
        row=r48o.candidate_row(current,candidate,True); final=canon(candidate["normalization"]["final_formula"])
        selected_full.append((current,candidate))
        selected.append({"step":len(selected)+1,"state_hash":formula_hash(current),"state_CLV":list(clv(current)),"state_max_width":max_width(current),"var":int(row["var"]),"final_CLV":row["final_CLV"],"final_max_width":int(row["final_max_width"]),"terminal":row["terminal"],"semantic_sat":row["semantic_sat"],"full_R47M_independent_replay_pass":True})
        if row["terminal"] is not None:
            lift=r48g.lift_sat_root(root,selected_full,candidate)
            if not lift["pass"]: raise AssertionError(("R48S_SAT_ROOT_LIFT_FAIL",case))
            return {"covered":True,"case":case,"root_hash":formula_hash(root),"root_CLV":list(clv(root)),"root_max_width":root_w,"selected_path":selected,"selected_pivots":[x["var"] for x in selected],"candidate_probe_count":probes,"max_persisted_width":maxw,"obstruction":None,"terminal":{"kind":row["terminal"],"semantic_sat":row["semantic_sat"],"final_hash":formula_hash(final),"final_CLV":list(clv(final)),"SAT_root_reconstruction_pass":True}}
        if row["final_max_width"]>WIDTH_CAP: raise AssertionError(("R48S_SELECTED_WIDTH_FAIL",case,row))
        maxw=max(maxw,int(row["final_max_width"])); current=final
    raise AssertionError("R48S_UNREACHABLE")


def run():
    reg=r48o.run()
    if reg["root"]["hash"]!=R48O_ROOT_HASH or [x["var"] for x in reg["selected_path"]]!=R48O_PIVOTS or reg["max_persisted_width"]!=4:
        raise AssertionError("R48S_R48O_REGRESSION_DRIFT")
    records=[]; seen=set(); metrics={"cases_seen":0,"semantic_or_nonfixpoint":0,"reachable_fixpoints":0,"duplicate_fixpoints":0,"unique_residuals_evaluated":0,"covered_residuals":0,"width4_obstructions":0,"total_candidate_probes":0}
    for n,ratio,seed in CASES:
        metrics["cases_seen"]+=1
        raw=canon(r33.deterministic_random_3cnf(int(seed),n=int(n),ratio=float(ratio)))
        validate_exact3(raw)
        case={"n":int(n),"ratio":float(ratio),"seed":int(seed),"input_hash":formula_hash(raw),"input_CLV":list(clv(raw))}
        reached=r47f.reachable_fixpoint(raw)
        if reached is None:
            metrics["semantic_or_nonfixpoint"]+=1; records.append({**case,"genuine_residual":False,"covered":None}); continue
        metrics["reachable_fixpoints"]+=1
        root=canon(reached["formula"]); rh=formula_hash(root)
        if rh in seen:
            metrics["duplicate_fixpoints"]+=1; records.append({**case,"genuine_residual":True,"duplicate_root_hash":rh,"covered":None}); continue
        seen.add(rh); metrics["unique_residuals_evaluated"]+=1
        result=run_root(root,case)
        result["reachability_trajectory"]=reached["trajectory"]
        records.append(result); metrics["total_candidate_probes"]+=int(result["candidate_probe_count"])
        if result["covered"]:
            metrics["covered_residuals"]+=1
        else:
            metrics["width4_obstructions"]+=1; break
    obstruction=next((x for x in records if x.get("covered") is False),None)
    if obstruction is not None:
        verdict="STRONGER_NO_VARIABLE_DECREASING_CANDIDATE_FOUND" if obstruction["obstruction"]["kind"]=="NO_VARIABLE_DECREASING_CANDIDATE" else "EXPLICIT_NATURAL_REACHABLE_WIDTH4_OBSTRUCTION_FOUND"
    elif metrics["unique_residuals_evaluated"]==0:
        verdict="NO_GENUINE_RESIDUALS_IN_FROZEN_SIZE_LADDER__FINITE_ONLY"
    else:
        verdict="ALL_GENUINE_RESIDUALS_IN_FROZEN_SIZE_LADDER_COVERED_BY_WIDTH4__FINITE_ONLY"
    maxw=max((x.get("max_persisted_width",0) for x in records if x.get("covered") is not None),default=None)
    hardest=max((x for x in records if x.get("covered") is True),key=lambda x:(x["candidate_probe_count"],len(x["selected_path"]),tuple(x["root_CLV"]),x["root_hash"]),default=None)
    return {"gate":GATE,"verdict":verdict,"frozen_cases":[{"n":n,"ratio":r,"seed":s} for n,r,s in CASES],"R48O_regression":{"root_hash":reg["root"]["hash"],"selected_pivots":[x["var"] for x in reg["selected_path"]],"max_persisted_width":reg["max_persisted_width"],"SAT_root_reconstruction_pass":reg["terminal"]["SAT_root_reconstruction"]["pass"]},"metrics":metrics,"maximum_observed_persisted_width":maxw,"hardest_covered_residual":hardest,"first_obstruction":obstruction,"records":records,"interpretation":{"finite_ladder_only":True,"success_proves_universal_W4":False,"one_obstruction_refutes_universal_W4_for_frozen_grammar":True},"firewall":{"UNIVERSAL_WIDTH_4_COVERAGE":"NOT_PROVED_UNLESS_REFUTED_BY_THIS_GATE","UNIVERSAL_CONSTANT_WIDTH_COVERAGE":"NOT_PROVED","UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE":"OPEN","O4_UNIVERSAL_COVERAGE":"OPEN","SAT_IN_P":"NOT_PROVED","P_EQ_NP":"NOT_PROVED","P_NE_NP":"NOT_PROVED","P_VS_NP":"OPEN","TRUMP_finished":False}}


def main():
    p=argparse.ArgumentParser();p.add_argument("--output");a=p.parse_args();d=run()
    if a.output:
        path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    o=d["first_obstruction"];h=d["hardest_covered_residual"]
    print(json.dumps({"gate":d["gate"],"verdict":d["verdict"],"metrics":d["metrics"],"maximum_observed_persisted_width":d["maximum_observed_persisted_width"],"hardest":None if h is None else {"case":h["case"],"root_hash":h["root_hash"],"root_CLV":h["root_CLV"],"selected_pivots":h["selected_pivots"],"candidate_probe_count":h["candidate_probe_count"],"max_persisted_width":h["max_persisted_width"]},"obstruction":None if o is None else {"case":o["case"],"root_hash":o["root_hash"],"root_CLV":o["root_CLV"],"kind":o["obstruction"]["kind"],"state_hash":o["obstruction"]["state_hash"],"state_CLV":o["obstruction"]["state_CLV"],"state_max_width":o["obstruction"]["state_max_width"]},"firewall":d["firewall"]},sort_keys=True))

if __name__=="__main__":main()
