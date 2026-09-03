from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47k_extended_normalization_closure_one_swap_falsifier as r47k
import janus_trump_r47l_certified_two_dp_composition_rescue_or_barrier as r47l

ROOT = Path(__file__).resolve().parents[1]
R47K_RESULT = ROOT / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
BASE_ORIGINAL_HASH = "eb13be26c29c106cf172db0be435aaf852d1e1248fced151c5356791f70024da"
BASE_RESIDUAL_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
BASE_RESIDUAL_CLV = (77, 206, 22)
BASE_DEPTH2_PAIR = (11, 20)


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def compact_pair(original, first, second, first_var, second_var, accepted):
    g1 = r33.canonical_formula(first["normalization"]["final_formula"])
    g2 = r33.canonical_formula(second["normalization"]["final_formula"])
    reconstruction = r47l.reconstruct_pair_sat(original, first, second)
    if not reconstruction["pass"]:
        raise AssertionError(("R47R_PAIR_RECONSTRUCTION_FAIL", first_var, second_var))
    return {
        "first_var": int(first_var),
        "second_var": int(second_var),
        "input_CLV": list(clv(original)),
        "first_forced_DP_CLV": first["DP"]["measure_after_forced_DP"],
        "first_final_CLV": list(clv(g1)),
        "first_terminal": first["normalization"]["terminal"],
        "first_restart_count": int(first["normalization"]["restart_count"]),
        "first_replay_pass": True,
        "second_forced_DP_CLV": second["DP"]["measure_after_forced_DP"],
        "second_final_CLV": list(clv(g2)),
        "second_terminal": second["normalization"]["terminal"],
        "second_restart_count": int(second["normalization"]["restart_count"]),
        "second_replay_pass": True,
        "pair_terminal": second["normalization"]["terminal"] is not None,
        "pair_descent": clv(g2) < clv(original),
        "accepted": bool(accepted),
        "SAT_reconstruction_pass": True,
    }


def depth2_scan(depth1_dead_formula, keep_all_failures=False):
    original = r33.canonical_formula(depth1_dead_formula)
    tested = 0
    best = None
    failures = []
    for first_var in r33.variables(original):
        first = r47j.macro_candidate_fixpoint(original, int(first_var))
        if first is None:
            continue
        first_replay = r47j.independent_fixpoint_macro_replay(original, first)
        if not first_replay["pass"]:
            raise AssertionError(("R47R_FIRST_REPLAY_FAIL", first_var, first_replay))
        g1 = r33.canonical_formula(first["normalization"]["final_formula"])
        if first["normalization"]["terminal"] is not None or clv(g1) < clv(original):
            raise AssertionError(("R47R_DEPTH1_DEAD_DRIFT", first_var, clv(g1), first["normalization"]["terminal"]))
        for second_var in r33.variables(g1):
            second = r47j.macro_candidate_fixpoint(g1, int(second_var))
            if second is None:
                continue
            second_replay = r47j.independent_fixpoint_macro_replay(g1, second)
            if not second_replay["pass"]:
                raise AssertionError(("R47R_SECOND_REPLAY_FAIL", first_var, second_var, second_replay))
            g2 = r33.canonical_formula(second["normalization"]["final_formula"])
            accepted = second["normalization"]["terminal"] is not None or clv(g2) < clv(original)
            tested += 1
            row = compact_pair(original, first, second, first_var, second_var, accepted)
            if accepted:
                return {
                    "covered": True,
                    "tested_pairs": tested,
                    "selected_pair": [int(first_var), int(second_var)],
                    "selected": row,
                    "best_failure": best,
                    "all_failures": None,
                }
            if best is None or (tuple(row["second_final_CLV"]), row["first_var"], row["second_var"]) < (tuple(best["second_final_CLV"]), best["first_var"], best["second_var"]):
                best = row
            if keep_all_failures:
                failures.append(row)
    return {
        "covered": False,
        "tested_pairs": tested,
        "selected_pair": None,
        "selected": None,
        "best_failure": best,
        "all_failures": failures if keep_all_failures else None,
    }


def load_base():
    sealed = json.loads(R47K_RESULT.read_text())
    original = r33.canonical_formula(sealed["mutated_original"]["formula"])
    if r47f.formula_hash(original) != BASE_ORIGINAL_HASH:
        raise AssertionError("R47R_BASE_ORIGINAL_HASH_DRIFT")
    reached = r47f.reachable_fixpoint(original)
    if reached is None:
        raise AssertionError("R47R_BASE_NO_RESIDUAL")
    residual = r33.canonical_formula(reached["formula"])
    if r47f.formula_hash(residual) != BASE_RESIDUAL_HASH or clv(residual) != BASE_RESIDUAL_CLV:
        raise AssertionError(("R47R_BASE_RESIDUAL_DRIFT", r47f.formula_hash(residual), clv(residual)))
    depth1 = r47k.first_extended_accept(residual)
    if depth1["covered"]:
        raise AssertionError(("R47R_BASE_DEPTH1_DRIFT", depth1["selected_var"]))
    depth2 = depth2_scan(residual)
    if not depth2["covered"] or tuple(depth2["selected_pair"]) != BASE_DEPTH2_PAIR:
        raise AssertionError(("R47R_BASE_DEPTH2_DRIFT", depth2))
    return sealed, original, residual, depth2


