#!/usr/bin/env python3
"""E10 12 source-locked VMs and 144 children; complete same-admin research audit."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e10_ood as e

def audit(folder,lockpath):
    e.frozen()
    lock,locksha=e.checked_lock(lockpath)
    expected={case+"__"+host+".json" for case in e.IDS for host in e.HOSTS}
    got={f.name for f in folder.glob("*.json")}
    if expected!=got:
        raise AssertionError("E10 original 12 VM receipts missing/untrusted "+
          repr({"missing":sorted(expected-got),"foreign":sorted(got-expected)}))
    originals={case:e.planted_source(case) for case in e.IDS}
    if len({v["sha"] for v in originals.values()})!=6:raise AssertionError("Duplicate source")
    outcomes=Counter();byarm={};byfamily={};source_rounds={}
    runners=set();runs=set();heads=set();digests={};complete=[]
    for file in sorted(folder.glob("*.json")):
        case,host=file.stem.split("__")
        src=originals[case]
        data=json.loads(file.read_text())
        if (data.get("schema")!="JANUS-TIME-SAT-004E10-FAMILY-NEW-SYNTHETIC-6-ARM-ORIGINAL-VM-V1"
            or (data.get("case"),data.get("original_os"))!=(case,host)
            or data.get("family")!=src["family"]
            or data.get("original_CNF_SHA256")!=src["sha"]
            or data.get("full_SAT_model_SHA256")!=src["model_sha"]
            or data.get("sealed_source_lock_SHA256")!=locksha
            or data.get("original_E9_pretrained_model_SHA256")!=e.MODEL_SHA
            or data.get("frozen_experiment_git_blob")!=e.PREREG_BLOB
            or (data.get("CPU_s"),data.get("WALL_s"),data.get("MEM"))!=(e.CPU,e.WALL,e.MEM)
            or data.get("original_children")!=12 or len(data.get("records",[]))!=12
            or data.get("new_external_blind_sources")!=0 or data.get("production_C023")!="UNCHANGED"):
            raise AssertionError("Source/model/receipt provenance changed "+file.name)
        pre=lock["source_precommit"][case]
        if (pre["original_CNF_SHA256"],pre["complete_original_SAT_model_SHA256"])!=(src["sha"],src["model_sha"]):
            raise AssertionError("Preflight independent original source lock mismatch")
        runners.add(data["original_runner_name"]);runs.add(str(data["original_run_id"]))
        heads.add(data["original_head"])
        casecounts=source_rounds.setdefault(case,Counter())
        for rep in (0,1):
            trials=[r for r in data["records"] if r["repeat"]==rep]
            if len(trials)!=6 or {r["arm"] for r in trials}!=set(e.ARMS):
                raise AssertionError("Missing complete original six arm pair")
            if any(set(r["shuffled_order"])!=set(e.ARMS) for r in trials):
                raise AssertionError("Original random arm ordering mutated")
            baseline=next(r for r in trials if r["arm"]=="raw_cms")
            for r in trials:
                status=r["outcome"].get("status")
                if status not in e.ALLOWED:
                    raise AssertionError("Unexplained child status; fail closed "+repr(r))
                if not 0<r["cold_child_full_wall_s"]<e.WALL+5:
                    raise AssertionError("Invalid observed actual cold full wall")
                o=r["outcome"]
                if status==e.SAT:
                    if (o.get("original_CNF_SHA256")!=src["sha"]
                        or o.get("original_full_model_SHA256")!=src["model_sha"]
                        or o.get("sealed_source_lock_SHA256")!=locksha
                        or o.get("original_E9_model_SHA256")!=e.MODEL_SHA
                        or o.get("original_model_pre_and_post_replayed") is not True
                        or (o.get("case"),o.get("arm"))!=(case,r["arm"])):
                        raise AssertionError("SAT not verified against authentic original source")
                    if r["arm"]=="e10_ood_abstain":
                        prediction=e.decision(src["rows"],src["n"],"e10_ood_abstain",e.model())
                        if (prediction["choice"]!=o["effective_representation"]
                            or len(prediction["equations"])!=o["selected_original_XOR_equations"]):
                            raise AssertionError("OOD inference outcome mismatches frozen predecision replay")
                outcomes[status]+=1
                byarm.setdefault(r["arm"],Counter())[status]+=1
                byfamily.setdefault(src["family"],Counter())[status]+=1
                casecounts[status]+=1
                if (r["arm"]!="raw_cms" and status==e.SAT
                    and baseline["outcome"]["status"]==e.SAT):
                    complete.append({
                      "family":src["family"],"case":case,"host":host,"repeat":rep,"arm":r["arm"],
                      "candidate_s":r["cold_child_full_wall_s"],
                      "raw_s":baseline["cold_child_full_wall_s"],
                      "raw_over_candidate":baseline["cold_child_full_wall_s"]/r["cold_child_full_wall_s"]})
        digests[file.name]=sha256(file.read_bytes()).hexdigest()
    if (len(runners)!=12 or len(heads)!=1 or len(runs)!=1 or
        len(digests)!=12 or sum(outcomes.values())!=144):
        raise AssertionError("Incomplete original E10 exact 12 runner 144 cold trial dataset")
    # SOURCE-grouped summaries are not independent instances across 2 Ubuntu images or repeats.
    famratios={}
    for family in e.FAMILIES:
        percase={}
        for case in e.IDS:
            if originals[case]["family"]!=family:continue
            percase[case]={}
            for arm in e.ARMS:
                ratios=[r["raw_over_candidate"] for r in complete if r["case"]==case and r["arm"]==arm]
                if ratios:percase[case][arm]={"pairs":len(ratios),"median":statistics.median(ratios)}
        famratios[family]=percase
    return {"schema":"JANUS-TIME-SAT-004E10-NEW-GENERATOR-3-FAMILY-12VM-144-COLD-AUDIT-V1",
      "result":"12_SOURCE_LOCKED_SAME_ADMIN_WORKERS_ALL_144_CHILD_VERDICTS",
      "original_run":next(iter(runs)),"original_head":next(iter(heads)),
      "original_pretrained_E9_MODEL_SHA256":e.MODEL_SHA,
      "original_frozen_policy_blob":e.PREREG_BLOB,
      "original_SOURCE_LOCK_SHA256":locksha,
      "original_12_distinct_VMs":12,"original_144_cold_children":144,
      "original_all_outcomes":dict(outcomes),
      "per_method_outcomes":{k:dict(v) for k,v in byarm.items()},
      "per_generator_family_outcomes":{k:dict(v) for k,v in byfamily.items()},
      "per_original_CNFS_source_group_outcomes":{k:dict(v) for k,v in source_rounds.items()},
      "source_grouped_complete_pair_ratios":famratios,
      "original_source_SHA":{k:v["sha"] for k,v in originals.items()},
      "original_full_model_SHA":{k:v["model_sha"] for k,v in originals.items()},
      "original_all_12_worker_SHA256":digests,
      "valid_completed_raw_vs_candidate_pair_count":len(complete),
      "all_completed_pairs":complete,
      "independent_generator_families":3,"synthetic_planted_sources":6,
      "source_holdout_from_E8_training_groups":True,
      "external_independent_blind_source_count":0,
      "same_GitHub_admin_verifier_is_not_external_Witness":True,
      "generalized_SAT_speedup_proven":False,
      "fourth_E10_production_gate":"NOT_READY","C023_main":"UNCHANGED",
      "global_champion":"NOT_ESTABLISHED"}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-lock",required=True,type=Path)
    p.add_argument("--receipts",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    r=audit(a.receipts,a.source_lock)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print("004E10_ORIGINAL_AUDIT_PASS",json.dumps({
      "workers":r["original_12_distinct_VMs"],"children":r["original_144_cold_children"],
      "outcomes":r["original_all_outcomes"],
      "paired_complete":r["valid_completed_raw_vs_candidate_pair_count"],
      "new_external_blind":0},sort_keys=True))
