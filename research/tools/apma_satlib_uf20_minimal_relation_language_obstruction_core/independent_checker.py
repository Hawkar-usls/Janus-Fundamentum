from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_mixed_carrier_barrier.check_schaefer_barrier import (
    is_0_valid,
    is_1_valid,
    is_horn,
    is_dual_horn,
    is_bijunctive,
    is_affine,
)

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_SATLIB_UF20_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORE_PREREGISTRATION_2026-09-16.json"
PARENT = ROOT / "research/TRUMP_SATLIB_UF20_FAMILY_SEALED_PORTFOLIO_REPLICATION_RESULT_2026-09-16.json"
PRIMITIVE = ROOT / "research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py"
EXPECTED = {
    PREREG: "b75582fe0e0cb53e5b55dcf37a84944477505f92",
    PARENT: "277214289387abf6cf7e2d97bdf7dcf1f1727e07",
    PRIMITIVE: "11fcacd5f0c550543f96648a7965734308509d22",
}
SOURCES = {
    "UF20_01": (ROOT / "research/source_data/SATLIB_UF20_01_2026-09-16.cnf", "8330041b292e0501f8d74c1b1d32ca96c4498864"),
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}
BASIS_NAMES = ("ZERO_VALID", "ONE_VALID", "HORN", "DUAL_HORN", "BIJUNCTIVE", "AFFINE")
TYPE_IDS = tuple("".join(map(str, bits)) for bits in itertools.product((0, 1), repeat=3))
CUBE3 = tuple(itertools.product((0, 1), repeat=3))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def relation(type_id: str) -> set[tuple[int, ...]]:
    forbidden = tuple(int(ch) for ch in type_id)
    return {row for row in CUBE3 if row != forbidden}


def classify(language: list[set[tuple[int, ...]]]) -> dict[str, bool]:
    if not language:
        return {name: True for name in BASIS_NAMES}
    return {
        "ZERO_VALID": is_0_valid(language),
        "ONE_VALID": is_1_valid(language),
        "HORN": is_horn(language),
        "DUAL_HORN": is_dual_horn(language),
        "BIJUNCTIVE": is_bijunctive(language),
        "AFFINE": is_affine(language),
    }


def ids(mask: int) -> list[str]:
    return [TYPE_IDS[i] for i in range(8) if mask & (1 << i)]


def bases(mask: int) -> list[str]:
    fp = classify([relation(x) for x in ids(mask)])
    return [name for name in BASIS_NAMES if fp[name]]


def enumerate_expected() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, list[str]]]:
    single = {type_id: bases(1 << i) for i, type_id in enumerate(TYPE_IDS)}
    rows=[]; obstruction=[]
    for mask in range(256):
        selected=ids(mask); b=bases(mask); obs=bool(selected) and not b
        rows.append({"mask":mask,"relation_types":selected,"size":len(selected),"candidate_bases":b,"obstruction":obs})
        if obs: obstruction.append(mask)
    obsset=set(obstruction); minimal=[]
    for mask in obstruction:
        proper=[sub for sub in range(256) if sub != mask and (sub & mask)==sub]
        if all(sub not in obsset for sub in proper):
            selected=ids(mask)
            minimal.append({"mask":mask,"relation_types":selected,"size":len(selected),"candidate_bases":[],"single_relation_basis_sets":{x:single[x] for x in selected}})
    return rows,minimal,single


def parse_surface(path: Path) -> Counter[str]:
    declared=None; pending=[]; clauses=[]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line=raw_line.strip()
        if not line or line.startswith("c") or line in {"%","0"}: continue
        if line.startswith("p "):
            p=line.split(); declared=(int(p[2]),int(p[3])); continue
        for x in map(int,line.split()):
            if x==0:
                assert len(pending)==3 and len({abs(z) for z in pending})==3
                clauses.append(tuple(pending)); pending=[]
            else: pending.append(x)
    assert not pending and declared==(20,91) and len(clauses)==91
    counts:Counter[str]=Counter()
    for clause in clauses:
        by={abs(lit):(0 if lit>0 else 1) for lit in clause}
        scope=sorted(by)
        counts["".join(str(by[v]) for v in scope)] += 1
    return counts


