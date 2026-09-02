from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35_nonaffine_core_freeze_structure_intake as r35
import janus_trump_r35b_single_literal_rup_vivification as r35b

SEED = 36001
N = 28
RATIO = 4.2
EXPECTED_RUP_FINAL_HASH = "6cda29fd34c3f4f0495f696ba3d371ebce4d4593c1f71face5ecf4af182751b0"
EXPECTED_RUP_FINAL_MEASURE_LCV = [146, 71, 28]
EXPECTED_RUP_STRENGTHENINGS = 153


def formula_hash(formula) -> str:
    return r35.canonical_json_sha256([list(c) for c in formula])


def reconstruct_frozen_stall() -> dict:
    source = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    source_hash = formula_hash(source)
    r33_first = r33.simplify(source)
    core = r33.canonical_formula(r33_first["final_formula"])
    core_hash = formula_hash(core)
    recognition = r34.recognize_complete_affine_cnf(core)
    if recognition["recognized"]:
        raise AssertionError("R36 seed 36001 unexpectedly became affine before RUP")
    rup = r35b.run_candidate(core)
    checker = r35b.independent_certificate_replay(core, rup)
    residual = r33.canonical_formula(rup["final_formula"])
    residual_hash = formula_hash(residual)
    if rup["status"] != "STALLED_RUP_CORE":
        raise AssertionError(("R36 stall status drift", rup["status"]))
    if rup["successful_strengthenings"] != EXPECTED_RUP_STRENGTHENINGS:
        raise AssertionError(("RUP strengthening count drift", rup["successful_strengthenings"]))
    if rup["final_measure"] != EXPECTED_RUP_FINAL_MEASURE_LCV:
        raise AssertionError(("RUP final measure drift", rup["final_measure"]))
    if residual_hash != EXPECTED_RUP_FINAL_HASH:
        raise AssertionError(("RUP residual hash drift", residual_hash))
    if not checker["pass"] or checker["final_conflict"]:
        raise AssertionError(("RUP checker drift", checker))
    return {
        "source": source,
        "source_hash": source_hash,
        "R33_first": r33_first,
        "pre_RUP_core": core,
        "pre_RUP_core_hash": core_hash,
        "RUP": rup,
        "RUP_checker": checker,
        "residual": residual,
        "residual_hash": residual_hash,
    }


def existing_portfolio_composition_probe(residual) -> dict:
    before_hash = formula_hash(residual)
    before_measure_CLV = list(r33.measure(residual))
    replay = r33.simplify(residual)
    replay_formula = r33.canonical_formula(replay["final_formula"])
    after_hash = formula_hash(replay_formula)
    after_measure_CLV = list(r33.measure(replay_formula))
    changed = after_hash != before_hash

    affine = None
    diagnostic_rup = None
    if changed and replay["terminal"] == "STALLED_STACK_LEAN_CORE":
        recognition = r34.recognize_complete_affine_cnf(replay_formula)
        affine = {
            "recognized": recognition["recognized"],
            "reason": recognition["reason"],
            "equation_count": recognition.get("equation_count"),
            "literal_inspections": recognition.get("literal_inspections"),
            "failed_vars": recognition.get("failed_vars"),
        }
        diagnostic = r35b.run_candidate(replay_formula)
        diagnostic_checker = r35b.independent_certificate_replay(replay_formula, diagnostic)
        diagnostic_final = r33.canonical_formula(diagnostic["final_formula"])
        diagnostic_rup = {
            "status": diagnostic["status"],
            "successful_strengthenings": diagnostic["successful_strengthenings"],
            "initial_measure_LCV": diagnostic["initial_measure"],
            "final_measure_LCV": diagnostic["final_measure"],
            "final_formula_hash": formula_hash(diagnostic_final),
            "independent_certificate_checker": diagnostic_checker,
            "ledger": diagnostic["ledger"],
        }

    return {
        "before_hash": before_hash,
        "before_measure_CLV": before_measure_CLV,
        "R33_replay": {
            "terminal": replay["terminal"],
            "rule_applications": replay["total_rule_applications"],
            "rule_counts": replay["rule_counts"],
            "certificate_bytes": replay["total_certificate_bytes"],
            "check_operation_count_upper_ledger": replay["total_check_operation_count_upper_ledger"],
            "after_hash": after_hash,
            "after_measure_CLV": after_measure_CLV,
            "changed": changed,
        },
        "R34_affine_after_R33_replay": affine,
        "one_diagnostic_R35B_pass_after_R33_replay": diagnostic_rup,
    }


