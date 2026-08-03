#!/usr/bin/env python3
"""Decompose the exact branch-frequency advantage on dangerous GT lineages.

Quotient-component frequency factorization is false.  This profile therefore
keeps clause history, polarity-insensitive variable identity, and the exact
Policy-0A selector.

For each of the 42 immediate-local non-tail bridge lineages that survives into
a later exact key, compare the selected branch variable with the strongest
variable touching the dangerous singleton tail.  Every unit of their frequency
difference is charged to one parent post-result clause and classified as:

- ROOT_NON_MINIMALITY: direct residual of an original N_v axiom;
- ROOT_TRANSITIVITY: direct residual of an original transitivity axiom;
- LOCAL_RESOLVENT: immediate output of the current frozen Resolution pass;
- INHERITED_DERIVED: inherited or otherwise derived history;
- OTHER_DERIVED: residual output not covered by the previous classes.

The profile does not assume that one class always wins.  It emits the exact
finite history vectors needed to formulate the next arbitrary-n lemma.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import parent_source_classes
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction
from janus_tear_gt_same_cut_parent_ancestry import (
    direct_root_labels,
    root_minimum_labels,
)
from janus_tear_gt_surviving_branch_frequency_profile import (
    audit as lineage_audit,
    quotient_map,
    relation,
)

ORIGIN_ORDER = (
    "ROOT_NON_MINIMALITY",
    "ROOT_TRANSITIVITY",
    "LOCAL_RESOLVENT",
    "INHERITED_DERIVED",
    "OTHER_DERIVED",
)


def clause_origin(root, clause, assignment, minimum_labels, state) -> str:
    labels = direct_root_labels(root, clause, assignment, minimum_labels)
    names = {str(label[0]) for label in labels}
    if "ROOT_NON_MINIMALITY" in names:
        return "ROOT_NON_MINIMALITY"
    if "ROOT_TRANSITIVITY" in names:
        return "ROOT_TRANSITIVITY"

    source_classes = set(parent_source_classes(state, clause))
    if "IMMEDIATE_LOCAL_RESOLVENT" in source_classes:
        return "LOCAL_RESOLVENT"
    if "INHERITED_KEY" in source_classes:
        return "INHERITED_DERIVED"
    return "OTHER_DERIVED"


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    root = tuple(context["root"])
    minimum_labels = root_minimum_labels(n, pairs)
    records = tuple(lineage_audit(n)["records"])

    counts: Counter[str] = Counter()
    gap_histogram: Counter[int] = Counter()
    source_delta_histogram: Counter[int] = Counter()
    origin_net: Counter[str] = Counter()
    origin_selected_only: Counter[str] = Counter()
    origin_tail_only: Counter[str] = Counter()
    origin_both: Counter[str] = Counter()
    vector_histogram: Counter[tuple[int, ...]] = Counter()
    sign_pattern_histogram: Counter[tuple[str, ...]] = Counter()
    rows = []

    for item in records:
        counts["lineages"] += 1
        state_id = int(item["parent_state"])
        state = policy.states[state_id]
        cnf = tuple(tuple(clause) for clause in state["post_result"])
        assignment = context["state_after_post"][state_id]
        selected = abs(int(item["branch_literal"]))
        bad_literal = int(item["literal"])
        source = tuple(item["post_source"])

        frequencies = Counter(
            abs(literal)
            for clause in cnf
            for literal in clause
        )
        assert frequencies[selected] == max(frequencies.values())

        source_graph = clause_component_graph(n, source, assignment, pairs)
        vertex_component = quotient_map(source_graph, n)
        tail_vertex, head_vertex = original_direction(bad_literal, pairs)
        tail_component = vertex_component[tail_vertex]
        head_component = vertex_component[head_vertex]

        tail_variables = []
        for variable in frequencies:
            low, high = pairs[int(variable)]
            label = relation(
                (vertex_component[int(low)], vertex_component[int(high)]),
                tail_component,
                head_component,
            )
            if label in ("TAIL_HEAD", "TAIL_TO_OTHER"):
                tail_variables.append(int(variable))
        assert tail_variables

        maximum_tail_frequency = max(frequencies[v] for v in tail_variables)
        strongest_tail_variables = tuple(sorted(
            variable
            for variable in tail_variables
            if frequencies[variable] == maximum_tail_frequency
        ))
        competitor = strongest_tail_variables[0]
        gap = frequencies[selected] - frequencies[competitor]
        assert gap >= 0
        if gap == 0:
            assert selected < competitor
            counts["tie_break_lineages"] += 1
        else:
            counts["strict_gap_lineages"] += 1
        gap_histogram[gap] += 1

        local_net: Counter[str] = Counter()
        local_selected_only: Counter[str] = Counter()
        local_tail_only: Counter[str] = Counter()
        local_both: Counter[str] = Counter()
        for clause in cnf:
            variables = {abs(literal) for literal in clause}
            has_selected = selected in variables
            has_tail = competitor in variables
            if not has_selected and not has_tail:
                continue
            origin = clause_origin(root, clause, assignment, minimum_labels, state)
            if has_selected and has_tail:
                local_both[origin] += 1
                origin_both[origin] += 1
            elif has_selected:
                local_net[origin] += 1
                local_selected_only[origin] += 1
                origin_net[origin] += 1
                origin_selected_only[origin] += 1
            else:
                local_net[origin] -= 1
                local_tail_only[origin] += 1
                origin_net[origin] -= 1
                origin_tail_only[origin] += 1

        assert sum(local_net.values()) == gap
        vector = tuple(local_net[origin] for origin in ORIGIN_ORDER)
        vector_histogram[vector] += 1
        signs = tuple(
            "POS" if value > 0 else "NEG" if value < 0 else "ZERO"
            for value in vector
        )
        sign_pattern_histogram[signs] += 1

        source_variables = {abs(literal) for literal in source}
        assert selected in source_variables
        source_delta = int(selected in source_variables) - int(
            competitor in source_variables
        )
        source_delta_histogram[source_delta] += 1
        if source_delta > 0:
            counts["source_selected_only"] += 1
        else:
            counts["source_contains_tail_competitor"] += 1

        rows.append(
            {
                "n": n,
                "parent_state": state_id,
                "bad_literal": bad_literal,
                "tail_vertex": tail_vertex,
                "head_vertex": head_vertex,
                "selected": selected,
                "competitor": competitor,
                "strongest_tail_variables": strongest_tail_variables,
                "selected_frequency": frequencies[selected],
                "tail_frequency": frequencies[competitor],
                "gap": gap,
                "source": source,
                "source_delta": source_delta,
                "origin_vector": vector,
                "origin_net": tuple(
                    (origin, local_net[origin])
                    for origin in ORIGIN_ORDER
                ),
                "selected_only": tuple(sorted(local_selected_only.items())),
                "tail_only": tuple(sorted(local_tail_only.items())),
                "both": tuple(sorted(local_both.items())),
            }
        )

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "gap_histogram": tuple(sorted(gap_histogram.items())),
        "source_delta_histogram": tuple(sorted(source_delta_histogram.items())),
        "origin_net": tuple((origin, origin_net[origin]) for origin in ORIGIN_ORDER),
        "origin_selected_only": tuple(
            (origin, origin_selected_only[origin]) for origin in ORIGIN_ORDER
        ),
        "origin_tail_only": tuple(
            (origin, origin_tail_only[origin]) for origin in ORIGIN_ORDER
        ),
        "origin_both": tuple(
            (origin, origin_both[origin]) for origin in ORIGIN_ORDER
        ),
        "vector_histogram": tuple(sorted(vector_histogram.items(), key=repr)),
        "sign_pattern_histogram": tuple(
            sorted(sign_pattern_histogram.items(), key=repr)
        ),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_gaps: Counter[int] = Counter()
    aggregate_source_delta: Counter[int] = Counter()
    aggregate_origin_net: Counter[str] = Counter()
    aggregate_vectors: Counter[tuple[int, ...]] = Counter()
    aggregate_signs: Counter[tuple[str, ...]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_gaps.update(dict(data["gap_histogram"]))
        aggregate_source_delta.update(dict(data["source_delta_histogram"]))
        aggregate_origin_net.update(dict(data["origin_net"]))
        aggregate_vectors.update(dict(data["vector_histogram"]))
        aggregate_signs.update(dict(data["sign_pattern_histogram"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  gap_histogram = {data['gap_histogram']}")
        print(f"  source_delta_histogram = {data['source_delta_histogram']}")
        print(f"  origin_net = {data['origin_net']}")
        print(f"  vector_histogram = {data['vector_histogram']}")
        print(f"  rows = {data['rows']}")

    assert aggregate_counts["lineages"] == 42
    assert aggregate_counts["strict_gap_lineages"] == 23
    assert aggregate_counts["tie_break_lineages"] == 19
    assert sum(aggregate_gaps.values()) == 42

    print("JANUS_GT_BRANCH_FREQUENCY_CONTRIBUTION_PROFILE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_GAPS = {tuple(sorted(aggregate_gaps.items()))}")
    print(
        "AGGREGATE_SOURCE_DELTA = "
        f"{tuple(sorted(aggregate_source_delta.items()))}"
    )
    print(
        "AGGREGATE_ORIGIN_NET = "
        f"{tuple((origin, aggregate_origin_net[origin]) for origin in ORIGIN_ORDER)}"
    )
    print(f"AGGREGATE_VECTORS = {tuple(sorted(aggregate_vectors.items(), key=repr))}")
    print(f"AGGREGATE_SIGNS = {tuple(sorted(aggregate_signs.items(), key=repr))}")
    print(
        "claim_boundary = exact finite history-sensitive frequency decomposition "
        "through GT_8; arbitrary-n selector inequality remains open"
    )


if __name__ == "__main__":
    self_test()
