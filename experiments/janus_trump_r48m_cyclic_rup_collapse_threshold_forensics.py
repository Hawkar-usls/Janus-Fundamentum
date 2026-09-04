from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r48i_cyclic_bipolar_rxr_pressure_scaling_law as r48i

GATE = "JANUS_TRUMP_R48M_CYCLIC_RUP_COLLAPSE_THRESHOLD_FORENSICS"
R_VALUES = (3, 6, 9)
EXPECTED = {
    3: {"n":25, "terminal_count":0},
    6: {"n":49, "terminal_count":49},
    9: {"n":73, "terminal_count":73},
}


def canon(f):
    return r33.canonical_formula(f)


def clv(f):
    return r33.measure(canon(f))


def direct_rup(formula):
    before = canon(formula)
    rup = r47j.r35b.run_candidate(before)
    replay = r47j.r35b.independent_certificate_replay(before, rup)
    if not replay["pass"]:
        raise AssertionError("R48M_DIRECT_RUP_REPLAY_FAIL")
    return {
        "status": rup["status"],
        "history_count": len(rup.get("history", [])),
        "final_CLV": list(clv(rup["final_formula"])),
        "replay_pass": True,
        "ledger": rup["ledger"],
    }


def pivot_forensics(formula, var):
    before = canon(formula)
    dp = r47m.r45a.exact_dp_record(before, int(var))
    if dp is None:
        raise AssertionError(("R48M_DP_RECORD_MISSING", var))
    dp_replay = r47m.r45a.independent_dp_replay(before, dp)
    envelope = r47m.r45a.polynomial_envelope(before, dp)
    if not dp_replay["pass"] or not envelope["pass"]:
        raise AssertionError(("R48M_DP_INTEGRITY_FAIL", var, dp_replay, envelope))
    forced = canon(dp["transformed"])
    norm = r47j.normalize_to_certified_fixpoint(forced)
    rounds = norm["rounds"]
    if not rounds:
        raise AssertionError(("R48M_NO_NORMALIZATION_ROUNDS", var))
    first = rounds[0]
    terminal_verification_pass = True
    if norm["terminal"] == "RUP_UNSAT":
        tv = norm["terminal_verification"]
        terminal_verification_pass = bool(tv and tv.get("pass"))
        if not terminal_verification_pass:
            raise AssertionError(("R48M_TERMINAL_RUP_REPLAY_FAIL", var))
    return {
        "var": int(var),
        "input_CLV": list(clv(before)),
        "forced_DP_CLV": list(clv(forced)),
        "DP_independent_replay_pass": True,
        "polynomial_intermediate_envelope_pass": True,
        "terminal": norm["terminal"],
        "semantic_sat": norm["semantic_sat"],
        "round_count": int(norm["round_count"]),
        "restart_count": int(norm["restart_count"]),
        "first_round": first,
        "RUP_terminal_replay_pass": terminal_verification_pass,
        "normalization_ledger": norm["ledger"],
        "final_CLV": list(norm["final_CLV"]),
        "direct_after_DP_RUP_UNSAT_zero_R33_apps": bool(
            norm["terminal"] == "RUP_UNSAT"
            and first.get("R33_apps") == 0
            and first.get("RUP_status") == "UNSAT_BY_UNIT_PROPAGATION"
            and first.get("round") == 0
        ),
    }


