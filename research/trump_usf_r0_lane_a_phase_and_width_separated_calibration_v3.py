from __future__ import annotations

"""Lane-A phase+width-separated calibration V3.

Scientific modules are immutable and blob-pinned.  This adapter changes only
calibration semantics already frozen in the phase-separation and
incidence->BA25-factor-width methodological successors.
"""

import argparse, hashlib, importlib, json, math, os, sys, traceback
from pathlib import Path
from typing import Any

OBJECT_ID="TRUMP_USF_R0_LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3"
EXPECTED_LANE_A_RECORDS=36
EXPECTED_GENERATED_REAL_INSTANCES=35

PHASE_SUCCESSOR=("research/TRUMP_USF_R0_LANE_A_INPUT_CLASS_VS_POST_REDUCER_TERMINAL_METHODOLOGICAL_SUCCESSOR_2026-09-10.json","6d8db87c7c0bc36e3e8c08d5df691714aa2448ff")
WIDTH_SUCCESSOR=("research/TRUMP_USF_R0_INCIDENCE_WIDTH_VS_BA25_FACTOR_TD_WIDTH_BINDING_METHODOLOGICAL_SUCCESSOR_2026-09-10.json","9b412cbbef47738ff80fa28355eed42bcd5694c6")
V1_FAILURE=("research/TRUMP_USF_R0_LANE_A_CALIBRATION_DISCOVERY_FAILURE_2026-09-10.json","97b454cefb2be61b6f0ccd021980b06831cab66d",34502250623,"8e139b1eb26a628ff8477d5cf1e984e7f7a86310")
V2_FAILURE=("research/TRUMP_USF_R0_LANE_A_PHASE_SEPARATED_CALIBRATION_V2_FAILURE_2026-09-10.json","0e88340237fd6e151ad14fad4f8565c5f1232d86",34515611337,"7df25df7a2d45bb9117f54fc5882259b3357c694")
ENTRYPOINT=("research/trump_usf_r0_execution_harness_frozen_entrypoint.py","50e8eedd461b87de37385cc9f3d30ea6224909fb")
CORE=("research/trump_usf_r0_execution_harness.py","ed4203bac76349ab377bb97f67bf1054d837bc96")
SCI={
"GENERATOR":("research/trump_usf_r0_frozen_generators.py","fe33883dc08e7e1eacadf287093aa0bb1f16c19a"),
"R37B":("experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py","f37da1c2e1696e35695096a2c748a222af7920cc"),
"R33":("experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py","c9234a1ef639a009cc6cb4c8a6098fd09bf9affe"),
"R34":("experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py","7f9bec920fa47af066570d874fe9127dc4b9b968"),
"R35":("experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py","ad237e341d9659d33da0568f134815776c1f95d8"),
"R35B":("experiments/janus_trump_r35b_single_literal_rup_vivification.py","259d2e38947d09b0c058963ad825a57f2e734203"),
"R38":("experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py","816b53c390d78af415e580eaf358acf191796205"),
"WIDTH_EXTENDER":("experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py","ea36a6b69f8c6034aa00ae4c4217bbd4d7735750"),
"BA25":("research/janus_trump_r50g25ba25.py","cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff"),
}
SOURCE_CLASSES={
"A1_2SAT_EQUIVALENCE_RING":("2CNF","R33_IS_2CNF_ON_ORIGINAL_CANONICAL_CNF"),
"A2_HORN_FORWARD_CHAIN":("HORN","R33_IS_HORN_ON_ORIGINAL_CANONICAL_CNF"),
"A3_RENAMABLE_HORN_FLIPPED_WIDTH3":("RENAMABLE_HORN","R38_GENERAL_RENAMABLE_HORN_RECOGNIZER_ON_ORIGINAL_CANONICAL_CNF"),
"A4_AFFINE_TSEITIN_CIRCULAR_LADDER":("AFFINE_XOR_COMPLETE_CNF_BUNDLE","R34_COMPLETE_AFFINE_CNF_RECOGNITION_ON_ORIGINAL_CANONICAL_CNF"),
}
A5="A5_HISTORICAL_R38"
A5_SOURCE_COMMIT="0b941a484143aa130bad9f7bdf9ca94fbbff79cb"
A5_RESIDUAL_HASH="3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
PHASE_LAW="SOURCE_MEMBERSHIP_PERP_POST_REDUCTION_TERMINAL_LABEL_SUBJECT_TO_EXACT_TRANSFORMATION_SOUNDNESS"
LIFT_LAW="BA25_FACTOR_TD_VERIFIED_WIDTH == max(INCIDENCE_TD_VERIFIED_UB, 1)"
FAILURE_DOMAINS=("SOURCE_CLASS_CALIBRATION_FAILURE","REDUCER_REPLAY_FAILURE","INCIDENCE_WIDTH_AUTHORITY_FAILURE","BA25_FACTOR_TD_BINDING_FAILURE","BA25_DIAGNOSTIC_FAILURE","POST_REDUCER_TERMINAL_CALIBRATION_FAILURE","TRUTH_AUTHORITY_FAILURE","CAUSAL_FIREWALL_FAILURE")
V3_CAUSAL_ORDER=("SCHEDULED_INSTANCE_ID","GENERATE","CANONICALIZE","FREEZE_ORIGINAL_CNF_SHA256","SOURCE_CLASS_CHECK_ORIGINAL_CNF_NO_TRUTH","RUN_FROZEN_REDUCER","CANONICALIZE_RESIDUAL","FREEZE_RESIDUAL_SHA256","MEASURE_INCIDENCE_WIDTH_EVIDENCE","POST_REDUCER_TERMINAL_RECOGNITION","CONSTRUCT_BA25_FACTOR_GRAPH_AND_TD","INDEPENDENT_FACTOR_TD_VALIDATION_AND_WIDTH_MEASUREMENT","VERIFY_FROZEN_TD_LIFT_RELATION","BA25_RESOURCE_GUARD_AND_DIAGNOSTIC_USING_FACTOR_WIDTH","TRUTH_ORACLE_LAST")

