from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m

GATE = "JANUS_TRUMP_R47V_R47N_FIRST_CAP_PRESERVING_PROJECTION_CHAIN"
ROOT_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
ROOT_CLV = (76, 203, 22)
C0 = 76
V0 = 22
LITERAL_CAP = C0 * V0
MAX_NONTERMINAL_SELECTED_STEPS = 22
MAX_CANDIDATE_PROBES = V0 * V0

# Exact sealed R47N reachable residual.  The first executable check below binds
# this literal payload to the frozen hash and CLV before it can be used.
ROOT_FORMULA = [
    (-25, -29),
    (-25, -27),
    (-24, -27),
    (-23, -25),
    (-20, -26),
    (-14, -18, -23),
    (-13, -16, 24),
    (-13, 18, -23),
    (-13, 25, 29),
    (-12, -13, 30),
    (-12, 20, -30),
    (-11, -27),
    (-10, -24, -29),
    (-10, -16, -23),
    (-9, -24, -29),
    (-9, -18, 30),
    (-9, 10),
    (-9, 11),
    (-8, 14, -29),
    (-7, -10, -26),
    (-5, -7, -12),
    (-5, 15, 16),
    (-4, -9, 25),
    (-4, -5, -15),
    (-4, -5, 23),
    (-4, 8, -10),
    (-2, -8, 29),
    (-2, 4, 13),
    (-2, 7, -30),
    (2, -27),
    (2, -16, -30),
    (2, 9, -29),
    (2, 10),
    (4, -27),
    (4, -8, 15),
    (4, 10),
    (4, 12, 15),
    (4, 12, 20),
    (4, 15, -26),
    (4, 15, 16),
    (4, 15, 25),
    (4, 15, 30),
    (4, 20, -30),
    (5, -14, -23),
    (5, -11, -26),
    (5, -8, 25),
    (5, 7),
    (5, 18, -24),
    (5, 20, -30),
    (7, -14),
    (8, 18, 23),
    (9, -20, -24),
    (9, 15, -18),
    (10, -15, 27),
    (10, -13, -14),
    (10, 12, -15),
    (10, 14, -16, 27),
    (10, 23, 27),
    (10, 27, 29),
    (11, -30),
    (11, -24),
    (11, -23),
    (11, 16),
    (11, 27),
    (12, -27),
    (13, -15, 26),
    (14, 20, -30),
    (15, -27),
    (15, 24, 30),
    (16, -27),
    (16, -26),
    (16, 20),
    (18, -24, -26),
    (20, -25),
    (24, -25),
    (24, 26, 29),
]


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def formula_hash(formula):
    return r42.formula_hash(r33.canonical_formula(formula))


def load_sealed_root():
    root = r33.canonical_formula(ROOT_FORMULA)
    got_hash = formula_hash(root)
    got_clv = clv(root)
    if got_hash != ROOT_HASH:
        raise AssertionError(("R47V_ROOT_HASH_DRIFT", got_hash, ROOT_HASH))
    if got_clv != ROOT_CLV:
        raise AssertionError(("R47V_ROOT_CLV_DRIFT", got_clv, ROOT_CLV))
    return root


def lift_assignment_through_selected_step(before_formula, candidate, assignment):
    assignment = dict(assignment)
    normalization = candidate["normalization"]
    for event in reversed(normalization["reconstruction_events"]):
        if event["kind"] == "R33":
            assignment = r33.reconstruct_model(event["result"], assignment)
        elif event["kind"] == "SA_BVE":
            assignment = r42.reconstruct_sa_bve(event["record"], assignment)
        else:
            raise AssertionError(("R47V_UNKNOWN_RECONSTRUCTION_EVENT", event["kind"]))
    assignment = r42.reconstruct_sa_bve(candidate["DP"], assignment)
    for v in sorted(set(r33.variables(before_formula)) - set(assignment)):
        assignment[v] = False
    if not r33.eval_formula(r33.canonical_formula(before_formula), assignment):
        raise AssertionError(("R47V_STEP_MODEL_RECONSTRUCTION_FAIL", candidate["var"]))
    return assignment


