#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, random, sys
from pathlib import Path
import numpy as np

SERIES=(16,32,64,128,256)
DEGREE=3
THRESHOLD=0.99
TAG="U_PAIR_1J_TSEITIN_EXPANDER_SEARCH_2026_09_18"
PREREG_COMMIT="854da3147c84e32f43ffc4e9205c761766775e08"

def h16(s:str)->str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]

def seed_int(s:str)->int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:16],16)

def generate_3_regular(n:int):
    for attempt in range(100000):
        rnd=random.Random(seed_int(f"{TAG}|GRAPH|n={n}|attempt={attempt}"))
        stubs=[v for v in range(n) for _ in range(DEGREE)]
        rnd.shuffle(stubs)
        seen=set(); edges=[]; ok=True
        for i in range(0,len(stubs),2):
            a,b=stubs[i],stubs[i+1]
            if a==b:
                ok=False; break
            e=tuple(sorted((a,b)))
            if e in seen:
                ok=False; break
            seen.add(e); edges.append(e)
        if not ok:
            continue
        adj=[[] for _ in range(n)]
        for a,b in edges:
            adj[a].append(b); adj[b].append(a)
        if any(len(xs)!=DEGREE for xs in adj):
            continue
        stack=[0]; seen_v={0}
        for x in stack:
            for y in adj[x]:
                if y not in seen_v:
                    seen_v.add(y); stack.append(y)
        if len(seen_v)!=n:
            continue
        return sorted(edges),attempt
    raise RuntimeError("failed deterministic simple connected 3-regular generation")

def lambda2_ratio(n:int,edges):
    A=np.zeros((n,n),dtype=float)
    for a,b in edges:
        A[a,b]=A[b,a]=1.0
    vals=np.linalg.eigvalsh(A)
    vals=np.sort(vals)[::-1]
    return float(vals[1]/DEGREE)

def charge_bits(n:int):
    bits=[seed_int(f"{TAG}|CHARGE|n={n}|v={v}") & 1 for v in range(n)]
    adjusted=False
    if sum(bits)%2==0:
        bits[0]^=1
        adjusted=True
    return bits,adjusted

def write_source(n:int,outdir:Path):
    edges,attempt=generate_3_regular(n)
    ratio=lambda2_ratio(n,edges)
    charge,adjusted=charge_bits(n)
    vids=[f"qv_{h16(f'{TAG}|VERTEX|n={n}|v={v}')}" for v in range(n)]
    erecs=[]
    for j,(a,b) in enumerate(edges):
        erecs.append({
            "edge_id":f"qe_{h16(f'{TAG}|EDGE|n={n}|j={j}|a={a}|b={b}')}",
            "u":vids[a],"v":vids[b],
            "boundary_var":f"y_{h16(f'{TAG}|BOUNDARY|n={n}|j={j}|a={a}|b={b}')}"
        })
    obj={
      "schema":"TSEITIN_EXPANDER_SEARCH_SOURCE_V1",
      "target":"TSEITIN_EXPANDER_SEARCH_RELATIONS",
      "n_vertices":n,"degree":DEGREE,"n_edges":len(erecs),
      "witness_bits":[f"w_{i}" for i in range(int(math.log2(n)))],
      "witness_decode_order":vids,
      "vertices":[{"vertex_id":vids[v],"charge":charge[v]} for v in range(n)],
      "edges":erecs,
      "source_provenance":{
        "generator_tag":TAG,
        "graph_attempt":attempt,
        "charge_parity_adjusted_at_fixed_vertex_zero":adjusted,
        "graph_selection_uses_spectral_metric":False
      },
      "qualification_record":{
        "simple":True,"regular_degree":DEGREE,"connected":True,
        "charge_xor":sum(charge)%2,
        "lambda2_over_degree":ratio,
        "threshold":THRESHOLD,
        "finite_spectral_stress_gate_pass":ratio<=THRESHOLD
      },
      "constructor_visible_semantics":{
        "boundary":"one bit per frozen edge",
        "local_violation":"charge(vertex) XOR XOR incident boundary edge bits",
        "witness":"binary code of any violated vertex",
        "domain":"TRUE_BY_ODD_CHARGE_PARITY",
        "explicit_search_output_node_present":False,
        "precomputed_violation_DAG_nodes_present":False
      }
    }
    p=outdir/f"source_n{n}.json"
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    return {
      "n":n,"file":p.name,
      "sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
      "graph_attempt":attempt,
      "lambda2_over_degree":ratio,
      "charge_weight":sum(charge)
    }

def main(outdir_s:str):
    outdir=Path(outdir_s); outdir.mkdir(parents=True,exist_ok=True)
    rows=[write_source(n,outdir) for n in SERIES]
    manifest={
      "artifact_id":"JANUS-U-PAIR-1J-TSEITIN-EXPANDER-SEARCH-SOURCE-FREEZE-MANIFEST-2026-09-18-v1.0",
      "prereg_commit":PREREG_COMMIT,
      "generator_tag":TAG,
      "series":rows,
      "selection_firewall":{
        "spectral_metric_used_for_graph_selection":False,
        "resampling_after_constructor_observation":False,
        "constructor_not_implemented_at_source_freeze":True
      }
    }
    (outdir/"source_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(manifest,sort_keys=True))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: input_generator.py OUT_DIR")
    main(sys.argv[1])
