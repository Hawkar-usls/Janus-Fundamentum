#!/usr/bin/env python3
"""Certify the two finite merged-tail conflict reason schemes.

The ancestry profile suggests an exact bifurcation through GT_8:

- every origin inference resolves one component-spanning/undirected-cycle-only
  parent with one directed-cycle parent;
- ancestor conflict cases contain the bad tail's root non-minimality clause and
  root transitivity in the all-source reason closure;
- direct conflict cases require no root non-minimality clause.

This checker also measures origin resolvent widths and parent widths to test
whether the extinction theorem can be reduced to a unit-resolvent lemma.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_merged_tail_reason_template_profile import audit


def self_test() -> None:
    counts: Counter[str] = Counter()
    causal_conflict: Counter[tuple[str, str]] = Counter()
    causal_event_width: Counter[tuple[str, int]] = Counter()
    causal_parent_widths: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_endpoint_shapes: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_closure_shapes: Counter[tuple[str, tuple[int, int]]] = Counter()
    causal_source_types: Counter[tuple[str, tuple[str, ...]]] = Counter()
    causal_root_classes: Counter = Counter()
    pivot_in_bad_parent_count: Counter[tuple[str, int]] = Counter()
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
            assert sorted(safety) == ["COMPONENT_SPANNING", "DIRECTED_CYCLE"]
            assert sorted(orientation) == ["HAS_DIRECTED_CYCLE", "UNDIRECTED_CYCLE_ONLY"]
            assert roles == (
                "NONBRIDGE_OR_NONSPANNING",
                "NONBRIDGE_OR_NONSPANNING",
            )

            relative = tuple(row["closure_relative_minimum"])
            root_classes = tuple(row["closure_root_classes"])
            if causal == "ANCESTOR_CONFLICT_SOURCE":
                assert relative == ("TAIL",)
                assert ("ROOT_TRANSITIVITY", None) in root_classes
                assert any(
                    kind == "ROOT_NON_MINIMALITY"
                    for kind, _vertex in root_classes
                )
                counts["ancestor_with_tail_nonminimality"] += 1
                counts["ancestor_with_root_transitivity"] += 1
            elif causal == "DIRECT_CONFLICT_SOURCE":
                assert relative == ()
                assert not any(
                    kind == "ROOT_NON_MINIMALITY"
                    for kind, _vertex in root_classes
                )
                counts["direct_without_nonminimality"] += 1
            else:
                raise AssertionError(causal)

            resolvent = tuple(row["resolvent"])
            left = tuple(row["left"])
            right = tuple(row["right"])
            event_width = len(resolvent)
            parent_widths = tuple(sorted((len(left), len(right))))
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
            pivot_in_bad_parent_count[(causal, parents_containing_bad)] += 1

            rows.append({
                "n": n,
                "causal": causal,
                "conflict": conflict,
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

    assert counts["ANCESTOR_CONFLICT_SOURCE"] == 13
    assert counts["DIRECT_CONFLICT_SOURCE"] == 4
    assert counts["ancestor_with_tail_nonminimality"] == 13
    assert counts["ancestor_with_root_transitivity"] == 13
    assert counts["direct_without_nonminimality"] == 4

    print("JANUS_GT_MERGED_TAIL_REASON_BIFURCATION = PASS")
    print(f"COUNTS = {dict(counts)}")
    print(f"CAUSAL_CONFLICT = {dict(causal_conflict)}")
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
        "claim_boundary = exact finite two-scheme certificate through GT_8; "
        "arbitrary-n unit-conflict induction remains open"
    )


if __name__ == "__main__":
    self_test()
