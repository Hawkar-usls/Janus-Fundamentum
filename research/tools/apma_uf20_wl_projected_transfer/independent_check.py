from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "UF20_02": (ROOT/"research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865", "cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6"),
    "UF20_03": (ROOT/"research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f", "30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d"),
    "UF20_04": (ROOT/"research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1", "db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3"),
    "UF20_05": (ROOT/"research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b", "fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6"),
}
FEATURES = ["WL1_MAX_VARIABLE_COLOR_CLASS_SIZE","WL1_VARIABLE_PARTITION_IS_DISCRETE","WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE","WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE"]
BLOCK = {FEATURES[0]:1, FEATURES[1]:True, FEATURES[2]:1, FEATURES[3]:True}
OPEN = ["UF20_02","UF20_04","UF20_05"]


def blob(path: Path):
    b=path.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode()+b).hexdigest()

def enc(obj: Any): return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def parse_dimacs(path: Path):
    clauses=[]; cur=[]; header=None
    for line in path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("c") or s in {"%","0"}: continue
        if s.startswith("p "):
            p=s.split(); header=(int(p[2]),int(p[3])); continue
        for z in map(int,s.split()):
            if z==0:
                assert len(cur)==3 and len({abs(x) for x in cur})==3
                clauses.append(tuple(cur)); cur=[]
            else: cur.append(z)
    assert header==(20,91) and len(clauses)==91 and not cur
    return clauses

def relation_id(clause): return "".join("0" if lit>0 else "1" for lit in sorted(clause,key=lambda x:abs(x)))

def projected(source, path):
    picked=[(i,c) for i,c in enumerate(parse_dimacs(path),1) if relation_id(c) in {"000","111"}]
    variables=sorted({abs(x) for _,c in picked for x in c}); constraints=[]
    for ordinal, clause in picked:
        scope=sorted(abs(x) for x in clause); allowed=[]
        for bits in itertools.product((0,1),repeat=3):
            a=dict(zip(scope,bits,strict=True))
            if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in clause): allowed.append(list(bits))
        constraints.append({"id":f"satlib_{source.lower()}_c{ordinal:03d}","scope":scope,"allowed":allowed})
    return raw_basis.canonicalize_raw({"variables":variables,"constraints":constraints}), [i for i,_ in picked]

def relsig(c):
    return (len(c["scope"]), tuple(sorted(tuple(int(x) for x in r) for r in c["allowed"])))

def ranks(d):
    vals=sorted(set(d.values()),key=repr); mp={v:i for i,v in enumerate(vals)}; return {k:mp[v] for k,v in d.items()}

def graph(raw):
    ns=[]; adj=defaultdict(set); lab={}
    for v in sorted(raw["variables"]): n=("v",int(v)); ns.append(n); adj[n]; lab[n]=("V",)
    for c in raw["constraints"]:
        n=("c",str(c["id"])); ns.append(n); adj[n]; lab[n]=("C",relsig(c))
        for v in sorted(set(map(int,c["scope"]))): vn=("v",v); adj[n].add(vn); adj[vn].add(n)
    return sorted(ns,key=lambda x:(x[0],str(x[1]))),adj,lab

def one(ns,adj,lab):
    col=ranks(lab); rounds=0
    while True:
        nxt=ranks({u:(col[u],tuple(sorted(col[v] for v in adj[u]))) for u in ns}); rounds+=1
        if len(set(nxt.values()))==len(set(col.values())): return nxt,rounds
        col=nxt

def two(ns,adj,lab):
    vc=ranks(lab); pairs=[(u,v) for u in ns for v in ns]
    col=ranks({(u,v):(vc[u],vc[v],u==v,v in adj[u]) for u,v in pairs}); rounds=0
    while True:
        sig={(u,v):(col[(u,v)],tuple(sorted((col[(u,w)],col[(w,v)]) for w in ns))) for u,v in pairs}
        nxt=ranks(sig); rounds+=1
        if len(set(nxt.values()))==len(set(col.values())): return nxt,rounds
        col=nxt

