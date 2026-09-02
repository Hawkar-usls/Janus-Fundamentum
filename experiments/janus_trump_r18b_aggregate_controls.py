#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from collections import Counter
from pathlib import Path
IDS=("R16-W05","R16-W06","R16-W07","R16-W08")

def aggregate(d):
    rows=[]
    for wid in IDS:
        p=d/f"JANUS_TRUMP_R18B_{wid}_RESULT_2026-09-02.json"
        if not p.exists(): return {"overall_verdict":"FAIL_INTEGRITY","reason":f"MISSING:{wid}","P_VS_NP":"OPEN"}
        x=json.loads(p.read_text()); rows.append({
            "id":wid,"suite":x["source"]["suite"],"n":x["source"]["n"],"bridge":x["source"]["bridge_variable_count"],"verdict":x["verdict"],
            "candidate_status":x["candidate"].get("status"),"elapsed_seconds":x["candidate"].get("elapsed_seconds"),"final_active_nodes":x["candidate"].get("final_active_nodes"),
            "max_nodes_seen":x["candidate"].get("maximum_nodes_seen_before_gc"),"nodes_created_total":x["candidate"].get("nodes_created_total"),"restrict_calls":x["candidate"].get("restrict_calls_total"),
            "compression_vs_width3_checkpoint":x["candidate"].get("compression_vs_R16_width3_checkpoint"),
            "original_allowed":x.get("comparison",{}).get("original_allowed"),"candidate_allowed":x.get("comparison",{}).get("candidate_allowed"),
            "false_positive":x.get("comparison",{}).get("false_positive_count"),"false_negative":x.get("comparison",{}).get("false_negative_count"),
            "truth_hash":x.get("comparison",{}).get("original_truth_table_sha256")
        })
    c=Counter(r["verdict"] for r in rows)
    if c["FAIL_INTEGRITY"]: overall="FAIL_INTEGRITY"
    elif c["MISMATCH_POST_DISCOVERY_CONTROL"]: overall="R18B_CONTROL_MISMATCH"
    elif c["OPEN_RESOURCE_LIMIT"]: overall="R18B_CONTROL_RESOURCE_OPEN"
    elif c["PASS_EXACT_POST_DISCOVERY_CONTROL"]==4: overall="R18B_PASS_EXACT_4_OF_4__R19_FRESH_UNSEEN_AUTHORIZED"
    else: overall="FAIL_INTEGRITY"
    return {"schema":"JANUS/TRUMP/R18B/POST_DISCOVERY_SEMANTIC_CONTROLS/AGGREGATE_RESULT/v1.0","created_date":"2026-09-02","overall_verdict":overall,"verdict_counts":dict(c),"worlds":rows,
            "scientific_interpretation":"These four controls have unread bridge truth but exposed structures. 4/4 exact success validates post-discovery semantics and authorizes a genuinely fresh R19 selector; it is not itself fresh structural unseen evidence.",
            "next_gate":"R19_FRESH_PROSPECTIVE_UNSEEN_SHANNON_DAG_HOLDOUT" if overall.startswith("R18B_PASS") else "FREEZE_R18B_RESULT_AND_INVESTIGATE_WITHOUT_TUNING",
            "claim_ceiling":"No global polynomial bound, arbitrary-CNF totality, SAT-in-P, P=NP, or P!=NP claim.","seal":"CAPTAIN_OBVIOUS_SAYS__PASS_THE_CONTROL_ROOM_BEFORE_THE_FIELD_TEST","P_VS_NP":"OPEN"}

def main():
    a=argparse.ArgumentParser(); a.add_argument('--input-dir',required=True); a.add_argument('--output',required=True); z=a.parse_args(); out=aggregate(Path(z.input_dir)); Path(z.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print(json.dumps(out,indent=2,sort_keys=True)); return 2 if out['overall_verdict']=='FAIL_INTEGRITY' else 0
if __name__=='__main__': raise SystemExit(main())
