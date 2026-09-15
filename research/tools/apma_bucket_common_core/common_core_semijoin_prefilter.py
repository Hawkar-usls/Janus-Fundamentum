from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as pair_v1

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-COMMON-CORE-SEMIJOIN-PREFILTER-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_COMMON_CORE_SEMIJOIN_PREFILTER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "87d2973744d6c6c2a0fc15b171d2b475525f46fb"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.3.json")
PARENT_STATE_BLOB = "88f66c52185662cd22a2c50f2f7b072a17cd6d25"
GUARDED = Path("research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py")
GUARDED_BLOB = "314034bac990e524d1db7743aef0aebd3b4565c1"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict:
    r=root()
    checks={
        "prereg_blob":git_blob_sha1(r/PREREG)==PREREG_BLOB,
        "parent_state_blob":git_blob_sha1(r/PARENT_STATE)==PARENT_STATE_BLOB,
        "guarded_blob":git_blob_sha1(r/GUARDED)==GUARDED_BLOB,
    }
    return {"ok":all(checks.values()),"checks":checks}


def firewall() -> dict:
    return {"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","CONNECTED_MIXED_CORE_SOLVED":"NO","GENERAL_EFFECTIVE_BUCKET_COMPRESSION":"NOT_PROVED","GENERAL_BUCKET_ELIMINATION_POLYNOMIAL":"NOT_PROVED","GLOBAL_APMA_FRONTIER_ADVANCE":"NONE_PENDING_HQ_REVIEW"}


def _factor(rel: dict, gi: int) -> dict:
    os=list(rel["scope"]); scope=sorted(os); pos={v:i for i,v in enumerate(os)}
    rows=sorted({tuple(int(row[pos[v]]) for v in scope) for row in rel["allowed"]})
    return {"id":f"orig:{gi}","gi":gi,"scope":scope,"rows":rows}


def _projection(f: dict, core: list[int], row: tuple[int,...]) -> tuple[int,...]:
    pos={v:i for i,v in enumerate(f["scope"])}
    return tuple(int(row[pos[v]]) for v in core)


def first_failed_original_bucket(raw: dict) -> dict:
    pred=guarded.explain(raw)
    if pred.get("status")!="OPEN_BUCKET_PRODUCT_BUDGET":
        return {"status":"OUT_OF_SCOPE_PREDECESSOR_NOT_OVERBUDGET","predecessor":pred}
    car=pred["carrier"]; fail=car["failed_bucket"]
    if int(car["resource_receipt"].get("total_combinations_enumerated_before_open",-1))!=0:
        return {"status":"OUT_OF_SCOPE_NOT_FIRST_BUCKET","predecessor":pred}
    if car["resource_receipt"].get("failed_bucket_combinations_enumerated")!=0:
        raise AssertionError("FAILED_BUCKET_ALREADY_ENUMERATED")
    canonical=canonicalize_raw(raw); cut=list(pred["parent_cut"]["cut_variables"])
    comps=parent_support.constraint_components_after_cut(canonical,cut)
    x=int(fail["variable"])
    comp=next(c for c in comps if any(x in canonical["constraints"][gi]["scope"] for gi in c))
    factors=[_factor(canonical["constraints"][gi],gi) for gi in comp]
    bucket=[f for f in factors if x in f["scope"]]
    if [f["id"] for f in bucket]!=list(fail["bucket_factor_ids"]):
        raise AssertionError("FAILED_BUCKET_ID_MISMATCH")
    core=sorted(set.intersection(*(set(f["scope"]) for f in bucket)))
    return {"status":"READY","predecessor":pred,"canonical":canonical,"cut":cut,"components":comps,"failed":fail,"failed_variable":x,"component":comp,"bucket":bucket,"common_core":core}


def proposal_record(canonical: dict, failed: dict, bucket: list[dict], core: list[int]) -> dict:
    body={"kind":"EXACT_COMMON_CORE_PROJECTION_INTERSECTION_SEMIJOIN_PREFILTER","raw_object_sha256":sha256_obj(canonical),"failed_variable":int(failed["variable"]),"bucket_factor_ids":[f["id"] for f in bucket],"common_core":core,"truth_authority":False,"proof_authority":False}
    body["proposal_sha256"]=sha256_obj(body)
    return body


