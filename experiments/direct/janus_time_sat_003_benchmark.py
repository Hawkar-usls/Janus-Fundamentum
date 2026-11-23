#!/usr/bin/env python3
"""TIME-SAT-003 research A/B/C: controlled comparisons, receipts, NO blind claim.

Reuses complete 60+5 public corpus unchanged. Additional synthetic challenges
have new fixed generation seed recorded ahead of benchmark. The generator is
public: NOT a blind exam. Proof traces from Glucose4 are independently RUP
checked from unchanged original CNF (same GitHub trust administrative domain).
Per-arm process isolated peak RSS is measured only on the *new* controls.
"""
from __future__ import annotations
from collections import defaultdict
from hashlib import sha256
import argparse
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
from time import perf_counter

from janus_time_sat_003 import ARMS,run_arm
from janus_time_sat_003_drup_witness import produce_and_check
from janus_time_sat_partial_001 import canonical_sat_cnf,source_hash
from janus_time_sat_partial_002_benchmark import fixed_controls
from janus_tachyon_001_fair_holdout import exact_truth,source_sha,fixed_suite

SOLVERS=("cadical195","glucose4")
SEED=20261101003
REPS_OLD=2
REPS_NEW=3

def new_controls():
    rng=random.Random(SEED)
    result=[]
    for n,units,unsat in ((64,8,False),(128,12,False),(220,16,False),
                          (240,20,False),(128,0,True),(220,0,True),(240,0,True)):
        # Source formula is intentionally public, the planted answer is
        # NEVER handed to the algorithm or run_arm.
        witness=rng.getrandbits(n)
        rows=[]
        for _ in range(2*n):
            v=rng.sample(range(1,n+1),3)
            row=[x if rng.randrange(2) else -x for x in v]
            if not any(bool(witness>>(abs(l)-1)&1)==(l>0) for l in row):
                index=rng.randrange(3)
                row[index]=-row[index]
            rows.append(tuple(row))
        for i in range(1,units+1):
            l=i if witness>>(i-1)&1 else -i
            pivot=n-i
            if pivot==i:pivot=n-i-1
            rows.extend(((l,pivot),(l,-pivot)))
        if unsat:
            for mask in range(16):
                rows.append(tuple((-v if mask>>(v-1)&1 else v) for v in range(1,5)))
        name=f"NEW_{'UNSAT_CORE' if unsat else 'PLANTED_WEDGES'}_{n}"
        result.append((name,tuple(rows),n,"SAT","new_public_not_blind"))
    return result

def median(values):
    return statistics.median(values)

def measure_one(case):
    name,rows,n,kind,family=case
    cnf=canonical_sat_cnf(rows,n,kind)
    repetitions=REPS_NEW if family=="new_public_not_blind" else REPS_OLD
    results={}
    for engine in SOLVERS:
        trials=defaultdict(list)
        for repeat in range(repetitions):
            order=ARMS if repeat%2==0 else tuple(reversed(ARMS))
            for arm in order:
                trial=run_arm(rows,n,kind,solver_name=engine,arm=arm)
                trials[arm].append(trial)
        outcomes={x["status"] for values in trials.values() for x in values}
        if len(outcomes)!=1:
            raise AssertionError("four-arm strong CDCL inconsistency: "+name)
        raw=median(x["full_wall_seconds"] for x in trials["raw"])
        results[engine]={}
        for arm in ARMS:
            items=trials[arm]
            t=median(x["full_wall_seconds"] for x in items)
            if len({tuple(x["derived_units"]) for x in items})!=1:
                raise AssertionError("nondeterministic implications "+name)
            results[engine][arm]={
                "answer":items[0]["status"],
                "median_full_seconds":t,
                "full_samples_seconds":[x["full_wall_seconds"] for x in items],
                "ratio_vs_raw":t/raw,
                "units":items[0]["derived_units"],
                "witness_count":items[0]["wedge_count"],
                "independent_entailment_audits":items[0]["audit_count"],
                "estimated_profit":items[0]["forecast"],
                "cdcl_stats":items[0]["cdcl_stats"],
                "skip_reason":items[0]["admission_reason"],
            }
    return {"id":name,"group":family,"n":n,"kind":kind,
            "cnf_source_sha256":source_hash(cnf,n),
            "encoded_clause_count":len(cnf),
            "answer":results["cadical195"]["raw"]["answer"],
            "solvers":results}

def measured_rss(case,engine,arm):
    name,rows,n,kind,family=case
    command=[sys.executable,str(Path(__file__).parent/"janus_time_sat_003_worker.py")]
    request={"rows":rows,"n":n,"kind":kind,"solver":engine,"arm":arm}
    started=perf_counter()
    process=subprocess.run(command,input=json.dumps(request),text=True,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                           timeout=30,check=False)
    process_wall=perf_counter()-started
    if process.returncode:
        raise RuntimeError(f"isolated worker failed {name} {engine} {arm}: {process.stderr[-1200:]}")
    data=json.loads(process.stdout)
    return {
        "per_process_native_peak_rss_kib":data["process_isolated_peak_rss_kib"],
        "child_processing_seconds":data["full_wall_seconds"],
        "child_process_including_startup_seconds":process_wall,
        "status":data["status"],
        "unit_count":len(data["derived_units"]),
    }

