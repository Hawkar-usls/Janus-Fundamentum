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
    P=json.loads(Path(prereg_path).read_text());R=json.loads(Path(result_path).read_text());V=json.loads(Path(verify_path).read_text());errors=[]
    def ck(c,m):
        if not c:errors.append(m)
    req=P["required_pass_names"];ck(P["state"]=="FROZEN_BEFORE_IMPLEMENTATION","prereg state");ck(P["required_pass_count"]==26 and req==EXPECTED and len(set(req))==26,"prereg exact names");ck(R["preregistration_commit"]==PREREG,"prereg commit");ck(list(R["obligations"].keys())==EXPECTED,"result exact name order");ck(set(R["obligations"])==set(EXPECTED),"result exact name set")
    for k in EXPECTED[:-2]:ck(R["obligations"][k]==1,f"base obligation {k}")
    ck(R["obligations"]["INDEPENDENT_REPLAY_PASS"]==0,"independent pending must be zero in builder");ck(R["obligations"]["PRESEAL_COMPLETENESS_PASS"]==0,"preseal pending must be zero in builder");ck(V["status"]=="PASS" and V["error_count"]==0 and V["P_BA17"]==1 and V["implementation_imported"] is False,"independent verifier")
    H=R["historical_immutability"];ck(H["BA16_status"]=="MIXED" and H["BA16_F14"]=="PRESERVED" and H["P_BA16_A"]==0 and H["P_BA16_MIXED"]==1,"BA16 immutability");ck(R["theorem"]["W_Q"]=="max(min(n+1,p+r+1),p+n+r-max(p,n,r))","W_Q");ck(R["theorem"]["full_BA4_bounds"]=="W_Q <= W_full <= max(13,W_Q)","full bounds")
    final={k:1 for k in EXPECTED};status="PASS" if not errors else "FAIL";out={"gate":"R50G25BA17_PRESEAL_COMPLETION","kind":"EXACT_PREREG_NAME_AUDIT","status":status,"errors":errors,"required_pass_names":EXPECTED,"required_pass_count":26,"required_passes":final if status=="PASS" else {},"all_required_passes":status=="PASS","P_BA17_FINAL":1 if status=="PASS" else 0,"BA16_F14_preserved":True,"P_BA16_A":0,"P_BA16_MIXED":1,"CI_GREEN_NE_SCIENTIFIC_SEAL":True};Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))
    if errors:raise SystemExit("; ".join(errors))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--prereg",required=True);a.add_argument("--result",required=True);a.add_argument("--verify",required=True);a.add_argument("--out",required=True);z=a.parse_args();main(z.prereg,z.result,z.verify,z.out)
