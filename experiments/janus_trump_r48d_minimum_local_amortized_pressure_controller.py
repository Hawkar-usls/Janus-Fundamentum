from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x
import janus_trump_r47z_r47x_minimum_additive_envelope_slack_rescue as r47z

GATE = "JANUS_TRUMP_R48D_MINIMUM_LOCAL_AMORTIZED_PRESSURE_CONTROLLER"
ROOT_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
ROOT_CLV = (75, 199, 22)
C0 = 75
V0 = 22
MAX_STEPS = V0
MAX_PROBES = V0 * V0


def canon(formula):
    return r33.canonical_formula(formula)


def clv(formula):
    return r33.measure(canon(formula))


def formula_hash(formula):
    return r47f.formula_hash(canon(formula))


def pressure_req(current_formula, final_formula):
    before = clv(current_formula)
    after = clv(final_formula)
    d_c = int(after[0] - before[0])
    d_v = int(before[2] - after[2])
    if d_v <= 0:
        return None
    num = max(0, d_c)
    return int((num + d_v - 1) // d_v)


def candidate_row(current, candidate, selected_replay_pass=None):
    current = canon(current)
    final_formula = canon(candidate["normalization"]["final_formula"])
    before = clv(current)
    after = clv(final_formula)
    terminal = candidate["normalization"]["terminal"]
    current_vars = set(r33.variables(current))
    final_vars = set(r33.variables(final_formula))
    no_fresh = final_vars.issubset(current_vars)
    d_v = int(before[2] - after[2])
    pressure = 0 if terminal is not None else pressure_req(current, final_formula)
    eligible = terminal is not None or (d_v > 0 and no_fresh and pressure is not None)
    return {
        "var": int(candidate["var"]),
        "input_hash": formula_hash(current),
        "input_CLV": list(before),
        "forced_DP_CLV": list(candidate["DP"]["measure_after_forced_DP"]),
        "final_hash": formula_hash(final_formula),
        "final_CLV": list(after),
        "terminal": terminal,
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "delta_C": int(after[0] - before[0]),
        "delta_V_eliminated": d_v,
        "a_req": pressure,
        "no_fresh_variables": bool(no_fresh),
        "selected_pivot_absent_after": bool(int(candidate["var"]) not in final_vars),
        "eligible": bool(eligible),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "full_R47M_independent_replay_pass": selected_replay_pass,
        "normalization_segment_count": int(candidate["normalization"]["segment_count"]),
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
    }


def selection_key(row):
    # Frozen order: terminal first; otherwise minimum local pressure, then final CLV, then pivot id.
    terminal_rank = 0 if row["terminal"] is not None else 1
    pressure = 0 if row["a_req"] is None else int(row["a_req"])
    f = row["final_CLV"]
    return (terminal_rank, pressure, int(f[0]), int(f[1]), int(f[2]), int(row["var"]))


def run_controller(root):
    root = canon(root)
    root_vars = set(r33.variables(root))
    current = root
    selected_full = []
    selected_steps = []
    state_profiles = []
    total_probes = 0

    while True:
        current = canon(current)
        before = clv(current)
        if not set(r33.variables(current)).issubset(root_vars):
            raise AssertionError("R48D_FRESH_VARIABLE_IN_PERSISTED_STATE")
        if len(selected_steps) > MAX_STEPS:
            raise AssertionError(("R48D_STEP_CAP_EXCEEDED", len(selected_steps)))

        rows = []
        candidates = {}
        for var in r33.variables(current):
            total_probes += 1
            if total_probes > MAX_PROBES:
                raise AssertionError(("R48D_PROBE_CAP_EXCEEDED", total_probes))
            candidate = r47m.macro_candidate_full_closure(current, int(var))
            if candidate is None:
                rows.append({
                    "var": int(var),
                    "candidate": False,
                    "eligible": False,
                    "terminal": None,
                    "a_req": None,
                })
                continue
            if not candidate["DP_independent_replay_pass"]:
                raise AssertionError(("R48D_DP_REPLAY_FAIL", var))
            if not candidate["polynomial_intermediate_envelope_pass"]:
                raise AssertionError(("R48D_POLY_INTERMEDIATE_FAIL", var))
            row = candidate_row(current, candidate, None)
            rows.append(row)
            candidates[int(var)] = candidate

        eligible = [r for r in rows if r.get("eligible", False)]
        if not eligible:
            return {
                "covered": False,
                "candidate_probe_count": int(total_probes),
                "selected_steps": selected_steps,
                "state_profiles": state_profiles,
                "obstruction": {
                    "state_hash": formula_hash(current),
                    "state_CLV": list(before),
                    "state_formula": [list(c) for c in current],
                    "candidate_rows": rows,
                },
            }

        chosen_row = min(eligible, key=selection_key)
        chosen = candidates[int(chosen_row["var"])]
        replay = r47m.independent_replay(current, chosen)
        if not replay["pass"]:
            raise AssertionError(("R48D_SELECTED_FULL_REPLAY_FAIL", chosen_row["var"], replay))
        chosen_row = candidate_row(current, chosen, True)
        final_formula = canon(chosen["normalization"]["final_formula"])

        if chosen_row["terminal"] is None:
            if chosen_row["delta_V_eliminated"] <= 0:
                raise AssertionError(("R48D_NONTERMINAL_NO_VARIABLE_DROP", chosen_row))
            if not chosen_row["no_fresh_variables"]:
                raise AssertionError(("R48D_NONTERMINAL_FRESH_VARIABLE", chosen_row))
            if not chosen_row["selected_pivot_absent_after"]:
                raise AssertionError(("R48D_SELECTED_PIVOT_SURVIVED", chosen_row))

        finite_pressures = [int(r["a_req"]) for r in eligible if r["terminal"] is None and r["a_req"] is not None]
        state_a_star = 0 if any(r["terminal"] is not None for r in eligible) else min(finite_pressures)
        state_profiles.append({
            "state_index": len(state_profiles),
            "state_hash": formula_hash(current),
            "state_CLV": list(before),
            "candidate_count": len(rows),
            "eligible_count": len(eligible),
            "terminal_candidate_count": sum(1 for r in eligible if r["terminal"] is not None),
            "a_star": int(state_a_star),
            "selected_var": int(chosen_row["var"]),
            "selected_a_req": int(chosen_row["a_req"] or 0),
            "selected_terminal": chosen_row["terminal"],
            "candidate_rows": rows,
        })
        selected_steps.append({
            "step": len(selected_steps) + 1,
            **chosen_row,
        })
        selected_full.append((current, chosen))

        if chosen_row["terminal"] is not None:
            sat_reconstruction = {"applicable": False, "pass": True}
            if chosen_row["semantic_sat"] is True:
                assignment = dict(chosen["normalization"]["terminal_assignment"] or {})
                for before_formula, cand in reversed(selected_full):
                    assignment = r47x.lift_assignment(before_formula, cand, assignment)
                for v in sorted(root_vars - set(assignment)):
                    assignment[v] = False
                if not r33.eval_formula(root, assignment):
                    raise AssertionError("R48D_ROOT_SAT_RECONSTRUCTION_FAIL")
                sat_reconstruction = {
                    "applicable": True,
                    "pass": True,
                    "assignment": {str(k): bool(v) for k, v in sorted(assignment.items())},
                }
            return {
                "covered": True,
                "candidate_probe_count": int(total_probes),
                "selected_steps": selected_steps,
                "state_profiles": state_profiles,
                "terminal": {
                    "kind": chosen_row["terminal"],
                    "semantic_sat": chosen_row["semantic_sat"],
                    "final_hash": formula_hash(final_formula),
                    "final_CLV": list(clv(final_formula)),
                },
                "SAT_root_reconstruction": sat_reconstruction,
                "obstruction": None,
            }

        if len(selected_steps) >= MAX_STEPS:
            raise AssertionError(("R48D_SELECTED_NONTERMINAL_STEP_BOUND_EXHAUSTED", len(selected_steps), clv(final_formula)))
        current = final_formula


def posthoc_amortization(root, run):
    root = canon(root)
    nonterminal = [s for s in run["selected_steps"] if s["terminal"] is None]
    A_run = max([int(s["a_req"]) for s in nonterminal], default=0)
    identities = []
    max_persisted_clauses = int(clv(root)[0])
    max_persisted_literals = int(clv(root)[1])
    for s in run["selected_steps"]:
        max_persisted_clauses = max(max_persisted_clauses, int(s["final_CLV"][0]))
        max_persisted_literals = max(max_persisted_literals, int(s["final_CLV"][1]))
        if s["terminal"] is not None:
            continue
        c0, _, v0 = s["input_CLV"]
        c1, _, v1 = s["final_CLV"]
        lhs = int(c1 + A_run * v1)
        rhs = int(c0 + A_run * v0)
        identities.append({
            "step": int(s["step"]),
            "var": int(s["var"]),
            "a_req": int(s["a_req"]),
            "lhs_C_next_plus_A_V_next": lhs,
            "rhs_C_plus_A_V": rhs,
            "pass": lhs <= rhs,
        })
        if lhs > rhs:
            raise AssertionError(("R48D_POSTHOC_WEIGHTED_IDENTITY_FAIL", s, A_run, lhs, rhs))

    induced_clause_bound = int(C0 + A_run * V0)
    if max_persisted_clauses > induced_clause_bound:
        raise AssertionError(("R48D_TELESCOPING_CLAUSE_BOUND_FAIL", max_persisted_clauses, induced_clause_bound))
    return {
        "A_run": int(A_run),
        "selected_nonterminal_pressure_sequence": [int(s["a_req"]) for s in nonterminal],
        "max_state_a_star": max([int(p["a_star"]) for p in run["state_profiles"]], default=0),
        "weighted_step_identities": identities,
        "all_weighted_step_identities_pass": all(x["pass"] for x in identities),
        "induced_persistent_clause_bound_C0_plus_A_run_V0": induced_clause_bound,
        "max_observed_persisted_clauses": int(max_persisted_clauses),
        "max_observed_persisted_literals": int(max_persisted_literals),
        "observed_clause_bound_pass": max_persisted_clauses <= induced_clause_bound,
    }


def run():
    _, _, root = r47z.load_target_root()
    if formula_hash(root) != ROOT_HASH or clv(root) != ROOT_CLV:
        raise AssertionError(("R48D_ROOT_DRIFT", formula_hash(root), clv(root)))
    result = run_controller(root)
    amort = posthoc_amortization(root, result)
    verdict = (
        "R47X_WITNESS_REACHES_CERTIFIED_TERMINAL_UNDER_MINIMUM_LOCAL_PRESSURE__FINITE_ONLY"
        if result["covered"] else
        "MINIMUM_LOCAL_PRESSURE_CONTROLLER_REACHES_NONTERMINAL_WITH_NO_CERTIFIED_VARIABLE_DECREASING_CANDIDATE"
    )
    return {
        "gate": GATE,
        "verdict": verdict,
        "sealed_target": {
            "root_hash": ROOT_HASH,
            "root_CLV": list(ROOT_CLV),
            "known_R47X_root_cap_failure": True,
            "known_R47Z_minimum_first_B_preserving_delta": 4,
        },
        "controller": {
            "selection": "TERMINAL_FIRST_THEN_MINIMUM_a_req_THEN_FINAL_CLV_THEN_PIVOT",
            "sequence_enumeration": False,
            "predeclared_persistent_clause_cap": False,
            "max_selected_nonterminal_steps": MAX_STEPS,
            "max_candidate_probes": MAX_PROBES,
        },
        "run": result,
        "posthoc_amortization": amort,
        "interpretation": {
            "finite_A_run_is_not_universal_polynomial_bound": True,
            "finite_success_does_not_prove_O4": True,
            "controller_uses_no_sequence_enumeration": True,
            "next_if_success": "RUN_SAME_CONTROLLER_ACROSS_FROZEN_R47X_FRONTIER_AND_MEASURE_MAX_A_run_AND_MAX_STATE_a_star",
            "next_if_failure": "SEAL_EXPLICIT_PROOF_AUTHORITY_OBSTRUCTION_INDEPENDENT_OF_FIXED_PERSISTENT_CAP",
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
    print(json.dumps({
        "gate": d["gate"],
        "verdict": d["verdict"],
        "covered": d["run"]["covered"],
        "candidate_probe_count": d["run"]["candidate_probe_count"],
        "selected_steps": [
            {"step":s["step"],"var":s["var"],"input_CLV":s["input_CLV"],"final_CLV":s["final_CLV"],"terminal":s["terminal"],"a_req":s["a_req"]}
            for s in d["run"]["selected_steps"]
        ],
        "terminal": d["run"].get("terminal"),
        "obstruction": d["run"].get("obstruction"),
        "posthoc_amortization": d["posthoc_amortization"],
        "firewall": d["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
