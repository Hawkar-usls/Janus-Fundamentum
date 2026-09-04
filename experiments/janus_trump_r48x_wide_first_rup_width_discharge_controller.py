from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r48o_width4_first_certified_chain_falsifier as r48o

GATE = "JANUS_TRUMP_R48X_WIDE_FIRST_RUP_WIDTH_DISCHARGE_CONTROLLER"
PATH = [2, 4, 5, 7, 9, 10]
DEEP_STEPS = {3, 4, 6}
EXPECTED_GENERAL_HISTORIES = {3: 28, 4: 2, 6: 68}
EXPECTED_R33_APPS = {3: 0, 4: 0, 6: 1}
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def fhash(f):
    return r48o.formula_hash(canon(f))


def maxw(f):
    x = canon(f)
    return max((len(c) for c in x), default=0)


def excess_width(f, W=WIDTH_CAP):
    return sum(max(0, len(c) - W) for c in canon(f))


def wide_clauses(f, W=WIDTH_CAP):
    return [tuple(c) for c in canon(f) if len(c) > W]


def first_wide_rup_strengthening(formula, W=WIDTH_CAP):
    formula = canon(formula)
    ledger = {"rup_checks": 0, "up_clause_scans": 0, "up_literal_inspections": 0}
    for clause in formula:
        if len(clause) <= W:
            continue
        for removed_literal in sorted(clause, key=r35b.lit_key):
            strengthened = tuple(l for l in clause if l != removed_literal)
            assumptions = tuple(-l for l in sorted(strengthened, key=r35b.lit_key))
            receipt = r35b.candidate_unit_propagation_trace(formula, assumptions)
            ledger["rup_checks"] += 1
            ledger["up_clause_scans"] += int(receipt["clause_scans"])
            ledger["up_literal_inspections"] += int(receipt["literal_inspections"])
            if not receipt["conflict"]:
                continue
            if not r35b.independent_up_conflict_checker(formula, assumptions):
                raise AssertionError(("R48X_INDEPENDENT_RUP_REPLAY_FAIL", clause, removed_literal))
            updated = canon(r35b.replace_clause_with_subclause(formula, clause, strengthened))
            before_E = excess_width(formula, W)
            after_E = excess_width(updated, W)
            if not after_E < before_E:
                raise AssertionError(("R48X_EXCESS_WIDTH_NOT_DESCENDING", before_E, after_E, clause, strengthened))
            return {
                "source_clause": list(clause),
                "removed_literal": int(removed_literal),
                "strengthened_clause": list(strengthened),
                "assumptions": list(assumptions),
                "up_receipt": receipt,
                "independent_up_conflict_pass": True,
                "formula_hash_before": fhash(formula),
                "formula_hash_after": fhash(updated),
                "CLV_before": list(clv(formula)),
                "CLV_after": list(clv(updated)),
                "max_width_before": maxw(formula),
                "max_width_after": maxw(updated),
                "E4_before": int(before_E),
                "E4_after": int(after_E),
                "updated_formula": updated,
            }, ledger
    return None, ledger


