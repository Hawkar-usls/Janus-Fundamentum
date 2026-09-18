#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import os
import random
import sys
from pathlib import Path

import numpy as np

SERIES=(16,32,64,128,256)
DEGREE=3
OR3_PER_VERTEX=2
SPECTRAL_THRESHOLD=0.99
TAG="U_PAIR_1J_CONNECTED_MIXED_AFFINE_OR3_EXPANDER_INTERLEAVE_2026_09_18"
PREREG_COMMIT="f1be149a9b34963ff410f40f606c5633e7f21063"
QUALIFICATION_ADDENDUM_COMMIT="5da0fbb9b5270fa29f77dbee6d1afd70e8801e25"


def canonical_bytes(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()


def sha256_bytes(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path:Path)->str:
    return sha256_bytes(path.read_bytes())


def derive_int(seed_hex:str,label:str)->int:
    return int(hashlib.sha256(bytes.fromhex(seed_hex)+b"|" + label.encode()).hexdigest()[:16],16)


def opaque(seed_hex:str,prefix:str,label:str)->str:
    return prefix+"_"+hashlib.sha256(bytes.fromhex(seed_hex)+b"|" + label.encode()).hexdigest()[:20]


def graph_for(n:int,seed_hex:str):
    for attempt in range(100000):
        rnd=random.Random(derive_int(seed_hex,f"GRAPH|n={n}|attempt={attempt}"))
        stubs=[v for v in range(n) for _ in range(DEGREE)]
        rnd.shuffle(stubs)
        edges=[]; seen=set(); ok=True
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
        adj=[set() for _ in range(n)]
        for a,b in edges:
            adj[a].add(b); adj[b].add(a)
        if any(len(xs)!=DEGREE for xs in adj):
            continue
        reached={0}; stack=[0]
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v not in reached:
                    reached.add(v); stack.append(v)
        if len(reached)!=n:
            continue
        return sorted(edges),adj,attempt
    raise RuntimeError("simple connected 3-regular graph generation exhausted")


def lambda2_ratio(n:int,edges)->float:
    A=np.zeros((n,n),dtype=float)
    for a,b in edges:
        A[a,b]=A[b,a]=1.0
    vals=np.sort(np.linalg.eigvalsh(A))[::-1]
    return float(vals[1]/DEGREE)


def selector_id(kind:str,var_id:str)->str:
    return ("pt_" if kind=="t" else "pf_")+hashlib.sha256((kind+"|"+var_id).encode()).hexdigest()[:20]


def compile_pair_positive_or3(source:dict)->dict:
    semantic_vars=list(source["boundary_vars"])
    for v in source["vertices"]:
        semantic_vars.extend([v["x_var"],v["s_var"]])
    if len(semantic_vars)!=len(set(semantic_vars)):
        raise ValueError("semantic variable collision")
    sel={z:{"t":selector_id("t",z),"f":selector_id("f",z)} for z in semantic_vars}
    return {
      "schema":"PAIR_POSITIVE_OR3_AFFINE_MIXED_V1",
      "source_schema":source["schema"],
      "n_vertices":source["n_vertices"],
      "boundary_semantic_vars":list(source["boundary_vars"]),
      "witness_semantic_vars":[z for v in source["vertices"] for z in (v["x_var"],v["s_var"])],
      "selector_map":sel,
      "pair_affine_factors":[
          {"semantic_var":z,"vars":[sel[z]["t"],sel[z]["f"]],"rhs":1}
          for z in semantic_vars
      ],
      "mixed_affine_factors":[
          {
            "factor_id":f["factor_id"],
            "vars":[sel[z]["t"] for z in f["vars"]],
            "rhs":f["rhs"]
          }
          for f in source["affine_factors"]
      ],
      "positive_or3_clauses":[
          {
            "clause_id":c["clause_id"],
            "selectors":[sel[l["var"]]["t" if l["positive"] else "f"] for l in c["literals"]]
          }
          for c in source["or3_clauses"]
      ],
      "compiler_provenance":{
        "mapping":"z->(t_z,f_z), t_z XOR f_z=1; +z->t_z; -z->f_z",
        "truth_table_enumeration":False
      }
    }


def clause_schedule(n:int,adj,seed_hex:str,plant_x,plant_s,x_ids,s_ids):
    for schedule_attempt in range(10000):
        rnd=random.Random(derive_int(seed_hex,f"CLAUSES|n={n}|attempt={schedule_attempt}"))
        clauses=[]; coverage=[0]*n; ok=True
        for j in range(OR3_PER_VERTEX*n):
            triple=None
            for _ in range(2000):
                vs=rnd.sample(range(n),3)
                if all(b not in adj[a] for a,b in itertools.combinations(vs,2)):
                    triple=vs; break
            if triple is None:
                ok=False; break
            roles=["x","s",rnd.choice(["x","s"])]
            rnd.shuffle(roles)
            true_slot=rnd.randrange(3)
            literals=[]
            for slot,(v,role) in enumerate(zip(triple,roles)):
                var_id=x_ids[v] if role=="x" else s_ids[v]
                value=plant_x[v] if role=="x" else plant_s[v]
                desired_truth=(slot==true_slot)
                positive=(value==int(desired_truth))
                literals.append({
                    "var":var_id,
                    "positive":bool(positive),
                    "vertex_index":v,
                    "role":role
                })
                coverage[v]+=1
            clauses.append({
                "clause_id":opaque(seed_hex,"oc",f"OR3|n={n}|attempt={schedule_attempt}|j={j}"),
                "literals":literals
            })
        if ok and min(coverage)>=2:
            return clauses,coverage,schedule_attempt
    raise RuntimeError("OR3 cross-neighborhood schedule exhausted")


def build_one(n:int,seed_hex:str,outdir:Path,plantdir:Path):
    edges_idx,adj,graph_attempt=graph_for(n,seed_hex)
    ratio=lambda2_ratio(n,edges_idx)

    vertex_ids=[opaque(seed_hex,"qv",f"VERTEX|n={n}|i={i}") for i in range(n)]
    x_ids=[opaque(seed_hex,"qx",f"X|n={n}|i={i}") for i in range(n)]
    s_ids=[opaque(seed_hex,"qs",f"S|n={n}|i={i}") for i in range(n)]

    edge_records=[]
    incident=[[] for _ in range(n)]
    boundary_vars=[]
    for j,(a,b) in enumerate(edges_idx):
        y=opaque(seed_hex,"qy",f"BOUNDARY|n={n}|j={j}|a={a}|b={b}")
        boundary_vars.append(y)
        edge_records.append({
            "edge_id":opaque(seed_hex,"qe",f"EDGE|n={n}|j={j}|a={a}|b={b}"),
            "u":vertex_ids[a],
            "v":vertex_ids[b],
            "u_index":a,
            "v_index":b,
            "boundary_var":y
        })
        incident[a].append(y); incident[b].append(y)

    rnd=random.Random(derive_int(seed_hex,f"PLANT_AND_CONSTANTS|n={n}"))
    plant_y={y:rnd.randrange(2) for y in boundary_vars}
    plant_x=[rnd.randrange(2) for _ in range(n)]
    constants=[rnd.randrange(2) for _ in range(n)]
    plant_s=[]
    for v in range(n):
        parity=constants[v]^plant_x[v]
        for y in incident[v]:
            parity ^= plant_y[y]
        plant_s.append(parity)

    clauses,coverage,clause_attempt=clause_schedule(
        n,adj,seed_hex,plant_x,plant_s,x_ids,s_ids
    )

    vertices=[
      {
        "vertex_id":vertex_ids[v],
        "vertex_index":v,
        "x_var":x_ids[v],
        "s_var":s_ids[v],
        "affine_constant":constants[v]
      }
      for v in range(n)
    ]

    affine_factors=[
      {
        "factor_id":opaque(seed_hex,"af",f"AFFINE|n={n}|v={v}"),
        "vertex_id":vertex_ids[v],
        "vertex_index":v,
        "vars":[x_ids[v],s_ids[v]]+sorted(incident[v]),
        "rhs":constants[v]
      }
      for v in range(n)
    ]

    source={
      "schema":"MIXED_AFFINE_OR3_EXPANDER_RELATION_V1",
      "target":"CONNECTED_MIXED_AFFINE_OR3_EXPANDER_INTERLEAVE",
      "n_vertices":n,
      "graph_degree":DEGREE,
      "n_edges":len(edge_records),
      "boundary_vars":boundary_vars,
      "vertices":vertices,
      "edges":edge_records,
      "affine_factors":affine_factors,
      "or3_clauses":clauses,
      "domain_contract":{
        "definition":"D_n(Y)=exists X,S F_n(X,S,Y)",
        "totality_assumed":False,
        "exact_domain_required":True
      },
      "witness_contract":{
        "witness_vars":[z for v in vertices for z in (v["x_var"],v["s_var"])],
        "conditional_on_exact_domain":True,
        "explicit_output_DAG_nodes_present":False,
        "precomputed_Skolem_functions_present":False
      },
      "source_provenance":{
        "prereg_commit":PREREG_COMMIT,
        "qualification_addendum_commit":QUALIFICATION_ADDENDUM_COMMIT,
        "seed_commitment":sha256_bytes(bytes.fromhex(seed_hex)),
        "graph_attempt":graph_attempt,
        "or3_schedule_attempt":clause_attempt,
        "graph_selection_uses_spectral_metric":False,
        "planted_assignment_committed":False,
        "constructor_implemented_at_source_freeze":False
      },
      "qualification_record":{
        "simple":True,
        "connected":True,
        "regular_degree":DEGREE,
        "lambda2_over_degree":ratio,
        "spectral_threshold":SPECTRAL_THRESHOLD,
        "finite_spectral_stress_gate_pass":ratio<=SPECTRAL_THRESHOLD,
        "or3_clause_count":len(clauses),
        "min_or3_vertex_coverage":min(coverage),
        "max_or3_vertex_coverage":max(coverage)
      }
    }

    sp=outdir/f"source_n{n}.json"
    sp.write_text(json.dumps(source,indent=2,sort_keys=True)+"\n")
    compiled=compile_pair_positive_or3(source)
    cp=outdir/f"pair_positive_or3_n{n}.json"
    cp.write_text(json.dumps(compiled,indent=2,sort_keys=True)+"\n")

    plant_assign=dict(plant_y)
    for v in range(n):
        plant_assign[x_ids[v]]=plant_x[v]
        plant_assign[s_ids[v]]=plant_s[v]
    pp=plantdir/f"plant_n{n}.json"
    pp.write_text(json.dumps({
        "n":n,
        "source_sha256":sha256_path(sp),
        "pair_compiled_sha256":sha256_path(cp),
        "assignments":plant_assign
    },indent=2,sort_keys=True)+"\n")

    return {
      "n":n,
      "source_file":sp.name,
      "source_sha256":sha256_path(sp),
      "pair_compiled_file":cp.name,
      "pair_compiled_sha256":sha256_path(cp),
      "graph_attempt":graph_attempt,
      "or3_schedule_attempt":clause_attempt,
      "lambda2_over_degree":ratio,
      "min_or3_vertex_coverage":min(coverage),
      "max_or3_vertex_coverage":max(coverage)
    }


def main(outdir_s:str,plantdir_s:str):
    seed_hex=os.environ.get("SOURCE_SEED_HEX","")
    if len(seed_hex)!=64:
        raise SystemExit("SOURCE_SEED_HEX must be a hidden 32-byte hex seed")
    bytes.fromhex(seed_hex)
    outdir=Path(outdir_s); plantdir=Path(plantdir_s)
    outdir.mkdir(parents=True,exist_ok=True)
    plantdir.mkdir(parents=True,exist_ok=True)

    rows=[build_one(n,seed_hex,outdir,plantdir) for n in SERIES]
    manifest={
      "artifact_id":"JANUS-U-PAIR-1J-CONNECTED-MIXED-AFFINE-OR3-EXPANDER-INTERLEAVE-SOURCE-FREEZE-MANIFEST-2026-09-18-v1.0",
      "prereg_commit":PREREG_COMMIT,
      "qualification_addendum_commit":QUALIFICATION_ADDENDUM_COMMIT,
      "seed_commitment":sha256_bytes(bytes.fromhex(seed_hex)),
      "series":rows,
      "selection_firewall":{
        "raw_seed_committed":False,
        "planted_assignment_committed":False,
        "resampling_after_constructor_observation":False,
        "spectral_metric_used_for_graph_selection":False,
        "constructor_not_implemented_at_source_freeze":True
      }
    }
    (outdir/"source_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "artifact_id":manifest["artifact_id"],
      "seed_commitment":manifest["seed_commitment"],
      "series":[{"n":r["n"],"lambda2_over_degree":r["lambda2_over_degree"]} for r in rows]
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: source_generator.py OUT_DIR EPHEMERAL_PLANT_DIR")
    main(sys.argv[1],sys.argv[2])
