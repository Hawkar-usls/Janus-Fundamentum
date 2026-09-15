from __future__ import annotations

import json, math

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cand
from research.tools.apma_mixed_carrier_barrier import check_schaefer_barrier as barrier

ARTIFACT_ID="JANUS-TRUMP-BICAMERAL-BUCKET-COMMON-CORE-SEMIJOIN-PREFILTER-INDEPENDENT-CHECK-2026-09-15-v1.0"
AUTHORITY="INDEPENDENT_CHECKER__SCOPED_ONLY"


def factor(rel:dict,gi:int)->dict:
    os=list(rel["scope"]); scope=sorted(os); pos={v:i for i,v in enumerate(os)}
    return {"id":f"orig:{gi}","gi":gi,"scope":scope,"rows":[tuple(int(row[pos[v]]) for v in scope) for row in rel["allowed"]]}


def independent_prefilter(raw:dict)->dict:
    pred=guarded.explain(raw)
    if pred.get("status")!="OPEN_BUCKET_PRODUCT_BUDGET": return {"status":"OUT_OF_SCOPE","predecessor":pred.get("status")}
    fail=pred["carrier"]["failed_bucket"]; rr=pred["carrier"]["resource_receipt"]
    if rr.get("total_combinations_enumerated_before_open")!=0 or rr.get("failed_bucket_combinations_enumerated")!=0: return {"status":"OUT_OF_SCOPE_NOT_FIRST_CLEAN_BUCKET"}
    can=canonicalize_raw(raw); cut=list(pred["parent_cut"]["cut_variables"]); x=int(fail["variable"])
    comps=parent_support.constraint_components_after_cut(can,cut); comp=next(c for c in comps if any(x in can["constraints"][gi]["scope"] for gi in c))
    fs=[factor(can["constraints"][gi],gi) for gi in comp]; bucket=[f for f in fs if x in f["scope"]]
    assert [f["id"] for f in bucket]==fail["bucket_factor_ids"]
    core=sorted(set.intersection(*(set(f["scope"]) for f in bucket)))
    supports=[]
    for f in bucket:
        pos=[f["scope"].index(v) for v in core]
        supports.append({tuple(row[p] for p in pos) for row in f["rows"]})
    common=set.intersection(*supports)
    filtered=json.loads(json.dumps(can)); after=[]
    for f in bucket:
        rel=filtered["constraints"][f["gi"]]; os=list(rel["scope"]); pos={v:i for i,v in enumerate(os)}; kept=[]
        for row in rel["allowed"]:
            sig=tuple(int(row[pos[v]]) for v in core)
            if sig in common: kept.append(row)
        rel["allowed"]=kept; after.append(len(kept))
    before=[len(f["rows"]) for f in bucket]
    if not common: return {"status":"EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION","core":core,"common":common,"before":before,"after":after,"raw_product":math.prod(before),"filtered_product":0,"failed_var":x}
    filtered_raw={"variables":list(filtered["variables"]),"constraints":filtered["constraints"]}
    handoff=guarded.explain(filtered_raw)
    terminal="ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION" if handoff.get("status")=="ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION" else ("OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2" if handoff.get("status")=="OPEN_BUCKET_PRODUCT_BUDGET" else "OPEN_FILTERED_HANDOFF_TERMINAL")
    verified=False
    if handoff.get("status")=="ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        w={int(k):int(v) for k,v in handoff["carrier"]["witness"]["assignment"].items()}; verified=guarded.verify_original_assignment(can,w)
        if not verified: terminal="OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE"
    return {"status":terminal,"core":core,"common":common,"before":before,"after":after,"raw_product":math.prod(before),"filtered_product":math.prod(after),"failed_var":x,"handoff":handoff.get("status"),"witness_verified":verified}


