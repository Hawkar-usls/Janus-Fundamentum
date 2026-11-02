#!/usr/bin/env python3
"""TIME-SAT-004E4 — transport three 004E3 survivor variants to four OTHER public families.

All four formulas were already available in prior JANUS research: not an external
blind holdout. Exact original bytes come only from original SHA-pinned archives,
not a live network; source, allocation, model and cold-process limits are checked.
No production merge, self-promoted champion or general speedup claim.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
import tempfile
from time import perf_counter,process_time
import zipfile

from janus_time_sat_004e3_swarm import select_verified_xor
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004d4b_real_pilot import original_model_replay

ROOT=Path("experiments/time_sat_004_external")
PRE=ROOT/"PREREGISTERED_004E4_OTHER_PUBLIC_FAMILIES_20261102.json"
PRE_BLOB="a3f1f0f5fd2df7c15386cbb762eb5ac44c69e959"
ZIP=ROOT/"time_sat_004d7_evidence/original-actions-ubuntu22.zip"
ZIP_SHA="795b3b4dfcfd7a83a205289b6b350c8afdc656874ff096c21b3986bf3a4ca3a1"
LIGHTS=ROOT/"time_sat_004d8_evidence/lights-out.original.cnf"
CASES={
    "lights-out":("",625,9216,45312,"6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361"),
    "or_randxor":("0be1e12a8e7282d1a4e389bb90f6dbc7",1200,8093,32400,"d63fa30fbe7003f7a2eff5939ab29c6064819d818115b630f57228cc86eedce1"),
    "greentao":("08cf53ca00dce11f5bfc02121c9bcd33",527,12692,38748,"622732d1d213e930a7711270aefa079c9329cb9a446b4f24d848fea2cab6b5a7"),
    "p-center":("011984fd82d62d609e776fbf5de75440",2320,8620,31414,"0542d88497b5a7ef610e30a570e8be9088bdb343e4b54d31561b5ae47bfa906b"),
}
VARIANTS=("native_all","native_width3plus_only","adaptive_80")
CPU=6
WALL=10
MEM=2147483648
REPS=2
SEED=20261102084
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
ALLOWED={SAT,"UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
         "UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def frozen():
    p=subprocess.run(["git","hash-object",str(PRE)],capture_output=True,text=True,check=True).stdout.strip()
    if p!=PRE_BLOB:raise AssertionError("004E4 FROZEN RESEARCH POLICY WAS MODIFIED")
    j=json.loads(PRE.read_text())
    if (tuple(j["fixed_candidates"])!=VARIANTS
        or [x["family"] for x in j["cases"]]!=list(CASES)
        or j["design"]["matrix_jobs"]!=24
        or j["design"]["fresh_children_per_job"]!=4
        or j["design"]["total_expected_cold_processes"]!=96
        or j["design"]["CPU_soft_seconds"]!=CPU
        or j["design"]["WALL_timeout_seconds"]!=WALL
        or j["design"]["RLIMIT_AS_bytes"]!=MEM
        or j["design"]["shuffled_pair_order_seed"]!=SEED):
        raise AssertionError("004E4 preregistration fields don't match executable")
    for c in j["cases"]:
        gid,n,m,lits,sha=CASES[c["family"]]
        if (c["n"],c["m"],c["literals"],c["CNF_SHA256"])!=(n,m,lits,sha):
            raise AssertionError("004E4 ORIGINAL candidate SHA/shape replaced")
        if gid and c["GBD_id_NOT_SHA256"]!=gid:
            raise AssertionError("Original ID mismatch")
    return j

def archived_cnf(family):
    if family not in CASES:raise AssertionError("Case not in frozen cohort")
    gid,n,m,literals,sha=CASES[family]
    if not gid:
        raw=LIGHTS.read_bytes()
    else:
        if digest(ZIP)!=ZIP_SHA:
            raise AssertionError("Archived original 004D7 ZIP bytes modified")
        with zipfile.ZipFile(ZIP) as f:
            filenames=[x for x in f.namelist() if Path(x).name==gid+".original.cnf"]
            if len(filenames)!=1:
                raise AssertionError("Ambiguous or missing original Actions DIMACS member")
            raw=f.read(filenames[0])
    if sha256(raw).hexdigest()!=sha:
        raise AssertionError("Original CNF byte SHA mismatch: "+family)
    if len(raw)>2_000_000:
        raise AssertionError("Original CNF exceeds registered bound")
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/"original.cnf"
        path.write_bytes(raw)
        dims=scan_dimacs(path)
        if (dims["n_variables"],dims["n_clauses"],
            dims["n_literal_occurrences"])!=(n,m,literals):
            raise AssertionError("Strict original DIMACS count mismatch: "+family)
        rows=read_cnf(path,n,m,max_literals=120000)
    return rows,n,sha

def worker(family,variant):
    if family not in CASES or variant not in ("raw_cms",)+VARIANTS:
        raise AssertionError("Not a registered family or candidate")
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    rows,n,sha=archived_cnf(family)
    before=perf_counter()
    form=select_verified_xor(rows,n,variant)
    scan_s=perf_counter()-before
    # Exact-source partition and source-mask XOR semantics come from unchanged 004E3.
    if (form["converted_source_clauses"]+len(form["cnf_clauses"])!=len(rows)
        or (form["choice"]=="native_xor")!=(len(form["equations"])>0)):
        raise AssertionError("Source clause XOR allocation lost an original clause")
    import pycryptosat
    solver=pycryptosat.Solver(threads=1)
    for eq in form["equations"]:
        solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
    for row in form["cnf_clauses"]:
        solver.add_clause(row)
    started_solver=perf_counter()
    sat,answer=solver.solve()
    solve_s=perf_counter()-started_solver
    if sat is True:
        if answer is None or len(answer)<=n:
            raise AssertionError("Incomplete SAT model")
        model=[i if bool(answer[i]) else -i for i in range(1,n+1)]
        if not original_model_replay(rows,n,model):
            raise AssertionError("004E4 model does not satisfy original full CNF")
        if family=="p-center":
            raise AssertionError("SAT output contradicts archived original P-center UNSAT RUP proof")
        status=SAT
    elif sat is False:
        if family=="lights-out":
            raise AssertionError("UNSAT contradicts original verified lights-out SAT model")
        status="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
    else:
        status="UNKNOWN_SOLVER_NO_ANSWER"
    return {
        "status":status,"family":family,"variant":variant,
        "original_CNF_SHA256":sha,
        "original_variables":n,"original_clauses":len(rows),
        "selected_XOR_equations":len(form["equations"]),
        "converted_original_clause_count":form["converted_source_clauses"],
        "original_residual_clauses":len(form["cnf_clauses"]),
        "representation":form["choice"],"scan_status":form["scan_status"],
        "source_scan_seconds":scan_s,"native_solve_seconds":solve_s,
        "cold_inner_wall_seconds":perf_counter()-started,
        "cold_child_CPU_seconds":process_time(),
        "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "all_SAT_models_original_full_replay":True,
        "UNSAT_certification":"NOT_PERFORMED_BY_004E4",
        "external_hidden_original":False,"production_C023":"UNCHANGED"}

def matrix_pair(family,variant,output):
    frozen()
    if family not in CASES or variant not in VARIANTS:
        raise AssertionError("Unregistered matrix combination")
    archived_cnf(family)
    records=[]
    for rep in range(REPS):
        choices=["candidate","raw_baseline"]
        random.Random(SEED+23*list(CASES).index(family)+5*VARIANTS.index(variant)+rep).shuffle(choices)
        for role in choices:
            actual=variant if role=="candidate" else "raw_cms"
            command=[sys.executable,str(Path(__file__).resolve()),"--child",
                     "--family",family,"--variant",actual]
            start=perf_counter()
            try:
                child=subprocess.run(command,capture_output=True,text=True,timeout=WALL,check=False)
                if child.returncode:
                    verdict=classify_nonzero_exit(child.returncode)
                    verdict["status"]=verdict["verdict"]
                    verdict["return_code"]=child.returncode
                    verdict["stderr_tail"]=child.stderr[-900:]
                else:
                    verdict=json.loads(child.stdout)
            except subprocess.TimeoutExpired:
                verdict={"status":"UNKNOWN_WALL_TIMEOUT"}
            record={"repeat":rep,"role":role,"actual_variant":actual,"pair_order":choices,
                    "full_cold_wall_seconds":perf_counter()-start,"result":verdict}
            records.append(record)
            print("004E4_ORIGINAL",family,variant,rep,role,
                  verdict.get("status","MISSING"),round(record["full_cold_wall_seconds"],3),flush=True)
    if len(records)!=4 or any(x["result"].get("status") not in ALLOWED for x in records):
        raise AssertionError("Invalid matrix child, lost results or unregistered error")
    for x in records:
        if x["result"]["status"]==SAT:
            if (x["result"]["original_CNF_SHA256"]!=CASES[family][4]
                or x["result"]["all_SAT_models_original_full_replay"] is not True):
                raise AssertionError("Original SAT source replay proof missing")
    report={"schema":"JANUS-TIME-SAT-004E4-FOUR-OTHER-PUBLIC-SOURCE-PAIRED-MATRIX-V1",
      "status":"PRESEEN_BY_JANUS_DIFFERENT_FROM_004E3_DEV_COHORT_NOT_BLIND",
      "precommitted_policy_git_blob":PRE_BLOB,
      "github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
      "github_head":os.getenv("GITHUB_SHA","LOCAL"),
      "github_job":os.getenv("GITHUB_JOB","LOCAL"),
      "runner_os":os.getenv("RUNNER_OS","LOCAL"),
      "runner_name":os.getenv("RUNNER_NAME","LOCAL"),
      "runner_arch":os.getenv("RUNNER_ARCH","LOCAL"),
      "family":family,"variant":variant,
      "original_CNF_SHA256":CASES[family][4],
      "CPU_soft_seconds":CPU,"wall_seconds":WALL,
      "RLIMIT_AS_bytes":MEM,"paired_repetitions":REPS,
      "records":records,"source_already_seen_elsewhere":True,
      "independent_004C_witness":"OPEN","production_C023":"UNCHANGED",
      "global_champion":"NOT_ESTABLISHED"}
    output.mkdir(parents=True,exist_ok=True)
    (output/(family+"__"+variant+"__"+os.getenv("RUNNER_OS","LOCAL")+".json")).write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("004E4_VM_COMPLETE",family,variant,
          "SAT",sum(x["result"]["status"]==SAT for x in records),flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--child",action="store_true")
    a.add_argument("--family",choices=tuple(CASES),required=True)
    a.add_argument("--variant",choices=("raw_cms",)+VARIANTS,required=True)
    a.add_argument("--out",type=Path)
    x=a.parse_args()
    if x.child:
        frozen()
        print(json.dumps(worker(x.family,x.variant),sort_keys=True))
    else:
        if x.out is None or x.variant=="raw_cms":
            raise SystemExit("Matrix job must be one of three fixed candidates with --out")
        matrix_pair(x.family,x.variant,x.out)
