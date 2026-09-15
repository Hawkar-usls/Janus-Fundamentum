#!/usr/bin/env python3
"""Test the canonical root non-minimality shield for every non-tail bridge.

Finite path extraction through GT_8 found exactly one root non-minimality
alternate-path witness per non-tail bridge occurrence.  This checker tests the
strong structural statement directly.

For a bad bridge literal l : a -> b in an inherited component-spanning clause,
consider the original non-minimality axiom N_a (every vertex has a predecessor).
It contains the complementary literal -l : b -> a.  The claimed shield is:

- the residual of N_a is present in the same exact key;
- it remains component-spanning;
- -l is present but is not a bridge;
- another residual literal gives a parallel quotient edge between the same two
  Hasse components.

A parallel quotient edge is a one-edge pivot-avoiding path and therefore blocks
the same-cut double-bridge obstruction.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_merge_sources import reduce_clause
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_same_cut_parent_ancestry import root_minimum_labels


def original_direction(literal: int, pairs):
    low, high = pairs[abs(int(literal))]
    return (int(low), int(high)) if literal > 0 else (int(high), int(low))


def audit(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    minimum_labels = root_minimum_labels(n, pairs)
    root_by_vertex = {vertex: clause for clause, vertex in minimum_labels.items()}
    assert set(root_by_vertex) == set(range(n))

    counts: Counter[str] = Counter()
    parallel_multiplicity: Counter[int] = Counter()
    tail_component_sizes: Counter[int] = Counter()
    head_component_sizes: Counter[int] = Counter()
    examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        key = tuple(state["key"])
        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in key
        }
        classes = {
            clause: str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in key
        }

        # Recover original-vertex membership from the quotient partition.
        representative_graph = next(iter(graphs.values()))
        parts = tuple(
            tuple(int(vertex) for vertex in part)
            for part in representative_graph["parts"]
        )
        vertex_component_list = [-1] * n
        for component_index, part in enumerate(parts):
            for vertex in part:
                vertex_component_list[vertex] = component_index
        assert all(value >= 0 for value in vertex_component_list)
        vertex_component = tuple(vertex_component_list)
        component_members = Counter(vertex_component)

        for clause in key:
            if classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                literal = int(literal)
                record = bridge_record(clause, graphs[clause], pairs, literal)
                if record is None or record["role"] == "TAIL_SINGLETON":
                    continue

                counts["non_tail_bridge_occurrences"] += 1
                tail_vertex, head_vertex = original_direction(literal, pairs)
                root_clause = root_by_vertex[tail_vertex]
                root_residual = reduce_clause(root_clause, assignment)
                assert root_residual is not None
                assert root_residual in key
                assert -literal in root_residual
                assert classes[root_residual] == "COMPONENT_SPANNING"
                assert bridge_record(
                    root_residual,
                    graphs[root_residual],
                    pairs,
                    -literal,
                ) is None

                tail_component = vertex_component[tail_vertex]
                head_component = vertex_component[head_vertex]
                pivot_edge = tuple(sorted((tail_component, head_component)))
                parallel_literals = []
                for left, right, edge_literal in graphs[root_residual]["external_edges"]:
                    edge_literal = int(edge_literal)
                    if edge_literal == -literal:
                        continue
                    if tuple(sorted((int(left), int(right)))) == pivot_edge:
                        parallel_literals.append(edge_literal)

                assert parallel_literals
                counts["canonical_root_shields"] += 1
                parallel_multiplicity[len(parallel_literals)] += 1
                tail_component_sizes[component_members[tail_component]] += 1
                head_component_sizes[component_members[head_component]] += 1

                if len(examples) < 60:
                    examples.append({
                        "n": n,
                        "state_id": int(state["id"]),
                        "call_id": call_id,
                        "novelty": novelty,
                        "bad_clause": clause,
                        "literal": literal,
                        "role": str(record["role"]),
                        "tail_vertex": tail_vertex,
                        "head_vertex": head_vertex,
                        "tail_component": tail_component,
                        "head_component": head_component,
                        "tail_component_size": component_members[tail_component],
                        "head_component_size": component_members[head_component],
                        "root_non_minimality": root_clause,
                        "root_residual": root_residual,
                        "parallel_literals": tuple(sorted(parallel_literals)),
                    })

    assert counts["non_tail_bridge_occurrences"] == counts["canonical_root_shields"]
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "parallel_multiplicity": tuple(sorted(parallel_multiplicity.items())),
        "tail_component_sizes": tuple(sorted(tail_component_sizes.items())),
        "head_component_sizes": tuple(sorted(head_component_sizes.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_parallel: Counter[int] = Counter()
    aggregate_tail_sizes: Counter[int] = Counter()
    aggregate_head_sizes: Counter[int] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_parallel.update(dict(data["parallel_multiplicity"]))
        aggregate_tail_sizes.update(dict(data["tail_component_sizes"]))
        aggregate_head_sizes.update(dict(data["head_component_sizes"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  parallel_multiplicity = {data['parallel_multiplicity']}")
        print(f"  tail_component_sizes = {data['tail_component_sizes']}")
        print(f"  head_component_sizes = {data['head_component_sizes']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["non_tail_bridge_occurrences"] == 62
    assert aggregate_counts["canonical_root_shields"] == 62
    print("JANUS_GT_ROOT_NONMINIMALITY_BRIDGE_SHIELD = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_parallel_multiplicity = {tuple(sorted(aggregate_parallel.items()))}")
    print(f"aggregate_tail_component_sizes = {tuple(sorted(aggregate_tail_sizes.items()))}")
    print(f"aggregate_head_component_sizes = {tuple(sorted(aggregate_head_sizes.items()))}")
    print(
        "claim_boundary = canonical finite root shield through GT_8; "
        "arbitrary-n preservation of the root residual remains open"
    )


if __name__ == "__main__":
    self_test()
