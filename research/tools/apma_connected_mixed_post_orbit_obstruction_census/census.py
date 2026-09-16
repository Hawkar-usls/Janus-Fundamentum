from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_bucket_raw_predecessor_nonunique_reachability_acquisition_census import census as source_registry
from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_log_alien_transfer import log_alien_transfer
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate

ARTIFACT_ID = "JANUS-TRUMP-SOURCE-AUTHORIZED-CONNECTED-MIXED-RAW-POST-ORBIT-PORTFOLIO-OBSTRUCTION-CENSUS-2026-09-16-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__EVIDENCE_LOCALIZATION_BEFORE_NEW_MECHANISM_DESIGN"
PASS_FOUND = "PASS_DIAGNOSTIC_FIRST_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FROZEN"
PASS_NONE = "PASS_DIAGNOSTIC_NO_CURRENT_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FOUND"
FAIL_SOURCE = "FAIL_DIAGNOSTIC_SOURCE_PROVENANCE_OR_PORTFOLIO_BINDING_INCOMPLETE"

PREREG = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "d5742ab49067f8d842bb8d805254b7cbba6e3f10"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-16_v3.22.json")
PARENT_STATE_BLOB = "a8cd4e3fe62f4db59cbd43588b877ecfca4c7517"
SOURCE_REGISTRY = Path("research/tools/apma_bucket_raw_predecessor_nonunique_reachability_acquisition_census/census.py")
SOURCE_REGISTRY_BLOB = "0886fe4b41652e52f76e862a752acab0832a5302"
RAW_BASIS = Path("research/tools/apma_unseen_basis/raw_relation_basis.py")
RAW_BASIS_BLOB = "63490c05ef3e91a4f682f75da26ff2af811839a6"
COMPOSITIONAL = Path("research/tools/apma_unseen_basis/compositional_basis.py")
COMPOSITIONAL_BLOB = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"
LOG_ALIEN = Path("research/tools/apma_log_alien_transfer/log_alien_transfer.py")
LOG_ALIEN_BLOB = "d20cd94fa2e0324e301f55211152c2d410099425"
ORBIT = Path("research/tools/apma_unseen_local_invariant_orbit_count/candidate.py")
ORBIT_BLOB = "a076cfc56d68aad0348415e313705da1f6b9cdcd"
PRIOR_CLOSURE = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_GT2_UNADMITTED_RAW_OBSTRUCTION_CENSUS_RESULT_2026-09-16.json")
PRIOR_CLOSURE_BLOB = "df02fe97ac99c6d930c186680f9440c826c570ee"

SCHAEFER_NAMES = ("ZERO_VALID", "ONE_VALID", "HORN", "DUAL_HORN", "BIJUNCTIVE", "AFFINE")
OR2_KEY = (2, ("01", "10", "11"))
EVEN_XOR3_KEY = (3, ("000", "011", "101", "110"))


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def source_guard() -> dict[str, Any]:
    r = root()
    expected = {
        PREREG: PREREG_BLOB,
        PARENT_STATE: PARENT_STATE_BLOB,
        SOURCE_REGISTRY: SOURCE_REGISTRY_BLOB,
        RAW_BASIS: RAW_BASIS_BLOB,
        COMPOSITIONAL: COMPOSITIONAL_BLOB,
        LOG_ALIEN: LOG_ALIEN_BLOB,
        ORBIT: ORBIT_BLOB,
        PRIOR_CLOSURE: PRIOR_CLOSURE_BLOB,
    }
    checks = {str(path): git_blob_sha1(r / path) == blob for path, blob in expected.items()}
    inherited = source_registry.source_guard()
    checks["inherited_26_entry_source_registry_guard"] = bool(inherited.get("ok"))
    return {"ok": all(checks.values()), "checks": checks, "inherited": inherited}


def canonical_raw(raw: dict) -> dict:
    return raw_basis.canonicalize_raw(raw)


def raw_sha256(raw: dict) -> str:
    return hashlib.sha256(canonical_bytes(canonical_raw(raw))).hexdigest()


def relation_key(row: dict) -> tuple[int, tuple[str, ...]]:
    return int(row["arity"]), tuple(str(x) for x in row["allowed"])


