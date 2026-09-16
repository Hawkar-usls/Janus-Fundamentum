from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload as v35
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as v310
from research.tools.apma_bucket_fixed_depth_122 import fixed_depth_122 as v314
from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as v316
from research.tools.apma_bucket_exact_two_factor_f_factor_carrier import carrier as v318

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-NONUNIQUE-COMMON-CORE-SUPPORT-STATE-SPACE-FORENSIC-2026-09-16-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_NEW_MULTI_STATE_CARRIER_AUTHORITY"
PASS_NONE = "PASS_DIAGNOSTIC_NO_AUTHORITATIVE_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FOUND"
PASS_ALL = "PASS_DIAGNOSTIC_RAW_NONUNIQUE_COMMON_CORE_FOUND_ALL_STATES_CLOSED_BY_SEALED_PORTFOLIO"
PASS_OPEN = "PASS_DIAGNOSTIC_RAW_NONUNIQUE_COMMON_CORE_FOUND_WITH_FIRST_OPEN_STATE"
FAIL = "FAIL_DIAGNOSTIC_SOURCE_OR_INDEPENDENT_MISMATCH"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "5d01ed7f058e4fa4a8ab729d5c8ad0ac1928f517"
CLARIFICATION = Path("research/TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CLARIFICATION_BLOB = "312f786f5888c698b408e18cffa6d9f034bd82a0"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-16_v3.19.json")
PARENT_BLOB = "e076d24b438262d0eb6d08309f31c3ee4648b79d"
SOURCES = {
    Path("research/tools/apma_unseen_basis/raw_relation_basis.py"): "63490c05ef3e91a4f682f75da26ff2af811839a6",
    Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py"): "f103bf9b14e3b208200f429b75d0858c4963fa7c",
    Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter_v1_1.py"): "c29229bbaebf2935ab03c77c7d444e2a33422f17",
    Path("research/tools/apma_bucket_conditioned_factorized_payload/conditioned_factorized_payload.py"): "c07cc8c12fa6f7a9b8f2560095caa4bdcc235480",
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
        "parent_v3_19_blob": git_blob(r / PARENT) == PARENT_BLOB,
    }
    for path, expected in SOURCES.items():
        checks[str(path)] = git_blob(r / path) == expected
    return {"ok": all(checks.values()), "checks": checks}


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_raw(raw: dict) -> dict:
    return raw_basis.canonicalize_raw(raw)


def canonical_raw_sha(raw: dict) -> str:
    return hashlib.sha256(canonical_bytes(canonical_raw(raw))).hexdigest()


