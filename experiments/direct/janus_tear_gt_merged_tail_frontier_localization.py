#!/usr/bin/env python3
"""Localize every fresh merged-tail non-tail birth relative to the frontier.

The corrected reason cross-table shows that all 17 post-unit-conflict origins
resolve two binary parents to a unit bad literal.  In the component-spanning
binary parent the bad literal is non-bridge.  Graph-theoretically, a connected
two-edge graph in which an edge is non-bridge must consist of two parallel
edges on exactly two quotient vertices.

This checker measures for all 18 fresh merged-tail births:

- novelty level versus target n-2;
- quotient component count;
- parent and resolvent widths;
- whether both parents contain the bad literal;
- parent safety/orientation classes;
- semantic state fate.

The goal is to determine whether merged-tail births are frontier-local and
therefore incapable of bypassing the earlier n-2 historical joins.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit
from janus_tear_gt_merged_tail_state_diagnostic import final_event_class
from janus_tear_gt_rank_safety_dichotomy import safety_class


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2
    raw = raw_audit(n)

    counts: Counter[str] = Counter()
    novelty_levels: Counter[int] = Counter()
    novelty_gaps: Counter[int] = Counter()
    component_counts: Counter[int] = Counter()
    width_shapes: Counter[tuple[int, int, int]] = Counter()
    safety_shapes: Counter[tuple[str, str]] = Counter()
    orientation_shapes: Counter[tuple[str, str]] = Counter()
    fate_shapes: Counter[str] = Counter()
    bad_parent_counts: Counter[int] = Counter()
    rows = []

    for example in raw["fresh_examples"]:
        tail_size, head_size = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        counts["fresh_merged_tail_occurrences"] += 1
        state_id = int(example["state_id"])
        call_id = int(example["call_id"])
        event_index = int(example["event_index"])
        state = policy.states[state_id]
        event = state["resolution_events"][event_index]
        left = tuple(event["left"])
        right = tuple(event["right"])
        resolvent = tuple(event["resolvent"])
        bad_literal = int(example["literal"])
        assignment = context["call_after_pre"][call_id]

        clauses = (left, right, resolvent)
        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in clauses
        }
        component_count_values = {
            int(graphs[clause]["component_count"])
            for clause in clauses
        }
        assert len(component_count_values) == 1
        component_count = next(iter(component_count_values))
        component_counts[component_count] += 1

        novelty = int(levels[call_id])
        novelty_levels[novelty] += 1
        novelty_gap = target - novelty
        novelty_gaps[novelty_gap] += 1

        width_shape = tuple(sorted((len(left), len(right)))) + (len(resolvent),)
        width_shapes[width_shape] += 1

        safety = tuple(sorted((
            str(safety_class(n, left, assignment, pairs)["classification"]),
            str(safety_class(n, right, assignment, pairs)["classification"]),
        )))
        orientation = tuple(sorted((
            str(orientation_class(left, graphs[left], pairs)["classification"]),
            str(orientation_class(right, graphs[right], pairs)["classification"]),
        )))
        safety_shapes[safety] += 1
        orientation_shapes[orientation] += 1

        parent_count = sum(
            1 for parent in (left, right) if bad_literal in parent
        )
        bad_parent_counts[parent_count] += 1

        fate = final_event_class(tuple(state.get("post_units", ())))
        if fate in ("OPPOSITE_UNITS_CONFLICT", "EMPTY_ON_UNIT_ASSIGNMENT"):
            fate_class = "POST_UNIT_CONFLICT"
        else:
            fate_class = str(state["terminal"])
        fate_shapes[fate_class] += 1

        if novelty == target:
            counts["born_at_target_frontier"] += 1
        elif novelty < target:
            counts["born_before_target_frontier"] += 1
        else:
            counts["born_after_target_frontier"] += 1

        if component_count == 2:
            counts["two_component_births"] += 1

        rows.append({
            "n": n,
            "target": target,
            "state_id": state_id,
            "call_id": call_id,
            "event_index": event_index,
            "novelty": novelty,
            "novelty_gap": novelty_gap,
            "component_count": component_count,
            "endpoint_shape": (int(tail_size), int(head_size)),
            "parent_widths": tuple(sorted((len(left), len(right)))),
            "resolvent_width": len(resolvent),
            "bad_parent_count": parent_count,
            "parent_safety": safety,
            "parent_orientation": orientation,
            "fate": fate_class,
        })

    expected = {4: 1, 5: 8, 6: 4, 7: 2, 8: 3}[n]
    assert counts["fresh_merged_tail_occurrences"] == expected
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "novelty_levels": tuple(sorted(novelty_levels.items())),
        "novelty_gaps": tuple(sorted(novelty_gaps.items())),
        "component_counts": tuple(sorted(component_counts.items())),
        "width_shapes": tuple(sorted(width_shapes.items())),
        "safety_shapes": tuple(sorted(safety_shapes.items())),
        "orientation_shapes": tuple(sorted(orientation_shapes.items())),
        "fate_shapes": tuple(sorted(fate_shapes.items())),
        "bad_parent_counts": tuple(sorted(bad_parent_counts.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_novelty_gaps: Counter[int] = Counter()
    aggregate_components: Counter[int] = Counter()
    aggregate_widths: Counter[tuple[int, int, int]] = Counter()
    aggregate_safety: Counter[tuple[str, str]] = Counter()
    aggregate_orientation: Counter[tuple[str, str]] = Counter()
    aggregate_fates: Counter[str] = Counter()
    aggregate_bad_parents: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_novelty_gaps.update(dict(data["novelty_gaps"]))
        aggregate_components.update(dict(data["component_counts"]))
        aggregate_widths.update(dict(data["width_shapes"]))
        aggregate_safety.update(dict(data["safety_shapes"]))
        aggregate_orientation.update(dict(data["orientation_shapes"]))
        aggregate_fates.update(dict(data["fate_shapes"]))
        aggregate_bad_parents.update(dict(data["bad_parent_counts"]))
        rows.append({
            "n": n,
            "target": data["target"],
            "counts": dict(data["counts"]),
            "novelty_gaps": dict(data["novelty_gaps"]),
            "component_counts": dict(data["component_counts"]),
            "width_shapes": dict(data["width_shapes"]),
            "fates": dict(data["fate_shapes"]),
        })

    assert aggregate_counts["fresh_merged_tail_occurrences"] == 18
    print("JANUS_GT_MERGED_TAIL_FRONTIER_LOCALIZATION = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(aggregate_counts)}")
    print(f"NOVELTY_GAPS = {dict(sorted(aggregate_novelty_gaps.items()))}")
    print(f"COMPONENT_COUNTS = {dict(sorted(aggregate_components.items()))}")
    print(f"WIDTH_SHAPES = {dict(aggregate_widths)}")
    print(f"PARENT_SAFETY = {dict(aggregate_safety)}")
    print(f"PARENT_ORIENTATION = {dict(aggregate_orientation)}")
    print(f"FATES = {dict(aggregate_fates)}")
    print(f"BAD_PARENT_COUNTS = {dict(aggregate_bad_parents)}")
    print(
        "claim_boundary = finite frontier-localization census through GT_8; "
        "arbitrary-n localization and global counting remain open"
    )


if __name__ == "__main__":
    self_test()
