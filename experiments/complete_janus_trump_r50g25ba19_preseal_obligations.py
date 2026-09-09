from __future__ import annotations
import argparse,json
from pathlib import Path

PREREG_COMMIT="d243eebfb3b9facfaf9bd67ff34fcea3ac57a556"
EXPECTED=[
"STATUS_FIRST_PASS","PREREGISTRATION_BEFORE_IMPLEMENTATION_PASS",
"BA16_PRESERVATION_PASS","BA17_PRESERVATION_PASS","BA18_PRESERVATION_PASS",
"SECOND_SUPPORT_SYMBOLIC_PASS","SECOND_DERIVED_RS_SUPPORT_PASS","SECOND_SUPPORT_PROVENANCE_PASS",
"C_PIVOT_MIXED_POLARITY_PASS","ALL_POSITIVE_C_PARENTS_DERIVED_PASS","ALL_NEGATIVE_C_SUPPORT_DERIVED_PASS",
"GEN4_PNRS_RAW_PASS","GEN4_PNRS_DISTINCT_PASS","GEN4_BIJECTION_PASS","GEN4_ZERO_DUPLICATE_PASS",
"WIDTH3_TO_WIDTH4_PASS","SECOND_TAG_IDENTITY_PASS",
"SECOND_TAG_ERASURE_CONTROL_PASS","SECOND_TAG_IDENTIFICATION_CONTROL_PASS",
"DIRECT_FINAL_PROJECTION_PASS","FINAL_MODEL_COUNT_PASS","RECONSTRUCTION_PASS","FULL_ORIGINAL_CNF_VALIDATION_PASS",
"COMPOSITE_TRIPLE_SIGNATURE_PASS","NO_NEW_VARIABLE_IDENTITY_PASS",
"SOURCE_OUTPUT_FIREWALL_PASS","FINAL_WIDTH_PASS","SAFE_TRANSIENT_WIDTH_BOUND_PASS",
"SECOND_TERNARY_CARRIER_PASS","ACTUAL_WORK_ACCOUNTING_PASS","GENERIC_GPNRS_PASS",
"NO_MANUAL_INSERTION_PASS","INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"]

def main(prereg_path,result_path,verify_path,out_path):
    P=json.loads(Path(prereg_path).read_text())
    R=json.loads(Path(result_path).read_text())
    V=json.loads(Path(verify_path).read_text())
    errors=[]
    def ck(x,m):
        if not x:errors.append(m)
    req=P["required_pass_names"]
    ck(P["state"]=="FROZEN_BEFORE_IMPLEMENTATION","prereg state")
    ck(P["required_pass_count"]==34 and req==EXPECTED and len(set(req))==34,"exact prereg names/order")
    ck(R["preregistration_commit"]==PREREG_COMMIT,"prereg commit")
    ck(set(R["obligations"])==set(EXPECTED) and len(R["obligations"])==34,"result exact name set")
    for k in EXPECTED[:-2]:ck(R["obligations"].get(k)==1,f"builder obligation {k}")
    ck(R["obligations"].get("INDEPENDENT_REPLAY_PASS")==0,"builder independent pending")
    ck(R["obligations"].get("PRESEAL_COMPLETENESS_PASS")==0,"builder preseal pending")
    ck(R["falsifiers"]==[] and R["failed_builder_obligations"]==[],"builder scientific clean")
    ck(V["status"]=="PASS" and V["error_count"]==0 and V["P_BA19"]==1 and V["implementation_imported"] is False,"independent replay")
    H=R["historical_immutability"]
    ck(H["BA16_F14"]=="PRESERVED_FOREVER" and H["P_BA16_A"]==0 and H["P_BA16_MIXED"]==1,"BA16 immutability")
    ck(H["BA17"]=="SEALED_AND_UNCHANGED" and H["BA18"]=="SEALED_AND_UNCHANGED","parent preservation")
    ck(R["symbolic"]["c_layer"]["raw"]=="p*n*r*s" and R["symbolic"]["c_layer"]["distinct"]=="p*n*r*s","gen4")
    ck(R["symbolic"]["width_growth"]["BA19_final_clause_width"]==4,"width4")
    ck(R["symbolic"]["signature"]["NEW_VARIABLE_IDENTITY_COUNT"]==0,"identity")
    ck(R["work_accounting"]["total_certificate_work"]=="O(g*(p+n+r+s+n^2+r^2)+p*n*r*s)","complexity")
    final={k:1 for k in EXPECTED}
    status="PASS" if not errors else "FAIL"
    out={"gate":"R50G25BA19_PRESEAL_COMPLETION","kind":"EXACT_PREREG_NAME_AUDIT",
         "status":status,"errors":errors,"required_pass_names":EXPECTED,"required_pass_count":34,
         "required_passes":final if status=="PASS" else {},
         "all_required_passes":status=="PASS","P_BA19_FINAL":1 if status=="PASS" else 0,
         "BA16_F14":"PRESERVED_FOREVER","P_BA16_A":0,"P_BA16_MIXED":1,
         "BA17_preserved":True,"BA18_preserved":True,"BA20_started":False,
         "CI_GREEN_NE_SCIENTIFIC_SEAL":True}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("; ".join(errors))

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--prereg",required=True);a.add_argument("--result",required=True)
    a.add_argument("--verify",required=True);a.add_argument("--out",required=True)
    z=a.parse_args();main(z.prereg,z.result,z.verify,z.out)