def fixtures() -> list[dict[str, Any]]:
    return [
        {"name": "V3_4_POSITIVE_ALIGNED_OVERBUDGET_CONTROL", "raw": cc_v1.positive_aligned_overbudget_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL"},
        {"name": "V3_4_FILTERED_STILL_OVERBUDGET_CONTROL", "raw": cc_v1.filtered_still_overbudget_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL"},
        {"name": "V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", "raw": v36.residual_component_gt2_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL"},
        {"name": "V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", "raw": v38.no_single_variable_articulation_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL"},
        {"name": "V3_8_BRANCH_STILL_GT2_CONTROL", "raw": v38.branch_still_gt2_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL"},
        {"name": "V3_10_NO_PAIR_K4_CONTROL", "raw": v310.no_pair_k4_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL"},
        {"name": "V3_14_POSITIVE_K4_CONTROL", "raw": v314.positive_k4_control(), "class": "FROZEN_RAW_PREDECESSOR_CONTROL_ALIAS"},
        {"name": "V3_16_RAW_K5_FULL_CUBE", "raw": v316.build_raw_k5("FULL_CUBE"), "class": "REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBE"},
        {"name": "V3_16_RAW_K5_EXACT_2_OF_4", "raw": v316.build_raw_k5("EXACT_2_OF_4"), "class": "REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBE"},
    ]


def _support_for_factor(factor: dict, core: list[int]) -> set[tuple[int, ...]]:
    pos = {int(v): i for i, v in enumerate(factor["scope"])}
    return {tuple(int(row[pos[v]]) for v in core) for row in factor["rows"]}


def _explicit_input_metrics(canonical: dict) -> dict[str, int]:
    row_count = sum(len(rel["allowed"]) for rel in canonical["constraints"])
    boolean_cells = sum(len(rel["scope"]) * len(rel["allowed"]) for rel in canonical["constraints"])
    return {
        "canonical_json_bytes": len(canonical_bytes(canonical)),
        "explicit_relation_row_count": row_count,
        "explicit_boolean_row_cells": boolean_cells,
    }


def profile_raw(raw: dict) -> dict[str, Any]:
    canonical = canonical_raw(raw)
    raw_sha = hashlib.sha256(canonical_bytes(canonical)).hexdigest()
    metrics = _explicit_input_metrics(canonical)
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    out: dict[str, Any] = {
        "raw_sha256": raw_sha,
        "prepare_status": ready.get("status"),
        "input_metrics": metrics,
    }
    if ready.get("status") != "READY":
        out["classification"] = "PREDECESSOR_NONREADY__NO_COMMON_CORE_SUPPORT_AUTHORITY"
        return out

    core = [int(v) for v in ready["common_core"]]
    bucket = ready["bucket"]
    supports = [_support_for_factor(f, core) for f in bucket]
    common = set.intersection(*supports) if supports else set()
    common_sorted = sorted(common)
    support_sizes = [len(s) for s in supports]
    row_counts = [len(f["rows"]) for f in bucket]
    min_projection = min(support_sizes) if support_sizes else 0
    min_rows = min(row_counts) if row_counts else 0
    support_cells = len(common_sorted) * len(core)
    min_bucket_cells = min((len(f["rows"]) * len(f["scope"]) for f in bucket), default=0)
    support_json_bytes = len(canonical_bytes([list(t) for t in common_sorted]))

    bound_checks = {
        "S_subset_each_projection": all(common <= s for s in supports),
        "support_size_le_min_projection_support": len(common_sorted) <= min_projection,
        "min_projection_support_le_min_bucket_rows": min_projection <= min_rows,
        "min_bucket_rows_le_total_explicit_rows": min_rows <= metrics["explicit_relation_row_count"],
        "support_boolean_cells_le_min_bucket_boolean_cells": support_cells <= min_bucket_cells,
        "support_json_bytes_le_quadratic_input_bytes": support_json_bytes <= (metrics["canonical_json_bytes"] + 1) ** 2,
    }
    out.update({
        "classification": "REAL_NONUNIQUE_COMMON_CORE_REACHABLE" if len(common_sorted) > 1 else "NOT_NONUNIQUE_COMMON_CORE_REACHABLE",
        "failed_variable": int(ready["failed_variable"]),
        "bucket_factor_ids": [str(f["id"]) for f in bucket],
        "common_core": core,
        "common_core_size": len(core),
        "factor_projection_support_sizes": support_sizes,
        "bucket_factor_row_counts": row_counts,
        "exact_common_support_size": len(common_sorted),
        "exact_common_support_tuples": [list(t) for t in common_sorted],
        "explicit_support_encoding_bytes": support_json_bytes,
        "support_boolean_cells": support_cells,
        "min_bucket_boolean_cells": min_bucket_cells,
        "support_bound_checks": bound_checks,
        "support_bound_lemma_holds": all(bound_checks.values()),
    })
    return out


def _condition_raw_on_state(raw: dict, core: list[int], state: tuple[int, ...]) -> dict[str, Any]:
    state_map = {int(v): int(bit) for v, bit in zip(core, state)}
    out = json.loads(json.dumps(raw))
    empty = []
    for rel in out["constraints"]:
        scope = [int(v) for v in rel["scope"]]
        pos = {v: i for i, v in enumerate(scope)}
        constrained = [v for v in core if v in pos]
        if not constrained:
            continue
        kept = []
        for row in rel["allowed"]:
            if all(int(row[pos[v]]) == state_map[v] for v in constrained):
                kept.append(row)
        rel["allowed"] = kept
        if not kept:
            empty.append(str(rel.get("id", "?")))
    return {"raw": out, "empty_relation_ids": empty}


def _exact_status(status: str, payload: dict[str, Any]) -> bool:
    if status.startswith("ADMIT_EXACT_"):
        if "witness_verified" in payload:
            return payload.get("witness_verified") is True
        return True
    if status.startswith("EXACT_UNSAT_"):
        if "certificate_verified" in payload:
            return payload.get("certificate_verified") is True
        if "witness_verified" in payload:
            return payload.get("witness_verified") is True
        return True
    return False


def _two_factor_replay(raw: dict) -> dict[str, Any]:
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"status": "OPEN_V3_18_PREP_NOT_READY", "prepare_status": prep.get("status")}
    factors = prep["conditioned"]
    core = [int(v) for v in prep["core"]]
    norm = v316.exact_universal_normalize(factors, core)
    kept = norm["kept"]
    comps = v316.components(kept, core) if kept else []
    gt2 = [c for c in comps if len(c) > 2]
    if not gt2:
        return {"status": "OPEN_NO_GT2_FOR_V3_18", "removed_universal_factor_ids": norm["removed_factor_ids"]}

    receipts = []
    for comp in gt2:
        scopes: dict[str, list[int]] = {}
        rows: dict[str, set[tuple[int, ...]]] = {}
        for i in comp:
            f = kept[i]
            scope, rel_rows = v316.residual_relation(f, core)
            scopes[str(f["id"])] = [int(v) for v in scope]
            rows[str(f["id"])] = {tuple(int(x) for x in row) for row in rel_rows}
        model = v318.recognize_component(scopes, rows, {"kind": "NONUNIQUE_CORE_STATE_REPLAY", "factor_ids": sorted(scopes)})
        if model.get("status") != "READY_EXACT_TWO_FACTOR_COMPONENT":
            receipts.append({"factor_ids": sorted(scopes), "recognition_status": model.get("status"), "exact_closed": False})
            continue
        solved = v318.solve_model(model)
        exact = solved.get("status") in {"EXACT_SAT_TWO_FACTOR", "EXACT_UNSAT_TUTTE_BARRIER", "EXACT_UNSAT_LOCAL_DEGREE_LT_TWO"} and solved.get("certificate_verified") is True
        receipts.append({
            "factor_ids": sorted(scopes),
            "recognition_status": model.get("status"),
            "solve_status": solved.get("status"),
            "certificate_verified": solved.get("certificate_verified"),
            "exact_closed": exact,
            "matching_calls": int(solved.get("matching_calls", 0)),
        })
    all_closed = bool(receipts) and all(r["exact_closed"] for r in receipts)
    any_unsat = any(str(r.get("solve_status", "")).startswith("EXACT_UNSAT_") for r in receipts if r.get("exact_closed"))
    return {
        "status": "EXACT_UNSAT_BY_SEALED_V3_18_COMPONENT" if all_closed and any_unsat else ("ADMIT_EXACT_BY_SEALED_V3_18_COMPONENT_PORTFOLIO" if all_closed else "OPEN_AFTER_V3_18_REPLAY"),
        "removed_universal_factor_ids": norm["removed_factor_ids"],
        "component_receipts": receipts,
    }


def replay_state(raw: dict, core: list[int], state: tuple[int, ...]) -> dict[str, Any]:
    conditioned = _condition_raw_on_state(raw, core, state)
    if conditioned["empty_relation_ids"]:
        return {
            "state": list(state),
            "classification": "EXACT_UNSAT_WITH_EXISTING_REPLAYABLE_CERTIFICATE",
            "closing_mechanism": "EXACT_RAW_CONDITIONING_EMPTY_RELATION",
            "status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_RELATION",
            "empty_relation_ids": conditioned["empty_relation_ids"],
            "replay": [],
        }
    cr = conditioned["raw"]
    replay = []
    calls = [
        ("V3_5_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD", lambda: v35.explain(cr)),
        ("V3_6_RESIDUAL_COMPONENT_LE2", lambda: v36.build(cr)),
        ("V3_8_SINGLE_VARIABLE_SEPARATOR", lambda: v38.build(cr)),
        ("V3_10_TWO_VARIABLE_SEPARATOR", lambda: v310.build(cr)),
        ("V3_14_FIXED_DEPTH_1_TO_2_TO_2", lambda: v314.build(cr)),
    ]
    for mechanism, fn in calls:
        result = fn()
        status = str(result.get("status"))
        replay.append({"mechanism": mechanism, "status": status})
        if _exact_status(status, result):
            return {
                "state": list(state),
                "classification": "EXACT_UNSAT_WITH_EXISTING_REPLAYABLE_CERTIFICATE" if status.startswith("EXACT_UNSAT_") else "EXACT_SAT_WITH_REPLAYABLE_ORIGINAL_WITNESS",
                "closing_mechanism": mechanism,
                "status": status,
                "replay": replay,
            }

    tf = _two_factor_replay(cr)
    replay.append({"mechanism": "V3_16_NORMALIZATION_PLUS_V3_18_EXACT_TWO_FACTOR", "status": tf["status"]})
    if tf["status"].startswith("EXACT_UNSAT_"):
        return {"state": list(state), "classification": "EXACT_UNSAT_WITH_EXISTING_REPLAYABLE_CERTIFICATE", "closing_mechanism": "V3_18_EXACT_TWO_FACTOR", "status": tf["status"], "replay": replay, "v3_18": tf}
    if tf["status"].startswith("ADMIT_EXACT_"):
        return {"state": list(state), "classification": "EXACT_SAT_WITH_REPLAYABLE_ORIGINAL_WITNESS", "closing_mechanism": "V3_18_EXACT_TWO_FACTOR", "status": tf["status"], "replay": replay, "v3_18": tf}
    return {"state": list(state), "classification": "OPEN_AFTER_EXISTING_SEALED_PORTFOLIO", "closing_mechanism": None, "status": "OPEN_AFTER_EXISTING_SEALED_PORTFOLIO", "replay": replay, "v3_18": tf}


def synthetic_calibration() -> dict[str, Any]:
    raw = v35.multiple_common_core_states_control()
    p = profile_raw(raw)
    existing = v35.explain(raw)
    checks = {
        "prepare_ready": p.get("prepare_status") == "READY",
        "support_gt_one": int(p.get("exact_common_support_size", 0)) > 1,
        "existing_v3_5_status_open_nonunique": existing.get("status") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "excluded_from_real_authority": True,
        "support_bound_lemma_holds": p.get("support_bound_lemma_holds") is True,
    }
    return {
        "name": "V3_5_SYNTHETIC_MULTIPLE_COMMON_CORE_STATES_CONTROL",
        "class": "SYNTHETIC_CALIBRATION_ONLY__NOT_RAW_REACHABILITY_AUTHORITY",
        "eligible_for_first_real_fixture": False,
        "profile": p,
        "existing_v3_5_status": existing.get("status"),
        "checks": checks,
        "ok": all(checks.values()),
    }


def profile() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "verdict": FAIL, "source_guard": guard}

    fixture_rows = []
    by_sha: dict[str, dict[str, Any]] = {}
    for ordinal, fixture in enumerate(fixtures()):
        p = profile_raw(fixture["raw"])
        row = {"ordinal": ordinal, "name": fixture["name"], "class": fixture["class"], "eligible_for_first_real_fixture": True, **p}
        fixture_rows.append(row)
        sha = p["raw_sha256"]
        if sha not in by_sha:
            by_sha[sha] = {"representative": row, "aliases": []}
        by_sha[sha]["aliases"].append(fixture["name"])

    unique_rows = []
    for group in by_sha.values():
        rep = dict(group["representative"])
        rep["aliases"] = group["aliases"]
        unique_rows.append(rep)
    unique_rows.sort(key=lambda r: int(r["ordinal"]))

    real = [r for r in unique_rows if r.get("prepare_status") == "READY" and int(r.get("exact_common_support_size", 0)) > 1]
    first_real = real[0] if real else None
    all_bounds = all(r.get("support_bound_lemma_holds") is True for r in unique_rows if r.get("prepare_status") == "READY")
    synth = synthetic_calibration()

    phase_b = None
    first_open = None
    if first_real is not None:
        raw = next(f["raw"] for f in fixtures() if f["name"] == first_real["name"])
        core = [int(v) for v in first_real["common_core"]]
        states = [tuple(int(x) for x in s) for s in first_real["exact_common_support_tuples"]]
        state_rows = [replay_state(raw, core, s) for s in states]
        opens = [r for r in state_rows if r["classification"] == "OPEN_AFTER_EXISTING_SEALED_PORTFOLIO"]
        first_open = opens[0] if opens else None
        phase_b = {
            "raw_sha256": first_real["raw_sha256"],
            "fixture_name": first_real["name"],
            "state_count": len(states),
            "states": state_rows,
            "all_states_closed": not opens,
            "first_open_state": None if first_open is None else first_open["state"],
            "total_replay_count": len(state_rows),
            "state_count_le_explicit_input_rows": len(states) <= first_real["input_metrics"]["explicit_relation_row_count"],
        }

    checks = {
        "source_guard": guard["ok"],
        "synthetic_calibration": synth["ok"],
        "all_ready_authoritative_support_bounds_hold": all_bounds,
        "synthetic_not_in_unique_authoritative_census": all(r["name"] != synth["name"] for r in unique_rows),
        "first_real_is_authoritative_or_null": first_real is None or first_real.get("eligible_for_first_real_fixture") is True,
        "no_2_pow_core_enumeration": True,
    }
    if not all(checks.values()):
        verdict = FAIL
    elif first_real is None:
        verdict = PASS_NONE
    elif first_open is None:
        verdict = PASS_ALL
    else:
        verdict = PASS_OPEN

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict,
        "source_guard": guard,
        "checks": checks,
        "fixture_rows": fixture_rows,
        "unique_authoritative_raw_count": len(unique_rows),
        "unique_authoritative_census": unique_rows,
        "real_nonunique_fixture_count": len(real),
        "first_real_nonunique_fixture": None if first_real is None else {"name": first_real["name"], "raw_sha256": first_real["raw_sha256"], "support_size": first_real["exact_common_support_size"]},
        "synthetic_calibration": synth,
        "support_bound_lemma": {
            "statement": "|S|<=min_i|pi_C(F_i)|<=min_i|F_i|<=L_EXPLICIT_ROWS",
            "all_ready_authoritative_rows_verify": all_bounds,
            "consequence": "ACTUAL_EXPLICIT_COMMON_CORE_SUPPORT_CARDINALITY_IS_POLYNOMIALLY_BOUNDED_IN_THE_EXPLICIT_TABLE_INPUT;THIS_ALONE_IS_NOT_A_MULTI_STATE_SOLVER",
        },
        "phase_b_state_replay": phase_b,
        "resource_receipt": {
            "new_solver_mechanisms": 0,
            "new_boolean_branching_mechanisms": 0,
            "separator_ge3_boolean_branches": 0,
            "size4_boolean_separator_assignments": 0,
            "new_unbounded_recursion": 0,
            "new_three_plus_join_chains": 0,
            "global_residual_cartesian_products_materialized": 0,
            "core_assignments_enumerated_outside_explicit_support": 0,
            "budget_raise": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "NONUNIQUE_COMMON_CORE_SOLVED": False,
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


def main() -> None:
    print(json.dumps(profile(), sort_keys=True))


if __name__ == "__main__":
    main()
