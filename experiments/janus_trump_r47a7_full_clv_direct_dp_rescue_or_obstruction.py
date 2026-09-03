from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a

FROZEN = r33.canonical_formula([
    [-3,-5,-7],[-3,4,6],[-3,6,7],[-2,-5,7],[-2,-4,7],[-2,6,-7],[-1,-3,7],
    [-1,-2,-3],[-1,2,-4],[-1,3,6],[1,-4,-6],[1,2,3],[1,5,-6],[2,4,5],
    [3,-4,-7],[3,4,-5],[3,4,6],[4,-6,-7],[4,-5,6],
])


def pivot_row(formula, var: int):
    before = r33.canonical_formula(formula)
    dp = r45a.exact_dp_record(before, int(var))
    if dp is None:
        return None
    replay = r45a.independent_dp_replay(before, dp)
    envelope = r45a.polynomial_envelope(before, dp)
    forced = r33.canonical_formula(dp["transformed"])
    norm = r45a.normalize_after_dp(forced)
    final_formula = r33.canonical_formula(norm["final_formula"])
    macro = r45a.macro_candidate_for_var(before, int(var))
    after_r33 = r33.canonical_formula(norm["R33_result"]["final_formula"])
    rup_status = None
    rup_final_clv = None
    if norm.get("RUP_record") is not None:
        rup = norm["RUP_record"]
        rup_status = rup.get("status")
        rup_final_clv = list(r33.measure(r33.canonical_formula(rup["final_formula"])))
    return {
        "var": int(var),
        "before_CLV": list(r33.measure(before)),
        "immediate_DP_CLV": list(r33.measure(forced)),
        "immediate_clause_gain": len(before) - len(forced),
        "immediate_DP_CLV_descent": r33.measure(forced) < r33.measure(before),
        "DP_replay_pass": bool(replay["pass"]),
        "DP_polynomial_envelope_pass": bool(envelope["pass"]),
        "after_R33_CLV": list(r33.measure(after_r33)),
        "R33_terminal": norm["R33_result"]["terminal"],
        "normalization_terminal": norm.get("terminal"),
        "RUP_status": rup_status,
        "RUP_final_CLV": rup_final_clv,
        "final_CLV": list(r33.measure(final_formula)),
        "final_CLV_descent": r33.measure(final_formula) < r33.measure(before),
        "macro_accepted": bool(macro["accepted"]),
        "macro_net_CLV_descent": bool(macro["net_CLV_descent"]),
        "temporary_internal_ascent": bool(macro["temporary_internal_ascent"]),
    }


def run():
    before = FROZEN
    assert list(r33.measure(before)) == [19,57,7]
    rows = [pivot_row(before, int(v)) for v in r33.variables(before)]
    rows = [r for r in rows if r is not None]
    any_direct = any(r["immediate_DP_CLV_descent"] for r in rows)
    any_normalized = any(r["macro_accepted"] for r in rows)
    selected = r45a.select_macro(before)
    chosen = selected.get("selected") or selected.get("selected_macro") or selected.get("macro")
    if chosen is None and isinstance(selected.get("candidates"), list):
        acc = [x for x in selected["candidates"] if x.get("accepted")]
        chosen = min(acc, key=lambda x: tuple(x.get("selection_key", []))) if acc else None

    if any_direct:
        verdict = "CLAUSE_ONLY_OBSTRUCTION__FULL_CLV_DIRECT_DP_DESCENT_EXISTS"
    elif any_normalized:
        verdict = "FULL_CLV_DIRECT_DP_OBSTRUCTION__NORMALIZATION_RESCUE_EXISTS"
    else:
        verdict = "FULL_CLV_DIRECT_DP_AND_NORMALIZATION_OBSTRUCTION"

    out = {
        "gate": "JANUS_TRUMP_R47A7_FULL_CLV_DIRECT_DP_RESCUE_OR_OBSTRUCTION",
        "verdict": verdict,
        "input_CLV": list(r33.measure(before)),
        "rows": rows,
        "any_immediate_full_CLV_descent": any_direct,
        "any_normalized_macro_acceptance": any_normalized,
        "selected_var": None if chosen is None else chosen.get("var"),
        "selected_immediate_DP_CLV_descent": None if chosen is None else chosen.get("immediate_DP_CLV_descent"),
        "selected_final_CLV": None if chosen is None else chosen.get("final_CLV"),
        "selected_normalization_terminal": None if chosen is None else chosen.get("normalization", {}).get("terminal"),
        "selected_normalization_R33_terminal": None if chosen is None else chosen.get("normalization", {}).get("R33_result", {}).get("terminal"),
        "selected_RUP_status": None if chosen is None or chosen.get("normalization", {}).get("RUP_record") is None else chosen["normalization"]["RUP_record"].get("status"),
        "firewall": {
            "FULL_CLV_DIRECT_DP_UNIVERSAL": "NOT_PROVED",
            "R47A_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
