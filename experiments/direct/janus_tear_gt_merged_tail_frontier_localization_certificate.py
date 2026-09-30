#!/usr/bin/env python3
"""Red/green certificate for merged-tail frontier localization.

The certificate asserts the exact structural consequence suggested by the
binary origin geometry: every fresh merged-tail non-tail birth through GT_8
occurs with two quotient components at novelty level n-2.  If true, these
births arise only after the historical restriction frontier has already been
reached and cannot replace an earlier required component join.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_merged_tail_frontier_localization import audit


def self_test() -> None:
    counts: Counter[str] = Counter()
    novelty_gaps: Counter[int] = Counter()
    components: Counter[int] = Counter()
    widths: Counter[tuple[int, int, int]] = Counter()
    safety: Counter[tuple[str, str]] = Counter()
    orientation: Counter[tuple[str, str]] = Counter()
    fates: Counter[str] = Counter()
    bad_parent_counts: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        counts.update(dict(data["counts"]))
        novelty_gaps.update(dict(data["novelty_gaps"]))
        components.update(dict(data["component_counts"]))
        widths.update(dict(data["width_shapes"]))
        safety.update(dict(data["safety_shapes"]))
        orientation.update(dict(data["orientation_shapes"]))
        fates.update(dict(data["fate_shapes"]))
        bad_parent_counts.update(dict(data["bad_parent_counts"]))
        rows.append({
            "n": n,
            "target": data["target"],
            "occurrences": dict(data["counts"])[
                "fresh_merged_tail_occurrences"
            ],
            "novelty_gaps": dict(data["novelty_gaps"]),
            "component_counts": dict(data["component_counts"]),
            "width_shapes": dict(data["width_shapes"]),
            "fates": dict(data["fate_shapes"]),
        })

    assert counts["fresh_merged_tail_occurrences"] == 18
    assert counts["born_at_target_frontier"] == 18
    assert counts.get("born_before_target_frontier", 0) == 0
    assert counts.get("born_after_target_frontier", 0) == 0
    assert novelty_gaps == Counter({0: 18})
    assert components == Counter({2: 18})
    assert counts["two_component_births"] == 18

    print("JANUS_GT_MERGED_TAIL_FRONTIER_LOCALIZATION_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(counts)}")
    print(f"NOVELTY_GAPS = {dict(novelty_gaps)}")
    print(f"COMPONENT_COUNTS = {dict(components)}")
    print(f"WIDTH_SHAPES = {dict(widths)}")
    print(f"PARENT_SAFETY = {dict(safety)}")
    print(f"PARENT_ORIENTATION = {dict(orientation)}")
    print(f"FATES = {dict(fates)}")
    print(f"BAD_PARENT_COUNTS = {dict(bad_parent_counts)}")
    print(
        "claim_boundary = exhaustive finite frontier-localization certificate "
        "through GT_8; arbitrary-n localization and global frontier counting "
        "remain open"
    )


if __name__ == "__main__":
    self_test()
