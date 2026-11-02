#!/usr/bin/env python3
"""Research-only independent same-administration source original model & cost audit."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e11_parity_probe as m

def audit(directory,lock_path):
    m.frozen()
    lock,locksha=m.checked_lock(lock_path)
    expected={c+"__"+os+".json" for c in m.IDS for os in m.HOSTS}
    found={p.name for p in directory.glob("*.json")}
    if found!=expected:
        raise AssertionError("E11 original matrix missing/foreign original VM receipts: "+str({
            "missing":sorted(expected-found),"foreign":sorted(found-expected)}))
    sources={case:m.source(case) for case in m.IDS}
    original_runs=set();heads=set();runners=set();counts=Counter()
    per_source={};per_worker={};receipt_hashes={};completed_pairs=[];predictions={}
    for p in sorted(directory.glob("*.json")):
        case,os=p.stem.split("__")
        raw=p.read_bytes();j=json.loads(raw);s=sources[case]
        if (j.get("schema")!="JANUS-TIME-SAT-004E11-7-ARM-14-COLD-CHILD-ORIGINAL-GITHUB-VM-V1"
            or j["case"]!=case or j["original_os"]!=os
            or j["original_CNF_SHA256"]!=s["sha"]
            or j["complete_SAT_model_SHA256"]!=s["model_sha"]
            or j["frozen_protocol_git_blob"]!=m.PLAN_BLOB
            or j["old_trained_model_SHA256"]!=m.OLD_MODEL_SHA
            or j["preworker_lock_sha"]!=locksha
            or j["source_is_new_internal"]!=(case in m.NEW)
            or j["external_hidden_sources"]!=0
            or j["C023_main"]!="UNCHANGED"
            or (j["CPU_s"],j["WALL_s"],j["MEM"])!=(m.CPU,m.WALL,m.MEM)
            or j["cold_children"]!=14 or len(j["records"])!=14):
            raise AssertionError("Source/model/cost/matrix guard invalid on "+p.name)
        original_runs.add(str(j["original_run_id"]))
        heads.add(j["original_head"]);runners.add(j["original_runner_name"])
        armcounts=Counter()
        for repeat in (0,1):
            subset=[x for x in j["records"] if x["repeat"]==repeat]
            if (len(subset)!=7 or {x["arm"] for x in subset}!=set(m.ARMS)
                or any(set(x["shuffled_order"])!=set(m.ARMS) for x in subset)):
                raise AssertionError("Missing/duplicated original same-worker 7-arm comparison")
            original=next(x for x in subset if x["arm"]=="raw_cms")
            for row in subset:
                o=row["outcome"];status=o.get("status")
                if status not in m.ALLOWED:raise AssertionError("Unknown non-source-verified child")
                if not 0<row["full_cold_child_wall_seconds"]<m.WALL+4:
                    raise AssertionError("Invalid full cold measured cost")
                counts[status]+=1;armcounts[(row["arm"],status)]+=1
                if status==m.SAT and (o["original_CNF_SHA256"]!=s["sha"]
                    or o["complete_model_SHA256"]!=s["model_sha"]
                    or o["source_lock_SHA256"]!=locksha
                    or o["original_SAT_model_verified"]!="PASS"):
                    raise AssertionError("Unverified source/model or precommitted SHA")
                if row["arm"]=="e11_prefix_certified" and status==m.SAT:
                    predictions.setdefault(case,[]).append(o["source_only_decision"])
                if (row["arm"]!="raw_cms" and status==m.SAT
                    and original["outcome"]["status"]==m.SAT):
                    completed_pairs.append({
                        "case":case,"family":s["family"],"ubuntu":os,
                        "repeat":repeat,"arm":row["arm"],
                        "source_IS_new_internal":case in m.NEW,
                        "full_cold_raw_wall_seconds":original["full_cold_child_wall_seconds"],
                        "full_cold_candidate_wall_seconds":row["full_cold_child_wall_seconds"],
                        "raw_over_candidate":original["full_cold_child_wall_seconds"]/
                              row["full_cold_child_wall_seconds"]
                    })
        per_worker[p.stem]={arm:{
            "verified_SAT":armcounts[(arm,m.SAT)],
            "UNKNOWN_CPU":armcounts[(arm,"UNKNOWN_CPU_LIMIT_SIGXCPU")],
            "UNKNOWN_WALL":armcounts[(arm,"UNKNOWN_WALL_TIMEOUT")]
            } for arm in m.ARMS}
        receipt_hashes[p.name]=sha256(raw).hexdigest()
    if (len(original_runs)!=1 or len(heads)!=1 or len(runners)!=16
        or sum(counts.values())!=224):
        raise AssertionError("Mixed runs/HEAD or not exactly 16 independent GitHub VM receipts")
    for case in m.IDS:
        per_source[case]={
            "family":sources[case]["family"],
            "original_source_SHA256":sources[case]["sha"],
            "source_type":"NEW_INTERNAL_SYNTHETIC" if case in m.NEW else "PRESEEN_NEGATIVE_CONTROL",
            "arms":{arm:{
                "verified_SAT":sum(per_worker[case+"__"+os][arm]["verified_SAT"] for os in m.HOSTS),
                "UNKNOWN_CPU":sum(per_worker[case+"__"+os][arm]["UNKNOWN_CPU"] for os in m.HOSTS),
                "UNKNOWN_WALL":sum(per_worker[case+"__"+os][arm]["UNKNOWN_WALL"] for os in m.HOSTS)
            } for arm in m.ARMS}
        }
    grouped={}
    for r in completed_pairs:
        key=r["case"]+"__"+r["arm"]
        grouped.setdefault(key,[]).append(r["raw_over_candidate"])
    pairs={key:{
        "same_VM_completed_pairs":len(values),
        "median_raw_over_candidate":statistics.median(values),
        "min":min(values),"max":max(values)
    } for key,values in grouped.items()}
    return {
        "schema":"JANUS-TIME-SAT-004E11-SOURCE-BOUND-16-VM-224-TRIAL-7-ARM-INDEPENDENT-SAME-ADMIN-AUDIT-V1",
        "status":"ORIGINAL_SHA_16_DISTINCT_GITHUB_VMS_224_CHILD_MODEL_VERIFIED",
        "original_source_run_id":next(iter(original_runs)),
        "original_source_HEAD":next(iter(heads)),
        "frozen_git_blob":m.PLAN_BLOB,"preworker_source_lock_SHA256":locksha,
        "pretrained_E9_model_SHA256":m.OLD_MODEL_SHA,
        "original_VM_count":16,"original_cold_children":224,
        "all_outcomes":dict(counts),
        "source_group_count":8,"new_internal_originals":6,
        "new_internal_generator_families":3,"preseen_negative_controls":2,
        "per_original_CNF":per_source,
        "original_VM_by_arm":per_worker,
        "original_VM_receipt_sha256":receipt_hashes,
        "prefix_policy_original_predictions":predictions,
        "completed_same_source_same_VM_pairs":completed_pairs,
        "completed_pair_count":len(completed_pairs),
        "grouped_finite_ratios_ONLY_COMPLETED":pairs,
        "source_independence_warning":"New PARITY topologies are JANUS-built and previously seen Lights-out has related cross-grid structure. Pairs on two Ubuntu repeat same exact CNF, not independent external data.",
        "global_champion":"NOT_ADMITTED",
        "004C_external_custodian":"OPEN",
        "production_C023_main":"UNCHANGED",
        "paid_Rowan_NAS":"NONE"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--receipts",type=Path,required=True)
    p.add_argument("--source-lock",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=audit(a.receipts,a.source_lock)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("004E11_SOURCE_AUDIT_PASS",json.dumps({
        "16_VMs":r["original_VM_count"],"children":224,
        "outcomes":r["all_outcomes"],"completed_pairs":r["completed_pair_count"]},sort_keys=True))
