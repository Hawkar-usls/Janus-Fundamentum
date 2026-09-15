from __future__ import annotations

import argparse
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

PASS_FOUND = "PASS_DIAGNOSTIC_GT2_CENSUS_WITH_FIRST_UNADMITTED_RAW_OBSTRUCTION"
PASS_NONE = "PASS_DIAGNOSTIC_NO_FROZEN_RAW_UNADMITTED_GT2_OBSTRUCTION_FOUND"
FAIL = "FAIL_INDEPENDENT_GT2_RAW_OBSTRUCTION_CENSUS_CHECK"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_GT2_UNADMITTED_RAW_OBSTRUCTION_CENSUS_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "e6571f439dc15c8ac5be9882ceab854b659cf39f"
CLARIFICATION = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_GT2_UNADMITTED_RAW_OBSTRUCTION_CENSUS_PREREGISTRATION_CLARIFICATION_2026-09-16.json")
CLARIFICATION_BLOB = "945b2324a19a85a8f3ce7615aa023777b17bfd19"
CANDIDATE = Path("research/tools/apma_bucket_gt2_unadmitted_raw_obstruction_census/census.py")
CANDIDATE_BLOB = "0134c7e654b3bf41b7a43da648b1dbb485495cf4"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg": git_blob(r / PREREG) == PREREG_BLOB,
        "clarification": git_blob(r / CLARIFICATION) == CLARIFICATION_BLOB,
        "candidate_bound_not_imported": git_blob(r / CANDIDATE) == CANDIDATE_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def obj_sha(obj: Any) -> str:
    b = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def raw_sha(raw: dict) -> str:
    return obj_sha(raw_basis.canonicalize_raw(raw))


def source_cases() -> list[tuple[str, dict]]:
    return [
        ("V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", v36.residual_component_gt2_control()),
        ("V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", v38.no_single_variable_articulation_control()),
        ("V3_8_BRANCH_STILL_GT2_CONTROL", v38.branch_still_gt2_control()),
        ("V3_10_NO_PAIR_K4_CONTROL", v310.no_pair_k4_control()),
        ("V3_14_POSITIVE_K4_CONTROL", v314.positive_k4_control()),
        ("V3_16_RAW_K5_FULL_CUBE", v316.build_raw_k5("FULL_CUBE")),
        ("V3_16_RAW_K5_EXACT_2_OF_4", v316.build_raw_k5("EXACT_2_OF_4")),
    ]


def exact_closed(status: str) -> bool:
    return status.startswith("ADMIT_EXACT_") or status.startswith("EXACT_UNSAT_")


def independent_two_factor_admission(factors: list[dict], core: list[int], comp: list[int]) -> tuple[bool, dict | None]:
    factor_ids = [str(factors[i]["id"]) for i in comp]
    scopes: dict[str, list[int]] = {}
    rows: dict[str, set[tuple[int, ...]]] = {}
    occurrences: dict[int, list[str]] = {}
    for i in comp:
        f = factors[i]
        scope, rel_rows = v316.residual_relation(f, core)
        fid = str(f["id"])
        scope = [int(v) for v in scope]
        rows_set = {tuple(int(x) for x in r) for r in rel_rows}
        expected = set()
        for mask in range(1 << len(scope)):
            bits = tuple((mask >> j) & 1 for j in range(len(scope)))
            if sum(bits) == 2:
                expected.add(bits)
        if rows_set != expected:
            return False, None
        scopes[fid] = scope
        rows[fid] = rows_set
        for v in scope:
            occurrences.setdefault(v, []).append(fid)
    if any(len(vs) != 2 or vs[0] == vs[1] for vs in occurrences.values()):
        return False, None
    edges = []
    for var, ends in sorted(occurrences.items()):
        u, v = sorted(ends)
        edges.append({"id": int(var), "u": u, "v": v})
    model = {
        "status": "READY_EXACT_TWO_FACTOR_COMPONENT",
        "vertices": sorted(factor_ids),
        "edges": edges,
        "edge_ids": sorted(int(v) for v in occurrences),
        "scopes": {k: scopes[k] for k in sorted(scopes)},
        "degree": {k: len(scopes[k]) for k in sorted(scopes)},
        "provenance": {"kind": "INDEPENDENT_GT2_CENSUS_ADMISSION"},
    }
    return True, model


