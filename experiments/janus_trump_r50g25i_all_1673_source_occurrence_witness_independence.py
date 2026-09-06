from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import janus_trump_r50g25a_bce_bve_joint_debt_hypergraph as r50g25a
import janus_trump_r50g25b_source_realizability_minimum_joint_debt as r50g25b
import janus_trump_r50g25h_sealed_result as r50g25h_sealed
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25I_ALL_1673_SOURCE_OCCURRENCE_REPLAY_AND_WITNESS_INDEPENDENCE_AUDIT"
EXPECTED_OCCURRENCES = 1673
EXPECTED_UNIQUE_STATES = 1212
EXPECTED_SOURCES = 30
PIVOT = 1


def canon(formula):
    return r50g25b.canon(formula)


def truth_signature(r33, formula):
    formula = r33.canonical_formula(formula)
    vs = list(r33.variables(formula))
    if len(vs) > 6:
        raise AssertionError(("R50G25I_EXACT_CONTROL_VAR_BOUND_DRIFT", len(vs)))
    bits = []
    model_count = 0
    for assignment_bits in itertools.product((False, True), repeat=len(vs)):
        assignment = dict(zip(vs, assignment_bits))
        sat = bool(r33.eval_formula(formula, assignment))
        bits.append("1" if sat else "0")
        model_count += int(sat)
    payload = json.dumps({"variables": vs, "truth": "".join(bits)}, sort_keys=True, separators=(",", ":"))
    return {
        "variables": vs,
        "assignment_space_checked": 2 ** len(vs),
        "model_count": model_count,
        "sat": model_count > 0,
        "truth_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
    }


def micro_route_signature(micro):
    rounds = []
    for row in micro.get("rounds", []):
        rounds.append({
            "R33_terminal": row.get("R33_terminal"),
            "R33_apps": int(row.get("R33_apps", 0)),
            "RUP_removed_literal": row.get("RUP_removed_literal"),
            "restart": bool(row.get("restart", row.get("micro_restart", False))),
            "stop": row.get("stop"),
        })
    payload = {
        "terminal": micro.get("terminal"),
        "semantic_sat": micro.get("semantic_sat"),
        "round_count": int(micro.get("round_count", 0)),
        "restart_count": int(micro.get("restart_count", micro.get("ledger", {}).get("restart_count", 0))),
        "RUP_successful_strengthenings": int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0)),
        "rounds": rounds,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest(), payload


