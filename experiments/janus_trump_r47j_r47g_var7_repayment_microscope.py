from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f

SEED = 473383
N = 30
RATIO = 3.8
PIVOT = 7
FIXPOINT_HASH = "3130377ee52a6d6abf01f44fdc5f1a96cf83d701e30f70debea26cd347b7a495"


def clv(formula):
    return tuple(int(x) for x in r33.measure(r33.canonical_formula(formula)))


def delta(a, b):
    return [int(a[i] - b[i]) for i in range(3)]


def run() -> dict:
    original = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    reached = r47f.reachable_fixpoint(original)
    if reached is None:
        raise AssertionError("R47J_PARENT_NO_LONGER_REACHES_FIXPOINT")
    F_formula = r33.canonical_formula(reached["formula"])
    if r42.formula_hash(F_formula) != FIXPOINT_HASH:
        raise AssertionError(("R47J_FIXPOINT_HASH_DRIFT", r42.formula_hash(F_formula), FIXPOINT_HASH))

    candidate = r45a.macro_candidate_for_var(F_formula, PIVOT)
    if candidate is None or not candidate["accepted"]:
        raise AssertionError(("R47J_VAR7_NO_LONGER_ACCEPTED", candidate))
    replay = r45a.independent_macro_replay(F_formula, candidate)
    if not replay["pass"]:
        raise AssertionError(("R47J_MACRO_REPLAY_FAIL", replay))

    F = clv(F_formula)
    D = tuple(int(x) for x in candidate["DP"]["measure_after_forced_DP"])
    r33_result = candidate["normalization"]["R33_result"]
    P_formula = r33.canonical_formula(r33_result["final_formula"])
    P = clv(P_formula)
    G_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
    G = clv(G_formula)
    affine = r34.recognize_complete_affine_cnf(P_formula)
    rup = candidate["normalization"].get("RUP_record")

    if list(F) != [87, 233, 25] or list(D) != [87, 238, 24] or list(G) != [87, 233, 24]:
        raise AssertionError(("R47J_BOUNDARY_DRIFT", F, D, G))

    r33_clause_repayment = D[0] - P[0]
    r33_literal_repayment = D[1] - P[1]
    post_r33_clause_repayment = P[0] - G[0]
    post_r33_literal_repayment = P[1] - G[1]

    if candidate["normalization"]["terminal"] is not None:
        repayment_owner = "TERMINAL_ESCAPE"
    elif r33_literal_repayment > 0 and post_r33_literal_repayment > 0:
        repayment_owner = "R33_AND_POST_R33_COMPOSITION"
    elif r33_literal_repayment > 0:
        repayment_owner = "R33_ONLY"
    elif post_r33_literal_repayment > 0:
        repayment_owner = "RUP_OR_POST_R33_ONLY"
    else:
        repayment_owner = "NO_LITERAL_REPAYMENT_DETECTED"

    result = {
        "schema": "JANUS_TRUMP_R47J_R47G_VAR7_REPAYMENT_MICROSCOPE_RESULT",
        "version": "1.0",
        "date": "2026-09-03",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL_UNCOMMITTED"),
        "gate": "JANUS_TRUMP_R47J_R47G_VAR7_REPAYMENT_MICROSCOPE",
        "parent": {
            "seed": SEED,
            "n": N,
            "ratio": RATIO,
            "fixpoint_hash": r42.formula_hash(F_formula),
            "pivot": PIVOT,
        },
        "F_CLV": list(F),
        "D_after_exact_DP_CLV": list(D),
        "post_R33_CLV": list(P),
        "final_CLV": list(G),
        "DP_overage_vs_F": delta(D, F),
        "R33_repayment_D_to_P": [r33_clause_repayment, r33_literal_repayment, D[2] - P[2]],
        "post_R33_repayment_P_to_G": [post_r33_clause_repayment, post_r33_literal_repayment, P[2] - G[2]],
        "total_repayment_D_to_G": delta(D, G),
        "repayment_owner": repayment_owner,
        "R33": {
            "terminal": r33_result["terminal"],
            "rule_counts": r33_result["rule_counts"],
            "total_rule_applications": int(r33_result["total_rule_applications"]),
            "history": r33_result["history"],
            "strict_progress": bool(r33_result["strict_progress"]),
        },
        "affine": {
            "recognized": bool(affine["recognized"]),
            "reason": affine.get("reason"),
        },
        "RUP": None if rup is None else {
            "status": rup["status"],
            "successful_strengthenings": int(rup["successful_strengthenings"]),
            "history": rup.get("history", []),
            "ledger": rup.get("ledger", {}),
        },
        "candidate": {
            "terminal": candidate["normalization"]["terminal"],
            "accepted": bool(candidate["accepted"]),
            "temporary_internal_ascent": bool(candidate["temporary_internal_ascent"]),
            "net_CLV_descent": bool(candidate["net_CLV_descent"]),
            "DP_independent_replay_pass": bool(candidate["DP_independent_replay"]["pass"]),
            "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope"]["pass"]),
            "independent_macro_replay_pass": bool(replay["pass"]),
        },
        "interpretation": {
            "single_witness_only": True,
            "next_use": "Generalize the observed repayment-producing rule pattern into a sufficient condition, or adversarially suppress that pattern while preserving reachability.",
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    return result


def self_test():
    assert delta((10, 35, 7), (10, 30, 8)) == [0, 5, -1]
    print("R47J_SELF_TEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact = {
        "gate": result["gate"],
        "F_CLV": result["F_CLV"],
        "D_after_exact_DP_CLV": result["D_after_exact_DP_CLV"],
        "post_R33_CLV": result["post_R33_CLV"],
        "final_CLV": result["final_CLV"],
        "R33_repayment_D_to_P": result["R33_repayment_D_to_P"],
        "post_R33_repayment_P_to_G": result["post_R33_repayment_P_to_G"],
        "repayment_owner": result["repayment_owner"],
        "R33_rule_counts": result["R33"]["rule_counts"],
        "RUP_status": None if result["RUP"] is None else result["RUP"]["status"],
        "RUP_successful_strengthenings": None if result["RUP"] is None else result["RUP"]["successful_strengthenings"],
        "firewall": result["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
