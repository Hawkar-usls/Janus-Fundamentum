#!/usr/bin/env python3
from __future__ import annotations
import json,sys,time
from pathlib import Path

SERIES=(5,9,17,33,65)

def build(n:int):
    assert n%2==1 and n>=1
    t=(n+1)//2
    nodes={}
    calls=0
    def rec(i,c):
        nonlocal calls
        calls+=1
        if c>=t:
            return "T"
        if c+(n-i)<t:
            return "F"
        sid=f"S_{i}_{c}"
        if sid in nodes:
            return sid
        nodes[sid]={
            "state":[i,c],
            "guard_var":i+1,
            "false_child":None,
            "true_child":None
        }
        nodes[sid]["false_child"]=rec(i+1,c)
        nodes[sid]["true_child"]=rec(i+1,c+1)
        return sid
    start=time.perf_counter_ns()
    root=rec(0,0)
    elapsed=time.perf_counter_ns()-start
    edges=2*len(nodes)
    return {
      "n":n,"threshold":t,"root":root,
      "terminals":{"T":{"value":1},"F":{"value":0}},
      "nodes":nodes,
      "metrics":{
        "reachable_nonterminal_states":len(nodes),
        "total_DAG_nodes":len(nodes)+2,
        "edges":edges,
        "builder_steps":calls,
        "build_time_ns":elapsed
      },
      "construction":"CANONICAL_COUNTING_STATE_DAG",
      "truth_table_enumeration":False,
      "sat_solver_calls":0
    }

def main(out_dir):
    d=Path(out_dir); d.mkdir(parents=True,exist_ok=True)
    summary=[]
    for n in SERIES:
        obj=build(n)
        p=d/f"majority_reference_n{n}.json"
        p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        summary.append({k:obj["metrics"][k] for k in ("reachable_nonterminal_states","total_DAG_nodes","edges","builder_steps")} | {"n":n,"threshold":obj["threshold"],"path":str(p)})
    out={
      "artifact_id":"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-REFERENCE-DAG-RESULT-2026-09-18-v1.0",
      "series":summary,
      "claim":"Finite exact node counts for a canonical O(n^2) counting-state decision DAG; representation baseline only.",
      "scientific_firewall":{"synthesis_not_tested":True,"GENERAL_SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"}
    }
    (d/"reference_summary.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: reference_builder.py OUT_DIR")
    main(sys.argv[1])
