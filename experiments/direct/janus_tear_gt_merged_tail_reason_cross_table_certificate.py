#!/usr/bin/env python3
"""Compact corrected cross-table for merged-tail conflict reasons.

This deliberately avoids the false pointwise identification of the 13 ancestor
sources with the 13 closures containing the tail non-minimality axiom.  It
recomputes the full finite profile and reports honest aggregate cross-tables.
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
    event_widths: Counter[int] = Counter()
    causal_event_width: Counter[tuple[str, int]] = Counter()
    causal_parent_widths: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_endpoint_shapes: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_closure_shapes: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_source_types: Counter[tuple[str, tuple[str, ...]]] = Counter()
    causal_root_classes: Counter = Counter()
    parents_containing_bad: Counter[tuple[str, int]] = Counter()
    parent_safety: Counter[tuple[str, str]] = Counter()
    parent_orientation: Counter[tuple[str, str]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        size_counts: Counter[str] = Counter()
        size_widths: Counter[int] = Counter()
        for row in data["rows"]:
            causal = str(row["causal_class"])
            conflict = str(row["conflict_kind"])
            counts[causal] += 1
            size_counts[causal] += 1
            causal_conflict[(causal, conflict)] += 1

            safety = tuple(sorted(tuple(row["parent_safety"])))
            orientation = tuple(sorted(tuple(row["parent_orientation"])))
            roles = tuple(row["parent_roles"])
            assert safety == ("COMPONENT_SPANNING", "DIRECTED_CYCLE")
            assert orientation == (
                "HAS_DIRECTED_CYCLE",
                "UNDIRECTED_CYCLE_ONLY",
            )
            assert roles == (
                "NONBRIDGE_OR_NONSPANNING",
                "NONBRIDGE_OR_NONSPANNING",
            )
            parent_safety[safety] += 1
            parent_orientation[orientation] += 1

            relative = tuple(row["closure_relative_minimum"])
            root_classes = tuple(row["closure_root_classes"])
            feature = root_feature(relative, root_classes)
            causal_root_feature[(causal, feature)] += 1
            causal_relative[(causal, relative)] += 1

            resolvent = tuple(row["resolvent"])
            left = tuple(row["left"])
            right = tuple(row["right"])
            width = len(resolvent)
            parent_width_pair = tuple(sorted((len(left), len(right))))
            event_widths[width] += 1
            size_widths[width] += 1
            causal_event_width[(causal, width)] += 1
            causal_parent_widths[(causal, parent_width_pair)] += 1
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
            parent_count = sum(
                1 for parent in (left, right) if bad_literal in parent
            )
            assert parent_count >= 1
            parents_containing_bad[(causal, parent_count)] += 1

        rows.append({
            "n": n,
            "causal_counts": dict(size_counts),
            "event_widths": dict(sorted(size_widths.items())),
        })

    assert counts == Counter({
        "ANCESTOR_CONFLICT_SOURCE": 13,
        "DIRECT_CONFLICT_SOURCE": 4,
    })
    assert parent_safety == Counter({
        ("COMPONENT_SPANNING", "DIRECTED_CYCLE"): 17,
    })
    assert parent_orientation == Counter({
        ("HAS_DIRECTED_CYCLE", "UNDIRECTED_CYCLE_ONLY"): 17,
    })
    assert sum(event_widths.values()) == 17

    print("JANUS_GT_MERGED_TAIL_REASON_CROSS_TABLE_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(counts)}")
    print(f"PARENT_SAFETY = {dict(parent_safety)}")
    print(f"PARENT_ORIENTATION = {dict(parent_orientation)}")
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
    print(f"PARENTS_CONTAINING_BAD = {dict(parents_containing_bad)}")
    print(
        "claim_boundary = corrected finite aggregate cross-table through GT_8; "
        "no pointwise causal/root correlation or arbitrary-n theorem asserted"
    )


if __name__ == "__main__":
    self_test()