def counterexample_receipt(source, replacement, mutant, reached, residual, depth1):
    full = depth2_scan(residual, keep_all_failures=True)
    if full["covered"]:
        raise AssertionError("R47R_DEAD_REPLAY_BECAME_COVERED")
    return {
        "source_clause": list(source),
        "replacement_clause": list(replacement),
        "mutated_original_hash": r47f.formula_hash(mutant),
        "mutated_original_CLV": list(clv(mutant)),
        "mutated_original_formula": [list(c) for c in mutant],
        "reachability_trajectory": reached["trajectory"],
        "residual_hash": r47f.formula_hash(residual),
        "residual_CLV": list(clv(residual)),
        "residual_formula": [list(c) for c in residual],
        "depth1_rows": depth1["rows_prefix"],
        "depth2_tested_pairs": int(full["tested_pairs"]),
        "all_depth2_failed_pairs": full["all_failures"],
        "best_depth2_failure": full["best_failure"],
        "certified_lower_bound": "d(F)>2_WITHIN_FROZEN_GRAMMAR",
    }


def run():
    _, base_original, base_residual, base_depth2 = load_base()
    eligible = [c for c in base_original if any(abs(l) in {11,20} for l in c)]
    if not eligible:
        raise AssertionError("R47R_NO_ELIGIBLE_SOURCE_CLAUSES")

    metrics = {
        "eligible_source_clause_count": len(eligible),
        "frontier_positions": 0,
        "mutants_generated": 0,
        "duplicate_replacements_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "unique_fixpoints": 0,
        "depth1_covered": 0,
        "depth1_dead": 0,
        "depth2_rescued": 0,
        "depth2_dead": 0,
        "depth2_pairs_tested": 0,
    }
    seen = set()
    counterexample = None
    hardest_rescue = None

    for source in eligible:
        for replacement in r47i.signed_same_support_variants(source):
            metrics["frontier_positions"] += 1
            mutant = r47i.mutate_one_clause(base_original, source, replacement)
            if mutant is None:
                metrics["duplicate_replacements_skipped"] += 1
                continue
            metrics["mutants_generated"] += 1
            reached = r47f.reachable_fixpoint(mutant)
            if reached is None:
                metrics["semantic_or_nonfixpoint"] += 1
                continue
            metrics["reachable_fixpoints"] += 1
            residual = r33.canonical_formula(reached["formula"])
            rh = r47f.formula_hash(residual)
            if rh in seen:
                continue
            seen.add(rh)
            metrics["unique_fixpoints"] += 1

            depth1 = r47k.first_extended_accept(residual)
            if depth1["covered"]:
                metrics["depth1_covered"] += 1
                continue
            metrics["depth1_dead"] += 1
            depth2 = depth2_scan(residual)
            metrics["depth2_pairs_tested"] += int(depth2["tested_pairs"])
            if depth2["covered"]:
                metrics["depth2_rescued"] += 1
                record = {
                    "source_clause": list(source),
                    "replacement_clause": list(replacement),
                    "mutated_original_hash": r47f.formula_hash(mutant),
                    "residual_hash": rh,
                    "residual_CLV": list(clv(residual)),
                    "tested_pairs": int(depth2["tested_pairs"]),
                    "selected_pair": depth2["selected_pair"],
                    "selected": depth2["selected"],
                }
                if hardest_rescue is None or (record["tested_pairs"], tuple(record["residual_CLV"]), record["residual_hash"]) > (hardest_rescue["tested_pairs"], tuple(hardest_rescue["residual_CLV"]), hardest_rescue["residual_hash"]):
                    hardest_rescue = record
                continue

            metrics["depth2_dead"] += 1
            counterexample = counterexample_receipt(source, replacement, mutant, reached, residual, depth1)
            break
        if counterexample is not None:
            break

    verdict = (
        "EXPLICIT_REACHABLE_TARGETED_TWO_SWAP_DEPTH2_COUNTEREXAMPLE_FOUND"
        if counterexample is not None
        else "NO_DEPTH2_COUNTEREXAMPLE_IN_FROZEN_RESCUE_DISRUPTION_FRONTIER__O4_OPEN"
    )
    out = {
        "gate": "JANUS_TRUMP_R47R_TARGETED_TWO_SWAP_DEPTH2_RESCUE_DISRUPTION",
        "verdict": verdict,
        "baseline_regression": {
            "base_original_hash": BASE_ORIGINAL_HASH,
            "base_residual_hash": BASE_RESIDUAL_HASH,
            "base_depth1_dead": True,
            "base_depth2_selected_pair": base_depth2["selected_pair"],
            "base_depth2_final_CLV": base_depth2["selected"]["second_final_CLV"],
        },
        "target_variables": [11,20],
        "metrics": metrics,
        "first_counterexample": counterexample,
        "hardest_depth2_rescue_if_none": hardest_rescue,
        "interpretation": {
            "finite_targeted_frontier_only": True,
            "counterexample_if_found_proves_d_gt_2_for_that_witness": True,
            "counterexample_if_found_does_not_prove_unbounded_depth": True,
            "unbounded_depth_not_authorized": True,
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_FIXED_DEPTH2_GRAMMAR": "OPEN",
            "UNIVERSAL_CONSTANT_K_EXISTS": "NOT_PROVED",
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
