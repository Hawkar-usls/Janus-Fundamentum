#!/usr/bin/env python3
"""TIME-SAT-004E12C0 development-only audit, not a newly trained E12C gate.

Replays ALL exact archived original E12B 600 worker children. Enforces 20
source-matched workers, hashes, full original source/model provenance, and
reports CPU censoring and independent-source-group vs repeated-pair counts.
No SAT generation, no new holdout; zero production/model changes.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
from pathlib import Path
import statistics

ROOT=Path("experiments/time_sat_004_external/time_sat_004e12b_evidence")
ORIGINAL_RUN="41479552023"
ORIGINAL_SHA="5f09929a1bf715cfccdafce10755d85d4aa0cab1"
ORIGINAL_BLOB="04c79834b227b2b814aa305bcea0a9813e23ed26"
SAT="SAT_ORIGINAL_CNF_MODEL_VERIFIED"
CPU="UNKNOWN_CPU_LIMIT_SIGXCPU"
WALL="UNKNOWN_WALL_TIMEOUT"
ARMS=("e12b_support_index","unaltered_e11_prefix","native_all","raw_cms","cadical195_original")
VARIANTS=("as_emitted","global_clause_literal_shuffle","round_robin_support_literal_shuffle")
OS=("ubuntu-22.04","ubuntu-24.04")

def med(v):
    if not v: return None
    return statistics.median(v)

def describe(v):
    if not v:return {"n":0,"median":None,"min":None,"max":None,"IQR":None}
    s=sorted(v);k=len(s)//2
    lo=med(s[:k]) if len(s)>1 else s[0]
    hi=med(s[-k:]) if len(s)>1 else s[0]
    return {"n":len(v),"median":med(s),"min":s[0],"max":s[-1],
            "IQR":hi-lo,"Q1_Tukey":lo,"Q3_Tukey":hi}

def audit(root=ROOT):
    summary_data=(root/"SUMMARY.json").read_bytes()
    summary=json.loads(summary_data)
    prev=summary["original_science_independent_same_admin_reaudited"]
    if (summary["original_scientific_run"]!=int(ORIGINAL_RUN)
        or summary["original_scientific_HEAD"]!=ORIGINAL_SHA
        or prev["original_HEAD"]!=ORIGINAL_SHA
        or prev["frozen_protocol_git_blob"]!=ORIGINAL_BLOB
        or prev["original_cold_children"]!=600
        or prev["fully_completed_raw_candidate_pairs"]!=456
        or summary["original_GitHub_ZIP_count"]!=22):
        raise AssertionError("Not the immutable SHA-original E12B development archive")
    originals=prev["per_original_CNF"]
    source_cases=set(originals)
    if len(source_cases)!=10:raise AssertionError("Not 10 exactly known original SAT CNFs")
    expected={case+"__"+os+".json" for case in source_cases for os in OS}
    folder=root/"original-20-worker-JSON"
    seen={p.name for p in folder.glob("*.json")}
    if expected!=seen:raise AssertionError("Missing or untrusted worker receipts")
    workers=set();runs=set();heads=set()
    counts=Counter();by_method=defaultdict(Counter);by_family=defaultdict(Counter)
    by_case=defaultdict(Counter);by_variant=defaultdict(Counter)
    paired=defaultdict(list);components=defaultdict(lambda:defaultdict(list))
    all_matched=0
    for path in sorted(folder.glob("*.json")):
        buf=path.read_bytes()
        if sha256(buf).hexdigest()!=prev["all_receipt_SHA256"][path.name]:
            raise AssertionError("Original GitHub worker JSON SHA mismatch "+path.name)
        case,os=path.stem.split("__")
        j=json.loads(buf)
        if (j.get("schema")!="JANUS-TIME-SAT-004E12B-30-FROZEN-COLD-COST-ORIGINAL-VM-V1"
            or j.get("case")!=case or j.get("original_os")!=os
            or str(j.get("original_run_id"))!=ORIGINAL_RUN
            or j.get("original_HEAD")!=ORIGINAL_SHA
            or j.get("prereg_git_blob")!=ORIGINAL_BLOB
            or j.get("original_source_SHA256")!=originals[case]["original_CNF_SHA256"]
            or j.get("full_model_SHA256")!=originals[case]["complete_model_SHA256"]
            or len(j.get("records",[]))!=30):
            raise AssertionError("Source/model/job metadata mismatch "+path.name)
        workers.add(j["original_runner_name"]);runs.add(str(j["original_run_id"]));heads.add(j["original_HEAD"])
        for variant in VARIANTS:
            var_records=[r for r in j["records"] if r["variant"]==variant]
            for rep in (0,1):
                rows=[r for r in var_records if r["repeat"]==rep]
                if len(rows)!=5 or {r["arm"] for r in rows}!=set(ARMS):
                    raise AssertionError("Same-source same-VM 5 arms and repeats incomplete")
                raw=next(r for r in rows if r["arm"]=="raw_cms")
                for row in rows:
                    arm=row["arm"];o=row["outcome"];status=o.get("status")
                    if status not in (SAT,CPU,WALL):
                        raise AssertionError("Unknown worker termination misreported")
                    if not 0<row["full_cold_child_wall_s"]<21:
                        raise AssertionError("Unbounded/invalid full cold process time")
                    if status==SAT:
                        if (o.get("original_source_SHA256")!=originals[case]["original_CNF_SHA256"]
                            or o.get("transformed_original_CNF_SHA256")!=originals[case]["original_SHA_variants"][variant]
                            or o.get("complete_model_SHA256")!=originals[case]["complete_model_SHA256"]
                            or o.get("original_complete_SAT_model_replay")!="PASS"):
                            raise AssertionError("Invalid source SHA or full original model proof")
                        for k in ("solver_wall_s","full_source_analysis_wall_s","peak_RSS_KiB"):
                            if o.get(k) is None or o[k]<0:
                                raise AssertionError("No full native solver/index/RSS cost receipt")
                        group=(case,variant,arm)
                        components[group]["native_solver_s"].append(o["solver_wall_s"])
                        components[group]["index_or_analysis_s"].append(o["full_source_analysis_wall_s"])
                        components[group]["RSS_KiB"].append(o["peak_RSS_KiB"])
                        components[group]["full_cold_wall_s"].append(row["full_cold_child_wall_s"])
                    counts[status]+=1;by_method[arm][status]+=1
                    by_case[case][status]+=1
                    by_family[originals[case]["family"]][status]+=1
                    by_variant[variant][status]+=1
                    if arm!="raw_cms" and status==SAT and raw["outcome"].get("status")==SAT:
                        ratio=raw["full_cold_child_wall_s"]/row["full_cold_child_wall_s"]
                        paired[(case,variant,arm)].append(ratio);all_matched+=1
    if (len(workers),len(runs),len(heads),sum(counts.values()),all_matched)!=(20,1,1,600,456):
        raise AssertionError("Must retain exact 20 VM, one HEAD/run, 600 children and 456 fully comparable pairs")
    if counts!={SAT:576,CPU:24}:
        raise AssertionError("Unexpected original outcome stats; don't reinterpret censored")
    for arm in ARMS:
        if sum(by_method[arm].values())!=120:raise AssertionError("Method coverage drift")
    if by_method["cadical195_original"][CPU]!=24 or any(
        v[CPU] for k,v in by_method.items() if k!="cadical195_original"):
        raise AssertionError("CPU timeouts not all CaDiCaL")
    if {case:v[CPU] for case,v in by_case.items() if v[CPU]}!={"e12b-torus-g14":12,"e12b-torus-g18":12}:
        raise AssertionError("CPU censoring by source not 2 torus originals")
    condensed={}
    for (case,variant,arm),ratios in sorted(paired.items()):
        condensed.setdefault(case,{}).setdefault(variant,{})[arm]=describe(ratios)
    part={}
    for (case,variant,arm),fields in sorted(components.items()):
        if case=="e12b-circulant-n288":
            part.setdefault(variant,{})[arm]={k:describe(v) for k,v in fields.items()}
    benefit=list(paired[("e12b-circulant-n288","global_clause_literal_shuffle","e12b_support_index")])
    raw_pre=part["as_emitted"]["raw_cms"]["native_solver_s"]["median"]
    raw_post=part["global_clause_literal_shuffle"]["raw_cms"]["native_solver_s"]["median"]
    summary_out={
       "schema":"JANUS-TIME-SAT-004E12C0-SOURCE-STRATIFIED-REGRET-AND-COST-CONTROL-V1",
       "analysis_scope":"REPLAY_E12B_DEVELOPMENT_ARCHIVE_ONLY_NO_NEW_E12C_MODEL_OR_HOLDOUT",
       "source_E12B_run":ORIGINAL_RUN,"source_scientific_HEAD":ORIGINAL_SHA,
       "source_frozen_protocol_blob":ORIGINAL_BLOB,
       "source_original_SUMMARY_SHA256":sha256(summary_data).hexdigest(),
       "raw_originals":10,"source_presentations":30,
       "worker_VM":20,"cold_children":600,
       "source_SAT_verified":counts[SAT],"CPU_UNKNOWN":counts[CPU],
       "possible_paired_comparisons":480,"actual_completed_pairs":all_matched,
       "nonpaired_comparators_due_to_CPU_UNKNOWN":24,
       "RAW_baseline_self_comparisons_EXCLUDED":120,
       "CPU_UNKNOWN_by_source":{k:v[CPU] for k,v in by_case.items() if v[CPU]},
       "CPU_UNKNOWN_by_arm":{k:v[CPU] for k,v in by_method.items()},
       "CPU_UNKNOWN_by_variant":{k:v[CPU] for k,v in by_variant.items()},
       "CPU_UNKNOWN_by_family":{k:v[CPU] for k,v in by_family.items()},
       "source_grouped_paired_ratios_full_cold":condensed,
       "n288_component_breakdown_four_matched_cold_repeats":part,
       "n288_raw_solver_original_over_global_shuffle_median":raw_pre/raw_post,
       "n288_shuffled_raw_over_E12B":describe(benefit),
       "rules_for_future_E12C":{
         "baseline_RAW_is_not_a_candidate_pair":True,
         "source_group_not_worker_repeat_is_independence_unit":True,
         "report_4_repeats_median_min_max_Tukey_IQR_no_population_CI":True,
         "all_CPU_wall_limits_are_UNKNOWN":True,
         "predeclare_per_source_regret_and_>1.5x_slowdown_guard":True,
         "original_source_complete_SAT_replay_required":True,
         "order_invariant_method_choice_does_NOT_guarantee_order_invariant_payoff":True,
         "no_posthoc_new_holdout_claims":True},
       "external_custodian":"OPEN","E12C_candidate":"NOT_IMPLEMENTED",
       "C023_production":"UNCHANGED","no_paid_Rowan_or_owner_NAS_PC":True}
    return summary_out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=audit(args.root)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004E12C0_DEVELOPMENT_SOURCE_AUDIT_PASS",json.dumps({
       "source_originals":result["raw_originals"],"trials":result["cold_children"],
       "SAT":result["source_SAT_verified"],"UNKNOWN":result["CPU_UNKNOWN"],
       "paired":result["actual_completed_pairs"],
       "shuffled_n288_solver_RAW_speedup":result["n288_raw_solver_original_over_global_shuffle_median"]},sort_keys=True))
