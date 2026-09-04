from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47x_cap_projection_coverage_one_swap_falsifier as r47x

GATE = "JANUS_TRUMP_R47Z_R47X_MINIMUM_ADDITIVE_ENVELOPE_SLACK_RESCUE"
SOURCE = (-9, 11, -20)
REPLACEMENT = (-9, -11, -20)
MUTATED_HASH = "db4aeb56dd23ae20c82470ec9cc7cdfbe2e5234b2f87212fac24e703e9469020"
ROOT_HASH = "ed330049538dc3fb487019c71bb49bde65494dc88453e50bed73b49d4ee17ca6"
ROOT_CLV = (75, 199, 22)
R47X_OBSTRUCTION_HASH = "a4f361a15ba24f9be4db6bf9ab31c0718f776981646d84938359b49b5ec532d2"
R47X_OBSTRUCTION_CLV = (75, 202, 21)
C0 = 75
V0 = 22
MAX_DELTA = V0


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def formula_hash(formula):
    return r47f.formula_hash(r33.canonical_formula(formula))


def load_target_root():
    center_original, _, _ = r47x.load_center_original()
    mutated = r47i.mutate_one_clause(center_original, SOURCE, REPLACEMENT)
    if mutated is None:
        raise AssertionError("R47Z_TARGET_MUTATION_COLLAPSED_TO_DUPLICATE")
    r47x.validate_exact_3cnf(mutated)
    if formula_hash(mutated) != MUTATED_HASH:
        raise AssertionError(("R47Z_MUTATED_HASH_DRIFT", formula_hash(mutated), MUTATED_HASH))
    reached = r47f.reachable_fixpoint(mutated)
    if reached is None:
        raise AssertionError("R47Z_TARGET_NO_LONGER_REACHES_FIXPOINT")
    root = r33.canonical_formula(reached["formula"])
    if formula_hash(root) != ROOT_HASH:
        raise AssertionError(("R47Z_ROOT_HASH_DRIFT", formula_hash(root), ROOT_HASH))
    if clv(root) != ROOT_CLV:
        raise AssertionError(("R47Z_ROOT_CLV_DRIFT", clv(root), ROOT_CLV))
    return mutated, reached, root


def compact_candidate(current, candidate, B, Vroot, accepted, replay_pass=None):
    current_clv = clv(current)
    forced = tuple(candidate["DP"]["measure_after_forced_DP"])
    final_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
    final_clv = clv(final_formula)
    terminal = candidate["normalization"]["terminal"]
    envelope_slack = B - current_clv[0]
    exact_dp_gain = current_clv[0] - forced[0]
    return {
        "var": int(candidate["var"]),
        "input_CLV": list(current_clv),
        "envelope_B": int(B),
        "envelope_slack_before": int(envelope_slack),
        "forced_DP_CLV": list(forced),
        "forced_DP_clause_overflow": int(max(0, forced[0] - B)),
        "exact_DP_clause_gain_g": int(exact_dp_gain),
        "R47Y_slack_safe_pretest": bool(exact_dp_gain >= -envelope_slack),
        "final_hash": formula_hash(final_formula),
        "final_CLV": list(final_clv),
        "final_clause_overflow": int(max(0, final_clv[0] - B)),
        "normalization_clause_repayment": int(forced[0] - final_clv[0]),
        "terminal": terminal,
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "envelope_accepted": bool(accepted),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "full_R47M_independent_replay_pass": replay_pass,
        "selected_pivot_absent_after": bool(int(candidate["var"]) not in set(r33.variables(final_formula))),
        "final_variables_subset_root": bool(set(r33.variables(final_formula)).issubset(set(r33.variables(current)))),
        "normalization_segment_count": int(candidate["normalization"]["segment_count"]),
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
    }


