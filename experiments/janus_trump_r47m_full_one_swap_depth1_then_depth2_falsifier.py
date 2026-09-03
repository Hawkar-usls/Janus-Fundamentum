from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47k_extended_normalization_closure_one_swap_falsifier as r47k
import janus_trump_r47l_certified_two_dp_composition_rescue_or_barrier as r47l

BASE_SEED = 473383
BASE_N = 30
BASE_RATIO = 3.8
BASE_ORIGINAL_HASH = "31621a04517fa41a334187572001608dff9b338dc529d8a809b5ee95bccf9297"
ORDINAL55_SOURCE = (-23, 24, 25)
ORDINAL55_REPLACEMENT = (23, 24, -25)
ORDINAL55_RESIDUAL_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
ORDINAL55_EXPECTED_PAIR = (11, 20)
CONTINUATION_START = 56


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def compact_pair(original, first, second, first_var, second_var, pair_accepted):
    first_final = r33.canonical_formula(first["normalization"]["final_formula"])
    second_final = r33.canonical_formula(second["normalization"]["final_formula"])
    sat_reconstruction = r47l.reconstruct_pair_sat(original, first, second)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R47M_PAIR_SAT_RECONSTRUCTION_FAIL", first_var, second_var))
    return {
        "first_var": int(first_var),
        "second_var": int(second_var),
        "input_CLV": list(clv(original)),
        "first_final_CLV": list(clv(first_final)),
        "first_terminal": first["normalization"]["terminal"],
        "first_restart_count": int(first["normalization"]["restart_count"]),
        "first_replay_pass": True,
        "second_forced_DP_CLV": second["DP"]["measure_after_forced_DP"],
        "second_final_CLV": list(clv(second_final)),
        "second_terminal": second["normalization"]["terminal"],
        "second_restart_count": int(second["normalization"]["restart_count"]),
        "second_replay_pass": True,
        "pair_terminal": second["normalization"]["terminal"] is not None,
        "pair_descent": clv(second_final) < clv(original),
        "accepted": bool(pair_accepted),
        "SAT_reconstruction_pass": True,
    }


def depth2_scan(depth1_dead_formula, keep_all_failures=False):
    original = r33.canonical_formula(depth1_dead_formula)
    tested = 0
    best_failure = None
    all_failures = []

    for first_var in r33.variables(original):
        first = r47j.macro_candidate_fixpoint(original, int(first_var))
        if first is None:
            continue
        first_replay = r47j.independent_fixpoint_macro_replay(original, first)
        if not first_replay["pass"]:
            raise AssertionError(("R47M_FIRST_REPLAY_FAIL", first_var, first_replay))
        first_final = r33.canonical_formula(first["normalization"]["final_formula"])
        if first["normalization"]["terminal"] is not None or clv(first_final) < clv(original):
            raise AssertionError(("R47M_DEPTH1_DEAD_INTEGRITY_FAIL", first_var, clv(first_final), first["normalization"]["terminal"]))

        for second_var in r33.variables(first_final):
            if int(second_var) == int(first_var):
                continue
            second = r47j.macro_candidate_fixpoint(first_final, int(second_var))
            if second is None:
                continue
            second_replay = r47j.independent_fixpoint_macro_replay(first_final, second)
            if not second_replay["pass"]:
                raise AssertionError(("R47M_SECOND_REPLAY_FAIL", first_var, second_var, second_replay))
            second_final = r33.canonical_formula(second["normalization"]["final_formula"])
            pair_accepted = second["normalization"]["terminal"] is not None or clv(second_final) < clv(original)
            tested += 1
            row = compact_pair(original, first, second, first_var, second_var, pair_accepted)
            if pair_accepted:
                return {
                    "covered": True,
                    "tested_pairs": tested,
                    "selected_pair": [int(first_var), int(second_var)],
                    "selected": row,
                    "best_failure_before_accept": best_failure,
                    "all_failures": None,
                }
            if best_failure is None or (tuple(row["second_final_CLV"]), row["first_var"], row["second_var"]) < (tuple(best_failure["second_final_CLV"]), best_failure["first_var"], best_failure["second_var"]):
                best_failure = row
            if keep_all_failures:
                all_failures.append(row)

    return {
        "covered": False,
        "tested_pairs": tested,
        "selected_pair": None,
        "selected": None,
        "best_failure_before_accept": best_failure,
        "all_failures": all_failures if keep_all_failures else None,
    }


