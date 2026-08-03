#!/usr/bin/env python3
"""Compact certificate for the Policy-0A branch-frequency mechanism.

Imports the full surviving-lineage frequency profiler but emits only the
aggregate mechanism through GT_8.  No examples are printed.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_surviving_branch_frequency_profile import audit


def self_test() -> None:
    counts: Counter[str] = Counter()
    relations: Counter[str] = Counter()
    tail_gaps: Counter[int] = Counter()
    head_gaps: Counter[int] = Counter()
    max_relation_sets: Counter[tuple[str, ...]] = Counter()
    max_candidate_counts: Counter[int] = Counter()
    selected_ranks: Counter[int] = Counter()
    frequency_shapes: Counter[tuple[int, int, int, int]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        counts.update(dict(data["counts"]))
        relations.update(dict(data["selected_relation_histogram"]))
        tail_gaps.update(dict(data["tail_gap_histogram"]))
        head_gaps.update(dict(data["head_gap_histogram"]))
        max_relation_sets.update(dict(data["max_relation_sets"]))
        max_candidate_counts.update(dict(data["max_candidate_counts"]))
        selected_ranks.update(dict(data["selected_rank_among_max"]))
        frequency_shapes.update(dict(data["frequency_shapes"]))
        rows.append({
            "n": n,
            "lineages": dict(data["counts"]).get("lineages", 0),
            "strict_tail_gap": dict(data["counts"]).get(
                "strict_tail_frequency_gap", 0
            ),
            "tail_ties_maximum": dict(data["counts"]).get(
                "tail_ties_maximum", 0
            ),
            "tail_excluded_by_tie_break": dict(data["counts"]).get(
                "tail_excluded_by_tie_break", 0
            ),
            "selected_relations": dict(data["selected_relation_histogram"]),
            "tail_gaps": dict(data["tail_gap_histogram"]),
        })

    assert counts["lineages"] == 42
    assert counts["selected_complement_in_source"] == 42
    assert counts["strict_tail_frequency_gap"] + counts[
        "tail_excluded_by_tie_break"
    ] == 42
    assert selected_ranks == Counter({1: 42})
    assert relations == Counter({"HEAD_TO_OTHER": 39, "DISJOINT": 3})

    print("JANUS_GT_SURVIVING_BRANCH_FREQUENCY_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(counts)}")
    print(f"SELECTED_RELATIONS = {dict(relations)}")
    print(f"TAIL_GAPS = {dict(sorted(tail_gaps.items()))}")
    print(f"HEAD_GAPS = {dict(sorted(head_gaps.items()))}")
    print(f"MAX_RELATION_SETS = {dict(max_relation_sets)}")
    print(f"MAX_CANDIDATE_COUNTS = {dict(sorted(max_candidate_counts.items()))}")
    print(f"SELECTED_RANKS = {dict(selected_ranks)}")
    print(f"FREQUENCY_SHAPES = {dict(sorted(frequency_shapes.items()))}")
    print(
        "claim_boundary = compact finite frequency certificate through GT_8; "
        "uniform arbitrary-n inequality remains open"
    )


if __name__ == "__main__":
    self_test()
