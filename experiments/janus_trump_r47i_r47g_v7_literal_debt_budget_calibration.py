from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r45b_frozen_26_stall_quotient_macro_coverage as r45b

SEED = 473383
N = 30
RATIO = 3.8
PIVOT = 7
FIXPOINT_HASH = "3130377ee52a6d6abf01f44fdc5f1a96cf83d701e30f70debea26cd347b7a495"
FIXPOINT_CLV = [87, 233, 25]
FORCED_DP_CLV = [87, 238, 24]
FINAL_CLV = [87, 233, 24]


def run() -> dict:
    original = r33.deterministic_random_3cnf(SEED, n=N, ratio=RATIO)
    label = f"R47I_R47G_ONSET_SEED_{SEED}_N{N}_R{RATIO}"
    _, fixpoint = r45b.replay_r42_terminal_formula(original, label)
    fixpoint = r33.canonical_formula(fixpoint)
    if r42.formula_hash(fixpoint) != FIXPOINT_HASH:
        raise AssertionError(("R47I_FIXPOINT_HASH_DRIFT", r42.formula_hash(fixpoint)))
    if list(r33.measure(fixpoint)) != FIXPOINT_CLV:
        raise AssertionError(("R47I_FIXPOINT_CLV_DRIFT", list(r33.measure(fixpoint))))

    candidate = r45a.macro_candidate_for_var(fixpoint, PIVOT)
    if candidate is None:
        raise AssertionError("R47I_V7_NO_LONGER_BIPOLAR")
    macro_replay = r45a.independent_macro_replay(fixpoint, candidate)
    dp = candidate["DP"]
    forced_clv = list(dp["measure_after_forced_DP"])
    norm = candidate["normalization"]
    post_r33_clv = list(norm["R33_result"]["final_measure"])
    final_clv = list(candidate["final_CLV"])
    rup = norm["RUP_record"]
    if rup is None:
        rup_status = None
        s = 0
        rup_replay = {"pass": True, "reason": "RUP_NOT_INVOKED"}
    else:
        rup_status = rup["status"]
        s = int(rup["successful_strengthenings"])
        post_r33_formula = r33.canonical_formula(norm["R33_result"]["final_formula"])
        rup_replay = r35b.independent_certificate_replay(post_r33_formula, rup)

    input_clv = list(candidate["input_CLV"])
    d_l = forced_clv[1] - input_clv[1]
    q = forced_clv[1] - post_r33_clv[1]
    actual_r_l = forced_clv[1] - final_clv[1]
    budget = q + s
    result = {
        "schema": "JANUS_TRUMP_R47I_R47G_V7_LITERAL_DEBT_BUDGET_CALIBRATION_RESULT",
        "version": "1.0",
        "date": "2026-09-03",
        "gate": "JANUS_TRUMP_R47I_R47G_V7_LITERAL_DEBT_BUDGET_CALIBRATION",
        "witness": {
            "seed": SEED,
            "n": N,
            "ratio": RATIO,
            "fixpoint_hash": r42.formula_hash(fixpoint),
            "pivot": PIVOT,
        },
        "input_CLV": input_clv,
        "forced_DP_CLV": forced_clv,
        "post_R33_CLV": post_r33_clv,
        "final_CLV": final_clv,
        "literal_debt_d": d_l,
        "R33_literal_repayment_q": q,
        "RUP_status": rup_status,
        "RUP_successful_strengthenings_s": s,
        "certificate_visible_budget_q_plus_s": budget,
        "actual_total_literal_repayment_rL": actual_r_l,
        "budget_closes_debt": budget >= d_l,
        "RUP_independent_replay_pass": bool(rup_replay["pass"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay"]["pass"]),
        "macro_independent_replay_pass": bool(macro_replay["pass"]),
        "accepted": bool(candidate["accepted"]),
        "terminal": norm["terminal"],
        "strict_descent_only_by_variable_tiebreak": final_clv[:2] == input_clv[:2] and final_clv[2] < input_clv[2],
        "RUP_history": rup["history"] if rup is not None else [],
        "verdict": None,
        "firewall": {
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    passed = (
        input_clv == FIXPOINT_CLV
        and forced_clv == FORCED_DP_CLV
        and final_clv == FINAL_CLV
        and d_l == 5
        and budget >= 5
        and result["RUP_independent_replay_pass"]
        and result["DP_independent_replay_pass"]
        and result["macro_independent_replay_pass"]
        and result["accepted"]
        and result["terminal"] is None
        and result["strict_descent_only_by_variable_tiebreak"]
    )
    result["verdict"] = "R47G_V7_LITERAL_DEBT_BUDGET_CALIBRATED__O4_OPEN" if passed else "R47I_CALIBRATION_INTEGRITY_FAILURE"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    compact = {k: v for k, v in result.items() if k != "RUP_history"}
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    main()
