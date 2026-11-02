#!/usr/bin/env python3
"""TIME-SAT-004E7: five previously seen public CNF families; five-arm full-cost transfer.

Do not assert source SAT if no original full model exists. Each SAT solver answer
is checked on every original *transformed* clause; every UNSAT remains solver-only.
All 200 children run in short-lived VM jobs, with same-host comparisons only.
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
from tempfile import TemporaryDirectory
from time import perf_counter,process_time

from janus_time_sat_004e2_adaptive_gate import original as e2_original
from janus_time_sat_004e4_transfer import archived_cnf as e4_original
from janus_time_sat_004e6_semantic_selector import normalized_selector
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d4b_real_pilot import original_model_replay

ROOT=Path("experiments/time_sat_004_external")
FROZEN=ROOT/"PREREGISTERED_004E7_FIVE_OTHER_PUBLIC_SOURCES_20261102.json"
FROZEN_BLOB="48740d947f678ff11894033b8cbe91ef6f4d6c59"
CASES={
"linear-equations":("dd2e52c12cafa012316052c6c2ac06ea48ccf1c999a5ae57a25c5f208e1cb9bc",1200,21040),
"xor-shifting":("03bae774557f351990c0348c7b11933d8760f4d7a8cf60455f1d4754fe9739c0",2273,8366),
"minimum-disagreement-parity":("6e054967f4c71d900b2bba2508fea2054ac13de78fa0b0b6a94753f66e9e95fc",1250,7190),
"or_randxor":("d63fa30fbe7003f7a2eff5939ab29c6064819d818115b630f57228cc86eedce1",1200,8093),
"greentao":("622732d1d213e930a7711270aefa079c9329cb9a446b4f24d848fea2cab6b5a7",527,12692),
}
FAMILIES=tuple(CASES)
STATES=("unaltered","taut20_duplicate10")
ARMS=("new_semantic80","old_adaptive80","native_all","raw_cms","cadical195_original")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
SEED=20261102087
CPU=6
WALL=10
MEM=2147483648
REPS=2
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
UNSAT="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"
ALLOWED={SAT,UNSAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}

def frozen():
    blob=subprocess.run(["git","hash-object",str(FROZEN)],check=True,
        text=True,capture_output=True).stdout.strip()
    if blob!=FROZEN_BLOB:raise AssertionError("004E7 prereg file Git blob changed")
    data=json.loads(FROZEN.read_text())
    d=data["design"]
    expected=[{"family":f,"sha256":CASES[f][0],"n":CASES[f][1],"m":CASES[f][2]} for f in FAMILIES]
    for a,b in zip(data["original_frozen_sources"],expected):
        if any(a[k]!=v for k,v in b.items()):raise AssertionError("004E7 original source SHA or shape changed")
    if (len(data["original_frozen_sources"])!=5 or
        tuple(data["representation_states"])!=STATES or
        tuple(data["arms"])!=ARMS or
        tuple(d["os"])!=HOSTS or
        (d["matrix_jobs"],d["max_parallel"],d["cold_child_count"])!=(20,20,200) or
        (d["CPU_soft_s"],d["WALL_timeout_s"],d["RLIMIT_AS_bytes"])!=(CPU,WALL,MEM) or
        data["rewrite"]["seed"]!=SEED or data["new_external_blinded_sources"]!=0):
        raise AssertionError("Original preregistered family grid, arms, budgets or science disclosure changed")
    return data

def source(family):
    if family not in CASES:raise AssertionError("Unregistered source")
    if family in ("or_randxor","greentao"):
        rows,n,sha=e4_original(family)
    else:
        rows,n,sha=e2_original(family)
    exp,nn,mm=CASES[family]
    if (sha,n,len(rows))!=(exp,nn,mm):
        raise AssertionError("Archived third-party SATCompetition source SHA/model/shape changed")
    return rows,n,sha

def transform(rows,n,family,state):
    if family not in CASES or state not in STATES:
        raise AssertionError("Unregistered original source or presentation")
    rng=random.Random(SEED+109*FAMILIES.index(family)+29*STATES.index(state))
    clauses=[list(row) for row in rows]
    if state=="unaltered":
        taut=dup=0
    else:
        taut=(20*len(rows)+99)//100
        dup=(10*len(rows)+99)//100
        # Only SOURCE-DUPLICATE clauses and tautological clauses are appended.
        originals=[list(r) for r in rows]
        for _ in range(taut):
            v=rng.randint(1,n)
            taut_clause=[v,-v]
            rng.shuffle(taut_clause)
            clauses.append(taut_clause)
        for _ in range(dup):
            r=list(originals[rng.randrange(len(originals))])
            rng.shuffle(r)
            if r and rng.getrandbits(1):
                r.insert(rng.randrange(len(r)+1),r[0])
            clauses.append(r)
        rng.shuffle(clauses)
    if len(clauses)!=len(rows)+taut+dup:
        raise AssertionError("Lost or added clauses beyond preregistered deterministic CNF append")
    payload=("p cnf "+str(n)+" "+str(len(clauses))+"\n"+
        "".join(" ".join(map(str,r))+" 0\n" for r in clauses)).encode("ascii")
    return {
        "rows":clauses,"n":n,"bytes":payload,
        "CNF_SHA256":sha256(payload).hexdigest(),
        "original_source_clauses":len(rows),"generated_clauses":len(clauses),
        "added_tautologies":taut,"added_duplicate_original_clauses":dup,
        "source_is_semantically_equivalent_by_construction":True
    }

def materialize(family,state):
    rows,n,sha=source(family)
    data=transform(rows,n,family,state)
    data["original_source_SHA256"]=sha
    return data

def run_child(family,state,arm,expected_sha):
    if arm not in ARMS:raise AssertionError("Wrong preregistered arm")
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    prepared=materialize(family,state)
    if expected_sha!=prepared["CNF_SHA256"]:
        raise AssertionError("Original generated presentation SHA differs from paired parent")
    with TemporaryDirectory() as t:
        path=Path(t)/"known-original-source-transformed.cnf"
        path.write_bytes(prepared["bytes"])
        shape=scan_dimacs(path)
        if (shape["n_variables"],shape["n_clauses"],
            shape["n_literal_occurrences"])!=(
             prepared["n"],prepared["generated_clauses"],
             sum(len(row) for row in prepared["rows"])):
            raise AssertionError("Generated source bytes were not a strict DIMACS replay")
        rows=read_cnf(path,prepared["n"],prepared["generated_clauses"],max_literals=160000)
    if rows!=prepared["rows"]:
        raise AssertionError("Generated original source clause identity failed")
    started_selection=perf_counter()
    if arm=="cadical195_original":
        selected={"equations":[],"cnf_clauses":rows,"choice":"cadical195_original",
                  "metric":{"normalization":"NO_SCAN_NATIVE_NONXOR_BASELINE"}}
    else:
        selected=normalized_selector(rows,prepared["n"],arm)
    selector_wall=perf_counter()-started_selection
    if arm=="cadical195_original":
        from pysat.solvers import Solver
        start_solve=perf_counter()
        with Solver(name="cadical195",bootstrap_with=rows) as solver:
            sat=solver.solve()
            model=solver.get_model() if sat else None
        solving=perf_counter()-start_solve
    else:
        import pycryptosat
        solver=pycryptosat.Solver(threads=1)
        for eq in selected["equations"]:
            solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
        for clause in selected["cnf_clauses"]:
            solver.add_clause(clause)
        start_solve=perf_counter()
        sat,answer=solver.solve()
        solving=perf_counter()-start_solve
        model=([i if bool(answer[i]) else -i for i in range(1,prepared["n"]+1)]
            if sat is True and answer is not None and len(answer)>prepared["n"] else None)
    if sat is True:
        if model is None or not original_model_replay(rows,prepared["n"],model):
            raise AssertionError("SAT model not verified against ORIGINAL strict transformed CNF")
        status=SAT
    elif sat is False:
        status=UNSAT # no portable independent original CNF proof
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {
        "status":status,"family":family,"presentation_state":state,"arm":arm,
        "original_CNF_SHA256":prepared["original_source_SHA256"],
        "strict_transformed_original_CNF_SHA256":prepared["CNF_SHA256"],
        "transformed_clause_count":prepared["generated_clauses"],
        "source_original_clause_count":prepared["original_source_clauses"],
        "added_tautologies":prepared["added_tautologies"],
        "added_duplicate_original_clauses":prepared["added_duplicate_original_clauses"],
        "semantic_normalization_and_selection":selected["metric"],
        "effective_solver_representation":selected["choice"],
        "selected_source_XOR_count":len(selected["equations"]),
        "remaining_source_CNF_clauses":len(selected["cnf_clauses"]),
        "selector_wall_seconds":selector_wall,"native_solver_wall_seconds":solving,
        "full_cold_child_inner_wall_seconds":perf_counter()-started,
        "full_cold_child_CPU_seconds":process_time(),
        "peak_memory_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "SAT_check":"ALL_TRANSFORMED_SOURCE_CLAUSES_REPLAYED" if status==SAT else "NOT_APPLICABLE",
        "UNSAT_check":"SOLVER_ONLY_NO_PORTABLE_CERTIFICATE" if status==UNSAT else "NOT_APPLICABLE",
        "external_independently_hidden_source":False,"C023_main":"UNCHANGED"
    }

def run_job(family,state,out):
    frozen()
    prepared=materialize(family,state)
    records=[]
    for repeat in range(REPS):
        order=list(ARMS)
        random.Random(SEED+31*FAMILIES.index(family)+43*STATES.index(state)+repeat).shuffle(order)
        for arm in order:
            started=perf_counter()
            cmd=[sys.executable,str(Path(__file__).resolve()),
                 "--child","--family",family,"--state",state,
                 "--arm",arm,"--expected-sha",prepared["CNF_SHA256"]]
            try:
                x=subprocess.run(cmd,capture_output=True,text=True,check=False,timeout=WALL)
                if x.returncode:
                    result=classify_nonzero_exit(x.returncode)
                    result["status"]=result["verdict"]
                    result["child_exit_code"]=x.returncode
                    result["stderr_tail"]=x.stderr[-800:]
                else:result=json.loads(x.stdout)
            except subprocess.TimeoutExpired:
                result={"status":"UNKNOWN_WALL_TIMEOUT"}
            record={
                "repeat":repeat,"arm":arm,"randomized_five_arm_order":order,
                "full_cold_child_wall_seconds":perf_counter()-started,
                "outcome":result}
            records.append(record)
            print("004E7_TRIAL",family,state,repeat,arm,result.get("status"),
                  round(record["full_cold_child_wall_seconds"],3),flush=True)
    if (len(records)!=10 or
        any(r["outcome"].get("status") not in ALLOWED for r in records)):
        raise AssertionError("Missing or unexplained scientific child failure, refuse CI PASS")
    for r in records:
        o=r["outcome"]
        if o["status"]==SAT and (
            o["original_CNF_SHA256"]!=prepared["original_source_SHA256"] or
            o["strict_transformed_original_CNF_SHA256"]!=prepared["CNF_SHA256"] or
            o["SAT_check"]!="ALL_TRANSFORMED_SOURCE_CLAUSES_REPLAYED"):
            raise AssertionError("Invalid original SHA or SAT model replay")
    report={
        "schema":"JANUS-TIME-SAT-004E7-FIVE-SOURCE-FIVE-ARM-PRESEEN-TRANSFER-VM-V1",
        "state":"DEVELOPMENT_ONLY_NO_INDEPENDENT_BLIND_HOLDOUT",
        "frozen_policy_git_blob":FROZEN_BLOB,
        "github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
        "github_head":os.getenv("GITHUB_SHA","LOCAL"),
        "runner_name":os.getenv("RUNNER_NAME","LOCAL"),
        "runner_OS":os.getenv("SAT_004E7_OS","LOCAL"),
        "family":family,"presentation_state":state,
        "original_CNF_SHA256":prepared["original_source_SHA256"],
        "transformed_original_CNF_SHA256":prepared["CNF_SHA256"],
        "added_tautologies":prepared["added_tautologies"],
        "added_duplicate_original_clauses":prepared["added_duplicate_original_clauses"],
        "cold_trials":10,"CPU_soft_s":CPU,"WALL_s":WALL,"RLIMIT_AS_bytes":MEM,
        "records":records,"no_promotion":True,"outside_admin_Witness":"OPEN",
        "paid_Rowan":"NONE","C023_main":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    (out/(family+"__"+state+"__"+os.getenv("SAT_004E7_OS","LOCAL")+".json")).write_text(
       json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("004E7_WORKER_COMPLETE",family,state,
          json.dumps({v:sum(r["arm"]==v and r["outcome"]["status"]==SAT for r in records)
                      for v in ARMS},sort_keys=True),flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--child",action="store_true")
    p.add_argument("--family",choices=FAMILIES,required=True)
    p.add_argument("--state",choices=STATES,required=True)
    p.add_argument("--arm",choices=ARMS,default="new_semantic80")
    p.add_argument("--expected-sha",default="")
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.child:
        frozen()
        print(json.dumps(run_child(a.family,a.state,a.arm,a.expected_sha),sort_keys=True))
    else:
        if a.out is None:raise SystemExit("Must supply --out")
        run_job(a.family,a.state,a.out)
