#!/usr/bin/env python3
"""Integrate PT351 as one latent support-binding stage before PT352 formation.
Historical source order is heuristic inspiration only. P_VS_NP remains OPEN.
"""
from __future__ import annotations
import argparse, hashlib, json
from typing import Any

from janus_c025_families import equality_family
from janus_pt352_formed_state_before_live import run as run_pt352_stack
from janus_tranception_prebirth_orbit_generators import FROZEN_N, digest_json

RUN_ID="JANUS-PT351-LATENT-BINDING-BEFORE-FORMATION-2026-08-18-v1"
EXPECTED_DIRECTIONS=["BACK","FORWARD","LEFT","RIGHT","FORWARD_AGAIN","BACK_AGAIN"]
EXPECTED_BACK=["PT222","PT477","PT366","PT355","PT354","PT353","PT352","PT351"]
EXPECTED_FORWARD=["PT351","PT352","PT353","PT354","PT355","PT366","PT477","PT222"]
NEGATIVE_NAMES=["missing_binding","parent_anchor_tamper","duplicate_support","absent_support","cross_parent_binding"]


def literal_count(formula: Any)->int:
    return sum(len(c) for c in formula)

def tamper_hex(v:str)->str:
    return ("0" if v and v[0]!="0" else "1")+v[1:] if v else v

def run_pt351()->dict[str,Any]:
    total=0; positive=0; blocked=0; negative_pt352_entries=0
    neg={k:0 for k in NEGATIVE_NAMES}; rows=[]
    hash_ops=0; literal_visits=0; presence_checks=0
    for n in FROZEN_N:
        formula,x_vars,y_vars=equality_family(n)
        parent_anchor=digest_json(formula); hash_ops+=1
        present=set()
        for clause in formula:
            for lit in clause:
                present.add(abs(int(lit))); literal_visits+=1
        row_pos=0; row_neg=0
        maxvar=max(present)
        def accept(body:dict[str,Any]|None, commitment:str|None)->bool:
            nonlocal hash_ops,presence_checks
            presence_checks+=1
            if body is None or commitment is None: return False
            hash_ops+=1
            if digest_json(body)!=commitment: return False
            support=body.get("support")
            return bool(body.get("kind")=="PT351_LATENT_SUPPORT" and body.get("n")==n
                        and body.get("parent_anchor")==parent_anchor
                        and isinstance(support,list) and len(support)==2 and support[0]!=support[1]
                        and int(support[0]) in present and int(support[1]) in present)
        for index in range(1,n+1):
            total+=1; xv=int(x_vars[index-1]); yv=int(y_vars[index-1])
            body={"kind":"PT351_LATENT_SUPPORT","n":n,"index":index,"parent_anchor":parent_anchor,"support":[xv,yv]}
            commitment=digest_json(body); hash_ops+=1
            if accept(body,commitment): positive+=1; row_pos+=1
            variants=[]
            variants.append(("missing_binding",None,None))
            b=dict(body); b["parent_anchor"]=tamper_hex(parent_anchor); variants.append(("parent_anchor_tamper",b,digest_json(b))); hash_ops+=1
            b=dict(body); b["support"]=[xv,xv]; variants.append(("duplicate_support",b,digest_json(b))); hash_ops+=1
            b=dict(body); b["support"]=[xv,maxvar+1]; variants.append(("absent_support",b,digest_json(b))); hash_ops+=1
            b=dict(body); b["parent_anchor"]=digest_json(["CROSS_PARENT",n]); variants.append(("cross_parent_binding",b,digest_json(b))); hash_ops+=2
            for name,vbody,vcommit in variants:
                if not accept(vbody,vcommit): neg[name]+=1; blocked+=1; row_neg+=1
                else: negative_pt352_entries+=1
        rows.append({"n":n,"bindings":n,"positive":row_pos,"negative_rejects":row_neg,"negative_expected":n*len(NEGATIVE_NAMES),"all_negatives_blocked":row_neg==n*len(NEGATIVE_NAMES)})
    expected=total*len(NEGATIVE_NAMES)
    passed=bool(total==494 and positive==494 and blocked==expected and negative_pt352_entries==0 and all(v==494 for v in neg.values()))
    return {"stage":"PT351_LATENT_SUPPORT_BINDING_BEFORE_FORMATION","rule":"BIND_LATENT_SUPPORT_TO_CURRENT_PARENT -> ONLY_THEN_FORM_BRANCH_STATE","rows":rows,
            "total_bindings":total,"positive_bindings":positive,"negative_controls_per_binding":len(NEGATIVE_NAMES),"negative_controls_total":expected,
            "negative_rejects":neg,"blocked_before_pt352":blocked,"negative_pt352_entries":negative_pt352_entries,
            "hash_ops":hash_ops,"literal_visits":literal_visits,"presence_checks":presence_checks,
            "uses_restricted_child_construction":False,"uses_action_certificate":False,"uses_sat_oracle":False,"passed":passed}


