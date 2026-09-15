#!/usr/bin/env python3
"""Cross-classify finite merged-tail conflict reason templates.

The first version incorrectly inferred a pointwise correlation from equal
aggregate counts: there are 13 ancestor conflict sources and 13 closures
containing the bad tail's root non-minimality clause, but these are not the same
13 occurrences.  This corrected checker retains only the universal parent
geometry and emits honest cross-tables for causal class, root ancestry,
conflict type, origin width, and parent width.

It also tests whether the origin resolvents are units.  No direct/ancestor root
correlation is asserted unless it follows from the reported cross-table.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_merged_tail_reason_template_profile import audit


def root_feature(relative, root_classes) -> str:
    has_nonminimality = any(
        kind == "ROOT_NON_MINIMALITY" for kind, _vertex in root_classes
    )
    has_transitivity = ("ROOT_TRANSITIVITY", None) in root_classes
    if relative == ("TAIL",) and has_nonminimality and has_transitivity:
        return "TAIL_NONMINIMALITY_PLUS_TRANSITIVITY"
    if relative == () and not has_nonminimality and has_transitivity:
        return "TRANSITIVITY_WITHOUT_NONMINIMALITY"
    if relative == () and not has_nonminimality and not has_transitivity:
        return "DERIVED_ONLY"
    return "OTHER_ROOT_PATTERN"


def self_test() -> None:
    counts: Counter[str] = Counter()
    causal_conflict: Counter[tuple[str, str]] = Counter()
    causal_root_feature: Counter[tuple[str, str]] = Counter()
    causal_relative: Counter[tuple[str, tuple[str, ...]]] = Counter()
    causal_event_width: Counter[tuple[str, int]] = Counter()
    causal_parent_widths: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_endpoint_shapes: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_closure_shapes: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_source_types: Counter[tuple[str, tuple[str, ...]]] = Counter()
    causal_root_classes: Counter = Counter()
    pivot_in_bad_parent_count: Counter[tuple[str, int]] = Counter()
    parent_safety_unordered: Counter[tuple[str, str]] = Counter()
    parent_orientation_unordered: Counter[tuple[str, str]] = Counter()
    event_widths: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        for row in data["rows"]:
            causal = str(row["causal_class"])
            counts[causal] += 1
            conflict = str(row["conflict_kind"])
            causal_conflict[(causal, conflict)] += 1

            safety = tuple(row["parent_safety"])
            orientation = tuple(row["parent_orientation"])
            roles = tuple(row["parent_roles"])
            safety_unordered = tuple(sorted(safety))
            orientation_unordered = tuple(sorted(orientation))
            assert safety_unordered == (
                "COMPONENT_SPANNING",
                "DIRECTED_CYCLE",
            )
            assert orientation_unordered == (
                "HAS_DIRECTED_CYCLE",
                "UNDIRECTED_CYCLE_ONLY",
            )
            assert roles == (
                "NONBRIDGE_OR_NONSPANNING",
                "NONBRIDGE_OR_NONSPANNING",
            )
            parent_safety_unordered[safety_unordered] += 1
            parent_orientation_unordered[orientation_unordered] += 1

            relative = tuple(row["closure_relative_minimum"])
            root_classes = tuple(row["closure_root_classes"])
            feature = root_feature(relative, root_classes)
            causal_root_feature[(causal, feature)] += 1
            causal_relative[(causal, relative)] += 1

            resolvent = tuple(row["resolvent"])
            left = tuple(row["left"])
            right = tuple(row["right"])
            event_width = len(resolvent)
            parent_widths = tuple(sorted((len(left), len(right))))
            event_widths[event_width] += 1
            causal_event_width[(causal, event_width)] += 1
            causal_parent_widths[(causal, parent_widths)] += 1
            causal_endpoint_shapes[(causal, tuple(row["endpoint_shape"]))] += 1
            causal_closure_shapes[(
                causal,
                (
                    int(row["closure_source_count"]),
                    int(row["closure_event_count"]),
                ),
            )] += 1
            causal_source_types[(
                causal,
                tuple(row["closure_source_types"]),
            )] += 1
            causal_root_classes[(causal, root_classes)] += 1

            pivot = int(row["pivot"])
            bad_literal = int(row["bad_literal"])
            assert abs(bad_literal) != pivot
            parents_containing_bad = sum(
                1 for parent in (left, right) if bad_literal in parent
            )
            assert parents_containing_bad >= 1
            pivot_in_bad_parent_count[(causal, parents_containing_bad)] += 1

            rows.append({
                "n": n,
                "causal": causal,
                "conflict": conflict,
                "root_feature": feature,
                "relative_minimum": relative,
                "event_width": event_width,
                "parent_widths": parent_widths,
                "endpoint_shape": tuple(row["endpoint_shape"]),
                "closure_shape": (
                    int(row["closure_source_count"]),
                    int(row["closure_event_count"]),
                ),
                "source_types": tuple(row["closure_source_types"]),
                "root_classes": root_classes,
                "parents_containing_bad": parents_containing_bad,
            })

    assert counts == Counter({
        "ANCESTOR_CONFLICT_SOURCE": 13,
        "DIRECT_CONFLICT_SOURCE": 4,
    })
    assert parent_safety_unordered == Counter({
        ("COMPONENT_SPANNING", "DIRECTED_CYCLE"): 17,
    })
    assert parent_orientation_unordered == Counter({
        ("HAS_DIRECTED_CYCLE", "UNDIRECTED_CYCLE_ONLY"): 17,
    })
    assert sum(event_widths.values()) == 17

    print("JANUS_GT_MERGED_TAIL_REASON_CROSS_TABLE = PASS")
    print(f"COUNTS = {dict(counts)}")
    print(f"PARENT_SAFETY_UNORDERED = {dict(parent_safety_unordered)}")
    print(f"PARENT_ORIENTATION_UNORDERED = {dict(parent_orientation_unordered)}")
    print(f"CAUSAL_CONFLICT = {dict(causal_conflict)}")
    print(f"CAUSAL_ROOT_FEATURE = {dict(causal_root_feature)}")
    print(f"CAUSAL_RELATIVE_MINIMUM = {dict(causal_relative)}")
    print(f"EVENT_WIDTHS = {dict(sorted(event_widths.items()))}")
    print(f"CAUSAL_EVENT_WIDTH = {dict(causal_event_width)}")
    print(f"CAUSAL_PARENT_WIDTHS = {dict(causal_parent_widths)}")
    print(f"CAUSAL_ENDPOINT_SHAPES = {dict(causal_endpoint_shapes)}")
    print(f"CAUSAL_CLOSURE_SHAPES = {dict(causal_closure_shapes)}")
    print(f"CAUSAL_SOURCE_TYPES = {dict(causal_source_types)}")
    print(f"CAUSAL_ROOT_CLASSES = {dict(causal_root_classes)}")
    print(f"PARENTS_CONTAINING_BAD = {dict(pivot_in_bad_parent_count)}")
    for row in rows:
        print(f"ROW = {row}")
    print(
        "claim_boundary = corrected finite cross-table through GT_8; "
        "no pointwise causal/root correlation or arbitrary-n theorem asserted"
    )


if __name__ == "__main__":
    self_test()
