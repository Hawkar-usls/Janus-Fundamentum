#!/usr/bin/env python3
"""Classify where pre-frontier GT double-bridge pairs first enter a state.

The transition-reflection audit shows that every non-root exact-key
complementary double-bridge pair through GT_8 has a unique double-bridge source
pair in the immediately preceding parent post-result.  Therefore branch
restriction, quotient contraction, and child pre-units create no such pair in
the finite traces.

This audit isolates the remaining creation site inside each Policy-0A state:

    entry key K
      -> frozen one-pass Resolution output R
      -> post-unit residual P.

For every complementary double-bridge pair in P it asks:

1. Did a double-bridge source pair already exist in R before post-units?
2. If so, did a double-bridge pair already exist in K?
3. If local Resolution was required, was one side or both sides fresh?
4. What parent safety classes and bridge roles produced each required fresh
   clause?

The script is an exact finite discovery certificate through GT_8.  It does not
claim an arbitrary-n local preservation theorem.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import product
from typing import Iterable

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_double_bridge_transition_birth import (
    enumerate_double_bridges,
    unit_assignments,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]


def residual_sources(
    clauses: Iterable[Clause], assignments: dict[int, bool]
) -> dict[Clause, tuple[Clause, ...]]:
    result: dict[Clause, list[Clause]] = defaultdict(list)
    for clause in clauses:
        residual = reduce_clause(tuple(clause), assignments)
        if residual is not None:
            result[tuple(residual)].append(tuple(clause))
    return {
        residual: tuple(sources)
        for residual, sources in result.items()
    }


def bridge_status(n: int, clause: Clause, literal: int, assignment, pairs):
    structure = safety_class(n, clause, assignment, pairs)
    classification = str(structure["classification"])
    if classification != "COMPONENT_SPANNING":
        return classification, None
    graph = clause_component_graph(n, clause, assignment, pairs)
    bridge = bridge_record(clause, graph, pairs, literal)
    if bridge is None:
        return "SPANNING_NONBRIDGE", None
    return "BRIDGE", bridge


def is_double_bridge_source(
    n: int,
    left: Clause,
    right: Clause,
    pivot: int,
    assignment,
    pairs,
):
    left_status, left_bridge = bridge_status(
        n, left, pivot, assignment, pairs
    )
    right_status, right_bridge = bridge_status(
        n, right, -pivot, assignment, pairs
    )
    if left_bridge is None or right_bridge is None:
        return None
    return {
        "left_status": left_status,
        "right_status": right_status,
        "left_bridge": left_bridge,
        "right_bridge": right_bridge,
    }


def raw_origin_labels(state) -> dict[Clause, frozenset[str]]:
    labels: dict[Clause, set[str]] = defaultdict(set)
    for clause in state["key"]:
        labels[tuple(clause)].add("ENTRY_KEY")
    for event in state.get("resolution_events", ()):
        labels[tuple(event["resolvent"])].add("LOCAL_RESOLVENT")
    assert set(state["resolution_output"]) == set(labels)
    return {clause: frozenset(kinds) for clause, kinds in labels.items()}


def local_events_by_resolvent(state) -> dict[Clause, tuple[dict[str, object], ...]]:
    events: dict[Clause, list[dict[str, object]]] = defaultdict(list)
    for event in state.get("resolution_events", ()):
        events[tuple(event["resolvent"])].append(event)
    return {clause: tuple(items) for clause, items in events.items()}


def event_signature(
    n: int,
    event: dict[str, object],
    eventual_literal: int,
    assignment,
    pairs,
):
    left = tuple(event["left"])
    right = tuple(event["right"])
    event_pivot = int(event["pivot"])
    left_class = str(
        safety_class(n, left, assignment, pairs)["classification"]
    )
    right_class = str(
        safety_class(n, right, assignment, pairs)["classification"]
    )

    literal_roles = []
    for side, parent, classification in (
        ("LEFT", left, left_class),
        ("RIGHT", right, right_class),
    ):
        if eventual_literal not in parent:
            literal_roles.append((side, "ABSENT"))
            continue
        if classification != "COMPONENT_SPANNING":
            literal_roles.append((side, classification))
            continue
        graph = clause_component_graph(n, parent, assignment, pairs)
        bridge = bridge_record(parent, graph, pairs, eventual_literal)
        if bridge is None:
            literal_roles.append((side, "SPANNING_NONBRIDGE"))
        else:
            literal_roles.append((side, f"BRIDGE_{bridge['role']}"))

    return {
        "parent_classes": tuple(sorted((left_class, right_class))),
        "literal_roles": tuple(literal_roles),
        "event_pivot_equals_eventual": event_pivot == abs(eventual_literal),
        "event_pivot": event_pivot,
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    stage_modes: Counter[str] = Counter()
    required_local_sides: Counter[int] = Counter()
    origin_patterns: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    event_parent_classes: Counter[tuple[str, str]] = Counter()
    event_literal_roles: Counter[tuple[tuple[str, str], ...]] = Counter()
    event_pivot_relation: Counter[bool] = Counter()
    post_unit_histogram: Counter[int] = Counter()
    novelty_histogram: Counter[int] = Counter()
    source_multiplicity: Counter[tuple[int, int]] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        post_result = state.get("post_result")
        if post_result is None:
            continue

        before_assignment = context["call_after_pre"][call_id]
        after_assignment = context["state_after_post"][state_id]
        key = tuple(tuple(clause) for clause in state["key"])
        resolution_output = tuple(
            tuple(clause) for clause in state["resolution_output"]
        )
        post = tuple(tuple(clause) for clause in post_result)
        post_units = unit_assignments(state.get("post_units", ()))
        post_unit_histogram[len(post_units)] += 1

        post_pairs = enumerate_double_bridges(
            n, post, after_assignment, pairs
        )
        if not post_pairs:
            continue

        raw_sources = residual_sources(resolution_output, post_units)
        assert set(post) == set(raw_sources)
        origins = raw_origin_labels(state)
        events_by_resolvent = local_events_by_resolvent(state)

        for pair_record in post_pairs:
            counts["post_double_bridge_occurrences"] += 1
            novelty_histogram[novelty] += 1
            pivot = int(pair_record["pivot"])
            post_left = tuple(pair_record["left"])
            post_right = tuple(pair_record["right"])
            assert pair_record["left_bridge"]["role"] == "TAIL_SINGLETON"
            assert pair_record["right_bridge"]["role"] == "TAIL_SINGLETON"
            assert pair_record["left_bridge"]["cut"] != pair_record["right_bridge"]["cut"]

            left_sources = raw_sources[post_left]
            right_sources = raw_sources[post_right]
            source_multiplicity[(len(left_sources), len(right_sources))] += 1

            source_pairs = []
            for left_source, right_source in product(left_sources, right_sources):
                source_pair = is_double_bridge_source(
                    n,
                    left_source,
                    right_source,
                    pivot,
                    before_assignment,
                    pairs,
                )
                if source_pair is not None:
                    source_pairs.append((left_source, right_source, source_pair))

            if not source_pairs:
                mode = "CREATED_BY_POST_UNITS"
                counts["post_unit_created"] += 1
                stage_modes[mode] += 1
                if len(examples) < 100:
                    examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "novelty": novelty,
                        "mode": mode,
                        "pivot": pivot,
                        "post_left": post_left,
                        "post_right": post_right,
                        "post_units": tuple(sorted(post_units.items())),
                        "left_sources": left_sources,
                        "right_sources": right_sources,
                    })
                continue

            # Select a source pair minimizing the number of locally required
            # sides, then lexicographically for deterministic replay.
            def local_cost(item):
                left_source, right_source, _record = item
                left_required = "ENTRY_KEY" not in origins[left_source]
                right_required = "ENTRY_KEY" not in origins[right_source]
                return (
                    int(left_required) + int(right_required),
                    left_source,
                    right_source,
                )

            left_source, right_source, source_pair = min(
                source_pairs, key=local_cost
            )
            left_origin = tuple(sorted(origins[left_source]))
            right_origin = tuple(sorted(origins[right_source]))
            origin_patterns[(left_origin, right_origin)] += 1
            left_local_required = "ENTRY_KEY" not in origins[left_source]
            right_local_required = "ENTRY_KEY" not in origins[right_source]
            local_sides = int(left_local_required) + int(right_local_required)
            required_local_sides[local_sides] += 1

            if local_sides == 0:
                mode = "INHERITED_FROM_ENTRY_KEY"
                counts["entry_inherited"] += 1
            elif local_sides == 1:
                mode = "CREATED_WITH_ONE_LOCAL_SIDE"
                counts["one_local_side"] += 1
            else:
                mode = "CREATED_WITH_TWO_LOCAL_SIDES"
                counts["two_local_sides"] += 1
            stage_modes[mode] += 1

            local_event_details = []
            for source, eventual_literal, required in (
                (left_source, pivot, left_local_required),
                (right_source, -pivot, right_local_required),
            ):
                if not required:
                    continue
                assert source in events_by_resolvent
                signatures = []
                for event in events_by_resolvent[source]:
                    signature = event_signature(
                        n,
                        event,
                        eventual_literal,
                        before_assignment,
                        pairs,
                    )
                    signatures.append(signature)
                    event_parent_classes[signature["parent_classes"]] += 1
                    event_literal_roles[signature["literal_roles"]] += 1
                    event_pivot_relation[
                        bool(signature["event_pivot_equals_eventual"])
                    ] += 1
                local_event_details.append({
                    "source": source,
                    "eventual_literal": eventual_literal,
                    "signatures": tuple(signatures),
                })

            if len(examples) < 100:
                examples.append({
                    "n": n,
                    "state_id": state_id,
                    "call_id": call_id,
                    "novelty": novelty,
                    "mode": mode,
                    "pivot": pivot,
                    "post_left": post_left,
                    "post_right": post_right,
                    "post_units": tuple(sorted(post_units.items())),
                    "source_left": left_source,
                    "source_right": right_source,
                    "source_bridges": (
                        source_pair["left_bridge"],
                        source_pair["right_bridge"],
                    ),
                    "origins": (left_origin, right_origin),
                    "local_events": tuple(local_event_details),
                })

    assert counts["post_double_bridge_occurrences"] > 0
    assert (
        counts["entry_inherited"]
        + counts["one_local_side"]
        + counts["two_local_sides"]
        + counts["post_unit_created"]
        == counts["post_double_bridge_occurrences"]
    )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "stage_modes": tuple(sorted(stage_modes.items())),
        "required_local_sides": tuple(sorted(required_local_sides.items())),
        "origin_patterns": tuple(sorted(origin_patterns.items(), key=repr)),
        "event_parent_classes": tuple(
            sorted(event_parent_classes.items(), key=repr)
        ),
        "event_literal_roles": tuple(
            sorted(event_literal_roles.items(), key=repr)
        ),
        "event_pivot_relation": tuple(sorted(event_pivot_relation.items())),
        "post_unit_histogram": tuple(sorted(post_unit_histogram.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "source_multiplicity": tuple(sorted(source_multiplicity.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_modes: Counter[str] = Counter()
    aggregate_local_sides: Counter[int] = Counter()
    aggregate_origins: Counter[tuple[tuple[str, ...], tuple[str, ...]]] = Counter()
    aggregate_parent_classes: Counter[tuple[str, str]] = Counter()
    aggregate_literal_roles: Counter[tuple[tuple[str, str], ...]] = Counter()
    aggregate_pivot_relation: Counter[bool] = Counter()
    aggregate_post_units: Counter[int] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    aggregate_multiplicity: Counter[tuple[int, int]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_modes.update(dict(data["stage_modes"]))
        aggregate_local_sides.update(dict(data["required_local_sides"]))
        aggregate_origins.update(dict(data["origin_patterns"]))
        aggregate_parent_classes.update(dict(data["event_parent_classes"]))
        aggregate_literal_roles.update(dict(data["event_literal_roles"]))
        aggregate_pivot_relation.update(dict(data["event_pivot_relation"]))
        aggregate_post_units.update(dict(data["post_unit_histogram"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        aggregate_multiplicity.update(dict(data["source_multiplicity"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["stage_modes"],
            data["event_parent_classes"],
            data["event_pivot_relation"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  stage_modes = {data['stage_modes']}")
        print(f"  required_local_sides = {data['required_local_sides']}")
        print(f"  origin_patterns = {data['origin_patterns']}")
        print(f"  event_parent_classes = {data['event_parent_classes']}")
        print(f"  event_literal_roles = {data['event_literal_roles']}")
        print(f"  event_pivot_relation = {data['event_pivot_relation']}")
        print(f"  post_unit_histogram = {data['post_unit_histogram']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  source_multiplicity = {data['source_multiplicity']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["post_double_bridge_occurrences"] > 0
    print("JANUS_GT_DOUBLE_BRIDGE_LOCAL_CREATION = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_STAGE_MODES = {tuple(sorted(aggregate_modes.items()))}")
    print(f"AGGREGATE_REQUIRED_LOCAL_SIDES = {tuple(sorted(aggregate_local_sides.items()))}")
    print(f"AGGREGATE_ORIGIN_PATTERNS = {tuple(sorted(aggregate_origins.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_PARENT_CLASSES = {tuple(sorted(aggregate_parent_classes.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_LITERAL_ROLES = {tuple(sorted(aggregate_literal_roles.items(), key=repr))}")
    print(f"AGGREGATE_EVENT_PIVOT_RELATION = {tuple(sorted(aggregate_pivot_relation.items()))}")
    print(f"AGGREGATE_POST_UNITS = {tuple(sorted(aggregate_post_units.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(f"AGGREGATE_SOURCE_MULTIPLICITY = {tuple(sorted(aggregate_multiplicity.items()))}")
    print(
        "claim_boundary = finite exact local-creation census through GT_8; "
        "arbitrary-n local double-bridge preservation remains open"
    )


if __name__ == "__main__":
    self_test()
