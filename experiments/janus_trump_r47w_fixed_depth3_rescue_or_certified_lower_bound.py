from __future__ import annotations

import hashlib
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47k_extended_normalization_closure_one_swap_falsifier as r47k
import janus_trump_r47r_targeted_two_swap_depth2_rescue_disruption as r47r

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "research" / "JANUS_TRUMP_R47R_TARGETED_TWO_SWAP_DEPTH2_COUNTEREXAMPLE_COMPACT_RESULT_2026-09-04.json"
EXPECTED_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_CLV = (76, 203, 22)
EXPECTED_DEPTH2_COUNT = 462
EXPECTED_DEPTH2_LEDGER_HASH = "72416db56bcff832efed776c902e8d2e158cc706139bfac44e6c5366ab8340ed"


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def canonical_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_witness():
    data = json.loads(RESULT.read_text())
    if data["certified_lower_bound"] != "d(F)>2_WITHIN_FROZEN_GRAMMAR":
        raise AssertionError("R47W_PARENT_LOWER_BOUND_DRIFT")
    f = r33.canonical_formula(data["witness"]["residual_formula"])
    if r47f.formula_hash(f) != EXPECTED_HASH:
        raise AssertionError(("R47W_HASH_DRIFT", r47f.formula_hash(f)))
    if clv(f) != EXPECTED_CLV:
        raise AssertionError(("R47W_CLV_DRIFT", clv(f)))
    return data, f


def replay_layer(before, claimed, label):
    replay = r47j.independent_fixpoint_macro_replay(before, claimed)
    if not replay["pass"]:
        raise AssertionError(("R47W_LAYER_REPLAY_FAIL", label, replay))
    return True


def recompute_pair(original, first_var, second_var):
    first = r47j.macro_candidate_fixpoint(original, int(first_var))
    if first is None:
        raise AssertionError(("R47W_FIRST_MISSING", first_var))
    replay_layer(original, first, (first_var,))
    g1 = r33.canonical_formula(first["normalization"]["final_formula"])
    if first["normalization"]["terminal"] is not None or clv(g1) < clv(original):
        raise AssertionError(("R47W_DEPTH1_PARENT_DRIFT", first_var, clv(g1)))

    second = r47j.macro_candidate_fixpoint(g1, int(second_var))
    if second is None:
        raise AssertionError(("R47W_SECOND_MISSING", first_var, second_var))
    replay_layer(g1, second, (first_var, second_var))
    g2 = r33.canonical_formula(second["normalization"]["final_formula"])
    if second["normalization"]["terminal"] is not None or clv(g2) < clv(original):
        raise AssertionError(("R47W_DEPTH2_PARENT_DRIFT", first_var, second_var, clv(g2)))
    return first, g1, second, g2


def reconstruct_previous_layer(before, candidate, assignment_after):
    assignment = {int(k): bool(v) for k, v in dict(assignment_after).items()}
    for reduced in reversed(candidate["normalization"]["R33_reconstruction_results"]):
        assignment = r33.reconstruct_model(reduced, assignment)
    assignment = r42.reconstruct_sa_bve(candidate["DP"], assignment)
    for v in r33.variables(before):
        assignment.setdefault(int(v), False)
    return assignment


def verify_terminal_sat_composition(original, first, g1, second, g2, third):
    if third["normalization"]["semantic_sat"] is not True:
        return {"applicable": False, "pass": True}
    sat3 = third["SAT_reconstruction"]
    if not sat3.get("applicable") or not sat3.get("pass"):
        return {"applicable": True, "pass": False, "reason": "THIRD_LAYER_RECONSTRUCTION_FAILED"}
    assignment_g2 = dict(sat3["assignment"])
    if not r33.eval_formula(g2, assignment_g2):
        return {"applicable": True, "pass": False, "reason": "G2_ASSIGNMENT_FAIL"}
    assignment_g1 = reconstruct_previous_layer(g1, second, assignment_g2)
    if not r33.eval_formula(g1, assignment_g1):
        return {"applicable": True, "pass": False, "reason": "G1_RECONSTRUCTION_FAIL"}
    assignment_f = reconstruct_previous_layer(original, first, assignment_g1)
    passed = r33.eval_formula(original, assignment_f)
    return {
        "applicable": True,
        "pass": bool(passed),
        "assignment_size": len(assignment_f),
    }