def verify_proposal(canonical: dict, failed: dict, bucket: list[dict], core: list[int], p: dict) -> bool:
    b=dict(p); claimed=b.pop("proposal_sha256",None)
    return isinstance(claimed,str) and sha256_obj(b)==claimed and p.get("kind")=="EXACT_COMMON_CORE_PROJECTION_INTERSECTION_SEMIJOIN_PREFILTER" and p.get("raw_object_sha256")==sha256_obj(canonical) and p.get("failed_variable")==int(failed["variable"]) and p.get("bucket_factor_ids")==[f["id"] for f in bucket] and p.get("common_core")==core


def support_and_filter(canonical: dict, bucket: list[dict], core: list[int]) -> dict:
    supports=[]
    for f in bucket:
        s={_projection(f,core,row) for row in f["rows"]}
        supports.append(s)
    common=set.intersection(*supports) if supports else set()
    row_counts_before=[len(f["rows"]) for f in bucket]
    filtered_counts=[]; changed={}
    filtered=json.loads(json.dumps(canonical))
    for f,s in zip(bucket,supports):
        rel=filtered["constraints"][f["gi"]]
        os=list(rel["scope"]); pos={v:i for i,v in enumerate(os)}
        kept=[]
        for row in rel["allowed"]:
            sig=tuple(int(row[pos[v]]) for v in core)
            if sig in common:
                kept.append(row)
        rel["allowed"]=kept
        filtered_counts.append(len(kept)); changed[str(f["gi"])]=len(kept)
    return {"supports":supports,"common":common,"filtered":filtered,"row_counts_before":row_counts_before,"row_counts_after":filtered_counts,"changed":changed}


def _prod(xs:list[int])->int:
    return math.prod(xs) if xs else 1


def build(raw: dict, proposal_override: dict|None=None) -> dict:
    ready=first_failed_original_bucket(raw)
    if ready["status"]!="READY": return ready
    canonical=ready["canonical"]; bucket=ready["bucket"]; core=ready["common_core"]; fail=ready["failed"]
    proposal=proposal_override or proposal_record(canonical,fail,bucket,core)
    if not verify_proposal(canonical,fail,bucket,core,proposal): return {"status":"REJECT_TAMPERED_PROVENANCE"}
    if not core or ready["failed_variable"] not in core: return {"status":"OPEN_NO_COMMON_CORE"}
    sf=support_and_filter(canonical,bucket,core)
    raw_product=_prod(sf["row_counts_before"]); filtered_product=_prod(sf["row_counts_after"])
    receipt={"failed_variable":ready["failed_variable"],"common_core":core,"common_core_size":len(core),"support_sizes":[len(x) for x in sf["supports"]],"common_support_size":len(sf["common"]),"raw_bucket_product":raw_product,"filtered_bucket_product":filtered_product,"row_counts_before":sf["row_counts_before"],"row_counts_after":sf["row_counts_after"],"bucket_cartesian_combinations_enumerated":0,"budget_raised":False,"alternative_orders":0,"generic_transfer_calls":0,"external_solver_calls":0}
    if not sf["common"]:
        return {"status":"EXACT_UNSAT_BY_EMPTY_COMMON_CORE_SUPPORT_INTERSECTION","proposal":proposal,"receipt":receipt,"witness":None,"witness_verified":True}
    filtered_raw={"variables":list(sf["filtered"]["variables"]),"constraints":sf["filtered"]["constraints"]}
    handoff=guarded.explain(filtered_raw)
    receipt["handoff_terminal"]=handoff.get("status")
    if handoff.get("status")=="OPEN_BUCKET_PRODUCT_BUDGET":
        receipt["handoff_failed_bucket_enumerations"]=handoff.get("carrier",{}).get("resource_receipt",{}).get("failed_bucket_combinations_enumerated")
        return {"status":"OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2","proposal":proposal,"receipt":receipt,"handoff":handoff}
    if handoff.get("status")!="ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status":"OPEN_FILTERED_HANDOFF_TERMINAL","proposal":proposal,"receipt":receipt,"handoff":handoff}
    witness=handoff["carrier"]["witness"]["assignment"]
    assignment={int(k):int(v) for k,v in witness.items()}
    verified=guarded.verify_original_assignment(canonical,assignment)
    receipt["original_witness_verified"]=verified
    return {"status":"ADMIT_EXACT_COMMON_CORE_SEMIJOIN_THEN_GUARDED_ELIMINATION" if verified else "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE","proposal":proposal,"receipt":receipt,"handoff_terminal":handoff.get("status"),"witness":witness,"witness_verified":verified}