def run_forensics() -> dict:
    frozen = reconstruct_frozen_stall()
    residual = frozen["residual"]
    structure = r35.structure_intake(residual)
    probe = existing_portfolio_composition_probe(residual)

    if probe["R33_replay"]["terminal"] != "STALLED_STACK_LEAN_CORE":
        verdict = "R37_FIRST_FRESH_RUP_STALL_FROZEN__R33_REPLAY_REACHES_EXISTING_TERMINAL"
    elif probe["R33_replay"]["changed"]:
        verdict = "R37_FIRST_FRESH_RUP_STALL_FROZEN__EXISTING_R33_RULE_REACTIVATED"
    else:
        verdict = "R37_FIRST_FRESH_RUP_STALL_FROZEN__NO_EXISTING_RULE_REACTIVATED"

    return {
        "schema": "JANUS_TRUMP_R37_FIRST_FRESH_RUP_STALL_FORENSICS_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "frozen_selector": {"seed": SEED, "n": N, "ratio": RATIO, "selection": "FIRST_STALL_IN_R36_PREREGISTERED_ORDER"},
        "R36_provenance": {
            "world_verdict": "OPEN_UNSEEN_RUP_STALL__TRUTH_SAT_DIAGNOSTIC_ONLY",
            "independent_truth": "SAT_DIAGNOSTIC_ONLY__NOT_USED_BY_FORENSICS",
            "expected_RUP_strengthenings": EXPECTED_RUP_STRENGTHENINGS,
            "expected_RUP_final_measure_LCV": EXPECTED_RUP_FINAL_MEASURE_LCV,
            "expected_RUP_final_formula_sha256": EXPECTED_RUP_FINAL_HASH,
        },
        "reconstruction": {
            "source_measure_CLV": list(r33.measure(frozen["source"])),
            "source_hash": frozen["source_hash"],
            "R33_first_terminal": frozen["R33_first"]["terminal"],
            "R33_first_rule_applications": frozen["R33_first"]["total_rule_applications"],
            "pre_RUP_core_measure_CLV": list(r33.measure(frozen["pre_RUP_core"])),
            "pre_RUP_core_hash": frozen["pre_RUP_core_hash"],
            "RUP_status": frozen["RUP"]["status"],
            "RUP_strengthenings": frozen["RUP"]["successful_strengthenings"],
            "RUP_checker_pass": frozen["RUP_checker"]["pass"],
            "RUP_residual_measure_LCV": frozen["RUP"]["final_measure"],
            "RUP_residual_measure_CLV": list(r33.measure(residual)),
            "RUP_residual_hash": frozen["residual_hash"],
            "RUP_residual_clauses": [list(c) for c in residual],
        },
        "structure_intake": structure,
        "existing_portfolio_composition_probe": probe,
        "candidate_firewall": {
            "new_reduction_rule_added": False,
            "new_terminal_solver_added": False,
            "external_SAT_solver_used": False,
            "assignment_enumeration_used": False,
            "known_SAT_truth_used_to_choose_transform": False,
            "R33_R34_R35B_bytes_modified": False,
            "portfolio_cycle_iterated": False,
        },
        "captain_verdict": {
            "law": "BEFORE INVENTING A NEW TOOL, CHECK WHETHER THE LAST TOOL REACTIVATED AN OLD CERTIFIED TOOL.",
            "next_if_R33_reactivated": "R37B_FIXED_CERTIFIED_PORTFOLIO_RESTART_CYCLE",
            "next_if_not_reactivated": "TOPA_CAPTAIN_SINGLE_NEW_SAT_SIDE_MECHANISM_SELECTION_ON_SEALED_RESIDUAL",
        },
        "R31_obligation_impact": {"obligations_closed": 0},
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_forensics()
    assert d["reconstruction"]["RUP_residual_hash"] == EXPECTED_RUP_FINAL_HASH
    assert d["reconstruction"]["RUP_strengthenings"] == EXPECTED_RUP_STRENGTHENINGS
    assert d["reconstruction"]["RUP_checker_pass"] is True
    assert not any(d["candidate_firewall"].values())
    print("R37_SELF_TEST_PASS", d["verdict"], d["existing_portfolio_composition_probe"]["R33_replay"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_forensics(), indent=2, sort_keys=True) + "\n"
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
