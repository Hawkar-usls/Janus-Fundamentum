#!/usr/bin/env python3
"""Certify the transitivity tree-exchange normal form of all finite non-root wings.

This checker consumes the already exact producer-provenance records, but it
independently reconstructs the quotient simple graphs used by the new pure
lemma.  For every non-root unshielded occurrence through GT_8 it verifies:

* one root-transitivity directed-cycle parent;
* one component-spanning in-arborescence parent;
* resolving the complementary pivot replaces one tree edge by the third edge
  of a quotient triangle;
* the new bad bridge cut equals the removed pivot-edge cut;
* the pivot side has two quotient vertices;
* the deterministic selected edge is its unique internal edge.

The result is a finite instantiation certificate, not the arbitrary-n producer
normal-form reachability theorem.
"""

from __future__ import annotations

from collections import Counter, deque

from janus_tear_gt_nonroot_wing_provenance import audit as provenance_audit


def vertex_components(parts):
    out = {}
    for index, part in enumerate(parts):
        for vertex in part:
            out[int(vertex)] = int(index)
    return out


def quotient_edges(edge_records, component_of):
    edges = []
    for tail, head, literal in edge_records:
        u = component_of[int(tail)]
        v = component_of[int(head)]
        if u == v:
            continue
        edge = tuple(sorted((u, v)))
        edges.append((edge, int(literal)))
    return tuple(edges)


def simple_edge_set(records):
    edges = [edge for edge, _literal in records]
    assert len(edges) == len(set(edges)), ("parallel quotient edge", records)
    return frozenset(edges)


def components(vertices, edges):
    adjacency = {vertex: set() for vertex in vertices}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    result = []
    unseen = set(vertices)
    while unseen:
        start = min(unseen)
        queue = deque([start])
        seen = {start}
        unseen.remove(start)
        while queue:
            current = queue.popleft()
            for nxt in adjacency[current]:
                if nxt not in seen:
                    seen.add(nxt)
                    unseen.discard(nxt)
                    queue.append(nxt)
        result.append(frozenset(seen))
    return tuple(sorted(result, key=lambda part: (len(part), tuple(sorted(part)))))


def cut_after_removal(vertices, edges, removed):
    assert removed in edges
    remaining = frozenset(edge for edge in edges if edge != removed)
    parts = components(vertices, remaining)
    assert len(parts) == 2, (edges, removed, parts)
    return frozenset(parts)


def connected(vertices, edges):
    return len(components(vertices, edges)) == 1


def root_label_names(origin, side):
    return tuple(str(label[0]) for label in origin[f"{side}_root_labels"])


def parent_record(origin, side):
    return {
        "clause": tuple(origin[side]),
        "safety": str(origin[f"{side}_safety"]),
        "orientation": str(origin[f"{side}_orientation"]),
        "labels": root_label_names(origin, side),
        "edges": tuple(origin[f"{side}_edges"]),
    }


