from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47n_r47m_joint_stack_closure_one_swap_falsifier as r47n

EXPECTED_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_CLV = (76, 203, 22)
SOURCE_CLAUSE = (-17, 20, 26)
REPLACEMENT_CLAUSE = (-17, -20, -26)
EXPECTED_ORIGINAL_HASH = "6592d016738439574c3cb19a8fc63a4e06e121b7249a9adc7257962bf21e78e9"


def clv(formula):
    return tuple(int(x) for x in r33.measure(r33.canonical_formula(formula)))


def reconstruct_r47n():
    _, center = r47n.load_center_original()
    mutated = r47i.mutate_one_clause(center, SOURCE_CLAUSE, REPLACEMENT_CLAUSE)
    if mutated is None:
        raise AssertionError("R47O2_MUTATION_NO_LONGER_VALID")
    mutated = r33.canonical_formula(mutated)
    if r47f.formula_hash(mutated) != EXPECTED_ORIGINAL_HASH:
        raise AssertionError(("R47O2_ORIGINAL_HASH_DRIFT", r47f.formula_hash(mutated)))
    reached = r47f.reachable_fixpoint(mutated)
    if reached is None:
        raise AssertionError("R47O2_R47N_NO_LONGER_REACHES_FIXPOINT")
    formula = r33.canonical_formula(reached["formula"])
    if r47f.formula_hash(formula) != EXPECTED_HASH:
        raise AssertionError(("R47O2_FIXPOINT_HASH_DRIFT", r47f.formula_hash(formula)))
    if clv(formula) != EXPECTED_CLV:
        raise AssertionError(("R47O2_FIXPOINT_CLV_DRIFT", clv(formula)))
    return mutated, reached, formula


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


def pair_candidate(root, first_var, second_var):
    root = r33.canonical_formula(root)
    first = r47j.macro_candidate_fixpoint(root, int(first_var))
    if first is None:
        return None
    first_replay = r47j.independent_fixpoint_macro_replay(root, first)
    if not first_replay["pass"]:
        raise AssertionError(("R47O2_FIRST_REPLAY_FAIL", first_var, first_replay))
    if first["normalization"]["terminal"] is not None or tuple(first["final_CLV"]) < clv(root):
        raise AssertionError(("R47O2_DEPTH1_INTEGRITY_DRIFT", first_var, first["final_CLV"], first["normalization"]["terminal"]))
    g1 = r33.canonical_formula(first["normalization"]["final_formula"])
    if int(second_var) not in r33.variables(g1) or int(second_var) == int(first_var):
        return None
    second = r47j.macro_candidate_fixpoint(g1, int(second_var))
    if second is None:
        return None
    second_replay = r47j.independent_fixpoint_macro_replay(g1, second)
    if not second_replay["pass"]:
        raise AssertionError(("R47O2_SECOND_REPLAY_FAIL", first_var, second_var, second_replay))
    g2 = r33.canonical_formula(second["normalization"]["final_formula"])
    terminal = second["normalization"]["terminal"] is not None
    descent = clv(g2) < clv(root)
    sat_reconstruction = reconstruct_pair_sat(root, first, second)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R47O2_PAIR_SAT_RECONSTRUCTION_FAIL", first_var, second_var))
    return {
        "first_var": int(first_var),
        "second_var": int(second_var),
        "first": compact_layer(root, first),
        "second": compact_layer(g1, second),
        "final_CLV": list(clv(g2)),
        "pair_terminal": bool(terminal),
        "pair_terminal_kind": second["normalization"]["terminal"],
        "pair_descent": bool(descent),
        "accepted": bool(terminal or descent),
        "first_replay_pass": True,
        "second_replay_pass": True,
        "SAT_reconstruction_pass": bool(sat_reconstruction["pass"]),
    }


def failure_key(row):
    return (tuple(row["final_CLV"]), int(row["first_var"]), int(row["second_var"]))


