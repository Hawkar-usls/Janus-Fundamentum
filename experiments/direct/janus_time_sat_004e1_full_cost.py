#!/usr/bin/env python3
"""JANUS TIME-SAT-004E1 · single public preseen mixed SAT instance full-cost calibration.

Precisely one original SAT Competition 2026 binary-tree-parity CNF.
Four fixed arms, two seeded orders, identical 30s CPU / 36s wall / 2 GiB
process limits on TWO independent Ubuntu runner versions. All costs include
cold child startup, original source hash/parse, optional exact source mask
XOR extraction, native solving, and original full CNF SAT-model replay.

This is developmental evidence only; NO blind or general speedup claim.
A SIGXCPU is UNKNOWN, not UNSAT, and cannot support finite speed ratio.
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

from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor
from janus_time_sat_004d4b_real_pilot import original_model_replay

FROZEN=Path("experiments/time_sat_004_external/PREREGISTERED_004E1_FULL_COST_BINARY_TREE_20261102.json")
FROZEN_BLOB="42d4dc9b4e596209d6f0806ee47abfae3e0d8512"
ARCHIVE=Path("experiments/time_sat_004_external/time_sat_004d4b_evidence")
SOURCE=ARCHIVE/"7db30d12cb06f0dc2f30abff80d96d6a.original.cnf"
MODEL=ARCHIVE/"binary-tree-parity-SAT-original-model.json"
SHA="8d94924bef8978b28a2bf95472556b280bef5d98b6833c6db33554098f52d2d8"
N=1023
M=4088
LITERALS=12099
XOR=857
RESIDUAL=660
EXTRACTED_CLAUSES=3428
ARMS=("janus_extracted_xor_cms_native",
      "cryptominisat_original_cnf",
      "cadical195_original_cnf",
      "glucose4_original_cnf")
CPU=30
WALL=36
MEM=2_147_483_648
REPEATS=2
SEED=20261102047

def digest_file(path):
    h=sha256()
    with path.open("rb") as fd:
        for chunk in iter(lambda:fd.read(65536),b""):h.update(chunk)
    return h.hexdigest()

def check_frozen():
    actual=subprocess.run(["git","hash-object",str(FROZEN)],
        capture_output=True,text=True,check=True).stdout.strip()
    if actual!=FROZEN_BLOB:
        raise AssertionError("Frozen original source/solver protocol Git blob changed")
    p=json.loads(FROZEN.read_text())
    expected=p["locked_arms"]
    if expected!=list(ARMS) or p["comparability"]["repeats_per_arm_per_host"]!=REPEATS:
        raise AssertionError("Registered arms/repeats changed")
    if (p["comparability"]["CPU_seconds_soft"]!=CPU
        or p["comparability"]["wall_seconds"]!=WALL):
        raise AssertionError("Registered budget changed")
    return p

def read_original():
    if digest_file(SOURCE)!=SHA:raise AssertionError("Original CNF SHA changed")
    dims=scan_dimacs(SOURCE)
    if (dims["n_variables"]!=N or dims["n_clauses"]!=M
        or dims["n_literal_occurrences"]!=LITERALS):
        raise AssertionError("Original strict DIMACS dimensions changed")
    rows=read_cnf(SOURCE,N,M,max_literals=120000)
    known=json.loads(MODEL.read_text())
    if (known["original_CNF_SHA256"]!=SHA
        or len(known["signed_model"])!=N
        or not original_model_replay(rows,N,known["signed_model"])):
        raise AssertionError("Earlier independently archived SAT model not valid on ORIGINAL CNF")
    return rows

def perform(arm):
    if arm not in ARMS:raise AssertionError("Unknown pre-registered engine")
    # RLIMIT_CPU counts the cold child as well, not just solver internals.
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    start=perf_counter()
    rows=read_original()
    started=perf_counter()
    eqs=0
    residual=M
    consumed=0
    p=None
    if arm=="janus_extracted_xor_cms_native":
        p=extract_mixed_xor(rows,N)
        if p["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("Original parity partition no longer verified")
        eqs=len(p["equations"])
        consumed=p["source_xor_clauses"]
        residual=len(p["residual_clauses"])
        if (eqs,residual,consumed)!=(XOR,RESIDUAL,EXTRACTED_CLAUSES):
            raise AssertionError("Original frozen source parity cover unexpectedly changed")
    extract_seconds=perf_counter()-started
    setup_start=perf_counter()
    stats=None
    if arm in ARMS[:2]:
        import pycryptosat
        solver=pycryptosat.Solver(threads=1)
        if p is None:
            for clause in rows:solver.add_clause(clause)
        else:
            for eq in p["equations"]:
                solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
            for clause in p["residual_clauses"]:solver.add_clause(clause)
        setup_seconds=perf_counter()-setup_start
        solve_start=perf_counter()
        sat,answer=solver.solve()
        solve_seconds=perf_counter()-solve_start
        if sat is True:
            if answer is None or len(answer)<=N:
                raise AssertionError("Native CMS returned incomplete SAT assignment")
            model=[i if bool(answer[i]) else -i for i in range(1,N+1)]
        elif sat is False:
            raise AssertionError("Native CMS returned UNSAT for SHA-bound VERIFIED SAT source")
        else:
            return {"status":"UNKNOWN_NATIVE_SOLVER_NO_ANSWER","arm":arm,
                    "original_sha256":SHA,"cold_child_CPU_seconds":process_time()}
    else:
        from pysat.solvers import Solver
        name="cadical195" if arm=="cadical195_original_cnf" else "glucose4"
        with Solver(name=name,bootstrap_with=rows) as solver:
            setup_seconds=perf_counter()-setup_start
            solve_start=perf_counter()
            sat=solver.solve()
            solve_seconds=perf_counter()-solve_start
            answer=solver.get_model() if sat else None
            stats=solver.accum_stats()
        if sat is True:
            model=answer
        elif sat is False:
            raise AssertionError("Raw CDCL returned UNSAT for SHA-bound VERIFIED SAT source")
        else:
            return {"status":"UNKNOWN_CDCL_NO_ANSWER","arm":arm,
                    "original_sha256":SHA,"cold_child_CPU_seconds":process_time()}
    if model is None or not original_model_replay(rows,N,model):
        raise AssertionError("SAT solver model FAILS every original CNF clause")
    return {
        "status":"SAT_ORIGINAL_CNF_MODEL_VERIFIED",
        "arm":arm,"source_original_sha256":SHA,
        "verified_original_source_variables":N,
        "verified_original_source_clauses":M,
        "source_XOR_equations_native":eqs,
        "source_clauses_converted_to_XOR":consumed,
        "original_residual_source_clauses":residual,
        "source_hash_CNF_model_replay":"PASS",
        "inner_seconds_including_original_CNF_and_model_replay":perf_counter()-start,
        "source_XOR_extract_seconds":extract_seconds,
        "native_input_build_seconds":setup_seconds,
        "native_solver_seconds":solve_seconds,
        "complete_cold_child_CPU_seconds":process_time(),
        "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "solver_stats":stats,
        "no_UNSAT_claim":True,
        "outside_admin_witness":"NOT_ATTEMPTED",
        "production_C023":"UNCHANGED"
    }

def benchmark(output):
    check_frozen()
    # SHA/model check before any benchmark or changed CPU limits.
    read_original()
    output.mkdir(parents=True,exist_ok=True)
    results=[]
    for rep in range(REPEATS):
        order=list(ARMS)
        random.Random(SEED+rep).shuffle(order)
        for arm in order:
            start=perf_counter()
            cmd=[sys.executable,str(Path(__file__).resolve()),"--worker","--arm",arm]
            try:
                child=subprocess.run(cmd,capture_output=True,text=True,
                                     check=False,timeout=WALL)
                if child.returncode:
                    outcome=classify_nonzero_exit(child.returncode)
                    outcome["return_code"]=child.returncode
                    outcome["stderr_tail"]=child.stderr[-900:]
                else:
                    outcome=json.loads(child.stdout)
            except subprocess.TimeoutExpired:
                outcome={"status":"UNKNOWN_WALL_TIMEOUT","verdict":"UNKNOWN_WALL_TIMEOUT"}
            record={
                "repeat":rep,"arm":arm,"arm_order":order,
                "full_cold_child_wall_seconds":perf_counter()-start,
                "result":outcome
            }
            results.append(record)
            print("004E1_TRIAL",rep,arm,
                  outcome.get("status",outcome.get("verdict","UNKNOWN")),
                  round(record["full_cold_child_wall_seconds"],3),flush=True)
    out={
        "schema":"JANUS-TIME-SAT-004E1-BINARY-TREE-PUBLIC-FULL-COLD-CPU-WALL-2026-11-02-V1",
        "status":"PUBLIC_PRESEEN_DEV_COST_CALIBRATION_NO_HIDDEN_CLAIM",
        "source_sha256":SHA,"source_n":N,"source_m":M,
        "known_full_original_SAT_model_replayed":True,
        "frozen_protocol_git_blob":FROZEN_BLOB,
        "github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "github_head":os.getenv("GITHUB_SHA","LOCAL"),
        "environment":os.getenv("RUNNER_OS","LOCAL"),
        "arms":ARMS,"repeats":REPEATS,
        "CPU_limit_seconds":CPU,"wall_timeout_seconds":WALL,
        "RLIMIT_AS_bytes":MEM,
        "all_full_cost_includes":"cold Python startup/imports, SHA, DIMACS parse, model check, XOR recognition, setup, solve and original-clause replay",
        "speedup_if_censored":"NOT_DEFINED",
        "explanatory_limit":"ONE ALREADY-SEEN PUBLIC SAT instance, N=2 per arm per host, not blind, no claimed population performance",
        "results":results,
        "original_C023_main":"UNCHANGED","external_independent_Witness":"OPEN"
    }
    (output/"comparison.json").write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    # A CPU timeout from an ordinary solver is a valid measured UNKNOWN.
    if (len(results)!=REPEATS*len(ARMS)
        or any(x["result"].get("status","").startswith("ABSTAIN")
            or x["result"].get("verdict","").startswith("ERROR")
            or x["result"].get("status")=="UNKNOWN_WALL_TIMEOUT" for x in results)):
        raise AssertionError("004E1_MISSING_CASE_OR_UNEXPECTED_RESEARCH_FAILURE")
    print("TIME_SAT_004E1_COMPLETE",json.dumps({
       "comparisons":len(results),
       "SAT_verified":sum(x["result"].get("status")=="SAT_ORIGINAL_CNF_MODEL_VERIFIED" for x in results),
       "CPU_or_other_unknown":sum(x["result"].get("status")!="SAT_ORIGINAL_CNF_MODEL_VERIFIED" for x in results)},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--worker",action="store_true")
    ap.add_argument("--arm",choices=ARMS)
    ap.add_argument("--out",type=Path)
    opts=ap.parse_args()
    if opts.worker:
        if opts.arm is None:raise SystemExit("Missing --arm")
        check_frozen()
        print(json.dumps(perform(opts.arm),sort_keys=True),flush=True)
    else:
        if opts.out is None:raise SystemExit("Missing --out")
        benchmark(opts.out)
