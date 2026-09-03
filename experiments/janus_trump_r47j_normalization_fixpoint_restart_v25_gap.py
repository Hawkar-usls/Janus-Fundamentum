from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a

RESULT_PATH = Path(__file__).resolve().parents[1] / "research" / "JANUS_TRUMP_R47I_EXPLICIT_REACHABLE_ONE_SWAP_MACRO_DEAD_COUNTEREXAMPLE_RESULT_2026-09-03.json"
EXPECTED_FIXPOINT_HASH = "c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"
EXPECTED_FIXPOINT_CLV = (63, 155, 20)


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def restart_height_bound(forced_formula):
    C, _, V = clv(forced_formula)
    return (C + 1) * (C * max(1, V) + 1) * (V + 1)


def load_counterexample():
    data = json.loads(RESULT_PATH.read_text())
    formula = r33.canonical_formula(data["genuine_residual_fixpoint"]["formula"])
    if r42.formula_hash(formula) != EXPECTED_FIXPOINT_HASH:
        raise AssertionError("R47J_FIXPOINT_HASH_DRIFT")
    if clv(formula) != EXPECTED_FIXPOINT_CLV:
        raise AssertionError("R47J_FIXPOINT_CLV_DRIFT")
    return data, formula


def normalize_to_certified_fixpoint(transformed_formula):
    forced = r33.canonical_formula(transformed_formula)
    state = forced
    height_bound = restart_height_bound(forced)
    rounds = []
    r33_reconstruction_results = []
    terminal = None
    semantic_sat: Optional[bool] = None
    terminal_assignment: Optional[Dict[int, bool]] = None
    terminal_verification = None
    total_ledger = {
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "GF2_estimated_bit_ops": 0,
        "restart_count": 0,
    }

    for round_index in range(height_bound + 1):
        before = state
        before_clv = clv(before)
        reduced = r33.simplify(before)
        after_r33 = r33.canonical_formula(reduced["final_formula"])
        after_r33_clv = clv(after_r33)
        if after_r33 != before and not after_r33_clv < before_clv:
            raise AssertionError(("R47J_R33_NOT_STRICT_DESCENT", round_index, before_clv, after_r33_clv))
        if reduced["history"]:
            r33_reconstruction_results.append(reduced)
        total_ledger["R33_check_operation_upper_ledger"] += int(reduced["total_check_operation_count_upper_ledger"])
        total_ledger["R33_certificate_bytes"] += int(reduced["total_certificate_bytes"])

        round_row = {
            "round": round_index,
            "before_CLV": list(before_clv),
            "R33_apps": int(reduced["total_rule_applications"]),
            "after_R33_CLV": list(after_r33_clv),
            "R33_terminal": reduced["terminal"],
        }

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("R47J_DECLARED_TERMINAL_VERIFY_FAIL", solved))
            terminal = solved["kind"]
            semantic_sat = bool(solved["sat"])
            terminal_assignment = solved.get("assignment")
            terminal_verification = solved
            round_row["stop"] = terminal
            rounds.append(round_row)
            state = after_r33
            break

        affine = r34.recognize_complete_affine_cnf(after_r33)
        round_row["affine_recognized"] = bool(affine["recognized"])
        if affine["recognized"]:
            solution = r34.solve_gf2_with_certificate(affine["equations"])
            verify = r34.verify_affine_certificate(after_r33, affine, solution)
            if not verify["pass"]:
                raise AssertionError(("R47J_AFFINE_VERIFY_FAIL", verify))
            terminal = "AFFINE_XOR_SAT" if solution["sat"] else "AFFINE_XOR_UNSAT"
            semantic_sat = bool(solution["sat"])
            terminal_assignment = solution.get("assignment")
            terminal_verification = verify
            total_ledger["GF2_estimated_bit_ops"] += int(solution["estimated_bit_ops"])
            round_row["stop"] = terminal
            rounds.append(round_row)
            state = after_r33
            break

        rup = r35b.run_candidate(after_r33)
        rup_replay = r35b.independent_certificate_replay(after_r33, rup)
        if not rup_replay["pass"]:
            raise AssertionError(("R47J_RUP_REPLAY_FAIL", round_index, rup_replay))
        after_rup = r33.canonical_formula(rup["final_formula"])
        after_rup_clv = clv(after_rup)
        total_ledger["RUP_checks"] += int(rup["ledger"]["rup_checks"])
        total_ledger["RUP_UP_clause_scans"] += int(rup["ledger"]["up_clause_scans"])
        total_ledger["RUP_UP_literal_inspections"] += int(rup["ledger"]["up_literal_inspections"])
        round_row.update({
            "RUP_status": rup["status"],
            "RUP_history_count": len(rup.get("history", [])),
            "RUP_replay_pass": True,
            "after_RUP_CLV": list(after_rup_clv),
        })

        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal = "RUP_UNSAT"
            semantic_sat = False
            terminal_verification = rup_replay
            round_row["stop"] = terminal
            rounds.append(round_row)
            state = after_rup
            break

        if after_rup != after_r33:
            if not after_rup_clv < after_r33_clv:
                raise AssertionError(("R47J_RUP_CHANGE_NOT_STRICT_DESCENT", round_index, after_r33_clv, after_rup_clv))
            if not after_rup_clv < before_clv:
                raise AssertionError(("R47J_RESTART_STATE_NOT_STRICT_DESCENT", round_index, before_clv, after_rup_clv))
            total_ledger["restart_count"] += 1
            round_row["restart"] = True
            rounds.append(round_row)
            state = after_rup
            continue

        round_row["stop"] = "CERTIFIED_NORMALIZATION_FIXPOINT"
        rounds.append(round_row)
        state = after_rup
        break
    else:
        raise AssertionError(("R47J_RESTART_HEIGHT_BOUND_EXHAUSTED", height_bound))

    if len(rounds) > height_bound + 1:
        raise AssertionError("R47J_ROUND_BOUND_FAIL")

    return {
        "forced_formula_hash": r42.formula_hash(forced),
        "forced_CLV": list(clv(forced)),
        "height_bound": int(height_bound),
        "rounds": rounds,
        "round_count": len(rounds),
        "restart_count": int(total_ledger["restart_count"]),
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_assignment": terminal_assignment,
        "terminal_verification": terminal_verification,
        "final_formula": [list(c) for c in state],
        "final_formula_hash": r42.formula_hash(state),
        "final_CLV": list(clv(state)),
        "R33_reconstruction_results": r33_reconstruction_results,
        "ledger": total_ledger,
    }


