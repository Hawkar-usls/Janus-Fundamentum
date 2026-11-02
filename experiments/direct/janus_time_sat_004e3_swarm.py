#!/usr/bin/env python3
"""004E3: 24 independent ephemeral GitHub job challengers, paired within VM.

24 combinations = 4 previously seen public SATCompetition families * 6
mathematically equivalent source-derived XOR policies. Each matrix job runs
two randomized paired repeats (candidate and raw CMS on SAME machine) with
6 CPU seconds, 10 wall, 2GiB per cold child. All original clauses retained
either explicitly or through complete source-equivalent parity blocks.
No self-evolution or production model swaps; no independent holdout claim.
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

from janus_time_sat_004e2_adaptive_gate import (
    original,CASES,NAMES,extract_mixed_xor,original_model_replay,
    digest_file,scan_dimacs,read_cnf
)
from janus_time_sat_004b_baselines import classify_nonzero_exit

FREEZE=Path("experiments/time_sat_004_external/PREREGISTERED_004E3_SWARM_24_20261102.json")
FREEZE_BLOB="2978d87878f8e60b0893efba7256bf03b7fb99b1"
VARIANTS=("raw_cms","scan_noop_cms","native_all",
          "native_width2_only","native_width3plus_only","adaptive_80")
CPU=6
WALL=10
MEM=2147483648
REPS=2
SEED=20261102083
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"

def frozen():
    dig=subprocess.run(["git","hash-object",str(FREEZE)],
                       check=True,text=True,capture_output=True).stdout.strip()
    if dig!=FREEZE_BLOB:
        raise AssertionError("004E3 scientific preregistration tampered")
    j=json.loads(FREEZE.read_text())
    if (j["variants"]!=list(VARIANTS) or j["four_original_public_source_families"]!=list(NAMES)
        or j["plan"]["matrix_jobs"]!=24 or j["plan"]["paired_repetitions"]!=REPS
        or j["plan"]["fresh_child_CPU_soft_s"]!=CPU
        or j["plan"]["fresh_child_WALL_s"]!=WALL):
        raise AssertionError("004E3 frozen suite or resource caps changed")
    return j

def select_verified_xor(original_rows,n,variant):
    """Build verified equivalent mixed representation from original full masks.

    Any extracted equation NOT selected must have its exact source clause
    indices restored to CNF; no source clause can disappear unrepresented.
    """
    if variant not in VARIANTS:raise ValueError("Not preregistered 004E3 policy")
    if variant=="raw_cms":
        return {"choice":"raw_original","equations":[],"cnf_clauses":original_rows,
                "converted_source_clauses":0,"scan_status":"NOT_SCANNED"}
    p=extract_mixed_xor(original_rows,n)
    if p["status"]!="SOURCE_PARTITION_VERIFIED":
        if not p["status"].startswith("ABSTAIN_"):
            raise AssertionError("Unexpected XOR extractor proof status")
        return {"choice":"raw_fallback","equations":[],"cnf_clauses":original_rows,
                "converted_source_clauses":0,"scan_status":p["status"]}
    total=len(original_rows)
    full=p["equations"]
    used=set()
    selected=[]
    scan_noop=variant=="scan_noop_cms"
    for eq in full:
        width=len(eq["variables"])
        keep=(variant=="native_all" or
              (variant=="native_width2_only" and width<=2) or
              (variant=="native_width3plus_only" and width>=3) or
              (variant=="adaptive_80" and p["source_xor_clauses"]/total>=0.8))
        if scan_noop:keep=False
        if keep:
            indices=eq["original_clause_indices"]
            if any(i in used for i in indices):
                raise AssertionError("Overlapping original XOR source allocation")
            used.update(indices)
            selected.append(eq)
    # Unselected source masks and all residual clauses remain original CNF.
    clauses=[original_rows[i] for i in range(total) if i not in used]
    if len(clauses)+len(used)!=total:
        raise AssertionError("Original source clauses were lost")
    if any(i<0 or i>=total for i in used):
        raise AssertionError("Derived XOR references outside original source")
    return {"choice":"native_xor" if selected else "raw_after_scan",
            "equations":selected,"cnf_clauses":clauses,
            "converted_source_clauses":len(used),"scan_status":p["status"],
            "full_XOR_equations_available":len(full),
            "full_original_coverage_fraction":p["source_xor_clauses"]/total}

def child(family,variant):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    rows,n,original_SHA=original(family)
    started_scan=perf_counter()
    form=select_verified_xor(rows,n,variant)
    scan_s=perf_counter()-started_scan
    import pycryptosat
    solver=pycryptosat.Solver(threads=1)
    for eq in form["equations"]:
        solver.add_xor_clause(list(eq["variables"]),bool(eq["rhs"]))
    for row in form["cnf_clauses"]:
        solver.add_clause(list(row))
    solver_s=perf_counter()
    sat,assignment=solver.solve()
    native_s=perf_counter()-solver_s
    if sat is True:
        if assignment is None or len(assignment)<=n:
            raise AssertionError("Solver SAT assignment incomplete")
        values=[i if bool(assignment[i]) else -i for i in range(1,n+1)]
        if not original_model_replay(rows,n,values):
            raise AssertionError("Every-original-source-clause SAT replay FAILED")
        status=SAT
    elif sat is False:
        if family=="binary-tree-parity":
            raise AssertionError("UNSAT conflicts with prior original-source full SAT model")
        status="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {
        "status":status,"family":family,"variant":variant,
        "original_SHA256":original_SHA,
        "source_n":n,"original_clause_count":len(rows),
        "converted_original_clause_count":form["converted_source_clauses"],
        "selected_XOR_equations":len(form["equations"]),
        "residual_original_clauses":len(form["cnf_clauses"]),
        "structural_scan_status":form["scan_status"],
        "effective_representation":form["choice"],
        "scan_wall_seconds":scan_s,"native_solver_wall_seconds":native_s,
        "full_cold_inner_wall_seconds":perf_counter()-started,
        "full_cold_process_CPU_seconds":process_time(),
        "max_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "original_model_verified":status==SAT,
        "C023_main":"UNCHANGED","outside_admin":"NOT_INDEPENDENT"
    }

def paired(family,variant,out):
    frozen()
    if family not in NAMES or variant not in VARIANTS:
        raise AssertionError("Matrix job not in frozen 24 combinations")
    # This pre-check is not counted as a candidate child's cold process time.
    rows,n,sha=original(family)
    records=[]
    for repeat in range(REPS):
        arms=["candidate","raw_baseline"]
        random.Random(SEED+31*NAMES.index(family)+7*VARIANTS.index(variant)+repeat).shuffle(arms)
        for arm in arms:
            actual=variant if arm=="candidate" else "raw_cms"
            before=perf_counter()
            command=[sys.executable,str(Path(__file__).resolve()),
                     "--child","--family",family,"--variant",actual]
            try:
                r=subprocess.run(command,capture_output=True,text=True,
                                 check=False,timeout=WALL)
                if r.returncode!=0:
                    outcome=classify_nonzero_exit(r.returncode)
                    outcome["status"]=outcome["verdict"]
                    outcome["return_code"]=r.returncode
                    outcome["stderr_tail"]=r.stderr[-450:]
                else:outcome=json.loads(r.stdout)
            except subprocess.TimeoutExpired:
                outcome={"status":"UNKNOWN_WALL_TIMEOUT","verdict":"UNKNOWN_WALL_TIMEOUT"}
            full_wall=perf_counter()-before
            record={"repeat":repeat,"role":arm,"actual_variant":actual,
                    "randomized_pair_order":arms,
                    "full_cold_child_wall_seconds":full_wall,"outcome":outcome}
            records.append(record)
            print("004E3",family,variant,repeat,arm,
                  outcome.get("status","MISSING"),round(full_wall,4),flush=True)
    allowed={SAT,"UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
             "UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT",
             "UNKNOWN_SOLVER_NO_ANSWER"}
    if (len(records)!=4 or
        any(x["outcome"].get("status") not in allowed for x in records)):
        raise AssertionError("004E3 failed/invalid child outcome: no silent PASS")
    if any(x["outcome"].get("status")==SAT and
           x["outcome"]["original_SHA256"]!=sha for x in records):
        raise AssertionError("Successful child source not original")
    report={
        "schema":"JANUS-TIME-SAT-004E3-PAIRED-VARIANT-VM-ORIGINAL-CNF-V1",
        "status":"PRESEEN_SOURCE_DEVELOPMENT_SWARM_NOT_EXTERNAL",
        "frozen_git_blob":FREEZE_BLOB,
        "github_run_id":os.environ.get("GITHUB_RUN_ID","LOCAL"),
        "github_head":os.environ.get("GITHUB_SHA","LOCAL"),
        "github_job":os.environ.get("GITHUB_JOB","LOCAL"),
        "runner_name":os.environ.get("RUNNER_NAME","LOCAL"),
        "github_runner_os":os.environ.get("RUNNER_OS","LOCAL"),
        "github_runner_arch":os.environ.get("RUNNER_ARCH","LOCAL"),
        "family":family,"variant":variant,"original_CNF_SHA256":sha,
        "paired_repetitions":REPS,"child_CPU_s":CPU,"wall_s":WALL,"address_space_bytes":MEM,
        "expected_child_trials":4,"original_bytes_replayed":True,
        "no_independent_holdout":True,"new_algorithmic_speedup_unproven":True,
        "no_production_promotion":True,"records":records
    }
    out.mkdir(parents=True,exist_ok=True)
    file=out/(family+"__"+variant+".json")
    file.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("004E3_WORKER_COMPLETE",json.dumps({"case":family,"variant":variant,
      "trials":4,"SAT":sum(x["outcome"].get("status")==SAT for x in records)},
      sort_keys=True),flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--child",action="store_true")
    a.add_argument("--family",choices=NAMES,required=True)
    a.add_argument("--variant",choices=VARIANTS,required=True)
    a.add_argument("--out",type=Path)
    opt=a.parse_args()
    if opt.child:
        frozen()
        print(json.dumps(child(opt.family,opt.variant),sort_keys=True))
    else:
        if opt.out is None:raise SystemExit("--out required")
        paired(opt.family,opt.variant,opt.out)
