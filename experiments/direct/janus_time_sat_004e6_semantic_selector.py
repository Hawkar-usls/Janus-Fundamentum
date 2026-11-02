#!/usr/bin/env python3
"""TIME-SAT-004E6: exact-clause semantic-core 80% gate, fully source replayed.

Repair is narrow: tautology / duplicate literal / duplicate clause invariance.
It is NOT invariant to arbitrary logically implied non-tautological clauses.
Source copies are previously known and transformations synthetic/not blinded.
"""
from __future__ import annotations
import argparse
from collections import Counter
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

from janus_time_sat_004e5_metamorphic import original_verified
from janus_time_sat_004e3_swarm import select_verified_xor
from janus_time_sat_004b_acquire import scan_dimacs
from janus_time_sat_004b_baselines import read_cnf,classify_nonzero_exit
from janus_time_sat_004d4b_real_pilot import original_model_replay

PRE=Path("experiments/time_sat_004_external/PREREGISTERED_004E6_SEMANTIC_NORMALIZED_GATE_20261102.json")
BLOB="9b33d072c5253bcd4039bf0e6e3d90136b70686a"
FAMILIES=("lights-out","binary-tree-parity")
STATES=("rename_only","taut5_duplicate5","taut30_duplicate20")
VALUES={"rename_only":(0,0),"taut5_duplicate5":(5,5),"taut30_duplicate20":(30,20)}
ARMS=("old_adaptive80","new_semantic80","native_all","raw_cms")
HOSTS=("ubuntu-22.04","ubuntu-24.04")
SEED=20261102086
CPU=6
WALL=10
MEM=2147483648
REPS=2
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
ALLOWED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT","UNKNOWN_SOLVER_NO_ANSWER"}
SHA={
"lights-out":"6be9bfe6b44454a061a2e93350f589643f8a16f5bca6babdaa50a2d3d7069361",
"binary-tree-parity":"8d94924bef8978b28a2bf95472556b280bef5d98b6833c6db33554098f52d2d8"}

def preregistered():
    h=subprocess.run(["git","hash-object",str(PRE)],text=True,capture_output=True,check=True).stdout.strip()
    if h!=BLOB:raise AssertionError("004E6 preregistration altered; REFUSE")
    p=json.loads(PRE.read_text())
    q=p["comparison"]
    if (p["new_metamorphic_cohort"]["seed"]!=SEED
        or p["policy"]["coverage_threshold"]!=0.8
        or p["policy"]["mode"]!="canonical_exact_clause_dedup_and_tautology_elimination"
        or tuple(q["arms_on_each_VM"])!=ARMS
        or tuple(q["os"])!=HOSTS
        or tuple(q["source_families"])!=FAMILIES
        or tuple(q["metamorphic_states"])!=STATES
        or (q["jobs"],q["total_children"],q["repetitions_each_arm_on_same_VM"])!=(12,96,2)
        or (q["CPU_soft_s"],q["WALL_timeout_s"],q["RLIMIT_AS_bytes"])!=(CPU,WALL,MEM)
        or p["new_metamorphic_cohort"]["claimed_new_independent_SAT_sources"]!=0):
        raise AssertionError("004E6 preregistration and executable disagree")
    for case in p["source_origins"]:
        if case["CNF_SHA256"]!=SHA[case["family"]]:
            raise AssertionError("004E6 source SHA swapped")
    return p

