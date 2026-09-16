from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as reference_census

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865", "e44b98343881d9f7657aa6c40fc6854559ca2cdd12e59edc7dddc22246d19d4f"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f", "7c9e05d9fa369935a0bf7d571b8c3b9a4a20244e3dfa75710987db2661553ac2"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1", "722b2479ea25355374d07b4d3c859c51af864b9158fda203270f1edda8e7086c"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b", "184f0f830dd2c2d1dd5fccd2b5b29304f27f15518b2b1e1315a4e9d5b5a30eb7"),
}
CLOSED_ORBIT = {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_sha(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def parse(path: Path) -> list[tuple[int, ...]]:
    clauses=[]; declared=None; pending=[]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        s=raw_line.strip()
        if not s or s.startswith("c") or s in {"%","0"}: continue
        if s.startswith("p "):
            p=s.split(); declared=(int(p[2]),int(p[3])); continue
        for x in map(int,s.split()):
            if x==0:
                assert len(pending)==3 and len({abs(z) for z in pending})==3
                clauses.append(tuple(pending)); pending=[]
            else: pending.append(x)
    assert not pending and declared==(20,91) and len(clauses)==91
    return clauses


def normalize(source: str, clauses: list[tuple[int, ...]]) -> dict[str, Any]:
    constraints=[]
    for ordinal,clause in enumerate(clauses,1):
        scope=sorted(abs(lit) for lit in clause); allowed=[]
        for bits in itertools.product((0,1),repeat=3):
            a=dict(zip(scope,bits,strict=True))
            if any((a[abs(lit)]==1) if lit>0 else (a[abs(lit)]==0) for lit in clause): allowed.append(list(bits))
        constraints.append({"id":f"satlib_{source.lower()}_c{ordinal:03d}","scope":scope,"allowed":allowed})
    return raw_basis.canonicalize_raw({"variables":list(range(1,21)),"constraints":constraints})


def independent_row(source: str, path: Path, expected_raw: str) -> dict[str, Any]:
    raw=normalize(source,parse(path)); raw_sha=canonical_sha(raw); assert raw_sha==expected_raw
    elig=reference_census.eligibility(raw); assert elig.get("eligible") is True
    comp=compositional_basis.induce_compositional_basis(raw)
    comp_rec={"status":comp.get("status"),"component_count":comp.get("component_count"),"open_component_count":comp.get("open_component_count")}
    log=reference_census.replay_log_alien(raw)
    if log.get("closed"):
        return {"source":source,"status":"CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER","raw_sha256":raw_sha,"eligibility_class":elig.get("eligibility_class"),"compositional":comp_rec,"log_closed":True,"orbit_executed":False,"orbit_status":None,"orbit_solver_authority":None}
    orbit=orbit_candidate.run_candidate(raw)
    closed=orbit.get("status") in CLOSED_ORBIT and orbit.get("solver_authority") is True
    return {"source":source,"status":"CLOSED_BY_SEALED_ORBIT_COUNT_V1" if closed else "UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO","raw_sha256":raw_sha,"eligibility_class":elig.get("eligibility_class"),"compositional":comp_rec,"log_closed":False,"orbit_executed":True,"orbit_status":orbit.get("status"),"orbit_solver_authority":orbit.get("solver_authority")}


def projected_candidate_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source":row.get("source"),
        "status":row.get("status"),
        "raw_sha256":row.get("raw_sha256"),
        "eligibility_class":(row.get("eligibility") or {}).get("eligibility_class"),
        "compositional":row.get("compositional"),
        "log_closed":bool((row.get("log_alien") or {}).get("closed", False)),
        "orbit_executed":(row.get("orbit") or {}).get("executed"),
        "orbit_status":(row.get("orbit") or {}).get("status"),
        "orbit_solver_authority":(row.get("orbit") or {}).get("solver_authority"),
    }


def main(candidate: dict[str, Any]) -> dict[str, Any]:
    rows={r.get("source"):r for r in candidate.get("rows",[])}
    independent={name:independent_row(name,path,raw_sha) for name,(path,_,raw_sha) in SOURCES.items()}
    checks={"candidate_not_imported":True,"source_set":set(rows)==set(SOURCES)}
    for name,(path,source_blob,_) in SOURCES.items():
        checks[f"{name}_source_blob"]=blob(path)==source_blob
        checks[f"{name}_replay"]=projected_candidate_row(rows.get(name,{}))==independent[name]
    counts=dict(sorted(Counter(r["status"] for r in independent.values()).items()))
    checks["outcome_counts"]=candidate.get("outcome_counts")==counts
    checks["verdict"]=candidate.get("verdict")=="PASS_DIAGNOSTIC_FAMILY_SEALED_PORTFOLIO_REPLICATION"
    rr=candidate.get("resource_receipt",{})
    checks["resources"]=rr.get("new_adapters")==0 and rr.get("new_solver_mechanisms")==0 and rr.get("new_carrier_mechanisms")==0 and rr.get("new_symmetry_mechanisms")==0 and rr.get("new_separator_branching")==0 and rr.get("full_variable_cube_enumerations")==0 and rr.get("budget_raise") is False
    sf=candidate.get("scientific_firewall",{})
    checks["firewall"]=sf.get("P_VS_NP")=="OPEN" and sf.get("GENERAL_SAT_IN_P")=="NOT_PROVED" and sf.get("CONNECTED_MIXED_CORE_SOLVED")=="NO"
    return {"artifact_id":"JANUS-TRUMP-SATLIB-UF20-FAMILY-SEALED-PORTFOLIO-REPLICATION-INDEPENDENT-CHECK-2026-09-16-v1.1","verified":all(checks.values()),"candidate_imported":False,"checks":checks,"independent_rows":independent,"independent_outcome_counts":counts}


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate-json",required=True); args=ap.parse_args()
    candidate=json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    result=main(candidate); print(json.dumps(result,sort_keys=True,separators=(",", ":")))
    if not result["verified"]: raise SystemExit(1)