def run():
    frozen,oldlarge,mechanism=fixed_controls()
    new=new_controls()
    all_cases=frozen+oldlarge+mechanism+new
    rows=[]
    for case in all_cases:
        observed=measure_one(case)
        if case[2]<=10:
            expected="SAT" if exact_truth(case[1],case[2],case[3]) else "UNSAT"
            if observed["answer"]!=expected:
                raise AssertionError("independent exhaustive truth mismatch "+case[0])
        if "UNSAT_CORE" in case[0] and observed["answer"]!="UNSAT":
            raise AssertionError("known blocking-core contradiction lost")
        rows.append(observed)
    new_results=[]
    for case in new:
        r=next(x for x in rows if x["id"]==case[0])
        cnf=canonical_sat_cnf(case[1],case[2],case[3])
        proof=produce_and_check(cnf,timeout_seconds=12)
        if "UNSAT_CORE" in case[0] and proof.get("proof_status")!="INDEPENDENT_RUP_REPLAY_PASS":
            raise AssertionError("fresh core UNSAT has no verified independent DRUP proof "+case[0]+": "+str(proof))
        if "PLANTED" in case[0] and proof.get("solver_status")!="SAT":
            raise AssertionError("planted SAT challenge inconsistent "+case[0])
        isolated={engine:{arm:measured_rss(case,engine,arm) for arm in ARMS}
                  for engine in SOLVERS}
        new_results.append({
            "id":case[0],
            "source_sha256":r["cnf_source_sha256"],
            "unit_proof":proof,
            "original_cnf_for_independent_replay":([list(row) for row in cnf]
                if proof.get("solver_status")=="UNSAT" else None),
            "isolated_peak_rss":isolated,
        })
    summary={}
    for group in sorted({x["group"] for x in rows}):
        selected=[x for x in rows if x["group"]==group]
        summary[group]={}
        for engine in SOLVERS:
            summary[group][engine]={
                arm:{
                  "median_ratio_of_individual_case_medians":median(
                      c["solvers"][engine][arm]["ratio_vs_raw"] for c in selected),
                  "faster_cases":sum(c["solvers"][engine][arm]["ratio_vs_raw"]<1 for c in selected),
                  "slower_cases":sum(c["solvers"][engine][arm]["ratio_vs_raw"]>1 for c in selected),
                  "total_cases":len(selected),
                  "cases_with_implied_units":sum(bool(c["solvers"][engine][arm]["units"]) for c in selected),
                } for arm in ARMS[1:]
            }
    return {
        "schema":"JANUS-TIME-SAT-003-ABC-RESEARCH-RESULTS-v1",
        "status":"RESEARCH_UNPROMOTED_PUBLIC_DATA",
        "provenance":{
          "github_sha":os.getenv("GITHUB_SHA","local"),
          "github_run_id":os.getenv("GITHUB_RUN_ID","local"),
          "platform":platform.platform(),
          "previous_frozen_60_sha256":source_sha(fixed_suite()),
          "new_generator_seed":SEED,
          "new_manifest_sha256":sha256(json.dumps(
              [(x["id"],x["cnf_source_sha256"]) for x in rows if x["group"]=="new_public_not_blind"],
              sort_keys=True,separators=(",",":")).encode()).hexdigest(),
        },
        "experimental_arms":ARMS,
        "frozen_profit_coefficients":{"min_n":64,"min_rows":128,
                                     "saving_per_occurrence":16,"scan_per_lit":2,
                                     "audit_per_unit_row":4,"insert_per_unit":8},
        "baseline":"cold raw CaDiCaL195 / Glucose4 on identical source CNF",
        "proof_policy":"Glucose4 DRUP on original CNF; separate no-solver RUP replay; rejects tampering and missing empty clause",
        "proof_trust_limit":"Independent algorithm in the SAME GitHub repository and administration domain, NOT independently administered Witness",
        "rss_policy":"new challenge cases only, each arm in separate fresh Python process; includes interpreter and dependent libraries",
        "external_blind_challenge":"NOT_OBTAINED",
        "aggregates":summary,"new_controls":new_results,"cases":rows,
        "promotion_gate":{"correctness":"CHECK_TESTS_AND_CI",
                          "net_CDCL_speedup":"MEASURE_NOT_ASSUME",
                          "new_drup_proof":"CHECK_NEW_UNSAT_CORE",
                          "external_hidden_challenges":"NOT_DONE",
                          "independently_owned_witness":"NOT_DONE",
                          "C023_main":"UNCHANGED","P_vs_NP":"OPEN"},
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"schema":result["schema"],"status":result["status"],
          "provenance":result["provenance"],"aggregates":result["aggregates"],
          "new_controls":[{"id":x["id"],"proof":x["unit_proof"]}
                          for x in result["new_controls"]],
          "promotion_gate":result["promotion_gate"]},sort_keys=True))
