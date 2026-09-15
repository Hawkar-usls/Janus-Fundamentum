#!/usr/bin/env python3
"""Classify root ancestry and parent geometry of merged-tail conflict lineages.

For the 17 fresh merged-tail non-tail bridge occurrences that are causally
consumed by post-local unit contradiction, this diagnostic records:

- conflict kind and direct/ancestor causal class;
- safety/orientation classes of the local Resolution parents;
- direct root ancestry of every all-source unit-reason closure clause;
- whether each closure source is an inherited key clause, an immediate local
  resolvent, a direct root residual, or another local output;
- which root non-minimality vertices occur relative to the bad literal tail and
  head.

The goal is to expose a small finite template for the arbitrary-n extinction
proof.  Only the already certified count of 17 causal cases is asserted.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import (
    clause_component_graph,
    execution_context,
)
from janus_tear_gt_directed_component_clause_audit import orientation_class
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit
from janus_tear_gt_merged_tail_state_diagnostic import final_event_class
from janus_tear_gt_merged_tail_unit_conflict_provenance import build_reason_certificate
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_nonminimality_bridge_shield import original_direction
from janus_tear_gt_same_cut_parent_ancestry import (
    direct_root_labels,
    root_minimum_labels,
)

CONFLICT_CLASSES = {
    "OPPOSITE_UNITS_CONFLICT",
    "EMPTY_ON_UNIT_ASSIGNMENT",
}


def primary_root_classes(labels):
    result = []
    for kind, vertex, _root_clause in labels:
        if kind == "ROOT_NON_MINIMALITY":
            result.append((str(kind), int(vertex)))
        else:
            result.append((str(kind), None))
    return tuple(sorted(result, key=repr))


def relative_vertex_class(vertex, tail, head):
    if vertex is None:
        return "NONE"
    if int(vertex) == int(tail):
        return "TAIL"
    if int(vertex) == int(head):
        return "HEAD"
    return "OTHER"


def audit(n: int):
    context = execution_context(n)
    root = tuple(context["root"])
    policy = context["policy"]
    pairs = context["pairs"]
    raw = raw_audit(n)
    minimum_labels = root_minimum_labels(n, pairs)

    counts: Counter[str] = Counter()
    conflict_kinds: Counter[str] = Counter()
    causal_classes: Counter[str] = Counter()
    parent_safety_pairs: Counter[tuple[str, str]] = Counter()
    parent_orientation_pairs: Counter[tuple[str, str]] = Counter()
    parent_role_pairs: Counter[tuple[str, ...]] = Counter()
    endpoint_shapes: Counter[tuple[int, int]] = Counter()
    closure_source_type_sets: Counter[tuple[str, ...]] = Counter()
    closure_root_class_sets: Counter[tuple[tuple[str, int | None], ...]] = Counter()
    closure_relative_minimum_sets: Counter[tuple[str, ...]] = Counter()
    closure_size_shapes: Counter[tuple[int, int]] = Counter()
    event_parent_root_pairs: Counter[
        tuple[
            tuple[tuple[str, int | None], ...],
            tuple[tuple[str, int | None], ...],
        ]
    ] = Counter()
    rows = []
    certificate_cache = {}

    for example in raw["fresh_examples"]:
        tail_size, head_size = tuple(example["endpoint_shape"])
        if int(tail_size) <= 1:
            continue

        state_id = int(example["state_id"])
        state = policy.states[state_id]
        post_events = tuple(state.get("post_units", ()))
        final_class = final_event_class(post_events)
        if final_class not in CONFLICT_CLASSES:
            counts["nonconflict_merged_tail_cases"] += 1
            continue

        counts["conflict_merged_tail_cases"] += 1
        event_index = int(example["event_index"])
        event = state["resolution_events"][event_index]
        event_clause = tuple(event["resolvent"])
        left = tuple(event["left"])
        right = tuple(event["right"])
        literal = int(example["literal"])
        tail_vertex, head_vertex = original_direction(literal, pairs)
        endpoint_shapes[(int(tail_size), int(head_size))] += 1

        call_id = int(example["call_id"])
        assignment = context["call_after_pre"][call_id]
        clauses = (left, right)
        graphs = {
            clause: clause_component_graph(n, clause, assignment, pairs)
            for clause in clauses
        }
        parent_safety = tuple(
            str(safety_class(n, clause, assignment, pairs)["classification"])
            for clause in clauses
        )
        parent_orientation = tuple(
            str(orientation_class(clause, graphs[clause], pairs)["classification"])
            for clause in clauses
        )
        parent_safety_pairs[parent_safety] += 1
        parent_orientation_pairs[parent_orientation] += 1

        roles = tuple(sorted(
            str(parent["role"])
            for parent in example["parents"]
        ))
        parent_role_pairs[roles] += 1

        left_labels = primary_root_classes(
            direct_root_labels(root, left, assignment, minimum_labels)
        )
        right_labels = primary_root_classes(
            direct_root_labels(root, right, assignment, minimum_labels)
        )
        event_parent_root_pairs[(left_labels, right_labels)] += 1

        if state_id not in certificate_cache:
            certificate_cache[state_id] = build_reason_certificate(
                tuple(state["resolution_output"]),
                post_events,
            )
        certificate = certificate_cache[state_id]
        conflict_kind = str(certificate["conflict_kind"])
        conflict_kinds[conflict_kind] += 1

        root_sources = set(certificate["conflict_root_sources"])
        closure_sources = tuple(certificate["closure_sources"])
        if event_clause in root_sources:
            causal = "DIRECT_CONFLICT_SOURCE"
        elif event_clause in set(closure_sources):
            causal = "ANCESTOR_CONFLICT_SOURCE"
        else:
            causal = "COLOCATED_NONCAUSAL"
        causal_classes[causal] += 1
        assert causal != "COLOCATED_NONCAUSAL"

        event_resolvents = {
            tuple(item["resolvent"])
            for item in state.get("resolution_events", ())
        }
        key = set(tuple(clause) for clause in state["key"])
        source_types = set()
        root_classes = set()
        relative_minimum = set()
        per_source = []

        for source in closure_sources:
            source = tuple(source)
            labels = primary_root_classes(
                direct_root_labels(root, source, assignment, minimum_labels)
            )
            if labels != (("INHERITED_DERIVED", None),):
                source_types.add("DIRECT_ROOT_RESIDUAL")
            if source in event_resolvents:
                source_types.add("IMMEDIATE_LOCAL_RESOLVENT")
            if source in key:
                source_types.add("INHERITED_KEY")
            if (
                labels == (("INHERITED_DERIVED", None),)
                and source not in event_resolvents
                and source not in key
            ):
                source_types.add("OTHER_OUTPUT")

            for kind, vertex in labels:
                root_classes.add((kind, vertex))
                if kind == "ROOT_NON_MINIMALITY":
                    relative_minimum.add(
                        relative_vertex_class(vertex, tail_vertex, head_vertex)
                    )

            per_source.append({
                "clause": source,
                "root_labels": labels,
                "in_key": source in key,
                "immediate_local": source in event_resolvents,
                "is_conflict_root": source in root_sources,
            })

        closure_source_type_sets[tuple(sorted(source_types))] += 1
        closure_root_class_sets[tuple(sorted(root_classes, key=repr))] += 1
        closure_relative_minimum_sets[tuple(sorted(relative_minimum))] += 1
        closure_size_shapes[(
            int(certificate["closure_source_count"]),
            int(certificate["closure_event_count"]),
        )] += 1

        rows.append({
            "n": n,
            "state_id": state_id,
            "call_id": call_id,
            "event_index": event_index,
            "bad_literal": literal,
            "tail_vertex": tail_vertex,
            "head_vertex": head_vertex,
            "endpoint_shape": (int(tail_size), int(head_size)),
            "pivot": int(event["pivot"]),
            "left": left,
            "right": right,
            "resolvent": event_clause,
            "parent_safety": parent_safety,
            "parent_orientation": parent_orientation,
            "parent_roles": roles,
            "parent_root_labels": (left_labels, right_labels),
            "conflict_kind": conflict_kind,
            "causal_class": causal,
            "closure_source_types": tuple(sorted(source_types)),
            "closure_root_classes": tuple(sorted(root_classes, key=repr)),
            "closure_relative_minimum": tuple(sorted(relative_minimum)),
            "closure_source_count": certificate["closure_source_count"],
            "closure_event_count": certificate["closure_event_count"],
            "closure_sources": tuple(per_source),
        })

    expected_conflicts = {4: 0, 5: 8, 6: 4, 7: 2, 8: 3}
    expected_nonconflicts = {4: 1, 5: 0, 6: 0, 7: 0, 8: 0}
    assert counts["conflict_merged_tail_cases"] == expected_conflicts[n]
    assert counts["nonconflict_merged_tail_cases"] == expected_nonconflicts[n]

    return {
        "n": n,
        "counts": tuple(sorted(counts.items())),
        "conflict_kinds": tuple(sorted(conflict_kinds.items())),
        "causal_classes": tuple(sorted(causal_classes.items())),
        "parent_safety_pairs": tuple(sorted(parent_safety_pairs.items())),
        "parent_orientation_pairs": tuple(sorted(parent_orientation_pairs.items())),
        "parent_role_pairs": tuple(sorted(parent_role_pairs.items(), key=repr)),
        "endpoint_shapes": tuple(sorted(endpoint_shapes.items())),
        "closure_source_type_sets": tuple(sorted(closure_source_type_sets.items(), key=repr)),
        "closure_root_class_sets": tuple(sorted(closure_root_class_sets.items(), key=repr)),
        "closure_relative_minimum_sets": tuple(sorted(closure_relative_minimum_sets.items(), key=repr)),
        "closure_size_shapes": tuple(sorted(closure_size_shapes.items())),
        "event_parent_root_pairs": tuple(sorted(event_parent_root_pairs.items(), key=repr)),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_conflicts: Counter[str] = Counter()
    aggregate_causal: Counter[str] = Counter()
    aggregate_safety: Counter[tuple[str, str]] = Counter()
    aggregate_orientation: Counter[tuple[str, str]] = Counter()
    aggregate_roles: Counter[tuple[str, ...]] = Counter()
    aggregate_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_source_types: Counter[tuple[str, ...]] = Counter()
    aggregate_root_classes: Counter[tuple[tuple[str, int | None], ...]] = Counter()
    aggregate_relative: Counter[tuple[str, ...]] = Counter()
    aggregate_closure_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_parent_roots: Counter = Counter()
    all_rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_conflicts.update(dict(data["conflict_kinds"]))
        aggregate_causal.update(dict(data["causal_classes"]))
        aggregate_safety.update(dict(data["parent_safety_pairs"]))
        aggregate_orientation.update(dict(data["parent_orientation_pairs"]))
        aggregate_roles.update(dict(data["parent_role_pairs"]))
        aggregate_shapes.update(dict(data["endpoint_shapes"]))
        aggregate_source_types.update(dict(data["closure_source_type_sets"]))
        aggregate_root_classes.update(dict(data["closure_root_class_sets"]))
        aggregate_relative.update(dict(data["closure_relative_minimum_sets"]))
        aggregate_closure_shapes.update(dict(data["closure_size_shapes"]))
        aggregate_parent_roots.update(dict(data["event_parent_root_pairs"]))
        all_rows.extend(data["rows"])
        print(f"SIZE_ROW = {{'n': {n}, 'counts': {dict(data['counts'])}, "
              f"'conflicts': {dict(data['conflict_kinds'])}, "
              f"'causal': {dict(data['causal_classes'])}, "
              f"'parent_safety': {dict(data['parent_safety_pairs'])}, "
              f"'parent_orientation': {dict(data['parent_orientation_pairs'])}}}")

    assert aggregate_counts["conflict_merged_tail_cases"] == 17
    assert aggregate_counts["nonconflict_merged_tail_cases"] == 1
    assert aggregate_causal == Counter({
        "ANCESTOR_CONFLICT_SOURCE": 13,
        "DIRECT_CONFLICT_SOURCE": 4,
    })

    print("JANUS_GT_MERGED_TAIL_REASON_TEMPLATE_PROFILE = PASS")
    print(f"COUNTS = {dict(aggregate_counts)}")
    print(f"CONFLICT_KINDS = {dict(aggregate_conflicts)}")
    print(f"CAUSAL_CLASSES = {dict(aggregate_causal)}")
    print(f"PARENT_SAFETY_PAIRS = {dict(aggregate_safety)}")
    print(f"PARENT_ORIENTATION_PAIRS = {dict(aggregate_orientation)}")
    print(f"PARENT_ROLE_PAIRS = {dict(aggregate_roles)}")
    print(f"ENDPOINT_SHAPES = {dict(aggregate_shapes)}")
    print(f"CLOSURE_SOURCE_TYPE_SETS = {dict(aggregate_source_types)}")
    print(f"CLOSURE_ROOT_CLASS_SETS = {dict(aggregate_root_classes)}")
    print(f"CLOSURE_RELATIVE_MINIMUM_SETS = {dict(aggregate_relative)}")
    print(f"CLOSURE_SIZE_SHAPES = {dict(aggregate_closure_shapes)}")
    print(f"EVENT_PARENT_ROOT_PAIRS = {dict(aggregate_parent_roots)}")
    for row in all_rows:
        print(f"ROW = {row}")
    print(
        "claim_boundary = finite root-ancestry template profile through GT_8; "
        "no arbitrary-n reason-closure theorem asserted"
    )


if __name__ == "__main__":
    self_test()