def run():
    original, reached, root = reconstruct_r47n()
    depth1_rows = []
    for var in r33.variables(root):
        candidate = r47j.macro_candidate_fixpoint(root, int(var))
        if candidate is None:
            continue
        replay = r47j.independent_fixpoint_macro_replay(root, candidate)
        if not replay["pass"]:
            raise AssertionError(("R47O2_DEPTH1_REPLAY_FAIL", var))
        depth1_rows.append({
            "var": int(var),
            "final_CLV": candidate["final_CLV"],
            "terminal": candidate["normalization"]["terminal"],
            "accepted": bool(candidate["accepted"]),
        })
    depth1_accepted = [r["var"] for r in depth1_rows if r["accepted"]]
    if depth1_accepted:
        raise AssertionError(("R47O2_R47N_NOT_DEPTH1_DEAD", depth1_accepted))

    tested = 0
    skipped = 0
    first_accepted = None
    best_failure = None
    for first_var in r33.variables(root):
        first = r47j.macro_candidate_fixpoint(root, int(first_var))
        if first is None:
            continue
        g1 = r33.canonical_formula(first["normalization"]["final_formula"])
        for second_var in r33.variables(g1):
            if int(second_var) == int(first_var):
                continue
            pair = pair_candidate(root, int(first_var), int(second_var))
            if pair is None:
                skipped += 1
                continue
            tested += 1
            if pair["accepted"]:
                first_accepted = pair
                break
            if best_failure is None or failure_key(pair) < failure_key(best_failure):
                best_failure = pair
        if first_accepted is not None:
            break

    if first_accepted is not None:
        verdict = "R47N_COUNTEREXAMPLE_RESCUED_BY_CERTIFIED_FIXED_DEPTH2_DP_COMPOSITION"
        depth_lower_bound = "d(F)=2 under frozen R47J/R47L depth grammar"
    else:
        verdict = "R47N_COUNTEREXAMPLE_SURVIVES_ALL_CERTIFIED_FIXED_DEPTH2_DP_COMPOSITIONS__D_F_GT_2"
        depth_lower_bound = "d(F)>2 under frozen R47J/R47L depth grammar"

    out = {
        "schema":"JANUS_TRUMP_R47O2_R47N_EXACT_DEPTH2_RESCUE_OR_LOWER_BOUND_RESULT",
        "version":"1.0",
        "date":"2026-09-03",
        "source_git_commit":os.environ.get("GITHUB_SHA","LOCAL_UNCOMMITTED"),
        "gate":"JANUS_TRUMP_R47O2_R47N_EXACT_DEPTH2_RESCUE_OR_LOWER_BOUND",
        "verdict":verdict,
        "R47N":{
            "mutated_original_hash":r47f.formula_hash(original),
            "fixpoint_hash":r47f.formula_hash(root),
            "fixpoint_CLV":list(clv(root)),
            "trajectory":reached["trajectory"],
            "depth1_accepted_pivots":depth1_accepted,
        },
        "tested_ordered_pairs_until_stop":tested,
        "skipped_nonapplicable_pairs":skipped,
        "first_accepted_pair":first_accepted,
        "best_failure_if_none":best_failure,
        "certified_depth_statement":depth_lower_bound,
        "resource_envelope":{
            "fixed_depth":2,
            "ordered_pair_scan":"O(V0^2)",
            "coarse_second_DP_representation":"O(C0^4)",
            "polynomial_for_fixed_depth":True,
        },
        "interpretation":{
            "new_inference_rule_added":False,
            "new_proof_authority_added":False,
            "depth2_rescue_does_not_prove_universal_K2":True,
            "depth2_survival_does_not_authorize_depth3_as_algorithmic_promotion":True,
        },
        "epistemic_firewall":{
            "UNIVERSAL_CONSTANT_K_EXISTS":"NOT_PROVED",
            "K_EQUALS_2":"NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE":"OPEN",
            "SAT_IN_P":"NOT_PROVED",
            "P_EQ_NP":"NOT_PROVED",
            "P_NE_NP":"NOT_PROVED",
            "P_VS_NP":"OPEN",
            "TRUMP_finished":False,
        },
    }
    return out


def main():
    p=argparse.ArgumentParser(); p.add_argument("--output"); args=p.parse_args()
    out=run()
    if args.output:
        path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "gate":out["gate"],"verdict":out["verdict"],
        "tested_ordered_pairs_until_stop":out["tested_ordered_pairs_until_stop"],
        "first_accepted_pair":out["first_accepted_pair"],
        "best_failure_if_none":out["best_failure_if_none"],
        "certified_depth_statement":out["certified_depth_statement"],
        "firewall":out["epistemic_firewall"]},sort_keys=True))

if __name__=="__main__": main()
