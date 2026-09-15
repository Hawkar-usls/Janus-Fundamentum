#!/usr/bin/env python3
"""Failure-tolerant local Resolution birth census for C024.

The first version incorrectly assumed that every fresh non-tail bridge already
has a merged head component.  A counterexample shows that local Resolution may
create the bridge while both oriented endpoint components are still singleton.
Because a fresh resolvent cannot be a parent again in the same one-pass state,
this is not itself the unsafe double-bridge obstruction.

This v2 census records all fresh non-tail bridge births and their endpoint
shapes, parent roles, and alternate paths without assuming merged-head at birth.
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
    endpoint_shapes: Counter[tuple[int, int]] = Counter()
    result_roles: Counter[str] = Counter()
    parent_roles: Counter[tuple[str, ...]] = Counter()
    parent_classes: Counter[tuple[str, str]] = Counter()
    parent_orientations: Counter[tuple[str, str]] = Counter()
    path_lengths: Counter[int] = Counter()
    path_words: Counter[str] = Counter()
    pivot_on_path: Counter[bool] = Counter()
    fresh_examples = []

    for state in policy.states.values():
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue
        assignment = context["call_after_pre"][call_id]

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

                counts["non_tail_resolvent_literals"] += 1
                sizes = endpoint_sizes(graphs[resolvent], literal, pairs)
                shape = (int(sizes["tail_size"]), int(sizes["head_size"]))
                endpoint_shapes[shape] += 1
                result_roles[str(result_bridge["role"])] += 1
                if shape == (1, 1):
                    counts["singleton_singleton_shape"] += 1
                if shape[0] == 1 and shape[1] >= 2:
                    counts["singleton_tail_merged_head_shape"] += 1
                if shape[0] >= 2:
                    counts["merged_tail_shape"] += 1

                records = []
                roles = []
                preexisting_bad = False
                for side, parent in (("LEFT", left), ("RIGHT", right)):
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
                    roles.append(role)

                    path = None
                    uses_pivot = None
                    if parent_bridge is None and classes[parent] == "COMPONENT_SPANNING":
                        parent_sizes = endpoint_sizes(graphs[parent], literal, pairs)
                        path = shortest_alternate_path(
                            parent,
                            graphs[parent],
                            pairs,
                            literal,
                            int(parent_sizes["tail_component"]),
                            int(parent_sizes["head_component"]),
                        )
                        path_lengths[int(path["length"])] += 1
                        path_words[str(path["orientation_word"])] += 1
                        uses_pivot = any(
                            abs(int(edge_literal)) == pivot
                            for edge_literal in path["literals"]
                        )
                        pivot_on_path[uses_pivot] += 1
                    records.append({
                        "side": side,
                        "clause": parent,
                        "class": classes[parent],
                        "orientation": orientations[parent],
                        "role": role,
                        "path": path,
                        "uses_pivot": uses_pivot,
                    })

                parent_roles[tuple(sorted(roles))] += 1
                parent_classes[(classes[left], classes[right])] += 1
                parent_orientations[(orientations[left], orientations[right])] += 1
                if preexisting_bad:
                    counts["preexisting_non_tail"] += 1
                    continue

                counts["fresh_non_tail_births"] += 1
                if any(record["uses_pivot"] for record in records):
                    counts["fresh_birth_with_pivot_path"] += 1
                if len(fresh_examples) < 100:
                    fresh_examples.append({
                        "n": n,
                        "state_id": int(state["id"]),
                        "call_id": call_id,
                        "event_index": event_index,
                        "novelty": novelty,
                        "pivot": pivot,
                        "resolvent": resolvent,
                        "literal": literal,
                        "result_role": str(result_bridge["role"]),
                        "endpoint_shape": shape,
                        "parents": tuple(records),
                    })

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "endpoint_shapes": tuple(sorted(endpoint_shapes.items())),
        "result_roles": tuple(sorted(result_roles.items())),
        "parent_roles": tuple(sorted(parent_roles.items(), key=repr)),
        "parent_classes": tuple(sorted(parent_classes.items())),
        "parent_orientations": tuple(sorted(parent_orientations.items())),
        "path_lengths": tuple(sorted(path_lengths.items())),
        "path_words": tuple(sorted(path_words.items())),
        "pivot_on_path": tuple(sorted(pivot_on_path.items())),
        "fresh_examples": tuple(fresh_examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_roles: Counter[str] = Counter()
    aggregate_parent_roles: Counter[tuple[str, ...]] = Counter()
    aggregate_paths: Counter[int] = Counter()
    aggregate_words: Counter[str] = Counter()
    aggregate_pivot: Counter[bool] = Counter()

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["endpoint_shapes"]))
        aggregate_roles.update(dict(data["result_roles"]))
        aggregate_parent_roles.update(dict(data["parent_roles"]))
        aggregate_paths.update(dict(data["path_lengths"]))
        aggregate_words.update(dict(data["path_words"]))
        aggregate_pivot.update(dict(data["pivot_on_path"]))
        print(f"ORDER_SIZE = {n}")
        print(f"  counts = {data['counts']}")
        print(f"  endpoint_shapes = {data['endpoint_shapes']}")
        print(f"  result_roles = {data['result_roles']}")
        print(f"  parent_roles = {data['parent_roles']}")
        print(f"  parent_classes = {data['parent_classes']}")
        print(f"  parent_orientations = {data['parent_orientations']}")
        print(f"  path_lengths = {data['path_lengths']}")
        print(f"  path_words = {data['path_words']}")
        print(f"  pivot_on_path = {data['pivot_on_path']}")
        print(f"  fresh_examples = {data['fresh_examples']}")

    assert aggregate_counts["fresh_non_tail_births"] > 0
    print("JANUS_GT_LOCAL_RESOLUTION_BAD_BRIDGE_BIRTH_V2 = PASS")
    print(f"aggregate_counts = {tuple(sorted(aggregate_counts.items()))}")
    print(f"aggregate_endpoint_shapes = {tuple(sorted(aggregate_shapes.items()))}")
    print(f"aggregate_result_roles = {tuple(sorted(aggregate_roles.items()))}")
    print(f"aggregate_parent_roles = {tuple(sorted(aggregate_parent_roles.items(), key=repr))}")
    print(f"aggregate_path_lengths = {tuple(sorted(aggregate_paths.items()))}")
    print(f"aggregate_path_words = {tuple(sorted(aggregate_words.items()))}")
    print(f"aggregate_pivot_on_path = {tuple(sorted(aggregate_pivot.items()))}")
    print(
        "claim_boundary = failure-tolerant finite local birth census through GT_8; "
        "temporal shielding before the next key remains to be proved"
    )


if __name__ == "__main__":
    self_test()
