from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i

GATE = "JANUS_TRUMP_R49J_FULL_ONE_SWAP_BIPOLAR_NONTAUTO_WIDTH5_CORE_SHARD"


def compact(row):
    return {
        "frontier_ordinal": int(row["provenance"]["frontier_ordinal"]),
        "phase": row["provenance"]["phase"],
        "root_hash": row["root_hash"],
        "root_CLV": row["root_CLV"],
        "root_max_width": int(row["root_max_width"]),
        "variable_count": int(row["variable_count"]),
        "pure_variables": row["pure_variables"],
        "safe_bipolar_pivots": row["safe_bipolar_pivots"],
        "minimum_chi_star": row["minimum_chi_star"],
        "maximum_chi_star": row["maximum_chi_star"],
        "is_core": bool(row["is_bipolar_nontauto_cross_union_width5_core"]),
    }


def run(start_ordinal: int, end_ordinal: int):
    if start_ordinal < 1 or end_ordinal < start_ordinal:
        raise AssertionError(("R49J_BAD_RANGE", start_ordinal, end_ordinal))

    center_original, _, _ = r47x.load_center_original()
    seen_fixpoints = set()
    rows = []
    first_core = None
    metrics = {
        "frontier_positions_in_range": 0,
        "mutants_generated": 0,
        "duplicate_mutations_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "duplicate_fixpoints_skipped": 0,
        "unique_fixpoints_inspected": 0,
        "roots_with_pure_literal": 0,
        "roots_with_chi_star_safe_bipolar_pivot": 0,
        "cores_found": 0,
    }

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal < start_ordinal:
            continue
        if ordinal > end_ordinal:
            break
        metrics["frontier_positions_in_range"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue
        metrics["mutants_generated"] += 1
        r47x.validate_exact_3cnf(mutated)
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = r49i.canon(reached["formula"])
        rh = r49i.fhash(root)
        if rh in seen_fixpoints:
            metrics["duplicate_fixpoints_skipped"] += 1
            continue
        seen_fixpoints.add(rh)
        provenance = {
            "kind": "FULL_ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
        }
        row = r49i.inspect_state(root, provenance, ordinal)
        metrics["unique_fixpoints_inspected"] += 1
        if row["pure_variables"]:
            metrics["roots_with_pure_literal"] += 1
        if row["safe_bipolar_pivots"]:
            metrics["roots_with_chi_star_safe_bipolar_pivot"] += 1
        if row["is_bipolar_nontauto_cross_union_width5_core"]:
            metrics["cores_found"] += 1
            first_core = row
            rows.append(compact(row))
            break
        rows.append(compact(row))

    return {
        "gate": GATE,
        "verdict": "EXPLICIT_REACHABLE_BIPOLAR_NONTAUTO_WIDTH5_CORE_FOUND" if first_core is not None else "NO_CORE_IN_SHARD__FINITE_ONLY",
        "shard": {"start_ordinal": int(start_ordinal), "end_ordinal": int(end_ordinal)},
        "metrics": metrics,
        "first_core": first_core,
        "rows": rows,
        "interpretation": {
            "one_core_refutes_universal_easy_pure_or_chi_star_safe_pivot_existence": first_core is not None,
            "no_core_in_this_finite_shard_proves_universal_easy_lane_existence": False,
            "search_is_full_one_swap_frontier_when_all_shards_1_through_798_complete": True,
        },
        "firewall": {
            "R49H_LOCAL_SAFE_PIVOT_LEMMA": "UNCHANGED_PROVED_IN_SCOPE",
            "UNIVERSAL_EASY_LANE_EXISTENCE": "REFUTED" if first_core is not None else "NOT_PROVED",
            "PARTIAL_R47J_DIRECT_W4_STEP_COVERAGE": "OPEN",
            "DIRECT_W4_STEP_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = run(a.start, a.end)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "shard": out["shard"],
        "metrics": out["metrics"],
        "first_core": out["first_core"],
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
