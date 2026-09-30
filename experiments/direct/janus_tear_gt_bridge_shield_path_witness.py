#!/usr/bin/env python3
"""Extract explicit pivot-avoiding path witnesses for every non-tail bridge.

For each pre-frontier component-spanning clause C with a bridge literal l that
is not tail-singleton, and for every component-spanning clause D containing the
complement -l, the blocker census says -l is non-bridge.  This checker makes
that statement constructive: after deleting -l from D it emits a shortest
component path connecting the pivot endpoints.

The path is also classified by orientation and by one-generation root ancestry
of C and D.  The resulting histogram is intended to reveal the finite template
needed for the arbitrary-n induction.
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


def shortest_alternate_path(clause, graph, pairs, removed_literal, start, goal):
    directed = {
        int(edge_literal): (int(tail), int(head))
        for tail, head, edge_literal in directed_edges(clause, graph, pairs)[0]
    }
    adjacency = defaultdict(list)
    for left, right, edge_literal in graph["external_edges"]:
        edge_literal = int(edge_literal)
        if edge_literal == removed_literal:
            continue
        left = int(left)
        right = int(right)
        adjacency[left].append((right, edge_literal))
        adjacency[right].append((left, edge_literal))

    queue = deque([int(start)])
    predecessor = {int(start): None}
    while queue:
        vertex = queue.popleft()
        if vertex == int(goal):
            break
        for other, edge_literal in sorted(adjacency.get(vertex, ()), key=repr):
            if other in predecessor:
                continue
            predecessor[other] = (vertex, edge_literal)
            queue.append(other)

    assert int(goal) in predecessor
    vertices = [int(goal)]
    literals = []
    cursor = int(goal)
    while predecessor[cursor] is not None:
        previous, edge_literal = predecessor[cursor]
        vertices.append(previous)
        literals.append(edge_literal)
        cursor = previous
    vertices.reverse()
    literals.reverse()

    orientation_word = []
    for index, edge_literal in enumerate(literals):
        source = vertices[index]
        destination = vertices[index + 1]
        tail, head = directed[edge_literal]
        if (source, destination) == (tail, head):
            orientation_word.append("F")
        elif (source, destination) == (head, tail):
            orientation_word.append("R")
        else:
            raise AssertionError("path edge endpoints disagree with directed edge")

    return {
        "vertices": tuple(vertices),
        "literals": tuple(literals),
        "orientation_word": "".join(orientation_word),
        "length": len(literals),
    }


def primary_label(labels):
    label = labels[0]
    if label[0] == "ROOT_NON_MINIMALITY":
        return f"ROOT_NON_MINIMALITY({label[1]})"
    return str(label[0])


def audit(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2
    minimum_labels = root_minimum_labels(n, pairs)

    counts: Counter[str] = Counter()
    path_lengths: Counter[int] = Counter()
    orientation_words: Counter[str] = Counter()
    role_path_lengths: Counter[tuple[str, int]] = Counter()
    ancestry_pairs: Counter[tuple[str, str]] = Counter()
    orientation_pairs: Counter[tuple[str, str]] = Counter()
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
        orientations = {
            clause: str(orientation_class(clause, graphs[clause], pairs)["classification"])
            for clause in key
        }
        labels = {
            clause: direct_root_labels(root, clause, assignment, minimum_labels)
            for clause in key
        }

        for clause in key:
            if classes[clause] != "COMPONENT_SPANNING":
                continue
            for literal in clause:
                literal = int(literal)
                record = bridge_record(clause, graphs[clause], pairs, literal)
                if record is None or record["role"] == "TAIL_SINGLETON":
                    continue

                counts["non_tail_bridge_occurrences"] += 1
                complement_witnesses = 0
                for other in key:
                    if -literal not in other or classes[other] != "COMPONENT_SPANNING":
                        continue
                    other_bridge = bridge_record(other, graphs[other], pairs, -literal)
                    assert other_bridge is None

                    # l : u -> v, while -l : v -> u.  Delete -l and find an
                    # alternate path from v to u in the complementary parent.
                    start = int(record["head"])
                    goal = int(record["tail"])
                    path = shortest_alternate_path(
                        other,
                        graphs[other],
                        pairs,
                        -literal,
                        start,
                        goal,
                    )
                    assert path["length"] >= 1

                    complement_witnesses += 1
                    counts["spanning_complement_path_witnesses"] += 1
                    path_lengths[int(path["length"])] += 1
                    orientation_words[str(path["orientation_word"])] += 1
                    role_path_lengths[(str(record["role"]), int(path["length"]))] += 1
                    ancestry_pairs[(
                        primary_label(labels[clause]),
                        primary_label(labels[other]),
                    )] += 1
                    orientation_pairs[(orientations[clause], orientations[other])] += 1

                    if len(examples) < 60:
                        examples.append({
                            "n": n,
                            "state_id": int(state["id"]),
                            "call_id": call_id,
                            "novelty": novelty,
                            "bad_clause": clause,
                            "bad_literal": literal,
                            "bad_role": str(record["role"]),
                            "bad_orientation": orientations[clause],
                            "bad_ancestry": labels[clause],
                            "complement_clause": other,
                            "complement_orientation": orientations[other],
                            "complement_ancestry": labels[other],
                            "path": path,
                        })

                assert complement_witnesses >= 1
                counts["non_tail_occurrences_with_path_shield"] += 1

    assert counts["non_tail_bridge_occurrences"] == counts[
        "non_tail_occurrences_with_path_shield"
    ]
    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "path_lengths": tuple(sorted(path_lengths.items())),
        "orientation_words": tuple(sorted(orientation_words.items())),
        "role_path_lengths": tuple(sorted(role_path_lengths.items(), key=repr)),
        "ancestry_pairs": tuple(sorted(ancestry_pairs.items(), key=repr)),
        "orientation_pairs": tuple(sorted(orientation_pairs.items())),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_lengths: Counter[int] = Counter()
    aggregate_words: Counter[str] = Counter()
    aggregate_role_lengths: Counter[tuple[str, int]] = Counter()
    aggregate_ancestry: Counter[tuple[str, str]] = Counter()
    aggregate_orientation: Counter[tuple[str, str]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_lengths.update(dict(data["path_lengths"]))
        aggregate_words.update(dict(data["orientation_words"]))
        aggregate_role_lengths.update(dict(data["role_path_lengths"]))
        aggregate_ancestry.update(dict(data["ancestry_pairs"]))
        aggregate_orientation.update(dict(data["orientation_pairs"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  path_lengths = {data['path_lengths']}")
        print(f"  orientation_words = {data['orientation_words']}")
        print(f"  role_path_lengths = {data['role_path_lengths']}")
        print(f"  ancestry_pairs = {data['ancestry_pairs']}")
        print(f"  orientation_pairs = {data['orientation_pairs']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["non_tail_bridge_occurrences"] == 62
    assert aggregate_counts["non_tail_occurrences_with_path_shield"] == 62
    assert aggregate_counts["spanning_complement_path_witnesses"] >= 62

    print("JANUS_GT_BRIDGE_SHIELD_PATH_WITNESS = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_path_lengths = {tuple(sorted(aggregate_lengths.items()))}")
    print(f"aggregate_orientation_words = {tuple(sorted(aggregate_words.items()))}")
    print(f"aggregate_role_path_lengths = {tuple(sorted(aggregate_role_lengths.items(), key=repr))}")
    print(f"aggregate_ancestry_pairs = {tuple(sorted(aggregate_ancestry.items(), key=repr))}")
    print(f"aggregate_orientation_pairs = {tuple(sorted(aggregate_orientation.items()))}")
    print(
        "claim_boundary = explicit finite alternate-path shields through GT_8; "
        "path-template induction remains open"
    )


if __name__ == "__main__":
    self_test()
