from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SPEC_SCHEMA="janus.c049_1.b5.fixed_discovery_round3_from_verified_prefix_layout_spec.v1"
PLAN_SCHEMA="janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1_1"
B51_SCHEMA="janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
B52B_SCHEMA="janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"


def cb(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":")).encode("utf-8")
def dg(x:Any)->str:return hashlib.sha256(cb(x)).hexdigest()
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def key(x:Any)->str:return cb(x).decode("utf-8")


def tree_nodes(raw:dict)->dict[str,dict]:
    nodes=raw.get("tree",{}).get("nodes",[])
    if not isinstance(nodes,list):raise AssertionError("tree nodes")
    out={str(n["id"]):n for n in nodes}
    if len(out)!=len(nodes):raise AssertionError("tree node ids")
    return out


def verify(spec:dict,pre:dict,plan:dict,round2_layout:dict,round3_input:dict,round3:dict)->dict:
    if spec.get("schema")!=SPEC_SCHEMA or spec.get("status")!="SPEC_FROZEN_CANDIDATE_ONLY":raise AssertionError("spec")
    pp=pre.get("proof_payload")
    if not isinstance(pp,dict) or pre.get("semantic_digest")!=dg(pp):raise AssertionError("preprocessing")
    if plan.get("schema")!=PLAN_SCHEMA or plan.get("semantic_digest")!=dg(plan.get("proof_payload")):raise AssertionError("plan")
    pl=plan["proof_payload"]
    if pl.get("preprocessing_authority_version")!="V1_1_CANONICAL_RREF" or pl.get("preprocessing_semantic_digest")!=pre["semantic_digest"]:raise AssertionError("preprocessing authority")
    schedule=pl.get("schedule_occurrence_indices")
    if not isinstance(schedule,list) or len(schedule)<3 or schedule[:3]!=[0,1,2]:raise AssertionError("fixed prefix3 schedule")
    by={int(x["occurrence_index"]):x for x in pp.get("discovery_catalog",[])}
    if set(schedule[:3])-set(by):raise AssertionError("discovery occurrence universe")
    dims=[len(by[i].get("normal_space",[])) for i in schedule[:3]]
    if dims!=spec["bounded_control"]["fixed_reduced_dimensions"]:raise AssertionError("fixed reduced dimensions")
    if int(pp["ambient_dim"])!=spec["bounded_control"]["ambient_dim"] or int(pp["k"])!=spec["bounded_control"]["k"]:raise AssertionError("bounded parameters")

    if round2_layout.get("schema")!=B52B_SCHEMA or round2_layout.get("semantic_digest")!=dg(round2_layout.get("proof_payload")):raise AssertionError("round2 layout")
    q=round2_layout["proof_payload"]
    if q.get("reconstruction_status")!="LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW" or q.get("candidate_found_layout") is not True:raise AssertionError("round2 layout status")
    if q.get("maximum_cut_width")>int(pp["k"]):raise AssertionError("round2 layout width")
    order=q.get("factor_order_ids")
    if not isinstance(order,list) or len(order)!=2:raise AssertionError("round2 order")
    prefix2=[by[i]["factor_id"] for i in schedule[:2]]
    if sorted(map(key,order))!=sorted(map(key,prefix2)) or len(set(map(key,order)))!=2:raise AssertionError("round2 exact prefix permutation")

    expected_by_id={key(by[i]["factor_id"]):by[i] for i in schedule[:3]}
    input_factors=round3_input.get("factors")
    expected_prefix3=[{"id":by[i]["factor_id"],"normal_space":by[i]["normal_space"],"affine_offset":by[i]["affine_offset"]} for i in schedule[:3]]
    if input_factors!=expected_prefix3:raise AssertionError("round3 factor subject")
    if round3_input.get("caps")!=spec["bounded_control"]["caps"]:raise AssertionError("round3 caps")

    nodes=tree_nodes(round3_input)
    if round3_input.get("tree",{}).get("root")!="r3_root":raise AssertionError("round3 root")
    root=nodes.get("r3_root"); left=nodes.get("r3_prefix"); p0=nodes.get("r3_p0"); p1=nodes.get("r3_p1"); new=nodes.get("r3_new")
    if not all(isinstance(x,dict) for x in (root,left,p0,p1,new)):raise AssertionError("round3 required nodes")
    if root!={"id":"r3_root","left":"r3_prefix","right":"r3_new"}:raise AssertionError("round3 root shape")
    if left!={"id":"r3_prefix","left":"r3_p0","right":"r3_p1"}:raise AssertionError("round3 prefix subtree shape")
    if p0!={"id":"r3_p0","factor_id":order[0]} or p1!={"id":"r3_p1","factor_id":order[1]}:raise AssertionError("verified layout order not used")
    next_id=by[schedule[2]]["factor_id"]
    if new!={"id":"r3_new","factor_id":next_id}:raise AssertionError("next fixed factor")

    for fid in order+[next_id]:
        source=expected_by_id[key(fid)]
        hits=[x for x in input_factors if key(x["id"])==key(fid)]
        if len(hits)!=1:raise AssertionError("round3 factor uniqueness")
        if hits[0]["normal_space"]!=source["normal_space"] or cb(hits[0]["affine_offset"])!=cb(source["affine_offset"]):raise AssertionError("round3 factor identity")

    if round3.get("schema")!=B51_SCHEMA or round3.get("semantic_digest")!=dg(round3.get("proof_payload")):raise AssertionError("round3 B5.1")
    r=round3["proof_payload"]
    status=r.get("capability_status")
    if status not in {"CLOSED_COMPLETE_TRACE","OPEN_RUNTIME_CAPABILITY"}:raise AssertionError("round3 capability status")
    if r.get("terminal_promotion")!="NONE":raise AssertionError("terminal promotion")
    sb=r.get("strict_boundary",{})
    if sb.get("found_layout")!="FORBIDDEN" or sb.get("no_layout_at_cap")!="FORBIDDEN" or sb.get("b5_complete") is not False or sb.get("p_vs_np")!="OPEN":raise AssertionError("round3 claim promotion")

    receipts=r.get("node_receipts",[])
    if not isinstance(receipts,list):raise AssertionError("node receipts")
    max_boundary=max((len(x.get("B_v_rref",[])) for x in receipts),default=0)
    max_bprime=max((len(x.get("Bprime_v_rref_if_internal",[])) for x in receipts if x.get("Bprime_v_rref_if_internal") is not None),default=0)
    if max(max_boundary,max_bprime)>3*int(pp["k"]):raise AssertionError("3k scaffold width")

    if status=="CLOSED_COMPLETE_TRACE":
        count=int(r.get("root_entry_count_if_closed") or 0)
        branch="CLOSED_NONEMPTY" if count>0 else "CLOSED_EMPTY"
        next_gate="C049.1_B5_FIXED_DISCOVERY_ROUND3_B5_2_RECONSTRUCTION" if count>0 else "C049.1_B5_FIXED_DISCOVERY_ROUND3_B5_3_NEGATIVE_TERMINAL_REVIEW"
    else:
        count=None;branch="OPEN";next_gate="C049.1_B5_FIXED_DISCOVERY_ROUND3_CAPABILITY_OPEN"
    return {"status":"PASS","verified_round2_order":order,"new_factor_id":next_id,"round3_capability_status":status,"round3_branch":branch,"round3_root_entries":count,"max_boundary_dimension":max_boundary,"max_bprime_dimension":max_bprime,"next_gate":next_gate}


