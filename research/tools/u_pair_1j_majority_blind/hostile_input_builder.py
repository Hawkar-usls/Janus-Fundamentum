#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

SERIES=(5,9,17,33,65)
SALT="U_PAIR_1J_IMPLICIT_MAJORITY_HOSTILE_V1"

def opaque_state(n,i,c):
    h=hashlib.sha256(f"{SALT}|{n}|{i}|{c}".encode()).hexdigest()[:20]
    return f"q_{h}"

def opaque_terminal(n,value):
    h=hashlib.sha256(f"{SALT}|{n}|terminal|{value}".encode()).hexdigest()[:20]
    return f"z_{h}"

def build(n):
    t=(n+1)//2
    T=opaque_terminal(n,1); F=opaque_terminal(n,0)
    states={}
    layers={str(i):[] for i in range(n)}
    memo={}
    def rec(i,c):
        if c>=t: return T
        if c+(n-i)<t: return F
        key=(i,c)
        if key in memo: return memo[key]
        sid=opaque_state(n,i,c); memo[key]=sid
        states[sid]={"layer":i,"guard_var":f"y_{i+1}","true_child":None,"false_child":None}
        layers[str(i)].append(sid)
        states[sid]["false_child"]=rec(i+1,c)
        states[sid]["true_child"]=rec(i+1,c+1)
        return sid
    root=rec(0,0)
    for xs in layers.values(): xs.sort()
    return {
      "artifact_id":f"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-HOSTILE-INPUT-n{n}-v1",
      "family":"ODD_IMPLICIT_MAJORITY_SKOL_RELATION",
      "n":n,
      "boundary_variables":[f"y_{i}" for i in range(1,n+1)],
      "witness_variable":"x",
      "root_state":root,
      "layers":layers,
      "states":states,
      "terminals":{
        T:{"force_witness":{"variable":"x","value":1}},
        F:{"force_witness":{"variable":"x","value":0}}
      },
      "blind_surface":{
        "count_labels_exposed":False,
        "threshold_exposed":False,
        "explicit_majority_output_node":False,
        "existing_witness_DAG_node":False
      },
      "structural_contract":{
        "each_nonterminal_has_one_boundary_guard":True,
        "children_are_exact_complementary_guard_branches":True,
        "layer_strictly_increases":True,
        "terminal_witness_force_is_local":True
      }
    }

def main(outdir):
    d=Path(outdir); d.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n in SERIES:
        obj=build(n)
        p=d/f"implicit_majority_hostile_n{n}.json"
        p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        rows.append({"n":n,"path":str(p),"states":len(obj["states"]),"terminals":len(obj["terminals"])})
    receipt={
      "artifact_id":"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-HOSTILE-INPUT-SOURCE-FREEZE-2026-09-18-v1.0",
      "series":rows,
      "generation_authority":{
        "semantic_family":"x = MAJ_n(Y)",
        "opaque_state_surface":True,
        "truth_table_enumeration":False,
        "SAT_solver_calls":0
      },
      "constructor_visibility_contract":{
        "constructor_reads_generated_input_only":True,
        "constructor_imports_this_builder":False,
        "constructor_may_not_decode_opaque_state_ids":True
      }
    }
    (d/"source_freeze_receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: hostile_input_builder.py OUTDIR")
    main(sys.argv[1])
