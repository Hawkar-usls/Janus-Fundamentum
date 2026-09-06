from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25d_pi_unique_stalled_lean_core_witness as r50g25d_pi

GATE = "JANUS_TRUMP_R50G25E_PI_STALLED_LEAN_CORE_ALTERNATE_DOOR_FORENSICS"


def _chain():
    r50g25d = r50g25d_pi.r50g25d
    r50g25c = r50g25d.r50g25c
    r50g25b = r50g25c.r50g25b
    r50g25a = r50g25b.r50g25a
    r50g23 = r50g25a.r50g24.r50g23
    return r50g23, r50g23.r35b, r50g23.r33


def canon(r33, formula):
    return r33.canonical_formula(formula)


def fjson(formula):
    return [list(c) for c in formula]


def clause_key(clause):
    return (len(clause), tuple(clause))


def reduced_signature(r33, formula):
    reduced = r33.simplify(formula)
    history = reduced.get("history", [])
    first_rule = str(history[0]["rule"]) if history else None
    unit_literals = sorted((c[0] for c in formula if len(c) == 1), key=r33.lit_key)
    final_formula = canon(r33, reduced.get("final_formula", []))
    return {
        "input_CLV": list(r33.measure(formula)),
        "unit_literals_before_R33": [int(x) for x in unit_literals],
        "R33_rule_count": len(history),
        "R33_first_rule": first_rule,
        "R33_rule_sequence": [str(x["rule"]) for x in history],
        "R33_unit_sequence": [int(x["literal"]) for x in history if x["rule"] == "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE"],
        "R33_terminal": str(reduced.get("terminal")),
        "R33_final_CLV": list(r33.measure(final_formula)),
        "R33_final_formula_empty": len(final_formula) == 0,
    }


def inclusion_minimal_conflict_support(r35b, r33, formula, assumptions, reverse=False):
    support = list(canon(r33, formula))
    order = list(reversed(support)) if reverse else list(support)
    checks = 0
    if not r35b.independent_up_conflict_checker(tuple(support), assumptions):
        raise AssertionError("R50G25E_PI_FULL_FORMULA_DOES_NOT_REPRODUCE_RUP_CONFLICT")
    for clause in order:
        if clause not in support:
            continue
        trial = tuple(c for c in support if c != clause)
        checks += 1
        if r35b.independent_up_conflict_checker(trial, assumptions):
            support = list(trial)
    result = canon(r33, support)
    if not r35b.independent_up_conflict_checker(result, assumptions):
        raise AssertionError("R50G25E_PI_MIN_SUPPORT_LOST_CONFLICT")
    for clause in result:
        trial = tuple(c for c in result if c != clause)
        checks += 1
        if r35b.independent_up_conflict_checker(trial, assumptions):
            raise AssertionError(("R50G25E_PI_SUPPORT_NOT_INCLUSION_MINIMAL", clause))
    return {
        "clause_count": len(result),
        "clauses": fjson(result),
        "checker_calls": checks,
        "inclusion_minimal": True,
        "minimum_cardinality_certified": False,
    }


