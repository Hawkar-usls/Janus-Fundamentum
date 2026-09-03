from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j

BASE_SEED = 473383
BASE_N = 30
BASE_RATIO = 3.8
BASE_ORIGINAL_HASH = "31621a04517fa41a334187572001608dff9b338dc529d8a809b5ee95bccf9297"
BASE_FIXPOINT_HASH = "3130377ee52a6d6abf01f44fdc5f1a96cf83d701e30f70debea26cd347b7a495"
R47I_SOURCE = (-7, -10, -26)
R47I_REPLACEMENT = (-7, 10, 26)
R47I_MUTATED_HASH = "bcf7813aab117047cfe0d6613a0c9704a163102e4296c4b67cbea2e86016fd89"
R47I_FIXPOINT_HASH = "c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"
R47I_EXPECTED_EXTENDED_ACCEPTED = (13, 25, 28, 29)


def compact_extended_candidate(before, candidate, replay_pass=None):
    return {
        "var": int(candidate["var"]),
        "input_CLV": candidate["input_CLV"],
        "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
        "final_CLV": candidate["final_CLV"],
        "terminal": candidate["normalization"]["terminal"],
        "round_count": int(candidate["normalization"]["round_count"]),
        "restart_count": int(candidate["normalization"]["restart_count"]),
        "net_CLV_descent": bool(candidate["net_CLV_descent"]),
        "accepted": bool(candidate["accepted"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "independent_macro_replay_pass": replay_pass,
    }


def first_extended_accept(fixpoint):
    before = r33.canonical_formula(fixpoint)
    rows = []
    checked = 0
    for var in r33.variables(before):
        checked += 1
        candidate = r47j.macro_candidate_fixpoint(before, int(var))
        if candidate is None:
            rows.append({"var": int(var), "candidate": False, "accepted": False})
            continue
        if not candidate["DP_independent_replay_pass"] or not candidate["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R47K_CANDIDATE_INTEGRITY_FAIL", var))
        if candidate["accepted"]:
            replay = r47j.independent_fixpoint_macro_replay(before, candidate)
            if not replay["pass"]:
                raise AssertionError(("R47K_ACCEPTED_REPLAY_FAIL", var, replay))
            rows.append(compact_extended_candidate(before, candidate, True))
            return {
                "covered": True,
                "variables_checked": checked,
                "total_variables": len(r33.variables(before)),
                "selected_var": int(var),
                "selected": rows[-1],
                "rows_prefix": rows,
            }
        rows.append(compact_extended_candidate(before, candidate, None))
    return {
        "covered": False,
        "variables_checked": checked,
        "total_variables": len(r33.variables(before)),
        "selected_var": None,
        "selected": None,
        "rows_prefix": rows,
    }


def full_extended_scan(fixpoint):
    before = r33.canonical_formula(fixpoint)
    rows = []
    accepted = []
    for var in r33.variables(before):
        candidate = r47j.macro_candidate_fixpoint(before, int(var))
        if candidate is None:
            rows.append({"var": int(var), "candidate": False, "accepted": False})
            continue
        replay_pass = None
        if candidate["accepted"]:
            replay = r47j.independent_fixpoint_macro_replay(before, candidate)
            if not replay["pass"]:
                raise AssertionError(("R47K_FULL_SCAN_REPLAY_FAIL", var, replay))
            replay_pass = True
            accepted.append(int(var))
        rows.append(compact_extended_candidate(before, candidate, replay_pass))
    return {"accepted_pivots": accepted, "rows": rows}


def old_accepted_pivots(fixpoint):
    before = r33.canonical_formula(fixpoint)
    accepted = []
    for var in r33.variables(before):
        candidate = r45a.macro_candidate_for_var(before, int(var))
        if candidate is not None and candidate["accepted"]:
            accepted.append(int(var))
    return accepted


def frontier(original):
    sources_v7 = [c for c in original if any(abs(l) == 7 for l in c)]
    sources_other = [c for c in original if c not in sources_v7]
    for phase, sources in (("PIVOT7_TOUCHING", sources_v7), ("REMAINING_SUPPORTS", sources_other)):
        for source in sources:
            for replacement in r47i.signed_same_support_variants(source):
                mutated = r47i.mutate_one_clause(original, source, replacement)
                if mutated is None:
                    yield phase, source, replacement, None
                else:
                    yield phase, source, replacement, mutated


def score_hardest(record):
    return (
        int(record["variables_checked_to_first_accept"]),
        -int(record.get("accepted_pivot_count", 10**9)),
        str(record["fixpoint_hash"]),
    )


def compact_covered_record(ordinal, phase, source, replacement, mutated, reached, scan):
    fixpoint = r33.canonical_formula(reached["formula"])
    return {
        "frontier_ordinal": int(ordinal),
        "phase": phase,
        "source_clause": list(source),
        "replacement_clause": list(replacement),
        "mutated_original_hash": r47f.formula_hash(mutated),
        "mutated_original_CLV": list(r33.measure(mutated)),
        "fixpoint_hash": r47f.formula_hash(fixpoint),
        "fixpoint_CLV": list(r33.measure(fixpoint)),
        "variables_checked_to_first_accept": int(scan["variables_checked"]),
        "total_fixpoint_variables": int(scan["total_variables"]),
        "selected_var": scan["selected_var"],
        "selected": scan["selected"],
        "rows_prefix": scan["rows_prefix"],
        "trajectory": reached["trajectory"],
    }


def run():
    original = r33.deterministic_random_3cnf(BASE_SEED, n=BASE_N, ratio=BASE_RATIO)
    if r47f.formula_hash(original) != BASE_ORIGINAL_HASH:
        raise AssertionError("R47K_BASE_ORIGINAL_HASH_DRIFT")
    base_reached = r47f.reachable_fixpoint(original)
    if base_reached is None:
        raise AssertionError("R47K_BASE_NO_FIXPOINT")
    base_fixpoint = r33.canonical_formula(base_reached["formula"])
    if r47f.formula_hash(base_fixpoint) != BASE_FIXPOINT_HASH:
        raise AssertionError("R47K_BASE_FIXPOINT_HASH_DRIFT")
    base_scan = first_extended_accept(base_fixpoint)
    if not base_scan["covered"]:
        raise AssertionError("R47K_BASE_NOT_COVERED")

    r47i_mutant = r47i.mutate_one_clause(original, R47I_SOURCE, R47I_REPLACEMENT)
    if r47i_mutant is None or r47f.formula_hash(r47i_mutant) != R47I_MUTATED_HASH:
        raise AssertionError("R47K_R47I_MUTANT_HASH_DRIFT")
    r47i_reached = r47f.reachable_fixpoint(r47i_mutant)
    if r47i_reached is None:
        raise AssertionError("R47K_R47I_MUTANT_NO_FIXPOINT")
    r47i_fixpoint = r33.canonical_formula(r47i_reached["formula"])
    if r47f.formula_hash(r47i_fixpoint) != R47I_FIXPOINT_HASH:
        raise AssertionError("R47K_R47I_FIXPOINT_HASH_DRIFT")
    old_accept = old_accepted_pivots(r47i_fixpoint)
    if old_accept:
        raise AssertionError(("R47K_OLD_GRAMMAR_COUNTEREXAMPLE_DRIFT", old_accept))
    r47i_extended_full = full_extended_scan(r47i_fixpoint)
    if tuple(r47i_extended_full["accepted_pivots"]) != R47I_EXPECTED_EXTENDED_ACCEPTED:
        raise AssertionError(("R47K_R47J_REGRESSION_DRIFT", r47i_extended_full["accepted_pivots"]))

    metrics = {
        "frontier_positions": 0,
        "mutants_generated": 0,
        "mutants_skipped_duplicate": 0,
        "semantic_or_nonfixpoint_mutants": 0,
        "reachable_fixpoints": 0,
        "unique_reachable_fixpoints": 0,
        "extended_covered_fixpoints": 0,
        "extended_macro_dead_fixpoints": 0,
        "phase": {},
    }
    seen_fixpoints = set()
    first_counterexample = None
    hardest = None
    hardest_primary = -1

    for ordinal, (phase, source, replacement, mutated) in enumerate(frontier(original), 1):
        metrics["frontier_positions"] += 1
        pm = metrics["phase"].setdefault(phase, {
            "frontier_positions": 0,
            "mutants_generated": 0,
            "reachable_fixpoints": 0,
            "unique_reachable_fixpoints": 0,
            "extended_covered": 0,
            "extended_macro_dead": 0,
        })
        pm["frontier_positions"] += 1
        if mutated is None:
            metrics["mutants_skipped_duplicate"] += 1
            continue
        metrics["mutants_generated"] += 1
        pm["mutants_generated"] += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint_mutants"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        pm["reachable_fixpoints"] += 1
        fixpoint = r33.canonical_formula(reached["formula"])
        fh = r47f.formula_hash(fixpoint)
        if fh in seen_fixpoints:
            continue
        seen_fixpoints.add(fh)
        metrics["unique_reachable_fixpoints"] += 1
        pm["unique_reachable_fixpoints"] += 1

        scan = first_extended_accept(fixpoint)
        record = compact_covered_record(ordinal, phase, source, replacement, mutated, reached, scan)
        if not scan["covered"]:
            metrics["extended_macro_dead_fixpoints"] += 1
            pm["extended_macro_dead"] += 1
            full_scan = full_extended_scan(fixpoint)
            if full_scan["accepted_pivots"]:
                raise AssertionError(("R47K_FIRST_SCAN_FALSE_NEGATIVE", full_scan["accepted_pivots"]))
            record["all_extended_macro_rows"] = full_scan["rows"]
            record["mutated_original_formula"] = [list(c) for c in mutated]
            record["fixpoint_formula"] = [list(c) for c in fixpoint]
            first_counterexample = record
            break

        metrics["extended_covered_fixpoints"] += 1
        pm["extended_covered"] += 1
        primary = int(scan["variables_checked"])
        if primary >= hardest_primary:
            full_scan = full_extended_scan(fixpoint)
            record["accepted_pivots"] = full_scan["accepted_pivots"]
            record["accepted_pivot_count"] = len(full_scan["accepted_pivots"])
            if hardest is None or score_hardest(record) > score_hardest(hardest):
                hardest = record
                hardest_primary = primary

    if first_counterexample is not None:
        verdict = "EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_R47J_EXTENDED_FIXPOINT_CLOSURE_GRAMMAR_FOUND"
    else:
        verdict = "NO_COUNTEREXAMPLE_IN_FULL_FROZEN_ONE_SWAP_FRONTIER__EXTENDED_O4_STILL_OPEN"

    out = {
        "gate": "JANUS_TRUMP_R47K_EXTENDED_NORMALIZATION_CLOSURE_ONE_SWAP_FALSIFIER",
        "verdict": verdict,
        "regression": {
            "base_fixpoint_hash": BASE_FIXPOINT_HASH,
            "base_extended_selected_var": base_scan["selected_var"],
            "R47I_mutant_hash": R47I_MUTATED_HASH,
            "R47I_fixpoint_hash": R47I_FIXPOINT_HASH,
            "old_R45A_accepted_pivots": old_accept,
            "R47J_extended_accepted_pivots": r47i_extended_full["accepted_pivots"],
        },
        "metrics": metrics,
        "first_counterexample": first_counterexample,
        "hardest_covered": hardest,
        "interpretation": {
            "finite_frontier_only": True,
            "full_one_swap_coverage_if_no_counterexample_does_not_prove_O4": True,
            "counterexample_if_found_refutes_current_extended_grammar_only": True,
            "runtime_selection_policy": "FIRST_CERTIFIED_ACCEPTED_PIVOT",
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_EXTENDED_GRAMMAR": "OPEN",
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
