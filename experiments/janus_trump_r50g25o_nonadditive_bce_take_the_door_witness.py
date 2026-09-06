from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import janus_trump_r50g25n_derived_clause_or_nonadditive_door as r50g25n
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25O_NONADDITIVE_BCE_TAKE_THE_DOOR_WITNESS"
TARGET_HASH = r50g25n.TARGET_HASH
TARGET_CLAUSE = tuple(r50g25n.EXPECTED_REQUIREMENT["clause"])
BLOCKING_LITERAL = int(r50g25n.EXPECTED_REQUIREMENT["blocking_literal"])


def models_over_vars(r33, formula, vs):
    models = []
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if r33.eval_formula(formula, a):
            models.append(a)
    return models


def blocked_clause_certificate(r33, formula, clause, blocking_literal):
    cset = set(clause)
    parents = []
    for other in formula:
        if -blocking_literal not in other:
            continue
        resolvent = (cset - {blocking_literal}) | (set(other) - {-blocking_literal})
        taut_pairs = sorted({abs(x) for x in resolvent if -x in resolvent})
        parents.append({
            "opposite_parent": list(other),
            "resolvent": list(r33.canonical_clause(resolvent)),
            "tautology_witness_variables": taut_pairs,
            "tautological": bool(taut_pairs),
        })
    return {
        "clause": list(clause),
        "blocking_literal": blocking_literal,
        "opposite_parent_count": len(parents),
        "opposite_parents": parents,
        "pass": bool(parents) and all(x["tautological"] for x in parents),
    }


