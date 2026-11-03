#!/usr/bin/env python3
"""JANUS E12C5 R5: cold comparison of a SHA-locked cross-family selector.

Not an external witness. Same-admin SAT original clause replay only.
Censored baselines have NO numerical solve time or speedup.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
from statistics import median
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_time_sat_004e12c5_r5_model as m
import janus_time_sat_004e12c5_r3_selector as r3
import janus_time_sat_004e12c5_profit_test as r1

ARMS=("janus_r5_selector","janus_exact_gf2_ablation",
      "cryptominisat_native_xor","cryptominisat_original_cnf",
      "cadical195_original_cnf")
EXTERNAL=ARMS[2:]
CASES=[x[0] for x in m.CASES]
ORDER_SEED=202611051530
SAT="SAT_VERIFIED_ORIGINAL_CNF"
ABSTAIN="ABSTAIN_NO_EXACT_XOR"
CPU=8
WALL=12
MEM=2_147_483_648

def read_fit(path,expected_sha):
    data=path.read_bytes()
    if sha256(data).hexdigest()!=expected_sha:
        raise AssertionError("R5_FIT_SHA_CHANGED")
    obj=json.loads(data)
    _,proto_sha=m.frozen()
    if (obj["schema"]!="JANUS-E12C5-R5-PAST_ONLY_TWO_CLASS_COST_FIT-V1"
        or obj["prereg_sha256"]!=proto_sha
        or obj["prior_R4_report_blob_sha1"]!=m.R4_REPORT_SHA
        or obj["exact_non_grid_independent_original_count"]!=2
        or obj["R5_originals_in_fit"]!=0
        or not obj["no_model_retraining_on_R5"]
        or set(obj["eligible_non_grid_exact_widths"])!={"4","5"}
        or len(obj["R4_source_original_sha256"])!=8):
        raise AssertionError("R5_WRONG_PAST_ONLY_MODEL")
    return obj

def cold(case,arm,source_sha,fit_path,fit_sha):
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    started=perf_counter()
    _,protocol_sha=m.frozen()
    n,rows=m.source(case)
    gotsha=r1.original_sha(rows,n)
    if gotsha!=source_sha:
        raise AssertionError("R5_SOURCE_SHA_NOT_PRESERVED")
    selected=arm
    reason="EXTERNAL_BASELINE"
    prediction=None
    input_features=None
    profiling_s=None
    native_eq=None
    model=None
    solver_status=ABSTAIN
    if arm=="janus_r5_selector":
        fit=read_fit(fit_path,fit_sha)
        selected,certificate,reason,prediction=m.choose(rows,n,fit)
        input_features=prediction["structural_profile"]
        profiling_s=prediction["profile_wall_s"]
        if selected=="janus_gf2":
            model,err,native_eq=r3.gf2(rows,n,certificate)
        elif selected=="cryptominisat_native_xor":
            model,err,native_eq=r3.crypto(rows,n,True)
        elif selected=="cryptominisat_original_cnf":
            model,err,native_eq=r3.crypto(rows,n,False)
        elif selected=="cadical195_original_cnf":
            model,err=r3.raw_cadical(rows)
        else:
            raise AssertionError("R5_UNKNOWN_SELECTED_SOLVER")
        solver_status=err or SAT
    elif arm=="janus_exact_gf2_ablation":
        features,cover=m.feature_profile(rows,n)
        if cover is not None:
            model,err,native_eq=r3.gf2(rows,n,cover)
            solver_status=err or SAT
    elif arm=="cryptominisat_native_xor":
        features,cover=m.feature_profile(rows,n)
        if cover is not None:
            model,err,native_eq=r3.crypto(rows,n,True)
            solver_status=err or SAT
    elif arm=="cryptominisat_original_cnf":
        model,err,native_eq=r3.crypto(rows,n,False)
        solver_status=err or SAT
    elif arm=="cadical195_original_cnf":
        model,err=r3.raw_cadical(rows)
        solver_status=err or SAT
    else:
        raise AssertionError("R5_UNREGISTERED_ARM")
    witness_sha=None
    if model is not None:
        if not r1.cnf_ok(rows,model):
            raise AssertionError("R5_SAT_MODEL_FAILED_FULL_ORIGINAL_CNF_REPLAY")
        solver_status=SAT
        witness_sha=sha256(m.canonical(model)).hexdigest()
    if solver_status==SAT and not witness_sha:
        raise AssertionError("R5_SAT_RECEIPT_WITH_NO_VALID_WITNESS")
    if solver_status not in (SAT,ABSTAIN,"UNSAT_SOLVER_NO_PORTABLE_PROOF","UNKNOWN_SOLVER"):
        raise AssertionError("R5_UNKNOWN_CHILD_OUTCOME")
    print(json.dumps({
        "schema":"JANUS-E12C5-R5-COLD-V1",
        "case":case,"arm":arm,"selected_engine":selected,
        "reason":reason,"prediction":prediction,
        "input_features":input_features,"feature_profiling_s":profiling_s,
        "source_sha256":gotsha,
        "source_n":n,"source_clauses":len(rows),
        "protocol_sha256":protocol_sha,
        "prior_fit_sha256":fit_sha,
        "solver_status":solver_status,
        "witness_sha256":witness_sha,
        "replayed_original_clause_count":len(rows) if witness_sha else None,
        "certified_xor_equations":native_eq,
        "inner_full_cold_wall_s":perf_counter()-started,
        "cpu_limit_s":CPU,"memory_limit_bytes":MEM,
        "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "no_C023_promotion":True
    },sort_keys=True),flush=True)

def benchmark(fitpath,out):
    p,proto_sha=m.frozen()
    model_sha=sha256(fitpath.read_bytes()).hexdigest()
    fit=read_fit(fitpath,model_sha)
    originals={}
    train_shas=set(fit["R4_source_original_sha256"].values())
    for case,kind,n,width,eq,seed,rem,extra in m.CASES:
        n2,rows=m.source(case)
        if n2!=n:
            raise AssertionError("R5_SOURCE_DIMENSION_DRIFT")
        h=r1.original_sha(rows,n)
        f,cover=m.feature_profile(rows,n)
        if h in train_shas or any(z["sha256"]==h for z in originals.values()):
            raise AssertionError("R5_CURRENT_SOURCE_IN_PAST_TRAINING_OR_DUPLICATED")
        originals[case]={
            "sha256":h,"n":n,"clauses":len(rows),"source_kind":kind,
            "preregistered_width":width,"original_literal_count":sum(len(r) for r in rows),
            "original_full_exact_xor":f["exact_original_xor_cover"],
            "structural_profile":f,"past_training":False}
    if len(originals)!=12:
        raise AssertionError("R5_INCOMPLETE_UNSEEN_COHORT")
    out.mkdir(parents=True,exist_ok=True)
    children=[]
    for ci,case in enumerate(CASES):
        for repetition in range(3):
            ordered=list(ARMS)
            random.Random(ORDER_SEED+ci*100+repetition).shuffle(ordered)
            for slot,arm in enumerate(ordered):
                command=[sys.executable,str(Path(__file__).resolve()),"--child",
                         "--case",case,"--arm",arm,
                         "--source-sha",originals[case]["sha256"],
                         "--fit",str(fitpath),"--fit-sha",model_sha]
                t=perf_counter()
                try:
                    q=subprocess.run(command,text=True,capture_output=True,
                                     timeout=WALL,check=False)
                    if q.returncode==0:
                        result=json.loads(q.stdout)
                        if (result["case"]!=case or result["arm"]!=arm
                            or result["source_sha256"]!=originals[case]["sha256"]
                            or result["protocol_sha256"]!=proto_sha
                            or result["prior_fit_sha256"]!=model_sha):
                            raise AssertionError("R5_COLD_CHILD_SOURCE_OR_FIT_RECEIPT_MISMATCH")
                    else:
                        result={"solver_status":"ERROR_CPU_OR_CHILD_FAILURE",
                                "returncode":q.returncode,"stderr_tail":q.stderr[-1500:]}
                except subprocess.TimeoutExpired:
                    result={"solver_status":"UNKNOWN_WALL_CENSORED"}
                elapsed=perf_counter()-t
                children.append({
                    "case":case,"repeat":repetition,"arm":arm,
                    "randomized_order_slot":slot,
                    "parent_full_cold_wall_s":elapsed,
                    "child":result})
                print("E12C5_R5_COLD",case,repetition,arm,result["solver_status"],
                      round(elapsed,5),flush=True)
    if len(children)!=len(CASES)*3*len(ARMS):
        raise AssertionError("R5_EXPECTED_EXACTLY_180_CHILDREN_PER_WORKER")
    summary={}
    for case in originals:
        arm_stats={}
        for arm in ARMS:
            observations=[q for q in children if q["case"]==case and q["arm"]==arm]
            complete=(len(observations)==3
                      and all(q["child"]["solver_status"]==SAT for q in observations))
            arm_stats[arm]={
                "SAT_replay_3of3":complete,
                "median_verified_full_cold_s":median(q["parent_full_cold_wall_s"] for q in observations) if complete else None,
                "statuses":[q["child"]["solver_status"] for q in observations]
            }
        select=arm_stats[ARMS[0]]
        valid_competitors=[arm_stats[arm]["median_verified_full_cold_s"]
                           for arm in EXTERNAL if arm_stats[arm]["SAT_replay_3of3"]]
        gain=min(valid_competitors)/select["median_verified_full_cold_s"] if (
            select["SAT_replay_3of3"] and valid_competitors) else None
        used=[q["child"]["selected_engine"] for q in children
             if q["case"]==case and q["arm"]==ARMS[0] and q["child"]["solver_status"]==SAT]
        summary[case]={
            "arms":arm_stats,"gain_vs_fastest_completed_external":gain,
            "selected_solver":used[0] if len(used)==3 and len(set(used))==1 else None,
            "all_applicable_competitors_verified":all(
                arm_stats[arm]["SAT_replay_3of3"] or (
                    arm=="cryptominisat_native_xor"
                    and not originals[case]["original_full_exact_xor"])
                for arm in EXTERNAL)
        }
    record={
        "schema":"JANUS-E12C5-R5-RAW-WORKER-V1",
        "pre_registered_protocol_git_blob_sha1":m.FROZEN_BLOB,
        "prereg_sha256":proto_sha,
        "fitted_from_prior_sha256":model_sha,
        "fit_prior_original_source_sha256":fit["R4_source_original_sha256"],
        "source_manifest":originals,
        "raw_cold_records":children,
        "summary":summary,
        "host_platform":platform.platform(),
        "script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "model_script_sha256":sha256(Path(m.__file__).read_bytes()).hexdigest(),
        "censored_not_numeric_win":True,
        "GF2_ablation_not_external_baseline":True,
        "training_cannot_see_R5_SAT_timings":True,
        "external_independent_admin":"NOT_CONNECTED",
        "E12C4":"UNTOUCHED","C023":"UNCHANGED"}
    (out/"RESULT.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
    print("R5_HOST_BENCHMARK_COMPLETED",json.dumps({
        c:{"selected":v["selected_solver"],"gain":v["gain_vs_fastest_completed_external"],
           "all_competitors_verified":v["all_applicable_competitors_verified"]}
        for c,v in summary.items()},sort_keys=True),flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--child",action="store_true")
    a.add_argument("--case",choices=CASES)
    a.add_argument("--arm",choices=ARMS)
    a.add_argument("--source-sha")
    a.add_argument("--fit",type=Path,required=True)
    a.add_argument("--fit-sha")
    a.add_argument("--out",type=Path)
    v=a.parse_args()
    if v.child:
        if not(v.case and v.arm and v.source_sha and v.fit_sha):
            a.error("--child requires --case --arm --source-sha --fit-sha")
        cold(v.case,v.arm,v.source_sha,v.fit,v.fit_sha)
    elif v.out:
        benchmark(v.fit,v.out)
    else:a.error("--out required")
if __name__=="__main__":
    main()
