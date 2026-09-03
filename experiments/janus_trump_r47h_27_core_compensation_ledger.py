from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r45b_frozen_26_stall_quotient_macro_coverage as r45b

Formula = Tuple[Tuple[int, ...], ...]

R47G_SEED = 473383
R47G_N = 30
R47G_RATIO = 3.8
R47G_FIXPOINT_HASH = "3130377ee52a6d6abf01f44fdc5f1a96cf83d701e30f70debea26cd347b7a495"
R47G_FIXPOINT_CLV = [87, 233, 25]
EXPECTED_CORE_COUNT = 27


def clv(formula: Formula) -> Tuple[int, int, int]:
    return r33.measure(r33.canonical_formula(formula))


def genuine_fixpoint_integrity(formula: Formula) -> dict:
    f = r33.canonical_formula(formula)
    reduced = r33.simplify(f)
    after_r33 = r33.canonical_formula(reduced["final_formula"])
    affine = r34.recognize_complete_affine_cnf(after_r33)
    rup = r35b.run_candidate(after_r33)
    rup_replay = r35b.independent_certificate_replay(after_r33, rup)
    after_rup = r33.canonical_formula(rup["final_formula"])
    bve, bve_ledger = r42.best_sa_bve_candidate(after_rup)
    fields = {
        "R33_terminal": reduced["terminal"],
        "R33_applications": int(reduced["total_rule_applications"]),
        "R33_unchanged": after_r33 == f,
        "affine_recognized": bool(affine["recognized"]),
        "RUP_status": rup["status"],
        "RUP_successful_strengthenings": int(rup["successful_strengthenings"]),
        "RUP_unchanged": after_rup == f,
        "RUP_independent_replay_pass": bool(rup_replay["pass"]),
        "BVE_candidate_present": bve is not None,
        "BVE_variables_checked": int(bve_ledger["variables_checked"]),
    }
    passed = (
        fields["R33_terminal"] == "STALLED_STACK_LEAN_CORE"
        and fields["R33_applications"] == 0
        and fields["R33_unchanged"]
        and not fields["affine_recognized"]
        and fields["RUP_status"] == "STALLED_RUP_CORE"
        and fields["RUP_successful_strengthenings"] == 0
        and fields["RUP_unchanged"]
        and fields["RUP_independent_replay_pass"]
        and not fields["BVE_candidate_present"]
    )
    return {"pass": passed, **fields}


def debt_class(input_clv: Tuple[int, int, int], forced_clv: Tuple[int, int, int]) -> str:
    if forced_clv[0] > input_clv[0]:
        return "CLAUSE_DEBT"
    if forced_clv[0] == input_clv[0] and forced_clv[1] > input_clv[1]:
        return "LITERAL_DEBT"
    return "INVALID_DEBT_PARTITION"


def acceptance_lane(candidate: dict, input_clv: Tuple[int, int, int], forced_clv: Tuple[int, int, int], final_clv: Tuple[int, int, int]) -> str:
    if candidate["normalization"]["terminal"] is not None:
        return "CERTIFIED_TERMINAL_ESCAPE"
    if not candidate["accepted"]:
        return "REJECTED_INSUFFICIENT_REPAYMENT"
    d_c = forced_clv[0] - input_clv[0]
    d_l = forced_clv[1] - input_clv[1]
    r_c = forced_clv[0] - final_clv[0]
    r_l = forced_clv[1] - final_clv[1]
    if r_c > d_c:
        return "CLAUSE_DEBT_OVERPAID"
    if r_c == d_c and r_l > d_l:
        return "CLAUSE_TIE_LITERAL_DEBT_OVERPAID"
    if r_c == d_c and r_l == d_l and final_clv[2] < input_clv[2]:
        return "EXACT_C_L_REPAYMENT_VARIABLE_TIEBREAK"
    return "INVALID_ACCEPTED_NONTERMINAL_LANE"


