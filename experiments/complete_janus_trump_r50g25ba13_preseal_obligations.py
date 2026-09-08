from __future__ import annotations

import argparse
import json
from pathlib import Path

PREREG_PATH = Path("research/JANUS_TRUMP_R50G25BA13_PREREGISTRATION.json")
EXPECTED_PREREG_COMMIT = "f1c2a7dc0c7924c96132fa9d14d8f42ac8ec2c5a"
METRICS = ("raw_pairs","tautological_pairs","non_tautological_pairs","duplicates","retained",
           "live_clause_peak","R_peak","B_peak","E_peak","W_peak")


def main(result_path, verify_path, out_path):
    prereg=json.loads(PREREG_PATH.read_text())
    r=json.loads(Path(result_path).read_text())
    v=json.loads(Path(verify_path).read_text())

    required=list(prereg["required_passes"])
    exact_required_count=(len(required)==30 and len(set(required))==30)
    prereg_identity=(r.get("preregistration_commit")==EXPECTED_PREREG_COMMIT and prereg.get("state")=="FROZEN_BEFORE_IMPLEMENTATION")
    expected_tail=required[-2:]==["INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"]
    base_required=required[:-2]
    builder_keys=set(r.get("obligations",{}))
    verifier_keys=set(v.get("obligations",{}))
    names_complete=(builder_keys==set(base_required) and verifier_keys==set(base_required))

    passes={}
    for name in base_required:
        passes[name]=1 if (r["obligations"].get(name)==1 and v["obligations"].get(name)==1) else 0

    independent_ok=(v.get("status")=="PASS" and v.get("error_count")==0 and v.get("v_independent_verifier")==1 and v.get("P_BA13")==1)
    passes["INDEPENDENT_REPLAY_PASS"]=1 if independent_ok else 0

    work=r.get("actual_carrier_work",{})
    work_names=["A_SOURCE_CARRIER_TRANSPORT","B_ACTUAL_X_ELIMINATION","C_ACTUAL_Y_ELIMINATION","D_ACTUAL_Z_ELIMINATION"]
    work_complete=(list(work.keys())==work_names or set(work.keys())==set(work_names))
    metrics_complete=work_complete and all(all(k in work[name] for k in METRICS) for name in work_names)

    A=work.get("A_SOURCE_CARRIER_TRANSPORT",{})
    B=work.get("B_ACTUAL_X_ELIMINATION",{})
    C=work.get("C_ACTUAL_Y_ELIMINATION",{})
    D=work.get("D_ACTUAL_Z_ELIMINATION",{})
    exact_work=(
        A.get("raw_pairs")==10324 and A.get("tautological_pairs")==3414 and A.get("non_tautological_pairs")==6910
        and A.get("duplicates")==306 and A.get("retained")==1946 and A.get("R_peak")==85 and A.get("B_peak")==45
        and A.get("E_peak")==5 and A.get("W_peak")==13
        and B.get("raw_pairs")==1 and B.get("retained")==1 and B.get("E_peak")==6 and B.get("W_peak")==2
        and C.get("raw_pairs")==1 and C.get("retained")==1 and C.get("E_peak")==5 and C.get("W_peak")==2
        and D.get("raw_pairs")==2 and D.get("retained")==2 and D.get("E_peak")==5 and D.get("W_peak")==2
    )

    result_complete=(
        r.get("failure_count")==0 and r.get("base_pass_count")==28 and r.get("base_required_count")==28
        and r.get("outcome")=="BA13-A_MINIMAL_GENERATION3_RESOLUTION_FANOUT_CASCADE_CERTIFIED"
        and r.get("P_BA13")==0 and r.get("independent_replay_pending") is True
        and r.get("preseal_completeness_pending") is True
    )
    scope_ok=(
        r.get("generic_depth4_started") is False and r.get("parameterized_depth3_started") is False
        and r.get("repeated_multiplication_started") is False and r.get("next_gate_started") is False
        and r.get("BA14_started") is False and r.get("P_VS_NP")=="OPEN"
        and r.get("SAT_IN_P")=="NOT_PROVED" and r.get("TRUMP_finished") is False
    )
    prereg_report_contract=(
        prereg.get("preseal_completeness_firewall",{}).get("required_named_pass_count")==30
        and prereg.get("preseal_completeness_firewall",{}).get("law")=="CI GREEN != SCIENTIFIC SEAL"
    )

    preseal_ok=(
        exact_required_count and expected_tail and prereg_identity and names_complete and metrics_complete and exact_work
        and result_complete and scope_ok and prereg_report_contract
        and all(passes[name]==1 for name in required[:-1])
    )
    passes["PRESEAL_COMPLETENESS_PASS"]=1 if preseal_ok else 0

    all_ok=(list(passes.keys())==required and len(passes)==30 and all(passes[name]==1 for name in required))
    out={
      "gate":"R50G25BA13_MINIMAL_GENERATION3_RESOLUTION_FANOUT_CASCADE",
      "kind":"PRESEAL_OBLIGATION_COMPLETION",
      "frozen_preregistration_commit":EXPECTED_PREREG_COMMIT,
      "preregistration_file":str(PREREG_PATH),
      "theorem_or_scope_changed":False,
      "required_passes":passes,
      "required_pass_names":required,
      "required_pass_count":len(passes),
      "all_required_passes":all_ok,
      "report_contract":{
        "exact_prereg_named_list_replayed":list(passes.keys())==required,
        "builder_and_verifier_base_names_exact":names_complete,
        "four_actual_work_ledgers_present":work_complete,
        "all_ten_metrics_per_ledger_present":metrics_complete,
        "exact_preregistered_transport_and_pivot_targets_replayed":exact_work,
        "CI_GREEN_not_sufficient":True
      },
      "actual_carrier_work":work,
      "independent_replay_status":v.get("status"),
      "P_BA13_FINAL":1 if all_ok else 0,
      "status":"PASS" if all_ok else "FAIL",
      "BA14_started":False,
      "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if not all_ok:
        missing=[k for k in required if passes.get(k)!=1]
        raise SystemExit("BA13 preseal completion failed: "+",".join(missing))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--result",required=True); ap.add_argument("--verify",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); main(a.result,a.verify,a.out)
