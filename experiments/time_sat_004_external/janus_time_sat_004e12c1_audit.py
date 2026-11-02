#!/usr/bin/env python3
"""E12C1 exact original-SHA model and source-group real full cold cost evaluator."""
from __future__ import annotations
import argparse,json,statistics,sys
from pathlib import Path
from collections import Counter,defaultdict
from hashlib import sha256
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12c1_cost_aware as m

def audit(receipts,lock_path):
    p=m.frozen();lock,locksha=m.load_lock(lock_path)
    expected={case+"__"+os+".json" for case in m.IDS for os in m.HOSTS}
    present={x.name for x in receipts.glob("*.json")}
    if present!=expected:raise AssertionError("Missing/foreign original VM JSON: "+str(expected-present))
    heads=set();runs=set();runners=set();counts=Counter();by_arm=defaultdict(Counter)
    per_case={};grouped=defaultdict(list);full_pairs=[];all_shas={}
    probe_counts=Counter()
    for fp in sorted(receipts.glob("*.json")):
        case,os=fp.stem.split("__")
        d=fp.read_bytes();j=json.loads(d);src=m.source(case)
        if (j.get("schema")!="JANUS-TIME-SAT-004E12C1-36-FROZEN-COLD-ORIGINAL-VM-V1"
            or (j.get("case"),j.get("original_os"))!=(case,os)
            or (j.get("original_source_SHA256"),j.get("full_model_SHA256"))!=(
                src["sha"],src["model_sha"])
            or j.get("prereg_Git_blob")!=m.BLOB or j.get("preworker_lock_SHA256")!=locksha
            or (j.get("repeats"),j.get("variants"),j.get("arms"),j.get("children"))!=(2,3,6,36)
            or (j.get("CPU"),j.get("WALL"),j.get("MEM"))!=(m.CPU,m.WALL,m.MEM)
            or j.get("external_independent_sources")!=0 or j.get("C023_main")!="UNCHANGED"
            or len(j.get("records",[]))!=36):
            raise AssertionError("Original SHA/frozen source/worker contract mismatch "+fp.name)
        if not j["original_runner"] or j["original_runner"] in runners:
            raise AssertionError("Actual hosted VM runner identity duplicate")
        runners.add(j["original_runner"])
        heads.add(j["original_HEAD"]);runs.add(str(j["original_run_id"]))
        for variant in m.VARIANTS:
            sub=m.variant(case,variant);sealed=lock["source"][case][variant]
            if (sealed["original_variant_CNF_SHA256"],sealed["original_source_SHA256"],
                sealed["full_SAT_model_SHA256"])!=(sub["sha"],sub["base_sha"],sub["model_sha"]):
                raise AssertionError("Source/complete model SHA altered after frozen lock")
            for rep in range(2):
                records=[x for x in j["records"] if x["variant"]==variant and x["repeat"]==rep]
                if (len(records)!=6 or {x["arm"] for x in records}!=set(m.ARMS)
                    or any(set(x["order"])!=set(m.ARMS) for x in records)):
                    raise AssertionError("Not original 6 frozen randomized arms")
                raw=next(x for x in records if x["arm"]=="raw_cms")
                prev=next(x for x in records if x["arm"]=="e12b_support_index")
                for z in records:
                    o=z["outcome"];status=o.get("status");arm=z["arm"]
                    if (status not in m.ALLOWED or
                        not 0<z["full_cold_child_wall_s"]<m.WALL+4):
                        raise AssertionError("Unregistered/censored bad original outcome")
                    counts[status]+=1;by_arm[arm][status]+=1
                    if status==m.SAT:
                        if ((o.get("case"),o.get("variant"),o.get("arm"))!=(case,variant,arm)
                            or (o.get("original_source_SHA256"),
                                o.get("transformed_original_CNF_SHA256"),
                                o.get("complete_planted_SAT_model_SHA256"))!=(
                                sub["base_sha"],sub["sha"],sub["model_sha"])
                            or o.get("preworker_lock_SHA256")!=locksha
                            or o.get("complete_original_CNF_SAT_model_replay")!="PASS"
                            or o.get("C023_main")!="UNCHANGED"):
                            raise AssertionError("Original SAT proof/source checksum violated")
                        if arm=="e12c1_cost_aware":
                            if o.get("predecision",{}).get("eligible")!=sealed["candidate_source_XOR_eligible"]:
                                raise AssertionError("E12C1 source reordering changed pre-frozen eligibility")
                            probe_counts[o["raw_bounded_probe_status"]]+=1
                    if (arm!="raw_cms" and status==m.SAT and
                        raw["outcome"].get("status")==m.SAT):
                        ratio=raw["full_cold_child_wall_s"]/z["full_cold_child_wall_s"]
                        grouped[(case,variant,arm)].append(ratio)
                        full_pairs.append({"case":case,"variant":variant,"os":os,
                            "repeat":rep,"arm":arm,"raw_over_candidate":ratio})
                    if (arm=="e12c1_cost_aware" and status==m.SAT and
                        prev["outcome"].get("status")==m.SAT):
                        grouped[(case,variant,"C1_OVER_E12B")].append(
                            prev["full_cold_child_wall_s"]/z["full_cold_child_wall_s"])
        all_shas[fp.name]=sha256(d).hexdigest()
    if (len(runners),len(runs),len(heads),sum(counts.values()))!=(20,1,1,720):
        raise AssertionError("Not 20 real unique hosted VMs, one head/run and 720 cold children")
    by_group={}
    for case in m.IDS:
        d={}
        for v in m.VARIANTS:
            d[v]=lock["source"][case][v]["candidate_source_XOR_eligible"]
        if len(set(d.values()))!=1:
            raise AssertionError("E12C1 original source eligible flip under exact equivalent CNF order")
        by_group[case]={"source_kind":"INTERNAL_JANUS_SYNTHETIC_NOT_EXTERNAL",
            "family":m.source(case)["family"],"original_source_SHA256":m.source(case)["sha"],
            "complete_model_SHA256":m.source(case)["model_sha"],
            "eligibility_by_equivalent_variant":d,
            "source_variant_SHA256":{v:lock["source"][case][v]["original_variant_CNF_SHA256"]
                                   for v in m.VARIANTS}}
    summary={key[0]+"__"+key[1]+"__"+key[2]:{
             "paired_completed":len(values),
             "median":statistics.median(values),
             "min":min(values),"max":max(values)}
             for key,values in sorted(grouped.items())}
    negatives=[{"case":case,"variant":v,"raw_over_C1_median":x["median"]}
         for k,x in summary.items()
         if k.endswith("__e12c1_cost_aware")
         for case,v,arm in [k.split("__")]
         if x["median"]<1.0]
    return {
       "schema":"JANUS-TIME-SAT-004E12C1-20-VM-720-FROZEN-SOURCE-MODEL-TRIAL-AUDIT-V1",
       "status":"ORIGINAL_COLD_720_MODEL_SHA_AND_SOURCE_REPLAY_AUDITED",
       "original_scientific_run_id":next(iter(runs)),
       "original_scientific_HEAD":next(iter(heads)),
       "prereg_git_blob":m.BLOB,
       "dev_calibration_git_blob":m.AUDIT_BLOB,
       "preworker_lock_sha256":locksha,
       "VM_runner_names":20,"cloud_children":720,
       "SAT_and_unknown_counts":dict(counts),
       "by_method":{arm:dict(counts) for arm,counts in by_arm.items()},
       "RAW_baseline_self_trials":120,
       "potential_raw_vs_other_method_pairs":600,
       "actual_completed_raw_vs_alternative_pairs":len(full_pairs),
       "candidate_raw_probe_status_count":dict(probe_counts),
       "source_groups":by_group,
       "fully_completed_original_same_VM_paired_ratios":full_pairs,
       "grouped_original_source_variant_finite_full_cold_ratios":summary,
       "all_original_worker_JSON_SHA256":all_shas,
       "candidate_negatives_as_observed_without_posthoc_exclusion":negatives,
       "external_independent_originals":0,"global_champion":"NOT_ADMITTED",
       "C023_production":"UNCHANGED"
    }
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--receipts",type=Path,required=True)
    a.add_argument("--source-lock",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    x=a.parse_args();result=audit(x.receipts,x.source_lock)
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("E12C1_ORIGINAL_720_CHILD_AUDIT_PASS",json.dumps({
        "outcomes":result["SAT_and_unknown_counts"],
        "full_pairs":result["actual_completed_raw_vs_alternative_pairs"],
        "new_original_SAT":len(result["source_groups"])},sort_keys=True))
