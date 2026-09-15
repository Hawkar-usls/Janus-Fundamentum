from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as v310
from research.tools.apma_bucket_fixed_depth_122 import fixed_depth_122 as v314
from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as v316
from research.tools.apma_bucket_exact_two_factor_f_factor_carrier import carrier as v318

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-GT2-UNADMITTED-RAW-OBSTRUCTION-CENSUS-2026-09-16-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_NEW_SOLVER_OR_SEPARATOR_AUTHORITY"
PASS_FOUND = "PASS_DIAGNOSTIC_GT2_CENSUS_WITH_FIRST_UNADMITTED_RAW_OBSTRUCTION"
PASS_NONE = "PASS_DIAGNOSTIC_NO_FROZEN_RAW_UNADMITTED_GT2_OBSTRUCTION_FOUND"
FAIL = "FAIL_DIAGNOSTIC_SOURCE_OR_CLASSIFICATION_MISMATCH"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_GT2_UNADMITTED_RAW_OBSTRUCTION_CENSUS_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "e6571f439dc15c8ac5be9882ceab854b659cf39f"
CLARIFICATION = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_GT2_UNADMITTED_RAW_OBSTRUCTION_CENSUS_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CLARIFICATION_BLOB = "945b2324a19a85a8f3ce7615aa023777b17bfd19"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-16_v3.18.json")
PARENT_BLOB = "a932adfe4167e227c65d1e92043efff466224b0e"
SOURCES = {
    Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py"): "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8",
    Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py"): "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0",
    Path("research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py"): "0853ebb9a3e273fdaeca172dbe2502cc7214cf61",
    Path("research/tools/apma_bucket_fixed_depth_122/fixed_depth_122.py"): "2e02bac1d78b751d22df2c50a01980ae06bd2751",
    Path("research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py"): "4128f0db77dfc1391b6ec539f201250bfb3d8b6e",
    Path("research/tools/apma_bucket_exact_two_factor_f_factor_carrier/carrier.py"): "21c66961f9ce809e7af824c8b0892f2e017463d9",
}


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "clarification_blob": git_blob(r / CLARIFICATION) == CLARIFICATION_BLOB,
        "parent_v3_18_blob": git_blob(r / PARENT) == PARENT_BLOB,
    }
    for p, expected in SOURCES.items():
        checks[str(p)] = git_blob(r / p) == expected
    return {"ok": all(checks.values()), "checks": checks}