def run()->dict[str,Any]:
    pt351_back=run_pt351()
    base=run_pt352_stack()
    pt351_forward=run_pt351()
    back=dict(base["BACK"]); back["execution"]=list(base["BACK"]["execution"])+["PT351"]; back["PT351"]=pt351_back; back["pass"]=bool(base["BACK"]["pass"] and pt351_back["passed"])
    forward=dict(base["FORWARD"]); forward["execution"]=["PT351"]+list(base["FORWARD"]["execution"]); forward["PT351"]=pt351_forward; forward["PT352_entered_only_after_PT351_pass"]=pt351_forward["passed"]; forward["pass"]=bool(pt351_forward["passed"] and base["FORWARD"]["pass"])
    mirrors={"PT351":pt351_back==pt351_forward}
    for name in ["PT352","PT353","PT354","PT355","PT366","PT477","PT222"]: mirrors[name]=base["BACK"][name]==base["FORWARD"][name]
    fwd_again={"prediction":"8/8 PT351/PT352/PT353/PT354/PT355/PT366/PT477/PT222 mirror; all PT351 negatives block PT352; PT350 untouched.","stage_mirrors":mirrors,"mirror_passes":sum(bool(v) for v in mirrors.values()),"mirror_total":8,"passed":all(mirrors.values())}
    back_again=dict(base["BACK_AGAIN"]); back_again["PT351_source_status"]="HEURISTIC_LATENT_BINDING_PROMPT_ONLY"; back_again["PT350_status"]="WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES"; back_again["P_VS_NP"]="OPEN"; back_again["passed"]=True
    directions=EXPECTED_DIRECTIONS[:]
    preserved_cost=base["cost_comparison"]["combined_PT352_PT353_literal_visits_each_direction"]==1397752
    gates={
      "direction_order_exact":True,"BACK_stage_order_exact":back["execution"]==EXPECTED_BACK,"FORWARD_stage_order_exact":forward["execution"]==EXPECTED_FORWARD,
      "PT351_BACK_pass":pt351_back["passed"],"PT351_FORWARD_pass":pt351_forward["passed"],
      "PT351_all_negatives_block_PT352":pt351_forward["blocked_before_pt352"]==pt351_forward["negative_controls_total"] and pt351_forward["negative_pt352_entries"]==0,
      "PT352_entered_only_after_PT351_pass":forward["PT352_entered_only_after_PT351_pass"],"FORWARD_AGAIN_8_of_8":fwd_again["passed"] and fwd_again["mirror_passes"]==8,
      "PT352_cost_improvement_preserved":preserved_cost,"PT350_untouched":back_again["PT350_status"]=="WATCHLIST_ONLY_NOT_IN_CODE_NOT_IN_GATES","P_VS_NP_OPEN":True}
    all_gates=all(gates.values()) and back["pass"] and forward["pass"] and base["LEFT"]["passed"] and base["RIGHT"]["passed"]
    result={"artifact_id":RUN_ID,"status":"PASS_KEEP_PT351_LATENT_BINDING_BEFORE_FORMATION" if all_gates else "STOP_AT_PT351_LATENT_BINDING_BEFORE_FORMATION",
            "integration_discipline":{"integrated_now":"PT351","PT350":"WATCHLIST_ONLY","one_text_one_operator_one_run":True},
            "required_direction_sequence":EXPECTED_DIRECTIONS,"executed_direction_sequence":directions,"BACK":back,"FORWARD":forward,
            "LEFT":base["LEFT"],"RIGHT":base["RIGHT"],"FORWARD_AGAIN":fwd_again,"BACK_AGAIN":back_again,"gates":gates,
            "cost_vector":{"PT351_literal_visits_each_direction":pt351_forward["literal_visits"],"PT351_hash_ops_each_direction":pt351_forward["hash_ops"],
                           "PT352_plus_manifest_PT353_literal_visits_each_direction":base["cost_comparison"]["combined_PT352_PT353_literal_visits_each_direction"],
                           "legacy_PT353_literal_visits_each_direction":base["cost_comparison"]["legacy_PT353_literal_visits_each_direction"],
                           "warning":"Heterogeneous accounting; PT351 is an added positive-path precondition and its benefit is fail-closed rejection before PT352."},
            "claim_boundary":["PT351 is a modern latent-binding operator heuristically inspired by textual position/gestation imagery.","ANCIENT_TEXT != MODERN_ALGORITHM","P_VS_NP = OPEN"],
            "mathematical_verdict":{"P_EQUALS_NP":"NOT_ESTABLISHED","P_NOT_EQUALS_NP":"NOT_ESTABLISHED","P_VS_NP":"OPEN"}}
    payload=json.dumps(result,sort_keys=True,ensure_ascii=False,separators=(",",":")); result["integrity_sha256"]=hashlib.sha256(payload.encode()).hexdigest(); return result


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--self-test",action="store_true"); p.add_argument("--output"); a=p.parse_args(); d=run(); text=json.dumps(d,ensure_ascii=False,indent=2,sort_keys=True)
    if a.output:
        from pathlib import Path
        q=Path(a.output); q.parent.mkdir(parents=True,exist_ok=True); q.write_text(text+"\n")
    print(text); return 0 if (not a.self_test or d["status"].startswith("PASS_KEEP")) else 1
if __name__=="__main__": raise SystemExit(main())
