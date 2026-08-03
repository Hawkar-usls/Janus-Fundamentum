#!/usr/bin/env python3
"""Profile the exact Policy-0A branch-frequency reason on surviving lineages.

For each of the 42 local bad-resolvent lineages that reaches a later exact key,
reconstruct the parent post-result CNF and the deterministic branch choice.
Compare the selected variable frequency with every variable whose comparison
edge touches the bad tail component, the bad head component, or neither.

The census distinguishes two possible proof routes:

- a strict frequency gap excludes every tail-touching variable; or
- tail-touching variables tie for maximum but lose the minimum-index rule.

No asymptotic claim is assumed; the output identifies the finite mechanism.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_resolvent_survival_filter import audit as survival_audit
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction


def quotient_map(graph, n: int):
    vertex_component = [-1] * n
    for component, part in enumerate(graph["parts"]):
        for vertex in part:
            vertex_component[int(vertex)] = component
    assert all(component >= 0 for component in vertex_component)
    return tuple(vertex_component)


def relation(
    components: tuple[int, int],
    tail_component: int,
    head_component: int,
) -> str:
    endpoints = set(components)
    if tail_component in endpoints and head_component in endpoints:
        return "TAIL_HEAD"
    if tail_component in endpoints:
        return "TAIL_TO_OTHER"
    if head_component in endpoints:
        return "HEAD_TO_OTHER"
    return "DISJOINT"


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    survival = survival_audit(n)

    counts: Counter[str] = Counter()
    selected_relation_histogram: Counter[str] = Counter()
    tail_gap_histogram: Counter[int] = Counter()
    head_gap_histogram: Counter[int] = Counter()
    max_relation_sets: Counter[tuple[str, ...]] = Counter()
    max_candidate_counts: Counter[int] = Counter()
    selected_rank_among_max: Counter[int] = Counter()
    frequency_shapes: Counter[tuple[int, int, int, int]] = Counter()
    records = []

    for item in survival["records"]:
        counts["lineages"] += 1
        parent_state_id = int(item["parent_state"])
        parent_state = policy.states[parent_state_id]
        parent_cnf = tuple(tuple(clause) for clause in parent_state["post_result"])
        branch_literal = int(item["branch_literal"])
        selected = abs(branch_literal)
        literal = int(item["literal"])
        source = tuple(item["post_source"])

        frequencies = Counter(
            abs(candidate)
            for clause in parent_cnf
            for candidate in clause
        )
        maximum = max(frequencies.values())
        maximum_variables = tuple(sorted(
            variable
            for variable, frequency in frequencies.items()
            if frequency == maximum
        ))
        assert selected == maximum_variables[0]
        assert frequencies[selected] == maximum
        selected_rank_among_max[maximum_variables.index(selected) + 1] += 1
        max_candidate_counts[len(maximum_variables)] += 1

        parent_assignment = context["state_after_post"][parent_state_id]
        source_graph = clause_component_graph(
            n, source, parent_assignment, pairs
        )
        vertex_component = quotient_map(source_graph, n)
        tail_vertex, head_vertex = original_direction(literal, pairs)
        tail_component = vertex_component[tail_vertex]
        head_component = vertex_component[head_vertex]

        relation_by_variable = {}
        for variable in frequencies:
            low, high = pairs[int(variable)]
            relation_by_variable[int(variable)] = relation(
                (vertex_component[int(low)], vertex_component[int(high)]),
                tail_component,
                head_component,
            )

        selected_relation = relation_by_variable[selected]
        selected_relation_histogram[selected_relation] += 1
        assert selected_relation in ("HEAD_TO_OTHER", "DISJOINT")

        max_relations = tuple(sorted({
            relation_by_variable[variable]
            for variable in maximum_variables
        }))
        max_relation_sets[max_relations] += 1

        tail_variables = [
            variable
            for variable, label in relation_by_variable.items()
            if label in ("TAIL_HEAD", "TAIL_TO_OTHER")
        ]
        head_variables = [
            variable
            for variable, label in relation_by_variable.items()
            if label in ("TAIL_HEAD", "HEAD_TO_OTHER")
        ]
        disjoint_variables = [
            variable
            for variable, label in relation_by_variable.items()
            if label == "DISJOINT"
        ]

        max_tail = max((frequencies[v] for v in tail_variables), default=0)
        max_head = max((frequencies[v] for v in head_variables), default=0)
        max_disjoint = max((frequencies[v] for v in disjoint_variables), default=0)
        tail_gap = maximum - max_tail
        head_gap = maximum - max_head
        tail_gap_histogram[tail_gap] += 1
        head_gap_histogram[head_gap] += 1
        frequency_shapes[(maximum, max_tail, max_head, max_disjoint)] += 1

        if tail_gap > 0:
            counts["strict_tail_frequency_gap"] += 1
        else:
            counts["tail_ties_maximum"] += 1
            tail_max_variables = tuple(sorted(
                variable
                for variable in tail_variables
                if frequencies[variable] == maximum
            ))
            assert tail_max_variables
            assert selected < min(tail_max_variables)
            counts["tail_excluded_by_tie_break"] += 1

        assert -branch_literal in source
        counts["selected_complement_in_source"] += 1

        records.append({
            "n": n,
            "parent_state": parent_state_id,
            "bad_literal": literal,
            "tail_vertex": tail_vertex,
            "head_vertex": head_vertex,
            "selected_variable": selected,
            "selected_literal": branch_literal,
            "selected_relation": selected_relation,
            "selected_frequency": maximum,
            "maximum_variables": maximum_variables,
            "maximum_relations": max_relations,
            "max_tail_frequency": max_tail,
            "max_head_frequency": max_head,
            "max_disjoint_frequency": max_disjoint,
            "tail_gap": tail_gap,
            "head_gap": head_gap,
            "source": source,
        })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "selected_relation_histogram": tuple(sorted(selected_relation_histogram.items())),
        "tail_gap_histogram": tuple(sorted(tail_gap_histogram.items())),
        "head_gap_histogram": tuple(sorted(head_gap_histogram.items())),
        "max_relation_sets": tuple(sorted(max_relation_sets.items(), key=repr)),
        "max_candidate_counts": tuple(sorted(max_candidate_counts.items())),
        "selected_rank_among_max": tuple(sorted(selected_rank_among_max.items())),
        "frequency_shapes": tuple(sorted(frequency_shapes.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_tail_gaps: Counter[int] = Counter()
    aggregate_head_gaps: Counter[int] = Counter()
    aggregate_max_relations: Counter[tuple[str, ...]] = Counter()
    aggregate_candidate_counts: Counter[int] = Counter()
    aggregate_ranks: Counter[int] = Counter()
    aggregate_shapes: Counter[tuple[int, int, int, int]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_relations.update(dict(data["selected_relation_histogram"]))
        aggregate_tail_gaps.update(dict(data["tail_gap_histogram"]))
        aggregate_head_gaps.update(dict(data["head_gap_histogram"]))
        aggregate_max_relations.update(dict(data["max_relation_sets"]))
        aggregate_candidate_counts.update(dict(data["max_candidate_counts"]))
        aggregate_ranks.update(dict(data["selected_rank_among_max"]))
        aggregate_shapes.update(dict(data["frequency_shapes"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  selected_relation_histogram = {data['selected_relation_histogram']}")
        print(f"  tail_gap_histogram = {data['tail_gap_histogram']}")
        print(f"  head_gap_histogram = {data['head_gap_histogram']}")
        print(f"  max_relation_sets = {data['max_relation_sets']}")
        print(f"  max_candidate_counts = {data['max_candidate_counts']}")
        print(f"  selected_rank_among_max = {data['selected_rank_among_max']}")
        print(f"  frequency_shapes = {data['frequency_shapes']}")
        print(f"  records = {data['records']}")

    assert aggregate_counts["lineages"] == 42
    assert aggregate_counts["selected_complement_in_source"] == 42
    assert aggregate_counts["strict_tail_frequency_gap"] + aggregate_counts[
        "tail_excluded_by_tie_break"
    ] == 42
    assert aggregate_ranks == Counter({1: 42})

    print("JANUS_GT_SURVIVING_BRANCH_FREQUENCY_PROFILE = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_selected_relations = {tuple(sorted(aggregate_relations.items()))}")
    print(f"aggregate_tail_gaps = {tuple(sorted(aggregate_tail_gaps.items()))}")
    print(f"aggregate_head_gaps = {tuple(sorted(aggregate_head_gaps.items()))}")
    print(f"aggregate_max_relation_sets = {tuple(sorted(aggregate_max_relations.items(), key=repr))}")
    print(f"aggregate_max_candidate_counts = {tuple(sorted(aggregate_candidate_counts.items()))}")
    print(f"aggregate_selected_ranks = {tuple(sorted(aggregate_ranks.items()))}")
    print(f"aggregate_frequency_shapes = {tuple(sorted(aggregate_shapes.items()))}")
    print(
        "claim_boundary = finite exact frequency mechanism through GT_8; "
        "uniform frequency inequality remains open"
    )


if __name__ == "__main__":
    self_test()