def run_wide_first(initial, W=WIDTH_CAP):
    formula = canon(initial)
    initial_E = excess_width(formula, W)
    initial_literal_mass = clv(formula)[1]
    history = []
    ledger = {"rup_checks": 0, "up_clause_scans": 0, "up_literal_inspections": 0}

    for _ in range(initial_E + 1):
        if maxw(formula) <= W:
            return {
                "status": "WIDTH_RESET",
                "initial_hash": fhash(initial),
                "final_hash": fhash(formula),
                "initial_CLV": list(clv(initial)),
                "final_CLV": list(clv(formula)),
                "initial_max_width": maxw(initial),
                "final_max_width": maxw(formula),
                "initial_E4": int(initial_E),
                "final_E4": int(excess_width(formula, W)),
                "successful_strengthenings": len(history),
                "history": history,
                "ledger": ledger,
                "surviving_wide_clauses": [],
                "resource_bound_pass": len(history) <= initial_E,
                "literal_mass_never_increases": clv(formula)[1] <= initial_literal_mass,
                "final_formula": [list(c) for c in formula],
            }
        proposal, local = first_wide_rup_strengthening(formula, W)
        for k in ledger:
            ledger[k] += int(local[k])
        if proposal is None:
            survivors = wide_clauses(formula, W)
            return {
                "status": "WIDE_RUP_STALL",
                "initial_hash": fhash(initial),
                "final_hash": fhash(formula),
                "initial_CLV": list(clv(initial)),
                "final_CLV": list(clv(formula)),
                "initial_max_width": maxw(initial),
                "final_max_width": maxw(formula),
                "initial_E4": int(initial_E),
                "final_E4": int(excess_width(formula, W)),
                "successful_strengthenings": len(history),
                "history": history,
                "ledger": ledger,
                "surviving_wide_clauses": [list(c) for c in survivors],
                "resource_bound_pass": len(history) <= initial_E,
                "literal_mass_never_increases": clv(formula)[1] <= initial_literal_mass,
                "final_formula": [list(c) for c in formula],
            }
        updated = proposal.pop("updated_formula")
        history.append(proposal)
        formula = canon(updated)
    raise AssertionError(("R48X_INITIAL_E4_BOUND_EXHAUSTED", initial_E, len(history), excess_width(formula, W)))


