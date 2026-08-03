#!/usr/bin/env python3
"""Corrected all-source unit-conflict provenance for merged-tail births.

The state trace may retain branch child descriptors even when post-local unit
propagation terminates the state before recursion.  Therefore termination is
certified by the absence of any non-null child call, not by an empty children
array.  Conflict itself is certified semantically from the final post-unit
event by the v1 reason-DAG builder.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit
from janus_tear_gt_merged_tail_unit_conflict_provenance import (
    build_reason_certificate,
    semantic_conflict_kind,
)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    raw = raw_audit(n)

    counts: Counter[str] = Counter()
    terminal_labels: Counter[str] = Counter()
    conflict_kinds: Counter[str] = Counter()
    child_descriptor_counts: Counter[int] = Counter()
    executed_child_counts: Counter[int] = Counter()
    unique_state_ids: set[int] = set()
    unique_origin_events: set[tuple[int, int]] = set()
    closure_source_counts: Counter[int] = Counter()
    closure_event_counts: Counter[int] = Counter()
    event_clause_multiplicity: Counter[int] = Counter()
    records = []
    certificate_cache = {}

    for example in raw["fresh_examples"]:
        tail_size, _ = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        counts["fresh_merged_tail_occurrences"] += 1
        state_id = int(example["state_id"])
        event_index = int(example["event_index"])
        event_clause = tuple(example["resolvent"])
        unique_state_ids.add(state_id)
        unique_origin_events.add((state_id, event_index))

        state = policy.states[state_id]
        terminal = str(state["terminal"])
        terminal_labels[terminal] += 1

        children = tuple(state.get("children", ()))
        executed_children = tuple(
            child for child in children if child.get("call") is not None
        )
        child_descriptor_counts[len(children)] += 1
        executed_child_counts[len(executed_children)] += 1
        assert not executed_children

        post_events = tuple(state.get("post_units", ()))
        semantic_kind = semantic_conflict_kind(post_events)
        if state_id not in certificate_cache:
            certificate_cache[state_id] = build_reason_certificate(
                tuple(state["resolution_output"]),
                post_events,
            )
        certificate = certificate_cache[state_id]
        assert certificate["conflict_kind"] == semantic_kind

        conflict_kinds[str(certificate["conflict_kind"])] += 1
        closure_source_counts[int(certificate["closure_source_count"])] += 1
        closure_event_counts[int(certificate["closure_event_count"])] += 1

        root_sources = set(certificate["conflict_root_sources"])
        closure_sources = set(certificate["closure_sources"])
        occurrences_in_output = sum(
            1 for clause in state["resolution_output"]
            if tuple(clause) == event_clause
        )
        event_clause_multiplicity[occurrences_in_output] += 1
        assert occurrences_in_output == 1

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
            "pivot": int(example["pivot"]),
            "bad_literal": int(example["literal"]),
            "endpoint_shape": tuple(example["endpoint_shape"]),
            "event_clause": event_clause,
            "terminal_label": terminal,
            "child_descriptor_count": len(children),
            "executed_child_count": len(executed_children),
            "classification": classification,
            "conflict_kind": certificate["conflict_kind"],
            "unit_event_count": certificate["unit_event_count"],
            "closure_event_count": certificate["closure_event_count"],
            "closure_source_count": certificate["closure_source_count"],
            "conflict_root_sources": certificate["conflict_root_sources"],
        })

    assert counts["fresh_merged_tail_occurrences"] == 18
    assert executed_child_counts == Counter({0: 18})
    assert sum(
        counts[label]
        for label in (
            "DIRECT_CONFLICT_SOURCE",
            "ANCESTOR_CONFLICT_SOURCE",
            "COLOCATED_NONCAUSAL",
        )
    ) == 18

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "terminal_labels": tuple(sorted(terminal_labels.items())),
        "conflict_kinds": tuple(sorted(conflict_kinds.items())),
        "child_descriptor_counts": tuple(sorted(child_descriptor_counts.items())),
        "executed_child_counts": tuple(sorted(executed_child_counts.items())),
        "unique_states": len(unique_state_ids),
        "unique_origin_events": len(unique_origin_events),
        "closure_source_counts": tuple(sorted(closure_source_counts.items())),
        "closure_event_counts": tuple(sorted(closure_event_counts.items())),
        "event_clause_multiplicity": tuple(sorted(event_clause_multiplicity.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    aggregate_conflicts: Counter[str] = Counter()
    aggregate_descriptors: Counter[int] = Counter()
    aggregate_executed: Counter[int] = Counter()
    aggregate_closure_sources: Counter[int] = Counter()
    aggregate_closure_events: Counter[int] = Counter()
    aggregate_multiplicity: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_terminals.update(dict(data["terminal_labels"]))
        aggregate_conflicts.update(dict(data["conflict_kinds"]))
        aggregate_descriptors.update(dict(data["child_descriptor_counts"]))
        aggregate_executed.update(dict(data["executed_child_counts"]))
        aggregate_closure_sources.update(dict(data["closure_source_counts"]))
        aggregate_closure_events.update(dict(data["closure_event_counts"]))
        aggregate_multiplicity.update(dict(data["event_clause_multiplicity"]))
        rows.append({
            "n": n,
            "occurrences": dict(data["counts"]).get(
                "fresh_merged_tail_occurrences", 0
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
            "unique_states": data["unique_states"],
            "unique_origin_events": data["unique_origin_events"],
            "terminal_labels": dict(data["terminal_labels"]),
            "conflict_kinds": dict(data["conflict_kinds"]),
            "child_descriptors": dict(data["child_descriptor_counts"]),
            "executed_children": dict(data["executed_child_counts"]),
        })

    assert aggregate_counts["fresh_merged_tail_occurrences"] == 18
    assert aggregate_executed == Counter({0: 18})
    print("JANUS_GT_MERGED_TAIL_UNIT_CONFLICT_PROVENANCE_V2 = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(aggregate_counts)}")
    print(f"TERMINAL_LABELS = {dict(aggregate_terminals)}")
    print(f"CONFLICT_KINDS = {dict(aggregate_conflicts)}")
    print(f"CHILD_DESCRIPTOR_COUNTS = {dict(aggregate_descriptors)}")
    print(f"EXECUTED_CHILD_COUNTS = {dict(aggregate_executed)}")
    print(f"CLOSURE_SOURCE_COUNTS = {dict(sorted(aggregate_closure_sources.items()))}")
    print(f"CLOSURE_EVENT_COUNTS = {dict(sorted(aggregate_closure_events.items()))}")
    print(f"EVENT_CLAUSE_MULTIPLICITY = {dict(aggregate_multiplicity)}")
    print(
        "claim_boundary = exact finite all-source unit-reason provenance through GT_8; "
        "arbitrary-n merged-tail conflict theorem remains open"
    )


if __name__ == "__main__":
    self_test()
