#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json
from pathlib import Path

SPEC_SCHEMA="janus.c049_1.b4_6_4.actual_engine_composition_authority_supplement.v2"
R109_SCHEMA="janus.c049_1.b4_6_3.corrected_node6_parent_refinement_authority_closure_audit.v1"
R110_SCHEMA="janus.c049_1.b4_6_3.corrected_node6_up_k_authority_closure_audit.v1"
R111_SCHEMA="janus.c049_1.b4_6_3.corrected_node6_integration_node7_preflight_authority_closure_audit.v1"
Q80_SCHEMA="janus.c049_1.b4_6_4.actual_engine_q80_composition_authority_closure_audit.v1"
FINAL_AUDIT_SCHEMA="janus.c049_1.b4_6_4.actual_engine_composition_independent_semantic_audit.v1"

class VError(AssertionError):
    def __init__(self, code): super().__init__(code); self.code=code

def req(v,code):
    if not v: raise VError(code)
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
def dg(x): return hashlib.sha256(canon(x)).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def check_semantic(x, schema, scope, code):
    req(x.get("schema")==schema, code+"_SCHEMA")
    req(x.get("semantic_digest_scope")==scope, code+"_SCOPE")
    req(dg(x[scope])==x.get("semantic_digest"), code+"_DIGEST")
    return x[scope]

def verify(spec,r109,r110,r111,q80,final_audit):
    s=check_semantic(spec,SPEC_SCHEMA,"supplement_payload","S01_SPEC")
    a109=check_semantic(r109,R109_SCHEMA,"audit_payload","S02_R109")
    a110=check_semantic(r110,R110_SCHEMA,"audit_payload","S03_R110")
    a111=check_semantic(r111,R111_SCHEMA,"audit_payload","S04_R111")
    aq=check_semantic(q80,Q80_SCHEMA,"audit_payload","S05_Q80")
    af=check_semantic(final_audit,FINAL_AUDIT_SCHEMA,"audit_payload","S06_FINAL_AUDIT")

    e=s["early_trace_authorities"]
    req(a109["pr"]==109 and a109["proof_subject"]==e["node6_parent_refinement"]["proof_head"],"S07_R109_BIND")
    req(a109["review_id"]==e["node6_parent_refinement"]["review_id"],"S07_R109_BIND")
    req(r109["semantic_digest"]==e["node6_parent_refinement"]["receipt_semantic_digest"],"S07_R109_BIND")
    req(a109["admission"]["corrected_node6_parent_refinement_complete"] is True,"S08_R109_CLAIM")
    req(a109["admission"]["corrected_node6_parent_up_k_complete"] is False,"S08_R109_CEILING")

    req(a110["pr"]==110 and a110["proof_subject"]==e["node6_up_k"]["proof_head"],"S09_R110_BIND")
    req(a110["review_id"]==e["node6_up_k"]["review_id"],"S09_R110_BIND")
    req(r110["semantic_digest"]==e["node6_up_k"]["receipt_semantic_digest"],"S09_R110_BIND")
    req(a110["parent_authority"]["receipt_git_blob"]==e["node6_up_k"]["parent_receipt_git_blob"],"S10_R110_PARENT")
    req(a110["parent_authority"]["review_id"]==a109["review_id"],"S10_R110_PARENT")
    req(a110["admission"]["corrected_node6_parent_up_k_complete"] is True and a110["admission"]["corrected_node6_up_k_admitted"] is True,"S11_R110_CLAIM")

    req(a111["pr"]==111 and a111["proof_subject"]==e["node6_to_node7"]["proof_head"],"S12_R111_BIND")
    req(a111["review_id"]==e["node6_to_node7"]["review_id"],"S12_R111_BIND")
    req(r111["semantic_digest"]==e["node6_to_node7"]["receipt_semantic_digest"],"S12_R111_BIND")
    req(a111["parent_authority"]["receipt_git_blob"]==e["node6_to_node7"]["parent_receipt_git_blob"],"S13_R111_PARENT")
    req(a111["parent_authority"]["review_id"]==a110["review_id"],"S13_R111_PARENT")
    req(a111["admission"]["node6_to_node7_language_handoff"]=="ADMITTED","S14_R111_CLAIM")
    req(a111["admission"]["corrected_node7_parent_refinement_complete"] is False,"S14_R111_CEILING")

    q=s["q80_canonical_authority"]
    req(aq["exact_proof_head"]==q["proof_head"] and aq["review_id"]==q["review_id"],"S15_Q80_BIND")
    req(q80["semantic_digest"]==q["receipt_semantic_digest"],"S15_Q80_BIND")
    req(aq["admission"]["node8_authority_closed"] is True and aq["admission"]["q80_composition_replay_complete"] is True,"S16_Q80_CLAIM")
    req(aq["q80_replay"]["total_repaired_tampers_rejected"]=="16/16","S16_Q80_TAMPERS")

    f=s["frozen_mathematical_subject"]
    req(af["proof_subject"]["head_sha"]==f["proof_head"],"S17_FINAL_SUBJECT")
    req(af["proof_subject"]["candidate_sha256"]==f["candidate_sha256"],"S17_FINAL_CANDIDATE")
    req(af["proof_subject"]["candidate_semantic_digest"]==f["candidate_semantic_digest"],"S17_FINAL_CANDIDATE")
    req(af["proof_subject"]["ci_run_id"]==f["workflow_run_id"] and af["proof_subject"]["ci_job_id"]==f["workflow_job_id"],"S18_FINAL_CI")
    req(af["independent_verifier"]["invariants"]=="18/18" and af["independent_verifier"]["digest_repaired_tampers_rejected"]=="18/18","S19_FINAL_VERIFY")
    req(af["independent_verifier"]["root_empty_consumed_as_composition_premise"] is False,"S20_NONVACUITY")
    req(af["independent_verifier"]["positive_control_pass"] is True,"S20_NONVACUITY")

    req(s["prior_final_review"]["review_id"]==af["review_id"],"S21_REVIEW_LINK")
    req(s["prior_final_review"]["mathematical_candidate_changed"] is False,"S21_REVIEW_LINK")
    req(s["admission_boundary"]["supplement_ci_does_not_self_admit"] is True,"S22_CEILING")
    req(s["strict_boundary"]["terminal_completeness_proved"] is False and s["strict_boundary"]["no_layout_at_cap"]=="FORBIDDEN" and s["strict_boundary"]["p_vs_np"]=="OPEN","S22_CEILING")

