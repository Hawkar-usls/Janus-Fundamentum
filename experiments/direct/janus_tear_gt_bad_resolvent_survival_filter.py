#!/usr/bin/env python3
"""Filter local non-tail bridge births by survival into a later exact key.

The failure-tolerant local census sees many fresh non-tail bridge literals,
including terminal/frontier clauses that are never eligible as parents in a
later state.  This audit follows only the lineages that actually produce one of
the 62 non-tail bridge occurrences in a subsequent exact cache key.

For every exact-key bad occurrence whose immediate parent post-clause comes
from a local Resolution event, record three stages:

    fresh event resolvent -> parent post-unit residual -> child exact key.

The audit measures endpoint component sizes, bridge roles, branch novelty, and
whether the transition activates the untouched root non-minimality shield.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import (
    EXPECTED_BAD,
    endpoint_sizes,
    parent_map,
    parent_source_classes,
)
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_global_clause_shrink_census import unit_assignments
from janus_tear_gt_rank_safety_dichotomy import safety_class


def classify_size_transition(before, after):
    tail_before, head_before = before
    tail_after, head_after = after
    labels = []
    if tail_after > tail_before:
        labels.append("TAIL_GREW")
    elif tail_after == tail_before:
        labels.append("TAIL_STABLE")
    else:
        labels.append("TAIL_SHRANK")
    if head_after > head_before:
        labels.append("HEAD_GREW")
    elif head_after == head_before:
        labels.append("HEAD_STABLE")
    else:
        labels.append("HEAD_SHRANK")
    return tuple(labels)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2
    parents = parent_map(policy)

    counts: Counter[str] = Counter()
    event_shapes: Counter[tuple[int, int]] = Counter()
    post_shapes: Counter[tuple[int, int]] = Counter()
    child_shapes: Counter[tuple[int, int]] = Counter()
    event_roles: Counter[str] = Counter()
    post_roles: Counter[str] = Counter()
    transition_histogram: Counter[tuple[str, ...]] = Counter()
    novelty_histogram: Counter[int] = Counter()
    pre_unit_histogram: Counter[int] = Counter()
    event_multiplicity_histogram: Counter[int] = Counter()
    records = []

    for child_state in policy.states.values():
        child_call = int(child_state["entry_call"])
        child_novelty = int(levels[child_call])
        if child_novelty > target:
            continue
        child_assignment = context["call_after_pre"][child_call]
        child_key = tuple(child_state["key"])
        child_graphs = {
            clause: clause_component_graph(n, clause, child_assignment, pairs)
            for clause in child_key
        }
        child_classes = {
            clause: str(safety_class(n, clause, child_assignment, pairs)["classification"])
            for clause in child_key
        }

        for clause in child_key:
            if child_classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                literal = int(literal)
                child_bridge = bridge_record(clause, child_graphs[clause], pairs, literal)
                if child_bridge is None or child_bridge["role"] == "TAIL_SINGLETON":
                    continue

                counts["exact_key_bad_occurrences"] += 1
                child_size_record = endpoint_sizes(child_graphs[clause], literal, pairs)
                child_shape = (
                    int(child_size_record["tail_size"]),
                    int(child_size_record["head_size"]),
                )
                assert child_shape[0] == 1 and child_shape[1] >= 2
                child_shapes[child_shape] += 1

                edge = parents[child_call]
                parent_state = policy.states[int(edge["state_id"])]
                parent_call = int(edge["parent_call"])
                parent_assignment = context["state_after_post"][int(edge["state_id"])]
                parent_post = tuple(tuple(item) for item in parent_state["post_result"])
                post_units = unit_assignments(parent_state.get("post_units", []))

                sources = [
                    source
                    for source in parent_post
                    if literal in source
                    and reduce_clause(source, child_assignment) == clause
                    and "IMMEDIATE_LOCAL_RESOLVENT" in parent_source_classes(
                        parent_state, source
                    )
                ]
                if not sources:
                    counts["inherited_only_occurrences"] += 1
                    continue

                counts["immediate_local_occurrences"] += 1
                for source in sources:
                    post_graph = clause_component_graph(
                        n, source, parent_assignment, pairs
                    )
                    post_size_record = endpoint_sizes(post_graph, literal, pairs)
                    post_shape = (
                        int(post_size_record["tail_size"]),
                        int(post_size_record["head_size"]),
                    )
                    post_shapes[post_shape] += 1
                    post_bridge = bridge_record(source, post_graph, pairs, literal)
                    assert post_bridge is not None
                    post_roles[str(post_bridge["role"])] += 1

                    origins = [
                        (event_index, event)
                        for event_index, event in enumerate(
                            parent_state.get("resolution_events", [])
                        )
                        if literal in tuple(event["resolvent"])
                        and reduce_clause(tuple(event["resolvent"]), post_units) == source
                    ]
                    assert origins
                    event_multiplicity_histogram[len(origins)] += 1

                    for event_index, event in origins:
                        event_clause = tuple(event["resolvent"])
                        before_assignment = context["call_after_pre"][parent_call]
                        event_graph = clause_component_graph(
                            n, event_clause, before_assignment, pairs
                        )
                        event_size_record = endpoint_sizes(
                            event_graph, literal, pairs
                        )
                        event_shape = (
                            int(event_size_record["tail_size"]),
                            int(event_size_record["head_size"]),
                        )
                        event_shapes[event_shape] += 1
                        event_bridge = bridge_record(
                            event_clause, event_graph, pairs, literal
                        )
                        assert event_bridge is not None
                        event_roles[str(event_bridge["role"])] += 1

                        event_to_post = classify_size_transition(
                            event_shape, post_shape
                        )
                        post_to_child = classify_size_transition(
                            post_shape, child_shape
                        )
                        transition = (*event_to_post, "THEN", *post_to_child)
                        transition_histogram[transition] += 1
                        novelty_increment = child_novelty - int(levels[parent_call])
                        novelty_histogram[novelty_increment] += 1
                        child_pre_units = tuple(
                            policy.calls[child_call].get("pre_units", [])
                        )
                        pre_unit_histogram[len(child_pre_units)] += 1

                        records.append({
                            "n": n,
                            "parent_state": int(parent_state["id"]),
                            "parent_call": parent_call,
                            "child_state": int(child_state["id"]),
                            "child_call": child_call,
                            "event_index": event_index,
                            "pivot": int(event["pivot"]),
                            "literal": literal,
                            "event_resolvent": event_clause,
                            "post_source": source,
                            "child_clause": clause,
                            "event_role": str(event_bridge["role"]),
                            "post_role": str(post_bridge["role"]),
                            "child_role": str(child_bridge["role"]),
                            "event_shape": event_shape,
                            "post_shape": post_shape,
                            "child_shape": child_shape,
                            "transition": transition,
                            "branch_literal": int(edge["branch_literal"]),
                            "novelty_increment": novelty_increment,
                            "child_pre_unit_count": len(child_pre_units),
                        })

    assert counts["exact_key_bad_occurrences"] == EXPECTED_BAD[n]
    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "event_shapes": tuple(sorted(event_shapes.items())),
        "post_shapes": tuple(sorted(post_shapes.items())),
        "child_shapes": tuple(sorted(child_shapes.items())),
        "event_roles": tuple(sorted(event_roles.items())),
        "post_roles": tuple(sorted(post_roles.items())),
        "transition_histogram": tuple(sorted(transition_histogram.items(), key=repr)),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "pre_unit_histogram": tuple(sorted(pre_unit_histogram.items())),
        "event_multiplicity_histogram": tuple(sorted(event_multiplicity_histogram.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_event_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_post_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_child_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_event_roles: Counter[str] = Counter()
    aggregate_post_roles: Counter[str] = Counter()
    aggregate_transitions: Counter[tuple[str, ...]] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_pre_units: Counter[int] = Counter()
    aggregate_multiplicity: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_event_shapes.update(dict(data["event_shapes"]))
        aggregate_post_shapes.update(dict(data["post_shapes"]))
        aggregate_child_shapes.update(dict(data["child_shapes"]))
        aggregate_event_roles.update(dict(data["event_roles"]))
        aggregate_post_roles.update(dict(data["post_roles"]))
        aggregate_transitions.update(dict(data["transition_histogram"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        aggregate_pre_units.update(dict(data["pre_unit_histogram"]))
        aggregate_multiplicity.update(dict(data["event_multiplicity_histogram"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  event_shapes = {data['event_shapes']}")
        print(f"  post_shapes = {data['post_shapes']}")
        print(f"  child_shapes = {data['child_shapes']}")
        print(f"  event_roles = {data['event_roles']}")
        print(f"  post_roles = {data['post_roles']}")
        print(f"  transition_histogram = {data['transition_histogram']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  pre_unit_histogram = {data['pre_unit_histogram']}")
        print(f"  event_multiplicity_histogram = {data['event_multiplicity_histogram']}")
        print(f"  records = {data['records']}")

    assert aggregate_counts["exact_key_bad_occurrences"] == 62
    assert aggregate_counts["immediate_local_occurrences"] == 42
    assert aggregate_counts["inherited_only_occurrences"] == 20
    print("JANUS_GT_BAD_RESOLVENT_SURVIVAL_FILTER = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_event_shapes = {tuple(sorted(aggregate_event_shapes.items()))}")
    print(f"aggregate_post_shapes = {tuple(sorted(aggregate_post_shapes.items()))}")
    print(f"aggregate_child_shapes = {tuple(sorted(aggregate_child_shapes.items()))}")
    print(f"aggregate_event_roles = {tuple(sorted(aggregate_event_roles.items()))}")
    print(f"aggregate_post_roles = {tuple(sorted(aggregate_post_roles.items()))}")
    print(f"aggregate_transitions = {tuple(sorted(aggregate_transitions.items(), key=repr))}")
    print(f"aggregate_novelty = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"aggregate_pre_units = {tuple(sorted(aggregate_pre_units.items()))}")
    print(f"aggregate_event_multiplicity = {tuple(sorted(aggregate_multiplicity.items()))}")
    print(
        "claim_boundary = finite survival filter through GT_8; "
        "arbitrary-n temporal shielding remains open"
    )


if __name__ == "__main__":
    self_test()
