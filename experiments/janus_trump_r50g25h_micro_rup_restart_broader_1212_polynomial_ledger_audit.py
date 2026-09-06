from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25c_source_preimage_obstruction_forensics as r50g25c
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25H_MICRO_RUP_RESTART_BROADER_1212_AND_POLYNOMIAL_LEDGER_AUDIT"
EXPECTED_UNIQUE = 1212
EXPECTED_WEIGHTED = 1673
EXPECTED_FROZEN_SOURCES = 30
PIVOT = 1


def polynomial_meter_envelope(measure):
    """Explicit polynomial envelope for the metered micro-scheduler primitives.

    This is a ledger envelope, not a universal SAT runtime theorem.  It uses only
    the initial post-DP C,V bounds.  Throughout R33/RUP, clause count and variable
    count do not increase; total literal occurrences are therefore <= C*V.
    Every successful R33 or RUP transformation strictly descends CLV.
    """
    c, _l, v = (int(x) for x in measure)
    lcap = c * v
    state_triplet_bound = (c + 1) * (lcap + 1) * (v + 1)

    # One worst-case R33 scan iteration: taut + unit + pure + subsumption + BCE + BVE.
    r33_scan_cap = 2 * lcap + c + c * c + lcap * c + v * c * c
    # Across all rounds, strict transformations plus one terminal/stall scan per call.
    r33_check_ops_bound = (2 * state_triplet_bound + 1) * r33_scan_cap

    # first_rup_strengthening tests at most one candidate per literal occurrence.
    # A deterministic UP check performs at most V+1 full scans before fixpoint/conflict.
    rup_checks_bound = state_triplet_bound * lcap
    rup_clause_scans_bound = state_triplet_bound * lcap * c * (v + 1)
    rup_literal_inspections_bound = state_triplet_bound * lcap * lcap * (v + 1)
    restart_bound = max(0, state_triplet_bound - 1)

    # Complete-affine GF(2) solve: row_xors <= C*V and each xor is metered by C+V+1 bits.
    gf2_estimated_bit_ops_bound = c * v * (c + v + 1)

    return {
        "C0": c,
        "V0": v,
        "literal_occurrence_cap_CV": lcap,
        "strict_CLV_state_triplet_bound": state_triplet_bound,
        "R33_check_operation_upper_ledger_bound": r33_check_ops_bound,
        "RUP_checks_bound": rup_checks_bound,
        "RUP_UP_clause_scans_bound": rup_clause_scans_bound,
        "RUP_UP_literal_inspections_bound": rup_literal_inspections_bound,
        "restart_count_bound": restart_bound,
        "GF2_estimated_bit_ops_bound": gf2_estimated_bit_ops_bound,
    }


def counter_json(counter):
    return {str(k): int(v) for k, v in sorted(counter.items(), key=lambda kv: str(kv[0]))}


