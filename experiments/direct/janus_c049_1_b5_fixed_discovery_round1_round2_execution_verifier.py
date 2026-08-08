from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SPEC_SCHEMA="janus.c049_1.b5.fixed_discovery_round1_round2_execution_composition_spec.v1"
PLAN_SCHEMA="janus.c049_1.b5.fixed_discovery_round_orchestration_binding_candidate.v1_1"
B51_SCHEMA="janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"


def cb(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def dg(x:Any)->str:return hashlib.sha256(cb(x)).hexdigest()
def load(p:Path)->Any:return json.loads(p.read_text())


def factor_from_discovery(x:dict)->dict:
    return {"id":x["factor_id"],"normal_space":x["normal_space"],"affine_offset":x["affine_offset"]}


def node_by_id(artifact:dict,node_id:str)->dict:
    hits=[x for x in artifact["proof_payload"]["node_receipts"] if x.get("node_id")==node_id]
    if len(hits)!=1:raise AssertionError("node receipt uniqueness: "+node_id)
    return hits[0]


def verify(spec:dict,pre:dict,plan:dict,r1in:dict,r1:dict,r2in:dict,r2:dict)->dict:
    if spec.get("schema")!=SPEC_SCHEMA or spec.get("status")!="SPEC_FROZEN_CANDIDATE_ONLY" or spec.get("version")!="1.1":raise AssertionError("spec")
    if plan.get("schema")!=PLAN_SCHEMA or plan.get("semantic_digest")!=dg(plan.get("proof_payload")):raise AssertionError("plan")
    pp=pre.get("proof_payload"); pl=plan["proof_payload"]
    if not isinstance(pp,dict) or pre.get("semantic_digest")!=dg(pp):raise AssertionError("preprocessing")
    if pl.get("preprocessing_authority_version")!="V1_1_CANONICAL_RREF":raise AssertionError("preprocessing authority downgrade")
    if pl.get("preprocessing_semantic_digest")!=pre["semantic_digest"]:raise AssertionError("preprocessing subject")
    if pl.get("fixed_discovery_catalog_semantic_digest")!=pp.get("discovery_catalog_semantic_digest"):raise AssertionError("catalog subject")
    schedule=pl.get("schedule_occurrence_indices"); rounds=pl.get("rounds")
    if not isinstance(schedule,list) or len(schedule)<2 or not isinstance(rounds,list) or len(rounds)<2:raise AssertionError("need two rounds")
    if rounds[0]["prefix_occurrence_indices"]!=schedule[:1] or rounds[1]["prefix_occurrence_indices"]!=schedule[:2]:raise AssertionError("prefix chain")
    if rounds[1]["new_occurrence_index"]!=schedule[1]:raise AssertionError("new factor binding")
    by={int(x["occurrence_index"]):x for x in pp["discovery_catalog"]}
    f1=factor_from_discovery(by[schedule[0]]); f2=factor_from_discovery(by[schedule[1]])
    bounded=spec.get("bounded_control",{})
    if int(pp["ambient_dim"])!=bounded.get("ambient_dim") or int(pp["k"])!=bounded.get("k"):raise AssertionError("bounded control parameters")
    dims=[len(by[i].get("normal_space",[])) for i in schedule[:2]]
    if dims!=bounded.get("fixed_reduced_dimensions"):raise AssertionError("bounded reduced dimensions")
    caps=bounded.get("caps")
    expected1={"ambient_dim":int(pp["ambient_dim"]),"k":int(pp["k"]),"caps":caps,"factors":[f1],"tree":{"root":"round1_leaf","nodes":[{"id":"round1_leaf","factor_id":f1["id"]}]}}
    expected2={"ambient_dim":int(pp["ambient_dim"]),"k":int(pp["k"]),"caps":caps,"factors":[f1,f2],"tree":{"root":"round2_root","nodes":[{"id":"round2_root","left":"round2_left","right":"round2_right"},{"id":"round2_left","factor_id":f1["id"]},{"id":"round2_right","factor_id":f2["id"]}]}}
    if r1in!=expected1:raise AssertionError("round1 input not exact prefix1")
    if r2in!=expected2:raise AssertionError("round2 input not exact prefix2")
    for name,a in (("round1",r1),("round2",r2)):
        if a.get("schema")!=B51_SCHEMA or a.get("semantic_digest")!=dg(a.get("proof_payload")):raise AssertionError(name+" B5.1 digest")
        p=a["proof_payload"]
        if p.get("capability_status")!="CLOSED_COMPLETE_TRACE":raise AssertionError(name+" not CLOSED")
        if p.get("terminal_promotion")!="NONE":raise AssertionError(name+" terminal promotion")
        b=p.get("strict_boundary",{})
        if b.get("found_layout")!="FORBIDDEN" or b.get("no_layout_at_cap")!="FORBIDDEN" or b.get("b5_complete") is not False or b.get("p_vs_np")!="OPEN":raise AssertionError(name+" claim promotion")
    c1=r1["proof_payload"]["canonical_factor_catalog"]
    c2=r2["proof_payload"]["canonical_factor_catalog"]
    if c1!=sorted([f1],key=lambda x:x["id"]):raise AssertionError("round1 factor catalog")
    if c2!=sorted([f1,f2],key=lambda x:x["id"]):raise AssertionError("round2 factor catalog")

    r1root=node_by_id(r1,"round1_leaf")
    r2left=node_by_id(r2,"round2_left")
    if r1root.get("covered_factor_ids")!=[f1["id"]] or r2left.get("covered_factor_ids")!=[f1["id"]]:raise AssertionError("prefix occurrence coverage handoff")
    if r1root.get("factor_identity_records")!=r2left.get("factor_identity_records"):raise AssertionError("factor identity handoff")
    expected_identity=[{"factor_id":f1["id"],"affine_offset":f1["affine_offset"]}]
    if r1root.get("factor_identity_records")!=expected_identity:raise AssertionError("affine identity")
    b1=r1root.get("B_v_rref"); b2=r2left.get("B_v_rref")
    if b1!=[]:raise AssertionError("round1 root boundary must be zero")
    if b2!=f1["normal_space"] or b2==[]:raise AssertionError("round2 left nonzero boundary context")
    if r1root.get("output_full_set_digest")==r2left.get("output_full_set_digest"):
        raise AssertionError("boundary-relative full sets unexpectedly collapsed to same digest")

    affine1={x["factor_id"]:x["affine_offset"] for x in r1["proof_payload"]["affine_offset_identity_ledger"]}
    affine2={x["factor_id"]:x["affine_offset"] for x in r2["proof_payload"]["affine_offset_identity_ledger"]}
    if affine1.get(f1["id"])!=f1["affine_offset"] or affine2.get(f1["id"])!=f1["affine_offset"] or affine2.get(f2["id"])!=f2["affine_offset"]:raise AssertionError("global affine identity")
    return {
        "status":"PASS",
        "round1_boundary":b1,
        "round2_left_boundary":b2,
        "round1_prefix_occurrence_identity":expected_identity,
        "round2_left_occurrence_identity":r2left["factor_identity_records"],
        "round1_root_entries":r1["proof_payload"]["root_entry_count_if_closed"],
        "round2_root_entries":r2["proof_payload"]["root_entry_count_if_closed"],
        "round2_root_nonempty":int(r2["proof_payload"]["root_entry_count_if_closed"] or 0)>0,
        "next_gate":"C049.1_B5_FIXED_DISCOVERY_ROUND2_B5_2_RECONSTRUCTION" if int(r2["proof_payload"]["root_entry_count_if_closed"] or 0)>0 else "C049.1_B5_FIXED_DISCOVERY_ROUND2_NEGATIVE_TERMINAL_REVIEW"
    }


def main():
    p=argparse.ArgumentParser()
    for n in ("spec","preprocessing","plan","round1-input","round1-candidate","round2-input","round2-candidate"):p.add_argument("--"+n,type=Path,required=True)
    a=p.parse_args();r=verify(load(a.spec),load(a.preprocessing),load(a.plan),load(getattr(a,"round1_input")),load(getattr(a,"round1_candidate")),load(getattr(a,"round2_input")),load(getattr(a,"round2_candidate")))
    print("JANUS_B5_FIXED_DISCOVERY_ROUND1_ROUND2_EXECUTION_COMPOSITION_VERIFIER = PASS")
    print("ROUND1_B5_1 = CLOSED_COMPLETE_TRACE");print("ROUND2_B5_1 = CLOSED_COMPLETE_TRACE")
    print("ROUND1_PREFIX_TO_ROUND2_LEFT_OCCURRENCE_IDENTITY = PASS")
    print("BOUNDARY_CONTEXT_CHANGE = ZERO_TO_NONZERO_CONFIRMED")
    print("RAW_BOUNDARY_RELATIVE_FULL_SET_STATE_HANDOFF = FORBIDDEN")
    print("ROUND1_ROOT_ENTRIES =",r["round1_root_entries"]);print("ROUND2_ROOT_ENTRIES =",r["round2_root_entries"]);print("ROUND2_ROOT_NONEMPTY =",r["round2_root_nonempty"]);print("NEXT_GATE =",r["next_gate"])
    print("FULL_ROUND_EXECUTION = NOT_ESTABLISHED");print("B5_COMPLETE = FALSE");print("C049_1_COMPLETE = FALSE");print("P_VS_NP = OPEN")

if __name__=="__main__":main()
