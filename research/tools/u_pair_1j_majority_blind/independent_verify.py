#!/usr/bin/env python3
from __future__ import annotations
import json,sys,time
from pathlib import Path

def verify(rel,cand):
    assert rel["schema"]=="LAYERED_BINARY_RELATION_V1"
    assert cand["schema"]=="PROOF_CARRYING_LAYERED_WITNESS_V1"
    assert cand["derivation"]["reference_import_used"] is False
    assert cand["derivation"]["SAT_solver_calls"]==0
    assert cand["derivation"]["generic_validity_calls"]==0
    assert cand["derivation"]["truth_table_enumeration"] is False
    states=rel["states"]; nodes=cand["proof_nodes"]; sp=cand["state_proof"]
    assert set(sp)==set(states)
    start=time.perf_counter_ns(); visits=0
    order=sorted(states,key=lambda sid:states[sid]["layer"],reverse=True)
    for sid in order:
        visits+=1
        s=states[sid]; pid=sp[sid]
        assert pid in nodes
        p=nodes[pid]
        if s["kind"]=="TERMINAL":
            assert p=={"rule":"CONST","value":s["forced_x"]}
        else:
            t=sp[s["true_child"]]; f=sp[s["false_child"]]
            if t==f:
                assert pid==t
            else:
                assert p=={"rule":"GUARDED_ITE","guard":s["guard_var"],"true_child":t,"false_child":f}
    assert cand["witness_root"]==sp[rel["initial_state"]]
    # Domain proof by structural totality, not semantic enumeration.
    reachable=set(); stack=[rel["initial_state"]]
    while stack:
        sid=stack.pop()
        if sid in reachable: continue
        reachable.add(sid); s=states[sid]
        if s["kind"]=="TERMINAL":
            assert s["forced_x"] in (0,1)
        else:
            assert s["false_child"] in states and s["true_child"] in states
            assert states[s["false_child"]]["layer"]>s["layer"]
            assert states[s["true_child"]]["layer"]>s["layer"]
            stack.extend([s["false_child"],s["true_child"]])
    assert reachable==set(states)
    elapsed=time.perf_counter_ns()-start
    return {
      "verdict":"PASS_INDEPENDENT_LAYERED_PROOF_CARRYING_WITNESS",
      "T_verify_ns":elapsed,
      "verifier_node_visits":visits,
      "domain_verified":"TRUE_BY_TOTAL_DETERMINISTIC_COMPLEMENTARY_TRANSITIONS",
      "reference_DAG_read":False,
      "candidate_constructor_imported":False,
      "semantic_truth_table_used":False
    }

def main(relpath,candpath,out):
    result=verify(json.loads(Path(relpath).read_text()),json.loads(Path(candpath).read_text()))
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=4: raise SystemExit("usage: independent_verify.py RELATION CANDIDATE OUT")
    main(sys.argv[1],sys.argv[2],sys.argv[3])
