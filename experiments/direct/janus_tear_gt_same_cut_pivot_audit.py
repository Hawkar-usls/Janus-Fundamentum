#!/usr/bin/env python3
"""Audit the exact same-cut obstruction for every frozen GT parent pair.

For two component-spanning parent clauses with complementary pivot literals, an
undirected rank-deficient resolvent is possible exactly when the pivot is a
bridge in both parents and deleting it induces the same component bipartition.
The resolvent is structurally unsafe only when the nonpivot directed union is
also acyclic.

This checker enumerates all frozen parent pairs in every pre-frontier Policy-0A
state, independent of one-pass budgets and pair order.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import directed_edges, has_directed_cycle
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_policy0t_trace_certificate import canonical_clause


def graph_rank(component_count: int, edges) -> int:
    dsu = DSU(component_count)
    for left, right in edges:
        dsu.union(left, right)
    return component_count - len(
        {dsu.find(vertex) for vertex in range(component_count)}
    )


def external_edges_without_literal(graph, literal):
    return tuple(
        (int(left), int(right))
        for left, right, edge_literal in graph["external_edges"]
        if int(edge_literal) != literal
    )


def canonical_cut(component_count: int, edges):
    dsu = DSU(component_count)
    for left, right in edges:
        dsu.union(left, right)
    groups: dict[int, set[int]] = defaultdict(set)
    for vertex in range(component_count):
        groups[dsu.find(vertex)].add(vertex)
    parts = tuple(sorted((tuple(sorted(group)) for group in groups.values())))
    if len(parts) != 2:
        return None
    left, right = parts
    return min((left, right), (right, left))


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    same_cut_result_classes: Counter[str] = Counter()
    same_cut_rank_shapes: Counter[tuple[int, int, int]] = Counter()
    different_cut_result_classes: Counter[str] = Counter()
    examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        positive: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        negative: dict[int, list[tuple[int, ...]]] = defaultdict(list)
        for clause in sorted(key, key=lambda item: (len(item), item)):
            for literal in clause:
                (positive if literal > 0 else negative)[abs(literal)].append(clause)

        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in key
        }
        classes = {
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
                    if resolvent is None or not resolvent:
                        counts["empty_or_rejected_pairs"] += 1
                        continue
                    counts["legal_nonempty_pairs"] += 1

                    left_graph = graphs[left]
                    right_graph = graphs[right]
                    component_count = int(left_graph["component_count"])
                    assert component_count == int(right_graph["component_count"])

                    if (
                        classes[left] != "COMPONENT_SPANNING"
                        or classes[right] != "COMPONENT_SPANNING"
                    ):
                        counts["nonspanning_parent_pairs"] += 1
                        continue

                    counts["spanning_parent_pairs"] += 1
                    left_without = external_edges_without_literal(left_graph, pivot)
                    right_without = external_edges_without_literal(right_graph, -pivot)
                    left_rank = graph_rank(component_count, tuple((a, b) for a, b, _ in left_graph["external_edges"]))
                    right_rank = graph_rank(component_count, tuple((a, b) for a, b, _ in right_graph["external_edges"]))
                    left_remainder_rank = graph_rank(component_count, left_without)
                    right_remainder_rank = graph_rank(component_count, right_without)
                    left_bridge = left_remainder_rank == left_rank - 1
                    right_bridge = right_remainder_rank == right_rank - 1

                    if not (left_bridge and right_bridge):
                        counts["not_double_bridge"] += 1
                        continue

                    counts["double_bridge_pairs"] += 1
                    left_cut = canonical_cut(component_count, left_without)
                    right_cut = canonical_cut(component_count, right_without)
                    assert left_cut is not None and right_cut is not None

                    structure = safety_class(n, resolvent, assignment, pairs)
                    result_class = str(structure["classification"])
                    result_graph = clause_component_graph(n, resolvent, assignment, pairs)
                    result_rank = graph_rank(
                        component_count,
                        tuple(
                            (int(a), int(b))
                            for a, b, _literal in result_graph["external_edges"]
                        ),
                    )
                    same_cut = left_cut == right_cut

                    if same_cut:
                        counts["same_cut_double_bridge"] += 1
                        same_cut_result_classes[result_class] += 1
                        same_cut_rank_shapes[(left_rank, right_rank, result_rank)] += 1
                        external, _internal = directed_edges(
                            resolvent, result_graph, pairs
                        )
                        directed_cycle = has_directed_cycle(
                            component_count, external
                        )
                        if directed_cycle:
                            counts["same_cut_with_directed_cycle"] += 1
                        else:
                            counts["same_cut_without_directed_cycle"] += 1
                        if result_class == "UNSAFE_ACYCLIC_LOW_RANK":
                            counts["unsafe_same_cut"] += 1
                    else:
                        counts["different_cut_double_bridge"] += 1
                        different_cut_result_classes[result_class] += 1

                    if len(examples) < 40:
                        examples.append(
                            {
                                "n": n,
                                "state_id": int(state["id"]),
                                "call_id": call_id,
                                "novelty": novelty,
                                "pivot": pivot,
                                "left": left,
                                "right": right,
                                "resolvent": resolvent,
                                "left_cut": left_cut,
                                "right_cut": right_cut,
                                "same_cut": same_cut,
                                "result_class": result_class,
                                "left_rank": left_rank,
                                "right_rank": right_rank,
                                "result_rank": result_rank,
                            }
                        )

    assert counts["unsafe_same_cut"] == 0
    assert counts["same_cut_without_directed_cycle"] == 0

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "same_cut_result_classes": tuple(sorted(same_cut_result_classes.items())),
        "same_cut_rank_shapes": tuple(sorted(same_cut_rank_shapes.items())),
        "different_cut_result_classes": tuple(
            sorted(different_cut_result_classes.items())
        ),
        "examples": tuple(examples),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_same_classes: Counter[str] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_same_classes.update(dict(data["same_cut_result_classes"]))
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["same_cut_result_classes"],
                data["same_cut_rank_shapes"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  same_cut_result_classes = {data['same_cut_result_classes']}")
        print(f"  same_cut_rank_shapes = {data['same_cut_rank_shapes']}")
        print(f"  different_cut_result_classes = {data['different_cut_result_classes']}")
        print(f"  examples = {data['examples']}")

    print("JANUS_GT_SAME_CUT_PIVOT_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_same_cut_classes = {tuple(sorted(aggregate_same_classes.items()))}")
    print("finite_result = every same-cut double-bridge resolvent contains a directed cycle through GT_8")
    print("claim_boundary = finite all-frozen-pair audit; GT-specific directed-cycle theorem remains open")


if __name__ == "__main__":
    self_test()