def verify_ordinal55(original):
    target = None
    for ordinal, (phase, source, replacement, mutated) in enumerate(r47k.frontier(original), 1):
        if ordinal != 55:
            continue
        target = (phase, source, replacement, mutated)
        break
    if target is None:
        raise AssertionError("R47M_ORDINAL55_MISSING")
    phase, source, replacement, mutated = target
    if tuple(source) != ORDINAL55_SOURCE or tuple(replacement) != ORDINAL55_REPLACEMENT or mutated is None:
        raise AssertionError(("R47M_ORDINAL55_MUTATION_DRIFT", source, replacement))
    reached = r47f.reachable_fixpoint(mutated)
    if reached is None:
        raise AssertionError("R47M_ORDINAL55_NO_FIXPOINT")
    fixpoint = r33.canonical_formula(reached["formula"])
    if r47f.formula_hash(fixpoint) != ORDINAL55_RESIDUAL_HASH:
        raise AssertionError(("R47M_ORDINAL55_HASH_DRIFT", r47f.formula_hash(fixpoint)))
    depth1 = r47k.first_extended_accept(fixpoint)
    if depth1["covered"]:
        raise AssertionError(("R47M_ORDINAL55_DEPTH1_DRIFT", depth1["selected_var"]))
    depth2 = depth2_scan(fixpoint)
    if not depth2["covered"] or tuple(depth2["selected_pair"]) != ORDINAL55_EXPECTED_PAIR:
        raise AssertionError(("R47M_ORDINAL55_DEPTH2_DRIFT", depth2))
    return {
        "phase": phase,
        "source_clause": list(source),
        "replacement_clause": list(replacement),
        "residual_hash": ORDINAL55_RESIDUAL_HASH,
        "residual_CLV": list(clv(fixpoint)),
        "depth1_covered": False,
        "depth2_selected_pair": depth2["selected_pair"],
        "depth2_final_CLV": depth2["selected"]["second_final_CLV"],
        "depth2_tested_pairs": depth2["tested_pairs"],
    }


def counterexample_receipt(ordinal, phase, source, replacement, mutated, reached, fixpoint, depth1, depth2):
    # Re-run depth2 only for the dead witness with complete failure ledger.
    full_depth2 = depth2_scan(fixpoint, keep_all_failures=True)
    if full_depth2["covered"]:
        raise AssertionError("R47M_COUNTEREXAMPLE_REPLAY_BECAME_COVERED")
    return {
        "frontier_ordinal": int(ordinal),
        "phase": phase,
        "source_clause": list(source),
        "replacement_clause": list(replacement),
        "mutated_original_hash": r47f.formula_hash(mutated),
        "mutated_original_CLV": list(clv(mutated)),
        "mutated_original_formula": [list(c) for c in mutated],
        "reachability_trajectory": reached["trajectory"],
        "fixpoint_hash": r47f.formula_hash(fixpoint),
        "fixpoint_CLV": list(clv(fixpoint)),
        "fixpoint_formula": [list(c) for c in fixpoint],
        "depth1_rows": depth1["rows_prefix"],
        "depth2_tested_pair_count": full_depth2["tested_pairs"],
        "all_depth2_failed_pairs": full_depth2["all_failures"],
        "best_depth2_failure": full_depth2["best_failure_before_accept"],
    }


