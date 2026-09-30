#!/usr/bin/env python3
"""Audit the only rank pattern capable of creating an unsafe resolvent.

For fixed Hasse components, an unsafe acyclic low-rank resolvent from two
component-spanning parents must lose one graphic-rank unit relative to both
parents. Therefore the complementary pivot edge is rank-essential in both
parents: deleting it lowers each parent rank. C024 calls this a double-bridge
pivot.

This audit enumerates every frozen parent pair in every pre-frontier Policy-0A
state. It classifies:

- whether the pivot is external and rank-essential in each parent;
- parent and resolvent safety classes;
- resolvent rank loss;
- whether an unsafe candidate exists before applying the policy width filter;
- whether width filtering is responsible for excluding any unsafe candidate.

The exact one-pass pair order and budgets are irrelevant here; all frozen pairs
are enumerated.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_policy0t_trace_certificate import canonical_clause


def graphic_rank(graph: dict[str, object]) -> int:
    component_count = int(graph["component_count"])
    dsu = DSU(component_count)
    for left, right, _literal in graph["external_edges"]:
        dsu.union(int(left), int(right))
    return component_count - len(
        {dsu.find(component) for component in range(component_count)}
    )


def remove_pivot_literal(clause, pivot_literal):
    return tuple(literal for literal in clause if literal != pivot_literal)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    pair_class_histogram: Counter[tuple[str, str, str]] = Counter()
    rank_shape_histogram: Counter[tuple[int, int, int]] = Counter()
    double_bridge_result_histogram: Counter[str] = Counter()
    double_bridge_rank_shape: Counter[tuple[int, int, int]] = Counter()
    unsafe_without_width_examples = []
    double_bridge_examples = []
    minimum_unsafe_width_excess = None
    maximum_unsafe_width_excess = 0

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        width_limit = int(state["width_limit"])
        positive: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        negative: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for clause in sorted(key, key=lambda item: (len(item), item)):
            for literal in clause:
                (positive if literal > 0 else negative)[abs(literal)].append(clause)

        graph_cache = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in key
        }
        rank_cache = {
            clause: graphic_rank(graph)
            for clause, graph in graph_cache.items()
        }
        class_cache = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in key
        }

        for pivot in sorted(set(positive) & set(negative)):
            for left in positive[pivot]:
                for right in negative[pivot]:
                    counts["frozen_pairs"] += 1
                    raw = (set(left) - {pivot}) | (set(right) - {-pivot})
                    if any(-literal in raw for literal in raw):
                        counts["tautological_pairs"] += 1
                        continue
                    resolvent = canonical_clause(raw)
                    if resolvent is None:
                        counts["normalization_rejected_pairs"] += 1
                        continue
                    if not resolvent:
                        counts["empty_resolvents"] += 1
                        continue

                    counts["nonempty_nontautological_pairs"] += 1
                    left_rank = rank_cache[left]
                    right_rank = rank_cache[right]
                    resolvent_graph = clause_component_graph(
                        n, resolvent, assignment, pairs
                    )
                    resolvent_rank = graphic_rank(resolvent_graph)
                    resolvent_structure = safety_class(
                        n, resolvent, assignment, pairs
                    )
                    result_class = str(resolvent_structure["classification"])
                    left_class = class_cache[left]
                    right_class = class_cache[right]
                    pair_class_histogram[(left_class, right_class, result_class)] += 1
                    rank_shape_histogram[(left_rank, right_rank, resolvent_rank)] += 1

                    left_remainder = remove_pivot_literal(left, pivot)
                    right_remainder = remove_pivot_literal(right, -pivot)
                    left_remainder_rank = graphic_rank(
                        clause_component_graph(
                            n, left_remainder, assignment, pairs
                        )
                    )
                    right_remainder_rank = graphic_rank(
                        clause_component_graph(
                            n, right_remainder, assignment, pairs
                        )
                    )
                    left_bridge = left_rank == left_remainder_rank + 1
                    right_bridge = right_rank == right_remainder_rank + 1

                    if left_bridge:
                        counts["left_bridge_pairs"] += 1
                    if right_bridge:
                        counts["right_bridge_pairs"] += 1
                    if left_bridge and right_bridge:
                        counts["double_bridge_pairs"] += 1
                        double_bridge_result_histogram[result_class] += 1
                        double_bridge_rank_shape[
                            (left_rank, right_rank, resolvent_rank)
                        ] += 1
                        if len(double_bridge_examples) < 30:
                            double_bridge_examples.append(
                                {
                                    "n": n,
                                    "state_id": int(state["id"]),
                                    "call_id": call_id,
                                    "novelty": novelty,
                                    "pivot": pivot,
                                    "left": left,
                                    "right": right,
                                    "resolvent": resolvent,
                                    "left_class": left_class,
                                    "right_class": right_class,
                                    "result_class": result_class,
                                    "left_rank": left_rank,
                                    "right_rank": right_rank,
                                    "resolvent_rank": resolvent_rank,
                                    "width": len(resolvent),
                                    "width_limit": width_limit,
                                }
                            )

                    unsafe = result_class == "UNSAFE_ACYCLIC_LOW_RANK"
                    within_width = len(resolvent) <= width_limit
                    if unsafe:
                        counts["unsafe_without_width_filter"] += 1
                        if within_width:
                            counts["unsafe_within_width_filter"] += 1
                        else:
                            counts["unsafe_excluded_by_width"] += 1
                            excess = len(resolvent) - width_limit
                            minimum_unsafe_width_excess = (
                                excess
                                if minimum_unsafe_width_excess is None
                                else min(minimum_unsafe_width_excess, excess)
                            )
                            maximum_unsafe_width_excess = max(
                                maximum_unsafe_width_excess, excess
                            )
                        if len(unsafe_without_width_examples) < 30:
                            unsafe_without_width_examples.append(
                                {
                                    "n": n,
                                    "state_id": int(state["id"]),
                                    "call_id": call_id,
                                    "novelty": novelty,
                                    "pivot": pivot,
                                    "left": left,
                                    "right": right,
                                    "resolvent": resolvent,
                                    "left_class": left_class,
                                    "right_class": right_class,
                                    "left_bridge": left_bridge,
                                    "right_bridge": right_bridge,
                                    "left_rank": left_rank,
                                    "right_rank": right_rank,
                                    "resolvent_rank": resolvent_rank,
                                    "width": len(resolvent),
                                    "width_limit": width_limit,
                                    "within_width": within_width,
                                    "structure": resolvent_structure,
                                }
                            )

    # Any unsafe resolvent from two spanning parents must exhibit the rank-loss
    # pattern captured by double-bridge. The assertion is conditional so other
    # unsafe parent classes, if ever observed, remain explicit data.
    for example in unsafe_without_width_examples:
        if (
            example["left_class"] == "COMPONENT_SPANNING"
            and example["right_class"] == "COMPONENT_SPANNING"
        ):
            assert example["left_bridge"] and example["right_bridge"]

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "pair_class_histogram": tuple(sorted(pair_class_histogram.items())),
        "rank_shape_histogram": tuple(sorted(rank_shape_histogram.items())),
        "double_bridge_result_histogram": tuple(
            sorted(double_bridge_result_histogram.items())
        ),
        "double_bridge_rank_shape": tuple(sorted(double_bridge_rank_shape.items())),
        "minimum_unsafe_width_excess": minimum_unsafe_width_excess,
        "maximum_unsafe_width_excess": maximum_unsafe_width_excess,
        "unsafe_without_width_examples": tuple(unsafe_without_width_examples),
        "double_bridge_examples": tuple(double_bridge_examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_double_results: Counter[str] = Counter()
    unsafe_sizes = []
    double_bridge_sizes = []

    for n in range(4, 9):
        data = audit(n)
        counts = dict(data["counts"])
        aggregate.update(counts)
        aggregate_double_results.update(
            dict(data["double_bridge_result_histogram"])
        )
        if counts.get("unsafe_without_width_filter", 0):
            unsafe_sizes.append(n)
        if counts.get("double_bridge_pairs", 0):
            double_bridge_sizes.append(n)
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["double_bridge_result_histogram"],
                data["minimum_unsafe_width_excess"],
                data["maximum_unsafe_width_excess"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  double_bridge_result_histogram = {data['double_bridge_result_histogram']}")
        print(f"  double_bridge_rank_shape = {data['double_bridge_rank_shape']}")
        print(f"  minimum_unsafe_width_excess = {data['minimum_unsafe_width_excess']}")
        print(f"  maximum_unsafe_width_excess = {data['maximum_unsafe_width_excess']}")
        print(f"  unsafe_without_width_examples = {data['unsafe_without_width_examples']}")
        print(f"  double_bridge_examples = {data['double_bridge_examples']}")

    print("JANUS_GT_DOUBLE_BRIDGE_PIVOT_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(
        "aggregate_double_bridge_results = "
        f"{tuple(sorted(aggregate_double_results.items()))}"
    )
    print(f"unsafe_sizes = {tuple(unsafe_sizes)}")
    print(f"double_bridge_sizes = {tuple(double_bridge_sizes)}")
    print("claim_boundary = finite all-frozen-pair bridge census; asymptotic exclusion remains open")


if __name__ == "__main__":
    self_test()
