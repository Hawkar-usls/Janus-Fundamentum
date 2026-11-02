#!/usr/bin/env python3
"""004E4 research aggregator — separate same-admin VM, 24 original worker receipts.
No external independent witness, no hidden tests, no unconditional global champion.
"""
from __future__ import annotations
from collections import Counter
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e4_transfer as m

HOSTS=("ubuntu-22.04","ubuntu-24.04")

def audit(folder):
    p=m.frozen()
    expected={f+"__"+v+"__"+host+".json" for f in m.CASES
              for v in m.VARIANTS for host in HOSTS}
    found={x.name for x in folder.glob("*.json")}
    if found!=expected:
        raise AssertionError("004E4 original worker artifacts missing/foreign: "+
                             repr({"missing":sorted(expected-found),"extra":sorted(found-expected)}))
    source_sha={};detail={};sources=set();run_ids=set();heads=set()
    total=0;sat=0;censored=0;solver_only_unsat=0
    for file in sorted(folder.glob("*.json")):
        a=json.loads(file.read_text())
        f,v,host=file.stem.split("__")
        if (a.get("schema")!="JANUS-TIME-SAT-004E4-FOUR-OTHER-PUBLIC-SOURCE-PAIRED-MATRIX-V1"
            or (a["family"],a["variant"],a["runner_os"])!=(f,v,host)
            or a["precommitted_policy_git_blob"]!=m.PRE_BLOB
            or a["original_CNF_SHA256"]!=m.CASES[f][4]
            or a["CPU_soft_seconds"]!=m.CPU or a["wall_seconds"]!=m.WALL
            or a["RLIMIT_AS_bytes"]!=m.MEM or a["paired_repetitions"]!=2
            or a["source_already_seen_elsewhere"] is not True
            or a["global_champion"]!="NOT_ESTABLISHED"
            or a["production_C023"]!="UNCHANGED"):
            raise AssertionError("Untrusted original worker source or preregistration mismatch: "+file.name)
        run_ids.add(str(a["github_run_id"]));heads.add(a["github_head"])
        if len(a["records"])!=4:raise AssertionError("Missing original worker child")
        byrole={};bycount=Counter()
        for rep in (0,1):
            pair=[x for x in a["records"] if x["repeat"]==rep]
            if len(pair)!=2 or {x["role"] for x in pair}!={"candidate","raw_baseline"}:
                raise AssertionError("Original paired role invalid")
            if any(set(x["pair_order"])!={"candidate","raw_baseline"} for x in pair):
                raise AssertionError("Original arm randomization broken")
            for x in pair:
                status=x["result"].get("status")
                if status not in m.ALLOWED:
                    raise AssertionError("Unreported worker error "+repr(x))
                if x["actual_variant"]!=(v if x["role"]=="candidate" else "raw_cms"):
                    raise AssertionError("Paired challenger mutated")
                if x["full_cold_wall_seconds"]<0:
                    raise AssertionError("Negative full cold cost")
                if status==m.SAT:
                    if (x["result"].get("original_CNF_SHA256")!=m.CASES[f][4]
                        or x["result"].get("all_SAT_models_original_full_replay") is not True
                        or x["result"]["family"]!=f
                        or x["result"]["original_clauses"]!=m.CASES[f][2]):
                        raise AssertionError("SAT without source-bound full model replay")
                    if f=="p-center":raise AssertionError("SAT contradictory to archived original P-center UNSAT")
                    sat+=1
                if status in ("UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT"):
                    censored+=1
                if status=="UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF":
                    if f=="lights-out":
                        raise AssertionError("UNSAT contradicts verified source SAT model")
                    solver_only_unsat+=1
                byrole.setdefault(x["role"],Counter())[status]+=1
                bycount[status]+=1
                total+=1
        source_sha[file.name]=sha256(file.read_bytes()).hexdigest()
        detail[file.stem]={"candidate":dict(byrole["candidate"]),
                           "raw":dict(byrole["raw_baseline"]),
                           "all_statuses":dict(bycount),
                           "no_finite_speed_ratio_when_censored":True}
    if total!=96 or len(run_ids)!=1 or len(heads)!=1 or len(source_sha)!=24:
        raise AssertionError("All 24 external matrix jobs and exactly 96 trials mandatory")
    return {
      "schema":"JANUS-TIME-SAT-004E4-FOUR-OTHER-KNOWN-PUBLIC-FAMILIES-AUDIT-V1",
      "result":"24_RESEARCH_MATRIX_RECEIPTS_96_COLD_TRIALS_COLLECTED_NOT_BLIND",
      "original_CI_run_id":next(iter(run_ids)),
      "original_source_head":next(iter(heads)),
      "frozen_policy_blob":m.PRE_BLOB,
      "original_worker_records":24,
      "isolated_cold_child_processes":total,
      "original_verified_SAT":sat,
      "CPU_or_wall_unknown":censored,
      "solver_only_UNSAT_not_proven":solver_only_unsat,
      "original_cases_different_from_004E3_but_previously_observed":list(m.CASES),
      "original_case_sha256":{k:v[4] for k,v in m.CASES.items()},
      "hosts":list(HOSTS),"candidate_variants":list(m.VARIANTS),
      "all_outcomes":detail,"original_json_sha256":source_sha,
      "best_global_variant":"NOT_ESTABLISHED",
      "four_sources_all_public_and_seen_before":True,
      "no_external_blind_holdout":True,"independent_004C_witness":"OPEN",
      "no_finite_ratio_from_censored_baselines":True,
      "no_native_UNSAT_portable_proof":True,
      "C023_main":"UNCHANGED","no_paid_Rowans":True
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--evidence",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    obj=audit(a.evidence)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print("004E4_AGGREGATOR_PASS",json.dumps({
        "unique_original_workers":obj["original_worker_records"],
        "cold_children":obj["isolated_cold_child_processes"],
        "verified_SAT":obj["original_verified_SAT"],
        "CPU_OR_WALL_UNKNOWN":obj["CPU_or_wall_unknown"],
        "solver_only_UNSAT_NO_PROOF":obj["solver_only_UNSAT_not_proven"],
        "global_champion":"NOT_ESTABLISHED"},sort_keys=True))
