from __future__ import annotations

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
PREREG = ROOT / "research/TRUMP_SATLIB_UF20_FAMILY_SEALED_PORTFOLIO_REPLICATION_PREREGISTRATION_2026-09-16.json"
EXPECTED_PREREG_BLOB = "b72861af2453178dbad30ae72311f277369bd6f6"
SOURCES = {
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865", "e44b98343881d9f7657aa6c40fc6854559ca2cdd12e59edc7dddc22246d19d4f"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f", "7c9e05d9fa369935a0bf7d571b8c3b9a4a20244e3dfa75710987db2661553ac2"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1", "722b2479ea25355374d07b4d3c859c51af864b9158fda203270f1edda8e7086c"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b", "184f0f830dd2c2d1dd5fccd2b5b29304f27f15518b2b1e1315a4e9d5b5a30eb7"),
}
SEALED = {
    ROOT / "research/tools/apma_external_satlib_uf20_01_replay/replay.py": "67ae8bd40c58c6bb1f22f7651111d33ba6be1d0b",
    ROOT / "research/tools/apma_unseen_basis/raw_relation_basis.py": "63490c05ef3e91a4f682f75da26ff2af811839a6",
    ROOT / "research/tools/apma_connected_mixed_post_orbit_obstruction_census/census.py": "f5aa39804983d49149c976e8367a96397bad888e",
    ROOT / "research/tools/apma_unseen_basis/compositional_basis.py": "fdc83a3368a4ad362f00d3ee8aad958f06f8d264",
    ROOT / "research/tools/apma_log_alien_transfer/log_alien_transfer.py": "d20cd94fa2e0324e301f55211152c2d410099425",
    ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py": "a076cfc56d68aad0348415e313705da1f6b9cdcd",
}
CLOSED_ORBIT = {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"}


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def parse_dimacs(path: Path) -> list[tuple[int, ...]]:
    clauses: list[tuple[int, ...]] = []
    declared = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("c") or line in {"%", "0"}:
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError(f"BAD_HEADER:{path.name}")
            declared = (int(parts[2]), int(parts[3]))
            continue
        vals = [int(x) for x in line.split()]
        if not vals or vals[-1] != 0:
            raise ValueError(f"CLAUSE_MISSING_ZERO:{path.name}")
        clause = tuple(vals[:-1])
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError(f"NOT_STRICT_DISTINCT_3CNF:{path.name}")
        clauses.append(clause)
    if declared != (20, 91) or len(clauses) != 91:
        raise ValueError(f"DIMACS_COUNT_MISMATCH:{path.name}:{declared}:{len(clauses)}")
    return clauses


def normalize(source: str, clauses: list[tuple[int, ...]]) -> dict[str, Any]:
    constraints = []
    prefix = source.lower()
    for ordinal, clause in enumerate(clauses, 1):
        scope = sorted(abs(lit) for lit in clause)
        allowed = []
        for bits in itertools.product((0, 1), repeat=3):
            assignment = dict(zip(scope, bits, strict=True))
            satisfied = any(
                (assignment[abs(lit)] == 1) if lit > 0 else (assignment[abs(lit)] == 0)
                for lit in clause
            )
            if satisfied:
                allowed.append(list(bits))
        constraints.append({"id": f"satlib_{prefix}_c{ordinal:03d}", "scope": scope, "allowed": allowed})
    return raw_basis.canonicalize_raw({"variables": list(range(1, 21)), "constraints": constraints})


def source_guard() -> dict[str, Any]:
    bindings = {str(PREREG.relative_to(ROOT)): blob(PREREG) == EXPECTED_PREREG_BLOB}
    for path, expected in SEALED.items():
        bindings[str(path.relative_to(ROOT))] = blob(path) == expected
    source_bindings = {name: blob(path) == expected_blob for name, (path, expected_blob, _) in SOURCES.items()}
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    status_ok = prereg.get("status") == "FROZEN_BEFORE_UF20_02_TO_UF20_05_PORTFOLIO_REPLAY"
    return {"ok": all(bindings.values()) and all(source_bindings.values()) and status_ok, "bindings": bindings, "source_bindings": source_bindings, "prereg_status_ok": status_ok}


def replay_one(source: str, path: Path, expected_raw_sha: str) -> dict[str, Any]:
    clauses = parse_dimacs(path)
    raw = normalize(source, clauses)
    raw_sha = hashlib.sha256(canonical_bytes(raw)).hexdigest()
    if raw_sha != expected_raw_sha:
        return {"source": source, "status": "SOURCE_RAW_OR_BINDING_GUARD_FAILURE", "raw_sha256": raw_sha, "expected_raw_sha256": expected_raw_sha}

    eligibility = reference_census.eligibility(raw)
    if not eligibility.get("eligible"):
        return {"source": source, "status": "SOURCE_RAW_OR_BINDING_GUARD_FAILURE", "raw_sha256": raw_sha, "eligibility": eligibility, "reason": "NOT_ELIGIBLE_CONNECTED_MIXED"}

    comp = compositional_basis.induce_compositional_basis(raw)
    comp_receipt = {
        "status": comp.get("status"),
        "component_count": comp.get("component_count"),
        "open_component_count": comp.get("open_component_count"),
    }

    log_alien = reference_census.replay_log_alien(raw)
    if log_alien.get("closed"):
        win = log_alien.get("winning_attempt", {})
        return {
            "source": source,
            "status": "CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER",
            "raw_sha256": raw_sha,
            "eligibility": eligibility,
            "compositional": comp_receipt,
            "log_alien": log_alien,
            "orbit": {"executed": False, "reason": "STOP_ON_FIRST_EXISTING_AUTHORITATIVE_CLOSURE"},
            "closure": {"mechanism": "SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER", "status": win.get("status")},
        }

    orbit = orbit_candidate.run_candidate(raw)
    orbit_receipt = {
        "executed": True,
        "status": orbit.get("status"),
        "solver_authority": orbit.get("solver_authority"),
        "raw_semantic_sha256": orbit.get("raw_semantic_sha256"),
        "cells": orbit.get("cells"),
        "nontrivial_cells": orbit.get("nontrivial_cells"),
        "quotient_states_Q": orbit.get("quotient_states_Q"),
        "certificate_type": (orbit.get("certificate") or {}).get("type"),
        "resource_receipt": orbit.get("resource_receipt", {}),
    }
    if orbit.get("status") in CLOSED_ORBIT and orbit.get("solver_authority") is True:
        status = "CLOSED_BY_SEALED_ORBIT_COUNT_V1"
        closure = {"mechanism": "EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT", "status": orbit.get("status")}
    else:
        status = "UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO"
        closure = None
    return {
        "source": source,
        "status": status,
        "raw_sha256": raw_sha,
        "eligibility": eligibility,
        "compositional": comp_receipt,
        "log_alien": log_alien,
        "orbit": orbit_receipt,
        "closure": closure,
    }


def firewall() -> dict[str, Any]:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
    }


