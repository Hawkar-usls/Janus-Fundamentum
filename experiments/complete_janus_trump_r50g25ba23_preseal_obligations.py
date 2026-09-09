from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

PREREG_COMMIT="592a24b603c10213ab110d5d27b1308b0fc69656"
IMPLEMENTATION_COMMIT="c392db4372ba7aa72c87af00cc279aba60ead01d"
VERIFIER_COMMIT="710feabea9d536daef1acba8663de2a8879e05ae"
GATE="R50G25BA23_EXPONENTIAL_ITERATED_DGDBO_RESIDUAL_STATE_GROWTH"


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--prereg",default="research/JANUS_TRUMP_R50G25BA23_PREREGISTRATION.json");ap.add_argument("--result",default="ba23_result.json");ap.add_argument("--verify",default="ba23_verify.json");ap.add_argument("--out",default="ba23_completion.json");args=ap.parse_args()
    prereg=json.loads(Path(args.prereg).read_text());result=json.loads(Path(args.result).read_text());verify=json.loads(Path(args.verify).read_text())
    required=prereg["required_passes"]
    errors=[]
    if prereg.get("gate")!=GATE or prereg.get("state")!="FROZEN_BEFORE_IMPLEMENTATION": errors.append("prereg identity/state mismatch")
    if prereg.get("required_pass_count")!=len(required): errors.append("prereg count mismatch")
    if len(required)!=24 or len(set(required))!=24: errors.append("expected exactly 24 unique obligations")
    bm=result.get("pass_map",{})
    if set(bm)!=set(required): errors.append("builder exact-name set mismatch")
    base=required[:-2]
    if not all(bm.get(k)==1 for k in base): errors.append("builder base obligation failed")
    if bm.get("INDEPENDENT_REPLAY_PASS")!=0 or bm.get("PRESEAL_COMPLETENESS_PASS")!=0: errors.append("builder prematurely sealed")
    if verify.get("status")!="PASS" or verify.get("v_independent_verifier")!=1 or verify.get("P_BA23")!=1: errors.append("independent verifier failed")
    if verify.get("implementation_imported") is not False: errors.append("verifier imported implementation")
    if verify.get("errors"): errors.append("verifier errors present")
    if set(verify.get("required_pass_names",[]))!=set(required): errors.append("verifier obligation set mismatch")
    cand=result.get("scientific_result_candidate",{})
    expected={"active_state_law":"A_t=2^t","final_state_law":"A_m=2^m","satisfiable_final_states":"2^m-1","cumulative_level_states":"2^(m+1)-1","direct_model_count":"3^m-2^m"}
    for k,v in expected.items():
        if cand.get(k)!=v: errors.append(f"candidate mismatch {k}")
    large=result.get("large_symbolic_diagnostic",{})
    if large.get("states_materialized")!=0 or large.get("generic_proof_uses_enumeration") is not False: errors.append("generic materialization firewall failed")
    if result.get("no_materialization",{}).get("generic_2_pow_m_state_enumeration")!=0: errors.append("generic 2^m enumeration hidden")
    if result.get("BA24_started") is not False: errors.append("BA24 started")
    if result.get("firewall",{}).get("P_VS_NP")!="OPEN" or result.get("firewall",{}).get("SAT_IN_P")!="NOT_PROVED": errors.append("complexity firewall changed")
    final_map={k:int(bm[k]) for k in required}
    final_map["INDEPENDENT_REPLAY_PASS"]=int(not errors)
    final_map["PRESEAL_COMPLETENESS_PASS"]=int(not errors)
    if errors:
        final_pass=sum(final_map.values());P=0;status="FAIL"
    else:
        assert all(final_map[k]==1 for k in required)
        final_pass=len(required);P=1;status="PASS"
    completion={
      "gate":GATE,"status":status,"required_pass_count":len(required),"required_passes":required,
      "pass_map":final_map,"pass_count":final_pass,"P_BA23_FINAL":P,
      "preregistration_commit":PREREG_COMMIT,"implementation_commit":IMPLEMENTATION_COMMIT,"independent_verifier_commit":VERIFIER_COMMIT,
      "result_sha256":sha_file(args.result),"independent_verify_sha256":sha_file(args.verify),
      "scientific_summary":{
        "active_state_law":"2^t","final_state_law":"2^m","input_scale":"Theta(m)",
        "direct_model_count":"3^m-2^m","exact_same_level_merge":"IMPOSSIBLE_BY_SEMANTIC_DISTINCTNESS",
        "order_robustness":"SYMBOLICALLY_PROVED","strategy_barrier":"EXPLICIT_ITERATED_BA22_RESIDUAL_STATE_COMPILATION_NOT_POLYNOMIAL_STATE_ON_FROZEN_FAMILY",
        "other_symbolic_compression":"OPEN_NOT_RULED_OUT"
      },
      "CI_GREEN_NE_SCIENTIFIC_SEAL":True,"falsifiers":[] if not errors else errors,
      "BA24_started":False,"firewall":{"SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN","P_equals_NP_proved":False,"P_not_equals_NP_proved":False}
    }
    Path(args.out).write_text(json.dumps(completion,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"pass_count":final_pass,"required":len(required),"P_BA23_FINAL":P},sort_keys=True))
    if errors: raise SystemExit("; ".join(errors))

if __name__=="__main__": main()
