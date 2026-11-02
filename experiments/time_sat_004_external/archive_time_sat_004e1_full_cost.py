#!/usr/bin/env python3
"""004E1: preserve exact original dual-host public full-cost calibration results.

Refuse to turn resource-censored controls into finite speedup ratios, and do
not claim independent blind evaluation of a repeatedly viewed public CNF.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import shutil
import statistics
import zipfile

RUN=41417001461
HEAD="8a3feced3c5e9d1171286a41b83f900fc7c83fec"
CNF_SHA="8d94924bef8978b28a2bf95472556b280bef5d98b6833c6db33554098f52d2d8"
ARMS=("janus_extracted_xor_cms_native",
      "cryptominisat_original_cnf",
      "cadical195_original_cnf",
      "glucose4_original_cnf")
SUCCESS="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
UNKNOWN={"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_NATIVE_SOLVER_NO_ANSWER","UNKNOWN_CDCL_NO_ANSWER"}
ORIGINAL=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence/7db30d12cb06f0dc2f30abff80d96d6a.original.cnf")

def sha(b):return sha256(b).hexdigest()

def original(host,zip_path,want_sha):
    raw=zip_path.read_bytes()
    if sha(raw)!=want_sha:raise AssertionError("Original Actions ZIP SHA mismatch")
    with zipfile.ZipFile(zip_path) as z:
        if set(z.namelist())!={"comparison.json"}:
            raise AssertionError("Unexpected original Actions artifact ZIP contents")
        payload=z.read("comparison.json")
    j=json.loads(payload)
    if (j["schema"]!="JANUS-TIME-SAT-004E1-BINARY-TREE-PUBLIC-FULL-COLD-CPU-WALL-2026-11-02-V1"
        or j["github_run_id"]!=str(RUN)
        or j["github_head"]!=HEAD
        or j["source_sha256"]!=CNF_SHA
        or j["CPU_limit_seconds"]!=30
        or j["wall_timeout_seconds"]!=36
        or j["repeats"]!=2
        or tuple(j["arms"])!=ARMS):
        raise AssertionError("Original CI source/head/CPU/arms inconsistent")
    byarm=defaultdict(list)
    if len(j["results"])!=8:raise AssertionError("Original paired arm grid incomplete")
    for row in j["results"]:
        arm=row["arm"]
        if arm not in ARMS or row["repeat"] not in (0,1):
            raise AssertionError("Nonpreregistered arm or repetition")
        if row["arm_order"] and set(row["arm_order"])!=set(ARMS):
            raise AssertionError("Frozen arm order modified")
        byarm[arm].append(row)
        detail=row["result"]
        verdict=detail.get("status",detail.get("verdict"))
        if verdict not in {SUCCESS}|UNKNOWN:
            raise AssertionError("Unexpected engine error or UNSAT on verified SAT "+str(verdict))
        if verdict==SUCCESS and detail["source_original_sha256"]!=CNF_SHA:
            raise AssertionError("Successful model not bound to source SHA")
    if any(len(byarm[arm])!=2 or sorted(r["repeat"] for r in byarm[arm])!=[0,1]
           for arm in ARMS):
        raise AssertionError("Original case/arm grid not paired")
    summary={}
    for arm in ARMS:
        records=byarm[arm]
        complete=[r for r in records if r["result"].get("status")==SUCCESS]
        data={
            "run_count":2,
            "original_source_verified_SAT_count":len(complete),
            "unknown_censored_or_internal_count":2-len(complete),
            "statuses":[r["result"].get("status",r["result"].get("verdict"))
                        for r in records],
            "full_cold_child_wall_seconds_observed":[r["full_cold_child_wall_seconds"]
                                                      for r in records],
        }
        if len(complete)==2:
            data["median_full_cold_wall_seconds"]=statistics.median(
                r["full_cold_child_wall_seconds"] for r in complete)
            data["median_full_cold_CPU_seconds"]=statistics.median(
                r["result"]["complete_cold_child_CPU_seconds"] for r in complete)
            data["max_success_RSS_KiB"]=max(r["result"]["peak_RSS_KiB"] for r in complete)
        else:
            data["full_completed_pair_median"]="UNDEFINED_CENSORED"
        summary[arm]=data
    return payload,summary

def run(a,b,hash22,hash24,out):
    if sha(ORIGINAL.read_bytes())!=CNF_SHA:
        raise AssertionError("Original permanently archived competition source changed")
    z22,data22=original("ubuntu22",a,hash22)
    z24,data24=original("ubuntu24",b,hash24)
    out.mkdir(parents=True,exist_ok=True)
    for name,zipfile_,original_json in (("ubuntu22",a,z22),("ubuntu24",b,z24)):
        shutil.copyfile(zipfile_,out/("original-actions-"+name+".zip"))
        (out/("original-"+name+".json")).write_bytes(original_json)
    results={}
    for host,record in (("ubuntu22",data22),("ubuntu24",data24)):
        mixed=record["janus_extracted_xor_cms_native"]
        comparison={}
        for arm in ARMS[1:]:
            ref=record[arm]
            if (mixed.get("median_full_cold_wall_seconds") is not None
                and ref.get("median_full_cold_wall_seconds") is not None):
                comparison[arm]={
                  "status":"FINITE_PAIR_MEDIAN_DEV_SOURCE_ONLY",
                  "same_host_full_wall_median_ratio_baseline_divided_by_mixed":
                      ref["median_full_cold_wall_seconds"]/mixed["median_full_cold_wall_seconds"],
                  "same_host_full_CPU_median_ratio_baseline_divided_by_mixed":
                      ref["median_full_cold_CPU_seconds"]/mixed["median_full_cold_CPU_seconds"]}
            else:
                comparison[arm]={"status":"UNDEFINED_AT_LEAST_ONE_CENSORED",
                                 "finite_speedup_ratio":"NOT_DEFINED"}
        results[host]={"arm_results":record,"dev_only_pair_median_comparisons":comparison}
    outj={
      "schema":"JANUS-TIME-SAT-004E1-DURABLE-DUAL-RUNNER-PRESEEN-SOURCE-COLD-PROFIT-V1",
      "status":"ORIGINAL_SHA_PINNED_PUBLIC_DEV_TIME_CALIBRATION_NOT_EXTERNAL_WITNESS",
      "original_CI_run":RUN,"original_tested_head":HEAD,
      "original_original_source_CNF_SHA256":CNF_SHA,
      "original_CI_zip_sha256":{"ubuntu22":hash22,"ubuntu24":hash24},
      "same_host_results":results,
      "source_population":"N_1_PREVIOUSLY_SEEN_PUBLIC_BINARY_TREE_SAT",
      "repetitions_per_arm_per_host":2,
      "individual_child_soft_CPU_seconds":30,
      "unknown_CPU_censored_not_UNSAT":True,
      "scientific_limit":"Even finite within-source median ratios cannot establish statistical reproducibility or broad generalizable performance. No external independent holdout.",
      "004C_independent_external_Witness":"OPEN",
      "004F_production":"NOT_READY",
      "original_C023_main":"UNCHANGED",
      "source_files_sha256":{p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}
    }
    (out/"summary.json").write_text(json.dumps(outj,sort_keys=True,indent=2)+"\n")
    print("004E1_ARCHIVE_ORIGINAL_PASS",json.dumps({
      "hosts":2,"source_sha":CNF_SHA,
      "sats_per_host":{h:{a:v["original_source_verified_SAT_count"]
                    for a,v in d["arm_results"].items()} for h,d in results.items()}},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",type=Path,required=True)
    p.add_argument("--zip24",type=Path,required=True)
    p.add_argument("--sha22",required=True)
    p.add_argument("--sha24",required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    run(args.zip22,args.zip24,args.sha22,args.sha24,args.out)
