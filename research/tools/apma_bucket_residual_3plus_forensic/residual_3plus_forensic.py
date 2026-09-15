from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-3PLUS-STRUCTURE-FORENSIC-2026-09-15-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_3PLUS_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "386c3cdb9fdcc89892e553a15c01eabffabba689"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.6.json")
PARENT_STATE_BLOB = "a0ac20d6d0e023d776a930865a990e7b9eec52f7"
PARENT_CANDIDATE = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
PARENT_CANDIDATE_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    d = path.read_bytes()
    return hashlib.sha1(f"blob {len(d)}\0".encode("ascii") + d).hexdigest()


def source_guard() -> dict:
    r = root()
    p = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": p.get("status") == "FROZEN_BEFORE_DIAGNOSTIC_IMPLEMENTATION",
        "parent_state_blob": blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_candidate_blob": blob(r / PARENT_CANDIDATE) == PARENT_CANDIDATE_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def _conditioned_data() -> dict:
    raw = v36.residual_component_gt2_control()
    parent = v36.prepare(raw)
    predecessor = cc_v11.explain(raw)
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    if predecessor.get("status") != "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2" or ready.get("status") != "READY":
        return {"status": "HALT_PREDECESSOR_NOT_READY", "parent": parent.get("status"), "predecessor": predecessor.get("status"), "ready": ready.get("status")}
    core = [int(v) for v in ready["common_core"]]
    sf = cc_v1.support_and_filter(ready["canonical"], ready["bucket"], core)
    common = sorted(sf["common"])
    if len(common) != 1:
        return {"status": "HALT_COMMON_CORE_NOT_UNIQUE", "common_support_size": len(common)}
    state = tuple(int(x) for x in common[0])
    conditioned = []
    for f in ready["bucket"]:
        rows = [tuple(int(x) for x in row) for row in f["rows"] if cc_v1._projection(f, core, row) == state]
        conditioned.append({**f, "rows": rows})
    components = v36.residual_components(conditioned, core)
    target = next((c for c in components if len(c) >= 3), None)
    if target is None:
        return {"status": "HALT_NO_RESIDUAL_3PLUS_COMPONENT", "components": components}
    factors = [conditioned[i] for i in target]
    return {"status": "READY", "raw": raw, "parent": parent, "predecessor": predecessor, "ready": ready, "core": core, "state": state, "all_components": components, "target_indices": list(target), "factors": factors}


def _residual_scope(f: dict, core: list[int]) -> list[int]:
    C = set(core)
    return [int(v) for v in f["scope"] if int(v) not in C]


def _edges(factors: list[dict], core: list[int]) -> list[dict]:
    scopes = [set(_residual_scope(f, core)) for f in factors]
    out = []
    for i in range(len(factors)):
        for j in range(i + 1, len(factors)):
            ov = sorted(scopes[i] & scopes[j])
            if ov:
                out.append({"i": i, "j": j, "left": factors[i]["id"], "right": factors[j]["id"], "overlap": ov, "overlap_cardinality": len(ov)})
    return out


def _component_count(n: int, edges: list[tuple[int,int]], removed_vertex: int | None = None) -> int:
    nodes = [i for i in range(n) if i != removed_vertex]
    if not nodes:
        return 0
    adj = {i: [] for i in nodes}
    for a,b in edges:
        if a == removed_vertex or b == removed_vertex:
            continue
        if a in adj and b in adj:
            adj[a].append(b); adj[b].append(a)
    seen = set(); count = 0
    for s in nodes:
        if s in seen: continue
        count += 1; stack=[s]; seen.add(s)
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if v not in seen: seen.add(v); stack.append(v)
    return count


def _articulation_relations(n: int, edges: list[dict]) -> list[int]:
    e=[(x["i"],x["j"]) for x in edges]
    base=_component_count(n,e)
    return [i for i in range(n) if _component_count(n,e,i) > base]


def _articulation_variables(factors: list[dict], core: list[int]) -> list[int]:
    scopes=[set(_residual_scope(f,core)) for f in factors]
    vars_=sorted(set().union(*scopes)) if scopes else []
    def comps(without: int | None) -> int:
        edges=[]
        for i in range(len(scopes)):
            for j in range(i+1,len(scopes)):
                a=set(scopes[i]); b=set(scopes[j])
                if without is not None: a.discard(without); b.discard(without)
                if a & b: edges.append((i,j))
        return _component_count(len(scopes),edges)
    base=comps(None)
    return [v for v in vars_ if comps(v)>base]


def _kruskal_tree(n: int, edges: list[dict]) -> list[dict]:
    parent=list(range(n))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    out=[]
    for e in sorted(edges,key=lambda x:(-x["overlap_cardinality"],x["left"],x["right"],x["i"],x["j"])):
        a,b=find(e["i"]),find(e["j"])
        if a==b: continue
        if a>b: a,b=b,a
        parent[b]=a; out.append(e)
        if len(out)==n-1: break
    return out


