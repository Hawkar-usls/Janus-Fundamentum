from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g10_wide_fixpoint_forces_alternate_certified_door as r50g10
import janus_trump_r50g22_all_direct5_v7_cycle_realizer_or_rejection as r50g22

GATE = "JANUS_TRUMP_R50G23_DIRECT5_SKELETON_R47J_COLLAPSE_CASCADE_AND_MINIMUM_ANTI_COLLAPSE_DEBT"
EXPECTED_CLEAN_SKELETONS = 30
PIVOT = 1


def canon(formula):
    return r33.canonical_formula(formula)


def max_width(formula):
    return max((len(c) for c in canon(formula)), default=0)


def clean_skeletons_from_frozen_r50g22():
    selected = []
    replayed = 0
    for k in range(2, 8):
        for sign_mask in range(128):
            for geometry in r50g22.GEOMETRIES:
                for rotation in r50g22.ROTATIONS:
                    replayed += 1
                    spec = r50g22.candidate_spec(k, sign_mask, geometry, rotation)
                    f, hmap, designated = r50g22.build_source(k, sign_mask, geometry, rotation)
                    if not r50g10.exact_pre_bve_clean(f):
                        continue
                    micro = r50g4.micro_r33_status(f)
                    direct = r50g4.first_r33_micro_candidate(f)
                    if not (
                        micro["status"] == "IMMEDIATE_BVE_W4_ESCAPE"
                        and direct["kind"] == "PROPOSAL"
                        and direct["rule"] == "BOUNDED_VARIABLE_ELIMINATION"
                        and int(direct["var"]) == PIVOT
                    ):
                        continue
                    selected.append({
                        "spec": spec,
                        "source": f,
                        "source_hash": r50g4.fhash(f),
                        "source_CLV": list(r33.measure(f)),
                        "declared_hub_map": {str(a): int(b) for a, b in sorted(hmap.items())},
                        "designated": designated,
                    })
    if replayed != r50g22.DECLARED_FAMILY_SIZE:
        raise AssertionError(("R50G23_R50G22_FAMILY_REPLAY_COUNT_DRIFT", replayed, r50g22.DECLARED_FAMILY_SIZE))
    if len(selected) != EXPECTED_CLEAN_SKELETONS:
        raise AssertionError(("R50G23_CLEAN_SKELETON_COUNT_DRIFT", len(selected), EXPECTED_CLEAN_SKELETONS))
    return selected


def compact_r33_record(record):
    out = {
        "rule": str(record["rule"]),
        "measure_before": list(record["measure_before"]),
        "measure_after": list(record["measure_after"]),
    }
    for key in (
        "literal", "var", "clause", "blocking_literal", "deleted",
        "witness_subclause", "positive", "negative", "resolvents",
        "removed_clauses", "touched_clauses"
    ):
        if key in record:
            out[key] = record[key]
    return out


