#!/usr/bin/env python3
"""Fail-closed E9 source-locked 16 VM/160 cold-child cost-to-observe auditor.

Original E8 training manifest and SHA verified before every validation model is
admitted. Group by actual original CNF SHA, NOT repeated Ubuntu trials.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e9_cost_to_observe as m

def audit(directory,trained):
    model,modelsha=m.checked_model(trained)
    expected={case+"__"+os+".json" for case in m.IDS for os in m.HOSTS}
    found={p.name for p in directory.glob("*.json")}
    if expected!=found:
        raise AssertionError("Not complete original 16 VM source list: "+str({
            "missing":sorted(expected-found),"extra":sorted(found-expected)}))
    sources={case:m.validation_source(case) for case in m.IDS}
    counts=Counter();runners=set();run_ids=set();heads=set()
    perworker={};persource={};all_sha={}
    completed_pairs=[]
    for path in sorted(directory.glob("*.json")):
        case,osname=path.stem.split("__")
        file=path.read_bytes();data=json.loads(file)
        source=sources[case]
        if (data.get("schema")!="JANUS-TIME-SAT-004E9-SOURCE-BOUND-COST-KNN-FIVE-ARM-COLD-VM-V1"
            or data["case"]!=case or data["runner_OS"]!=osname
            or data["original_CNF_SHA256"]!=source["sha"]
            or data["original_complete_SAT_model_SHA256"]!=source["model_sha"]
            or data["trained_model_SHA256"]!=modelsha
            or data["frozen_git_blob"]!=m.PLAN_BLOB
            or (data["CPU_soft_s"],data["WALL_s"],data["RLIMIT_AS_bytes"])!=(m.CPU,m.WALL,m.MEM)
            or data["repetitions"]!=2 or data["cold_children"]!=10
            or data["source_training_overlap"]!=(case in m.PUBLIC)
            or data["no_global_champion"] is not True
            or data["C023_main"]!="UNCHANGED"):
            raise AssertionError("Wrong source SHA, trained model, budget or host in original E9 worker")
        if len(data["records"])!=10:
            raise AssertionError("Missing cold child")
        run_ids.add(str(data["github_run_id"]));heads.add(data["original_head"]);runners.add(data["runner_name"])
        arms={}
        for rep in (0,1):
            subset=[row for row in data["records"] if row["repeat"]==rep]
            if (len(subset)!=5 or {r["arm"] for r in subset}!=set(m.ARMS)
                or any(set(x["shuffled_order"])!=set(m.ARMS) for x in subset)):
                raise AssertionError("Original E9 same-VM five-arm randomized comparison incomplete")
            for row in subset:
                o=row["outcome"]
                if not 0<row["full_cold_child_wall_seconds"]<m.WALL+4:
                    raise AssertionError("Full cold child time invalid")
                if o.get("status") not in m.ALLOWED:
                    raise AssertionError("Non-allowed crash/UNSAT result must not be hidden")
                counts[o["status"]]+=1
                arms.setdefault(row["arm"],[]).append(row)
                if o["status"]==m.SAT:
                    if (o["source_original_CNF_SHA256"]!=source["sha"]
                        or o["source_full_model_SHA256"]!=source["model_sha"]
                        or o["trained_model_SHA256"]!=modelsha
                        or o["source_original_model_pre_and_post"]!="PASS"):
                        raise AssertionError("Returned original SAT model or trained prediction is unverified")
            raw=next(x for x in subset if x["arm"]=="raw_cms")
            for row in subset:
                if (row["arm"]!="raw_cms" and
                    raw["outcome"]["status"]==row["outcome"]["status"]==m.SAT):
                    completed_pairs.append({
                        "case":case,"new_seed":case in m.NEW,"ubuntu":osname,
                        "repetition":rep,"arm":row["arm"],
                        "raw_full_wall":raw["full_cold_child_wall_seconds"],
                        "candidate_full_wall":row["full_cold_child_wall_seconds"],
                        "raw_over_candidate_full_wall":raw["full_cold_child_wall_seconds"]/
                                row["full_cold_child_wall_seconds"]
                    })
        summary={}
        for arm,records in arms.items():
            if len(records)!=2:raise AssertionError("Original child arm repeated/missing")
            sats=sum(r["outcome"]["status"]==m.SAT for r in records)
            summary[arm]={
                "model_verified_SAT":sats,
                "UNKNOWN_CPU":sum(r["outcome"]["status"]=="UNKNOWN_CPU_LIMIT_SIGXCPU" for r in records),
                "UNKNOWN_WALL":sum(r["outcome"]["status"]=="UNKNOWN_WALL_TIMEOUT" for r in records),
                "median_full_cold_wall_if_both_SAT":statistics.median(r["full_cold_child_wall_seconds"] for r in records)
                         if sats==2 else "UNDEFINED_CENSORED",
                "actual_cost_model_predictions":[r["outcome"].get("predecision_prediction") for r in records
                     if r["outcome"]["status"]==m.SAT and arm=="cost_nearest"]
            }
        perworker[path.stem]=summary
        all_sha[path.name]=sha256(file).hexdigest()
    if (len(runners)!=16 or len(run_ids)!=1 or len(heads)!=1
        or len(perworker)!=16 or sum(counts.values())!=160):
        raise AssertionError("16 unique original VM runners/one original HEAD/160 trials required")
    for case in m.IDS:
        pairs=[perworker[case+"__"+os] for os in m.HOSTS]
        persource[case]={
            "development_regression_training_overlap":case in m.PUBLIC,
            "new_seed_same_generator_validation":case in m.NEW,
            "source_sha256":sources[case]["sha"],
            "by_arm":{
                arm:{
                    "original_verified_SAT":sum(x[arm]["model_verified_SAT"] for x in pairs),
                    "original_UNKNOWN_CPU":sum(x[arm]["UNKNOWN_CPU"] for x in pairs),
                    "original_UNKNOWN_WALL":sum(x[arm]["UNKNOWN_WALL"] for x in pairs)
                } for arm in m.ARMS
            }
        }
    return {
        "schema":"JANUS-TIME-SAT-004E9-TRAIN-E8-TEST-NEW-SEED-SAME-GENERATOR-SOURCE-AUDIT-V1",
        "status":"ALL_16_VM_ORIGINAL_SHA_MODEL_BOUND_160_CHILD_RECEIPTS_ACCOUNTED",
        "original_source_run":next(iter(run_ids)),
        "original_source_scientific_HEAD":next(iter(heads)),
        "precommitted_git_blob":m.PLAN_BLOB,
        "trained_model_SHA256":modelsha,
        "original_E8_training_source_cases":8,
        "validation_new_seed_internal_generator_source_cases":6,
        "public_training_overlap_regression_sources":2,
        "original_distinct_GitHub_VM_runner_names":16,
        "original_cold_child_outcomes":sum(counts.values()),
        "all_verdicts":dict(counts),
        "per_source_original_SHA_and_outcomes":persource,
        "per_VM_original_arm_receipts":perworker,
        "original_receipt_SHA256":all_sha,
        "completed_same_VM_finite_raw_candidate_pairs":completed_pairs,
        "complete_pair_count":len(completed_pairs),
        "independent_external_custodian_cases":0,
        "statistical_independence_warning":"16 runner observations from only 8 source CNFs, six new seeds from SAME internal generator, two public sources IN TRAINING; cannot claim blind generality",
        "unknown_not_unsat":True,
        "global_champion":"NOT_ESTABLISHED",
        "C023_main":"UNCHANGED",
        "paid_Rowan":"NONE"
    }

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipts",type=Path,required=True)
    ap.add_argument("--model",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    x=ap.parse_args()
    result=audit(x.receipts,x.model)
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004E9_SCIENTIFIC_AUDIT_PASS",json.dumps({
       "workers":16,"children":160,"new_seed_not_independent":6,
       "results":result["all_verdicts"]},sort_keys=True))