class StageFailure(RuntimeError):
    def __init__(self,domain,stage,detail):
        super().__init__(f"{domain}:{stage}:{detail}"); self.domain=domain; self.stage=stage; self.detail=detail

def blob(path:Path)->str:
    b=path.read_bytes(); return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def jbytes(x)->bytes:return (json.dumps(x,indent=2,sort_keys=True)+"\n").encode()
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def assert_pins(root:Path):
    pins={"PHASE_SUCCESSOR":PHASE_SUCCESSOR,"WIDTH_SUCCESSOR":WIDTH_SUCCESSOR,"V1_FAILURE":V1_FAILURE[:2],"V2_FAILURE":V2_FAILURE[:2],"ENTRYPOINT":ENTRYPOINT,"CORE":CORE,**SCI}
    out={}
    for role,(p,e) in pins.items():
        o=blob(root/p)
        if o!=e: raise RuntimeError(f"PINNED_BLOB_DRIFT:{role}:{o}:{e}")
        out[role]={"path":p,"expected":e,"observed":o}
    return out

def modules(root:Path):
    for d in ("research","experiments"):
        s=str(root/d)
        if s not in sys.path: sys.path.insert(0,s)
    core=importlib.import_module("trump_usf_r0_execution_harness")
    entry=importlib.import_module("trump_usf_r0_execution_harness_frozen_entrypoint")
    ass,gen,r33,r34,r35,r35b,r38,width,ba25=core.load_modules(root)
    return core,entry,gen,r33,r34,r35,r35b,r38,width,ba25,ass