def detailed_normalization_replay(forced_formula, official_normalization):
    forced = canon(forced_formula)
    state = forced
    transitions = []
    round_rows = []
    height_bound = r47j.restart_height_bound(forced)
    terminal = None

    for round_index in range(height_bound + 1):
        before = state
        reduced = r33.simplify(before)
        after_r33 = canon(reduced["final_formula"])
        row = {
            "round": int(round_index),
            "before_CLV": list(r33.measure(before)),
            "R33_rule_count": len(reduced["history"]),
            "after_R33_CLV": list(r33.measure(after_r33)),
            "R33_terminal": reduced["terminal"],
        }
        for local_index, record in enumerate(reduced["history"], 1):
            transitions.append({
                "phase": "R33",
                "round": int(round_index),
                "local_index": int(local_index),
                "label": "R33:" + str(record["rule"]),
                "record": compact_r33_record(record),
            })

        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            solved = r42.solve_declared_terminal(after_r33, reduced["terminal"])
            if not solved["verification_pass"]:
                raise AssertionError(("R50G23_TERMINAL_VERIFY_FAIL", solved))
            terminal = str(solved["kind"])
            row["stop"] = terminal
            round_rows.append(row)
            state = after_r33
            break

        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            raise AssertionError(("R50G23_UNEXPECTED_AFFINE_BEFORE_DECLARED_DIRECT_EMPTY", round_index, r33.measure(after_r33)))

        rup = r35b.run_candidate(after_r33)
        rup_replay = r35b.independent_certificate_replay(after_r33, rup)
        if not rup_replay["pass"]:
            raise AssertionError(("R50G23_RUP_REPLAY_FAIL", round_index, rup_replay))
        after_rup = canon(rup["final_formula"])
        row.update({
            "RUP_status": rup["status"],
            "RUP_history_count": len(rup.get("history", [])),
            "after_RUP_CLV": list(r33.measure(after_rup)),
        })
        for local_index, record in enumerate(rup.get("history", []), 1):
            transitions.append({
                "phase": "RUP",
                "round": int(round_index),
                "local_index": int(local_index),
                "label": "RUP:SINGLE_LITERAL_RUP",
                "record": {
                    "source_clause": record["source_clause"],
                    "removed_literal": int(record["removed_literal"]),
                    "strengthened_clause": record["strengthened_clause"],
                    "measure_before": record["measure_before"],
                    "measure_after": record["measure_after"],
                },
            })

        if rup["status"] == "UNSAT_BY_UNIT_PROPAGATION":
            terminal = "RUP_UNSAT"
            row["stop"] = terminal
            round_rows.append(row)
            state = after_rup
            break
        if after_rup != after_r33:
            row["restart"] = True
            round_rows.append(row)
            state = after_rup
            continue

        row["stop"] = "CERTIFIED_NORMALIZATION_FIXPOINT"
        round_rows.append(row)
        state = after_rup
        break
    else:
        raise AssertionError("R50G23_REPLAY_HEIGHT_BOUND_EXHAUSTED")

    official_final = canon(official_normalization["final_formula"])
    if state != official_final:
        raise AssertionError(("R50G23_DETAILED_REPLAY_FINAL_DRIFT", state, official_final))
    if terminal != official_normalization["terminal"]:
        raise AssertionError(("R50G23_DETAILED_REPLAY_TERMINAL_DRIFT", terminal, official_normalization["terminal"]))
    if len(round_rows) != int(official_normalization["round_count"]):
        raise AssertionError(("R50G23_DETAILED_REPLAY_ROUND_COUNT_DRIFT", len(round_rows), official_normalization["round_count"]))

    return {
        "terminal": terminal,
        "rounds": round_rows,
        "transitions": transitions,
        "transition_labels": [x["label"] for x in transitions],
        "final_CLV": list(r33.measure(state)),
    }


def direct_blocking_debt(first_transition):
    phase = str(first_transition["phase"])
    rec = first_transition["record"]
    if phase == "RUP":
        return {
            "debt_class": "DIRECT_ADDITIVE_BLOCK_IMPOSSIBLE_AT_SAME_STATE",
            "reason": "UP_CONFLICT_MONOTONE_UNDER_CLAUSE_ADDITION",
            "minimum_added_clause_count_lower_bound": None,
            "requires_prestate_change_or_nonadditive_modification": True,
        }

    rule = str(rec["rule"])
    if rule == "PURE_LITERAL_AUTARKY":
        l = int(rec["literal"])
        return {
            "debt_class": "OPPOSITE_POLARITY_OCCURRENCE",
            "minimum_added_clause_count_lower_bound": 1,
            "required_literal": -l,
            "required_variable": abs(l),
            "necessary_not_sufficient": True,
        }
    if rule == "BLOCKED_CLAUSE_ELIMINATION":
        l = int(rec["blocking_literal"])
        return {
            "debt_class": "NONTAUTOLOGICAL_OPPOSITE_BLOCKER_SUPPORT",
            "minimum_added_clause_count_lower_bound": 1,
            "required_literal": -l,
            "blocked_clause": rec["clause"],
            "necessary_not_sufficient": True,
        }
    if rule == "BOUNDED_VARIABLE_ELIMINATION":
        x = int(rec["var"])
        return {
            "debt_class": "PIVOT_TOUCH_REQUIRED_FOR_DIRECT_ADDITIVE_BVE_BLOCK",
            "minimum_added_clause_count_lower_bound": 1,
            "required_variable": x,
            "allowed_required_literals": [x, -x],
            "necessary_not_sufficient": True,
        }
    if rule in {
        "TAUTOLOGY_DELETION",
        "UNIT_PROPAGATION_WITH_RECONSTRUCTION_TRACE",
        "SUBSUMPTION",
    }:
        return {
            "debt_class": "DIRECT_ADDITIVE_BLOCK_IMPOSSIBLE_AT_SAME_STATE",
            "reason": rule + "_PERSISTS_UNDER_PURE_CLAUSE_ADDITION",
            "minimum_added_clause_count_lower_bound": None,
            "requires_prestate_change_or_nonadditive_modification": True,
        }
    raise AssertionError(("R50G23_UNKNOWN_FIRST_RULE", rule, rec))


