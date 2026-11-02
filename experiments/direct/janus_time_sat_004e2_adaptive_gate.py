#!/usr/bin/env python3
"""TIME-SAT-004E2 · four PRESEEN public family, cost-aware XOR-gate calibration.

A fixed structural threshold (80% equivalent original clauses, >=1 complete
XOR) chooses native XOR CryptoMiniSat, else original-CNF CryptoMiniSat.
All actions include the extraction cost. No-op scan+raw controls the gate
cost; raw CMS/CaDiCaL195/Glucose4 are also run from cold original source.

These are REUSED PUBLIC sources with training leakage, so NO holdout claims,
no learned unseen-family accuracy, no claims of general SAT speedup.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from time import perf_counter,process_time

from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor
from janus_time_sat_004d4b_real_pilot import original_model_replay

ROOT=Path("experiments/time_sat_004_external")
FROZEN=ROOT/"PREREGISTERED_004E2_PRESEEN_MULTIFAMILY_ADAPTIVE_20261102.json"
FROZEN_BLOB="09563db338939cb19b0bb6aab7ce56dce3eda5f2"
ARCHIVE=ROOT/"time_sat_004d4b_evidence"
CASES=(
    ("linear-equations","247e42e46495f1c4b8707e497af8c93e",
     "dd2e52c12cafa012316052c6c2ac06ea48ccf1c999a5ae57a25c5f208e1cb9bc",1200,21040,81360),
    ("xor-shifting","1707c4c24e66b2cfe6c03955b638bebf",
     "03bae774557f351990c0348c7b11933d8760f4d7a8cf60455f1d4754fe9739c0",2273,8366,23774),
    ("minimum-disagreement-parity","16ca57f2cdffd5b0260fc771017e1f04",
     "6e054967f4c71d900b2bba2508fea2054ac13de78fa0b0b6a94753f66e9e95fc",1250,7190,25729),
    ("binary-tree-parity","7db30d12cb06f0dc2f30abff80d96d6a",
     "8d94924bef8978b28a2bf95472556b280bef5d98b6833c6db33554098f52d2d8",1023,4088,12099),
)
NAMES=tuple(x[0] for x in CASES)
ARMS=("adaptive_cms","noop_scan_cms","cms_original","cadical195_original","glucose4_original")
FRACTION_MIN=0.8
CPU=6
WALL=10
MEM=2_147_483_648
REPEATS=2
SEED=20261102082

def digest_file(path):
    h=sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):h.update(chunk)
    return h.hexdigest()

def check_frozen():
    digest=subprocess.run(["git","hash-object",str(FROZEN)],capture_output=True,
                          text=True,check=True).stdout.strip()
    if digest!=FROZEN_BLOB:
        raise AssertionError("004E2 frozen policy altered: REFUSE")
    p=json.loads(FROZEN.read_text())
    expected=[{"family":name,"id":gid,"source_sha256":sha,"n":n,"m":m,"literals":li}
              for name,gid,sha,n,m,li in CASES]
    for a,b in zip(p["cases"],expected):
        if any(a.get(key)!=value for key,value in b.items()):
            raise AssertionError("004E2 original source candidate changed: REFUSE")
    if len(p["cases"])!=len(expected):
        raise AssertionError("Candidate count changed")
    if p["fixed_arms"]!=list(ARMS):
        raise AssertionError("Arm list changed")
    x=p["candidate_policy"];c=p["comparability"]
    if (x["frozen_threshold_clauses_converted_to_XOR_fraction"]!=FRACTION_MIN
        or x["frozen_min_XOR_equations"]!=1
        or x["only_status_allowing_XOR"]!="SOURCE_PARTITION_VERIFIED"
        or c["CPU_soft_seconds_per_child"]!=CPU
        or c["wall_timeout_seconds_per_child"]!=WALL
        or c["repeats_each_arm_case_host"]!=REPEATS
        or c["shuffled_arm_order_seed"]!=SEED
        or c["virtual_mem_RLIMIT_AS_bytes"]!=MEM):
        raise AssertionError("004E2 frozen threshold/caps changed")
    return p

def original(case_name):
    if case_name not in NAMES:raise AssertionError("Unknown case")
    name,gid,sha,n,m,lits=CASES[NAMES.index(case_name)]
    path=ARCHIVE/(gid+".original.cnf")
    if digest_file(path)!=sha:raise AssertionError("Exact source SHA256 mismatch: "+name)
    dims=scan_dimacs(path)
    if (dims["n_variables"],dims["n_clauses"],
        dims["n_literal_occurrences"])!=(n,m,lits):
        raise AssertionError("Exact source DIMACS shape mismatch: "+name)
    rows=read_cnf(path,n,m,max_literals=120000)
    if name=="binary-tree-parity":
        cert=json.loads((ARCHIVE/"binary-tree-parity-SAT-original-model.json").read_text())
        if (cert["original_CNF_SHA256"]!=sha or
            not original_model_replay(rows,n,cert["signed_model"])):
            raise AssertionError("Earlier SHA-bound full original SAT model failed")
    return rows,n,sha

def gate_decision(extraction,m):
    """Pure fail-closed decision, never estimates runtime based on this case."""
    status=extraction.get("status","MISSING")
    if status.startswith("ABSTAIN_"):
        return {"choose":"raw_CMS","reason":status,"converted_clause_fraction":0.0,
                "extracted_equations":0}
    if status!="SOURCE_PARTITION_VERIFIED":
        raise AssertionError("Unknown or broken source extraction: DO NOT SOLVE")
    count=extraction["complete_xor_equation_count"]
    used=extraction["source_xor_clauses"]
    residual=extraction["source_residual_clauses"]
    if (type(count)!=int or type(used)!=int or type(residual)!=int
        or count<0 or used<0 or used>m or used+residual!=m
        or len(extraction["equations"])!=count
        or len(extraction["residual_clauses"])!=residual
        or len(extraction["xor_source_clause_indices"])!=used
        or len(extraction["residual_source_clause_indices"])!=residual):
        raise AssertionError("Invalid complete source partition or clause counts")
    indices=extraction["xor_source_clause_indices"]+extraction["residual_source_clause_indices"]
    if len(indices)!=m or len(set(indices))!=m or set(indices)!=set(range(m)):
        raise AssertionError("Source clause allocation not exact-cover")
    fraction=used/m if m else 0.0
    use=count>=1 and fraction>=FRACTION_MIN
    return {"choose":"native_xor_CMS" if use else "raw_CMS",
            "reason":"EXACT_SOURCE_XOR_FRACTION_GATE" if use else "BELOW_FROZEN_XOR_COVERAGE_GATE",
            "converted_clause_fraction":fraction,
            "extracted_equations":count}

def run_one(case_name,arm):
    if arm not in ARMS:raise AssertionError("Not a frozen original competitor")
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    began=perf_counter()
    rows,n,sha=original(case_name)
    decision={"choose":"raw_CMS","reason":"NO_SCAN_RAW_BASELINE",
              "converted_clause_fraction":0.0,"extracted_equations":0}
    extraction_seconds=0.0
    partition=None
    if arm in ("adaptive_cms","noop_scan_cms"):
        before=perf_counter()
        partition=extract_mixed_xor(rows,n)
        decision=gate_decision(partition,len(rows))
        extraction_seconds=perf_counter()-before
        if arm=="noop_scan_cms":
            decision={**decision,"choose":"raw_CMS",
                      "reason":"NOOP_SCAN_ALWAYS_RAW_VERIFIED_CONTROL"}
    effective="raw_CMS" if arm in ("cms_original","noop_scan_cms") else (
        decision["choose"] if arm=="adaptive_cms" else arm)
    setup_start=perf_counter()
    if effective in ("raw_CMS","native_xor_CMS"):
        import pycryptosat
        s=pycryptosat.Solver(threads=1)
        if effective=="native_xor_CMS":
            if partition is None or partition["status"]!="SOURCE_PARTITION_VERIFIED":
                raise AssertionError("XOR solver may only receive verified source partition")
            for eq in partition["equations"]:
                s.add_xor_clause(eq["variables"],bool(eq["rhs"]))
            for clause in partition["residual_clauses"]:
                s.add_clause(clause)
        else:
            for clause in rows:s.add_clause(clause)
        setup_seconds=perf_counter()-setup_start
        before=perf_counter()
        sat,answer=s.solve()
        solver_seconds=perf_counter()-before
        if sat is True:
            if answer is None or len(answer)<=n:
                raise AssertionError("Incomplete CMS model")
            signed=[i if bool(answer[i]) else -i for i in range(1,n+1)]
        else:
            signed=None
    else:
        from pysat.solvers import Solver
        with Solver(name="cadical195" if effective=="cadical195_original" else "glucose4",
                    bootstrap_with=rows) as solver:
            setup_seconds=perf_counter()-setup_start
            before=perf_counter()
            sat=solver.solve()
            solver_seconds=perf_counter()-before
            signed=solver.get_model() if sat else None
    if sat is True:
        if signed is None or not original_model_replay(rows,n,signed):
            raise AssertionError("Solver output violates ORIGINAL SHA-bound CNF")
        status="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
    elif sat is False:
        if case_name=="binary-tree-parity":
            raise AssertionError("UNSAT conflicts with archived verified original SAT model")
        status="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
    else:
        status="UNKNOWN_NO_ANSWER"
    return {
        "status":status,"family":case_name,"arm":arm,
        "effective_solver":effective,
        "source_sha256":sha,
        "original_clause_count":len(rows),
        "gate":decision,
        "source_scan_and_extraction_wall_seconds":extraction_seconds,
        "solver_setup_seconds":setup_seconds,
        "native_solver_seconds":solver_seconds,
        "cold_inner_end_to_end_wall_seconds":perf_counter()-began,
        "cold_child_total_CPU_seconds":process_time(),
        "max_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "all_SAT_models_checked_on_original_CNF":True,
        "UNSAT_portable_certification":"NOT_PERFORMED",
        "C023_main":"UNCHANGED",
        "external_holdout":"NO_REUSED_PUBLIC_SOURCES"
    }

def run_batch(out):
    policy=check_frozen()
    for family in NAMES:
        original(family)
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    for family in NAMES:
        for rep in range(REPEATS):
            order=list(ARMS)
            random.Random(SEED+NAMES.index(family)*31+rep).shuffle(order)
            for arm in order:
                command=[sys.executable,str(Path(__file__).resolve()),
                         "--worker","--family",family,"--arm",arm]
                started=perf_counter()
                try:
                    result=subprocess.run(command,text=True,capture_output=True,
                                          check=False,timeout=WALL)
                    if result.returncode:
                        outcome=classify_nonzero_exit(result.returncode)
                        outcome["return_code"]=result.returncode
                        outcome["stderr_tail"]=result.stderr[-1000:]
                    else:outcome=json.loads(result.stdout)
                except subprocess.TimeoutExpired:
                    outcome={"status":"UNKNOWN_WALL_TIMEOUT","verdict":"UNKNOWN_WALL_TIMEOUT"}
                record={"family":family,"repeat":rep,"arm":arm,"order":order,
                        "full_cold_wall_seconds":perf_counter()-started,
                        "outcome":outcome}
                records.append(record)
                print("004E2_TRIAL",family,rep,arm,
                      outcome.get("status",outcome.get("verdict","UNKNOWN")),
                      round(record["full_cold_wall_seconds"],3),flush=True)
    expected=len(NAMES)*REPEATS*len(ARMS)
    allowed={"SAT_ORIGINAL_CNF_MODEL_VERIFIED","UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
             "UNKNOWN_NO_ANSWER","UNKNOWN_CPU_LIMIT_SIGXCPU"}
    if len(records)!=expected:
        raise AssertionError("Incomplete frozen cohort")
    for rec in records:
        state=rec["outcome"].get("status",rec["outcome"].get("verdict","MISSING"))
        if state not in allowed:
            raise AssertionError("Unregistered failure or wall timeout: "+str(rec))
    product={
        "schema":"JANUS-TIME-SAT-004E2-PRESEEN-MULTIFAMILY-FULL-COST-SAFE-GATE-2026-11-02-V1",
        "status":"PUBLIC_PRESEEN_DEVELOPMENT_ONLY_NO_BLIND_EVALUATION",
        "frozen_policy_blob":FROZEN_BLOB,
        "host":os.getenv("RUNNER_OS","LOCAL"),
        "github_head":os.getenv("GITHUB_SHA","LOCAL"),
        "github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "cases":[{"family":x[0],"CNF_SHA256":x[2]} for x in CASES],
        "arms":ARMS,"repeats":REPEATS,
        "cpu_limit_seconds":CPU,"wall_limit_seconds":WALL,
        "RLIMIT_AS_bytes":MEM,
        "total_expected_trials_per_host":expected,
        "declared_gate_threshold_fraction":FRACTION_MIN,
        "negative_control":"noop_scan_cms = same XOR scan then raw CMS",
        "strict_skip_control":"cms_original = raw original CNF only",
        "null_results_and_CPU_censored_retained":True,
        "NO_finite_speedup_ratio_if_any_comparator_censored":True,
        "zero_hidden_instances":True,
        "unverified_UNSAT_is_not_a_proof":True,
        "fairness":"Comparisons are individual cold wall/process CPU within same Ubuntu runner; no cross-host ratios. Novelty of all 4 source families is ZERO.",
        "production_C023":"UNCHANGED",
        "external_independent_004C_Witness":"OPEN",
        "external_scientific_004F_gate":"NOT_READY",
        "records":records
    }
    (out/"comparison.json").write_text(json.dumps(product,sort_keys=True,indent=2)+"\n")
    print("004E2_COMPLETE",json.dumps({
        "per_host_trials":expected,
        "verified_SAT":sum(r["outcome"].get("status")=="SAT_ORIGINAL_CNF_MODEL_VERIFIED" for r in records),
        "unknown_CPU_censored":sum(r["outcome"].get("status")=="UNKNOWN_CPU_LIMIT_SIGXCPU" for r in records),
        "no_blind_claim":True},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--worker",action="store_true")
    p.add_argument("--family",choices=NAMES)
    p.add_argument("--arm",choices=ARMS)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.worker:
        if a.family is None or a.arm is None:raise SystemExit("Missing fixed family and arm")
        check_frozen()
        print(json.dumps(run_one(a.family,a.arm),sort_keys=True))
    else:
        if a.out is None:raise SystemExit("Missing --out")
        run_batch(a.out)
