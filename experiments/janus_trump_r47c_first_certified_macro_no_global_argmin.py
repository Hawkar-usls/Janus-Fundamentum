from __future__ import annotations

import concurrent.futures
import json
import os

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r45b_frozen_26_stall_quotient_macro_coverage as r45b

SEEDS = tuple(r45b.FROZEN_STALL_SEEDS)


def first_certified_macro(formula):
    before = r33.canonical_formula(formula)
    vars_ = r33.variables(before)
    constructed = 0
    for checked, var in enumerate(vars_, 1):
        candidate = r45a.macro_candidate_for_var(before, int(var))
        if candidate is None:
            continue
        constructed += 1
        if not candidate["accepted"]:
            continue
        replay = r45a.independent_macro_replay(before, candidate)
        if not replay["pass"]:
            raise AssertionError(("R47C_SELECTED_REPLAY_FAIL", var, replay))
        return {
            "selected": candidate,
            "selected_replay": replay,
            "variables_checked": checked,
            "candidates_constructed": constructed,
            "total_variables": len(vars_),
        }
    return {
        "selected": None,
        "selected_replay": None,
        "variables_checked": len(vars_),
        "candidates_constructed": constructed,
        "total_variables": len(vars_),
    }


def audit_seed(seed: int):
    cases = r45b.frozen_case_map()
    label, original = cases[int(seed)]
    inherited, stall = r45b.replay_r42_terminal_formula(original, label)
    stall = r33.canonical_formula(stall)
    out = first_certified_macro(stall)
    selected = out["selected"]
    covered = bool(selected is not None and selected["accepted"] and out["selected_replay"] and out["selected_replay"]["pass"])
    return {
        "seed": int(seed),
        "label": label,
        "stall_hash": inherited["terminal_formula_hash"],
        "stall_CLV": list(r33.measure(stall)),
        "total_variables": out["total_variables"],
        "variables_checked": out["variables_checked"],
        "candidates_constructed": out["candidates_constructed"],
        "candidate_constructions_avoided_vs_all_variables": out["total_variables"] - out["variables_checked"],
        "covered": covered,
        "selected_var": None if selected is None else selected["var"],
        "selected_terminal": None if selected is None else selected["normalization"]["terminal"],
        "selected_final_CLV": None if selected is None else selected["final_CLV"],
        "selected_net_CLV_descent": None if selected is None else selected["net_CLV_descent"],
        "selected_replay_pass": bool(out["selected_replay"] and out["selected_replay"]["pass"]),
    }


def run():
    if len(SEEDS) != 26 or len(set(SEEDS)) != 26:
        raise AssertionError("R47C_FROZEN_LEDGER_DRIFT")
    workers = min(4, max(1, os.cpu_count() or 1), len(SEEDS))
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        rows = list(pool.map(audit_seed, SEEDS))
    rows.sort(key=lambda r: r["seed"])
    failures = [r for r in rows if not r["covered"]]
    total_slots = sum(r["total_variables"] for r in rows)
    checked_slots = sum(r["variables_checked"] for r in rows)
    avoided = total_slots - checked_slots
    metrics = {
        "case_count": len(rows),
        "covered_count": len(rows) - len(failures),
        "failure_count": len(failures),
        "total_variable_slots": total_slots,
        "variables_checked_to_first_accept": checked_slots,
        "candidate_constructions_avoided_vs_all_variable_slots": avoided,
        "avoided_fraction": 0.0 if total_slots == 0 else avoided / total_slots,
        "terminal_selection_count": sum(1 for r in rows if r["selected_terminal"] is not None),
        "descent_only_selection_count": sum(1 for r in rows if r["selected_terminal"] is None and r["selected_net_CLV_descent"]),
    }
    verdict = (
        "FIRST_CERTIFIED_MACRO_POLICY_VALID_ON_26_FROZEN_STALLS__O4_OPEN"
        if not failures
        else "FIRST_CERTIFIED_MACRO_POLICY_REGRESSION_FAILURE"
    )
    out = {
        "gate": "JANUS_TRUMP_R47C_FIRST_CERTIFIED_MACRO_NO_GLOBAL_ARGMIN",
        "verdict": verdict,
        "workers": workers,
        "metrics": metrics,
        "rows": rows,
        "failures": failures,
        "symbolic_local_theorem": {
            "global_argmin_required_for_local_correctness": False,
            "global_argmin_required_for_strict_progress": False,
            "first_accepted_policy_is_deterministic": True,
            "coverage_must_be_reproved_for_first_policy": True,
        },
        "firewall": {
            "FIRST_POLICY_UNIVERSAL_COVERAGE": "NOT_PROVED",
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
