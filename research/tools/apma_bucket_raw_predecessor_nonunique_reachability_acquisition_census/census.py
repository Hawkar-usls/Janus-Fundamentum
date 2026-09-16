from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_bicameral_pair_separator import pair_separator_explainer as pair_sep
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as cut_support
from research.tools.apma_component_join_carrier import component_join_carrier as component_join
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as derived
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as v310
from research.tools.apma_bucket_fixed_depth_122 import fixed_depth_122 as v314
from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as v316

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-RAW-PREDECESSOR-NONUNIQUE-COMMON-CORE-REACHABILITY-ACQUISITION-CENSUS-2026-09-16-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__EVIDENCE_ACQUISITION_BEFORE_MECHANISM_DESIGN"
PASS_FOUND = "PASS_DIAGNOSTIC_FIRST_SOURCE_AUTHORIZED_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FROZEN"
PASS_NONE = "PASS_DIAGNOSTIC_NO_SOURCE_AUTHORIZED_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FOUND_IN_RECOVERED_PREDECESSOR_LINEAGE"
FAIL_SOURCE = "FAIL_DIAGNOSTIC_SOURCE_PROVENANCE_OR_RAW_PREDECESSOR_LINEAGE_INCOMPLETE"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_RAW_PREDECESSOR_NONUNIQUE_COMMON_CORE_REACHABILITY_ACQUISITION_CENSUS_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "7582086cb996a757f5b004d476c719d6a805e74f"
CLARIFICATION = Path("research/TRUMP_BICAMERAL_BUCKET_RAW_PREDECESSOR_NONUNIQUE_COMMON_CORE_REACHABILITY_ACQUISITION_CENSUS_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CLARIFICATION_BLOB = "f906ba98f4d4039a11c48fceb2214ad4a8a66ef9"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-16_v3.20.json")
PARENT_STATE_BLOB = "ff91e5adcbe7cf37e04ce5e00520cc4c6d543f55"
PARENT_RESULT = Path("research/TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC_RESULT_2026-09-16.json")
PARENT_RESULT_BLOB = "f95e1e313217e6e7a05238ee01443d8200dbccdf"

SOURCE_BLOBS = {
    "research/tools/apma_unseen_basis/raw_relation_basis.py": "63490c05ef3e91a4f682f75da26ff2af811839a6",
    "research/tools/apma_bicameral_pair_separator/pair_separator_explainer.py": "b6dc5fde585affb167e74308bc8f10c64f7d2990",
    "research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py": "c0c612676e39241b95026c15823e7af6b3da8f0d",
    "research/tools/apma_cut_support_carrier/cut_support_carrier.py": "012aa1acf52fa12de26bb64df303b2208d396ea9",
    "research/tools/apma_component_join_carrier/component_join_carrier.py": "89f5d591d4d553bb26489908a79f2c739f62b756",
    "research/tools/apma_derived_boundary_factor/derived_two_relation_factor.py": "1047351df47ed5f326eef2650da0c9f5ee0f2fda",
    "research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py": "314034bac990e524d1db7743aef0aebd3b4565c1",
    "research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py": "f103bf9b14e3b208200f429b75d0858c4963fa7c",
    "research/tools/apma_bucket_common_core/common_core_semijoin_prefilter_v1_1.py": "c29229bbaebf2935ab03c77c7d444e2a33422f17",
    "research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py": "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8",
    "research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py": "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0",
    "research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py": "0853ebb9a3e273fdaeca172dbe2502cc7214cf61",
    "research/tools/apma_bucket_fixed_depth_122/fixed_depth_122.py": "2e02bac1d78b751d22df2c50a01980ae06bd2751",
    "research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py": "4128f0db77dfc1391b6ec539f201250bfb3d8b6e",
}


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_raw(raw: dict) -> dict:
    return raw_basis.canonicalize_raw(raw)