def source_check(gen,r33,r34,r38,record,outdir,index):
    if record.family_id==A5:
        return {"applicable":False,"family_id":A5,"SOURCE_CLASS_EXPECTATION_PASS":None,"truth_or_solver_output_consumed":False}
    g=gen.generate(record); f=gen.canonical_formula(g.formula); h=gen.canonical_dimacs_sha256(f)
    cls,authority=SOURCE_CLASSES[record.family_id]
    if cls=="2CNF": full={"recognized":bool(r33.is_2cnf(f)),"predicate":"r33.is_2cnf"}
    elif cls=="HORN": full={"recognized":bool(r33.is_horn(f)),"predicate":"r33.is_horn"}
    elif cls=="RENAMABLE_HORN": full=r38.renamable_horn_recognition(f)
    else: full=r34.recognize_complete_affine_cnf(f)
    rb=jbytes(full); d=outdir/"source_class_receipts"; d.mkdir(parents=True,exist_ok=True); (d/f"{index:03d}.json").write_bytes(rb)
    return {"applicable":True,"scheduled_instance_id":record.scheduled_instance_id,"SOURCE_CLASS":cls,"recognizer_authority":authority,"evaluation_phase":"ORIGINAL_CANONICAL_CNF_BEFORE_FROZEN_REDUCER","original_canonical_dimacs_sha256_frozen_before_recognizer":h,"recognizer_receipt_sha256":sha(rb),"SOURCE_CLASS_EXPECTATION_PASS":bool(full.get("recognized")),"truth_or_solver_output_consumed":False,"exclusive_membership_required":False}

def factor_td_binding(core,width,ba25,width_private):
    """Generic binding; acceptance width is measured from the actual supplied factor TD."""
    u_i=width_private["verified_td_upper_bound"]
    ov=width_private["_orig_vars"]; clauses=width_private["_clauses"]
    inst=ba25.embed_cnf(len(ov),clauses)
    fv,fe=ba25.factor_graph(inst)
    ftd=width.extend_incidence_td_to_ba25(width_private["_td"],len(ov),len(clauses))
    iv=core.independent_validate_td(set(fv),set(fe),ftd.bags,ftd.edges)
    if iv.get("pass") is not True: raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE","INDEPENDENT_FACTOR_TD_VALIDATION",iv)
    u_f=iv["width"]
    expected=max(u_i,1)
    if u_f!=expected: raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE","FROZEN_EXTENDER_LIFT_RELATION",{"measured_u_F":u_f,"u_I":u_i,"expected":expected})
    ok,native=ba25.validate_td(fv,fe,ftd,claimed_tau=u_f)
    if not ok: raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE","BA25_NATIVE_FACTOR_TD_VALIDATION",native)
    pub={"INCIDENCE_TD_VERIFIED_UB":u_i,"BA25_FACTOR_TD_VERIFIED_WIDTH":u_f,"BA25_FACTOR_TD_VALIDATION_PASS":True,"independent_factor_td_validation":iv,"ba25_native_factor_td_validation":native,"frozen_lift_expected_width":expected,"frozen_lift_relation":LIFT_LAW,"frozen_lift_relation_pass":True,"claimed_tau_binding":"BA25_FACTOR_TD_VERIFIED_WIDTH","bare_cross_domain_tau_used":False}
    return pub,{"inst":inst,"factor_td":ftd,"factor_vertices":fv,"factor_edges":fe}

def ba25_v3(core,ba25,r33,residual,binding,private):
    c,_,v=r33.measure(residual); u_f=binding["BA25_FACTOR_TD_VERIFIED_WIDTH"]
    if u_f>core.BA25_MAX_VERIFIED_TAU or v>core.BA25_MAX_RESIDUAL_VARIABLES or c>core.BA25_MAX_RESIDUAL_CLAUSES:
        return {"status":"NOT_RUN_RESOURCE_GUARD","resource_guard_parameter_domain":"BA25_FACTOR_TD_VERIFIED_WIDTH","BA25_FACTOR_TD_VERIFIED_WIDTH":u_f,"limits":{"BA25_FACTOR_TD_VERIFIED_WIDTH":core.BA25_MAX_VERIFIED_TAU,"variables":core.BA25_MAX_RESIDUAL_VARIABLES,"clauses":core.BA25_MAX_RESIDUAL_CLAUSES},"truth_authority":False}
    dp=ba25.run_dp(private["inst"],private["factor_td"],proof=False)
    if dp.get("tau")!=u_f: raise StageFailure("BA25_DIAGNOSTIC_FAILURE","BA25_DP_WIDTH_DOMAIN",{"reported":dp.get("tau"),"verified":u_f})
    if dp.get("state_bound")!=2**(u_f+2): raise StageFailure("BA25_DIAGNOSTIC_FAILURE","BA25_STATE_BOUND_DOMAIN",{"observed":dp.get("state_bound"),"u_F":u_f})
    wr=ba25.witness_receipt(private["inst"],dp.get("witness"))
    if dp.get("sat") and wr.get("direct_verify") is not True: raise StageFailure("BA25_DIAGNOSTIC_FAILURE","BA25_WITNESS_REPLAY",wr)
    return {"status":"BA25_DIAGNOSTIC_COMPLETE","resource_guard_parameter_domain":"BA25_FACTOR_TD_VERIFIED_WIDTH","BA25_FACTOR_TD_VERIFIED_WIDTH":u_f,"peak_table_states":dp["max_states"],"state_bound":dp["state_bound"],"sat_diagnostic":dp["sat"],"model_count_diagnostic":dp["count"],"witness_receipt":wr,"truth_authority":False,"independent_truth_oracle_replaced":False}

