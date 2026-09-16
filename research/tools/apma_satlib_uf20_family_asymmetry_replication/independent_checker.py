from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}


def blob(path: Path) -> str:
    b = path.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode("ascii") + b).hexdigest()


def parse(path: Path) -> list[tuple[int, ...]]:
    out=[]; declared=None
    for line in path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("c") or s in {"%","0"}: continue
        if s.startswith("p "):
            p=s.split(); declared=(int(p[2]),int(p[3])); continue
        xs=[int(x) for x in s.split()]
        if xs[-1] != 0: raise ValueError("BAD_DIMACS")
        out.append(tuple(xs[:-1]))
    if declared != (20,91) or len(out) != 91: raise ValueError("BAD_COUNTS")
    return out


def raw(source_key: str, clauses: list[tuple[int,...]]) -> dict:
    cons=[]
    for i,cl in enumerate(clauses,1):
        scope=sorted(abs(x) for x in cl); allowed=[]
        for bits in itertools.product((0,1), repeat=3):
            a=dict(zip(scope,bits))
            if any(bool(a[abs(l)]) if l>0 else not bool(a[abs(l)]) for l in cl): allowed.append(list(bits))
        cons.append({"id":f"satlib_{source_key.lower()}_c{i:03d}","scope":scope,"allowed":sorted(allowed)})
    cons.sort(key=lambda r:(tuple(r["scope"]),tuple("".join(map(str,t)) for t in r["allowed"]),r["id"]))
    return {"variables":list(range(1,21)),"constraints":cons}


