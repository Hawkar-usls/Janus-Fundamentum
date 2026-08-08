from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

SPEC_SCHEMA="janus.c049_1.b5.round3_join_path_capability_aperture_spec.v1"
B51_SCHEMA="janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"


def cb(x:Any)->bytes:return json.dumps(x,sort_keys=True,separators=(",",":")).encode("utf-8")
def dg(x:Any)->str:return hashlib.sha256(cb(x)).hexdigest()
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))


def verify_artifact(name:str,artifact:dict)->dict:
    if artifact.get("schema")!=B51_SCHEMA or artifact.get("semantic_digest_scope")!="proof_payload":raise AssertionError(name+" headers")
    p=artifact.get("proof_payload")
    if not isinstance(p,dict) or artifact.get("semantic_digest")!=dg(p):raise AssertionError(name+" digest")
    if p.get("terminal_promotion")!="NONE":raise AssertionError(name+" terminal promotion")
    sb=p.get("strict_boundary",{})
    if sb.get("found_layout")!="FORBIDDEN" or sb.get("no_layout_at_cap")!="FORBIDDEN" or sb.get("b5_complete") is not False or sb.get("p_vs_np")!="OPEN":raise AssertionError(name+" claim promotion")
    return p


def verify(spec:dict,baseline_input:dict,baseline:dict,aperture_input:dict,aperture:dict)->dict:
    if spec.get("schema")!=SPEC_SCHEMA or spec.get("status")!="SPEC_FROZEN_CAUSAL_CLASSIFICATION_ONLY":raise AssertionError("spec")
    if baseline_input.get("ambient_dim")!=spec["exact_subject"]["ambient_dim"] or baseline_input.get("k")!=spec["exact_subject"]["k"]:raise AssertionError("subject parameters")
    if baseline_input.get("caps")!=spec["baseline_caps"]:raise AssertionError("baseline caps")
    if aperture_input.get("caps")!=spec["aperture_caps"]:raise AssertionError("aperture caps")
    expected=copy.deepcopy(baseline_input);expected["caps"]=copy.deepcopy(spec["aperture_caps"])
    if aperture_input!=expected:raise AssertionError("single-variable aperture rule")
    basep=verify_artifact("baseline",baseline);ap=verify_artifact("aperture",aperture)
    if basep.get("caps")!=spec["baseline_caps"] or ap.get("caps")!=spec["aperture_caps"]:raise AssertionError("artifact/input caps binding")
    req=spec["baseline_required_result"]
    if basep.get("capability_status")!=req["capability_status"]:raise AssertionError("baseline capability")
    reason=basep.get("open_reason")
    expected_reason={"status":"OPEN_RUNTIME_CAPABILITY","reason":req["open_reason"],"stage":req["open_stage"],"cap":spec["baseline_caps"]["max_join_paths"],"observed":req["observed_join_path_precheck"]}
    if reason!=expected_reason:raise AssertionError("baseline OPEN reason replay")
    if basep.get("root_entry_count_if_closed") is not None or basep.get("root_full_set_digest_if_closed") is not None:raise AssertionError("baseline fake closed root")
    status=ap.get("capability_status")
    if status not in {"CLOSED_COMPLETE_TRACE","OPEN_RUNTIME_CAPABILITY"}:raise AssertionError("aperture capability")
    if status=="CLOSED_COMPLETE_TRACE":
        count=ap.get("root_entry_count_if_closed")
        if not isinstance(count,int) or count<0:raise AssertionError("aperture closed root count")
        if ap.get("open_reason") is not None:raise AssertionError("closed aperture carries open reason")
        branch="CLOSED_NONEMPTY" if count>0 else "CLOSED_EMPTY"
        classification="BASELINE_OPEN_CAUSED_BY_DECLARED_JOIN_PATH_CAP_IN_EXACT_SUBJECT"
        next_gate="C049.1_B5_FIXED_DISCOVERY_ROUND3_B5_2_RECONSTRUCTION" if count>0 else "C049.1_B5_FIXED_DISCOVERY_ROUND3_B5_3_NEGATIVE_TERMINAL_REVIEW"
    else:
        count=None
        reason2=ap.get("open_reason")
        if not isinstance(reason2,dict) or reason2.get("status")!="OPEN_RUNTIME_CAPABILITY":raise AssertionError("aperture OPEN reason")
        branch="OPEN"
        classification="CAPABILITY_OBSTRUCTION_PERSISTS_AT_APERTURE"
        next_gate="C049.1_B5_FIXED_DISCOVERY_ROUND3_CAPABILITY_OPEN_RECLASSIFICATION"
    if spec["strict_boundary"].get("asymptotic_runtime")!="NOT_ESTABLISHED" or spec["strict_boundary"].get("p_vs_np")!="OPEN":raise AssertionError("spec ceiling")
    return {"status":"PASS","baseline_open_reason":reason,"aperture_capability_status":status,"aperture_branch":branch,"aperture_root_entries":count,"aperture_open_reason":ap.get("open_reason"),"classification":classification,"next_gate":next_gate}


def main()->None:
    ap=argparse.ArgumentParser()
    for n in ("spec","baseline-input","baseline-candidate","aperture-input","aperture-candidate"):ap.add_argument("--"+n,type=Path,required=True)
    a=ap.parse_args();r=verify(load(a.spec),load(a.baseline_input),load(a.baseline_candidate),load(a.aperture_input),load(a.aperture_candidate))
    print("JANUS_B5_ROUND3_JOIN_PATH_CAPABILITY_APERTURE_VERIFIER = PASS")
    print("SINGLE_VARIABLE_CAP_CHANGE = PASS")
    print("BASELINE_OPEN_REASON =",json.dumps(r["baseline_open_reason"],sort_keys=True,separators=(",",":")))
    print("APERTURE_CAPABILITY_STATUS =",r["aperture_capability_status"]);print("APERTURE_BRANCH =",r["aperture_branch"]);print("APERTURE_ROOT_ENTRIES =",r["aperture_root_entries"])
    print("APERTURE_OPEN_REASON =",json.dumps(r["aperture_open_reason"],sort_keys=True,separators=(",",":")))
    print("CAPABILITY_CLASSIFICATION =",r["classification"]);print("NEXT_GATE =",r["next_gate"])
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED");print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED");print("B5_COMPLETE = FALSE");print("C049_1_COMPLETE = FALSE");print("P_VS_NP = OPEN")

if __name__=="__main__":main()
