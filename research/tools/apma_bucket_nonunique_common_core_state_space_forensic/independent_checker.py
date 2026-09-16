from __future__ import annotations

import argparse
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

ARTIFACT_ID = "JANUS-TRUMP-NONUNIQUE-COMMON-CORE-STATE-SPACE-FORENSIC-INDEPENDENT-CHECK-2026-09-16-v1.0"
PASS_NONE = "PASS_DIAGNOSTIC_NO_AUTHORITATIVE_RAW_NONUNIQUE_COMMON_CORE_FIXTURE_FOUND"
PASS_ALL = "PASS_DIAGNOSTIC_RAW_NONUNIQUE_COMMON_CORE_FOUND_ALL_STATES_CLOSED_BY_SEALED_PORTFOLIO"
PASS_OPEN = "PASS_DIAGNOSTIC_RAW_NONUNIQUE_COMMON_CORE_FOUND_WITH_FIRST_OPEN_STATE"
FAIL = "FAIL_DIAGNOSTIC_SOURCE_OR_INDEPENDENT_MISMATCH"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "5d01ed7f058e4fa4a8ab729d5c8ad0ac1928f517"
CLARIFICATION = Path("research/TRUMP_BICAMERAL_BUCKET_NONUNIQUE_COMMON_CORE_SUPPORT_STATE_SPACE_FORENSIC_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CLARIFICATION_BLOB = "312f786f5888c698b408e18cffa6d9f034bd82a0"
CANDIDATE = Path("research/tools/apma_bucket_nonunique_common_core_state_space_forensic/forensic.py")
CANDIDATE_BLOB = "d3c1c53dea652242135b25a2f63ecd73efa62f17"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-16_v3.19.json")
PARENT_BLOB = "e076d24b438262d0eb6d08309f31c3ee4648b79d"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg": blob(r / PREREG) == PREREG_BLOB,
        "clarification": blob(r / CLARIFICATION) == CLARIFICATION_BLOB,
        "candidate_bound_not_imported": blob(r / CANDIDATE) == CANDIDATE_BLOB,
        "parent_v3_19": blob(r / PARENT) == PARENT_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def raw_sha(raw: dict) -> str:
    return hashlib.sha256(canonical_bytes(raw_basis.canonicalize_raw(raw))).hexdigest()


def fixture_defs() -> list[tuple[str, dict]]:
    return [
        ("V3_4_POSITIVE_ALIGNED_OVERBUDGET_CONTROL", cc_v1.positive_aligned_overbudget_control()),
        ("V3_4_FILTERED_STILL_OVERBUDGET_CONTROL", cc_v1.filtered_still_overbudget_control()),
        ("V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", v36.residual_component_gt2_control()),
        ("V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", v38.no_single_variable_articulation_control()),
        ("V3_8_BRANCH_STILL_GT2_CONTROL", v38.branch_still_gt2_control()),
        ("V3_10_NO_PAIR_K4_CONTROL", v310.no_pair_k4_control()),
        ("V3_14_POSITIVE_K4_CONTROL", v314.positive_k4_control()),
        ("V3_16_RAW_K5_FULL_CUBE", v316.build_raw_k5("FULL_CUBE")),
        ("V3_16_RAW_K5_EXACT_2_OF_4", v316.build_raw_k5("EXACT_2_OF_4")),
    ]


def profile_independent(raw: dict) -> dict[str, Any]:
    canonical = raw_basis.canonicalize_raw(raw)
    sha = hashlib.sha256(canonical_bytes(canonical)).hexdigest()
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    out: dict[str, Any] = {"raw_sha256": sha, "prepare_status": ready.get("status")}
    if ready.get("status") != "READY":
        return out
    core = [int(v) for v in ready["common_core"]]
    supports: list[set[tuple[int, ...]]] = []
    row_counts = []
    for factor in ready["bucket"]:
        scope = [int(v) for v in factor["scope"]]
        pos = {v: i for i, v in enumerate(scope)}
        support = set()
        for row in factor["rows"]:
            support.add(tuple(int(row[pos[v]]) for v in core))
        supports.append(support)
        row_counts.append(len(factor["rows"]))
    common = set.intersection(*supports) if supports else set()
    tuples = sorted(common)
    total_rows = sum(len(rel["allowed"]) for rel in canonical["constraints"])
    total_cells = sum(len(rel["scope"]) * len(rel["allowed"]) for rel in canonical["constraints"])
    min_projection = min((len(s) for s in supports), default=0)
    min_rows = min(row_counts, default=0)
    min_bucket_cells = min((len(f["rows"]) * len(f["scope"]) for f in ready["bucket"]), default=0)
    support_cells = len(tuples) * len(core)
    checks = {
        "subset_each": all(common <= s for s in supports),
        "support_le_min_projection": len(tuples) <= min_projection,
        "min_projection_le_min_rows": min_projection <= min_rows,
        "min_rows_le_total_rows": min_rows <= total_rows,
        "support_cells_le_min_bucket_cells": support_cells <= min_bucket_cells,
        "support_cells_le_total_cells": support_cells <= total_cells,
    }
    out.update({
        "common_core": core,
        "bucket_factor_ids": [str(f["id"]) for f in ready["bucket"]],
        "factor_projection_support_sizes": [len(s) for s in supports],
        "exact_common_support_size": len(tuples),
        "exact_common_support_tuples": [list(t) for t in tuples],
        "support_bound_checks": checks,
        "support_bound_lemma_holds": all(checks.values()),
    })
    return out


def condition_independent(raw: dict, core: list[int], state: tuple[int, ...]) -> tuple[dict, list[str]]:
    state_map = dict(zip(core, state))
    out = json.loads(json.dumps(raw))
    empty = []
    for rel in out["constraints"]:
        scope = [int(v) for v in rel["scope"]]
        pos = {v: i for i, v in enumerate(scope)}
        overlap = [v for v in core if v in pos]
        if not overlap:
            continue
        kept = [row for row in rel["allowed"] if all(int(row[pos[v]]) == int(state_map[v]) for v in overlap)]
        rel["allowed"] = kept
        if not kept:
            empty.append(str(rel.get("id", "?")))
    return out, empty


def exact_status(status: str, obj: dict) -> bool:
    if not (status.startswith("ADMIT_EXACT_") or status.startswith("EXACT_UNSAT_")):
        return False
    if "witness_verified" in obj and obj.get("witness_verified") is not True:
        return False
    if "certificate_verified" in obj and obj.get("certificate_verified") is not True:
        return False
    return True


def two_factor_independent(raw: dict) -> str:
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return "OPEN_V3_18_PREP_NOT_READY"
    factors = prep["conditioned"]
    core = [int(v) for v in prep["core"]]
    norm = v316.exact_universal_normalize(factors, core)
    kept = norm["kept"]
    comps = v316.components(kept, core) if kept else []
    gt2 = [c for c in comps if len(c) > 2]
    if not gt2:
        return "OPEN_NO_GT2_FOR_V3_18"
    statuses = []
    for comp in gt2:
        scopes = {}
        rows = {}
        for idx in comp:
            factor = kept[idx]
            rs, rr = v316.residual_relation(factor, core)
            scopes[str(factor["id"])] = [int(v) for v in rs]
            rows[str(factor["id"])] = {tuple(int(x) for x in row) for row in rr}
        model = v318.recognize_component(scopes, rows, {"kind": "INDEPENDENT_NONUNIQUE_REPLAY"})
        if model.get("status") != "READY_EXACT_TWO_FACTOR_COMPONENT":
            return "OPEN_AFTER_V3_18_REPLAY"
        solved = v318.solve_model(model)
        if solved.get("certificate_verified") is not True:
            return "OPEN_AFTER_V3_18_REPLAY"
        statuses.append(str(solved.get("status")))
    if any(s.startswith("EXACT_UNSAT_") for s in statuses):
        return "EXACT_UNSAT_BY_SEALED_V3_18_COMPONENT"
    if statuses and all(s == "EXACT_SAT_TWO_FACTOR" for s in statuses):
        return "ADMIT_EXACT_BY_SEALED_V3_18_COMPONENT_PORTFOLIO"
    return "OPEN_AFTER_V3_18_REPLAY"


def replay_independent(raw: dict, core: list[int], state: tuple[int, ...]) -> dict[str, Any]:
    cr, empty = condition_independent(raw, core, state)
    if empty:
        return {"state": list(state), "classification": "EXACT_UNSAT_WITH_EXISTING_REPLAYABLE_CERTIFICATE", "status": "EXACT_UNSAT_BY_EMPTY_CONDITIONED_RELATION"}
    for name, fn in [
        ("V3_5", lambda: v35.explain(cr)),
        ("V3_6", lambda: v36.build(cr)),
        ("V3_8", lambda: v38.build(cr)),
        ("V3_10", lambda: v310.build(cr)),
        ("V3_14", lambda: v314.build(cr)),
    ]:
        obj = fn()
        status = str(obj.get("status"))
        if exact_status(status, obj):
            return {"state": list(state), "classification": "EXACT_UNSAT_WITH_EXISTING_REPLAYABLE_CERTIFICATE" if status.startswith("EXACT_UNSAT_") else "EXACT_SAT_WITH_REPLAYABLE_ORIGINAL_WITNESS", "status": status, "closing": name}
    status = two_factor_independent(cr)
    if status.startswith("EXACT_UNSAT_"):
        return {"state": list(state), "classification": "EXACT_UNSAT_WITH_EXISTING_REPLAYABLE_CERTIFICATE", "status": status, "closing": "V3_18"}
    if status.startswith("ADMIT_EXACT_"):
        return {"state": list(state), "classification": "EXACT_SAT_WITH_REPLAYABLE_ORIGINAL_WITNESS", "status": status, "closing": "V3_18"}
    return {"state": list(state), "classification": "OPEN_AFTER_EXISTING_SEALED_PORTFOLIO", "status": "OPEN_AFTER_EXISTING_SEALED_PORTFOLIO"}


def independent_result() -> dict[str, Any]:
    rows = []
    by_sha: dict[str, dict[str, Any]] = {}
    defs = fixture_defs()
    for ordinal, (name, raw) in enumerate(defs):
        p = profile_independent(raw)
        row = {"ordinal": ordinal, "name": name, **p}
        rows.append(row)
        if p["raw_sha256"] not in by_sha:
            by_sha[p["raw_sha256"]] = {"representative": row, "aliases": []}
        by_sha[p["raw_sha256"]]["aliases"].append(name)
    unique = []
    for g in by_sha.values():
        x = dict(g["representative"])
        x["aliases"] = g["aliases"]
        unique.append(x)
    unique.sort(key=lambda x: int(x["ordinal"]))
    real = [x for x in unique if x.get("prepare_status") == "READY" and int(x.get("exact_common_support_size", 0)) > 1]
    first = real[0] if real else None
    state_rows = None
    first_open = None
    if first is not None:
        raw = next(raw for name, raw in defs if name == first["name"])
        core = [int(v) for v in first["common_core"]]
        states = [tuple(int(v) for v in s) for s in first["exact_common_support_tuples"]]
        state_rows = [replay_independent(raw, core, s) for s in states]
        opens = [x for x in state_rows if x["classification"] == "OPEN_AFTER_EXISTING_SEALED_PORTFOLIO"]
        first_open = opens[0] if opens else None
    verdict = PASS_NONE if first is None else (PASS_ALL if first_open is None else PASS_OPEN)
    return {"rows": rows, "unique": unique, "real": real, "first": first, "states": state_rows, "first_open": first_open, "verdict": verdict}


def check(candidate: dict) -> dict[str, Any]:
    guard = source_guard()
    independent = independent_result()
    candidate_by_sha = {r["raw_sha256"]: r for r in candidate.get("unique_authoritative_census", [])}
    row_match = {}
    for row in independent["unique"]:
        cand = candidate_by_sha.get(row["raw_sha256"])
        row_match[row["raw_sha256"]] = bool(cand) and all([
            cand.get("prepare_status") == row.get("prepare_status"),
            cand.get("common_core") == row.get("common_core"),
            cand.get("bucket_factor_ids") == row.get("bucket_factor_ids"),
            cand.get("factor_projection_support_sizes") == row.get("factor_projection_support_sizes"),
            cand.get("exact_common_support_size") == row.get("exact_common_support_size"),
            cand.get("exact_common_support_tuples") == row.get("exact_common_support_tuples"),
            cand.get("support_bound_lemma_holds") == row.get("support_bound_lemma_holds"),
        ])

    synthetic_raw = v35.multiple_common_core_states_control()
    synthetic_profile = profile_independent(synthetic_raw)
    synthetic_status = v35.explain(synthetic_raw).get("status")
    candidate_states = candidate.get("phase_b_state_replay", {}).get("states") if candidate.get("phase_b_state_replay") else None
    state_vector_match = True
    if independent["states"] is not None:
        if candidate_states is None:
            state_vector_match = False
        else:
            state_vector_match = [(x["state"], x["classification"]) for x in candidate_states] == [(x["state"], x["classification"]) for x in independent["states"]]

    checks = {
        "source_guard": guard["ok"],
        "candidate_helpers_imported": False,
        "same_unique_raw_count": candidate.get("unique_authoritative_raw_count") == len(independent["unique"]),
        "same_real_nonunique_count": candidate.get("real_nonunique_fixture_count") == len(independent["real"]),
        "all_unique_rows_match_by_sha": bool(row_match) and all(row_match.values()),
        "candidate_verdict_matches_independent": candidate.get("verdict") == independent["verdict"],
        "support_bound_holds_independently": all(x.get("support_bound_lemma_holds") is True for x in independent["unique"] if x.get("prepare_status") == "READY"),
        "synthetic_support_gt_one": int(synthetic_profile.get("exact_common_support_size", 0)) > 1,
        "synthetic_existing_status_open_nonunique": synthetic_status == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "synthetic_excluded_from_authoritative_sha_set": synthetic_profile["raw_sha256"] not in {x["raw_sha256"] for x in independent["unique"]},
        "phase_b_state_vector_match": state_vector_match,
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
        "independent_unique_raw_count": len(independent["unique"]),
        "independent_real_nonunique_count": len(independent["real"]),
        "independent_first_real": None if independent["first"] is None else {"name": independent["first"]["name"], "raw_sha256": independent["first"]["raw_sha256"], "support_size": independent["first"]["exact_common_support_size"]},
        "independent_unique_census": independent["unique"],
        "synthetic_calibration": {"profile": synthetic_profile, "existing_v3_5_status": synthetic_status},
        "independent_phase_b_states": independent["states"],
        "scientific_firewall": {"P_VS_NP": "OPEN", "GENERAL_SAT_IN_P": "NOT_PROVED", "NONUNIQUE_COMMON_CORE_SOLVED": False},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    print(json.dumps(check(candidate), sort_keys=True))


if __name__ == "__main__":
    main()