def main(candidate: dict[str, Any]) -> dict[str, Any]:
    rows,minimal,single=enumerate_expected()
    candidate_rows={int(r["mask"]):r for r in candidate.get("language_rows",[])}
    candidate_cores={int(r["mask"]):r for r in candidate.get("minimal_cores",[])}
    checks:dict[str,bool]={
        "candidate_not_imported":True,
        "binding_files":all(blob(path)==expected for path,expected in EXPECTED.items()),
        "source_blobs":all(blob(path)==expected for path,expected in SOURCES.values()),
        "256_rows":len(candidate_rows)==256 and set(candidate_rows)==set(range(256)),
        "single_relation_basis_sets":candidate.get("single_relation_basis_sets")==single,
        "minimal_core_count":candidate.get("minimal_core_count")==len(minimal),
        "obstruction_subset_count":candidate.get("obstruction_subset_count")==sum(1 for r in rows if r["obstruction"]),
    }
    for row in rows:
        c=candidate_rows.get(row["mask"],{})
        checks[f"mask_{row['mask']:03d}"]=c.get("relation_types")==row["relation_types"] and c.get("size")==row["size"] and c.get("candidate_bases")==row["candidate_bases"] and c.get("obstruction")==row["obstruction"]
    for core in minimal:
        c=candidate_cores.get(core["mask"],{})
        checks[f"core_{core['mask']:03d}"]=c.get("relation_types")==core["relation_types"] and c.get("size")==core["size"] and c.get("candidate_bases")==[] and c.get("single_relation_basis_sets")==core["single_relation_basis_sets"]

    source_map={r.get("source"):r for r in candidate.get("source_presence_map",[])}
    expected_masks=[r["mask"] for r in minimal]
    independent_sources={}
    for source,(path,_) in SOURCES.items():
        counts=parse_surface(path)
        surface=[x for x in TYPE_IDS if counts[x]>0]
        present=[mask for mask in expected_masks if all(counts[x]>0 for x in ids(mask))]
        independent_sources[source]={"surface":surface,"counts":{x:counts[x] for x in TYPE_IDS},"minimal_core_masks_present":present}
        c=source_map.get(source,{})
        checks[f"{source}_surface"]=c.get("relation_surface")==surface and c.get("surface_is_exact_frozen_eight")== (surface==list(TYPE_IDS)) and c.get("relation_type_clause_counts")==independent_sources[source]["counts"] and c.get("minimal_core_masks_present")==present

    checks["verdict"]=candidate.get("verdict")== ("PASS_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORES_ENUMERATED" if minimal else "NO_RELATION_LANGUAGE_OBSTRUCTION_FOUND")
    rr=candidate.get("resource_receipt",{})
    checks["resources"]=rr.get("relation_languages_enumerated")==256 and rr.get("formula_subsets_enumerated")==0 and rr.get("variable_assignment_cubes_enumerated")==0 and rr.get("solver_invocations")==0 and rr.get("new_solver_mechanisms")==0 and rr.get("new_carrier_mechanisms")==0 and rr.get("new_adapters")==0 and rr.get("new_quotients")==0 and rr.get("budget_raise") is False
    sf=candidate.get("scientific_firewall",{})
    checks["firewall"]=sf.get("P_VS_NP")=="OPEN" and sf.get("GENERAL_SAT_IN_P")=="NOT_PROVED" and sf.get("MINIMAL_LANGUAGE_CORE_IMPLIES_HARDNESS") is False

    return {
        "artifact_id":"JANUS-TRUMP-SATLIB-UF20-MINIMAL-RELATION-LANGUAGE-OBSTRUCTION-CORE-INDEPENDENT-CHECK-2026-09-16-v1.0",
        "authority":"INDEPENDENT_DIAGNOSTIC_CHECK_ONLY",
        "candidate_imported":False,
        "verified":all(checks.values()),
        "checks":checks,
        "independent_minimal_cores":minimal,
        "independent_minimal_core_count":len(minimal),
        "independent_sources":independent_sources,
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate-json",required=True); args=ap.parse_args()
    candidate=json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    result=main(candidate); print(json.dumps(result,sort_keys=True,separators=(",", ":")))
    if not result["verified"]: raise SystemExit(1)
