from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35_nonaffine_core_freeze_structure_intake as r35
import janus_trump_r35b_single_literal_rup_vivification as r35b

Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]

FROZEN_SEEDS = (36001, 36002, 36003, 36004, 36005, 36006, 36007, 36008)
FROZEN_N = 28
FROZEN_RATIO = 4.2


def candidate_world(seed: int) -> dict:
    started = time.perf_counter()
    source = r33.deterministic_random_3cnf(seed, n=FROZEN_N, ratio=FROZEN_RATIO)
    source_hash = r35.canonical_json_sha256([list(c) for c in source])

    r33_result = r33.simplify(source)
    core = r33.canonical_formula(r33_result["final_formula"])
    core_hash = r35.canonical_json_sha256([list(c) for c in core])

    base = {
        "seed": seed,
        "source_measure_CLV": list(r33.measure(source)),
        "source_hash": source_hash,
        "R33_terminal": r33_result["terminal"],
        "R33_final_measure_CLV": r33_result["final_measure"],
        "R33_rule_applications": r33_result["total_rule_applications"],
        "R33_rule_counts": r33_result["rule_counts"],
        "R33_check_operation_upper_ledger": r33_result["total_check_operation_count_upper_ledger"],
        "R33_certificate_bytes": r33_result["total_certificate_bytes"],
        "core_hash": core_hash,
        "core_formula": [list(c) for c in core],
    }

    if r33_result["terminal"] != "STALLED_STACK_LEAN_CORE":
        return {
            **base,
            "candidate_stage": "PRE_RUP_TERMINAL",
            "candidate_status": r33_result["terminal"],
            "candidate_semantic_claim": None,
            "candidate_elapsed_seconds": time.perf_counter() - started,
        }

    recognition = r34.recognize_complete_affine_cnf(core)
    if recognition["recognized"]:
        solution = r34.solve_gf2_with_certificate(recognition["equations"])
        certificate = r34.verify_affine_certificate(core, recognition, solution)
        return {
            **base,
            "candidate_stage": "AFFINE_TERMINAL",
            "candidate_status": "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT",
            "candidate_semantic_claim": bool(solution["sat"]),
            "affine": {
                "recognized": True,
                "equation_count": recognition["equation_count"],
                "literal_inspections": recognition["literal_inspections"],
                "row_xors": solution["row_xors"],
                "row_swaps": solution["row_swaps"],
                "estimated_bit_ops": solution["estimated_bit_ops"],
                "certificate": certificate,
            },
            "candidate_elapsed_seconds": time.perf_counter() - started,
        }

    rup = r35b.run_candidate(core)
    rup_checker = r35b.independent_certificate_replay(core, rup)
    return {
        **base,
        "candidate_stage": "RUP",
        "candidate_status": rup["status"],
        "candidate_semantic_claim": False if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION" else None,
        "affine_rejection_reason": recognition["reason"],
        "affine_failed_vars": recognition.get("failed_vars"),
        "RUP": {
            "initial_measure_LCV": rup["initial_measure"],
            "final_measure_LCV": rup["final_measure"],
            "successful_strengthenings": rup["successful_strengthenings"],
            "ledger": rup["ledger"],
            "certificate_history_bytes": len(json.dumps(rup["history"], sort_keys=True, separators=(",", ":")).encode("utf-8")),
            "independent_certificate_checker": rup_checker,
            "final_formula_hash": rup_checker.get("final_formula_hash"),
            "final_up_conflict": rup["final_up_receipt"]["conflict"],
            "final_up_conflict_kind": rup["final_up_receipt"].get("conflict_kind"),
        },
        "candidate_elapsed_seconds": time.perf_counter() - started,
    }


