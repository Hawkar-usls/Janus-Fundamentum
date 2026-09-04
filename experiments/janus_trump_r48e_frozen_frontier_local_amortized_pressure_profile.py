from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r48d_minimum_local_amortized_pressure_controller as r48d

GATE = "JANUS_TRUMP_R48E_FROZEN_FRONTIER_LOCAL_AMORTIZED_PRESSURE_PROFILE"
MAX_ORDINAL = 64
R47X_ROOT_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
R47X_EXPECTED_A_RUN = 1
R47X_EXPECTED_MAX_A_STAR = 1
R47X_EXPECTED_PIVOTS = [7, 2, 15, 5]


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def run_general_controller(root):
    root = canon(root)
    C0, _, V0 = clv(root)
    if V0 <= 0:
        raise AssertionError(("R48E_ZERO_VARIABLE_ROOT", clv(root)))
    old = (r48d.C0, r48d.V0, r48d.MAX_STEPS, r48d.MAX_PROBES)
    try:
        r48d.C0 = int(C0)
        r48d.V0 = int(V0)
        r48d.MAX_STEPS = int(V0)
        r48d.MAX_PROBES = int(V0 * V0)
        run = r48d.run_controller(root)
        amort = r48d.posthoc_amortization(root, run)
    finally:
        r48d.C0, r48d.V0, r48d.MAX_STEPS, r48d.MAX_PROBES = old
    return run, amort


def compact_success(root, provenance, run, amort):
    if not run["covered"]:
        raise AssertionError("R48E_COMPACT_SUCCESS_ON_OBSTRUCTION")
    root = canon(root)
    steps = []
    for s in run["selected_steps"]:
        steps.append({
            "step": int(s["step"]),
            "var": int(s["var"]),
            "input_CLV": s["input_CLV"],
            "forced_DP_CLV": s["forced_DP_CLV"],
            "final_CLV": s["final_CLV"],
            "delta_C": int(s["delta_C"]),
            "delta_V_eliminated": int(s["delta_V_eliminated"]),
            "a_req": int(s["a_req"] or 0),
            "terminal": s["terminal"],
            "semantic_sat": s["semantic_sat"],
            "DP_independent_replay_pass": bool(s["DP_independent_replay_pass"]),
            "polynomial_intermediate_envelope_pass": bool(s["polynomial_intermediate_envelope_pass"]),
            "full_R47M_independent_replay_pass": bool(s["full_R47M_independent_replay_pass"]),
        })
    state_pressures = [{
        "state_index": int(p["state_index"]),
        "state_hash": p["state_hash"],
        "state_CLV": p["state_CLV"],
        "candidate_count": int(p["candidate_count"]),
        "eligible_count": int(p["eligible_count"]),
        "terminal_candidate_count": int(p["terminal_candidate_count"]),
        "a_star": int(p["a_star"]),
        "selected_var": int(p["selected_var"]),
        "selected_a_req": int(p["selected_a_req"]),
        "selected_terminal": p["selected_terminal"],
    } for p in run["state_profiles"]]
    return {
        "provenance": provenance,
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "covered": True,
        "candidate_probe_count": int(run["candidate_probe_count"]),
        "selected_step_count": len(steps),
        "selected_pivots": [s["var"] for s in steps],
        "selected_steps": steps,
        "state_pressures": state_pressures,
        "A_run": int(amort["A_run"]),
        "max_state_a_star": int(amort["max_state_a_star"]),
        "pressure_sequence": [int(x) for x in amort["selected_nonterminal_pressure_sequence"]],
        "induced_persistent_clause_bound": int(amort["induced_persistent_clause_bound_C0_plus_A_run_V0"]),
        "max_observed_persisted_clauses": int(amort["max_observed_persisted_clauses"]),
        "max_observed_persisted_literals": int(amort["max_observed_persisted_literals"]),
        "weighted_identities_pass": bool(amort["all_weighted_step_identities_pass"]),
        "observed_clause_bound_pass": bool(amort["observed_clause_bound_pass"]),
        "terminal": run["terminal"],
        "SAT_root_reconstruction_pass": bool(run["SAT_root_reconstruction"]["pass"]),
    }


