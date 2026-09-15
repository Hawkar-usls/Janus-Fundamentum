from __future__ import annotations

import json
from collections import defaultdict, deque

from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_3plus_forensic import residual_3plus_forensic as prof

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-3PLUS-STRUCTURE-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_3PLUS_STRUCTURE_FORENSIC"


def _scope(f, core):
    C=set(core); return [int(v) for v in f["scope"] if int(v) not in C]


def _data():
    raw=v36.residual_component_gt2_control(); pred=cc_v11.explain(raw); ready=cc_v11.first_failed_original_bucket_v11(raw)
    if pred.get("status")!="OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2" or ready.get("status")!="READY": return {"status":"HALT"}
    core=[int(v) for v in ready["common_core"]]; common=sorted(cc_v1.support_and_filter(ready["canonical"],ready["bucket"],core)["common"])
    if len(common)!=1:return {"status":"HALT_COMMON"}
    state=tuple(int(x) for x in common[0]); factors=[]
    for f in ready["bucket"]:
        pos={int(v):i for i,v in enumerate(f["scope"])}
        cpos=[pos[v] for v in core]
        rows=[tuple(int(x) for x in r) for r in f["rows"] if tuple(int(r[p]) for p in cpos)==state]
        factors.append({**f,"rows":rows})
    scopes=[set(_scope(f,core)) for f in factors]; adj={i:set() for i in range(len(factors))}
    for i in range(len(factors)):
        for j in range(i+1,len(factors)):
            if scopes[i]&scopes[j]: adj[i].add(j); adj[j].add(i)
    seen=set(); comps=[]
    for s in range(len(factors)):
        if s in seen: continue
        q=[s]; seen.add(s); c=[]
        while q:
            u=q.pop(0); c.append(u)
            for w in sorted(adj[u]):
                if w not in seen: seen.add(w); q.append(w)
        comps.append(sorted(c))
    target=next(c for c in comps if len(c)>=3); fs=[factors[i] for i in target]
    return {"status":"READY","pred":pred,"ready":ready,"core":core,"state":state,"comps":comps,"factors":fs}


def _edges(fs,core):
    scopes=[set(_scope(f,core)) for f in fs]; out=[]
    for i in range(len(fs)):
        for j in range(i+1,len(fs)):
            ov=sorted(scopes[i]&scopes[j])
            if ov: out.append({"i":i,"j":j,"left":fs[i]["id"],"right":fs[j]["id"],"overlap":ov,"overlap_cardinality":len(ov)})
    return out


def _prim_tree(n,edges):
    if n<=1:return []
    used={0}; out=[]
    while len(used)<n:
        candidates=[e for e in edges if (e["i"] in used) ^ (e["j"] in used)]
        if not candidates: break
        e=min(candidates,key=lambda x:(-x["overlap_cardinality"],x["left"],x["right"],x["i"],x["j"]))
        out.append(e); used.add(e["i"]); used.add(e["j"])
    return out


def _running(fs,core,tree):
    scopes=[set(_scope(f,core)) for f in fs]; adj={i:set() for i in range(len(fs))}
    for e in tree: adj[e["i"]].add(e["j"]); adj[e["j"]].add(e["i"])
    failures=[]
    for v in sorted(set().union(*scopes) if scopes else set()):
        nodes={i for i,s in enumerate(scopes) if v in s}
        if len(nodes)<=1:continue
        seen={min(nodes)}; q=deque(seen)
        while q:
            u=q.popleft()
            for w in adj[u]&nodes:
                if w not in seen:seen.add(w);q.append(w)
        if seen!=nodes:failures.append(v)
    return {"ok":not failures,"failure_variables":failures}


def _relation_articulations(n,edges):
    base=[(e["i"],e["j"]) for e in edges]
    def cc(rem=None):
        nodes=[i for i in range(n) if i!=rem]
        if not nodes:return 0
        adj={i:set() for i in nodes}
        for a,b in base:
            if a==rem or b==rem:continue
            adj[a].add(b);adj[b].add(a)
        seen=set(); c=0
        for s in nodes:
            if s in seen:continue
            c+=1;q=[s];seen.add(s)
            while q:
                u=q.pop()
                for w in adj[u]:
                    if w not in seen:seen.add(w);q.append(w)
        return c
    b=cc();return [i for i in range(n) if cc(i)>b]


def _variable_articulations(fs,core):
    scopes=[set(_scope(f,core)) for f in fs]; vars_=sorted(set().union(*scopes))
    def cc(rem=None):
        adj={i:set() for i in range(len(fs))}
        for i in range(len(fs)):
            for j in range(i+1,len(fs)):
                a=set(scopes[i]);b=set(scopes[j]);
                if rem is not None:a.discard(rem);b.discard(rem)
                if a&b:adj[i].add(j);adj[j].add(i)
        seen=set();c=0
        for s in range(len(fs)):
            if s in seen:continue
            c+=1;q=[s];seen.add(s)
            while q:
                u=q.pop()
                for w in adj[u]:
                    if w not in seen:seen.add(w);q.append(w)
        return c
    b=cc();return [v for v in vars_ if cc(v)>b]