def run():
    parent = r50g25n.run()
    if parent["verdict"] != "EXACT_NO_GO_FOR_ANY_ADDITIVE_EXISTING_VARIABLE_ENTAILED_CLAUSE_ON_MINIMAL_WITNESS":
        raise AssertionError(("R50G25O_PARENT_N_VERDICT_DRIFT", parent["verdict"]))

    target = r50g25n.find_target()
    _b, r50g23, r35b, r33, r47j = r50g25g._chain()
    if r50g23.r50g4.fhash(target) != TARGET_HASH:
        raise AssertionError("R50G25O_TARGET_HASH_DRIFT")
    if TARGET_CLAUSE not in target:
        raise AssertionError("R50G25O_TARGET_CLAUSE_MISSING")

    certificate = blocked_clause_certificate(r33, target, TARGET_CLAUSE, BLOCKING_LITERAL)
    if not certificate["pass"]:
        raise AssertionError(("R50G25O_BCE_CERTIFICATE_FAIL", certificate))
    if certificate["opposite_parent_count"] != 1:
        raise AssertionError(("R50G25O_OPPOSITE_PARENT_COUNT_DRIFT", certificate))

    reduced = r33.canonical_formula(c for c in target if c != TARGET_CLAUSE)
    if not r33.measure(reduced) < r33.measure(target):
        raise AssertionError(("R50G25O_NO_STRICT_MEASURE_DESCENT", r33.measure(target), r33.measure(reduced)))

    vs = list(r33.variables(target))
    if len(vs) != 6:
        raise AssertionError(("R50G25O_VARIABLE_COUNT_DRIFT", vs))
    before_models = models_over_vars(r33, target, vs)
    after_models = models_over_vars(r33, reduced, vs)
    if len(before_models) != 14:
        raise AssertionError(("R50G25O_BEFORE_MODEL_COUNT_DRIFT", len(before_models)))

    # Deletion is monotone: every original model must satisfy the reduced formula.
    original_to_reduced_failures = sum(1 for a in before_models if not r33.eval_formula(reduced, a))

    # Independent reconstruction of every reduced model using the exact R33 BCE rule.
    fake_result = {
        "history": [{
            "rule": "BLOCKED_CLAUSE_ELIMINATION",
            "clause": list(TARGET_CLAUSE),
            "blocking_literal": BLOCKING_LITERAL,
        }]
    }
    reconstruction_failures = 0
    reconstructed_models = []
    for a in after_models:
        rec = r33.reconstruct_model(fake_result, dict(a))
        if not r33.eval_formula(target, rec):
            reconstruction_failures += 1
        reconstructed_models.append(rec)

    sat_equivalent_with_reconstruction = (
        bool(before_models) == bool(after_models)
        and original_to_reduced_failures == 0
        and reconstruction_failures == 0
    )
    if not sat_equivalent_with_reconstruction:
        raise AssertionError((
            "R50G25O_BCE_SAT_EQUIVALENCE_OR_RECONSTRUCTION_FAIL",
            len(before_models), len(after_models), original_to_reduced_failures, reconstruction_failures,
        ))

    # Deliberately record that BCE deletion is not truth-function equivalence on
    # the same assignments; its contract is equisatisfiability + reconstruction.
    truth_function_equal = all(
        r33.eval_formula(target, a) == r33.eval_formula(reduced, a)
        for a in (dict(zip(vs, bits)) for bits in itertools.product((False, True), repeat=len(vs)))
    )

    reduced_r33 = r33.simplify(reduced)
    micro = r50g25g.micro_normalize(reduced, r50g23, r35b, r33, r47j)

    # Also verify that the frozen R33 implementation itself recognizes the source
    # formula as immediately reducible by BCE. Which BCE it chooses first may be a
    # scheduler tie-break, so the gate does not require the same clause to be first.
    baseline = r33.simplify(target)
    baseline_first_rule = baseline["history"][0]["rule"] if baseline.get("history") else None
    if baseline_first_rule != "BLOCKED_CLAUSE_ELIMINATION":
        raise AssertionError(("R50G25O_BASELINE_DOOR_DRIFT", baseline_first_rule))

    verdict = "CERTIFIED_NONADDITIVE_BCE_DOOR_REPLACES_IMPOSSIBLE_ADDITIVE_NEUTRALIZATION_ON_WITNESS"
    next_gate = "R50G25P_TAKE_LIVE_REDUCTION_DOOR_REPLAY_ACROSS_696_ADDITIVE_NO_GO_TARGETS"

    return {
        "gate": GATE,
        "parent_N_run": 34037524016,
        "target": {
            "state_hash": TARGET_HASH,
            "CLV_before": list(r33.measure(target)),
            "CLV_after_exact_BCE_deletion": list(r33.measure(reduced)),
            "model_count_before": len(before_models),
            "model_count_after_deletion_on_same_6_vars": len(after_models),
            "baseline_first_R33_rule": baseline_first_rule,
        },
        "BCE_certificate": certificate,
        "semantic_contract": {
            "truth_function_equal_on_same_assignments": truth_function_equal,
            "SAT_status_equal": bool(before_models) == bool(after_models),
            "original_models_satisfy_reduced_failure_count": original_to_reduced_failures,
            "reduced_model_reconstruction_failure_count": reconstruction_failures,
            "equisatisfiable_with_reconstruction": sat_equivalent_with_reconstruction,
            "contract_kind": "SAT_PRESERVING_NONADDITIVE_REDUCTION_WITH_RECONSTRUCTION",
        },
        "downstream": {
            "R33_after_manual_BCE_terminal": reduced_r33.get("terminal"),
            "R33_after_manual_BCE_rule_applications": int(reduced_r33.get("total_rule_applications", 0)),
            "micro_terminal": micro.get("terminal"),
            "micro_semantic_sat": micro.get("semantic_sat"),
            "micro_restart_count": int(micro.get("restart_count", 0)),
            "micro_RUP_successful_strengthenings": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
            "micro_SAT_reconstruction_pass": bool(micro.get("SAT_reconstruction", {}).get("pass", False)) if micro.get("semantic_sat") is True else None,
        },
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "anti_collapse_cover_construction_is_a_hardening_experiment_not_a_required_solver_step": True,
            "live_BCE_should_be_taken_not_semantics_preservingly_blocked_when_the_goal_is_solving": True,
            "BCE_deletion_is_not_same_assignment_truth_function_equivalence": True,
            "BCE_deletion_is_SAT_preserving_with_polynomial_reconstruction_certificate": True,
            "one_witness_success_is_not_outer_coverage": True,
            "no_family_expansion": True,
        },
        "firewall": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
