#!/usr/bin/env python3
"""Classify direct ancestry of every same-cut double-bridge parent pair.

For each pre-frontier frozen pair of component-spanning clauses whose
complementary pivot is a bridge in both parents and induces the same cut, this
audit asks whether each parent clause is directly obtainable by simplifying an
original smart-GT axiom under the current complete entry assignment.

Direct root classes:
- ROOT_NON_MINIMALITY(vertex)
- ROOT_TRANSITIVITY

Clauses with no matching original residual are INHERITED_DERIVED.  The audit
also records orientation classes and the directed-cycle witness in the
resolvent.  It is a one-generation ancestry census, not full proof provenance.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    DSU,
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import (
    directed_edges,
    has_directed_cycle,
    orientation_class,
)
from janus_tear_gt_same_cut_pivot_audit import canonical_cut
from janus_tear_gt_unit_merge_root_ancestry import non_minimality_clauses
from janus_tear_policy0t_trace_certificate import canonical_clause


def graph_rank(component_count: int, edges) -> int:
    dsu = DSU(component_count)
    for left, right in edges:
        dsu.union(left, right)
    return component_count - len(
        {dsu.find(vertex) for vertex in range(component_count)}
    )


def root_minimum_labels(n, pairs):
    minimum = non_minimality_clauses(n, pairs)
    result = {}
    for vertex, clause in enumerate(sorted(minimum)):
        result[clause] = vertex
    # The sorted order above is not guaranteed to equal vertex order. Recover
    # the target vertex by finding the unique vertex touched by every literal.
    corrected = {}
    for clause in minimum:
        touched = []
        for candidate in range(n):
            if all(candidate in pairs[abs(literal)] for literal in clause):
                touched.append(candidate)
        assert len(touched) == 1
        corrected[clause] = touched[0]
    return corrected


def direct_root_labels(root, clause, assignment, minimum_labels):
    labels = []
    for root_clause in root:
        if reduce_clause(root_clause, assignment) != clause:
            continue
        if root_clause in minimum_labels:
            labels.append(("ROOT_NON_MINIMALITY", minimum_labels[root_clause], root_clause))
        else:
            labels.append(("ROOT_TRANSITIVITY", None, root_clause))
    if not labels:
        return (("INHERITED_DERIVED", None, None),)
    return tuple(labels)


def external_without_literal(graph, literal):
    return tuple(
        (int(left), int(right))
        for left, right, edge_literal in graph["external_edges"]
        if int(edge_literal) != literal
    )


def audit(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2
    minimum_labels = root_minimum_labels(n, pairs)

    counts: Counter[str] = Counter()
    ancestry_pairs: Counter[tuple[str, str]] = Counter()
    orientation_pairs: Counter[tuple[str, str]] = Counter()
    minimum_vertex_pairs: Counter[tuple[int | None, int | None]] = Counter()
    cycle_length_histogram: Counter[int] = Counter()
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
        ranks = {
            clause: graph_rank(
                int(graph["component_count"]),
                tuple((int(a), int(b)) for a, b, _literal in graph["external_edges"]),
            )
            for clause, graph in graphs.items()
        }
        labels = {
            clause: direct_root_labels(root, clause, assignment, minimum_labels)
            for clause in key
        }
        orientations = {
            clause: str(orientation_class(clause, graphs[clause], pairs)["classification"])
            for clause in key
        }

        for pivot in sorted(set(positive) & set(negative)):
            for left in positive[pivot]:
                for right in negative[pivot]:
                    left_graph = graphs[left]
                    right_graph = graphs[right]
                    component_count = int(left_graph["component_count"])
                    if ranks[left] != component_count - 1 or ranks[right] != component_count - 1:
                        continue

                    left_without = external_without_literal(left_graph, pivot)
                    right_without = external_without_literal(right_graph, -pivot)
                    if graph_rank(component_count, left_without) != ranks[left] - 1:
                        continue
                    if graph_rank(component_count, right_without) != ranks[right] - 1:
                        continue
                    left_cut = canonical_cut(component_count, left_without)
                    right_cut = canonical_cut(component_count, right_without)
                    assert left_cut is not None and right_cut is not None
                    if left_cut != right_cut:
                        continue

                    raw = (set(left) - {pivot}) | (set(right) - {-pivot})
                    if any(-literal in raw for literal in raw):
                        counts["tautological_same_cut_pairs"] += 1
                        continue
                    resolvent = canonical_clause(raw)
                    if resolvent is None or not resolvent:
                        counts["empty_or_rejected_same_cut_pairs"] += 1
                        continue
                    result_graph = clause_component_graph(n, resolvent, assignment, pairs)
                    external, _internal = directed_edges(resolvent, result_graph, pairs)
                    assert has_directed_cycle(component_count, external)

                    counts["same_cut_pairs"] += 1
                    left_labels = labels[left]
                    right_labels = labels[right]
                    left_primary = left_labels[0]
                    right_primary = right_labels[0]
                    ancestry_pairs[(str(left_primary[0]), str(right_primary[0]))] += 1
                    orientation_pairs[(orientations[left], orientations[right])] += 1
                    minimum_vertex_pairs[(left_primary[1], right_primary[1])] += 1

                    # Find the shortest directed cycle length by brute force over
                    # the small component graph.
                    adjacency = defaultdict(list)
                    for tail, head, _literal in external:
                        adjacency[int(tail)].append(int(head))
                    shortest = component_count + 1
                    for start in range(component_count):
                        queue = [(start, 0)]
                        seen_distance = {start: 0}
                        while queue:
                            vertex, distance = queue.pop(0)
                            for other in adjacency.get(vertex, ()):
                                if other == start:
                                    shortest = min(shortest, distance + 1)
                                elif other not in seen_distance:
                                    seen_distance[other] = distance + 1
                                    queue.append((other, distance + 1))
                    assert shortest <= component_count
                    cycle_length_histogram[shortest] += 1

                    if len(examples) < 40:
                        examples.append(
                            {
                                "n": n,
                                "state_id": int(state["id"]),
                                "call_id": call_id,
                                "novelty": novelty,
                                "component_count": component_count,
                                "pivot": pivot,
                                "cut": left_cut,
                                "left": left,
                                "right": right,
                                "resolvent": resolvent,
                                "left_labels": left_labels,
                                "right_labels": right_labels,
                                "left_orientation": orientations[left],
                                "right_orientation": orientations[right],
                                "shortest_cycle_length": shortest,
                            }
                        )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "ancestry_pairs": tuple(sorted(ancestry_pairs.items(), key=repr)),
        "orientation_pairs": tuple(sorted(orientation_pairs.items())),
        "minimum_vertex_pairs": tuple(sorted(minimum_vertex_pairs.items(), key=repr)),
        "cycle_length_histogram": tuple(sorted(cycle_length_histogram.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    rows = []
    aggregate_counts: Counter[str] = Counter()
    aggregate_ancestry: Counter[tuple[str, str]] = Counter()
    aggregate_orientation: Counter[tuple[str, str]] = Counter()
    aggregate_cycles: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_ancestry.update(dict(data["ancestry_pairs"]))
        aggregate_orientation.update(dict(data["orientation_pairs"]))
        aggregate_cycles.update(dict(data["cycle_length_histogram"]))
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["ancestry_pairs"],
                data["orientation_pairs"],
                data["cycle_length_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  ancestry_pairs = {data['ancestry_pairs']}")
        print(f"  orientation_pairs = {data['orientation_pairs']}")
        print(f"  minimum_vertex_pairs = {data['minimum_vertex_pairs']}")
        print(f"  cycle_length_histogram = {data['cycle_length_histogram']}")
        print(f"  examples = {data['examples']}")

    print("JANUS_GT_SAME_CUT_PARENT_ANCESTRY = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_ancestry = {tuple(sorted(aggregate_ancestry.items(), key=repr))}")
    print(f"aggregate_orientation = {tuple(sorted(aggregate_orientation.items()))}")
    print(f"aggregate_cycle_lengths = {tuple(sorted(aggregate_cycles.items()))}")
    print("claim_boundary = finite one-generation ancestry census; recursive parent provenance remains open")


if __name__ == "__main__":
    self_test()