def tagged(domain,stage,fn):
    def w(*a,**k):
        try:return fn(*a,**k)
        except StageFailure:raise
        except Exception as e:raise StageFailure(domain,stage,f"{type(e).__name__}:{e}") from e
    return w

def run_entrypoint_v3(mods,instance_id):
    core,entry,gen,r33,r34,r35,r35b,r38,width,ba25,ass=mods
    old=(core.run_frozen_reducer,core.terminal_recognition,core.truth_oracle,entry.width_evidence,entry.ba25_diagnostic)
    factor_holder={}
    def width_tag(c,w,f,label):
        stage="INCIDENCE_WIDTH_"+str(label)
        try:return old[3](c,w,f,label)
        except Exception as e:raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE",stage,f"{type(e).__name__}:{e}") from e
    def bdiag(c,b,w,r,residual,wp):
        try:
            binding,private=factor_td_binding(c,w,b,wp)
            factor_holder["binding"]=binding
            return {"factor_td_binding":binding,**ba25_v3(c,b,r,residual,binding,private)}
        except StageFailure:
            raise
        except Exception as e:
            domain="BA25_DIAGNOSTIC_FAILURE" if "binding" in factor_holder else "BA25_FACTOR_TD_BINDING_FAILURE"
            stage="BA25_DIAGNOSTIC" if "binding" in factor_holder else "FACTOR_TD_BINDING"
            raise StageFailure(domain,stage,f"{type(e).__name__}:{e}") from e
    core.run_frozen_reducer=tagged("REDUCER_REPLAY_FAILURE","RUN_FROZEN_REDUCER",old[0])
    core.terminal_recognition=tagged("POST_REDUCER_TERMINAL_CALIBRATION_FAILURE","POST_REDUCER_TERMINAL_RECOGNITION",old[1])
    core.truth_oracle=tagged("TRUTH_AUTHORITY_FAILURE","TRUTH_ORACLE",old[2])
    entry.width_evidence=width_tag
    entry.ba25_diagnostic=bdiag
    try:
        rec=entry.run_scheduled_instance(instance_id,Path(__file__).resolve().parents[1],execute_truth=True)
    finally:
        core.run_frozen_reducer,core.terminal_recognition,core.truth_oracle,entry.width_evidence,entry.ba25_diagnostic=old
    if "binding" not in factor_holder: raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE","FACTOR_TD_BINDING","BINDING_RECEIPT_MISSING")
    return rec

def reducer_ok(rec):
    r=rec.get("reducer",{}); bad=[]
    if r.get("source_controller_blob_asserted")!=SCI["R37B"][1]:bad.append("R37B_BLOB_DRIFT")
    if r.get("new_reduction_rule_added") is not False:bad.append("NEW_REDUCTION_RULE_FLAG")
    if r.get("initial_canonical_dimacs_sha256")!=rec.get("original_canonical_dimacs_sha256"):bad.append("INITIAL_HASH")
    if r.get("residual_canonical_dimacs_sha256")!=rec.get("residual_canonical_dimacs_sha256"):bad.append("RESIDUAL_HASH")
    for i,x in enumerate(r.get("transformation_ledger",[])):
        if not str(x.get("certificate_replay_status","")).endswith("PASS"):bad.append(f"CERT:{i}")
    return not bad,bad

