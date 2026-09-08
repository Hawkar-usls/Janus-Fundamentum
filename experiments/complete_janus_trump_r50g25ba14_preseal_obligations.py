from __future__ import annotations
import argparse,json
from pathlib import Path

PREREG_PATH=Path("research/JANUS_TRUMP_R50G25BA14_PREREGISTRATION.json")
EXPECTED_PREREG_COMMIT="3bd91d3c22158375704adb25421da66ea38330b0"
METRICS=("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained","live_clause_peak","R_peak","B_peak","E_peak","W_peak")

def main(result_path,verify_path,out_path):
    prereg=json.loads(PREREG_PATH.read_text()); r=json.loads(Path(result_path).read_text()); v=json.loads(Path(verify_path).read_text())
    required=list(prereg["required_passes"]); exact_names=(len(required)==35 and len(set(required))==35); tail_ok=required[-2:]==["INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"]; base=required[:-2]
    prereg_identity=(prereg.get("state")=="FROZEN_BEFORE_IMPLEMENTATION" and r.get("preregistration_commit")==EXPECTED_PREREG_COMMIT)
    names_complete=(set(r.get("obligations",{}))==set(base) and set(v.get("obligations",{}))==set(base)); passes={}
    for name in base: passes[name]=1 if r["obligations"].get(name)==1 and v["obligations"].get(name)==1 else 0
    independent_ok=(v.get("status")=="PASS" and v.get("P_BA14_independent")==1 and v.get("pass_count")==33 and v.get("required_count")==33 and v.get("imports_BA14_implementation") is False); passes["INDEPENDENT_REPLAY_PASS"]=1 if independent_ok else 0
    st=r.get("source_transport",{}); gp=st.get("generic_per_transition",{})
    source_exact=(st.get("local_targets_pass") is True and gp.get("raw_pairs")=="2320p+2001(r+2)" and gp.get("tautological_pairs")=="782p+658(r+2)" and gp.get("non_tautological_pairs")=="1538p+1343(r+2)" and gp.get("duplicates")=="78p+57(r+2)" and gp.get("retained")=="414p+383(r+2)" and gp.get("R_peak")=="17(p+r+2)" and gp.get("B_peak")=="9(p+r+2)" and gp.get("E_peak")=="p+r+2" and gp.get("W_peak")==13 and st.get("generic_g_multiplier")=="g-1")
    boundaries=r.get("actual_boundary_work",[]); boundary_exact=True
    for b in boundaries:
        p=int(b["p"]); rr=int(b["r"]); W=b["ledgers"]; B=W["B_ACTUAL_X_ELIMINATION"]; C=W["C_ACTUAL_Y_ELIMINATION"]; D=W["D_ACTUAL_Z_ELIMINATION"]
        boundary_exact &= all(all(k in L for k in METRICS) for L in (B,C,D))
        boundary_exact &= (B["raw_pairs"]==p and B["tautological_pairs"]==0 and B["non_tautological_pairs"]==p and B["duplicates"]==0 and B["retained"]==p and B["live_clause_peak"]==p+rr+2 and B["R_peak"]==p+rr+2 and B["B_peak"]==p and B["E_peak"]==2*p+rr+2 and B["W_peak"]==2)
        boundary_exact &= (C["raw_pairs"]==p and C["tautological_pairs"]==0 and C["non_tautological_pairs"]==p and C["duplicates"]==0 and C["retained"]==p and C["live_clause_peak"]==p+rr+1 and C["R_peak"]==p+rr+1 and C["B_peak"]==p and C["E_peak"]==2*p+rr+1 and C["W_peak"]==2)
        boundary_exact &= (D["raw_pairs"]==p*rr and D["tautological_pairs"]==0 and D["non_tautological_pairs"]==p*rr and D["duplicates"]==0 and D["retained"]==p*rr and D["live_clause_peak"]==max(p+rr,p*rr) and D["R_peak"]==p+rr and D["B_peak"]==p*rr and D["E_peak"]==p+rr+p*rr and D["W_peak"]==min(p,rr)+1)
    boundary_coverage=sorted((int(b["p"]),int(b["r"])) for b in boundaries)==sorted(tuple(x) for x in prereg["holdouts"]["frozen"])
    work={"A_SOURCE_CARRIER_TRANSPORT":{"raw_pairs":"(g-1)[2320p+2001(r+2)]","tautological_pairs":"(g-1)[782p+658(r+2)]","non_tautological_pairs":"(g-1)[1538p+1343(r+2)]","duplicates":"(g-1)[78p+57(r+2)]","retained":"(g-1)[414p+383(r+2)]","live_clause_peak":gp.get("live_clause_peak"),"R_peak":"17(p+r+2)","B_peak":"9(p+r+2)","E_peak":"p+r+2","W_peak":13},
      "B_ACTUAL_X_ELIMINATION":{"raw_pairs":"p","tautological_pairs":0,"non_tautological_pairs":"p","duplicates":0,"retained":"p","live_clause_peak":"p+r+2","R_peak":"p+r+2","B_peak":"p","E_peak":"2p+r+2","W_peak":2},
      "C_ACTUAL_Y_ELIMINATION":{"raw_pairs":"p","tautological_pairs":0,"non_tautological_pairs":"p","duplicates":0,"retained":"p","live_clause_peak":"p+r+1","R_peak":"p+r+1","B_peak":"p","E_peak":"2p+r+1","W_peak":2},
      "D_ACTUAL_Z_ELIMINATION":{"raw_pairs":"p*r","tautological_pairs":0,"non_tautological_pairs":"p*r","duplicates":0,"retained":"p*r","live_clause_peak":"max(p+r,p*r)","R_peak":"p+r","B_peak":"p*r","E_peak":"p+r+p*r","W_peak":"min(p,r)+1"}}
    metrics_complete=all(all(k in L for k in METRICS) for L in work.values())
    result_complete=(r.get("failure_count")==0 and r.get("base_pass_count")==33 and r.get("base_required_count")==33 and r.get("outcome")=="BA14-A_PARAMETERIZED_GENERATION3_FINAL_FANOUT_CASCADE_CERTIFIED" and r.get("P_BA14")==0 and r.get("independent_replay_pending") is True and r.get("preseal_completeness_pending") is True and r.get("parameterized_depth3_certified_pre_replay") is True)
    scope_ok=(r.get("repeated_multiplication_started") is False and r.get("next_gate_started") is False and r.get("BA15_started") is False and r.get("P_VS_NP")=="OPEN" and r.get("SAT_IN_P")=="NOT_PROVED" and r.get("TRUMP_finished") is False)
    preseal_ok=(exact_names and tail_ok and prereg_identity and names_complete and independent_ok and source_exact and boundary_exact and boundary_coverage and metrics_complete and result_complete and scope_ok and all(passes[n]==1 for n in required[:-1])); passes["PRESEAL_COMPLETENESS_PASS"]=1 if preseal_ok else 0
    all_ok=(list(passes.keys())==required and len(passes)==35 and all(passes[n]==1 for n in required))
    out={"gate":"R50G25BA14_PARAMETERIZED_GENERATION3_FINAL_FANOUT_CASCADE","kind":"PRESEAL_OBLIGATION_COMPLETION","frozen_preregistration_commit":EXPECTED_PREREG_COMMIT,"preregistration_file":str(PREREG_PATH),"theorem_or_scope_changed":False,"required_passes":passes,"required_pass_names":required,"required_pass_count":len(passes),"all_required_passes":all_ok,
      "report_contract":{"exact_prereg_named_list_replayed":list(passes.keys())==required,"builder_and_verifier_base_names_exact":names_complete,"four_symbolic_actual_work_ledgers_present":set(work)=={"A_SOURCE_CARRIER_TRANSPORT","B_ACTUAL_X_ELIMINATION","C_ACTUAL_Y_ELIMINATION","D_ACTUAL_Z_ELIMINATION"},"all_ten_metrics_per_ledger_present":metrics_complete,"source_transport_targets_replayed":source_exact,"all_frozen_boundary_holdouts_cover_exact_p_p_pr_work":boundary_exact and boundary_coverage,"CI_GREEN_not_sufficient":True},
      "actual_carrier_work":work,"independent_replay_status":v.get("status"),"independent_diagnostics":{"source_rows":v.get("source_rows"),"stage1_rows":v.get("stage1_rows"),"stage2_rows":v.get("stage2_rows"),"final_rows":v.get("final_rows"),"full_BA4_source_model_cases":v.get("full_BA4_source_model_cases"),"full_BA4_reconstruction_cases":v.get("full_BA4_reconstruction_cases")},"P_BA14_FINAL":1 if all_ok else 0,"status":"PASS" if all_ok else "FAIL","repeated_multiplication_started":False,"BA15_started":False,"firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if not all_ok: raise SystemExit("BA14 preseal completion failed: "+",".join(n for n in required if passes.get(n)!=1))
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.verify,a.out)
