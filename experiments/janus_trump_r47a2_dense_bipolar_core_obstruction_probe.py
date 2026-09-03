from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a

Formula = tuple[tuple[int, ...], ...]

FROZEN: Formula = r33.canonical_formula([
    [-1,-2,-5],[-1,-2,5],[-1,2,5],[1,-4,-5],[1,-3,4],[1,-2,-3],[1,-2,3],
    [1,2,-4],[2,-4,-5],[2,-4,5],[2,-3,4],[2,3,5],[3,4,-5],
])


def dp_row(formula: Formula, var: int) -> dict:
    pos, neg, resolvents, pair_checks = r42.all_dp_resolvents(formula, var)
    base = tuple(c for c in formula if var not in c and -var not in c)
    base_set = set(base)
    new = tuple(r for r in resolvents if r not in base_set)
    transformed = r42.subsumption_minimize(r33.canonical_formula(list(base) + list(resolvents)))
    return {
        "var": var,
        "p": len(pos),
        "n": len(neg),
        "unique_non_tautological_resolvents": len(resolvents),
        "new_resolvents": len(new),
        "pair_checks": pair_checks,
        "before_CLV": list(r33.measure(formula)),
        "after_DP_CLV": list(r33.measure(transformed)),
        "direct_DP_descent": r33.measure(transformed) < r33.measure(formula),
        "strict_unique_expansion_vs_removed": len(resolvents) > len(pos) + len(neg),
    }


def run() -> dict:
    formula = FROZEN
    r33_result = r33.simplify(formula)
    r33_final = r33.canonical_formula(r33_result["final_formula"])
    rows = [dp_row(formula, v) for v in r33.variables(formula)]

    affine = r34.recognize_complete_affine_cnf(formula)
    rup = r35b.run_candidate(formula)
    rup_replay = r35b.independent_certificate_replay(formula, rup)
    macro = r45a.select_macro(formula)

    selected = macro.get("selected") or macro.get("selected_macro") or macro.get("macro")
    if selected is None and isinstance(macro.get("candidates"), list):
        accepted = [x for x in macro["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None

    out = {
        "formula": [list(c) for c in formula],
        "input_CLV": list(r33.measure(formula)),
        "R33": {
            "terminal": r33_result["terminal"],
            "rule_counts": r33_result["rule_counts"],
            "total_rule_applications": r33_result["total_rule_applications"],
            "final_formula_equal_input": r33_final == formula,
        },
        "DP_rows": rows,
        "all_variables_strict_unique_expansion_vs_removed": all(r["strict_unique_expansion_vs_removed"] for r in rows),
        "any_direct_DP_descent": any(r["direct_DP_descent"] for r in rows),
        "affine": {"recognized": bool(affine["recognized"]), "reason": affine.get("reason")},
        "RUP": {
            "status": rup["status"],
            "successful_strengthening_count": len(rup.get("strengthenings", [])),
            "independent_replay_pass": bool(rup_replay["pass"]),
            "final_CLV": list(r33.measure(r33.canonical_formula(rup["final_formula"]))),
        },
        "R45A": {
            "status": macro.get("status"),
            "has_selected_macro": selected is not None,
            "selected_var": None if selected is None else selected.get("var"),
            "selected_terminal": None if selected is None else selected.get("normalization", {}).get("terminal"),
            "selected_net_CLV_descent": None if selected is None else selected.get("net_CLV_descent"),
            "selected_final_CLV": None if selected is None else selected.get("final_CLV"),
            "variables_checked": macro.get("ledger", {}).get("variables_checked") if isinstance(macro.get("ledger"), dict) else None,
        },
        "firewall": {
            "R47A_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
