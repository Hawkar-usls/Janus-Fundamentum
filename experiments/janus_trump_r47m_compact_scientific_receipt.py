from __future__ import annotations

import contextlib
import hashlib
import io
import json

import janus_trump_r47m_full_one_swap_depth1_then_depth2_falsifier as r47m


def canonical_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def run():
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        full = r47m.run()

    if full["gate"] != "JANUS_TRUMP_R47M_FULL_ONE_SWAP_DEPTH1_THEN_DEPTH2_FALSIFIER":
        raise AssertionError("R47M_COMPACT_GATE_DRIFT")
    fw = full["firewall"]
    assert fw["O4_UNIVERSAL_COVERAGE_FOR_FIXED_DEPTH2_GRAMMAR"] == "OPEN"
    assert fw["UNBOUNDED_DEPTH_POLYNOMIAL"] == "NOT_PROVED"
    assert fw["SAT_IN_P"] == "NOT_PROVED"
    assert fw["P_VS_NP"] == "OPEN"
    assert fw["TRUMP_finished"] is False

    compact = {
        "gate": full["gate"],
        "source_science": "BYTE_FOR_BYTE_FROZEN_R47M_RUN",
        "scientific_parent_commit": "11302552fdc17f6d07a2f93bafa44fa8ddecabd3",
        "verdict": full["verdict"],
        "counterexample_found": full["first_counterexample"] is not None,
        "inherited_integrity": full["inherited_integrity"],
        "metrics": full["metrics"],
        "firewall": fw,
    }

    c = full["first_counterexample"]
    if c is not None:
        failed = c["all_depth2_failed_pairs"]
        if not failed or any(row["accepted"] for row in failed):
            raise AssertionError("R47M_COMPACT_BAD_DEAD_LEDGER")
        if len(failed) != int(c["depth2_tested_pair_count"]):
            raise AssertionError("R47M_COMPACT_PAIR_COUNT_DRIFT")
        compact["counterexample"] = {
            "frontier_ordinal": c["frontier_ordinal"],
            "phase": c["phase"],
            "source_clause": c["source_clause"],
            "replacement_clause": c["replacement_clause"],
            "mutated_original_hash": c["mutated_original_hash"],
            "mutated_original_CLV": c["mutated_original_CLV"],
            "fixpoint_hash": c["fixpoint_hash"],
            "fixpoint_CLV": c["fixpoint_CLV"],
            "depth1_row_count": len(c["depth1_rows"]),
            "depth1_rows_sha256": canonical_hash(c["depth1_rows"]),
            "depth2_tested_pair_count": c["depth2_tested_pair_count"],
            "all_depth2_failed_pairs_sha256": canonical_hash(failed),
            "best_depth2_failure": c["best_depth2_failure"],
            "mutated_original_formula": c["mutated_original_formula"],
            "fixpoint_formula": c["fixpoint_formula"],
        }
        compact["hardest_depth2_rescue_if_no_counterexample"] = None
    else:
        compact["counterexample"] = None
        compact["hardest_depth2_rescue_if_no_counterexample"] = full["hardest_depth2_rescue_if_no_counterexample"]

    print(json.dumps(compact, sort_keys=True))
    return compact


if __name__ == "__main__":
    run()