def semantic_core(rows,n):
    """Sound CNF-normalization: remove tautologies and exact duplicate clauses.

    Retains all nontrivial independent clauses and empty clauses. A deduped
    literal is within an OR clause, not an XOR. Fail closed on bad literals.
    """
    if type(n)!=int or not 1<=n<=5000 or len(rows)>30000:
        raise AssertionError("Invalid source size")
    core=[];seen=set();taut=duplicates=repeat_lits=0
    for clause in rows:
        if not isinstance(clause,(list,tuple)):raise AssertionError("Bad clause")
        literals=set()
        for v in clause:
            if type(v)!=int or v==0 or abs(v)>n:
                raise AssertionError("Invalid literal")
            if v in literals:repeat_lits+=1
            literals.add(v)
        if any(-v in literals for v in literals):
            taut+=1
            continue
        canonical=tuple(sorted(literals,key=lambda x:(abs(x),x<0)))
        if canonical in seen:
            duplicates+=1
            continue
        seen.add(canonical)
        core.append(list(canonical))
    return core,{"tautology_clauses":taut,"duplicate_clauses":duplicates,
                 "repeated_literals_in_clause":repeat_lits,
                 "original_clauses":len(rows),"semantic_core_clauses":len(core),
                 "clauses_deletions_proved_semantically":taut+duplicates}

def normalized_selector(rows,n,arm):
    """Use E3 complete sign-mask extractor ONLY on equivalent normalized source."""
    if arm not in ARMS:raise AssertionError("Unregistered candidate")
    if arm=="raw_cms":
        return {"equations":[],"cnf_clauses":rows,"choice":"raw_original",
                "metric":{"fraction":0.0,"selected":0,"normalization":"SKIPPED_RAW_REFERENCE"}}
    if arm!="new_semantic80":
        x=select_verified_xor(rows,n,"adaptive_80" if arm=="old_adaptive80" else "native_all")
        return {"equations":x["equations"],"cnf_clauses":x["cnf_clauses"],
                "choice":x["choice"],
                "metric":{"fraction":x["converted_source_clauses"]/len(rows),
                          "selected":len(x["equations"]),
                          "normalization":"NONE_ORIGINAL_004E3",
                          "scan_status":x.get("scan_status")}}
    core,stats=semantic_core(rows,n)
    x=select_verified_xor(core,n,"adaptive_80")
    if x["converted_source_clauses"]+len(x["cnf_clauses"])!=len(core):
        raise AssertionError("Source semantic-core clause partition lost clauses")
    fraction=x["converted_source_clauses"]/len(core) if core else 0.0
    if x["choice"]=="native_xor":
        if len(x["equations"])==0 or fraction<.8:
            raise AssertionError("Normalization gate admitted without full exact 80pct proof")
        return {"equations":x["equations"],"cnf_clauses":x["cnf_clauses"],
                "choice":"native_xor","metric":{"fraction":fraction,"selected":len(x["equations"]),
                         "normalization":"VERIFIED_TAUTOLOGY_AND_EXACT_DUP_CNF_CORE",
                         "scan_status":x["scan_status"],**stats}}
    # Strict original-CNF fallback; no free normalization advantage if skip.
    return {"equations":[],"cnf_clauses":rows,"choice":"raw_original_after_core_scan",
            "metric":{"fraction":fraction,"selected":0,
                      "normalization":"PAID_FEATURE_SCAN_THEN_RAW_ORIGINAL_FALLBACK",
                      "scan_status":x.get("scan_status"),**stats}}

def mutate(rows,n,assignment,family,state):
    """New E6 seed; names, polarities, order, taut and duplicate clauses."""
    if family not in FAMILIES or state not in STATES:raise AssertionError("Case unregistered")
    t,d=VALUES[state]
    rng=random.Random(SEED+71*FAMILIES.index(family)+101*STATES.index(state))
    images=list(range(1,n+1));rng.shuffle(images)
    flips=[False]+[bool(rng.getrandbits(1)) for _ in range(n)]
    remap={old:images[old-1] for old in range(1,n+1)}
    values={abs(v):v>0 for v in assignment}
    model=[0]*n
    for old in range(1,n+1):
        new=remap[old];model[new-1]=new if (values[old]!=flips[old]) else -new
    body=[]
    for clause in rows:
        r=[remap[abs(l)] if ((l>0)!=flips[abs(l)]) else -remap[abs(l)] for l in clause]
        rng.shuffle(r);body.append(r)
    original=list(body)
    ta=(len(rows)*t+99)//100
    du=(len(rows)*d+99)//100
    for _ in range(ta):
        v=rng.randint(1,n);l=[v,-v];rng.shuffle(l);body.append(l)
    for _ in range(du):
        copy=list(original[rng.randrange(len(original))])
        rng.shuffle(copy)
        if copy and rng.getrandbits(1):copy.insert(rng.randrange(len(copy)+1),copy[0])
        body.append(copy)
    rng.shuffle(body)
    if len(body)!=len(rows)+ta+du or not original_model_replay(body,n,model):
        raise AssertionError("New E6 metamorphic source not SAT preserving")
    binary=("p cnf "+str(n)+" "+str(len(body))+"\n"+
            "".join(" ".join(map(str,r))+" 0\n" for r in body)).encode("ascii")
    return {"rows":body,"n":n,"data":binary,"SHA256":sha256(binary).hexdigest(),
            "model":model,"model_SHA256":sha256(json.dumps(model).encode()).hexdigest(),
            "added_tautologies":ta,"added_duplicates":du,"old_source_clauses":len(rows)}