def main() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": "JANUS-TRUMP-SATLIB-UF20-FAMILY-SEALED-PORTFOLIO-REPLICATION-2026-09-16-v1.0", "authority": "DIAGNOSTIC_ONLY__SOURCE_BOUND_FAMILY_REPLAY_OF_EXISTING_SEALED_PORTFOLIO", "verdict": "SOURCE_RAW_OR_BINDING_GUARD_FAILURE", "source_guard": guard, "scientific_firewall": firewall()}
    rows = [replay_one(name, path, raw_sha) for name, (path, _, raw_sha) in SOURCES.items()]
    if any(r["status"] == "SOURCE_RAW_OR_BINDING_GUARD_FAILURE" for r in rows):
        verdict = "SOURCE_RAW_OR_BINDING_GUARD_FAILURE"
    else:
        verdict = "PASS_DIAGNOSTIC_FAMILY_SEALED_PORTFOLIO_REPLICATION"
    return {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-FAMILY-SEALED-PORTFOLIO-REPLICATION-2026-09-16-v1.0",
        "authority": "DIAGNOSTIC_ONLY__SOURCE_BOUND_FAMILY_REPLAY_OF_EXISTING_SEALED_PORTFOLIO",
        "verdict": verdict,
        "source_guard": guard,
        "rows": rows,
        "outcome_counts": dict(sorted(Counter(r["status"] for r in rows).items())),
        "resource_receipt": {
            "new_adapters": 0,
            "new_solver_mechanisms": 0,
            "new_carrier_mechanisms": 0,
            "new_symmetry_mechanisms": 0,
            "new_separator_branching": 0,
            "full_variable_cube_enumerations": 0,
            "budget_raise": False,
        },
        "scientific_firewall": firewall(),
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
