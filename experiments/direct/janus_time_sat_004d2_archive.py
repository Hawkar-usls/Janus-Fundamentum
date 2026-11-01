#!/usr/bin/env python3
"""Evidence preservation for original CI #41330327931, EXACT original bytes.

Archive first; never recompute or substitute original 30-run observations.
No solver calls. Refuse mismatching source, incomplete statuses or changed
digest and compute medians only for FINISHED/SAT methods; CPU-censored arms
are labeled UNKNOWN, not inferred solver finish time or speedup ratio.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import statistics
import zipfile

RUN_ID=41330327931
RUN_HEAD="3f9c415f3579aa34510dd124364d4d9084894eb1"
SOURCE_SHA="6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361"
ORIGINAL={
"ubuntu-22.04":{"id":13093360122,"sha256":"389b84b3dccc24a6b2a9261d645c7652426faf0fa7d9aa6a82b8acf27044d61f"},
"ubuntu-24.04":{"id":13093161095,"sha256":"8c4b9b5f6f5d8ecf4cda97a9018da8f96706caaf31aa369cbd2eb72d597d3898"}}
ARMS=("janus_gf2","cryptominisat_native_xor","cryptominisat_original_cnf","cadical195_original_cnf","glucose4_original_cnf")
SAT_ARMS=ARMS[:3]
TIMEOUT_ARMS=ARMS[3:]

def sha(b):return sha256(b).hexdigest()

def collect(paths,out):
    data={}
    pins={}
    out.mkdir(parents=True,exist_ok=True)
    for host,meta in ORIGINAL.items():
        path=paths[host]
        b=path.read_bytes()
        if sha(b)!=meta["sha256"]:raise AssertionError("SOURCE_ZIP_SHA256_MISMATCH "+host)
        with zipfile.ZipFile(path) as z:
            files=z.namelist()
            if files!=["benchmark.json"]:raise AssertionError("ZIP_FILES_INVALID "+str(files))
            raw=z.read("benchmark.json")
        obj=json.loads(raw)
        if (obj["original_CNF_SHA256"]!=SOURCE_SHA or obj["original_n"]!=625
            or obj["original_m"]!=9216 or obj["repeats"]!=3
            or obj["randomization_seed"]!=20261101042
            or set(obj["arms"])!=set(ARMS)
            or obj["resource_budgets"]["CPU_seconds_per_arm"]!=8
            or obj["resource_budgets"]["virtual_memory_limit_bytes_per_arm"]!=2147483648
            or len(obj["results"])!=15):
            raise AssertionError("UNEXPECTED_BENCHMARK_METHOD "+host)
        per_arm={name:[] for name in ARMS}
        for trial in obj["results"]:
            arm=trial["arm"]
            per_arm[arm].append(trial)
            if arm in SAT_ARMS:
                if trial["result"].get("verdict")!="SAT_ORIGINAL_CNF_INDEPENDENTLY_VERIFIED":
                    raise AssertionError("SAT_ARM_NOT_VERIFIED "+str(trial))
                if trial["result"].get("original_CNF_SHA256")!=SOURCE_SHA:
                    raise AssertionError("SOLVER_SOURCE_NOT_EXACT "+host)
                if trial["result"].get("verification")!="EVERY_ORIGINAL_DIMACS_CLAUSE":
                    raise AssertionError("MISSING_ORIGINAL_MODEL_REPLAY")
            else:
                if trial["result"].get("verdict")!="UNKNOWN_CPU_LIMIT_SIGXCPU":
                    raise AssertionError("BASELINE_NOT_CPU_CENSORED "+str(trial))
            if trial["repeat"] not in (0,1,2):
                raise AssertionError("BAD_REPETITION")
        if any(sorted(t["repeat"] for t in trials)!=[0,1,2] for trials in per_arm.values()):
            raise AssertionError("INCOMPLETE_ARM_REPEATS "+host)
        dest=out/("original-GitHub-Actions-"+host+".zip")
        dest.write_bytes(b)
        (out/("original-"+host+".json")).write_bytes(raw)
        medians={arm:(statistics.median(t["full_end_to_end_child_wall_seconds"] for t in trials)
                      if arm in SAT_ARMS else None) for arm,trials in per_arm.items()}
        paired_ratio=medians["cryptominisat_native_xor"]/medians["janus_gf2"]
        # Ratio of medians is DESCRIPTIVE ONLY, n=3 per machine, not a robust CI.
        pins[host]={
          "original_artifact_id":meta["id"],"original_zip_sha256":meta["sha256"],
          "original_json_sha256":sha(raw),
          "meanings":"all original measured child times and runtime memory stored in unaltered JSON",
          "median_seconds_of_successful_complete_end_to_end_process":medians,
          "median_ratio_native_xor_over_JANUS":paired_ratio,
          "CryptoMiniSat_native_XOR_successes":3,"CryptoMiniSat_original_CNF_successes":3,
          "JANUS_gf2_successes":3,"CaDiCaL_CPU_timeouts":3,"Glucose_CPU_timeouts":3
        }
        data[host]=obj
    receipt={
      "schema":"JANUS-TIME-SAT-004D2-ORIGINAL-CI-EXACT-30-ARM-REPLAY-EVIDENCE-V1",
      "source_run_id":RUN_ID,"source_branch_tested_SHA":RUN_HEAD,
      "source_CNF_sha256":SOURCE_SHA,
      "n_625_m_9216_original_CNF":True,
      "all_original_SHA_rechecked":"PASS",
      "original_results_immutable":True,
      "hosts":pins,
      "total_tested_child_processes":30,
      "original_SAT_model_replays":18,
      "original_generic_CDCL_CPU_timeouts":12,
      "n_repeats_each_host":3,
      "result":"JANUS_SOLVES_SAME_SOURCE_FAST_AS_SPECIALIZED_XOR_WITHIN_NARROW_PUBLIC_CASE",
      "randomized_order":"SEE_ORIGINAL_JSON",
      "confidence_intervals":"NOT_CREDIBLY_ESTIMABLE_WITH_THREE_REPEATS_EACH_HOST",
      "extrapolation":"NONE_ONLY_ONE_PUBLIC_XOR_CASE",
      "external_hidden_holdout":"NOT_TESTED",
      "external_administrative_Witness":"NOT_TESTED",
      "statistical_gain_over_CryptoMiniSat":"NOT_ESTABLISHED",
      "production_C023":"UNCHANGED",
      "P_equals_NP":"OPEN"
    }
    (out/"summary.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("TIME_SAT_004D2_ARCHIVE_PASS",json.dumps({
      "hosts":{host:{k:v for k,v in val["median_seconds_of_successful_complete_end_to_end_process"].items()}
               for host,val in pins.items()},
      "verified_SAT":18,"censored_CDCL":12},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--zip-22",required=True,type=Path)
    p.add_argument("--zip-24",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    collect({"ubuntu-22.04":a.zip_22,"ubuntu-24.04":a.zip_24},a.out)