def materialize(family,state):
    rows,n,sha,model=original_verified(family)
    if sha!=SHA[family]:raise AssertionError("Source SHA mismatch")
    a=mutate(rows,n,model,family,state)
    a["source_SHA256"]=sha
    return a

def single(family,state,arm,expect):
    resource.setrlimit(resource.RLIMIT_AS,(MEM,MEM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    started=perf_counter()
    data=materialize(family,state)
    if data["SHA256"]!=expect:
        raise AssertionError("Cold child transformed CNF SHA differs from parent")
    with TemporaryDirectory() as folder:
        path=Path(folder)/"original_transformed.cnf"
        path.write_bytes(data["data"])
        shape=scan_dimacs(path)
        if (shape["n_clauses"]!=len(data["rows"]) or
            shape["n_variables"]!=data["n"] or
            shape["n_literal_occurrences"]!=sum(map(len,data["rows"]))):
            raise AssertionError("Strict DIMACS transform not replayed")
        rows=read_cnf(path,data["n"],len(data["rows"]),max_literals=200000)
    if not original_model_replay(rows,data["n"],data["model"]):
        raise AssertionError("Known original SAT assignment fails rewritten exact source")
    before=perf_counter()
    form=normalized_selector(rows,data["n"],arm)
    prep=perf_counter()-before
    import pycryptosat
    solver=pycryptosat.Solver(threads=1)
    for eq in form["equations"]:
        solver.add_xor_clause(eq["variables"],bool(eq["rhs"]))
    for clause in form["cnf_clauses"]:
        solver.add_clause(clause)
    solving=perf_counter()
    sat,result=solver.solve()
    native=perf_counter()-solving
    if sat is True:
        if result is None or len(result)<=data["n"]:raise AssertionError("Incomplete model")
        model=[i if bool(result[i]) else -i for i in range(1,data["n"]+1)]
        if not original_model_replay(rows,data["n"],model):
            raise AssertionError("Original transformed CNF full SAT check failed")
        status=SAT
    elif sat is False:raise AssertionError("UNSAT incompatible with original known SAT model")
    else:status="UNKNOWN_SOLVER_NO_ANSWER"
    return {"status":status,"family":family,"state":state,"arm":arm,
            "original_source_SHA256":data["source_SHA256"],
            "transformed_CNF_SHA256":data["SHA256"],
            "known_full_model_SHA256":data["model_SHA256"],
            "source_clauses":len(rows),"semantic_core_gate":form["metric"],
            "effective_representation":form["choice"],
            "selected_XOR_equations":len(form["equations"]),
            "remaining_solver_CNF_clauses":len(form["cnf_clauses"]),
            "source_scan_and_normalize_wall_s":prep,
            "native_solver_wall_s":native,
            "full_child_inner_wall_s":perf_counter()-started,
            "full_child_CPU_s":process_time(),
            "peak_RSS_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "original_full_clause_model_replay":"PASS_PRE_AND_POST",
            "external_hidden":"NO_SYNTHETIC_PRESEEN",
            "production_C023_main":"UNCHANGED"}

def matrix(family,state,out):
    preregistered()
    a=materialize(family,state)
    records=[]
    for rep in range(REPS):
        order=list(ARMS)
        random.Random(SEED+19*FAMILIES.index(family)+13*STATES.index(state)+rep).shuffle(order)
        for arm in order:
            began=perf_counter()
            command=[sys.executable,str(Path(__file__).resolve()),"--child","--family",family,
                     "--state",state,"--arm",arm,"--expected-sha",a["SHA256"]]
            try:
                child=subprocess.run(command,capture_output=True,text=True,timeout=WALL,check=False)
                if child.returncode:
                    data=classify_nonzero_exit(child.returncode)
                    data["status"]=data.get("verdict","UNRECOGNIZED")
                    data["exit_code"]=child.returncode
                    data["stderr_tail"]=child.stderr[-400:]
                else:data=json.loads(child.stdout)
            except subprocess.TimeoutExpired:
                data={"status":"UNKNOWN_WALL_TIMEOUT"}
            r={"repeat":rep,"arm":arm,"shuffled_order":order,
               "full_cold_child_wall_s":perf_counter()-began,"outcome":data}
            records.append(r)
            print("004E6_TRIAL",family,state,rep,arm,data.get("status"),round(r["full_cold_child_wall_s"],3),flush=True)
    if len(records)!=8 or any(r["outcome"].get("status") not in ALLOWED for r in records):
        raise AssertionError("Missing or invalid child, do not call CI PASS")
    for r in records:
        o=r["outcome"]
        if o["status"]==SAT and (o["transformed_CNF_SHA256"]!=a["SHA256"] or
                                o["original_full_clause_model_replay"]!="PASS_PRE_AND_POST"):
            raise AssertionError("Source SHA/model replay mismatch")
    summary={"schema":"JANUS-TIME-SAT-004E6-FOUR-ARM-SAME-VM-SAT-EQUIVALENT-REPAIR-V1",
         "scientific_status":"RESEARCH_DIAGNOSTIC_TWO_PRESEEN_PUBLIC_SOURCE_FAMILIES_NOT_BLIND",
         "precommit_git_blob":BLOB,"github_run_id":os.getenv("GITHUB_RUN_ID","LOCAL"),
         "github_head":os.getenv("GITHUB_SHA","LOCAL"),
         "runner_name":os.getenv("RUNNER_NAME","LOCAL"),
         "os":os.getenv("SAT_004E6_OS","LOCAL"),
         "family":family,"state":state,
         "source_original_sha":a["source_SHA256"],"transformed_sha":a["SHA256"],
         "model_sha":a["model_SHA256"],"added_tautologies":a["added_tautologies"],
         "added_duplicates":a["added_duplicates"],
         "cpu_soft_s":CPU,"wall_s":WALL,"mem_bytes":MEM,
         "cold_children_expected":8,"repeats":REPS,
         "records":records,"no_production_promotion":True,
         "new_external_independent_CNF":0,"production_C023":"UNCHANGED"}
    out.mkdir(parents=True,exist_ok=True)
    (out/(family+"__"+state+"__"+os.getenv("SAT_004E6_OS","LOCAL")+".json")).write_text(
        json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("004E6_WORKER_COMPLETED",family,state,
          "sat",sum(r["outcome"]["status"]==SAT for r in records),flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--child",action="store_true")
    a.add_argument("--family",choices=FAMILIES,required=True)
    a.add_argument("--state",choices=STATES,required=True)
    a.add_argument("--arm",choices=ARMS,required=True)
    a.add_argument("--expected-sha",default="")
    a.add_argument("--out",type=Path)
    x=a.parse_args()
    if x.child:
        preregistered()
        print(json.dumps(single(x.family,x.state,x.arm,x.expected_sha),sort_keys=True))
    else:
        if x.out is None:raise SystemExit("--out required")
        matrix(x.family,x.state,x.out)
