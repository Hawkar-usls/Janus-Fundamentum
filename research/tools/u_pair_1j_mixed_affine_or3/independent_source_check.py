#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import itertools
import json
import math
import sys
from collections import Counter,deque
from pathlib import Path

import numpy as np

SERIES=(16,32,64,128,256)
DEGREE=3
SPECTRAL_THRESHOLD=0.99
PREREG_COMMIT="f1be149a9b34963ff410f40f606c5633e7f21063"
QUALIFICATION_ADDENDUM_COMMIT="5da0fbb9b5270fa29f77dbee6d1afd70e8801e25"


def canonical_bytes(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()


def sha256_path(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def selector_id(kind:str,var_id:str)->str:
    return ("pt_" if kind=="t" else "pf_")+hashlib.sha256((kind+"|"+var_id).encode()).hexdigest()[:20]


def compile_pair_positive_or3(source:dict)->dict:
    semantic_vars=list(source["boundary_vars"])
    for v in source["vertices"]:
        semantic_vars.extend([v["x_var"],v["s_var"]])
    assert len(semantic_vars)==len(set(semantic_vars))
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
          {"factor_id":f["factor_id"],"vars":[sel[z]["t"] for z in f["vars"]],"rhs":f["rhs"]}
          for f in source["affine_factors"]
      ],
      "positive_or3_clauses":[
          {"clause_id":c["clause_id"],"selectors":[sel[l["var"]]["t" if l["positive"] else "f"] for l in c["literals"]]}
          for c in source["or3_clauses"]
      ],
      "compiler_provenance":{
        "mapping":"z->(t_z,f_z), t_z XOR f_z=1; +z->t_z; -z->f_z",
        "truth_table_enumeration":False
      }
    }


def eval_literal(lit,assignment):
    b=bool(assignment[lit["var"]])
    return b if lit["positive"] else (not b)


def check_one(source_path:Path,compiled_path:Path,plant_path:Path,row:dict):
    source=json.loads(source_path.read_text())
    compiled=json.loads(compiled_path.read_text())
    plant=json.loads(plant_path.read_text())

    assert sha256_path(source_path)==row["source_sha256"]==plant["source_sha256"]
    assert sha256_path(compiled_path)==row["pair_compiled_sha256"]==plant["pair_compiled_sha256"]
    assert source["schema"]=="MIXED_AFFINE_OR3_EXPANDER_RELATION_V1"
    assert source["target"]=="CONNECTED_MIXED_AFFINE_OR3_EXPANDER_INTERLEAVE"
    n=source["n_vertices"]
    assert n==row["n"] and n in SERIES
    assert source["graph_degree"]==DEGREE
    assert source["domain_contract"]["totality_assumed"] is False
    assert source["domain_contract"]["exact_domain_required"] is True
    assert source["witness_contract"]["explicit_output_DAG_nodes_present"] is False
    assert source["witness_contract"]["precomputed_Skolem_functions_present"] is False
    prov=source["source_provenance"]
    assert prov["prereg_commit"]==PREREG_COMMIT
    assert prov["qualification_addendum_commit"]==QUALIFICATION_ADDENDUM_COMMIT
    assert prov["graph_selection_uses_spectral_metric"] is False
    assert prov["planted_assignment_committed"] is False
    assert prov["constructor_implemented_at_source_freeze"] is False

    vertices=source["vertices"]
    assert len(vertices)==n
    by_index={v["vertex_index"]:v for v in vertices}
    assert set(by_index)==set(range(n))
    vertex_ids={v["vertex_id"]:v["vertex_index"] for v in vertices}
    x_owner={v["x_var"]:v["vertex_index"] for v in vertices}
    s_owner={v["s_var"]:v["vertex_index"] for v in vertices}
    assert not (set(x_owner)&set(s_owner))

    edges=source["edges"]
    assert len(edges)==3*n//2==source["n_edges"]
    adj=[set() for _ in range(n)]
    incident=[[] for _ in range(n)]
    seen_edges=set(); degree=[0]*n; boundary=set()
    A=np.zeros((n,n),dtype=float)
    for e in edges:
        a=e["u_index"]; b=e["v_index"]
        assert a in by_index and b in by_index and a!=b
        assert e["u"]==by_index[a]["vertex_id"] and e["v"]==by_index[b]["vertex_id"]
        key=tuple(sorted((a,b)))
        assert key not in seen_edges; seen_edges.add(key)
        y=e["boundary_var"]
        assert y not in boundary; boundary.add(y)
        degree[a]+=1; degree[b]+=1
        adj[a].add(b); adj[b].add(a)
        incident[a].append(y); incident[b].append(y)
        A[a,b]=A[b,a]=1.0
    assert all(d==DEGREE for d in degree)
    reached={0}; q=deque([0])
    while q:
        u=q.popleft()
        for v in adj[u]:
            if v not in reached:
                reached.add(v); q.append(v)
    assert len(reached)==n
    assert set(source["boundary_vars"])==boundary

    vals=np.sort(np.linalg.eigvalsh(A))[::-1]
    ratio=float(vals[1]/DEGREE)
    assert ratio<=SPECTRAL_THRESHOLD
    assert abs(ratio-float(source["qualification_record"]["lambda2_over_degree"]))<1e-10
    assert source["qualification_record"]["finite_spectral_stress_gate_pass"] is True

    af=source["affine_factors"]
    assert len(af)==n
    af_by_v={f["vertex_index"]:f for f in af}
    assert set(af_by_v)==set(range(n))
    assignment=plant["assignments"]
    for v in range(n):
        vr=by_index[v]; f=af_by_v[v]
        assert f["vertex_id"]==vr["vertex_id"]
        assert f["rhs"]==vr["affine_constant"]
        assert set(f["vars"])=={vr["x_var"],vr["s_var"],*incident[v]}
        parity=0
        for z in f["vars"]:
            parity ^= int(assignment[z])
        assert parity==int(f["rhs"])

    clauses=source["or3_clauses"]
    assert len(clauses)==2*n
    coverage=[0]*n
    all_plant_satisfied=True
    exact_one_true=0
    for c in clauses:
        lits=c["literals"]
        assert len(lits)==3
        assert len({l["var"] for l in lits})==3
        verts=[l["vertex_index"] for l in lits]
        assert len(set(verts))==3
        for a,b in itertools.combinations(verts,2):
            assert b not in adj[a]
        roles={l["role"] for l in lits}
        assert "x" in roles and "s" in roles
        for l in lits:
            v=l["vertex_index"]
            assert l["var"]==(by_index[v]["x_var"] if l["role"]=="x" else by_index[v]["s_var"])
            coverage[v]+=1
        truth=[eval_literal(l,assignment) for l in lits]
        all_plant_satisfied &= any(truth)
        exact_one_true += int(sum(bool(x) for x in truth)==1)
    assert all_plant_satisfied
    assert min(coverage)>=2
    assert source["qualification_record"]["min_or3_vertex_coverage"]==min(coverage)
    assert source["qualification_record"]["max_or3_vertex_coverage"]==max(coverage)

    recomp=compile_pair_positive_or3(source)
    assert recomp==compiled
    assert compiled["compiler_provenance"]["truth_table_enumeration"] is False
    for c in compiled["positive_or3_clauses"]:
        assert len(c["selectors"])==3

    return {
      "n":n,
      "n_edges":len(edges),
      "n_affine_factors":len(af),
      "n_or3_clauses":len(clauses),
      "lambda2_over_degree":ratio,
      "min_or3_vertex_coverage":min(coverage),
      "max_or3_vertex_coverage":max(coverage),
      "plant_satisfies_all_affine":True,
      "plant_satisfies_all_or3":True,
      "or3_clauses_exactly_one_true_at_plant":exact_one_true,
      "pair_compilation_exact_match":True,
      "source_sha256":sha256_path(source_path),
      "pair_compiled_sha256":sha256_path(compiled_path)
    }


