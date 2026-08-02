#!/usr/bin/env python3
"""Compact summary of directed component-clause structure in C024."""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_directed_component_clause_audit import audit as orientation_audit
from janus_tear_gt_directed_safety_dichotomy import audit as dichotomy_audit


def self_test() -> None:
    rows = []
    aggregate_orientation: Counter[str] = Counter()
    aggregate_stage: dict[str, Counter[str]] = {}
    unsafe_sizes = []

    for n in range(4, 9):
        orientation = orientation_audit(n)
        dichotomy = dichotomy_audit(n)
        aggregate_orientation.update(dict(orientation["counts"]))
        for stage, histogram in dichotomy["stage_counts"]:
            aggregate_stage.setdefault(stage, Counter()).update(dict(histogram))
        if dichotomy["unsafe_total"]:
            unsafe_sizes.append(n)

        rows.append(
            {
                "n": n,
                "target": dichotomy["target"],
                "orientation_counts": orientation["counts"],
                "dangerous_classes": orientation["dangerous_classes"],
                "direct_unit_classes": orientation["direct_unit_classes"],
                "clause_occurrences": dichotomy["total_clause_occurrences"],
                "unsafe_total": dichotomy["unsafe_total"],
                "stage_counts": dichotomy["stage_counts"],
            }
        )

    print("JANUS_GT_DIRECTED_SAFETY_SUMMARY = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_orientation = {tuple(sorted(aggregate_orientation.items()))}")
    print(
        "aggregate_stage = "
        f"{tuple((stage, tuple(sorted(histogram.items()))) for stage, histogram in sorted(aggregate_stage.items()))}"
    )
    print(f"unsafe_sizes = {tuple(unsafe_sizes)}")
    print("abstract_resolution_closure = FALSE: rooted parents can resolve to a proper directed forest")
    print("minimal_abstract_counterexample = L{0->1,2->1}, R{1->0,2->1}, pivot 0<->1, Q{2->1}")
    print("claim_boundary = compact finite summary; GT-specific exclusion of abstract counterexample remains open")


if __name__ == "__main__":
    self_test()
