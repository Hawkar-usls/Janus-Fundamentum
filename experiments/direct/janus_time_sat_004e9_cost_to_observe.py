#!/usr/bin/env python3
"""JANUS 004E9: cost-to-observe selection trained ONLY on prior 004E8 source results.

Eight E8 original CNFs supply exactly EIGHT training groups; four repetitions
of one source NEVER count as distinct training samples. All E9 validation data
are generated with frozen seeds BEFORE training artifact is made and before
validation VMs launch. New seeds use same planted generator, NOT external data.
Public regressions overlap E8 training, do NOT call them held-out.

Algorithm deliberately simple and auditable:
  cheap first-128-clause width/count fingerprint + nearest archived E8 source;
  if positive outcome's full-cold RAW/NATIVE advantage >=20% or native completed
  despite all raw controls CPU-censored, and distance <=1.75, scan and use only
  independently source-proven native XOR. Otherwise SKIP expensive scan -> raw.
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
import statistics

from janus_time_sat_004e8_model_first import (
    source as e8source,synth as e8synth,cnf_bytes,choose as e8choose,
    SAT,ALLOW,original_model_replay,scan_dimacs,read_cnf,classify_nonzero_exit
)
from janus_time_sat_004e6_semantic_selector import normalized_selector

ROOT=Path("experiments/time_sat_004_external")
PLAN=ROOT/"PREREGISTERED_004E9_E8_TRAIN_NEW_SEED_VALIDATION_20261102.json"
PLAN_BLOB="58d7e035895865cc596ac925154d843876df8427"
E8_SUMMARY=ROOT/"time_sat_004e8_evidence/SUMMARY.json"
E8_SUMMARY_BLOB="2f7c00617e59b8f83058d0eadb4ffc5b414616c4"
E8_RECEIPTS=ROOT/"time_sat_004e8_evidence/original-worker-JSON"
HOSTS=("ubuntu-22.04","ubuntu-24.04")
ARMS=("cost_nearest","semantic80","native_all","raw_cms","cadical195_original")
REPS=2
CPU=12
WALL=16
MEM=2147483648
SEED=20261102089
PUBLIC=("public-lightsout-625","public-binary-tree-1023")
NEW=("e9-planted-3sat-n128","e9-planted-3sat-n192","e9-planted-3sat-n256",
     "e9-mixed-planted-xor-n128","e9-mixed-planted-xor-n192","e9-mixed-planted-xor-n256")
IDS=PUBLIC+NEW
TRAIN=("public-lightsout-625","public-binary-tree-1023",
       "planted-3sat-n96","planted-3sat-n160","planted-3sat-n224",
       "mixed-planted-xor-n96","mixed-planted-xor-n160","mixed-planted-xor-n224")
DISTANCE_MAX=1.75
MIN_RAW_OVER_NATIVE_RATIO=1.20
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}

def git_blob(path):
    return subprocess.run(["git","hash-object",str(path)],capture_output=True,
        text=True,check=True).stdout.strip()

def frozen():
    if git_blob(PLAN)!=PLAN_BLOB:raise AssertionError("E9 frozen protocol tampered")
    p=json.loads(PLAN.read_text())
    d=p["validation_budget"]
    if (tuple(p["E8_training_case_ids"])!=TRAIN
       or tuple(x["id"] for x in p["validation_sources"])!=IDS
       or tuple(d["ubuntu"])!=HOSTS or tuple(d["methods"])!=ARMS
       or (d["original_GitHub_VM_jobs"],d["maximum_simultaneous_jobs"],
           d["cold_children"],d["repeats_per_method_each_VM"])!=(16,8,160,REPS)
       or (d["CPU_soft_seconds"],d["wall_timeout_seconds"],
           d["virtual_memory_bytes"])!=(CPU,WALL,MEM)
       or p["E8_scientific_run"]!=41454451078
       or p["E8_scientific_HEAD"]!="f58576a34f0f51bbeb99fd2d93e7bf160d2914f1"):
        raise AssertionError("E9 scientific train/test source, score or CPU contract altered")
    return p

def fingerprint(rows,n):
    """Source-only cheap, deterministic; use no solved SAT labels or future data."""
    if n<1 or not rows:raise AssertionError("Invalid source for low-cost feature probe")
    prefix=rows[:min(len(rows),128)]
    widths=[len(set(abs(l) for l in c)) for c in prefix]
    if any(w==0 for w in widths):raise AssertionError("Unexpected empty prefix source clause")
    m=len(rows)
    return [math.log2(n),math.log2(m),
            sum(widths)/len(widths),
            sum(x==3 for x in widths)/len(widths),
            math.log2(m/n)]

def distance(a,b):
    if len(a)!=5 or len(b)!=5:raise AssertionError("Wrong fixed feature count")
    weights=(1.0,0.8,1.5,1.0,0.4)
    return sum(w*abs(x-y) for w,x,y in zip(weights,a,b))

def observed_training_model():
    """Group source outcomes before labeling; E8 original bytes are SHA-bound."""
    p=frozen()
    if git_blob(E8_SUMMARY)!=E8_SUMMARY_BLOB:
        raise AssertionError("E8 source archive SHA changed after E9 prereg")
    sys.path.insert(0,str(ROOT))  # Prior E8 audit lives in adjacent original-archive module directory
    from janus_time_sat_004e8_audit import audit as old_audit
    a=old_audit(E8_RECEIPTS)
    if (a["source_scientific_run_id"]!="41454451078"
        or a["source_scientific_head"]!=p["E8_scientific_HEAD"]
        or a["original_children"]!=160 or a["original_workers"]!=16):
        raise AssertionError("E8 archived source/auditor cohorts cannot train")
    archived=json.loads(E8_SUMMARY.read_text())
    if archived["recomputed_audit"]!=a:
        raise AssertionError("E8 original auditor differs from fully replayed training artifact")
    entries=[]
    for case in TRAIN:
        original=e8source(case)
        rows=original["rows"]
        native=[]
        raw=[]
        paired=[]
        for osname in HOSTS:
            record=json.loads((E8_RECEIPTS/(case+"__"+osname+".json")).read_text())
            if (record["original_source_sha256"]!=original["sha"]
               or record["original_complete_model_sha256"]!=original["model_sha"]):
                raise AssertionError("E8 trained source/model SHA mismatch")
            for rep in (0,1):
                n=next(r for r in record["records"] if r["repeat"]==rep and r["arm"]=="native_all")
                q=next(r for r in record["records"] if r["repeat"]==rep and r["arm"]=="raw_cms")
                for x in (n,q):
                    if x["outcome"]["status"] not in ALLOWED:
                        raise AssertionError("E8 unknown prior child status")
                native.append(n);raw.append(q)
                if n["outcome"]["status"]==q["outcome"]["status"]==SAT:
                    paired.append(q["full_cold_child_wall_seconds"]/n["full_cold_child_wall_seconds"])
        ns=sum(r["outcome"]["status"]==SAT for r in native)
        rs=sum(r["outcome"]["status"]==SAT for r in raw)
        if ns==4 and rs<4 and all(r["outcome"]["status"] in
                                  {SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT"}
                                  for r in raw):
            label="XOR"
            why="NATIVE_VERIFIED_4_OF_4_RAW_CENSORED"
        elif ns==rs==4 and len(paired)==4 and statistics.median(paired)>=MIN_RAW_OVER_NATIVE_RATIO:
            label="XOR"
            why="NATIVE_FULL_COLD_PAIR_MEDIAN_OVER_20PCT"
        else:
            label="RAW"
            why="NO_PRIOR_FULL_COLD_NET_PROFIT_EVIDENCE"
        entries.append({
            "training_source_SHA256":original["sha"],
            "original_source_group":case,
            "fingerprint":fingerprint(rows,original["n"]),
            "original_FULL_COLD_native_verified_SAT":ns,
            "original_FULL_COLD_raw_verified_SAT":rs,
            "completed_same_VM_pair_count":len(paired),
            "prior_completed_pair_raw_over_native_median":statistics.median(paired) if paired else None,
            "label":label,"rationale":why
        })
    if len({x["training_source_SHA256"] for x in entries})!=8:
        raise AssertionError("Cannot treat duplicate source SHAs as independent groups")
    return entries,a

def validation_source(case):
    p=frozen()
    item=next((x for x in p["validation_sources"] if x["id"]==case),None)
    if item is None:raise AssertionError("Foreign validation case")
    if case in PUBLIC:
        original=e8source(case)
        if original["sha"]!=item["source_sha256"]:
            raise AssertionError("Prior public SAT source SHA lost")
        return original
    rows,n,model=e8synth(item)
    if n!=item["n"] or len(rows)!=item["expected_m"]:
        raise AssertionError("New E9 planted deterministic source shape mismatch")
    payload=cnf_bytes(n,rows)
    source_hash=sha256(payload).hexdigest()
    model_hash=sha256(json.dumps(model).encode()).hexdigest()
    if not original_model_replay(rows,n,model):
        raise AssertionError("New generated source full planted SAT model invalid")
    return {"id":case,"family":"SYNTHETIC_NEW_SEED_SAME_GENERATOR",
            "provenance":"SYNTHETIC_SEED_NOT_EXTERNAL",
            "n":n,"rows":rows,"m":len(rows),"sha":source_hash,
            "bytes":payload,"model":model,"model_sha":model_hash,
            "generator":"E8_SAME_GENERATOR_NEW_PREREG_SEED"}

def create_model(out):
    train,a=observed_training_model()
    sources={case:validation_source(case) for case in IDS}
    if len({x["sha"] for x in sources.values()})!=8:
        raise AssertionError("Two validation source IDs collide by identical source SHA")
    model={
      "schema":"JANUS-TIME-SAT-004E9-E8-TRAIN-FROZEN-COST-TO-OBSERVE-KNN-V1",
      "source_training_run":41454451078,
      "source_training_head":"f58576a34f0f51bbeb99fd2d93e7bf160d2914f1",
      "frozen_protocol_git_blob":PLAN_BLOB,
      "prior_E8_original_source_summary_blob":E8_SUMMARY_BLOB,
      "original_E8_case_groups":8,
      "original_E8_vm_repeats_NOT_independent":32,
      "training_entries":train,
      "new_seed_validation_source_ids":list(NEW),
      "training_overlap_regression_source_ids":list(PUBLIC),
      "validation_sources_precommitted_before_matrix":{
         case:{"source_SHA256":s["sha"],"complete_SAT_model_SHA256":s["model_sha"],
               "n":s["n"],"m":s["m"],
               "source_kind":s["provenance"]}
         for case,s in sources.items()},
      "feature": "first128 CNF source clauses plus n/m, no SAT label at inference",
      "distance_max":DISTANCE_MAX,
      "positive_label_requires_full_cold_speedup_factor":MIN_RAW_OVER_NATIVE_RATIO,
      "fallback": "SKIP_NORMALIZATION_SCAN_AND_SOLVE_RAW_ORIGINAL",
      "XOR_only_if":"EXACT_ORIGINAL_SOURCE_COMPLETE_PARITY_GROUPS_VALIDATED",
      "selection_only_development":True,
      "no_external_blinded_source_claim":True,
      "no_auto_champion_promotion":True,
      "E8_original_audit_status":a["status"],
      "C023_main":"UNCHANGED"
    }
    out.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(model,sort_keys=True,indent=2)+"\n"
    (out/"MODEL.json").write_text(raw)
    (out/"MODEL.sha256").write_text(sha256(raw.encode()).hexdigest()+"  MODEL.json\n")
    print("004E9_TRAINING_MODEL_FROZEN_BEFORE_VALIDATION",json.dumps({
       "sources":8,"positive_labels":[x["original_source_group"] for x in train if x["label"]=="XOR"],
       "new_seed_val":len(NEW),"model_SHA256":sha256(raw.encode()).hexdigest()},sort_keys=True))
    return model

def checked_model(path):
    p=frozen()
    raw=path.read_bytes()
    sha_path=path.with_name("MODEL.sha256")
    line=sha_path.read_text().strip()
    if line!=sha256(raw).hexdigest()+"  MODEL.json":
        raise AssertionError("Model artifact SHA mismatch before any validation solve")
    model=json.loads(raw)
    if (model["schema"]!="JANUS-TIME-SAT-004E9-E8-TRAIN-FROZEN-COST-TO-OBSERVE-KNN-V1"
        or model["frozen_protocol_git_blob"]!=PLAN_BLOB
        or model["source_training_run"]!=41454451078
        or len(model["training_entries"])!=8
        or len(model["validation_sources_precommitted_before_matrix"])!=8
        or model["distance_max"]!=DISTANCE_MAX
        or model["positive_label_requires_full_cold_speedup_factor"]!=MIN_RAW_OVER_NATIVE_RATIO):
        raise AssertionError("Wrong version/parameters or cohort of E9 pretrained model")
    return model,sha256(raw).hexdigest()

def policy(rows,n,arm,model):
    if arm not in ARMS:raise AssertionError("Unknown method")
    if arm=="cost_nearest":
        feat=fingerprint(rows,n)
        entry=min(model["training_entries"],key=lambda r:(distance(feat,r["fingerprint"]),r["original_source_group"]))
        d=distance(feat,entry["fingerprint"])
        confident=d<=DISTANCE_MAX and entry["label"]=="XOR" and entry["original_FULL_COLD_native_verified_SAT"]==4
        if confident:
            choice=normalized_selector(rows,n,"native_all")
            return {**choice,"cost_prediction":{
                 "choose":"NATIVE_SOURCE_XOR" if choice["choice"]=="native_xor" else "RAW_SAFE_FALLBACK",
                 "nearest_training_original_group":entry["original_source_group"],
                 "cheap_distance":d,"training_label":entry["label"],
                 "inference_features":feat,"expensive_XOR_scan_performed":True}}
        return {"equations":[],"cnf_clauses":rows,"choice":"raw_without_expensive_scan",
                "metric":{"normalization":"SKIPPED_EXPENSIVE_SCAN","selected":0},
                "cost_prediction":{"choose":"SKIP_SCAN_RAW","nearest_training_original_group":entry["original_source_group"],
                 "cheap_distance":d,"training_label":entry["label"],
                 "inference_features":feat,"expensive_XOR_scan_performed":False}}
    if arm=="semantic80":return normalized_selector(rows,n,"new_semantic80")
    if arm=="native_all":return normalized_selector(rows,n,"native_all")
    if arm=="raw_cms":return normalized_selector(rows,n,"raw_cms")
    return {"equations":[],"cnf_clauses":rows,"choice":"cadical195_original","metric":{"normalization":"NO_SCAN"}}

def child(case,arm,modelpath,expected_sha,expected_model):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    start=perf_counter()
    model,modelsha=checked_model(modelpath)
    src=validation_source(case)
    if (src["sha"],src["model_sha"])!=(expected_sha,expected_model):
        raise AssertionError("Validation SAT source/model SHA changed from preflight artifact")
    expected_entry=model["validation_sources_precommitted_before_matrix"][case]
    if (src["sha"],src["model_sha"])!=(
        expected_entry["source_SHA256"],expected_entry["complete_SAT_model_SHA256"]):
        raise AssertionError("Cross-worker validation original source SHA differs from frozen preflight")
    with TemporaryDirectory() as t:
        path=Path(t)/"original.cnf"
        path.write_bytes(src["bytes"])
        shape=scan_dimacs(path)
        if (shape["n_variables"],shape["n_clauses"],
             shape["n_literal_occurrences"])!=(src["n"],src["m"],sum(map(len,src["rows"]))):
            raise AssertionError("Strict E9 original source DIMACS shape changed")
        rows=read_cnf(path,src["n"],src["m"],max_literals=200000)
    if rows!=src["rows"] or not original_model_replay(rows,src["n"],src["model"]):
        raise AssertionError("Pre-solve original full SAT model replay failed")
    before=perf_counter()
    selected=policy(rows,src["n"],arm,model)
    select_wall=perf_counter()-before
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as solver:
            stamp=perf_counter()
            sat=solver.solve()
            solving=perf_counter()-stamp
            answer=solver.get_model() if sat is True else None
    else:
        import pycryptosat
        solver=pycryptosat.Solver(threads=1)
        for eq in selected["equations"]:
            solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
        for clause in selected["cnf_clauses"]:solver.add_clause(clause)
        stamp=perf_counter()
        sat,vector=solver.solve()
        solving=perf_counter()-stamp
        answer=([i if bool(vector[i]) else -i for i in range(1,src["n"]+1)]
             if sat is True and vector is not None and len(vector)>src["n"] else None)
    if sat is True:
        if answer is None or not original_model_replay(rows,src["n"],answer):
            raise AssertionError("Returned SAT model violates ORIGINAL source CNF")
        status=SAT
    elif sat is False:
        raise AssertionError("UNSAT impossible on source with verified complete SAT model")
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":status,"case":case,"arm":arm,
        "source_original_CNF_SHA256":src["sha"],"source_full_model_SHA256":src["model_sha"],
        "trained_model_SHA256":modelsha,"source_kind":src["provenance"],
        "feature_observation_and_selection_wall_s":select_wall,
        "solver_wall_seconds":solving,
        "full_cold_inner_wall_s":perf_counter()-start,
        "full_cold_CPU_seconds":process_time(),
        "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "selected_original_XOR_equations":len(selected["equations"]),
        "effective_representation":selected["choice"],
        "predecision_prediction":selected.get("cost_prediction",{}),
        "source_original_model_pre_and_post":"PASS",
        "independent_external_custodian":"NOT_PRESENT",
        "main_C023":"UNCHANGED"}

def matrix(case,out,modelpath):
    frozen()
    model,modelsha=checked_model(modelpath)
    src=validation_source(case)
    records=[]
    for rep in range(REPS):
        order=list(ARMS)
        random.Random(SEED+43*IDS.index(case)+rep).shuffle(order)
        for arm in order:
            begin=perf_counter()
            cmd=[sys.executable,str(Path(__file__).resolve()),"--child","--case",case,
                 "--arm",arm,"--model",str(modelpath),
                 "--expected-sha",src["sha"],"--expected-model",src["model_sha"]]
            try:
                result=subprocess.run(cmd,capture_output=True,text=True,check=False,timeout=WALL)
                if result.returncode:
                    o=classify_nonzero_exit(result.returncode)
                    o["status"]=o.get("verdict","UNREGISTERED")
                    o["returncode"]=result.returncode
                    o["stderr_tail"]=result.stderr[-700:]
                else:o=json.loads(result.stdout)
            except subprocess.TimeoutExpired:o={"status":"UNKNOWN_WALL_TIMEOUT"}
            records.append({"repeat":rep,"arm":arm,"shuffled_order":order,
                "full_cold_child_wall_seconds":perf_counter()-begin,"outcome":o})
            print("004E9_CHILD",case,rep,arm,o.get("status"),
                  round(records[-1]["full_cold_child_wall_seconds"],4),flush=True)
    if len(records)!=10 or any(r["outcome"].get("status") not in ALLOWED for r in records):
        raise AssertionError("Unknown source solver error or missing E9 child")
    for r in records:
        o=r["outcome"]
        if o["status"]==SAT and (
           o["source_original_CNF_SHA256"]!=src["sha"]
           or o["source_full_model_SHA256"]!=src["model_sha"]
           or o["trained_model_SHA256"]!=modelsha
           or o["source_original_model_pre_and_post"]!="PASS"):
            raise AssertionError("Not an original-source verified SAT model")
    receipt={"schema":"JANUS-TIME-SAT-004E9-SOURCE-BOUND-COST-KNN-FIVE-ARM-COLD-VM-V1",
        "cohort_type":"E8_TRAIN_NEW_SEED_VALIDATION_SAME_INTERNAL_GENERATOR_PLUS_PRESEEN_PUBLIC_REGRESSION",
        "E8_training_original_run":41454451078,
        "frozen_git_blob":PLAN_BLOB,
        "trained_model_SHA256":modelsha,
        "source_training_overlap":case in PUBLIC,
        "github_run_id":os.environ.get("GITHUB_RUN_ID","LOCAL"),
        "original_head":os.environ.get("GITHUB_SHA","LOCAL"),
        "runner_name":os.environ.get("RUNNER_NAME","LOCAL"),
        "runner_OS":os.environ.get("SAT_004E9_OS","LOCAL"),
        "case":case,"original_CNF_SHA256":src["sha"],
        "original_complete_SAT_model_SHA256":src["model_sha"],
        "source_kind":src["provenance"],
        "CPU_soft_s":CPU,"WALL_s":WALL,"RLIMIT_AS_bytes":MEM,
        "repetitions":REPS,"cold_children":10,"records":records,
        "no_global_champion":True,"outside_004C_Witness":"OPEN","C023_main":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    (out/(case+"__"+os.environ.get("SAT_004E9_OS","LOCAL")+".json")).write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("004E9_JOB_COMPLETED",case,"SAT",
       sum(x["outcome"]["status"]==SAT for x in records),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--train",action="store_true")
    ap.add_argument("--out",type=Path)
    ap.add_argument("--child",action="store_true")
    ap.add_argument("--case",choices=IDS)
    ap.add_argument("--arm",choices=ARMS,default="cost_nearest")
    ap.add_argument("--model",type=Path)
    ap.add_argument("--expected-sha",default="")
    ap.add_argument("--expected-model",default="")
    x=ap.parse_args()
    if x.train:
        if x.out is None:raise SystemExit("--out needed for training artifacts")
        create_model(x.out)
    elif x.child:
        if x.model is None or x.case is None:raise SystemExit("--model/--case required")
        frozen()
        print(json.dumps(child(x.case,x.arm,x.model,x.expected_sha,x.expected_model),sort_keys=True))
    else:
        if x.out is None or x.case is None or x.model is None:
            raise SystemExit("--out, --case, --model required")
        matrix(x.case,x.out,x.model)
