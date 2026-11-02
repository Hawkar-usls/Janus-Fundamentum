#!/usr/bin/env python3
"""JANUS TIME-SAT-004E8: model-first, four-category, five-arm full cold cost.

Two exact archived PUBLIC model-verified CNF instances plus six synthetic,
fully planted SAT instances. Synthetic instances are NOT external benchmarks.
All source and model generation is frozen by manifest and seed before CI.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter,process_time

from janus_time_sat_004e5_metamorphic import original_verified
from janus_time_sat_004e6_semantic_selector import normalized_selector
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d4b_real_pilot import original_model_replay

ROOT=Path("experiments/time_sat_004_external")
FROZEN=ROOT/"PREREGISTERED_004E8_SAT_MODEL_FIRST_COST_20261102.json"
FROZEN_BLOB="220f9d867b2355523b134dc86fe816b74a177e5d"
IDS=("public-lightsout-625","public-binary-tree-1023",
     "planted-3sat-n96","planted-3sat-n160","planted-3sat-n224",
     "mixed-planted-xor-n96","mixed-planted-xor-n160","mixed-planted-xor-n224")
ARMS=("new_semantic80","native_all","noop_normalize_then_raw_cms",
      "raw_cms","cadical195_original")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
CPU=12
WALL=16
MEM=2147483648
REPEATS=2
SEED=20261102088
ALLOW={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}

def freeze():
    actual=subprocess.run(["git","hash-object",str(FROZEN)],capture_output=True,
                          text=True,check=True).stdout.strip()
    if actual!=FROZEN_BLOB:raise AssertionError("004E8 immutable prereg Git blob drift")
    manifest=json.loads(FROZEN.read_text())
    d=manifest["budget"]
    if (tuple(x["id"] for x in manifest["cases"])!=IDS
        or tuple(manifest["arms"])!=ARMS
        or tuple(d["host_images"])!=HOSTS
        or (d["matrix_jobs"],d["cases"],d["arms"],d["repeats"],d["total_cold_children"])!=(16,8,5,2,160)
        or (d["CPU_soft_s"],d["WALL_timeout_s"],d["RLIMIT_AS_bytes"],d["order_seed"])!=(CPU,WALL,MEM,SEED)
        or manifest["scope"]["new_external_blinded_CNF_cases"]!=0
        or manifest["scope"]["C023_main"]!="UNCHANGED"):
        raise AssertionError("004E8 registered original/source/CPU/arm policy changed")
    return manifest

def cnf_bytes(n,rows):
    return ("p cnf "+str(n)+" "+str(len(rows))+"\n"+
            "".join(" ".join(map(str,c))+" 0\n" for c in rows)).encode("ascii")

def planted_clause(rng,n,assignment):
    v=sorted(rng.sample(range(1,n+1),3))
    signs=[rng.getrandbits(1) for _ in v]
    c=tuple(x if sign else -x for x,sign in zip(v,signs))
    if not any((lit>0)==assignment[abs(lit)] for lit in c):
        return None
    return c

def synth(case):
    n=case["n"]
    rng=random.Random(case["seed"])
    assignment={v:bool(rng.getrandbits(1)) for v in range(1,n+1)}
    complete=[v if assignment[v] else -v for v in range(1,n+1)]
    rows=[];seen=set()
    xor_equations=case.get("xor3_equations",0)
    supports=set()
    while len(supports)<xor_equations:
        support=tuple(sorted(rng.sample(range(1,n+1),3)))
        if support in supports:continue
        supports.add(support)
        rhs=sum(assignment[v] for v in support)%2
        for values in product((0,1),repeat=3):
            if sum(values)%2==rhs:continue
            clause=tuple(v if not bit else -v for v,bit in zip(support,values))
            if clause in seen:raise AssertionError("Duplicated exact original XOR mask")
            seen.add(clause)
            rows.append(list(clause))
    desired=case.get("requested_3cnf",case.get("added_3cnf"))
    if not isinstance(desired,int) or desired<1:raise AssertionError("Invalid planted clause count")
    added=0
    for _ in range(desired*60):
        if added==desired:break
        c=planted_clause(rng,n,assignment)
        if c is None or c in seen:continue
        seen.add(c);rows.append(list(c));added+=1
    if added!=desired:raise AssertionError("No unique planted SAT 3-clauses within bounded attempts")
    rng.shuffle(rows)
    if any(len(c)!=3 or len({abs(x) for x in c})!=3 for c in rows):
        raise AssertionError("Invalid original planted 3-clause")
    if case.get("expected_m",len(rows))!=len(rows):
        raise AssertionError("Precommitted source size mismatch")
    if not original_model_replay(rows,n,complete):
        raise AssertionError("Constructed original does not satisfy planted full model")
    return rows,n,complete

def source(case_id):
    if case_id not in IDS:raise AssertionError("Unregistered original source")
    case=freeze()["cases"][IDS.index(case_id)]
    if case["kind"]=="KNOWN_PUBLIC_ORIGINAL_SAT":
        public_family=case["family"]
        rows,n,sha,model=original_verified(public_family)
        if (sha,n,len(rows))!=(case["source_sha256"],case["n"],case["m"]):
            raise AssertionError("Archived original competition source SHA or shape changed")
        provenance="PRESEEN_PUBLIC_COMPETITION_SOURCE"
    elif case["kind"]=="SYNTHETIC_PLANTED_SAT":
        rows,n,model=synth(case)
        sha=sha256(cnf_bytes(n,rows)).hexdigest()
        provenance="OPEN_GENERATOR_PLANTED_SAT_NOT_EXTERNAL"
    else:raise AssertionError("Unregistered SAT source class")
    if (len(model)!=n or {abs(x) for x in model}!=set(range(1,n+1))
        or not original_model_replay(rows,n,model)):
        raise AssertionError("Original pre-solve full SAT model is invalid")
    payload=cnf_bytes(n,rows)
    return {"id":case_id,"family":case["family"],"provenance":provenance,
            "n":n,"rows":rows,"m":len(rows),"sha":sha,"bytes":payload,
            "model":model,"model_sha":sha256(json.dumps(model).encode()).hexdigest(),
            "generator":"PUBLIC_EXACT_ARCHIVE" if case["kind"]=="KNOWN_PUBLIC_ORIGINAL_SAT"
                          else "PLANTED_SEEDED_3CNF_EXACT_XOR_V1"}

def choose(rows,n,arm):
    if arm=="cadical195_original":
        return {"equations":[],"cnf_clauses":rows,"choice":"cadical195_original",
                "metric":{"normalization":"NO_FEATURE_SCAN"}}
    if arm=="noop_normalize_then_raw_cms":
        same=normalized_selector(rows,n,"new_semantic80")
        return {"equations":[],"cnf_clauses":rows,"choice":"NOOP_SCANNED_ORIGINAL_RAW",
                "metric":{"normalization":"FULL_SCAN_PERFORMED_THEN_DISCARDED",
                          "prior_scan_fraction":same["metric"].get("fraction"),
                          "prior_XOR_equations":len(same["equations"])}}
    return normalized_selector(rows,n,arm)

def child(case_id,arm,expect_sha,expect_model_sha):
    if arm not in ARMS:raise AssertionError("Unregistered 004E8 method")
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    a=source(case_id)
    if (a["sha"],a["model_sha"])!=(expect_sha,expect_model_sha):
        raise AssertionError("Original SHA or full SAT assignment changed in child")
    with TemporaryDirectory() as t:
        p=Path(t)/"original.cnf"
        p.write_bytes(a["bytes"])
        d=scan_dimacs(p)
        if (d["n_variables"],d["n_clauses"],d["n_literal_occurrences"])!=(
            a["n"],a["m"],sum(map(len,a["rows"]))):
            raise AssertionError("Original CNF malformed on disk")
        rows=read_cnf(p,a["n"],a["m"],max_literals=200000)
    if rows!=a["rows"] or not original_model_replay(rows,a["n"],a["model"]):
        raise AssertionError("Original pre-solve SAT model or DIMACS replay mismatch")
    stamp=perf_counter()
    chosen=choose(rows,a["n"],arm)
    features_time=perf_counter()-stamp
    solver_setup=perf_counter()
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as slv:
            setup=perf_counter()-solver_setup
            before=perf_counter()
            sat=slv.solve()
            solve_s=perf_counter()-before
            solution=slv.get_model() if sat is True else None
    else:
        import pycryptosat
        slv=pycryptosat.Solver(threads=1)
        for eq in chosen["equations"]:
            slv.add_xor_clause(eq["variables"],bool(eq["rhs"]))
        for clause in chosen["cnf_clauses"]:slv.add_clause(clause)
        setup=perf_counter()-solver_setup
        before=perf_counter()
        sat,ans=slv.solve()
        solve_s=perf_counter()-before
        solution=[i if bool(ans[i]) else -i for i in range(1,a["n"]+1)] if (
            sat is True and ans is not None and len(ans)>a["n"]) else None
    if sat is True:
        if solution is None or not original_model_replay(rows,a["n"],solution):
            raise AssertionError("Returned solver model does not satisfy full exact original CNF")
        status=SAT
    elif sat is False:
        raise AssertionError("UNSAT on source with independently pre-replayed COMPLETE SAT assignment")
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":status,"case":case_id,"family":a["family"],"arm":arm,
            "source_provenance":a["provenance"],"source_original_CNF_SHA256":a["sha"],
            "source_complete_model_SHA256":a["model_sha"],"source_variables":a["n"],
            "source_clauses":a["m"],"candidate_representation":chosen["choice"],
            "selected_XOR_equations":len(chosen["equations"]),
            "feature_selection_wall_seconds":features_time,"solver_setup_wall_seconds":setup,
            "solver_wall_seconds":solve_s,"cold_inner_wall_seconds":perf_counter()-started,
            "cold_child_CPU_seconds":process_time(),
            "max_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "original_full_SAT_model_pre_and_post":"PASS",
            "actual_external_hidden":False,"global_champion":"NOT_ADMITTED",
            "production_C023":"UNCHANGED"}

def matrix(case_id,out):
    freeze()
    original=source(case_id)
    records=[]
    for rep in range(REPEATS):
        order=list(ARMS)
        random.Random(SEED+41*IDS.index(case_id)+rep).shuffle(order)
        for arm in order:
            start=perf_counter()
            command=[sys.executable,str(Path(__file__).resolve()),"--child",
                     "--case",case_id,"--arm",arm,
                     "--expected-sha",original["sha"],
                     "--expected-model-sha",original["model_sha"]]
            try:
                r=subprocess.run(command,text=True,capture_output=True,check=False,timeout=WALL)
                if r.returncode:
                    verdict=classify_nonzero_exit(r.returncode)
                    verdict["status"]=verdict.get("verdict","UNRECOGNIZED")
                    verdict["exit_code"]=r.returncode
                    verdict["stderr_tail"]=r.stderr[-500:]
                else:verdict=json.loads(r.stdout)
            except subprocess.TimeoutExpired:
                verdict={"status":"UNKNOWN_WALL_TIMEOUT"}
            records.append({"repeat":rep,"arm":arm,"shuffled_order":order,
                           "full_cold_child_wall_seconds":perf_counter()-start,"outcome":verdict})
            print("004E8_TRIAL",case_id,rep,arm,verdict.get("status"),
                  round(records[-1]["full_cold_child_wall_seconds"],4),flush=True)
    if len(records)!=10 or any(x["outcome"].get("status") not in ALLOW for x in records):
        raise AssertionError("Original child was missing or failed outside allowed scientific statuses")
    for x in records:
        o=x["outcome"]
        if o["status"]==SAT and (o["source_original_CNF_SHA256"]!=original["sha"]
            or o["source_complete_model_SHA256"]!=original["model_sha"]
            or o["original_full_SAT_model_pre_and_post"]!="PASS"):
            raise AssertionError("Original source SHA/model receipt cannot be verified")
    output={"schema":"JANUS-TIME-SAT-004E8-EIGHT-CASE-FIVE-ARM-COLD-PAIR-VM-V1",
      "scope":"2_PRESEEN_PUBLIC_6_SYNTHETIC_PLANTED_NO_INDEPENDENT_HOLDOUT",
      "frozen_manifest_blob":FROZEN_BLOB,
      "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
      "original_head":os.getenv("GITHUB_SHA","LOCAL"),
      "original_runner_name":os.getenv("RUNNER_NAME","LOCAL"),
      "original_ubuntu":os.getenv("SAT_004E8_OS","LOCAL"),
      "case_id":case_id,"source_family":original["family"],
      "original_source_sha256":original["sha"],
      "original_complete_model_sha256":original["model_sha"],
      "source_kind":original["provenance"],
      "original_n":original["n"],"original_m":original["m"],
      "source_model_verified_preflight":True,
      "original_cold_children":10,"CPU_soft_s":CPU,"WALL_s":WALL,
      "RLIMIT_AS":MEM,"records":records,
      "no_global_champion":True,"new_hidden_sources":0,
      "production_C023":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    (out/(case_id+"__"+os.getenv("SAT_004E8_OS","LOCAL")+".json")).write_text(
        json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("004E8_MATRIX_COMPLETED",case_id,"SAT",
          sum(x["outcome"]["status"]==SAT for x in records),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--child",action="store_true")
    p.add_argument("--case",required=True,choices=IDS)
    p.add_argument("--arm",choices=ARMS,default="new_semantic80")
    p.add_argument("--out",type=Path)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--expected-model-sha",default="")
    a=p.parse_args()
    if a.child:
        freeze()
        print(json.dumps(child(a.case,a.arm,a.expected_sha,a.expected_model_sha),sort_keys=True))
    else:
        if a.out is None:raise SystemExit("Missing --out for fixed full-cohort benchmark")
        matrix(a.case,a.out)
