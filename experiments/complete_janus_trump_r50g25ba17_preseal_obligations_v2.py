from __future__ import annotations
import argparse,json
from pathlib import Path

PREREG="688594a8a450b567603a2abbead7b3b885eff0c0"
EXPECTED=[
"STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS","BA16_F14_IMMUTABILITY_PASS",
"SOURCE_WIDTH_PASS","T_Z_WIDTH_PASS","E_Z_WIDTH_PASS","T_X_WIDTH_PASS","E_X_WIDTH_PASS",
"T_Y_WIDTH_PASS","E_Y_WIDTH_PASS","T_B1_WIDTH_PASS","LATER_B_MONOTONICITY_PASS",
"EARLIER_STAGE_DOMINATION_PASS","CORRECTED_GLOBAL_WIDTH_PASS","PIECEWISE_EQUIVALENCE_PASS",
"F14_RECOVERY_PASS","PARAMETER_REGIME_AUDIT_PASS","COMPLETE_BIPARTITE_WIDTH_LEMMA_PASS",
"COMPLETE_MULTIPARTITE_WIDTH_LEMMA_PASS","FULL_BA4_LOWER_BOUND_PASS",
"FULL_BA4_UPPER_COMPOSITION_PASS","ACTUAL_BA16_REPLAY_PASS","WIDTH_CERTIFICATE_PASS",
"COMPLEXITY_PASS","INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"]

def main(prereg_path,result_path,verify_path,out_path):
    P=json.loads(Path(prereg_path).read_text())
    R=json.loads(Path(result_path).read_text())
    V=json.loads(Path(verify_path).read_text())
    errors=[]
    def ck(c,m):
        if not c: errors.append(m)

    req=P["required_pass_names"]
    ck(P["state"]=="FROZEN_BEFORE_IMPLEMENTATION","prereg state")
    ck(P["required_pass_count"]==26,"prereg count")
    ck(req==EXPECTED,"prereg exact ordered names")
    ck(len(set(req))==26,"prereg names unique")
    ck(R["preregistration_commit"]==PREREG,"prereg commit")

    # JSON mapping order is serialization metadata, not scientific authority.
    # The authoritative order is the frozen prereg list above. For the builder
    # mapping, require exact name SET, exact cardinality, and exact values.
    ck(len(R["obligations"])==26,"result obligation cardinality")
    ck(set(R["obligations"])==set(EXPECTED),"result exact name set")
    for k in EXPECTED[:-2]:
        ck(R["obligations"][k]==1,f"base obligation {k}")
    ck(R["obligations"]["INDEPENDENT_REPLAY_PASS"]==0,"independent pending must be zero in builder")
    ck(R["obligations"]["PRESEAL_COMPLETENESS_PASS"]==0,"preseal pending must be zero in builder")

    ck(V["status"]=="PASS" and V["error_count"]==0 and V["P_BA17"]==1 and V["implementation_imported"] is False,"independent verifier")
    H=R["historical_immutability"]
    ck(H["BA16_status"]=="MIXED" and H["BA16_F14"]=="PRESERVED" and H["BA16_QUOTIENT_WIDTH_PASS"]==0 and H["P_BA16_A"]==0 and H["P_BA16_MIXED"]==1 and H["retroactive_flip"] is False,"BA16 immutability")
    ck(R["theorem"]["W_Q"]=="max(min(n+1,p+r+1),p+n+r-max(p,n,r))","W_Q")
    ck(R["theorem"]["full_BA4_bounds"]=="W_Q <= W_full <= max(13,W_Q)","full bounds")

    status="PASS" if not errors else "FAIL"
    final={k:1 for k in EXPECTED} if status=="PASS" else {}
    out={
      "gate":"R50G25BA17_PRESEAL_COMPLETION_HARDENED_V2",
      "kind":"EXACT_PREREG_NAME_SET_AND_FROZEN_ORDER_AUDIT",
      "status":status,
      "errors":errors,
      "required_pass_names":EXPECTED,
      "required_pass_count":26,
      "required_passes":final,
      "all_required_passes":status=="PASS",
      "P_BA17_FINAL":1 if status=="PASS" else 0,
      "BA16_F14_preserved":True,
      "P_BA16_A":0,
      "P_BA16_MIXED":1,
      "report_contract":{
        "frozen_prereg_order_is_authority":True,
        "builder_mapping_exact_name_set_required":True,
        "serialized_mapping_order_is_not_authority":True
      },
      "gap_predecessor":{
        "run_id":34286386953,
        "status":"BUILDER_AND_INDEPENDENT_PASS_BUT_UNSEALED_REPORTING_ORDER_GAP",
        "scientific_authority":False
      },
      "CI_GREEN_NE_SCIENTIFIC_SEAL":True
    }
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors: raise SystemExit("; ".join(errors))

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--prereg",required=True);a.add_argument("--result",required=True);a.add_argument("--verify",required=True);a.add_argument("--out",required=True)
    z=a.parse_args();main(z.prereg,z.result,z.verify,z.out)
