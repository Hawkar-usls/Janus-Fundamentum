#!/usr/bin/env python3
"""Source-bound audit of 24 original metamorphic worker receipts / 96 children."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import statistics
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e5_metamorphic as m
from janus_time_sat_004e3_swarm import select_verified_xor

ALLOWED={m.SAT,"UNKNOWN_CPU_LIMIT_SIGXCPU","UNKNOWN_WALL_TIMEOUT",
         "UNKNOWN_SOLVER_NO_ANSWER"}
OS=("ubuntu-22.04","ubuntu-24.04")

def verify(directory):
    m.preflight()
    expected={f+"__pad"+str(p)+"__"+v+"__"+os+".json"
              for f in m.FAMILIES for p in m.PADS for v in m.VARIANTS for os in OS}
    actual={p.name for p in directory.glob("*.json")}
    if expected!=actual:
        raise AssertionError("Incomplete or contaminated original metamorphic worker archive: "+
          repr({"missing":sorted(expected-actual),"extra":sorted(actual-expected)}))
    source={ (f,p):m.materialize(f,p) for f in m.FAMILIES for p in m.PADS }
    run=set()
    head=set()
    runners=set()
    sha={}
    observations={}
    counters=Counter()
    for path in sorted(directory.glob("*.json")):
        raw=path.read_bytes()
        report=json.loads(raw)
        if report.get("schema")!="JANUS-TIME-SAT-004E5-METAMORPHIC-SAME-VM-FROZEN-RECEIPT-V1":
            raise AssertionError("Unrecognized original worker record")
        family,pstr,variant,osname=path.stem.split("__")
        pad=int(pstr.removeprefix("pad"))
        if (family,pad,variant,osname)!=(report["family"],report["padding_percent"],
                                          report["variant"],report["runner_os"]):
            raise AssertionError("Original worker file identity not source-bound")
        expected_info=source[(family,pad)]
        if (report["transformed_CNF_SHA256"]!=expected_info["generated_SHA256"]
            or report["original_CNF_SHA256"]!=expected_info["original_SHA256"]
            or report["transformed_full_model_SHA256"]!=expected_info["model_SHA256"]
            or report["frozen_policy_blob"]!=m.PRE_BLOB
            or report["source_rewrite_model_preflight"]!="PASS"
            or report["CPU_soft_s"]!=m.CPU or report["wall_s"]!=m.WALL
            or report["RLIMIT_AS"]!=m.MEM
            or report["no_global_champion"] is not True):
            raise AssertionError("Original model/SHA/policy/budget was tampered")
        if len(report["records"])!=4:
            raise AssertionError("Four cold children per VM required")
        run.add(str(report["github_run_id"]))
        head.add(report["github_head"])
        runners.add(report["runner_name"])
        by_role={}
        for role in ("candidate","raw_baseline"):
            pair=sorted([r for r in report["records"] if r["role"]==role],key=lambda x:x["repeat"])
            if len(pair)!=2 or [r["repeat"] for r in pair]!=[0,1]:
                raise AssertionError("Original paired repeats missing/duplicated")
            by_role[role]=pair
        for r in report["records"]:
            if set(r["same_VM_order"])!={"candidate","raw_baseline"}:
                raise AssertionError("Invalid paired random ordering")
            if r["method"]!=(variant if r["role"]=="candidate" else "raw_cms"):
                raise AssertionError("Wrong original control/candidate")
            o=r["outcome"]
            status=o.get("status")
            if status not in ALLOWED:
                raise AssertionError("Unexpected unregistered solver status "+str(status))
            if status==m.SAT:
                if (o.get("transformed_CNF_SHA256")!=expected_info["generated_SHA256"]
                    or o.get("full_original_SAT_model_check")!="PASS_BEFORE_AND_AFTER"
                    or o.get("original_CNF_SHA256")!=expected_info["original_SHA256"]):
                    raise AssertionError("SAT not independently bound to exact transformed model")
            counters[status]+=1
        source_form=select_verified_xor(expected_info["rows"],
                                         expected_info["n"],variant)
        if source_form["converted_source_clauses"]+len(source_form["cnf_clauses"])!=len(expected_info["rows"]):
            raise AssertionError("Metamorphic generated clauses lost in source proof")
        cand_sat=sum(r["outcome"]["status"]==m.SAT for r in by_role["candidate"])
        raw_sat=sum(r["outcome"]["status"]==m.SAT for r in by_role["raw_baseline"])
        finite=(cand_sat==raw_sat==2)
        ratios=[by_role["raw_baseline"][i]["full_cold_child_wall_seconds"]/
                by_role["candidate"][i]["full_cold_child_wall_seconds"]
                for i in range(2)] if finite else []
        observations[path.stem]={
            "source_transformed_SHA256":expected_info["generated_SHA256"],
            "padding_clauses":expected_info["padding_clauses"],
            "verified_candidate_SAT":cand_sat,"verified_raw_SAT":raw_sat,
            "candidate_statuses":[r["outcome"]["status"] for r in by_role["candidate"]],
            "raw_statuses":[r["outcome"]["status"] for r in by_role["raw_baseline"]],
            "original_source_coverage_fraction":
                source_form["converted_source_clauses"]/len(expected_info["rows"]),
            "selected_native_XOR_equations":len(source_form["equations"]),
            "candidate_representation":source_form["choice"],
            "same_VM_ratio_only_if_both_complete":statistics.median(ratios) if finite
                else "UNDEFINED_CENSORED"
        }
        sha[path.name]=sha256(raw).hexdigest()
    if len(run)!=1 or len(head)!=1 or len(runners)!=24 or len(observations)!=24:
        raise AssertionError("Expected unique 24 VM names and identical original run SHA")
    return {
        "schema":"JANUS-TIME-SAT-004E5-24-VM-METAMORPHIC-ROBUSTNESS-AUDIT-V1",
        "status":"ALL_SOURCE_IDENTITIES_FROZEN_24_WORKER_96_COLD_CHILDREN_AUDITED",
        "source_job_run_id":next(iter(run)),"original_git_head":next(iter(head)),
        "policy_git_blob":m.PRE_BLOB,
        "verified_worker_receipts":24,
        "verified_unique_runner_names":len(runners),
        "verified_cold_child_outcomes":sum(counters.values()),
        "all_status_counts":dict(counters),
        "source_originals":{f:m.SOURCE[f][0] for f in m.FAMILIES},
        "source_transformed_SHA_by_case":{
            f+"__pad"+str(p):v["generated_SHA256"] for (f,p),v in source.items()},
        "per_worker":observations,
        "receipts_sha256":sha,
        "new_external_independent_SAT_cases":0,
        "no_external_holdout":True,
        "no_universal_speedup_or_automated_champion":True,
        "original_C023_main":"UNCHANGED",
        "interpretation":"These are logical renamings and tautological paddings of TWO PRESEEN source SAT problems, not new independent samples. Even if threshold loses a model on padded equivalent CNF, this is an engineering counterexample to representation-invariant policy, not a new SAT algorithm generality claim."
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    audit=verify(args.in_dir)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(audit,sort_keys=True,indent=2)+"\n")
    print("004E5_SOURCE_AUDIT_PASS",json.dumps({
       "jobs":audit["verified_worker_receipts"],
       "children":audit["verified_cold_child_outcomes"],
       "SAT":audit["all_status_counts"].get(m.SAT,0),
       "external_holdout":False},sort_keys=True))