def reconstruct_sat(before_formula, dp_record, normalization):
    if normalization["semantic_sat"] is not True:
        return {"applicable": False, "pass": True}
    assignment = dict(normalization["terminal_assignment"] or {})
    for result in reversed(normalization["R33_reconstruction_results"]):
        assignment = r33.reconstruct_model(result, assignment)
    assignment = r42.reconstruct_sa_bve(dp_record, assignment)
    missing = set(r33.variables(before_formula)) - set(assignment)
    for v in sorted(missing):
        assignment[v] = False
    passed = r33.eval_formula(r33.canonical_formula(before_formula), assignment)
    return {"applicable": True, "pass": passed, "assignment": assignment}


def macro_candidate_fixpoint(before_formula, var):
    before = r33.canonical_formula(before_formula)
    dp = r45a.exact_dp_record(before, int(var))
    if dp is None:
        return None
    dp_replay = r45a.independent_dp_replay(before, dp)
    envelope = r45a.polynomial_envelope(before, dp)
    if not dp_replay["pass"] or not envelope["pass"]:
        raise AssertionError(("R47J_DP_OR_ENVELOPE_FAIL", var, dp_replay, envelope))
    forced = r33.canonical_formula(dp["transformed"])
    normalization = normalize_to_certified_fixpoint(forced)
    final_formula = r33.canonical_formula(normalization["final_formula"])
    sat_reconstruction = reconstruct_sat(before, dp, normalization)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R47J_SAT_RECONSTRUCTION_FAIL", var))
    accepted = normalization["terminal"] is not None or clv(final_formula) < clv(before)
    return {
        "var": int(var),
        "input_hash": r42.formula_hash(before),
        "input_CLV": list(clv(before)),
        "DP": dp,
        "DP_independent_replay_pass": bool(dp_replay["pass"]),
        "polynomial_intermediate_envelope_pass": bool(envelope["pass"]),
        "normalization": normalization,
        "SAT_reconstruction": sat_reconstruction,
        "final_CLV": list(clv(final_formula)),
        "net_CLV_descent": clv(final_formula) < clv(before),
        "accepted": bool(accepted),
    }


