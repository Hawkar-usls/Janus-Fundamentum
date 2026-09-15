from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_bucket_single_then_pair_forensic import single_then_pair_forensic as prev
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-SINGLE-THEN-PAIR-THEN-REMAINDER-STRUCTURE-FORENSIC-2026-09-15-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_THEN_PAIR_THEN_REMAINDER_STRUCTURE_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "94bb5964dc9893edcb8dfe721f7fd99282d02896"
PREV = Path("research/tools/apma_bucket_single_then_pair_forensic/single_then_pair_forensic.py")
PREV_BLOB = "72e48e12afb67a7df12af872748991ddd81a8a22"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "previous_diagnostic_blob": blob(r / PREV) == PREV_BLOB,
        "parent_v3_12_exists": (r / "registry/TRUMP_CURRENT_STATE_2026-09-15_v3.12.json").exists(),
    }
    return {"ok": all(checks.values()), "checks": checks}


def restrict_assignment(f: dict, assignment: dict[int, int]) -> dict | None:
    scope = [int(v) for v in f["scope"]]
    rows = [tuple(int(x) for x in r) for r in f["rows"]]
    positions = [(i, v) for i, v in enumerate(scope) if v in assignment]
    keep = [i for i, v in enumerate(scope) if v not in assignment]
    survivors = set()
    for row in rows:
        if all(row[i] == assignment[v] for i, v in positions):
            survivors.add(tuple(row[i] for i in keep))
    if not survivors:
        return None
    return {**f, "scope": [scope[i] for i in keep], "rows": sorted(survivors)}


def component_factors(fs: list[dict], core: list[int]) -> list[tuple[list[int], list[dict]]]:
    scopes = [prev.rscope(f, core) for f in fs]
    comps = prev.components(scopes)
    return [(comp, [fs[i] for i in comp]) for comp in comps]


def scan_remainder(fs: list[dict], core: list[int]) -> dict:
    scan = prev.scan_pairs(fs, core)
    return {
        "factor_count": len(fs),
        "residual_scopes": [sorted(prev.rscope(f, core)) for f in fs],
        "pair_cut_count": scan["pair_cut_count"],
        "admissible_pair_count": scan["admissible_pair_count"],
        "lexicographic_first_admissible_pair": scan["lexicographic_first_admissible_pair"],
        "admissible_pairs": scan["admissible_pairs"],
    }


def run() -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard}

    raw = pair_v310.no_pair_k4_control()
    parent = pair_v310.explain(raw)
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"artifact_id": ARTIFACT_ID, "status": "FAIL_PARENT_PREP", "parent": parent.get("status"), "prep": prep.get("status")}

    target = next(c for c in prep["residual_components"] if len(c) > 2)
    fs0 = [prep["conditioned"][i] for i in target]
    variables = sorted(set().union(*(prev.rscope(f, prep["core"]) for f in fs0)))
    records = []
    first_level_branch_cases = 0
    gt2_remainder_cases = 0
    gt2_remainders_with_admissible_pair = 0

    for variable in variables:
        for value in (0, 1):
            fs_single = []
            for f in fs0:
                z = restrict_assignment(f, {variable: value})
                if z is None:
                    raise AssertionError("FROZEN_PARENT_SAID_SINGLE_CONDITION_NONEMPTY")
                fs_single.append(z)
            first_scan = prev.scan_pairs(fs_single, prep["core"])
            if not first_scan["pair_cuts"]:
                records.append({"single": [variable, value], "first_pair": None, "error": "NO_RAW_PAIR_CUT"})
                continue
            first_pair = tuple(first_scan["pair_cuts"][0]["pair"])
            branch_records = []
            for pair_values in ((0,0),(0,1),(1,0),(1,1)):
                first_level_branch_cases += 1
                fs_pair = []
                empty = False
                assignment = {first_pair[0]: pair_values[0], first_pair[1]: pair_values[1]}
                for f in fs_single:
                    z = restrict_assignment(f, assignment)
                    if z is None:
                        empty = True
                        break
                    fs_pair.append(z)
                if empty:
                    branch_records.append({"pair_values": list(pair_values), "exact_empty_unsat": True})
                    continue
                comps = component_factors(fs_pair, prep["core"])
                sizes = [len(comp) for comp, _ in comps]
                gt2 = []
                for comp, cfs in comps:
                    if len(comp) > 2:
                        gt2_remainder_cases += 1
                        rr = scan_remainder(cfs, prep["core"])
                        if rr["admissible_pair_count"] > 0:
                            gt2_remainders_with_admissible_pair += 1
                        gt2.append(rr)
                branch_records.append({
                    "pair_values": list(pair_values),
                    "exact_empty_unsat": False,
                    "component_sizes": sizes,
                    "gt2_remainders": gt2,
                })
            records.append({
                "single": [variable, value],
                "first_pair": list(first_pair),
                "first_pair_directly_admissible": first_scan["pair_cuts"][0] in first_scan["admissible_pairs"],
                "branches": branch_records,
            })

    summary = {
        "single_condition_count": len(records),
        "first_level_pair_branch_cases": first_level_branch_cases,
        "gt2_remainder_cases": gt2_remainder_cases,
        "gt2_remainders_with_admissible_pair": gt2_remainders_with_admissible_pair,
        "all_gt2_remainders_have_admissible_pair": gt2_remainder_cases > 0 and gt2_remainders_with_admissible_pair == gt2_remainder_cases,
        "component_size_patterns": sorted({tuple(b.get("component_sizes", [])) for r in records for b in r.get("branches", []) if not b.get("exact_empty_unsat", False)}),
        "remainder_factor_count_patterns": sorted({g["factor_count"] for r in records for b in r.get("branches", []) for g in b.get("gt2_remainders", [])}),
        "remainder_first_admissible_pairs": sorted({tuple(g["lexicographic_first_admissible_pair"]) for r in records for b in r.get("branches", []) for g in b.get("gt2_remainders", []) if g["lexicographic_first_admissible_pair"] is not None}),
    }
    ok = parent.get("status") == "OPEN_NO_ADMISSIBLE_RESIDUAL_TWO_VARIABLE_SEPARATOR" and len(records) == 12 and first_level_branch_cases == 48
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": "PASS_DIAGNOSTIC_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_SINGLE_THEN_PAIR_THEN_REMAINDER_STRUCTURE_FORENSIC" if ok else "FAIL_DIAGNOSTIC",
        "source_guard": guard,
        "parent_terminal": parent.get("status"),
        "records": records,
        "summary": summary,
        "resource_receipt": {
            "sat_branch_execution": 0,
            "solver_execution": 0,
            "pair_carrier_execution": 0,
            "three_plus_join_chains_materialized": 0,
            "global_residual_cartesian_products_materialized": 0,
            "unbounded_recursive_search": False,
            "budget_raised": False,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