def _running_intersection(factors: list[dict], core: list[int], tree: list[dict]) -> dict:
    scopes=[set(_residual_scope(f,core)) for f in factors]
    adj={i:[] for i in range(len(factors))}
    for e in tree: adj[e["i"]].append(e["j"]); adj[e["j"]].append(e["i"])
    failures=[]
    for v in sorted(set().union(*scopes) if scopes else set()):
        nodes=[i for i,s in enumerate(scopes) if v in s]
        if len(nodes)<=1: continue
        allowed=set(nodes); seen={nodes[0]}; stack=[nodes[0]]
        while stack:
            u=stack.pop()
            for w in adj[u]:
                if w in allowed and w not in seen: seen.add(w); stack.append(w)
        if seen!=allowed: failures.append({"variable":v,"nodes":nodes,"connected_nodes":sorted(seen)})
    return {"ok": not failures, "failures": failures}


def _row_map(f: dict, row: tuple[int,...]) -> dict[int,int]:
    return {int(v):int(bit) for v,bit in zip(f["scope"],row)}


def _pair_metrics(factors: list[dict], edges: list[dict]) -> list[dict]:
    out=[]
    for e in edges:
        L,R=factors[e["i"]],factors[e["j"]]; ov=e["overlap"]
        compatible=0; left_ok=set(); right_ok=set(); comparisons=0
        for li,lrow in enumerate(L["rows"]):
            lm=_row_map(L,lrow)
            for ri,rrow in enumerate(R["rows"]):
                comparisons+=1; rm=_row_map(R,rrow)
                if all(lm[v]==rm[v] for v in ov):
                    compatible+=1; left_ok.add(li); right_ok.add(ri)
        out.append({**e,"left_rows":len(L["rows"]),"right_rows":len(R["rows"]),"row_pair_comparisons":comparisons,"compatible_pairs":compatible,"left_rows_with_support":len(left_ok),"right_rows_with_support":len(right_ok)})
    return out


def _semijoin_closure(factors: list[dict], edges: list[dict]) -> dict:
    active=[set(range(len(f["rows"]))) for f in factors]
    progression=[]; changed=True; sweep=0
    while changed:
        changed=False; sweep+=1
        for e in sorted(edges,key=lambda x:(x["i"],x["j"])):
            i,j=e["i"],e["j"]; ov=e["overlap"]
            keep_i=set(); keep_j=set()
            for li in active[i]:
                lm=_row_map(factors[i],factors[i]["rows"][li])
                for rj in active[j]:
                    rm=_row_map(factors[j],factors[j]["rows"][rj])
                    if all(lm[v]==rm[v] for v in ov): keep_i.add(li); keep_j.add(rj)
            ni=active[i]&keep_i; nj=active[j]&keep_j
            if ni!=active[i] or nj!=active[j]: changed=True
            active[i],active[j]=ni,nj
        progression.append({"sweep":sweep,"active_row_counts":[len(x) for x in active]})
        if sweep>len(factors)+len(edges)+2: break
    return {"progression":progression,"fixed_point_row_counts":[len(x) for x in active],"global_join_materialized":False}


def run() -> dict:
    g=source_guard()
    if not g["ok"]: return {"artifact_id":ARTIFACT_ID,"status":"HALT_SOURCE_GUARD","source_guard":g}
    d=_conditioned_data()
    if d.get("status")!="READY": return {"artifact_id":ARTIFACT_ID,**d,"source_guard":g}
    factors=d["factors"]; core=d["core"]; edges=_edges(factors,core); tree=_kruskal_tree(len(factors),edges)
    ri=_running_intersection(factors,core,tree)
    return {
        "artifact_id":ARTIFACT_ID,"authority":AUTHORITY,"status":"PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_3PLUS_STRUCTURE_FORENSIC","source_guard":g,
        "parent_terminal":d["parent"].get("status"),"predecessor_terminal":d["predecessor"].get("status"),"common_core_size":len(core),"unique_common_state":list(d["state"]),
        "all_residual_component_sizes":[len(c) for c in d["all_components"]],"target_component_indices":d["target_indices"],"target_factor_ids":[f["id"] for f in factors],
        "residual_scopes":[_residual_scope(f,core) for f in factors],"edge_count":len(edges),"edges":edges,
        "relation_articulation_vertices":_articulation_relations(len(factors),edges),"variable_articulation_points":_articulation_variables(factors,core),
        "kruskal_join_tree":tree,"running_intersection":ri,"pairwise_compatibility":_pair_metrics(factors,edges),"semijoin_closure":_semijoin_closure(factors,edges),
        "resource_receipt":{"three_plus_join_chains_materialized":0,"global_residual_cartesian_products_materialized":0,"alternative_order_search":0,"solver_calls":0},
        "scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","GENERAL_PARTIAL_OVERLAP_FACTORIZATION":"NOT_PROVED","GLOBAL_APMA_FRONTIER_ADVANCE":"NONE"}
    }


def main()->None: print(json.dumps(run(),sort_keys=True))
if __name__=="__main__": main()
