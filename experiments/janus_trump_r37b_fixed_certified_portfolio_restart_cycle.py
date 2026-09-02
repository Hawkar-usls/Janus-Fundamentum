from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35_nonaffine_core_freeze_structure_intake as r35
import janus_trump_r35b_single_literal_rup_vivification as r35b

SEED = 36001
N = 28
RATIO = 4.2
R37_FIRST_RUP_HASH = "6cda29fd34c3f4f0495f696ba3d371ebce4d4593c1f71face5ecf4af182751b0"
R37_FOLLOWUP_HASH = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"


def formula_hash(formula) -> str:
    return r35.canonical_json_sha256([list(c) for c in formula])


def clv(formula) -> Tuple[int, int, int]:
    return r33.measure(formula)


def status_from_r33_terminal(terminal: str) -> str:
    return {
        "EMPTY_CNF_SAT": "DIRECT_SAT_EMPTY_CNF",
        "EMPTY_CLAUSE_UNSAT": "DIRECT_UNSAT_EMPTY_CLAUSE",
        "HORN": "DECLARED_POLY_TERMINAL_HORN",
        "2CNF": "DECLARED_POLY_TERMINAL_2CNF",
    }[terminal]


def run_fixed_cycle() -> dict:
    formula = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    initial_formula = formula
    initial_clv = clv(formula)
    m, _, n = initial_clv
    state_measure_bound = (m + 1) * (m * n + 1) * (n + 1) - 1

    cycles: List[dict] = []
    total_successful_transformations = 0
    ledger = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "RUP_certificate_history_bytes": 0,
        "GF2_estimated_bit_ops": 0,
    }

    terminal_status = None
    terminal_semantic_claim = None
    affine_certificate = None
    terminal_formula = formula

    for cycle_index in range(state_measure_bound + 1):
        cycle_before = formula
        cycle_before_hash = formula_hash(cycle_before)
        cycle_before_clv = clv(cycle_before)

        r33_result = r33.simplify(cycle_before)
        after_r33 = r33.canonical_formula(r33_result["final_formula"])
        after_r33_hash = formula_hash(after_r33)
        after_r33_clv = clv(after_r33)
        r33_changed = after_r33_hash != cycle_before_hash
        if r33_changed and not (after_r33_clv < cycle_before_clv):
            raise AssertionError(("R33 violated global CLV descent", cycle_before_clv, after_r33_clv))

        total_successful_transformations += r33_result["total_rule_applications"]
        ledger["R33_check_operation_upper_ledger"] += r33_result["total_check_operation_count_upper_ledger"]
        ledger["R33_certificate_bytes"] += r33_result["total_certificate_bytes"]

        cycle_record: Dict = {
            "cycle": cycle_index,
            "before_hash": cycle_before_hash,
            "before_measure_CLV": list(cycle_before_clv),
            "R33": {
                "terminal": r33_result["terminal"],
                "rule_applications": r33_result["total_rule_applications"],
                "rule_counts": r33_result["rule_counts"],
                "after_hash": after_r33_hash,
                "after_measure_CLV": list(after_r33_clv),
                "changed": r33_changed,
            },
        }

        if r33_result["terminal"] != "STALLED_STACK_LEAN_CORE":
            terminal_status = status_from_r33_terminal(r33_result["terminal"])
            terminal_semantic_claim = True if terminal_status == "DIRECT_SAT_EMPTY_CNF" else False if terminal_status == "DIRECT_UNSAT_EMPTY_CLAUSE" else None
            terminal_formula = after_r33
            cycle_record["stop"] = terminal_status
            cycles.append(cycle_record)
            break

        recognition = r34.recognize_complete_affine_cnf(after_r33)
        cycle_record["R34"] = {
            "recognized": recognition["recognized"],
            "reason": recognition["reason"],
            "equation_count": recognition.get("equation_count"),
            "literal_inspections": recognition.get("literal_inspections"),
            "failed_vars": recognition.get("failed_vars"),
        }
        if recognition["recognized"]:
            solution = r34.solve_gf2_with_certificate(recognition["equations"])
            certificate = r34.verify_affine_certificate(after_r33, recognition, solution)
            if not certificate["pass"]:
                raise AssertionError(("affine certificate failed", certificate))
            ledger["GF2_estimated_bit_ops"] += solution["estimated_bit_ops"]
            terminal_status = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            terminal_semantic_claim = bool(solution["sat"])
            affine_certificate = certificate
            terminal_formula = after_r33
            cycle_record["R34"]["solution"] = {
                "sat": solution["sat"],
                "rank": solution["rank"],
                "row_xors": solution["row_xors"],
                "row_swaps": solution["row_swaps"],
                "estimated_bit_ops": solution["estimated_bit_ops"],
                "certificate": certificate,
            }
            cycle_record["stop"] = terminal_status
            cycles.append(cycle_record)
            break

        rup = r35b.run_candidate(after_r33)
        rup_checker = r35b.independent_certificate_replay(after_r33, rup)
        if not rup_checker["pass"]:
            raise AssertionError(("RUP certificate replay failed", cycle_index, rup_checker))
        after_rup = r33.canonical_formula(rup["final_formula"])
        after_rup_hash = formula_hash(after_rup)
        after_rup_clv = clv(after_rup)
        rup_changed = after_rup_hash != after_r33_hash
        if rup_changed and not (after_rup_clv < after_r33_clv):
            raise AssertionError(("RUP violated global CLV descent", after_r33_clv, after_rup_clv))
        if (r33_changed or rup_changed) and not (after_rup_clv < cycle_before_clv):
            raise AssertionError(("full cycle failed global CLV descent", cycle_before_clv, after_rup_clv))

        total_successful_transformations += rup["successful_strengthenings"]
        ledger["RUP_checks"] += rup["ledger"]["rup_checks"]
        ledger["RUP_UP_clause_scans"] += rup["ledger"]["up_clause_scans"]
        ledger["RUP_UP_literal_inspections"] += rup["ledger"]["up_literal_inspections"]
        ledger["RUP_certificate_history_bytes"] += len(json.dumps(rup["history"], sort_keys=True, separators=(",", ":")).encode("utf-8"))

        cycle_record["RUP"] = {
            "status": rup["status"],
            "successful_strengthenings": rup["successful_strengthenings"],
            "initial_measure_LCV": rup["initial_measure"],
            "final_measure_LCV": rup["final_measure"],
            "after_hash": after_rup_hash,
            "after_measure_CLV": list(after_rup_clv),
            "changed": rup_changed,
            "independent_certificate_checker": rup_checker,
        }

        # Frozen R37 discovery checkpoints: these are exact replay guards, not routing hints.
        if cycle_index == 0:
            if after_rup_hash != R37_FIRST_RUP_HASH or rup["successful_strengthenings"] != 153:
                raise AssertionError(("R37 first RUP checkpoint drift", after_rup_hash, rup["successful_strengthenings"]))
        if cycle_index == 1:
            if r33_result["total_rule_applications"] != 26 or after_r33_clv != (45, 110, 13):
                raise AssertionError(("R37 reactivated R33 checkpoint drift", r33_result["total_rule_applications"], after_r33_clv))
            if after_rup_hash != R37_FOLLOWUP_HASH or rup["successful_strengthenings"] != 5:
                raise AssertionError(("R37 followup RUP checkpoint drift", after_rup_hash, rup["successful_strengthenings"]))

        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal_status = "RUP_UNSAT"
            terminal_semantic_claim = False
            terminal_formula = after_rup
            cycle_record["stop"] = terminal_status
            cycles.append(cycle_record)
            break

        if not rup_changed:
            terminal_status = "STALLED_PORTFOLIO_FIXPOINT"
            terminal_semantic_claim = None
            terminal_formula = after_rup
            cycle_record["stop"] = terminal_status
            cycles.append(cycle_record)
            break

        cycle_record["restart"] = True
        cycles.append(cycle_record)
        formula = after_rup
    else:
        raise AssertionError("polynomial state-measure bound exhausted")

    if total_successful_transformations > state_measure_bound:
        raise AssertionError(("successful transformation count exceeds frozen polynomial measure-state bound", total_successful_transformations, state_measure_bound))

    return {
        "initial_formula_hash": formula_hash(initial_formula),
        "initial_measure_CLV": list(initial_clv),
        "state_measure_domain_upper_bound": state_measure_bound,
        "cycles": cycles,
        "cycle_count": len(cycles),
        "restart_count": sum(bool(c.get("restart")) for c in cycles),
        "total_successful_transformations": total_successful_transformations,
        "terminal_status": terminal_status,
        "terminal_semantic_claim": terminal_semantic_claim,
        "terminal_formula_hash": formula_hash(terminal_formula),
        "terminal_measure_CLV": list(clv(terminal_formula)),
        "affine_certificate": affine_certificate,
        "ledger": ledger,
    }


