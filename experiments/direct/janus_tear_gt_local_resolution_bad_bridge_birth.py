#!/usr/bin/env python3
"""Audit fresh non-tail bridge births at one-pass local Resolution events.

A branch-lifecycle census showed that every bad bridge occurrence already exists
in the parent post-result.  This checker moves to the exact Resolution event.
For every fresh resolvent and every non-tail bridge literal in it, it records:

- whether the same literal was already a non-tail bridge in either parent;
- the component classes and directed classes of both parents;
- a shortest pivot-avoiding path for the literal in every parent where it was
  non-bridge;
- whether the Resolution pivot lies on that alternate path;
- the endpoint component sizes before and after the inference.

No component contraction occurs during Resolution, so a new bridge can only be
created by deleting the pivot literals and combining the remaining parent
edges.  The histogram isolates the finite template needed for the arbitrary-n
Resolution induction.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_bridge_shield_path_witness import shortest_alternate_path
from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    parent_role_histogram: Counter[tuple[str, ...]] = Counter()
    parent_class_histogram: Counter[tuple[str, str]] = Counter()
    parent_orientation_histogram: Counter[tuple[str, str]] = Counter()
    alternate_path_lengths: Counter[int] = Counter()
    alternate_path_words: Counter[str] = Counter()
    pivot_on_path_histogram: Counter[bool] = Counter()
    endpoint_size_histogram: Counter[tuple[int, int]] = Counter()
    new_birth_examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]
        state_id = int(state["id"])

        for event_index, event in enumerate(state.get("resolution_events", [])):
            left = tuple(event["left"])
            right = tuple(event["right"])
            resolvent = tuple(event["resolvent"])
            pivot = int(event["pivot"])

            clauses = (left, right, resolvent)
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

            if classes[resolvent] != "COMPONENT_SPANNING":
                continue

            for literal in resolvent:
                literal = int(literal)
                result_bridge = bridge_record(
                    resolvent, graphs[resolvent], pairs, literal
                )
                if result_bridge is None or result_bridge["role"] == "TAIL_SINGLETON":
                    continue

                counts["bad_resolvent_literal_occurrences"] += 1
                result_sizes = endpoint_sizes(graphs[resolvent], literal, pairs)
                assert result_sizes["tail_size"] == 1
                assert result_sizes["head_size"] >= 2
                endpoint_size_histogram[(
                    int(result_sizes["tail_size"]),
                    int(result_sizes["head_size"]),
                )] += 1

                parent_records = []
                parent_roles = []
                preexisting_bad = False
                for label, parent in (("LEFT", left), ("RIGHT", right)):
                    if literal not in parent:
                        continue
                    parent_bridge = (
                        bridge_record(parent, graphs[parent], pairs, literal)
                        if classes[parent] == "COMPONENT_SPANNING"
                        else None
                    )
                    if parent_bridge is None:
                        role = "NONBRIDGE_OR_NONSPANNING"
                    else:
                        role = str(parent_bridge["role"])
                        if role != "TAIL_SINGLETON":
                            preexisting_bad = True
                    parent_roles.append(role)

                    path = None
                    if parent_bridge is None and classes[parent] == "COMPONENT_SPANNING":
                        sizes = endpoint_sizes(graphs[parent], literal, pairs)
                        path = shortest_alternate_path(
                            parent,
                            graphs[parent],
                            pairs,
                            literal,
                            int(sizes["tail_component"]),
                            int(sizes["head_component"]),
                        )
                        alternate_path_lengths[int(path["length"])] += 1
                        alternate_path_words[str(path["orientation_word"])] += 1
                        pivot_on_path = any(
                            abs(int(edge_literal)) == pivot
                            for edge_literal in path["literals"]
                        )
                        pivot_on_path_histogram[pivot_on_path] += 1
                    else:
                        pivot_on_path = None

                    parent_records.append({
                        "side": label,
                        "clause": parent,
                        "class": classes[parent],
                        "orientation": orientations[parent],
                        "bridge_role": role,
                        "path": path,
                        "pivot_on_path": pivot_on_path,
                        "sizes": endpoint_sizes(graphs[parent], literal, pairs),
                    })

                assert parent_records
                parent_role_histogram[tuple(sorted(parent_roles))] += 1
                parent_class_histogram[(classes[left], classes[right])] += 1
                parent_orientation_histogram[(orientations[left], orientations[right])] += 1

                if preexisting_bad:
                    counts["preexisting_bad_resolvent_literals"] += 1
                    continue

                counts["fresh_bad_resolvent_literals"] += 1
                if any(record["pivot_on_path"] for record in parent_records):
                    counts["fresh_birth_with_pivot_on_alternate_path"] += 1
                if all(
                    record["pivot_on_path"] in (None, True)
                    for record in parent_records
                ):
                    counts["all_relevant_paths_use_pivot"] += 1

                if len(new_birth_examples) < 120:
                    new_birth_examples.append({
                        "n": n,
                        "state_id": state_id,
                        "call_id": call_id,
                        "event_index": event_index,
                        "novelty": novelty,
                        "pivot": pivot,
                        "left": left,
                        "right": right,
                        "resolvent": resolvent,
                        "literal": literal,
                        "result_role": str(result_bridge["role"]),
                        "result_sizes": result_sizes,
                        "left_class": classes[left],
                        "right_class": classes[right],
                        "left_orientation": orientations[left],
                        "right_orientation": orientations[right],
                        "parents_with_literal": tuple(parent_records),
                    })

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "parent_role_histogram": tuple(sorted(parent_role_histogram.items(), key=repr)),
        "parent_class_histogram": tuple(sorted(parent_class_histogram.items())),
        "parent_orientation_histogram": tuple(sorted(parent_orientation_histogram.items())),
        "alternate_path_lengths": tuple(sorted(alternate_path_lengths.items())),
        "alternate_path_words": tuple(sorted(alternate_path_words.items())),
        "pivot_on_path_histogram": tuple(sorted(pivot_on_path_histogram.items())),
        "endpoint_size_histogram": tuple(sorted(endpoint_size_histogram.items())),
        "new_birth_examples": tuple(new_birth_examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_roles: Counter[tuple[str, ...]] = Counter()
    aggregate_classes: Counter[tuple[str, str]] = Counter()
    aggregate_orientations: Counter[tuple[str, str]] = Counter()
    aggregate_lengths: Counter[int] = Counter()
    aggregate_words: Counter[str] = Counter()
    aggregate_pivot_path: Counter[bool] = Counter()
    aggregate_sizes: Counter[tuple[int, int]] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_roles.update(dict(data["parent_role_histogram"]))
        aggregate_classes.update(dict(data["parent_class_histogram"]))
        aggregate_orientations.update(dict(data["parent_orientation_histogram"]))
        aggregate_lengths.update(dict(data["alternate_path_lengths"]))
        aggregate_words.update(dict(data["alternate_path_words"]))
        aggregate_pivot_path.update(dict(data["pivot_on_path_histogram"]))
        aggregate_sizes.update(dict(data["endpoint_size_histogram"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  parent_role_histogram = {data['parent_role_histogram']}")
        print(f"  parent_class_histogram = {data['parent_class_histogram']}")
        print(f"  parent_orientation_histogram = {data['parent_orientation_histogram']}")
        print(f"  alternate_path_lengths = {data['alternate_path_lengths']}")
        print(f"  alternate_path_words = {data['alternate_path_words']}")
        print(f"  pivot_on_path_histogram = {data['pivot_on_path_histogram']}")
        print(f"  endpoint_size_histogram = {data['endpoint_size_histogram']}")
        print(f"  new_birth_examples = {data['new_birth_examples']}")

    assert aggregate_counts["fresh_bad_resolvent_literals"] > 0
    print("JANUS_GT_LOCAL_RESOLUTION_BAD_BRIDGE_BIRTH = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_parent_roles = {tuple(sorted(aggregate_roles.items(), key=repr))}")
    print(f"aggregate_parent_classes = {tuple(sorted(aggregate_classes.items()))}")
    print(f"aggregate_parent_orientations = {tuple(sorted(aggregate_orientations.items()))}")
    print(f"aggregate_alternate_path_lengths = {tuple(sorted(aggregate_lengths.items()))}")
    print(f"aggregate_alternate_path_words = {tuple(sorted(aggregate_words.items()))}")
    print(f"aggregate_pivot_on_path = {tuple(sorted(aggregate_pivot_path.items()))}")
    print(f"aggregate_endpoint_sizes = {tuple(sorted(aggregate_sizes.items()))}")
    print(
        "claim_boundary = finite local-Resolution birth census through GT_8; "
        "arbitrary-n Resolution induction remains open"
    )


if __name__ == "__main__":
    self_test()
