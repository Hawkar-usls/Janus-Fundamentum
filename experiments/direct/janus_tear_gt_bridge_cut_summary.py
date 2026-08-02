#!/usr/bin/env python3
"""Compact summary of C024 double-bridge and same-cut audits."""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_double_bridge_pivot_audit import audit as bridge_audit
from janus_tear_gt_same_cut_pivot_audit import audit as cut_audit


def pick(counts, names):
    table = dict(counts)
    return {name: int(table.get(name, 0)) for name in names}


def self_test() -> None:
    rows = []
    aggregate_bridge: Counter[str] = Counter()
    aggregate_cut: Counter[str] = Counter()
    aggregate_same_classes: Counter[str] = Counter()

    for n in range(4, 9):
        bridge = bridge_audit(n)
        cut = cut_audit(n)
        bridge_selected = pick(
            bridge["counts"],
            (
                "frozen_pairs",
                "nonempty_nontautological_pairs",
                "left_bridge_pairs",
                "right_bridge_pairs",
                "double_bridge_pairs",
                "unsafe_without_width_filter",
                "unsafe_within_width_filter",
                "unsafe_excluded_by_width",
            ),
        )
        cut_selected = pick(
            cut["counts"],
            (
                "frozen_pairs",
                "legal_nonempty_pairs",
                "spanning_parent_pairs",
                "not_double_bridge",
                "double_bridge_pairs",
                "same_cut_double_bridge",
                "different_cut_double_bridge",
                "same_cut_with_directed_cycle",
                "same_cut_without_directed_cycle",
                "unsafe_same_cut",
            ),
        )
        same_classes = {
            str(name): int(count)
            for name, count in cut["same_cut_result_classes"]
        }
        aggregate_bridge.update(bridge_selected)
        aggregate_cut.update(cut_selected)
        aggregate_same_classes.update(same_classes)
        row = {
            "n": n,
            "target": int(cut["target"]),
            "bridge": bridge_selected,
            "cut": cut_selected,
            "same_cut_result_classes": same_classes,
            "same_cut_rank_shapes": tuple(cut["same_cut_rank_shapes"]),
        }
        rows.append(row)
        print(f"BRIDGE_CUT_ROW = {row}")

    print("JANUS_GT_BRIDGE_CUT_SUMMARY = PASS")
    print(f"aggregate_bridge = {dict(sorted(aggregate_bridge.items()))}")
    print(f"aggregate_cut = {dict(sorted(aggregate_cut.items()))}")
    print(
        "aggregate_same_cut_result_classes = "
        f"{dict(sorted(aggregate_same_classes.items()))}"
    )
    print("claim_boundary = compact finite summary; same-cut directed-cycle exclusion for all n remains open")


if __name__ == "__main__":
    self_test()
