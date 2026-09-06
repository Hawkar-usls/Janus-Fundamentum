from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25c_source_preimage_obstruction_forensics as r50g25c

GATE = "JANUS_TRUMP_R50G25D_DYNAMIC_REPLACEMENT_AFTER_SOURCE_NORMALIZED_MINIMUM_JOINT_DEBT"
EXPECTED_GE3_UNIQUE = 991
EXPECTED_GE3_WEIGHTED = 1317
PIVOT = 1


def canon(formula):
    return r50g25c.canon(formula)


def bce_key(row):
    return (tuple(int(x) for x in row["clause"]), int(row["blocking_literal"]))


def bve_key(row):
    return int(row["pivot"])


def run():
    parent = r50g25c.run()
    if parent["ge3_unique_state_count"] != EXPECTED_GE3_UNIQUE:
        raise AssertionError(("R50G25D_PARENT_GE3_UNIQUE_DRIFT", parent["ge3_unique_state_count"]))
    if parent["ge3_weighted_occurrence_count"] != EXPECTED_GE3_WEIGHTED:
        raise AssertionError(("R50G25D_PARENT_GE3_WEIGHTED_DRIFT", parent["ge3_weighted_occurrence_count"]))
    if not parent["all_679_mismatches_explained_by_subsumption_normal_form"]:
        raise AssertionError("R50G25D_REQUIRES_SOURCE_NORMAL_FORM_PARENT")
    if parent["genuine_DP_noncommutation_unique_count"] != 0:
        raise AssertionError("R50G25D_GENUINE_NONCOMMUTATION_PARENT_DRIFT")
    if parent["R47J_replay_failure_unique_count"] != 0:
        raise AssertionError("R50G25D_PARENT_REPLAY_FAILURE_DRIFT")

    r50g25b = r50g25c.r50g25b
    r50g25a = r50g25b.r50g25a
    r50g23 = r50g25a.r50g24.r50g23
    r47j = r50g23.r47j
    r42 = r47j.r45a.r42
    r33 = r50g23.r33

    _p, unique = r50g25b.rebuild_unique_states()
    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}

    seen_unique = 0
    seen_weighted = 0
    first_rule_unique = Counter()
    first_rule_weighted = Counter()
    terminal_unique = Counter()
    terminal_weighted = Counter()
    replacement_class_unique = Counter()
    replacement_class_weighted = Counter()
    dynamic_minimum_unique = Counter()
    dynamic_minimum_weighted = Counter()
    original_bce_status_unique = Counter()
    original_bce_status_weighted = Counter()
    original_bve_status_unique = Counter()
    original_bve_status_weighted = Counter()
    new_bce_count_hist_unique = Counter()
    new_bve_count_hist_unique = Counter()

    all_original_resolved_unique = 0
    all_original_resolved_weighted = 0
    all_original_resolved_but_replacement_unique = 0
    all_original_resolved_but_replacement_weighted = 0
    no_bce_bve_debt_unique = 0
    no_bce_bve_debt_weighted = 0
    source_lift_replay_failure_unique = 0
    source_lift_replay_failure_weighted = 0

    examples = []
    anomalies = []

    for key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        target = canon(entry["forced_formula"])
        cover = r50g25b.exact_minimum_cover(target)
        minimum = int(cover["minimum"])
        if minimum < 3:
            continue

        seen_unique += 1
        count = int(entry["occurrence_count"])
        seen_weighted += count

        witness = entry["witness"]
        source_item = source_by_hash[witness["source_hash"]]
        source = canon(source_item["source"])
        c1 = tuple(int(x) for x in witness["first_clause"])
        c2 = tuple(int(x) for x in witness["second_clause"])
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]
        lifted_source = canon(list(source) + [c1, c2] + lifted)

        dp = r47j.r45a.exact_dp_record(lifted_source, PIVOT)
        if dp is None:
            source_lift_replay_failure_unique += 1
            source_lift_replay_failure_weighted += count
            if len(anomalies) < 20:
                anomalies.append({"state_hash": r50g23.r50g4.fhash(target), "reason": "DP_RECORD_MISSING"})
            continue
        dp_replay = r47j.r45a.independent_dp_replay(lifted_source, dp)
        if not dp_replay.get("pass"):
            source_lift_replay_failure_unique += 1
            source_lift_replay_failure_weighted += count
            if len(anomalies) < 20:
                anomalies.append({"state_hash": r50g23.r50g4.fhash(target), "reason": "DP_REPLAY_FAIL"})
            continue

        actual = canon(dp["transformed"])
        expected = canon(list(target) + lifted)
        normalized_expected = canon(r42.subsumption_minimize(expected))
        if actual != expected and actual != normalized_expected:
            raise AssertionError(("R50G25D_PARENT_SOURCE_NORMAL_FORM_DRIFT", witness))

        macro = r47j.macro_candidate_fixpoint(lifted_source, PIVOT)
        if macro is None:
            raise AssertionError(("R50G25D_MACRO_MISSING", witness))
        replay = r47j.independent_fixpoint_macro_replay(lifted_source, macro)
        if not replay.get("pass"):
            raise AssertionError(("R50G25D_R47J_REPLAY_FAIL", witness))

        target_bces = r50g25a.blocked_candidates(target)
        target_bves = r50g25a.all_bve_candidates(target)
        actual_bces = r50g25a.blocked_candidates(actual)
        actual_bves = r50g25a.all_bve_candidates(actual)

        target_bce_keys = {bce_key(x) for x in target_bces}
        actual_bce_keys = {bce_key(x) for x in actual_bces}
        target_bve_keys = {bve_key(x) for x in target_bves}
        actual_bve_keys = {bve_key(x) for x in actual_bves}

        removed_bce = 0
        unblocked_bce = 0
        persisted_bce = 0
        for row in target_bces:
            clause = tuple(int(x) for x in row["clause"])
            lit = int(row["blocking_literal"])
            if clause not in actual:
                removed_bce += 1
            elif r50g25c.blocked_on(actual, clause, lit):
                persisted_bce += 1
            else:
                unblocked_bce += 1
        persisted_bve = sum(1 for x in target_bve_keys if x in actual_bve_keys)
        resolved_bve = len(target_bve_keys) - persisted_bve

        original_bce_status_unique["REMOVED_BY_NORMAL_FORM"] += removed_bce
        original_bce_status_unique["UNBLOCKED"] += unblocked_bce
        original_bce_status_unique["PERSISTED"] += persisted_bce
        original_bce_status_weighted["REMOVED_BY_NORMAL_FORM"] += removed_bce * count
        original_bce_status_weighted["UNBLOCKED"] += unblocked_bce * count
        original_bce_status_weighted["PERSISTED"] += persisted_bce * count
        original_bve_status_unique["RESOLVED"] += resolved_bve
        original_bve_status_unique["PERSISTED"] += persisted_bve
        original_bve_status_weighted["RESOLVED"] += resolved_bve * count
        original_bve_status_weighted["PERSISTED"] += persisted_bve * count

        original_resolved = persisted_bce == 0 and persisted_bve == 0
        if original_resolved:
            all_original_resolved_unique += 1
            all_original_resolved_weighted += count

        new_bces = actual_bce_keys - target_bce_keys
        new_bves = actual_bve_keys - target_bve_keys
        new_bce_count_hist_unique[len(new_bces)] += 1
        new_bve_count_hist_unique[len(new_bves)] += 1

        debt_present = bool(actual_bces or actual_bves)
        if not debt_present:
            replacement_class = "NO_BCE_BVE_DEBT_AFTER_SOURCE_NORMALIZED_MINIMUM_COVER"
            no_bce_bve_debt_unique += 1
            no_bce_bve_debt_weighted += count
            dynamic_minimum = 0
        else:
            dynamic_cover = r50g25b.exact_minimum_cover(actual)
            dynamic_minimum = int(dynamic_cover["minimum"])
            if original_resolved and (new_bces or new_bves):
                replacement_class = "PURE_DYNAMIC_REPLACEMENT_DEBT"
                all_original_resolved_but_replacement_unique += 1
                all_original_resolved_but_replacement_weighted += count
            elif persisted_bce or persisted_bve:
                if new_bces or new_bves:
                    replacement_class = "PERSISTENT_PLUS_NEW_DYNAMIC_DEBT"
                else:
                    replacement_class = "PERSISTENT_ORIGINAL_DYNAMIC_DEBT"
            else:
                replacement_class = "DYNAMIC_DEBT_OTHER"

        replacement_class_unique[replacement_class] += 1
        replacement_class_weighted[replacement_class] += count
        dynamic_minimum_unique[dynamic_minimum] += 1
        dynamic_minimum_weighted[dynamic_minimum] += count

        first_label, _reduced = r50g25c.first_r33_label(actual)
        first_rule_unique[first_label] += 1
        first_rule_weighted[first_label] += count
        terminal = str(macro["normalization"].get("terminal"))
        terminal_unique[terminal] += 1
        terminal_weighted[terminal] += count

        row = {
            "state_hash": r50g23.r50g4.fhash(target),
            "occurrence_count": count,
            "initial_minimum_cover": minimum,
            "post_lift_CLV": list(r33.measure(actual)),
            "first_R33_rule": first_label,
            "full_R47J_terminal": terminal,
            "original_BCE_count": len(target_bces),
            "original_BCE_removed": removed_bce,
            "original_BCE_unblocked": unblocked_bce,
            "original_BCE_persisted": persisted_bce,
            "original_BVE_count": len(target_bves),
            "original_BVE_resolved": resolved_bve,
            "original_BVE_persisted": persisted_bve,
            "all_original_BCE_BVE_debts_resolved": original_resolved,
            "new_BCE_requirement_count": len(new_bces),
            "new_BVE_requirement_count": len(new_bves),
            "dynamic_replacement_class": replacement_class,
            "dynamic_minimum_binary_incidence_cover": dynamic_minimum,
        }
        if len(examples) < 16:
            examples.append(row)

    if seen_unique != EXPECTED_GE3_UNIQUE:
        raise AssertionError(("R50G25D_GE3_UNIQUE_DRIFT", seen_unique))
    if seen_weighted != EXPECTED_GE3_WEIGHTED:
        raise AssertionError(("R50G25D_GE3_WEIGHTED_DRIFT", seen_weighted))
    if source_lift_replay_failure_unique != 0:
        raise AssertionError(("R50G25D_SOURCE_LIFT_REPLAY_FAILURE", source_lift_replay_failure_unique))

    dynamic_debt_unique = seen_unique - no_bce_bve_debt_unique
    dynamic_debt_weighted = seen_weighted - no_bce_bve_debt_weighted
    next_gate = (
        "R50G25E_SOURCE_REALIZABILITY_OF_DYNAMIC_REPLACEMENT_DEBT"
        if dynamic_debt_unique > 0
        else "R50G25E_POST_DEBT_ESCAPE_DOOR_AUDIT"
    )

    return {
        "gate": GATE,
        "parent_gate": parent["gate"],
        "parent_all_679_mismatches_subsumption_only": parent["all_679_mismatches_explained_by_subsumption_normal_form"],
        "ge3_unique_state_count": seen_unique,
        "ge3_weighted_occurrence_count": seen_weighted,
        "source_lift_replay_failure_unique_count": source_lift_replay_failure_unique,
        "source_lift_replay_failure_weighted_count": source_lift_replay_failure_weighted,
        "replacement_class_unique_partition": dict(sorted(replacement_class_unique.items())),
        "replacement_class_weighted_partition": dict(sorted(replacement_class_weighted.items())),
        "dynamic_BCE_BVE_debt_unique_count": dynamic_debt_unique,
        "dynamic_BCE_BVE_debt_weighted_count": dynamic_debt_weighted,
        "no_BCE_BVE_debt_after_lift_unique_count": no_bce_bve_debt_unique,
        "no_BCE_BVE_debt_after_lift_weighted_count": no_bce_bve_debt_weighted,
        "all_original_BCE_BVE_debts_resolved_unique_count": all_original_resolved_unique,
        "all_original_BCE_BVE_debts_resolved_weighted_count": all_original_resolved_weighted,
        "all_original_resolved_but_replacement_debt_unique_count": all_original_resolved_but_replacement_unique,
        "all_original_resolved_but_replacement_debt_weighted_count": all_original_resolved_but_replacement_weighted,
        "dynamic_minimum_binary_incidence_cover_unique_histogram": {str(k): v for k, v in sorted(dynamic_minimum_unique.items())},
        "dynamic_minimum_binary_incidence_cover_weighted_histogram": {str(k): v for k, v in sorted(dynamic_minimum_weighted.items())},
        "actual_first_R33_rule_unique_partition": dict(sorted(first_rule_unique.items())),
        "actual_first_R33_rule_weighted_partition": dict(sorted(first_rule_weighted.items())),
        "full_R47J_terminal_unique_partition": dict(sorted(terminal_unique.items())),
        "full_R47J_terminal_weighted_partition": dict(sorted(terminal_weighted.items())),
        "original_BCE_requirement_status_unique_totals": dict(sorted(original_bce_status_unique.items())),
        "original_BCE_requirement_status_weighted_totals": dict(sorted(original_bce_status_weighted.items())),
        "original_BVE_requirement_status_unique_totals": dict(sorted(original_bve_status_unique.items())),
        "original_BVE_requirement_status_weighted_totals": dict(sorted(original_bve_status_weighted.items())),
        "new_BCE_requirement_count_unique_histogram": {str(k): v for k, v in sorted(new_bce_count_hist_unique.items())},
        "new_BVE_requirement_count_unique_histogram": {str(k): v for k, v in sorted(new_bve_count_hist_unique.items())},
        "examples": examples,
        "anomalies": anomalies,
        "next_gate": next_gate,
        "interpretation_contract": {
            "dynamic_debt_is_measured_after_actual_DP_subsumption_normal_form": True,
            "one_round_dynamic_debt_is_not_iterated_closure_proof": True,
            "minimum_dynamic_cover_is_static_incidence_only": True,
            "dynamic_debt_presence_is_not_escape_impossibility_proof": True,
            "R47J_terminal_without_intervention_is_not_post_intervention_terminal": True,
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
