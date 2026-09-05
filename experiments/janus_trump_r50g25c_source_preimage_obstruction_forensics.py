from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r50g25b_source_realizability_minimum_joint_debt as r50g25b

GATE = "JANUS_TRUMP_R50G25C_SOURCE_PREIMAGE_OBSTRUCTION_FORENSICS"
EXPECTED_GE3_UNIQUE = 991
EXPECTED_EXACT_UNIQUE = 312
EXPECTED_MISMATCH_UNIQUE = 679
EXPECTED_MISMATCH_WEIGHTED = 892
PIVOT = 1


def canon(formula):
    return r50g25b.canon(formula)


def blocked_on(formula, clause, lit):
    formula = canon(formula)
    clause = tuple(clause)
    lit = int(lit)
    if clause not in formula:
        return False
    cset = set(clause)
    for other in formula:
        if -lit not in other:
            continue
        resolvent = (cset - {lit}) | (set(other) - {-lit})
        if not any(-x in resolvent for x in resolvent):
            return False
    return True


def first_r33_label(formula):
    r33 = r50g25b.r50g25a.r50g24.r50g23.r33
    reduced = r33.simplify(canon(formula))
    history = reduced.get("history", [])
    if history:
        return "R33:" + str(history[0]["rule"]), reduced
    return "R33_TERMINAL:" + str(reduced.get("terminal")), reduced


