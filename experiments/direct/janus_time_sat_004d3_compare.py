#!/usr/bin/env python3
"""TIME-SAT-004D3B: frozen post-structure public two-original-source comparison.

Two NEW SAT Competition 2026 Lights-out instances: SAT model and GF(2)
algebraic contradiction. 5 arms x 3 randomized repeats x 2 original
sources x 2 Ubuntu workers. Original SHA bytes fixed BEFORE benchmarking.
No hidden-test claim, no portable UNSAT proof or universal P=NP claim.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import random
import resource
import subprocess
import sys
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d1_xor import (
    group_parity_equations,solve_if_exact_xor,
    independently_replay_unsat_combination
)

BASE=Path("experiments/time_sat_004_external/time_sat_004d3_evidence")
CASES={
 "lightsout_new_sat":{
  "file":"lightsout-1.original.cnf",
  "gbd_id":"28dcc4119e1bbb5fbd3fdd8f4140f28d",
  "n":2702,"m":8933,
  "sha256":"b2c2008e5d24a7aa82499d1486af2550a53a7167e46836c4b9977846204ad483",
  "expected_certified_original_GF2_result":"SAT"},
 "lightsout_new_unsat":{
  "file":"lightsout-2.original.cnf",
  "gbd_id":"0efcbd10294eb001b16b4d126923372f",
  "n":529,"m":7744,
  "sha256":"84729f80119b50efac42d9477438abbc58c8712654ffe1fcdf9f324e44ae165d",
  "expected_certified_original_GF2_result":"UNSAT"}
}
ARMS=("janus_gf2","cryptominisat_native_xor","cryptominisat_original_cnf",
      "cadical195_original_cnf","glucose4_original_cnf")
REPEATS=3
SEED=20261101043
CPU=8
WALL=11
AS_BYTES=2_147_483_648

def read_exact(case):
    meta=CASES[case]
    path=BASE/meta["file"]
    if sha256(path.read_bytes()).hexdigest()!=meta["sha256"]:
        raise AssertionError("original competition source SHA mismatch")
    with path.open("r",encoding="ascii") as f:
        headers=[x.strip() for x in f if x.startswith("p cnf ")]
    if len(headers)!=1:
        raise AssertionError("original DIMACS header mismatch")
    parts=headers[0].split()
    if (int(parts[2]),int(parts[3]))!=(meta["n"],meta["m"]):
        raise AssertionError("original competition DIMACS dimensions changed")
    rows=read_cnf(path,meta["n"],meta["m"])
    return rows

def model_valid(rows,n,values):
    return len(values)>=n and all(
       any(values.get(abs(l)) is (l>0) for l in row) for row in rows)

def run_one(case,arm,rows):
    if arm not in ARMS:raise AssertionError("unregistered algorithm")
    meta=CASES[case]
    n=meta["n"]
    start=perf_counter()
    assignment=None
    equation_count=None
    native_seconds=None
    stats=None
    algebraic=None
    if arm=="janus_gf2":
        gf2=solve_if_exact_xor(rows,n)
        if gf2["coverage_status"]!="EXACT_XOR_COVER_PASS":
            raise AssertionError("frozen exact XOR source no longer exact")
        equation_count=gf2["equation_count"]
        native_seconds=gf2["gf2_and_verification_seconds"]
        stats={"rank":gf2["gf2_rank"]}
        if gf2["verdict"]=="SAT_ORIGINAL_MODEL_VERIFIED":
            assignment={abs(l):l>0 for l in gf2["model"]}
        elif gf2["verdict"]=="GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY":
            combination=gf2["xor_contradiction_equation_indices"]
            if not independently_replay_unsat_combination(rows,n,combination):
                raise AssertionError("GF2 contradiction not replayed on original")
            algebraic={"equation_combination_length":len(combination),
                       "original_GF2_source_replay":"PASS",
                       "independent_external_admin":"NOT_DONE",
                       "portable_DRUP_LRAT":"NOT_PRODUCED"}
        else:
            raise AssertionError("GF2 original source unexpectedly unknown")
    elif arm.startswith("cryptominisat"):
        import pycryptosat
        cms=pycryptosat.Solver(threads=1)
        if arm=="cryptominisat_native_xor":
            cover=group_parity_equations(rows,n)
            if cover["status"]!="EXACT_XOR_COVER_PASS":
                raise AssertionError("frozen native XOR model source not exact")
            equation_count=len(cover["equations"])
            for eq in cover["equations"]:
                cms.add_xor_clause(list(eq["variables"]),bool(eq["rhs"]))
        else:
            for row in rows:
                cms.add_clause(list(row))
        before=perf_counter()
        sat,model=cms.solve()
        native_seconds=perf_counter()-before
        if sat is None:
            return {"arm":arm,"verdict":"UNKNOWN_CMS_INTERNAL_LIMIT"}
        if sat:
            if model is None or len(model)<=n:
                raise AssertionError("CMS SAT answer no complete model")
            assignment={i:bool(model[i]) for i in range(1,n+1)}
        stats={"engine":"CryptoMiniSat","pycryptosat_pin":"5.15.0",
               "native_xor_constraints":equation_count}
    else:
        from pysat.solvers import Solver
        engine="cadical195" if arm.startswith("cadical") else "glucose4"
        with Solver(name=engine,bootstrap_with=rows) as cdcl:
            before=perf_counter()
            sat=cdcl.solve()
            native_seconds=perf_counter()-before
            if sat is None:
                return {"arm":arm,"verdict":"UNKNOWN_PYSAT_INTERNAL_LIMIT"}
            if sat:
                model=cdcl.get_model() or []
                assignment={abs(v):v>0 for v in model}
            stats=cdcl.accum_stats()
    if assignment is not None:
        if meta["expected_certified_original_GF2_result"]!="SAT":
            raise AssertionError("solver returned SAT for source-bound certified GF2 contradiction")
        if not model_valid(rows,n,assignment):
            raise AssertionError("SAT model failed every-original-CNF-clause replay")
        verdict="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
    else:
        if meta["expected_certified_original_GF2_result"]!="UNSAT":
            raise AssertionError("solver returned UNSAT for source-bound verified SAT input")
        verdict=("GF2_UNSAT_SOURCE_COMBINATION_REPLAYED_SAME_ADMIN" if arm=="janus_gf2"
                 else "UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF")
    return {"arm":arm,"verdict":verdict,
            "original_GBD_id_NOT_SHA256":meta["gbd_id"],
            "original_SHA256":meta["sha256"],
            "source_n":n,"source_clauses":len(rows),
            "parity_equation_count":equation_count,
            "native_algorithm_seconds":native_seconds,
            "child_inner_seconds_after_parse":perf_counter()-start,
            "successful_process_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "algebraic_certificate":algebraic,"native_solver_stats":stats,
            "source_SAT_model_checked_every_original_clause":assignment is not None,
            "UNSAT_outside_admin_verifier":"NOT_PERFORMED"}

def worker(case,arm):
    resource.setrlimit(resource.RLIMIT_AS,(AS_BYTES,AS_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    rows=read_exact(case)
    receipt=run_one(case,arm,rows)
    print(json.dumps(receipt,sort_keys=True),flush=True)

def benchmark(out):
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for case,meta in CASES.items():
        original=read_exact(case)
        if len(original)!=meta["m"]:
            raise AssertionError("source row count changed")
        for repeat in range(REPEATS):
            arms=list(ARMS)
            random.Random(SEED+100*list(CASES).index(case)+repeat).shuffle(arms)
            for arm in arms:
                cmd=[sys.executable,str(Path(__file__).resolve()),"--worker",
                     "--case",case,"--arm",arm]
                before=perf_counter()
                try:
                    child=subprocess.run(cmd,capture_output=True,text=True,
                                         timeout=WALL,check=False)
                    if child.returncode:
                        outcome=classify_nonzero_exit(child.returncode)
                        outcome["return_code"]=child.returncode
                        outcome["stderr_tail"]=child.stderr[-1000:]
                    else:
                        outcome=json.loads(child.stdout)
                except subprocess.TimeoutExpired:
                    outcome={"verdict":"UNKNOWN_WALL_TIMEOUT"}
                elapsed=perf_counter()-before
                rows.append({"case":case,"gbd_id":meta["gbd_id"],
                             "arm":arm,"repeat":repeat,
                             "randomized_order":arms,
                             "full_child_end_to_end_wall_seconds":elapsed,
                             "result":outcome})
                print("004D3B",case,repeat,arm,
                      outcome["verdict"],round(elapsed,4),flush=True)
    outdata={
      "schema":"JANUS-TIME-SAT-004D3B-TWO-NEW-PUBLIC-LIGHTSOUT-BUDGETED-FAIR-V1",
      "status":"RESEARCH_ONLY_END_TO_END_COMPARISON_NOT_GENERALIZED_HIDDEN",
      "source_selection":"Only first 2 frozen 004D3 sources with independently complete XOR covers; no substituted instances",
      "original_permanent_source_archive":"experiments/time_sat_004_external/time_sat_004d3_evidence/manifest.json",
      "new_cases":CASES,
      "arms":ARMS,"repeats_per_host":REPEATS,
      "random_order_seed":SEED,
      "child_limit_CPU_seconds":CPU,"parent_limit_wall_seconds":WALL,
      "child_limit_address_space_bytes":AS_BYTES,
      "full_cost_includes":"Python cold start+source read+sha+DIMACS parse+XOR cover/extract+solve+original model/contradiction verification",
      "UNSAT_other_solvers":"SOLVER_ONLY_NO_PORTABLE_PROOF",
      "uncertainty":"Per-case samples only, population advantage not established",
      "independent_outside_Github_Witness":"OPEN",
      "other_7_004D3_sources":"ABSTAIN_NOT_BENCHMARKED",
      "C023_main":"UNCHANGED",
      "results":rows}
    (out/"comparison.json").write_text(json.dumps(outdata,sort_keys=True,indent=2)+"\n")
    print("004D3B_SUMMARY",json.dumps({key:sum(x["result"]["verdict"]==key
         for x in rows) for key in sorted({x["result"]["verdict"] for x in rows})},
         sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--worker",action="store_true")
    p.add_argument("--case",choices=list(CASES))
    p.add_argument("--arm",choices=ARMS)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.worker:
        if not a.case or not a.arm:raise SystemExit("--case and --arm required")
        worker(a.case,a.arm)
    else:
        if not a.out:raise SystemExit("--out required")
        benchmark(a.out)
