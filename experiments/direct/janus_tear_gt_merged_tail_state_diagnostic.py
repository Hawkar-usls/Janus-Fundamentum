#!/usr/bin/env python3
"""Failure-tolerant state census for all fresh merged-tail local births.

This diagnostic makes no extinction or causality assumption.  For each fresh
local non-tail bridge occurrence with non-singleton oriented tail, it records:

- state terminal label;
- number of child descriptors and executed child calls;
- post-unit event count and final event shape;
- whether the post-unit trace itself ends in a semantic contradiction.

The result decides whether unit-conflict provenance is applicable to all 18
occurrences or only a strict subset.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit


def final_event_class(events) -> str:
    if not events:
        return "NO_POST_UNITS"
    event = events[-1]
    kind = str(event["kind"])
    if kind == "opposite_units":
        units = tuple(int(value) for value in event["units"])
        unit_set = set(units)
        return (
            "OPPOSITE_UNITS_CONFLICT"
            if any(-literal in unit_set for literal in unit_set)
            else "OPPOSITE_UNITS_MALFORMED"
        )
    if kind == "unit":
        return (
            "EMPTY_ON_UNIT_ASSIGNMENT"
            if event.get("after") is None
            else "NONCONFLICT_UNIT_END"
        )
    return f"OTHER_{kind}"


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    raw = raw_audit(n)

    counts: Counter[str] = Counter()
    terminals: Counter[str] = Counter()
    descriptor_counts: Counter[int] = Counter()
    executed_counts: Counter[int] = Counter()
    post_event_counts: Counter[int] = Counter()
    final_classes: Counter[str] = Counter()
    state_shapes: Counter[tuple[str, int, str]] = Counter()
    unique_states = set()
    unique_events = set()
    rows = []

    for example in raw["fresh_examples"]:
        tail_size, head_size = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        counts["fresh_merged_tail_occurrences"] += 1
        state_id = int(example["state_id"])
        event_index = int(example["event_index"])
        state = policy.states[state_id]
        unique_states.add(state_id)
        unique_events.add((state_id, event_index))

        terminal = str(state["terminal"])
        children = tuple(state.get("children", ()))
        executed = tuple(
            child for child in children if child.get("call") is not None
        )
        events = tuple(state.get("post_units", ()))
        final_class = final_event_class(events)

        terminals[terminal] += 1
        descriptor_counts[len(children)] += 1
        executed_counts[len(executed)] += 1
        post_event_counts[len(events)] += 1
        final_classes[final_class] += 1
        state_shapes[(terminal, len(executed), final_class)] += 1

        if final_class in (
            "OPPOSITE_UNITS_CONFLICT",
            "EMPTY_ON_UNIT_ASSIGNMENT",
        ):
            counts["semantic_post_unit_conflict"] += 1
        else:
            counts["no_semantic_post_unit_conflict"] += 1
        if executed:
            counts["has_executed_child"] += 1
        else:
            counts["no_executed_child"] += 1

        rows.append({
            "n": n,
            "state_id": state_id,
            "call_id": int(example["call_id"]),
            "event_index": event_index,
            "pivot": int(example["pivot"]),
            "bad_literal": int(example["literal"]),
            "endpoint_shape": (int(tail_size), int(head_size)),
            "terminal": terminal,
            "child_descriptors": len(children),
            "executed_children": len(executed),
            "child_calls": tuple(
                int(child["call"])
                for child in executed
            ),
            "post_event_count": len(events),
            "final_event_class": final_class,
            "final_event": events[-1] if events else None,
        })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "terminals": tuple(sorted(terminals.items())),
        "descriptor_counts": tuple(sorted(descriptor_counts.items())),
        "executed_counts": tuple(sorted(executed_counts.items())),
        "post_event_counts": tuple(sorted(post_event_counts.items())),
        "final_classes": tuple(sorted(final_classes.items())),
        "state_shapes": tuple(sorted(state_shapes.items(), key=repr)),
        "unique_states": len(unique_states),
        "unique_events": len(unique_events),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_terminals: Counter[str] = Counter()
    aggregate_descriptors: Counter[int] = Counter()
    aggregate_executed: Counter[int] = Counter()
    aggregate_post_events: Counter[int] = Counter()
    aggregate_final: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[str, int, str]] = Counter()
    all_rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_terminals.update(dict(data["terminals"]))
        aggregate_descriptors.update(dict(data["descriptor_counts"]))
        aggregate_executed.update(dict(data["executed_counts"]))
        aggregate_post_events.update(dict(data["post_event_counts"]))
        aggregate_final.update(dict(data["final_classes"]))
        aggregate_shapes.update(dict(data["state_shapes"]))
        all_rows.extend(data["rows"])
        print(f"SIZE_ROW = {{'n': {n}, 'counts': {dict(data['counts'])}, "
              f"'terminals': {dict(data['terminals'])}, "
              f"'executed': {dict(data['executed_counts'])}, "
              f"'final': {dict(data['final_classes'])}, "
              f"'unique_states': {data['unique_states']}, "
              f"'unique_events': {data['unique_events']}}}")

    assert aggregate_counts["fresh_merged_tail_occurrences"] == 18
    print("JANUS_GT_MERGED_TAIL_STATE_DIAGNOSTIC = PASS")
    print(f"COUNTS = {dict(aggregate_counts)}")
    print(f"TERMINALS = {dict(aggregate_terminals)}")
    print(f"CHILD_DESCRIPTOR_COUNTS = {dict(aggregate_descriptors)}")
    print(f"EXECUTED_CHILD_COUNTS = {dict(aggregate_executed)}")
    print(f"POST_EVENT_COUNTS = {dict(aggregate_post_events)}")
    print(f"FINAL_EVENT_CLASSES = {dict(aggregate_final)}")
    print(f"STATE_SHAPES = {dict(aggregate_shapes)}")
    for row in all_rows:
        print(f"ROW = {row}")
    print(
        "claim_boundary = failure-tolerant finite state census through GT_8; "
        "no causality or extinction theorem asserted"
    )


if __name__ == "__main__":
    self_test()