def post_candidate_minisat22_verify(source_formula: Formula) -> dict:
    # Imported here by design: this verifier is unavailable to candidate_world.
    from pysat.solvers import Minisat22

    clauses = [list(c) for c in source_formula]
    with Minisat22(bootstrap_with=clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    assignment = None
    model_rechecks = None
    if sat and model is not None:
        chosen = {abs(l): l > 0 for l in model if abs(l) <= FROZEN_N}
        assignment = {str(v): bool(chosen.get(v, False)) for v in range(1, FROZEN_N + 1)}
        model_rechecks = r33.eval_formula(source_formula, {int(v): b for v, b in assignment.items()})
    return {
        "solver": "PySAT_Minisat22",
        "sat": bool(sat),
        "model_rechecks_original_CNF": model_rechecks,
        "assignment": assignment,
    }


def classify_world(candidate: dict, verifier: dict) -> dict:
    stage = candidate["candidate_stage"]
    claim = candidate["candidate_semantic_claim"]
    truth = verifier["sat"]

    if stage == "AFFINE_TERMINAL":
        cert_ok = candidate["affine"]["certificate"]["pass"]
        if not cert_ok or claim != truth:
            verdict = "FAIL_SEMANTIC_MISMATCH"
        else:
            verdict = "PASS_AFFINE_TERMINAL__NOT_RUP_EVIDENCE"
    elif stage == "RUP":
        checker_ok = candidate["RUP"]["independent_certificate_checker"]["pass"]
        if not checker_ok:
            verdict = "FAIL_INTEGRITY"
        elif candidate["candidate_status"] == "UNSAT_BY_UNIT_PROPAGATION":
            verdict = "PASS_EXACT_UNSEEN_RUP_UNSAT" if truth is False else "FAIL_SEMANTIC_MISMATCH"
        else:
            verdict = "OPEN_UNSEEN_RUP_STALL__TRUTH_SAT_DIAGNOSTIC_ONLY" if truth else "OPEN_UNSEEN_RUP_STALL__TRUTH_UNSAT_DIAGNOSTIC_ONLY"
    else:
        verdict = "PASS_PRE_RUP_TERMINAL__NOT_RUP_EVIDENCE"

    return {
        "seed": candidate["seed"],
        "verdict": verdict,
        "candidate_stage": stage,
        "candidate_status": candidate["candidate_status"],
        "candidate_semantic_claim": claim,
        "independent_truth_sat": truth,
        "candidate": candidate,
        "post_candidate_verifier": verifier,
    }


def run_holdout() -> dict:
    # All candidate executions finish before any independent exact truth is opened.
    candidate_results: List[dict] = [candidate_world(seed) for seed in FROZEN_SEEDS]

    verified_worlds = []
    for candidate in candidate_results:
        source = r33.deterministic_random_3cnf(candidate["seed"], n=FROZEN_N, ratio=FROZEN_RATIO)
        source_hash = r35.canonical_json_sha256([list(c) for c in source])
        if source_hash != candidate["source_hash"]:
            raise AssertionError("source regeneration drift")
        verifier = post_candidate_minisat22_verify(source)
        verified_worlds.append(classify_world(candidate, verifier))

    verdicts = [w["verdict"] for w in verified_worlds]
    failures = [v for v in verdicts if v.startswith("FAIL_")]
    eligible = [w for w in verified_worlds if w["candidate_stage"] == "RUP"]
    rup_success = [w for w in eligible if w["verdict"] == "PASS_EXACT_UNSEEN_RUP_UNSAT"]
    rup_stalls = [w for w in eligible if w["verdict"].startswith("OPEN_UNSEEN_RUP_STALL")]

    if failures:
        aggregate = "R36_FAIL_INTEGRITY_OR_SEMANTIC_MISMATCH"
    elif not eligible:
        aggregate = "R36_NO_ELIGIBLE_NONAFFINE_RUP_WORLDS__INCONCLUSIVE"
    elif rup_stalls:
        aggregate = "R36_FRESH_UNSEEN_RUP_SURVIVAL_WITH_OPEN_STALLS"
    else:
        aggregate = "R36_FRESH_UNSEEN_RUP_EXACT_ON_ALL_ELIGIBLE_NONAFFINE_WORLDS__NO_UNIVERSAL_CLAIM"

    counts: Dict[str, int] = {}
    for v in verdicts:
        counts[v] = counts.get(v, 0) + 1

    return {
        "schema": "JANUS_TRUMP_R36_FRESH_NONAFFINE_RUP_VIVIFICATION_HOLDOUT_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "aggregate_verdict": aggregate,
        "frozen_holdout": {
            "seeds": list(FROZEN_SEEDS),
            "n": FROZEN_N,
            "ratio": FROZEN_RATIO,
            "world_count": len(FROZEN_SEEDS),
            "selected_after_R35B_seal": True,
            "replacement_or_filtering": False,
        },
        "candidate_firewall": {
            "R33_modified": False,
            "R34_modified": False,
            "R35B_modified": False,
            "external_solver_inside_candidate": False,
            "truth_opened_before_all_candidates_terminal": False,
            "new_mechanism_added": False,
            "world_replacement_after_observation": False,
        },
        "counts": {
            "world_verdicts": counts,
            "eligible_nonaffine_RUP_worlds": len(eligible),
            "RUP_exact_UNSAT_successes": len(rup_success),
            "RUP_open_stalls": len(rup_stalls),
            "pre_RUP_terminals": sum(w["candidate_stage"] == "PRE_RUP_TERMINAL" for w in verified_worlds),
            "affine_terminals": sum(w["candidate_stage"] == "AFFINE_TERMINAL" for w in verified_worlds),
            "semantic_or_integrity_failures": len(failures),
        },
        "worlds": verified_worlds,
        "captain_verdict": {
            "law": "A discovered deletion rule earns generalization evidence only on worlds selected after the freeze. Earlier portfolio terminals are not credited to RUP; stalls remain OPEN.",
            "RUP_survived_without_semantic_mismatch": not failures and bool(eligible),
        },
        "R31_obligation_impact": {
            "obligations_closed": 0,
            "reason": "Finite prospective holdout evidence cannot prove that a RUP strengthening exists on every nonterminal 3-CNF.",
        },
        "next_gate": {
            "if_stalls": "R37_FRESH_RUP_STALL_FORENSICS__FREEZE_FIRST_STALLED_RESIDUAL_BEFORE_ANY_NEW_RULE",
            "if_all_eligible_exact": "NEW_PREREGISTERED_SIZE_LADDER_AND_ADVERSARIAL_FAMILIES",
        },
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    # No frozen R36 world is generated here. Test only routing/classification helpers.
    fake_stall = {
        "seed": -1,
        "candidate_stage": "RUP",
        "candidate_status": "STALLED_RUP_CORE",
        "candidate_semantic_claim": None,
        "RUP": {"independent_certificate_checker": {"pass": True}},
    }
    assert classify_world(fake_stall, {"sat": True})["verdict"] == "OPEN_UNSEEN_RUP_STALL__TRUTH_SAT_DIAGNOSTIC_ONLY"
    fake_unsat = {
        "seed": -2,
        "candidate_stage": "RUP",
        "candidate_status": "UNSAT_BY_UNIT_PROPAGATION",
        "candidate_semantic_claim": False,
        "RUP": {"independent_certificate_checker": {"pass": True}},
    }
    assert classify_world(fake_unsat, {"sat": False})["verdict"] == "PASS_EXACT_UNSEEN_RUP_UNSAT"
    assert classify_world(fake_unsat, {"sat": True})["verdict"] == "FAIL_SEMANTIC_MISMATCH"
    print("R36_SELF_TEST_PASS__NO_HOLDOUT_WORLDS_GENERATED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_holdout(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
