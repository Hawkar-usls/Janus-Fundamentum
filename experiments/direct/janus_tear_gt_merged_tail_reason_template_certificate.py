#!/usr/bin/env python3
"""Compact aggregate certificate for merged-tail conflict reason templates."""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_merged_tail_reason_template_profile import audit


def self_test() -> None:
    counts: Counter[str] = Counter()
    conflicts: Counter[str] = Counter()
    causal: Counter[str] = Counter()
    safety: Counter[tuple[str, str]] = Counter()
    orientation: Counter[tuple[str, str]] = Counter()
    roles: Counter[tuple[str, ...]] = Counter()
    shapes: Counter[tuple[int, int]] = Counter()
    source_types: Counter[tuple[str, ...]] = Counter()
    root_classes: Counter = Counter()
    relative: Counter[tuple[str, ...]] = Counter()
    closure_shapes: Counter[tuple[int, int]] = Counter()
    parent_roots: Counter = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        counts.update(dict(data["counts"]))
        conflicts.update(dict(data["conflict_kinds"]))
        causal.update(dict(data["causal_classes"]))
        safety.update(dict(data["parent_safety_pairs"]))
        orientation.update(dict(data["parent_orientation_pairs"]))
        roles.update(dict(data["parent_role_pairs"]))
        shapes.update(dict(data["endpoint_shapes"]))
        source_types.update(dict(data["closure_source_type_sets"]))
        root_classes.update(dict(data["closure_root_class_sets"]))
        relative.update(dict(data["closure_relative_minimum_sets"]))
        closure_shapes.update(dict(data["closure_size_shapes"]))
        parent_roots.update(dict(data["event_parent_root_pairs"]))
        rows.append({
            "n": n,
            "conflict_cases": dict(data["counts"]).get("conflict_merged_tail_cases", 0),
            "nonconflict_cases": dict(data["counts"]).get("nonconflict_merged_tail_cases", 0),
            "conflict_kinds": dict(data["conflict_kinds"]),
            "causal_classes": dict(data["causal_classes"]),
            "parent_safety": dict(data["parent_safety_pairs"]),
            "parent_orientation": dict(data["parent_orientation_pairs"]),
        })

    assert counts == Counter({
        "conflict_merged_tail_cases": 17,
        "nonconflict_merged_tail_cases": 1,
    })
    assert causal == Counter({
        "ANCESTOR_CONFLICT_SOURCE": 13,
        "DIRECT_CONFLICT_SOURCE": 4,
    })

    print("JANUS_GT_MERGED_TAIL_REASON_TEMPLATE_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(counts)}")
    print(f"CONFLICT_KINDS = {dict(conflicts)}")
    print(f"CAUSAL_CLASSES = {dict(causal)}")
    print(f"PARENT_SAFETY_PAIRS = {dict(safety)}")
    print(f"PARENT_ORIENTATION_PAIRS = {dict(orientation)}")
    print(f"PARENT_ROLE_PAIRS = {dict(roles)}")
    print(f"ENDPOINT_SHAPES = {dict(shapes)}")
    print(f"CLOSURE_SOURCE_TYPE_SETS = {dict(source_types)}")
    print(f"CLOSURE_ROOT_CLASS_SETS = {dict(root_classes)}")
    print(f"CLOSURE_RELATIVE_MINIMUM_SETS = {dict(relative)}")
    print(f"CLOSURE_SIZE_SHAPES = {dict(closure_shapes)}")
    print(f"EVENT_PARENT_ROOT_PAIRS = {dict(parent_roots)}")
    print(
        "claim_boundary = compact finite ancestry certificate through GT_8; "
        "arbitrary-n reason-template theorem remains open"
    )


if __name__ == "__main__":
    self_test()