def sha256_obj(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def canonical_raw_sha(raw: dict) -> str:
    return sha256_obj(raw_basis.canonicalize_raw(raw))


def fixtures() -> list[dict[str, Any]]:
    return [
        {"name": "V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", "raw": v36.residual_component_gt2_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL", "eligible": True},
        {"name": "V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", "raw": v38.no_single_variable_articulation_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL", "eligible": True},
        {"name": "V3_8_BRANCH_STILL_GT2_CONTROL", "raw": v38.branch_still_gt2_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL", "eligible": True},
        {"name": "V3_10_NO_PAIR_K4_CONTROL", "raw": v310.no_pair_k4_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL", "eligible": True},
        {"name": "V3_14_POSITIVE_K4_CONTROL", "raw": v314.positive_k4_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL_ALIAS", "eligible": True},
        {"name": "V3_16_RAW_K5_FULL_CUBE", "raw": v316.build_raw_k5("FULL_CUBE"), "class": "REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBE", "eligible": True},
        {"name": "V3_16_RAW_K5_EXACT_2_OF_4", "raw": v316.build_raw_k5("EXACT_2_OF_4"), "class": "REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBE", "eligible": True},
    ]


def is_exact_closure(status: str) -> bool:
    return status.startswith("ADMIT_EXACT_") or status.startswith("EXACT_UNSAT_")


def factor_fingerprint(f: dict, core: list[int]) -> dict[str, Any]:
    scope, rows = v316.residual_relation(f, core)
    sem = v316.factor_semantics(f, core)
    return {
        "factor_id": str(f["id"]),
        "residual_scope": [int(v) for v in scope],
        "residual_arity": len(scope),
        "tuple_count": len(rows),
        "universal": bool(sem["universal"]),
        "relation_sha256": sem["relation_sha256"],
        "fingerprint": sem["fingerprint"],
    }


def exact_two_factor_component_result(factors: list[dict], core: list[int], comp: list[int]) -> dict[str, Any]:
    scopes: dict[str, list[int]] = {}
    rows: dict[str, set[tuple[int, ...]]] = {}
    for i in comp:
        f = factors[i]
        scope, rel_rows = v316.residual_relation(f, core)
        scopes[str(f["id"])] = [int(v) for v in scope]
        rows[str(f["id"])] = {tuple(int(x) for x in r) for r in rel_rows}
    model = v318.recognize_component(scopes, rows, {"kind": "GT2_CENSUS_COMPONENT", "factor_ids": sorted(scopes)})
    if model.get("status") != "READY_EXACT_TWO_FACTOR_COMPONENT":
        return {"recognized": False, "recognition_status": model.get("status")}
    solved = v318.solve_model(model)
    exact = solved.get("status") in {"EXACT_SAT_TWO_FACTOR", "EXACT_UNSAT_TUTTE_BARRIER", "EXACT_UNSAT_LOCAL_DEGREE_LT_TWO"} and solved.get("certificate_verified") is True
    return {
        "recognized": True,
        "recognition_status": model.get("status"),
        "solve_status": solved.get("status"),
        "certificate_verified": solved.get("certificate_verified"),
        "exact_closed": exact,
        "matching_calls": int(solved.get("matching_calls", 0)),
    }


def classify_raw(raw: dict) -> dict[str, Any]:
    raw_sha = canonical_raw_sha(raw)
    prep = v38._prepare(raw)
    out: dict[str, Any] = {"raw_sha256": raw_sha, "prepare_status": prep.get("status")}
    if prep.get("status") != "READY":
        out["classification"] = "PREDECESSOR_NONREADY__NOT_A_RAW_GT2_OBSTRUCTION"
        return out

    factors = prep["conditioned"]
    core = [int(v) for v in prep["core"]]
    before_components = v316.components(factors, core)
    before_gt2 = [c for c in before_components if len(c) > 2]
    out["common_core"] = core
    out["residual_component_sizes_before_normalization"] = [len(c) for c in before_components]
    if not before_gt2:
        out["classification"] = "OUT_OF_SCOPE_NO_GT2"
        return out

    norm = v316.exact_universal_normalize(factors, core)
    normalized_factors = norm["kept"]
    after_components = v316.components(normalized_factors, core) if normalized_factors else []
    after_gt2 = [c for c in after_components if len(c) > 2]
    out["universal_normalization"] = {
        "removed_factor_ids": norm["removed_factor_ids"],
        "residual_component_sizes_after": [len(c) for c in after_components],
    }
    if not after_gt2:
        out["classification"] = "CLOSED_BY_EXACT_UNIVERSAL_NORMALIZATION"
        out["closing_mechanism"] = "V3_16_EXACT_UNIVERSAL_RESIDUAL_RELATION_NORMALIZATION"
        return out

    replay = []
    for mechanism, fn in [
        ("V3_6_RESIDUAL_COMPONENT_LE2", v36.build),
        ("V3_8_SINGLE_VARIABLE_SEPARATOR", v38.build),
        ("V3_10_TWO_VARIABLE_SEPARATOR", v310.build),
        ("V3_14_FIXED_DEPTH_1_TO_2_TO_2", v314.build),
    ]:
        result = fn(raw)
        status = str(result.get("status"))
        replay.append({"mechanism": mechanism, "status": status})
        if is_exact_closure(status):
            out["sealed_portfolio_replay"] = replay
            out["classification"] = "CLOSED_BY_SEALED_RAW_CARRIER"
            out["closing_mechanism"] = mechanism
            out["closing_status"] = status
            return out
    out["sealed_portfolio_replay"] = replay

    two_factor_receipts = []
    all_two_factor_closed = True
    for comp in after_gt2:
        rec = exact_two_factor_component_result(normalized_factors, core, comp)
        rec["component_factor_ids"] = sorted(str(normalized_factors[i]["id"]) for i in comp)
        rec["component_size"] = len(comp)
        two_factor_receipts.append(rec)
        if not rec.get("exact_closed"):
            all_two_factor_closed = False
    out["v3_18_two_factor_components"] = two_factor_receipts
    if all_two_factor_closed and two_factor_receipts:
        out["classification"] = "CLOSED_BY_SEALED_V3_18_EXACT_TWO_FACTOR_COMPONENT_CARRIER"
        out["closing_mechanism"] = "V3_18_EXACT_TWO_FACTOR_COMPONENT_CARRIER"
        return out

    unresolved = []
    for comp, tf in zip(after_gt2, two_factor_receipts):
        if tf.get("exact_closed"):
            continue
        unresolved.append({
            "factor_ids": sorted(str(normalized_factors[i]["id"]) for i in comp),
            "factor_count": len(comp),
            "factors": [factor_fingerprint(normalized_factors[i], core) for i in comp],
            "two_factor_recognition_status": tf.get("recognition_status"),
        })
    out["classification"] = "OPEN_AFTER_ALL_SEALED_CARRIERS"
    out["unresolved_gt2_components"] = unresolved
    return out


def profile() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "verdict": FAIL, "source_guard": guard}

    rows = []
    by_sha: dict[str, dict[str, Any]] = {}
    for fixture in fixtures():
        classification = classify_raw(fixture["raw"])
        row = {"name": fixture["name"], "class": fixture["class"], "eligible_for_first_real_obstruction": fixture["eligible"], **classification}
        rows.append(row)
        sha = classification["raw_sha256"]
        if sha not in by_sha:
            by_sha[sha] = {"raw_sha256": sha, "aliases": [], "representative": row}
        by_sha[sha]["aliases"].append(fixture["name"])

    unique_rows = []
    for sha, group in by_sha.items():
        rep = dict(group["representative"])
        rep["aliases"] = group["aliases"]
        unique_rows.append(rep)

    unit = v314.depth_cap_unit_control()
    unit_calibration = {
        "name": "V3_14_UNIT_ONLY_K5_DEPTH_CAP_CONTROL",
        "status": unit.get("status"),
        "unit_test_only": unit.get("unit_test_only"),
        "raw_reachability_authority": unit.get("raw_reachability_authority"),
        "eligible_for_first_real_obstruction": False,
    }

    unadmitted = [r for r in unique_rows if r.get("eligible_for_first_real_obstruction") and r.get("classification") == "OPEN_AFTER_ALL_SEALED_CARRIERS"]
    first = unadmitted[0] if unadmitted else None
    verdict = PASS_FOUND if first is not None else PASS_NONE

    counts: dict[str, int] = {}
    for r in unique_rows:
        counts[r["classification"]] = counts.get(r["classification"], 0) + 1

    checks = {
        "source_guard": guard["ok"],
        "unit_k5_excluded_from_real_raw_obstruction": unit_calibration["unit_test_only"] is True and unit_calibration["raw_reachability_authority"] is False and unit_calibration["eligible_for_first_real_obstruction"] is False,
        "v3_14_positive_k4_deduplicates_with_v3_10_no_pair_k4": any(set(r["aliases"]) == {"V3_10_NO_PAIR_K4_CONTROL", "V3_14_POSITIVE_K4_CONTROL"} for r in unique_rows),
        "full_cube_k5_closed_by_universal_normalization": any(r["name"] == "V3_16_RAW_K5_FULL_CUBE" and r["classification"] == "CLOSED_BY_EXACT_UNIVERSAL_NORMALIZATION" for r in rows),
        "exact_two_of_four_k5_closed_by_v3_18": any(r["name"] == "V3_16_RAW_K5_EXACT_2_OF_4" and r["classification"] == "CLOSED_BY_SEALED_V3_18_EXACT_TWO_FACTOR_COMPONENT_CARRIER" for r in rows),
        "all_unique_raw_inputs_have_classification": all(bool(r.get("classification")) for r in unique_rows),
    }
    if not all(checks.values()):
        verdict = FAIL

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict,
        "source_guard": guard,
        "checks": checks,
        "fixture_rows": rows,
        "unique_raw_census": unique_rows,
        "unique_raw_count": len(unique_rows),
        "classification_counts": counts,
        "unadmitted_raw_obstruction_count": len(unadmitted),
        "first_real_raw_obstruction": first,
        "unit_only_calibration": unit_calibration,
        "captain_obvious": {
            "if_none_found": "DO_NOT_CLAIM_GENERAL_GT2_SOLVED__SHIFT_TO_OPEN_NONUNIQUE_COMMON_CORE_SUPPORT_OR_ACQUIRE_NEW_RAW_PREDECESSOR_EVIDENCE",
            "if_found": "FREEZE_THE_FIRST_RAW_OBSTRUCTION_BEFORE_ANY_NEW_MECHANISM_DESIGN",
        },
        "resource_receipt": {
            "new_solver_mechanisms": 0,
            "new_boolean_branching_mechanisms": 0,
            "new_unbounded_recursion": 0,
            "new_join_chains": 0,
            "new_global_cartesian_products": 0,
            "replays_existing_sealed_carriers_only": True,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT": "OPEN",
            "SIZE4_BRANCHING_LICENSED": False,
            "EXTRA_RECURSION_AUTHORIZED": False,
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


if __name__ == "__main__":
    print(json.dumps(profile(), ensure_ascii=False, sort_keys=True))