def run():
    parent = r50g25d_pi.run()
    if parent["unique_stalled_lean_core_witness_count"] != 1:
        raise AssertionError(("R50G25E_PI_PARENT_WITNESS_DRIFT", parent["unique_stalled_lean_core_witness_count"]))
    witness = parent["witness"]

    r50g23, r35b, r33 = _chain()
    initial = canon(r33, witness["post_DP_formula"])
    if list(r33.measure(initial)) != [13, 36, 6]:
        raise AssertionError(("R50G25E_PI_INITIAL_CLV_DRIFT", r33.measure(initial)))

    rup = r35b.run_candidate(initial)
    replay = r35b.independent_certificate_replay(initial, rup)
    if not replay.get("pass"):
        raise AssertionError(("R50G25E_PI_RUP_REPLAY_FAIL", replay))
    history = rup.get("history", [])
    if len(history) != 21:
        raise AssertionError(("R50G25E_PI_RUP_HISTORY_COUNT_DRIFT", len(history)))
    final_rup = canon(r33, rup["final_formula"])
    if list(r33.measure(final_rup)) != [6, 6, 6]:
        raise AssertionError(("R50G25E_PI_FINAL_RUP_CLV_DRIFT", r33.measure(final_rup)))

    baseline = reduced_signature(r33, initial)
    if baseline["R33_terminal"] != "STALLED_STACK_LEAN_CORE" or baseline["R33_rule_count"] != 0:
        raise AssertionError(("R50G25E_PI_BASELINE_NOT_STALLED", baseline))

    state = initial
    prefix_rows = []
    states_after = {}
    first_any_r33_progress = None
    first_unit_present = None
    first_unit_first_rule = None
    first_empty_cnf = None

    for index, record in enumerate(history, 1):
        source = tuple(int(x) for x in record["source_clause"])
        strengthened = tuple(int(x) for x in record["strengthened_clause"])
        removed_literal = int(record["removed_literal"])
        assumptions = tuple(int(x) for x in record["assumptions"])
        if source not in state:
            raise AssertionError(("R50G25E_PI_PREFIX_SOURCE_MISSING", index, source))
        if removed_literal not in source:
            raise AssertionError(("R50G25E_PI_PREFIX_REMOVED_LITERAL_MISSING", index, removed_literal))
        if not r35b.independent_up_conflict_checker(state, assumptions):
            raise AssertionError(("R50G25E_PI_PREFIX_RUP_CERT_FAIL", index))

        before = state
        state = r35b.replace_clause_with_subclause(state, source, strengthened)
        states_after[index] = state
        before_set, after_set = set(before), set(state)
        disappeared = sorted(before_set - after_set, key=clause_key)
        appeared = sorted(after_set - before_set, key=clause_key)
        sig = reduced_signature(r33, state)

        if first_any_r33_progress is None and sig["R33_rule_count"] > 0:
            first_any_r33_progress = index
        if first_unit_present is None and sig["unit_literals_before_R33"]:
            first_unit_present = index
        if first_unit_first_rule is None and sig["R33_first_rule"] == "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE":
            first_unit_first_rule = index
        if first_empty_cnf is None and sig["R33_terminal"] == "EMPTY_CNF_SAT" and sig["R33_final_formula_empty"]:
            first_empty_cnf = index

        prefix_rows.append({
            "prefix_length": index,
            "RUP_event": {
                "step": int(record["step"]),
                "source_clause": list(source),
                "removed_literal": removed_literal,
                "strengthened_clause": list(strengthened),
                "assumptions": list(assumptions),
                "R35B_measure_before": record["measure_before"],
                "R35B_measure_after": record["measure_after"],
            },
            "formula_clause_delta": {
                "disappeared_count": len(disappeared),
                "appeared_count": len(appeared),
                "disappeared": fjson(disappeared),
                "appeared": fjson(appeared),
                "exact_duplicate_coalescence_count": max(0, len(disappeared) - len(appeared)),
            },
            "counterfactual_immediate_R33_restart": sig,
        })

    if canon(r33, state) != final_rup:
        raise AssertionError("R50G25E_PI_PREFIX_REPLAY_FINAL_DRIFT")
    if first_any_r33_progress is None:
        raise AssertionError("R50G25E_PI_NO_R33_OPENING_PREFIX")
    if first_unit_first_rule is None:
        raise AssertionError("R50G25E_PI_NO_UNIT_FIRST_PREFIX")
    if first_empty_cnf is None:
        raise AssertionError("R50G25E_PI_NO_EMPTY_CNF_PREFIX")

    decisive_index = int(first_empty_cnf)
    decisive_record = history[decisive_index - 1]
    decisive_pre = initial if decisive_index == 1 else states_after[decisive_index - 1]
    decisive_post = states_after[decisive_index]
    assumptions = tuple(int(x) for x in decisive_record["assumptions"])

    support_forward = inclusion_minimal_conflict_support(r35b, r33, decisive_pre, assumptions, reverse=False)
    support_reverse = inclusion_minimal_conflict_support(r35b, r33, decisive_pre, assumptions, reverse=True)

    decisive_receipt = decisive_record.get("up_receipt", {})
    trail = decisive_receipt.get("trail", [])
    receipt_summary = {
        "conflict": bool(decisive_receipt.get("conflict")),
        "conflict_kind": decisive_receipt.get("conflict_kind"),
        "conflict_clause": decisive_receipt.get("conflict_clause"),
        "trail_length": len(trail),
        "trail": trail,
        "clause_scans": int(decisive_receipt.get("clause_scans", 0)),
        "literal_inspections": int(decisive_receipt.get("literal_inspections", 0)),
    }

    final_sig = reduced_signature(r33, final_rup)
    if final_sig["R33_unit_sequence"] != [2, 3, 4, -5, -6, 7]:
        raise AssertionError(("R50G25E_PI_FINAL_UNIT_SEQUENCE_DRIFT", final_sig["R33_unit_sequence"]))
    if final_sig["R33_terminal"] != "EMPTY_CNF_SAT":
        raise AssertionError(("R50G25E_PI_FINAL_R33_TERMINAL_DRIFT", final_sig))

    decisive_row = prefix_rows[decisive_index - 1]
    next_gate = "R50G25F_PI_RUP_THRESHOLD_EVENT_CAUSAL_SUPPORT_AND_SCHEDULE_LIFT"

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "witness_identity": {
            "spec": witness["spec"],
            "source_hash": witness["source_hash"],
            "target_state_hash": witness["target_state_hash"],
            "post_DP_hash": witness["post_DP_hash"],
        },
        "sealed_RUP_run": {
            "status": rup["status"],
            "history_count": len(history),
            "successful_strengthenings": int(rup["successful_strengthenings"]),
            "initial_R33_CLV": list(r33.measure(initial)),
            "final_R33_CLV": list(r33.measure(final_rup)),
            "independent_certificate_replay_pass": True,
            "ledger": rup.get("ledger", {}),
        },
        "counterfactual_prefix_restart_probe": {
            "baseline": baseline,
            "first_prefix_with_any_R33_progress": first_any_r33_progress,
            "first_prefix_with_unit_clause_present": first_unit_present,
            "first_prefix_with_UNIT_as_first_R33_rule": first_unit_first_rule,
            "shortest_actual_history_prefix_whose_immediate_R33_restart_reaches_EMPTY_CNF": first_empty_cnf,
            "prefix_rows": prefix_rows,
        },
        "decisive_threshold_event": {
            "history_index": decisive_index,
            "event": decisive_row["RUP_event"],
            "formula_clause_delta": decisive_row["formula_clause_delta"],
            "pre_CLV": list(r33.measure(decisive_pre)),
            "post_CLV": list(r33.measure(decisive_post)),
            "post_event_immediate_R33": decisive_row["counterfactual_immediate_R33_restart"],
            "RUP_conflict_receipt": receipt_summary,
            "forward_greedy_inclusion_minimal_clause_support": support_forward,
            "reverse_greedy_inclusion_minimal_clause_support": support_reverse,
            "support_sets_identical": support_forward["clauses"] == support_reverse["clauses"],
        },
        "sealed_final_restart_effect": {
            "RUP_final_CLV": list(r33.measure(final_rup)),
            "R33_after_sealed_RUP": final_sig,
            "UNIT_cascade": [2, 3, 4, -5, -6, 7],
            "terminal": "EMPTY_CNF_SAT",
        },
        "next_gate": next_gate,
        "interpretation_contract": {
            "RUP_history_entries_are_sequential_single_literal_vivification_events": True,
            "shortest_prefix_is_with_respect_to_actual_deterministic_R35B_history_order": True,
            "counterfactual_immediate_restart_is_not_the_sealed_R47J_schedule": True,
            "first_empty_cnf_prefix_is_not_a_minimum_unordered_event_subset": True,
            "greedy_clause_support_is_inclusion_minimal_not_minimum_cardinality": True,
            "causal_threshold_is_for_this_single_sealed_witness_only": True,
            "RUP_restart_door_generalization_outside_this_witness": False,
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
