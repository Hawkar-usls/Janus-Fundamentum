#!/usr/bin/env python3
"""TOPA closure audit for the current TRUMP algorithm lineage.

This is an adversarial theorem-readiness audit, not a theorem prover. It inspects
frozen TRUMP source/prereg/result artifacts for explicit blockers to a valid
P-vs-NP closure claim. A blocker is sufficient to keep P_VS_NP=OPEN.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DIRECT = ROOT / "experiments/janus_trump_p_vs_np_direct_challenge_r0.py"
R3 = ROOT / "experiments/janus_trump_osiris_r3_natural_residuals.py"
R3B = ROOT / "experiments/janus_trump_osiris_r3b_proof_carrying_recovery.py"
R4 = ROOT / "experiments/janus_trump_osiris_r4_roi_gate.py"
R5 = ROOT / "experiments/janus_trump_osiris_r5_fehlerbild_positive_roi_discovery.py"
R5_PRE = ROOT / "research/JANUS_TRUMP_OSIRIS_R5_FEHLERBILD_POSITIVE_ROI_DISCOVERY_PREREGISTRATION_2026-09-01.json"
R5_RES = ROOT / "research/JANUS_TRUMP_OSIRIS_R5_FEHLERBILD_POSITIVE_ROI_DISCOVERY_RESULT_SUMMARY_2026-09-01.json"
PRE = ROOT / "research/JANUS_TRUMP_TOPA_P_VS_NP_CLOSURE_AUDIT_PREREGISTRATION_2026-09-01.json"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def j(path: Path) -> dict:
    return json.loads(text(path))


def contains(path: Path, needle: str) -> bool:
    return needle in text(path)


def audit() -> dict:
    prereg = j(PRE)
    direct = text(DIRECT)
    r3 = text(R3)
    r3b = text(R3B)
    r4 = text(R4)
    r5 = text(R5)
    r5_pre = j(R5_PRE)
    r5_res = j(R5_RES)

    # Evidence facts are source-level and frozen-result observations.
    evidence = {
        "r5_bounded_discovery_arena": r5_pre["frozen_arena"]["max_variables_for_exact_discovery"] == 14,
        "r5_discovery_not_validation": r5_pre["discovery_not_validation"]["promotion_allowed"] is False,
        "r5_zero_positive_roi": r5_res["results"]["positive_roi_rows"] == 0,
        "r5_aggregate_spiral_more_expensive": r5_res["results"]["spiral_total_ops_sum"] > r5_res["results"]["exact_total_ops_sum"],
        "r5_uses_exact_search_witness": "exact_search_witness" in r5,
        "r5_uses_dpll_verifier": "dpll(" in r5,
        "r5_has_exhaustive_separator_assignment_loop": "product((False, True), repeat=len(sep_order))" in r5,
        "r5_has_legacy_exact_fallback": "PROOF_CARRYING_EXACT_FALLBACK" in r5_pre["frozen_spiral_policy"]["priority"],
        "r3_exact_search_is_binary_recursive": "for val in (False, True):" in r3 and "hit = rec(i + 1, a)" in r3,
        "r3_dpll_dependency": "from janus_trump_p_vs_np_direct_challenge_r0 import canon, corpus, dpll" in r3,
        "r4_conservative_abstention": "ABSTAIN_TO_EXACT" in r4,
        "direct_challenge_explicitly_keeps_open": '"P_VS_NP":"OPEN"' in direct or '"P_VS_NP": "OPEN"' in direct,
    }

    theorem_flag_names = [
        "complete_arbitrary_cnf_algorithm",
        "correctness_proof_every_input",
        "polynomial_transition_bound",
        "polynomial_representation_bound_every_step",
        "polynomial_discovery_bound",
        "polynomial_translation_update_bound",
        "polynomial_independent_verification_bound",
        "no_hidden_oracle_or_advice",
        "polynomial_deferred_debt_bound",
    ]
    direct_flags = {}
    for name in theorem_flag_names:
        if f'"{name}": False' in direct:
            direct_flags[name] = False
        elif f'"{name}": True' in direct:
            direct_flags[name] = True
        else:
            direct_flags[name] = None

    obligations = {
        "ARBITRARY_CNF_SCOPE": not evidence["r5_bounded_discovery_arena"] and direct_flags.get("complete_arbitrary_cnf_algorithm") is True,
        "TOTAL_CORRECTNESS_EVERY_INPUT": direct_flags.get("correctness_proof_every_input") is True,
        "POLYNOMIAL_TRANSITION_BOUND": direct_flags.get("polynomial_transition_bound") is True,
        "POLYNOMIAL_REPRESENTATION_BOUND_EVERY_STEP": direct_flags.get("polynomial_representation_bound_every_step") is True,
        "POLYNOMIAL_ROUTE_DISCOVERY_BOUND": direct_flags.get("polynomial_discovery_bound") is True,
        "POLYNOMIAL_TRANSLATION_UPDATE_BOUND": direct_flags.get("polynomial_translation_update_bound") is True,
        "POLYNOMIAL_END_TO_END_VERIFICATION_OR_PROOF_CHECKING_BOUND": direct_flags.get("polynomial_independent_verification_bound") is True,
        "NO_EXPONENTIAL_FALLBACK": not (
            evidence["r5_uses_exact_search_witness"]
            or evidence["r5_uses_dpll_verifier"]
            or evidence["r5_has_exhaustive_separator_assignment_loop"]
            or evidence["r5_has_legacy_exact_fallback"]
            or evidence["r3_exact_search_is_binary_recursive"]
        ),
        "NO_HIDDEN_ORACLE_OR_ADVICE": direct_flags.get("no_hidden_oracle_or_advice") is True,
        "NO_DEFERRED_EXPONENTIAL_DEBT": direct_flags.get("polynomial_deferred_debt_bound") is True,
        "FORMAL_OR_MACHINE_CHECKABLE_GLOBAL_PROOF": False,
    }

    blockers = [name for name, ok in obligations.items() if not ok]
    closure_ready = len(blockers) == 0

    # Extra empirical information is not itself a theorem obligation, but it is
    # useful adversarial evidence about the present implementation.
    empirical = {
        "r5_rows": r5_res["results"]["rows"],
        "r5_families": r5_res["results"]["families"],
        "positive_roi_rows": r5_res["results"]["positive_roi_rows"],
        "exact_total_ops_sum": r5_res["results"]["exact_total_ops_sum"],
        "spiral_total_ops_sum": r5_res["results"]["spiral_total_ops_sum"],
        "aggregate_delta_w": r5_res["results"]["aggregate_delta_w"],
        "closest_observed_delta_w": r5_res["results"]["closest_observed_case"]["delta_w"],
    }

    return {
        "schema": "JANUS/TRUMP/TOPA/P_VS_NP_CLOSURE_AUDIT/RESULT/v1.0",
        "status": "FROZEN_AUDIT_RESULT",
        "audited_branch": prereg["audited_head"],
        "closure_ready": closure_ready,
        "P_VS_NP": "CLOSED" if closure_ready else "OPEN",
        "verdict": "TOPA_P_VS_NP_CLOSURE_READY" if closure_ready else "TOPA_P_VS_NP_CLOSURE_NOT_READY__BLOCKERS_LOCALIZED__OPEN",
        "mandatory_obligations": obligations,
        "blocking_obligations": blockers,
        "direct_challenge_theorem_flags": direct_flags,
        "source_evidence": evidence,
        "empirical_context": empirical,
        "highest_admissible_claim": (
            "The current TRUMP lineage contains useful exact, proof-carrying and structural-search mechanisms, but it does not presently establish a polynomial-time algorithm for arbitrary CNF SAT. Explicit exhaustive/exact fallbacks remain in the execution path, multiple global polynomial bounds are unproved, R5 is bounded discovery-only, and R5 found zero positive-ROI spiral cases. Therefore P vs NP remains OPEN."
        ),
        "next_closure_target": (
            "Replace or globally bound every exhaustive primitive and fallback, then prove end-to-end polynomial time and correctness for arbitrary CNF without finite caps; only after those obligations are machine-checkably discharged can a P=NP claim enter closure review."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    result = audit()
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "verdict": result["verdict"],
        "P_VS_NP": result["P_VS_NP"],
        "closure_ready": result["closure_ready"],
        "blocking_obligations": result["blocking_obligations"],
        "empirical_context": result["empirical_context"],
    }, indent=2))
    return 0 if not result["closure_ready"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