def incidence_ok(rec):
    bad=[]
    for lab in ("before","after"):
        x=rec.get("width_evidence",{}).get(lab,{})
        iv=x.get("treewidth_interval")
        if not isinstance(iv,list) or len(iv)!=2 or iv[0]>iv[1]:bad.append("INTERVAL:"+lab)
        for k in ("independent_td_validation","independent_degeneracy_replay","independent_minor_min_width_replay"):
            if x.get(k,{}).get("pass") is not True:bad.append(k+":"+lab)
    return not bad,bad

def terminal_ok(core,rec,fam):
    t=rec.get("terminal_recognition",{}); c=t.get("classification"); lab=t.get("terminal")
    if fam==A5:return c=="OPEN_CORE",([] if c=="OPEN_CORE" else ["A5_EXPECTED_OPEN_CORE"])
    if c!="TERMINAL_MEMBER":return False,[f"NOT_TERMINAL_MEMBER:{c}"]
    return lab in core.TERMINAL_CATALOGUE,([] if lab in core.TERMINAL_CATALOGUE else ["OUTSIDE_CATALOGUE"])

def truth_ok(rec):
    t=rec.get("truth_oracle",{}); s=t.get("truth_state")
    if s=="SAT_WITNESS_VERIFIED":return t.get("direct_original_cnf_validation",{}).get("pass") is True
    if s=="UNSAT_PROOF_VERIFIED":return t.get("proof_exists") is True and t.get("checker_exit_code")==0
    return False