def run():
    parent = r50g25g.run()
    if parent["family_unique_state_count"] != 991:
        raise AssertionError(("R50G25H_PARENT_991_DRIFT", parent["family_unique_state_count"]))
    if not parent["all_991_micro_schedule_terminal"]:
        raise AssertionError("R50G25H_REQUIRES_TERMINAL_R50G25G_PARENT")
    if parent["exact_micro_semantic_mismatch_count"] != 0:
        raise AssertionError("R50G25H_PARENT_MICRO_SEMANTIC_DRIFT")

    r50g25b, r50g23, r35b, r33, r47j = r50g25g._chain()
    r42 = r50g23.r42
    _p, unique = r50g25b.rebuild_unique_states()
    if len(unique) != EXPECTED_UNIQUE:
        raise AssertionError(("R50G25H_UNIQUE_STATE_DRIFT", len(unique)))

    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}
    if len(source_by_hash) != EXPECTED_FROZEN_SOURCES:
        raise AssertionError(("R50G25H_FROZEN_SOURCE_DRIFT", len(source_by_hash)))

    minimum_hist_unique = Counter()
    minimum_hist_weighted = Counter()
    source_normal_form = Counter()
    exact_truth = Counter()
    sealed_terminal = Counter()
    micro_terminal = Counter()
    terminal_pairs = Counter()
    micro_round_hist = Counter()
    micro_restart_hist = Counter()
    micro_rup_strength_hist = Counter()

    weighted_total = 0
    source_lift_replay_failure = 0
    exact_control_out_of_domain = 0
    exact_sealed_mismatch = 0
    exact_micro_mismatch = 0
    sealed_micro_semantic_disagreement = 0
    micro_reconstruction_failure = 0
    micro_residual = 0
    sealed_residual = 0
    ledger_bound_violation_count = 0

    aggregate_micro_ledger = Counter({
        "R33_check_operation_upper_ledger": 0,
        "R33_certificate_bytes": 0,
        "RUP_checks": 0,
        "RUP_UP_clause_scans": 0,
        "RUP_UP_literal_inspections": 0,
        "RUP_successful_strengthenings": 0,
        "GF2_estimated_bit_ops": 0,
        "restart_count": 0,
    })
    aggregate_polynomial_bound = Counter({
        "R33_check_operation_upper_ledger_bound": 0,
        "RUP_checks_bound": 0,
        "RUP_UP_clause_scans_bound": 0,
        "RUP_UP_literal_inspections_bound": 0,
        "restart_count_bound": 0,
        "GF2_estimated_bit_ops_bound": 0,
    })
    max_utilization = Counter()
    examples = []
    anomalies = []

    for _key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        count = int(entry["occurrence_count"])
        weighted_total += count
        target = r50g25b.canon(entry["forced_formula"])
        cover = r50g25b.exact_minimum_cover(target)
        minimum = int(cover["minimum"])
        minimum_hist_unique[minimum] += 1
        minimum_hist_weighted[minimum] += count

        witness = entry["witness"]
        source_item = source_by_hash[witness["source_hash"]]
        source = r50g25b.canon(source_item["source"])
        c1 = tuple(int(x) for x in witness["first_clause"])
        c2 = tuple(int(x) for x in witness["second_clause"])
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]
        lifted_source = r50g25b.canon(list(source) + [c1, c2] + lifted)

        dp = r47j.r45a.exact_dp_record(lifted_source, PIVOT)
        if dp is None:
            source_lift_replay_failure += 1
            if len(anomalies) < 20:
                anomalies.append({"state_hash": r50g23.r50g4.fhash(target), "reason": "DP_RECORD_MISSING"})
            continue
        dp_replay = r47j.r45a.independent_dp_replay(lifted_source, dp)
        if not dp_replay.get("pass"):
            source_lift_replay_failure += 1
            if len(anomalies) < 20:
                anomalies.append({"state_hash": r50g23.r50g4.fhash(target), "reason": "DP_REPLAY_FAIL"})
            continue

        actual = r50g25b.canon(dp["transformed"])
        expected = r50g25b.canon(list(target) + lifted)
        normalized_expected = r50g25b.canon(r42.subsumption_minimize(expected))
        if actual == expected:
            normal_class = "EXACT_EXPECTED_POST_DP"
        elif actual == normalized_expected:
            normal_class = "SUBSUMPTION_NORMAL_FORM_ONLY"
        else:
            normal_class = "GENUINE_SOURCE_PREIMAGE_NONCOMMUTATION"
        source_normal_form[normal_class] += 1

        truth = None
        try:
            truth = r50g25g.exact_semantic(r33, actual)
            exact_truth["SAT" if truth["sat"] else "UNSAT"] += 1
        except AssertionError:
            exact_control_out_of_domain += 1

        sealed = r47j.normalize_to_certified_fixpoint(actual)
        micro = r50g25g.micro_normalize(actual, r50g23, r35b, r33, r47j)

        sealed_term = str(sealed.get("terminal")) if sealed.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        micro_term = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        sealed_terminal[sealed_term] += 1
        micro_terminal[micro_term] += 1
        terminal_pairs[(sealed_term, micro_term)] += 1
        micro_round_hist[int(micro.get("round_count", 0))] += 1
        micro_restart_hist[int(micro.get("restart_count", 0))] += 1

        micro_rup_strengthenings = int(micro["ledger"].get("RUP_successful_strengthenings", 0))
        micro_rup_strength_hist[micro_rup_strengthenings] += 1
        r50g25g.add_ledger(aggregate_micro_ledger, micro.get("ledger", {}), rup_strengthenings=None)

        if sealed.get("semantic_sat") is None:
            sealed_residual += 1
        if micro.get("semantic_sat") is None:
            micro_residual += 1

        sealed_sat = sealed.get("semantic_sat")
        micro_sat = micro.get("semantic_sat")
        if sealed_sat is not None and micro_sat is not None and bool(sealed_sat) != bool(micro_sat):
            sealed_micro_semantic_disagreement += 1
        if truth is not None and sealed_sat is not None and bool(sealed_sat) != bool(truth["sat"]):
            exact_sealed_mismatch += 1
        if truth is not None and micro_sat is not None and bool(micro_sat) != bool(truth["sat"]):
            exact_micro_mismatch += 1
        if micro_sat is True and not micro["SAT_reconstruction"].get("pass"):
            micro_reconstruction_failure += 1

        envelope = polynomial_meter_envelope(r33.measure(actual))
        for key in aggregate_polynomial_bound:
            aggregate_polynomial_bound[key] += int(envelope[key])

        observed_to_bound = {
            "R33_check_operation_upper_ledger": "R33_check_operation_upper_ledger_bound",
            "RUP_checks": "RUP_checks_bound",
            "RUP_UP_clause_scans": "RUP_UP_clause_scans_bound",
            "RUP_UP_literal_inspections": "RUP_UP_literal_inspections_bound",
            "restart_count": "restart_count_bound",
            "GF2_estimated_bit_ops": "GF2_estimated_bit_ops_bound",
        }
        local_violations = []
        for obs_key, bound_key in observed_to_bound.items():
            observed = int(micro["ledger"].get(obs_key, 0))
            bound = int(envelope[bound_key])
            if observed > bound:
                local_violations.append({"metric": obs_key, "observed": observed, "bound": bound})
            if bound > 0:
                ratio = observed / bound
                if ratio > max_utilization[obs_key]:
                    max_utilization[obs_key] = ratio
        if local_violations:
            ledger_bound_violation_count += 1
            if len(anomalies) < 20:
                anomalies.append({
                    "state_hash": r50g23.r50g4.fhash(target),
                    "reason": "POLYNOMIAL_METER_ENVELOPE_VIOLATION",
                    "violations": local_violations,
                })

        if len(examples) < 24:
            examples.append({
                "state_hash": r50g23.r50g4.fhash(target),
                "occurrence_count": count,
                "minimum_static_binary_incidence_cover": minimum,
                "source_normal_form_class": normal_class,
                "post_DP_CLV": list(r33.measure(actual)),
                "exact_sat": None if truth is None else bool(truth["sat"]),
                "sealed_terminal": sealed_term,
                "micro_terminal": micro_term,
                "micro_rounds": int(micro.get("round_count", 0)),
                "micro_restarts": int(micro.get("restart_count", 0)),
                "micro_RUP_strengthenings": micro_rup_strengthenings,
                "meter_envelope": envelope,
            })

    if weighted_total != EXPECTED_WEIGHTED:
        raise AssertionError(("R50G25H_WEIGHTED_OCCURRENCE_DRIFT", weighted_total))

    evaluated_unique = EXPECTED_UNIQUE - source_lift_replay_failure
    exact_checked = evaluated_unique - exact_control_out_of_domain
    all_micro_terminal = micro_residual == 0 and evaluated_unique == EXPECTED_UNIQUE
    all_metered_within_envelope = ledger_bound_violation_count == 0
    all_semantics_clean = (
        exact_sealed_mismatch == 0
        and exact_micro_mismatch == 0
        and sealed_micro_semantic_disagreement == 0
        and micro_reconstruction_failure == 0
    )

    if source_lift_replay_failure:
        next_gate = "R50G25I_SOURCE_LIFT_REPLAY_FAILURE_FORENSICS"
    elif micro_residual:
        next_gate = "R50G25I_MICRO_RUP_RESTART_RESIDUAL_FIXPOINT_FORENSICS"
    elif ledger_bound_violation_count:
        next_gate = "R50G25I_POLYNOMIAL_METER_ENVELOPE_VIOLATION_FORENSICS"
    elif not all_semantics_clean:
        next_gate = "R50G25I_SEMANTIC_OR_RECONSTRUCTION_MISMATCH_FORENSICS"
    elif exact_control_out_of_domain:
        next_gate = "R50G25I_EXACT_VALIDATION_DOMAIN_EXTENSION"
    else:
        next_gate = "R50G25I_ALL_1673_SOURCE_OCCURRENCE_REPLAY_AND_WITNESS_INDEPENDENCE_AUDIT"

    pair_json = {
        f"{a} -> {b}": int(v)
        for (a, b), v in sorted(terminal_pairs.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    }

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "coverage_contract": {
            "frozen_source_skeleton_count": EXPECTED_FROZEN_SOURCES,
            "new_source_skeletons_added": 0,
            "parent_ge3_unique_states": 991,
            "broader_all_pair_post_DP_unique_states": EXPECTED_UNIQUE,
            "newly_covered_unique_states_beyond_G": EXPECTED_UNIQUE - 991,
            "all_pair_weighted_occurrences": EXPECTED_WEIGHTED,
        },
        "minimum_static_binary_incidence_cover_unique_histogram": counter_json(minimum_hist_unique),
        "minimum_static_binary_incidence_cover_weighted_histogram": counter_json(minimum_hist_weighted),
        "source_normal_form_unique_partition": counter_json(source_normal_form),
        "source_lift_replay_failure_unique_count": source_lift_replay_failure,
        "evaluated_unique_state_count": evaluated_unique,
        "exact_validation_checked_unique_count": exact_checked,
        "exact_validation_out_of_domain_unique_count": exact_control_out_of_domain,
        "exact_truth_unique_partition": counter_json(exact_truth),
        "sealed_terminal_unique_partition": counter_json(sealed_terminal),
        "micro_terminal_unique_partition": counter_json(micro_terminal),
        "sealed_to_micro_terminal_pair_unique_partition": pair_json,
        "sealed_residual_fixpoint_unique_count": sealed_residual,
        "micro_residual_fixpoint_unique_count": micro_residual,
        "all_1212_micro_schedule_terminal": all_micro_terminal,
        "exact_sealed_semantic_mismatch_count": exact_sealed_mismatch,
        "exact_micro_semantic_mismatch_count": exact_micro_mismatch,
        "sealed_micro_semantic_disagreement_count": sealed_micro_semantic_disagreement,
        "micro_SAT_reconstruction_failure_count": micro_reconstruction_failure,
        "micro_round_count_unique_histogram": counter_json(micro_round_hist),
        "micro_restart_count_unique_histogram": counter_json(micro_restart_hist),
        "micro_RUP_successful_strengthenings_unique_histogram": counter_json(micro_rup_strength_hist),
        "aggregate_micro_ledger": dict(sorted((k, int(v)) for k, v in aggregate_micro_ledger.items())),
        "aggregate_polynomial_meter_envelope": dict(sorted((k, int(v)) for k, v in aggregate_polynomial_bound.items())),
        "polynomial_meter_envelope_violation_unique_count": ledger_bound_violation_count,
        "all_metered_micro_operations_within_explicit_polynomial_envelope": all_metered_within_envelope,
        "max_observed_to_bound_utilization": {k: float(v) for k, v in sorted(max_utilization.items())},
        "examples": examples,
        "anomalies": anomalies,
        "next_gate": next_gate,
        "interpretation_contract": {
            "broader_coverage_adds_zero_new_source_skeletons": True,
            "broader_coverage_is_all_1212_unique_pair_post_DP_states_from_the_same_frozen_30": True,
            "exact_minimum_cover_is_experimental_input_generation_not_candidate_algorithm_core": True,
            "exact_assignment_enumeration_is_validation_oracle_only": True,
            "polynomial_meter_envelope_covers_metered_R33_RUP_restart_GF2_operations": True,
            "certificate_serialization_bytes_are_reported_empirically_not_formally_bounded_here": True,
            "independent_replay_checker_cost_is_not_in_the_numeric_meter_envelope": True,
            "meter_envelope_is_a_local_scheduler_complexity_contract_not_universal_SAT_coverage": True,
            "all_1212_terminal_if_true_is_not_universal_3CNF_terminal_coverage": True,
            "unique_state_witness_replay_does_not_yet_prove_all_1673_source_preimages_are_interchangeable": True,
        },
        "firewall": {
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    args = ap.parse_args()
    out = run()
    text = json.dumps(out, sort_keys=True, indent=2)
    if args.out:
        p = Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
