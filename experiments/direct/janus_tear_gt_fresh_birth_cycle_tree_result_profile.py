#!/usr/bin/env python3
"""Profile all finite fresh non-tail bridge births by Gate-A hypotheses.

For every fresh non-tail bridge occurrence reported by the exact GT_4..GT_8
Resolution-birth census, reconstruct the unique mixed parent pair and classify:

- whether the component-spanning parent is a simple in-arborescence;
- whether the other parent has an external directed cycle;
- whether the simple external raw resolvent is a tree/in-arborescence;
- whether the occurrence is one of the non-root immediate-local unshielded
  P-lineages in the complete branch-handoff census.

The script is a finite discovery/falsification certificate.  It does not promote
cycle/tree/tree-result reachability to arbitrary n.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_fresh_bad_bridge_parent_class_certificate import MIXED_PAIR
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as birth_audit
from janus_tear_gt_nonroot_arborescence_exchange_census import (
    arborescence_profile,
    graph_components,
    simple_external_edges,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_unshielded_birth_handoff_census import audit as handoff_audit


def simple_tree(vertex_count: int, edges) -> bool:
    return (
        len(edges) == vertex_count - 1
        and len(graph_components(vertex_count, edges)) == 1
    )


def classify(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    state_by_id = {int(state["id"]): state for state in policy.states.values()}

    handoff_keys = {
        (
            int(item["state_id"]),
            tuple(item["clause"]),
            int(item["literal"]),
        )
        for item in handoff_audit(n)["rows"]
        if int(item["depth"]) > 0
    }

    births = birth_audit(n)
    examples = tuple(births["fresh_examples"])
    expected = int(dict(births["counts"]).get("fresh_non_tail_births", 0))
    assert len(examples) == expected

    counts: Counter[str] = Counter()
    cells: Counter[tuple[bool, bool, bool, bool]] = Counter()
    result_orientations: Counter[str] = Counter()
    tree_shapes: Counter[tuple[int, int, bool]] = Counter()
    unshielded_tree_shapes: Counter[tuple[int, int, bool]] = Counter()
    event_multiplicity: Counter[tuple[int, int]] = Counter()
    rows = []
    violations = []

    for example in examples:
        state_id = int(example["state_id"])
        call_id = int(example["call_id"])
        event_index = int(example["event_index"])
        literal = int(example["literal"])
        state = state_by_id[state_id]
        event = state["resolution_events"][event_index]
        assignment = context["call_after_pre"][call_id]
        left = tuple(event["left"])
        right = tuple(event["right"])
        result = tuple(event["resolvent"])
        clauses = (left, right, result)
        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in clauses
        }
        classes = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in clauses
        }
        unordered = tuple(sorted((classes[left], classes[right])))
        assert unordered == MIXED_PAIR, (n, state_id, event_index, unordered)

        spanning = left if classes[left] == "COMPONENT_SPANNING" else right
        cycle = right if spanning == left else left
        vertex_count = int(graphs[result]["component_count"])
        assert int(graphs[spanning]["component_count"]) == vertex_count
        assert int(graphs[cycle]["component_count"]) == vertex_count

        spanning_records, spanning_edges, spanning_simple = simple_external_edges(
            spanning, graphs[spanning], pairs
        )
        cycle_records, _cycle_edges, _cycle_simple = simple_external_edges(
            cycle, graphs[cycle], pairs
        )
        result_records, result_edges, result_simple = simple_external_edges(
            result, graphs[result], pairs
        )

        spanning_profile = arborescence_profile(spanning_records, vertex_count)
        spanning_is_tree = spanning_simple and spanning_profile is not None
        cycle_orientation = str(
            orientation_class(cycle, graphs[cycle], pairs)["classification"]
        )
        cycle_has_directed_cycle = cycle_orientation == "HAS_DIRECTED_CYCLE"
        result_is_tree = result_simple and simple_tree(vertex_count, result_edges)
        result_profile = (
            arborescence_profile(result_records, vertex_count)
            if result_is_tree
            else None
        )
        result_is_arborescence = result_profile is not None
        key = (state_id, result, literal)
        is_nonroot_unshielded = key in handoff_keys

        cell = (
            spanning_is_tree,
            cycle_has_directed_cycle,
            result_is_tree,
            is_nonroot_unshielded,
        )
        cells[cell] += 1
        counts["fresh_occurrences"] += 1
        counts["spanning_simple_arborescence"] += int(spanning_is_tree)
        counts["cycle_has_directed_cycle"] += int(cycle_has_directed_cycle)
        counts["result_simple_tree"] += int(result_is_tree)
        counts["result_in_arborescence"] += int(result_is_arborescence)
        counts["nonroot_unshielded"] += int(is_nonroot_unshielded)
        event_multiplicity[(state_id, event_index)] += 1
        result_orientations[str(
            orientation_class(result, graphs[result], pairs)["classification"]
        )] += 1

        source_shape = None
        if spanning_profile is not None:
            source_shape = (
                int(spanning_profile["height"]),
                int(spanning_profile["nonstar_count"]),
                bool(spanning_profile["one_subdivision_star"]),
            )
            tree_shapes[source_shape] += 1
            if is_nonroot_unshielded:
                unshielded_tree_shapes[source_shape] += 1

        row = {
            "n": n,
            "state_id": state_id,
            "call_id": call_id,
            "depth": int(state["depth"]),
            "event_index": event_index,
            "pivot": int(event["pivot"]),
            "literal": literal,
            "spanning_parent": spanning,
            "cycle_parent": cycle,
            "result": result,
            "spanning_is_simple_arborescence": spanning_is_tree,
            "spanning_shape": source_shape,
            "cycle_orientation": cycle_orientation,
            "cycle_has_directed_cycle": cycle_has_directed_cycle,
            "result_simple_tree": result_is_tree,
            "result_in_arborescence": result_is_arborescence,
            "result_orientation": str(
                orientation_class(result, graphs[result], pairs)["classification"]
            ),
            "nonroot_unshielded": is_nonroot_unshielded,
            "endpoint_shape": tuple(example["endpoint_shape"]),
        }
        rows.append(row)

        if is_nonroot_unshielded and not (
            spanning_is_tree
            and cycle_has_directed_cycle
            and result_is_tree
            and result_is_arborescence
        ):
            violations.append(row)

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "cells": tuple(sorted(cells.items(), key=repr)),
        "result_orientations": tuple(sorted(result_orientations.items())),
        "tree_shapes": tuple(sorted(tree_shapes.items(), key=repr)),
        "unshielded_tree_shapes": tuple(
            sorted(unshielded_tree_shapes.items(), key=repr)
        ),
        "distinct_events": len(event_multiplicity),
        "multi_occurrence_events": sum(
            1 for value in event_multiplicity.values() if value > 1
        ),
        "rows": tuple(rows),
        "violations": tuple(violations),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_cells: Counter[tuple[bool, bool, bool, bool]] = Counter()
    aggregate_orientations: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[int, int, bool]] = Counter()
    aggregate_unshielded_shapes: Counter[tuple[int, int, bool]] = Counter()
    all_unshielded = []
    total_events = 0
    total_multi = 0

    for n in range(4, 9):
        data = classify(n)
        assert not data["violations"], data["violations"]
        aggregate_counts.update(dict(data["counts"]))
        aggregate_cells.update(dict(data["cells"]))
        aggregate_orientations.update(dict(data["result_orientations"]))
        aggregate_shapes.update(dict(data["tree_shapes"]))
        aggregate_unshielded_shapes.update(dict(data["unshielded_tree_shapes"]))
        total_events += int(data["distinct_events"])
        total_multi += int(data["multi_occurrence_events"])
        all_unshielded.extend(
            row for row in data["rows"] if row["nonroot_unshielded"]
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  cells = {data['cells']}")
        print(f"  result_orientations = {data['result_orientations']}")
        print(f"  tree_shapes = {data['tree_shapes']}")
        print(f"  unshielded_tree_shapes = {data['unshielded_tree_shapes']}")
        print(
            "  unshielded_rows = "
            f"{tuple(row for row in data['rows'] if row['nonroot_unshielded'])}"
        )

    assert aggregate_counts["fresh_occurrences"] == 77
    assert aggregate_counts["nonroot_unshielded"] == 3
    assert len(all_unshielded) == 3
    assert all(
        row["spanning_is_simple_arborescence"]
        and row["cycle_has_directed_cycle"]
        and row["result_simple_tree"]
        and row["result_in_arborescence"]
        for row in all_unshielded
    )

    print("JANUS_GT_FRESH_BIRTH_CYCLE_TREE_RESULT_PROFILE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_CELLS = {tuple(sorted(aggregate_cells.items(), key=repr))}")
    print(
        "AGGREGATE_RESULT_ORIENTATIONS = "
        f"{tuple(sorted(aggregate_orientations.items()))}"
    )
    print(f"AGGREGATE_TREE_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(
        "AGGREGATE_UNSHIELDED_TREE_SHAPES = "
        f"{tuple(sorted(aggregate_unshielded_shapes.items(), key=repr))}"
    )
    print(f"DISTINCT_ORIGIN_EVENTS = {total_events}")
    print(f"MULTI_OCCURRENCE_EVENTS = {total_multi}")
    print(f"UNSHIELDED_ROWS = {tuple(all_unshielded)}")
    print(
        "claim_boundary = complete finite profile of all 77 fresh non-tail "
        "bridge occurrences through GT_8; arbitrary-n cycle/tree/tree-result "
        "reachability remains open"
    )


if __name__ == "__main__":
    self_test()
