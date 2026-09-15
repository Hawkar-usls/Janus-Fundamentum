#!/usr/bin/env python3
"""Trace full producer provenance for every non-root unshielded tail-wing case.

The complete GT_4..GT_8 handoff census finds exactly three non-root unshielded
P-occurrences, all in one GT_8 state and all handled by the proved two-node
tail-wing implication.  This audit reconstructs their exact producer layer:

- call/state/depth/context and relation components;
- deterministic selected variable and complete maximum-frequency set;
- immediate frozen Resolution event(s) producing the post clause;
- parent safety/orientation and direct root-residual labels;
- bad bridge and selected edge in directed vertex coordinates;
- child fates and canonical exact-key admission boundary.

The audit is template extraction only; no arbitrary-n reachability claim is
assumed.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_global_clause_shrink_census import unit_assignments
from janus_tear_gt_nonroot_unshielded_wing_profile import audit as wing_audit
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction
from janus_tear_gt_same_cut_parent_ancestry import (
    direct_root_labels,
    root_minimum_labels,
)


def directed_clause_edges(clause, pairs):
    return tuple(
        (*original_direction(int(literal), pairs), int(literal))
        for literal in clause
    )


def audit(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    pairs = context["pairs"]
    minimum_labels = root_minimum_labels(n, pairs)
    wing = wing_audit(n)

    counts: Counter[str] = Counter()
    event_parent_families: Counter[tuple[str, str]] = Counter()
    event_parent_safety: Counter[tuple[str, str]] = Counter()
    event_parent_orientation: Counter[tuple[str, str]] = Counter()
    event_pivots: Counter[int] = Counter()
    source_root_label_shapes: Counter[tuple[str, ...]] = Counter()
    parent_root_label_shapes: Counter[tuple[str, ...]] = Counter()
    maximum_set_sizes: Counter[int] = Counter()
    selected_ranks: Counter[int] = Counter()
    records = []

    for item in wing["rows"]:
        counts["occurrences"] += 1
        state_id = int(item["state_id"])
        call_id = int(item["call_id"])
        state = policy.states[state_id]
        call = policy.calls[call_id]
        clause = tuple(item["clause"])
        literal = int(item["literal"])
        selected = int(item["selected"])

        before_assignment = context["call_after_pre"][call_id]
        post_assignment = context["state_after_post"][state_id]
        post_units = unit_assignments(state.get("post_units", []))
        assert post_assignment == {**before_assignment, **post_units}

        before_graph = clause_component_graph(
            n, clause, before_assignment, pairs
        )
        post_graph = clause_component_graph(
            n, clause, post_assignment, pairs
        )
        bad_bridge = bridge_record(clause, post_graph, pairs, literal)
        assert bad_bridge is not None
        bad_sizes = endpoint_sizes(post_graph, literal, pairs)

        post = tuple(tuple(candidate) for candidate in state["post_result"])
        frequencies = Counter(
            abs(candidate)
            for candidate_clause in post
            for candidate in candidate_clause
        )
        maximum = max(frequencies.values())
        maximum_variables = tuple(sorted(
            variable
            for variable, frequency in frequencies.items()
            if frequency == maximum
        ))
        assert selected == maximum_variables[0]
        maximum_set_sizes[len(maximum_variables)] += 1
        selected_ranks[maximum_variables.index(selected) + 1] += 1

        origins = []
        for event_index, event in enumerate(state.get("resolution_events", [])):
            event_resolvent = tuple(event["resolvent"])
            if reduce_clause(event_resolvent, post_units) != clause:
                continue
            left = tuple(event["left"])
            right = tuple(event["right"])
            left_class = str(
                safety_class(n, left, before_assignment, pairs)["classification"]
            )
            right_class = str(
                safety_class(n, right, before_assignment, pairs)["classification"]
            )
            left_graph = clause_component_graph(
                n, left, before_assignment, pairs
            )
            right_graph = clause_component_graph(
                n, right, before_assignment, pairs
            )
            left_orientation = str(
                orientation_class(left, left_graph, pairs)["classification"]
            )
            right_orientation = str(
                orientation_class(right, right_graph, pairs)["classification"]
            )
            left_labels = direct_root_labels(
                root, left, before_assignment, minimum_labels
            )
            right_labels = direct_root_labels(
                root, right, before_assignment, minimum_labels
            )
            family = tuple(sorted((
                "DIRECT_ROOT" if left_labels else "DERIVED",
                "DIRECT_ROOT" if right_labels else "DERIVED",
            )))
            safety_pair = tuple(sorted((left_class, right_class)))
            orientation_pair = tuple(sorted((
                left_orientation,
                right_orientation,
            )))
            event_parent_families[family] += 1
            event_parent_safety[safety_pair] += 1
            event_parent_orientation[orientation_pair] += 1
            event_pivots[int(event["pivot"])] += 1
            parent_root_label_shapes[
                tuple(sorted(str(label[0]) for label in (*left_labels, *right_labels)))
            ] += 1

            origins.append(
                {
                    "event_index": event_index,
                    "attempt": int(event["attempt"]),
                    "pivot": int(event["pivot"]),
                    "resolvent": event_resolvent,
                    "left": left,
                    "right": right,
                    "left_safety": left_class,
                    "right_safety": right_class,
                    "left_orientation": left_orientation,
                    "right_orientation": right_orientation,
                    "left_root_labels": left_labels,
                    "right_root_labels": right_labels,
                    "left_edges": directed_clause_edges(left, pairs),
                    "right_edges": directed_clause_edges(right, pairs),
                }
            )

        assert origins
        counts["producing_events"] += len(origins)
        source_labels = direct_root_labels(
            root, clause, post_assignment, minimum_labels
        )
        source_root_label_shapes[
            tuple(sorted(str(label[0]) for label in source_labels))
        ] += 1

        records.append(
            {
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "depth": int(state["depth"]),
                "context": tuple(call["context"]),
                "before_assignment": tuple(sorted(before_assignment.items())),
                "post_units": tuple(state.get("post_units", [])),
                "post_assignment": tuple(sorted(post_assignment.items())),
                "before_parts": tuple(before_graph["parts"]),
                "post_parts": tuple(post_graph["parts"]),
                "clause": clause,
                "clause_edges": directed_clause_edges(clause, pairs),
                "bad_literal": literal,
                "bad_direction": original_direction(literal, pairs),
                "bad_bridge": bad_bridge,
                "bad_sizes": bad_sizes,
                "selected": selected,
                "selected_direction": original_direction(
                    next(candidate for candidate in clause if abs(candidate) == selected),
                    pairs,
                ),
                "selected_frequency": frequencies[selected],
                "maximum_variables": maximum_variables,
                "maximum_frequencies": tuple(
                    (variable, frequencies[variable])
                    for variable in maximum_variables
                ),
                "origins": tuple(origins),
                "children": tuple(item["children"]),
            }
        )

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "event_parent_families": tuple(sorted(event_parent_families.items(), key=repr)),
        "event_parent_safety": tuple(sorted(event_parent_safety.items(), key=repr)),
        "event_parent_orientation": tuple(sorted(event_parent_orientation.items(), key=repr)),
        "event_pivots": tuple(sorted(event_pivots.items())),
        "source_root_label_shapes": tuple(sorted(source_root_label_shapes.items(), key=repr)),
        "parent_root_label_shapes": tuple(sorted(parent_root_label_shapes.items(), key=repr)),
        "maximum_set_sizes": tuple(sorted(maximum_set_sizes.items())),
        "selected_ranks": tuple(sorted(selected_ranks.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_families: Counter[tuple[str, str]] = Counter()
    aggregate_safety: Counter[tuple[str, str]] = Counter()
    aggregate_orientation: Counter[tuple[str, str]] = Counter()
    aggregate_pivots: Counter[int] = Counter()
    aggregate_source_labels: Counter[tuple[str, ...]] = Counter()
    aggregate_parent_labels: Counter[tuple[str, ...]] = Counter()
    aggregate_max_sizes: Counter[int] = Counter()
    aggregate_ranks: Counter[int] = Counter()
    all_records = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_families.update(dict(data["event_parent_families"]))
        aggregate_safety.update(dict(data["event_parent_safety"]))
        aggregate_orientation.update(dict(data["event_parent_orientation"]))
        aggregate_pivots.update(dict(data["event_pivots"]))
        aggregate_source_labels.update(dict(data["source_root_label_shapes"]))
        aggregate_parent_labels.update(dict(data["parent_root_label_shapes"]))
        aggregate_max_sizes.update(dict(data["maximum_set_sizes"]))
        aggregate_ranks.update(dict(data["selected_ranks"]))
        all_records.extend(data["records"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  event_parent_families = {data['event_parent_families']}")
        print(f"  event_parent_safety = {data['event_parent_safety']}")
        print(f"  event_parent_orientation = {data['event_parent_orientation']}")
        print(f"  event_pivots = {data['event_pivots']}")
        print(f"  source_root_label_shapes = {data['source_root_label_shapes']}")
        print(f"  parent_root_label_shapes = {data['parent_root_label_shapes']}")
        print(f"  maximum_set_sizes = {data['maximum_set_sizes']}")
        print(f"  selected_ranks = {data['selected_ranks']}")
        print(f"  records = {data['records']}")

    assert aggregate_counts["occurrences"] == 3
    assert len({(record["state_id"], record["call_id"]) for record in all_records}) == 1
    assert aggregate_ranks == Counter({1: 3})

    print("JANUS_GT_NONROOT_WING_PROVENANCE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_FAMILIES = {tuple(sorted(aggregate_families.items(), key=repr))}")
    print(f"AGGREGATE_SAFETY = {tuple(sorted(aggregate_safety.items(), key=repr))}")
    print(f"AGGREGATE_ORIENTATION = {tuple(sorted(aggregate_orientation.items(), key=repr))}")
    print(f"AGGREGATE_PIVOTS = {tuple(sorted(aggregate_pivots.items()))}")
    print(f"AGGREGATE_SOURCE_LABELS = {tuple(sorted(aggregate_source_labels.items(), key=repr))}")
    print(f"AGGREGATE_PARENT_LABELS = {tuple(sorted(aggregate_parent_labels.items(), key=repr))}")
    print(f"AGGREGATE_MAX_SET_SIZES = {tuple(sorted(aggregate_max_sizes.items()))}")
    print(f"AGGREGATE_SELECTED_RANKS = {tuple(sorted(aggregate_ranks.items()))}")
    print(f"ALL_RECORDS = {tuple(all_records)}")
    print(
        "claim_boundary = exact producer provenance for all non-root wing cases "
        "through GT_8; arbitrary-n wing reachability remains open"
    )


if __name__ == "__main__":
    self_test()
