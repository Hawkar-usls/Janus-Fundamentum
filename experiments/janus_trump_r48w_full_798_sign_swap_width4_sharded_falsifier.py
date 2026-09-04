from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48q_width4_full_frozen_frontier_falsifier as r48q

GATE = "JANUS_TRUMP_R48W_FULL_798_SIGN_SWAP_WIDTH4_SHARDED_FALSIFIER"
PARENT_R48Q_SEAL = "b6c94caf2883b49e52a887b2c0bd13590afc96e8"
EXPECTED_SOURCE_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
EXPECTED_SOURCE_CLV = (114, 342, 30)
EXPECTED_TOTAL_FRONTIER = 798
PREFIX_END = 64
ATTACK_START = 65
ATTACK_END = 798
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return tuple(r33.measure(canon(f)))


def fhash(f):
    return r48q.formula_hash(canon(f))


def compact_covered(record):
    return {
        "covered": True,
        "root_hash": record["root_hash"],
        "root_CLV": record["root_CLV"],
        "root_max_width": record["root_max_width"],
        "provenance": record["provenance"],
        "candidate_probe_count": int(record["candidate_probe_count"]),
        "selected_step_count": len(record["selected_path"]),
        "selected_pivots": [int(x["var"]) for x in record["selected_path"]],
        "max_persisted_width": int(record["max_persisted_width"]),
        "terminal": record["terminal"],
    }


def run(start: int, end: int):
    if not (ATTACK_START <= start <= end <= ATTACK_END):
        raise AssertionError(("R48W_INVALID_SHARD_RANGE", start, end))

    original, _, _ = r47x.load_center_original()
    original = canon(original)
    if fhash(original) != EXPECTED_SOURCE_HASH:
        raise AssertionError(("R48W_SOURCE_HASH_DRIFT", fhash(original)))
    if clv(original) != EXPECTED_SOURCE_CLV:
        raise AssertionError(("R48W_SOURCE_CLV_DRIFT", clv(original)))

    frontier = list(r47x.frontier(original))
    if len(frontier) != EXPECTED_TOTAL_FRONTIER:
        raise AssertionError(("R48W_FRONTIER_LENGTH_DRIFT", len(frontier), EXPECTED_TOTAL_FRONTIER))

    metrics = {
        "assigned_positions": int(end - start + 1),
        "frontier_positions_seen": 0,
        "mutants_generated": 0,
        "duplicate_mutations_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "duplicate_fixpoints_within_shard": 0,
        "unique_reachable_roots_evaluated": 0,
        "covered_roots": 0,
        "width4_obstruction_roots": 0,
        "total_candidate_probes": 0,
        "total_selected_steps": 0,
    }
    seen = set()
    covered_records = []
    first_obstruction = None

    for ordinal in range(start, end + 1):
        phase, source, replacement, mutated = frontier[ordinal - 1]
        metrics["frontier_positions_seen"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue

        r47x.validate_exact_3cnf(mutated)
        metrics["mutants_generated"] += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue

        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        rh = fhash(root)
        if rh in seen:
            metrics["duplicate_fixpoints_within_shard"] += 1
            continue
        seen.add(rh)

        provenance = {
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": fhash(mutated),
        }
        record = r48q.run_width4_root(root, provenance)
        metrics["unique_reachable_roots_evaluated"] += 1
        metrics["total_candidate_probes"] += int(record["candidate_probe_count"])
        metrics["total_selected_steps"] += len(record["selected_path"])

        if not record["covered"]:
            metrics["width4_obstruction_roots"] += 1
            first_obstruction = record
            break

        metrics["covered_roots"] += 1
        covered_records.append(compact_covered(record))

    verdict = (
        "EXPLICIT_REACHABLE_WIDTH4_OBSTRUCTION_FOUND"
        if first_obstruction is not None
        else "SHARD_COVERED__FINITE_ONLY"
    )
    hardest = max(
        covered_records,
        key=lambda x: (
            int(x["candidate_probe_count"]),
            int(x["selected_step_count"]),
            tuple(x["root_CLV"]),
            x["root_hash"],
        ),
        default=None,
    )
    maximum_observed_persisted_width = max(
        [int(x["max_persisted_width"]) for x in covered_records]
        + ([] if first_obstruction is None else [int(first_obstruction["max_persisted_width"])]),
        default=None,
    )

    return {
        "gate": GATE,
        "parent_R48Q_seal_commit": PARENT_R48Q_SEAL,
        "verdict": verdict,
        "width_cap": WIDTH_CAP,
        "shard": {"start": int(start), "end": int(end)},
        "source": {
            "hash": EXPECTED_SOURCE_HASH,
            "CLV": list(EXPECTED_SOURCE_CLV),
            "expected_total_frontier_positions": EXPECTED_TOTAL_FRONTIER,
            "sealed_prefix_end": PREFIX_END,
        },
        "metrics": metrics,
        "maximum_observed_persisted_width": maximum_observed_persisted_width,
        "hardest_covered_root": hardest,
        "first_obstruction": first_obstruction,
        "covered_roots": covered_records,
        "interpretation": {
            "finite_shard_only": True,
            "one_reachable_obstruction_refutes_universal_W4_for_frozen_grammar": True,
            "shard_success_proves_universal_W4": False,
            "cross_shard_deduplication_not_required_for_correctness": True,
        },
        "firewall": {
            "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED_UNLESS_REFUTED_BY_THIS_GATE",
            "UNIVERSAL_CONSTANT_WIDTH_COVERAGE": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--start", type=int, required=True)
    p.add_argument("--end", type=int, required=True)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    out = run(a.start, a.end)
    if a.output is not None:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    obstruction = out["first_obstruction"]
    print(json.dumps({
        "gate": out["gate"],
        "verdict": out["verdict"],
        "shard": out["shard"],
        "metrics": out["metrics"],
        "maximum_observed_persisted_width": out["maximum_observed_persisted_width"],
        "hardest_covered_root": out["hardest_covered_root"],
        "first_obstruction": None if obstruction is None else {
            "root_hash": obstruction["root_hash"],
            "root_CLV": obstruction["root_CLV"],
            "provenance": obstruction["provenance"],
            "selected_pivots": [int(x["var"]) for x in obstruction["selected_path"]],
            "obstruction_kind": obstruction["obstruction"]["kind"],
            "state_hash": obstruction["obstruction"]["state_hash"],
            "state_CLV": obstruction["obstruction"]["state_CLV"],
            "state_max_width": obstruction["obstruction"]["state_max_width"],
        },
        "firewall": out["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