def common_prefix(sequences):
    if not sequences:
        return []
    prefix = list(sequences[0])
    for seq in sequences[1:]:
        n = min(len(prefix), len(seq))
        i = 0
        while i < n and prefix[i] == seq[i]:
            i += 1
        prefix = prefix[:i]
        if not prefix:
            break
    return prefix


def first_transition_shape(step):
    rec = step["record"]
    if step["phase"] == "RUP":
        return {
            "phase": "RUP",
            "removed_variable": abs(int(rec["removed_literal"])),
            "source_width": len(rec["source_clause"]),
            "child_width": len(rec["strengthened_clause"]),
        }
    rule = str(rec["rule"])
    out = {"phase": "R33", "rule": rule}
    if "literal" in rec:
        out["literal_variable"] = abs(int(rec["literal"]))
    if "blocking_literal" in rec:
        out["blocking_variable"] = abs(int(rec["blocking_literal"]))
        out["clause_width"] = len(rec["clause"])
    if "var" in rec:
        out["pivot"] = int(rec["var"])
        out["positive_parent_count"] = len(rec.get("positive", []))
        out["negative_parent_count"] = len(rec.get("negative", []))
        out["resolvent_count"] = len(rec.get("resolvents", []))
    if rule == "SUBSUMPTION":
        out["deleted_width"] = len(rec["deleted"])
        out["witness_width"] = len(rec["witness_subclause"])
    return out


