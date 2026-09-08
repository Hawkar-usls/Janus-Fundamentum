from __future__ import annotations

import argparse
import json
from pathlib import Path

PREREG_PATH=Path("research/JANUS_TRUMP_R50G25BA15_PREREGISTRATION.json")
EXPECTED_PREREG="f39af29741c62b6e04d4a665eb6697ef4c461d68"
METRICS=("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained","live_clause_peak","R_peak","B_peak","E_peak","W_peak")

def main(result_path,verify_path,out_path):
    prereg=json.loads(PREREG_PATH.read_text());r=json.loads(Path(result_path).read_text());v=json.loads(Path(verify_path).read_text())
    required=list(prereg["required_passes"]);base=required[:-2]
    exact_names=(len(required)==40 and len(set(required))==40 and required[-2:]==["INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"])
    prereg_ok=(prereg.get("state")=="FROZEN_BEFORE_IMPLEMENTATION" and prereg.get("preseal_completeness_firewall",{}).get("required_named_pass_count")==40 and prereg.get("preseal_completeness_firewall",{}).get("law")=="CI GREEN != SCIENTIFIC SEAL" and r.get("preregistration_commit")==EXPECTED_PREREG)
    rb=r.get("obligations",{});vb=v.get("obligations",{})
    names_ok=(len(rb)==len(base) and len(vb)==len(base) and set(rb)==set(base) and set(vb)==set(base))
    passes={name:(1 if rb.get(name)==1 and vb.get(name)==1 else 0) for name in base}
    independent_ok=(v.get("status")=="PASS" and v.get("error_count")==0 and v.get("v_independent_verifier")==1 and v.get("P_BA15")==1 and v.get("implementation_imported") is False)
    passes["INDEPENDENT_REPLAY_PASS"]=1 if independent_ok else 0
    source=r.get("source_transport",{});pos=source.get("positive_local",{});neg=source.get("negative_local",{})
    local_metrics=all(k in pos and k in neg for k in METRICS)
    exact_local=(pos.get("raw_pairs")==2320 and pos.get("tautological_pairs")==782 and pos.get("non_tautological_pairs")==1538 and pos.get("duplicates")==78 and pos.get("retained")==414 and pos.get("R_peak")==17 and pos.get("B_peak")==9 and pos.get("W_peak")==13 and neg.get("raw_pairs")==2001 and neg.get("tautological_pairs")==658 and neg.get("non_tautological_pairs")==1343 and neg.get("duplicates")==57 and neg.get("retained")==383 and neg.get("R_peak")==17 and neg.get("B_peak")==9 and neg.get("W_peak")==13)
    boundary_ok=True
    for b in r.get("actual_boundary_work",[]):
        p,n,rr=b["p"],b["n"],b["r"];x=b["ledgers"]["B_ACTUAL_X_ELIMINATION"];y=b["ledgers"]["C_ACTUAL_Y_ELIMINATION"]
        boundary_ok &= all(k in x and k in y for k in METRICS) and x["raw_pairs"]==p and x["retained"]==p and y["raw_pairs"]==p*n and y["retained"]==p*n and y["W_peak"]==min(p,n)+1
        boundary_ok &= len(b.get("b_ledgers",[]))==n
        for j,d in enumerate(b.get("b_ledgers",[])):
            q=n+j*(rr-1);Et=n*(p+rr)+j*(p*rr-p-rr)
            boundary_ok &= all(k in d for k in METRICS) and d["raw_pairs"]==p*rr and d["retained"]==p*rr and d["E_peak"]==Et+p*rr and d["W_peak"]==min(p+1,q+rr)
    result_ok=(r.get("failure_count")==0 and r.get("base_pass_count")==38 and r.get("base_required_count")==38 and r.get("outcome")=="BA15-A_PARAMETERIZED_TWO_CONSECUTIVE_GENERATION_MULTIPLICATION_CERTIFIED" and r.get("P_BA15")==0 and r.get("independent_replay_pending") is True and r.get("preseal_completeness_pending") is True)
    scope_ok=(r.get("self_sustaining_support_certified") is False and r.get("derived_future_support_certified") is False and r.get("repeated_multiplication_started") is False and r.get("next_gate_started") is False and r.get("BA16_started") is False and r.get("P_VS_NP")=="OPEN" and r.get("SAT_IN_P")=="NOT_PROVED" and r.get("TRUMP_finished") is False)
    scaffold=r.get("source_scaffold_firewall",{});scaffold_ok=(scaffold.get("pass") is True and scaffold.get("law")=="SUCCESSIVE_MULTIPLICATION != EXPONENTIAL_BLOWUP" and scaffold.get("self_sustaining_cascade_certified") is False)
    preseal_ok=(exact_names and prereg_ok and names_ok and independent_ok and local_metrics and exact_local and boundary_ok and result_ok and scope_ok and scaffold_ok and all(passes[x]==1 for x in required[:-1]))
    passes["PRESEAL_COMPLETENESS_PASS"]=1 if preseal_ok else 0
    all_ok=(len(passes)==40 and set(passes)==set(required) and all(passes[x]==1 for x in required))
    out={"gate":"R50G25BA15_PARAMETERIZED_TWO_CONSECUTIVE_GENERATION_FILL_MULTIPLICATION","kind":"PRESEAL_OBLIGATION_COMPLETION_HARDENED_V2","frozen_preregistration_commit":EXPECTED_PREREG,"theorem_or_scope_changed":False,"required_passes":passes,"required_pass_names":required,"required_pass_count":len(passes),"all_required_passes":all_ok,
      "report_contract":{"ordered_required_pass_names_copied_from_frozen_prereg":required,"builder_and_verifier_exact_name_sets":names_ok,"serialized_mapping_order_is_not_authority":True,"all_ten_metrics_per_actual_ledger_present":boundary_ok,"local_BA4_kernels_exact":exact_local,"source_scaffold_firewall_present":scaffold_ok,"CI_GREEN_not_sufficient":True},
      "gap_predecessor":{"run_id":34279236625,"gap_receipt_commit":"02ed464b645dbc1c95043115863ec57d35986339","status":"UNSEALED_REPORTING_ORDER_GAP"},
      "independent_replay_status":v.get("status"),"P_BA15_FINAL":1 if all_ok else 0,"status":"PASS" if all_ok else "FAIL","self_sustaining_support_certified":False,"BA16_started":False,"firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if not all_ok:raise SystemExit("BA15 hardened preseal completion failed: "+",".join(x for x in required if passes.get(x)!=1))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True);a=ap.parse_args();main(a.result,a.verify,a.out)