def main(srcdir_s:str,plantdir_s:str,out_s:str,freeze_sha:str):
    src=Path(srcdir_s); plantdir=Path(plantdir_s)
    manifest=json.loads((src/"source_manifest.json").read_text())
    assert manifest["prereg_commit"]==PREREG_COMMIT
    assert manifest["qualification_addendum_commit"]==QUALIFICATION_ADDENDUM_COMMIT
    sf=manifest["selection_firewall"]
    assert sf["raw_seed_committed"] is False
    assert sf["planted_assignment_committed"] is False
    assert sf["resampling_after_constructor_observation"] is False
    assert sf["spectral_metric_used_for_graph_selection"] is False
    assert sf["constructor_not_implemented_at_source_freeze"] is True
    assert [r["n"] for r in manifest["series"]]==list(SERIES)

    rows=[]
    for row in manifest["series"]:
        rows.append(check_one(
            src/row["source_file"],
            src/row["pair_compiled_file"],
            plantdir/f"plant_n{row['n']}.json",
            row
        ))

    result={
      "artifact_id":"JANUS-U-PAIR-1J-CONNECTED-MIXED-AFFINE-OR3-EXPANDER-INTERLEAVE-INDEPENDENT-SOURCE-CHECK-2026-09-18-v1.0",
      "prereg_commit":PREREG_COMMIT,
      "qualification_addendum_commit":QUALIFICATION_ADDENDUM_COMMIT,
      "source_freeze_commit":freeze_sha,
      "seed_commitment":manifest["seed_commitment"],
      "checks":{
        "all_source_hashes_match":True,
        "all_pair_compiled_hashes_match":True,
        "all_simple_connected_3_regular":True,
        "all_finite_spectral_stress_gate_pass":True,
        "all_affine_factors_match_backbone":True,
        "all_or3_cross_distinct_nonadjacent_neighborhoods":True,
        "all_or3_mixed_x_s_roles":True,
        "all_or3_coverage_gate_pass":True,
        "ephemeral_plant_proves_nonempty_relation":True,
        "canonical_pair_positive_or3_compilation_exact":True,
        "no_explicit_output_DAG_nodes":True,
        "no_precomputed_Skolem_functions":True,
        "constructor_not_implemented_at_source_freeze":True
      },
      "rows":rows,
      "verdict":"PASS_SOURCE_FREEZE_INDEPENDENT_CHECK",
      "scientific_firewall":{
        "plant_is_not_a_Skolem_function":True,
        "domain_totality_not_established":True,
        "hostile_synthesis_not_run":True,
        "finite_spectral_gate_is_not_asymptotic_expander_theorem":True,
        "GENERAL_SAT_IN_P":"NOT_PROVED",
        "P_EQ_NP":"NOT_PROVED",
        "P_VS_NP":"OPEN"
      }
    }
    Path(out_s).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "verdict":result["verdict"],
      "rows":[{"n":r["n"],"lambda2_over_degree":r["lambda2_over_degree"]} for r in rows]
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=5:
        raise SystemExit("usage: independent_source_check.py SRC_DIR EPHEMERAL_PLANT_DIR OUT_JSON SOURCE_FREEZE_SHA")
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
