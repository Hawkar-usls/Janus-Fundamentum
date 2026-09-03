from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47a7_full_clv_direct_dp_rescue_or_obstruction as r47a7


def r33_polynomial_step_cap(formula) -> int:
    f = r33.canonical_formula(formula)
    C = len(f)
    V = len(r33.variables(f))
    lmax_safe = 2 * C * max(1, V)
    return (C + 1) * (lmax_safe + 1) * (V + 1)


def r33_simplify_polycap(formula) -> dict:
    f = r33.canonical_formula(formula)
    cap = r33_polynomial_step_cap(f)
    out = r33.simplify(f, max_steps=cap)
    if out["terminal"] == "FAIL_STEP_LIMIT":
        raise AssertionError(("R47B_POLYNOMIAL_CAP_EXHAUSTED", cap, out["initial_measure"], out["final_measure"]))
    return out


def same_r33_result(a: dict, b: dict) -> bool:
    return (
        a["terminal"] == b["terminal"]
        and a["final_formula"] == b["final_formula"]
        and a["history"] == b["history"]
        and a["rule_counts"] == b["rule_counts"]
        and a["final_measure"] == b["final_measure"]
    )


def rup_symbolic_bounds(formula) -> dict:
    f = r33.canonical_formula(formula)
    C = len(f)
    V = len(r33.variables(f))
    L = sum(len(c) for c in f)
    rup_checks = L * (L + 1)
    up_literal_inspections = (V + 1) * (((L + 1) * L * L) + ((L + 2) * L))
    up_clause_scans = (V + 1) * C * (((L + 1) * L) + (L + 2))
    return {
        "C": C,
        "V": V,
        "L": L,
        "rup_checks_upper": rup_checks,
        "up_literal_inspections_upper": up_literal_inspections,
        "up_clause_scans_upper": up_clause_scans,
    }


def audit_rup(formula) -> dict:
    f = r33.canonical_formula(formula)
    candidate = r35b.run_candidate(f)
    replay = r35b.independent_certificate_replay(f, candidate)
    bounds = rup_symbolic_bounds(f)
    ledger = candidate["ledger"]
    within = {
        "rup_checks": int(ledger["rup_checks"]) <= bounds["rup_checks_upper"],
        "up_literal_inspections": int(ledger["up_literal_inspections"]) <= bounds["up_literal_inspections_upper"],
        "up_clause_scans": int(ledger["up_clause_scans"]) <= bounds["up_clause_scans_upper"],
    }
    return {
        "input_CLV": list(r33.measure(f)),
        "status": candidate["status"],
        "successful_strengthenings": len(candidate.get("history", [])),
        "ledger": ledger,
        "bounds": bounds,
        "within_bounds": within,
        "independent_replay_pass": bool(replay["pass"]),
        "pass": bool(replay["pass"] and all(within.values())),
    }


def run():
    cases = [
        ("easy_tail", r33.easy_redundant_tail()),
        ("blocked", r33.blocked_clause_control()),
        ("bve", r33.bve_control()),
        ("prism8", r33.prism_tseitin(8)),
        ("prism12", r33.prism_tseitin(12)),
        ("random33001", r33.deterministic_random_3cnf(33001)),
        ("random33004", r33.deterministic_random_3cnf(33004)),
    ]
    for v in r33.variables(r47a7.FROZEN):
        dp = r45a.exact_dp_record(r47a7.FROZEN, int(v))
        if dp is not None:
            cases.append((f"r47a6_forced_dp_v{v}", r33.canonical_formula(dp["transformed"])))

    rows = []
    rup_rows = []
    for name, formula in cases:
        f = r33.canonical_formula(formula)
        default = r33.simplify(f)
        poly = r33_simplify_polycap(f)
        cap = r33_polynomial_step_cap(f)
        equal = same_r33_result(default, poly)
        row = {
            "name": name,
            "input_CLV": list(r33.measure(f)),
            "polycap": cap,
            "default_terminal": default["terminal"],
            "polycap_terminal": poly["terminal"],
            "rule_applications": poly["total_rule_applications"],
            "cap_slack": cap - poly["total_rule_applications"],
            "identical_to_default": equal,
        }
        rows.append(row)
        if poly["terminal"] == "STALLED_STACK_LEAN_CORE":
            rup_rows.append({"name": name, **audit_rup(r33.canonical_formula(poly["final_formula"]))})

    pass_r33 = all(r["identical_to_default"] and r["cap_slack"] >= 1 for r in rows)
    pass_rup = all(r["pass"] for r in rup_rows)
    verdict = (
        "POLYNOMIAL_R33_CAP_AND_RUP_ENVELOPE_SEALED__UNIVERSAL_COVERAGE_OPEN"
        if pass_r33 and pass_rup
        else "RESOURCE_ENVELOPE_REGRESSION_MISMATCH"
    )
    out = {
        "gate": "JANUS_TRUMP_R47B_POLYNOMIAL_R33_RUP_RESOURCE_ENVELOPE",
        "verdict": verdict,
        "R33_rows": rows,
        "RUP_rows": rup_rows,
        "symbolic_status": {
            "R33_step_cap_degree_coarse": "O(C^2 V^2)",
            "DP_peak_representation": "O(C^2 V)",
            "RUP_search_work_coarse": "O(V L^3)",
            "all_variable_scan_multiplier": "at most V",
            "O3_POLYNOMIAL_WORK_PER_TRANSITION": "SYMBOLICALLY_CLOSED_FOR_FROZEN_GRAMMAR_WITH_POLYCAP_R33" if pass_r33 and pass_rup else "OPEN_REGRESSION",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
        },
        "firewall": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