def main()->None:
    ap=argparse.ArgumentParser()
    for n in ("spec","preprocessing","plan","round2-layout","round3-input","round3-candidate"):ap.add_argument("--"+n,type=Path,required=True)
    a=ap.parse_args();report=verify(load(a.spec),load(a.preprocessing),load(a.plan),load(a.round2_layout),load(a.round3_input),load(a.round3_candidate))
    print("JANUS_B5_FIXED_DISCOVERY_ROUND3_FROM_VERIFIED_PREFIX_LAYOUT_VERIFIER = PASS")
    print("VERIFIED_ROUND2_FACTOR_ORDER_IDS =",json.dumps(report["verified_round2_order"],sort_keys=True,separators=(",",":")))
    print("ROUND3_NEW_FIXED_FACTOR_ID =",json.dumps(report["new_factor_id"],sort_keys=True,separators=(",",":")))
    print("ROUND3_PREFIX_SUBTREE_FROM_VERIFIED_LAYOUT = PASS")
    print("ROUND3_MAX_BOUNDARY_DIMENSION =",report["max_boundary_dimension"]);print("ROUND3_MAX_BPRIME_DIMENSION =",report["max_bprime_dimension"]);print("SCAFFOLD_3K_BOUND = PASS")
    print("ROUND3_CAPABILITY_STATUS =",report["round3_capability_status"]);print("ROUND3_BRANCH =",report["round3_branch"]);print("ROUND3_ROOT_ENTRIES =",report["round3_root_entries"]);print("NEXT_GATE =",report["next_gate"])
    print("RAW_PREVIOUS_ROOT_STATE_REUSE = FORBIDDEN");print("FULL_SCHEDULE_EXECUTION = NOT_ESTABLISHED");print("B5_COMPLETE = FALSE");print("C049_1_COMPLETE = FALSE");print("P_VS_NP = OPEN")

if __name__=="__main__":main()