def run():
    _, _, root = r48o.reconstruct_root()
    current = canon(root)
    rows = []

    for step, var in enumerate(PATH, 1):
        candidate = r48o.r47m.macro_candidate_full_closure(current, int(var))
        if candidate is None:
            raise AssertionError(("R48X_PATH_CANDIDATE_MISSING", step, var))
        replay = r48o.r47m.independent_replay(current, candidate)
        if not replay["pass"]:
            raise AssertionError(("R48X_PATH_REPLAY_FAIL", step, var, replay))
        forced = canon(candidate["DP"]["transformed"])
        full_final = canon(candidate["normalization"]["final_formula"])

        if step in DEEP_STEPS:
            if maxw(forced) != 5:
                raise AssertionError(("R48X_EXPECTED_FORCED_WIDTH5_DRIFT", step, maxw(forced)))

            # Harness-alignment addendum: R47J always applies R33 before its RUP call.
            r33_stage = r33.simplify(forced)
            post_r33 = canon(r33_stage["final_formula"])
            r33_apps = int(r33_stage["total_rule_applications"])
            if r33_apps != EXPECTED_R33_APPS[step]:
                raise AssertionError(("R48X_R33_STAGE_DRIFT", step, r33_apps, EXPECTED_R33_APPS[step]))

            general = r35b.run_candidate(post_r33)
            general_replay = r35b.independent_certificate_replay(post_r33, general)
            if not general_replay["pass"]:
                raise AssertionError(("R48X_GENERAL_RUP_REPLAY_FAIL", step, general_replay))
            if int(general["successful_strengthenings"]) != EXPECTED_GENERAL_HISTORIES[step]:
                raise AssertionError(("R48X_GENERAL_HISTORY_DRIFT", step, general["successful_strengthenings"]))

            wide = run_wide_first(post_r33, WIDTH_CAP)
            if not wide["resource_bound_pass"] or not wide["literal_mass_never_increases"]:
                raise AssertionError(("R48X_WIDE_RESOURCE_INVARIANT_FAIL", step, wide))
            if any(not h["independent_up_conflict_pass"] for h in wide["history"]):
                raise AssertionError(("R48X_WIDE_CERTIFICATE_FAIL", step))

            rows.append({
                "step": int(step),
                "pivot": int(var),
                "forced_hash": fhash(forced),
                "forced_CLV": list(clv(forced)),
                "forced_max_width": maxw(forced),
                "forced_E4": excess_width(forced),
                "R33_stage": {
                    "application_count": r33_apps,
                    "post_R33_hash": fhash(post_r33),
                    "post_R33_CLV": list(clv(post_r33)),
                    "post_R33_max_width": maxw(post_r33),
                    "post_R33_E4": excess_width(post_r33),
                },
                "general_RUP": {
                    "status": general["status"],
                    "successful_strengthenings": int(general["successful_strengthenings"]),
                    "rup_checks": int(general["ledger"]["rup_checks"]),
                    "up_clause_scans": int(general["ledger"]["up_clause_scans"]),
                    "up_literal_inspections": int(general["ledger"]["up_literal_inspections"]),
                    "final_max_width": maxw(general["final_formula"]),
                    "independent_replay_pass": True,
                },
                "wide_first": wide,
                "full_R47M_terminal": candidate["normalization"]["terminal"],
                "full_R47M_final_max_width": maxw(full_final),
                "full_R47M_SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
            })
        current = full_final

    reset = {r["step"]: r["wide_first"]["status"] == "WIDTH_RESET" for r in rows}
    if reset[3] and reset[4] and not reset[6]:
        classification = "WIDE_FIRST_REPRODUCES_BOTH_NONTERMINAL_RESETS_AND_ISOLATES_STEP6_SURVIVOR"
    elif reset[3] and reset[4] and reset[6]:
        classification = "WIDE_FIRST_RESETS_ALL_THREE_DEEP_STEPS"
    elif reset[3] or reset[4]:
        classification = "WIDE_FIRST_PARTIAL_RESET_ONLY"
    else:
        classification = "WIDE_FIRST_FAILS_TO_REPRODUCE_SEALED_NONTERMINAL_RESETS"

    return {
        "gate": GATE,
        "classification": classification,
        "width_cap": WIDTH_CAP,
        "harness_alignment_addendum_applied": True,
        "rows": rows,
        "resource_theorem": {
            "potential": "E4(F)=sum_C max(0,|C|-4)",
            "every_success_strictly_decreases_E4": True,
            "successful_step_bound": "successful_strengthenings <= E4(initial)",
            "proof_scope": "conditional on existence of a certified wide-clause RUP strengthening; no coverage claim",
            "equivalence_argument": "each accepted subclause is RUP-implied by the current formula and itself implies the replaced parent clause, so replacement is equivalence-preserving; every implication witness is independently replayed",
        },
        "summary": {
            "R33_application_counts": {str(r["step"]): r["R33_stage"]["application_count"] for r in rows},
            "post_R33_E4": {str(r["step"]): r["R33_stage"]["post_R33_E4"] for r in rows},
            "general_successful_strengthenings": {str(r["step"]): r["general_RUP"]["successful_strengthenings"] for r in rows},
            "wide_successful_strengthenings": {str(r["step"]): r["wide_first"]["successful_strengthenings"] for r in rows},
            "general_rup_checks": {str(r["step"]): r["general_RUP"]["rup_checks"] for r in rows},
            "wide_rup_checks": {str(r["step"]): r["wide_first"]["ledger"]["rup_checks"] for r in rows},
            "wide_statuses": {str(r["step"]): r["wide_first"]["status"] for r in rows},
            "survivor_counts": {str(r["step"]): len(r["wide_first"]["surviving_wide_clauses"]) for r in rows},
        },
        "interpretation": {
            "finite_R48V_calibration_only": True,
            "first_run_33865461712_was_harness_input_mismatch": True,
            "universal_width4_reset_proved": False,
            "wide_first_can_be_used_as_certified_fast_producer_when_it_succeeds": True,
            "general_RUP_remains_valid_fallback": True,
        },
        "firewall": {
            "UNIVERSAL_WIDTH_RESET_LEMMA": "NOT_PROVED",
            "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
            "UNIVERSAL_CONSTANT_WIDTH_COVERAGE": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    d = run()
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": d["gate"],
        "classification": d["classification"],
        "summary": d["summary"],
        "rows": [{
            "step": r["step"],
            "pivot": r["pivot"],
            "forced_E4": r["forced_E4"],
            "r33_apps": r["R33_stage"]["application_count"],
            "post_R33_E4": r["R33_stage"]["post_R33_E4"],
            "general_successes": r["general_RUP"]["successful_strengthenings"],
            "general_checks": r["general_RUP"]["rup_checks"],
            "wide_status": r["wide_first"]["status"],
            "wide_successes": r["wide_first"]["successful_strengthenings"],
            "wide_checks": r["wide_first"]["ledger"]["rup_checks"],
            "wide_final_width": r["wide_first"]["final_max_width"],
            "wide_survivors": r["wide_first"]["surviving_wide_clauses"],
        } for r in d["rows"]],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
