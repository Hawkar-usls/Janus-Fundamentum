#!/usr/bin/env python3
"""TIME-SAT-004B: isolated raw CDCL screening without JANUS 240-var limits.

SAT answers independently replay on exact decoded original input clauses.
UNSAT here means *solver reported UNSAT only*, not a portable verified proof.
TIMEOUT/ERROR/RESOURCE_LIMIT are never relabeled UNSAT.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
from time import perf_counter


def read_cnf(path:Path,n:int,m:int,max_literals=2_000_000):
    clauses=[];partial=[];total=0
    with path.open("r",encoding="ascii") as fp:
        for line in fp:
            ln=line.strip()
            if not ln or ln.startswith("c") or ln.startswith("p cnf "):continue
            for token in ln.split():
                v=int(token)
                if v:
                    if abs(v)>n:raise ValueError("literal > n")
                    partial.append(v);total+=1
                    if total>max_literals:raise MemoryError("literal count budget")
                else:
                    clauses.append(partial);partial=[]
                    if len(clauses)>m:raise ValueError("too many clauses")
    if partial or len(clauses)!=m:raise ValueError("clause mismatch")
    return clauses


def solve_one(path,engine,n,m):
    resource.setrlimit(resource.RLIMIT_AS,(2_147_483_648,2_147_483_648))
    resource.setrlimit(resource.RLIMIT_CPU,(16,17))
    started=perf_counter()
    rows=read_cnf(path,n,m)
    from pysat.solvers import Solver
    with Solver(name=engine,bootstrap_with=rows) as solver:
        answer=solver.solve()
        model=solver.get_model() if answer else None
        stats=solver.accum_stats()
    elapsed=perf_counter()-started
    if answer:
        assignment={abs(l):l>0 for l in model or []}
        valid=all(any(assignment.get(abs(l),False)==(l>0)
                and abs(l) in assignment for l in row) for row in rows)
        if not valid:raise AssertionError("SAT model fails source DIMACS replay")
    return {
      "verdict":"SAT_VERIFIED_ORIGINAL_CNF" if answer else "UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF",
      "solving_with_initialization_seconds":elapsed,
      "peak_child_RSS_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
      "native_CDCL_statistics":stats,
      "portable_unsat_proof":"NOT_PRODUCED",
      "original_model_checked":bool(answer)
    }


def classify_nonzero_exit(return_code: int) -> dict:
    """Record Linux process failure without inferring SAT/UNSAT.

    SIGKILL or another signal alone cannot establish a cause (OOM, CPU hard
    limit, external cancellation). Only SIGXCPU indicates CPU soft-limit.
    """
    if type(return_code) is not int or return_code == 0:
        raise ValueError("expected nonzero integer return code")
    if return_code > 0:
        return {"verdict":"ENGINE_NONZERO_EXIT", "exit_code":return_code}
    signum = -return_code
    try:
        signame = signal.Signals(signum).name
    except ValueError:
        signame = "UNKNOWN_SIGNAL"
    return {
        "verdict":("UNKNOWN_CPU_LIMIT_SIGXCPU" if signum==signal.SIGXCPU
                   else "UNKNOWN_PROCESS_SIGNAL"),
        "process_signal":signame,
        "signal_number":signum,
        "limit_interpretation":("CPU_SOFT_LIMIT_REACHED" if signum==signal.SIGXCPU
                                else "UNKNOWN_SIGNAL_CAUSE"),
    }


def bounded_parent(output:Path,*,per_solver_wall_s=18):
    source=json.loads((output/"acquisition.json").read_text())
    if source["schema"]!="JANUS-TIME-SAT-004B-EXTERNAL-ORIGIN-DIMACS-ACQUISITION-V1":
        raise ValueError("unexpected source")
    results=[]
    for row in source["results"]:
        case={key:row.get(key) for key in
              ("GBD_database_ID_NOT_SHA256","family","upstream_label_UNVERIFIED","status",
               "source_sha256","uncompressed_sha256","original_transfer_bytes",
               "n_variables","n_clauses","n_literal_occurrences","solver_status")}
        case["solver_results"]={}
        if row.get("solver_status")!="READY_FOR_STRICT_BASELINE":
            results.append(case);continue
        path=output/"downloads"/(row["GBD_database_ID_NOT_SHA256"]+".cnf")
        # Source SHA-256 asserted AGAIN here before each solver.
        if sha256(path.read_bytes()).hexdigest()!=row["uncompressed_sha256"]:
            case["solver_status"]="SOURCE_SHA256_MISMATCH";results.append(case);continue
        for engine in ("cadical195","glucose4"):
            cmd=[sys.executable,str(Path(__file__).resolve()),
                 "--child",str(path),"--engine",engine,
                 "--n",str(row["n_variables"]),"--m",str(row["n_clauses"])]
            began=perf_counter()
            try:
                child=subprocess.run(cmd,text=True,capture_output=True,
                                     timeout=per_solver_wall_s,check=False)
                if child.returncode:
                    entry=classify_nonzero_exit(child.returncode)
                    entry.update({"return_code":child.returncode,
                                  "stderr_tail":child.stderr[-800:]})
                else:
                    entry=json.loads(child.stdout)
            except subprocess.TimeoutExpired:
                entry={"verdict":"UNKNOWN_WALL_TIMEOUT"}
            except Exception as exc:
                entry={"verdict":"ENGINE_EXCEPTION","error_type":type(exc).__name__}
            entry["end_to_end_child_wall_seconds"]=perf_counter()-began
            case["solver_results"][engine]=entry
        results.append(case)
        print("BENCH",case["family"],case["solver_results"]["cadical195"]["verdict"],
              case["solver_results"]["glucose4"]["verdict"],flush=True)
    report={
      "schema":"JANUS-TIME-SAT-004B-BOUNDED-RAW-CDCL-SCREEN-V1",
      "status":"EXTERNAL_ORIGIN_PUBLIC_NOT_BLINDED_NO_ALGORITHM_PROMOTION",
      "inputs_manifest":source["schema"],
      "candidate_count":len(results),
      "solvers":["CaDiCaL195","Glucose4"],
      "limits":{"child_wall_seconds":per_solver_wall_s,"RLIMIT_AS_bytes":2_147_483_648,
                "RLIMIT_CPU_seconds":16,
                "max_parallel_workers":1,"production_C023":"UNCHANGED"},
      "per_candidate":results,
      "negative_result_policy":"UNSAT without replayable original-CNF proof is solver-only; UNKNOWN never UNSAT",
      "external_blind":"NOT_PERFORMED",
    }
    (output/"screen.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SCREEN_SUMMARY",json.dumps({"candidate_count":len(results),"statuses":{
        r["family"]:[v.get("verdict") for v in r["solver_results"].values()]
        for r in results}},sort_keys=True),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path)
    p.add_argument("--child",type=Path)
    p.add_argument("--engine",choices=["cadical195","glucose4"])
    p.add_argument("--n",type=int)
    p.add_argument("--m",type=int)
    a=p.parse_args()
    if a.child:
        try:
            print(json.dumps(solve_one(a.child,a.engine,a.n,a.m),sort_keys=True))
        except (MemoryError,ValueError) as exc:
            print(json.dumps({"verdict":"ENGINE_RESOURCE_OR_VALIDATION_REJECT","error_type":type(exc).__name__}))
    else:
        bounded_parent(a.out)
