#!/usr/bin/env python3
"""TIME-SAT-004D0 limited public-origin pilot, NOT full 004D acceptance.

Two sources frozen from 004B BEFORE any 004D evaluation:
first SAT-metadata CPU-timed-out and first UNSAT-metadata CPU-timed-out
in the original registered order. Exactly lights-out and Green–Tao.
Two strong CDCL engines, same CPU, AS and wall caps, isolated per variant.
Four arms: raw, feature_only, janus_direct, frozen Janus forecast.
Every original transfer/decoded SHA256 bound to twice-checked first 004B
receipts. One ordered run per arm; no speed claim, no statistical inference.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from time import perf_counter

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import classify_nonzero_exit
from janus_time_sat_004d_adapter import ARMS,CPU,RAM

FROZEN_SHA={
"01d6fa8efd18ebfecd06af408958477b":{
"original":"59704ea1179fc5eab68989230b53158a67fffb955a6780b2f93c0aea341a356b",
"decoded":"6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361",
"family":"lights-out","label":"sat","n":625,"m":9216},
"08cf53ca00dce11f5bfc02121c9bcd33":{
"original":"2f1cf3ad7791e2d98a352d2eae5ff7c785a87cae5ba57d9a1327163e7a4a2925",
"decoded":"622732d1d213e930a7711270aefa079c9329cb9a446b4f24d848fea2cab6b5a7",
"family":"greentao","label":"unsat","n":527,"m":12692}
}
EXPECTED_PREREG_GIT_BLOB="dc658d57453813bb306aa20f45b3385571f1fe3d"
EXTERNAL_STATUS="PUBLIC_EXPLORATORY_UNBLINDED"
ENGINE=("cadical195","glucose4")
RNG_SEED=2026110104
WALL=9


def run_pilot(out):
    prereg=Path("experiments/time_sat_004_external/PREREGISTERED_SATCOMP2026_PILOT_20261101.json")
    j=json.loads(prereg.read_text())
    check=subprocess.run(["git","hash-object",str(prereg)],
                         capture_output=True,text=True,check=True).stdout.strip()
    if check!=EXPECTED_PREREG_GIT_BLOB:
        raise AssertionError("PREREGISTRATION_BLOB_CHANGED")
    original=j["candidates"]
    cohort=[c for c in original if c["hash"] in FROZEN_SHA]
    if [x["hash"] for x in cohort]!=list(FROZEN_SHA):
        raise AssertionError("FIRST_SAT_AND_UNSAT_COHORT_CHANGED")
    out.mkdir(parents=True,exist_ok=True)
    download=out/"downloads"
    download.mkdir(exist_ok=True)
    trials=[]
    rng=random.Random(RNG_SEED)
    for c in cohort:
        source=FROZEN_SHA[c["hash"]]
        if c["family"]!=source["family"] or c["result"]!=source["label"]:
            raise AssertionError("FROZEN_LABEL_OR_FAMILY_CHANGED")
        raw,raw_meta=retrieve(c,download)
        if raw_meta["source_sha256"]!=source["original"]:
            raise AssertionError("UNEXPECTED_EXTERNAL_ORIGINAL_BYTE_SHA")
        decoded=download/(c["hash"]+".cnf")
        decoded_meta=unpack_bounded(raw,decoded)
        if decoded_meta["uncompressed_sha256"]!=source["decoded"]:
            raise AssertionError("UNEXPECTED_DECODED_BYTE_SHA")
        dim=scan_dimacs(decoded)
        if (dim["n_variables"],dim["n_clauses"])!=(source["n"],source["m"]):
            raise AssertionError("BAD_EXTERNAL_DIMENSIONS")
        if not dim["suitable_for_bounded_solver"]:
            raise AssertionError("PRE_REGISTERED_SOURCE_NOW_EXCEEDS_SAFETY_CAP")
        case={"id":c["hash"],"family":c["family"],"catalog_label_UNVERIFIED":c["result"],
              "original_sha256":raw_meta["source_sha256"],
              "decoded_sha256":decoded_meta["uncompressed_sha256"],
              "dimensions":dim,"engines":{}}
        for engine in ENGINE:
            arms=list(ARMS)
            rng.shuffle(arms)
            observations={}
            for arm in arms:
                command=[sys.executable,str(Path(__file__).resolve().parent/"janus_time_sat_004d_adapter.py"),
                         "--source",str(decoded),"--n",str(dim["n_variables"]),
                         "--m",str(dim["n_clauses"]),"--engine",engine,"--arm",arm]
                start=perf_counter()
                try:
                    process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                           text=True,timeout=WALL,check=False)
                    if process.returncode:
                        observation=classify_nonzero_exit(process.returncode)
                        observation["return_code"]=process.returncode
                        observation["stderr_tail"]=process.stderr[-600:]
                    else:
                        observation=json.loads(process.stdout)
                except subprocess.TimeoutExpired:
                    observation={"verdict":"UNKNOWN_WALL_TIMEOUT"}
                observation["end_to_end_process_wall_seconds"]=perf_counter()-start
                observations[arm]=observation
                print("004D0",case["family"],engine,arm,
                      observation["verdict"],round(observation["end_to_end_process_wall_seconds"],4),
                      flush=True)
            valid={x["verdict"] for x in observations.values()
                   if x["verdict"].startswith("SAT_ORIGINAL_") or
                      x["verdict"].startswith("UNSAT_SOLVER_ONLY_")}
            if len(valid)>1:
                raise AssertionError("INCORRECT_SAT_UNSAT_DISAGREEMENT")
            case["engines"][engine]={"randomized_order":arms,"arms":observations}
        trials.append(case)
    result={
      "schema":"JANUS-TIME-SAT-004D0-BOUNDED-LARGE-CNF-SMOKE-V1",
      "status":EXTERNAL_STATUS,
      "scope":"TWO_FROZEN_REAL_COMPETITION_PUBLIC_CASES_NOT_COMPLETE_004D",
      "precommitted_selection":"first SAT-metadata and first UNSAT-metadata 004B CPU-limited instances in frozen registration order",
      "cohort":list(FROZEN_SHA.keys()),"seed":RNG_SEED,
      "engines":ENGINE,"arms":ARMS,"repeats":1,
      "time_limit_child_CPU_seconds":CPU,
      "time_limit_child_wall_seconds":WALL,
      "child_RLIMIT_AS_bytes":RAM,
      "cloud_HEAD_sha":os.getenv("GITHUB_SHA","local"),
      "cloud_run":os.getenv("GITHUB_RUN_ID","local"),
      "full_cost_accounting":"child startup + original file parsing + feature scan/proof + CDCL + SAT replay",
      "inference":"JANUS direct original-clause 2-CNF resolution only, not a full separate time-reversed SAT solver",
      "source_SHA256:first_captured_and_second_validated":True,
      "UNSAT_certificates":"NOT_GENERATED_ON_004D0",
      "native_simplification_separate_control":"NOT_YET_MEASURED",
      "paired_confidence_intervals":"NOT_POSSIBLE_ONE_REPETITION",
      "actual_hard_benchmark_gate":"NOT_YET_PASSED",
      "external_admin_Witness":"NOT_PRESENT",
      "C023":"UNCHANGED","P_equals_NP":"OPEN",
      "results":trials
    }
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("004D0_SUMMARY",json.dumps({
        "cases":len(trials),
        "each_case":{x["family"]:{e:{arm:obs["verdict"] for arm,obs in eng["arms"].items()}
                     for e,eng in x["engines"].items()} for x in trials},
        "no_production":True},sort_keys=True),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    run_pilot(args.out)
