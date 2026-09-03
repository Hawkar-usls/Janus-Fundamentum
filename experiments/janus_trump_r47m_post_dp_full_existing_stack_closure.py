from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Optional

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j

RESULT_PATH = Path(__file__).resolve().parents[1] / "research" / "JANUS_TRUMP_R47K_EXPLICIT_REACHABLE_COUNTEREXAMPLE_TO_EXTENDED_NORMALIZATION_CLOSURE_RESULT_2026-09-03.json"
EXPECTED_FIXPOINT_HASH = "9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde"
EXPECTED_FIXPOINT_CLV = (77, 206, 22)
EXPECTED_R47J_ACCEPTED = ()


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def load_counterexample():
    data = json.loads(RESULT_PATH.read_text())
    formula = r33.canonical_formula(data["genuine_residual_fixpoint"]["formula"])
    if r42.formula_hash(formula) != EXPECTED_FIXPOINT_HASH:
        raise AssertionError(("R47M_FIXPOINT_HASH_DRIFT", r42.formula_hash(formula)))
    if clv(formula) != EXPECTED_FIXPOINT_CLV:
        raise AssertionError(("R47M_FIXPOINT_CLV_DRIFT", clv(formula)))
    return data, formula


def outer_height_bound(forced_formula):
    C, _, V = clv(forced_formula)
    return (C + 1) * (C * max(1, V) + 1) * (V + 1)


def normalize_full_existing_stack(transformed_formula):
    forced = r33.canonical_formula(transformed_formula)
    state = forced
    bound = outer_height_bound(forced)
    segments = []
    reconstruction_events = []
    total_sa_bve = 0
    terminal = None
    semantic_sat: Optional[bool] = None
    terminal_assignment: Optional[Dict[int, bool]] = None
    terminal_verification = None

    for outer_index in range(bound + 1):
        before_segment = state
        before_segment_clv = clv(before_segment)
        norm = r47j.normalize_to_certified_fixpoint(before_segment)
        after_norm = r33.canonical_formula(norm["final_formula"])
        after_norm_clv = clv(after_norm)
        if after_norm != before_segment and not after_norm_clv < before_segment_clv:
            raise AssertionError(("R47M_R47J_SEGMENT_NOT_DESCENT", outer_index, before_segment_clv, after_norm_clv))
        for rr in norm["R33_reconstruction_results"]:
            reconstruction_events.append({"kind":"R33", "result":rr})

        row = {
            "outer": int(outer_index),
            "before_CLV": list(before_segment_clv),
            "R47J_final_CLV": list(after_norm_clv),
            "R47J_round_count": int(norm["round_count"]),
            "R47J_restart_count": int(norm["restart_count"]),
            "R47J_terminal": norm["terminal"],
        }

        if norm["terminal"] is not None:
            terminal = norm["terminal"]
            semantic_sat = norm["semantic_sat"]
            terminal_assignment = norm["terminal_assignment"]
            terminal_verification = norm["terminal_verification"]
            row["stop"] = terminal
            segments.append(row)
            state = after_norm
            break

        bve, bve_ledger = r42.best_sa_bve_candidate(after_norm)
        row["SA_BVE_variables_checked"] = int(bve_ledger["variables_checked"])
        row["SA_BVE_resolution_pair_checks"] = int(bve_ledger["resolution_pair_checks"])
        row["SA_BVE_subsumption_pair_upper_ledger"] = int(bve_ledger["subsumption_pair_upper_ledger"])
        if bve is None:
            row["SA_BVE_applied"] = False
            row["stop"] = "CERTIFIED_FULL_EXISTING_STACK_FIXPOINT"
            segments.append(row)
            state = after_norm
            break

        bve_replay = r42.independent_sa_bve_replay(after_norm, bve)
        if not bve_replay["pass"]:
            raise AssertionError(("R47M_SA_BVE_REPLAY_FAIL", outer_index, bve_replay))
        after_bve = r33.canonical_formula(bve["transformed"])
        after_bve_clv = clv(after_bve)
        if not after_bve_clv < after_norm_clv:
            raise AssertionError(("R47M_SA_BVE_NOT_STRICT_DESCENT", outer_index, after_norm_clv, after_bve_clv))
        if not after_bve_clv < before_segment_clv:
            raise AssertionError(("R47M_OUTER_RESTART_NOT_STRICT_DESCENT", outer_index, before_segment_clv, after_bve_clv))

        reconstruction_events.append({"kind":"SA_BVE", "record":bve})
        total_sa_bve += 1
        row.update({
            "SA_BVE_applied": True,
            "SA_BVE_var": int(bve["var"]),
            "SA_BVE_before_CLV": bve["measure_before"],
            "SA_BVE_after_CLV": bve["measure_after"],
            "SA_BVE_replay_pass": True,
            "restart": True,
        })
        segments.append(row)
        state = after_bve
    else:
        raise AssertionError(("R47M_OUTER_HEIGHT_BOUND_EXHAUSTED", bound))

    return {
        "forced_formula_hash": r42.formula_hash(forced),
        "forced_CLV": list(clv(forced)),
        "height_bound": int(bound),
        "segments": segments,
        "segment_count": len(segments),
        "SA_BVE_application_count": int(total_sa_bve),
        "terminal": terminal,
        "semantic_sat": semantic_sat,
        "terminal_assignment": terminal_assignment,
        "terminal_verification": terminal_verification,
        "final_formula": [list(c) for c in state],
        "final_formula_hash": r42.formula_hash(state),
        "final_CLV": list(clv(state)),
        "reconstruction_events": reconstruction_events,
    }