def compact_obstruction(root, provenance, run, amort):
    if run["covered"]:
        raise AssertionError("R48E_COMPACT_OBSTRUCTION_ON_SUCCESS")
    obstruction = run["obstruction"]
    return {
        "provenance": provenance,
        "root_hash": formula_hash(root),
        "root_CLV": list(clv(root)),
        "covered": False,
        "candidate_probe_count": int(run["candidate_probe_count"]),
        "selected_step_count": len(run["selected_steps"]),
        "selected_pivots": [int(s["var"]) for s in run["selected_steps"]],
        "A_run_before_obstruction": int(amort["A_run"]),
        "max_state_a_star_before_obstruction": int(amort["max_state_a_star"]),
        "obstruction": {
            "state_hash": obstruction["state_hash"],
            "state_CLV": obstruction["state_CLV"],
            "state_formula": obstruction["state_formula"],
            "candidate_rows": obstruction["candidate_rows"],
        },
    }


def profile_root(root, provenance):
    run, amort = run_general_controller(root)
    if run["covered"]:
        return compact_success(root, provenance, run, amort)
    return compact_obstruction(root, provenance, run, amort)


def run():
    center_original, _, center_fixpoint = r47x.load_center_original()
    records = []
    seen = set()
    metrics = {
        "frontier_positions_seen": 0,
        "mutants_generated": 0,
        "duplicate_mutations_skipped": 0,
        "semantic_or_nonfixpoint": 0,
        "reachable_fixpoints": 0,
        "unique_reachable_fixpoints_profiled": 0,
        "covered_roots": 0,
        "controller_obstruction_roots": 0,
        "total_candidate_probes": 0,
        "total_selected_steps": 0,
    }

    center_record = profile_root(center_fixpoint, {
        "kind": "CENTER_CONTROL",
        "frontier_ordinal": 0,
        "phase": "CENTER",
        "source_clause": None,
        "replacement_clause": None,
    })
    records.append(center_record)
    seen.add(center_record["root_hash"])

    for ordinal, (phase, source, replacement, mutated) in enumerate(r47x.frontier(center_original), 1):
        if ordinal > MAX_ORDINAL:
            break
        metrics["frontier_positions_seen"] += 1
        if mutated is None:
            metrics["duplicate_mutations_skipped"] += 1
            continue
        r47x.validate_exact_3cnf(mutated)
        metrics["mutants_generated"] += 1
        reached = r47f.reachable_fixpoint(mutated)
        if reached is None:
            metrics["semantic_or_nonfixpoint"] += 1
            continue
        metrics["reachable_fixpoints"] += 1
        root = canon(reached["formula"])
        fh = formula_hash(root)
        if fh in seen:
            continue
        seen.add(fh)
        records.append(profile_root(root, {
            "kind": "ONE_SWAP_REACHABLE_FIXPOINT",
            "frontier_ordinal": int(ordinal),
            "phase": phase,
            "source_clause": list(source),
            "replacement_clause": list(replacement),
            "mutated_original_hash": formula_hash(mutated),
        }))

    metrics["unique_reachable_fixpoints_profiled"] = len(records)
    metrics["covered_roots"] = sum(1 for r in records if r["covered"])
    metrics["controller_obstruction_roots"] = sum(1 for r in records if not r["covered"])
    metrics["total_candidate_probes"] = sum(int(r["candidate_probe_count"]) for r in records)
    metrics["total_selected_steps"] = sum(int(r["selected_step_count"]) for r in records)

    regression = next((r for r in records if r["root_hash"] == R47X_ROOT_HASH), None)
    if regression is None:
        raise AssertionError("R48E_R47X_REGRESSION_ROOT_NOT_FOUND")
    if not regression["covered"]:
        raise AssertionError("R48E_R47X_REGRESSION_BECAME_OBSTRUCTION")
    if regression["A_run"] != R47X_EXPECTED_A_RUN:
        raise AssertionError(("R48E_R47X_A_RUN_DRIFT", regression["A_run"]))
    if regression["max_state_a_star"] != R47X_EXPECTED_MAX_A_STAR:
        raise AssertionError(("R48E_R47X_A_STAR_DRIFT", regression["max_state_a_star"]))
    if regression["selected_pivots"] != R47X_EXPECTED_PIVOTS:
        raise AssertionError(("R48E_R47X_PIVOTS_DRIFT", regression["selected_pivots"]))

    covered = [r for r in records if r["covered"]]
    obstructed = [r for r in records if not r["covered"]]
    histogram = Counter(str(int(r["A_run"])) for r in covered)
    hardest = None
    if covered:
        hardest = max(covered, key=lambda r: (
            int(r["A_run"]),
            int(r["max_state_a_star"]),
            int(r["candidate_probe_count"]),
            tuple(r["root_CLV"]),
            r["root_hash"],
        ))
    max_A = max([int(r["A_run"]) for r in covered], default=None)
    max_a_star = max([int(r["max_state_a_star"]) for r in covered], default=None)
    max_persisted_C = max([int(r["max_observed_persisted_clauses"]) for r in covered], default=None)
    max_persisted_L = max([int(r["max_observed_persisted_literals"]) for r in covered], default=None)

    verdict = (
        "EXPLICIT_REACHABLE_STATE_WITH_NO_CERTIFIED_VARIABLE_DECREASING_R47M_CANDIDATE_FOUND"
        if obstructed else
        "FULL_FROZEN_FRONTIER_PROFILED_UNDER_LOCAL_AMORTIZED_PRESSURE__FINITE_ONLY"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "frozen_frontier": {
            "center_original_hash": r47x.CENTER_ORIGINAL_HASH,
            "ordinal_window": [1,MAX_ORDINAL],
            "center_control_included": True,
            "deduplicate_by_reachable_fixpoint_hash": True,
        },
        "R47X_regression": {
            "root_hash": R47X_ROOT_HASH,
            "A_run": regression["A_run"],
            "max_state_a_star": regression["max_state_a_star"],
            "selected_pivots": regression["selected_pivots"],
            "pass": True,
        },
        "metrics": metrics,
        "profile_summary": {
            "A_run_histogram": dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
            "maximum_observed_A_run": max_A,
            "maximum_observed_state_a_star": max_a_star,
            "maximum_observed_persisted_clauses": max_persisted_C,
            "maximum_observed_persisted_literals": max_persisted_L,
        },
        "hardest_covered_root": hardest,
        "first_controller_obstruction": None if not obstructed else obstructed[0],
        "roots": records,
        "interpretation": {
            "finite_frontier_only": True,
            "finite_max_A_run_proves_universal_polynomial_a": False,
            "finite_full_frontier_coverage_proves_O4": False,
            "no_sequence_enumeration": True,
            "no_predeclared_persistent_clause_cap": True,
            "next_if_covered": "R48F_INPUT_SIZE_OR_STRUCTURED_AFFINE_EVASIVE_LADDER_FOR_A_run_AND_a_star_GROWTH",
            "next_if_obstruction": "SEAL_EXACT_STATE_AND_CLASSIFY_MISSING_PROOF_AUTHORITY_BEFORE_NEW_RULE",
        },
        "firewall": {
            "UNIVERSAL_POLYNOMIAL_a_EXISTS": "NOT_PROVED",
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    d = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    h = d["hardest_covered_root"]
    o = d["first_controller_obstruction"]
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "R47X_regression": d["R47X_regression"],
        "metrics": d["metrics"],
        "profile_summary": d["profile_summary"],
        "hardest_covered_root": None if h is None else {
            "root_hash": h["root_hash"],
            "root_CLV": h["root_CLV"],
            "A_run": h["A_run"],
            "max_state_a_star": h["max_state_a_star"],
            "candidate_probe_count": h["candidate_probe_count"],
            "selected_pivots": h["selected_pivots"],
            "provenance": h["provenance"],
        },
        "first_controller_obstruction": None if o is None else {
            "root_hash": o["root_hash"],
            "root_CLV": o["root_CLV"],
            "provenance": o["provenance"],
            "obstruction": o["obstruction"],
        },
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
