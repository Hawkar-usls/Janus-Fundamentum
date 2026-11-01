#!/usr/bin/env python3
"""TIME-SAT-004D4B: four pre-frozen real public SATComp26 mixed candidates.

All download/original DIMACS SHA are pinned to original dual-worker 004D3.
First perform source-only partial XOR detection; ONLY if a real residual CNF
AND at least one *complete source-proven XOR block* were extracted, run
exactly 3 preregistered cold-process solver arms with identical resource
budgets, 2 paired repetitions each. NEVER silently benchmark a no-XOR case.

Public seen-source DEVELOPMENT test, not an external hidden holdout.
UNSAT from any solver: SOLVER_ONLY / NOT PORTABLE PROOF.
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
from time import perf_counter

from janus_time_sat_004b_acquire import retrieve,unpack_bounded,scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d4_mixed_xor import extract_mixed_xor

FROZEN=Path("experiments/time_sat_004_external/PREREGISTERED_004D4B_PUBLIC_FOUR_MIXED_20261101.json")
FROZEN_BLOB="0cbf0eee23aa77b399ad2057f113ac1e48bd8405"
ARMS=("janus_mixed_native_xor","cryptominisat_original_cnf","cadical195_original_cnf")
REPEATS=2
CPU=8
WALL=11
AS_BYTES=2_147_483_648
RANDOM_SEED=20261101045
MAX_CASES=4

def digest_file(path):
    h=sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(65536),b""):
            h.update(chunk)
    return h.hexdigest()

def frozen_sources():
    sha=subprocess.run(["git","hash-object",str(FROZEN)],capture_output=True,
                       text=True,check=True).stdout.strip()
    if sha!=FROZEN_BLOB:
        raise AssertionError("004D4B frozen original candidate manifest mutated")
    data=json.loads(FROZEN.read_text())
    sources=data["candidates"]
    if len(sources)!=MAX_CASES or len({x["GBD_id_NOT_SHA256"] for x in sources})!=MAX_CASES:
        raise AssertionError("frozen four candidates are not unique")
    if [x["family"] for x in sources]!=[
        "linear-equations","xor-shifting","minimum-disagreement-parity","binary-tree-parity"]:
        raise AssertionError("frozen cohort family order modified")
    return sources

def check_original(path,case):
    if digest_file(path)!=case["decoded_CNF_SHA256"]:
        raise AssertionError("Original DIMACS byte SHA mismatch")
    shape=scan_dimacs(path)
    if shape!=case["original_shape"]:
        raise AssertionError("Original DIMACS grammar or counts mismatch")
    if not (1<=shape["n_variables"]<=5000 and shape["n_clauses"]<=30000
            and shape["n_literal_occurrences"]<=120000):
        raise AssertionError("Original outside approved source limits")
    return shape

def original_model_replay(rows,n,values):
    if len(values)!=n or {abs(x) for x in values}!={*range(1,n+1)}:
        return False
    assignment={abs(x):x>0 for x in values}
    return all(any(assignment[abs(v)]==(v>0) for v in clause) for clause in rows)

def worker(path,case,arm):
    resource.setrlimit(resource.RLIMIT_AS,(AS_BYTES,AS_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    n=case["original_shape"]["n_variables"]
    m=case["original_shape"]["n_clauses"]
    started=perf_counter()
    check_original(path,case)
    rows=read_cnf(path,n,m,max_literals=120000)
    extracted=None
    xors=0
    residual=m
    if arm=="janus_mixed_native_xor":
        extracted=extract_mixed_xor(rows,n)
        if extracted["status"]!="SOURCE_PARTITION_VERIFIED":
            return {"verdict":"ABSTAIN_ORIGINAL_MIXED_XOR_NOT_PROVEN",
                    "structural_status":extracted["status"]}
        xors=len(extracted["equations"])
        residual=len(extracted["residual_clauses"])
        if xors==0 or residual==0:
            return {"verdict":"ABSTAIN_NOT_PARTIAL_MIXED_XOR",
                    "xor_equations":xors,"residual_original_clauses":residual}
        if extracted["source_xor_clauses"]+residual!=m:
            raise AssertionError("Original clause loss")
    before=perf_counter()
    if arm in ("janus_mixed_native_xor","cryptominisat_original_cnf"):
        import pycryptosat
        s=pycryptosat.Solver(threads=1)
        if extracted is not None:
            for eq in extracted["equations"]:
                s.add_xor_clause(eq["variables"],bool(eq["rhs"]))
            for clause in extracted["residual_clauses"]:
                s.add_clause(clause)
        else:
            for clause in rows:s.add_clause(clause)
        input_seconds=perf_counter()-before
        sat,model=s.solve()
        native_solve_seconds=perf_counter()-(before+input_seconds)
        if sat is None:verdict="UNKNOWN_NATIVE_SOLVER_UNRESOLVED"
        elif sat:
            if model is None or len(model)<=n:
                raise AssertionError("Incomplete original SAT model")
            values=[i if bool(model[i]) else -i for i in range(1,n+1)]
            if not original_model_replay(rows,n,values):
                raise AssertionError("SAT model violates source original CNF")
            verdict="SAT_ORIGINAL_CNF_VERIFIED"
        else:verdict="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
    elif arm=="cadical195_original_cnf":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as s:
            input_seconds=perf_counter()-before
            start_solve=perf_counter()
            sat=s.solve()
            native_solve_seconds=perf_counter()-start_solve
            model=s.get_model() if sat else None
            solver_stats=s.accum_stats()
        if sat is None:verdict="UNKNOWN_CDCL_INTERNAL"
        elif sat:
            if not model or not original_model_replay(rows,n,model):
                raise AssertionError("CaDiCaL model invalid on original DIMACS")
            verdict="SAT_ORIGINAL_CNF_VERIFIED"
        else:verdict="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
    else:raise AssertionError("Unregistered 004D4B solver arm")
    return {
      "verdict":verdict,"arm":arm,"original_decoded_SHA256":case["decoded_CNF_SHA256"],
      "n":n,"m":m,"complete_XOR_equations":xors,
      "xor_source_clauses":0 if extracted is None else extracted["source_xor_clauses"],
      "residual_source_clauses":residual,
      "child_inner_seconds_including_parse_and_verification":perf_counter()-started,
      "input_construction_seconds":input_seconds,
      "native_solver_seconds":native_solve_seconds,
      "successful_child_peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "UNSAT_portable_certificate":"NOT_PRODUCED",
      "independent_administrative_Witness":"NOT_PERFORMED",
    }

def analyze_source(path,case):
    shape=check_original(path,case)
    before=perf_counter()
    rows=read_cnf(path,shape["n_variables"],shape["n_clauses"],max_literals=120000)
    x=extract_mixed_xor(rows,shape["n_variables"])
    structural_s=perf_counter()-before
    if x["status"]!="SOURCE_PARTITION_VERIFIED":
        return {"status":x["status"],"xor_equations":None,"xor_source_clauses":None,
                "residual_original_clauses":None,"structural_seconds":structural_s,
                "benchmark_admitted":False,
                "source_n":shape["n_variables"],"source_m":shape["n_clauses"]}
    consumed=x["source_xor_clauses"]
    residual=x["source_residual_clauses"]
    eq=x["complete_xor_equation_count"]
    if consumed+residual!=shape["n_clauses"]:
        raise AssertionError("Original source clause partition incomplete")
    return {"status":"SOURCE_PARTITION_VERIFIED","xor_equations":eq,
            "xor_source_clauses":consumed,"residual_original_clauses":residual,
            "fraction_original_clauses_extracted":consumed/shape["n_clauses"],
            "structural_seconds":structural_s,
            "benchmark_admitted":eq>0 and residual>0,
            "source_n":shape["n_variables"],"source_m":shape["n_clauses"]}

def main(out):
    sources=frozen_sources()
    out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for i,case in enumerate(sources):
        name=case["GBD_id_NOT_SHA256"]
        item={"index":i,"family":case["family"],"GBD_id_NOT_SHA256":name,
              "frozen_original_CNF_SHA256":case["decoded_CNF_SHA256"],
              "frozen_transfer_SHA256":case["original_transfer_SHA256"],
              "source_status":"NOT_DOWNLOADED","structural":None,"benchmark":[]}
        raw=decoded=None
        try:
            raw,download=retrieve({"hash":name,"official_uri":case["official_URI"]},out)
            if download["source_sha256"]!=case["original_transfer_SHA256"]:
                raise AssertionError("Original GBD transfer changed")
            decoded=out/(name+".cnf")
            decoded_meta=unpack_bounded(raw,decoded)
            if decoded_meta["uncompressed_sha256"]!=case["decoded_CNF_SHA256"]:
                raise AssertionError("Original decoded GBD source SHA changed")
            check_original(decoded,case)
            item["source_status"]="ORIGINAL_SHA_AND_DIMACS_VERIFIED"
            item["structural"]=analyze_source(decoded,case)
            if item["structural"]["benchmark_admitted"]:
                for repeat in range(REPEATS):
                    order=list(ARMS)
                    random.Random(RANDOM_SEED+i*100+repeat).shuffle(order)
                    for arm in order:
                        before=perf_counter()
                        cmd=[sys.executable,str(Path(__file__).resolve()),"--worker",
                             "--source",str(decoded),"--case-index",str(i),"--arm",arm]
                        try:
                            child=subprocess.run(cmd,capture_output=True,text=True,
                                                 check=False,timeout=WALL)
                            if child.returncode:
                                outcome=classify_nonzero_exit(child.returncode)
                                outcome["return_code"]=child.returncode
                                outcome["stderr_tail"]=child.stderr[-800:]
                            else:outcome=json.loads(child.stdout)
                        except subprocess.TimeoutExpired:
                            outcome={"verdict":"UNKNOWN_WALL_TIMEOUT"}
                        item["benchmark"].append({
                            "repeat":repeat,"arm":arm,"randomized_arm_order":order,
                            "full_cold_child_wall_seconds":perf_counter()-before,
                            "result":outcome})
                        print("004D4B_COLD",case["family"],arm,
                              outcome["verdict"],flush=True)
            print("004D4B_SOURCE",case["family"],
                  item["structural"]["status"],"eq",
                  item["structural"].get("xor_equations"),
                  "residual",item["structural"].get("residual_original_clauses"),flush=True)
        except Exception as e:
            item["source_status"]="SOURCE_OR_ANALYSIS_EXCEPTION"
            item["error_class"]=type(e).__name__
            item["error_message"]=str(e)[:300]
        finally:
            if raw is not None:raw.unlink(missing_ok=True)
            if decoded is not None:decoded.unlink(missing_ok=True)
        rows.append(item)
    result={
      "schema":"JANUS-TIME-SAT-004D4B-REAL-FOUR-PUBLIC-SOURCE-MIXED-XOR-CNF-V1",
      "status":"RESEARCH_PUBLIC_PRESEEN_SOURCE_NOT_BLIND_NO_PRODUCTION",
      "original_frozen_manifest_git_blob":FROZEN_BLOB,
      "Github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
      "Github_HEAD":os.getenv("GITHUB_SHA","LOCAL"),
      "source_provenance":"Exact SHA-256 pinned 004D3 original GitHub dual-worker source receipts",
      "CPU_seconds_per_child":CPU,"WALL_seconds_per_child":WALL,
      "RLIMIT_AS_bytes":AS_BYTES,
      "repeats_per_solver_per_worker":REPEATS,
      "eligible_solver_arms":ARMS,
      "noXOR_noBenchmark":True,
      "source_original_SAT_model_check":"ALL_ORIGINAL_CLAUSES",
      "solver_UNSAT_certification":"SOLVER_ONLY_NO_PORTABLE_PROOF",
      "external_Witness":"OPEN","C023_main":"UNCHANGED",
      "cases":rows}
    (out/"result.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    if any(x["source_status"]!="ORIGINAL_SHA_AND_DIMACS_VERIFIED" or x["structural"] is None
           or (x["structural"]["benchmark_admitted"] and
               len(x["benchmark"])!=REPEATS*len(ARMS)) for x in rows):
        raise AssertionError("004D4B_INCOMPLETE_ORIGINAL_COHORT_OR_MATCHED_ARMS")
    print("TIME_SAT_004D4B_SUMMARY",json.dumps({
       "sources_verified":len(rows),
       "positive_partial_xor":sum(x["structural"]["benchmark_admitted"] for x in rows),
       "solver_trial_records":sum(len(x["benchmark"]) for x in rows),
       "statuses":{x["family"]:x["structural"]["status"] for x in rows}},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--worker",action="store_true")
    p.add_argument("--source",type=Path)
    p.add_argument("--case-index",type=int)
    p.add_argument("--arm",choices=ARMS)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.worker:
        cases=frozen_sources()
        if a.source is None or a.case_index is None or a.arm is None:
            raise SystemExit("Need worker args")
        print(json.dumps(worker(a.source,cases[a.case_index],a.arm),sort_keys=True))
    else:
        if a.out is None:raise SystemExit("--out required")
        main(a.out)
