#!/usr/bin/env python3
"""Exact finite extinction provenance for all fresh merged-tail births.

The failure-tolerant state census falsified the claim that all 18 occurrences
end in post-unit contradiction.  The exact split through GT_8 is:

- 17 occurrences in post-unit contradictory states with no executed child;
- one GT_4 occurrence in a BRANCH_UNSAT state with two executed children and no
  post-unit events.

For the 17 conflict cases this checker reconstructs the all-source unit-reason
closure and classifies the event resolvent as direct, ancestral, or merely
co-located.  For the branch case it verifies that neither child exact key
contains the same literal as a component-spanning non-tail bridge.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit
from janus_tear_gt_merged_tail_fate_census import child_contains_bad
from janus_tear_gt_merged_tail_state_diagnostic import final_event_class
from janus_tear_gt_merged_tail_unit_conflict_provenance import (
    build_reason_certificate,
)

CONFLICT_FINAL_CLASSES = {
    "OPPOSITE_UNITS_CONFLICT",
    "EMPTY_ON_UNIT_ASSIGNMENT",
}
EXPECTED_MERGED_TAIL = {4: 1, 5: 8, 6: 4, 7: 2, 8: 3}


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    raw = raw_audit(n)
    call_to_state = {
        int(state["entry_call"]): int(state["id"])
        for state in policy.states.values()
    }

    counts: Counter[str] = Counter()
    terminal_labels: Counter[str] = Counter()
    conflict_kinds: Counter[str] = Counter()
    branch_child_outcomes: Counter[str] = Counter()
    closure_source_counts: Counter[int] = Counter()
    closure_event_counts: Counter[int] = Counter()
    event_clause_multiplicity: Counter[int] = Counter()
    unique_conflict_states = set()
    unique_branch_states = set()
    records = []
    certificate_cache = {}

    for example in raw["fresh_examples"]:
        tail_size, _ = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        counts["fresh_merged_tail_occurrences"] += 1
        state_id = int(example["state_id"])
        event_index = int(example["event_index"])
        literal = int(example["literal"])
        event_clause = tuple(example["resolvent"])
        state = policy.states[state_id]
        terminal = str(state["terminal"])
        terminal_labels[terminal] += 1
        post_events = tuple(state.get("post_units", ()))
        final_class = final_event_class(post_events)
        children = tuple(state.get("children", ()))
        executed = tuple(
            child for child in children if child.get("call") is not None
        )

        occurrences_in_output = sum(
            1 for clause in state["resolution_output"]
            if tuple(clause) == event_clause
        )
        event_clause_multiplicity[occurrences_in_output] += 1
        assert occurrences_in_output == 1

        if final_class in CONFLICT_FINAL_CLASSES:
            counts["post_unit_conflict_occurrences"] += 1
            unique_conflict_states.add(state_id)
            assert not executed

            if state_id not in certificate_cache:
                certificate_cache[state_id] = build_reason_certificate(
                    tuple(state["resolution_output"]),
                    post_events,
                )
            certificate = certificate_cache[state_id]
            expected_kind = (
                "OPPOSITE_UNITS"
                if final_class == "OPPOSITE_UNITS_CONFLICT"
                else "EMPTY_ON_UNIT_ASSIGNMENT"
            )
            assert certificate["conflict_kind"] == expected_kind
            conflict_kinds[expected_kind] += 1
            closure_source_counts[int(certificate["closure_source_count"])] += 1
            closure_event_counts[int(certificate["closure_event_count"])] += 1

            root_sources = set(certificate["conflict_root_sources"])
            closure_sources = set(certificate["closure_sources"])
            if event_clause in root_sources:
                classification = "DIRECT_CONFLICT_SOURCE"
            elif event_clause in closure_sources:
                classification = "ANCESTOR_CONFLICT_SOURCE"
            else:
                classification = "COLOCATED_NONCAUSAL"
            counts[classification] += 1

            records.append({
                "n": n,
                "state_id": state_id,
                "call_id": int(example["call_id"]),
                "event_index": event_index,
                "literal": literal,
                "endpoint_shape": tuple(example["endpoint_shape"]),
                "event_clause": event_clause,
                "terminal": terminal,
                "extinction_kind": "POST_UNIT_CONFLICT",
                "conflict_kind": expected_kind,
                "causal_class": classification,
                "closure_source_count": certificate["closure_source_count"],
                "closure_event_count": certificate["closure_event_count"],
            })
            continue

        counts["branch_unsat_occurrences"] += 1
        unique_branch_states.add(state_id)
        assert terminal == "BRANCH_UNSAT"
        assert final_class == "NO_POST_UNITS"
        assert executed

        bad_children = 0
        for child in executed:
            child_call = int(child["call"])
            child_state_id = call_to_state.get(child_call)
            if child_state_id is None:
                branch_child_outcomes["NO_EXACT_KEY"] += 1
                continue
            child_state = policy.states[child_state_id]
            child_assignment = context["call_after_pre"][child_call]
            if child_contains_bad(
                n,
                child_state,
                literal,
                pairs,
                child_assignment,
            ):
                bad_children += 1
                branch_child_outcomes["BAD_EXACT_KEY"] += 1
            else:
                branch_child_outcomes["ABSENT_OR_SAFE"] += 1
        assert bad_children == 0
        counts["branch_extinction_without_bad_child"] += 1

        records.append({
            "n": n,
            "state_id": state_id,
            "call_id": int(example["call_id"]),
            "event_index": event_index,
            "literal": literal,
            "endpoint_shape": tuple(example["endpoint_shape"]),
            "event_clause": event_clause,
            "terminal": terminal,
            "extinction_kind": "BRANCH_UNSAT_WITHOUT_BAD_CHILD",
            "executed_child_calls": tuple(int(child["call"]) for child in executed),
        })

    expected = EXPECTED_MERGED_TAIL[n]
    assert counts["fresh_merged_tail_occurrences"] == expected
    assert counts["post_unit_conflict_occurrences"] + counts[
        "branch_unsat_occurrences"
    ] == expected
    assert branch_child_outcomes.get("BAD_EXACT_KEY", 0) == 0

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "terminal_labels": tuple(sorted(terminal_labels.items())),
        "conflict_kinds": tuple(sorted(conflict_kinds.items())),
        "branch_child_outcomes": tuple(sorted(branch_child_outcomes.items())),
        "closure_source_counts": tuple(sorted(closure_source_counts.items())),
        "closure_event_counts": tuple(sorted(closure_event_counts.items())),
        "event_clause_multiplicity": tuple(sorted(event_clause_multiplicity.items())),
        "unique_conflict_states": len(unique_conflict_states),
        "unique_branch_states": len(unique_branch_states),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    aggregate_conflicts: Counter[str] = Counter()
    aggregate_children: Counter[str] = Counter()
    aggregate_closure_sources: Counter[int] = Counter()
    aggregate_closure_events: Counter[int] = Counter()
    aggregate_multiplicity: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_terminals.update(dict(data["terminal_labels"]))
        aggregate_conflicts.update(dict(data["conflict_kinds"]))
        aggregate_children.update(dict(data["branch_child_outcomes"]))
        aggregate_closure_sources.update(dict(data["closure_source_counts"]))
        aggregate_closure_events.update(dict(data["closure_event_counts"]))
        aggregate_multiplicity.update(dict(data["event_clause_multiplicity"]))
        rows.append({
            "n": n,
            "occurrences": dict(data["counts"]).get(
                "fresh_merged_tail_occurrences", 0
            ),
            "post_unit_conflict": dict(data["counts"]).get(
                "post_unit_conflict_occurrences", 0
            ),
            "branch_unsat": dict(data["counts"]).get(
                "branch_unsat_occurrences", 0
            ),
            "direct": dict(data["counts"]).get(
                "DIRECT_CONFLICT_SOURCE", 0
            ),
            "ancestor": dict(data["counts"]).get(
                "ANCESTOR_CONFLICT_SOURCE", 0
            ),
            "colocated": dict(data["counts"]).get(
                "COLOCATED_NONCAUSAL", 0
            ),
            "unique_conflict_states": data["unique_conflict_states"],
            "unique_branch_states": data["unique_branch_states"],
        })

    assert aggregate_counts["fresh_merged_tail_occurrences"] == 18
    assert aggregate_counts["post_unit_conflict_occurrences"] == 17
    assert aggregate_counts["branch_unsat_occurrences"] == 1
    assert aggregate_counts["branch_extinction_without_bad_child"] == 1
    assert aggregate_children.get("BAD_EXACT_KEY", 0) == 0

    print("JANUS_GT_MERGED_TAIL_EXTINCTION_PROVENANCE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(aggregate_counts)}")
    print(f"TERMINAL_LABELS = {dict(aggregate_terminals)}")
    print(f"CONFLICT_KINDS = {dict(aggregate_conflicts)}")
    print(f"BRANCH_CHILD_OUTCOMES = {dict(aggregate_children)}")
    print(f"CLOSURE_SOURCE_COUNTS = {dict(sorted(aggregate_closure_sources.items()))}")
    print(f"CLOSURE_EVENT_COUNTS = {dict(sorted(aggregate_closure_events.items()))}")
    print(f"EVENT_CLAUSE_MULTIPLICITY = {dict(aggregate_multiplicity)}")
    print(
        "claim_boundary = exact finite extinction provenance through GT_8; "
        "arbitrary-n merged-tail extinction theorem remains open"
    )


if __name__ == "__main__":
    self_test()
