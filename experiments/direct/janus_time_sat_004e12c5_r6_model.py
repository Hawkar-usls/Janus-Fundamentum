#!/usr/bin/env python3
"""JANUS R6: frozen R5-only cost forecasts for exact XOR and mixed CNF.

Pre-solve structural classifier, no SAT outcome or benchmark timing used
for selection. One historical source in mixed/width3 is *weak evidence*;
this is a falsifiable, development-only selector, not production.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha1,sha256
import json
import math
from pathlib import Path
from statistics import median
from time import perf_counter
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
import janus_time_sat_004e12c5_r5_model as r5
import janus_time_sat_004e12c5_r3_selector as r3
import janus_time_sat_004e12c5_profit_test as r1

PROTOCOL=ROOT/"experiments/time_sat_004_external/E12C5_R6_PREREG.json"
PROTOCOL_BLOB_SHA="150fc8b9d27a37485f46e0a2bd5aaf6ab6a3450f"
TRAINING=ROOT/"experiments/time_sat_004_external/E12C5_R6_PRIOR_R5_TIMINGS.json"
TRAINING_BLOB_SHA="ffbf8f231b473f985f1baf3a4c1afa8f3abf6fec"
R5_POSTRUN=ROOT/"experiments/time_sat_004_external/E12C5_R5_POSTRUN_REPORT.json"
R5_POSTRUN_BLOB_SHA="9ceb03f8738b4ed2d45159695ff354051da5799b"
CASES=(
 ("r6_xor3_80","EXACT_RANDOM_XOR",80,3,80,2026110603080,0,0),
 ("r6_xor3_128","EXACT_RANDOM_XOR",128,3,128,2026110603128,0,0),
 ("r6_xor4_128","EXACT_RANDOM_XOR",128,4,128,2026110604128,0,0),
 ("r6_xor5_160","EXACT_RANDOM_XOR",160,5,160,2026110605160,0,0),
 ("r6_xor6_96","EXACT_RANDOM_XOR",96,6,96,2026110606096,0,0),
 ("r6_mixed4_112","MIXED_XOR_PLUS_CNF",112,4,112,2026110608112,0,48),
 ("r6_mixed4_144","MIXED_XOR_PLUS_CNF",144,4,144,2026110608144,0,64),
 ("r6_mixed5_128","MIXED_XOR_PLUS_CNF",128,5,128,2026110608128,0,56),
 ("r6_partial4_128","DAMAGED_RANDOM_XOR",128,4,128,2026110607128,1,0),
 ("r6_partial5_128","DAMAGED_RANDOM_XOR",128,5,128,2026110607528,1,0),
 ("r6_3cnf96","PLANTED_3CNF",96,3,0,2026110609096,0,336),
 ("r6_3cnf144","PLANTED_3CNF",144,3,0,2026110609144,0,504),
)
EXT_ARMS=("cryptominisat_native_xor","cryptominisat_original_cnf","cadical195_original_cnf")
GF2_ARM="janus_exact_gf2_ablation"
SAT="SAT_VERIFIED_ORIGINAL_CNF"

def canonical(x):
    return (json.dumps(x,sort_keys=True,separators=(",",":"))+"\n").encode()

def blob_sha(data):
    return sha1(b"blob "+str(len(data)).encode()+bytes([0])+data).hexdigest()

def frozen_protocol():
    raw=PROTOCOL.read_bytes()
    if blob_sha(raw)!=PROTOCOL_BLOB_SHA:
        raise AssertionError("R6_PREREG_CHANGED_AFTER_MEASUREMENT_FREEZE")
    p=json.loads(raw)
    actual=[(q["id"],q["kind"],q["n"],q.get("width",3),q.get("equations",0),
             q["seed"],q.get("removed_clauses",0),q.get("extra_3cnf",q.get("m",0)))
             for q in p["new_sources"]]
    if (p["schema"]!="JANUS-E12C5-R6-PREREG-CROSS-FAMILY-COST-FORECAST-V1"
        or actual!=list(CASES)
        or p["evaluation"]["total_cold_subprocesses"]!=360
        or p["history"]["primary_training_blob_sha1"]!=TRAINING_BLOB_SHA):
        raise AssertionError("R6_FROZEN_COHORT_DRIFT")
    return p,sha256(raw).hexdigest()

def read_training():
    p,_=frozen_protocol()
    raw=TRAINING.read_bytes()
    if blob_sha(raw)!=TRAINING_BLOB_SHA:
        raise AssertionError("R6_R5_TRAINING_BLOB_CHANGED")
    report_raw=R5_POSTRUN.read_bytes()
    if blob_sha(report_raw)!=R5_POSTRUN_BLOB_SHA:
        raise AssertionError("R6_R5_ORIGINAL_REPORT_SHA_CHANGED")
    report=json.loads(report_raw)
    j=json.loads(raw)
    if (j["schema"]!="JANUS-E12C5-R6-PAST-TRAINING-TIMING-SNAPSHOT-V1"
        or j["n_distinct_historical_originals"]!=12
        or len(j["hosts"])!=2
        or j["r5_original_sha256"]!={
            key:value["sha256"] for key,value in report["source_manifest"].items()}
        or report["frozen_scientific_verdict"]!="R5_NO_PREREGISTERED_GENERALIZED_GAIN"
        or len(set(j["r5_original_sha256"].values()))!=12
        or len({h["host_job_id"] for h in j["hosts"]})!=2):
        raise AssertionError("R6_R5_TRAINING_NOT_REPRODUCIBLE")
    return j

def source(case):
    registered=next((q for q in CASES if q[0]==case),None)
    if registered is None:
        raise AssertionError("R6_UNREGISTERED_TEST_SOURCE")
    _,kind,n,width,eq,seed,removed,extra=registered
    return r5.plant_random_xor(n,width,eq,seed,removed,extra)

def signmask_profile(rows,n):
    """Only CNF sign patterns and support counts; never GF2 elimination."""
    if n<1 or n>2500 or len(rows)>35000:
        raise AssertionError("R6_UNSAFE_INPUT_SIZE")
    groups={}
    lengths=Counter()
    literals=0
    for row in rows:
        if not row or len(row)>6:
            raise AssertionError("R6_BAD_CLAUSE_WIDTH")
        literals+=len(row)
        if literals>160000:
            raise AssertionError("R6_TOO_MANY_LITERALS")
        if any(type(x) is not int or abs(x)>n or x==0 for x in row):
            raise AssertionError("R6_BAD_LITERAL")
        support=tuple(sorted(abs(v) for v in row))
        if len(set(support))!=len(row):
            raise AssertionError("R6_DUPLICATE_VARIABLE_IN_CLAUSE")
        mask=sum(1<<i for i,v in enumerate(support) if -v in row)
        groups.setdefault(support,[]).append(mask)
        lengths[len(row)]+=1
    certified=[]
    residual=[]
    for support,masks in groups.items():
        is_full=(len(masks)==2**(len(support)-1) and
                 len(masks)==len(set(masks)) and
                 len({x.bit_count()%2 for x in masks})==1)
        (certified if is_full else residual).append((support,masks))
    full=not residual and bool(certified)
    # Independent exact full-cover proof when selecting standalone GF2.
    cover=None
    if full:
        cover=r5.r4.xor.group_parity_equations(rows,n)
        if (cover.get("status")!="EXACT_XOR_COVER_PASS"
            or len(cover["equations"])!=len(certified)):
            raise AssertionError("R6_EXACT_CNF_PROOF_MISMATCH")
    widths=Counter(len(s) for s,m in certified)
    width=next(iter(widths)) if len(widths)==1 else None
    degrees=[0]*(n+1)
    for support,masks in certified:
        for v in support:degrees[v]+=1
    av=sum(degrees[1:])/n
    cv=math.sqrt(sum((x-av)**2 for x in degrees[1:])/n)/av if av else 0.
    extra_clause_count=sum(len(mask) for s,mask in residual)
    profile={
        "n":n,"clauses":len(rows),"literals":literals,
        "clause_lengths":dict(lengths),
        "complete_parity_blocks":len(certified),
        "incomplete_support_groups":len(residual),
        "incomplete_clause_count":extra_clause_count,
        "complete_block_fraction":len(certified)/len(groups),
        "complete_equation_width_histogram":dict(widths),
        "uniform_complete_equation_width":width,
        "complete_equations_per_var":len(certified)/n,
        "complete_support_degree_cv":cv,
        "whole_original_exact_xor":full,
        "incomplete_clause_widths":dict(Counter(len(s) for s,m in residual
                                                   for _ in m)),
    }
    return profile,cover

def med_for(host,case,arm):
    r=host["case_medians"][case][arm]
    t=r["median_rounded_full_cold_s"]
    if t is None:
        return None
    if (r["statuses"]!=[SAT]*3 or type(t) not in (float,int) or t<=0):
        raise AssertionError("R6_NUMERIC_TIMING_NOT_PROVEN_SAT_THREE_REPEATS")
    return t

def history_class(fit_cases):
    j=read_training()
    result={}
    for case in fit_cases:
        by_host=[]
        for h in j["hosts"]:
            arms={a:med_for(h,case,a) for a in (GF2_ARM,)+EXT_ARMS}
            best=min(z for z in (arms[a] for a in EXT_ARMS) if z is not None)
            by_host.append({"host":h["host_job_name"],"times":arms,
                "fastest_external_s":best,
                "GF2_over_fastest":best/arms[GF2_ARM] if arms[GF2_ARM] is not None else None,
                "CMS_original_over_CaDiCaL":(
                    arms["cryptominisat_original_cnf"]/arms["cadical195_original_cnf"]
                    if arms["cryptominisat_original_cnf"] is not None
                       and arms["cadical195_original_cnf"] is not None else None)})
        result[case]={
            "original_sha256":j["r5_original_sha256"][case],
            "prior_hosts":by_host
        }
    return result

def fit_from_past():
    _,proto_sha=frozen_protocol()
    names=["r5_xor3_96","r5_xor4_112a","r5_xor4_160",
           "r5_xor5_144a","r5_xor5_144b","r5_xor6_128",
           "r5_mixed4_112","r5_mixed5_144","r5_partial4_112",
           "r5_partial5_144","r5_three96","r5_three144"]
    prior=history_class(names)
    decisions={}
    def ratios(cases,key):
        return [q[key] for name in cases for q in prior[name]["prior_hosts"]]
    decisions["gf2_width3_supported"]=min(ratios(["r5_xor3_96"],"GF2_over_fastest"))>=1.15
    decisions["gf2_width4_supported"]=min(ratios(["r5_xor4_112a","r5_xor4_160"],"GF2_over_fastest"))>=1.25
    decisions["gf2_width5_supported"]=min(ratios(["r5_xor5_144a","r5_xor5_144b"],"GF2_over_fastest"))>=1.25
    decisions["cadical_mixed4_supported"]=min(ratios(["r5_mixed4_112"],"CMS_original_over_CaDiCaL"))>=1.50
    decisions["cadical_partial4_supported"]=min(ratios(["r5_partial4_112"],"CMS_original_over_CaDiCaL"))>=1.30
    if not all(decisions.values()):
        raise AssertionError("R6_FROZEN_R5_TRAINING_SUPPORT_NOT_PRESENT")
    prior_shas=[r["original_sha256"] for r in prior.values()]
    if len(prior_shas)!=12 or len(set(prior_shas))!=12:
        raise AssertionError("R6_MISSING_12_UNIQUE_PRIOR_ORIGINALS")
    return {
        "schema":"JANUS-E12C5-R6-PAST_ONLY-FROZEN_COST_FIT-V1",
        "prereg_sha256":proto_sha,
        "prior_training_blob_sha1":TRAINING_BLOB_SHA,
        "prior_report_blob_sha1":R5_POSTRUN_BLOB_SHA,
        "historical_cases":prior,
        "training_original_SHA256":sorted(prior_shas),
        "n_originals":12,"n_distinct_GITUB_Hosts":2,
        "decisions":decisions,
        "no_R6_source_used_for_fit":True,
        "no_numeric_gain_for_censored_baseline":True,
        "main_C023":"UNCHANGED"
    }

def estimated_costs(fit,n,prior_case,kind):
    """Pre-solve extrapolation from exactly one or two historical source SHA."""
    historical=fit["historical_cases"][prior_case]
    source_n=int(prior_case.rsplit("_",1)[-1]) if False else None
    reference_n={"r5_xor3_96":96,"r5_xor4_112a":112,
                 "r5_xor4_160":160,"r5_xor5_144a":144,
                 "r5_xor5_144b":144,"r5_mixed4_112":112,
                 "r5_partial4_112":112}.get(prior_case)
    if reference_n is None:raise AssertionError("UNREGISTERED_COST_PRIOR")
    factor=(n/reference_n)**1.5
    times={}
    for key in (GF2_ARM,)+EXT_ARMS:
        xs=[h["times"][key] for h in historical["prior_hosts"] if h["times"][key] is not None]
        times[key]=median(xs)*factor if xs else None
    external=[times[x] for x in EXT_ARMS if times[x] is not None]
    return {"cost_forecast_full_cold_seconds":times,
            "forecast_fastest_verified_external_seconds":min(external),
            "historical_support_original_sha256":[historical["original_sha256"]],
            "historical_reference_case":prior_case,
            "extrapolation_power":1.5}

def choose(rows,n,fit):
    """No source ID/seed/known label passed; strictly input-structure only."""
    t=perf_counter()
    f,cover=signmask_profile(rows,n)
    elapsed=perf_counter()-t
    if (fit["schema"]!="JANUS-E12C5-R6-PAST_ONLY-FROZEN_COST_FIT-V1"
        or not fit["no_R6_source_used_for_fit"]):
        raise AssertionError("R6_NOT_FROZEN_PAST_ONLY_FIT")
    info={"features":f,"profile_wall_s":elapsed,
          "forecast":None,"prior_only":True}
    if elapsed>2.0:
        return "cryptominisat_original_cnf",None,"STRUCTURAL_PROFILING_OVERRUN_SAFE_RAW",info
    w=f["uniform_complete_equation_width"]
    density=f["complete_equations_per_var"]
    cv=f["complete_support_degree_cv"]
    eligible=0.8<=density<=1.2 and .25<=cv<=.75
    if f["whole_original_exact_xor"]:
        basis={3:"r5_xor3_96",4:"r5_xor4_112a",5:"r5_xor5_144a"}
        if w in basis and eligible and 64<=n<=180 and fit["decisions"]["gf2_width"+str(w)+"_supported"]:
            info["forecast"]=estimated_costs(fit,n,basis[w],"full_exact")
            info["confidence_lower_bound_gain"]=min(h["GF2_over_fastest"] for h in
                                  fit["historical_cases"][basis[w]]["prior_hosts"])
            return "janus_gf2",cover,"PRIOR_EXACT_WIDTH"+str(w)+"_GAIN_SUPPORT",info
        return "cryptominisat_native_xor",cover,"UNCERTAIN_EXACT_XOR_NATIVE_FALLBACK",info
    # A damaged parity block is not a certified XOR equation; route full original CNF.
    full_groups=f["complete_parity_blocks"]
    incompletes=f["incomplete_support_groups"]
    residual=f["incomplete_clause_count"]
    residual_widths=set(map(int,f["incomplete_clause_widths"]))
    if (w==4 and incompletes==1
        and f["complete_block_fraction"]>.97
        and residual_widths=={4}
        and fit["decisions"]["cadical_partial4_supported"]):
        info["forecast"]=estimated_costs(fit,n,"r5_partial4_112","partial4")
        return "cadical195_original_cnf",None,"PRIOR_SINGLE_DAMAGED_WIDTH4_CADICAL",info
    if (w==4 and incompletes>=1
        and residual_widths=={3}
        and .25<=residual/max(1,full_groups)<=.75
        and .8<=density<=1.2 and 80<=n<=180
        and fit["decisions"]["cadical_mixed4_supported"]):
        info["forecast"]=estimated_costs(fit,n,"r5_mixed4_112","mixed4")
        return "cadical195_original_cnf",None,"PRIOR_MIXED_WIDTH4_CADICAL",info
    return "cryptominisat_original_cnf",None,"UNSUPPORTED_OR_SPARSE_MIXED_SAFE_RAW",info

def preflight():
    fit=fit_from_past()
    source_shas=[]
    for case,kind,n,width,eq,seed,dmg,extra in CASES:
        actual_n,rows=source(case)
        if n!=actual_n:raise AssertionError("R6_SOURCE_N_MISMATCH")
        sha=r1.original_sha(rows,n)
        if sha in fit["training_original_SHA256"]:
            raise AssertionError("R6_TRAINING_SOURCE_LEAK")
        source_shas.append(sha)
        engine,cover,reason,info=choose(rows,n,fit)
        if kind=="EXACT_RANDOM_XOR" and cover is None:
            raise AssertionError("R6_EXACT_PARITY_NOT_CERTIFIED")
        if kind!="EXACT_RANDOM_XOR" and engine in ("janus_gf2","cryptominisat_native_xor"):
            raise AssertionError("R6_INVALID_NONEXACT_SOLVER_SELECTION")
    if len(set(source_shas))!=12:raise AssertionError("R6_DUPLICATED_NEW_SOURCE")
    print("R6_NEW_ORIGINAL_SHA_PROOF_PASS",json.dumps(dict(zip((x[0] for x in CASES),source_shas)),sort_keys=True))
    return fit

def main():
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--preflight",action="store_true")
    a.add_argument("--fit-output",type=Path)
    args=a.parse_args()
    if args.fit_output:
        fit=fit_from_past()
        args.fit_output.parent.mkdir(parents=True,exist_ok=True)
        args.fit_output.write_bytes(canonical(fit))
        print("R6_PAST_ONLY_FIT_SHA256",sha256(args.fit_output.read_bytes()).hexdigest(),
              "historical",len(fit["training_original_SHA256"]))
    if args.preflight:preflight()
if __name__=="__main__":
    main()
