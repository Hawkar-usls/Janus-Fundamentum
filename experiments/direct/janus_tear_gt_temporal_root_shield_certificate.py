#!/usr/bin/env python3
"""Compact finite certificate for the C024 temporal root-shield handoff.

This checker combines four independently instrumented layers through GT_8:

1. raw local non-tail Resolution output;
2. survival into later exact cache keys;
3. geometry of the unique intervening branch;
4. canonical untouched root non-minimality shields.

It certifies the finite temporal statement only.  The arbitrary-n survivor
induction and global Formula-Caching lower-bound transfer remain open.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_resolvent_survival_filter import audit as survival_audit
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit as raw_audit
from janus_tear_gt_root_nonminimality_bridge_shield import audit as root_audit
from janus_tear_gt_surviving_bad_branch_geometry import audit as branch_audit


def self_test() -> None:
    raw_counts: Counter[str] = Counter()
    raw_shapes: Counter[tuple[int, int]] = Counter()
    survival_counts: Counter[str] = Counter()
    event_shapes: Counter[tuple[int, int]] = Counter()
    child_shapes: Counter[tuple[int, int]] = Counter()
    transitions: Counter[tuple[str, ...]] = Counter()
    novelty: Counter[int] = Counter()
    pre_units: Counter[int] = Counter()
    branch_counts: Counter[str] = Counter()
    branch_relations: Counter[str] = Counter()
    root_counts: Counter[str] = Counter()
    root_head_sizes: Counter[int] = Counter()
    root_parallel: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        raw = raw_audit(n)
        survival = survival_audit(n)
        branch = branch_audit(n)
        root = root_audit(n)

        raw_counts.update(dict(raw["counts"]))
        raw_shapes.update(dict(raw["endpoint_shapes"]))
        survival_counts.update(dict(survival["counts"]))
        event_shapes.update(dict(survival["event_shapes"]))
        child_shapes.update(dict(survival["child_shapes"]))
        transitions.update(dict(survival["transition_histogram"]))
        novelty.update(dict(survival["novelty_histogram"]))
        pre_units.update(dict(survival["pre_unit_histogram"]))
        branch_counts.update(dict(branch["counts"]))
        branch_relations.update(dict(branch["relation_histogram"]))
        root_counts.update(dict(root["counts"]))
        root_head_sizes.update(dict(root["head_component_sizes"]))
        root_parallel.update(dict(root["parallel_multiplicity"]))

        rows.append({
            "n": n,
            "raw_non_tail": dict(raw["counts"]).get(
                "non_tail_resolvent_literals", 0
            ),
            "exact_key_bad": dict(survival["counts"])[
                "exact_key_bad_occurrences"
            ],
            "immediate_local": dict(survival["counts"]).get(
                "immediate_local_occurrences", 0
            ),
            "inherited": dict(survival["counts"]).get(
                "inherited_only_occurrences", 0
            ),
            "branch_avoids_tail": dict(branch["counts"]).get(
                "branch_avoids_tail", 0
            ),
            "canonical_root_shields": dict(root["counts"])[
                "canonical_root_shields"
            ],
        })

    assert raw_counts == Counter({
        "non_tail_resolvent_literals": 93,
        "fresh_non_tail_births": 77,
        "singleton_tail_merged_head_shape": 56,
        "fresh_birth_with_pivot_path": 24,
        "singleton_singleton_shape": 19,
        "merged_tail_shape": 18,
        "preexisting_non_tail": 16,
    })
    assert raw_shapes == Counter({
        (1, 3): 23,
        (1, 1): 19,
        (1, 2): 17,
        (1, 4): 9,
        (1, 5): 7,
        (2, 3): 6,
        (2, 4): 4,
        (3, 5): 3,
        (3, 2): 2,
        (3, 4): 2,
        (2, 1): 1,
    })

    assert survival_counts == Counter({
        "exact_key_bad_occurrences": 62,
        "immediate_local_occurrences": 42,
        "inherited_only_occurrences": 20,
    })
    assert event_shapes == Counter({
        (1, 3): 14,
        (1, 1): 12,
        (1, 2): 11,
        (1, 4): 5,
    })
    assert all(tail == 1 for tail, _ in event_shapes)
    assert child_shapes == Counter({
        (1, 3): 21,
        (1, 4): 17,
        (1, 2): 12,
        (1, 5): 12,
    })
    assert transitions == Counter({
        (
            "TAIL_STABLE", "HEAD_STABLE", "THEN",
            "TAIL_STABLE", "HEAD_GREW",
        ): 39,
        (
            "TAIL_STABLE", "HEAD_STABLE", "THEN",
            "TAIL_STABLE", "HEAD_STABLE",
        ): 3,
    })
    assert novelty == Counter({1: 42})
    assert pre_units == Counter({0: 42})

    assert branch_counts == Counter({
        "surviving_local_lineages": 42,
        "novel_branches": 42,
        "zero_child_pre_units": 42,
        "branch_avoids_tail": 42,
        "one_literal_branch_restrictions": 42,
        "head_growth_branches": 39,
        "head_stable_disjoint_branches": 3,
    })
    assert branch_relations == Counter({
        "HEAD_TO_OTHER": 39,
        "DISJOINT": 3,
    })

    assert root_counts == Counter({
        "non_tail_bridge_occurrences": 62,
        "canonical_root_shields": 62,
    })
    assert root_head_sizes == Counter({2: 12, 3: 21, 4: 17, 5: 12})
    assert root_parallel == Counter({1: 12, 2: 21, 3: 17, 4: 12})

    # Exact-key endpoint shapes and root-shield head sizes are the same census.
    assert Counter({head: count for (_, head), count in child_shapes.items()}) == root_head_sizes
    # No non-singleton-tail local occurrence appears in the surviving event set.
    assert sum(
        count for (tail, _), count in raw_shapes.items() if tail > 1
    ) == 18
    assert all(tail == 1 for tail, _ in event_shapes)

    print("JANUS_GT_TEMPORAL_ROOT_SHIELD_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"RAW_COUNTS = {dict(raw_counts)}")
    print(f"RAW_ENDPOINT_SHAPES = {dict(sorted(raw_shapes.items()))}")
    print(f"SURVIVAL_COUNTS = {dict(survival_counts)}")
    print(f"SURVIVING_EVENT_SHAPES = {dict(sorted(event_shapes.items()))}")
    print(f"EXACT_KEY_SHAPES = {dict(sorted(child_shapes.items()))}")
    print(f"BRANCH_RELATIONS = {dict(branch_relations)}")
    print(f"ROOT_HEAD_SIZES = {dict(sorted(root_head_sizes.items()))}")
    print(f"ROOT_PARALLEL_MULTIPLICITY = {dict(sorted(root_parallel.items()))}")
    print(
        "claim_boundary = exhaustive temporal certificate through GT_8; "
        "arbitrary-n temporal survivor induction remains open"
    )


if __name__ == "__main__":
    self_test()
