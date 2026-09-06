from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import janus_trump_r50g25e_pi_stalled_lean_core_alternate_door_forensics as r50g25e

GATE = "JANUS_TRUMP_R50G25F_PI_RUP_THRESHOLD_EVENT_CAUSAL_SUPPORT_AND_SCHEDULE_LIFT"
EXPECTED_POST_DP_HASH = "0ca7d0383f488b1d8c55ef6f3596470748ed3432cc24aee7f82918ecf9997a90"
PINNED_POST_DP = [
    [-5, -7],
    [-3, -4, -6],
    [-3, 4, -5],
    [-3, 5, -6],
    [-2, -3, -6, 7],
    [-2, -3, 6, 7],
    [-2, 3],
    [-2, 5, -6],
    [2, -4],
    [2, 3],
    [2, 6],
    [4, 5, -7],
    [4, 5, -6],
]


def exact_model_set(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    out = []
    for bits in itertools.product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if r33.eval_formula(formula, a):
            out.append(tuple(sorted(a.items())))
    return out


def micro_rup_restart_normalize(initial, r50g23, r35b, r33):
    r34 = r50g23.r34
    r42 = r50g23.r42
    r47j = r50g23.r47j
    state = r33.canonical_formula(initial)
    height_bound = r47j.restart_height_bound(state)
    rounds = []
    total = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "RUP_successful_strengthenings": 0,
        "micro_restart_count": 0,
    }
    final_reduced = None
    terminal = None
    terminal_verification = None

    for round_index in range(height_bound + 1):
        before = state
        before_clv = r33.measure(before)
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        after_r33_clv = r33.measure(after_r33)
        total["R33_check_operation_upper_ledger"] += int(reduced["total_check_operation_count_upper_ledger"])
        total["R33_certificate_bytes"] += int(reduced["total_certificate_bytes"])

        row = {
            "round": round_index,
            "before_CLV": list(before_clv),
            "R33_apps": int(reduced["total_rule_applications"]),
            "R33_rule_sequence": [str(x["rule"]) for x in reduced["history"]],
            "after_R33_CLV": list(after_r33_clv),
            "R33_terminal": str(reduced["terminal"]),
        }

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("R50G25F_PI_DECLARED_TERMINAL_VERIFY_FAIL", solved))
            terminal = str(solved["kind"])
            terminal_verification = solved
            final_reduced = reduced
            state = after_r33
            row["stop"] = terminal
            rounds.append(row)
            break

        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            raise AssertionError("R50G25F_PI_UNEXPECTED_AFFINE_ON_PINNED_WITNESS")

        proposal, ledger = r35b.first_rup_strengthening(after_r33)
        total["RUP_checks"] += int(ledger["rup_checks"])
        total["RUP_UP_clause_scans"] += int(ledger["up_clause_scans"])
        total["RUP_UP_literal_inspections"] += int(ledger["up_literal_inspections"])
        if proposal is None:
            terminal = "CERTIFIED_MICRO_RUP_RESTART_FIXPOINT"
            state = after_r33
            row["stop"] = terminal
            rounds.append(row)
            break

        source = tuple(proposal["source_clause"])
        strengthened = tuple(proposal["strengthened_clause"])
        assumptions = tuple(proposal["assumptions"])
        if not r35b.independent_up_conflict_checker(after_r33, assumptions):
            raise AssertionError(("R50G25F_PI_MICRO_RUP_CERT_FAIL", round_index, proposal))
        after_rup = r35b.replace_clause_with_subclause(after_r33, source, strengthened)
        after_rup_clv = r33.measure(after_rup)
        if not after_rup_clv < after_r33_clv:
            raise AssertionError(("R50G25F_PI_MICRO_RUP_NOT_STRICT_R33_CLV_DESCENT", after_r33_clv, after_rup_clv))

        total["RUP_successful_strengthenings"] += 1
        total["micro_restart_count"] += 1
        row.update({
            "RUP_event": {
                "source_clause": list(source),
                "removed_literal": int(proposal["removed_literal"]),
                "strengthened_clause": list(strengthened),
                "assumptions": list(assumptions),
                "UP_conflict_kind": proposal["up_receipt"].get("conflict_kind"),
                "UP_conflict_clause": proposal["up_receipt"].get("conflict_clause"),
            },
            "after_single_RUP_CLV": list(after_rup_clv),
            "micro_restart": True,
        })
        rounds.append(row)
        state = after_rup
    else:
        raise AssertionError(("R50G25F_PI_MICRO_HEIGHT_BOUND_EXHAUSTED", height_bound))

    if final_reduced is None or terminal is None:
        raise AssertionError("R50G25F_PI_MICRO_NO_TERMINAL_RECONSTRUCTION")

    seed_assignment = dict((terminal_verification or {}).get("assignment") or {})
    reconstructed = r33.reconstruct_model(final_reduced, seed_assignment)
    for v in r33.variables(initial):
        reconstructed.setdefault(int(v), False)
    initial_sat = r33.eval_formula(r33.canonical_formula(initial), reconstructed)

    return {
        "height_bound": int(height_bound),
        "round_count": len(rounds),
        "rounds": rounds,
        "terminal": terminal,
        "final_CLV": list(r33.measure(state)),
        "final_formula": [list(c) for c in state],
        "ledger": total,
        "reconstructed_assignment": {str(k): bool(v) for k, v in sorted(reconstructed.items())},
        "reconstructed_assignment_satisfies_initial_post_DP": bool(initial_sat),
    }


