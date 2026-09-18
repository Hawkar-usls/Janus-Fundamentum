#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

SERIES=(5,9,17,33,65)
SALT="U_PAIR_1J_IMPLICIT_MAJORITY_HOSTILE_V1"

def sid(n,i,c):
    return "q_"+hashlib.sha256(f"{SALT}|{n}|{i}|{c}".encode()).hexdigest()[:20]
def tid(n,v):
    return "z_"+hashlib.sha256(f"{SALT}|{n}|terminal|{v}".encode()).hexdigest()[:20]

def expected(n):
    t=(n+1)//2; T=tid(n,1); F=tid(n,0)
    states={}; layers={str(i):[] for i in range(n)}; seen={}
    def rec(i,c):
        if c>=t:return T
        if c+(n-i)<t:return F
        if (i,c) in seen:return seen[(i,c)]
        q=sid(n,i,c);seen[(i,c)]=q
        states[q]={"layer":i,"guard_var":f"y_{i+1}","true_child":None,"false_child":None}
        layers[str(i)].append(q)
        states[q]["false_child"]=rec(i+1,c)
        states[q]["true_child"]=rec(i+1,c+1)
        return q
    root=rec(0,0)
    for xs in layers.values():xs.sort()
    return root,states,layers,{T:{"force_witness":{"variable":"x","value":1}},F:{"force_witness":{"variable":"x","value":0}}}

def main(indir,out):
    d=Path(indir);rows=[]
    for n in SERIES:
        obj=json.loads((d/f"implicit_majority_hostile_n{n}.json").read_text())
        root,states,layers,terms=expected(n)
        assert obj["root_state"]==root
        assert obj["states"]==states
        assert obj["layers"]==layers
        assert obj["terminals"]==terms
        assert obj["blind_surface"]=={
          "count_labels_exposed":False,
          "threshold_exposed":False,
          "explicit_majority_output_node":False,
          "existing_witness_DAG_node":False
        }
        # Structural audit independent of candidate synthesis.
        for q,nd in obj["states"].items():
            assert nd["guard_var"]==f"y_{nd['layer']+1}"
            for child in (nd["true_child"],nd["false_child"]):
                if child in obj["states"]:
                    assert obj["states"][child]["layer"]==nd["layer"]+1
                else:
                    assert child in obj["terminals"]
        rows.append({"n":n,"states":len(states),"root":root,"opaque_id_prefix_ok":all(q.startswith("q_") for q in states)})
    result={
      "artifact_id":"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-HOSTILE-INPUT-INDEPENDENT-CHECK-v1",
      "verdict":"PASS_INDEPENDENT_IMPLICIT_MAJORITY_HOSTILE_INPUT_FREEZE",
      "rows":rows,
      "candidate_constructor_imported":False,
      "reference_branch_imported":False
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: hostile_input_check.py INDIR OUT")
    main(sys.argv[1],sys.argv[2])
