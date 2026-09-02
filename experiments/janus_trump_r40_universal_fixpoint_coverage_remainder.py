from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

R37B = Path("research/JANUS_TRUMP_R37B_FIXED_CERTIFIED_PORTFOLIO_RESTART_CYCLE_RESULT_SUMMARY_2026-09-02.json")
R38 = Path("research/JANUS_TRUMP_R38_PORTFOLIO_FIXPOINT_FREEZE_STRUCTURE_INTAKE_RESULT_SUMMARY_2026-09-02.json")
R39 = Path("research/JANUS_TRUMP_R39_EXACT_QHORN_RECOGNITION_RESULT_SUMMARY_2026-09-02.json")

EXPECTED_HASH = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
EXPECTED_CLV = [45, 105, 13]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_r40() -> dict:
    a, b, c = load(R37B), load(R38), load(R39)

    lineage_checks = {
        "R37B_sealed": a["status"] == "SEALED_FROM_SUCCESSFUL_GITHUB_ACTIONS_RUN",
        "R37B_controller_polynomial_termination": a["global_progress"]["polynomial_termination_of_this_controller"] is True,
        "R37B_halts_at_nonsemantic_stall": a["verdict"] == "R37B_FIXED_RESTART_CYCLE_STALLS_AT_PORTFOLIO_FIXPOINT__NO_SEMANTIC_VERDICT",
        "R37B_decision_completeness_not_proved": a["global_progress"]["decision_completeness_proved"] is False,
        "R37B_fixpoint_hash_match": a["terminal_fixpoint"]["canonical_formula_sha256"] == EXPECTED_HASH,
        "R37B_fixpoint_measure_match": a["terminal_fixpoint"]["measure_CLV"] == EXPECTED_CLV,
        "R38_same_fixpoint": b["fixpoint"]["canonical_formula_sha256"] == EXPECTED_HASH,
        "R38_no_audited_standard_terminal": b["verdict"] == "R38_FIXPOINT_FROZEN__NO_AUDITED_STANDARD_TERMINAL_RECOGNIZED",
        "R39_same_fixpoint": c["frozen_fixpoint"]["canonical_formula_sha256"] == EXPECTED_HASH,
        "R39_exact_qhorn_rejected": c["verdict"] == "R39_QHORN_REJECTED_LOCAL_EXACT__RETURN_TO_UNIVERSAL_COVERAGE",
        "R39_replay_pass": c["q_Horn"]["independent_replay_pass"] is True,
    }
    valid = all(lineage_checks.values())

    if valid:
        verdict = "R40_CURRENT_FIXED_CONTROLLER_UNIVERSAL_COVERAGE_REFUTED_BY_REACHABLE_STALLED_FIXPOINT"
        refuted = True
    else:
        verdict = "R40_COVERAGE_WITNESS_INVALID_OR_LINEAGE_DRIFT"
        refuted = False

    return {
        "schema": "JANUS_TRUMP_R40_UNIVERSAL_FIXPOINT_COVERAGE_AND_REMAINDER_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "coverage_statement_under_test": "FOR_ALL admissible 3CNF phi: the fixed R37B controller returns a semantic SAT/UNSAT verdict",
        "refutation_rule": "ONE reachable input on which the fixed controller halts without semantic decision refutes that universal coverage statement",
        "sealed_witness": {
            "seed": 36001,
            "n": 28,
            "ratio": 4.2,
            "reachable_under_fixed_R37B_controller": valid,
            "terminal_measure_CLV": EXPECTED_CLV,
            "terminal_formula_sha256": EXPECTED_HASH,
            "controller_stop": a["cycles"][-1]["stop"],
            "semantic_verdict": None,
            "polynomial_termination_of_this_controller": a["global_progress"]["polynomial_termination_of_this_controller"],
            "decision_completeness": False,
        },
        "lineage_checks": lineage_checks,
        "current_controller_universal_decision_coverage_refuted": refuted,
        "post_hoc_observations": {
            "R38_standard_terminal_recognition": "NONE",
            "R39_qHorn_recognized": False,
            "authority": "OBSERVATIONAL_ONLY__DOES_NOT_RETROACTIVELY_CHANGE_R37B_CONTROLLER",
        },
        "captain_verdict": {
            "law": "STOP EXPLAINING ONE STALL. PROVE WHY THE NEXT FIXED MACHINE CANNOT STALL.",
            "required_successor_property": "FOR_EACH reachable nonterminal S: DECIDE(S) OR certified strict descent under one frozen input-independent successor grammar",
            "next_gate": "R41_SUCCESSOR_CONTROLLER_DECIDE_OR_DESCEND_GRAMMAR_PREREGISTRATION",
        },
        "proof_ladder": {
            "highest_verified_level": "L1_LOCAL_FINITE_INSTANCE_EXACTNESS_ONLY",
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "scientific_interpretation": {
            "confirmed": "The current fixed R37B controller is not universally decision-complete because a sealed reachable 3-CNF execution halts at a nonsemantic portfolio fixpoint.",
            "not_claimed": "This does not refute every possible successor controller and does not prove P != NP.",
            "design_consequence": "No new operator or terminal family may be promoted merely because it repairs this witness; a successor must carry an explicit decide-or-descend coverage obligation.",
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    d = run_r40()
    assert all(d["lineage_checks"].values())
    assert d["current_controller_universal_decision_coverage_refuted"] is True
    assert d["verdict"] == "R40_CURRENT_FIXED_CONTROLLER_UNIVERSAL_COVERAGE_REFUTED_BY_REACHABLE_STALLED_FIXPOINT"
    assert d["proof_ladder"]["L2_UNIVERSAL_3CNF_COVERAGE"] is False
    assert d["P_VS_NP"] == "OPEN"
    print("R40_SELF_TEST_PASS", d["verdict"])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_r40(), indent=2, sort_keys=True) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
