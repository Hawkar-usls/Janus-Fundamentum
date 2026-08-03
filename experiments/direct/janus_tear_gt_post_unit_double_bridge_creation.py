#!/usr/bin/env python3
"""Classify every double-bridge pair created by post-unit propagation.

The failure-tolerant stage census found 553 raw post-result double-bridge pairs
through GT_8 which have no double-bridge source pair in the raw Resolution
output.  All are different-cut, and none becomes a newly-created exact-key pair
across the following branch/child-preunit transition.

This checker inspects the unique raw source clauses immediately before the
post-unit batch.  For each eventual pivot side it records:

- source safety class and bridge status before units;
- eventual bridge role after units;
- quotient component counts before and after;
- literal deletion caused by the unit batch;
- whether the unit variables touch the eventual isolated tail component;
- whether zero, one, or two pivot sides were already bridges.

It is a finite theorem-discovery audit.  It asserts exact replay, genuine
post-unit creation, and the independently observed different-cut conclusion,
but no proposed arbitrary-n pattern.
"""

from __future__ import annotations

from collections import Counter
from itertools import product

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_double_bridge_local_creation import bridge_status
from janus_tear_gt_double_bridge_transition_birth import (
    enumerate_double_bridges,
    unit_assignments,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class

Clause = tuple[int, ...]


def residual_sources(clauses, assignments):
    result: dict[Clause, list[Clause]] = {}
    for clause in clauses:
        residual = reduce_clause(tuple(clause), assignments)
        if residual is None:
            continue
        result.setdefault(tuple(residual), []).append(tuple(clause))
    return {
        residual: tuple(sources)
        for residual, sources in result.items()
    }


def source_status(n: int, clause: Clause, literal: int, assignment, pairs):
    status, bridge = bridge_status(n, clause, literal, assignment, pairs)
    structure = safety_class(n, clause, assignment, pairs)
    graph = clause_component_graph(n, clause, assignment, pairs)
    return {
        "status": status,
        "bridge": bridge,
        "classification": str(structure["classification"]),
        "component_count": int(graph["component_count"]),
        "graphic_rank": int(structure["graphic_rank"]),
        "directed_cycle": bool(structure["directed_cycle"]),
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    pre_status_pairs: Counter[tuple[str, str]] = Counter()
    pre_class_pairs: Counter[tuple[str, str]] = Counter()
    pre_bridge_count: Counter[int] = Counter()
    post_role_pairs: Counter[tuple[str, str]] = Counter()
    cut_relation: Counter[str] = Counter()
    component_delta_pairs: Counter[tuple[int, int]] = Counter()
    width_delta_pairs: Counter[tuple[int, int]] = Counter()
    unit_count_histogram: Counter[int] = Counter()
    tail_touch_pairs: Counter[tuple[bool, bool]] = Counter()
    source_multiplicity: Counter[tuple[int, int]] = Counter()
    novelty_histogram: Counter[int] = Counter()
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
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        post = tuple(tuple(clause) for clause in post_result)
        post_units = unit_assignments(state.get("post_units", ()))
        if not post_units:
            continue

        sources = residual_sources(output, post_units)
        assert set(post) == set(sources)
        post_pairs = enumerate_double_bridges(n, post, after_assignment, pairs)

        for record in post_pairs:
            pivot = int(record["pivot"])
            post_left = tuple(record["left"])
            post_right = tuple(record["right"])
            left_sources = sources[post_left]
            right_sources = sources[post_right]
            source_multiplicity[(len(left_sources), len(right_sources))] += 1

            source_combinations = []
            double_source_exists = False
            for left_source, right_source in product(left_sources, right_sources):
                left_info = source_status(
                    n, left_source, pivot, before_assignment, pairs
                )
                right_info = source_status(
                    n, right_source, -pivot, before_assignment, pairs
                )
                source_combinations.append(
                    (left_source, right_source, left_info, right_info)
                )
                if left_info["bridge"] is not None and right_info["bridge"] is not None:
                    double_source_exists = True

            if double_source_exists:
                continue

            counts["post_unit_created_pairs"] += 1
            novelty_histogram[novelty] += 1
            unit_count_histogram[len(post_units)] += 1

            # Deterministic representative: maximize the number of pre-existing
            # bridge sides, then prefer spanning sources, then lexical clauses.
            def source_rank(item):
                left_source, right_source, left_info, right_info = item
                bridge_count = int(left_info["bridge"] is not None) + int(
                    right_info["bridge"] is not None
                )
                spanning_count = int(
                    left_info["classification"] == "COMPONENT_SPANNING"
                ) + int(right_info["classification"] == "COMPONENT_SPANNING")
                return (-bridge_count, -spanning_count, left_source, right_source)

            left_source, right_source, left_info, right_info = min(
                source_combinations, key=source_rank
            )
            statuses = (str(left_info["status"]), str(right_info["status"]))
            classes = tuple(sorted((
                str(left_info["classification"]),
                str(right_info["classification"]),
            )))
            pre_status_pairs[statuses] += 1
            pre_class_pairs[classes] += 1
            bridge_count = int(left_info["bridge"] is not None) + int(
                right_info["bridge"] is not None
            )
            pre_bridge_count[bridge_count] += 1

            left_post_bridge = record["left_bridge"]
            right_post_bridge = record["right_bridge"]
            roles = tuple(sorted((
                str(left_post_bridge["role"]),
                str(right_post_bridge["role"]),
            )))
            post_role_pairs[roles] += 1
            same_cut = left_post_bridge["cut"] == right_post_bridge["cut"]
            cut_relation["SAME_CUT" if same_cut else "DIFFERENT_CUT"] += 1
            assert not same_cut

            left_source_graph = clause_component_graph(
                n, left_source, before_assignment, pairs
            )
            right_source_graph = clause_component_graph(
                n, right_source, before_assignment, pairs
            )
            left_post_graph = record["left_graph"]
            right_post_graph = record["right_graph"]
            component_delta_pairs[(
                int(left_source_graph["component_count"])
                - int(left_post_graph["component_count"]),
                int(right_source_graph["component_count"])
                - int(right_post_graph["component_count"]),
            )] += 1
            width_delta_pairs[(
                len(left_source) - len(post_left),
                len(right_source) - len(post_right),
            )] += 1

            unit_vertices = {
                vertex
                for variable in post_units
                for vertex in pairs[variable]
            }
            left_tail_vertices = set(
                left_post_graph["parts"][int(left_post_bridge["tail"])]
            )
            right_tail_vertices = set(
                right_post_graph["parts"][int(right_post_bridge["tail"])]
            )
            touches = (
                bool(unit_vertices & left_tail_vertices),
                bool(unit_vertices & right_tail_vertices),
            )
            tail_touch_pairs[touches] += 1

            if len(examples) < 140:
                examples.append({
                    "n": n,
                    "state_id": state_id,
                    "call_id": call_id,
                    "novelty": novelty,
                    "pivot": pivot,
                    "post_units": tuple(sorted(post_units.items())),
                    "left_source": left_source,
                    "right_source": right_source,
                    "left_pre": left_info,
                    "right_pre": right_info,
                    "post_left": post_left,
                    "post_right": post_right,
                    "post_roles": roles,
                    "same_cut": same_cut,
                    "left_post_bridge": left_post_bridge,
                    "right_post_bridge": right_post_bridge,
                    "component_deltas": (
                        int(left_source_graph["component_count"])
                        - int(left_post_graph["component_count"]),
                        int(right_source_graph["component_count"])
                        - int(right_post_graph["component_count"]),
                    ),
                    "width_deltas": (
                        len(left_source) - len(post_left),
                        len(right_source) - len(post_right),
                    ),
                    "tail_touches": touches,
                })

    assert counts["post_unit_created_pairs"] > 0
    assert cut_relation["SAME_CUT"] == 0

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "pre_status_pairs": tuple(sorted(pre_status_pairs.items(), key=repr)),
        "pre_class_pairs": tuple(sorted(pre_class_pairs.items(), key=repr)),
        "pre_bridge_count": tuple(sorted(pre_bridge_count.items())),
        "post_role_pairs": tuple(sorted(post_role_pairs.items(), key=repr)),
        "cut_relation": tuple(sorted(cut_relation.items())),
        "component_delta_pairs": tuple(
            sorted(component_delta_pairs.items(), key=repr)
        ),
        "width_delta_pairs": tuple(sorted(width_delta_pairs.items(), key=repr)),
        "unit_count_histogram": tuple(sorted(unit_count_histogram.items())),
        "tail_touch_pairs": tuple(sorted(tail_touch_pairs.items(), key=repr)),
        "source_multiplicity": tuple(sorted(source_multiplicity.items())),
        "novelty_histogram": tuple(sorted(novelty_histogram.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_status: Counter[tuple[str, str]] = Counter()
    aggregate_classes: Counter[tuple[str, str]] = Counter()
    aggregate_bridge_count: Counter[int] = Counter()
    aggregate_roles: Counter[tuple[str, str]] = Counter()
    aggregate_cuts: Counter[str] = Counter()
    aggregate_components: Counter[tuple[int, int]] = Counter()
    aggregate_widths: Counter[tuple[int, int]] = Counter()
    aggregate_units: Counter[int] = Counter()
    aggregate_touches: Counter[tuple[bool, bool]] = Counter()
    aggregate_multiplicity: Counter[tuple[int, int]] = Counter()
    aggregate_novelty: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_status.update(dict(data["pre_status_pairs"]))
        aggregate_classes.update(dict(data["pre_class_pairs"]))
        aggregate_bridge_count.update(dict(data["pre_bridge_count"]))
        aggregate_roles.update(dict(data["post_role_pairs"]))
        aggregate_cuts.update(dict(data["cut_relation"]))
        aggregate_components.update(dict(data["component_delta_pairs"]))
        aggregate_widths.update(dict(data["width_delta_pairs"]))
        aggregate_units.update(dict(data["unit_count_histogram"]))
        aggregate_touches.update(dict(data["tail_touch_pairs"]))
        aggregate_multiplicity.update(dict(data["source_multiplicity"]))
        aggregate_novelty.update(dict(data["novelty_histogram"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["pre_status_pairs"],
            data["pre_bridge_count"],
            data["post_role_pairs"],
            data["component_delta_pairs"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  pre_status_pairs = {data['pre_status_pairs']}")
        print(f"  pre_class_pairs = {data['pre_class_pairs']}")
        print(f"  pre_bridge_count = {data['pre_bridge_count']}")
        print(f"  post_role_pairs = {data['post_role_pairs']}")
        print(f"  cut_relation = {data['cut_relation']}")
        print(f"  component_delta_pairs = {data['component_delta_pairs']}")
        print(f"  width_delta_pairs = {data['width_delta_pairs']}")
        print(f"  unit_count_histogram = {data['unit_count_histogram']}")
        print(f"  tail_touch_pairs = {data['tail_touch_pairs']}")
        print(f"  source_multiplicity = {data['source_multiplicity']}")
        print(f"  novelty_histogram = {data['novelty_histogram']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["post_unit_created_pairs"] == 553
    assert aggregate_cuts == Counter({"DIFFERENT_CUT": 553})
    print("JANUS_GT_POST_UNIT_DOUBLE_BRIDGE_CREATION = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_PRE_STATUS_PAIRS = {tuple(sorted(aggregate_status.items(), key=repr))}")
    print(f"AGGREGATE_PRE_CLASS_PAIRS = {tuple(sorted(aggregate_classes.items(), key=repr))}")
    print(f"AGGREGATE_PRE_BRIDGE_COUNT = {tuple(sorted(aggregate_bridge_count.items()))}")
    print(f"AGGREGATE_POST_ROLE_PAIRS = {tuple(sorted(aggregate_roles.items(), key=repr))}")
    print(f"AGGREGATE_CUT_RELATION = {tuple(sorted(aggregate_cuts.items()))}")
    print(f"AGGREGATE_COMPONENT_DELTAS = {tuple(sorted(aggregate_components.items(), key=repr))}")
    print(f"AGGREGATE_WIDTH_DELTAS = {tuple(sorted(aggregate_widths.items(), key=repr))}")
    print(f"AGGREGATE_UNIT_COUNTS = {tuple(sorted(aggregate_units.items()))}")
    print(f"AGGREGATE_TAIL_TOUCHES = {tuple(sorted(aggregate_touches.items(), key=repr))}")
    print(f"AGGREGATE_SOURCE_MULTIPLICITY = {tuple(sorted(aggregate_multiplicity.items()))}")
    print(f"AGGREGATE_NOVELTY = {tuple(sorted(aggregate_novelty.items()))}")
    print(
        "claim_boundary = finite post-unit creation census through GT_8; "
        "arbitrary-n different-cut preservation remains open"
    )


if __name__ == "__main__":
    self_test()
