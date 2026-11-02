#!/usr/bin/env python3
"""004E3 external job evidence sweep. Fail if any of the 24 original jobs missing.

Does NOT claim 24 concurrently running VMs or an unseen test. Winner is a
within-source DEVELOPMENT completion lead only; no post-hoc auto promotion.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e3_swarm as worker

SAT=worker.SAT
ACCEPTED={SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT",
          "UNKNOWN_SOLVER_NO_ANSWER","UNSAT_SOLVER_ONLY_NO_PORTABLE_PROOF"}

def scan(evidence):
    p=worker.frozen()
    if not evidence.is_dir():raise AssertionError("Missing original GitHub Actions artifacts")
    expected={family+"__"+variant+".json"
              for family in worker.NAMES for variant in worker.VARIANTS}
    actual={x.name for x in evidence.glob("*.json")}
    if actual!=expected:
        raise AssertionError("Missing or extra matrix worker evidence: "+
            repr({"missing":sorted(expected-actual),"extra":sorted(actual-expected)}))
    records={}
    original_file_sha={}
    run_ids=set()
    heads=set()
    for path in sorted(evidence.glob("*.json")):
        raw=path.read_bytes();file=json.loads(raw)
        if file.get("schema")!="JANUS-TIME-SAT-004E3-PAIRED-VARIANT-VM-ORIGINAL-CNF-V1":
            raise AssertionError("Incorrect job receipt schema")
        fam,variant=path.stem.split("__")
        if (file["family"],file["variant"])!=(fam,variant):
            raise AssertionError("Matrix candidate identity differs from artifact file")
        i=worker.NAMES.index(fam)
        exp=worker.CASES[i][2]
        if (file["original_CNF_SHA256"]!=exp
            or file["frozen_git_blob"]!=worker.FREEZE_BLOB
            or len(file["records"])!=4
            or file["paired_repetitions"]!=2
            or file["child_CPU_s"]!=6
            or file["no_production_promotion"] is not True
            or file["no_independent_holdout"] is not True):
            raise AssertionError("Incompatible source SHA, immutable research contract or paired arm count")
        run_ids.add(str(file["github_run_id"]))
        heads.add(file["github_head"])
        for rep in (0,1):
            sub=[r for r in file["records"] if r["repeat"]==rep]
            if len(sub)!=2 or {r["role"] for r in sub}!={"candidate","raw_baseline"}:
                raise AssertionError("Each original VM must compare candidate with raw on same VM")
            if any(set(r["randomized_pair_order"])!={"candidate","raw_baseline"} for r in sub):
                raise AssertionError("Paired randomized order incorrect")
        for row in file["records"]:
            o=row["outcome"]
            if o.get("status") not in ACCEPTED:
                raise AssertionError("Unexpected failure or unregistered verdict "+str(o))
            if o["status"]==SAT:
                if (o.get("original_SHA256")!=exp or
                    o.get("original_model_verified") is not True or
                    o.get("family")!=fam or
                    o.get("source_n")!=worker.CASES[i][3]):
                    raise AssertionError("SAT success without original-source model verification")
            if row["full_cold_child_wall_seconds"]<0:
                raise AssertionError("Negative timing")
        original_file_sha[path.name]=sha256(raw).hexdigest()
        records[(fam,variant)]=file
    if len(run_ids)!=1 or len(heads)!=1:
        raise AssertionError("Worker original run/HEADs differ, cannot aggregate")
    # Parent run ID only, scientific conclusion still only one development cohort.
    per_family={}
    for family in worker.NAMES:
        options={}
        for variant in worker.VARIANTS:
            file=records[(family,variant)]
            cand=[r for r in file["records"] if r["role"]=="candidate"]
            raw=[r for r in file["records"] if r["role"]=="raw_baseline"]
            sc=sum(x["outcome"]["status"]==SAT for x in cand)
            sb=sum(x["outcome"]["status"]==SAT for x in raw)
            pairwise=[]
            if sc==2 and sb==2:
                for repeat in (0,1):
                    q=next(x for x in cand if x["repeat"]==repeat)
                    t=next(x for x in raw if x["repeat"]==repeat)
                    pairwise.append(t["full_cold_child_wall_seconds"]/q["full_cold_child_wall_seconds"])
            options[variant]={
                "candidate_model_verified_SAT":sc,
                "paired_raw_model_verified_SAT":sb,
                "candidate_verdict_counts":dict(Counter(x["outcome"]["status"] for x in cand)),
                "paired_raw_verdict_counts":dict(Counter(x["outcome"]["status"] for x in raw)),
                "candidate_median_cold_wall_seconds_IF_ALL_COMPLETED":(
                    statistics.median(x["full_cold_child_wall_seconds"] for x in cand)
                    if sc==2 else "UNDEFINED_CENSORED"),
                "paired_same_vm_finite_ratio_if_both_finish":(
                    statistics.median(pairwise) if len(pairwise)==2
                    else "UNDEFINED_ANY_CENSORED"),
                "no_global_production_promotion":True
            }
        best=max(v["candidate_model_verified_SAT"] for v in options.values())
        winners=[k for k,v in options.items()
                 if v["candidate_model_verified_SAT"]==best and best>0]
        per_family[family]={
            "outcome_per_variant":options,
            "highest_verified_completion_count":best,
            "development_completion_leaders_only":winners,
            "global_winner":"NOT_ESTABLISHED",
            "raw_baseline_correctly_censored_where_applicable":True
        }
    return {
        "schema":"JANUS-TIME-SAT-004E3-24-MATRIX-JOBS-VERIFIED-RESEARCH-AUDIT-V1",
        "scientific_status":"24_SEPARATE_JOB_RECEIPTS_COMPLETE_PRESEEN_DEVELOPMENT_NO_BLIND_WINNER",
        "original_GitHub_run_id":list(run_ids)[0],
        "original_head_SHA":list(heads)[0],
        "immutable_prereg_git_blob":worker.FREEZE_BLOB,
        "requested_matrix_jobs":24,
        "verified_unique_candidate_case_pairs":len(records),
        "verified_cold_child_trials":sum(len(a["records"]) for a in records.values()),
        "requested_parallel_cap":p["plan"]["maximum_simultaneously_requested"],
        "observed_parallel_simultaneous_VMs":"NOT_ESTABLISHED_BY_ARTIFACTS_ONLY_USE_GITHUB_JOBS_TIMESTAMPS",
        "all_sources_already_public_seen":True,
        "fully independent external holdout":"NOT_PERFORMED",
        "per_family":per_family,
        "original_job_receipt_sha256":original_file_sha,
        "prevent_promotion":True,
        "independent_004C_Witness":"OPEN","production_C023_main":"UNCHANGED",
        "note":"24 separate GitHub jobs are not 24 independent hidden sources and do not necessarily run concurrently; ranking is engineering-only with original source-model verification."
    }

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--evidence",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=scan(args.evidence)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("004E3_SCIENCE_AUDIT_PASS",json.dumps({
        "original_matrix_jobs":result["verified_unique_candidate_case_pairs"],
        "original_child_trials":result["verified_cold_child_trials"],
        "external_holdout":False,
        "production_promotion":False},sort_keys=True))