def sha(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def connected(nodes, adj):
    nodes=set(nodes)
    if len(nodes)<=1:return True
    st=[next(iter(nodes))]; seen={st[0]}
    while st:
        u=st.pop()
        for v in adj[u]&nodes:
            if v not in seen: seen.add(v); st.append(v)
    return seen==nodes


def cut_counts(vars_,adj):
    out={}
    for k in range(1,5):
        n=0
        for cut in itertools.combinations(vars_,k):
            rem=set(vars_)-set(cut)
            if len(rem)>1 and not connected(rem,adj): n+=1
        out[str(k)]=n
    return out


def relkey(c): return tuple(sorted("".join(str(int(b)) for b in r) for r in c["allowed"]))


def summary(source_key,path):
    clauses=parse(path); r=raw(source_key,clauses); vars_=r["variables"]
    adj={v:set() for v in vars_}
    for c in r["constraints"]:
        for a,b in itertools.combinations(c["scope"],2): adj[a].add(b);adj[b].add(a)
    deg={v:len(adj[v]) for v in vars_}; edges=sum(deg.values())//2; cuts=cut_counts(vars_,adj)
    overlap=Counter(); o1={c["id"]:set() for c in r["constraints"]}; o2={c["id"]:set() for c in r["constraints"]}
    for a,b in itertools.combinations(r["constraints"],2):
        k=len(set(a["scope"])&set(b["scope"])); overlap[k]+=1
        if k>=1:o1[a["id"]].add(b["id"]);o1[b["id"]].add(a["id"])
        if k>=2:o2[a["id"]].add(b["id"]);o2[b["id"]].add(a["id"])
    keys=sorted({relkey(c) for c in r["constraints"]}); idx={k:i for i,k in enumerate(keys)}; vr={v:[0]*len(keys) for v in vars_}
    for c in r["constraints"]:
        i=idx[relkey(c)]
        for v in c["scope"]:vr[v][i]+=1
    pos=Counter();neg=Counter()
    for cl in clauses:
        for lit in cl:(pos if lit>0 else neg)[abs(lit)]+=1
    groups=defaultdict(list)
    for v in vars_:
        sig=(deg[v],pos[v],neg[v],tuple(vr[v]),tuple(sorted(deg[n] for n in adj[v])))
        h=hashlib.sha256(json.dumps(sig,separators=(",",":")).encode()).hexdigest()[:16];groups[h].append(v)
    rem=set(vars_);work={v:set(adj[v]) for v in vars_};degen=0
    while rem:
        v=min(rem,key=lambda x:(len(work[x]&rem),x));degen=max(degen,len(work[v]&rem));rem.remove(v)
    tri=sum(1 for a,b,c in itertools.combinations(vars_,3) if b in adj[a] and c in adj[a] and c in adj[b])
    return {"source_blob_sha1":blob(path),"raw_sha256":sha(r),"edges":edges,"degree_min":min(deg.values()),"degree_max":max(deg.values()),"cut_counts":cuts,"overlap_counts":{str(k):overlap[k] for k in sorted(overlap)},"overlap_ge1_connected":connected(o1,o1),"overlap_ge2_connected":connected(o2,o2),"relation_surface_count":len(keys),"distinct_signature_count":len(groups),"all_singleton_signatures":all(len(x)==1 for x in groups.values()),"degeneracy":degen,"triangle_count":tri}


def main(candidate):
    checks={}; independent={}
    rows={r["source"]:r for r in candidate.get("rows",[])}
    checks["candidate_verdict_known"] = candidate.get("verdict") in {"REPLICATION_ALL_FOUR_MATCH_DENSE_LOW_CUT_ALL_SINGLETON_PROFILE","PARTIAL_REPLICATION_SIGNATURE_CLASSES_EMERGE","PARTIAL_REPLICATION_LOW_ORDER_SEPARATOR_EMERGES","PARTIAL_REPLICATION_OTHER_PROFILE_DIVERGENCE"}
    for name,(path,expected_blob) in SOURCES.items():
        s=summary(name,path); independent[name]=s; c=rows.get(name,{})
        checks[f"{name}_source_blob"] = s["source_blob_sha1"] == expected_blob == c.get("source_blob_sha1")
        checks[f"{name}_raw_sha"] = s["raw_sha256"] == c.get("raw_sha256")
        checks[f"{name}_p1"] = c.get("P1_primal",{}).get("edges")==s["edges"] and c.get("P1_primal",{}).get("degree_min")==s["degree_min"] and c.get("P1_primal",{}).get("degree_max")==s["degree_max"] and c.get("P1_primal",{}).get("cut_counts")==s["cut_counts"]
        checks[f"{name}_p3"] = c.get("P3_overlap",{}).get("pair_intersection_counts")==s["overlap_counts"] and c.get("P3_overlap",{}).get("graph_ge1_connected")==s["overlap_ge1_connected"] and c.get("P3_overlap",{}).get("graph_ge2_connected")==s["overlap_ge2_connected"]
        checks[f"{name}_p4"] = c.get("P4_local_mixing",{}).get("relation_surface_count")==s["relation_surface_count"]
        checks[f"{name}_p5"] = c.get("P5_variable_signature",{}).get("distinct_signature_count")==s["distinct_signature_count"] and c.get("P5_variable_signature",{}).get("all_singleton_signatures")==s["all_singleton_signatures"]
        checks[f"{name}_p6"] = c.get("P6_core",{}).get("degeneracy")==s["degeneracy"] and c.get("P6_core",{}).get("triangle_count")==s["triangle_count"]
    sf=candidate.get("scientific_firewall",{})
    checks["firewall"] = sf.get("P_VS_NP")=="OPEN" and sf.get("GENERAL_SAT_IN_P")=="NOT_PROVED" and sf.get("NEW_SOLVER_MECHANISMS")==0 and sf.get("NEW_CARRIER_MECHANISMS")==0
    return {"artifact_id":"JANUS-TRUMP-SATLIB-UF20-FAMILY-ASYMMETRY-REPLICATION-INDEPENDENT-CHECK-2026-09-16-v1.0","authority":"INDEPENDENT_DIAGNOSTIC_CHECK_ONLY","verified":all(checks.values()),"profile_imported":False,"checks":checks,"independent_rows":independent}


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--profile-json",required=True);a=ap.parse_args();candidate=json.loads(Path(a.profile_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(candidate),sort_keys=True))
