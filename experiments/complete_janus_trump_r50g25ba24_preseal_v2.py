from __future__ import annotations
import argparse, json
from pathlib import Path

GATE="R50G25BA24_HYBRID_DBO_FOREIGN_CNF_INTERFACE_DP"

def run(prereg_path,result_path,verify_path):
    prereg=json.loads(Path(prereg_path).read_text())
    result=json.loads(Path(result_path).read_text())
    verify=json.loads(Path(verify_path).read_text())
    names=list(prereg["required_passes"])
    assert prereg["gate"]==GATE and prereg["state"]=="FROZEN_BEFORE_IMPLEMENTATION"
    assert result["gate"]==GATE and verify["gate"]==GATE
    assert len(names)==len(set(names))==38
    assert names[-2:]==["INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"]
    assert set(result["pass_map"])==set(names)
    assert all(int(result["pass_map"][k])==1 for k in names[:-2])
    assert int(result["pass_map"]["INDEPENDENT_REPLAY_PASS"])==0
    assert int(result["pass_map"]["PRESEAL_COMPLETENESS_PASS"])==0
    assert verify["status"]=="PASS" and verify["P_BA24_independent"]==1
    assert verify["implementation_imported"] is False
    assert verify.get("hardened_after_run1_harness_gap") is True
    assert not verify["falsifiers"] and not result["falsifiers"]
    assert result["materialization_counters"]=={"BA23_subset_residual_states":0,"DGDBO_objects":0,"prime_implicate_records":0}
    large=result["diagnostics"]["ba23"]["large"]
    assert large["kappa"]==3 and large["max_table_states"]<=16
    assert large["subset_states_materialized"]==0
    assert large["dp_count"]==large["expected"]
    assert result["diagnostics"]["source"]["pass"] and result["diagnostics"]["source"]["cases"]==18
    assert verify["source_reconstruction"]["pass"] and verify["source_reconstruction"]["cases"]==12
    assert result["firewall"]["UNBOUNDED_KAPPA_POLYNOMIAL_TIME"]=="NOT_CLAIMED"
    assert result["firewall"]["P_VS_NP"]=="OPEN"
    final={k:int(result["pass_map"][k]) for k in names}
    final["INDEPENDENT_REPLAY_PASS"]=1
    final["PRESEAL_COMPLETENESS_PASS"]=1
    assert all(final[k]==1 for k in names)
    return {
        "gate":GATE,
        "status":"PASS",
        "required_names":names,
        "required_passes":f"{sum(final.values())}/{len(names)}",
        "pass_map":final,
        "P_BA24_FINAL":1,
        "independent_replay":"PASS",
        "implementation_imported":False,
        "hardened_after_run1_harness_gap":True,
        "scientific_label":"BA24_A_PROOF_CARRYING_HYBRID_DBO_FOREIGN_CNF_BLOCK_INCIDENCE_FPT_PROCESSING_CERTIFIED",
        "materialization_counters":result["materialization_counters"],
        "ba23_control":{
            "m64_kappa":large["kappa"],
            "max_table_states":large["max_table_states"],
            "model_count":large["dp_count"],
            "expected_model_count":large["expected"],
            "subset_states_materialized":large["subset_states_materialized"]
        },
        "source_reconstruction":{"builder_cases":18,"independent_cases":12},
        "runtime":result["scientific_result_candidate"]["runtime"],
        "decomposition_scope":result["scientific_result_candidate"]["decomposition_scope"],
        "CI_GREEN_NE_SCIENTIFIC_SEAL":True,
        "falsifiers":[],
        "firewall":result["firewall"]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",default="research/JANUS_TRUMP_R50G25BA24_PREREGISTRATION.json")
    ap.add_argument("--result",default="ba24_result.json")
    ap.add_argument("--verify",default="ba24_verify_v2.json")
    ap.add_argument("--out",default="ba24_completion_v2.json")
    a=ap.parse_args()
    out=run(a.prereg,a.result,a.verify)
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"passes":out["required_passes"],"P_BA24_FINAL":out["P_BA24_FINAL"]},sort_keys=True))
if __name__=="__main__": main()