def explain(raw: dict) -> dict:
    g=source_guard()
    if not g["ok"]: return {"artifact_id":ARTIFACT_ID,"status":"HALT_SOURCE_GUARD","source_guard":g,"scientific_firewall":firewall()}
    try: canonicalize_raw(raw)
    except RawBasisInputError as e: return {"artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"status":"REJECT_RAW_INPUT","reason":str(e),"source_guard":g,"scientific_firewall":firewall()}
    carrier=build(raw)
    return {"artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"status":carrier["status"],"source_guard":g,"carrier":carrier,"scientific_firewall":firewall()}


def _mixed_right_relation(A:list[int], start:int)->dict:
    pats=[]
    OR=[(0,1),(1,0),(1,1)]; XOR=[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]
    for a,b in OR:
        for x,y,z in XOR: pats.append(list(A)+[a,b,x,y,z])
    return {"id":"right_mixed_product","scope":list(range(20))+list(range(start,start+5)),"allowed":pats}


def _decoy(seed:int,n:int=20)->list[int]:
    return [((seed>>(i%8))^(i//2)^1)&1 for i in range(n)]


def positive_aligned_overbudget_control()->dict:
    raw=pair_v1.three_relation_no_anchor_control(); X=pair_v1._bits(7,20); A=pair_v1._bits(5,20); Y=list(range(20,40)); extras=[]; start=47
    for i in range(20):
        p=start+i; count=3 if i%2==0 else 4
        rows=[X+[0]]
        for j in range(1,count): rows.append(_decoy(40+i*7+j)+[(i+j)&1])
        extras.append({"id":f"aligned_{i}","scope":Y+[p],"allowed":rows})
    qstart=start+20
    raw["variables"]=list(range(qstart+5))
    raw["constraints"]=raw["constraints"][:-1]+extras+[_mixed_right_relation(A,qstart)]
    return raw


def filtered_still_overbudget_control()->dict:
    raw=pair_v1.three_relation_no_anchor_control(); X=pair_v1._bits(7,20); A=pair_v1._bits(5,20); Y=list(range(20,40)); extras=[]; start=47
    for i in range(20):
        p0=start+2*i; p1=p0+1
        rows=[X+[a,b] for a,b in [(0,0),(0,1),(1,0),(1,1)]]
        extras.append({"id":f"sticky_{i}","scope":Y+[p0,p1],"allowed":rows})
    qstart=start+40
    raw["variables"]=list(range(qstart+5))
    raw["constraints"]=raw["constraints"][:-1]+extras+[_mixed_right_relation(A,qstart)]
    return raw


def injected_hint_control()->dict:
    raw=positive_aligned_overbudget_control(); raw["common_core"]="TRUSTED_Y"; return raw


def tampered_control()->dict:
    raw=positive_aligned_overbudget_control(); ready=first_failed_original_bucket(raw); p=proposal_record(ready["canonical"],ready["failed"],ready["bucket"],ready["common_core"]); p["common_core"]=list(reversed(p["common_core"])); return build(raw,p)


def main()->None:
    print(json.dumps({"artifact_id":ARTIFACT_ID,"positive":explain(positive_aligned_overbudget_control()),"hostile_empty":explain(guarded.overbudget_control()),"sticky_open":explain(filtered_still_overbudget_control()),"hint":explain(injected_hint_control()),"tamper":tampered_control(),"scientific_firewall":firewall()},sort_keys=True))

if __name__=="__main__": main()