def run():
    original = r33.deterministic_random_3cnf(BASE_SEED, n=BASE_N, ratio=BASE_RATIO)
    if r47f.formula_hash(original) != BASE_ORIGINAL_HASH:
        raise AssertionError("R47M_BASE_ORIGINAL_HASH_DRIFT")

    ordinal55 = verify_ordinal55(original)

    metrics = {
        "inherited_prefix_positions_1_54": 54,
        "inherited_prefix_depth2_safe_via_depth1": True,
        "ordinal55_depth2_regression_covered": True,
        "continuation_frontier_positions_seen": 0,
        "continuation_mutants_generated": 0,
        "continuation_duplicate_mutations_skipped": 0,
        "continuation_semantic_or_nonfixpoint": 0,
        "continuation_reachable_fixpoints": 0,
        "continuation_unique_fixpoints": 0,
        "continuation_depth1_covered": 0,
        "continuation_depth1_dead": 0,
        "continuation_depth2_rescued": 0,
        "continuation_depth2_dead": 0,
        "continuation_depth2_pairs_tested": 0,
    }
    seen = set()
    first_counterexample = None
    hardest_depth2_rescue = None

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47k.frontier(original), 1):
        if ordinal < CONTINUATION_START:
            continue
        metrics["continuation_frontier_positions_seen"] += 1
        if mutated is None:
            metrics["continuation_duplicate_mutations_skipped"] += 1
            continue
        metrics["continuation_mutants_generated"] += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["continuation_semantic_or_nonfixpoint"] += 1
            continue
        metrics["continuation_reachable_fixpoints"] += 1
        fixpoint = r33.canonical_formula(reached["formula"])
        fh = r47f.formula_hash(fixpoint)
        if fh in seen:
            continue
        seen.add(fh)
        metrics["continuation_unique_fixpoints"] += 1

        depth1 = r47k.first_extended_accept(fixpoint)
        if depth1["covered"]:
            metrics["continuation_depth1_covered"] += 1
            continue

        metrics["continuation_depth1_dead"] += 1
        depth2 = depth2_scan(fixpoint)
        metrics["continuation_depth2_pairs_tested"] += int(depth2["tested_pairs"])
        if depth2["covered"]:
            metrics["continuation_depth2_rescued"] += 1
            record = {
                "frontier_ordinal": int(ordinal),
                "phase": phase,
                "source_clause": list(source),
                "replacement_clause": list(replacement),
                "mutated_original_hash": r47f.formula_hash(mutated),
                "fixpoint_hash": fh,
                "fixpoint_CLV": list(clv(fixpoint)),
                "depth2_tested_pairs": int(depth2["tested_pairs"]),
                "selected_pair": depth2["selected_pair"],
                "selected": depth2["selected"],
            }
            if hardest_depth2_rescue is None or (record["depth2_tested_pairs"], tuple(record["fixpoint_CLV"]), record["fixpoint_hash"]) > (hardest_depth2_rescue["depth2_tested_pairs"], tuple(hardest_depth2_rescue["fixpoint_CLV"]), hardest_depth2_rescue["fixpoint_hash"]):
                hardest_depth2_rescue = record
            continue

        metrics["continuation_depth2_dead"] += 1
        first_counterexample = counterexample_receipt(ordinal, phase, source, replacement, mutated, reached, fixpoint, depth1, depth2)
        break

    if first_counterexample is not None:
        verdict = "EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_FIXED_DEPTH2_GRAMMAR_FOUND"
    else:
        verdict = "FULL_FROZEN_ONE_SWAP_FRONTIER_COVERED_BY_DEPTH1_OR_DEPTH2__O4_STILL_OPEN"

    out = {
        "gate": "JANUS_TRUMP_R47M_FULL_ONE_SWAP_DEPTH1_THEN_DEPTH2_FALSIFIER",
        "verdict": verdict,
        "inherited_integrity": {
            "R47K_prefix_positions_1_54_authorized": True,
            "ordinal55": ordinal55,
        },
        "metrics": metrics,
        "first_counterexample": first_counterexample,
        "hardest_depth2_rescue_if_no_counterexample": hardest_depth2_rescue,
        "interpretation": {
            "depth1_first_policy": True,
            "depth2_only_on_depth1_dead": True,
            "finite_full_frontier_coverage_if_true_does_not_prove_O4": True,
            "unbounded_depth_not_authorized": True,
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_FIXED_DEPTH2_GRAMMAR": "OPEN",
            "UNBOUNDED_DEPTH_POLYNOMIAL": "NOT_PROVED",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
