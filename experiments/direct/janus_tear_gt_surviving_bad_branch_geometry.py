#!/usr/bin/env python3
"""Certify the intervening branch geometry of surviving bad resolvents.

The survival filter isolates 42 local-Resolution non-tail bridge occurrences
that actually enter a later exact cache key.  For each lineage this checker
examines the unique intervening branch at the parent post-state quotient.

It verifies the temporal geometry suggested by the finite traces:

- the branch is novel;
- it never touches the singleton tail component of the bad literal;
- when the head component grows, the branch joins the head to another
  component;
- when the head size stays fixed, the branch is disjoint from both bad
  endpoints;
- child pre-unit propagation is absent;
- the branch falsifies and deletes one literal of the surviving source clause.

This turns the finite temporal-shield observation into an explicit certificate;
the arbitrary-n preservation proof remains open.
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
    component_sizes = {}
    for component, part in enumerate(graph["parts"]):
        component_sizes[component] = len(part)
        for vertex in part:
            vertex_component[int(vertex)] = component
    assert all(component >= 0 for component in vertex_component)
    return tuple(vertex_component), component_sizes


def classify_branch(
    tail_component: int,
    head_component: int,
    branch_components: tuple[int, int],
) -> str:
    left, right = branch_components
    endpoints = {left, right}
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
    relation_histogram: Counter[str] = Counter()
    head_delta_histogram: Counter[int] = Counter()
    other_size_histogram: Counter[int] = Counter()
    source_branch_polarity: Counter[str] = Counter()
    records = []

    for record in survival["records"]:
        counts["surviving_local_lineages"] += 1
        parent_state_id = int(record["parent_state"])
        parent_call = int(record["parent_call"])
        child_call = int(record["child_call"])
        literal = int(record["literal"])
        branch_literal = int(record["branch_literal"])
        source = tuple(record["post_source"])
        child_clause = tuple(record["child_clause"])

        assert int(record["novelty_increment"]) == 1
        assert int(record["child_pre_unit_count"]) == 0
        counts["novel_branches"] += 1
        counts["zero_child_pre_units"] += 1

        parent_assignment = context["state_after_post"][parent_state_id]
        source_graph = clause_component_graph(
            n, source, parent_assignment, pairs
        )
        vertex_component, component_sizes = quotient_map(source_graph, n)

        tail_vertex, head_vertex = original_direction(literal, pairs)
        tail_component = vertex_component[tail_vertex]
        head_component = vertex_component[head_vertex]
        assert tail_component != head_component
        assert component_sizes[tail_component] == 1

        branch_low, branch_high = pairs[abs(branch_literal)]
        branch_components = (
            vertex_component[int(branch_low)],
            vertex_component[int(branch_high)],
        )
        assert branch_components[0] != branch_components[1]

        relation = classify_branch(
            tail_component, head_component, branch_components
        )
        relation_histogram[relation] += 1
        assert relation != "TAIL_HEAD"
        assert relation != "TAIL_TO_OTHER"
        counts["branch_avoids_tail"] += 1

        post_tail, post_head = tuple(record["post_shape"])
        child_tail, child_head = tuple(record["child_shape"])
        assert post_tail == child_tail == 1
        head_delta = int(child_head) - int(post_head)
        head_delta_histogram[head_delta] += 1

        if head_delta > 0:
            assert relation == "HEAD_TO_OTHER"
            other_component = (
                branch_components[1]
                if branch_components[0] == head_component
                else branch_components[0]
            )
            other_size = int(component_sizes[other_component])
            assert head_delta == other_size
            other_size_histogram[other_size] += 1
            counts["head_growth_branches"] += 1
        else:
            assert head_delta == 0
            assert relation == "DISJOINT"
            counts["head_stable_disjoint_branches"] += 1

        # The child assignment removes the falsified branch literal from the
        # surviving source.  The signed child literal is the true assignment,
        # hence its complement is the falsified clause literal.
        assert -branch_literal in source
        assert branch_literal not in source
        assert len(source) == len(child_clause) + 1
        source_branch_polarity["FALSIFIED_COMPLEMENT"] += 1
        counts["one_literal_branch_restrictions"] += 1

        records.append({
            "n": n,
            "parent_state": parent_state_id,
            "parent_call": parent_call,
            "child_call": child_call,
            "bad_literal": literal,
            "tail_vertex": tail_vertex,
            "head_vertex": head_vertex,
            "tail_component": tail_component,
            "head_component": head_component,
            "branch_literal": branch_literal,
            "branch_components": branch_components,
            "relation": relation,
            "post_shape": (post_tail, post_head),
            "child_shape": (child_tail, child_head),
            "head_delta": head_delta,
            "source": source,
            "child_clause": child_clause,
        })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "relation_histogram": tuple(sorted(relation_histogram.items())),
        "head_delta_histogram": tuple(sorted(head_delta_histogram.items())),
        "other_size_histogram": tuple(sorted(other_size_histogram.items())),
        "source_branch_polarity": tuple(sorted(source_branch_polarity.items())),
        "records": tuple(records),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_deltas: Counter[int] = Counter()
    aggregate_other_sizes: Counter[int] = Counter()
    aggregate_polarity: Counter[str] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_relations.update(dict(data["relation_histogram"]))
        aggregate_deltas.update(dict(data["head_delta_histogram"]))
        aggregate_other_sizes.update(dict(data["other_size_histogram"]))
        aggregate_polarity.update(dict(data["source_branch_polarity"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  relation_histogram = {data['relation_histogram']}")
        print(f"  head_delta_histogram = {data['head_delta_histogram']}")
        print(f"  other_size_histogram = {data['other_size_histogram']}")
        print(f"  source_branch_polarity = {data['source_branch_polarity']}")
        print(f"  records = {data['records']}")

    assert aggregate_counts["surviving_local_lineages"] == 42
    assert aggregate_counts["branch_avoids_tail"] == 42
    assert aggregate_counts["novel_branches"] == 42
    assert aggregate_counts["zero_child_pre_units"] == 42
    assert aggregate_counts["head_growth_branches"] == 39
    assert aggregate_counts["head_stable_disjoint_branches"] == 3
    assert aggregate_counts["one_literal_branch_restrictions"] == 42
    assert aggregate_relations == Counter({
        "HEAD_TO_OTHER": 39,
        "DISJOINT": 3,
    })
    assert aggregate_deltas[0] == 3
    assert sum(value for delta, value in aggregate_deltas.items() if delta > 0) == 39
    assert aggregate_polarity == Counter({"FALSIFIED_COMPLEMENT": 42})

    print("JANUS_GT_SURVIVING_BAD_BRANCH_GEOMETRY = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_relations = {tuple(sorted(aggregate_relations.items()))}")
    print(f"aggregate_head_deltas = {tuple(sorted(aggregate_deltas.items()))}")
    print(f"aggregate_other_sizes = {tuple(sorted(aggregate_other_sizes.items()))}")
    print(f"aggregate_source_branch_polarity = {tuple(sorted(aggregate_polarity.items()))}")
    print(
        "claim_boundary = exact finite branch-geometry certificate through GT_8; "
        "arbitrary-n temporal survivor lemma remains open"
    )


if __name__ == "__main__":
    self_test()
