#!/usr/bin/env python3
"""004D9B: preregistered tiny development paired cold SAT baselines.

All four arms are measured as fresh processes, including preprocessing,
import/initialization, SAT model replay, memory, CPU and wall timeout. Same
admin + synthetic fixtures are NEVER independent or generalizable evidence.
UNSAT without a portable independent proof is NOT counted as verified.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
from statistics import median
from time import perf_counter

HERE=Path(__file__).resolve().parent
DIRECT=HERE.parent / "direct"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(DIRECT))
from time_sat_004d9b_science_demo import cases
from janus_time_sat_004d4d_paged_support import extract_paged_mixed_xor
from janus_time_sat_004d7_rank_gate import source_rank_experiment
from janus_time_sat_004d8_sat_gate import certified_model

PROTOCOL=HERE/"TIME_SAT_004D9B_DEVELOPMENT_BENCHMARK_PROTOCOL.json"
PROTOCOL_GIT_BLOB="0b43de65770dda2397a3ec60d1a87b61bfb7e26a"
EXPECTED_ARMS=(
    "janus_resolution_plus_cms_native",
    "cryptominisat_original_cnf",
    "cryptominisat_native_source_xor",
    "cadical195_original_cnf",
)
SAT="SAT_VERIFIED_ORIGINAL_CNF"

def protocol():
    digest=subprocess.run(["git","hash-object",str(PROTOCOL)],text=True,
                          capture_output=True,check=True).stdout.strip()
    if digest!=PROTOCOL_GIT_BLOB:
        raise AssertionError("Frozen benchmark protocol Git blob mismatch")
    p=json.loads(PROTOCOL.read_text())
    if (p["schema"]!="JANUS-TIME-SAT-004D9B-FAIR-SOLVER-DEVELOPMENT-PROTOCOL-V1"
        or tuple(p["arms"])!=EXPECTED_ARMS
        or list(p["source_set"])!=list(cases())
        or p["prospective_external_source_allowlist"]
        or p["paired_repetitions"]!=3):
        raise AssertionError("Frozen benchmark experiment was changed")
    return p

def source_info(name):
    item=cases()[name]
    n,rows=item["n"],item["rows"]
    raw=json.dumps({"n":n,"rows":rows},sort_keys=True,separators=(",",":")).encode()
    return n,rows,sha256(raw).hexdigest()

def solver_cryptominisat(n, clauses, equations):
    import pycryptosat
    s=pycryptosat.Solver()
    for clause in clauses:
        s.add_clause(list(clause))
    for eq in equations:
        s.add_xor_clause(list(eq["variables"]), bool(eq["rhs"]))
    result,assignment=s.solve()
    if not result:
        return None,"UNSAT_UNVERIFIED_NO_PORTABLE_PROOF"
    signed=[i if (i<len(assignment) and assignment[i]) else -i
            for i in range(1,n+1)]
    return signed,None

def solver_cadical(n, clauses):
    from pysat.solvers import Cadical195
    with Cadical195(bootstrap_with=clauses) as s:
        if not s.solve():
            return None,"UNSAT_UNVERIFIED_NO_PORTABLE_PROOF"
        values=s.get_model()
    mapping={abs(v):v>0 for v in values if 1<=abs(v)<=n}
    signed=[i if mapping.get(i,False) else -i for i in range(1,n+1)]
    return signed,None

def cold_child(case,arm,expected_sha):
    # Resource bounds are defense-in-depth in addition to parent timeout.
    p=protocol()
    resource.setrlimit(resource.RLIMIT_CPU,(p["cpu_limit_seconds_per_child"],
                                            p["cpu_limit_seconds_per_child"]+1))
    resource.setrlimit(resource.RLIMIT_AS,(p["memory_limit_bytes"],p["memory_limit_bytes"]))
    started=perf_counter()
    n,rows,sha=source_info(case)
    if sha!=expected_sha:
        raise AssertionError("Input original SOURCE SHA mismatch")
    derived=[]
    explicit=[]
    if arm=="cadical195_original_cnf":
        model,problem=solver_cadical(n,rows)
    elif arm=="cryptominisat_original_cnf":
        model,problem=solver_cryptominisat(n,rows,[])
    else:
        cover=extract_paged_mixed_xor(rows,n)
        if cover["status"]!="SOURCE_PARTITION_VERIFIED":
            raise AssertionError("Failed exact source partition")
        explicit=cover["equations"]
        residual=cover["residual_clauses"]
        if arm=="janus_resolution_plus_cms_native":
            analysis=source_rank_experiment(rows,n)
            if analysis["status"]!="SOURCE_PROOF_REPLAY_AND_EXACT_GF2_RANK_PASS":
                raise AssertionError("JANUS proof/rank audit failed")
            derived=analysis["additional_parity_keys"]
        elif arm!="cryptominisat_native_source_xor":
            raise AssertionError("Unregistered arm")
        model,problem=solver_cryptominisat(n,residual,explicit+derived)
    if model is not None:
        replay=certified_model(rows,n,model)
        if replay["status"]!="SAT_VERIFIED_EVERY_ORIGINAL_CLAUSE":
            raise AssertionError("Solver model fails original source CNF")
        status=SAT
    else:
        status=problem or "UNKNOWN_NO_SAT_MODEL"
    elapsed=perf_counter()-started
    print(json.dumps({
        "case":case,"arm":arm,"original_source_sha256":sha,
        "status":status,"source_n":n,"source_clauses":len(rows),
        "source_original_verified_clauses":len(rows) if model is not None else None,
        "signed_model_sha256":sha256(json.dumps(model,separators=(",",":")).encode()).hexdigest()
                              if model is not None else None,
        "source_native_xor_equations":len(explicit),"JANUS_entailed_new_XOR_equations":len(derived),
        "child_full_wall_seconds":elapsed,
        "child_maxrss_KiB":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "independent_external_admin":"NO",
        "UNSAT_proof":"NOT_PRODUCED","C023":"UNCHANGED",
        "protocol_git_blob":PROTOCOL_GIT_BLOB
    },sort_keys=True),flush=True)

def run_benchmark(out):
    p=protocol()
    results=[]
    for case in p["source_set"]:
        n,rows,source_sha=source_info(case)
        for repetition in range(p["paired_repetitions"]):
            arms=list(EXPECTED_ARMS)
            random.Random(p["randomized_arm_order_seed"]+repetition+len(results)).shuffle(arms)
            for slot,arm in enumerate(arms):
                command=[sys.executable,str(Path(__file__).resolve()),"--child",
                         "--case",case,"--arm",arm,"--source-sha",source_sha]
                started=perf_counter()
                try:
                    result=subprocess.run(command,text=True,capture_output=True,
                                          timeout=p["wall_limit_seconds_per_child"])
                    if result.returncode==0:
                        r=json.loads(result.stdout)
                        if (r["case"]!=case or r["arm"]!=arm
                            or r["original_source_sha256"]!=source_sha
                            or r["protocol_git_blob"]!=PROTOCOL_GIT_BLOB):
                            raise AssertionError("Child receipt not source/protocol bound")
                    else:
                        r={"status":"ERROR_CHILD_EXIT","exit_code":result.returncode,
                           "stderr_tail":result.stderr[-1500:]}
                except subprocess.TimeoutExpired:
                    r={"status":"UNKNOWN_WALL_TIMEOUT_CENSORED"}
                results.append({"case":case,"repeat":repetition,"arm":arm,
                                "order":slot,"full_cold_parent_wall_seconds":perf_counter()-started,
                                "child":r})
    summary={}
    for case in p["source_set"]:
        arms={}
        for arm in EXPECTED_ARMS:
            items=[r for r in results if r["case"]==case and r["arm"]==arm]
            statuses=[r["child"]["status"] for r in items]
            complete=(len(items)==p["paired_repetitions"] and all(x==SAT for x in statuses))
            arms[arm]={
                "statuses":statuses,"all_sat_verified":complete,
                "median_full_cold_wall_seconds":median(x["full_cold_parent_wall_seconds"]
                                                        for x in items) if complete else None,
                "peak_rss_KiB":max((x["child"].get("child_maxrss_KiB",0) or 0)
                                     for x in items)
            }
        janus=arms[EXPECTED_ARMS[0]]
        others=[arms[x] for x in EXPECTED_ARMS[1:]]
        all_baselines=all(x["all_sat_verified"] for x in others)
        ratio=(min(x["median_full_cold_wall_seconds"] for x in others)/
               janus["median_full_cold_wall_seconds"]
               if janus["all_sat_verified"] and all_baselines else None)
        summary[case]={
            "arms":arms,"all_external_style_baselines_verified":all_baselines,
            "gain_vs_fastest_verified_baseline":ratio,
            "scientific_gate":"DEVELOPMENT_ONLY_NO_EXTERNAL_CLAIM",
            "meets_synthetic_gain_threshold_only":(ratio>=p["claim_min_gain_ratio"]) if ratio is not None else None,
            "censored_baselines_never_counted_as_wins":True
        }
    report={
        "schema":"JANUS-TIME-SAT-004D9B-FROZEN-DEVELOPMENT-PAIRED-FULL-COLD-V1",
        "protocol_blob":PROTOCOL_GIT_BLOB,
        "originals":[{"case":c,"sha256":source_info(c)[2]} for c in p["source_set"]],
        "platform":platform.platform(),"python":sys.version,
        "repetitions":p["paired_repetitions"],"arms":list(EXPECTED_ARMS),
        "raw_records":results,"summary":summary,
        "independent_external_custody":"NOT_OBTAINED",
        "no_science_promotion":True,"R6_frozen_failure":"NOT_OVERRIDDEN",
        "C023":"UNCHANGED"
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"SYNTHETIC_PAIRED_BENCHMARK_RECORDED",
                      "total_cold_runs":len(results),
                      "cases":{c:{"gain":v["gain_vs_fastest_verified_baseline"],
                                   "all_baselines_verified":v["all_external_style_baselines_verified"]}
                               for c,v in summary.items()}},sort_keys=True))

def main():
    q=argparse.ArgumentParser()
    q.add_argument("--child",action="store_true")
    q.add_argument("--case",choices=list(cases()))
    q.add_argument("--arm",choices=EXPECTED_ARMS)
    q.add_argument("--source-sha")
    q.add_argument("--out",type=Path)
    a=q.parse_args()
    if a.child:
        if not (a.case and a.arm and a.source_sha):
            q.error("Cold child requires case, arm and source SHA")
        cold_child(a.case,a.arm,a.source_sha)
    elif a.out:
        run_benchmark(a.out)
    else:
        q.error("Provide --out to run preregistered synthetic development cohort")
if __name__=="__main__":
    main()