def compact_layer(candidate):
    return {
        "var": int(candidate["var"]),
        "input_CLV": candidate["input_CLV"],
        "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
        "final_CLV": candidate["final_CLV"],
        "terminal": candidate["normalization"]["terminal"],
        "restart_count": int(candidate["normalization"]["restart_count"]),
        "round_count": int(candidate["normalization"]["round_count"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
    }


def run():
    parent, original = load_witness()

    depth1 = r47k.first_extended_accept(original)
    if depth1["covered"]:
        raise AssertionError(("R47W_PARENT_DEPTH1_DRIFT", depth1["selected_var"]))

    depth2 = r47r.depth2_scan(original, keep_all_failures=True)
    if depth2["covered"]:
        raise AssertionError(("R47W_PARENT_DEPTH2_DRIFT", depth2["selected_pair"]))
    failures = depth2["all_failures"]
    if len(failures) != EXPECTED_DEPTH2_COUNT:
        raise AssertionError(("R47W_DEPTH2_COUNT_DRIFT", len(failures)))
    ledger_hash = canonical_hash(failures)
    if ledger_hash != EXPECTED_DEPTH2_LEDGER_HASH:
        raise AssertionError(("R47W_DEPTH2_LEDGER_HASH_DRIFT", ledger_hash))

    ordered_prefixes = sorted(
        failures,
        key=lambda row: (tuple(row["second_final_CLV"]), int(row["first_var"]), int(row["second_var"])),
    )

    tested_triples = 0
    selected = None
    best_failure = None
    failure_digest_rows = []

    for pair_row in ordered_prefixes:
        first_var = int(pair_row["first_var"])
        second_var = int(pair_row["second_var"])
        first, g1, second, g2 = recompute_pair(original, first_var, second_var)

        for third_var in r33.variables(g2):
            third = r47j.macro_candidate_fixpoint(g2, int(third_var))
            if third is None:
                continue
            replay_layer(g2, third, (first_var, second_var, int(third_var)))
            g3 = r33.canonical_formula(third["normalization"]["final_formula"])
            accepted = third["normalization"]["terminal"] is not None or clv(g3) < clv(original)
            tested_triples += 1
            row = {
                "sequence": [first_var, second_var, int(third_var)],
                "prefix_final_CLV": list(clv(g2)),
                "third_forced_DP_CLV": third["DP"]["measure_after_forced_DP"],
                "final_CLV": list(clv(g3)),
                "terminal": third["normalization"]["terminal"],
                "accepted": bool(accepted),
                "third_restart_count": int(third["normalization"]["restart_count"]),
            }
            if accepted:
                terminal_sat_reconstruction = verify_terminal_sat_composition(
                    original, first, g1, second, g2, third
                )
                if not terminal_sat_reconstruction["pass"]:
                    raise AssertionError(("R47W_TERMINAL_SAT_COMPOSITION_FAIL", row, terminal_sat_reconstruction))
                selected = {
                    **row,
                    "layers": [compact_layer(first), compact_layer(second), compact_layer(third)],
                    "terminal_SAT_composed_reconstruction": terminal_sat_reconstruction,
                    "all_three_independent_replays_pass": True,
                }
                break

            failure_digest_rows.append(row)
            if best_failure is None or (
                tuple(row["final_CLV"]), tuple(row["sequence"])
            ) < (
                tuple(best_failure["final_CLV"]), tuple(best_failure["sequence"])
            ):
                best_failure = row
        if selected is not None:
            break

    if selected is not None:
        verdict = "EXPLICIT_CERTIFIED_DEPTH3_RESCUE_FOUND__d(F)=3_FOR_THIS_WITNESS"
        certified_depth_statement = "d(F)=3_FOR_THIS_FINITE_REACHABLE_WITNESS"
    else:
        # Every legal triple has been exhausted because early stop occurs only on acceptance.
        verdict = "ALL_LEGAL_DEPTH3_SEQUENCES_FAILED__d(F)>3_FOR_THIS_WITNESS"
        certified_depth_statement = "d(F)>3_FOR_THIS_FINITE_REACHABLE_WITNESS"

    out = {
        "gate": "JANUS_TRUMP_R47W_FIXED_DEPTH3_RESCUE_OR_CERTIFIED_LOWER_BOUND",
        "parent_R47R_commit": "d3ae7985a45cbf57af8fbf33015c69de85f52ec1",
        "input_hash": r47f.formula_hash(original),
        "input_CLV": list(clv(original)),
        "sealed_parent_lower_bound": parent["certified_lower_bound"],
        "depth1_reconfirmed_dead": True,
        "depth2_reconfirmed_dead": True,
        "depth2_failed_pair_count": len(failures),
        "depth2_failed_pair_ledger_sha256": ledger_hash,
        "depth3_tested_triples": tested_triples,
        "selected": selected,
        "best_depth3_failure": best_failure,
        "failed_depth3_prefix_sha256": canonical_hash(failure_digest_rows),
        "verdict": verdict,
        "certified_depth_statement": certified_depth_statement,
        "resource_contract": {
            "fixed_depth": 3,
            "naive_sequence_envelope": "O(V^3)",
            "unbounded_depth_escalation_authorized": False,
        },
        "firewall": {
            "UNIVERSAL_CONSTANT_K_EXISTS": "NOT_PROVED",
            "UNBOUNDED_DEPTH_FAMILY_EXISTS": "NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE": "OPEN",
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
