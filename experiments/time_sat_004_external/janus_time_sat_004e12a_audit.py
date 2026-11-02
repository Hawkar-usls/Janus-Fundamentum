#!/usr/bin/env python3
"""004E12A exact 16 VM/288 child source-locked same-admin audit."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12a_clause_order as m

def audit(receipts,lockpath):
    m.frozen()
    lock,locksha=m.checked_lock(lockpath)
    expected={case+"__"+os+".json" for case in m.IDS for os in m.HOSTS}
    found={f.name for f in receipts.glob("*.json")}
    if found!=expected:raise AssertionError("Missing/foreign original source VM receipts "+repr({
            "missing":sorted(expected-found),"foreign":sorted(found-expected)}))
    source={case:{v:m.transformed(case,v) for v in m.VARIANTS} for case in m.IDS}
    totals=Counter();byarm={};byvariant={};per_case={};all_ratios=[]
    runners=set();runs=set();heads=set();sha_records={}
    for path in sorted(receipts.glob("*.json")):
        case,os=path.stem.split("__")
        raw=path.read_bytes();j=json.loads(raw)
        if (j.get("schema")!="JANUS-TIME-SAT-004E12A-3-CLAUSE-ORDER-18-COLD-ORIGINAL-VM-V1"
            or j.get("case")!=case or j.get("original_OS")!=os
            or j.get("frozen_git_blob")!=m.BLOB
            or j.get("unmodified_E11_policy_blob")!=m.e.PLAN_BLOB
            or j.get("original_preworker_source_lock_sha")!=locksha
            or j.get("original_children")!=18
            or (j.get("CPU"),j.get("WALL"),j.get("MEM"))!=(m.CPU,m.WALL,m.MEM)
            or j.get("external_source_count")!=0 or j.get("C023_main")!="UNCHANGED"
            or len(j.get("records",[]))!=18):
            raise AssertionError("Original immutable scientific contract failed "+path.name)
        runners.add(j["original_runner_ID"]);runs.add(str(j["original_run_id"]));heads.add(j["original_HEAD"])
        bycase=per_case.setdefault(case,{})
        for variant in m.VARIANTS:
            pin=lock["sources_and_variant_decisions_preworker"][case][variant]
            s=source[case][variant]
            if pin["transformed_original_CNF_SHA256"]!=s["sha"]:
                raise AssertionError("Regenerated source SHA differs from original immutable preworker lock")
            subset=[x for x in j["records"] if x["variant"]==variant]
            if len(subset)!=6:raise AssertionError("Expected 6 complete original cold process records")
            bycase.setdefault(variant,Counter())
            for rep in range(2):
                rs=[r for r in subset if r["repeat"]==rep]
                if len(rs)!=3 or {r["arm"] for r in rs}!=set(m.ARMS):
                    raise AssertionError("Incomplete 3 frozen arm same VM comparison")
                if any(set(r["shuffled_arm_order"])!=set(m.ARMS) for r in rs):
                    raise AssertionError("Original method randomization plan corrupt")
                raw_arm=next(x for x in rs if x["arm"]=="raw_cms")
                for r in rs:
                    status=r["outcome"].get("status")
                    if status not in m.ALLOWED or not 0<r["total_cold_child_wall_s"]<m.WALL+5:
                        raise AssertionError("Unregistered/invalid original source child")
                    totals[status]+=1
                    byarm.setdefault(r["arm"],Counter())[status]+=1
                    byvariant.setdefault(variant,Counter())[status]+=1
                    bycase[variant][r["arm"]+"__"+status]+=1
                    o=r["outcome"]
                    if status==m.SAT:
                        if (o.get("case")!=case or o.get("variant")!=variant or o.get("arm")!=r["arm"]
                           or o.get("original_E11_source_SHA256")!=s["base_SHA256"]
                           or o.get("transformed_original_CNF_SHA256")!=s["sha"]
                           or o.get("original_complete_SAT_model_SHA256")!=s["model_sha"]
                           or o.get("original_preworker_SOURCE_LOCK_SHA256")!=locksha
                           or o.get("E11_policy_source_Git_blob")!=m.e.PLAN_BLOB
                           or o.get("full_transformed_original_CNF_SAT_model_replay")!="PASS"):
                            raise AssertionError("False or unverified original-CNF SAT output")
                        if r["arm"]=="unaltered_e11_prefix_certified":
                            if o["unmodified_E11_predecision"]["decision"]!=pin["expected_E11_prefix_choice"]:
                                raise AssertionError("Original frozen E11 prefix decision changed")
                    if (r["arm"]!="raw_cms" and status==m.SAT
                        and raw_arm["outcome"].get("status")==m.SAT):
                        all_ratios.append({"case":case,"variant":variant,"os":os,"repeat":rep,
                            "arm":r["arm"],
                            "raw_over_candidate":raw_arm["total_cold_child_wall_s"]/r["total_cold_child_wall_s"],
                            "candidate_full_wall_s":r["total_cold_child_wall_s"],
                            "raw_full_wall_s":raw_arm["total_cold_child_wall_s"]})
        sha_records[path.name]=sha256(raw).hexdigest()
    if len(runners)!=16 or len(runs)!=1 or len(heads)!=1 or sum(totals.values())!=288:
        raise AssertionError("Not 16 distinct original VMs /288 child receipts from one run/head")
    ratios={}
    for row in all_ratios:
        k=row["case"]+"__"+row["variant"]+"__"+row["arm"]
        ratios.setdefault(k,[]).append(row["raw_over_candidate"])
    grouped={k:{"completed_pairs":len(v),"median_raw_over_candidate":statistics.median(v),
                 "min":min(v),"max":max(v)} for k,v in ratios.items()}
    flips=[]
    for case in m.IDS:
        baseline=lock["sources_and_variant_decisions_preworker"][case]["as_emitted"]["expected_E11_prefix_choice"]
        for v in m.VARIANTS[1:]:
            new=lock["sources_and_variant_decisions_preworker"][case][v]["expected_E11_prefix_choice"]
            if new!=baseline:flips.append({"case":case,"variant":v,"original_decision":baseline,"new_decision":new,
                "original_SHA":source[case]["as_emitted"]["sha"],"reordered_SHA":source[case][v]["sha"]})
    return {"schema":"JANUS-TIME-SAT-004E12A-SOURCE-EQUIVALENT-CLAUSE-ORDER-16VM-288-ORIGINAL-AUDIT-V1",
      "status":"ORIGINAL_16_VM_288_CHILD_SOURCE_EQUIVALENCE_AUDITED",
      "original_science_run_id":next(iter(runs)),"original_science_HEAD":next(iter(heads)),
      "original_preregistered_Git_blob":m.BLOB,"unaltered_E11_policy_Git_blob":m.e.PLAN_BLOB,
      "original_source_lock_SHA256":locksha,"original_VM_count":16,"original_cold_children":288,
      "original_verdict_counts":dict(totals),
      "per_method_counts":{k:dict(v) for k,v in byarm.items()},
      "per_variant_counts":{k:dict(v) for k,v in byvariant.items()},
      "per_source_variant_arm_status_counts":{k:{v:dict(c) for v,c in vv.items()} for k,vv in per_case.items()},
      "precommitted_before_worker_E11_prefix_flips":flips,
      "flips_present":len(flips)>0,
      "all_original_24_transformed_source_SHA256":{case:{v:source[case][v]["sha"] for v in m.VARIANTS} for case in m.IDS},
      "all_original_source_model_SHA256":{case:source[case]["as_emitted"]["model_sha"] for case in m.IDS},
      "all_original_worker_JSON_SHA256":sha_records,
      "completed_same_VM_same_case_variant_RAW_vs_candidate_ratios":all_ratios,
      "grouped_finite_source_variant_ratios":grouped,
      "fully_completed_paired_count":len(all_ratios),
      "original_external_hidden_sources":0,"same_GitHub_owner_not_external_witness":True,
      "no_permutation_selected_after_outcomes":True,
      "no_E11_tuning":True,"global_champion":"NOT_ADMITTED",
      "C023_main":"UNCHANGED","004C":"OPEN","004F":"NOT_READY"}
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-receipts",type=Path,required=True)
    ap.add_argument("--source-lock",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    x=ap.parse_args()
    a=audit(x.original_receipts,x.source_lock)
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(a,sort_keys=True,indent=2)+"\n")
    print("004E12A_ORIGINAL_AUDIT_PASS",json.dumps({
      "VMs":16,"children":288,"outcomes":a["original_verdict_counts"],
      "prefix_decision_flips":len(a["precommitted_before_worker_E11_prefix_flips"]),
      "completed_finite_pairs":a["fully_completed_paired_count"],
      "external":0},sort_keys=True))