def compact_probe(current, candidate, cap_accepted, replay=None):
    final_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
    final_clv = clv(final_formula)
    current_vars = set(r33.variables(current))
    final_vars = set(r33.variables(final_formula))
    root_vars = set(r33.variables(load_sealed_root()))
    return {
        "var": int(candidate["var"]),
        "input_hash": formula_hash(current),
        "input_CLV": list(clv(current)),
        "forced_DP_CLV": list(candidate["DP"]["measure_after_forced_DP"]),
        "final_hash": formula_hash(final_formula),
        "final_CLV": list(final_clv),
        "terminal": candidate["normalization"]["terminal"],
        "semantic_sat": candidate["normalization"]["semantic_sat"],
        "producer_net_CLV_descent": bool(candidate["net_CLV_descent"]),
        "cap_accepted": bool(cap_accepted),
        "clause_cap_pass": bool(final_clv[0] <= C0),
        "literal_cap_pass": bool(final_clv[1] <= LITERAL_CAP),
        "variable_rank_strict": bool(final_clv[2] < clv(current)[2]),
        "variables_subset_root": bool(final_vars.issubset(root_vars)),
        "selected_pivot_absent_after": bool(int(candidate["var"]) not in final_vars),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "normalization_segment_count": int(candidate["normalization"]["segment_count"]),
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
        "full_R47M_independent_replay_pass": replay["pass"] if replay is not None else None,
        "current_variable_count": len(current_vars),
        "final_variable_count": len(final_vars),
    }


