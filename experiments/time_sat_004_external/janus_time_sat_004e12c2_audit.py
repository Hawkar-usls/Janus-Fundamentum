#!/usr/bin/env python3
"""Source/model locked original E12C2 16 VM /576 cold child science auditor."""
from __future__ import annotations
import argparse,json,statistics,sys
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12c2_width6_no_probe as m

def audit(receipts,source_lock):
    m.frozen();lock,locksha=m.checked_lock(source_lock)
    expected={case+"__"+os+".json" for case in m.IDS for os in m.HOSTS}
    found={x.name for x in receipts.glob("*.json")}
    if found!=expected:raise AssertionError("Need exact original 16 worker receipts, no foreign files "+repr(expected-found))
    runners=set();runs=set();heads=set()
    counts=Counter();by_arm=defaultdict(Counter);by_case=defaultdict(Counter);by_family=defaultdict(Counter)
    worker_SHA={};pairs=defaultdict(list);result_pairs=[];decisions={}
    probe_c1=Counter()
    for fp in sorted(receipts.glob("*.json")):
        case,os=fp.stem.split("__");raw=fp.read_bytes();j=json.loads(raw)
        src=m.original(case)
        if (j.get("schema")!="JANUS-TIME-SAT-004E12C2-36-COLD-ORIGINAL-VM-V1"
            or (j.get("case"),j.get("original_os"))!=(case,os)
            or (j.get("original_source_sha"),j.get("source_model_sha"))!=(src["sha"],src["model_sha"])
            or j.get("prereg_git_blob")!=m.BLOB
            or j.get("source_lock_sha")!=locksha
            or (j.get("cold_children"),j.get("CPU"),j.get("WALL"),j.get("MEM"))!=(36,m.CPU,m.WALL,m.MEM)
            or j.get("outside_admin_sources")!=0
            or j.get("C023_main")!="UNCHANGED"
            or len(j.get("records",[]))!=36):
            raise AssertionError("Source original identity/deterministic worker receipt mismatched "+fp.name)
        runner=j["original_runner_name"]
        if not runner or runner in runners:raise AssertionError("Reused runner VM name")
        runners.add(runner);runs.add(str(j["original_run_id"]));heads.add(j["original_HEAD"])
        d=decisions.setdefault(case,{})
        for v in m.VARIANTS:
            s=m.variant(case,v)
            seal=lock["origins"][case][v]
            if ((seal["original_SHA256"],seal["original_variant_SHA256"],seal["complete_original_model_SHA256"])!=
                (s["base_sha"],s["sha"],s["model_sha"])):
                raise AssertionError("Original preworker source SHA changed")
            d[v]=seal["frozen_candidate_choice"]
            for rep in range(2):
                records=[x for x in j["records"] if x["variant"]==v and x["repeat"]==rep]
                if (len(records)!=6 or {x["arm"] for x in records}!=set(m.ARMS)
                    or any(set(x["random_arm_order"])!=set(m.ARMS) for x in records)):
                    raise AssertionError("Missing original complete six-arm cold trial")
                raw_base=next(x for x in records if x["arm"]=="raw_cms")
                prev=next(x for x in records if x["arm"]=="e12b_frozen_width5")
                for x in records:
                    arm=x["arm"];o=x["outcome"];status=o.get("status")
                    if status not in m.ALLOWED or not 0<x["full_cold_child_wall_s"]<m.WALL+5:
                        raise AssertionError("Unrecognized/unbounded original cold child outcome")
                    counts[status]+=1;by_arm[arm][status]+=1;by_case[case][status]+=1
                    by_family[src["family"]][status]+=1
                    if status==m.SAT:
                        if ((o.get("case"),o.get("variant"),o.get("arm"))!=(case,v,arm)
                            or (o.get("original_source_SHA256"),o.get("transformed_source_SHA256"),
                               o.get("original_complete_SAT_model_SHA256"))!=(
                                s["base_sha"],s["sha"],s["model_sha"])
                            or o.get("preworker_source_lock_SHA256")!=locksha
                            or o.get("original_complete_CNF_model_replay")!="PASS"
                            or o.get("C023_main")!="UNCHANGED"):
                            raise AssertionError("Source-SHA original SAT proof receipt missing")
                        if arm==m.ARMS[0]:
                            if (o.get("frozen_decision")!=seal["frozen_candidate_choice"]
                                or o.get("raw_probe_status")!="NOT_RUN"
                                or o.get("raw_probe_wall_s")!=0
                                or o.get("verified_native_XOR_equations",0)<0):
                                raise AssertionError("NEW C2 candidate drifted from prereg source choice or used pilot")
                        if arm=="e12c1_frozen_raw_pilot":
                            probe_c1[o["raw_probe_status"]]+=1
                        for key in ("source_index_wall_s","native_solver_wall_s","peak_RSS_KiB"):
                            if not isinstance(o.get(key),(int,float)) or o[key]<0:
                                raise AssertionError("Missing full source index/solver/RSS timing")
                    if (arm!="raw_cms" and status==m.SAT
                        and raw_base["outcome"].get("status")==m.SAT):
                        ratio=raw_base["full_cold_child_wall_s"]/x["full_cold_child_wall_s"]
                        pairs[(case,v,arm)].append(ratio)
                        result_pairs.append({"case":case,"variant":v,"os":os,"rep":rep,"arm":arm,
                          "raw_s":raw_base["full_cold_child_wall_s"],
                          "candidate_s":x["full_cold_child_wall_s"],
                          "RAW_over_candidate":ratio})
                    if (arm==m.ARMS[0] and status==m.SAT
                        and prev["outcome"].get("status")==m.SAT):
                        pairs[(case,v,"C2_OVER_E12B")].append(
                            prev["full_cold_child_wall_s"]/x["full_cold_child_wall_s"])
        worker_SHA[fp.name]=sha256(raw).hexdigest()
    if (len(runners),len(runs),len(heads),sum(counts.values()))!=(16,1,1,576):
        raise AssertionError("Not original 16 unique VMs, one exact run/head and all 576 children")
    for a in m.ARMS:
        if sum(by_arm[a].values())!=96:
            raise AssertionError("One baseline/model arm did not run 96 original trials")
    if any(len(set(choices.values()))!=1 for choices in decisions.values()):
        raise AssertionError("Source-order invariant new candidate changed choice")
    stats={}
    for (case,variant,arm),xs in sorted(pairs.items()):
        stats[case+"__"+variant+"__"+arm]={"pairs":len(xs),
             "median":statistics.median(xs),"min":min(xs),"max":max(xs)}
    risk=[]
    for case in m.IDS:
        chosen=[]
        for v in m.VARIANTS:
            entry=stats.get(case+"__"+v+"__"+m.ARMS[0])
            if entry:chosen.append(entry["median"])
        if chosen and min(chosen)<2/3:
            risk.append({"case":case,"worst_variant_median_RAW_over_C2":min(chosen)})
    return {"schema":"JANUS-TIME-SAT-004E12C2-16VM-576-COLD-FROZEN-WIDTH6-NO-RAW-PROBE-AUDIT-V1",
       "original_run_id":next(iter(runs)),"original_science_HEAD":next(iter(heads)),
       "preregister_git_blob":m.BLOB,"preworker_source_lock_SHA256":locksha,
       "distinct_real_worker_names":16,"original_cold_children":576,
       "original_outcomes":dict(counts),
       "by_arm":{k:dict(v) for k,v in by_arm.items()},
       "by_source":{k:dict(v) for k,v in by_case.items()},
       "by_family":{k:dict(v) for k,v in by_family.items()},
       "source_order_invariant_choices":decisions,
       "source_SHA_per_original":{case:m.original(case)["sha"] for case in m.IDS},
       "source_model_SHA_per_original":{case:m.original(case)["model_sha"] for case in m.IDS},
       "original_worker_JSON_SHA256":worker_SHA,
       "same_VM_matched_raw_comparison_count":len(result_pairs),
       "fully_completed_raw_alternative_pairs":result_pairs,
       "source_grouped_comparison_ratios":stats,
       "C1_original_probe_statuses":dict(probe_c1),
       "new_C2_original_probe_count":0,
       "source_level_gt_1_5x_regressions":risk,
       "production_champion":"NOT_ADMITTED",
       "original_external_blind_sources":0,
       "same_admin_GitHub_audit_not_external_Witness":True,
       "production_C023_main":"UNCHANGED",
       "new_unseen_generator_topology_external":"NO"}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--receipts",type=Path,required=True)
    p.add_argument("--source-lock",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    x=p.parse_args();d=audit(x.receipts,x.source_lock)
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
    print("E12C2_ORIGINAL_576_CHILD_AUDIT_PASS",json.dumps({
      "children":576,"outcomes":d["original_outcomes"],
      "finite_pairs":d["same_VM_matched_raw_comparison_count"],
      "C1_raw_probes":d["C1_original_probe_statuses"],
      "C2_pilot_runs":0,
      "regressions":d["source_level_gt_1_5x_regressions"]},sort_keys=True))
