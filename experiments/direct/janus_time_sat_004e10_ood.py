#!/usr/bin/env python3
"""TIME-SAT-004E10: pre-frozen E9 model, group-new synthetic SAT families.

Three generator families entirely absent from E8 training: planted 3-color,
Exact-One task allocation, width-four parity+guards. No source is external.
Source complete models and hashes are precommitted before the first worker.
"""
from __future__ import annotations
import argparse
import itertools
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

from janus_time_sat_004e9_cost_to_observe import (
    checked_model as e9_model,policy as e9_policy,
    fingerprint,distance,ARMS as E9_ARMS,
    original_model_replay,scan_dimacs,read_cnf,classify_nonzero_exit)
from janus_time_sat_004e6_semantic_selector import normalized_selector

ROOT=Path("experiments/time_sat_004_external")
PREREG=ROOT/"PREREGISTERED_004E10_OOD_NEW_GENERATOR_FAMILIES_20261102.json"
PREREG_BLOB="149b06f6cc34edf3e1d8c73947bf0bdde915b96c"
MODEL=ROOT/"time_sat_004e9_evidence/original-frozen-E8-model/MODEL.json"
MODEL_SHA="12280a2df2cceea69fd1890603d1795994939b84636d7da9efc231a6a7298397"
FAMILIES=("planted-graph-3color","planted-exact-one-allocation","planted-guarded-width4-parity")
IDS=("e10-graph3color-v36","e10-graph3color-v60",
     "e10-exactone-t28","e10-exactone-t48",
     "e10-guarded-parity-n80","e10-guarded-parity-n128")
ARMS=("e9_cost_nearest","e10_ood_abstain","semantic80",
      "native_all","raw_cms","cadical195_original")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
SEED=202611021310
CPU=12
WALL=16
MEM=2147483648
REPS=2
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}
MARGIN=0.50
TOL=0.25
MAX_DIST=1.75

def digest(b):return sha256(b).hexdigest()
def git_blob(path):
    return subprocess.run(["git","hash-object",str(path)],capture_output=True,
                          text=True,check=True).stdout.strip()

def frozen():
    if git_blob(PREREG)!=PREREG_BLOB:raise AssertionError("Frozen E10 experimental registration SHA changed")
    p=json.loads(PREREG.read_text())
    budget=p["budgets"]
    if (tuple(x["case"] for x in p["new_source_generator_families"])!=IDS
        or tuple(p["fixed_arms"])!=ARMS
        or tuple(budget["host_images"])!=HOSTS
        or (budget["original_workers"],budget["max_parallel"],
            budget["total_children"],budget["cold_repeats_each_arm_per_worker"])!=(12,6,144,2)
        or (budget["CPU_soft_s"],budget["wall_timeout_s"],budget["RLIMIT_AS_bytes"])!=(CPU,WALL,MEM)
        or p["original_frozen_E9_model_SHA256"]!=MODEL_SHA
        or (p["frozen_ood_gate"]["positive_negative_margin_min"],
            p["frozen_ood_gate"]["feature_training_minmax_tolerance"],
            p["frozen_ood_gate"]["distmax"])!=(MARGIN,TOL,MAX_DIST)
        or p["validation"]["external_blinded_originals"]!=0
        or p["validation"]["production_main_C023"]!="UNCHANGED"):
        raise AssertionError("Registered E10 sources, rules, costs or safety gates changed")
    return p

def model():
    m,sha=e9_model(MODEL)
    if sha!=MODEL_SHA:raise AssertionError("Previously frozen E9 original MODEL.json SHA drift")
    labels=[e["label"] for e in m["training_entries"]]
    if len(labels)!=8 or labels.count("XOR")!=2:
        raise AssertionError("Unexpected retuned E9 prior training outcome/model")
    return m

def original_cnf(n,rows):
    return ("p cnf "+str(n)+" "+str(len(rows))+"\n"+
            "".join(" ".join(map(str,clause))+" 0\n" for clause in rows)).encode("ascii")

def all_model_ok(rows,n,signed):
    return (len(signed)==n and {abs(x) for x in signed}==set(range(1,n+1))
            and original_model_replay(rows,n,signed))

