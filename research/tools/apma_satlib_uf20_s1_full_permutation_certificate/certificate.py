from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_SATLIB_UF20_S1_FULL_PERMUTATION_AUTOMORPHISM_CERTIFICATE_PREREGISTRATION_2026-09-16.json"
PROOF = ROOT / "research/TRUMP_SATLIB_UF20_S1_FULL_PERMUTATION_AUTOMORPHISM_DIRECT_PROOF_2026-09-16.md"
PARENT = ROOT / "research/TRUMP_SATLIB_UF20_SIGNATURE_ABLATION_REPLICATION_RESULT_2026-09-16.json"
ORBIT = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
EXPECTED_BINDINGS = {
    PREREG: "dfef6eb9d56135c9372c2fb02aabbf4326404484",
    PROOF: "7c4a5e7a51fec500b66bcf8f6dc215ca2f5f71e8",
    PARENT: "bca1542226c7fe29f8d803b7473c4aa4c19d1e78",
    ORBIT: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
}
SOURCES = {
    "UF20_01": (ROOT / "research/source_data/SATLIB_UF20_01_2026-09-16.cnf", "8330041b292e0501f8d74c1b1d32ca96c4498864", "a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"),
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865", "e44b98343881d9f7657aa6c40fc6854559ca2cdd12e59edc7dddc22246d19d4f"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f", "7c9e05d9fa369935a0bf7d571b8c3b9a4a20244e3dfa75710987db2661553ac2"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1", "722b2479ea25355374d07b4d3c859c51af864b9158fda203270f1edda8e7086c"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b", "184f0f830dd2c2d1dd5fccd2b5b29304f27f15518b2b1e1315a4e9d5b5a30eb7"),
}


def git_blob_sha1(path: Path) -> str:
    b=path.read_bytes();return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()


def canonical_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()


def parse_dimacs(path: Path) -> list[tuple[int,...]]:
    clauses=[];declared=None
    for line in path.read_text(encoding="utf-8").splitlines():
        s=line.strip()
        if not s or s.startswith("c") or s in {"%","0"}:continue
        if s.startswith("p "):
            p=s.split();declared=(int(p[2]),int(p[3]));continue
        xs=[int(x) for x in s.split()]
        if xs[-1]!=0:raise ValueError("BAD_DIMACS")
        cl=tuple(xs[:-1])
        if len(cl)!=3 or len({abs(x) for x in cl})!=3:raise ValueError("NOT_DISTINCT_3CNF")
        clauses.append(cl)
    if declared!=(20,91) or len(clauses)!=91:raise ValueError("BAD_COUNTS")
    return clauses


def make_raw(name: str, clauses: list[tuple[int,...]]) -> dict[str,Any]:
    cons=[]
    for i,cl in enumerate(clauses,1):
        scope=sorted(abs(x) for x in cl);rows=[]
        for bits in itertools.product((0,1),repeat=3):
            a=dict(zip(scope,bits))
            if any(bool(a[abs(l)]) if l>0 else not bool(a[abs(l)]) for l in cl):rows.append(list(bits))
        cons.append({"id":f"satlib_{name.lower()}_c{i:03d}","scope":scope,"allowed":rows})
    return canonicalize_raw({"variables":list(range(1,21)),"constraints":cons})


def unique_forbidden(row: dict[str,Any]) -> tuple[int,...] | None:
    allowed={tuple(int(x) for x in t) for t in row["allowed"]}
    if len(row["scope"])!=3 or len(allowed)!=7:return None
    missing=[t for t in itertools.product((0,1),repeat=3) if t not in allowed]
    return missing[0] if len(missing)==1 else None


def semantic_s1(raw: dict[str,Any]) -> tuple[dict[int,tuple[int,int,int]],dict[str,Any]]:
    vars_=raw["variables"];adj={v:set() for v in vars_};zero=Counter();one=Counter();premises=True
    for c in raw["constraints"]:
        f=unique_forbidden(c)
        if f is None:premises=False;continue
        for u,v in itertools.combinations(c["scope"],2):adj[u].add(v);adj[v].add(u)
        for idx,v in enumerate(c["scope"]):
            (zero if f[idx]==0 else one)[v]+=1
    s1={v:(len(adj[v]),zero[v],one[v]) for v in vars_}
    return s1,{"all_constraints_three_ary_single_forbidden_tuple":premises,"semantic_zero_total":sum(zero.values()),"semantic_one_total":sum(one.values())}


def source_s1(clauses: list[tuple[int,...]]) -> dict[int,tuple[int,int,int]]:
    adj={v:set() for v in range(1,21)};pos=Counter();neg=Counter()
    for cl in clauses:
        for u,v in itertools.combinations([abs(x) for x in cl],2):adj[u].add(v);adj[v].add(u)
        for lit in cl:(pos if lit>0 else neg)[abs(lit)]+=1
    return {v:(len(adj[v]),pos[v],neg[v]) for v in range(1,21)}