def run():
    parent, unique = r50g25b.rebuild_unique_states()
    r50g25a = r50g25b.r50g25a
    r50g23 = r50g25a.r50g24.r50g23
    r33 = r50g23.r33
    r47j = r50g23.r47j
    r42 = r47j.r45a.r42

    skeletons = r50g23.clean_skeletons_from_frozen_r50g22()
    source_by_hash = {item["source_hash"]: item for item in skeletons}

    exact_unique = 0
    exact_weighted = 0
    mismatch_unique = 0
    mismatch_weighted = 0
    subsumption_only_unique = 0
    subsumption_only_weighted = 0
    genuine_noncommutation_unique = 0
    genuine_noncommutation_weighted = 0
    replay_failure_unique = 0
    replay_failure_weighted = 0

    mismatch_direction_unique = Counter()
    mismatch_direction_weighted = Counter()
    first_rule_unique = Counter()
    first_rule_weighted = Counter()
    full_terminal_unique = Counter()
    full_terminal_weighted = Counter()
    target_removed_clause_hist = Counter()
    cover_removed_clause_hist = Counter()

    bce_resolution_unique = Counter()
    bce_resolution_weighted = Counter()
    bve_resolution_unique = Counter()
    bve_resolution_weighted = Counter()
    all_original_debts_resolved_unique = 0
    all_original_debts_resolved_weighted = 0

    examples = []
    anomalies = []

    ge3_seen = 0
    ge3_weighted = 0

    for key, entry in sorted(unique.items(), key=lambda kv: (kv[1]["forced_CLV"], kv[0])):
        cover = r50g25b.exact_minimum_cover(entry["forced_formula"])
        minimum = int(cover["minimum"])
        if minimum < 3:
            continue
        ge3_seen += 1
        count = int(entry["occurrence_count"])
        ge3_weighted += count

        witness = entry["witness"]
        item = source_by_hash[witness["source_hash"]]
        source = canon(item["source"])
        c1 = tuple(int(x) for x in witness["first_clause"])
        c2 = tuple(int(x) for x in witness["second_clause"])
        lifted = [tuple(int(x) for x in clause) for clause in cover["clauses"]]

        base_source = canon(list(source) + [c1, c2])
        lifted_source = canon(list(base_source) + lifted)
        target = canon(entry["forced_formula"])
        unminimized_expected = canon(list(target) + lifted)

        base_dp = r47j.r45a.exact_dp_record(base_source, PIVOT)
        lifted_dp = r47j.r45a.exact_dp_record(lifted_source, PIVOT)
        if base_dp is None or lifted_dp is None:
            raise AssertionError(("R50G25C_DP_RECORD_MISSING", witness))
        if not r47j.r45a.independent_dp_replay(base_source, base_dp)["pass"]:
            raise AssertionError(("R50G25C_BASE_DP_REPLAY_FAIL", witness))
        if not r47j.r45a.independent_dp_replay(lifted_source, lifted_dp)["pass"]:
            raise AssertionError(("R50G25C_LIFTED_DP_REPLAY_FAIL", witness))

        base_actual = canon(base_dp["transformed"])
        actual = canon(lifted_dp["transformed"])
        if base_actual != target:
            raise AssertionError(("R50G25C_PARENT_TARGET_NOT_BASE_DP", witness))

        if actual == unminimized_expected:
            exact_unique += 1
            exact_weighted += count
            continue

        mismatch_unique += 1
        mismatch_weighted += count

        parents_same = (
            base_dp["positive"] == lifted_dp["positive"]
            and base_dp["negative"] == lifted_dp["negative"]
        )
        resolvents_same = (
            base_dp["full_non_tautological_resolvents"]
            == lifted_dp["full_non_tautological_resolvents"]
        )
        normalized_expected = r42.subsumption_minimize(unminimized_expected)
        normalized_match = canon(normalized_expected) == actual

        target_removed = [c for c in target if c not in actual]
        cover_removed = [c for c in lifted if c not in actual]
        target_removed_clause_hist[len(target_removed)] += 1
        cover_removed_clause_hist[len(cover_removed)] += 1

        cover_subsumes_target = any(
            set(k) <= set(c)
            for c in target_removed
            for k in lifted
        )
        target_subsumes_cover = any(
            set(k) <= set(c)
            for c in cover_removed
            for k in target
        )
        cover_subsumes_cover = any(
            set(a) <= set(b) and a != b
            for b in cover_removed
            for a in lifted
        )
        directions = []
        if cover_subsumes_target:
            directions.append("COVER_SUBSUMES_TARGET")
        if target_subsumes_cover:
            directions.append("TARGET_SUBSUMES_COVER")
        if cover_subsumes_cover:
            directions.append("COVER_SUBSUMES_COVER")
        direction = "+".join(directions) if directions else "NO_DIRECT_TARGET_COVER_DIRECTION"
        mismatch_direction_unique[direction] += 1
        mismatch_direction_weighted[direction] += count

        macro = r47j.macro_candidate_fixpoint(lifted_source, PIVOT)
        replay_ok = False
        if macro is not None:
            replay = r47j.independent_fixpoint_macro_replay(lifted_source, macro)
            replay_ok = bool(replay.get("pass"))

        if parents_same and resolvents_same and normalized_match and replay_ok:
            classification = "SUBSUMPTION_ONLY_NORMAL_FORM_PREIMAGE"
            subsumption_only_unique += 1
            subsumption_only_weighted += count
        elif not replay_ok:
            classification = "R47J_REPLAY_FAILURE"
            replay_failure_unique += 1
            replay_failure_weighted += count
        else:
            classification = "GENUINE_DP_NONCOMMUTATION"
            genuine_noncommutation_unique += 1
            genuine_noncommutation_weighted += count

        target_bces = r50g25a.blocked_candidates(target)
        target_bves = r50g25a.all_bve_candidates(target)
        actual_bve_pivots = {int(row["pivot"]) for row in r50g25a.all_bve_candidates(actual)}

        bce_persisted = 0
        bce_removed = 0
        bce_unblocked = 0
        for req in target_bces:
            clause = tuple(req["clause"])
            lit = int(req["blocking_literal"])
            if clause not in actual:
                bce_removed += 1
            elif blocked_on(actual, clause, lit):
                bce_persisted += 1
            else:
                bce_unblocked += 1
        bve_persisted = 0
        bve_resolved = 0
        for req in target_bves:
            pivot = int(req["pivot"])
            if pivot in actual_bve_pivots:
                bve_persisted += 1
            else:
                bve_resolved += 1

        bce_resolution_unique["REMOVED_BY_NORMAL_FORM"] += bce_removed
        bce_resolution_unique["UNBLOCKED"] += bce_unblocked
        bce_resolution_unique["PERSISTED"] += bce_persisted
        bce_resolution_weighted["REMOVED_BY_NORMAL_FORM"] += bce_removed * count
        bce_resolution_weighted["UNBLOCKED"] += bce_unblocked * count
        bce_resolution_weighted["PERSISTED"] += bce_persisted * count
        bve_resolution_unique["RESOLVED"] += bve_resolved
        bve_resolution_unique["PERSISTED"] += bve_persisted
        bve_resolution_weighted["RESOLVED"] += bve_resolved * count
        bve_resolution_weighted["PERSISTED"] += bve_persisted * count

        all_resolved = bce_persisted == 0 and bve_persisted == 0
        if all_resolved:
            all_original_debts_resolved_unique += 1
            all_original_debts_resolved_weighted += count

        label, reduced = first_r33_label(actual)
        first_rule_unique[label] += 1
        first_rule_weighted[label] += count
        terminal = str(macro["normalization"].get("terminal")) if macro is not None else "NO_MACRO"
        full_terminal_unique[terminal] += 1
        full_terminal_weighted[terminal] += count

        row = {
            "state_hash": r50g23.r50g4.fhash(target),
            "minimum": minimum,
            "occurrence_count": count,
            "classification": classification,
            "parents_same": parents_same,
            "resolvents_same": resolvents_same,
            "normalized_expected_matches_actual": normalized_match,
            "subsumption_direction": direction,
            "target_removed_clause_count": len(target_removed),
            "cover_removed_clause_count": len(cover_removed),
            "original_BCE": {
                "count": len(target_bces),
                "removed": bce_removed,
                "unblocked": bce_unblocked,
                "persisted": bce_persisted,
            },
            "original_BVE": {
                "count": len(target_bves),
                "resolved": bve_resolved,
                "persisted": bve_persisted,
            },
            "all_original_BCE_BVE_debts_resolved": all_resolved,
            "actual_first_R33_rule": label,
            "actual_R33_terminal": reduced.get("terminal"),
            "full_R47J_terminal": terminal,
            "R47J_replay_pass": replay_ok,
        }
        if classification == "SUBSUMPTION_ONLY_NORMAL_FORM_PREIMAGE" and len(examples) < 12:
            examples.append(row)
        if classification != "SUBSUMPTION_ONLY_NORMAL_FORM_PREIMAGE" and len(anomalies) < 20:
            anomalies.append(row)

    if ge3_seen != EXPECTED_GE3_UNIQUE:
        raise AssertionError(("R50G25C_GE3_UNIQUE_DRIFT", ge3_seen))
    if exact_unique != EXPECTED_EXACT_UNIQUE:
        raise AssertionError(("R50G25C_EXACT_UNIQUE_DRIFT", exact_unique))
    if mismatch_unique != EXPECTED_MISMATCH_UNIQUE:
        raise AssertionError(("R50G25C_MISMATCH_UNIQUE_DRIFT", mismatch_unique))
    if mismatch_weighted != EXPECTED_MISMATCH_WEIGHTED:
        raise AssertionError(("R50G25C_MISMATCH_WEIGHTED_DRIFT", mismatch_weighted))

    all_subsumption_only = (
        subsumption_only_unique == EXPECTED_MISMATCH_UNIQUE
        and genuine_noncommutation_unique == 0
        and replay_failure_unique == 0
    )
    next_gate = (
        "R50G25D_DYNAMIC_REPLACEMENT_AFTER_SOURCE_NORMALIZED_MINIMUM_JOINT_DEBT"
        if all_subsumption_only
        else "R50G25D_NONCOMMUTING_DP_PREIMAGE_OBSTRUCTION"
    )

    return {
        "gate": GATE,
        "parent_gate": r50g25b.GATE,
        "ge3_unique_state_count": ge3_seen,
        "ge3_weighted_occurrence_count": ge3_weighted,
        "exact_preimage_unique_count": exact_unique,
        "exact_preimage_weighted_count": exact_weighted,
        "exact_state_mismatch_unique_count": mismatch_unique,
        "exact_state_mismatch_weighted_count": mismatch_weighted,
        "subsumption_only_normal_form_preimage_unique_count": subsumption_only_unique,
        "subsumption_only_normal_form_preimage_weighted_count": subsumption_only_weighted,
        "genuine_DP_noncommutation_unique_count": genuine_noncommutation_unique,
        "genuine_DP_noncommutation_weighted_count": genuine_noncommutation_weighted,
        "R47J_replay_failure_unique_count": replay_failure_unique,
        "R47J_replay_failure_weighted_count": replay_failure_weighted,
        "all_679_mismatches_explained_by_subsumption_normal_form": all_subsumption_only,
        "mismatch_subsumption_direction_unique_partition": dict(sorted(mismatch_direction_unique.items())),
        "mismatch_subsumption_direction_weighted_partition": dict(sorted(mismatch_direction_weighted.items())),
        "target_removed_clause_count_unique_histogram": {str(k): v for k, v in sorted(target_removed_clause_hist.items())},
        "cover_removed_clause_count_unique_histogram": {str(k): v for k, v in sorted(cover_removed_clause_hist.items())},
        "original_BCE_requirement_resolution_unique_totals": dict(sorted(bce_resolution_unique.items())),
        "original_BCE_requirement_resolution_weighted_totals": dict(sorted(bce_resolution_weighted.items())),
        "original_BVE_requirement_resolution_unique_totals": dict(sorted(bve_resolution_unique.items())),
        "original_BVE_requirement_resolution_weighted_totals": dict(sorted(bve_resolution_weighted.items())),
        "mismatch_states_with_all_original_BCE_BVE_debts_resolved_unique_count": all_original_debts_resolved_unique,
        "mismatch_states_with_all_original_BCE_BVE_debts_resolved_weighted_count": all_original_debts_resolved_weighted,
        "actual_first_R33_rule_on_mismatch_unique_partition": dict(sorted(first_rule_unique.items())),
        "actual_first_R33_rule_on_mismatch_weighted_partition": dict(sorted(first_rule_weighted.items())),
        "actual_full_R47J_terminal_on_mismatch_unique_partition": dict(sorted(full_terminal_unique.items())),
        "actual_full_R47J_terminal_on_mismatch_weighted_partition": dict(sorted(full_terminal_weighted.items())),
        "examples": examples,
        "anomalies": anomalies,
        "next_gate": next_gate,
        "interpretation_contract": {
            "subsumption_only_normal_form_preimage_is_exact_state_preimage": False,
            "subsumption_only_normal_form_preimage_is_source_lift_under_actual_DP_semantics": True,
            "original_debt_resolution_is_no_new_escape_proof": False,
            "actual_first_rule_partition_is_dynamic_next_gate_evidence": True,
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
