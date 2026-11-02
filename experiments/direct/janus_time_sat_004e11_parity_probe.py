#!/usr/bin/env python3
"""004E11: strictly precommitted SAT-equivalent new parity topologies + two old controls.

Eight original CNFs only, three JANUS-owned SYNTHETIC parity generator
families, six new source SHA and complete models locked before any worker.
Tests one new conservative source-only prefix XOR certificate probe against
previous E9/E10, existing source-proved native, raw CMS and CaDiCaL.
NEVER claim these formulae are externally withheld/independent.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import itertools
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter,process_time

from janus_time_sat_004e10_ood import (
    model as frozen_e9_model, decision as e10_decision,
    planted_source as e10_source, original_cnf, all_model_ok,
    scan_dimacs,read_cnf,classify_nonzero_exit,original_model_replay)
from janus_time_sat_004e8_model_first import source as e8_source
from janus_time_sat_004e6_semantic_selector import normalized_selector

ROOT=Path("experiments/time_sat_004_external")
PLAN=ROOT/"PREREGISTERED_004E11_PREFIX_PARITY_16VM_20261102.json"
PLAN_BLOB="17ea362b0c569b9b815130ac31c598c261174cc2"
OLD_MODEL_SHA="12280a2df2cceea69fd1890603d1795994939b84636d7da9efc231a6a7298397"
HOSTS=("ubuntu-22.04","ubuntu-24.04")
IDS=("e11-torus-cross-16x16","e11-torus-cross-22x22",
     "e11-circulant-5tap-n256","e11-circulant-5tap-n384",
     "e11-diagonal-grid-14x14","e11-diagonal-grid-20x20",
     "e10-exactone-t48","mixed-planted-xor-n224")
NEW=IDS[:6]
ARMS=("e11_prefix_certified","e9_cost_nearest","e10_ood_abstain",
      "semantic80","native_all","raw_cms","cadical195_original")
CPU=12
WALL=16
MEM=2147483648
REPEATS=2
SEED=202611021511
PREFIX=192
MIN_EQ=4
MIN_FRAC=0.70
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}

def digest(b):return sha256(b).hexdigest()

def frozen():
    actual=subprocess.run(["git","hash-object",str(PLAN)],capture_output=True,
                          text=True,check=True).stdout.strip()
    if actual!=PLAN_BLOB:raise AssertionError("004E11 preregistration Git blob SHA changed")
    p=json.loads(PLAN.read_text())
    b=p["benchmark"];s=p["selector_policy"]
    if (tuple(x["id"] for x in p["source_cases"])!=IDS
        or tuple(b["Ubuntu"])!=HOSTS or tuple(b["arms"])!=ARMS
        or (b["original_VM_jobs"],b["max_simultaneous_jobs"],
            b["cold_subprocesses"],b["repeats_each_arm_worker"])!=(16,8,224,REPEATS)
        or (b["CPU_soft_s"],b["wall_timeout_s"],b["RLIMIT_AS_bytes"])!=(CPU,WALL,MEM)
        or (s["first_clauses_source_proved"],s["min_source_proven_complete_XOR_count"],
            s["min_prefix_XOR_original_clause_fraction"])!=(PREFIX,MIN_EQ,MIN_FRAC)
        or p["generator"]["independent_external_sources"]!=0):
        raise AssertionError("004E11 preregistered original cohort/threshold/budget changed")
    return p

def new_source(case):
    spec=next((x for x in frozen()["source_cases"] if x["id"]==case),None)
    if spec is None or spec["kind"]!="NEW_INTERNAL_SYNTHETIC_SAT":
        raise AssertionError("Not a registered original new source")
    rng=random.Random(spec["seed"])
    family=spec["family"]
    if "grid" in spec:
        size=spec["grid"];n=size*size
    else:n=spec["n"]
    if n<16:raise AssertionError("Under-sized generator")
    truth={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
    signed=[i if truth[i] else -i for i in range(1,n+1)]
    supports=[]
    if family=="new_internal_periodic_grid_cross_parity":
        for row in range(size):
            for col in range(size):
                pts=[(row,col),(row,(col+1)%size),(row,(col-1)%size),
                     ((row+1)%size,col),((row-1)%size,col)]
                supports.append(tuple(sorted(1+r*size+c for r,c in pts)))
    elif family=="new_internal_circulant_5tap_parity":
        offsets=spec["offsets"]
        for base in range(n):
            supports.append(tuple(sorted(1+(base+dx)%n for dx in offsets)))
    elif family=="new_internal_diagonal_4tap_grid_parity":
        for row in range(size):
            for col in range(size):
                pts=[(row,col),(row,(col+1)%size),((row+1)%size,col),
                     ((row+1)%size,(col+1)%size)]
                supports.append(tuple(sorted(1+r*size+c for r,c in pts)))
    else:raise AssertionError("Unregistered parity topology")
    if (len(supports)!=n or len(set(supports))!=n or
        any(len(set(s))!=len(s) or len(s) not in (4,5) for s in supports)):
        raise AssertionError("New source has collapsed parity supports")
    blocks=[]
    for support in supports:
        rhs=sum(int(truth[i]) for i in support)%2
        block=[]
        for bits in itertools.product((0,1),repeat=len(support)):
            if sum(bits)%2==rhs:continue
            block.append([v if bit==0 else -v for v,bit in zip(support,bits)])
        if len(block)!=2**(len(support)-1):
            raise AssertionError("Original parity signs incomplete")
        rng.shuffle(block)
        blocks.append(block)
    rng.shuffle(blocks) # shuffled groups, ALL source masks within each intact block
    rows=[clause for block in blocks for clause in block]
    if not all_model_ok(rows,n,signed):
        raise AssertionError("Generated original SAT source model invalid")
    payload=original_cnf(n,rows)
    return {"id":case,"family":family,"n":n,"m":len(rows),"rows":rows,
            "model":signed,"sha":digest(payload),
            "model_sha":digest(json.dumps(signed).encode()),"bytes":payload,
            "provenance":"INTERNAL_SYNTHETIC_KNOWN_FULL_SAT_NOT_EXTERNAL",
            "source_block_complete":True}

def source(case):
    if case not in IDS:raise AssertionError("Unexpected source case")
    if case in NEW:return new_source(case)
    if case=="e10-exactone-t48":
        src=e10_source(case)
        return {**src,"provenance":"PRESEEN_E10_NEGATIVE_CONTROL","source_block_complete":False}
    old=e8_source(case)
    return {**old,"provenance":"PRESEEN_E8_NEGATIVE_CONTROL","source_block_complete":False}

def lock_sources(out):
    p=frozen();model=frozen_e9_model()
    sources={c:source(c) for c in IDS}
    if len({x["sha"] for x in sources.values()})!=8:
        raise AssertionError("E11 original-source SHAs not distinct")
    previous=set(x["training_source_SHA256"] for x in model["training_entries"])
    if any(sources[c]["sha"] in previous for c in NEW):
        raise AssertionError("Accidentally reused E8 source in claimed novel synthetics")
    identities={case:{
        "original_CNF_SHA256":v["sha"],
        "complete_original_SAT_model_SHA256":v["model_sha"],
        "n":v["n"],"m":v["m"],"source_provenance":v["provenance"],
        "family":v["family"],"new_internal_synthetic":case in NEW}
        for case,v in sources.items()}
    lock={"schema":"JANUS-TIME-SAT-004E11-PRESOLVE-ORIGINAL-CNF-FULL-SAT-MODEL-LOCK-V1",
          "manifest_git_blob":PLAN_BLOB,"old_E9_trained_model_SHA256":OLD_MODEL_SHA,
          "all_original_sources_and_complete_models":identities,
          "genuinely_external_sources":0,"production_C023":"UNCHANGED",
          "precommitted_before_004E11_worker":True}
    out.mkdir(parents=True,exist_ok=True)
    content=json.dumps(lock,sort_keys=True,indent=2)+"\n"
    (out/"SOURCE_LOCK.json").write_text(content)
    (out/"SOURCE_LOCK.sha256").write_text(digest(content.encode())+"  SOURCE_LOCK.json\n")
    print("004E11_PREWORKER_LOCK_PASS",json.dumps(
        {"cases":8,"new_internal":6,"sha":digest(content.encode())},sort_keys=True))
    return lock

def checked_lock(path):
    raw=path.read_bytes()
    if path.with_name("SOURCE_LOCK.sha256").read_text().strip()!=digest(raw)+"  SOURCE_LOCK.json":
        raise AssertionError("Original source/model lock SHA tampered")
    lock=json.loads(raw)
    if (lock.get("schema")!="JANUS-TIME-SAT-004E11-PRESOLVE-ORIGINAL-CNF-FULL-SAT-MODEL-LOCK-V1"
        or lock.get("manifest_git_blob")!=PLAN_BLOB
        or lock.get("old_E9_trained_model_SHA256")!=OLD_MODEL_SHA
        or set(lock.get("all_original_sources_and_complete_models",{}))!=set(IDS)
        or lock.get("genuinely_external_sources")!=0):
        raise AssertionError("Unregistered or modified scientific lock")
    return lock,digest(raw)

def policy(rows,n,arm,trained):
    if arm not in ARMS:raise AssertionError("Unregistered arm")
    if arm=="e11_prefix_certified":
        prefix=rows[:min(PREFIX,len(rows))]
        preview=normalized_selector(prefix,n,"native_all")
        coverage=(len(prefix)-len(preview["cnf_clauses"]))/len(prefix)
        n_eq=len(preview["equations"])
        admit=(n_eq>=MIN_EQ and coverage>=MIN_FRAC)
        if admit:
            exact=normalized_selector(rows,n,"native_all")
            if exact["choice"]!="native_xor":
                raise AssertionError("Sound prefix XOR must agree with full source prover")
            return {**exact,"source_only_decision":{
                "decision":"E11_PREFIX_SOURCE_CERTIFIED_NATIVE",
                "original_prefix_clauses":len(prefix),
                "complete_prefix_source_XOR":n_eq,
                "complete_prefix_clause_fraction":coverage,
                "full_scan_performed":True}}
        return {"equations":[],"cnf_clauses":rows,"choice":"e11_prefix_abstain_raw",
                "metric":{"scope":"prefix192_only"},
                "source_only_decision":{
                    "decision":"E11_PREFIX_ABSTAIN_RAW","original_prefix_clauses":len(prefix),
                    "complete_prefix_source_XOR":n_eq,
                    "complete_prefix_clause_fraction":coverage,
                    "full_scan_performed":False}}
    return e10_decision(rows,n,arm,trained)

def child(case,arm,lock_path,expected_sha):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    lock,lock_sha=checked_lock(lock_path)
    trained=frozen_e9_model()
    src=source(case)
    expected=lock["all_original_sources_and_complete_models"][case]
    if (src["sha"]!=expected_sha or src["sha"]!=expected["original_CNF_SHA256"]
        or src["model_sha"]!=expected["complete_original_SAT_model_SHA256"]):
        raise AssertionError("Original source or model SHA mismatch pre-worker")
    with TemporaryDirectory() as temp:
        p=Path(temp)/"original-source.cnf"
        p.write_bytes(src["bytes"])
        shape=scan_dimacs(p)
        if (shape["n_variables"],shape["n_clauses"],
            shape["n_literal_occurrences"])!=(src["n"],src["m"],sum(map(len,src["rows"]))):
            raise AssertionError("Original SAT source DIMACS shape mismatch")
        rows=read_cnf(p,src["n"],src["m"],max_literals=200000)
    if rows!=src["rows"] or not all_model_ok(rows,src["n"],src["model"]):
        raise AssertionError("Original SAT complete model failed source replay")
    before=perf_counter()
    chosen=policy(rows,src["n"],arm,trained)
    feature_wall=perf_counter()-before
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as solver:
            stamp=perf_counter();sat=solver.solve();solve_wall=perf_counter()-stamp
            answer=solver.get_model() if sat is True else None
    else:
        import pycryptosat
        solver=pycryptosat.Solver(threads=1)
        for eq in chosen["equations"]:
            solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
        for clause in chosen["cnf_clauses"]:solver.add_clause(clause)
        stamp=perf_counter();sat,vector=solver.solve();solve_wall=perf_counter()-stamp
        answer=([i if bool(vector[i]) else -i for i in range(1,src["n"]+1)]
                if sat is True and vector is not None and len(vector)>src["n"] else None)
    if sat is True:
        if answer is None or not original_model_replay(rows,src["n"],answer):
            raise AssertionError("Solver result is not a valid original source SAT model")
        verdict=SAT
    elif sat is False:
        raise AssertionError("UNSAT on previously independently model-verified SAT source")
    else:verdict="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":verdict,"case":case,"arm":arm,"family":src["family"],
        "original_CNF_SHA256":src["sha"],"complete_model_SHA256":src["model_sha"],
        "source_lock_SHA256":lock_sha,
        "pretrained_model_SHA256":OLD_MODEL_SHA,
        "feature_probe_full_scan_and_selection_wall_s":feature_wall,
        "native_solver_wall_s":solve_wall,
        "full_cold_inner_wall_s":perf_counter()-started,
        "full_cold_CPU_s":process_time(),
        "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "selected_exact_source_XOR_equations":len(chosen["equations"]),
        "actual_solver_representation":chosen["choice"],
        "source_only_decision":chosen.get("source_only_decision",chosen.get("cost_prediction",{})),
        "original_SAT_model_verified":"PASS",
        "independent_external_source":False,
        "C023_main":"UNCHANGED"}

def matrix(case,lock_path,out):
    frozen()
    lock,lock_sha=checked_lock(lock_path)
    src=source(case)
    if src["sha"]!=lock["all_original_sources_and_complete_models"][case]["original_CNF_SHA256"]:
        raise AssertionError("Original source SHA drifts before any comparison")
    records=[]
    for rep in range(REPEATS):
        order=list(ARMS)
        random.Random(SEED+79*IDS.index(case)+rep).shuffle(order)
        for arm in order:
            start=perf_counter()
            cmd=[sys.executable,str(Path(__file__).resolve()),"--child","--case",case,
                 "--arm",arm,"--source-lock",str(lock_path),"--expected-sha",src["sha"]]
            try:
                result=subprocess.run(cmd,text=True,capture_output=True,check=False,timeout=WALL)
                if result.returncode:
                    o=classify_nonzero_exit(result.returncode)
                    o["status"]=o.get("verdict","NONREGISTERED")
                    o["exit_code"]=result.returncode
                    o["stderr_tail"]=result.stderr[-700:]
                else:o=json.loads(result.stdout)
            except subprocess.TimeoutExpired:o={"status":"UNKNOWN_WALL_TIMEOUT"}
            records.append({"repeat":rep,"arm":arm,"shuffled_order":order,
                "full_cold_child_wall_seconds":perf_counter()-start,"outcome":o})
            print("004E11_COLD_CHILD",case,rep,arm,o.get("status"),
                round(records[-1]["full_cold_child_wall_seconds"],4),flush=True)
    if len(records)!=14 or any(r["outcome"].get("status") not in ALLOWED for r in records):
        raise AssertionError("Original E11 scientific evidence missing or crashed")
    for r in records:
        o=r["outcome"]
        if o["status"]==SAT and (
          o["original_CNF_SHA256"]!=src["sha"]
          or o["complete_model_SHA256"]!=src["model_sha"]
          or o["source_lock_SHA256"]!=lock_sha
          or o["original_SAT_model_verified"]!="PASS"):
            raise AssertionError("Original exact source model not independently proven")
    receipt={
       "schema":"JANUS-TIME-SAT-004E11-7-ARM-14-COLD-CHILD-ORIGINAL-GITHUB-VM-V1",
       "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
       "original_head":os.getenv("GITHUB_SHA","LOCAL"),
       "original_runner_name":os.getenv("RUNNER_NAME","LOCAL"),
       "original_os":os.getenv("SAT_E11_OS","LOCAL"),
       "case":case,"family":src["family"],
       "original_CNF_SHA256":src["sha"],
       "complete_SAT_model_SHA256":src["model_sha"],
       "frozen_protocol_git_blob":PLAN_BLOB,
       "preworker_lock_sha":lock_sha,"old_trained_model_SHA256":OLD_MODEL_SHA,
       "cold_children":14,"CPU_s":CPU,"WALL_s":WALL,"MEM":MEM,
       "source_is_new_internal":case in NEW,
       "external_hidden_sources":0,"C023_main":"UNCHANGED",
       "records":records}
    out.mkdir(parents=True,exist_ok=True)
    (out/(case+"__"+os.getenv("SAT_E11_OS","LOCAL")+".json")).write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("004E11_ORIGINAL_VM_PASS",case, "SAT",sum(
        x["outcome"]["status"]==SAT for x in records),flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--child",action="store_true")
    ap.add_argument("--case",choices=IDS)
    ap.add_argument("--arm",choices=ARMS,default="e11_prefix_certified")
    ap.add_argument("--source-lock",type=Path)
    ap.add_argument("--expected-sha",default="")
    ap.add_argument("--out",type=Path)
    x=ap.parse_args()
    if x.preflight:
        if x.out is None:raise SystemExit("--out required")
        lock_sources(x.out)
    elif x.child:
        if x.case is None or x.source_lock is None:raise SystemExit("--case/--source-lock required")
        frozen()
        print(json.dumps(child(x.case,x.arm,x.source_lock,x.expected_sha),sort_keys=True))
    else:
        if x.case is None or x.out is None or x.source_lock is None:
            raise SystemExit("--case/--out/--source-lock required")
        matrix(x.case,x.source_lock,x.out)