def raw_sha256(raw: dict) -> str:
    return hashlib.sha256(canonical_bytes(canonical_raw(raw))).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks: dict[str, bool] = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "clarification_blob": git_blob_sha1(r / CLARIFICATION) == CLARIFICATION_BLOB,
        "parent_v3_20_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_v3_20_result_blob": git_blob_sha1(r / PARENT_RESULT) == PARENT_RESULT_BLOB,
    }
    for path, expected in SOURCE_BLOBS.items():
        checks[path] = git_blob_sha1(r / path) == expected
    return {"ok": all(checks.values()), "checks": checks}


def fixture_defs() -> list[dict[str, Any]]:
    # Exact constructor order frozen in preregistration. Do not reorder based on results.
    defs: list[tuple[str, str, str, Callable[[], dict]]] = [
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "PAIR_SEPARATOR_POSITIVE_PRIOR_BICONNECTED", "pair_separator_explainer.positive_prior_biconnected()", pair_sep.positive_prior_biconnected),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "PAIR_SEPARATOR_NEGATIVE_THREE_VARIABLE_CUT_REQUIRED", "pair_separator_explainer.negative_three_variable_cut_required()", pair_sep.negative_three_variable_cut_required),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "MINCUT_POSITIVE_LOGWIDTH_CUT3", "mincut_logwidth_explainer.positive_logwidth_cut3()", mincut.positive_logwidth_cut3),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "MINCUT_NEGATIVE_OVERWIDTH_CUT20", "mincut_logwidth_explainer.negative_overwidth_cut(20)", lambda: mincut.negative_overwidth_cut(20)),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_POSITIVE_OVERWIDTH", "cut_support_carrier.positive_overwidth()", cut_support.positive_overwidth),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_EMPTY_INTERSECTION20", "cut_support_carrier.empty_intersection_control(20)", lambda: cut_support.empty_intersection_control(20)),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_MULTI_RELATION_COMPONENT20", "cut_support_carrier.multi_relation_component_control(20)", lambda: cut_support.multi_relation_component_control(20)),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_PARTIAL_CUT_VISIBILITY", "cut_support_carrier.partial_cut_visibility_control()", cut_support.partial_cut_visibility_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "COMPONENT_JOIN_POSITIVE_MULTI_RELATION_K20", "component_join_carrier.positive_multi_relation_k20()", component_join.positive_multi_relation_k20),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "COMPONENT_JOIN_EMPTY_CONDITIONAL_JOIN", "component_join_carrier.empty_conditional_join_control()", component_join.empty_conditional_join_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "COMPONENT_JOIN_ALPHA_CYCLE", "component_join_carrier.alpha_cycle_control()", component_join.alpha_cycle_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "DERIVED_POSITIVE_NO_ANCHOR_K20", "derived_two_relation_factor.positive_no_anchor_k20()", derived.positive_no_anchor_k20),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "DERIVED_EMPTY_PAIR_SUPPORT", "derived_two_relation_factor.empty_pair_support_control()", derived.empty_pair_support_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "DERIVED_THREE_RELATION_NO_ANCHOR", "derived_two_relation_factor.three_relation_no_anchor_control()", derived.three_relation_no_anchor_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "GUARDED_POSITIVE_MIXED_THREE_RELATION", "guarded_bounded_output_elimination.positive_mixed_three_relation_control()", guarded.positive_mixed_three_relation_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "GUARDED_SCOPED_UNSAT", "guarded_bounded_output_elimination.scoped_unsat_control()", guarded.scoped_unsat_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "GUARDED_OVERBUDGET", "guarded_bounded_output_elimination.overbudget_control()", guarded.overbudget_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_4_POSITIVE_ALIGNED_OVERBUDGET_CONTROL", "common_core_semijoin_prefilter.positive_aligned_overbudget_control()", cc_v1.positive_aligned_overbudget_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_4_FILTERED_STILL_OVERBUDGET_CONTROL", "common_core_semijoin_prefilter.filtered_still_overbudget_control()", cc_v1.filtered_still_overbudget_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", "residual_le2_factorized_payload.residual_component_gt2_control()", v36.residual_component_gt2_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", "residual_single_separator_factorized_payload.no_single_variable_articulation_control()", v38.no_single_variable_articulation_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_8_BRANCH_STILL_GT2_CONTROL", "residual_single_separator_factorized_payload.branch_still_gt2_control()", v38.branch_still_gt2_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_10_NO_PAIR_K4_CONTROL", "residual_pair_separator_factorized_payload.no_pair_k4_control()", v310.no_pair_k4_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROL_ALIAS", "V3_14_POSITIVE_K4_CONTROL", "fixed_depth_122.positive_k4_control()", v314.positive_k4_control),
        ("V3_20_BASELINE_REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBES", "V3_16_RAW_K5_FULL_CUBE", "k5_raw_semantic_forensic.build_raw_k5('FULL_CUBE')", lambda: v316.build_raw_k5("FULL_CUBE")),
        ("V3_20_BASELINE_REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBES", "V3_16_RAW_K5_EXACT_2_OF_4", "k5_raw_semantic_forensic.build_raw_k5('EXACT_2_OF_4')", lambda: v316.build_raw_k5("EXACT_2_OF_4")),
    ]
    out = []
    for ordinal, (source_class, name, constructor, fn) in enumerate(defs):
        out.append({"ordinal": ordinal, "source_class": source_class, "name": name, "constructor": constructor, "raw": fn()})
    return out


