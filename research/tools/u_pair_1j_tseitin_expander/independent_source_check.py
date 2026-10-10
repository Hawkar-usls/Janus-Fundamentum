#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math,sys
from collections import deque
from pathlib import Path
import numpy as np

DEGREE=3
THRESHOLD=0.99
SERIES=(16,32,64,128,256)

def sha256_path(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check_one(p:Path,row:dict):
    obj=json.loads(p.read_text())
    n=obj["n_vertices"]
    assert n==row["n"] and n in SERIES
    assert obj["schema"]=="TSEITIN_EXPANDER_SEARCH_SOURCE_V1"
    assert obj["target"]=="TSEITIN_EXPANDER_SEARCH_RELATIONS"
    assert obj["degree"]==DEGREE
    assert n & (n-1)==0
    assert len(obj["witness_bits"])==int(math.log2(n))
    vids=[v["vertex_id"] for v in obj["vertices"]]
    assert len(vids)==n and len(set(vids))==n
    assert obj["witness_decode_order"]==vids
    charges={v["vertex_id"]:int(v["charge"]) for v in obj["vertices"]}
    assert set(charges.values()) <= {0,1}
    assert sum(charges.values())%2==1

    edges=obj["edges"]
    assert len(edges)==3*n//2==obj["n_edges"]
    degree={v:0 for v in vids}; seen=set(); bvars=set()
    A=np.zeros((n,n),dtype=float); pos={v:i for i,v in enumerate(vids)}
    for e in edges:
        u,v=e["u"],e["v"]
        assert u in degree and v in degree and u!=v
        key=tuple(sorted((u,v)))
        assert key not in seen; seen.add(key)
        assert e["boundary_var"] not in bvars; bvars.add(e["boundary_var"])
        degree[u]+=1; degree[v]+=1
        A[pos[u],pos[v]]=A[pos[v],pos[u]]=1.0
    assert all(x==DEGREE for x in degree.values())

    q=deque([vids[0]]); reached={vids[0]}
    adj={v:[] for v in vids}
    for u,v in seen:
        adj[u].append(v); adj[v].append(u)
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in reached:
                reached.add(v); q.append(v)
    assert len(reached)==n

    vals=np.sort(np.linalg.eigvalsh(A))[::-1]
    ratio=float(vals[1]/DEGREE)
    assert ratio<=THRESHOLD
    assert abs(ratio-float(obj["qualification_record"]["lambda2_over_degree"])) < 1e-10
    assert obj["qualification_record"]["finite_spectral_stress_gate_pass"] is True
    assert obj["source_provenance"]["graph_selection_uses_spectral_metric"] is False
    sem=obj["constructor_visible_semantics"]
    assert sem["explicit_search_output_node_present"] is False
    assert sem["precomputed_violation_DAG_nodes_present"] is False
    return {
      "n":n,"n_edges":len(edges),"charge_xor":1,
      "lambda2_over_degree":ratio,
      "source_sha256":sha256_path(p),
      "simple_3_regular_connected":True
    }

def main(srcdir_s:str,out_s:str,freeze_sha:str):
    src=Path(srcdir_s); manifest=json.loads((src/"source_manifest.json").read_text())
    assert manifest["prereg_commit"]=="854da3147c84e32f43ffc4e9205c761766775e08"
    assert manifest["selection_firewall"]["constructor_not_implemented_at_source_freeze"] is True
    assert manifest["selection_firewall"]["spectral_metric_used_for_graph_selection"] is False
    assert [r["n"] for r in manifest["series"]]==list(SERIES)
    rows=[]
    for row in manifest["series"]:
        p=src/row["file"]
        assert sha256_path(p)==row["sha256"]
        got=check_one(p,row)
        assert got["source_sha256"]==row["sha256"]
        rows.append(got)
    result={
      "artifact_id":"JANUS-U-PAIR-1J-TSEITIN-EXPANDER-SEARCH-INDEPENDENT-SOURCE-CHECK-2026-09-18-v1.0",
      "source_freeze_commit":freeze_sha,
      "prereg_commit":manifest["prereg_commit"],
      "checks":{
        "all_sha256_match_manifest":True,
        "all_simple_3_regular_connected":True,
        "all_odd_charge":True,
        "all_finite_spectral_stress_gate_pass":True,
        "no_explicit_search_output_nodes":True,
        "no_precomputed_violation_DAG_nodes":True,
        "constructor_not_implemented_at_source_freeze":True
      },
      "rows":rows,
      "verdict":"PASS_SOURCE_FREEZE_INDEPENDENT_CHECK",
      "scientific_firewall":{
        "finite_spectral_gate_is_not_asymptotic_expander_theorem":True,
        "hostile_synthesis_not_run":True,
        "GENERAL_SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN"
      }
    }
    Path(out_s).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("usage: independent_source_check.py SRC_DIR OUT_JSON SOURCE_FREEZE_SHA")
    main(sys.argv[1],sys.argv[2],sys.argv[3])
