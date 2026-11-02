#!/usr/bin/env python3
"""Strict E12C3 source-SHA 16 hosted VMs/640 outcomes, original SAT model and ablated mask audit."""
from __future__ import annotations
import argparse,json,statistics,sys
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e12c3_partial_mask_falsification as m

def audit(folder,lockpath):
    m.frozen();lock,locksha=m.checked_lock(lockpath)
    expected={case+"__"+os+".json" for case in m.IDS for os in m.HOSTS}
    found={x.name for x in folder.glob("*.json")}
    if found!=expected:
        raise AssertionError("Missing/or foreign original worker receipts "+str(expected-found))
    runners=set();runs=set();heads=set();counts=Counter();by_arm=defaultdict(Counter)
    receipts={};pairs=defaultdict(list);finite=[];cases={}
    for file in sorted(folder.glob("*.json")):
        case,os=file.stem.split("__")
        raw=file.read_bytes();j=json.loads(raw);original=m.original(case)
        if (j.get("schema")!="JANUS-TIME-SAT-004E12C3-40-ORIGINAL-SOURCE-FROZEN-COLD-VM-V1"
            or (j.get("case"),j.get("original_os"))!=(case,os)
            or (j.get("original_CNF_SHA256"),j.get("original_complete_model_SHA256"))!=(
                 original["sha"],original["model_sha"])
            or j.get("prereg_Git_blob")!=m.BLOB
            or j.get("preworker_source_lock_SHA256")!=locksha
            or (j.get("cold_children"),j.get("CPU"),j.get("WALL"),j.get("MEM"))!=(40,m.CPU,m.WALL,m.MEM)
            or j.get("independent_external_sources")!=0 or j.get("C023_main")!="UNCHANGED"
            or len(j.get("records",[]))!=40):
            raise AssertionError("Original source/model/C023/child metadata corrupted "+file.name)
        if not j["original_runner_name"] or j["original_runner_name"] in runners:
            raise AssertionError("20? expected unique original VM runner for each 16 job")
        runners.add(j["original_runner_name"]);runs.add(str(j["original_run_id"]));heads.add(j["original_HEAD"])
        for var in m.VARIANTS:
            s=m.variant(case,var);pin=lock["sources"][case][var]
            if ((pin["base_original_CNF_SHA256"],pin["base_original_complete_model_SHA256"],
                 pin["source_variant_CNF_SHA256"],pin["source_variant_complete_SAT_model_SHA256"])!=(
                 s["base_sha"],s["base_model_sha"],s["sha"],s["model_sha"])
                 or pin["frozen_C2_decision"]!=m.policy(s["rows"],s["n"],m.ARMS[0])["decision"]["choice"]):
                raise AssertionError("Frozen source/original CNF SHA/model/candidate decision drift")
            index=m.c1.source_index_all_widths(s["rows"],s["n"])
            if index["counts"].get(6,0)!=m.config(case)["full_equations"]:
                raise AssertionError("Incomplete source XOR mask wrongly accepted as proved")
            for rep in (0,1):
                batch=[x for x in j["records"] if x["variant"]==var and x["repeat"]==rep]
                if (len(batch)!=5 or {x["arm"] for x in batch}!=set(m.ARMS)
                    or any(set(x["randomized_arm_order"])!=set(m.ARMS) for x in batch)):
                    raise AssertionError("Missing one same-VM source-equivalent five-arm cold trial")
                base=next(x for x in batch if x["arm"]=="raw_cms")
                for row in batch:
                    o=row["outcome"];arm=row["arm"];status=o.get("status")
                    if status not in m.ALLOWED or not 0<row["full_cold_child_wall_s"]<m.WALL+4:
                        raise AssertionError("Unknown/misclassified original child termination")
                    counts[status]+=1;by_arm[arm][status]+=1
                    if status==m.SAT:
                        if ((o.get("case"),o.get("variant"),o.get("arm"))!=(case,var,arm)
                            or (o.get("base_original_CNF_SHA256"),o.get("variant_original_CNF_SHA256"),
                                o.get("base_original_full_SAT_model_SHA256"),o.get("variant_original_full_SAT_model_SHA256"))!=(
                                s["base_sha"],s["sha"],s["base_model_sha"],s["model_sha"])
                            or o.get("preworker_source_lock_SHA256")!=locksha
                            or o.get("source_partial_masks_not_misclassified") is not True
                            or o.get("source_exact_width6_equations_proven")!=m.config(case)["full_equations"]
                            or o.get("full_original_CNF_complete_model_replay")!="PASS"
                            or o.get("production_C023_main")!="UNCHANGED"):
                            raise AssertionError("SAT child source-model proof malformed")
                        if arm==m.ARMS[0] and o["candidate_decision"]!=pin["frozen_C2_decision"]:
                            raise AssertionError("Postworker C2 candidate decision order flip")
                    if arm!="raw_cms" and status==m.SAT and base["outcome"].get("status")==m.SAT:
                        ratio=base["full_cold_child_wall_s"]/row["full_cold_child_wall_s"]
                        pairs[(case,var,arm)].append(ratio)
                        finite.append({"case":case,"variant":var,"os":os,"repeat":rep,"arm":arm,
                            "raw_over_method_full_cold":ratio})
        receipts[file.name]=sha256(raw).hexdigest()
    if (len(runners),len(runs),len(heads),sum(counts.values()))!=(16,1,1,640):
        raise AssertionError("Original 16 distinct VM/one source HEAD/640 child source counts incorrect")
    for arm in m.ARMS:
        if sum(by_arm[arm].values())!=128:raise AssertionError("Unregistered arm count")
    bad=[]
    summary={}
    for (case,var,arm),data in sorted(pairs.items()):
        med=statistics.median(data)
        summary[case+"__"+var+"__"+arm]={"completed_pairs":len(data),
            "median_raw_over_method":med,"min":min(data),"max":max(data)}
        if arm==m.ARMS[0] and med<2/3:
            bad.append({"case":case,"variant":var,"ratio_RAW_over_C2":med})
    choice_counts=Counter()
    for case in m.IDS:
        pinned={v:lock["sources"][case][v]["frozen_C2_decision"] for v in m.VARIANTS}
        if len(set(pinned.values()))!=1:
            raise AssertionError("Candidate C2 source choice changed under SAT-equivalent representation/variable isomorphism")
        choice_counts[next(iter(pinned.values()))]+=1
        cases[case]={
         "source_kind":"NEW_JANUS_INTERNAL_NOT_EXTERNAL",
         "family":m.config(case)["kind"],
         "original_CNF_SHA256":m.original(case)["sha"],
         "base_complete_SAT_model_SHA256":m.original(case)["model_sha"],
         "full_width6_source_certificates":m.config(case)["full_equations"],
         "incomplete_width6_source_masks":m.config(case)["equations"]-m.config(case)["full_equations"],
         "equivalent_original_CNF_and_renamed_isomorphism_decisions":pinned,
         "renamed_variant_is_same_original_SAT_up_to_variable_bijection":True,
         "source_model_SHA_variants":{v:lock["sources"][case][v]["source_variant_complete_SAT_model_SHA256"] for v in m.VARIANTS},
         "source_CNF_SHA_variants":{v:lock["sources"][case][v]["source_variant_CNF_SHA256"] for v in m.VARIANTS}}
    return {
     "schema":"JANUS-TIME-SAT-004E12C3-16-VM-640-CHILD-ORIGINAL-SOURCE-STRICT-PROOF-AUDIT-V1",
     "status":"ORIGINAL_640_SOURCE_MODEL_CNF_SHA_AND_PARTIAL_XOR_CORRECTNESS_VERIFIED",
     "original_run_id":next(iter(runs)),"original_scientific_HEAD":next(iter(heads)),
     "prereg_manifest_Git_blob":m.BLOB,"preworker_source_lock_SHA256":locksha,
     "actual_distinct_hosted_VMs":16,"all_cold_children":640,
     "outcomes":dict(counts),
     "by_frozen_method":{arm:dict(v) for arm,v in by_arm.items()},
     "original_RAW_baseline_self_trials":128,
     "possible_RAW_vs_alternative_original_matched_pairs":512,
     "actual_both_SAT_completed_finite_pairs":len(finite),
     "finite_same_VM_original_source_pairs":finite,
     "source_variant_grouped_medians":summary,
     "original_source_groups":cases,
     "frozen_candidate_decision_counts_across_8_originals":dict(choice_counts),
     "incorrect_partial_mask_XOR_admissions":0,
     "candidate_losses_over_1_5x_vs_RAW_on_source_variant_median":bad,
     "original_worker_JSON_SHA256":receipts,
     "outside_independent_custodian_sources":0,
     "global_champion":"NOT_ADMITTED","main_C023":"UNCHANGED"}
if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--receipts",required=True,type=Path)
    a.add_argument("--source-lock",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    x=a.parse_args()
    q=audit(x.receipts,x.source_lock)
    x.out.parent.mkdir(parents=True,exist_ok=True)
    x.out.write_text(json.dumps(q,sort_keys=True,indent=2)+"\n")
    print("E12C3_STRICT_PARTIAL_MASK_FALSIFICATION_AUDIT_PASS",json.dumps({
        "VMs":16,"children":640,"outcomes":q["outcomes"],
        "pairs":q["actual_both_SAT_completed_finite_pairs"],
        "wrong_source_mask_XOR":0},sort_keys=True))
