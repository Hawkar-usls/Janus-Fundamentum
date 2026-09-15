#!/usr/bin/env python3
"""Census every non-root transitivity x in-arborescence Resolution exchange.

The remaining C024 local gate asks why every reachable non-root immediate-local
unshielded bridge has the proved two-node tail-wing form.  The three finite
examples are produced by resolving a root transitivity triangle against an
inherited in-arborescence.  This checker broadens the microscope to *all* such
non-root frozen Resolution events through GT_8.

For each event with one `HAS_DIRECTED_CYCLE` parent and one
`IN_ARBORESCENCE` component-spanning parent it reconstructs:

- the directed tree root, height and number of non-star edges;
- whether the cycle is a direct residual of a root transitivity axiom;
- whether the inference is the exact one-edge tree exchange;
- the pivot-cut side sizes;
- every newly introduced bridge and its cut side sizes;
- whether that bridge is one of the complete unshielded P-occurrences;
- whether the deterministic selected comparison is internal to the pivot side.

No normal form is assumed.  The script is a finite discovery certificate; the
arbitrary-n producer reachability theorem remains open.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import (
    directed_edges,
    orientation_class,
)
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_same_cut_parent_ancestry import (
    direct_root_labels,
    root_minimum_labels,
)
from janus_tear_gt_unshielded_birth_handoff_census import audit as handoff_audit

Clause = tuple[int, ...]
Edge = tuple[int, int]


def component_map(parts, n: int) -> tuple[int, ...]:
    out = [-1] * n
    for index, part in enumerate(parts):
        for vertex in part:
            out[int(vertex)] = int(index)
    assert all(value >= 0 for value in out)
    return tuple(out)


def simple_external_edges(clause, graph, pairs):
    records = tuple(
        (int(tail), int(head), int(literal))
        for tail, head, literal in directed_edges(clause, graph, pairs)[0]
    )
    undirected = tuple(
        tuple(sorted((tail, head)))
        for tail, head, _literal in records
    )
    return records, frozenset(undirected), len(undirected) == len(set(undirected))


def graph_components(vertex_count: int, edges: frozenset[Edge]):
    adjacency = [set() for _ in range(vertex_count)]
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    unseen = set(range(vertex_count))
    parts = []
    while unseen:
        start = min(unseen)
        queue = deque([start])
        seen = {start}
        unseen.remove(start)
        while queue:
            vertex = queue.popleft()
            for other in adjacency[vertex]:
                if other in seen:
                    continue
                seen.add(other)
                unseen.discard(other)
                queue.append(other)
        parts.append(frozenset(seen))
    return tuple(sorted(parts, key=lambda part: (len(part), tuple(sorted(part)))))


def cut_after_removal(vertex_count: int, edges: frozenset[Edge], removed: Edge):
    assert removed in edges
    parts = graph_components(vertex_count, edges - {removed})
    if len(parts) != 2:
        return None
    return frozenset(parts)


def arborescence_profile(records, vertex_count: int):
    outgoing: dict[int, list[int]] = defaultdict(list)
    incoming: dict[int, list[int]] = defaultdict(list)
    for tail, head, _literal in records:
        outgoing[tail].append(head)
        incoming[head].append(tail)
    roots = tuple(vertex for vertex in range(vertex_count) if not outgoing[vertex])
    if len(roots) != 1:
        return None
    root = roots[0]
    if any(len(outgoing[vertex]) != (0 if vertex == root else 1) for vertex in range(vertex_count)):
        return None

    depth = {root: 0}
    unresolved = set(range(vertex_count)) - {root}
    while unresolved:
        progressed = False
        for vertex in tuple(unresolved):
            head = outgoing[vertex][0]
            if head not in depth:
                continue
            depth[vertex] = depth[head] + 1
            unresolved.remove(vertex)
            progressed = True
        if not progressed:
            return None

    nonstar = tuple(
        (tail, head)
        for tail, head, _literal in records
        if head != root
    )
    return {
        "root": root,
        "height": max(depth.values(), default=0),
        "depth_histogram": tuple(sorted(Counter(depth.values()).items())),
        "nonstar_edges": tuple(sorted(nonstar)),
        "nonstar_count": len(nonstar),
        "one_subdivision_star": len(nonstar) == 1 and max(depth.values()) == 2,
    }


def selected_component_edge(state, graph, pairs, n: int):
    selected = int(state["branch_var"])
    low, high = pairs[selected]
    cmap = component_map(graph["parts"], n)
    edge = tuple(sorted((cmap[int(low)], cmap[int(high)])))
    return selected, edge


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    root = tuple(context["root"])
    minimum_labels = root_minimum_labels(n, pairs)
    target = n - 2

    unshielded = {
        (
            int(item["state_id"]),
            tuple(item["clause"]),
            int(item["literal"]),
        )
        for item in handoff_audit(n)["rows"]
        if int(item["depth"]) > 0
    }

    counts: Counter[str] = Counter()
    tree_shapes: Counter[tuple[int, int, bool]] = Counter()
    pivot_side_sizes: Counter[tuple[int, int]] = Counter()
    new_bridge_side_sizes: Counter[tuple[int, int]] = Counter()
    unshielded_tree_shapes: Counter[tuple[int, int, bool]] = Counter()
    unshielded_pivot_sizes: Counter[tuple[int, int]] = Counter()
    selected_relations: Counter[str] = Counter()
    cycle_root_labels: Counter[tuple[str, ...]] = Counter()
    exchange_failures: Counter[str] = Counter()
    examples = []
    unshielded_examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        depth = int(state["depth"])
        novelty = int(levels[call_id])
        if depth == 0 or novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]

        for event_index, event in enumerate(state.get("resolution_events", ())):
            left = tuple(event["left"])
            right = tuple(event["right"])
            result = tuple(event["resolvent"])
            clauses = (left, right, result)
            graphs = {
                clause: clause_component_graph(n, clause, assignment, pairs)
                for clause in clauses
            }
            classes = {
                clause: str(safety_class(n, clause, assignment, pairs)["classification"])
                for clause in clauses
            }
            orientations = {
                clause: str(orientation_class(clause, graphs[clause], pairs)["classification"])
                for clause in clauses
            }
            tree_parents = [
                clause
                for clause in (left, right)
                if classes[clause] == "COMPONENT_SPANNING"
                and orientations[clause] == "IN_ARBORESCENCE"
            ]
            cycle_parents = [
                clause
                for clause in (left, right)
                if orientations[clause] == "HAS_DIRECTED_CYCLE"
            ]
            if len(tree_parents) != 1 or len(cycle_parents) != 1:
                continue
            tree = tree_parents[0]
            cycle = cycle_parents[0]
            if classes[result] != "COMPONENT_SPANNING":
                continue

            counts["candidate_events"] += 1
            vertex_count = int(graphs[tree]["component_count"])
            tree_records, tree_edges, tree_simple = simple_external_edges(
                tree, graphs[tree], pairs
            )
            cycle_records, cycle_edges, cycle_simple = simple_external_edges(
                cycle, graphs[cycle], pairs
            )
            result_records, result_edges, result_simple = simple_external_edges(
                result, graphs[result], pairs
            )
            profile = arborescence_profile(tree_records, vertex_count)
            if profile is None or not tree_simple:
                exchange_failures["TREE_NOT_SIMPLE_ARBORESCENCE"] += 1
                continue
            counts["simple_arborescence_events"] += 1
            shape = (
                int(profile["height"]),
                int(profile["nonstar_count"]),
                bool(profile["one_subdivision_star"]),
            )
            tree_shapes[shape] += 1

            labels = direct_root_labels(
                root, cycle, assignment, minimum_labels
            )
            label_names = tuple(sorted(str(label[0]) for label in labels))
            cycle_root_labels[label_names] += 1

            pivot = int(event["pivot"])
            pivot_tree = [
                tuple(sorted((tail, head)))
                for tail, head, literal in tree_records
                if abs(literal) == pivot
            ]
            if len(pivot_tree) != 1:
                exchange_failures["PIVOT_NOT_UNIQUE_EXTERNAL_TREE_EDGE"] += 1
                continue
            pivot_edge = pivot_tree[0]
            pivot_cut = cut_after_removal(vertex_count, tree_edges, pivot_edge)
            if pivot_cut is None:
                exchange_failures["PIVOT_NOT_TREE_BRIDGE"] += 1
                continue
            side_sizes = tuple(sorted(len(part) for part in pivot_cut))
            pivot_side_sizes[side_sizes] += 1

            exact_exchange = False
            new_edges = result_edges - tree_edges
            removed_edges = tree_edges - result_edges
            if (
                cycle_simple
                and result_simple
                and len(cycle_edges) == 3
                and len(new_edges) == 1
                and removed_edges == frozenset({pivot_edge})
                and result_edges == (tree_edges - {pivot_edge}) | new_edges
            ):
                exact_exchange = True
                counts["exact_tree_exchange"] += 1
            else:
                exchange_failures["NOT_EXACT_ONE_EDGE_EXCHANGE"] += 1

            selected, selected_edge = selected_component_edge(
                state, graphs[result], pairs, n
            )
            relation = "OUTSIDE_PIVOT_SIDE"
            selected_side = None
            for part in pivot_cut:
                if set(selected_edge) <= set(part):
                    relation = "INTERNAL_PIVOT_SIDE"
                    selected_side = part
                    break
            if selected_edge == pivot_edge:
                relation = "PIVOT"
            elif any(
                selected_edge[0] in part and selected_edge[1] not in part
                for part in pivot_cut
            ):
                relation = "CROSS_CUT"
            selected_relations[relation] += 1

            new_bridge_records = []
            for literal in result:
                literal = int(literal)
                bridge = bridge_record(result, graphs[result], pairs, literal)
                if bridge is None:
                    continue
                edge = tuple(sorted((int(bridge["tail"]), int(bridge["head"]))))
                if edge not in new_edges:
                    continue
                cut = bridge["cut"]
                sizes = tuple(sorted(len(part) for part in cut))
                new_bridge_side_sizes[sizes] += 1
                key = (state_id, result, literal)
                is_unshielded = key in unshielded
                if is_unshielded:
                    counts["unshielded_new_bridges"] += 1
                    unshielded_tree_shapes[shape] += 1
                    unshielded_pivot_sizes[side_sizes] += 1
                new_bridge_records.append({
                    "literal": literal,
                    "bridge": bridge,
                    "side_sizes": sizes,
                    "unshielded": is_unshielded,
                })

            event_record = {
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "depth": depth,
                "novelty": novelty,
                "event_index": event_index,
                "pivot": pivot,
                "tree": tree,
                "cycle": cycle,
                "result": result,
                "tree_profile": profile,
                "cycle_root_labels": labels,
                "pivot_edge": pivot_edge,
                "pivot_cut": tuple(sorted(tuple(sorted(part)) for part in pivot_cut)),
                "pivot_side_sizes": side_sizes,
                "exact_exchange": exact_exchange,
                "new_edges": tuple(sorted(new_edges)),
                "selected": selected,
                "selected_edge": selected_edge,
                "selected_relation": relation,
                "selected_internal_side": (
                    tuple(sorted(selected_side)) if selected_side is not None else None
                ),
                "new_bridges": tuple(new_bridge_records),
            }
            if len(examples) < 100:
                examples.append(event_record)
            if any(item["unshielded"] for item in new_bridge_records):
                unshielded_examples.append(event_record)

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "tree_shapes": tuple(sorted(tree_shapes.items(), key=repr)),
        "pivot_side_sizes": tuple(sorted(pivot_side_sizes.items())),
        "new_bridge_side_sizes": tuple(sorted(new_bridge_side_sizes.items())),
        "unshielded_tree_shapes": tuple(
            sorted(unshielded_tree_shapes.items(), key=repr)
        ),
        "unshielded_pivot_sizes": tuple(sorted(unshielded_pivot_sizes.items())),
        "selected_relations": tuple(sorted(selected_relations.items())),
        "cycle_root_labels": tuple(sorted(cycle_root_labels.items(), key=repr)),
        "exchange_failures": tuple(sorted(exchange_failures.items())),
        "examples": tuple(examples),
        "unshielded_examples": tuple(unshielded_examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[int, int, bool]] = Counter()
    aggregate_pivot_sizes: Counter[tuple[int, int]] = Counter()
    aggregate_bridge_sizes: Counter[tuple[int, int]] = Counter()
    aggregate_unshielded_shapes: Counter[tuple[int, int, bool]] = Counter()
    aggregate_unshielded_pivots: Counter[tuple[int, int]] = Counter()
    aggregate_relations: Counter[str] = Counter()
    aggregate_labels: Counter[tuple[str, ...]] = Counter()
    aggregate_failures: Counter[str] = Counter()
    all_unshielded = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["tree_shapes"]))
        aggregate_pivot_sizes.update(dict(data["pivot_side_sizes"]))
        aggregate_bridge_sizes.update(dict(data["new_bridge_side_sizes"]))
        aggregate_unshielded_shapes.update(dict(data["unshielded_tree_shapes"]))
        aggregate_unshielded_pivots.update(dict(data["unshielded_pivot_sizes"]))
        aggregate_relations.update(dict(data["selected_relations"]))
        aggregate_labels.update(dict(data["cycle_root_labels"]))
        aggregate_failures.update(dict(data["exchange_failures"]))
        all_unshielded.extend(data["unshielded_examples"])
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  tree_shapes = {data['tree_shapes']}")
        print(f"  pivot_side_sizes = {data['pivot_side_sizes']}")
        print(f"  new_bridge_side_sizes = {data['new_bridge_side_sizes']}")
        print(f"  unshielded_tree_shapes = {data['unshielded_tree_shapes']}")
        print(f"  unshielded_pivot_sizes = {data['unshielded_pivot_sizes']}")
        print(f"  selected_relations = {data['selected_relations']}")
        print(f"  cycle_root_labels = {data['cycle_root_labels']}")
        print(f"  exchange_failures = {data['exchange_failures']}")
        print(f"  unshielded_examples = {data['unshielded_examples']}")

    assert aggregate_counts["unshielded_new_bridges"] == 3
    assert len(all_unshielded) == 3
    print("JANUS_GT_NONROOT_ARBORESCENCE_EXCHANGE_CENSUS = PASS")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_TREE_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(f"AGGREGATE_PIVOT_SIDE_SIZES = {tuple(sorted(aggregate_pivot_sizes.items()))}")
    print(f"AGGREGATE_NEW_BRIDGE_SIDE_SIZES = {tuple(sorted(aggregate_bridge_sizes.items()))}")
    print(f"AGGREGATE_UNSHIELDED_TREE_SHAPES = {tuple(sorted(aggregate_unshielded_shapes.items(), key=repr))}")
    print(f"AGGREGATE_UNSHIELDED_PIVOT_SIZES = {tuple(sorted(aggregate_unshielded_pivots.items()))}")
    print(f"AGGREGATE_SELECTED_RELATIONS = {tuple(sorted(aggregate_relations.items()))}")
    print(f"AGGREGATE_CYCLE_ROOT_LABELS = {tuple(sorted(aggregate_labels.items(), key=repr))}")
    print(f"AGGREGATE_EXCHANGE_FAILURES = {tuple(sorted(aggregate_failures.items()))}")
    print(f"UNSHIELDED_EXAMPLES = {tuple(all_unshielded)}")
    print(
        "claim_boundary = complete finite census of non-root transitivity x "
        "in-arborescence exchanges through GT_8; arbitrary-n normal-form "
        "reachability remains open"
    )


if __name__ == "__main__":
    self_test()
