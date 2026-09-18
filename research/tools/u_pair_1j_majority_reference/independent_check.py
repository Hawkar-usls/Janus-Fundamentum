#!/usr/bin/env python3
from __future__ import annotations
import json,sys
from pathlib import Path
SERIES=(5,9,17,33,65)

def verify(obj):
    n=obj["n"]; t=obj["threshold"]; nodes=obj["nodes"]
    assert t==(n+1)//2
    assert obj["root"]=="S_0_0"
    reachable=set()
    stack=[obj["root"]]
    while stack:
        sid=stack.pop()
        if sid in ("T","F"): continue
        assert sid in nodes,sid
        if sid in reachable: continue
        reachable.add(sid)
        nd=nodes[sid]
        i,c=nd["state"]
        assert sid==f"S_{i}_{c}"
        assert c<t and c+(n-i)>=t
        assert nd["guard_var"]==i+1
        for bit,key in ((0,"false_child"),(1,"true_child")):
            ni=i+1; nc=c+bit
            expected=("T" if nc>=t else ("F" if nc+(n-ni)<t else f"S_{ni}_{nc}"))
            assert nd[key]==expected,(sid,key,nd[key],expected)
            stack.append(expected)
    assert reachable==set(nodes)
    m=obj["metrics"]
    assert m["reachable_nonterminal_states"]==len(nodes)
    assert m["total_DAG_nodes"]==len(nodes)+2
    assert m["edges"]==2*len(nodes)
    return {"n":n,"nodes":len(nodes)+2,"nonterminal":len(nodes),"edges":2*len(nodes)}

def main(indir,out):
    d=Path(indir); rows=[]
    for n in SERIES:
        obj=json.loads((d/f"majority_reference_n{n}.json").read_text())
        rows.append(verify(obj))
    # Direct symbolic bound witnessed by state labels: all nonterminal nodes are a subset
    # of {(i,c):0<=i<=n,0<=c<=i}, whose cardinality is (n+1)(n+2)/2.
    bounds=[]
    for r in rows:
        n=r["n"]; upper=(n+1)*(n+2)//2+2
        assert r["nodes"]<=upper
        bounds.append({"n":n,"observed_nodes":r["nodes"],"quadratic_upper_bound":upper})
    result={
      "artifact_id":"JANUS-U-PAIR-1J-IMPLICIT-MAJORITY-REFERENCE-DAG-INDEPENDENT-CHECK-v1",
      "verdict":"PASS_INDEPENDENT_MAJORITY_REFERENCE_DAG",
      "rows":rows,
      "bounds":bounds,
      "proof_note":"Every nonterminal is uniquely labelled by a reachable pair (i,c); there are at most sum_{i=0}^n(i+1)=(n+1)(n+2)/2 such pairs. Local transitions preserve exact count. Thus this reference family has O(n^2) shared DAG size.",
      "semantic_truth_table_used":False,
      "candidate_synthesis_used":False
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":result["verdict"],"rows":rows},sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=3: raise SystemExit("usage: independent_check.py IN_DIR OUT")
    main(sys.argv[1],sys.argv[2])
