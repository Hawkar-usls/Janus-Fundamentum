from __future__ import annotations

import argparse
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

ARTIFACT_ID = "JANUS-TRUMP-RAW-PREDECESSOR-NONUNIQUE-COMMON-CORE-ACQUISITION-CENSUS-INDEPENDENT-CHECK-2026-09-16-v1.0"
PASS_FOUND = "PASS_DIAGNOSTIC_FIRST_SOURCE_AUTHORIZED_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FROZEN"
PASS_NONE = "PASS_DIAGNOSTIC_NO_SOURCE_AUTHORIZED_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FOUND_IN_RECOVERED_PREDECESSOR_LINEAGE"
FAIL = "FAIL_DIAGNOSTIC_CANDIDATE_INDEPENDENT_MISMATCH"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_RAW_PREDECESSOR_NONUNIQUE_COMMON_CORE_REACHABILITY_ACQUISITION_CENSUS_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "7582086cb996a757f5b004d476c719d6a805e74f"
CLARIFICATION = Path("research/TRUMP_BICAMERAL_BUCKET_RAW_PREDECESSOR_NONUNIQUE_COMMON_CORE_REACHABILITY_ACQUISITION_CENSUS_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CLARIFICATION_BLOB = "f906ba98f4d4039a11c48fceb2214ad4a8a66ef9"
CANDIDATE = Path("research/tools/apma_bucket_raw_predecessor_nonunique_reachability_acquisition_census/census.py")
CANDIDATE_BLOB = "0886fe4b41652e52f76e862a752acab0832a5302"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-16_v3.20.json")
PARENT_STATE_BLOB = "ff91e5adcbe7cf37e04ce5e00520cc4c6d543f55"
PARENT_RESULT = Path("research/TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC_RESULT_2026-09-16.json")
PARENT_RESULT_BLOB = "f95e1e313217e6e7a05238ee01443d8200dbccdf"

SOURCE_BLOBS = {
    "research/tools/apma_unseen_basis/raw_relation_basis.py": "63490c05ef3e91a4f682f75da26ff2af811839a6",
    "research/tools/apma_bicameral_pair_separator/pair_separator_explainer.py": "b6dc5fde585affb167e74308bc8f1e0da2a09228adb1" if False else "b6dc5fde585affb167e74308bc8f10c64f7d2990",
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


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks: dict[str, bool] = {
        "prereg": blob(r / PREREG) == PREREG_BLOB,
        "clarification": blob(r / CLARIFICATION) == CLARIFICATION_BLOB,
        "candidate_bound_but_not_imported": blob(r / CANDIDATE) == CANDIDATE_BLOB,
        "parent_v3_20": blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_v3_20_result": blob(r / PARENT_RESULT) == PARENT_RESULT_BLOB,
    }
    for path, expected in SOURCE_BLOBS.items():
        checks[path] = blob(r / path) == expected
    return {"ok": all(checks.values()), "checks": checks}


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def defs() -> list[dict[str, Any]]:
    items: list[tuple[str, str, str, Callable[[], dict]]] = [
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
    return [
        {"ordinal": i, "source_class": c, "name": n, "constructor": ctor, "raw": fn()}
        for i, (c, n, ctor, fn) in enumerate(items)
    ]


def independent_profile(raw: dict) -> dict[str, Any]:
    canonical = raw_basis.canonicalize_raw(raw)
    sha = hashlib.sha256(canonical_bytes(canonical)).hexdigest()
    prep = cc_v11.first_failed_original_bucket_v11(raw)
    out: dict[str, Any] = {"raw_sha256": sha, "prepare_status": prep.get("status")}
    if prep.get("status") != "READY":
        predecessor = prep.get("predecessor")
        if isinstance(predecessor, dict):
            out["predecessor_terminal"] = predecessor.get("status")
        return out

    core = [int(v) for v in prep["common_core"]]
    projection_sets: list[set[tuple[int, ...]]] = []
    row_counts: list[int] = []
    factor_ids: list[str] = []
    for factor in prep["bucket"]:
        scope = [int(v) for v in factor["scope"]]
        positions = [scope.index(v) for v in core]
        projections = {
            tuple(int(row[p]) for p in positions)
            for row in factor["rows"]
        }
        projection_sets.append(projections)
        row_counts.append(len(factor["rows"]))
        factor_ids.append(str(factor["id"]))
    common = set.intersection(*projection_sets) if projection_sets else set()
    tuples = sorted(common)
    total_rows = sum(len(r["allowed"]) for r in canonical["constraints"])
    min_projection = min((len(x) for x in projection_sets), default=0)
    min_rows = min(row_counts, default=0)
    out.update({
        "common_core": core,
        "bucket_factor_ids": factor_ids,
        "bucket_factor_row_counts": row_counts,
        "factor_projection_support_sizes": [len(x) for x in projection_sets],
        "exact_common_support_size": len(tuples),
        "exact_common_support_tuples": [list(x) for x in tuples],
        "support_bound_holds": (
            len(tuples) <= min_projection
            and min_projection <= min_rows
            and min_rows <= total_rows
            and len(tuples) <= total_rows
        ),
    })
    return out


def independent_result() -> dict[str, Any]:
    rows = []
    groups: dict[str, dict[str, Any]] = {}
    for item in defs():
        p = independent_profile(item["raw"])
        row = {
            "ordinal": item["ordinal"],
            "source_class": item["source_class"],
            "name": item["name"],
            "constructor": item["constructor"],
            **p,
        }
        rows.append(row)
        if p["raw_sha256"] not in groups:
            groups[p["raw_sha256"]] = {"representative": row, "aliases": []}
        groups[p["raw_sha256"]]["aliases"].append({
            "ordinal": item["ordinal"],
            "source_class": item["source_class"],
            "name": item["name"],
            "constructor": item["constructor"],
        })
    unique = []
    for group in groups.values():
        rec = dict(group["representative"])
        rec["aliases"] = group["aliases"]
        unique.append(rec)
    unique.sort(key=lambda x: int(x["ordinal"]))
    ready = [x for x in unique if x.get("prepare_status") == "READY"]
    nonunique = [x for x in ready if int(x.get("exact_common_support_size", 0)) > 1]
    first = nonunique[0] if nonunique else None
    return {
        "rows": rows,
        "unique": unique,
        "ready": ready,
        "nonunique": nonunique,
        "first": first,
        "verdict": PASS_FOUND if first is not None else PASS_NONE,
    }


def check(candidate: dict) -> dict[str, Any]:
    guard = source_guard()
    independent = independent_result()
    candidate_by_sha = {x["raw_sha256"]: x for x in candidate.get("unique_raw_census", [])}
    row_match: dict[str, bool] = {}
    for row in independent["unique"]:
        cand = candidate_by_sha.get(row["raw_sha256"])
        fields = [
            "prepare_status",
            "predecessor_terminal",
            "common_core",
            "bucket_factor_ids",
            "bucket_factor_row_counts",
            "factor_projection_support_sizes",
            "exact_common_support_size",
            "exact_common_support_tuples",
            "support_bound_holds",
            "aliases",
        ]
        row_match[row["raw_sha256"]] = bool(cand) and all(cand.get(k) == row.get(k) for k in fields)

    if independent["first"] is None:
        expected_first = None
    else:
        x = independent["first"]
        expected_first = {
            "ordinal": x["ordinal"],
            "name": x["name"],
            "raw_sha256": x["raw_sha256"],
            "aliases": x["aliases"],
            "common_core": x["common_core"],
            "exact_common_support_size": x["exact_common_support_size"],
            "exact_common_support_tuples": x["exact_common_support_tuples"],
        }
    candidate_first = candidate.get("first_real_nonunique_fixture")
    candidate_first_core = None if candidate_first is None else {
        k: candidate_first.get(k)
        for k in ["ordinal", "name", "raw_sha256", "aliases", "common_core", "exact_common_support_size", "exact_common_support_tuples"]
    }

    checks = {
        "source_guard": guard["ok"],
        "candidate_helpers_not_imported": True,
        "same_constructor_count": candidate.get("constructor_count") == len(independent["rows"]),
        "same_unique_raw_count": candidate.get("unique_raw_count") == len(independent["unique"]),
        "same_ready_unique_raw_count": candidate.get("ready_unique_raw_count") == len(independent["ready"]),
        "same_real_nonunique_unique_raw_count": candidate.get("real_nonunique_unique_raw_count") == len(independent["nonunique"]),
        "all_unique_rows_match_by_sha": bool(row_match) and all(row_match.values()),
        "candidate_verdict_matches_independent": candidate.get("verdict") == independent["verdict"],
        "first_real_fixture_matches": candidate_first_core == expected_first,
        "all_ready_support_bounds_hold_independently": all(x.get("support_bound_holds") is True for x in independent["ready"]),
        "no_target_aware_synthetic_nonunique_in_independent_inventory": all(x["name"] != "V3_5_SYNTHETIC_MULTIPLE_COMMON_CORE_STATES_CONTROL" for x in independent["rows"]),
        "p_vs_np_open": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "general_sat_not_proved": candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "nonunique_not_promoted": candidate.get("scientific_firewall", {}).get("NONUNIQUE_COMMON_CORE_SOLVED") is False,
    }

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_DIAGNOSTIC_CHECK_ONLY",
        "candidate_helpers_imported": False,
        "verdict": independent["verdict"] if all(checks.values()) else FAIL,
        "checks": checks,
        "row_match_by_sha": row_match,
        "independent_constructor_count": len(independent["rows"]),
        "independent_unique_raw_count": len(independent["unique"]),
        "independent_ready_unique_raw_count": len(independent["ready"]),
        "independent_real_nonunique_unique_raw_count": len(independent["nonunique"]),
        "independent_first_real_nonunique_fixture": expected_first,
        "independent_unique_raw_census": independent["unique"],
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "NONUNIQUE_COMMON_CORE_SOLVED": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    print(json.dumps(check(candidate), sort_keys=True))


if __name__ == "__main__":
    main()
