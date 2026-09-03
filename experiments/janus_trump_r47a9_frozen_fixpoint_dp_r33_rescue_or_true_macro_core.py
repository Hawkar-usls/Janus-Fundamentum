from __future__ import annotations

import concurrent.futures
import json
import os

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r45b_frozen_26_stall_quotient_macro_coverage as r45b
import janus_trump_r47a8_dp_r33_first_certified_rescue_complement_hunt as r47a8

SEEDS = tuple(r45b.FROZEN_STALL_SEEDS)


def selected_from_scan(scan):
    selected = scan.get("selected") or scan.get("selected_macro") or scan.get("macro")
    if selected is None and isinstance(scan.get("candidates"), list):
        accepted = [x for x in scan["candidates"] if x.get("accepted")]
        selected = min(accepted, key=lambda x: tuple(x.get("selection_key", []))) if accepted else None
    return selected


def verify_true_fixpoint(stall):
    before = r33.canonical_formula(stall)
    simp = r33.simplify(before)
    after_r33 = r33.canonical_formula(simp["final_formula"])
    if simp["terminal"] != "STALLED_STACK_LEAN_CORE" or after_r33 != before:
        raise AssertionError(("R47A9_NOT_R33_FIXPOINT", simp["terminal"], r33.measure(before), r33.measure(after_r33)))
    affine = r34.recognize_complete_affine_cnf(before)
    if affine["recognized"]:
        raise AssertionError("R47A9_UNEXPECTED_AFFINE_FIXPOINT")
    rup = r35b.run_candidate(before)
    rup_replay = r35b.independent_certificate_replay(before, rup)
    after_rup = r33.canonical_formula(rup["final_formula"])
    history = rup.get("history", [])
    if not rup_replay["pass"]:
        raise AssertionError("R47A9_RUP_REPLAY_FAIL")
    if rup["status"] != "STALLED_RUP_CORE" or history or after_rup != before:
        raise AssertionError(("R47A9_NOT_RUP_FIXPOINT", rup["status"], len(history), r33.measure(before), r33.measure(after_rup)))
    bve, bve_ledger = r42.best_sa_bve_candidate(before)
    if bve is not None:
        raise AssertionError(("R47A9_NOT_BVE_FIXPOINT", bve.get("var"), bve.get("measure_after")))
    return {
        "R33_terminal": simp["terminal"],
        "affine_recognized": False,
        "RUP_status": rup["status"],
        "RUP_history_count": len(history),
        "RUP_replay_pass": True,
        "BVE_candidate": None,
        "BVE_variables_checked": bve_ledger.get("variables_checked"),
    }


def audit_seed(seed: int):
    cases = r45b.frozen_case_map()
    label, original = cases[int(seed)]
    inherited, stall = r45b.replay_r42_terminal_formula(original, label)
    fixpoint = verify_true_fixpoint(stall)
    stall = r33.canonical_formula(stall)
    vars_count = len(r33.variables(stall))
    early = r47a8.first_dp_r33_rescue(stall)
    if early["selected_var"] is not None:
        return {
            "seed": int(seed),
            "label": label,
            "stall_hash": inherited["terminal_formula_hash"],
            "stall_CLV": list(r33.measure(stall)),
            "variable_count": vars_count,
            "fixpoint": fixpoint,
            "route": "EARLY_DP_R33",
            "early": early,
            "fallback": None,
            "covered": True,
        }

    scan = r45a.select_macro(stall)
    selected = selected_from_scan(scan)
    selected_replay = scan.get("selected_independent_replay")
    if selected is not None and selected_replay is None:
        selected_replay = r45a.independent_macro_replay(stall, selected)
    covered = bool(selected is not None and selected.get("accepted") and selected_replay and selected_replay["pass"])
    return {
        "seed": int(seed),
        "label": label,
        "stall_hash": inherited["terminal_formula_hash"],
        "stall_CLV": list(r33.measure(stall)),
        "variable_count": vars_count,
        "fixpoint": fixpoint,
        "route": "R45A_FALLBACK" if covered else "UNCOVERED_FIXPOINT",
        "early": early,
        "fallback": {
            "has_selection": selected is not None,
            "selected_var": None if selected is None else selected.get("var"),
            "selected_final_CLV": None if selected is None else selected.get("final_CLV"),
            "selected_terminal": None if selected is None else selected.get("normalization", {}).get("terminal"),
            "selected_net_CLV_descent": None if selected is None else selected.get("net_CLV_descent"),
            "selected_replay_pass": bool(selected_replay and selected_replay["pass"]),
            "candidate_count": scan.get("candidate_count"),
            "acceptable_candidate_count": scan.get("acceptable_candidate_count"),
            "global_polynomial_scan_bounds_pass": bool(scan.get("global_polynomial_scan_bounds", {}).get("pass")),
        },
        "covered": covered,
    }


def run():
    if len(SEEDS) != 26 or len(set(SEEDS)) != 26:
        raise AssertionError("R47A9_FROZEN_SEED_LEDGER_DRIFT")
    workers = min(4, max(1, os.cpu_count() or 1), len(SEEDS))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(audit_seed, SEEDS))
    rows.sort(key=lambda r: r["seed"])

    early_rows = [r for r in rows if r["route"] == "EARLY_DP_R33"]
    fallback_rows = [r for r in rows if r["route"] == "R45A_FALLBACK"]
    uncovered = [r for r in rows if r["route"] == "UNCOVERED_FIXPOINT"]
    early_terminal = [r for r in early_rows if r["early"]["probe"]["rescue_kind"] == "TERMINAL"]
    early_descent = [r for r in early_rows if r["early"]["probe"]["rescue_kind"] == "STRICT_CLV_DESCENT"]

    if uncovered:
        verdict = "FROZEN_FIXPOINT_WITH_NO_ACCEPTED_MACRO_FOUND"
    elif len(early_rows) == len(rows):
        verdict = "EARLY_DP_R33_RESCUES_ALL_26_FROZEN_FIXPOINTS__FINITE_ONLY"
    else:
        verdict = "EARLY_DP_R33_RESCUES_SUBSET__R45A_FALLBACK_COVERS_REMAINDER"

    metrics = {
        "frozen_fixpoint_count": len(rows),
        "early_rescue_count": len(early_rows),
        "fallback_count": len(fallback_rows),
        "uncovered_count": len(uncovered),
        "early_terminal_count": len(early_terminal),
        "early_strict_descent_count": len(early_descent),
        "sum_early_variables_checked": sum(int(r["early"]["variables_checked"]) for r in early_rows),
        "legacy_full_macro_variable_slots_on_early_rescued_states": sum(int(r["variable_count"]) for r in early_rows),
        "early_rescue_seeds": [r["seed"] for r in early_rows],
        "fallback_seeds": [r["seed"] for r in fallback_rows],
        "uncovered_seeds": [r["seed"] for r in uncovered],
    }

    out = {
        "gate": "JANUS_TRUMP_R47A9_FROZEN_FIXPOINT_DP_R33_RESCUE_OR_TRUE_MACRO_CORE",
        "verdict": verdict,
        "workers": workers,
        "metrics": metrics,
        "rows": rows,
        "first_uncovered": None if not uncovered else uncovered[0],
        "interpretation": {
            "finite_26_stall_audit_only": True,
            "universal_theorem_elevation_allowed": False,
            "early_search_is_not_proof_authority": True,
        },
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