def run_envelope_chain(root, B):
    root = r33.canonical_formula(root)
    root_vars = set(r33.variables(root))
    literal_envelope = B * V0
    current = root
    selected_full = []
    selected_rows = []
    probes = 0
    rejected = 0

    while True:
        current_clv = clv(current)
        if current_clv[0] > B:
            raise AssertionError(("R47Z_PERSISTED_STATE_EXCEEDS_B", current_clv, B))
        if current_clv[1] > literal_envelope:
            raise AssertionError(("R47Z_PERSISTED_STATE_EXCEEDS_LITERAL_ENVELOPE", current_clv, literal_envelope))
        if not set(r33.variables(current)).issubset(root_vars):
            raise AssertionError("R47Z_FRESH_VARIABLE_IN_PERSISTED_STATE")

        selected = None
        selected_replay = None
        selected_row = None
        rejected_here = []
        for var in r33.variables(current):
            probes += 1
            if probes > V0 * V0:
                raise AssertionError(("R47Z_PROBE_CAP_EXCEEDED", probes))
            candidate = r47m.macro_candidate_full_closure(current, int(var))
            if candidate is None:
                rejected += 1
                rejected_here.append({
                    "var": int(var),
                    "candidate": False,
                    "envelope_accepted": False,
                })
                continue
            if not candidate["DP_independent_replay_pass"]:
                raise AssertionError(("R47Z_DP_REPLAY_FAIL", var))
            if not candidate["polynomial_intermediate_envelope_pass"]:
                raise AssertionError(("R47Z_POLYNOMIAL_ENVELOPE_FAIL", var))

            final_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
            final_clv = clv(final_formula)
            terminal = candidate["normalization"]["terminal"] is not None
            accepted = terminal or (
                final_clv[0] <= B
                and final_clv[2] < current_clv[2]
                and set(r33.variables(final_formula)).issubset(root_vars)
            )
            if accepted:
                replay = r47m.independent_replay(current, candidate)
                if not replay["pass"]:
                    raise AssertionError(("R47Z_SELECTED_FULL_REPLAY_FAIL", var, replay))
                row = compact_candidate(current, candidate, B, V0, True, True)
                if not terminal:
                    if row["final_CLV"][0] > B:
                        raise AssertionError(("R47Z_SELECTED_CLAUSE_ENVELOPE_FAIL", row))
                    if row["final_CLV"][1] > literal_envelope:
                        raise AssertionError(("R47Z_SELECTED_LITERAL_ENVELOPE_FAIL", row))
                    if row["final_CLV"][2] >= current_clv[2]:
                        raise AssertionError(("R47Z_SELECTED_VARIABLE_RANK_FAIL", row))
                    if not row["selected_pivot_absent_after"]:
                        raise AssertionError(("R47Z_SELECTED_PIVOT_SURVIVED", row))
                selected = candidate
                selected_replay = replay
                selected_row = row
                break

            rejected += 1
            rejected_here.append(compact_candidate(current, candidate, B, V0, False, None))

        if selected is None:
            best = None
            rich = [r for r in rejected_here if r.get("candidate", True)]
            if rich:
                best = min(
                    rich,
                    key=lambda r: (
                        r["final_clause_overflow"],
                        r["final_CLV"][0],
                        r["final_CLV"][1],
                        r["var"],
                    ),
                )
            return {
                "covered": False,
                "B": int(B),
                "delta": int(B - C0),
                "selected_steps": selected_rows,
                "candidate_probe_count": probes,
                "rejected_probe_count": rejected,
                "obstruction": {
                    "state_hash": formula_hash(current),
                    "state_CLV": list(current_clv),
                    "state_formula": [list(c) for c in current],
                    "candidate_count": len(rejected_here),
                    "candidate_receipts": rejected_here,
                    "best_rejected": best,
                },
            }

        final_formula = r33.canonical_formula(selected["normalization"]["final_formula"])
        selected_rows.append({
            "step": len(selected_rows) + 1,
            "rejected_before_selection": len(rejected_here),
            **selected_row,
        })
        selected_full.append((current, selected, selected_replay))

        terminal = selected["normalization"]["terminal"]
        semantic_sat = selected["normalization"]["semantic_sat"]
        if terminal is not None:
            sat_reconstruction = {"applicable": False, "pass": True}
            if semantic_sat is True:
                assignment = dict(selected["normalization"]["terminal_assignment"] or {})
                for before_formula, cand, _ in reversed(selected_full):
                    assignment = r47x.lift_assignment(before_formula, cand, assignment)
                for v in sorted(root_vars - set(assignment)):
                    assignment[v] = False
                if not r33.eval_formula(root, assignment):
                    raise AssertionError("R47Z_ROOT_SAT_RECONSTRUCTION_FAIL")
                sat_reconstruction = {
                    "applicable": True,
                    "pass": True,
                    "assignment": {str(k): bool(v) for k, v in sorted(assignment.items())},
                }
            return {
                "covered": True,
                "B": int(B),
                "delta": int(B - C0),
                "selected_steps": selected_rows,
                "candidate_probe_count": probes,
                "rejected_probe_count": rejected,
                "terminal": {
                    "kind": terminal,
                    "semantic_sat": semantic_sat,
                    "final_hash": formula_hash(final_formula),
                    "final_CLV": list(clv(final_formula)),
                },
                "SAT_root_reconstruction": sat_reconstruction,
                "obstruction": None,
            }

        if len(selected_rows) > V0:
            raise AssertionError(("R47Z_STEP_CAP_EXCEEDED", len(selected_rows)))
        current = final_formula


