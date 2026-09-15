from __future__ import annotations

import hashlib, json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as v1

ARTIFACT_ID="JANUS-TRUMP-BICAMERAL-BUCKET-COMMON-CORE-SEMIJOIN-PREFILTER-CANDIDATE-2026-09-15-v1.1"
AUTHORITY="CANDIDATE_SUCCESSOR_REPAIR__NO_SCIENTIFIC_PROMOTION"
PREREG=Path("research/TRUMP_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_V1_1_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB="e390c2019671464f1af9ece1c42496447fdf8398"
V1=Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py")
V1_BLOB="f103bf9b14e3b208200f429b75d0858c4963fa7c"


def root(): return Path(__file__).resolve().parents[3]
def blob(path:Path):
    d=path.read_bytes(); return hashlib.sha1(f"blob {len(d)}\0".encode()+d).hexdigest()

def source_guard():
    r=root(); c={"v11_prereg_blob":blob(r/PREREG)==PREREG_BLOB,"frozen_v1_blob":blob(r/V1)==V1_BLOB}
    return {"ok":all(c.values()),"checks":c}

def firewall(): return v1.firewall()

def first_failed_original_bucket_v11(raw:dict)->dict:
    pred=guarded.explain(raw)
    if pred.get("status")!="OPEN_BUCKET_PRODUCT_BUDGET": return {"status":"OUT_OF_SCOPE_PREDECESSOR_NOT_OVERBUDGET","predecessor":pred}
    car=pred["carrier"]; fail=car["failed_bucket"]
    if car["resource_receipt"].get("failed_bucket_combinations_enumerated")!=0: raise AssertionError("FAILED_BUCKET_ALREADY_ENUMERATED")
    canonical=canonicalize_raw(raw); cut=list(pred["parent_cut"]["cut_variables"]); B=set(cut); x=int(fail["variable"])
    comps=parent_support.constraint_components_after_cut(canonical,cut)
    target=None
    for comp in comps:
        if any(x in canonical["constraints"][gi]["scope"] for gi in comp): target=comp; break
    if target is None: return {"status":"OUT_OF_SCOPE_FAILED_COMPONENT_NOT_FOUND","predecessor":pred}
    factors=[v1._factor(canonical["constraints"][gi],gi) for gi in target]
    internal=sorted({vv for f in factors for vv in f["scope"] if vv not in B})
    if not internal or x!=internal[0]:
        return {"status":"OUT_OF_SCOPE_NOT_FIRST_PRIVATE_BUCKET_OF_TARGET_COMPONENT","failed_variable":x,"target_internal_variables":internal,"predecessor":pred}
    bucket=[f for f in factors if x in f["scope"]]
    if [f["id"] for f in bucket]!=list(fail["bucket_factor_ids"]): raise AssertionError("FAILED_BUCKET_ID_MISMATCH")
    core=sorted(set.intersection(*(set(f["scope"]) for f in bucket)))
    return {"status":"READY","predecessor":pred,"canonical":canonical,"cut":cut,"components":comps,"failed":fail,"failed_variable":x,"component":target,"bucket":bucket,"common_core":core,"prior_other_component_combinations":int(car["resource_receipt"].get("total_combinations_enumerated_before_open",0))}

def build(raw:dict,proposal_override:dict|None=None)->dict:
    ready=first_failed_original_bucket_v11(raw)
    if ready["status"]!="READY": return ready
    canonical=ready["canonical"]; bucket=ready["bucket"]; core=ready["common_core"]; fail=ready["failed"]
    proposal=proposal_override or v1.proposal_record(canonical,fail,bucket,core)
    if not v1.verify_proposal(canonical,fail,bucket,core,proposal): return {"status":"REJECT_TAMPERED_PROVENANCE"}
    if not core or ready["failed_variable"] not in core: return {"status":"OPEN_NO_COMMON_CORE"}
    sf=v1.support_and_filter(canonical,bucket,core)
    raw_product=v1._prod(sf["row_counts_before"]); filtered_product=v1._prod(sf["row_counts_after"])
    receipt={"failed_variable":ready["failed_variable"],"common_core":core,"common_core_size":len(core),"support_sizes":[len(x) for x in sf["supports"]],"common_support_size":len(sf["common"]),"raw_bucket_product":raw_product,"filtered_bucket_product":filtered_product,"row_counts_before":sf["row_counts_before"],"row_counts_after":sf["row_counts_after"],"prior_other_component_combinations":ready["prior_other_component_combinations"],"target_component_first_private_bucket":True,"bucket_cartesian_combinations_enumerated":0,"budget_raised":False,"alternative_orders":0,"generic_transfer_calls":0,"external_solver_calls":0}
    if not sf["common"]:
        return {"status":"EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION","proposal":proposal,"receipt":receipt,"witness":None,"witness_verified":True}
    filtered_raw={"variables":list(sf["filtered"]["variables"]),"constraints":sf["filtered"]["constraints"]}
    handoff=guarded.explain(filtered_raw); receipt["handoff_terminal"]=handoff.get("status")
    if handoff.get("status")=="OPEN_BUCKET_PRODUCT_BUDGET":
        receipt["handoff_failed_bucket_enumerations"]=handoff.get("carrier",{}).get("resource_receipt",{}).get("failed_bucket_combinations_enumerated")
        return {"status":"OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2","proposal":proposal,"receipt":receipt,"handoff":handoff}
    if handoff.get("status")!="ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status":"OPEN_FILTERED_HANDOFF_TERMINAL","proposal":proposal,"receipt":receipt,"handoff":handoff}
    witness=handoff["carrier"]["witness"]["assignment"]; assn={int(k):int(v) for k,v in witness.items()}; verified=guarded.verify_original_assignment(canonical,assn); receipt["original_witness_verified"]=verified
    return {"status":"ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION" if verified else "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE","proposal":proposal,"receipt":receipt,"handoff_terminal":handoff.get("status"),"witness":witness,"witness_verified":verified}

def explain(raw:dict)->dict:
    g=source_guard()
    if not g["ok"]: return {"artifact_id":ARTIFACT_ID,"status":"HALT_SOURCE_GUARD","source_guard":g,"scientific_firewall":firewall()}
    try: canonicalize_raw(raw)
    except RawBasisInputError as e: return {"artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"status":"REJECT_RAW_INPUT","reason":str(e),"source_guard":g,"scientific_firewall":firewall()}
    c=build(raw); return {"artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"status":c["status"],"source_guard":g,"carrier":c,"scientific_firewall":firewall()}

def tampered_control()->dict:
    raw=v1.positive_aligned_overbudget_control(); ready=first_failed_original_bucket_v11(raw); p=v1.proposal_record(ready["canonical"],ready["failed"],ready["bucket"],ready["common_core"]); p["common_core"]=list(reversed(p["common_core"])); return build(raw,p)

def main():
    print(json.dumps({"artifact_id":ARTIFACT_ID,"positive":explain(v1.positive_aligned_overbudget_control()),"hostile_empty":explain(guarded.overbudget_control()),"sticky_open":explain(v1.filtered_still_overbudget_control()),"hint":explain(v1.injected_hint_control()),"tamper":tampered_control(),"scientific_firewall":firewall()},sort_keys=True))
if __name__=='__main__': main()
