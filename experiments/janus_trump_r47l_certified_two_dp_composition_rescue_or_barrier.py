from __future__ import annotations

import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j

ROOT = Path(__file__).resolve().parents[1]
R47K_RESULT = ROOT / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
EXPECTED_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
EXPECTED_CLV = (77, 206, 22)


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def load_counterexample():
    sealed = json.loads(R47K_RESULT.read_text())
    formula = r33.canonical_formula(sealed["genuine_residual_fixpoint"]["formula"])
    if r42.formula_hash(formula) != EXPECTED_HASH:
        raise AssertionError("R47L_SEALED_HASH_DRIFT")
    if clv(formula) != EXPECTED_CLV:
        raise AssertionError("R47L_SEALED_CLV_DRIFT")
    return sealed, formula


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
        raise AssertionError("R47L_SECOND_LAYER_SAT_RECONSTRUCTION_FAIL")
    assignment = {int(v): bool(b) for v, b in second_reconstructed["assignment"].items()}
    for result in reversed(first["normalization"]["R33_reconstruction_results"]):
        assignment = r33.reconstruct_model(result, assignment)
    assignment = r42.reconstruct_sa_bve(first["DP"], assignment)
    for v in r33.variables(original):
        assignment.setdefault(int(v), False)
    passed = r33.eval_formula(original, assignment)
    return {"applicable": True, "pass": passed, "assignment": assignment}


def pair_candidate(original, first_var, second_var):
    original = r33.canonical_formula(original)
    first = r47j.macro_candidate_fixpoint(original, int(first_var))
    if first is None:
        return None
    first_replay = r47j.independent_fixpoint_macro_replay(original, first)
    if not first_replay["pass"]:
        raise AssertionError(("R47L_FIRST_LAYER_REPLAY_FAIL", first_var, first_replay))
    if first["normalization"]["terminal"] is not None:
        # Sealed R47K says no depth-1 terminal or descent; this would be integrity drift.
        raise AssertionError(("R47L_UNEXPECTED_DEPTH1_TERMINAL", first_var, first["normalization"]["terminal"]))
    g1 = r33.canonical_formula(first["normalization"]["final_formula"])
    if int(second_var) not in r33.variables(g1):
        return None
    second = r47j.macro_candidate_fixpoint(g1, int(second_var))
    if second is None:
        return None
    second_replay = r47j.independent_fixpoint_macro_replay(g1, second)
    if not second_replay["pass"]:
        raise AssertionError(("R47L_SECOND_LAYER_REPLAY_FAIL", first_var, second_var, second_replay))
    g2 = r33.canonical_formula(second["normalization"]["final_formula"])
    pair_terminal = second["normalization"]["terminal"] is not None
    pair_descent = clv(g2) < clv(original)
    accepted = pair_terminal or pair_descent
    sat_reconstruction = reconstruct_pair_sat(original, first, second)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R47L_PAIR_SAT_RECONSTRUCTION_FAIL", first_var, second_var))
    return {
        "first_var": int(first_var),
        "second_var": int(second_var),
        "first": first,
        "second": second,
        "first_replay_pass": True,
        "second_replay_pass": True,
        "pair_terminal": bool(pair_terminal),
        "pair_terminal_kind": second["normalization"]["terminal"],
        "pair_descent": bool(pair_descent),
        "final_CLV": list(clv(g2)),
        "accepted": bool(accepted),
        "SAT_reconstruction": sat_reconstruction,
    }


def compact_pair(original, pair):
    first_final = r33.canonical_formula(pair["first"]["normalization"]["final_formula"])
    return {
        "first_var": pair["first_var"],
        "second_var": pair["second_var"],
        "input_CLV": list(clv(original)),
        "first_layer": compact_layer(original, pair["first"]),
        "second_layer": compact_layer(first_final, pair["second"]),
        "final_CLV": pair["final_CLV"],
        "pair_terminal": pair["pair_terminal"],
        "pair_terminal_kind": pair["pair_terminal_kind"],
        "pair_descent": pair["pair_descent"],
        "accepted": pair["accepted"],
        "first_replay_pass": pair["first_replay_pass"],
        "second_replay_pass": pair["second_replay_pass"],
        "SAT_reconstruction_pass": pair["SAT_reconstruction"]["pass"],
    }


def failure_key(row):
    # Lower lexicographic final CLV is closer/better; deterministic pivot order breaks ties.
    return (tuple(row["final_CLV"]), int(row["first_var"]), int(row["second_var"]))


def run():
    sealed, formula = load_counterexample()
    depth1_accepted = [r["var"] for r in sealed["extended_macro_rows"] if r["accepted"]]
    if depth1_accepted:
        raise AssertionError(("R47L_DEPTH1_COUNTEREXAMPLE_DRIFT", depth1_accepted))

    variables = r33.variables(formula)
    tested_pairs = 0
    skipped_pairs = 0
    first_accepted = None
    best_failure = None

    for first_var in variables:
        first = r47j.macro_candidate_fixpoint(formula, int(first_var))
        if first is None:
            continue
        first_replay = r47j.independent_fixpoint_macro_replay(formula, first)
        if not first_replay["pass"]:
            raise AssertionError(("R47L_FIRST_PRECHECK_REPLAY_FAIL", first_var))
        g1 = r33.canonical_formula(first["normalization"]["final_formula"])
        if first["normalization"]["terminal"] is not None or clv(g1) < clv(formula):
            raise AssertionError(("R47L_DEPTH1_COUNTEREXAMPLE_DRIFT", first_var, clv(g1), first["normalization"]["terminal"]))
        for second_var in r33.variables(g1):
            if int(second_var) == int(first_var):
                continue
            pair = pair_candidate(formula, int(first_var), int(second_var))
            if pair is None:
                skipped_pairs += 1
                continue
            tested_pairs += 1
            row = compact_pair(formula, pair)
            if row["accepted"]:
                first_accepted = row
                break
            if best_failure is None or failure_key(row) < failure_key(best_failure):
                best_failure = row
        if first_accepted is not None:
            break

    if first_accepted is not None:
        verdict = "R47K_COUNTEREXAMPLE_RESCUED_BY_CERTIFIED_DEPTH2_DP_COMPOSITION"
    else:
        verdict = "R47K_COUNTEREXAMPLE_SURVIVES_ALL_CERTIFIED_DEPTH2_DP_COMPOSITIONS"

    out = {
        "gate": "JANUS_TRUMP_R47L_CERTIFIED_TWO_DP_COMPOSITION_RESCUE_OR_BARRIER",
        "verdict": verdict,
        "sealed_counterexample": {
            "hash": EXPECTED_HASH,
            "CLV": list(EXPECTED_CLV),
            "depth1_accepted_pivots": depth1_accepted,
        },
        "mechanism": "FIXED_DEPTH_2_EXACT_DP_PLUS_R47J_NORMALIZATION_CLOSURE_COMPOSITION",
        "tested_ordered_pairs_until_stop": tested_pairs,
        "skipped_nonapplicable_pairs": skipped_pairs,
        "first_accepted_pair": first_accepted,
        "best_failure_if_none": best_failure,
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
            "depth2_rescue_if_true_does_not_prove_O4": True,
            "unbounded_depth_not_authorized": True,
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_DEPTH2_GRAMMAR": "OPEN",
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
