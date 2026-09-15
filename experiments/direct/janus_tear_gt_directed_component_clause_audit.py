#!/usr/bin/env python3
"""Classify signed component graphs of every pre-frontier GT local resolvent.

Undirected C024 evidence found only three classes: spanning trees, external
cycles, and clauses with internal literals; no proper external forest appeared.
This audit restores literal orientation.

A positive variable for unordered pair (u,v), u<v, represents u<v and is mapped
to directed edge u->v.  A negative literal represents v<u and reverses the edge.
After quotienting by current Hasse components, spanning trees are classified as:

- IN_ARBORESCENCE: one sink root, every other component has outdegree one;
- OUT_ARBORESCENCE: one source root, every other component has indegree one;
- MIXED_TREE: underlying spanning tree with neither orientation pattern.

External cyclic clauses are checked for directed-cycle support.  Certified
component-unit origins and direct post-local units are cross-referenced.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_pre_unit_recursive_provenance import audit as provenance_audit


def directed_edges(clause, graph, pairs):
    parts = tuple(graph["parts"])
    index = {
        vertex: component_index
        for component_index, component in enumerate(parts)
        for vertex in component
    }
    external = []
    internal = []
    for literal in clause:
        low, high = pairs[abs(literal)]
        tail, head = (low, high) if literal > 0 else (high, low)
        tail_component = index[tail]
        head_component = index[head]
        if tail_component == head_component:
            internal.append((tail_component, literal))
        else:
            external.append((tail_component, head_component, literal))
    return tuple(external), tuple(internal)


def reachable(start, adjacency):
    seen = set()
    stack = [start]
    while stack:
        vertex = stack.pop()
        if vertex in seen:
            continue
        seen.add(vertex)
        stack.extend(adjacency.get(vertex, ()))
    return seen


def has_directed_cycle(vertex_count, edges):
    adjacency = defaultdict(list)
    for tail, head, _literal in edges:
        adjacency[tail].append(head)
    visiting = set()
    visited = set()

    def dfs(vertex):
        if vertex in visiting:
            return True
        if vertex in visited:
            return False
        visiting.add(vertex)
        for other in adjacency.get(vertex, ()):
            if dfs(other):
                return True
        visiting.remove(vertex)
        visited.add(vertex)
        return False

    return any(dfs(vertex) for vertex in range(vertex_count))


def orientation_class(clause, graph, pairs):
    component_count = int(graph["component_count"])
    edges, internal = directed_edges(clause, graph, pairs)
    indegree = Counter()
    outdegree = Counter()
    adjacency = defaultdict(list)
    reverse = defaultdict(list)
    for tail, head, _literal in edges:
        outdegree[tail] += 1
        indegree[head] += 1
        adjacency[tail].append(head)
        reverse[head].append(tail)

    if internal:
        classification = "HAS_INTERNAL_LITERAL"
        roots = ()
    elif graph["spanning_tree"]:
        sink_roots = tuple(
            vertex
            for vertex in range(component_count)
            if outdegree[vertex] == 0
            and all(
                outdegree[other] == 1
                for other in range(component_count)
                if other != vertex
            )
            and len(reachable(vertex, reverse)) == component_count
        )
        source_roots = tuple(
            vertex
            for vertex in range(component_count)
            if indegree[vertex] == 0
            and all(
                indegree[other] == 1
                for other in range(component_count)
                if other != vertex
            )
            and len(reachable(vertex, adjacency)) == component_count
        )
        if sink_roots:
            classification = "IN_ARBORESCENCE"
            roots = sink_roots
        elif source_roots:
            classification = "OUT_ARBORESCENCE"
            roots = source_roots
        else:
            classification = "MIXED_SPANNING_TREE"
            roots = ()
    elif graph["classification"] == "EXTERNAL_CYCLE":
        classification = (
            "HAS_DIRECTED_CYCLE"
            if has_directed_cycle(component_count, edges)
            else "UNDIRECTED_CYCLE_ONLY"
        )
        roots = ()
    else:
        classification = str(graph["classification"])
        roots = ()

    return {
        "classification": classification,
        "roots": roots,
        "edges": edges,
        "internal": internal,
        "indegree": tuple(sorted(indegree.items())),
        "outdegree": tuple(sorted(outdegree.items())),
    }


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    dangerous_event_ids = set()
    provenance = provenance_audit(n)
    for merge in provenance["records"]:
        for path in merge["shortest_paths"]:
            event = path["origin_event"]
            assert event is not None
            dangerous_event_ids.add(
                (int(event["state_id"]), int(event["event_index"]))
            )

    counts: Counter[str] = Counter()
    width_by_class: dict[str, Counter[int]] = defaultdict(Counter)
    component_count_by_class: dict[str, Counter[int]] = defaultdict(Counter)
    dangerous_classes: Counter[str] = Counter()
    direct_unit_classes: Counter[str] = Counter()
    mixed_tree_examples = []
    undirected_only_cycle_examples = []
    records = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        state_id = int(state["id"])

        for event_index, event in enumerate(state.get("resolution_events", [])):
            clause = tuple(event["resolvent"])
            graph = clause_component_graph(n, clause, assignment, pairs)
            orientation = orientation_class(clause, graph, pairs)
            classification = str(orientation["classification"])
            is_dangerous = (state_id, event_index) in dangerous_event_ids
            is_direct_unit = (
                len(clause) == 1
                and graph["spanning_tree"]
                and int(graph["component_count"]) == 2
            )

            counts[classification] += 1
            width_by_class[classification][len(clause)] += 1
            component_count_by_class[classification][
                int(graph["component_count"])
            ] += 1
            if is_dangerous:
                dangerous_classes[classification] += 1
            if is_direct_unit:
                direct_unit_classes[classification] += 1

            record = {
                "state_id": state_id,
                "call_id": call_id,
                "event_index": event_index,
                "novelty": novelty,
                "clause": clause,
                "undirected_class": graph["classification"],
                "directed_class": classification,
                "component_count": graph["component_count"],
                "roots": orientation["roots"],
                "dangerous_origin": is_dangerous,
                "direct_component_unit": is_direct_unit,
            }
            if classification == "MIXED_SPANNING_TREE" and len(mixed_tree_examples) < 20:
                mixed_tree_examples.append(record)
            if classification == "UNDIRECTED_CYCLE_ONLY" and len(undirected_only_cycle_examples) < 20:
                undirected_only_cycle_examples.append(record)
            if is_dangerous or is_direct_unit:
                records.append(record)

    assert sum(dangerous_classes.values()) == len(dangerous_event_ids)
    assert dangerous_classes["IN_ARBORESCENCE"] == len(dangerous_event_ids)
    assert direct_unit_classes["IN_ARBORESCENCE"] == sum(
        direct_unit_classes.values()
    )

    tree_total = (
        counts["IN_ARBORESCENCE"]
        + counts["OUT_ARBORESCENCE"]
        + counts["MIXED_SPANNING_TREE"]
    )

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "tree_total": tree_total,
        "width_by_class": tuple(
            (classification, tuple(sorted(histogram.items())))
            for classification, histogram in sorted(width_by_class.items())
        ),
        "component_count_by_class": tuple(
            (classification, tuple(sorted(histogram.items())))
            for classification, histogram in sorted(component_count_by_class.items())
        ),
        "dangerous_classes": tuple(sorted(dangerous_classes.items())),
        "direct_unit_classes": tuple(sorted(direct_unit_classes.items())),
        "mixed_tree_examples": tuple(mixed_tree_examples),
        "undirected_only_cycle_examples": tuple(undirected_only_cycle_examples),
        "selected_records": tuple(records),
    }


def self_test() -> None:
    rows = []
    aggregate: Counter[str] = Counter()
    aggregate_dangerous: Counter[str] = Counter()
    aggregate_units: Counter[str] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate.update(dict(data["counts"]))
        aggregate_dangerous.update(dict(data["dangerous_classes"]))
        aggregate_units.update(dict(data["direct_unit_classes"]))
        rows.append(
            (
                n,
                data["target"],
                data["counts"],
                data["tree_total"],
                data["dangerous_classes"],
                data["direct_unit_classes"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  tree_total = {data['tree_total']}")
        print(f"  width_by_class = {data['width_by_class']}")
        print(f"  component_count_by_class = {data['component_count_by_class']}")
        print(f"  dangerous_classes = {data['dangerous_classes']}")
        print(f"  direct_unit_classes = {data['direct_unit_classes']}")
        print(f"  mixed_tree_examples = {data['mixed_tree_examples']}")
        print(
            "  undirected_only_cycle_examples = "
            f"{data['undirected_only_cycle_examples']}"
        )
        print(f"  selected_records = {data['selected_records']}")

    print("JANUS_GT_DIRECTED_COMPONENT_CLAUSE_AUDIT = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_counts = {tuple(sorted(aggregate.items()))}")
    print(f"aggregate_dangerous = {tuple(sorted(aggregate_dangerous.items()))}")
    print(f"aggregate_direct_units = {tuple(sorted(aggregate_units.items()))}")
    print("claim_boundary = finite directed-structure census; closure of all local Resolution events remains unproved")


if __name__ == "__main__":
    self_test()
