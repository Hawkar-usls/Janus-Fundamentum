from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "UF20_01": (ROOT / "research/source_data/SATLIB_UF20_01_2026-09-16.cnf", "8330041b292e0501f8d74c1b1d32ca96c4498864", "a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"),
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865", "e44b98343881d9f7657aa6c40fc6854559ca2cdd12e59edc7dddc22246d19d4f"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f", "7c9e05d9fa369935a0bf7d571b8c3b9a4a20244e3dfa75710987db2661553ac2"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1", "722b2479ea25355374d07b4d3c859c51af864b9158fda203270f1edda8e7086c"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b", "184f0f830dd2c2d1dd5fccd2b5b29304f27f15518b2b1e1315a4e9d5b5a30eb7"),
}


def blob(path: Path) -> str:
    b = path.read_bytes()
    return hashlib.sha1(f"blob {len(b)}\0".encode("ascii") + b).hexdigest()


def sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def parse(path: Path) -> list[tuple[int, ...]]:
    clauses=[]; declared=None
    for line in path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("c") or s in {"%","0"}: continue
        if s.startswith("p "):
            p=s.split(); declared=(int(p[2]),int(p[3])); continue
        xs=[int(x) for x in s.split()]
        if xs[-1] != 0: raise ValueError("BAD_DIMACS")
        cl=tuple(xs[:-1])
        if len(cl)!=3 or len({abs(x) for x in cl})!=3: raise ValueError("BAD_3CNF")
        clauses.append(cl)
    if declared!=(20,91) or len(clauses)!=91: raise ValueError("BAD_COUNTS")
    return clauses


def make_raw(name: str, clauses: list[tuple[int,...]]) -> dict[str,Any]:
    constraints=[]
    for i,cl in enumerate(clauses,1):
        scope=sorted(abs(x) for x in cl); rows=[]
        for bits in itertools.product((0,1), repeat=3):
            a=dict(zip(scope,bits))
            if any(bool(a[abs(lit)]) if lit>0 else not bool(a[abs(lit)]) for lit in cl): rows.append(list(bits))
        constraints.append({"id":f"satlib_{name.lower()}_c{i:03d}","scope":scope,"allowed":rows})
    return canonicalize_raw({"variables":list(range(1,21)),"constraints":constraints})


def relkey(c: dict[str,Any]) -> tuple[str,...]:
    return tuple(sorted("".join(str(int(b)) for b in row) for row in c["allowed"]))


def features(raw: dict[str,Any], clauses: list[tuple[int,...]]) -> dict[int,dict[str,Any]]:
    vars_=raw["variables"]; adj={v:set() for v in vars_}
    for c in raw["constraints"]:
        for u,v in itertools.combinations(c["scope"],2): adj[u].add(v);adj[v].add(u)
    deg={v:len(adj[v]) for v in vars_}; pos=Counter();neg=Counter()
    for cl in clauses:
        for lit in cl:(pos if lit>0 else neg)[abs(lit)]+=1
    surfaces=sorted({relkey(c) for c in raw["constraints"]}); idx={k:i for i,k in enumerate(surfaces)}
    if len(surfaces)!=8: raise ValueError("NOT_EIGHT_SURFACES")
    incidence={v:[0]*8 for v in vars_}
    for c in raw["constraints"]:
        j=idx[relkey(c)]
        for v in c["scope"]:incidence[v][j]+=1
    return {v:{
        "S0":(deg[v],),
        "S1":(deg[v],pos[v],neg[v]),
        "S2":(deg[v],pos[v],neg[v],tuple(incidence[v])),
        "S3":(deg[v],pos[v],neg[v],tuple(incidence[v]),tuple(sorted(deg[n] for n in adj[v]))),
    } for v in vars_}


def classes(feat: dict[int,dict[str,Any]], level: str) -> list[list[int]]:
    g=defaultdict(list)
    for v in sorted(feat): g[json.dumps(feat[v][level],separators=(",",":"))].append(v)
    out=[sorted(x) for x in g.values()];out.sort(key=lambda c:(c[0],len(c),c));return out


def comp_sizes(vertices: list[int], edges: list[tuple[int,int]]) -> list[int]:
    adj={v:set() for v in vertices}
    for u,v in edges:adj[u].add(v);adj[v].add(u)
    seen=set();out=[]
    for s in sorted(vertices):
        if s in seen:continue
        st=[s];seen.add(s);n=0
        while st:
            u=st.pop();n+=1
            for v in adj[u]:
                if v not in seen:seen.add(v);st.append(v)
        out.append(n)
    return sorted(out,reverse=True)


