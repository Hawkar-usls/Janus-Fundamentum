from __future__ import annotations

import json

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47a2_dense_bipolar_core_obstruction_probe as r47a2
import janus_trump_r47a3_post_subsumption_first_descent as r47a3


def successor(formula):
    before = r33.canonical_formula(formula)
    simp = r33.simplify(before)
    current = r33.canonical_formula(simp["final_formula"])
    if simp["terminal"] != "STALLED_STACK_LEAN_CORE":
        return {
            "route": "R33_TERMINAL_OR_REDUCTION",
            "terminal": simp["terminal"],
            "final_formula": current,
            "heavy_R45A_called": False,
        }

    affine = r34.recognize_complete_affine_cnf(current)
    if affine["recognized"]:
        return {
            "route": "AFFINE_TERMINAL",
            "affine": affine,
            "final_formula": current,
            "heavy_R45A_called": False,
        }

    fast = r47a3.first_certified_post_subsumption_descent(current)
    if fast.get("selected_var") is not None:
        assert fast["strict_descent"] is True
        assert fast["independent_replay_pass"] is True
        assert fast["polynomial_envelope_pass"] is True
        cert = r45a.exact_dp_record(current, int(fast["selected_var"]))
        return {
            "route": "POST_SUBSUMPTION_FIRST_DP_DESCENT",
            "selected_var": fast["selected_var"],
            "variables_checked": fast["variables_checked"],
            "gain": fast["gain"],
            "before_CLV": fast["before_CLV"],
            "after_CLV": fast["after_CLV"],
            "certificate": cert,
            "final_formula": r33.canonical_formula(cert["transformed"]),
            "heavy_R45A_called": False,
        }

    rup = r35b.run_candidate(current)
    replay = r35b.independent_certificate_replay(current, rup)
    rup_final = r33.canonical_formula(rup["final_formula"])
    if replay["pass"] and (
        rup["status"] == "UNSAT_BY_UNIT_PROPAGATION"
        or r33.measure(rup_final) < r33.measure(current)
    ):
        return {
            "route": "RUP_CERTIFIED",
            "status": rup["status"],
            "final_formula": rup_final,
            "heavy_R45A_called": False,
        }

    macro = r45a.select_macro(current)
    selected = macro.get("selected") or macro.get("selected_macro") or macro.get("macro")
    if selected is None and isinstance(macro.get("candidates"), list):
        accepted = [x for x in macro["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None
    return {
        "route": "R45A_FALLBACK",
        "has_selected_macro": selected is not None,
        "selected_var": None if selected is None else selected.get("var"),
        "selected_final_CLV": None if selected is None else selected.get("final_CLV"),
        "heavy_R45A_called": True,
    }


def run():
    result = successor(r47a2.FROZEN)
    out = {
        "gate": "JANUS_TRUMP_R47A4P_PRODUCTION_GRAMMAR_EARLY_DP",
        "result": result,
        "expected_route_on_r47a2_witness": "POST_SUBSUMPTION_FIRST_DP_DESCENT",
        "firewall": {
            "FIRST_CERTIFIED_DESCENT_UNIVERSAL": "NOT_PROVED",
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
