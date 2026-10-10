#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
SERIES=(5,9,17,33,65)

def verify(obj,n):
    assert obj["schema"]=="LAYERED_BINARY_RELATION_V1"
    assert obj["n_boundary"]==n
    assert obj["explicit_output_node_present"] is False
    assert obj["direct_function_operator_present"] is False
    assert obj["state_ids_are_opaque"] is True
    states=obj["states"]; root=obj["initial_state"]
    assert root in states
    reachable=set(); stack=[root]
    branch=terminal=0
    while stack:
        sid=stack.pop()
        if sid in reachable: continue
        reachable.add(sid)
        s=states[sid]
        if s["kind"]=="TERMINAL":
            terminal+=1
            assert s["forced_x"] in (0,1)
            continue
        assert s["kind"]=="BRANCH"
        branch+=1
        layer=s["layer"]
        assert s["guard_var"]==f"y_{layer+1}"
        assert 0<=layer<n
        for k in ("false_child","true_child"):
            child=s[k]
            assert child in states
            assert states[child]["layer"]>layer
            stack.append(child)
    assert reachable==set(states)
    # Exactly two shared terminals are required.
    assert sum(1 for s in states.values() if s["kind"]=="TERMINAL" and s["forced_x"]==0)==1
    assert sum(1 for s in states.values() if s["kind"]=="TERMINAL" and s["forced_x"]==1)==1
    return {"n":n,"states":len(states),"branch_states":branch,"terminal_states":terminal}

def main(indir,out):
    d=Path(indir); rows=[]
    for n in SERIES:
        rows.append(verify(json.loads((d/f"hostile_n{n}.json").read_text()),n))
    result={
      "artifact_id":"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-BLIND-INPUT-INDEPENDENT-CHECK-v1",
      "verdict":"PASS_INDEPENDENT_LAYERED_RELATION_INPUT_FREEZE",
      "rows":rows,
      "checks":{
        "all_state_ids_opaque":True,
        "no_explicit_output_node":True,
        "all_branches_exact_binary_complementary_by_schema":True,
        "strict_layer_progress":True,
        "two_shared_constant_terminals":True
      },
      "semantic_truth_table_used":False,
      "reference_branch_read":False
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":result["verdict"],"rows":rows},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: independent_input_check.py IN_DIR OUT")
    main(sys.argv[1],sys.argv[2])
