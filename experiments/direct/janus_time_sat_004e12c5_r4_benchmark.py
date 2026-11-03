#!/usr/bin/env python3
"""E12C5 R4 cold subprocess, exact model replay, frozen prior-only CNF model.

The R4 selector sees only original CNF and pre-trained immutable FIT.json.
Raw failures, abstentions and timeouts remain recorded without winning timings.
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
import janus_time_sat_004e12c5_r4_model as model
import janus_time_sat_004e12c5_r3_selector as r3
import janus_time_sat_004e12c5_profit_test as r1

ARMS=("janus_r4_pre_solve_predictor","janus_gf2_exact_ablation",
      "cryptominisat_native_xor","cryptominisat_original_cnf",
      "cadical195_original_cnf")
CONTROL_ARMS=("cryptominisat_native_xor","cryptominisat_original_cnf",
              "cadical195_original_cnf")
CPU_LIMIT=8
WALL_LIMIT=12
MEM_LIMIT=2147483648
ORDER_SEED=202611031421
SAT="SAT_VERIFIED_ORIGINAL_CNF"
ABSTAIN="ABSTAIN_NO_EXACT_XOR"
CASES=[x[0] for x in model.CASES]

def load_fit(path,expected_sha):
    raw=path.read_bytes()
    if sha256(raw).hexdigest()!=expected_sha:
        raise AssertionError("R4_FIT_SHA_CHANGED_OR_UNTRUSTED")
    _,preregsha=model.load_frozen()
    d=json.loads(raw)
    if (d["schema"]!="JANUS-E12C5-R4-PAST-ONLY-CNF-FIT-V1"
        or d["prereg_sha256"]!=preregsha
        or d["training_original_source_count"]!=13
        or d["training_distinct_side_size_count"]!=12
        or d["training_sources_git_blob_SHA1"]!=dict(model.PAST)
        or len(d["groups"])!=12
        or len(set(d["training_SHAs"]))!=13
        or d["scale"]!=list(model.SCALE)
        or d["K"]!=model.K
        or not d["FITTED_BEFORE_R4_RESULTS"]):
        raise AssertionError("R4_UNTRUSTED_FROZEN_FIT")
    return d

def cold(case,arm,expected_source_sha,fit_path,fit_sha):
    resource.setrlimit(resource.RLIMIT_AS,(MEM_LIMIT,MEM_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU_LIMIT,CPU_LIMIT+1))
    start=perf_counter()
    _,preregsha=model.load_frozen()
    n,rows=model.source(case)
    origsha=r1.original_sha(rows,n)
    if origsha!=expected_source_sha:
        raise AssertionError("R4_COLD_SOURCE_SHA_MISMATCH")
    if origsha in model.load_frozen()[0]["training_policy"].get("training_SHAs",[]):
        raise AssertionError("R4_TRAINING_SET_LEAKED")
    chosen=arm;reason="CONTROL_ONLY";prediction=None;profile_s=0.
    num_eq=None;status=ABSTAIN;signed=None
    if arm=="janus_r4_pre_solve_predictor":
        fit=load_fit(fit_path,fit_sha)
        chosen,cover,prediction,reason,features,profile_s=model.choose(rows,n,fit)
        if chosen=="janus_gf2":
            signed,error,num_eq=r3.gf2(rows,n,cover)
        elif chosen=="cryptominisat_native_xor":
            signed,error,num_eq=r3.crypto(rows,n,True)
        elif chosen=="cryptominisat_original_cnf":
            signed,error,num_eq=r3.crypto(rows,n,False)
        else:
            raise AssertionError("R4_ILLEGAL_SELECTED_ENGINE")
        status=error or SAT
    elif arm=="janus_gf2_exact_ablation":
        start_profile=perf_counter()
        features,cover=model.cnf_profile(rows,n)
        profile_s=perf_counter()-start_profile
        if cover["status"]=="EXACT_XOR_COVER_PASS":
            signed,error,num_eq=r3.gf2(rows,n,cover)
            status=error or SAT
        else:
            status=ABSTAIN
    elif arm=="cryptominisat_native_xor":
        cover=model.xor.group_parity_equations(rows,n)
        if cover["status"]=="EXACT_XOR_COVER_PASS":
            signed,error,num_eq=r3.crypto(rows,n,True)
            status=error or SAT
        else:
            status=ABSTAIN
    elif arm=="cryptominisat_original_cnf":
        signed,error,num_eq=r3.crypto(rows,n,False)
        status=error or SAT
    elif arm=="cadical195_original_cnf":
        signed,error=r3.raw_cadical(rows)
        status=error or SAT
    else:
        raise AssertionError("R4_UNKNOWN_ARM")
    witness_sha=None
    if signed is not None:
        if not r1.cnf_ok(rows,signed):
            raise AssertionError("R4_FALSE_SAT_ORIGINAL_CNF_MODEL")
        witness_sha=sha256(model.canonical(signed)).hexdigest()
        status=SAT
    if status==SAT and witness_sha is None:
        raise AssertionError("R4_FALSE_POSITIVE_MISSING_WITNESS")
    if status not in (SAT,ABSTAIN,"UNSAT_SOLVER_NO_PORTABLE_PROOF","UNKNOWN_SOLVER"):
        raise AssertionError("R4_UNREGISTERED_SOLVER_STATUS")
    print(json.dumps({
      "schema":"JANUS-E12C5-R4-COLD-CHILD-V1",
      "case":case,"arm":arm,"engine_selected":chosen,
      "decision_reason":reason,
      "predictions_prior_only":prediction,
      "feature_profile_wall_s":profile_s,
      "n":n,"clauses":len(rows),
      "original_sha256":origsha,
      "protocol_sha256":preregsha,
      "fit_sha256":fit_sha,
      "status":status,
      "witness_sha256":witness_sha,
      "original_cnf_verified":status==SAT,
      "certified_xor_equation_count":num_eq,
      "parent_subprocess_full_cold_wall_needed":True,
      "inner_wall_s":perf_counter()-start,
      "memory_peak_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "C023":"UNCHANGED"
    },sort_keys=True),flush=True)

def bench(fitpath,out):
    p,psha=model.load_frozen()
    fitsha=sha256(fitpath.read_bytes()).hexdigest()
    fit=load_fit(fitpath,fitsha)
    original_sources={}
    source_shas=set()
    for case,kind,dim,seed in model.CASES:
        n,rows=model.source(case)
        h=r1.original_sha(rows,n)
        if h in source_shas or h in fit["training_SHAs"]:
            raise AssertionError("R4_EVALUATION_SHA_TRAINING_OVERLAP")
        source_shas.add(h)
        f,proof=model.cnf_profile(rows,n)
        original_sources[case]={
           "sha256":h,"n":n,"clauses":len(rows),
           "literal_occurrences":sum(len(x) for x in rows),
           "experimental_family":kind,"training_original":False,
           "exact_xor_coverage":proof["status"]=="EXACT_XOR_COVER_PASS",
           "certification_status":proof["status"],
           "pre_solve_features":f
        }
    if len(original_sources)!=8:
        raise AssertionError("R4_ORIGINAL_SOURCE_COHORT_CHANGED")
    out.mkdir(parents=True,exist_ok=True)
    raw=[]
    for idx,case in enumerate(CASES):
        for repeat in range(3):
            ordered=list(ARMS)
            random.Random(ORDER_SEED+100*idx+repeat).shuffle(ordered)
            for slot,arm in enumerate(ordered):
                command=[sys.executable,str(Path(__file__).resolve()),
                         "--child","--case",case,"--arm",arm,
                         "--source-sha",original_sources[case]["sha256"],
                         "--fit",str(fitpath),"--fit-sha",fitsha]
                start=perf_counter()
                try:
                    r=subprocess.run(command,text=True,capture_output=True,
                                     timeout=WALL_LIMIT,check=False)
                    if r.returncode==0:
                        value=json.loads(r.stdout)
                        if (value["case"]!=case or value["arm"]!=arm
                            or value["original_sha256"]!=original_sources[case]["sha256"]
                            or value["fit_sha256"]!=fitsha
                            or value["protocol_sha256"]!=psha):
                            raise AssertionError("R4_CHILD_RECEIPT_COHORT_DRIFT")
                    else:
                        value={"status":"ERROR_OR_CPU_CENSORED","exit_code":r.returncode,
                               "stderr_tail":r.stderr[-1600:]}
                except subprocess.TimeoutExpired:
                    value={"status":"UNKNOWN_WALL_CENSORED"}
                elapsed=perf_counter()-start
                raw.append({"case":case,"arm":arm,"repeat":repeat,
                            "randomized_slot":slot,"parent_full_cold_wall_s":elapsed,
                            "child":value})
                print("E12C5_R4_COLD",case,repeat,arm,value["status"],
                      round(elapsed,5),flush=True)
    if len(raw)!=8*3*len(ARMS):
        raise AssertionError("R4_MISSING_COLD_CHILDREN")
    summary={}
    for case in CASES:
        byarm={}
        for arm in ARMS:
            data=[x for x in raw if x["case"]==case and x["arm"]==arm]
            complete=len(data)==3 and all(x["child"]["status"]==SAT for x in data)
            byarm[arm]={
                "verified_sat_3of3":complete,
                "median_full_cold_s":median(x["parent_full_cold_wall_s"] for x in data) if complete else None,
                "statuses":[x["child"]["status"] for x in data]
            }
        good=[byarm[a]["median_full_cold_s"] for a in CONTROL_ARMS
              if byarm[a]["verified_sat_3of3"]]
        chosen=byarm[ARMS[0]]
        ratio=min(good)/chosen["median_full_cold_s"] if chosen["verified_sat_3of3"] and good else None
        summary[case]={
            "arms":byarm,
            "ratio_to_fastest_verified_EXTERNAL":ratio,
            "censored_external_controls":[a for a in CONTROL_ARMS
                                         if not byarm[a]["verified_sat_3of3"]],
            "selected_engine":next((x["child"]["engine_selected"]
                for x in raw if x["case"]==case and x["arm"]==ARMS[0] and x["child"]["status"]==SAT),None),
        }
    report={
        "schema":"JANUS-E12C5-R4-RAW-RESULT-V1",
        "protocol_sha256":psha,
        "protocol_blob_sha1":model.FROZEN_BLOB,
        "fit_sha256":fitsha,
        "fit_train_original_sha256":fit["training_SHAs"],
        "fit_leave_one_side_out_median_log_error":fit["leave_one_side_out_median_absolute_log_gain_error"],
        "source_manifest":original_sources,
        "raw_cold_records":raw,
        "summary":summary,
        "executing_R4_script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "executing_R4_model_sha256":sha256(Path(model.__file__).read_bytes()).hexdigest(),
        "host":platform.platform(),
        "threads":1,
        "all_censored_results_retained":True,
        "all_source_SHA_r4_new_and_unique":True,
        "R4_samples_never_used_to_fit_own_selector":True,
        "production_C023":"UNCHANGED",
        "E12C4_loop":"UNMODIFIED",
        "external_independent_witness":"NOT_CONNECTED"
    }
    (out/"RESULT.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("E12C5_R4_HOST_COMPLETE",json.dumps({
      k:{"gain":v["ratio_to_fastest_verified_EXTERNAL"],
         "selected":v["selected_engine"],
         "censored":v["censored_external_controls"]} for k,v in summary.items()},
      sort_keys=True),flush=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--child",action="store_true")
    a.add_argument("--case",choices=CASES)
    a.add_argument("--arm",choices=ARMS)
    a.add_argument("--source-sha")
    a.add_argument("--fit",type=Path,required=True)
    a.add_argument("--fit-sha")
    a.add_argument("--out",type=Path)
    o=a.parse_args()
    if o.child:
        if not (o.case and o.arm and o.source_sha and o.fit_sha):
            a.error("--child requires --case --arm --source-sha --fit-sha")
        cold(o.case,o.arm,o.source_sha,o.fit,o.fit_sha)
    else:
        if o.out is None:a.error("--out required")
        bench(o.fit,o.out)
if __name__=="__main__":
    main()
