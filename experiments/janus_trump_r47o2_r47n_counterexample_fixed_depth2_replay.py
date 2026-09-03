from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47n_r47m_joint_stack_closure_one_swap_falsifier as r47n

EXPECTED_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_CLV = (76, 203, 22)
SOURCE = (-17, 20, 26)
REPLACEMENT = (-17, -20, -26)


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def load_r47n_counterexample():
    _, center = r47n.load_center_original()
    mutated = r47i.mutate_one_clause(center, SOURCE, REPLACEMENT)
    if mutated is None:
        raise AssertionError("R47O2_MUTATION_RECONSTRUCTION_FAILED")
    reached = r47f.reachable_fixpoint(mutated)
    if reached is None:
        raise AssertionError("R47O2_R47N_NO_LONGER_REACHES_FIXPOINT")
    formula = r33.canonical_formula(reached["formula"])
    if r42.formula_hash(formula) != EXPECTED_HASH:
        raise AssertionError(("R47O2_HASH_DRIFT", r42.formula_hash(formula)))
    if clv(formula) != EXPECTED_CLV:
        raise AssertionError(("R47O2_CLV_DRIFT", clv(formula)))
    return mutated, reached, formula


def compact_layer(input_formula, candidate):
    return {
        "var": int(candidate["var"]),
        "input_CLV": list(clv(input_formula)),
        "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
        "final_CLV": candidate["final_CLV"],
        "terminal": candidate["normalization"]["terminal"],
        "restart_count": int(candidate["normalization"]["restart_count"]),
        "round_count": int(candidate["normalization"]["round_count"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "single_layer_accepted_relative_to_its_input": bool(candidate["accepted"]),
    }


def reconstruct_pair_sat(original, first, second):
    if second["normalization"]["semantic_sat"] is not True:
        return {"applicable": False, "pass": True}
    second_reconstructed = second["SAT_reconstruction"]
    if not second_reconstructed["applicable"] or not second_reconstructed["pass"]:
        raise AssertionError("R47O2_SECOND_LAYER_SAT_RECONSTRUCTION_FAIL")
    assignment = {int(v): bool(b) for v, b in second_reconstructed["assignment"].items()}
    for result in reversed(first["normalization"]["R33_reconstruction_results"]):
        assignment = r33.reconstruct_model(result, assignment)
    assignment = r42.reconstruct_sa_bve(first["DP"], assignment)
    for v in r33.variables(original):
        assignment.setdefault(int(v), False)
    passed = r33.eval_formula(original, assignment)
    return {"applicable": True, "pass": passed, "assignment": assignment}


def compact_pair(original, first, second, second_input, first_var, second_var):
    final_formula = r33.canonical_formula(second["normalization"]["final_formula"])
    pair_terminal = second["normalization"]["terminal"] is not None
    pair_descent = clv(final_formula) < clv(original)
    sat_reconstruction = reconstruct_pair_sat(original, first, second)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R47O2_PAIR_SAT_RECONSTRUCTION_FAIL", first_var, second_var))
    return {
        "first_var": int(first_var),
        "second_var": int(second_var),
        "input_CLV": list(clv(original)),
        "first_layer": compact_layer(original, first),
        "second_layer": compact_layer(second_input, second),
        "final_CLV": list(clv(final_formula)),
        "pair_terminal": bool(pair_terminal),
        "pair_terminal_kind": second["normalization"]["terminal"],
        "pair_descent": bool(pair_descent),
        "accepted": bool(pair_terminal or pair_descent),
        "SAT_reconstruction_pass": bool(sat_reconstruction["pass"]),
    }


def failure_key(row):
    return (tuple(row["final_CLV"]), int(row["first_var"]), int(row["second_var"]))


def run():
    mutated, reached, formula = load_r47n_counterexample()
    variables = r33.variables(formula)

    first_cache = {}
    depth1_accepted = []
    for first_var in variables:
        first = r47j.macro_candidate_fixpoint(formula, int(first_var))
        if first is None:
            continue
        replay = r47j.independent_fixpoint_macro_replay(formula, first)
        if not replay["pass"]:
            raise AssertionError(("R47O2_FIRST_LAYER_REPLAY_FAIL", first_var, replay))
        if not first["DP_independent_replay_pass"] or not first["polynomial_intermediate_envelope_pass"]:
            raise AssertionError(("R47O2_FIRST_LAYER_RESOURCE_OR_DP_FAIL", first_var))
        g1 = r33.canonical_formula(first["normalization"]["final_formula"])
        if first["normalization"]["terminal"] is not None or clv(g1) < clv(formula):
            depth1_accepted.append(int(first_var))
        first_cache[int(first_var)] = (first, g1)

    if depth1_accepted:
        raise AssertionError(("R47O2_R47N_NOT_DEPTH1_DEAD_UNDER_R47J", depth1_accepted))

    tested_pairs = 0
    skipped_nonapplicable = 0
    first_accepted = None
    best_failure = None
    pair_prefix = []

    for first_var in variables:
        cached = first_cache.get(int(first_var))
        if cached is None:
            continue
        first, g1 = cached
        for second_var in r33.variables(g1):
            if int(second_var) == int(first_var):
                continue
            second = r47j.macro_candidate_fixpoint(g1, int(second_var))
            if second is None:
                skipped_nonapplicable += 1
                continue
            replay = r47j.independent_fixpoint_macro_replay(g1, second)
            if not replay["pass"]:
                raise AssertionError(("R47O2_SECOND_LAYER_REPLAY_FAIL", first_var, second_var, replay))
            if not second["DP_independent_replay_pass"] or not second["polynomial_intermediate_envelope_pass"]:
                raise AssertionError(("R47O2_SECOND_LAYER_RESOURCE_OR_DP_FAIL", first_var, second_var))
            tested_pairs += 1
            row = compact_pair(formula, first, second, g1, first_var, second_var)
            pair_prefix.append(row)
            if row["accepted"]:
                first_accepted = row
                break
            if best_failure is None or failure_key(row) < failure_key(best_failure):
                best_failure = row
        if first_accepted is not None:
            break

    verdict = (
        "R47N_COUNTEREXAMPLE_RESCUED_BY_FROZEN_FIXED_DEPTH2_R47L_GRAMMAR"
        if first_accepted is not None else
        "R47N_COUNTEREXAMPLE_SURVIVES_ALL_FROZEN_FIXED_DEPTH2_R47L_COMPOSITIONS"
    )
    return {
        "gate": "JANUS_TRUMP_R47O2_R47N_COUNTEREXAMPLE_FIXED_DEPTH2_REPLAY",
        "verdict": verdict,
        "sealed_R47N": {
            "mutated_original_hash": r47f.formula_hash(mutated),
            "fixpoint_hash": r42.formula_hash(formula),
            "fixpoint_CLV": list(clv(formula)),
            "reachability_trajectory": reached["trajectory"],
            "depth1_R47J_accepted_pivots": depth1_accepted,
        },
        "tested_ordered_pairs_until_stop": tested_pairs,
        "skipped_nonapplicable_pairs": skipped_nonapplicable,
        "first_accepted_pair": first_accepted,
        "best_failure_if_none": best_failure,
        "pair_prefix_until_stop": pair_prefix,
        "resource_envelope": {
            "ordered_pairs": "O(V0^2)",
            "first_DP_raw_clauses": "O(C0^2)",
            "second_DP_raw_clauses": "O(C0^4)",
            "fixed_depth": 2,
            "polynomial": True,
        },
        "interpretation": {
            "new_inference_rule_added": False,
            "new_proof_authority_added": False,
            "rescue_if_true_only_proves_dF_at_most_2_for_this_witness": True,
            "survival_if_true_refutes_K_equals_2_for_frozen_R47L_grammar": True,
            "unbounded_depth_not_authorized": True,
            "depth3_not_authorized_by_failure": True,
        },
        "firewall": {
            "UNIVERSAL_K_EXISTS": "NOT_PROVED",
            "K_EQ_2_UNIVERSAL": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact = {
        "gate": result["gate"],
        "verdict": result["verdict"],
        "sealed_R47N": result["sealed_R47N"],
        "tested_ordered_pairs_until_stop": result["tested_ordered_pairs_until_stop"],
        "skipped_nonapplicable_pairs": result["skipped_nonapplicable_pairs"],
        "first_accepted_pair": result["first_accepted_pair"],
        "best_failure_if_none": result["best_failure_if_none"],
        "firewall": result["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