def pivot_receipt(formula: Formula, var: int) -> dict | None:
    f = r33.canonical_formula(formula)
    candidate = r45a.macro_candidate_for_var(f, int(var))
    if candidate is None:
        return None
    input_clv = tuple(int(x) for x in candidate["input_CLV"])
    forced_clv = tuple(int(x) for x in candidate["DP"]["measure_after_forced_DP"])
    post_r33_clv = tuple(int(x) for x in candidate["normalization"]["R33_result"]["final_measure"])
    final_clv = tuple(int(x) for x in candidate["final_CLV"])
    d_c = forced_clv[0] - input_clv[0]
    d_l = forced_clv[1] - input_clv[1]
    r_c = forced_clv[0] - final_clv[0]
    r_l = forced_clv[1] - final_clv[1]
    macro_replay = r45a.independent_macro_replay(f, candidate)
    lane = acceptance_lane(candidate, input_clv, forced_clv, final_clv)
    return {
        "pivot": int(var),
        "input_CLV": list(input_clv),
        "forced_DP_CLV": list(forced_clv),
        "debt_class": debt_class(input_clv, forced_clv),
        "dC": int(d_c),
        "dL": int(d_l),
        "post_R33_CLV": list(post_r33_clv),
        "final_CLV": list(final_clv),
        "rC": int(r_c),
        "rL": int(r_l),
        "terminal": candidate["normalization"]["terminal"],
        "accepted": bool(candidate["accepted"]),
        "acceptance_lane": lane,
        "temporary_internal_ascent": bool(candidate["temporary_internal_ascent"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay"]["pass"]),
        "macro_independent_replay_pass": bool(macro_replay["pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope"]["pass"]),
    }


def canonical_frozen_26() -> List[Tuple[str, int, Formula]]:
    case_map = r45b.frozen_case_map()
    out = []
    for seed in r45b.FROZEN_STALL_SEEDS:
        if int(seed) not in case_map:
            raise AssertionError(("R47H_FROZEN_SEED_MISSING", seed))
        label, original = case_map[int(seed)]
        _, state = r45b.replay_r42_terminal_formula(original, label)
        out.append((label, int(seed), state))
    if len(out) != 26:
        raise AssertionError(("R47H_FROZEN_26_COUNT_DRIFT", len(out)))
    return out


def r47g_onset_fixpoint() -> Tuple[str, int, Formula]:
    original = r33.deterministic_random_3cnf(R47G_SEED, n=R47G_N, ratio=R47G_RATIO)
    label = f"R47G_ONSET_SEED_{R47G_SEED}_N{R47G_N}_R{R47G_RATIO}"
    _, state = r45b.replay_r42_terminal_formula(original, label)
    if r42.formula_hash(state) != R47G_FIXPOINT_HASH:
        raise AssertionError(("R47H_R47G_FIXPOINT_HASH_DRIFT", r42.formula_hash(state), R47G_FIXPOINT_HASH))
    if list(clv(state)) != R47G_FIXPOINT_CLV:
        raise AssertionError(("R47H_R47G_FIXPOINT_CLV_DRIFT", list(clv(state)), R47G_FIXPOINT_CLV))
    return label, R47G_SEED, state


def analyze_core(label: str, seed: int, formula: Formula, source: str) -> dict:
    f = r33.canonical_formula(formula)
    integrity = genuine_fixpoint_integrity(f)
    if not integrity["pass"]:
        raise AssertionError(("R47H_GENUINE_FIXPOINT_INTEGRITY_FAIL", label, integrity))

    pivots = []
    first_accepted = None
    for var in r33.variables(f):
        receipt = pivot_receipt(f, int(var))
        if receipt is None:
            continue
        pivots.append(receipt)
        if first_accepted is None and receipt["accepted"]:
            first_accepted = receipt

    invalid_debt = [p["pivot"] for p in pivots if p["debt_class"] == "INVALID_DEBT_PARTITION"]
    invalid_lane = [p["pivot"] for p in pivots if p["acceptance_lane"] == "INVALID_ACCEPTED_NONTERMINAL_LANE"]
    replay_failures = [p["pivot"] for p in pivots if not (p["DP_independent_replay_pass"] and p["macro_independent_replay_pass"] and p["polynomial_intermediate_envelope_pass"])]
    return {
        "source": source,
        "label": label,
        "seed": int(seed),
        "fixpoint_hash": r42.formula_hash(f),
        "fixpoint_CLV": list(clv(f)),
        "genuine_fixpoint_integrity": integrity,
        "bipolar_pivot_count": len(pivots),
        "CLAUSE_DEBT_count": sum(p["debt_class"] == "CLAUSE_DEBT" for p in pivots),
        "LITERAL_DEBT_count": sum(p["debt_class"] == "LITERAL_DEBT" for p in pivots),
        "accepted_pivot_count": sum(bool(p["accepted"]) for p in pivots),
        "terminal_accepted_count": sum(p["accepted"] and p["terminal"] is not None for p in pivots),
        "nonterminal_accepted_count": sum(p["accepted"] and p["terminal"] is None for p in pivots),
        "first_accepted_pivot": first_accepted,
        "invalid_debt_pivots": invalid_debt,
        "invalid_acceptance_lane_pivots": invalid_lane,
        "replay_failure_pivots": replay_failures,
        "covered": first_accepted is not None,
        "pivot_receipts": pivots,
    }


def run_audit() -> dict:
    corpus = [(label, seed, f, "R45B_FROZEN_26") for label, seed, f in canonical_frozen_26()]
    onset_label, onset_seed, onset_formula = r47g_onset_fixpoint()
    corpus.append((onset_label, onset_seed, onset_formula, "R47G_ONSET_N30"))
    if len(corpus) != EXPECTED_CORE_COUNT:
        raise AssertionError(("R47H_CORPUS_COUNT_DRIFT", len(corpus)))

    rows = [analyze_core(label, seed, formula, source) for label, seed, formula, source in corpus]
    onset = next(r for r in rows if r["source"] == "R47G_ONSET_N30")
    onset_v7 = next((p for p in onset["pivot_receipts"] if p["pivot"] == 7), None)
    onset_boundary_ok = bool(
        onset_v7
        and onset_v7["input_CLV"] == [87, 233, 25]
        and onset_v7["forced_DP_CLV"] == [87, 238, 24]
        and onset_v7["final_CLV"] == [87, 233, 24]
        and onset_v7["debt_class"] == "LITERAL_DEBT"
        and onset_v7["dC"] == 0
        and onset_v7["dL"] == 5
        and onset_v7["rC"] == 0
        and onset_v7["rL"] == 5
        and onset_v7["accepted"]
        and onset_v7["acceptance_lane"] == "EXACT_C_L_REPAYMENT_VARIABLE_TIEBREAK"
        and onset_v7["macro_independent_replay_pass"]
    )

    invalid_debt_core_count = sum(bool(r["invalid_debt_pivots"]) for r in rows)
    invalid_lane_core_count = sum(bool(r["invalid_acceptance_lane_pivots"]) for r in rows)
    replay_failure_core_count = sum(bool(r["replay_failure_pivots"]) for r in rows)
    uncovered = [r for r in rows if not r["covered"]]
    metrics = {
        "core_count": len(rows),
        "covered_core_count": sum(bool(r["covered"]) for r in rows),
        "uncovered_core_count": len(uncovered),
        "bipolar_pivot_count": sum(int(r["bipolar_pivot_count"]) for r in rows),
        "CLAUSE_DEBT_count": sum(int(r["CLAUSE_DEBT_count"]) for r in rows),
        "LITERAL_DEBT_count": sum(int(r["LITERAL_DEBT_count"]) for r in rows),
        "accepted_pivot_count": sum(int(r["accepted_pivot_count"]) for r in rows),
        "terminal_accepted_count": sum(int(r["terminal_accepted_count"]) for r in rows),
        "nonterminal_accepted_count": sum(int(r["nonterminal_accepted_count"]) for r in rows),
        "first_accept_terminal_count": sum(bool(r["first_accepted_pivot"] and r["first_accepted_pivot"]["terminal"] is not None) for r in rows),
        "first_accept_nonterminal_count": sum(bool(r["first_accepted_pivot"] and r["first_accepted_pivot"]["terminal"] is None) for r in rows),
        "first_accept_exact_C_L_repayment_variable_tiebreak_count": sum(bool(r["first_accepted_pivot"] and r["first_accepted_pivot"]["acceptance_lane"] == "EXACT_C_L_REPAYMENT_VARIABLE_TIEBREAK") for r in rows),
        "invalid_debt_core_count": invalid_debt_core_count,
        "invalid_acceptance_lane_core_count": invalid_lane_core_count,
        "replay_failure_core_count": replay_failure_core_count,
        "R47G_boundary_var7_pass": onset_boundary_ok,
    }

    integrity_ok = all(r["genuine_fixpoint_integrity"]["pass"] for r in rows)
    accounting_ok = invalid_debt_core_count == 0 and invalid_lane_core_count == 0
    replay_ok = replay_failure_core_count == 0
    if not integrity_ok or not accounting_ok or not replay_ok or not onset_boundary_ok:
        verdict = "R47H_27_CORE_LEDGER_INTEGRITY_FAILURE"
    elif uncovered:
        verdict = "EXPLICIT_REACHABLE_COMPENSATION_DEAD_FIXPOINT_FOUND"
    else:
        verdict = "ALL_27_REACHABLE_FIXPOINTS_HAVE_CERTIFIED_DEBT_REPAYMENT_OR_TERMINAL_ESCAPE__FINITE_ONLY"

    first_uncovered = None
    if uncovered:
        u = uncovered[0]
        first_uncovered = {
            "source": u["source"],
            "label": u["label"],
            "seed": u["seed"],
            "fixpoint_hash": u["fixpoint_hash"],
            "fixpoint_CLV": u["fixpoint_CLV"],
            "pivot_receipts": u["pivot_receipts"],
        }

    return {
        "schema": "JANUS_TRUMP_R47H_27_CORE_COMPENSATION_LEDGER_RESULT",
        "version": "1.0",
        "date": "2026-09-03",
        "gate": "JANUS_TRUMP_R47H_27_CORE_COMPENSATION_LEDGER",
        "verdict": verdict,
        "metrics": metrics,
        "rows": rows,
        "first_uncovered_reachable_fixpoint": first_uncovered,
        "interpretation": {
            "finite_corpus_only": True,
            "universal_theorem_elevation_allowed": False,
            "O4_restatement": "FOR_EVERY_REACHABLE_GENUINE_FIXPOINT_EXISTS_POLYNOMIALLY_DISCOVERABLE_CERTIFIED_TERMINAL_ESCAPE_OR_DEBT_REPAYMENT_DESCENT",
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


def compact_summary(result: dict) -> dict:
    return {
        "gate": result["gate"],
        "verdict": result["verdict"],
        "metrics": result["metrics"],
        "first_uncovered_reachable_fixpoint": result["first_uncovered_reachable_fixpoint"],
        "firewall": result["firewall"],
    }


def self_test() -> None:
    f = r33.canonical_formula([(1, 2, 3), (-1, 2, 4), (1, -2, 5), (-1, -2, 6)])
    dp = r45a.exact_dp_record(f, 1)
    assert dp is not None
    assert "measure_after_forced_DP" in dp
    assert r45a.independent_dp_replay(f, dp)["pass"]
    print("R47H_SELF_TEST_PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    result = run_audit()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(compact_summary(result), sort_keys=True))


if __name__ == "__main__":
    main()
