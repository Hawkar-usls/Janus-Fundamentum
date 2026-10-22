#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,time
from pathlib import Path

def canonical_bytes(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()

def synthesize(rel):
    states=rel["states"]
    order=sorted(states,key=lambda sid:states[sid]["layer"],reverse=True)
    proof_nodes={}
    state_proof={}
    hashcons={}
    visits=0
    next_id=0

    def intern_const(value):
        nonlocal next_id
        key=("CONST",int(value))
        if key in hashcons:return hashcons[key]
        pid=f"p{next_id}";next_id+=1
        proof_nodes[pid]={"rule":"CONST","value":int(value)}
        hashcons[key]=pid
        return pid

    def intern_ite(guard,t,f):
        nonlocal next_id
        if t==f:return t
        key=("GUARDED_ITE",guard,t,f)
        if key in hashcons:return hashcons[key]
        pid=f"p{next_id}";next_id+=1
        proof_nodes[pid]={"rule":"GUARDED_ITE","guard":guard,"true_child":t,"false_child":f}
        hashcons[key]=pid
        return pid

    start=time.perf_counter_ns()
    for sid in order:
        visits+=1
        s=states[sid]
        if s["kind"]=="TERMINAL":
            state_proof[sid]=intern_const(s["forced_x"])
        elif s["kind"]=="BRANCH":
            t=state_proof[s["true_child"]]
            f=state_proof[s["false_child"]]
            state_proof[sid]=intern_ite(s["guard_var"],t,f)
        else:
            raise ValueError("unsupported state kind")
    root=state_proof[rel["initial_state"]]
    elapsed=time.perf_counter_ns()-start
    candidate={
      "schema":"PROOF_CARRYING_LAYERED_WITNESS_V1",
      "domain":{"class":"TRUE_BY_TOTAL_DETERMINISTIC_LAYERED_RELATION"},
      "witness_root":root,
      "proof_nodes":proof_nodes,
      "state_proof":state_proof,
      "derivation":{
        "algorithm":"GENERIC_LAYERED_GUARDED_BACKWARD_SYNTHESIS_V1",
        "allowed_rules_used":sorted(set(n["rule"] for n in proof_nodes.values())),
        "special_function_recognizer_used":False,
        "reference_import_used":False,
        "SAT_solver_calls":0,
        "generic_validity_calls":0,
        "truth_table_enumeration":False
      },
      "metrics":{
        "S_synth_DAG_nodes":len(proof_nodes),
        "S_synth_DAG_bytes":len(canonical_bytes({"root":root,"nodes":proof_nodes})),
        "T_synth_ns":elapsed,
        "max_live_shared_nodes":len(proof_nodes),
        "constructor_state_visits":visits
      }
    }
    return candidate

def main(inp,out):
    rel=json.loads(Path(inp).read_text())
    result=synthesize(rel)
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"root":result["witness_root"],"metrics":result["metrics"]},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: constructor.py RELATION.json OUT.json")
    main(sys.argv[1],sys.argv[2])
