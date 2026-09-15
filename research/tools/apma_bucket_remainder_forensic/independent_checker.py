from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_bucket_remainder_forensic import remainder_forensic as cand
from research.tools.apma_bucket_single_then_pair_forensic import independent_checker as base
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-THEN-PAIR-THEN-REMAINDER-STRUCTURE-FORENSIC-INDEPENDENT-CHECK-2026-09-15-v1.0"
VERDICT = "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_THEN_PAIR_THEN_REMAINDER_STRUCTURE_FORENSIC"
CAND = Path("research/tools/apma_bucket_remainder_forensic/remainder_forensic.py")
CAND_BLOB = "fa4f94aaad7655786139d5726c2dcd0f8b1d555e"
BASE = Path("research/tools/apma_bucket_single_then_pair_forensic/independent_checker.py")
BASE_BLOB = "208af883ea4fc58c2e59ddc1658f683b8cccdc0f"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def scan_remainder(fs: list[dict], core: list[int]) -> dict:
    scan = base.pair_scan(fs, core)
    return {
        "factor_count": len(fs),
        "residual_scopes": [sorted(base.rscope(f, core)) for f in fs],
        "pair_cut_count": scan["pair_cut_count"],
        "admissible_pair_count": scan["admissible_pair_count"],
        "lexicographic_first_admissible_pair": scan["lexicographic_first_admissible_pair"],
    }


def independent_profile() -> dict:
    raw = pair_v310.no_pair_k4_control()
    parent = pair_v310.explain(raw)
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"status": "FAIL_PREP", "parent": parent.get("status")}

    target = next(c for c in prep["residual_components"] if len(c) > 2)
    fs0 = [prep["conditioned"][i] for i in target]
    variables = sorted(set().union(*(base.rscope(f, prep["core"]) for f in fs0)))
    records = []
    branch_cases = 0
    gt2_cases = 0
    gt2_admiss = 0

    for variable in variables:
        for value in (0, 1):
            fs_single = []
            for f in fs0:
                z = base.restrict_assignment(f, {variable: value})
                if z is None:
                    raise AssertionError("FROZEN_SINGLE_NONEMPTY")
                fs_single.append(z)
            scan1 = base.pair_scan(fs_single, prep["core"])
            if not scan1["pair_cuts"]:
                records.append({"single": [variable, value], "first_pair": None})
                continue
            first_pair = tuple(scan1["pair_cuts"][0]["pair"])
            branches = []
            for vals in ((0,0),(0,1),(1,0),(1,1)):
                branch_cases += 1
                assignment = {first_pair[0]: vals[0], first_pair[1]: vals[1]}
                rf = []
                empty = False
                for f in fs_single:
                    z = base.restrict_assignment(f, assignment)
                    if z is None:
                        empty = True
                        break
                    rf.append(z)
                if empty:
                    branches.append({"pair_values": list(vals), "exact_empty_unsat": True})
                    continue
                scopes = [base.rscope(f, prep["core"]) for f in rf]
                comps = base.bfs_components(scopes)
                gt2 = []
                for comp in comps:
                    if len(comp) > 2:
                        gt2_cases += 1
                        rr = scan_remainder([rf[i] for i in comp], prep["core"])
                        if rr["admissible_pair_count"] > 0:
                            gt2_admiss += 1
                        gt2.append(rr)
                branches.append({
                    "pair_values": list(vals),
                    "exact_empty_unsat": False,
                    "component_sizes": [len(c) for c in comps],
                    "gt2_remainders": gt2,
                })
            records.append({"single": [variable, value], "first_pair": list(first_pair), "branches": branches})

    summary = {
        "single_condition_count": len(records),
        "first_level_pair_branch_cases": branch_cases,
        "gt2_remainder_cases": gt2_cases,
        "gt2_remainders_with_admissible_pair": gt2_admiss,
        "all_gt2_remainders_have_admissible_pair": gt2_cases > 0 and gt2_admiss == gt2_cases,
        "component_size_patterns": sorted({tuple(b.get("component_sizes", [])) for r in records for b in r.get("branches", []) if not b.get("exact_empty_unsat", False)}),
        "remainder_factor_count_patterns": sorted({g["factor_count"] for r in records for b in r.get("branches", []) for g in b.get("gt2_remainders", [])}),
        "remainder_first_admissible_pairs": sorted({tuple(g["lexicographic_first_admissible_pair"]) for r in records for b in r.get("branches", []) for g in b.get("gt2_remainders", []) if g["lexicographic_first_admissible_pair"] is not None}),
    }
    return {"status": "READY", "parent": parent.get("status"), "records": records, "summary": summary}


def compact(records: list[dict]) -> list:
    out = []
    for r in records:
        branch_compact = []
        for b in r.get("branches", []):
            if b.get("exact_empty_unsat"):
                branch_compact.append([b["pair_values"], "EMPTY"])
            else:
                branch_compact.append([
                    b["pair_values"],
                    b["component_sizes"],
                    [[g["factor_count"], g["pair_cut_count"], g["admissible_pair_count"], g["lexicographic_first_admissible_pair"]] for g in b.get("gt2_remainders", [])],
                ])
        out.append([r["single"], r.get("first_pair"), branch_compact])
    return out


def run() -> dict:
    candidate = cand.run()
    ind = independent_profile()
    checks = {
        "G1_candidate_blob": blob(root() / CAND) == CAND_BLOB,
        "G1_base_independent_blob": blob(root() / BASE) == BASE_BLOB,
        "G1_candidate_guard": candidate.get("source_guard", {}).get("ok") is True,
        "G2_candidate_verdict": candidate.get("status") == VERDICT,
        "G2_independent_ready": ind.get("status") == "READY",
        "G3_parent_open_match": candidate.get("parent_terminal") == ind.get("parent") == "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR",
        "G4_summary_match": candidate.get("summary") == ind.get("summary"),
        "G5_records_compact_match": compact(candidate.get("records", [])) == compact(ind.get("records", [])),
        "G6_candidate_zero_solver": candidate["resource_receipt"]["solver_execution"] == 0,
        "G6_candidate_zero_pair_carrier": candidate["resource_receipt"]["pair_carrier_execution"] == 0,
        "G6_candidate_zero_3plus_join": candidate["resource_receipt"]["three_plus_join_chains_materialized"] == 0,
        "G6_candidate_zero_global_product": candidate["resource_receipt"]["global_residual_cartesian_products_materialized"] == 0,
        "G6_no_unbounded_recursion": candidate["resource_receipt"]["unbounded_recursive_search"] is False,
        "FW_p_vs_np": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "FW_general_sat": candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
    }
    verdict = VERDICT if all(checks.values()) else "FAIL_INDEPENDENT_MISMATCH"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__DIAGNOSTIC_ONLY",
        "verdict": verdict,
        "checks": checks,
        "candidate_summary": candidate.get("summary"),
        "independent_summary": ind.get("summary"),
        "candidate_compact": compact(candidate.get("records", [])),
        "independent_compact": compact(ind.get("records", [])),
        "independent_methods": {
            "componentization": "BFS",
            "single_and_pair_restriction": "INDEPENDENT_ASSIGNMENT_FILTER_PROJECT",
            "pair_scan": "INDEPENDENT_UNORDERED_PAIR_SCAN_FROM_PRIOR_INDEPENDENT_BACKEND",
            "candidate_pair_helpers_used": False
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE"
        }
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
