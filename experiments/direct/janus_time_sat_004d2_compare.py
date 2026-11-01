#!/usr/bin/env python3
"""TIME-SAT-004D2: cross-solver comparison on *same original* SATComp2026 CNF.

Five alternatives, each in fresh Python process under identical CPU/RAM/wall:
- JANUS exact-XOR detection + Python GF(2), independent original-CNF replay
- CryptoMiniSat (native XOR) AFTER exact original-CNF recognition (cost charged)
- CryptoMiniSat on ORIGINAL unchanged CNF, its own XOR reasoning allowed
- raw CaDiCaL195 on ORIGINAL CNF
- raw Glucose4 on ORIGINAL CNF

This is a PUBLIC, seen-development case. It is not blind or a head-to-head
universal SAT claim; CryptoMiniSat exposes specialized XOR capability.
Timeouts cannot be turned into solve times. Not a new SAT proof.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import resource
import signal
import subprocess
import sys
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d1_xor import group_parity_equations,solve_if_exact_xor,check_original_cnf

SOURCE_REL="experiments/time_sat_004_external/lightsout_01d6fa8_verified/original.cnf"
SOURCE_SHA="6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361"
SOURCE_N=625
SOURCE_M=9216
ARMS=("janus_gf2","cryptominisat_native_xor","cryptominisat_original_cnf",
      "cadical195_original_cnf","glucose4_original_cnf")
CPU_LIMIT=8
WALL_LIMIT=11
RAM_LIMIT=2_147_483_648
ORDER_SEED=20261101042
REPEATS=3

def full_verify(rows,n,assignment):
    if not isinstance(assignment,dict):return False
    return len(assignment)>=n and all(
        any(assignment.get(abs(l))==(l>0) for l in clause)
        for clause in rows)

def verify_source(path):
    if sha256(path.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise AssertionError("original public competition CNF SHA mismatch")
    n=m=None
    with path.open("r",encoding="ascii") as f:
        for line in f:
            if line.startswith("p cnf"):
                _,_,n,m=line.split()
                n=int(n);m=int(m)
                break
    if (n,m)!=(SOURCE_N,SOURCE_M):
        raise AssertionError("original SOURCE problem dimensions changed")
    return read_cnf(path,n,m)

def run_one(arm,rows,n=SOURCE_N):
    if arm not in ARMS:raise ValueError("unregistered solver")
    start=perf_counter()
    native_seconds=None
    equation_count=None
    solver_stats=None
    if arm=="janus_gf2":
        outcome=solve_if_exact_xor(rows,n)
        status=outcome["verdict"]
        if status!="SAT_ORIGINAL_MODEL_VERIFIED":
            raise AssertionError("original pinned Lights-out not exactly XOR SAT")
        assignment={abs(l):l>0 for l in outcome["model"]}
        equation_count=outcome["equation_count"]
        solver_stats={"gf2_rank":outcome["gf2_rank"]}
        native_seconds=outcome["gf2_and_verification_seconds"]
    elif arm.startswith("cryptominisat"):
        import pycryptosat
        solver=pycryptosat.Solver(threads=1)
        if arm=="cryptominisat_native_xor":
            receipt=group_parity_equations(rows,n)
            if receipt["status"]!="EXACT_XOR_COVER_PASS":
                raise AssertionError("incomplete source XOR cover")
            equation_count=len(receipt["equations"])
            for eq in receipt["equations"]:
                solver.add_xor_clause(list(eq["variables"]),bool(eq["rhs"]))
        else:
            for c in rows:solver.add_clause(list(c))
        before=perf_counter()
        answer,solution=solver.solve()
        native_seconds=perf_counter()-before
        if answer is None:
            return {"verdict":"UNKNOWN_CMS_INTERNAL_LIMIT","arm":arm,"source_sha256":SOURCE_SHA}
        if not answer:
            return {"verdict":"UNSAT_SOLVER_ONLY_NO_CERTIFICATE","arm":arm,"source_sha256":SOURCE_SHA}
        assignment={i:bool(solution[i]) for i in range(1,n+1)}
        solver_stats={"engine":"CryptoMiniSat","version":"pycryptosat 5.15.0","xor_equations":equation_count}
    else:
        from pysat.solvers import Solver
        engine="cadical195" if arm=="cadical195_original_cnf" else "glucose4"
        with Solver(name=engine,bootstrap_with=rows) as solver:
            before=perf_counter()
            answer=solver.solve()
            native_seconds=perf_counter()-before
            if answer is None:
                return {"verdict":"UNKNOWN_PYSAT_INTERNAL_LIMIT","arm":arm,"source_sha256":SOURCE_SHA}
            if not answer:
                return {"verdict":"UNSAT_SOLVER_ONLY_NO_CERTIFICATE","arm":arm,"source_sha256":SOURCE_SHA}
            solution=solver.get_model()
            solver_stats=solver.accum_stats()
        assignment={abs(x):x>0 for x in solution or []}
    # The original 9216 clauses are replayed, not just GF(2) equations.
    if not full_verify(rows,n,assignment):
        raise AssertionError("SAT MODEL REPLAY FAIL ON ORIGINAL CNF")
    whole=perf_counter()-start
    return {
        "arm":arm,"verdict":"SAT_ORIGINAL_CNF_INDEPENDENTLY_VERIFIED",
        "original_CNF_n":n,"original_CNF_m":len(rows),
        "original_CNF_SHA256":SOURCE_SHA,
        "source_XOR_equations_if_extracted":equation_count,
        "native_solver_time_seconds_including_solver_input":native_seconds,
        "inner_full_time_seconds_after_DIMACS_read":whole,
        "max_process_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "native_stats":solver_stats,
        "verification":"EVERY_ORIGINAL_DIMACS_CLAUSE",
        "portable_UNSAT_certificate":"NONE",
    }

def worker(source:Path,arm:str):
    resource.setrlimit(resource.RLIMIT_AS,(RAM_LIMIT,RAM_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU_LIMIT,CPU_LIMIT+1))
    rows=verify_source(source)
    response=run_one(arm,rows)
    print(json.dumps(response,sort_keys=True),flush=True)

def control(source:Path,out:Path):
    # Exactly the same source and resources, with randomized arm order.
    rows=verify_source(source)
    if len(rows)!=SOURCE_M:raise AssertionError("source clauses changed")
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    for repeat in range(REPEATS):
        order=list(ARMS)
        random.Random(ORDER_SEED+repeat).shuffle(order)
        for arm in order:
            cmd=[sys.executable,str(Path(__file__).resolve()),"--worker",
                 "--source",str(source),"--arm",arm]
            started=perf_counter()
            try:
                p=subprocess.run(cmd,text=True,capture_output=True,timeout=WALL_LIMIT,
                                 check=False)
                if p.returncode!=0:
                    result=classify_nonzero_exit(p.returncode)
                    result.update({"return_code":p.returncode,"stderr_tail":p.stderr[-1500:]})
                else:
                    result=json.loads(p.stdout)
            except subprocess.TimeoutExpired:
                result={"verdict":"UNKNOWN_WALL_TIMEOUT"}
            elapsed=perf_counter()-started
            records.append({"repeat":repeat,"order_slot":order.index(arm),"arm":arm,
                            "result":result,"full_end_to_end_child_wall_seconds":elapsed})
            print("004D2",repeat,arm,result["verdict"],round(elapsed,5),flush=True)
    summary={
        "schema":"JANUS-TIME-SAT-004D2-REAL-XOR-CNF-FAIR-BUDGET-PILOT-V1",
        "original_CNF_SHA256":SOURCE_SHA,"original_n":SOURCE_N,"original_m":SOURCE_M,
        "original_GBD_id":"01d6fa8efd18ebfecd06af408958477b",
        "study_scope":"ONE_PREVIOUSLY_SEEN_PUBLIC_COMPETITION_XOR_FAMILY_NOT_HIDDEN",
        "arms":ARMS,"randomization_seed":ORDER_SEED,"repeats":REPEATS,
        "time_metric":"full child end-to-end includes Python startup, importing solver, reading/rechecking entire original source, XOR recognition or native CNF insertion, solve and independent original CNF verification",
        "resource_budgets":{"CPU_seconds_per_arm":CPU_LIMIT,
                            "wall_seconds_per_arm":WALL_LIMIT,
                            "virtual_memory_limit_bytes_per_arm":RAM_LIMIT,
                            "engine_threads":"1"},
        "version_pins":{"python_sat":"1.9.dev17","pycryptosat":"5.15.0"},
        "original_source_unmodified":True,
        "native_preprocessor_control":"CryptoMiniSat both original CNF and separately extracted native XOR equations",
        "known_test_set":True,"external_sealed_challenge":"NOT_PERFORMED",
        "external_independent_Witness":"NOT_PERFORMED",
        "production_C023":"UNCHANGED",
        "results":records}
    (out/"benchmark.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("004D2_SUMMARY",json.dumps({"counts":{
       arm:{status:sum(x["arm"]==arm and x["result"]["verdict"]==status for x in records)
            for status in sorted({x["result"]["verdict"] for x in records})}
       for arm in ARMS},"source_sha":SOURCE_SHA},sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=Path(SOURCE_REL))
    p.add_argument("--out",type=Path)
    p.add_argument("--worker",action="store_true")
    p.add_argument("--arm",choices=ARMS)
    args=p.parse_args()
    if args.worker:
        if not args.arm:raise SystemExit("--arm is required with --worker")
        worker(args.source,args.arm)
    else:
        if args.out is None:raise SystemExit("--out required")
        control(args.source,args.out)