def audit_one_skeleton(item):
    f = canon(item["source"])
    candidate = r47j.macro_candidate_fixpoint(f, PIVOT)
    if candidate is None:
        raise AssertionError(("R50G23_R47J_CANDIDATE_MISSING", item["spec"]))
    replay = r47j.independent_fixpoint_macro_replay(f, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G23_R47J_REPLAY_FAIL", item["spec"], replay))
    norm = candidate["normalization"]
    if norm["terminal"] != "DIRECT_EMPTY_CNF" or canon(norm["final_formula"]):
        raise AssertionError(("R50G23_EXPECTED_DIRECT_EMPTY_DRIFT", item["spec"], norm["terminal"], norm["final_formula"]))
    forced = canon(candidate["DP"]["transformed"])
    detailed = detailed_normalization_replay(forced, norm)
    if not detailed["transitions"]:
        raise AssertionError(("R50G23_EMPTY_CASCADE", item["spec"]))
    first = detailed["transitions"][0]
    return {
        "spec": item["spec"],
        "source_hash": item["source_hash"],
        "source_CLV": item["source_CLV"],
        "forced_DP_CLV": list(r33.measure(forced)),
        "forced_DP_max_width": max_width(forced),
        "R47J_independent_replay_pass": True,
        "terminal": norm["terminal"],
        "round_count": int(norm["round_count"]),
        "restart_count": int(norm["restart_count"]),
        "transition_count": len(detailed["transitions"]),
        "transition_labels": detailed["transition_labels"],
        "first_transition": first,
        "first_transition_shape": first_transition_shape(first),
        "first_transition_direct_blocking_debt": direct_blocking_debt(first),
        "rounds": detailed["rounds"],
    }


def debt_source_lemmas():
    return {
        "PURE_LITERAL_AUTARKY": "to destroy purity by addition, at least one opposite-polarity occurrence is necessary",
        "BLOCKED_CLAUSE_ELIMINATION": "to destroy blockedness by addition, at least one opposite-literal clause with a non-tautological resolvent is necessary",
        "BOUNDED_VARIABLE_ELIMINATION": "a distinct added non-pivot clause preserves or strengthens acceptance; direct additive blocking must touch the pivot",
        "RUP": "an existing UP-conflict certificate remains a conflict after adding clauses",
        "TAUTOLOGY_UNIT_SUBSUMPTION": "the existing local witness persists under pure clause addition",
        "authority": "SOURCE_DEFINITION_NECESSITY_ONLY_NOT_SUFFICIENCY",
    }


def run():
    skeletons = clean_skeletons_from_frozen_r50g22()
    rows = [audit_one_skeleton(item) for item in skeletons]

    first_hist = Counter(row["transition_labels"][0] for row in rows)
    full_sig_hist = Counter(" -> ".join(row["transition_labels"]) for row in rows)
    transition_count_hist = Counter(row["transition_count"] for row in rows)
    restart_hist = Counter(row["restart_count"] for row in rows)
    round_hist = Counter(row["round_count"] for row in rows)
    shapes = Counter(json.dumps(row["first_transition_shape"], sort_keys=True) for row in rows)
    debt_classes = Counter(row["first_transition_direct_blocking_debt"]["debt_class"] for row in rows)
    prefix = common_prefix([row["transition_labels"] for row in rows])

    common_first = prefix[0] if prefix else None
    common_debt = None
    if common_first is not None and len(debt_classes) == 1:
        common_debt = rows[0]["first_transition_direct_blocking_debt"]

    exact_all_same_first = len(first_hist) == 1
    verdict = (
        "THIRTY_CLEAN_DIRECT5_SKELETONS_SHARE_EXACT_FIRST_COLLAPSE_MECHANISM__MINIMUM_DIRECT_BLOCKING_DEBT_EXTRACTED__UNIVERSAL_ALL_DIRECT5_OPEN"
        if exact_all_same_first
        else "THIRTY_CLEAN_DIRECT5_SKELETONS_SPLIT_AT_FIRST_COLLAPSE_TRANSITION__PARTITION_EMITTED__UNIVERSAL_ALL_DIRECT5_OPEN"
    )

    return {
        "gate": GATE,
        "mode": "EXACT_R50G22_30_SKELETON_REPLAY_PLUS_SOURCE_DEFINITION_NECESSARY_DEBT_LEMMAS",
        "selected_source_count": len(rows),
        "r50g22_family_replayed_only_to_recover_exact_set": r50g22.DECLARED_FAMILY_SIZE,
        "no_source_family_expansion": True,
        "all_same_pivot_R47J_terminal_direct_empty": all(row["terminal"] == "DIRECT_EMPTY_CNF" for row in rows),
        "all_independent_R47J_replays_pass": all(row["R47J_independent_replay_pass"] for row in rows),
        "first_transition_histogram": dict(sorted(first_hist.items())),
        "first_transition_shape_histogram": {k: v for k, v in sorted(shapes.items())},
        "first_transition_debt_class_histogram": dict(sorted(debt_classes.items())),
        "longest_common_transition_prefix": prefix,
        "common_first_transition": common_first,
        "common_first_direct_blocking_debt": common_debt,
        "full_cascade_signature_histogram": dict(sorted(full_sig_hist.items())),
        "transition_count_histogram": {str(k): v for k, v in sorted(transition_count_hist.items())},
        "round_count_histogram": {str(k): v for k, v in sorted(round_hist.items())},
        "restart_count_histogram": {str(k): v for k, v in sorted(restart_hist.items())},
        "debt_source_lemmas": debt_source_lemmas(),
        "skeleton_ledgers": rows,
        "critical_next_obligation": (
            "USE_THE_EXACT_COMMON_FIRST_COLLAPSE_MECHANISM_AND_NECESSARY_DEBT_TO_BUILD_OR_RULE_OUT_THE_MINIMUM_ANTI_COLLAPSE_AUGMENTATION_"
            "WHILE_PRESERVING_PRE_BVE_CLEANLINESS_IMMEDIATE_BVE_ESCAPE_AND_ALL_CERTIFIED_DOORS_CLOSED"
        ),
        "verdict": verdict,
        "firewall": {
            "FINITE_30_COMMON_CASCADE_IMPLIES_UNIVERSAL_ALL_DIRECT5": False,
            "NECESSARY_DIRECT_BLOCKING_DEBT_IS_SUFFICIENT_ANTI_COLLAPSE": False,
            "ALL_DIRECT5_V7_HUB_CYCLE_ELIMINATED": False,
            "V7_IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "IMMEDIATE_BVE_CASE_ELIMINATED": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
