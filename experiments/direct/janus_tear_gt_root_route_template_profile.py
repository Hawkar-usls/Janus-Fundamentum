#!/usr/bin/env python3
"""Classify exact root handoff routes by selected-edge bridge-cut geometry.

The root-only handoff probe proves finite safety through GT_12 but does not yet
separate the graph mechanisms.  This profile reconstructs every root
unshielded occurrence and classifies the selected comparison as:

- PIVOT: the selected variable is the bad pivot itself;
- CROSS_CUT: selected endpoints lie on opposite bad-bridge cut sides;
- INTERNAL_TAIL: selected endpoints lie inside the bad tail side;
- INTERNAL_HEAD: selected endpoints lie inside the bad head side.

For each class it records whether the selected literal occurs in the clause,
cut-side sizes, internal-edge multiplicities, and both child fates.  The goal is
to isolate pure graph implications from the remaining GT reachability theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_root_unshielded_handoff_probe import audit as root_audit, root_stages


def component_map(graph):
    result = {}
    for component_index, part in enumerate(graph["parts"]):
        for vertex in part:
            result[int(vertex)] = int(component_index)
    return result


def side_containing(cut, component_index: int):
    left, right = cut
    if component_index in left:
        return tuple(left), tuple(right)
    assert component_index in right
    return tuple(right), tuple(left)


def selected_geometry(graph, bad_bridge, sizes, selected: int, pairs):
    if selected == abs(int(bad_bridge["literal"])):
        return "PIVOT"

    vertex_component = component_map(graph)
    low, high = pairs[selected]
    selected_components = (
        vertex_component[int(low)],
        vertex_component[int(high)],
    )
    tail_side, head_side = side_containing(
        bad_bridge["cut"], int(sizes["tail_component"])
    )
    in_tail = tuple(component in tail_side for component in selected_components)
    if in_tail == (True, True):
        label = "INTERNAL_TAIL"
    elif in_tail == (False, False):
        label = "INTERNAL_HEAD"
    else:
        label = "CROSS_CUT"
    return label


def audit(n: int):
    stages = root_stages(n)
    pairs = stages["pairs"]
    assignment = dict(stages["post_assignment"])
    data = root_audit(n)

    counts: Counter[str] = Counter()
    geometry_histogram: Counter[str] = Counter()
    relation_geometry: Counter[tuple[str, str]] = Counter()
    fate_patterns: Counter[tuple[str, str, str]] = Counter()
    selected_occurrence: Counter[tuple[str, str]] = Counter()
    cut_shapes: Counter[tuple[str, int, int]] = Counter()
    internal_edge_counts: Counter[tuple[str, int, int]] = Counter()
    shield_multiplicity: Counter[tuple[str, int]] = Counter()
    rows = []

    for record in data["records"]:
        counts["occurrences"] += 1
        clause = tuple(record["clause"])
        literal = int(record["literal"])
        selected = int(record["selected"])
        graph = clause_component_graph(n, clause, assignment, pairs)
        bad_bridge = bridge_record(clause, graph, pairs, literal)
        assert bad_bridge is not None
        sizes = endpoint_sizes(graph, literal, pairs)
        assert int(sizes["tail_size"]) == 1
        assert int(sizes["head_size"]) == 1

        geometry = selected_geometry(graph, bad_bridge, sizes, selected, pairs)
        relation = str(record["selected_relation"])
        geometry_histogram[geometry] += 1
        relation_geometry[(relation, geometry)] += 1

        selected_literals = tuple(
            candidate for candidate in clause if abs(candidate) == selected
        )
        if selected_literals:
            assert len(selected_literals) == 1
            occurrence = "PRESENT_POS" if selected_literals[0] > 0 else "PRESENT_NEG"
        else:
            occurrence = "ABSENT"
        selected_occurrence[(geometry, occurrence)] += 1

        tail_side, head_side = side_containing(
            bad_bridge["cut"], int(sizes["tail_component"])
        )
        cut_shapes[(geometry, len(tail_side), len(head_side))] += 1

        vertex_component = component_map(graph)
        external_edges = tuple(
            (int(left), int(right), int(edge_literal))
            for left, right, edge_literal in graph["external_edges"]
        )
        tail_internal = tuple(
            edge_literal
            for left, right, edge_literal in external_edges
            if left in tail_side and right in tail_side
        )
        head_internal = tuple(
            edge_literal
            for left, right, edge_literal in external_edges
            if left in head_side and right in head_side
        )
        internal_edge_counts[(geometry, len(tail_internal), len(head_internal))] += 1

        fate_by_value = {
            bool(value): str(fate)
            for value, fate, _residual, _shield in record["fates"]
        }
        assert set(fate_by_value) == {False, True}
        pattern = (geometry, fate_by_value[False], fate_by_value[True])
        fate_patterns[pattern] += 1

        for _value, fate, _residual, shield in record["fates"]:
            if fate == "CANONICALLY_SHIELDED":
                assert shield is not None
                shield_multiplicity[(geometry, len(shield["parallel_literals"]))] += 1

        selected_low, selected_high = pairs[selected]
        rows.append(
            {
                "n": n,
                "selected": selected,
                "selected_pair": (int(selected_low), int(selected_high)),
                "selected_relation": relation,
                "selected_geometry": geometry,
                "selected_occurrence": occurrence,
                "clause": clause,
                "literal": literal,
                "bad_cut": bad_bridge["cut"],
                "tail_side": tail_side,
                "head_side": head_side,
                "tail_internal_edges": tail_internal,
                "head_internal_edges": head_internal,
                "fates": tuple(record["fates"]),
            }
        )

    assert counts["occurrences"] == dict(data["counts"])[
        "unshielded_local_bridge_occurrences"
    ]
    assert all(
        fate != "UNSAFE_UNSHIELDED_SURVIVES"
        for row in rows
        for _value, fate, _residual, _shield in row["fates"]
    )
    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "geometry_histogram": tuple(sorted(geometry_histogram.items())),
        "relation_geometry": tuple(sorted(relation_geometry.items(), key=repr)),
        "fate_patterns": tuple(sorted(fate_patterns.items(), key=repr)),
        "selected_occurrence": tuple(sorted(selected_occurrence.items(), key=repr)),
        "cut_shapes": tuple(sorted(cut_shapes.items(), key=repr)),
        "internal_edge_counts": tuple(sorted(internal_edge_counts.items(), key=repr)),
        "shield_multiplicity": tuple(sorted(shield_multiplicity.items(), key=repr)),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_geometry: Counter[str] = Counter()
    aggregate_relation_geometry: Counter[tuple[str, str]] = Counter()
    aggregate_fates: Counter[tuple[str, str, str]] = Counter()
    aggregate_occurrence: Counter[tuple[str, str]] = Counter()
    aggregate_shapes: Counter[tuple[str, int, int]] = Counter()
    aggregate_internal: Counter[tuple[str, int, int]] = Counter()
    aggregate_shields: Counter[tuple[str, int]] = Counter()

    for n in range(4, 13):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_geometry.update(dict(data["geometry_histogram"]))
        aggregate_relation_geometry.update(dict(data["relation_geometry"]))
        aggregate_fates.update(dict(data["fate_patterns"]))
        aggregate_occurrence.update(dict(data["selected_occurrence"]))
        aggregate_shapes.update(dict(data["cut_shapes"]))
        aggregate_internal.update(dict(data["internal_edge_counts"]))
        aggregate_shields.update(dict(data["shield_multiplicity"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  geometry = {data['geometry_histogram']}")
        print(f"  relation_geometry = {data['relation_geometry']}")
        print(f"  fate_patterns = {data['fate_patterns']}")
        print(f"  selected_occurrence = {data['selected_occurrence']}")
        print(f"  cut_shapes = {data['cut_shapes']}")
        print(f"  internal_edge_counts = {data['internal_edge_counts']}")
        print(f"  rows = {data['rows']}")

    assert aggregate_counts["occurrences"] == 62
    assert sum(aggregate_geometry.values()) == 62

    print("JANUS_GT_ROOT_ROUTE_TEMPLATE_PROFILE = PASS")
    print(f"AGGREGATE_GEOMETRY = {tuple(sorted(aggregate_geometry.items()))}")
    print(
        "AGGREGATE_RELATION_GEOMETRY = "
        f"{tuple(sorted(aggregate_relation_geometry.items(), key=repr))}"
    )
    print(f"AGGREGATE_FATES = {tuple(sorted(aggregate_fates.items(), key=repr))}")
    print(
        "AGGREGATE_SELECTED_OCCURRENCE = "
        f"{tuple(sorted(aggregate_occurrence.items(), key=repr))}"
    )
    print(f"AGGREGATE_CUT_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(
        "AGGREGATE_INTERNAL_EDGES = "
        f"{tuple(sorted(aggregate_internal.items(), key=repr))}"
    )
    print(f"AGGREGATE_SHIELDS = {tuple(sorted(aggregate_shields.items(), key=repr))}")
    print(
        "claim_boundary = exact root route template profile through GT_12; "
        "pure graph sublemmas and GT reachability remain to be separated"
    )


if __name__ == "__main__":
    self_test()
