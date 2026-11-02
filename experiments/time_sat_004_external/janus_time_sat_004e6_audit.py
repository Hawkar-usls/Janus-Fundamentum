#!/usr/bin/env python3
"""004E6 audit: require all 12 host/formula receipts, 96 nonfabricated outcomes."""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"direct"))
import janus_time_sat_004e6_semantic_selector as m

def audit(directory):
    m.preregistered()
    expected={f+"__"+state+"__"+os+".json"
              for f in m.FAMILIES for state in m.STATES for os in m.HOSTS}
    got={p.name for p in directory.glob("*.json")}
    if got!=expected:
        raise AssertionError("Missing or foreign original research matrix worker: "+
                             repr({"missing":sorted(expected-got),"extra":sorted(got-expected)}))
    totals=Counter()
    by_family={};checksums={};run=set();head=set();runner=set()
    for p in sorted(directory.glob("*.json")):
        a=json.loads(p.read_text())
        fam,state,osname=p.stem.split("__")
        origin=m.materialize(fam,state)
        if (a.get("schema")!="JANUS-TIME-SAT-004E6-FOUR-ARM-SAME-VM-SAT-EQUIVALENT-REPAIR-V1"
            or (a.get("family"),a.get("state"),a.get("os"))!=(fam,state,osname)
            or a.get("source_original_sha")!=m.SHA[fam]
            or a.get("transformed_sha")!=origin["SHA256"]
            or a.get("model_sha")!=origin["model_SHA256"]
            or a.get("precommit_git_blob")!=m.BLOB
            or a.get("cpu_soft_s")!=m.CPU or a.get("wall_s")!=m.WALL
            or a.get("mem_bytes")!=m.MEM or a.get("repeats")!=2
            or a.get("cold_children_expected")!=8
            or a.get("added_tautologies")!=origin["added_tautologies"]
            or a.get("added_duplicates")!=origin["added_duplicates"]
            or a.get("new_external_independent_CNF")!=0
            or a.get("no_production_promotion") is not True
            or a.get("production_C023")!="UNCHANGED"):
            raise AssertionError("Original evidence SHA or immutable policy mismatched: "+p.name)
        run.add(str(a["github_run_id"]));head.add(a["github_head"]);runner.add(a["runner_name"])
        if len(a["records"])!=8:
            raise AssertionError("Expected eight original cold processes on same GitHub VM")
        byarm={}
        for rep in (0,1):
            rows=[x for x in a["records"] if x["repeat"]==rep]
            if len(rows)!=4 or {x["arm"] for x in rows}!=set(m.ARMS):
                raise AssertionError("Each repeat needs the complete four-arm comparison")
            if any(set(x["shuffled_order"])!=set(m.ARMS) for x in rows):
                raise AssertionError("Worker paired randomized permutation invalid")
        for row in a["records"]:
            arm=row["arm"];verdict=row["outcome"]
            status=verdict.get("status")
            if status not in m.ALLOWED:
                raise AssertionError("Invalid/missing scientific original child: "+repr(verdict))
            if row["full_cold_child_wall_s"]<0:
                raise AssertionError("Impossible negative elapsed")
            if status==m.SAT:
                if (verdict.get("transformed_CNF_SHA256")!=origin["SHA256"]
                    or verdict.get("original_source_SHA256")!=m.SHA[fam]
                    or verdict.get("known_full_model_SHA256")!=origin["model_SHA256"]
                    or verdict.get("original_full_clause_model_replay")!="PASS_PRE_AND_POST"
                    or verdict.get("arm")!=arm):
                    raise AssertionError("Original SAT source-model full replay missing")
                if arm=="new_semantic80":
                    candidate=m.normalized_selector(origin["rows"],origin["n"],arm)
                    if (candidate["choice"]!=verdict["effective_representation"]
                        or candidate["metric"]["selected"]!=verdict["selected_XOR_equations"]):
                        raise AssertionError("New gate actual correct result contradicted by independent recomputation")
            totals[status]+=1
            byarm.setdefault(arm,Counter())[status]+=1
        by_family[p.stem]={k:dict(v) for k,v in byarm.items()}
        checksums[p.name]=sha256(p.read_bytes()).hexdigest()
    if len(run)!=1 or len(head)!=1 or len(runner)!=12 or sum(totals.values())!=96:
        raise AssertionError("All 12 distinct runner sources and 96 original child outcomes required")
    return {
        "schema":"JANUS-TIME-SAT-004E6-12-GITHUB-VMS-96-ORIGINAL-CHILD-RESEARCH-AUDIT-V1",
        "result":"FROZEN_SEMANTIC_NORMALIZED_SELECTOR_DIAGNOSTIC_ALL_ORIGINALS_AUDITED",
        "original_run_id":next(iter(run)),"original_head":next(iter(head)),
        "precommitted_git_blob":m.BLOB,
        "original_runner_count":12,"original_cold_children":96,
        "all_original_outcomes":dict(totals),
        "outcomes_by_family_state_host_and_arm":by_family,
        "source_CNF_SHA256":m.SHA,
        "original_worker_JSON_SHA256":checksums,
        "independent_external_witness":"NOT_OBTAINED_SAME_ADMIN",
        "new_blinded_SAT_sources":0,
        "global_champion":"NOT_ESTABLISHED",
        "C023_main":"UNCHANGED",
        "CPU_timeout_does_not_prove_UNSAT":True,
        "same_host_ratios_only_if_both_sat_and_complete":True,
        "semantic_scope":"Only tautologies, exact canonical duplicates and repeated literals, NOT arbitrary implied clauses, not all SAT-equivalent encodings.",
        "no_claim_of_generalized_SAT_speedup":True}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--in-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.in_dir)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("004E6_RESEARCH_AUDIT_PASS",json.dumps({
      "workers":12,"original_children":96,
      "SAT":result["all_original_outcomes"].get(m.SAT,0),
      "CPU_or_wall_UNKNOWN":sum(x for k,x in result["all_original_outcomes"].items() if k.startswith("UNKNOWN_")),
      "external_blind":False,"C023":"UNCHANGED"},sort_keys=True))
