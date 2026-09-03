from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47a3_post_subsumption_first_descent as r47a3
import janus_trump_r47a5_post_subsumption_descent_structural_theorem_or_counterexample as r47a5

FROZEN = r33.canonical_formula([
    [-3,-5,-7],[-3,4,6],[-3,6,7],[-2,-5,7],[-2,-4,7],[-2,6,-7],[-1,-3,7],
    [-1,-2,-3],[-1,2,-4],[-1,3,6],[1,-4,-6],[1,2,3],[1,5,-6],[2,4,5],
    [3,-4,-7],[3,4,-5],[3,4,6],[4,-6,-7],[4,-5,6],
])
N = 7


def selected_from_macro(macro):
    selected = macro.get("selected") or macro.get("selected_macro") or macro.get("macro")
    if selected is None and isinstance(macro.get("candidates"), list):
        accepted = [x for x in macro["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None
    return selected


def dp_r33_probe(formula, var: int):
    before = r33.canonical_formula(formula)
    dp = r45a.exact_dp_record(before, int(var))
    if dp is None:
        return None
    forced = r33.canonical_formula(dp["transformed"])
    simp = r33.simplify(forced)
    after = r33.canonical_formula(simp["final_formula"])
    terminal = simp["terminal"] != "STALLED_STACK_LEAN_CORE"
    descent = r33.measure(after) < r33.measure(before)
    return {
        "var": int(var),
        "DP_CLV": list(r33.measure(forced)),
        "R33_CLV": list(r33.measure(after)),
        "R33_terminal": simp["terminal"],
        "R33_rule_applications": int(simp["total_rule_applications"]),
        "rescue": bool(terminal or descent),
        "rescue_kind": "TERMINAL" if terminal else ("STRICT_CLV_DESCENT" if descent else "NONE"),
    }


def first_dp_r33_rescue(formula):
    before = r33.canonical_formula(formula)
    checked = 0
    for var in r33.variables(before):
        probe = dp_r33_probe(before, int(var))
        checked += 1
        if probe is None or not probe["rescue"]:
            continue
        claimed = r45a.macro_candidate_for_var(before, int(var))
        if claimed is None:
            raise AssertionError(("R47A8_SELECTED_VAR_LOST", var))
        replay = r45a.independent_macro_replay(before, claimed)
        if not claimed["accepted"] or not replay["pass"]:
            raise AssertionError(("R47A8_SELECTED_AUTHORITY_FAIL", var, claimed["accepted"], replay))
        return {
            "selected_var": int(var),
            "variables_checked": checked,
            "probe": probe,
            "authority_accepted": bool(claimed["accepted"]),
            "authority_replay_pass": bool(replay["pass"]),
            "authority_final_CLV": claimed["final_CLV"],
            "authority_terminal": claimed["normalization"].get("terminal"),
        }
    return {"selected_var": None, "variables_checked": checked}


def one_swap_neighbors(formula, universe):
    used = set(formula)
    for old in formula:
        base = used - {old}
        for new in universe:
            if new == old or new in base:
                continue
            yield r33.canonical_formula(list(base) + [new])


def eligible_original_core(formula):
    simp = r33.simplify(formula)
    final_formula = r33.canonical_formula(simp["final_formula"])
    if not (
        simp["terminal"] == "STALLED_STACK_LEAN_CORE"
        and simp["total_rule_applications"] == 0
        and final_formula == formula
    ):
        return False
    return r47a5.is_bipolar(formula)


def analyze_complement(formula, rows):
    affine = r34.recognize_complete_affine_cnf(formula)
    rup = r35b.run_candidate(formula)
    rup_replay = r35b.independent_certificate_replay(formula, rup)
    macro = r45a.select_macro(formula)
    selected = selected_from_macro(macro)
    return {
        "formula": [list(c) for c in formula],
        "input_CLV": list(r33.measure(formula)),
        "DP_R33_rows": rows,
        "affine_recognized": bool(affine["recognized"]),
        "RUP_status": rup["status"],
        "RUP_strengthening_count": len(rup.get("strengthenings", [])),
        "RUP_independent_replay_pass": bool(rup_replay["pass"]),
        "RUP_final_CLV": list(r33.measure(r33.canonical_formula(rup["final_formula"]))),
        "R45A_has_selection": selected is not None,
        "R45A_selected_var": None if selected is None else selected.get("var"),
        "R45A_selected_final_CLV": None if selected is None else selected.get("final_CLV"),
        "R45A_selected_terminal": None if selected is None else selected.get("normalization", {}).get("terminal"),
        "R45A_selected_net_CLV_descent": None if selected is None else selected.get("net_CLV_descent"),
    }


def run():
    before = FROZEN
    assert list(r33.measure(before)) == [19, 57, 7]

    old = r47a3.first_certified_post_subsumption_descent(before)
    new = first_dp_r33_rescue(before)
    assert old["selected_var"] is None
    assert new["selected_var"] is not None

    universe = r47a5.all_3clauses(N)
    seen = {before}
    stats = {
        "generated": 0,
        "unique": 0,
        "eligible_R33_lean_bipolar": 0,
        "DP_R33_complement_obstructions": 0,
    }
    complement = None
    for candidate in one_swap_neighbors(before, universe):
        stats["generated"] += 1
        if candidate in seen:
            continue
        seen.add(candidate)
        stats["unique"] += 1
        if not eligible_original_core(candidate):
            continue
        stats["eligible_R33_lean_bipolar"] += 1
        rows = [dp_r33_probe(candidate, int(v)) for v in r33.variables(candidate)]
        rows = [r for r in rows if r is not None]
        if rows and all(not r["rescue"] for r in rows):
            stats["DP_R33_complement_obstructions"] += 1
            complement = analyze_complement(candidate, rows)
            break

    verdict = (
        "DP_R33_PRODUCER_REGRESSION_PASS__COMPLEMENT_COUNTEREXAMPLE_FOUND"
        if complement is not None
        else "DP_R33_PRODUCER_REGRESSION_PASS__NO_COMPLEMENT_COUNTEREXAMPLE_IN_FROZEN_NEIGHBORHOOD"
    )
    out = {
        "gate": "JANUS_TRUMP_R47A8_DP_R33_FIRST_CERTIFIED_RESCUE_COMPLEMENT_HUNT",
        "verdict": verdict,
        "regression": {
            "input_CLV": list(r33.measure(before)),
            "old_clause_only_selected_var": old["selected_var"],
            "new_DP_R33": new,
        },
        "stats": stats,
        "complement_counterexample": complement,
        "firewall": {
            "DP_R33_RESCUE_UNIVERSAL": "NOT_PROVED",
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