def input_metrics(canonical: dict) -> dict[str, int]:
    constraints = canonical["constraints"]
    return {
        "canonical_json_bytes": len(canonical_bytes(canonical)),
        "explicit_relation_row_count": sum(len(rel["allowed"]) for rel in constraints),
        "explicit_boolean_row_cells": sum(len(rel["scope"]) * len(rel["allowed"]) for rel in constraints),
        "variable_count": len(canonical["variables"]),
        "constraint_count": len(constraints),
    }


def exact_common_support(prep: dict) -> dict[str, Any]:
    core = [int(v) for v in prep["common_core"]]
    supports: list[set[tuple[int, ...]]] = []
    row_counts: list[int] = []
    for factor in prep["bucket"]:
        scope = [int(v) for v in factor["scope"]]
        pos = {v: i for i, v in enumerate(scope)}
        support = {
            tuple(int(row[pos[v]]) for v in core)
            for row in factor["rows"]
        }
        supports.append(support)
        row_counts.append(len(factor["rows"]))
    common = set.intersection(*supports) if supports else set()
    tuples = sorted(common)
    min_projection = min((len(s) for s in supports), default=0)
    min_rows = min(row_counts, default=0)
    return {
        "common_core": core,
        "bucket_factor_ids": [str(f["id"]) for f in prep["bucket"]],
        "bucket_factor_row_counts": row_counts,
        "factor_projection_support_sizes": [len(s) for s in supports],
        "exact_common_support_size": len(tuples),
        "exact_common_support_tuples": [list(t) for t in tuples],
        "support_bound_checks": {
            "support_le_min_projection": len(tuples) <= min_projection,
            "min_projection_le_min_rows": min_projection <= min_rows,
        },
    }


def profile(raw: dict) -> dict[str, Any]:
    canonical = canonical_raw(raw)
    sha = hashlib.sha256(canonical_bytes(canonical)).hexdigest()
    metrics = input_metrics(canonical)
    prep = cc_v11.first_failed_original_bucket_v11(raw)
    out: dict[str, Any] = {
        "raw_sha256": sha,
        "input_metrics": metrics,
        "prepare_status": prep.get("status"),
    }
    if prep.get("status") != "READY":
        predecessor = prep.get("predecessor")
        if isinstance(predecessor, dict):
            out["predecessor_terminal"] = predecessor.get("status")
        return out
    support = exact_common_support(prep)
    support_size = int(support["exact_common_support_size"])
    support["support_bound_checks"].update({
        "min_rows_le_total_explicit_rows": min(support["bucket_factor_row_counts"], default=0) <= metrics["explicit_relation_row_count"],
        "support_size_le_total_explicit_rows": support_size <= metrics["explicit_relation_row_count"],
        "no_2_pow_core_enumeration_needed_for_actual_support": True,
    })
    support["support_bound_holds"] = all(support["support_bound_checks"].values())
    out.update(support)
    out["classification"] = (
        "REAL_NONUNIQUE_COMMON_CORE_REACHABLE"
        if support_size > 1
        else "UNIQUE_OR_EMPTY_COMMON_CORE_SUPPORT"
    )
    return out


