#!/usr/bin/env python3
"""Independent job, exact 20 original E7 VM receipts, 200 child statuses, no fabricated wins."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e7_transfer as m
from janus_time_sat_004e6_semantic_selector import normalized_selector

def audit(original):
    m.frozen()
    expected={f+"__"+state+"__"+os+".json"
              for f in m.FAMILIES for state in m.STATES for os in m.HOSTS}
    found={p.name for p in original.glob("*.json")}
    if expected!=found:
        raise AssertionError("Original E7 20-worker matrix is incomplete or contaminated: "+
          str({"missing":sorted(expected-found),"extra":sorted(found-expected)}))
    transforms={(f,s):m.materialize(f,s) for f in m.FAMILIES for s in m.STATES}
    original_run=set()
    original_HEAD=set()
    runner_names=set()
    counts=Counter()
    reports={}
    raw_sha={}
    for path in sorted(original.glob("*.json")):
        content=path.read_bytes()
        item=json.loads(content)
        if item.get("schema")!="JANUS-TIME-SAT-004E7-FIVE-SOURCE-FIVE-ARM-PRESEEN-TRANSFER-VM-V1":
            raise AssertionError("Unregistered original VM receipt")
        family,state,os=path.stem.split("__")
        if (item["family"],item["presentation_state"],item["runner_OS"])!=(family,state,os):
            raise AssertionError("Original E7 VM artifact filename and source identity differ")
        data=transforms[(family,state)]
        if (item["original_CNF_SHA256"]!=data["original_source_SHA256"] or
            item["transformed_original_CNF_SHA256"]!=data["CNF_SHA256"] or
            item["frozen_policy_git_blob"]!=m.FROZEN_BLOB or
            item["cold_trials"]!=10 or
            (item["CPU_soft_s"],item["WALL_s"],item["RLIMIT_AS_bytes"])!=(m.CPU,m.WALL,m.MEM) or
            item["no_promotion"] is not True or
            item["C023_main"]!="UNCHANGED" or
            len(item["records"])!=10):
            raise AssertionError("Altered scientific source, matrix, CPU budget, or deployment guard")
        original_run.add(str(item["github_run_id"]))
        original_HEAD.add(item["github_head"])
        runner_names.add(item["runner_name"])
        arms={}
        for arm in m.ARMS:
            trials=sorted([r for r in item["records"] if r["arm"]==arm],key=lambda r:r["repeat"])
            if len(trials)!=2 or [r["repeat"] for r in trials]!=[0,1]:
                raise AssertionError("Missing same-VM randomized arm repeat")
            arms[arm]=trials
        for rep in range(m.REPS):
            rows=[r for r in item["records"] if r["repeat"]==rep]
            if len(rows)!=5 or {r["arm"] for r in rows}!=set(m.ARMS) or any(
                set(r["randomized_five_arm_order"])!=set(m.ARMS) for r in rows):
                raise AssertionError("The original 5 arms were not randomized on the same VM")
        arm_summary={}
        for arm,records in arms.items():
            verified=0
            statuses=[]
            for row in records:
                o=row["outcome"]
                status=o.get("status")
                if status not in m.ALLOWED:raise AssertionError("Unallowed original child result")
                statuses.append(status);counts[status]+=1
                if status in {m.SAT,m.UNSAT}:
                    if (o["original_CNF_SHA256"]!=data["original_source_SHA256"] or
                        o["strict_transformed_original_CNF_SHA256"]!=data["CNF_SHA256"] or
                        o["arm"]!=arm):
                        raise AssertionError("Successful original SAT/UNSAT not bound to original CNF")
                    if status==m.SAT and o["SAT_check"]!="ALL_TRANSFORMED_SOURCE_CLAUSES_REPLAYED":
                        raise AssertionError("SAT outcome missing original source clause verification")
                    if status==m.UNSAT and o["UNSAT_check"]!="SOLVER_ONLY_NO_PORTABLE_CERTIFICATE":
                        raise AssertionError("UNSAT outcome was wrongly upgraded")
                if status==m.SAT:verified+=1
            arm_summary[arm]={
                "verified_original_clause_SAT":verified,
                "UNSAT_solver_only_no_portable_proof":statuses.count(m.UNSAT),
                "CPU_UNKNOWN":statuses.count("UNKNOWN_CPU_LIMIT_SIGXCPU"),
                "WALL_UNKNOWN":statuses.count("UNKNOWN_WALL_TIMEOUT"),
                "median_full_cold_wall_only_if_both_verified_SAT":(
                    statistics.median(x["full_cold_child_wall_seconds"] for x in records)
                    if verified==2 else "UNDEFINED_NOT_BOTH_SAT"),
                "both_child_verdicts":statuses
            }
        reports[path.stem]=arm_summary
        raw_sha[path.name]=sha256(content).hexdigest()
    if len(original_run)!=1 or len(original_HEAD)!=1 or len(runner_names)!=20:
        raise AssertionError("Mixed original run/HEAD or not twenty distinct ephemeral workers")
    features={}
    for family in m.FAMILIES:
        for state in m.STATES:
            data=transforms[(family,state)]
            new=normalized_selector(data["rows"],data["n"],"new_semantic80")
            old=normalized_selector(data["rows"],data["n"],"old_adaptive80")
            full=normalized_selector(data["rows"],data["n"],"native_all")
            features[family+"__"+state]={
                "source_SHA256":data["original_source_SHA256"],
                "equivalent_CNF_SHA256":data["CNF_SHA256"],
                "source_original_clause_count":data["original_source_clauses"],
                "tautology_padding":data["added_tautologies"],
                "duplicate_padding":data["added_duplicate_original_clauses"],
                "new_selector_choice":new["choice"],
                "old_selector_choice":old["choice"],
                "native_all_source_XOR_count":len(full["equations"]),
                "new_selector_XOR_count":len(new["equations"]),
                "new_selector_normalization_and_coverage":new["metric"],
                "old_selector_fraction":old["metric"]["fraction"],
                "original_truth":"UNVERIFIED_NO_ORIGINAL_COMPLETE_SAT_MODEL_OR_PORTABLE_UNSAT_PROOF_REGISTERED"
            }
    return {
      "schema":"JANUS-TIME-SAT-004E7-FIVE-OTHER-PUBLIC-FAMILIES-20-VM-SOURCE-AUDIT-V1",
      "scientific_status":"SOURCE_SHA_BOUND_20_VM_200_CHILD_COST_TRANSFER_NOT_EXTERNAL_BLIND",
      "original_GitHub_run":next(iter(original_run)),
      "original_GitHub_HEAD":next(iter(original_HEAD)),
      "preregistered_policy_Git_blob":m.FROZEN_BLOB,
      "original_distinct_VM_names":20,
      "original_VM_receipts":20,
      "original_full_cold_children":sum(counts.values()),
      "verdict_counts":dict(counts),
      "by_family_presentation_host_arms":reports,
      "structural_feature_stability":features,
      "original_worker_receipt_sha256":raw_sha,
      "hidden_new_external_cases":0,
      "SAT_validation":"Every solved candidate model replayed against exact original (possibly trivially padded) source CNF.",
      "UNSAT_validation":"No portable proof produced; all solver UNSAT remain solver-only.",
      "scientific_limit":"Five OTHER but PREVIOUSLY SEEN sources; arbitrary tautological/duplicate padded encodings are not independent SATComp source problems. No trained-on-benchmark general champion.",
      "auto_production_promotion":False,
      "C023_main":"UNCHANGED",
      "004C_external_Witness":"OPEN"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-receipts",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.original_receipts)
    if result["original_full_cold_children"]!=200:
        raise AssertionError("Frozen E7 original expected 200 bounded children")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004E7_INDEPENDENT_SOURCE_AUDIT_PASS",json.dumps({
      "workers":result["original_VM_receipts"],
      "children":result["original_full_cold_children"],
      "outcomes":result["verdict_counts"],"hidden_cases":0},sort_keys=True))