def run()->dict:
    pos_raw=cand.positive_aligned_overbudget_control(); sticky_raw=cand.filtered_still_overbudget_control(); hostile_raw=guarded.overbudget_control()
    cp=cand.explain(pos_raw); ch=cand.explain(hostile_raw); cs=cand.explain(sticky_raw); ci=cand.explain(cand.injected_hint_control()); ct=cand.tampered_control()
    ip=independent_prefilter(pos_raw); ih=independent_prefilter(hostile_raw); is_=independent_prefilter(sticky_raw)
    ppre=guarded.explain(pos_raw); spre=guarded.explain(sticky_raw)
    b=barrier.check_schaefer_barrier()
    checks={
      "P1_candidate_source_guard":cp.get("source_guard",{}).get("ok") is True,
      "P2_positive_predecessor_open":ppre.get("status")=="OPEN_BUCKET_PRODUCT_BUDGET",
      "P2_positive_first_failed_zero":ppre.get("carrier",{}).get("resource_receipt",{}).get("total_combinations_enumerated_before_open")==0,
      "P2_positive_raw_product_over_L2":cp["carrier"]["receipt"]["raw_bucket_product"]>ppre["carrier"]["budget"],
      "P3_core_matches_independent":cp["carrier"]["receipt"]["common_core"]==ip["core"],
      "P3_core_size20":len(ip["core"])==20,
      "P4_common_support_one":cp["carrier"]["receipt"]["common_support_size"]==1 and len(ip["common"])==1,
      "P4_row_counts_match":cp["carrier"]["receipt"]["row_counts_after"]==ip["after"],
      "P5_filtered_product_one":cp["carrier"]["receipt"]["filtered_bucket_product"]==1 and ip["filtered_product"]==1,
      "P6_positive_terminal":cp["status"]=="ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION",
      "P6_independent_positive_terminal":ip["status"]=="ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION",
      "P6_witness_verified":cp["carrier"].get("witness_verified") is True and ip.get("witness_verified") is True,
      "P7_hostile_exact_unsat":ch["status"]=="EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION" and ih["status"]=="EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION",
      "P7_hostile_common_empty":ch["carrier"]["receipt"]["common_support_size"]==0 and len(ih["common"])==0,
      "P8_sticky_predecessor_open":spre.get("status")=="OPEN_BUCKET_PRODUCT_BUDGET",
      "P8_sticky_terminal_open":cs["status"]=="OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2" and is_["status"]=="OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2",
      "P8_sticky_filtered_product_over_original_L2":cs["carrier"]["receipt"]["filtered_bucket_product"]>spre["carrier"]["budget"],
      "P8_sticky_zero_failed_enumeration":cs["carrier"]["receipt"].get("handoff_failed_bucket_enumerations")==0,
      "P10_hint_rejected":ci["status"]=="REJECT_RAW_INPUT",
      "P10_tamper_rejected":ct["status"]=="REJECT_TAMPERED_PROVENANCE",
      "P11_no_budget_raise":cp["carrier"]["receipt"]["budget_raised"] is False,
      "P11_zero_bucket_cartesian_prefilter":cp["carrier"]["receipt"]["bucket_cartesian_combinations_enumerated"]==0 and ch["carrier"]["receipt"]["bucket_cartesian_combinations_enumerated"]==0,
      "P11_zero_alternative_orders":cp["carrier"]["receipt"]["alternative_orders"]==0,
      "P12_schaefer_barrier":b.get("verdict")=="PASS_SCHAEFER_MIXED_CARRIER_BARRIER",
      "FW_p_vs_np_open":cp["scientific_firewall"]["P_VS_NP"]=="OPEN",
      "FW_general_sat_not_proved":cp["scientific_firewall"]["GENERAL_SAT_IN_P"]=="NOT_PROVED",
      "FW_general_compression_not_proved":cp["scientific_firewall"]["GENERAL_EFFECTIVE_BUCKET_COMPRESSION"]=="NOT_PROVED",
    }
    return {"artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"checks":checks,"controls":{"positive_raw_product":cp.get("carrier",{}).get("receipt",{}).get("raw_bucket_product"),"positive_filtered_product":cp.get("carrier",{}).get("receipt",{}).get("filtered_bucket_product"),"positive_core_size":cp.get("carrier",{}).get("receipt",{}).get("common_core_size"),"positive_terminal":cp["status"],"hostile_terminal":ch["status"],"sticky_filtered_product":cs.get("carrier",{}).get("receipt",{}).get("filtered_bucket_product"),"sticky_terminal":cs["status"],"hint_terminal":ci["status"],"tamper_terminal":ct["status"]},"verdict":"PASS_SCOPED_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1" if all(checks.values()) else "FAIL_OR_OPEN_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1","scientific_firewall":cp["scientific_firewall"]}


def main()->None:
    out=run(); print(json.dumps(out,sort_keys=True));
    if not all(out["checks"].values()): raise SystemExit(1)

if __name__=="__main__": main()