def eligibility(raw: dict) -> dict[str, Any]:
    canonical = canonical_raw(raw)
    groups = compositional_basis.canonical_constraint_components(canonical)
    surface = raw_basis.relation_surface(canonical)
    per_relation = raw_basis.classify_each(surface)
    global_fp = raw_basis.classify_language(raw_basis.surface_to_relations(surface))
    locally_admissible = [
        any(bool(row["fingerprint"].get(name)) for name in SCHAEFER_NAMES)
        for row in per_relation
    ]
    candidate_bases = [name for name in SCHAEFER_NAMES if global_fp.get(name)]
    connected = len(groups) == 1
    every_local = bool(per_relation) and all(locally_admissible)
    no_global = len(candidate_bases) == 0
    eligible = connected and every_local and no_global
    if not connected:
        cls = "OUT_OF_SCOPE_NOT_CONNECTED"
    elif not every_local:
        cls = "OUT_OF_SCOPE_INTRINSICALLY_NON_SCHAEFER_RELATION_PRESENT"
    elif not no_global:
        cls = "OUT_OF_SCOPE_SINGLE_GLOBAL_SCHAEFER_BASIS"
    else:
        cls = "ELIGIBLE_CONNECTED_MIXED"
    return {
        "eligible": eligible,
        "eligibility_class": cls,
        "incidence_component_count": len(groups),
        "relation_surface": surface,
        "per_relation_fingerprint": per_relation,
        "global_language_fingerprint": global_fp,
        "global_candidate_bases": candidate_bases,
    }


def prior_closure_sets() -> dict[str, set[str]]:
    data = json.loads((root() / PRIOR_CLOSURE).read_text(encoding="utf-8"))
    receipt = data["machine_receipt"]
    return {
        "normalization": set(receipt.get("closed_by_universal_normalization", [])),
        "two_factor": set(receipt.get("closed_by_v3_18_two_factor", [])),
    }


def prior_closure(aliases: list[str], sets: dict[str, set[str]]) -> dict[str, Any] | None:
    for alias in aliases:
        if alias in sets["normalization"]:
            return {"mechanism": "EXACT_PRIOR_RAW_SHA_RECEIPT__UNIVERSAL_NORMALIZATION", "alias": alias}
        if alias in sets["two_factor"]:
            return {"mechanism": "EXACT_PRIOR_RAW_SHA_RECEIPT__V3_18_TWO_FACTOR", "alias": alias}
    return None


def _canonical_relation_key_from_constraint(row: dict) -> tuple[int, tuple[str, ...]]:
    words = tuple(sorted("".join(str(int(b)) for b in t) for t in row["allowed"]))
    return len(row["scope"]), words


def log_alien_instance(canonical: dict, base_key: tuple[int, tuple[str, ...]], alien_key: tuple[int, tuple[str, ...]]) -> dict | None:
    base = []
    aliens = []
    for row in canonical["constraints"]:
        key = _canonical_relation_key_from_constraint(row)
        rec = {"id": str(row["id"]), "scope": [int(v) for v in row["scope"]]}
        if key == base_key:
            rec["kind"] = "OR2" if base_key == OR2_KEY else "EVEN_XOR3"
            base.append(rec)
        elif key == alien_key:
            rec["kind"] = "OR2" if alien_key == OR2_KEY else "EVEN_XOR3"
            aliens.append(rec)
        else:
            return None
    if not base or not aliens:
        return None
    return {
        "L": len(canonical_bytes(canonical)),
        "base_kind": "OR2" if base_key == OR2_KEY else "EVEN_XOR3",
        "alien_kind": "OR2" if alien_key == OR2_KEY else "EVEN_XOR3",
        "base_constraints": base,
        "alien_constraints": aliens,
    }


def replay_log_alien(canonical: dict) -> dict[str, Any]:
    surface_keys = {relation_key(row) for row in raw_basis.relation_surface(canonical)}
    if surface_keys != {OR2_KEY, EVEN_XOR3_KEY}:
        return {"applicable": False, "reason": "RELATION_SURFACE_NOT_EXACTLY_OR2_PLUS_EVEN_XOR3"}
    attempts = []
    for base_key, alien_key in ((OR2_KEY, EVEN_XOR3_KEY), (EVEN_XOR3_KEY, OR2_KEY)):
        instance = log_alien_instance(canonical, base_key, alien_key)
        if instance is None:
            continue
        result = log_alien_transfer.solve_instance(instance)
        attempts.append({
            "base_kind": instance["base_kind"],
            "alien_kind": instance["alien_kind"],
            "status": result.get("status"),
            "L": result.get("L", instance["L"]),
            "k": result.get("k", len(instance["alien_constraints"])),
            "q": result.get("q"),
            "q_pow_k": result.get("q_pow_k"),
            "metrics": result.get("metrics", {}),
        })
        if result.get("status") in {"SAT", "UNSAT"}:
            return {"applicable": True, "closed": True, "winning_attempt": attempts[-1], "attempts": attempts}
    return {"applicable": True, "closed": False, "attempts": attempts}


