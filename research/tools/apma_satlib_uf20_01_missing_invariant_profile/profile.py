from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RAW = Path("research/source_data/SATLIB_UF20_01_RAW_2026-09-16.json")
SOURCE = Path("research/source_data/SATLIB_UF20_01_2026-09-16.cnf")
FINAL = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_NEW_EVIDENCE_OBSTRUCTION_FINAL_SEAL_SATLIB_UF20_01_2026-09-16.json")
PREREG = Path("research/TRUMP_SATLIB_UF20_01_MISSING_INVARIANT_PROFILE_GATE_PREREGISTRATION_2026-09-16.json")
EXPECTED = {RAW:"8b69a8f533ffaec44f196eea8791b0678f3f579c", SOURCE:"8330041b292e0501f8d74c1b1d32ca96c4498864", FINAL:"40dfc73b95b6f7af56d933276dbc3144f61bb841", PREREG:"ea90275e9c28236e89871b9ad48e17079450f701"}
RAW_SHA = "a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"


def blob(path: Path) -> str:
    b=(ROOT/path).read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def guard():
    c={str(p):blob(p)==s for p,s in EXPECTED.items()}; return {"ok":all(c.values()),"checks":c}

def parse_source():
    out=[]
    for line in (ROOT/SOURCE).read_text().splitlines():
        s=line.strip()
        if not s or s.startswith("c") or s.startswith("p "): continue
        v=[int(x) for x in s.split()]
        if v[-1]!=0: raise ValueError("BAD_DIMACS")
        out.append(tuple(v[:-1]))
    if len(out)!=91: raise ValueError("BAD_CLAUSE_COUNT")
    return out

def conn(nodes, adj):
    nodes=set(nodes)
    if len(nodes)<=1:return True
    st=[next(iter(nodes))]; seen={st[0]}
    while st:
        u=st.pop()
        for v in adj[u]&nodes:
            if v not in seen: seen.add(v); st.append(v)
    return seen==nodes

def low_cuts(nodes, adj, maxk=4):
    nodes=tuple(sorted(nodes)); counts={}; examples={}; first=None
    for k in range(1,maxk+1):
        n=0; ex=[]
        for cut in itertools.combinations(nodes,k):
            rem=set(nodes)-set(cut)
            if len(rem)>1 and not conn(rem,adj):
                n+=1
                if len(ex)<12: ex.append(list(cut))
        counts[str(k)]=n; examples[str(k)]=ex
        if n and first is None:first=k
    return {"cut_counts":counts,"examples":examples,"minimum_cut_if_le4":first,"connectivity_lower_bound":5 if first is None else first}
def tarjan_art_bridges(nodes, adj):
    t=0; disc={}; low={}; parent={}; arts=set(); bridges=[]
    def dfs(u):
        nonlocal t
        t+=1; disc[u]=low[u]=t; children=0
        for v in sorted(adj[u]):
            if v not in disc:
                parent[v]=u; children+=1; dfs(v); low[u]=min(low[u],low[v])
                if u not in parent and children>1: arts.add(u)
                if u in parent and low[v]>=disc[u]: arts.add(u)
                if low[v]>disc[u]: bridges.append((u,v))
            elif parent.get(u)!=v: low[u]=min(low[u],disc[v])
    for u in sorted(nodes):
        if u not in disc: dfs(u)
    return sorted(arts), sorted([list(sorted(e)) for e in bridges])
def relkey(c): return tuple(sorted("".join(str(int(b)) for b in r) for r in c["allowed"]))
def fp(rows):
    rel={tuple(int(x) for x in w) for w in rows}; a=len(next(iter(rel)))
    AND=lambda x,y:tuple(i&j for i,j in zip(x,y)); OR=lambda x,y:tuple(i|j for i,j in zip(x,y))
    return {"ZERO_VALID":(0,)*a in rel,"ONE_VALID":(1,)*a in rel,
      "HORN":all(AND(x,y) in rel for x in rel for y in rel),"DUAL_HORN":all(OR(x,y) in rel for x in rel for y in rel)}
def incidence_disconnected_after_var_cut(raw, cut):
    cut=set(cut); vars=[v for v in raw["variables"] if v not in cut]
    constraints=[]; adj=defaultdict(set); nodes=set(("v",v) for v in vars)
    for c in raw["constraints"]:
        s=[v for v in c["scope"] if v not in cut]
        if not s: continue
        cn=("c",c["id"]); nodes.add(cn); constraints.append(cn)
        for v in s: vn=("v",v); adj[vn].add(cn); adj[cn].add(vn)
    if len(nodes)<=1:return False
    st=[next(iter(nodes))]; seen={st[0]}
    while st:
        u=st.pop()
        for v in adj[u]:
            if v not in seen:seen.add(v);st.append(v)
    return seen!=nodes
def incidence_var_cuts(raw,maxk=4):
    vars=tuple(raw["variables"]); counts={}; examples={}; first=None
    for k in range(1,maxk+1):
        n=0; ex=[]
        for cut in itertools.combinations(vars,k):
            if incidence_disconnected_after_var_cut(raw,cut):
                n+=1
                if len(ex)<12:ex.append(list(cut))
        counts[str(k)]=n; examples[str(k)]=ex
        if n and first is None:first=k
    return {"cut_counts":counts,"examples":examples,"minimum_variable_only_cut_if_le4":first,"connectivity_lower_bound":5 if first is None else first}
