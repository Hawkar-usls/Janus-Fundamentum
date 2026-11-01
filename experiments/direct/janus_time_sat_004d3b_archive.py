#!/usr/bin/env python3
"""Archive two EXACT TIME-SAT-004D3B CI artifacts without rewriting evidence.

Verify GitHub original ZIP SHA256, original JSON, frozen two-source hashes,
exactly 5x3x2 total arms per host, original status taxonomy. Derive descriptive
medians only for successfully completed runs. Preserve raw JSON and ZIP.
Other-solver UNSAT remains solver-only, not independently certified.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import statistics
import zipfile

from janus_time_sat_004d3_compare import ARMS,CASES,REPEATS,CPU,WALL,AS_BYTES

RUN=41333053744
HEAD="053882cb7bbc2c0b8e89c1b851c3c7a57ed51109"
GITHUB_ARTIFACTS={
 "ubuntu22":{"id":13093784909,
             "sha256":"da253df87b19b3e4b9f269cdedb9ca8fb33f0be2adfc5fe7b0a1fa0e4a4fa914"},
 "ubuntu24":{"id":13093978933,
             "sha256":"e79f57d294c1a2fb92774cceeb6f1a2b513842789a5b16c4df2e1e2d92caf619"},
}
EXPECTED={
 "lightsout_new_sat":{
  "janus_gf2":"SAT_ORIGINAL_CNF_MODEL_VERIFIED",
  "cryptominisat_native_xor":"UNKNOWN_CPU_LIMIT_SIGXCPU",
  "cryptominisat_original_cnf":"SAT_ORIGINAL_CNF_MODEL_VERIFIED",
  "cadical195_original_cnf":"UNKNOWN_CPU_LIMIT_SIGXCPU",
  "glucose4_original_cnf":"UNKNOWN_CPU_LIMIT_SIGXCPU"
 },
 "lightsout_new_unsat":{
  "janus_gf2":"GF2_UNSAT_SOURCE_COMBINATION_REPLAYED_SAME_ADMIN",
  "cryptominisat_native_xor":"UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
  "cryptominisat_original_cnf":"UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
  "cadical195_original_cnf":"UNKNOWN_CPU_LIMIT_SIGXCPU",
  "glucose4_original_cnf":"UNKNOWN_CPU_LIMIT_SIGXCPU"
 }
}
COMPLETED={
 "SAT_ORIGINAL_CNF_MODEL_VERIFIED",
 "GF2_UNSAT_SOURCE_COMBINATION_REPLAYED_SAME_ADMIN",
 "UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
}

def digest(b):return sha256(b).hexdigest()

def read_original_zip(path,worker):
    raw=path.read_bytes()
    meta=GITHUB_ARTIFACTS[worker]
    if digest(raw)!=meta["sha256"]:
        raise AssertionError("ORIGINAL_GITHUB_ZIP_SHA_CHANGED")
    with zipfile.ZipFile(path) as z:
        if set(z.namelist())!={"comparison.json"}:
            raise AssertionError("UNEXPECTED_GITHUB_ZIP_CONTENTS")
        binary=z.read("comparison.json")
    j=json.loads(binary)
    if (j.get("schema")!="JANUS-TIME-SAT-004D3B-TWO-NEW-PUBLIC-LIGHTSOUT-BUDGETED-FAIR-V1"
        or j.get("repeats_per_host")!=REPEATS
        or j.get("child_limit_CPU_seconds")!=CPU
        or j.get("parent_limit_wall_seconds")!=WALL
        or j.get("child_limit_address_space_bytes")!=AS_BYTES
        or len(j.get("results",[]))!=len(CASES)*len(ARMS)*REPEATS):
        raise AssertionError("ORIGINAL_EXPERIMENT_SHAPE_CHANGED")
    if j["new_cases"]!=CASES or tuple(j["arms"])!=ARMS:
        raise AssertionError("FROZEN_ALGORITHM_OR_SOURCE_MISMATCH")
    by_case={}
    for case,case_meta in CASES.items():
        by_case[case]={}
        for arm in ARMS:
            records=[x for x in j["results"] if x["case"]==case and x["arm"]==arm]
            if len(records)!=REPEATS or sorted(x["repeat"] for x in records)!=list(range(REPEATS)):
                raise AssertionError("MISSING_SAME_ARM_REPEATS")
            statuses={x["result"]["verdict"] for x in records}
            if statuses!={EXPECTED[case][arm]}:
                raise AssertionError("UNEXPECTED_ORIGINAL_ARM_OUTCOME: "+case+" "+arm+" "+repr(statuses))
            for x in records:
                if x["gbd_id"]!=case_meta["gbd_id"]:
                    raise AssertionError("ORIGINAL_GBD_ID_MISMATCH")
                if x["result"]["verdict"] in COMPLETED and x["result"].get("original_SHA256")!=case_meta["sha256"]:
                    raise AssertionError("COMPLETED_CHILD_SOURCE_HASH_NOT_BOUND")
                if x["result"]["verdict"]=="SAT_ORIGINAL_CNF_MODEL_VERIFIED" and not x["result"]["source_SAT_model_checked_every_original_clause"]:
                    raise AssertionError("UNVERIFIED_SAT_MODEL")
            if statuses.issubset(COMPLETED):
                values=[x["full_child_end_to_end_wall_seconds"] for x in records]
                by_case[case][arm]={
                    "success_count":REPEATS,
                    "median_end_to_end_wall_seconds":statistics.median(values),
                    "min_end_to_end_wall_seconds":min(values),
                    "max_end_to_end_wall_seconds":max(values)
                }
            else:
                by_case[case][arm]={"success_count":0,
                                   "CPU_censored_count":REPEATS,
                                   "speed_ratio":"NOT_DEFINED_CENSORED"}
    return binary,by_case

def archive(z22,z24,out):
    original={}
    out.mkdir(parents=True,exist_ok=True)
    for label,path in (("ubuntu22",z22),("ubuntu24",z24)):
        original_bytes,summaries=read_original_zip(path,label)
        shutil.copyfile(path,out/("original-github-"+label+".zip"))
        (out/("original-"+label+".json")).write_bytes(original_bytes)
        original[label]={
            "original_Github_artifact":GITHUB_ARTIFACTS[label],
            "original_inner_JSON_SHA256":digest(original_bytes),
            "cases":summaries
        }
    data={
      "schema":"JANUS-TIME-SAT-004D3B-TWO-NEW-LIGHTSOUT-EXACT-ORIGINAL-CI-EVIDENCE-V1",
      "status":"SOURCE_BOUND_TWO_WORKER_COMPARISON_PASS_CASE_DEPENDENT_RESULTS",
      "original_run_id":RUN,"original_tested_head":HEAD,
      "parent_original_sources":"experiments/time_sat_004_external/time_sat_004d3_evidence/manifest.json",
      "original_two_worker_receipts":original,
      "n_original_comparisons":2*len(CASES)*len(ARMS)*REPEATS,
      "original_models_replayed_in_CI":"SAT_ALL_SUCCESSFUL_SPECIALIZED_AND_CMS_ORIGINAL",
      "original_GF2_UNSAT_replayed_in_CI":"PASS_SAME_ADMIN",
      "unsat_other_solvers":"SOLVER_ONLY_NO_PORTABLE_PROOF",
      "both_standard_CDCL_solver_groups_all_CPU_censored":True,
      "native_XOR_new_SAT_ALL_CPU_censored":True,
      "native_XOR_new_UNSAT_faster_than_JANUS_GF2":True,
      "general_universal_speedup":"NOT_ESTABLISHED_TWO_SAME_FAMILY_PUBLIC_SOURCES",
      "confidence_intervals":"NOT_ESTABLISHED_THREE_SAMPLES_EACH_SOURCE_WORKER",
      "cross_family_transfer":"NOT_DEMONSTRATED_7_004D3_NON_LIGHTSOUT_ABSTAIN",
      "independent_administrative_Witness":"OPEN",
      "production_C023":"UNCHANGED",
    }
    data["file_sha256"]={p.name:digest(p.read_bytes())
                         for p in out.iterdir() if p.is_file()}
    (out/"summary.json").write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("004D3B_DURABLE_ORIGINAL_PASS",json.dumps({
        "original_worker_zips":2,
        "comparison_trials":data["n_original_comparisons"],
        "new_SAT":"JANUS_FAST_CMS_NATIVE_TIMEOUT",
        "new_UNSAT":"NATIVE_CMS_FASTER_THAN_JANUS",
        "source_guarantee":"PREREGISTERED_SHA"},
        sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip22",required=True,type=Path)
    p.add_argument("--zip24",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    archive(a.zip22,a.zip24,a.out)