def level_receipt(formula: orbit.NormalizedFormula, cls: list[list[int]]) -> dict[str,Any]:
    edges=[];tested=0;rows=[]
    for c in cls:
        local=[]
        for u,v in itertools.combinations(c,2):
            tested+=1
            if orbit.is_exact_transposition_automorphism(formula,u,v):local.append((u,v));edges.append((u,v))
        rows.append({"variables":c,"size":len(c),"candidate_pairs_tested":len(c)*(len(c)-1)//2,"exact_transposition_edges":[list(e) for e in local],"exact_component_sizes":comp_sizes(c,local)})
    non=[c for c in cls if len(c)>1]
    if not non:outcome="SIGNATURE_LEVEL_ALREADY_ALL_SINGLETON"
    elif edges:outcome="EXACT_TRANSPOSITION_SYMMETRY_REAPPEARS_WITHIN_COARSE_CLASS"
    else:outcome="COARSE_CLASSES_EXIST_BUT_ALL_EXACT_TRANSPOSITIONS_FAIL"
    return {"outcome":outcome,"class_count":len(cls),"class_size_multiset":sorted((len(c) for c in cls),reverse=True),"max_class_size":max(map(len,cls)),"non_singleton_class_count":len(non),"variables_in_non_singleton_classes":sum(map(len,non)),"candidate_transposition_pairs_tested":tested,"exact_semantic_transposition_count":len(edges),"exact_semantic_transposition_edges":[list(e) for e in edges],"classes":rows}


def independent_source(name: str,path: Path,expected_blob: str,expected_raw: str) -> dict[str,Any]:
    clauses=parse(path);raw=make_raw(name,clauses);raw_sha=sha(raw)
    formula=orbit.validate_and_normalize(raw);feat=features(raw,clauses)
    levels={lvl:level_receipt(formula,classes(feat,lvl)) for lvl in ("S0","S1","S2","S3")}
    return {"source":name,"source_blob_ok":blob(path)==expected_blob,"raw_sha256":raw_sha,"raw_sha_ok":raw_sha==expected_raw,"orbit_internal_semantic_sha256":formula.semantic_sha256,"levels":levels}


def main(candidate: dict[str,Any]) -> dict[str,Any]:
    independent={name:independent_source(name,path,b,raw) for name,(path,b,raw) in SOURCES.items()}
    candidate_rows={r.get("source"):r for r in candidate.get("rows",[])}
    checks={
        "candidate_source_guard":candidate.get("source_guard",{}).get("ok") is True,
        "five_candidate_rows":set(candidate_rows)==set(SOURCES),
        "sealed_primitive_path":candidate.get("sealed_exact_transposition_primitive",{}).get("path")=="research/tools/apma_unseen_local_invariant_orbit_count/candidate.py",
        "sealed_primitive_blob":candidate.get("sealed_exact_transposition_primitive",{}).get("blob")=="a076cfc56d68aad0348415e313705da1f6b9cdcd",
    }
    for name,ind in independent.items():
        row=candidate_rows.get(name,{})
        checks[f"{name}_source_blob"] = ind["source_blob_ok"]
        checks[f"{name}_raw_sha"] = ind["raw_sha_ok"] and row.get("raw_sha256")==ind["raw_sha256"]
        checks[f"{name}_orbit_semantic_sha"] = row.get("orbit_internal_semantic_sha256")==ind["orbit_internal_semantic_sha256"]
        for lvl in ("S0","S1","S2","S3"):
            checks[f"{name}_{lvl}_receipt"] = row.get("levels",{}).get(lvl)==ind["levels"][lvl]
    total_tests=sum(ind["levels"][lvl]["candidate_transposition_pairs_tested"] for ind in independent.values() for lvl in ("S0","S1","S2","S3"))
    total_exact=sum(ind["levels"][lvl]["exact_semantic_transposition_count"] for ind in independent.values() for lvl in ("S0","S1","S2","S3"))
    rr=candidate.get("resource_receipt",{})
    checks["resource_totals"] = rr.get("candidate_transposition_pairs_tested")==total_tests and rr.get("exact_semantic_transpositions_verified")==total_exact
    checks["resource_firewall"] = rr.get("pairs_outside_same_coarse_class_tested")==0 and rr.get("quotient_states_enumerated")==0 and rr.get("solver_invocations")==0 and rr.get("full_variable_cube_states_enumerated")==0 and rr.get("new_solver_mechanisms")==0 and rr.get("new_carrier_mechanisms")==0 and rr.get("new_representation_adapters")==0 and rr.get("separator_branching")==0 and rr.get("budget_raise") is False
    sf=candidate.get("scientific_firewall",{})
    checks["scientific_firewall"] = sf.get("P_VS_NP")=="OPEN" and sf.get("GENERAL_SAT_IN_P")=="NOT_PROVED" and sf.get("CONNECTED_MIXED_CORE_SOLVED")=="NO"
    return {"artifact_id":"JANUS-TRUMP-SATLIB-UF20-SIGNATURE-ABLATION-REPLICATION-INDEPENDENT-CHECK-2026-09-16-v1.0","authority":"INDEPENDENT_DIAGNOSTIC_CHECK_ONLY","verified":all(checks.values()),"ablation_imported":False,"checks":checks,"independent_rows":list(independent.values()),"independent_totals":{"candidate_transposition_pairs_tested":total_tests,"exact_semantic_transpositions_verified":total_exact}}


if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--candidate-json",required=True);a=ap.parse_args();candidate=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(candidate),sort_keys=True,separators=(",",":")))
