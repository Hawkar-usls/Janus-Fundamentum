#!/usr/bin/env python3
"""JANUS TIME-SAT-004D0: bounded original-CNF CNF-resolution preprocessing.

Not a universal new solver: this implements the previously tested JANUS-003
binary resolution plus original-CNF classical CDCL, WITHOUT old n<=240 cap.
Same original source clauses, solver, memory and CPU caps across raw,
feature_only, janus_direct, janus_frozen_forecast. For scientific feasibility
only; public fixed cases, no hidden test or new P=NP claim.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import resource
from time import perf_counter

ARMS=("raw","feature_only","janus_direct","janus_frozen_forecast")
MAX_SCAN_LITERALS=1_000_000
MAX_BINARY_ENTRIES=250_000
MAX_WITNESSES=8
RAM=2_147_483_648
CPU=6
# 003B coefficients preserved, not calibrated on these sources.
SAVE_PER_OCC=16
SCAN_PER_LIT=2
AUDIT_PER_UNIT_ROW=4
INSERT_PER_UNIT=8


def derive_binary_wedges(rows,n,*,max_scan=MAX_SCAN_LITERALS,max_entries=MAX_BINARY_ENTRIES):
    """A (a|b), (a|-b) -> a; original clause indexed, bounded scan.

    A failed scan returns NO units and leaves the original CNF untouched.
    This is NOT a global proof of absence of wedge structure.
    """
    seen={}
    witnesses={}
    occurrences={}
    scanned=0
    for idx,row in enumerate(rows):
        if scanned+len(row)>max_scan:
            return (),scanned,"SCAN_LITERAL_BUDGET",occurrences
        scanned+=len(row)
        for lit in row:
            if type(lit) is not int or lit==0 or abs(lit)>n:
                raise ValueError("original CNF literal is invalid")
            occurrences[abs(lit)]=occurrences.get(abs(lit),0)+1
        if len(row)!=2:continue
        a,b=row
        if a==b or a==-b:continue
        for shared,other in ((a,b),(b,a)):
            key=(shared,abs(other),1 if other>0 else -1)
            opposite=(shared,abs(other),-key[2])
            prior=seen.get(opposite)
            if prior is not None and shared not in witnesses:
                first_index,companion=prior
                witnesses[shared]=(shared,first_index,idx,companion)
            if key not in seen:
                if len(seen)>=max_entries:
                    return (),scanned,"BINARY_INDEX_BUDGET",occurrences
                seen[key]=(idx,other)
    contradictory={abs(k) for k in witnesses if -k in witnesses}
    selected=tuple(witnesses[k] for k in sorted(witnesses,key=lambda x:(abs(x),x<0))
                   if abs(k) not in contradictory)[:MAX_WITNESSES]
    return selected,scanned,"COMPLETE",occurrences


def independently_replay_witnesses(rows,witnesses):
    """Independent 2-variable truth-table entailment, not a SAT solver API.

    Verify both ORIGINAL clauses by exact indices and that no assignment
    satisfies both parents while falsifying derived unit. Tampering aborts
    experiment; it is never silently accepted as a harmless timeout.
    """
    targets=set()
    for lit,i,j,b in witnesses:
        if type(lit) is not int or type(b) is not int or not lit or not b or abs(lit)==abs(b):
            raise AssertionError("invalid target or pivot")
        if not (0<=i<len(rows) and 0<=j<len(rows)) or i==j:
            raise AssertionError("invalid original clause index")
        if abs(lit) in targets:raise AssertionError("duplicate variable witness")
        targets.add(abs(lit))
        c1=set(rows[i]);c2=set(rows[j])
        if c1!={lit,b} or c2!={lit,-b}:
            raise AssertionError("forged source clause pair")
        variables=(abs(lit),abs(b))
        for bits in range(4):
            assignment={variables[0]:bool(bits&1),variables[1]:bool(bits&2)}
            satisfied=lambda clause:any(assignment[abs(x)]==(x>0) for x in clause)
            if satisfied(rows[i]) and satisfied(rows[j]) and not (assignment[abs(lit)]==(lit>0)):
                raise AssertionError("logical resolution counterexample")
    return len(witnesses)


def frozen_cost(n,m,witnesses,scanned,occ):
    count=len(witnesses)
    saved=SAVE_PER_OCC*sum(occ.get(abs(w[0]),0) for w in witnesses)
    cost=SCAN_PER_LIT*scanned+AUDIT_PER_UNIT_ROW*m*count+INSERT_PER_UNIT*count
    net=saved-cost
    return {"admit":bool(n>=64 and m>=128 and count and net>0),
            "estimated_saved_abstract_units":saved,"estimated_cost_abstract_units":cost,
            "estimated_net_abstract_units":net,
            "rule":"FROZEN_UNCALIBRATED_003B_NOT_MILLISECONDS"}


def run(rows,n,engine,arm):
    from pysat.solvers import Solver
    if arm not in ARMS:raise ValueError("unknown arm")
    start=perf_counter()
    witnesses=()
    count=0
    reason="NO_EXTRA_FEATURE_WORK"
    forecast=None
    audited=0
    selected=()
    if arm!="raw":
        witnesses,count,reason,occ=derive_binary_wedges(rows,n)
        if reason=="COMPLETE":
            audited=independently_replay_witnesses(rows,witnesses)
            if arm=="janus_direct":
                selected=tuple(w[0] for w in witnesses)
            elif arm=="janus_frozen_forecast":
                forecast=frozen_cost(n,len(rows),witnesses,count,occ)
                if forecast["admit"]:
                    selected=tuple(w[0] for w in witnesses)
        if reason!="COMPLETE":witnesses=()
    # Source CNF is never dropped, reduced, renumbered or modified.
    solver_started=perf_counter()
    with Solver(name=engine,bootstrap_with=rows) as solver:
        for lit in selected:solver.add_clause([lit]) # independently proved redundant
        answer=solver.solve()
        model=solver.get_model() if answer else None
        stats=solver.accum_stats()
    solver_elapsed=perf_counter()-solver_started
    if answer is None:raise AssertionError("unknown solver result is not SAT/UNSAT")
    if answer:
        assignment={abs(x):x>0 for x in model or ()}
        if not all(any(abs(l) in assignment and assignment[abs(l)]==(l>0)
                       for l in clause) for clause in rows):
            raise AssertionError("model fails ORIGINAL source CNF")
    return {"verdict":"SAT_ORIGINAL_MODEL_VERIFIED" if answer else "UNSAT_SOLVER_ONLY_NOT_CERTIFIED",
            "arm":arm,"engine":engine,
            "derived_units":list(selected),"source_pair_witness_count":len(witnesses),
            "independent_2clause_witness_checks":audited,
            "source_scan_literals":count,"scan_reason":reason,
            "forecast":forecast,
            "full_child_seconds":perf_counter()-start,
            "native_solver_seconds":solver_elapsed,
            "native_stats":stats,
            "peak_process_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "unsat_portable_proof":"NOT_PRODUCED",
            "safety_note":"DOES_NOT_USE_240_VAR_VALIDATED_OR_003_PREPARE"}

def run_file(path,n,m,engine,arm):
    from janus_time_sat_004b_baselines import read_cnf
    resource.setrlimit(resource.RLIMIT_AS,(RAM,RAM))
    resource.setrlimit(resource.RLIMIT_CPU,(CPU,CPU+1))
    rows=read_cnf(path,n,m)
    return run(rows,n,engine,arm)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--n",type=int,required=True)
    parser.add_argument("--m",type=int,required=True)
    parser.add_argument("--engine",choices=["cadical195","glucose4"],required=True)
    parser.add_argument("--arm",choices=ARMS,required=True)
    args=parser.parse_args()
    start=perf_counter()
    try:
        r=run_file(args.source,args.n,args.m,args.engine,args.arm)
        r["full_child_including_parse_seconds"]=perf_counter()-start
        print(json.dumps(r,sort_keys=True))
    except (MemoryError,ValueError) as exc:
        print(json.dumps({"verdict":"RESOURCE_OR_INPUT_REJECTION",
                          "exception":type(exc).__name__}))