def main_profile():
    g=guard()
    if not g["ok"]: return {"verdict":"HALT_SOURCE_GUARD","source_guard":g}
    raw=json.loads((ROOT/RAW).read_text()); clauses=parse_source(); vars=raw["variables"]
    # primal
    adj={v:set() for v in vars}
    for c in raw["constraints"]:
        for u,v in itertools.combinations(c["scope"],2):adj[u].add(v);adj[v].add(u)
    edges=sum(len(x) for x in adj.values())//2
    arts,bridges=tarjan_art_bridges(vars,adj)
    cuts=low_cuts(vars,adj)
    # incidence articulation/bridges
    iadj=defaultdict(set); inodes=set()
    for v in vars:inodes.add(f"v:{v}")
    for c in raw["constraints"]:
        cn=f"c:{c['id']}";inodes.add(cn)
        for v in c["scope"]:vn=f"v:{v}";iadj[vn].add(cn);iadj[cn].add(vn)
    iarts,ibridges=tarjan_art_bridges(inodes,iadj)
    ivcuts=incidence_var_cuts(raw)
    # overlap geometry
    overlap=Counter(); o1={c["id"]:set() for c in raw["constraints"]}; o2={c["id"]:set() for c in raw["constraints"]}
    for a,b in itertools.combinations(raw["constraints"],2):
        k=len(set(a["scope"])&set(b["scope"])); overlap[k]+=1
        if k>=1:o1[a["id"]].add(b["id"]);o1[b["id"]].add(a["id"])
        if k>=2:o2[a["id"]].add(b["id"]);o2[b["id"]].add(a["id"])
    clause_ids=list(o1)
    # relations / local mixing
    keys=sorted({relkey(c) for c in raw["constraints"]}); idx={k:i for i,k in enumerate(keys)}
    rfp=[fp(k) for k in keys]
    rel_counts=[0]*len(keys); var_rel={v:[0]*len(keys) for v in vars}; horn={v:0 for v in vars}; dual={v:0 for v in vars}
    for c in raw["constraints"]:
        i=idx[relkey(c)];rel_counts[i]+=1
        for v in c["scope"]:
            var_rel[v][i]+=1; horn[v]+=int(rfp[i]["HORN"]); dual[v]+=int(rfp[i]["DUAL_HORN"])
    pos=Counter();neg=Counter()
    for cl in clauses:
        for lit in cl:(pos if lit>0 else neg)[abs(lit)]+=1
    sig={}; groups=defaultdict(list)
    deg={v:len(adj[v]) for v in vars}
    for v in vars:
        s=(deg[v],pos[v],neg[v],tuple(var_rel[v]),tuple(sorted(deg[n] for n in adj[v])))
        h=hashlib.sha256(json.dumps(s,separators=(",",":")).encode()).hexdigest()[:16];sig[v]=h;groups[h].append(v)
    # degeneracy
    rem=set(vars); work={v:set(adj[v]) for v in vars}; degen=0
    while rem:
        v=min(rem,key=lambda x:(len(work[x]&rem),x));degen=max(degen,len(work[v]&rem));rem.remove(v)
    triangles=sum(1 for a,b,c in itertools.combinations(vars,3) if b in adj[a] and c in adj[a] and c in adj[b])
    return {
      "artifact_id":"JANUS-TRUMP-SATLIB-UF20-01-MISSING-INVARIANT-PROFILE-2026-09-16-v1.0",
      "authority":"DIAGNOSTIC_ONLY__SOURCE_BOUND_OBSTRUCTION_PROFILE","verdict":"PASS_DIAGNOSTIC_PROFILE_FROZEN_OBSTRUCTION",
      "source_guard":g,"raw_sha256":RAW_SHA,
      "P1_primal":{"vertices":20,"edges":edges,"density":edges/190,"degree_min":min(deg.values()),"degree_max":max(deg.values()),"articulation_points":arts,"bridges":bridges,**cuts},
      "P2_incidence":{"vertices":len(inodes),"edges":273,"articulation_count":len(iarts),"articulation_points":iarts,"bridge_count":len(ibridges),"bridges":ibridges,"variable_only_cuts":ivcuts},
      "P3_overlap":{"pair_intersection_counts":{str(k):overlap[k] for k in sorted(overlap)},"graph_ge1_connected":conn(clause_ids,o1),"graph_ge2_connected":conn(clause_ids,o2),"graph_ge1_edges":sum(len(x) for x in o1.values())//2,"graph_ge2_edges":sum(len(x) for x in o2.values())//2},
      "P4_local_mixing":{"relation_surface_count":len(keys),"relation_constraint_counts":rel_counts,"relation_fingerprints":rfp,"per_variable_relation_counts":{str(v):var_rel[v] for v in vars},"per_variable_horn_incident":horn,"per_variable_dual_horn_incident":dual},
      "P5_variable_signature":{"distinct_signature_count":len(groups),"signature_groups":dict(sorted(groups.items())),"all_singleton_signatures":all(len(x)==1 for x in groups.values()),"per_variable_signature":{str(v):sig[v] for v in vars},"positive_occurrences":dict(pos),"negative_occurrences":dict(neg)},
      "P6_core":{"degeneracy":degen,"triangle_count":triangles,"low_order_primal_cut_counts":cuts["cut_counts"]},
      "scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","CONNECTED_MIXED_CORE_SOLVED":"NO","ARBITRARY_UNSEEN_INVARIANT_DISCOVERY":"NOT_PROVED","NEW_SOLVER_MECHANISMS":0,"NEW_CARRIER_MECHANISMS":0}
    }

if __name__=="__main__":print(json.dumps(main_profile(),sort_keys=True))