def verify_record(record):
    origins = tuple(record["origins"])
    assert len(origins) == 1
    origin = origins[0]
    assert tuple(origin["resolvent"]) == tuple(record["clause"])

    parents = [parent_record(origin, "left"), parent_record(origin, "right")]
    tree_parents = [
        parent
        for parent in parents
        if parent["safety"] == "COMPONENT_SPANNING"
        and parent["orientation"] == "IN_ARBORESCENCE"
    ]
    cycle_parents = [
        parent
        for parent in parents
        if parent["safety"] == "DIRECTED_CYCLE"
        and parent["orientation"] == "HAS_DIRECTED_CYCLE"
        and "ROOT_TRANSITIVITY" in parent["labels"]
    ]
    assert len(tree_parents) == 1
    assert len(cycle_parents) == 1
    tree_parent = tree_parents[0]
    cycle_parent = cycle_parents[0]
    assert "INHERITED_DERIVED" in tree_parent["labels"]

    parts = tuple(tuple(part) for part in record["before_parts"])
    component_of = vertex_components(parts)
    vertices = frozenset(range(len(parts)))

    tree_records = quotient_edges(tree_parent["edges"], component_of)
    cycle_records = quotient_edges(cycle_parent["edges"], component_of)
    result_records = quotient_edges(record["clause_edges"], component_of)
    tree_edges = simple_edge_set(tree_records)
    cycle_edges = simple_edge_set(cycle_records)
    result_edges = simple_edge_set(result_records)

    assert len(tree_edges) == len(vertices) - 1
    assert connected(vertices, tree_edges)
    assert len(cycle_edges) == 3
    cycle_vertices = frozenset(vertex for edge in cycle_edges for vertex in edge)
    assert len(cycle_vertices) == 3
    assert all(sum(vertex in edge for edge in cycle_edges) == 2 for vertex in cycle_vertices)

    pivot = int(origin["pivot"])
    pivot_tree = [edge for edge, literal in tree_records if abs(literal) == pivot]
    pivot_cycle = [edge for edge, literal in cycle_records if abs(literal) == pivot]
    assert len(pivot_tree) == 1
    assert len(pivot_cycle) == 1
    pivot_edge = pivot_tree[0]
    assert pivot_edge == pivot_cycle[0]

    bad_literal = int(record["bad_literal"])
    bad_cycle = [edge for edge, literal in cycle_records if literal == bad_literal]
    bad_result = [edge for edge, literal in result_records if literal == bad_literal]
    assert len(bad_cycle) == 1
    assert len(bad_result) == 1
    bad_edge = bad_cycle[0]
    assert bad_edge == bad_result[0]

    common_edges = (tree_edges & cycle_edges) - {pivot_edge}
    assert len(common_edges) == 1
    common_edge = next(iter(common_edges))
    assert cycle_edges == frozenset((pivot_edge, common_edge, bad_edge))

    expected_result = frozenset((tree_edges - {pivot_edge}) | {bad_edge})
    assert result_edges == expected_result
    assert len(result_edges) == len(vertices) - 1
    assert connected(vertices, result_edges)

    pivot_cut = cut_after_removal(vertices, tree_edges, pivot_edge)
    bad_cut = cut_after_removal(vertices, result_edges, bad_edge)
    assert pivot_cut == bad_cut

    bad_tail_vertex = int(record["bad_direction"][0])
    bad_tail_component = component_of[bad_tail_vertex]
    tail_sides = [part for part in bad_cut if bad_tail_component in part]
    assert len(tail_sides) == 1
    tail_side = tail_sides[0]
    assert len(tail_side) == 2

    selected = int(record["selected"])
    assert tuple(record["maximum_variables"]) == (selected,)
    selected_tail, selected_head = record["selected_direction"]
    selected_edge = tuple(sorted((
        component_of[int(selected_tail)],
        component_of[int(selected_head)],
    )))
    assert selected_edge in result_edges
    assert set(selected_edge) == set(tail_side)
    internal_edges = frozenset(
        edge for edge in result_edges if set(edge) <= set(tail_side)
    )
    assert internal_edges == frozenset((selected_edge,))

    children = tuple(record["children"])
    assert tuple(child["fate"] for child in children) == (
        "CLAUSE_EXTINCT",
        "TAIL_SINGLETON_SAFE",
    )

    return {
        "n": int(record["n"]),
        "state_id": int(record["state_id"]),
        "pivot": pivot,
        "selected": selected,
        "pivot_edge": pivot_edge,
        "common_edge": common_edge,
        "bad_edge": bad_edge,
        "cut": tuple(sorted(tuple(sorted(part)) for part in bad_cut)),
        "tail_side": tuple(sorted(tail_side)),
    }


def self_test():
    counts = Counter()
    rows = []
    for n in range(4, 9):
        data = provenance_audit(n)
        for record in data["records"]:
            rows.append(verify_record(record))
            counts["certified_occurrences"] += 1
            counts[f"order_{n}"] += 1

    assert counts["certified_occurrences"] == 3
    assert counts["order_8"] == 3
    assert len({row["state_id"] for row in rows}) == 1
    assert {row["pivot"] for row in rows} == {1}
    assert {row["selected"] for row in rows} == {8}

    print("JANUS_GT_NONROOT_TRANSITIVITY_TREE_EXCHANGE = PASS")
    print(f"COUNTS = {tuple(sorted(counts.items()))}")
    print(f"ROWS = {tuple(rows)}")
    print(
        "claim_boundary = pure tree-exchange lemma plus exact GT_4..GT_8 "
        "instantiation; arbitrary-n producer normal-form reachability open"
    )


if __name__ == "__main__":
    self_test()