def run():
    root = load_sealed_root()
    root_vars = set(r33.variables(root))
    current = root
    selected_full = []
    selected_rows = []
    probe_count = 0
    rejected_probe_count = 0
    max_normalized = list(clv(root))
    max_forced = [0, 0, 0]
    obstruction = None
    terminal = None
    semantic_sat = None
    terminal_verification = None

    while True:
        current_clv = clv(current)
        if current_clv[0] > C0 or current_clv[1] > LITERAL_CAP:
            raise AssertionError(("R47V_CURRENT_STATE_OUTSIDE_CAP", current_clv))
        if not set(r33.variables(current)).issubset(root_vars):
            raise AssertionError("R47V_FRESH_VARIABLE_APPEARED")

        selected = None
        selected_replay = None
        selected_probe_row = None
        rejected_rows = []

        for v in r33.variables(current):
            probe_count += 1
            if probe_count > MAX_CANDIDATE_PROBES:
                raise AssertionError(("R47V_CANDIDATE_PROBE_CAP_EXCEEDED", probe_count))

            candidate = r47m.macro_candidate_full_closure(current, int(v))
            if candidate is None:
                rejected_probe_count += 1
                rejected_rows.append({
                    "var": int(v),
                    "producer_returned_none": True,
                    "cap_accepted": False,
                })
                continue

            forced_clv = list(candidate["DP"]["measure_after_forced_DP"])
            max_forced = [max(max_forced[i], int(forced_clv[i])) for i in range(3)]
            final_formula = r33.canonical_formula(candidate["normalization"]["final_formula"])
            final_clv = clv(final_formula)
            final_vars = set(r33.variables(final_formula))
            terminal_here = candidate["normalization"]["terminal"] is not None
            cap_accepted = terminal_here or (
                final_clv[0] <= C0
                and final_clv[2] < current_clv[2]
                and final_vars.issubset(root_vars)
            )

            if cap_accepted:
                replay = r47m.independent_replay(current, candidate)
                if not replay["pass"]:
                    raise AssertionError(("R47V_SELECTED_FULL_R47M_REPLAY_FAIL", v, replay))
                row = compact_probe(current, candidate, True, replay)
                if not row["DP_independent_replay_pass"]:
                    raise AssertionError(("R47V_SELECTED_DP_REPLAY_FAIL", v))
                if not row["polynomial_intermediate_envelope_pass"]:
                    raise AssertionError(("R47V_SELECTED_POLYNOMIAL_ENVELOPE_FAIL", v))
                if not terminal_here:
                    if not row["clause_cap_pass"] or not row["literal_cap_pass"]:
                        raise AssertionError(("R47V_SELECTED_CAP_FAIL", v, row))
                    if not row["variable_rank_strict"] or not row["variables_subset_root"]:
                        raise AssertionError(("R47V_SELECTED_RANK_OR_VARIABLE_SET_FAIL", v, row))
                    if not row["selected_pivot_absent_after"]:
                        raise AssertionError(("R47V_SELECTED_PIVOT_SURVIVED", v, row))
                selected = candidate
                selected_replay = replay
                selected_probe_row = row
                break

            rejected_probe_count += 1
            rejected_rows.append(compact_probe(current, candidate, False, None))

        if selected is None:
            obstruction = {
                "state_hash": formula_hash(current),
                "state_CLV": list(current_clv),
                "state_formula": [list(c) for c in current],
                "candidate_receipts": rejected_rows,
                "candidate_count": len(rejected_rows),
            }
            break

        final_formula = r33.canonical_formula(selected["normalization"]["final_formula"])
        final_clv = clv(final_formula)
        max_normalized = [max(max_normalized[i], int(final_clv[i])) for i in range(3)]
        selected_rows.append({
            "step": len(selected_rows) + 1,
            "rejected_before_selection": len(rejected_rows),
            **selected_probe_row,
        })
        selected_full.append((current, selected, selected_replay))

        terminal = selected["normalization"]["terminal"]
        semantic_sat = selected["normalization"]["semantic_sat"]
        terminal_verification = selected["normalization"]["terminal_verification"]
        if terminal is not None:
            current = final_formula
            break

        if len(selected_rows) > MAX_NONTERMINAL_SELECTED_STEPS:
            raise AssertionError(("R47V_SELECTED_STEP_CAP_EXCEEDED", len(selected_rows)))
        current = final_formula

    sat_reconstruction = {"applicable": False, "pass": True}
    if terminal is not None and semantic_sat is True:
        assignment = dict(selected_full[-1][1]["normalization"]["terminal_assignment"] or {})
        for before_formula, candidate, _ in reversed(selected_full):
            assignment = lift_assignment_through_selected_step(before_formula, candidate, assignment)
        for v in sorted(root_vars - set(assignment)):
            assignment[v] = False
        sat_ok = r33.eval_formula(root, assignment)
        if not sat_ok:
            raise AssertionError("R47V_ROOT_SAT_RECONSTRUCTION_FAIL")
        sat_reconstruction = {
            "applicable": True,
            "pass": True,
            "assignment": {str(k): bool(v) for k, v in sorted(assignment.items())},
        }

    if obstruction is None:
        verdict = "R47N_REACHES_CERTIFIED_TERMINAL_UNDER_FIRST_CAP_PRESERVING_PROJECTION_CHAIN__FINITE_ONLY"
    else:
        verdict = "EXPLICIT_R47N_CHAIN_STATE_WITH_NO_CAP_PRESERVING_CERTIFIED_PIVOT_FOUND"

    result = {
        "gate": GATE,
        "verdict": verdict,
        "sealed_root": {
            "hash": ROOT_HASH,
            "CLV": list(ROOT_CLV),
            "C0": C0,
            "V0": V0,
            "literal_cap": LITERAL_CAP,
        },
        "policy": {
            "selection": "FIRST_CAP_PRESERVING_CERTIFIED_PIVOT",
            "candidate_producer": "R47M_EXACT_DP_PLUS_JOINT_EXISTING_R33_AFFINE_RUP_SA_BVE_CLOSURE",
            "sequence_enumeration": False,
        },
        "selected_steps": selected_rows,
        "metrics": {
            "selected_step_count": len(selected_rows),
            "candidate_probe_count": probe_count,
            "rejected_probe_count": rejected_probe_count,
            "maximum_normalized_CLV_coordinatewise": max_normalized,
            "maximum_forced_DP_CLV_coordinatewise": max_forced,
            "selected_step_cap": MAX_NONTERMINAL_SELECTED_STEPS,
            "candidate_probe_cap": MAX_CANDIDATE_PROBES,
        },
        "terminal": {
            "kind": terminal,
            "semantic_sat": semantic_sat,
            "verification": terminal_verification,
            "final_hash": formula_hash(current),
            "final_CLV": list(clv(current)),
        } if obstruction is None else None,
        "SAT_root_reconstruction": sat_reconstruction,
        "obstruction": obstruction,
        "interpretation": {
            "finite_success_proves_universal_cap_projection_coverage": False,
            "explicit_obstruction_if_present_refutes_this_frozen_first_cap_preserving_policy_on_the_reached_state": True,
            "fixed_macro_depth_required": False,
            "unbounded_uncapped_DP_authorized": False,
        },
        "firewall": {
            "CAP_PROJECTION_COVERAGE": "OPEN",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