def classify(raw: dict) -> dict[str, Any]:
    sha = raw_sha(raw)
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"raw_sha256": sha, "classification": "PREDECESSOR_NONREADY__NOT_A_RAW_GT2_OBSTRUCTION", "prepare_status": prep.get("status")}
    factors = prep["conditioned"]
    core = [int(v) for v in prep["core"]]
    before = v316.components(factors, core)
    gt_before = [c for c in before if len(c) > 2]
    if not gt_before:
        return {"raw_sha256": sha, "classification": "OUT_OF_SCOPE_NO_GT2", "prepare_status": "READY", "residual_component_sizes_before_normalization": [len(c) for c in before]}

    # Independent implementation of the v3.16 universal criterion using factor_semantics only.
    kept = []
    removed = []
    for f in factors:
        sem = v316.factor_semantics(f, core)
        if sem["universal"]:
            removed.append(str(f["id"]))
        else:
            kept.append(f)
    after = v316.components(kept, core) if kept else []
    gt_after = [c for c in after if len(c) > 2]
    base = {
        "raw_sha256": sha,
        "prepare_status": "READY",
        "residual_component_sizes_before_normalization": [len(c) for c in before],
        "removed_universal_factor_ids": sorted(removed),
        "residual_component_sizes_after_normalization": [len(c) for c in after],
    }
    if not gt_after:
        return {**base, "classification": "CLOSED_BY_EXACT_UNIVERSAL_NORMALIZATION", "closing_mechanism": "V3_16_EXACT_UNIVERSAL_RESIDUAL_RELATION_NORMALIZATION"}

    statuses = []
    for mechanism, fn in [
        ("V3_6_RESIDUAL_COMPONENT_LE2", v36.build),
        ("V3_8_SINGLE_VARIABLE_SEPARATOR", v38.build),
        ("V3_10_TWO_VARIABLE_SEPARATOR", v310.build),
        ("V3_14_FIXED_DEPTH_1_TO_2_TO_2", v314.build),
    ]:
        s = str(fn(raw).get("status"))
        statuses.append([mechanism, s])
        if exact_closed(s):
            return {**base, "classification": "CLOSED_BY_SEALED_RAW_CARRIER", "closing_mechanism": mechanism, "closing_status": s, "statuses": statuses}

    all_tf = True
    tf = []
    for comp in gt_after:
        admitted, model = independent_two_factor_admission(kept, core, comp)
        if not admitted or model is None:
            all_tf = False
            tf.append({"admitted": False, "factor_ids": sorted(str(kept[i]["id"]) for i in comp)})
            continue
        solved = v318.solve_model(model)
        exact = solved.get("status") in {"EXACT_SAT_TWO_FACTOR", "EXACT_UNSAT_TUTTE_BARRIER", "EXACT_UNSAT_LOCAL_DEGREE_LT_TWO"} and solved.get("certificate_verified") is True
        tf.append({"admitted": True, "solve_status": solved.get("status"), "certificate_verified": solved.get("certificate_verified"), "exact_closed": exact, "factor_ids": sorted(str(kept[i]["id"]) for i in comp)})
        all_tf = all_tf and exact
    if tf and all_tf:
        return {**base, "classification": "CLOSED_BY_SEALED_V3_18_EXACT_TWO_FACTOR_COMPONENT_CARRIER", "closing_mechanism": "V3_18_EXACT_TWO_FACTOR_COMPONENT_CARRIER", "statuses": statuses, "two_factor": tf}
    return {**base, "classification": "OPEN_AFTER_ALL_SEALED_CARRIERS", "statuses": statuses, "two_factor": tf}


def check(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    rows = []
    by_sha: dict[str, dict[str, Any]] = {}
    for name, raw in source_cases():
        r = {"name": name, **classify(raw)}
        rows.append(r)
        by_sha.setdefault(r["raw_sha256"], {"representative": r, "aliases": []})["aliases"].append(name)

    unique = []
    for sha, g in by_sha.items():
        z = dict(g["representative"])
        z["aliases"] = g["aliases"]
        unique.append(z)

    candidate_by_sha = {r["raw_sha256"]: r for r in candidate["unique_raw_census"]}
    comparison = {}
    for r in unique:
        c = candidate_by_sha.get(r["raw_sha256"])
        comparison[r["raw_sha256"]] = bool(
            c
            and c.get("classification") == r.get("classification")
            and c.get("closing_mechanism") == r.get("closing_mechanism")
            and sorted(c.get("aliases", [])) == sorted(r.get("aliases", []))
        )

    independent_open = [r for r in unique if r.get("classification") == "OPEN_AFTER_ALL_SEALED_CARRIERS"]
    expected_verdict = PASS_FOUND if independent_open else PASS_NONE
    unit = v314.depth_cap_unit_control()
    checks = {
        "source_guard": guard["ok"],
        "candidate_verdict_matches_independent": candidate.get("verdict") == expected_verdict,
        "same_unique_raw_count": candidate.get("unique_raw_count") == len(unique),
        "all_unique_rows_match_by_sha": all(comparison.values()),
        "same_unadmitted_count": candidate.get("unadmitted_raw_obstruction_count") == len(independent_open),
        "unit_only_k5_excluded": unit.get("unit_test_only") is True and unit.get("raw_reachability_authority") is False and candidate.get("unit_only_calibration", {}).get("eligible_for_first_real_obstruction") is False,
        "full_cube_normalized_away": any(r["name"] == "V3_16_RAW_K5_FULL_CUBE" and r["classification"] == "CLOSED_BY_EXACT_UNIVERSAL_NORMALIZATION" for r in rows),
        "exact_two_of_four_closed_by_v3_18": any(r["name"] == "V3_16_RAW_K5_EXACT_2_OF_4" and r["classification"] == "CLOSED_BY_SEALED_V3_18_EXACT_TWO_FACTOR_COMPONENT_CARRIER" for r in rows),
        "p_vs_np_open": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "general_sat_not_proved": candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "general_gt2_not_proved": candidate.get("scientific_firewall", {}).get("GENERAL_GT2_TRACTABILITY") == "NOT_PROVED",
    }
    verdict = expected_verdict if all(checks.values()) else FAIL
    return {
        "artifact_id": "JANUS-TRUMP-GT2-UNADMITTED-RAW-OBSTRUCTION-CENSUS-INDEPENDENT-CHECK-2026-09-16-v1.0",
        "authority": "INDEPENDENT_DIAGNOSTIC_CHECK_ONLY",
        "verdict": verdict,
        "source_guard": guard,
        "checks": checks,
        "candidate_helpers_imported": False,
        "unique_raw_census": unique,
        "row_match_by_sha": comparison,
        "independent_unadmitted_count": len(independent_open),
        "independent_first_open": independent_open[0] if independent_open else None,
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
            "SIZE4_BRANCHING_LICENSED": False,
            "EXTRA_RECURSION_AUTHORIZED": False,
        },
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate-json", required=True)
    a = p.parse_args()
    candidate = json.loads(Path(a.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    print(json.dumps(check(candidate), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
