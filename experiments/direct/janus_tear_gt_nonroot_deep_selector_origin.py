#!/usr/bin/env python3
"""Join the three deep exchange rows with exact selector-origin accounting.

This is a finite classifier, not an arbitrary-n selector theorem.  It matches
all GT_8 deep raw/post in-arborescence clauses to the history-sensitive branch
frequency contribution profile and emits the selected-versus-dangerous-tail
competitor gap together with its origin vector.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_branch_frequency_contribution_profile import (
    ORIGIN_ORDER,
    audit as frequency_audit,
)
from janus_tear_gt_nonroot_deep_exchange_absorption import classify as deep_classify


def self_test() -> None:
    deep_rows = tuple(deep_classify(8)["rows"])
    frequency_rows = tuple(frequency_audit(8)["rows"])

    joined = []
    gaps: Counter[int] = Counter()
    vectors: Counter[tuple[int, ...]] = Counter()
    competitors: Counter[int] = Counter()
    source_deltas: Counter[int] = Counter()

    for deep in deep_rows:
        matches = [
            row
            for row in frequency_rows
            if int(row["parent_state"]) == int(deep["state_id"])
            and tuple(row["source"]) == tuple(deep["post_clause"])
            and int(row["selected"]) == int(deep["selected"])
        ]
        assert len(matches) == 1, (deep, matches)
        row = matches[0]
        gap = int(row["gap"])
        vector = tuple(int(value) for value in row["origin_vector"])
        competitor = int(row["competitor"])
        source_delta = int(row["source_delta"])
        gaps[gap] += 1
        vectors[vector] += 1
        competitors[competitor] += 1
        source_deltas[source_delta] += 1
        joined.append({
            "state_id": int(deep["state_id"]),
            "event_index": int(deep["event_index"]),
            "source": tuple(deep["post_clause"]),
            "selected": int(row["selected"]),
            "competitor": competitor,
            "strongest_tail_variables": tuple(row["strongest_tail_variables"]),
            "selected_frequency": int(row["selected_frequency"]),
            "tail_frequency": int(row["tail_frequency"]),
            "gap": gap,
            "source_delta": source_delta,
            "origin_order": ORIGIN_ORDER,
            "origin_vector": vector,
            "selected_only": tuple(row["selected_only"]),
            "tail_only": tuple(row["tail_only"]),
            "both": tuple(row["both"]),
            "selected_component_sizes": tuple(deep["selected_component_sizes"]),
            "selected_literals": tuple(deep["selected_literals"]),
            "child_fates": tuple(
                (bool(child["value"]), str(child["fate"]), child["shape"])
                for child in deep["children"]
            ),
        })

    assert len(joined) == 3
    print("JANUS_GT_NONROOT_DEEP_SELECTOR_ORIGIN = PASS")
    print(f"ROWS = {tuple(joined)}")
    print(f"GAPS = {tuple(sorted(gaps.items()))}")
    print(f"VECTORS = {tuple(sorted(vectors.items(), key=repr))}")
    print(f"COMPETITORS = {tuple(sorted(competitors.items()))}")
    print(f"SOURCE_DELTAS = {tuple(sorted(source_deltas.items()))}")
    print(
        "claim_boundary = exact finite selector-origin join for the three GT_8 "
        "deep exchange rows; arbitrary-n selector dominance remains open"
    )


if __name__ == "__main__":
    self_test()