def dedup_source_entries() -> list[dict[str, Any]]:
    entries = source_registry.fixture_defs()
    if len(entries) != 26:
        raise RuntimeError(f"FROZEN_SOURCE_ENTRY_COUNT_MISMATCH:{len(entries)}")
    by_sha: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for entry in entries:
        sha = raw_sha256(entry["raw"])
        if sha not in by_sha:
            canonical = canonical_raw(entry["raw"])
            by_sha[sha] = {
                "first_ordinal": int(entry["ordinal"]),
                "raw_sha256": sha,
                "canonical_raw": canonical,
                "aliases": [],
                "source_classes": [],
                "constructors": [],
                "canonical_json_bytes": len(canonical_bytes(canonical)),
            }
            order.append(sha)
        rec = by_sha[sha]
        rec["aliases"].append(str(entry["name"]))
        rec["source_classes"].append(str(entry["source_class"]))
        rec["constructors"].append(str(entry["constructor"]))
    return [by_sha[sha] for sha in order]


def run_census() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "verdict": FAIL_SOURCE, "source_guard": guard, "scientific_firewall": firewall()}

    unique = dedup_source_entries()
    closure_sets = prior_closure_sets()
    rows = []
    first_obstruction = None
    eligible_count = 0
    classification_counts: dict[str, int] = {}

    for rec in unique:
        raw = rec["canonical_raw"]
        elig = eligibility(raw)
        row = {k: v for k, v in rec.items() if k != "canonical_raw"}
        row["eligibility"] = elig
        if not elig["eligible"]:
            classification = elig["eligibility_class"]
            row["classification"] = classification
            classification_counts[classification] = classification_counts.get(classification, 0) + 1
            rows.append(row)
            continue

        eligible_count += 1
        prior = prior_closure(rec["aliases"], closure_sets)
        compositional = compositional_basis.induce_compositional_basis(raw)
        row["compositional_replay"] = {
            "status": compositional.get("status"),
            "component_count": compositional.get("component_count"),
            "open_component_count": compositional.get("open_component_count"),
        }
        row["factorized_feedback_replay"] = "REGRESSION_ONLY__NO_SEALED_RAW_OBJECT_TO_FEEDBACK_OBLIGATION_BINDING"

        if prior is not None:
            row["prior_exact_closure"] = prior
            classification = "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_EXACT_PRIOR_RAW_SHA_RECEIPT"
        else:
            log_alien = replay_log_alien(raw)
            row["log_alien_replay"] = log_alien
            if log_alien.get("closed"):
                classification = "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER"
            else:
                orbit = orbit_candidate.run_candidate(raw)
                row["orbit_replay"] = {
                    "status": orbit.get("status"),
                    "solver_authority": orbit.get("solver_authority"),
                    "raw_semantic_sha256": orbit.get("raw_semantic_sha256"),
                    "cells": orbit.get("cells"),
                    "quotient_states_Q": orbit.get("quotient_states_Q"),
                    "resource_receipt": orbit.get("resource_receipt", {}),
                    "certificate_type": (orbit.get("certificate") or {}).get("type"),
                }
                if orbit.get("status") in {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"} and orbit.get("solver_authority") is True:
                    classification = "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_SEALED_ORBIT_COUNT_V1"
                else:
                    classification = "ELIGIBLE_CONNECTED_MIXED_UNADMITTED_POST_ORBIT_PORTFOLIO_OBSTRUCTION"
                    first_obstruction = {
                        "raw_sha256": rec["raw_sha256"],
                        "first_ordinal": rec["first_ordinal"],
                        "aliases": rec["aliases"],
                        "source_classes": rec["source_classes"],
                        "constructors": rec["constructors"],
                        "canonical_raw": raw,
                        "eligibility": elig,
                        "log_alien_replay": log_alien,
                        "orbit_replay": row.get("orbit_replay"),
                    }
        row["classification"] = classification
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        rows.append(row)
        if first_obstruction is not None:
            break

    verdict = PASS_FOUND if first_obstruction is not None else PASS_NONE
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict,
        "source_guard": guard,
        "constructor_entry_count": 26,
        "unique_raw_count": len(unique),
        "rows_evaluated_before_stop": len(rows),
        "eligible_connected_mixed_count_before_stop": eligible_count,
        "classification_counts": classification_counts,
        "first_real_post_orbit_obstruction": first_obstruction,
        "rows": rows,
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
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_FROM_THIS_DIAGNOSTIC_ALONE",
    }


def main() -> None:
    print(json.dumps(run_census(), sort_keys=True))


if __name__ == "__main__":
    main()