def compact_delta(row):
    out = {
        "delta": row["delta"],
        "B": row["B"],
        "covered": row["covered"],
        "selected_pivots": [int(s["var"]) for s in row["selected_steps"]],
        "selected_step_count": len(row["selected_steps"]),
        "candidate_probe_count": row["candidate_probe_count"],
        "rejected_probe_count": row["rejected_probe_count"],
    }
    if row["covered"]:
        out["terminal"] = row["terminal"]
    else:
        out["obstruction"] = {
            "state_hash": row["obstruction"]["state_hash"],
            "state_CLV": row["obstruction"]["state_CLV"],
            "candidate_count": row["obstruction"]["candidate_count"],
            "best_rejected": row["obstruction"]["best_rejected"],
        }
    return out


def run():
    mutated, reached, root = load_target_root()
    ladder = []
    minimum = None
    full_minimum = None

    for delta in range(MAX_DELTA + 1):
        B = C0 + delta
        result = run_envelope_chain(root, B)
        compact = compact_delta(result)
        ladder.append(compact)

        if delta == 0:
            if result["covered"]:
                raise AssertionError("R47Z_DELTA0_DID_NOT_REPRODUCE_R47X_FAILURE")
            if [int(s["var"]) for s in result["selected_steps"]] != [7]:
                raise AssertionError(("R47Z_DELTA0_SELECTED_PATH_DRIFT", result["selected_steps"]))
            if result["obstruction"]["state_hash"] != R47X_OBSTRUCTION_HASH:
                raise AssertionError(("R47Z_DELTA0_OBSTRUCTION_HASH_DRIFT", result["obstruction"]["state_hash"]))
            if tuple(result["obstruction"]["state_CLV"]) != R47X_OBSTRUCTION_CLV:
                raise AssertionError(("R47Z_DELTA0_OBSTRUCTION_CLV_DRIFT", result["obstruction"]["state_CLV"]))

        if result["covered"]:
            minimum = int(delta)
            full_minimum = result
            break

    verdict = (
        "MINIMUM_ADDITIVE_ENVELOPE_SLACK_RESCUE_FOUND"
        if minimum is not None
        else "NO_RESCUE_FOR_DELTA_LE_V0__FINITE_LOWER_BOUND_ONLY"
    )

    return {
        "gate": GATE,
        "verdict": verdict,
        "sealed_target": {
            "mutated_original_hash": MUTATED_HASH,
            "root_hash": ROOT_HASH,
            "root_CLV": list(ROOT_CLV),
            "C0": C0,
            "V0": V0,
            "R47X_obstruction_hash": R47X_OBSTRUCTION_HASH,
            "R47X_obstruction_CLV": list(R47X_OBSTRUCTION_CLV),
        },
        "delta_ladder": ladder,
        "minimum_delta": minimum,
        "minimum_envelope_B": None if minimum is None else C0 + minimum,
        "minimum_rescue_full": full_minimum,
        "interpretation": {
            "fixed_root_cap_C0_universal": False,
            "finite_minimum_delta_proves_universal_polynomial_envelope": False,
            "sequence_enumeration_used": False,
            "theorem_safe_reason": "B=C0+delta is fixed before each run, delta<=V0, so persisted states and one-step exact-DP probes remain polynomially bounded for this finite ladder.",
        },
        "firewall": {
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
    result = run()
    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "sealed_target": result["sealed_target"],
        "delta_ladder": result["delta_ladder"],
        "minimum_delta": result["minimum_delta"],
        "minimum_envelope_B": result["minimum_envelope_B"],
        "minimum_rescue": None if result["minimum_rescue_full"] is None else {
            "selected_pivots": [int(s["var"]) for s in result["minimum_rescue_full"]["selected_steps"]],
            "selected_steps": result["minimum_rescue_full"]["selected_steps"],
            "candidate_probe_count": result["minimum_rescue_full"]["candidate_probe_count"],
            "terminal": result["minimum_rescue_full"]["terminal"],
            "SAT_root_reconstruction_pass": result["minimum_rescue_full"]["SAT_root_reconstruction"]["pass"],
        },
        "firewall": result["firewall"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