def planted_source(case):
    p=frozen()
    x=next((v for v in p["new_source_generator_families"] if v["case"]==case),None)
    if x is None:raise AssertionError("Unknown original source group")
    rng=random.Random(x["seed"])
    family=x["family"]
    rows=[]
    n=x["n"]
    if family=="planted-graph-3color":
        vertices=x["vertices"]
        colors=[rng.randrange(3) for _ in range(vertices)]
        if len(set(colors))!=3:raise AssertionError("Planted palette unexpectedly degenerate")
        chosen=set()
        while len(chosen)<x["edges"]:
            u,v=sorted(rng.sample(range(vertices),2))
            if colors[u]!=colors[v]:chosen.add((u,v))
        for u in range(vertices):
            choices=[3*u+c+1 for c in range(3)]
            rows.append(choices)
            for c,d in itertools.combinations(choices,2):rows.append([-c,-d])
        for u,v in sorted(chosen):
            for c in range(3):
                rows.append([-(3*u+c+1),-(3*v+c+1)])
        model=[(3*u+c+1) if colors[u]==c else -(3*u+c+1)
               for u in range(vertices) for c in range(3)]
    elif family=="planted-exact-one-allocation":
        tasks=x["tasks"];k=x["choices"]
        slots=[rng.randrange(k) for _ in range(tasks)]
        # Consecutive-task pairwise conflicts are planted satisfiable.
        for i in range(1,tasks):
            if slots[i]==slots[i-1]:slots[i]=(slots[i]+1+rng.randrange(k-1))%k
        for task in range(tasks):
            atoms=[k*task+j+1 for j in range(k)]
            rows.append(atoms)
            for a,b in itertools.combinations(atoms,2):rows.append([-a,-b])
        for task in range(tasks-1):
            for slot in range(k):
                rows.append([-(k*task+slot+1),-(k*(task+1)+slot+1)])
        model=[(k*t+j+1) if slots[t]==j else -(k*t+j+1)
               for t in range(tasks) for j in range(k)]
    elif family=="planted-guarded-width4-parity":
        values={i:bool(rng.getrandbits(1)) for i in range(1,n+1)}
        model=[i if values[i] else -i for i in range(1,n+1)]
        supports=set()
        while len(supports)<x["width4_equations"]:
            supports.add(tuple(sorted(rng.sample(range(1,n+1),4))))
        seen=set()
        for support in sorted(supports):
            rhs=sum(int(values[v]) for v in support)%2
            for bits in itertools.product((0,1),repeat=4):
                if sum(bits)%2==rhs:continue
                clause=tuple(v if b==0 else -v for v,b in zip(support,bits))
                if clause in seen:raise AssertionError("Duplicate generated XOR source mask")
                seen.add(clause);rows.append(list(clause))
        remaining=x["planted_3clauses"]
        for _ in range(remaining*90):
            if remaining==0:break
            ids=sorted(rng.sample(range(1,n+1),3))
            c=tuple(v if rng.getrandbits(1) else -v for v in ids)
            if c in seen or not any((lit>0)==values[abs(lit)] for lit in c):continue
            seen.add(c);rows.append(list(c));remaining-=1
        if remaining:raise AssertionError("Unique planted guard clauses could not be sampled")
        rng.shuffle(rows)
    else:raise AssertionError("Generator family not registered")

    if not all_model_ok(rows,n,model):
        raise AssertionError("Original full planted SAT assignment invalid")
    if family=="planted-graph-3color" and len(rows)!=4*x["vertices"]+3*x["edges"]:
        raise AssertionError("Original graph CNF m mismatch")
    if family=="planted-exact-one-allocation" and len(rows)!=x["tasks"]*(1+x["choices"]*(x["choices"]-1)//2)+(x["tasks"]-1)*x["choices"]:
        raise AssertionError("Original exact-one CNF m mismatch")
    if family=="planted-guarded-width4-parity" and len(rows)!=8*x["width4_equations"]+x["planted_3clauses"]:
        raise AssertionError("Original 4XOR clauses count mismatch")

    raw=original_cnf(n,rows)
    return {"id":case,"family":family,"kind":"INTERNAL_NEW_GENERATOR_FAMILY_NOT_EXTERNAL",
            "n":n,"m":len(rows),"rows":rows,"bytes":raw,"sha":digest(raw),
            "model":model,"model_sha":digest(json.dumps(model).encode("utf-8"))}

def prepare(out):
    p=frozen()
    previous=model()
    sources={name:planted_source(name) for name in IDS}
    original_training=set(x["training_source_SHA256"] for x in previous["training_entries"])
    if len({x["sha"] for x in sources.values()})!=6 or any(x["sha"] in original_training for x in sources.values()):
        raise AssertionError("E10 cannot reuse E8 training exact source SHAs")
    locks={k:{"original_CNF_SHA256":s["sha"],"complete_original_SAT_model_SHA256":s["model_sha"],
              "n":s["n"],"m":s["m"],"family":s["family"],"internal_synthetic":True}
           for k,s in sources.items()}
    locked={"schema":"JANUS-TIME-SAT-004E10-PRESOLVE-SEALED-SYNTHETIC-SOURCES-V1",
            "frozen_protocol_git_blob":PREREG_BLOB,
            "frozen_training_model_SHA256":MODEL_SHA,
            "source_precommit":locks,
            "original_distinct_generator_families":3,
            "generator_family_grouped_no_train_sources":True,
            "external_blind_sources":0,
            "C023":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    raw=json.dumps(locked,indent=2,sort_keys=True)+"\n"
    (out/"SOURCE_LOCK.json").write_text(raw)
    (out/"SOURCE_LOCK.sha256").write_text(digest(raw.encode())+"  SOURCE_LOCK.json\n")
    print("004E10_PRECOMMITTED_SOURCES",json.dumps({k:v["original_CNF_SHA256"] for k,v in locks.items()},sort_keys=True))
    return locked

def checked_lock(path):
    raw=path.read_bytes()
    if path.with_name("SOURCE_LOCK.sha256").read_text().strip()!=digest(raw)+"  SOURCE_LOCK.json":
        raise AssertionError("Pre-worker new family source lock SHA changed")
    j=json.loads(raw)
    if (j.get("schema")!="JANUS-TIME-SAT-004E10-PRESOLVE-SEALED-SYNTHETIC-SOURCES-V1"
        or j.get("frozen_protocol_git_blob")!=PREREG_BLOB
        or j.get("frozen_training_model_SHA256")!=MODEL_SHA
        or set(j.get("source_precommit",{}))!=set(IDS)
        or j.get("external_blind_sources")!=0):
        raise AssertionError("Untrusted 004E10 source lock or pretrained model")
    return j,digest(raw)

def decision(rows,n,arm,model_data):
    if arm not in ARMS:raise AssertionError("Unknown posthoc method")
    if arm=="e9_cost_nearest":
        return e9_policy(rows,n,"cost_nearest",model_data)
    if arm=="e10_ood_abstain":
        feature=fingerprint(rows,n)
        training=model_data["training_entries"]
        closest=min(training,key=lambda r:(distance(feature,r["fingerprint"]),r["original_source_group"]))
        d=distance(feature,closest["fingerprint"])
        candidates=[e for e in training if e["label"]=="XOR"]
        rejected=[e for e in training if e["label"]=="RAW"]
        closest_positive=min(distance(feature,e["fingerprint"]) for e in candidates)
        closest_negative=min(distance(feature,e["fingerprint"]) for e in rejected)
        cols=list(zip(*(r["fingerprint"] for r in training)))
        within=all(min(col)-TOL<=v<=max(col)+TOL for v,col in zip(feature,cols))
        allow=(within and d<=MAX_DIST and closest["label"]=="XOR"
               and closest_positive+MARGIN<=closest_negative
               and closest["original_FULL_COLD_native_verified_SAT"]==4)
        if allow:
            derived=normalized_selector(rows,n,"native_all")
            return {**derived,"cost_prediction":{"choose":"E10_ADMIT_SOURCE_EQUIVALENT_XOR",
               "cheap_features":feature,"nearest_source":closest["original_source_group"],
               "nearest_L1":d,"nearest_positive_distance":closest_positive,
               "nearest_negative_distance":closest_negative,
               "training_bounds_ok":within,"expensive_scan":True}}
        return {"equations":[],"cnf_clauses":rows,"choice":"ood_abstain_raw_without_scan",
                "metric":{"normalization":"OOD_ABSTENTION_SOURCE_ONLY"},
                "cost_prediction":{"choose":"E10_OOD_ABSTAIN_RAW",
                  "cheap_features":feature,"nearest_source":closest["original_source_group"],
                  "nearest_L1":d,"nearest_positive_distance":closest_positive,
                  "nearest_negative_distance":closest_negative,
                  "training_bounds_ok":within,"expensive_scan":False}}
    if arm=="semantic80":return normalized_selector(rows,n,"new_semantic80")
    if arm=="native_all":return normalized_selector(rows,n,"native_all")
    if arm=="raw_cms":return normalized_selector(rows,n,"raw_cms")
    return {"equations":[],"cnf_clauses":rows,"choice":"cadical195_original",
            "metric":{"normalization":"NATIVE_BASELINE_NO_SCAN"}}

def child(case,arm,lockpath,expected_sha):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    start=perf_counter()
    source_lock,locksha=checked_lock(lockpath)
    m=model()
    source=planted_source(case)
    identity=source_lock["source_precommit"][case]
    if (source["sha"],source["model_sha"])!=(expected_sha,identity["complete_original_SAT_model_SHA256"]) or source["sha"]!=identity["original_CNF_SHA256"]:
        raise AssertionError("E10 original source SHA/model changed after preflight")
    with TemporaryDirectory() as tmp:
        p=Path(tmp)/"source-original.cnf"
        p.write_bytes(source["bytes"])
        shape=scan_dimacs(p)
        if (shape["n_variables"],shape["n_clauses"],shape["n_literal_occurrences"])!=(
            source["n"],source["m"],sum(map(len,source["rows"]))):
            raise AssertionError("Original DIMACS shape/lexical source mismatch")
        rows=read_cnf(p,source["n"],source["m"],max_literals=200000)
    if rows!=source["rows"] or not all_model_ok(rows,source["n"],source["model"]):
        raise AssertionError("Full original known-SAT model must pass before solving")
    select_start=perf_counter()
    chosen=decision(rows,source["n"],arm,m)
    feature_s=perf_counter()-select_start
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        with Solver(name="cadical195",bootstrap_with=rows) as slv:
            started=perf_counter();sat=slv.solve();solving=perf_counter()-started
            answer=slv.get_model() if sat else None
    else:
        import pycryptosat
        slv=pycryptosat.Solver(threads=1)
        for equation in chosen["equations"]:
            slv.add_xor_clause(equation["variables"],bool(equation["rhs"]))
        for clause in chosen["cnf_clauses"]:
            slv.add_clause(clause)
        started=perf_counter();sat,v=slv.solve();solving=perf_counter()-started
        answer=[i if bool(v[i]) else -i for i in range(1,source["n"]+1)] if sat is True and v is not None and len(v)>source["n"] else None
    if sat is True:
        if answer is None or not original_model_replay(rows,source["n"],answer):
            raise AssertionError("Solver-produced SAT assignment does not satisfy full original CNF")
        status=SAT
    elif sat is False:
        raise AssertionError("UNSAT contradicts preverified original planted SAT model")
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":status,"case":case,"arm":arm,"family":source["family"],
            "original_CNF_SHA256":source["sha"],"original_full_model_SHA256":source["model_sha"],
            "sealed_source_lock_SHA256":locksha,"original_E9_model_SHA256":MODEL_SHA,
            "original_model_pre_and_post_replayed":True,
            "feature_fingerprint_and_selector_wall_s":feature_s,
            "native_solver_wall_s":solving,"full_cold_inner_wall_s":perf_counter()-start,
            "full_cold_CPU_s":process_time(),"peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "selected_original_XOR_equations":len(chosen["equations"]),
            "effective_representation":chosen["choice"],
            "source_only_decision":chosen.get("cost_prediction",{}),
            "no_external_hidden_sample":True,"C023":"UNCHANGED"}

def matrix(case,lockpath,out):
    frozen()
    checked_lock(lockpath)
    src=planted_source(case)
    receipts=[]
    for rep in range(REPS):
        order=list(ARMS)
        random.Random(SEED+71*IDS.index(case)+rep).shuffle(order)
        for arm in order:
            start=perf_counter()
            command=[sys.executable,str(Path(__file__).resolve()),"--child","--case",case,
                     "--arm",arm,"--source-lock",str(lockpath),
                     "--expected-sha",src["sha"]]
            try:
                p=subprocess.run(command,capture_output=True,text=True,check=False,timeout=WALL)
                if p.returncode:
                    o=classify_nonzero_exit(p.returncode)
                    o["status"]=o.get("verdict","UNSUPPORTED_FAIL")
                    o["exit_code"]=p.returncode
                    o["stderr_tail"]=p.stderr[-500:]
                else:o=json.loads(p.stdout)
            except subprocess.TimeoutExpired:o={"status":"UNKNOWN_WALL_TIMEOUT"}
            receipts.append({"repeat":rep,"arm":arm,"shuffled_order":order,
                 "cold_child_full_wall_s":perf_counter()-start,"outcome":o})
            print("004E10_TRIAL",case,rep,arm,o["status"],
                  round(receipts[-1]["cold_child_full_wall_s"],4),flush=True)
    if len(receipts)!=12 or any(r["outcome"]["status"] not in ALLOWED for r in receipts):
        raise AssertionError("Invalid child original status; never report scientific job PASS")
    for r in receipts:
        o=r["outcome"]
        if o["status"]==SAT and (o["original_CNF_SHA256"]!=src["sha"]
               or o["original_full_model_SHA256"]!=src["model_sha"]
               or o["original_model_pre_and_post_replayed"] is not True):
            raise AssertionError("Source-locked original SAT proof receipt missing")
    lock,locksha=checked_lock(lockpath)
    output={"schema":"JANUS-TIME-SAT-004E10-FAMILY-NEW-SYNTHETIC-6-ARM-ORIGINAL-VM-V1",
            "original_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
            "original_head":os.getenv("GITHUB_SHA","LOCAL"),
            "original_runner_name":os.getenv("RUNNER_NAME","LOCAL"),
            "original_os":os.getenv("SAT_004E10_OS","LOCAL"),
            "case":case,"family":src["family"],"original_CNF_SHA256":src["sha"],
            "full_SAT_model_SHA256":src["model_sha"],
            "sealed_source_lock_SHA256":locksha,
            "original_E9_pretrained_model_SHA256":MODEL_SHA,
            "frozen_experiment_git_blob":PREREG_BLOB,
            "CPU_s":CPU,"WALL_s":WALL,"MEM":MEM,
            "original_children":12,"records":receipts,
            "new_external_blind_sources":0,
            "production_C023":"UNCHANGED",
            "scientific_status":"FAMILY_NOVEL_BUT_GENERATOR_SELF_AUTHORED"}
    out.mkdir(parents=True,exist_ok=True)
    (out/(case+"__"+os.getenv("SAT_004E10_OS","LOCAL")+".json")).write_text(
        json.dumps(output,sort_keys=True,indent=2)+"\n")
    print("004E10_ORIGINAL_WORKER_PASS",case,
          sum(x["outcome"]["status"]==SAT for x in receipts),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--preflight",action="store_true")
    p.add_argument("--child",action="store_true")
    p.add_argument("--case",choices=IDS)
    p.add_argument("--arm",choices=ARMS)
    p.add_argument("--source-lock",type=Path)
    p.add_argument("--expected-sha",default="")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.preflight:
        if a.out is None:raise SystemExit("--out required for sealed source preflight")
        prepare(a.out)
    elif a.child:
        if a.case is None or a.arm is None or a.source_lock is None:raise SystemExit("Missing frozen original child arguments")
        print(json.dumps(child(a.case,a.arm,a.source_lock,a.expected_sha),sort_keys=True))
    else:
        if a.case is None or a.out is None or a.source_lock is None:raise SystemExit("Missing E10 matrix args")
        matrix(a.case,a.source_lock,a.out)