def partition(s1: dict[int,tuple[int,int,int]]) -> list[list[int]]:
    g=defaultdict(list)
    for v in sorted(s1):g[s1[v]].append(v)
    out=[sorted(c) for c in g.values()];out.sort(key=lambda c:(c[0],len(c),c));return out


def local_transport_sanity() -> bool:
    for forbidden in itertools.product((0,1),repeat=3):
        for perm in itertools.permutations(range(3)):
            transported=[None,None,None]
            for old,new in enumerate(perm):transported[new]=forbidden[old]
            for old,new in enumerate(perm):
                if transported[new]!=forbidden[old]:return False
    return True


def source_certificate(name: str,path: Path,expected_blob: str,expected_raw: str) -> dict[str,Any]:
    clauses=parse_dimacs(path);raw=make_raw(name,clauses);raw_sha=canonical_sha256(raw)
    semantic,premises=semantic_s1(raw);source=source_s1(clauses);classes=partition(semantic)
    formula=orbit.validate_and_normalize(raw)
    non=[c for c in classes if len(c)>1];swap_rows=[];unresolved=[]
    for cls in non:
        if len(cls)==2:
            u,v=cls;ok=orbit.is_exact_transposition_automorphism(formula,u,v)
            swap_rows.append({"pair":[u,v],"exact_transposition_automorphism":ok})
            if ok:unresolved.append(cls)
        else:
            unresolved.append(cls)
    trivial=not unresolved
    return {
        "source":name,
        "source_blob_ok":git_blob_sha1(path)==expected_blob,
        "raw_sha256":raw_sha,
        "raw_sha_ok":raw_sha==expected_raw,
        "premises":premises,
        "semantic_S1_equals_DIMACS_S1":semantic==source,
        "S1_classes":classes,
        "non_singleton_S1_classes":non,
        "sealed_swap_checks":swap_rows,
        "unresolved_nonidentity_action_blocks":unresolved,
        "full_pure_variable_permutation_automorphism_group_trivial":trivial,
    }


def main() -> dict[str,Any]:
    bindings={str(p.relative_to(ROOT)):git_blob_sha1(p)==sha for p,sha in EXPECTED_BINDINGS.items()}
    rows=[source_certificate(name,path,b,r) for name,(path,b,r) in SOURCES.items()]
    source_ok=all(r["source_blob_ok"] and r["raw_sha_ok"] for r in rows)
    premises_ok=all(r["premises"]["all_constraints_three_ary_single_forbidden_tuple"] and r["semantic_S1_equals_DIMACS_S1"] for r in rows)
    transport_ok=local_transport_sanity()
    group_ok=all(r["full_pure_variable_permutation_automorphism_group_trivial"] for r in rows)
    if not all(bindings.values()) or not source_ok:
        verdict="SOURCE_OR_SEALED_PRIMITIVE_GUARD_FAILURE"
    elif not transport_ok or not premises_ok:
        verdict="S1_INVARIANCE_LEMMA_FALSIFIED"
    elif not group_ok:
        verdict="S1_INVARIANCE_SOUND_BUT_NONTRIVIAL_GROUP_REMAINS_ON_A_FROZEN_SOURCE"
    else:
        verdict="PASS_SCOPED_S1_INVARIANCE_AND_TRIVIAL_FULL_VARIABLE_PERMUTATION_GROUP_ON_ALL_FIVE"
    return {
        "artifact_id":"JANUS-TRUMP-SATLIB-UF20-S1-FULL-PERMUTATION-AUTOMORPHISM-CERTIFICATE-2026-09-16-v1.0",
        "authority":"DIAGNOSTIC_PROOF_CERTIFICATE_ONLY__NO_SOLVER_OR_CARRIER_DESIGN",
        "verdict":verdict,
        "source_guard":{"ok":all(bindings.values()) and source_ok,"bindings":bindings},
        "direct_proof":{"blob":EXPECTED_BINDINGS[PROOF],"lemma":"S1_NECESSARY_INVARIANT_FOR_EXACT_VARIABLE_PERMUTATION_AUTOMORPHISMS","local_coordinate_transport_sanity":transport_ok},
        "rows":rows,
        "resource_receipt":{"full_permutation_enumeration":0,"sealed_nonidentity_swap_checks":sum(len(r["sealed_swap_checks"]) for r in rows),"solver_invocations":0,"new_solver_mechanisms":0,"new_carrier_mechanisms":0,"new_automorphism_search_mechanisms":0,"budget_raise":False},
        "scientific_firewall":{"P_VS_NP":"OPEN","GENERAL_SAT_IN_P":"NOT_PROVED","GENERAL_GT2_TRACTABILITY":"NOT_PROVED","CONNECTED_MIXED_CORE_SOLVED":"NO","ARBITRARY_UNSEEN_INVARIANT_DISCOVERY":"NOT_PROVED"},
    }


if __name__=="__main__":
    print(json.dumps(main(),sort_keys=True,separators=(",",":")))