def execute(root:Path,out:Path):
    pins=assert_pins(root); mods=modules(root); core,entry,gen,*_=mods
    out.mkdir(parents=True,exist_ok=True); (out/"instances").mkdir(exist_ok=True)
    lane=[x for x in gen.DISCOVERY_SCHEDULE if x.lane=="A"]
    if len(lane)!=EXPECTED_LANE_A_RECORDS:raise RuntimeError("LANE_A_COUNT_DRIFT")
    rows=[]; fails=[]; completed=generated=a5count=0
    for i,r in enumerate(lane):
        src=source_check(gen,mods[3],mods[4],mods[7],r,out,i)
        if src.get("applicable") and src.get("SOURCE_CLASS_EXPECTATION_PASS") is not True:
            rec={"status":"FAIL","scheduled_instance_id":r.scheduled_instance_id,"authoritative_failure_domain":"SOURCE_CLASS_CALIBRATION_FAILURE","exact_causal_stage":"SOURCE_CLASS_CHECK","SOURCE_CLASS":src,"traceback":None}
        else:
            try:
                rec=run_entrypoint_v3(mods,r.scheduled_instance_id)
                if src.get("applicable") and src["original_canonical_dimacs_sha256_frozen_before_recognizer"]!=rec.get("original_canonical_dimacs_sha256"):raise StageFailure("CAUSAL_FIREWALL_FAILURE","SOURCE_PREFLIGHT_HASH_BINDING","SOURCE_AND_ENTRYPOINT_ORIGINAL_HASH_DIFFER")
                rok,rbad=reducer_ok(rec)
                if not rok:raise StageFailure("REDUCER_REPLAY_FAILURE","REDUCER_CERTIFICATE_REPLAY",rbad)
                wok,wbad=incidence_ok(rec)
                if not wok:raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE","INCIDENCE_WIDTH_REPLAY",wbad)
                tok,tbad=terminal_ok(core,rec,r.family_id)
                if not tok:raise StageFailure("POST_REDUCER_TERMINAL_CALIBRATION_FAILURE","POST_REDUCER_TERMINAL_RECOGNITION",tbad)
                if not truth_ok(rec):raise StageFailure("TRUTH_AUTHORITY_FAILURE","TRUTH_AUTHORITY_REPLAY",rec.get("truth_oracle",{}))
                if r.family_id==A5:
                    red=rec.get("reducer",{})
                    if red.get("A5_source_commit")!=A5_SOURCE_COMMIT or red.get("A5_historical_internal_residual_hash")!=A5_RESIDUAL_HASH:raise StageFailure("CAUSAL_FIREWALL_FAILURE","A5_HISTORICAL_REPLAY","A5_PROVENANCE_DRIFT")
                aft=rec["width_evidence"]["after"]; bind=rec["BA25_diagnostic"]["factor_td_binding"]
                rec["SOURCE_CLASS"]=src
                rec["INCIDENCE_TW_LB"]=aft["treewidth_lower_bound"];rec["INCIDENCE_TD_VERIFIED_UB"]=aft["verified_td_upper_bound"];rec["INCIDENCE_TW_INTERVAL"]=aft["treewidth_interval"]
                rec["BA25_FACTOR_TD_VERIFIED_WIDTH"]=bind["BA25_FACTOR_TD_VERIFIED_WIDTH"];rec["BA25_FACTOR_TD_VALIDATION_PASS"]=bind["BA25_FACTOR_TD_VALIDATION_PASS"];rec["BA25_FACTOR_TD_LIFT_RELATION_PASS"]=bind["frozen_lift_relation_pass"]
                rec["pass_flags"]={"SOURCE_CLASS_EXPECTATION_PASS":src.get("SOURCE_CLASS_EXPECTATION_PASS") if src.get("applicable") else None,"REDUCER_CERTIFICATE_REPLAY_PASS":True,"INCIDENCE_WIDTH_AUTHORITY_PASS":True,"BA25_FACTOR_TD_BINDING_PASS":True,"BA25_DIAGNOSTIC_VALID_OR_RESOURCE_GUARDED":rec["BA25_diagnostic"]["status"] in {"BA25_DIAGNOSTIC_COMPLETE","NOT_RUN_RESOURCE_GUARD"},"POST_REDUCER_TERMINAL_SOUND":True,"TRUTH_AUTHORITY_PASS":True,"CAUSAL_FIREWALL_PASS":True,"SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL_REQUIRED":False,"BARE_CROSS_DOMAIN_TAU_USED":False}
                rec["status"]="PASS";rec["causal_order_v3"]=V3_CAUSAL_ORDER;rec["truth_is_last_authoritative_stage"]=True
            except Exception as e:
                if isinstance(e,StageFailure):domain,stage,detail=e.domain,e.stage,e.detail
                else:domain,stage,detail="PIPELINE_INFRASTRUCTURE_FAILURE","UNCLASSIFIED",f"{type(e).__name__}:{e}"
                rec={"status":"FAIL","scheduled_instance_id":r.scheduled_instance_id,"family_id":r.family_id,"variant":r.variant,"authoritative_failure_domain":domain,"exact_causal_stage":stage,"detail":detail,"SOURCE_CLASS":src,"traceback":traceback.format_exc(),"finite_experiment_is_asymptotic_authority":False}
        b=jbytes(rec);(out/"instances"/f"{i:03d}.json").write_bytes(b)
        row={"scheduled_instance_id":r.scheduled_instance_id,"family_id":r.family_id,"variant":r.variant,"status":rec["status"],"record_sha256":sha(b)}
        if rec["status"]=="PASS":
            completed+=1;generated+=int(rec.get("generated_real_instance_increment",0));a5count+=int(r.family_id==A5)
            row.update({"original_sha256":rec.get("original_canonical_dimacs_sha256"),"residual_sha256":rec.get("residual_canonical_dimacs_sha256"),"INCIDENCE_TW_LB":rec.get("INCIDENCE_TW_LB"),"INCIDENCE_TD_VERIFIED_UB":rec.get("INCIDENCE_TD_VERIFIED_UB"),"INCIDENCE_TW_INTERVAL":rec.get("INCIDENCE_TW_INTERVAL"),"BA25_FACTOR_TD_VERIFIED_WIDTH":rec.get("BA25_FACTOR_TD_VERIFIED_WIDTH"),"BA25_FACTOR_TD_VALIDATION_PASS":rec.get("BA25_FACTOR_TD_VALIDATION_PASS"),"post_terminal":rec.get("terminal_recognition"),"BA25_status":rec.get("BA25_diagnostic",{}).get("status"),"truth_state":rec.get("truth_oracle",{}).get("truth_state"),"pass_flags":rec.get("pass_flags")})
        else:
            row.update({"authoritative_failure_domain":rec.get("authoritative_failure_domain"),"exact_causal_stage":rec.get("exact_causal_stage"),"detail":rec.get("detail")});fails.append(row)
        rows.append(row)
        if rec["status"]!="PASS":break
    passed=not fails and completed==36 and generated==35 and a5count==1
    result={"schema":OBJECT_ID+"_RESULT","version":"3.0","status":"LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_PASSED" if passed else "LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_FAILURE_STOPPED","phase_successor_blob":PHASE_SUCCESSOR[1],"width_successor_blob":WIDTH_SUCCESSOR[1],"phase_separation_law":PHASE_LAW,"width_lift_law":LIFT_LAW,"historical_failures_preserved":{"V1":{"run_id":V1_FAILURE[2],"receipt_commit":V1_FAILURE[3],"status_remains":"FAILED","retroactive_promotion":False},"V2":{"run_id":V2_FAILURE[2],"receipt_commit":V2_FAILURE[3],"status_remains":"FAILED","retroactive_promotion":False}},"workflow_commit":os.environ.get("GITHUB_SHA"),"run_id":int(os.environ["GITHUB_RUN_ID"]) if os.environ.get("GITHUB_RUN_ID") else None,"pinned_source_assertions":pins,"failure_domains":FAILURE_DOMAINS,"scheduled_lane_a_discovery_count":36,"completed_lane_a_records":completed,"generated_real_USF_instances_this_v3_gate":generated,"A5_historical_replay_count":a5count,"instances":rows,"failures":fails,"LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_PASSED":passed,"LANE_A_EXECUTION_COMPLETE":passed,"LANE_B_EXECUTION_STARTED":False,"LANE_C_EXECUTION_STARTED":False,"HOLDOUT_EXECUTION_STARTED":False,"PRIMARY_BLOCKER":"UNIVERSAL_RESIDUAL_STRUCTURAL_FUNNEL_THEOREM","H1":"OPEN","H2":"OPEN","H3":"OPEN","SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN","BA26_STARTED":False,"H1_supported_by_this_gate":False,"lane_b_release_if_passed_requires_separate_gate":passed,"stop":"STOP_AFTER_LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_NO_LANE_B_NO_LANE_C_NO_HOLDOUT_NO_BA26"}
    bb=jbytes(result);(out/"LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_RESULT.json").write_bytes(bb);(out/"LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_RESULT.sha256").write_text(sha(bb)+"  LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_RESULT.json\n")
    print("LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_RESULT_SHA256="+sha(bb));print("LANE_A_V3_COMPLETED_RECORDS="+str(completed));print("LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_PASSED="+str(passed).lower())
    return result

