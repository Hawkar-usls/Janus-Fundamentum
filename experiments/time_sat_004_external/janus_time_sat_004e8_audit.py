#!/usr/bin/env python3
"""004E8 exact 16 VM / 160 original SAT-child evaluator; no false speedups."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e8_model_first as m

def audit(folder):
    p=m.freeze()
    expected={i+"__"+os+".json" for i in m.IDS for os in m.HOSTS}
    received={file.name for file in folder.glob("*.json")}
    if received!=expected:
        raise AssertionError("Missing or foreign scientific 004E8 VM receipt "+
            repr({"missing":sorted(expected-received),"extra":sorted(received-expected)}))
    sources={case:m.source(case) for case in m.IDS}
    runids=set();heads=set();runners=set()
    counts=Counter();by_source={};original_sha={}
    complete_pairs=[]
    for path in sorted(folder.glob("*.json")):
        case,os=path.stem.split("__")
        a=json.loads(path.read_text())
        src=sources[case]
        if (a.get("schema")!="JANUS-TIME-SAT-004E8-EIGHT-CASE-FIVE-ARM-COLD-PAIR-VM-V1"
            or a.get("case_id")!=case or a.get("original_ubuntu")!=os
            or a.get("frozen_manifest_blob")!=m.FROZEN_BLOB
            or a.get("original_source_sha256")!=src["sha"]
            or a.get("original_complete_model_sha256")!=src["model_sha"]
            or (a.get("original_n"),a.get("original_m"))!=(src["n"],src["m"])
            or a.get("source_model_verified_preflight") is not True
            or a.get("original_cold_children")!=10
            or (a.get("CPU_soft_s"),a.get("WALL_s"),a.get("RLIMIT_AS"))!=(m.CPU,m.WALL,m.MEM)
            or a.get("no_global_champion") is not True
            or a.get("new_hidden_sources")!=0
            or a.get("production_C023")!="UNCHANGED"):
            raise AssertionError("Corrupt source SHA/planted full model or policy for "+path.name)
        if len(a.get("records",[]))!=10:
            raise AssertionError("Missing original cold outcomes")
        runids.add(str(a["original_run_id"]))
        heads.add(a["original_head"])
        runners.add(a["original_runner_name"])
        per_arm={}
        for rep in (0,1):
            subset=[r for r in a["records"] if r["repeat"]==rep]
            if (len(subset)!=len(m.ARMS)
                or {r["arm"] for r in subset}!=set(m.ARMS)
                or any(set(r["shuffled_order"])!=set(m.ARMS) for r in subset)):
                raise AssertionError("Required all five original same-VM method comparisons")
            raw=next(r for r in subset if r["arm"]=="raw_cms")
            for row in subset:
                status=row["outcome"].get("status","MISSING")
                if status not in m.ALLOW:
                    raise AssertionError("Unregistered child failure: "+str(row))
                if not 0<row["full_cold_child_wall_seconds"]<m.WALL+4:
                    raise AssertionError("Full child process wall cost invalid")
                counts[status]+=1
                per_arm.setdefault(row["arm"],Counter())[status]+=1
                if status==m.SAT:
                    outcome=row["outcome"]
                    if (outcome.get("case")!=case
                        or outcome.get("arm")!=row["arm"]
                        or outcome.get("source_original_CNF_SHA256")!=src["sha"]
                        or outcome.get("source_complete_model_SHA256")!=src["model_sha"]
                        or outcome.get("original_full_SAT_model_pre_and_post")!="PASS"):
                        raise AssertionError("Returned SAT model not bound to the exact original SHA")
                if (row["arm"]!="raw_cms" and row["outcome"].get("status")==m.SAT
                    and raw["outcome"].get("status")==m.SAT):
                    complete_pairs.append({
                        "source_case":case,"ubuntu":os,"repeat":rep,
                        "candidate":row["arm"],
                        "candidate_full_cold_wall_s":row["full_cold_child_wall_seconds"],
                        "raw_original_full_cold_wall_s":raw["full_cold_child_wall_seconds"],
                        "raw_over_candidate_full_wall_ratio":raw["full_cold_child_wall_seconds"]/
                                                            row["full_cold_child_wall_seconds"]})
        by_source[path.stem]={arm:dict(c) for arm,c in per_arm.items()}
        original_sha[path.name]=sha256(path.read_bytes()).hexdigest()
    if (len(runids)!=1 or len(heads)!=1 or len(runners)!=16
        or len(by_source)!=16 or sum(counts.values())!=160):
        raise AssertionError("Not 16 distinct original workers / complete 160 cold results")
    by_arm={}
    for r in by_source.values():
        for arm,sts in r.items():
            counter=by_arm.setdefault(arm,Counter())
            counter.update(sts)
    completed_only=[r["raw_over_candidate_full_wall_ratio"] for r in complete_pairs]
    return {
        "schema":"JANUS-TIME-SAT-004E8-MODEL-VERIFIED-EIGHT-CASE-FIVE-ARM-16-VM-SOURCE-AUDIT-V1",
        "status":"COMPLETE_16_WORKERS_160_ORIGINAL_CHILD_VERDICTS_BUT_NO_EXTERNAL_HOLDOUT",
        "source_scientific_run_id":next(iter(runids)),
        "source_scientific_head":next(iter(heads)),
        "frozen_manifest_blob":m.FROZEN_BLOB,
        "original_workers":16,"original_children":160,
        "all_outcomes":dict(counts),
        "per_method_counts":{k:dict(v) for k,v in by_arm.items()},
        "per_source_host_method_counts":by_source,
        "original_complete_models_SHA_by_case":{k:v["model_sha"] for k,v in sources.items()},
        "original_source_SHA_by_case":{k:v["sha"] for k,v in sources.items()},
        "original_worker_receipt_SHA256":original_sha,
        "paired_same_vm_same_repeat_both_verified_SAT":complete_pairs,
        "completed_only_ratio_count":len(complete_pairs),
        "all_completed_pair_ratio_median_DESCRIPTIVE_ONLY":statistics.median(completed_only) if completed_only else None,
        "no_censored_speed_ratio":True,
        "no_cross_source_population_generalization":True,
        "synthetic_planted_cases":6,"previously_seen_public_competition_cases":2,
        "outside_independent_hidden_sources":0,
        "global_speedup_proved":False,"global_champion":"NOT_ESTABLISHED",
        "external_004C_witness":"OPEN","production_004F":"NOT_READY",
        "C023_main":"UNCHANGED"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    x=audit(a.in_dir)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print("004E8_ALL_SOURCE_AUDIT_PASS",json.dumps({
        "original_VM":16,"children":160,"SAT":x["all_outcomes"].get(m.SAT,0),
        "UNKNOWN":sum(v for k,v in x["all_outcomes"].items() if k.startswith("UNKNOWN")),
        "complete_raw_comparator_pairs":x["completed_only_ratio_count"],
        "independent_hidden_CNF":0},sort_keys=True))