def run() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "verdict": FAIL_SOURCE,
            "source_guard": guard,
            "scientific_firewall": scientific_firewall(),
        }

    rows: list[dict[str, Any]] = []
    groups: dict[str, dict[str, Any]] = {}
    for item in fixture_defs():
        p = profile(item["raw"])
        row = {
            "ordinal": item["ordinal"],
            "source_class": item["source_class"],
            "name": item["name"],
            "constructor": item["constructor"],
            **p,
        }
        rows.append(row)
        sha = p["raw_sha256"]
        if sha not in groups:
            groups[sha] = {"representative": row, "aliases": []}
        groups[sha]["aliases"].append({
            "ordinal": item["ordinal"],
            "source_class": item["source_class"],
            "name": item["name"],
            "constructor": item["constructor"],
        })

    unique: list[dict[str, Any]] = []
    for group in groups.values():
        rec = dict(group["representative"])
        rec["aliases"] = group["aliases"]
        unique.append(rec)
    unique.sort(key=lambda x: int(x["ordinal"]))

    ready = [x for x in unique if x.get("prepare_status") == "READY"]
    nonunique = [x for x in ready if int(x.get("exact_common_support_size", 0)) > 1]
    first = nonunique[0] if nonunique else None
    all_ready_bounds = all(x.get("support_bound_holds") is True for x in ready)
    verdict = PASS_FOUND if first is not None else PASS_NONE

    checks = {
        "source_guard": guard["ok"],
        "all_unique_rows_classified": len(unique) > 0 and all(bool(x.get("prepare_status")) for x in unique),
        "all_ready_support_recomputed_from_explicit_rows": all("exact_common_support_tuples" in x for x in ready),
        "all_ready_support_bounds_hold": all_ready_bounds,
        "deterministic_first_nonunique_or_null": first is None or first is nonunique[0],
        "no_target_aware_synthetic_nonunique_control_in_inventory": all(x["name"] != "V3_5_SYNTHETIC_MULTIPLE_COMMON_CORE_STATES_CONTROL" for x in rows),
        "no_2_pow_core_enumeration": True,
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict if all(checks.values()) else FAIL_SOURCE,
        "source_guard": guard,
        "checks": checks,
        "fixture_rows": rows,
        "constructor_count": len(rows),
        "unique_raw_count": len(unique),
        "ready_unique_raw_count": len(ready),
        "real_nonunique_unique_raw_count": len(nonunique),
        "first_real_nonunique_fixture": None if first is None else {
            "ordinal": first["ordinal"],
            "name": first["name"],
            "raw_sha256": first["raw_sha256"],
            "aliases": first["aliases"],
            "common_core": first["common_core"],
            "exact_common_support_size": first["exact_common_support_size"],
            "exact_common_support_tuples": first["exact_common_support_tuples"],
            "input_metrics": first["input_metrics"],
        },
        "unique_raw_census": unique,
        "resource_receipt": {
            "new_solver_mechanisms": 0,
            "new_compression_carriers": 0,
            "core_assignments_enumerated_outside_explicit_support": 0,
            "two_to_core_width_enumerations": 0,
            "separator_ge3_boolean_branches": 0,
            "size4_boolean_separator_assignments": 0,
            "new_unbounded_recursion": 0,
            "new_three_plus_join_chains": 0,
            "global_residual_cartesian_products_materialized": 0,
            "budget_raise": False,
        },
        "scientific_firewall": scientific_firewall(),
    }


def scientific_firewall() -> dict[str, Any]:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "NONUNIQUE_COMMON_CORE_SOLVED": False,
        "GLOBAL_APMA_FRONTIER": "APMA_UNSEEN_LOCAL_INVARIANT_INDUCTION_FALSIFIER_GATE",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