def _hash_pair_metrics(fs,edges):
    out=[]
    for e in edges:
        L,R=fs[e["i"]],fs[e["j"]]; ov=e["overlap"]
        lp={int(v):i for i,v in enumerate(L["scope"])};rp={int(v):i for i,v in enumerate(R["scope"])}
        lc=defaultdict(int);rc=defaultdict(int)
        for row in L["rows"]:lc[tuple(row[lp[v]] for v in ov)]+=1
        for row in R["rows"]:rc[tuple(row[rp[v]] for v in ov)]+=1
        common=set(lc)&set(rc);pairs=sum(lc[k]*rc[k] for k in common)
        left_support=sum(lc[k] for k in common);right_support=sum(rc[k] for k in common)
        out.append({**e,"left_rows":len(L["rows"]),"right_rows":len(R["rows"]),"row_pair_comparisons":len(L["rows"])*len(R["rows"]),"compatible_pairs":pairs,"left_rows_with_support":left_support,"right_rows_with_support":right_support})
    return out


def _semijoin(fs,edges):
    active=[set(range(len(f["rows"]))) for f in fs]; progression=[];changed=True;sweep=0
    while changed:
        changed=False;sweep+=1
        for e in sorted(edges,key=lambda x:(x["i"],x["j"])):
            i,j=e["i"],e["j"];ov=e["overlap"];L,R=fs[i],fs[j]
            lp={int(v):k for k,v in enumerate(L["scope"])};rp={int(v):k for k,v in enumerate(R["scope"])}
            sigL={li:tuple(L["rows"][li][lp[v]] for v in ov) for li in active[i]};sigR={ri:tuple(R["rows"][ri][rp[v]] for v in ov) for ri in active[j]}
            common=set(sigL.values())&set(sigR.values());ni={li for li,s in sigL.items() if s in common};nj={ri for ri,s in sigR.items() if s in common}
            if ni!=active[i] or nj!=active[j]:changed=True
            active[i],active[j]=ni,nj
        progression.append({"sweep":sweep,"active_row_counts":[len(x) for x in active]})
        if sweep>len(fs)+len(edges)+2:break
    return {"progression":progression,"fixed_point_row_counts":[len(x) for x in active]}


def run():
    p=prof.run();d=_data()
    if d.get("status")!="READY":return {"verdict":"FAIL_DIAGNOSTIC_PREP"}
    fs=d["factors"];core=d["core"];edges=_edges(fs,core);tree=_prim_tree(len(fs),edges);running=_running(fs,core,tree);pairs=_hash_pair_metrics(fs,edges);semi=_semijoin(fs,edges)
    checks={
        "source_guard":p.get("source_guard",{}).get("ok") is True,
        "parent_open_gt2":p.get("parent_terminal")=="OPEN_RESIDUAL_COMPONENT_GT2",
        "component_sizes_match":p.get("all_residual_component_sizes")==[len(c) for c in d["comps"]],
        "factor_ids_match":p.get("target_factor_ids")==[f["id"] for f in fs],
        "edges_match":p.get("edges")==edges,
        "relation_articulations_match":p.get("relation_articulation_vertices")==_relation_articulations(len(fs),edges),
        "variable_articulations_match":p.get("variable_articulation_points")==_variable_articulations(fs,core),
        "running_intersection_agrees":p.get("running_intersection",{}).get("ok")==running["ok"],
        "pairwise_metrics_match":p.get("pairwise_compatibility")==pairs,
        "semijoin_fixed_point_match":p.get("semijoin_closure",{}).get("fixed_point_row_counts")==semi["fixed_point_row_counts"],
        "zero_join_chain":p.get("resource_receipt",{}).get("three_plus_join_chains_materialized")==0,
        "zero_global_cartesian":p.get("resource_receipt",{}).get("global_residual_cartesian_products_materialized")==0,
        "firewall_pvsnp":p.get("scientific_firewall",{}).get("P_VS_NP")=="OPEN",
    }
    return {"artifact_id":ARTIFACT_ID,"authority":"INDEPENDENT_DIAGNOSTIC_CHECKER","checks":checks,"profiler_status":p.get("status"),"target_factor_ids":[f["id"] for f in fs],"edges":edges,"prim_tree":tree,"running_intersection":running,"relation_articulation_vertices":_relation_articulations(len(fs),edges),"variable_articulation_points":_variable_articulations(fs,core),"pairwise_compatibility":pairs,"semijoin_closure":semi,"verdict":VERDICT if all(checks.values()) else "FAIL_DIAGNOSTIC_RESIDUAL_3PLUS_STRUCTURE_FORENSIC","scientific_firewall":p.get("scientific_firewall")}


def main():print(json.dumps(run(),sort_keys=True))
if __name__=="__main__":main()