def contract_only(root:Path):
    pins=assert_pins(root)
    p=json.loads((root/PHASE_SUCCESSOR[0]).read_text());w=json.loads((root/WIDTH_SUCCESSOR[0]).read_text())
    assert p["future_lane_a_pass_contract"]["explicitly_not_required"]=="SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL"
    assert w["future_ba25_binding_rule"]["claimed_tau_binding"]=="claimed_tau = BA25_FACTOR_TD_VERIFIED_WIDTH"
    assert w["future_ba25_binding_rule"]["required_lift_relation"]==LIFT_LAW
    return {"schema":OBJECT_ID+"_INERT_CONTRACT","pins_pass":True,"pins":pins,"real_lane_a_instance_executed":False,"phase_separation_active":True,"width_separation_active":True,"claimed_tau_binding":"BA25_FACTOR_TD_VERIFIED_WIDTH","lane_b_authorized":False,"lane_c_authorized":False,"holdout_authorized":False,"BA26_authorized":False}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--root",default=str(Path(__file__).resolve().parents[1]));ap.add_argument("--verify-contract-only",action="store_true");ap.add_argument("--execute-lane-a-v3",action="store_true");ap.add_argument("--output-dir");a=ap.parse_args();root=Path(a.root).resolve()
    if a.verify_contract_only:print(json.dumps(contract_only(root),indent=2,sort_keys=True));return
    if a.execute_lane_a_v3:
        if not a.output_dir:raise SystemExit("--output-dir required")
        execute(root,Path(a.output_dir).resolve());return
    raise SystemExit("V3_INERT")
if __name__=="__main__":main()