def independent_fixpoint_macro_replay(before_formula, claimed):
    recomputed = macro_candidate_fixpoint(before_formula, int(claimed["var"]))
    fields = {
        "recomputed_exists": recomputed is not None,
        "final_hash_ok": recomputed is not None and recomputed["normalization"]["final_formula_hash"] == claimed["normalization"]["final_formula_hash"],
        "final_CLV_ok": recomputed is not None and recomputed["final_CLV"] == claimed["final_CLV"],
        "terminal_ok": recomputed is not None and recomputed["normalization"]["terminal"] == claimed["normalization"]["terminal"],
        "rounds_ok": recomputed is not None and recomputed["normalization"]["rounds"] == claimed["normalization"]["rounds"],
        "accepted_ok": recomputed is not None and recomputed["accepted"] == claimed["accepted"],
    }
    return {"pass": all(fields.values()), **fields}


def compact_candidate(candidate, replay=None):
    dp_clv = candidate["DP"]["measure_after_forced_DP"]
    return {
        "var": candidate["var"],
        "input_CLV": candidate["input_CLV"],
        "forced_DP_CLV": dp_clv,
        "old_one_pass_final_CLV": None,
        "fixpoint_final_CLV": candidate["final_CLV"],
        "terminal": candidate["normalization"]["terminal"],
        "restart_count": candidate["normalization"]["restart_count"],
        "round_count": candidate["normalization"]["round_count"],
        "rounds": candidate["normalization"]["rounds"],
        "net_CLV_descent": candidate["net_CLV_descent"],
        "accepted": candidate["accepted"],
        "independent_replay_pass": replay["pass"] if replay is not None else None,
    }


def run():
    sealed, counterexample = load_counterexample()
    variables = r33.variables(counterexample)

    old_rows = []
    old_accepted = []
    for v in variables:
        c = r45a.macro_candidate_for_var(counterexample, int(v))
        if c is None:
            continue
        old_rows.append({"var": int(v), "final_CLV": c["final_CLV"], "terminal": c["normalization"]["terminal"], "accepted": bool(c["accepted"])})
        if c["accepted"]:
            old_accepted.append(int(v))
    if old_accepted:
        raise AssertionError(("R47J_OLD_COUNTEREXAMPLE_NO_LONGER_DEAD", old_accepted))

    new_rows = []
    new_accepted = []
    for v in variables:
        c = macro_candidate_fixpoint(counterexample, int(v))
        if c is None:
            continue
        replay = independent_fixpoint_macro_replay(counterexample, c) if c["accepted"] else None
        if replay is not None and not replay["pass"]:
            raise AssertionError(("R47J_ACCEPTED_REPLAY_FAIL", v, replay))
        row = compact_candidate(c, replay)
        old = next(x for x in old_rows if x["var"] == int(v))
        row["old_one_pass_final_CLV"] = old["final_CLV"]
        new_rows.append(row)
        if c["accepted"]:
            new_accepted.append(int(v))

    pivot25 = next(row for row in new_rows if row["var"] == 25)
    if pivot25["old_one_pass_final_CLV"] != [63, 156, 19]:
        raise AssertionError(("R47J_PIVOT25_OLD_BOUNDARY_DRIFT", pivot25))

    rescued = bool(new_accepted)
    verdict = (
        "R47I_COUNTEREXAMPLE_RESCUED_BY_CERTIFIED_NORMALIZATION_FIXPOINT_CLOSURE"
        if rescued
        else "R47I_COUNTEREXAMPLE_SURVIVES_CERTIFIED_NORMALIZATION_FIXPOINT_CLOSURE"
    )
    out = {
        "gate": "JANUS_TRUMP_R47J_NORMALIZATION_FIXPOINT_RESTART_V25_GAP",
        "verdict": verdict,
        "sealed_counterexample": {
            "fixpoint_hash": EXPECTED_FIXPOINT_HASH,
            "fixpoint_CLV": list(EXPECTED_FIXPOINT_CLV),
            "mutated_original_hash": sealed["mutated_original"]["hash"],
        },
        "old_frozen_R45A": {"accepted_pivots": old_accepted, "rows": old_rows},
        "new_single_mechanism": "RESTART_EXISTING_CERTIFIED_R33_AFFINE_RUP_NORMALIZATION_AFTER_EACH_CHANGING_RUP_PASS",
        "new_accepted_pivots": new_accepted,
        "pivot25": pivot25,
        "all_pivot_rows": new_rows,
        "interpretation": {
            "new_inference_rule_added": False,
            "new_proof_authority_added": False,
            "finite_counterexample_rescue_if_true_does_not_prove_O4": True,
        },
        "firewall": {
            "O4_UNIVERSAL_COVERAGE_FOR_EXTENDED_GRAMMAR": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }
    print(json.dumps(out, sort_keys=True))
    return out


if __name__ == "__main__":
    run()
