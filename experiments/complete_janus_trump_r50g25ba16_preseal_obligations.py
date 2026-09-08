from __future__ import annotations
import argparse, json
from pathlib import Path

PREREG_PATH=Path("research/JANUS_TRUMP_R50G25BA16_PREREGISTRATION.json")
EXPECTED_FALSE="QUOTIENT_WIDTH_PASS"

def main(result_path,verify_path,out_path):
    prereg=json.loads(PREREG_PATH.read_text())
    r=json.loads(Path(result_path).read_text())
    v=json.loads(Path(verify_path).read_text())
    required=list(prereg["required_passes"])
    if prereg.get("required_pass_count")!=39 or len(required)!=39 or len(set(required))!=39:
        raise SystemExit("frozen prereg exact-name contract invalid")
    if required[-2:]!=["INDEPENDENT_REPLAY_PASS","PRESEAL_COMPLETENESS_PASS"]:
        raise SystemExit("frozen tail contract changed")
    base=required[:-2]
    builder_names=list(r["obligations"].keys())
    builder_name_set_ok=set(builder_names)==set(base) and len(builder_names)==len(base)
    if not builder_name_set_ok:
        raise SystemExit("builder obligation name set/cardinality mismatch")
    if r["failed_frozen_obligations"]!=[EXPECTED_FALSE]:
        raise SystemExit("unexpected scientific falsifier set")
    if r["obligations"].get(EXPECTED_FALSE)!=0:
        raise SystemExit("frozen width falsifier not preserved")
    for name in base:
        if name==EXPECTED_FALSE:
            continue
        if r["obligations"].get(name)!=1:
            raise SystemExit("unexpected failed builder obligation: "+name)
    if not (r["scientific_mixed_result_pre_replay"] is True and
            r["expected_scientific_falsifier_preserved"] is True and
            r["P_BA16_A"]==0 and
            r["success_label_BA16_A_permitted"] is False):
        raise SystemExit("builder did not preserve mixed scientific state")
    if not (v["status"]=="PASS" and v["error_count"]==0 and v["v_independent_verifier"]==1
            and v["P_BA16_MIXED"]==1 and v["P_BA16_A"]==0 and v["implementation_imported"] is False):
        raise SystemExit("independent replay did not confirm mixed state")
    full={}
    for name in required:
        if name=="INDEPENDENT_REPLAY_PASS":
            full[name]=1
        elif name=="PRESEAL_COMPLETENESS_PASS":
            full[name]=1
        else:
            full[name]=int(r["obligations"][name])
    failed=[name for name in required if full[name]!=1]
    if failed!=[EXPECTED_FALSE]:
        raise SystemExit("completed scientific falsifier set mismatch")
    out={
      "gate":"R50G25BA16_PRESEAL_COMPLETION",
      "kind":"PRESEAL_OBLIGATION_COMPLETION_MIXED_SCIENTIFIC_RESULT",
      "status":"PASS_MIXED_F14_WIDTH_FALSIFIER_PRESERVED",
      "preregistration_commit":r["preregistration_commit"],
      "required_pass_count":len(required),
      "reported_pass_count":len(full),
      "scientific_pass_count":sum(full.values()),
      "scientific_failed_count":len(failed),
      "required_pass_names":required,
      "required_passes":full,
      "scientific_failed_obligations":failed,
      "all_required_names_reported":set(full)==set(required) and len(full)==len(required),
      "all_required_passes":False,
      "preseal_completeness_pass":True,
      "independent_replay_pass":True,
      "report_contract":{
        "builder_exact_name_set_and_cardinality":builder_name_set_ok,
        "serialized_mapping_order_is_not_authority":True,
        "ordered_required_names_preserved_from_frozen_prereg":True,
        "GEN3_aggregate_only_is_insufficient":True,
        "separate_required_fields_present":{
          "DERIVED_SUPPORT":"DERIVED_NR_SUPPORT_PASS" in full,
          "RAW_GEN3_PATHS":"RAW_GEN3_PNR_PATH_PASS" in full,
          "DISTINCT_GEN3_CLAUSES":"DISTINCT_GEN3_PR_PASS" in full,
          "DUPLICATE_COLLAPSE":"DUPLICATE_COUNT_PASS" in full,
          "IDENTITY_LOWER_BOUND":"IDENTITY_LOWER_BOUND_PASS" in full}},
      "mixed_scientific_result":{
        "derived_future_support":"CERTIFIED",
        "raw_gen3_paths":"p*n*r",
        "distinct_gen3_clauses":"p*r",
        "duplicate_resolvents":"p*r*(n-1)",
        "self_sustaining_distinct_multiplication":"NOT_CERTIFIED",
        "frozen_width_candidate":"FALSIFIED",
        "falsifier":"F14"},
      "P_BA16_A":0,
      "P_BA16_MIXED":1,
      "BA17_started":False,
      "P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    Path(out_path).write_text(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--result",required=True);ap.add_argument("--verify",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();main(a.result,a.verify,a.out)