def run_one(r):
    raw, construction = r48i.cyclic_bipolar_rxr(int(r))
    if raw is None:
        raise AssertionError(("R48M_R48I_CONSTRUCTION_DRIFT", r, construction))
    raw = canon(raw)
    expected_n = EXPECTED[int(r)]["n"]
    if len(r33.variables(raw)) != expected_n:
        raise AssertionError(("R48M_N_DRIFT", r, len(r33.variables(raw)), expected_n))

    pre = r47m.normalize_full_existing_stack(raw)
    if pre["terminal"] is not None:
        raise AssertionError(("R48M_PREPROJECTION_TERMINAL_DRIFT", r, pre["terminal"]))
    residual = canon(pre["final_formula"])
    if residual != raw:
        raise AssertionError(("R48M_PREPROJECTION_CHANGED_DRIFT", r, clv(raw), clv(residual)))

    direct = direct_rup(raw)
    rows = [pivot_forensics(raw, int(v)) for v in r33.variables(raw)]
    terminals = [x for x in rows if x["terminal"] is not None]
    rup_terminals = [x for x in rows if x["terminal"] == "RUP_UNSAT"]
    direct_zero_r33 = [x for x in rows if x["direct_after_DP_RUP_UNSAT_zero_R33_apps"]]
    if len(terminals) != EXPECTED[int(r)]["terminal_count"]:
        raise AssertionError(("R48M_TERMINAL_COUNT_DRIFT", r, len(terminals), EXPECTED[int(r)]["terminal_count"]))
    return {
        "r": int(r),
        "n": int(expected_n),
        "raw_hash": r48i.formula_hash(raw),
        "raw_CLV": list(clv(raw)),
        "direct_preprojection_RUP": direct,
        "preprojection_full_stack": {
            "terminal": pre["terminal"],
            "segment_count": int(pre["segment_count"]),
            "SA_BVE_application_count": int(pre["SA_BVE_application_count"]),
            "final_CLV": list(pre["final_CLV"]),
        },
        "pivot_count": len(rows),
        "terminal_count": len(terminals),
        "RUP_UNSAT_terminal_count": len(rup_terminals),
        "direct_after_DP_RUP_UNSAT_zero_R33_apps_count": len(direct_zero_r33),
        "all_pivots_direct_after_DP_RUP_UNSAT_zero_R33_apps": len(direct_zero_r33) == len(rows),
        "pivot_rows": rows,
    }


def run():
    rows = [run_one(r) for r in R_VALUES]
    r3, r6, r9 = rows
    replay_pattern_ok = (
        r3["terminal_count"] == 0
        and r6["terminal_count"] == r6["pivot_count"]
        and r9["terminal_count"] == r9["pivot_count"]
    )
    if not replay_pattern_ok:
        verdict = "SEALED_R48I_TERMINAL_PATTERN_FAILS_REPLAY"
    elif r6["all_pivots_direct_after_DP_RUP_UNSAT_zero_R33_apps"] and r9["all_pivots_direct_after_DP_RUP_UNSAT_zero_R33_apps"]:
        verdict = "ALL_PIVOT_RUP_COLLAPSE_IS_DIRECT_AFTER_DP_WITH_ZERO_R33_APPS"
    elif all(x["terminal"] == "RUP_UNSAT" for x in r6["pivot_rows"] + r9["pivot_rows"]):
        verdict = "ALL_PIVOT_RUP_COLLAPSE_REQUIRES_R33_MEDIATION"
    else:
        verdict = "MIXED_COLLAPSE_MECHANISMS_ACROSS_PIVOTS_OR_R_VALUES"
    return {
        "gate": GATE,
        "verdict": verdict,
        "rows": rows,
        "summary": {
            "r3_direct_preprojection_RUP_status": r3["direct_preprojection_RUP"]["status"],
            "r6_direct_preprojection_RUP_status": r6["direct_preprojection_RUP"]["status"],
            "r9_direct_preprojection_RUP_status": r9["direct_preprojection_RUP"]["status"],
            "r3_terminal_fraction_after_one_DP": [r3["terminal_count"], r3["pivot_count"]],
            "r6_terminal_fraction_after_one_DP": [r6["terminal_count"], r6["pivot_count"]],
            "r9_terminal_fraction_after_one_DP": [r9["terminal_count"], r9["pivot_count"]],
            "r6_direct_zero_R33_fraction": [r6["direct_after_DP_RUP_UNSAT_zero_R33_apps_count"], r6["pivot_count"]],
            "r9_direct_zero_R33_fraction": [r9["direct_after_DP_RUP_UNSAT_zero_R33_apps_count"], r9["pivot_count"]],
        },
        "interpretation": {
            "finite_r_values_prove_universal_threshold": False,
            "all_pivot_direct_collapse_if_observed_is_structural_signal": True,
            "next_symbolic_target": "Characterize a local/global condition under which exact projection of any pivot makes the residual UP-refutable, then test whether the condition follows from the cyclic difference-set density for all sufficiently large r or is an artifact of the frozen starters."
        },
        "firewall": {
            "UNIVERSAL_ROOT_POLYNOMIAL_PRESSURE_BOUND": "NOT_PROVED",
            "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output")
    a=p.parse_args()
    d=run()
    if a.output:
        path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "gate":d["gate"],
        "verdict":d["verdict"],
        "summary":d["summary"],
        "round0_samples": [{
            "r":x["r"],
            "first_pivot":x["pivot_rows"][0]["var"],
            "first_round":x["pivot_rows"][0]["first_round"],
        } for x in d["rows"]],
        "firewall":d["firewall"],
    },sort_keys=True))


if __name__=="__main__":
    main()