def run():
    parent = r50g25h_sealed.run()
    if parent["next_gate"] != "R50G25I_ALL_1673_SOURCE_OCCURRENCE_REPLAY_AND_WITNESS_INDEPENDENCE_AUDIT":
        raise AssertionError(("R50G25I_PARENT_GATE_DRIFT", parent["next_gate"]))
    if not parent["all_1212_micro_schedule_terminal"]:
        raise AssertionError("R50G25I_REQUIRES_TERMINAL_H_PARENT")
    if parent["seal"]["authoritative_RUP_successful_strengthenings_total"] != 6:
        raise AssertionError(("R50G25I_PARENT_RUP_TOTAL_DRIFT", parent["seal"]))

    _parent_a, occurrences = r50g25a.enumerate_pair_post_dp_states()
    if len(occurrences) != EXPECTED_OCCURRENCES:
        raise AssertionError(("R50G25I_OCCURRENCE_COUNT_DRIFT", len(occurrences)))

    r50g23 = r50g25a.r50g24.r50g23
    r47j = r50g23.r47j
    r42 = r47j.r45a.r42
    r33 = r50g23.r33
    r35b = r50g23.r35b

    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}
    if len(source_by_hash) != EXPECTED_SOURCES:
        raise AssertionError(("R50G25I_SOURCE_COUNT_DRIFT", len(source_by_hash)))

    cover_cache = {}
    actual_analysis_cache = {}
    target_groups = defaultdict(lambda: {
        "occurrence_count": 0,
        "source_hashes": set(),
        "actual_post_DP_hashes": set(),
        "truth_signatures": set(),
        "micro_route_signatures": set(),
        "micro_terminals": set(),
        "micro_semantics": set(),
        "source_normal_form_classes": Counter(),
        "rup_strengthening_counts": set(),
        "restart_counts": set(),
        "examples": [],
    })

    replay_failure_count = 0
    genuine_noncommutation_count = 0
    semantic_mismatch_count = 0
    reconstruction_failure_count = 0
    residual_count = 0
    exact_control_out_of_domain = 0
    occurrence_normal_form = Counter()
    occurrence_micro_terminal = Counter()
    occurrence_rup_hist = Counter()
    occurrence_restart_hist = Counter()
    anomalies = []

    for index, occurrence in enumerate(occurrences):
        target = canon(occurrence["forced_formula"])
        target_key = tuple(target)
        target_hash = r50g23.r50g4.fhash(target)

        if target_key not in cover_cache:
            cover_cache[target_key] = r50g25b.exact_minimum_cover(target)
        cover = cover_cache[target_key]
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]

        source_item = source_by_hash[occurrence["source_hash"]]
        source = canon(source_item["source"])
        c1 = tuple(int(x) for x in occurrence["first_clause"])
        c2 = tuple(int(x) for x in occurrence["second_clause"])
        lifted_source = canon(list(source) + [c1, c2] + lifted)

        dp = r47j.r45a.exact_dp_record(lifted_source, PIVOT)
        if dp is None:
            replay_failure_count += 1
            if len(anomalies) < 24:
                anomalies.append({"index": index, "target_state_hash": target_hash, "reason": "DP_RECORD_MISSING"})
            continue
        dp_replay = r47j.r45a.independent_dp_replay(lifted_source, dp)
        if not dp_replay.get("pass"):
            replay_failure_count += 1
            if len(anomalies) < 24:
                anomalies.append({"index": index, "target_state_hash": target_hash, "reason": "DP_REPLAY_FAIL"})
            continue

        actual = canon(dp["transformed"])
        actual_hash = r50g23.r50g4.fhash(actual)
        expected = canon(list(target) + lifted)
        normalized_expected = canon(r42.subsumption_minimize(expected))
        if actual == expected:
            normal_class = "EXACT_EXPECTED_POST_DP"
        elif actual == normalized_expected:
            normal_class = "SUBSUMPTION_NORMAL_FORM_ONLY"
        else:
            normal_class = "GENUINE_SOURCE_PREIMAGE_NONCOMMUTATION"
            genuine_noncommutation_count += 1
        occurrence_normal_form[normal_class] += 1

        if actual_hash not in actual_analysis_cache:
            try:
                truth = truth_signature(r33, actual)
            except AssertionError:
                exact_control_out_of_domain += 1
                truth = None
            micro = r50g25g.micro_normalize(actual, r50g23, r35b, r33, r47j)
            route_hash, route_payload = micro_route_signature(micro)
            reconstruction_pass = bool(micro.get("SAT_reconstruction", {}).get("pass", True))
            actual_analysis_cache[actual_hash] = {
                "truth": truth,
                "micro": micro,
                "route_hash": route_hash,
                "route_payload": route_payload,
                "reconstruction_pass": reconstruction_pass,
            }
        analysis = actual_analysis_cache[actual_hash]
        truth = analysis["truth"]
        micro = analysis["micro"]

        if micro.get("semantic_sat") is None:
            residual_count += 1
        if not analysis["reconstruction_pass"]:
            reconstruction_failure_count += 1
        if truth is not None and micro.get("semantic_sat") is not None and bool(truth["sat"]) != bool(micro["semantic_sat"]):
            semantic_mismatch_count += 1

        micro_terminal = str(micro.get("terminal")) if micro.get("terminal") is not None else "RESIDUAL_FIXPOINT"
        rup_count = int(micro.get("ledger", {}).get("RUP_successful_strengthenings", 0))
        restart_count = int(micro.get("restart_count", micro.get("ledger", {}).get("restart_count", 0)))
        occurrence_micro_terminal[micro_terminal] += 1
        occurrence_rup_hist[rup_count] += 1
        occurrence_restart_hist[restart_count] += 1

        group = target_groups[target_hash]
        group["occurrence_count"] += 1
        group["source_hashes"].add(str(occurrence["source_hash"]))
        group["actual_post_DP_hashes"].add(actual_hash)
        if truth is not None:
            group["truth_signatures"].add(truth["truth_sha256"])
        group["micro_route_signatures"].add(analysis["route_hash"])
        group["micro_terminals"].add(micro_terminal)
        group["micro_semantics"].add(str(micro.get("semantic_sat")))
        group["source_normal_form_classes"][normal_class] += 1
        group["rup_strengthening_counts"].add(rup_count)
        group["restart_counts"].add(restart_count)
        if len(group["examples"]) < 3:
            group["examples"].append({
                "source_hash": occurrence["source_hash"],
                "first_clause": occurrence["first_clause"],
                "second_clause": occurrence["second_clause"],
                "actual_post_DP_hash": actual_hash,
                "source_normal_form_class": normal_class,
                "micro_terminal": micro_terminal,
                "micro_RUP_strengthenings": rup_count,
                "micro_restarts": restart_count,
            })

    if replay_failure_count:
        evaluated_occurrences = EXPECTED_OCCURRENCES - replay_failure_count
    else:
        evaluated_occurrences = EXPECTED_OCCURRENCES

    if len(target_groups) != EXPECTED_UNIQUE_STATES:
        raise AssertionError(("R50G25I_TARGET_GROUP_COUNT_DRIFT", len(target_groups)))
    if sum(g["occurrence_count"] for g in target_groups.values()) != evaluated_occurrences:
        raise AssertionError("R50G25I_GROUP_OCCURRENCE_SUM_DRIFT")

    group_class_partition = Counter()
    multi_form_examples = []
    semantic_divergence_groups = 0
    route_divergence_groups = 0
    strong_witness_independent_groups = 0

    for state_hash, group in sorted(target_groups.items()):
        actual_count = len(group["actual_post_DP_hashes"])
        truth_count = len(group["truth_signatures"])
        route_count = len(group["micro_route_signatures"])
        semantic_count = len(group["micro_semantics"])

        if truth_count > 1 or semantic_count > 1:
            cls = "SEMANTIC_DIVERGENCE_ACROSS_SOURCE_PREIMAGES"
            semantic_divergence_groups += 1
        elif actual_count > 1 and route_count > 1:
            cls = "MULTIPLE_NORMAL_FORMS_ROUTE_DIVERGENCE_SAME_TRUTH"
            route_divergence_groups += 1
        elif actual_count > 1:
            cls = "MULTIPLE_NORMAL_FORMS_SAME_TRUTH_AND_ROUTE"
        elif route_count > 1:
            cls = "SAME_NORMAL_FORM_ROUTE_DIVERGENCE"
            route_divergence_groups += 1
        else:
            cls = "SOURCE_PREIMAGE_STRONG_WITNESS_INDEPENDENCE"
            strong_witness_independent_groups += 1
        group_class_partition[cls] += 1

        if cls != "SOURCE_PREIMAGE_STRONG_WITNESS_INDEPENDENCE" and len(multi_form_examples) < 24:
            multi_form_examples.append({
                "state_hash": state_hash,
                "classification": cls,
                "occurrence_count": group["occurrence_count"],
                "source_hash_count": len(group["source_hashes"]),
                "actual_post_DP_hash_count": actual_count,
                "truth_signature_count": truth_count,
                "micro_route_signature_count": route_count,
                "micro_terminals": sorted(group["micro_terminals"]),
                "micro_semantics": sorted(group["micro_semantics"]),
                "rup_strengthening_counts": sorted(group["rup_strengthening_counts"]),
                "restart_counts": sorted(group["restart_counts"]),
                "source_normal_form_classes": dict(sorted(group["source_normal_form_classes"].items())),
                "examples": group["examples"],
            })

    if replay_failure_count:
        next_gate = "R50G25J_SOURCE_OCCURRENCE_REPLAY_FAILURE_FORENSICS"
    elif genuine_noncommutation_count:
        next_gate = "R50G25J_GENUINE_SOURCE_PREIMAGE_NONCOMMUTATION_MINIMAL_PLATYPUS"
    elif semantic_divergence_groups:
        next_gate = "R50G25J_SOURCE_PREIMAGE_SEMANTIC_DIVERGENCE_MINIMAL_PLATYPUS"
    elif route_divergence_groups or group_class_partition["MULTIPLE_NORMAL_FORMS_SAME_TRUTH_AND_ROUTE"]:
        next_gate = "R50G25J_SOURCE_PREIMAGE_QUOTIENT_CONFLUENCE_FORENSICS"
    else:
        next_gate = "R50G25J_FROZEN_PAIR_STATE_SOURCE_PREIMAGE_CONFLUENCE_LEMMA_AND_OUTER_COVERAGE_GATE"

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "coverage_contract": {
            "frozen_source_skeleton_count": EXPECTED_SOURCES,
            "new_source_skeletons_added": 0,
            "all_pair_source_occurrence_count": EXPECTED_OCCURRENCES,
            "unique_target_state_count": EXPECTED_UNIQUE_STATES,
            "deduplication_removed_occurrences": EXPECTED_OCCURRENCES - EXPECTED_UNIQUE_STATES,
            "evaluated_source_occurrence_count": evaluated_occurrences,
        },
        "source_occurrence_replay_failure_count": replay_failure_count,
        "genuine_source_preimage_noncommutation_occurrence_count": genuine_noncommutation_count,
        "exact_validation_out_of_domain_actual_state_count": exact_control_out_of_domain,
        "exact_micro_semantic_mismatch_occurrence_count": semantic_mismatch_count,
        "micro_SAT_reconstruction_failure_occurrence_count": reconstruction_failure_count,
        "micro_residual_occurrence_count": residual_count,
        "occurrence_source_normal_form_partition": dict(sorted(occurrence_normal_form.items())),
        "occurrence_micro_terminal_partition": dict(sorted(occurrence_micro_terminal.items())),
        "occurrence_micro_RUP_strengthening_histogram": {str(k): int(v) for k, v in sorted(occurrence_rup_hist.items())},
        "occurrence_micro_restart_histogram": {str(k): int(v) for k, v in sorted(occurrence_restart_hist.items())},
        "unique_actual_post_DP_state_count_after_all_source_lifts": len(actual_analysis_cache),
        "target_group_witness_independence_partition": dict(sorted(group_class_partition.items())),
        "strong_witness_independent_target_group_count": strong_witness_independent_groups,
        "semantic_divergence_target_group_count": semantic_divergence_groups,
        "route_divergence_target_group_count": route_divergence_groups,
        "non_strong_examples": multi_form_examples,
        "anomalies": anomalies,
        "next_gate": next_gate,
        "interpretation_contract": {
            "all_1673_occurrences_are_from_the_same_frozen_30_source_skeletons": True,
            "exact_minimum_cover_is_cached_per_target_and_is_experimental_input_generation_only": True,
            "truth_signature_enumeration_is_validation_oracle_only": True,
            "strong_witness_independence_requires_one_actual_normal_form_and_one_micro_route_per_target_group": True,
            "multiple_normal_forms_with_same_truth_is_not_strong_confluence": True,
            "route_divergence_with_same_truth_is_not_semantic_failure": True,
            "all_1673_clean_if_true_is_not_universal_3CNF_coverage": True,
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
