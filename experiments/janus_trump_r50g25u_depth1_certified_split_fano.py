from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import janus_trump_r50g25t_fano_residual_minimization_independent_replay as r50g25t

GATE = "JANUS_TRUMP_R50G25U_DEPTH1_CERTIFIED_SPLIT_ACROSS_FANO_RESIDUAL"
PARENT_T_RUN = 34040530524
PREREG_COMMIT = "bc4444527d4203c6e5571e6d141f6a6d5cb595f3"
EXPECTED_HASH = "466163011411ccd10520539fb80f0bec7a9de934400961cfa6a25f1c58c38a00"
SPLIT_VAR = 1


def exact_model_count(r33, formula, universe):
    count = 0
    for bits in itertools.product((False, True), repeat=len(universe)):
        a = dict(zip(universe, bits))
        if r33.eval_formula(formula, a):
            count += 1
    return count


def sum_ledgers(children):
    keys = (
        "R33_check_operation_upper_ledger",
        "R33_certificate_bytes",
        "RUP_checks",
        "RUP_UP_clause_scans",
        "RUP_UP_literal_inspections",
        "RUP_successful_strengthenings",
        "GF2_estimated_bit_ops",
        "restart_count",
    )
    return {k: sum(int(c["micro_ledger"].get(k, 0)) for c in children) for k in keys}


def decisive_unsat(micro):
    return micro.get("terminal") is not None and micro.get("semantic_sat") is False


def run():
    _b, r50g23, r35b, r33, r47j = r50g25t.r50g25s.r50g25r.r50g25g._chain()
    formula = r50g25t.r50g25s.nae_formula(r33, r50g25t.r50g25s.fano_edges())
    formula_hash = r50g23.r50g4.fhash(formula)
    if formula_hash != EXPECTED_HASH or tuple(r33.measure(formula)) != (14, 42, 7):
        raise AssertionError(("R50G25U_TARGET_DRIFT", formula_hash, r33.measure(formula)))

    parent_micro = r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(formula, r50g23, r35b, r33, r47j)
    if parent_micro.get("terminal") is not None:
        raise AssertionError(("R50G25U_PARENT_NO_LONGER_RESIDUAL", parent_micro.get("terminal")))

    children = []
    for lit in (-SPLIT_VAR, SPLIT_VAR):
        child_formula = r33.canonical_formula(list(formula) + [(lit,)])
        if (lit,) not in child_formula:
            raise AssertionError(("R50G25U_CHILD_UNIT_MISSING", lit))

        baseline = r33.simplify(child_formula)
        replay_failures = r50g25t.r50g25s.r50g25r.independent_r33_history_audit(r33, child_formula, baseline)
        if replay_failures:
            raise AssertionError(("R50G25U_CHILD_R33_REPLAY_FAIL", lit, replay_failures))

        micro = r50g25t.r50g25s.r50g25r.r50g25g.micro_normalize(child_formula, r50g23, r35b, r33, r47j)
        ledger_ok, ledger_reason = r50g25t.r50g25s.r50g25r.polynomial_ledger_audit(r47j, r33, child_formula, micro)
        if not ledger_ok:
            raise AssertionError(("R50G25U_CHILD_LEDGER_FAIL", lit, ledger_reason))

        child = {
            "assumption_literal": lit,
            "meaning": f"x{SPLIT_VAR}={'true' if lit > 0 else 'false'}",
            "initial_CLV": list(r33.measure(child_formula)),
            "baseline_R33_terminal": baseline.get("terminal"),
            "baseline_R33_rule_applications": int(baseline.get("total_rule_applications", 0)),
            "baseline_R33_final_CLV": baseline.get("final_measure"),
            "micro_terminal": micro.get("terminal") if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT",
            "micro_semantic_sat": micro.get("semantic_sat"),
            "micro_decisive_UNSAT": decisive_unsat(micro),
            "micro_final_CLV": micro.get("final_CLV"),
            "micro_round_count": micro.get("round_count"),
            "micro_restart_count": micro.get("restart_count"),
            "micro_ledger": micro.get("ledger", {}),
            "micro_rounds": micro.get("rounds", []),
            "SAT_reconstruction": micro.get("SAT_reconstruction"),
        }
        children.append(child)

    both_unsat = all(c["micro_decisive_UNSAT"] for c in children)
    any_residual = any(c["micro_terminal"] == "RESIDUAL_FIXPOINT" for c in children)

    split_certificate = {
        "split_variable": SPLIT_VAR,
        "covered_assignments": [False, True],
        "children_present": sorted(c["assumption_literal"] for c in children) == [-SPLIT_VAR, SPLIT_VAR],
        "child_UNSAT_receipts": [bool(c["micro_decisive_UNSAT"]) for c in children],
        "parent_UNSAT_derived": bool(both_unsat),
        "logic": "(F AND not x1 UNSAT) AND (F AND x1 UNSAT) => F UNSAT",
    }

    universe = list(range(1, 8))
    parent_models = exact_model_count(r33, formula, universe)
    child_validation = []
    for lit in (-SPLIT_VAR, SPLIT_VAR):
        child_formula = r33.canonical_formula(list(formula) + [(lit,)])
        child_validation.append({
            "assumption_literal": lit,
            "assignment_space_checked": 128,
            "model_count": exact_model_count(r33, child_formula, universe),
        })

    if both_unsat:
        verdict = "FANO_RESIDUAL_CROSSED_BY_DEPTH1_CERTIFIED_SPLIT"
        next_gate = "R50G25V_SPLIT_DEPTH_AND_TREE_SIZE_AUDIT_BEYOND_FANO"
    elif any_residual:
        verdict = "DEPTH1_SPLIT_INSUFFICIENT_FOR_FANO_RESIDUAL"
        next_gate = "R50G25V_DEPTH2_SPLIT_OR_STRONGER_INFERENCE_ON_RESIDUAL_CHILD"
    else:
        verdict = "SPLIT_CHILD_NONRESIDUAL_BUT_NOT_BOTH_CERTIFIED_UNSAT"
        next_gate = "R50G25V_CHILD_TERMINAL_SEMANTIC_FORENSICS"

    aggregate = sum_ledgers(children)
    return {
        "gate": GATE,
        "parent_T_run": PARENT_T_RUN,
        "preregistration_commit": PREREG_COMMIT,
        "target": {
            "family": "FANO_NAE",
            "formula_hash": formula_hash,
            "CLV": list(r33.measure(formula)),
            "parent_micro_terminal": "RESIDUAL_FIXPOINT",
        },
        "new_door": {
            "kind": "DEPTH1_DPLL_STYLE_SPLIT_CERTIFICATE",
            "split_variable": SPLIT_VAR,
            "branch_depth": 1,
            "leaf_count": 2,
        },
        "children": children,
        "split_certificate": split_certificate,
        "aggregate_child_ledger": aggregate,
        "exact_truth_validation": {
            "parent_assignment_space_checked": 128,
            "parent_model_count": parent_models,
            "child_checks": child_validation,
            "validation_only_not_algorithmic_authority": True,
        },
        "verdict": verdict,
        "next_gate": next_gate,
        "interpretation_contract": {
            "depth1_split_is_a_local_certified_door_for_this_witness": bool(both_unsat),
            "one_witness_depth1_split_success_is_not_universal_completeness": True,
            "generic_branching_tree_can_be_exponential": True,
            "branching_is_not_polynomial_without_a_polynomial_depth_or_tree_size_bound": True,
            "truth_enumeration_is_not_algorithmic_authority": True,
            "Fano_counterexample_to_old_micro_schedule_remains_valid": True,
        },
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
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