def reconstruct_sat(before_formula, dp_record, normalization):
    if normalization["semantic_sat"] is not True:
        return {"applicable":False, "pass":True}
    assignment = dict(normalization["terminal_assignment"] or {})
    for event in reversed(normalization["reconstruction_events"]):
        if event["kind"] == "R33":
            assignment = r33.reconstruct_model(event["result"], assignment)
        elif event["kind"] == "SA_BVE":
            assignment = r42.reconstruct_sa_bve(event["record"], assignment)
        else:
            raise AssertionError(event["kind"])
    assignment = r42.reconstruct_sa_bve(dp_record, assignment)
    for v in sorted(set(r33.variables(before_formula)) - set(assignment)):
        assignment[v] = False
    passed = r33.eval_formula(r33.canonical_formula(before_formula), assignment)
    return {"applicable":True, "pass":passed, "assignment":assignment}


def macro_candidate_full_closure(before_formula, var):
    before = r33.canonical_formula(before_formula)
    dp = r45a.exact_dp_record(before, int(var))
    if dp is None:
        return None
    dp_replay = r45a.independent_dp_replay(before, dp)
    envelope = r45a.polynomial_envelope(before, dp)
    if not dp_replay["pass"] or not envelope["pass"]:
        raise AssertionError(("R47M_DP_OR_ENVELOPE_FAIL", var, dp_replay, envelope))
    forced = r33.canonical_formula(dp["transformed"])
    normalization = normalize_full_existing_stack(forced)
    final_formula = r33.canonical_formula(normalization["final_formula"])
    sat_reconstruction = reconstruct_sat(before, dp, normalization)
    if not sat_reconstruction["pass"]:
        raise AssertionError(("R47M_SAT_RECONSTRUCTION_FAIL", var))
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


def independent_replay(before_formula, claimed):
    recomputed = macro_candidate_full_closure(before_formula, int(claimed["var"]))
    fields = {
        "exists": recomputed is not None,
        "final_hash_ok": recomputed is not None and recomputed["normalization"]["final_formula_hash"] == claimed["normalization"]["final_formula_hash"],
        "final_CLV_ok": recomputed is not None and recomputed["final_CLV"] == claimed["final_CLV"],
        "terminal_ok": recomputed is not None and recomputed["normalization"]["terminal"] == claimed["normalization"]["terminal"],
        "segments_ok": recomputed is not None and recomputed["normalization"]["segments"] == claimed["normalization"]["segments"],
        "accepted_ok": recomputed is not None and recomputed["accepted"] == claimed["accepted"],
    }
    return {"pass":all(fields.values()), **fields}


