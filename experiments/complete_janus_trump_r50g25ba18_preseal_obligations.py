from __future__ import annotations
import argparse, json
from pathlib import Path

PREREG_COMMIT="1670788c9e6c10d77c1ed7bf4f0ccf2a32471285"
PARENT_META="bd003cb6004d587e7d970b9b580c1e90fc6ad458"
TERNARY_SUBPASSES=[
"TERNARY_CNF_REALIZATION_PASS","TERNARY_SOURCE_PREIMAGE_PASS","TERNARY_GENERIC_TRANSPORT_PASS",
"TERNARY_RECONSTRUCTION_PASS","TERNARY_FULL_ORIGINAL_CNF_VALIDATION_PASS"]
NAMED_FIELDS=["TERNARY_CARRIER","COMPOSITE_PAIR_SIGNATURE","RAW_GEN3","DISTINCT_GEN3","TAG_ERASURE_CONTROL","BA16_IDENTITY_PRESERVATION","OUTPUT_SIZE_FIREWALL"]

def main(prereg_path,result_path,verify_path,out_path):
    p=json.loads(Path(prereg_path).read_text())
    r=json.loads(Path(result_path).read_text())
    v=json.loads(Path(verify_path).read_text())
    errors=[]
    def ck(cond,msg):
        if not cond:errors.append(msg)
    req=p["required_passes"]
    ck(p["state"]=="FROZEN_BEFORE_IMPLEMENTATION","prereg state")
    ck(len(req)==46 and len(set(req))==46,"required pass count")
    ck(r["preregistration_commit"]==PREREG_COMMIT,"prereg commit")
    ck(r["parent_BA17_meta_commit"]==PARENT_META,"parent meta")
    ck(r["required_pass_names"]==req,"exact prereg-name order")
    ck(set(r["obligations"])==set(req),"exact obligation name set")
    ck(all(r["obligations"][k] for k in req if k not in ("INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS")),"builder obligations")
    ck(v["status"]=="PASS" and v["error_count"]==0 and v["P_BA18"]==1 and v["implementation_imported"] is False,"independent replay")
    ck(set(r["ternary_subpasses"])==set(TERNARY_SUBPASSES) and all(r["ternary_subpasses"].values()),"ternary subpasses")
    ck(set(r["named_fields"])==set(NAMED_FIELDS),"named field set")
    ck(r["named_fields"]["RAW_GEN3"]=="p*n*r" and r["named_fields"]["DISTINCT_GEN3"]=="p*n*r","gen3 named fields")
    ck(r["named_fields"]["COMPOSITE_PAIR_SIGNATURE"]["count"]=="n*r","signature named field")
    ck(r["named_fields"]["TAG_ERASURE_CONTROL"]["status"]=="PASS","tag erasure named field")
    ck(r["named_fields"]["BA16_IDENTITY_PRESERVATION"]["NEW_VARIABLE_IDENTITY_COUNT"]==0,"identity named field")
    ck(r["named_fields"]["OUTPUT_SIZE_FIREWALL"]["exponential_claimed"] is False,"output firewall named field")
    ck(r["historical_immutability"]["BA16_F14"]=="PRESERVED_FOREVER","BA16 F14")
    ck(r["historical_immutability"]["P_BA16_A"]==0 and r["historical_immutability"]["P_BA16_MIXED"]==1,"BA16 status")
    ck(r["historical_immutability"]["BA17_status"]=="SEALED_CORRECTED_WIDTH_CHILD_THEOREM_ONLY","BA17 preservation")
    ck(r["failure_count"]==0 and not r["falsifiers"],"falsifiers")
    ck(r["next_gate_started"] is False and r["BA19_started"] is False,"STOP")
    ck(r["P_VS_NP"]=="OPEN" and r["SAT_IN_P"]=="NOT_PROVED" and r["TRUMP_finished"] is False,"global firewall")
    completed={k:1 for k in req}
    out={"gate":"R50G25BA18_PRESEAL_COMPLETION","status":"PASS" if not errors else "FAIL",
         "errors":errors,"error_count":len(errors),"required_pass_count":len(req),"required_pass_names":req,
         "required_passes":completed if not errors else {k:int(bool(r["obligations"].get(k,False))) for k in req},
         "all_required_passes":not errors,"ternary_subpasses":r["ternary_subpasses"],
         "named_fields_present":NAMED_FIELDS if not errors else sorted(r.get("named_fields",{})),
         "P_BA18_FINAL":1 if not errors else 0,
         "BA16_F14_preserved":r["historical_immutability"]["BA16_F14"]=="PRESERVED_FOREVER",
         "P_BA16_A":r["historical_immutability"]["P_BA16_A"],"P_BA16_MIXED":r["historical_immutability"]["P_BA16_MIXED"],
         "BA19_started":r["BA19_started"]}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    if errors:raise SystemExit("BA18 preseal failure: "+errors[0])
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--prereg",required=True);ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();main(a.prereg,a.result,a.verify,a.out)
