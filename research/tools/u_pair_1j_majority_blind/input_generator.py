#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

SERIES=(5,9,17,33,65)
SALT="U_PAIR_1J_LAYERED_RELATION_V1_2026_09_18"

def opaque(n,i,c):
    return "q_"+hashlib.sha256(f"{SALT}|{n}|{i}|{c}".encode()).hexdigest()[:20]

def terminal(n,value):
    return "q_"+hashlib.sha256(f"{SALT}|{n}|terminal|{value}".encode()).hexdigest()[:20]

def build(n):
    assert n%2==1
    t=(n+1)//2
    t0=terminal(n,0); t1=terminal(n,1)
    states={
      t0:{"kind":"TERMINAL","layer":n+1,"forced_x":0},
      t1:{"kind":"TERMINAL","layer":n+1,"forced_x":1}
    }
    seen=set()
    def rec(i,c):
        if c>=t: return t1
        if c+(n-i)<t: return t0
        sid=opaque(n,i,c)
        if sid in seen: return sid
        seen.add(sid)
        # Placeholder first so recursion remains deterministic.
        states[sid]={"kind":"BRANCH","layer":i,"guard_var":f"y_{i+1}","false_child":None,"true_child":None}
        states[sid]["false_child"]=rec(i+1,c)
        states[sid]["true_child"]=rec(i+1,c+1)
        return sid
    root=rec(0,0)
    return {
      "schema":"LAYERED_BINARY_RELATION_V1",
      "n_boundary":n,
      "boundary_vars":[f"y_{i}" for i in range(1,n+1)],
      "witness_var":"x",
      "initial_state":root,
      "states":states,
      "explicit_output_node_present":False,
      "direct_function_operator_present":False,
      "state_ids_are_opaque":True,
      "constructor_visible_semantics":{
        "branch":"exact complementary split on one boundary variable",
        "terminal":"local UNIT_OR_CONSTANT_FORCE for x"
      }
    }

def main(outdir):
    d=Path(outdir); d.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n in SERIES:
        obj=build(n)
        p=d/f"hostile_n{n}.json"
        p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
        rows.append({
          "n":n,"path":str(p),"state_count":len(obj["states"]),
          "branch_states":sum(1 for s in obj["states"].values() if s["kind"]=="BRANCH"),
          "terminal_states":2
        })
    manifest={
      "artifact_id":"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-BLIND-INPUT-AUTHORITY-2026-09-18-v1.0",
      "schema":"LAYERED_BINARY_RELATION_V1",
      "series":rows,
      "selection":"Frozen n=5,9,17,33,65 from preregistration.",
      "constructor_visibility":"Only generated relation JSONs and this manifest; state ids are opaque and no direct output node is present.",
      "reference_imported":False
    }
    (d/"input_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: input_generator.py OUT_DIR")
    main(sys.argv[1])
