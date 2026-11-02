#!/usr/bin/env python3
"""JANUS TIME-SAT-004E5: exact SAT-preserving metamorphic gate robustness.

This tests the *stability of representation-based choices*, NOT new SAT
instances. Frozen seed/transform/padding on original source-verified SAT CNFs.
Each VM pairs candidate with raw native CMS on IDENTICAL generated DIMACS;
all solving children include source replay, full transformation and verification.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter,process_time

from janus_time_sat_004e2_adaptive_gate import original as source_e2
from janus_time_sat_004e4_transfer import archived_cnf
from janus_time_sat_004e3_swarm import select_verified_xor
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d4b_real_pilot import original_model_replay

ROOT=Path("experiments/time_sat_004_external")
PRE=ROOT/"PREREGISTERED_004E5_SAT_EQUIVALENT_PADDING_20261102.json"
PRE_BLOB="a417e339d2f1fa6214e43d8a3554191de0c51f77"
SOURCE={
    "lights-out":("6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361",
                  ROOT/"time_sat_004d8_evidence/original-ubuntu22-lights-out.result.json"),
    "binary-tree-parity":("8d94924bef8978b28a2bf95472556b280bef5d98b6833c6db33554098f52d2d8",
                  ROOT/"time_sat_004d4b_evidence/binary-tree-parity-SAT-original-model.json"),
}
FAMILIES=tuple(SOURCE)
PADS=(0,5,30)
VARIANTS=("native_all","adaptive_80")
CPU=6
WALL=10
MEM=2147483648
REPEATS=2
SEED=20261102085
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"

def preflight():
    h=subprocess.run(["git","hash-object",str(PRE)],capture_output=True,
                     text=True,check=True).stdout.strip()
    if h!=PRE_BLOB:raise AssertionError("Frozen signed-SAT metamorphic prereg Git blob changed")
    p=json.loads(PRE.read_text())
    mat=p["matrix"]
    if (mat["family"]!=list(FAMILIES) or mat["padding_percent"]!=list(PADS)
        or mat["candidate"]!=list(VARIANTS)
        or mat["jobs"]!=24 or mat["max_parallel"]!=20
        or mat["paired_repeats_per_worker"]!=REPEATS
        or mat["CPU_soft_s"]!=CPU
        or mat["WALL_timeout_s"]!=WALL
        or mat["RLIMIT_AS_bytes"]!=MEM
        or p["metamorphic_rewrite"]["seed"]!=SEED):
        raise AssertionError("Preregistered source families, variants, transformations or caps altered")
    return p

def original_verified(family):
    if family not in SOURCE:raise ValueError("Unregistered source family")
    if family=="lights-out":
        rows,n,sha=archived_cnf(family)
    else:
        rows,n,sha=source_e2(family)
    expected,model_path=SOURCE[family]
    if sha!=expected:raise AssertionError("Previously archived original-CNF SHA changed")
    model=json.loads(model_path.read_text(encoding="utf-8"))
    if model["original_CNF_SHA256"]!=sha:
        raise AssertionError("Original source/model not same SHA")
    assignment=model["signed_model"]
    if (len(assignment)!=n or {abs(v) for v in assignment}!=set(range(1,n+1))
        or not original_model_replay(rows,n,assignment)):
        raise AssertionError("Full original-source SAT model fails")
    return rows,n,sha,assignment

def transform(rows,n,assignment,family,pad):
    """Original formula ↔ this formula by variable/polarity bijection.

    Permutes clauses and literal order, adds only logically true clauses.
    Literal truth values and signed model are transformed consistently.
    """
    if family not in FAMILIES or pad not in PADS:
        raise AssertionError("Not one of six predeclared formulas")
    rng=random.Random(SEED+17*FAMILIES.index(family)+1009*pad)
    images=list(range(1,n+1))
    rng.shuffle(images)
    flipped=[False]+[bool(rng.getrandbits(1)) for _ in range(n)]
    remap={old:images[old-1] for old in range(1,n+1)}
    values={abs(lit):lit>0 for lit in assignment}
    transformed_model=[0]*n
    for old in range(1,n+1):
        new=remap[old]
        transformed_model[new-1]=new if (values[old] != flipped[old]) else -new
    rewritten=[]
    for row in rows:
        r=[]
        for lit in row:
            v=abs(lit)
            pos=(lit>0) != flipped[v]
            r.append(remap[v] if pos else -remap[v])
        rng.shuffle(r)
        rewritten.append(r)
    pad_count=(len(rows)*pad+99)//100
    for _ in range(pad_count):
        v=rng.randint(1,n)
        taut=[v,-v]
        rng.shuffle(taut)
        rewritten.append(taut)
    rng.shuffle(rewritten)
    if len(rewritten)!=len(rows)+pad_count:
        raise AssertionError("Tautological padding and source clause counts not exact")
    if not original_model_replay(rewritten,n,transformed_model):
        raise AssertionError("Signed model translation is not SAT-preserving")
    # Source-preserving strict deterministic DIMACS canonical serialization.
    body=("p cnf "+str(n)+" "+str(len(rewritten))+"\n"+
          "".join(" ".join(map(str,r))+" 0\n" for r in rewritten)).encode("ascii")
    return {
        "rows":rewritten,"n":n,"model":transformed_model,"data":body,
        "generated_SHA256":sha256(body).hexdigest(),
        "padding_clauses":pad_count,
        "original_clauses":len(rows),
        "generated_clauses":len(rewritten),
        "permutation_sha256":sha256(json.dumps(images).encode()).hexdigest(),
        "model_SHA256":sha256(json.dumps(transformed_model).encode()).hexdigest()
    }

def materialize(family,pad):
    rows,n,source_sha,model=original_verified(family)
    generated=transform(rows,n,model,family,pad)
    generated["original_SHA256"]=source_sha
    return generated

def single(family,pad,variant,expect_sha):
    if variant not in ("raw_cms",)+VARIANTS:
        raise AssertionError("Unknown fixed method")
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    generated=materialize(family,pad)
    if generated["generated_SHA256"]!=expect_sha:
        raise AssertionError("Cold child generated different prechecked transformed original CNF")
    n=generated["n"]
    with TemporaryDirectory() as directory:
        path=Path(directory)/"case.cnf"
        path.write_bytes(generated["data"])
        shape=scan_dimacs(path)
        if (shape["n_variables"]!=n or
            shape["n_clauses"]!=generated["generated_clauses"] or
            shape["n_literal_occurrences"]!=sum(map(len,generated["rows"]))):
            raise AssertionError("Generated strict DIMACS dimensions not roundtripped")
        rows=read_cnf(path,n,generated["generated_clauses"],max_literals=200000)
    if not original_model_replay(rows,n,generated["model"]):
        raise AssertionError("Full transformed-original SAT assignment fails")
    scanstart=perf_counter()
    form=select_verified_xor(rows,n,variant)
    scanned=perf_counter()-scanstart
    if form["converted_source_clauses"]+len(form["cnf_clauses"])!=len(rows):
        raise AssertionError("Source clauses lost during XOR substructure selection")
    import pycryptosat
    solver=pycryptosat.Solver(threads=1)
    for eq in form["equations"]:
        solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
    for row in form["cnf_clauses"]:
        solver.add_clause(row)
    solving_start=perf_counter()
    sat,values=solver.solve()
    solving_wall=perf_counter()-solving_start
    if sat is True:
        if values is None or len(values)<=n:
            raise AssertionError("Incomplete original transformed SAT model")
        answer=[i if bool(values[i]) else -i for i in range(1,n+1)]
        if not original_model_replay(rows,n,answer):
            raise AssertionError("SAT solver model fails original transformed CNF")
        status=SAT
    elif sat is False:
        raise AssertionError("UNSAT contradicts a fully verified original transformed SAT model")
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {
      "status":status,"family":family,"padding_percent":pad,"variant":variant,
      "original_CNF_SHA256":generated["original_SHA256"],
      "transformed_CNF_SHA256":generated["generated_SHA256"],
      "transformed_full_model_SHA256":generated["model_SHA256"],
      "original_source_clause_count":generated["original_clauses"],
      "added_tautology_clauses":generated["padding_clauses"],
      "transformed_source_clauses":generated["generated_clauses"],
      "source_proven_selected_XOR_count":len(form["equations"]),
      "original_clauses_converted":form["converted_source_clauses"],
      "original_unconverted_clauses":len(form["cnf_clauses"]),
      "source_XOR_scan_status":form["scan_status"],
      "selected_engine":form["choice"],
      "source_XOR_scan_wall_seconds":scanned,
      "native_solver_wall_seconds":solving_wall,
      "full_cold_inner_wall_seconds":perf_counter()-started,
      "full_cold_process_CPU_seconds":process_time(),
      "max_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "full_original_SAT_model_check":"PASS_BEFORE_AND_AFTER",
      "external_independent_Witness":"NOT_APPLICABLE_MUTATED_OLD_PUBLIC",
      "C023_main":"UNCHANGED"
    }

def matrix(family,pad,variant,out):
    preflight()
    generated=materialize(family,pad)
    expected_sha=generated["generated_SHA256"]
    records=[]
    for rep in range(REPEATS):
        order=["candidate","raw_baseline"]
        random.Random(SEED+61*FAMILIES.index(family)+43*pad+31*VARIANTS.index(variant)+rep).shuffle(order)
        for role in order:
            actual=variant if role=="candidate" else "raw_cms"
            before=perf_counter()
            try:
                c=subprocess.run(
                  [sys.executable,str(Path(__file__).resolve()),"--child",
                   "--family",family,"--padding",str(pad),"--variant",actual,
                   "--expected-sha",expected_sha],
                  capture_output=True,text=True,check=False,timeout=WALL)
                if c.returncode:
                    outcome=classify_nonzero_exit(c.returncode)
                    outcome["status"]=outcome.get("verdict","UNREGISTERED_ERROR")
                    outcome["exit_code"]=c.returncode
                    outcome["stderr_tail"]=c.stderr[-600:]
                else:
                    outcome=json.loads(c.stdout)
            except subprocess.TimeoutExpired:
                outcome={"status":"UNKNOWN_WALL_TIMEOUT"}
            records.append({"repeat":rep,"role":role,"method":actual,
                "same_VM_order":order,"full_cold_child_wall_seconds":perf_counter()-before,
                "outcome":outcome})
            print("004E5_TRIAL",family,pad,variant,rep,role,
                  outcome.get("status"),round(records[-1]["full_cold_child_wall_seconds"],3),
                  flush=True)
    allowed={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT",
             "UNKNOWN_SOLVER_NO_ANSWER"}
    if len(records)!=4 or any(x["outcome"].get("status") not in allowed for x in records):
        raise AssertionError("Unexpected original child verdict or missing paired trial")
    for r in records:
        o=r["outcome"]
        if o["status"]==SAT and o["transformed_CNF_SHA256"]!=expected_sha:
            raise AssertionError("Invalid source SHA assigned to original model verified SAT child")
    report={
        "schema":"JANUS-TIME-SAT-004E5-METAMORPHIC-SAME-VM-FROZEN-RECEIPT-V1",
        "scientific_scope":"SIX_DETERMINISTIC_TRANSFORMATIONS_OF_TWO_KNOWN_SAT_INPUTS_NOT_OUT_OF_SAMPLE",
        "frozen_policy_blob":PRE_BLOB,
        "github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "github_head":os.getenv("GITHUB_SHA","LOCAL"),
        "runner_name":os.getenv("RUNNER_NAME","LOCAL"),
        "runner_os":os.getenv("SAT_004E5_OS","LOCAL"),
        "family":family,"padding_percent":pad,"variant":variant,
        "original_CNF_SHA256":generated["original_SHA256"],
        "transformed_CNF_SHA256":expected_sha,
        "transformed_full_model_SHA256":generated["model_SHA256"],
        "source_rewrite_model_preflight":"PASS",
        "expected_cold_children":4,"CPU_soft_s":CPU,"wall_s":WALL,"RLIMIT_AS":MEM,
        "records":records,"no_global_champion":True,
        "outside_independent_Witness":"OPEN","C023_main":"UNCHANGED"
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/(family+"__pad"+str(pad)+"__"+variant+"__"+os.getenv("SAT_004E5_OS","LOCAL")+".json")).write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("004E5_WORKER_SUCCESS",family,pad,variant,"original_model_SAT",
          sum(x["outcome"]["status"]==SAT for x in records),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--child",action="store_true")
    p.add_argument("--family",required=True,choices=FAMILIES)
    p.add_argument("--padding",required=True,type=int,choices=PADS)
    p.add_argument("--variant",required=True,choices=("raw_cms",)+VARIANTS)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--out",type=Path)
    args=p.parse_args()
    if args.child:
        preflight()
        print(json.dumps(single(args.family,args.padding,args.variant,args.expected_sha),
                         sort_keys=True))
    else:
        if args.variant=="raw_cms" or args.out is None:raise SystemExit("Only candidate matrix jobs with --out")
        matrix(args.family,args.padding,args.variant,args.out)
