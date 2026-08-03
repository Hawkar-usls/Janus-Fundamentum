#!/usr/bin/env python3
"""Extract the exact non-root unshielded wing-collapse template.

The all-birth handoff census finds three non-root unshielded P-occurrences
through GT_8, all in one GT_8 state.  This profile reconstructs their parent
clause graphs and checks the candidate pure-graph mechanism:

- the bad bridge separates a two-node tail wing from the head side;
- the selected comparison joins two singleton relation components;
- the selected clause edge is the unique internal edge of that tail wing;
- the selected variable occurs in the clause;
- one branch polarity satisfies the clause;
- the other deletes the selected literal while contracting the complete tail
  wing to one quotient node, making the bad pivot TAIL_SINGLETON safe.

The singleton-endpoint check also instantiates the weaker proved
Singleton-Branch Same-Cut Preservation theorem.  The output is finite template
extraction, not yet an arbitrary-n reachability theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_unshielded_birth_handoff_census import audit as handoff_audit


def cut_side_for_vertex(cut, component_index: int):
    left, right = cut
    if component_index in left:
        return tuple(left), tuple(right)
    assert component_index in right
    return tuple(right), tuple(left)


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    handoff = handoff_audit(n)

    counts: Counter[str] = Counter()
    tail_side_sizes: Counter[int] = Counter()
    head_side_sizes: Counter[int] = Counter()
    selected_component_sizes: Counter[tuple[int, int]] = Counter()
    selected_clause_signs: Counter[int] = Counter()
    selected_internal_multiplicity: Counter[int] = Counter()
    rows = []

    for item in handoff["rows"]:
        if int(item["depth"]) == 0:
            continue
        counts["nonroot_occurrences"] += 1
        state = policy.states[int(item["state_id"])]
        assignment = context["state_after_post"][int(item["state_id"])]
        clause = tuple(item["clause"])
        literal = int(item["literal"])
        selected = int(item["selected"])
        graph = clause_component_graph(n, clause, assignment, pairs)
        assert str(safety_class(n, clause, assignment, pairs)["classification"]) == "COMPONENT_SPANNING"
        bad_bridge = bridge_record(clause, graph, pairs, literal)
        assert bad_bridge is not None
        sizes = endpoint_sizes(graph, literal, pairs)
        assert int(sizes["tail_size"]) == 1
        assert int(sizes["head_size"]) == 1

        tail_side, head_side = cut_side_for_vertex(
            bad_bridge["cut"], int(sizes["tail_component"])
        )
        tail_side_sizes[len(tail_side)] += 1
        head_side_sizes[len(head_side)] += 1

        selected_low, selected_high = pairs[selected]
        vertex_component = {}
        for component_index, part in enumerate(graph["parts"]):
            for vertex in part:
                vertex_component[int(vertex)] = int(component_index)
        selected_components = tuple(sorted((
            vertex_component[int(selected_low)],
            vertex_component[int(selected_high)],
        )))
        assert selected_components[0] != selected_components[1]
        assert set(selected_components).issubset(set(tail_side))
        counts["selected_inside_tail_side"] += 1

        component_sizes = tuple(
            len(graph["parts"][component])
            for component in selected_components
        )
        selected_component_sizes[tuple(sorted(component_sizes))] += 1
        assert component_sizes == (1, 1)
        counts["selected_joins_singleton_components"] += 1

        selected_literals = tuple(
            candidate for candidate in clause if abs(candidate) == selected
        )
        assert len(selected_literals) == 1
        selected_literal = int(selected_literals[0])
        selected_clause_signs[selected_literal] += 1
        counts["selected_literal_in_clause"] += 1

        internal_tail_edges = tuple(
            int(edge_literal)
            for left, right, edge_literal in graph["external_edges"]
            if int(left) in tail_side and int(right) in tail_side
        )
        selected_internal_multiplicity[len(internal_tail_edges)] += 1
        assert internal_tail_edges == (selected_literal,) or set(internal_tail_edges) == {selected_literal}
        counts["selected_unique_tail_internal_edge"] += 1

        assert len(tail_side) == 2
        counts["two_node_tail_wing"] += 1

        child_fates = {
            bool(child["value"]): str(child["fate"])
            for child in item["children"]
        }
        satisfying_value = selected_literal > 0
        assert child_fates[satisfying_value] == "CLAUSE_EXTINCT"
        assert child_fates[not satisfying_value] == "TAIL_SINGLETON_SAFE"
        counts["polarity_extinct_or_tail_safe"] += 1

        rows.append(
            {
                "n": n,
                "state_id": int(item["state_id"]),
                "call_id": int(item["call_id"]),
                "depth": int(item["depth"]),
                "novelty": int(item["novelty"]),
                "clause": clause,
                "literal": literal,
                "bad_bridge": bad_bridge,
                "tail_side": tail_side,
                "head_side": head_side,
                "selected": selected,
                "selected_literal": selected_literal,
                "selected_components": selected_components,
                "selected_component_sizes": component_sizes,
                "internal_tail_edges": internal_tail_edges,
                "children": tuple(item["children"]),
            }
        )

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "tail_side_sizes": tuple(sorted(tail_side_sizes.items())),
        "head_side_sizes": tuple(sorted(head_side_sizes.items())),
        "selected_component_sizes": tuple(
            sorted(selected_component_sizes.items())
        ),
        "selected_clause_signs": tuple(sorted(selected_clause_signs.items())),
        "selected_internal_multiplicity": tuple(
            sorted(selected_internal_multiplicity.items())
        ),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_tail_sizes: Counter[int] = Counter()
    aggregate_head_sizes: Counter[int] = Counter()
    aggregate_selected_sizes: Counter[tuple[int, int]] = Counter()
    aggregate_signs: Counter[int] = Counter()
    aggregate_internal: Counter[int] = Counter()
    all_rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_tail_sizes.update(dict(data["tail_side_sizes"]))
        aggregate_head_sizes.update(dict(data["head_side_sizes"]))
        aggregate_selected_sizes.update(dict(data["selected_component_sizes"]))
        aggregate_signs.update(dict(data["selected_clause_signs"]))
        aggregate_internal.update(dict(data["selected_internal_multiplicity"]))
        all_rows.extend(data["rows"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  tail_side_sizes = {data['tail_side_sizes']}")
        print(f"  selected_component_sizes = {data['selected_component_sizes']}")
        print(f"  selected_clause_signs = {data['selected_clause_signs']}")
        print(f"  rows = {data['rows']}")

    expected = 3
    for name in (
        "nonroot_occurrences",
        "selected_inside_tail_side",
        "selected_joins_singleton_components",
        "selected_literal_in_clause",
        "selected_unique_tail_internal_edge",
        "two_node_tail_wing",
        "polarity_extinct_or_tail_safe",
    ):
        assert aggregate_counts[name] == expected, (name, aggregate_counts[name])
    assert aggregate_selected_sizes == Counter({(1, 1): expected})
    assert len({(row["state_id"], row["call_id"]) for row in all_rows}) == 1

    print("JANUS_GT_NONROOT_UNSHIELDED_WING_PROFILE = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_TAIL_SIDE_SIZES = {tuple(sorted(aggregate_tail_sizes.items()))}")
    print(f"AGGREGATE_HEAD_SIDE_SIZES = {tuple(sorted(aggregate_head_sizes.items()))}")
    print(f"AGGREGATE_SELECTED_COMPONENT_SIZES = {tuple(sorted(aggregate_selected_sizes.items()))}")
    print(f"AGGREGATE_SELECTED_SIGNS = {tuple(sorted(aggregate_signs.items()))}")
    print(f"AGGREGATE_INTERNAL_EDGES = {tuple(sorted(aggregate_internal.items()))}")
    print(
        "finite_result = every non-root unshielded P-occurrence through GT_8 "
        "selects a comparison between singleton components and also instantiates "
        "the stronger two-node tail-wing handoff"
    )
    print(
        "claim_boundary = exact finite singleton-branch/wing template; arbitrary-n "
        "nonroot singleton-branch reachability remains open"
    )


if __name__ == "__main__":
    self_test()