def compact(candidate, replay=None):
    return {
        "var": int(candidate["var"]),
        "input_CLV": candidate["input_CLV"],
        "forced_DP_CLV": candidate["DP"]["measure_after_forced_DP"],
        "final_CLV": candidate["final_CLV"],
        "terminal": candidate["normalization"]["terminal"],
        "segment_count": int(candidate["normalization"]["segment_count"]),
        "SA_BVE_application_count": int(candidate["normalization"]["SA_BVE_application_count"]),
        "segments": candidate["normalization"]["segments"],
        "net_CLV_descent": bool(candidate["net_CLV_descent"]),
        "accepted": bool(candidate["accepted"]),
        "DP_independent_replay_pass": bool(candidate["DP_independent_replay_pass"]),
        "polynomial_intermediate_envelope_pass": bool(candidate["polynomial_intermediate_envelope_pass"]),
        "independent_replay_pass": replay["pass"] if replay is not None else None,
    }


def run():
    sealed, counterexample = load_counterexample()
    old_accepted = []
    for v in r33.variables(counterexample):
        c = r47j.macro_candidate_fixpoint(counterexample, int(v))
        if c is not None and c["accepted"]:
            old_accepted.append(int(v))
    if tuple(old_accepted) != EXPECTED_R47J_ACCEPTED:
        raise AssertionError(("R47M_R47J_COUNTEREXAMPLE_DRIFT", old_accepted))

    rows = []
    accepted = []
    first_accepted = None
    for v in r33.variables(counterexample):
        c = macro_candidate_full_closure(counterexample, int(v))
        if c is None:
            continue
        replay = independent_replay(counterexample, c) if c["accepted"] else None
        if replay is not None and not replay["pass"]:
            raise AssertionError(("R47M_ACCEPTED_REPLAY_FAIL", v, replay))
        row = compact(c, replay)
        rows.append(row)
        if c["accepted"]:
            accepted.append(int(v))
            if first_accepted is None:
                first_accepted = row

    verdict = (
        "R47K_COUNTEREXAMPLE_RESCUED_BY_POST_DP_FULL_EXISTING_STACK_CLOSURE"
        if accepted else
        "R47K_COUNTEREXAMPLE_SURVIVES_POST_DP_FULL_EXISTING_STACK_CLOSURE"
    )
    closest = [r for r in rows if r["var"] in (7,20)]
    return {
        "gate":"JANUS_TRUMP_R47M_POST_DP_FULL_EXISTING_STACK_CLOSURE",
        "verdict":verdict,
        "sealed_counterexample":{
            "fixpoint_hash":EXPECTED_FIXPOINT_HASH,
            "fixpoint_CLV":list(EXPECTED_FIXPOINT_CLV),
            "R47J_accepted_pivots":old_accepted,
        },
        "new_single_mechanism":"RESTART_R47J_NORMALIZATION_AFTER_EXISTING_CERTIFIED_R42_SA_BVE_UNTIL_JOINT_FIXPOINT",
        "accepted_pivots":accepted,
        "first_accepted":first_accepted,
        "closest_pivots_7_20":closest,
        "all_pivot_rows":rows,
        "resource_envelope":{
            "polynomial":True,
            "reason":"Each R47J segment is polynomial; every added SA-BVE is polynomially discovered and strictly CLV-descending; no fresh variables; restart count bounded by forced-formula CLV-state envelope."
        },
        "interpretation":{
            "new_inference_rule_added":False,
            "new_proof_authority_added":False,
            "finite_counterexample_rescue_if_true_does_not_prove_O4":True,
        },
        "firewall":{
            "O4_UNIVERSAL_COVERAGE_FOR_FULL_EXISTING_STACK_CLOSURE":"OPEN",
            "SAT_IN_P":"NOT_PROVED",
            "P_EQ_NP":"NOT_PROVED",
            "P_NE_NP":"NOT_PROVED",
            "P_VS_NP":"OPEN",
            "TRUMP_finished":False,
        },
    }


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
