#!/usr/bin/env python3
"""TIME-SAT-004E12A: falsify UNMODIFIED E11 by SAT-equivalent clause order.

No E11 selector threshold changes. Three transformations preserve exact source
CNF multiset, including exact signed literals, except literal order within OR.
E11's 192-clause source-equivalent prefix XOR proof is used unaltered.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter,process_time

import janus_time_sat_004e11_parity_probe as e

ROOT=Path("experiments/time_sat_004_external")
PLAN=ROOT/"PREREGISTERED_004E12A_CLAUSE_ORDER_20261102.json"
BLOB="fb8cd86ba47c0353f102afe3574ecd02c439ffc3"
IDS=e.IDS
VARIANTS=("as_emitted","global_random_clause_and_literal_shuffle",
          "round_robin_support_masks_and_literal_shuffle")
ARMS=("unaltered_e11_prefix_certified","native_all","raw_cms")
HOSTS=e.HOSTS
REPS=2
CPU=12
WALL=16
MEM=2147483648
BASE_SEED=202611021801
SAT=e.SAT
ALLOWED=e.ALLOWED

def sha(raw):return sha256(raw).hexdigest()

def frozen():
    f=subprocess.run(["git","hash-object",str(PLAN)],check=True,capture_output=True,text=True).stdout.strip()
    if f!=BLOB:raise AssertionError("E12 preregistration changed after freezing")
    p=json.loads(PLAN.read_text())
    b=p["benchmark"]
    if (tuple(x["id"] for x in p["cases"])!=IDS
        or tuple(p["variants"])!=VARIANTS or tuple(p["algorithm_arms"])!=ARMS
        or tuple(b["OS"])!=HOSTS
        or (b["VMs"],b["max_parallel"],b["source_cases"],b["variants_per_source"],
            b["arms"],b["repeats"],b["cold_children"])!=(16,8,8,3,3,2,288)
        or (b["CPU_soft_s"],b["WALL_s"],b["MEM_bytes"])!=(CPU,WALL,MEM)
        or p["E11_original_policy_blob"]!=e.PLAN_BLOB
        or p["original_E9_model_SHA256"]!=e.OLD_MODEL_SHA
        or p["scientific_criteria"]["external_independent_CNF"]!=0):
        raise AssertionError("Unregistered source, threshold, budget, or independence")
    return p

def signature(rows):
    return Counter(tuple(sorted(clause)) for clause in rows)

def transformed(case,variant):
    if case not in IDS or variant not in VARIANTS:
        raise AssertionError("Source or variant not in E12 frozen list")
    p=frozen()
    original=e.source(case)
    base=original["rows"]
    seed=p["cases"][IDS.index(case)]["variant_seed"]
    rng=random.Random(seed+VARIANTS.index(variant)*100003)
    if variant=="as_emitted":
        rows=[list(c) for c in base]
        payload=original["bytes"]
    elif variant=="global_random_clause_and_literal_shuffle":
        rows=[list(c) for c in base]
        for c in rows:rng.shuffle(c)
        rng.shuffle(rows)
        payload=e.original_cnf(original["n"],rows)
    else:
        groups=defaultdict(list)
        for c in base:groups[tuple(sorted(abs(x) for x in c))].append(list(c))
        supports=sorted(groups)
        rng.shuffle(supports)
        for key in supports:
            rng.shuffle(groups[key])
            for c in groups[key]:rng.shuffle(c)
        rows=[]
        for layer in range(max(len(v) for v in groups.values())):
            for key in supports:
                if layer<len(groups[key]):rows.append(groups[key][layer])
        payload=e.original_cnf(original["n"],rows)
    if (signature(rows)!=signature(base) or len(rows)!=original["m"]
        or not e.all_model_ok(rows,original["n"],original["model"])):
        raise AssertionError("Original source multiset or complete SAT model lost")
    if variant=="as_emitted" and sha(payload)!=original["sha"]:
        raise AssertionError("E11 original immutable bytes/hash changed")
    return {**original,"rows":rows,"bytes":payload,
            "sha":sha(payload),"base_SHA256":original["sha"],
            "variant":variant,"source_complete_clause_multiset_preserved":True}

def presolve_lock(out):
    e.frozen()
    p=frozen()
    # Diagnostic pre-outcome preview is fixed and saved BEFORE the worker matrix.
    training=e.frozen_e9_model()
    originals={}
    for case in IDS:
        originals[case]={}
        for variant in VARIANTS:
            s=transformed(case,variant)
            predicted=e.policy(s["rows"],s["n"],"e11_prefix_certified",training)
            originals[case][variant]={
              "original_E11_CNF_SHA256":s["base_SHA256"],
              "transformed_original_CNF_SHA256":s["sha"],
              "full_original_SAT_model_SHA256":s["model_sha"],
              "n":s["n"],"m":s["m"],
              "expected_E11_prefix_choice":predicted["source_only_decision"]["decision"],
              "prefix_original_clause_count":predicted["source_only_decision"]["original_prefix_clauses"],
              "prefix_source_proved_equations":predicted["source_only_decision"]["complete_prefix_source_XOR"],
              "prefix_coverage":predicted["source_only_decision"]["complete_prefix_clause_fraction"],
              "source_complete_clause_multiset_preserved":True}
    fixed={"schema":"JANUS-TIME-SAT-004E12A-PRESOLVE-SOURCE-MODEL-TRANSFORM-PREFIX-LOCK-V1",
      "preregistered_Git_blob":BLOB,"unmodified_E11_policy_blob":e.PLAN_BLOB,
      "prior_E9_training_model_SHA256":e.OLD_MODEL_SHA,
      "sources_and_variant_decisions_preworker":originals,
      "original_CNF_sources":len(IDS),"transformed_original_sources":24,
      "new_independent_external_origins":0,"C023_main":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    b=json.dumps(fixed,sort_keys=True,indent=2)+"\n"
    (out/"SOURCE_LOCK.json").write_text(b)
    (out/"SOURCE_LOCK.sha256").write_text(sha(b.encode())+"  SOURCE_LOCK.json\n")
    choices=Counter(x["expected_E11_prefix_choice"] for v in originals.values() for x in v.values())
    print("004E12A_FROZEN_PERMUTED_SOURCE_LOCK",json.dumps({"sources":24,"E11_preview_decisions":choices,
      "source_lock_SHA256":sha(b.encode())},sort_keys=True))
    return fixed

def checked_lock(path):
    raw=path.read_bytes()
    if path.with_name("SOURCE_LOCK.sha256").read_text().strip()!=sha(raw)+"  SOURCE_LOCK.json":
        raise AssertionError("Wrong original source lock SHA")
    j=json.loads(raw)
    if (j.get("schema")!="JANUS-TIME-SAT-004E12A-PRESOLVE-SOURCE-MODEL-TRANSFORM-PREFIX-LOCK-V1"
        or j.get("preregistered_Git_blob")!=BLOB
        or j.get("unmodified_E11_policy_blob")!=e.PLAN_BLOB
        or j.get("prior_E9_training_model_SHA256")!=e.OLD_MODEL_SHA
        or j.get("transformed_original_sources")!=24
        or set(j.get("sources_and_variant_decisions_preworker",{}))!=set(IDS)
        or j.get("new_independent_external_origins")!=0):
        raise AssertionError("Foreign original source lock")
    return j,sha(raw)

def child(case,variant,arm,lockpath,expected_sha):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    start=perf_counter()
    lock,locksha=checked_lock(lockpath)
    s=transformed(case,variant)
    pinned=lock["sources_and_variant_decisions_preworker"][case][variant]
    if (s["sha"]!=expected_sha or pinned["transformed_original_CNF_SHA256"]!=s["sha"]
       or pinned["original_E11_CNF_SHA256"]!=s["base_SHA256"]
       or pinned["full_original_SAT_model_SHA256"]!=s["model_sha"]):
        raise AssertionError("Original transformed source/model SHA drift")
    with TemporaryDirectory() as d:
        path=Path(d)/"original-transformed-source.cnf"
        path.write_bytes(s["bytes"])
        shape=e.scan_dimacs(path)
        if (shape["n_variables"],shape["n_clauses"],
            shape["n_literal_occurrences"])!=(s["n"],s["m"],sum(len(c) for c in s["rows"])):
            raise AssertionError("Original transformed strict DIMACS parse failed")
        rows=e.read_cnf(path,s["n"],s["m"],max_literals=200000)
    if rows!=s["rows"] or not e.all_model_ok(rows,s["n"],s["model"]):
        raise AssertionError("Presolve full original model proof invalid")
    before=perf_counter()
    if arm=="unaltered_e11_prefix_certified":
        chosen=e.policy(rows,s["n"],"e11_prefix_certified",e.frozen_e9_model())
        if chosen["source_only_decision"]["decision"]!=pinned["expected_E11_prefix_choice"]:
            raise AssertionError("Frozen preworker E11 decision differs")
    elif arm in ("native_all","raw_cms"):
        chosen=e.policy(rows,s["n"],arm,e.frozen_e9_model())
    else:raise AssertionError("Unregistered E12 original method")
    feature_time=perf_counter()-before
    import pycryptosat
    solver=pycryptosat.Solver(threads=1)
    for eq in chosen["equations"]:solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
    for row in chosen["cnf_clauses"]:solver.add_clause(row)
    stamp=perf_counter()
    satisfiable,vector=solver.solve()
    solver_wall=perf_counter()-stamp
    if satisfiable is False:
        raise AssertionError("UNSAT impossible with verified full planted original SAT model")
    if satisfiable is True:
        found=[i if bool(vector[i]) else -i for i in range(1,s["n"]+1)] if vector is not None and len(vector)>s["n"] else None
        if found is None or not e.original_model_replay(rows,s["n"],found):
            raise AssertionError("SAT model fails full exact transformed original CNF")
        status=SAT
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":status,"case":case,"variant":variant,"arm":arm,
      "original_E11_source_SHA256":s["base_SHA256"],
      "transformed_original_CNF_SHA256":s["sha"],
      "original_complete_SAT_model_SHA256":s["model_sha"],
      "original_preworker_SOURCE_LOCK_SHA256":locksha,
      "source_clauses_permutation_equivalence":"EXACT_OR_CLAUSE_MULTISET",
      "E11_policy_source_Git_blob":e.PLAN_BLOB,
      "E9_model_SHA256":e.OLD_MODEL_SHA,
      "actual_representation":chosen["choice"],
      "unmodified_E11_predecision":chosen.get("source_only_decision",{}),
      "selected_source_complete_XOR_equations":len(chosen["equations"]),
      "feature_analysis_wall_s":feature_time,"solver_wall_s":solver_wall,
      "total_inner_cold_wall_s":perf_counter()-start,
      "total_inner_CPU_s":process_time(),
      "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "full_transformed_original_CNF_SAT_model_replay":"PASS",
      "outside_admin_blind":False,"C023_main":"UNCHANGED"}

def matrix(case,lockpath,out):
    frozen()
    lock,locksha=checked_lock(lockpath)
    if case not in IDS:raise AssertionError("Foreign original source case")
    records=[]
    for variant in VARIANTS:
        original=transformed(case,variant)
        if original["sha"]!=lock["sources_and_variant_decisions_preworker"][case][variant]["transformed_original_CNF_SHA256"]:
            raise AssertionError("Original E12 source SHA changed before matrix")
        for rep in (0,1):
            arms=list(ARMS)
            random.Random(BASE_SEED+101*IDS.index(case)+77*VARIANTS.index(variant)+rep).shuffle(arms)
            for arm in arms:
                started=perf_counter()
                cmd=[sys.executable,str(Path(__file__).resolve()),"--child",
                    "--case",case,"--variant",variant,"--arm",arm,
                    "--source-lock",str(lockpath),"--expected-sha",original["sha"]]
                try:
                    r=subprocess.run(cmd,text=True,capture_output=True,timeout=WALL,check=False)
                    if r.returncode:
                        outcome=e.classify_nonzero_exit(r.returncode)
                        outcome["status"]=outcome.get("verdict","UNSUPPORTED_FAIL")
                        outcome["exit_code"]=r.returncode;outcome["stderr_tail"]=r.stderr[-800:]
                    else:outcome=json.loads(r.stdout)
                except subprocess.TimeoutExpired:
                    outcome={"status":"UNKNOWN_WALL_TIMEOUT"}
                records.append({"variant":variant,"repeat":rep,"arm":arm,"shuffled_arm_order":arms,
                    "total_cold_child_wall_s":perf_counter()-started,"outcome":outcome})
                print("004E12A_CHILD",case,variant,rep,arm,outcome.get("status"),
                      round(records[-1]["total_cold_child_wall_s"],4),flush=True)
    if len(records)!=18 or any(x["outcome"].get("status") not in ALLOWED for x in records):
        raise AssertionError("Missing or invalid original child")
    for r in records:
        o=r["outcome"]
        if o["status"]==SAT:
            expected=lock["sources_and_variant_decisions_preworker"][case][r["variant"]]
            if (o["transformed_original_CNF_SHA256"]!=expected["transformed_original_CNF_SHA256"]
                or o["original_complete_SAT_model_SHA256"]!=expected["full_original_SAT_model_SHA256"]
                or o["original_preworker_SOURCE_LOCK_SHA256"]!=locksha
                or o["full_transformed_original_CNF_SAT_model_replay"]!="PASS"):
                raise AssertionError("Original source SAT model evidence missing")
    out.mkdir(parents=True,exist_ok=True)
    result={"schema":"JANUS-TIME-SAT-004E12A-3-CLAUSE-ORDER-18-COLD-ORIGINAL-VM-V1",
        "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "original_HEAD":os.getenv("GITHUB_SHA","LOCAL"),
        "original_runner_ID":os.getenv("RUNNER_NAME","LOCAL"),
        "original_OS":os.getenv("E12_OS","LOCAL"),
        "case":case,"frozen_git_blob":BLOB,"unmodified_E11_policy_blob":e.PLAN_BLOB,
        "original_preworker_source_lock_sha":locksha,
        "original_children":18,"CPU":CPU,"WALL":WALL,"MEM":MEM,
        "external_source_count":0,"C023_main":"UNCHANGED","records":records}
    (out/(case+"__"+os.getenv("E12_OS","LOCAL")+".json")).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004E12A_ORIGINAL_18_CHILD_WORKER_PASS",case,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--child",action="store_true")
    p.add_argument("--case",choices=IDS)
    p.add_argument("--variant",choices=VARIANTS,default="as_emitted")
    p.add_argument("--arm",choices=ARMS,default="unaltered_e11_prefix_certified")
    p.add_argument("--source-lock",type=Path)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--out",type=Path)
    x=p.parse_args()
    if x.preflight:presolve_lock(x.out)
    elif x.child:print(json.dumps(child(x.case,x.variant,x.arm,x.source_lock,x.expected_sha),sort_keys=True))
    else:matrix(x.case,x.source_lock,x.out)