def evaluate(raw):
    ns,adj,lab=graph(raw); vs=[x for x in ns if x[0]=="v"]
    c1,r1=one(ns,adj,lab); c2,r2=two(ns,adj,lab)
    s1=sorted(Counter(c1[v] for v in vs).values()); s2=sorted(Counter(c2[(v,v)] for v in vs).values())
    return {FEATURES[0]:max(s1),FEATURES[1]:all(x==1 for x in s1),FEATURES[2]:max(s2),FEATURES[3]:all(x==1 for x in s2),"_receipt":{"variable_count":len(vs),"constraint_count":len(ns)-len(vs),"incidence_vertex_count":len(ns),"incidence_edge_count":sum(len(adj[n]) for n in ns)//2,"wl1_rounds":r1,"wl2_rounds":r2}}

def main(candidate_path: Path):
    candidate=json.loads(candidate_path.read_text())
    rows={}; guards={}
    for source,(path,expected_blob,expected_sha) in SOURCES.items():
        assert blob(path)==expected_blob
        raw,ords=projected(source,path); sha=hashlib.sha256(enc(raw)).hexdigest(); ok=sha==expected_sha
        guards[source]={"projected_sha256":sha,"expected_projected_sha256":expected_sha,"ok":ok,"selected_clause_ordinals":ords}
        assert ok; rows[source]=evaluate(raw)
    per={}; survivors=[]
    for f in FEATURES:
        open_matches={s:rows[s][f]==BLOCK[f] for s in OPEN}; closed_diff=rows["UF20_03"][f]!=BLOCK[f]; survives=all(open_matches.values()) and closed_diff
        per[f]={"blocker_value":BLOCK[f],"open_matches":open_matches,"closed_value":rows["UF20_03"][f],"closed_differs":closed_diff,"survives":survives}
        if survives: survivors.append(f)
    if len(survivors)==4: expected="PROJECTED_WL_TRANSFER_ALL_FOUR_SURVIVE__FRESH_HOLDOUT_PREREGISTRATION_MAY_FOLLOW"
    elif survivors: expected="PROJECTED_WL_TRANSFER_PARTIAL_SURVIVOR_SET__FREEZE_SURVIVORS_BEFORE_ANY_HOLDOUT_GATE"
    else: expected="PROJECTED_WL_TRANSFER_NO_SURVIVOR__DO_NOT_UNBLIND_FRESH_HOLDOUT_FOR_THIS_CANDIDATE"
    checks={
        "identity_guards_exact":candidate.get("identity_guards")==guards,
        "feature_rows_exact":candidate.get("feature_rows")==rows,
        "per_feature_exact":candidate.get("per_feature_transfer")==per,
        "survivor_set_exact":candidate.get("surviving_features")==sorted(survivors),
        "falsified_set_exact":candidate.get("falsified_features")==sorted(set(FEATURES)-set(survivors)),
        "verdict_exact":candidate.get("verdict")==expected,
        "holdouts_unread":candidate.get("blindness_receipt",{}).get("fresh_holdout_formula_reads")==0 and candidate.get("blindness_receipt",{}).get("fresh_holdout_wl_values")==0,
        "no_solver_or_new_reduction":candidate.get("resource_receipt",{}).get("solver_invocations")==0 and candidate.get("resource_receipt",{}).get("new_reduction_mechanisms")==0,
        "firewall":candidate.get("scientific_firewall",{}).get("P_VS_NP")=="OPEN" and candidate.get("scientific_firewall",{}).get("GENERAL_SAT_IN_P")=="NOT_PROVED"
    }
    return {"artifact_id":"JANUS-TRUMP-UF20-WL-PROJECTED-TRANSFER-INDEPENDENT-CHECK-2026-09-17-v1.0","verdict":"PASS_INDEPENDENT_PROJECTED_TRANSFER_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_PROJECTED_TRANSFER_VERIFICATION","checks":checks,"independent_feature_rows":rows,"independent_surviving_features":sorted(survivors),"expected_candidate_verdict":expected,"candidate_imported":False,"fresh_holdout_formula_reads":0,"fresh_holdout_wl_values":0,"scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED"}}

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--candidate",required=True); a=p.parse_args(); r=main(Path(a.candidate)); print(json.dumps(r,sort_keys=True,separators=(",",":"))); raise SystemExit(0 if r["verdict"].startswith("PASS_") else 1)