def verdict_for(status: str) -> str:
    if status in {"DIRECT_SAT_EMPTY_CNF", "DIRECT_UNSAT_EMPTY_CLAUSE"}:
        return "R37B_FIXED_RESTART_CYCLE_REACHES_DIRECT_SEMANTIC_TERMINAL__EXPOSED_ONLY"
    if status in {"DECLARED_POLY_TERMINAL_HORN", "DECLARED_POLY_TERMINAL_2CNF"}:
        return "R37B_FIXED_RESTART_CYCLE_REACHES_DECLARED_POLY_CLASS__SOLVER_NOT_INTEGRATED"
    if status in {"AFFINE_XOR_SAT", "AFFINE_XOR_UNSAT"}:
        return "R37B_FIXED_RESTART_CYCLE_REACHES_AFFINE_TERMINAL__EXPOSED_ONLY"
    if status == "RUP_UNSAT":
        return "R37B_FIXED_RESTART_CYCLE_RUP_UNSAT__EXPOSED_ONLY"
    if status == "STALLED_PORTFOLIO_FIXPOINT":
        return "R37B_FIXED_RESTART_CYCLE_STALLS_AT_PORTFOLIO_FIXPOINT__NO_SEMANTIC_VERDICT"
    raise AssertionError(status)


def run_audit() -> dict:
    cycle = run_fixed_cycle()
    return {
        "schema": "JANUS_TRUMP_R37B_FIXED_CERTIFIED_PORTFOLIO_RESTART_CYCLE_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict_for(cycle["terminal_status"]),
        "exposed_world": {"seed": SEED, "n": N, "ratio": RATIO, "known_R36_truth": "SAT_DIAGNOSTIC_ONLY__NOT_USED_BY_CANDIDATE"},
        "fixed_operator_order": ["R33_SAFE_REDUCTION_TO_FIXPOINT", "R34_AFFINE_CHECK", "R35B_RUP_TO_FIXPOINT", "RESTART_IF_RUP_CHANGED"],
        "global_progress_theorem_receipt": {
            "measure": "(C,L,V)_LEX",
            "initial_m": cycle["initial_measure_CLV"][0],
            "initial_n": cycle["initial_measure_CLV"][2],
            "C_upper_bound": cycle["initial_measure_CLV"][0],
            "L_upper_bound": cycle["initial_measure_CLV"][0] * cycle["initial_measure_CLV"][2],
            "V_upper_bound": cycle["initial_measure_CLV"][2],
            "state_measure_domain_upper_bound": cycle["state_measure_domain_upper_bound"],
            "observed_successful_transformations": cycle["total_successful_transformations"],
            "observed_restarts": cycle["restart_count"],
            "every_changed_stage_strictly_decreased_measure": True,
            "polynomial_termination_of_this_controller": True,
            "decision_completeness_proved": False,
        },
        "candidate": cycle,
        "candidate_firewall": {
            "new_semantic_rule_added": False,
            "new_terminal_language_added": False,
            "Horn_or_2SAT_solver_hidden": False,
            "external_SAT_solver_used": False,
            "assignment_enumeration_used": False,
            "known_truth_used_for_routing": False,
            "operator_order_dynamic": False,
        },
        "captain_verdict": {
            "law": "ITERATE REACTIVATING CERTIFIED OPERATORS UNDER ONE DESCENDING GLOBAL MEASURE BEFORE INVENTING A NEW OPERATOR.",
            "key_boundary": "Polynomial termination is now explicit for this fixed controller. The unresolved theorem is whether every nonterminal formula reaches a semantic or integrated polynomial terminal rather than a portfolio fixpoint.",
        },
        "R31_obligation_impact": {
            "obligations_closed": 0,
            "partial_progress": "A polynomial termination bound for the fixed restart controller is supported, but R31 requires universal decision completeness and end-to-end polynomial solving, not termination alone."
        },
        "next_gate": {
            "if_declared_poly_terminal": "INTEGRATE_EXACT_STANDARD_SOLVER_FOR_THAT_ALREADY_DECLARED_CLASS_IN_A_SEPARATE_PREREGISTERED_GATE",
            "if_direct_or_affine_terminal": "FREEZE_CONTROLLER_AND_RUN_FRESH_UNSEEN_RESTART_HOLDOUT",
            "if_fixpoint_stall": "FREEZE_EXACT_PORTFOLIO_FIXPOINT_BEFORE_ANY_NEW_SAT_SIDE_MECHANISM"
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_audit()
    c = d["candidate"]
    assert c["cycles"][0]["RUP"]["after_hash"] == R37_FIRST_RUP_HASH
    assert c["cycles"][1]["R33"]["rule_applications"] == 26
    assert c["cycles"][1]["RUP"]["after_hash"] == R37_FOLLOWUP_HASH
    assert c["total_successful_transformations"] <= c["state_measure_domain_upper_bound"]
    assert not any(d["candidate_firewall"].values())
    print("R37B_SELF_TEST_PASS", d["verdict"], c["cycle_count"], c["restart_count"], c["terminal_status"], c["terminal_measure_CLV"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_audit(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