def run():
    parent = r50g25e.run()
    if parent["witness_identity"]["post_DP_hash"] != EXPECTED_POST_DP_HASH:
        raise AssertionError(("R50G25F_PI_PARENT_POST_DP_HASH_DRIFT", parent["witness_identity"]["post_DP_hash"]))
    if parent["counterfactual_prefix_restart_probe"]["shortest_actual_history_prefix_whose_immediate_R33_restart_reaches_EMPTY_CNF"] != 1:
        raise AssertionError("R50G25F_PI_PARENT_THRESHOLD_NOT_ONE")

    r50g23, r35b, r33 = r50g25e._chain()
    r42 = r50g23.r42
    initial = r33.canonical_formula(PINNED_POST_DP)
    if r42.formula_hash(initial) != EXPECTED_POST_DP_HASH:
        raise AssertionError(("R50G25F_PI_PINNED_FORMULA_HASH_DRIFT", r42.formula_hash(initial)))
    if list(r33.measure(initial)) != [13, 36, 6]:
        raise AssertionError(("R50G25F_PI_PINNED_CLV_DRIFT", r33.measure(initial)))

    proposal, proposal_ledger = r35b.first_rup_strengthening(initial)
    if proposal is None:
        raise AssertionError("R50G25F_PI_FIRST_RUP_PROPOSAL_MISSING")
    first_event = {
        "source_clause": list(proposal["source_clause"]),
        "removed_literal": int(proposal["removed_literal"]),
        "strengthened_clause": list(proposal["strengthened_clause"]),
        "assumptions": list(proposal["assumptions"]),
    }
    expected_event = {
        "source_clause": [-3, -4, -6],
        "removed_literal": -3,
        "strengthened_clause": [-4, -6],
        "assumptions": [4, 6],
    }
    if first_event != expected_event:
        raise AssertionError(("R50G25F_PI_FIRST_EVENT_DRIFT", first_event))
    if not r35b.independent_up_conflict_checker(initial, tuple(proposal["assumptions"])):
        raise AssertionError("R50G25F_PI_FIRST_EVENT_INDEPENDENT_RUP_FAIL")

    once = r35b.replace_clause_with_subclause(initial, tuple(proposal["source_clause"]), tuple(proposal["strengthened_clause"]))
    models_before = exact_model_set(r33, initial)
    models_after = exact_model_set(r33, once)
    if models_before != models_after:
        raise AssertionError(("R50G25F_PI_64_ASSIGNMENT_SEMANTIC_CONTROL_FAIL", len(models_before), len(models_after)))

    micro = micro_rup_restart_normalize(initial, r50g23, r35b, r33)
    if micro["terminal"] != "DIRECT_EMPTY_CNF" or micro["final_CLV"] != [0, 0, 0]:
        raise AssertionError(("R50G25F_PI_MICRO_TERMINAL_DRIFT", micro["terminal"], micro["final_CLV"]))
    if micro["ledger"]["RUP_successful_strengthenings"] != 1:
        raise AssertionError(("R50G25F_PI_MICRO_EXPECTED_ONE_RUP", micro["ledger"]))
    if not micro["reconstructed_assignment_satisfies_initial_post_DP"]:
        raise AssertionError("R50G25F_PI_MICRO_RECONSTRUCTION_FAIL")

    sealed = parent["sealed_RUP_run"]
    sealed_terminal = parent["sealed_final_restart_effect"]["terminal"]
    if sealed_terminal != "EMPTY_CNF_SAT":
        raise AssertionError(("R50G25F_PI_SEALED_TERMINAL_DRIFT", sealed_terminal))

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "witness_identity": parent["witness_identity"],
        "threshold_event": {
            **first_event,
            "first_proposal_scan_ledger": proposal_ledger,
            "independent_RUP_conflict_replay_pass": True,
            "parent_forward_inclusion_minimal_support": parent["decisive_threshold_event"]["forward_greedy_inclusion_minimal_clause_support"],
            "parent_reverse_inclusion_minimal_support": parent["decisive_threshold_event"]["reverse_greedy_inclusion_minimal_clause_support"],
        },
        "exact_fixed_witness_semantic_control": {
            "variable_count": len(r33.variables(initial)),
            "assignment_space_checked": 2 ** len(r33.variables(initial)),
            "models_before_first_RUP": len(models_before),
            "models_after_first_RUP": len(models_after),
            "model_sets_equal": True,
            "authority": "FIXED_6_VARIABLE_VALIDATION_CONTROL_ONLY",
        },
        "micro_RUP_restart_schedule": micro,
        "sealed_vs_micro_witness_ledger": {
            "sealed_RUP_successful_strengthenings": int(sealed["successful_strengthenings"]),
            "micro_RUP_successful_strengthenings": int(micro["ledger"]["RUP_successful_strengthenings"]),
            "sealed_RUP_checks": int(sealed["ledger"]["rup_checks"]),
            "micro_RUP_checks": int(micro["ledger"]["RUP_checks"]),
            "sealed_RUP_UP_clause_scans": int(sealed["ledger"]["up_clause_scans"]),
            "micro_RUP_UP_clause_scans": int(micro["ledger"]["RUP_UP_clause_scans"]),
            "sealed_RUP_UP_literal_inspections": int(sealed["ledger"]["up_literal_inspections"]),
            "micro_RUP_UP_literal_inspections": int(micro["ledger"]["RUP_UP_literal_inspections"]),
            "same_empty_CNF_outcome_on_this_witness": True,
        },
        "causal_collapse_automaton_candidate": {
            "sealed_path": "STALLED_R33 -> RUP_FIXPOINT_21 -> RESTART -> UNIT_6 -> EMPTY_CNF",
            "micro_path": "STALLED_R33 -> RUP_1 -> RESTART -> BVE/BVE/SUBSUMPTIONx4/BCE/BVE/BCEx2/PURE -> EMPTY_CNF",
            "threshold_event_count_before_a_certified_R33_escape_exists": 1,
            "unit_door_first_becomes_available_at_prefix": 2,
        },
        "next_gate": "R50G25G_MICRO_RUP_RESTART_REPLAY_ACROSS_SOURCE_LIFT_STATE_FAMILY",
        "interpretation_contract": {
            "micro_restart_after_each_RUP_is_a_candidate_schedule_not_current_R47J": True,
            "single_witness_same_terminal_does_not_prove_family_equivalence": True,
            "witness_ledger_reduction_is_not_asymptotic_complexity_proof": True,
            "64_assignment_enumeration_is_validation_only_not_algorithmic_core": True,
            "first_RUP_threshold_is_shortest_ordered_prefix_not_minimum_unordered_subset": True,
            "RUP_supports_are_inclusion_minimal_not_minimum_cardinality": True,
            "candidate_schedule_must_be_replayed_on_broader_frozen_family_before_promotion": True,
        },
        "firewall": {
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "U_MU": "OPEN",
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
