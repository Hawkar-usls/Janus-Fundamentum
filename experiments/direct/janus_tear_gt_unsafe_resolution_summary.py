#!/usr/bin/env python3
"""Compact C024 summary for unsafe low-rank Resolution clauses.

This wrapper reports only the decisive counts from four exact audits:

1. clause occurrences already present in Policy-0A state layers;
2. legal parent pairs actually reached before the one-pass stop;
3. all legal pairs in the frozen parent lists, including pairs after stop;
4. one-generation lifecycle of every newly emitted unsafe clause.

It does not introduce a new solver or new classification rule.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_attempted_resolution_safety import audit as reached_audit
from janus_tear_gt_frozen_parent_unsafe_pair_search import audit as frozen_audit
from janus_tear_gt_rank_safety_dichotomy import audit as layer_audit
from janus_tear_gt_unsafe_clause_one_generation import audit as lifecycle_audit


def pick(counts, names):
    table = dict(counts)
    return {name: int(table.get(name, 0)) for name in names}


def self_test() -> None:
    rows = []
    aggregate_layer: Counter[str] = Counter()
    aggregate_reached: Counter[str] = Counter()
    aggregate_frozen: Counter[str] = Counter()
    aggregate_lifecycle: Counter[str] = Counter()
    aggregate_outcomes: Counter[str] = Counter()

    for n in range(4, 9):
        layer = layer_audit(n)
        reached = reached_audit(n)
        frozen = frozen_audit(n)
        lifecycle = lifecycle_audit(n)

        layer_unsafe_by_stage = {
            stage: int(count)
            for stage, count in layer["unsafe_by_stage"]
        }
        layer_selected = {
            "unsafe_total": int(layer["unsafe_total"]),
            "unsafe_new_resolvents": int(layer["unsafe_new_resolvents"]),
            **{f"unsafe_{stage.lower()}": count for stage, count in layer_unsafe_by_stage.items()},
        }
        reached_selected = pick(
            reached["counts"],
            (
                "attempted_pairs",
                "legal_nonempty_resolvents",
                "new_legal_resolvents",
                "duplicate_legal_resolvents",
                "unsafe_legal_resolvents",
                "unsafe_new_resolvents",
                "unsafe_duplicate_resolvents",
                "replayed_states",
                "replayed_events",
            ),
        )
        frozen_selected = pick(
            frozen["counts"],
            (
                "all_frozen_pairs",
                "legal_nonempty_pairs",
                "unsafe_pairs",
                "unsafe_reached",
                "unsafe_after_stop",
                "states",
            ),
        )
        lifecycle_selected = pick(
            lifecycle["counts"],
            (
                "unsafe_births",
                "killed_by_post_units",
                "born_in_terminal_state",
                "direct_conflict_child",
                "satisfied_by_branch",
                "satisfied_by_child_units",
                "child_terminal_before_key",
                "absent_from_child_key",
                "inherited_into_child_key",
                "inherited_became_safe",
                "inherited_still_unsafe",
            ),
        )
        outcomes = {
            str(name): int(count)
            for name, count in lifecycle["child_outcome_histogram"]
        }

        aggregate_layer.update(layer_selected)
        aggregate_reached.update(reached_selected)
        aggregate_frozen.update(frozen_selected)
        aggregate_lifecycle.update(lifecycle_selected)
        aggregate_outcomes.update(outcomes)

        row = {
            "n": n,
            "target": int(layer["target"]),
            "layer": layer_selected,
            "reached_pairs": reached_selected,
            "frozen_pairs": frozen_selected,
            "frozen_state_counts": {
                str(name): int(count)
                for name, count in frozen["state_counts"]
            },
            "earliest_after_stop_gap": frozen["earliest_after_stop_gap"],
            "maximum_after_stop_gap": int(frozen["maximum_after_stop_gap"]),
            "lifecycle": lifecycle_selected,
            "lifecycle_outcomes": outcomes,
            "inherited_classes": {
                str(name): int(count)
                for name, count in lifecycle["inherited_class_histogram"]
            },
        }
        rows.append(row)
        print(f"UNSAFE_RESOLUTION_ROW = {row}")

    print("JANUS_GT_UNSAFE_RESOLUTION_SUMMARY = PASS")
    print(f"aggregate_layer = {dict(sorted(aggregate_layer.items()))}")
    print(f"aggregate_reached_pairs = {dict(sorted(aggregate_reached.items()))}")
    print(f"aggregate_frozen_pairs = {dict(sorted(aggregate_frozen.items()))}")
    print(f"aggregate_lifecycle = {dict(sorted(aggregate_lifecycle.items()))}")
    print(f"aggregate_lifecycle_outcomes = {dict(sorted(aggregate_outcomes.items()))}")
    print("claim_boundary = compact finite summary; temporal amortized lower-bound theorem remains open")


if __name__ == "__main__":
    self_test()