def tampers(spec,r109,r110,r111,q80,final_audit):
    out=[]
    def attack(name,which,mut):
        xs=[copy.deepcopy(x) for x in (spec,r109,r110,r111,q80,final_audit)]
        mut(xs[which])
        scope=xs[which].get("semantic_digest_scope")
        if scope in xs[which]: xs[which]["semantic_digest"]=dg(xs[which][scope])
        try: verify(*xs)
        except VError as e: out.append((name,e.code)); return
        raise AssertionError("tamper survived "+name)
    attack("T01_R109_CLAIM",1,lambda x:x["audit_payload"]["admission"].__setitem__("corrected_node6_parent_refinement_complete",False))
    attack("T02_R109_UPK_PROMOTION",1,lambda x:x["audit_payload"]["admission"].__setitem__("corrected_node6_parent_up_k_complete",True))
    attack("T03_R110_PARENT",2,lambda x:x["audit_payload"]["parent_authority"].__setitem__("receipt_git_blob","0"*40))
    attack("T04_R110_ADMISSION",2,lambda x:x["audit_payload"]["admission"].__setitem__("corrected_node6_up_k_admitted",False))
    attack("T05_R111_PARENT",3,lambda x:x["audit_payload"]["parent_authority"].__setitem__("review_id",0))
    attack("T06_R111_HANDOFF",3,lambda x:x["audit_payload"]["admission"].__setitem__("node6_to_node7_language_handoff","BLOCKED"))
    attack("T07_Q80_AUTHORITY",4,lambda x:x["audit_payload"]["admission"].__setitem__("node8_authority_closed",False))
    attack("T08_Q80_REPLAY",4,lambda x:x["audit_payload"]["admission"].__setitem__("q80_composition_replay_complete",False))
    attack("T09_FINAL_SHA",5,lambda x:x["audit_payload"]["proof_subject"].__setitem__("candidate_sha256","0"*64))
    attack("T10_ROOT_EMPTY_SHORTCUT",5,lambda x:x["audit_payload"]["independent_verifier"].__setitem__("root_empty_consumed_as_composition_premise",True))
    req(len(out)==10,"S23_TAMPER_COUNT")
    return out

def main():
    ap=argparse.ArgumentParser()
    for n in ("spec","r109","r110","r111","q80","final_audit"):
        ap.add_argument("--"+n.replace("_","-"),type=Path,required=True)
    ap.add_argument("--tamper-suite",action="store_true")
    a=ap.parse_args()
    vals=[load(getattr(a,n)) for n in ("spec","r109","r110","r111","q80","final_audit")]
    verify(*vals)
    ts=tampers(*vals) if a.tamper_suite else []
    print("JANUS_ACTUAL_ENGINE_COMPOSITION_AUTHORITY_SUPPLEMENT_VERIFIER = PASS")
    print("EARLY_NODE6_AUTHORITY_CHAIN = 3/3")
    print("CANONICAL_Q80_AUTHORITY = PASS")
    print("FROZEN_FINAL_CANDIDATE_AUTHORITY_LINK = PASS")
    print("ROOT_EMPTY_CONSUMED_AS_COMPOSITION_PREMISE = FALSE")
    print("AUTHORITY_DIGEST_REPAIRED_TAMPERS_REJECTED =",f"{len(ts)}/10" if a.tamper_suite else "NOT_RUN")
    print("SUPPLEMENT_SELF_ADMISSION = FALSE")
    print("TERMINAL_COMPLETENESS_PROVED = FALSE")
    print("NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("P_VS_NP = OPEN")

if __name__=="__main__": main()
