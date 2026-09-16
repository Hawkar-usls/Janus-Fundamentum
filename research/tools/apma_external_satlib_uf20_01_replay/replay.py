from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as reference_census

ARTIFACT_ID = "JANUS-TRUMP-SATLIB-UF20-01-SEALED-PORTFOLIO-REPLAY-2026-09-16-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__FROZEN_NEW_SOURCE_SEALED_PORTFOLIO_REPLAY"
ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path("research/source_data/SATLIB_UF20_01_2026-09-16.cnf")
RAW = Path("research/source_data/SATLIB_UF20_01_RAW_2026-09-16.json")
FREEZE = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_NEW_EVIDENCE_SOURCE_FREEZE_SATLIB_UF20_01_2026-09-16.json")
PREREG = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_NEW_EVIDENCE_REPLAY_PREREGISTRATION_SATLIB_UF20_01_2026-09-16.json")
REFERENCE = Path("research/tools/apma_connected_mixed_post_orbit_obstruction_census/census.py")

EXPECTED_BLOBS = {
    SOURCE: "8330041b292e0501f8d74c1b1d32ca96c4498864",
    RAW: "8b69a8f533ffaec44f196eea8791b0678f3f579c",
    FREEZE: "e21a59d5f4a248dfa2b25f643e9220c96affb1cf",
    PREREG: "76a88842bbf0403f0838e3d7811b5205dced0eaf",
    REFERENCE: "f5aa39804983d49149c976e8367a96397bad888e",
}
EXPECTED_RAW_SHA = "a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"
EXPECTED_SOURCE_SHA = "abd551864c6ff7403c3f4fc52737467a029954ce5ae7b0e5bf9ef0a9dde13509"
CLOSED_ORBIT = {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"}


def git_blob_sha1(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def source_guard() -> dict[str, Any]:
    checks = {str(p): git_blob_sha1(p) == sha for p, sha in EXPECTED_BLOBS.items()}
    freeze = json.loads((ROOT / FREEZE).read_text(encoding="utf-8"))
    prereg = json.loads((ROOT / PREREG).read_text(encoding="utf-8"))
    checks["freeze_status"] = freeze.get("status") == "FROZEN_BEFORE_PORTFOLIO_REPLAY"
    checks["prereg_status"] = prereg.get("status") == "FROZEN_BEFORE_ANY_CANDIDATE_PORTFOLIO_REPLAY"
    checks["prereg_freeze_commit"] = prereg.get("source_freeze", {}).get("commit") == "0cf2c6d56786eba3818a15199f8abd943e5f5e3d"
    return {"ok": all(checks.values()), "checks": checks}


def parse_dimacs() -> tuple[int, list[tuple[int, ...]]]:
    nvars = None
    expected_clauses = None
    clauses: list[tuple[int, ...]] = []
    for raw in (ROOT / SOURCE).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[:2] != ["p", "cnf"]:
                raise ValueError("BAD_DIMACS_HEADER")
            nvars, expected_clauses = int(parts[2]), int(parts[3])
            continue
        vals = [int(x) for x in line.split()]
        if not vals or vals[-1] != 0:
            raise ValueError("CLAUSE_MISSING_ZERO")
        clause = tuple(vals[:-1])
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError("NOT_STRICT_WIDTH3_DISTINCT_VARIABLES")
        clauses.append(clause)
    if nvars != 20 or expected_clauses != 91 or len(clauses) != 91:
        raise ValueError("DIMACS_COUNT_MISMATCH")
    if any(abs(lit) < 1 or abs(lit) > nvars for clause in clauses for lit in clause):
        raise ValueError("DIMACS_VARIABLE_OUT_OF_RANGE")
    return nvars, clauses


def source_semantic_sha(nvars: int, clauses: list[tuple[int, ...]]) -> str:
    obj = {"format": "DIMACS_CNF", "variables": nvars, "clauses": [list(c) for c in clauses]}
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def normalize(nvars: int, clauses: list[tuple[int, ...]]) -> dict:
    constraints = []
    for ordinal, clause in enumerate(clauses, 1):
        scope = sorted(abs(lit) for lit in clause)
        allowed = []
        for bits in itertools.product((0, 1), repeat=3):
            assignment = dict(zip(scope, bits, strict=True))
            satisfied = any((assignment[abs(lit)] == 1) if lit > 0 else (assignment[abs(lit)] == 0) for lit in clause)
            if satisfied:
                allowed.append(list(bits))
        constraints.append({"id": f"satlib_uf20_01_c{ordinal:03d}", "scope": scope, "allowed": allowed})
    return raw_basis.canonicalize_raw({"variables": list(range(1, nvars + 1)), "constraints": constraints})


def run() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "verdict": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}

    nvars, clauses = parse_dimacs()
    src_sha = source_semantic_sha(nvars, clauses)
    regenerated = normalize(nvars, clauses)
    stored = raw_basis.canonicalize_raw(json.loads((ROOT / RAW).read_text(encoding="utf-8")))
    raw_sha = hashlib.sha256(canonical_bytes(regenerated)).hexdigest()
    freeze = json.loads((ROOT / FREEZE).read_text(encoding="utf-8"))
    frozen23 = set(freeze["frozen_corpus_nonalias_guard"]["frozen_23_sha256"])

    e0 = {
        "source_semantic_sha256": src_sha,
        "expected_source_semantic_sha256": EXPECTED_SOURCE_SHA,
        "raw_sha256": raw_sha,
        "expected_raw_sha256": EXPECTED_RAW_SHA,
        "regenerated_equals_frozen_raw": regenerated == stored,
        "raw_nonalias_frozen_23": raw_sha not in frozen23,
        "full_variable_assignments_enumerated": 0,
    }
    if not (src_sha == EXPECTED_SOURCE_SHA and raw_sha == EXPECTED_RAW_SHA and regenerated == stored and raw_sha not in frozen23):
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "verdict": "HALT_E0_SOURCE_SEMANTIC_GUARD", "source_guard": guard, "E0": e0, "scientific_firewall": firewall()}

    elig = reference_census.eligibility(stored)
    if not elig.get("eligible"):
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "verdict": "HALT_E1_NOT_ELIGIBLE_CONNECTED_MIXED", "source_guard": guard, "E0": e0, "E1": elig, "scientific_firewall": firewall()}

    compositional = compositional_basis.induce_compositional_basis(stored)
    comp_rec = {
        "status": compositional.get("status"),
        "component_count": compositional.get("component_count"),
        "open_component_count": compositional.get("open_component_count"),
    }

    log_alien = reference_census.replay_log_alien(stored)
    if log_alien.get("closed"):
        win = log_alien.get("winning_attempt", {})
        verdict = "PASS_DIAGNOSTIC_NEW_SOURCE_CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER"
        outcome = {"mechanism": "SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER", "status": win.get("status")}
        orbit_rec = {"executed": False, "reason": "STOP_ON_FIRST_EXISTING_AUTHORITATIVE_CLOSURE"}
        obstruction = None
    else:
        orbit = orbit_candidate.run_candidate(stored)
        orbit_rec = {
            "executed": True,
            "status": orbit.get("status"),
            "solver_authority": orbit.get("solver_authority"),
            "raw_semantic_sha256": orbit.get("raw_semantic_sha256"),
            "cells": orbit.get("cells"),
            "quotient_states_Q": orbit.get("quotient_states_Q"),
            "resource_receipt": orbit.get("resource_receipt", {}),
            "certificate_type": (orbit.get("certificate") or {}).get("type"),
        }
        if orbit.get("status") in CLOSED_ORBIT and orbit.get("solver_authority") is True:
            verdict = "PASS_DIAGNOSTIC_NEW_SOURCE_CLOSED_BY_SEALED_ORBIT_COUNT_V1"
            outcome = {"mechanism": "EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT", "status": orbit.get("status")}
            obstruction = None
        else:
            verdict = "PASS_DIAGNOSTIC_FIRST_REAL_NEW_POST_PORTFOLIO_OBSTRUCTION_IDENTIFIED"
            outcome = {"mechanism": None, "status": "UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO"}
            obstruction = {
                "raw_sha256": raw_sha,
                "source": "SATLIB_UF20_01",
                "eligibility_class": elig.get("eligibility_class"),
                "log_alien_replay": log_alien,
                "orbit_replay": orbit_rec,
            }

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict,
        "source_guard": guard,
        "E0": e0,
        "E1": elig,
        "E2_compositional_replay": comp_rec,
        "E3_log_alien_replay": log_alien,
        "E4_orbit_replay": orbit_rec,
        "outcome": outcome,
        "first_real_post_portfolio_obstruction": obstruction,
        "resource_receipt": {
            "new_solver_mechanisms": 0,
            "new_carrier_mechanisms": 0,
            "new_representation_adapters_to_force_old_carriers": 0,
            "full_variable_cube_enumerations": 0,
            "separator_ge3_boolean_branches": 0,
            "size4_boolean_separator_assignments": 0,
            "new_unbounded_recursion": 0,
            "new_three_plus_join_chains": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raise": False,
        },
        "scientific_firewall": firewall(),
    }


def firewall() -> dict[str, Any]:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_FROM_THIS_DIAGNOSTIC_ALONE",
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
