from __future__ import annotations

import contextlib
import hashlib
import io
import json

import janus_trump_r47r_targeted_two_swap_depth2_rescue_disruption as r47r


def canonical_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def run():
    # Harness-only extraction: execute the frozen R47R scientific search unchanged,
    # suppress its large stdout, and emit a compact receipt only.
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        full = r47r.run()

    if full["gate"] != "JANUS_TRUMP_R47R_TARGETED_TWO_SWAP_DEPTH2_RESCUE_DISRUPTION":
        raise AssertionError("R47R_COMPACT_GATE_DRIFT")
    if full["firewall"]["O4_UNIVERSAL_COVERAGE_FOR_FIXED_DEPTH2_GRAMMAR"] != "OPEN":
        raise AssertionError("R47R_COMPACT_O4_FIREWALL_DRIFT")
    if full["firewall"]["SAT_IN_P"] != "NOT_PROVED":
        raise AssertionError("R47R_COMPACT_SAT_FIREWALL_DRIFT")
    if full["firewall"]["P_VS_NP"] != "OPEN":
        raise AssertionError("R47R_COMPACT_PVNP_FIREWALL_DRIFT")

    compact = {
        "gate": full["gate"],
        "source_science": "BYTE_FOR_BYTE_FROZEN_R47R_RUN",
        "scientific_parent_commit": "fa73512161bb6686192154e65f3d0c4f4d93b880",
        "verdict": full["verdict"],
        "counterexample_found": full["first_counterexample"] is not None,
        "baseline_regression": full["baseline_regression"],
        "target_variables": full["target_variables"],
        "metrics": full["metrics"],
        "firewall": full["firewall"],
    }

    counterexample = full["first_counterexample"]
    if counterexample is not None:
        failed = counterexample["all_depth2_failed_pairs"]
        if not failed:
            raise AssertionError("R47R_COMPACT_EMPTY_FAILED_PAIR_LEDGER")
        if any(row["accepted"] for row in failed):
            raise AssertionError("R47R_COMPACT_ACCEPTED_PAIR_IN_DEAD_LEDGER")
        if len(failed) != int(counterexample["depth2_tested_pairs"]):
            raise AssertionError("R47R_COMPACT_LEDGER_COUNT_DRIFT")
        compact["counterexample"] = {
            "source_clause": counterexample["source_clause"],
            "replacement_clause": counterexample["replacement_clause"],
            "mutated_original_hash": counterexample["mutated_original_hash"],
            "mutated_original_CLV": counterexample["mutated_original_CLV"],
            "residual_hash": counterexample["residual_hash"],
            "residual_CLV": counterexample["residual_CLV"],
            "depth1_row_count": len(counterexample["depth1_rows"]),
            "depth1_rows_sha256": canonical_hash(counterexample["depth1_rows"]),
            "depth2_tested_pairs": counterexample["depth2_tested_pairs"],
            "all_depth2_failed": True,
            "all_depth2_failed_pairs_sha256": canonical_hash(failed),
            "best_depth2_failure": counterexample["best_depth2_failure"],
            "certified_lower_bound": counterexample["certified_lower_bound"],
            "mutated_original_formula": counterexample["mutated_original_formula"],
            "residual_formula": counterexample["residual_formula"],
        }
        compact["hardest_depth2_rescue_if_none"] = None
    else:
        compact["counterexample"] = None
        compact["hardest_depth2_rescue_if_none"] = full["hardest_depth2_rescue_if_none"]

    print(json.dumps(compact, sort_keys=True))
    return compact


if __name__ == "__main__":
    run()
