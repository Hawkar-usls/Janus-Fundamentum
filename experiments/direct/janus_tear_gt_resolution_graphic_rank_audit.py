#!/usr/bin/env python3
"""Measure graphic-rank creation and loss at every Policy-0A Resolution event.

The branch lemma proves that novelty plus clause-graph rank cannot decrease under
branch restriction.  The only remaining operation that creates new clauses is
the deterministic one-pass local Resolution rule.

For every pre-frontier Resolution event this audit records:
- graphic ranks of both parents and the resolvent;
- rank loss relative to the smaller and larger parent;
- component-graph class of all three clauses;
- the frontier score novelty + rank(resolvent) - 1;
- whether the event is an exact first origin of a certified later pre-unit merge;
- whether the resolvent is already a cross-component unit.

This is a census, not an assumed rank inequality.  It deliberately permits rank
loss and reports the exact shapes that must be charged by the transfer theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_pre_unit_recursive_provenance import audit as provenance_audit


def graphic_rank(graph: dict[str, object]) -> int:
    component_count = int(graph["component_count"])
    dsu = DSU(component_count)
    for left, right, _literal in graph["external_edges"]:
        dsu.union(int(left), int(right))
    return component_count - len(
        {dsu.find(component) for component in range(component_count)}
    )


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    dangerous_origins = set()
    provenance = provenance_audit(n)
    for merge in provenance["records"]:
        for path in merge["shortest_paths"]:
            event = path["origin_event"]
            assert event is not None
            dangerous_origins.add(
                (int(event["state_id"]), int(event["event_index"]))
            )

    counts: Counter[str] = Counter()
    rank_shape_histogram: Counter[tuple[int, int, int]] = Counter()
    loss_from_min_histogram: Counter[int] = Counter()
    loss_from_max_histogram: Counter[int] = Counter()
    frontier_score_deficit_histogram: Counter[int] = Counter()
    resolvent_class_histogram: Counter[str] = Counter()
    parent_class_histogram: Counter[tuple[str, str]] = Counter()
    dangerous_score_histogram: Counter[int] = Counter()
    direct_unit_novelty_histogram: Counter[int] = Counter()
    maximum_loss_from_min = 0
    maximum_loss_from_max = 0
    low_score_tree_events = []
    direct_unit_events = []
    dangerous_records = []
    largest_rank_loss_examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        state_id = int(state["id"])

        for event_index, event in enumerate(state.get("resolution_events", [])):
            left = tuple(event["left"])
            right = tuple(event["right"])
            resolvent = tuple(event["resolvent"])
            left_graph = clause_component_graph(n, left, assignment, pairs)
            right_graph = clause_component_graph(n, right, assignment, pairs)
            resolvent_graph = clause_component_graph(
                n, resolvent, assignment, pairs
            )
            left_rank = graphic_rank(left_graph)
            right_rank = graphic_rank(right_graph)
            resolvent_rank = graphic_rank(resolvent_graph)
            parent_min = min(left_rank, right_rank)
            parent_max = max(left_rank, right_rank)
            loss_from_min = parent_min - resolvent_rank
            loss_from_max = parent_max - resolvent_rank
            maximum_loss_from_min = max(maximum_loss_from_min, loss_from_min)
            maximum_loss_from_max = max(maximum_loss_from_max, loss_from_max)

            score = novelty + resolvent_rank - 1
            deficit = target - score
            is_dangerous_origin = (state_id, event_index) in dangerous_origins
            is_cross_component_unit = (
                len(resolvent) == 1
                and resolvent_graph["spanning_tree"]
                and int(resolvent_graph["component_count"]) == 2
            )

            counts["resolution_events"] += 1
            if novelty < target:
                counts["pre_frontier_resolution_events"] += 1
            if loss_from_min > 0:
                counts["rank_loss_below_both_parents"] += 1
            if loss_from_max > 0:
                counts["rank_loss_below_larger_parent"] += 1
            if resolvent_graph["spanning_tree"]:
                counts["spanning_tree_resolvents"] += 1
            if is_dangerous_origin:
                counts["dangerous_origins"] += 1
            if is_cross_component_unit:
                counts["direct_cross_component_units"] += 1

            rank_shape_histogram[(left_rank, right_rank, resolvent_rank)] += 1
            loss_from_min_histogram[loss_from_min] += 1
            loss_from_max_histogram[loss_from_max] += 1
            frontier_score_deficit_histogram[deficit] += 1
            resolvent_class_histogram[str(resolvent_graph["classification"])] += 1
            parent_class_histogram[
                (
                    str(left_graph["classification"]),
                    str(right_graph["classification"]),
                )
            ] += 1

            record = {
                "state_id": state_id,
                "call_id": call_id,
                "event_index": event_index,
                "novelty": novelty,
                "target": target,
                "pivot": int(event["pivot"]),
                "left": left,
                "right": right,
                "resolvent": resolvent,
                "left_rank": left_rank,
                "right_rank": right_rank,
                "resolvent_rank": resolvent_rank,
                "loss_from_min": loss_from_min,
                "loss_from_max": loss_from_max,
                "frontier_score": score,
                "frontier_deficit": deficit,
                "resolvent_class": resolvent_graph["classification"],
                "component_count": resolvent_graph["component_count"],
            }

            if is_dangerous_origin:
                dangerous_score_histogram[score] += 1
                dangerous_records.append(record)
            if is_cross_component_unit:
                direct_unit_novelty_histogram[novelty] += 1
                direct_unit_events.append(record)
            if resolvent_graph["spanning_tree"] and score < target:
                if len(low_score_tree_events) < 20:
                    low_score_tree_events.append(record)
            if loss_from_min == maximum_loss_from_min and loss_from_min > 0:
                if len(largest_rank_loss_examples) < 20:
                    largest_rank_loss_examples.append(record)

    assert counts["dangerous_origins"] == len(dangerous_origins)
    assert all(
        int(record["frontier_score"]) == target
        for record in dangerous_records
    )
    assert all(
        int(record["novelty"]) == target
        for record in direct_unit_events
    )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "rank_shape_histogram": tuple(sorted(rank_shape_histogram.items())),
        "loss_from_min_histogram": tuple(sorted(loss_from_min_histogram.items())),
        "loss_from_max_histogram": tuple(sorted(loss_from_max_histogram.items())),
        "frontier_score_deficit_histogram": tuple(
            sorted(frontier_score_deficit_histogram.items())
        ),
        "resolvent_class_histogram": tuple(sorted(resolvent_class_histogram.items())),
        "parent_class_histogram": tuple(sorted(parent_class_histogram.items())),
        "dangerous_score_histogram": tuple(sorted(dangerous_score_histogram.items())),
        "direct_unit_novelty_histogram": tuple(
            sorted(direct_unit_novelty_histogram.items())
        ),
        "maximum_loss_from_min": maximum_loss_from_min,
        "maximum_loss_from_max": maximum_loss_from_max,
        "low_score_tree_event_count": sum(
            count
            for deficit, count in frontier_score_deficit_histogram.items()
            if deficit > 0
        ),
        "low_score_tree_examples": tuple(low_score_tree_events),
        "direct_unit_events": tuple(direct_unit_events),
        "dangerous_records": tuple(dangerous_records),
        "largest_rank_loss_examples": tuple(largest_rank_loss_examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_loss_min: Counter[int] = Counter()
    aggregate_dangerous_scores: Counter[int] = Counter()
    maximum_loss_min = 0
    maximum_loss_max = 0

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_loss_min.update(dict(data["loss_from_min_histogram"]))
        aggregate_dangerous_scores.update(
            dict(data["dangerous_score_histogram"])
        )
        maximum_loss_min = max(maximum_loss_min, data["maximum_loss_from_min"])
        maximum_loss_max = max(maximum_loss_max, data["maximum_loss_from_max"])
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["maximum_loss_from_min"],
                data["maximum_loss_from_max"],
                data["dangerous_score_histogram"],
                data["direct_unit_novelty_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  loss_from_min_histogram = {data['loss_from_min_histogram']}")
        print(f"  loss_from_max_histogram = {data['loss_from_max_histogram']}")
        print(f"  frontier_score_deficit_histogram = {data['frontier_score_deficit_histogram']}")
        print(f"  resolvent_class_histogram = {data['resolvent_class_histogram']}")
        print(f"  dangerous_score_histogram = {data['dangerous_score_histogram']}")
        print(f"  direct_unit_novelty_histogram = {data['direct_unit_novelty_histogram']}")
        print(f"  maximum_loss_from_min = {data['maximum_loss_from_min']}")
        print(f"  maximum_loss_from_max = {data['maximum_loss_from_max']}")
        print(f"  low_score_tree_examples = {data['low_score_tree_examples']}")
        print(f"  direct_unit_events = {data['direct_unit_events']}")
        print(f"  dangerous_records = {data['dangerous_records']}")
        print(f"  largest_rank_loss_examples = {data['largest_rank_loss_examples']}")

    print("JANUS_GT_RESOLUTION_GRAPHIC_RANK_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_loss_from_min = {tuple(sorted(aggregate_loss_min.items()))}")
    print(f"aggregate_dangerous_scores = {tuple(sorted(aggregate_dangerous_scores.items()))}")
    print(f"maximum_loss_from_min = {maximum_loss_min}")
    print(f"maximum_loss_from_max = {maximum_loss_max}")
    print("claim_boundary = finite Resolution-rank census; no universal inference inequality claimed")


if __name__ == "__main__":
    self_test()
