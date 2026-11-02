#!/usr/bin/env python3
"""E12B strict original 20 VM x30 cold children source/model/cost auditor."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12b_support_index as m

def audit(folder,lockpath):
    lock,locksha=m.checked_lock(lockpath)
    m.frozen()
    expected={case+"__"+os+".json" for case in m.IDS for os in m.HOSTS}
    found={p.name for p in folder.glob("*.json")}
    if found!=expected:
        raise AssertionError("Missing or foreign worker: "+str({
            "missing":sorted(expected-found),"other":sorted(found-expected)}))
    runs=set();heads=set();runners=set();outcomes=Counter()
    names=set();per_source={};per_VM={};ratios=[];receipt_shas={}
    for path in sorted(folder.glob("*.json")):
        case,os=path.stem.split("__")
        raw=path.read_bytes();r=json.loads(raw)
        original=m.source(case)
        if (r.get("schema")!="JANUS-TIME-SAT-004E12B-30-FROZEN-COLD-COST-ORIGINAL-VM-V1"
            or (r.get("case"),r.get("original_os"))!=(case,os)
            or (r.get("original_source_SHA256"),r.get("full_model_SHA256"))!=
               (original["sha"],original["model_sha"])
            or r.get("preworker_lock_SHA256")!=locksha
            or r.get("prereg_git_blob")!=m.PREREG_BLOB
            or (r.get("repeats"),r.get("variants"),r.get("arms"),r.get("cold_children"))!=(2,3,5,30)
            or (r.get("CPU"),r.get("WALL"),r.get("MEM"))!=(m.CPU,m.WALL,m.MEM)
            or r.get("external_independent_sources")!=0
            or r.get("production_main")!="UNCHANGED"
            or len(r.get("records",[]))!=30):
            raise AssertionError("Wrong original SHA, model, original worker, or frozen budget: "+path.name)
        if not r["original_runner_name"] or r["original_runner_name"] in runners:
            raise AssertionError("Cannot prove 20 unique hosted VM runner receipts")
        runners.add(r["original_runner_name"]);runs.add(str(r["original_run_id"]))
        heads.add(r["original_HEAD"])
        worker_counts=Counter()
        for variant in m.VARIANTS:
            original_v=m.variant(case,variant)
            pin=lock["sources"][case][variant]
            if ((pin["original_source_SHA256"],pin["transformed_original_CNF_SHA256"],
                 pin["complete_original_SAT_model_SHA256"])!=
                (original_v["base_sha"],original_v["sha"],original_v["model_sha"])):
                raise AssertionError("Preworker original signed source/model SHA mismatch")
            for rep in range(2):
                subset=[x for x in r["records"] if x["variant"]==variant and x["repeat"]==rep]
                if (len(subset)!=5 or {z["arm"] for z in subset}!=set(m.ARMS)
                    or any(set(x["randomized_arm_order"])!=set(m.ARMS) for x in subset)):
                    raise AssertionError("5 distinct comparison arms randomized on same original VM missing")
                raw_control=next(z for z in subset if z["arm"]=="raw_cms")
                for z in subset:
                    o=z["outcome"];status=o.get("status")
                    if status not in m.ALLOWED or not 0<z["full_cold_child_wall_s"]<m.WALL+4:
                        raise AssertionError("Original subprocess error or invalid full cold wall")
                    worker_counts[(variant,z["arm"],status)]+=1
                    outcomes[status]+=1
                    if status==m.SAT:
                        if ((o.get("case"),o.get("variant"),o.get("arm"))!=
                            (case,variant,z["arm"])
                            or (o.get("original_source_SHA256"),o.get("transformed_original_CNF_SHA256"),
                                o.get("complete_model_SHA256"))!=
                               (original_v["base_sha"],original_v["sha"],original_v["model_sha"])
                            or o.get("preworker_source_lock_SHA256")!=locksha
                            or o.get("original_complete_SAT_model_replay")!="PASS"
                            or o.get("production_C023_main")!="UNCHANGED"):
                            raise AssertionError("Falsified SAT source/model proof or worker receipt")
                        if z["arm"]=="e12b_support_index" and (
                            o.get("predecision",{}).get("choice")!=pin["frozen_candidate_decision"]):
                            raise AssertionError("Source order decision differs from independent preworker lock")
                    if (z["arm"]!="raw_cms" and
                        status==m.SAT and raw_control["outcome"].get("status")==m.SAT):
                        ratios.append({"case":case,"family":original["family"],
                            "variant":variant,"repeat":rep,"os":os,"arm":z["arm"],
                            "raw_over_candidate":raw_control["full_cold_child_wall_s"]/
                                                  z["full_cold_child_wall_s"],
                            "raw_s":raw_control["full_cold_child_wall_s"],
                            "candidate_s":z["full_cold_child_wall_s"]})
        per_VM[path.stem]={v+"__"+arm:{
            "SAT":worker_counts[(v,arm,m.SAT)],
            "UNKNOWN_CPU":worker_counts[(v,arm,"UNKNOWN_CPU_LIMIT_SIGXCPU")],
            "UNKNOWN_WALL":worker_counts[(v,arm,"UNKNOWN_WALL_TIMEOUT")]
            } for v in m.VARIANTS for arm in m.ARMS}
        receipt_shas[path.name]=sha256(raw).hexdigest()
    if len(runners)!=20 or len(runs)!=1 or len(heads)!=1 or sum(outcomes.values())!=600:
        raise AssertionError("Not exactly 20 distinct VM one original run/HEAD 600 cold children")
    grouped={}
    for row in ratios:
        key=row["case"]+"__"+row["variant"]+"__"+row["arm"]
        grouped.setdefault(key,[]).append(row["raw_over_candidate"])
    ratio_summary={key:{"completed_pairs":len(vals),
                        "median_raw_over_candidate":statistics.median(vals),
                        "min":min(vals),"max":max(vals)} for key,vals in grouped.items()}
    for case in m.IDS:
        controls=[]
        for variant in m.VARIANTS:
            locked=lock["sources"][case][variant]
            controls.append(locked["frozen_candidate_decision"])
        if len(set(controls))!=1:raise AssertionError("Index classifier is order fragile")
        per_source[case]={"family":m.source(case)["family"],
            "original_CNF_SHA256":m.source(case)["sha"],
            "complete_model_SHA256":m.source(case)["model_sha"],
            "all_three_precommitted_permutations_same_decision":True,
            "frozen_predecision":controls[0],
            "original_SHA_variants":{v:lock["sources"][case][v]["transformed_original_CNF_SHA256"]
                                     for v in m.VARIANTS}}
    return {
      "schema":"JANUS-TIME-SAT-004E12B-STRICT-20-VM-600-CHILD-SOURCE-FROZEN-AUDIT-V1",
      "status":"ORIGINAL_ALL_20_VM_600_COLD_SOURCE_AND_COMPLETE_MODEL_RECEIPTS_VERIFIED",
      "original_run_id":next(iter(runs)),
      "original_HEAD":next(iter(heads)),
      "frozen_protocol_git_blob":m.PREREG_BLOB,
      "preworker_source_lock_SHA256":locksha,
      "distinct_VM_runner_names":20,
      "original_cold_children":600,
      "outcomes":dict(outcomes),
      "per_original_CNF":per_source,
      "per_worker":per_VM,
      "all_receipt_SHA256":receipt_shas,
      "fully_completed_raw_candidate_pairs":len(ratios),
      "same_VM_finite_pairs":ratios,
      "source_grouped_finite_pair_ratios":ratio_summary,
      "internal_synthetic_originals":10,"source_variants":30,
      "independent_external_custodian_originals":0,
      "global_champion":"NOT_ADMITTED",
      "C023_main":"UNCHANGED"
    }

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--receipts",required=True,type=Path)
    a.add_argument("--source-lock",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    opt=a.parse_args()
    result=audit(opt.receipts,opt.source_lock)
    opt.out.parent.mkdir(parents=True,exist_ok=True)
    opt.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("E12B_SCIENCE_AUDIT_PASS",json.dumps({
      "VMs":result["distinct_VM_runner_names"],"children":600,
      "statuses":result["outcomes"],"finite_pairs":result["fully_completed_raw_candidate_pairs"]
    },sort_keys=True))
