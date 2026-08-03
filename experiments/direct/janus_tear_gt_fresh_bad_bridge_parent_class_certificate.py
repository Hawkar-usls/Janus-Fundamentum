#!/usr/bin/env python3
"""Certify the finite parent-class reduction for fresh bad-bridge births.

The mixed-parent closure theorem proves that a legal Resolution inference with
one component-spanning parent and one directed-cycle parent cannot create an
unsafe acyclic low-rank clause.  This certificate checks the remaining finite
GT-specific observation: every fresh non-tail bridge occurrence produced in
pre-frontier exact states of GT_4,...,GT_8 has exactly that unordered parent
class pair.

The source census caps examples at 100 per order.  Each tested order has fewer
than 100 fresh occurrences, and this certificate explicitly checks that the
stored examples equal the reported fresh count before using them.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_local_resolution_bad_bridge_birth_v2 import audit
from janus_tear_gt_rank_safety_dichotomy import safety_class

MIXED_PAIR = ("COMPONENT_SPANNING", "DIRECTED_CYCLE")


def classify_fresh_examples(n: int) -> dict[str, object]:
    data = audit(n)
    counts = dict(data["counts"])
    expected_fresh = int(counts.get("fresh_non_tail_births", 0))
    examples = tuple(data["fresh_examples"])
    assert len(examples) == expected_fresh

    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    state_by_id = {int(state["id"]): state for state in policy.states.values()}

    ordered_pairs: Counter[tuple[str, str]] = Counter()
    unordered_pairs: Counter[tuple[str, str]] = Counter()
    occurrence_shapes: Counter[tuple[int, int]] = Counter()
    event_occurrences: Counter[tuple[int, int]] = Counter()
    violations = []

    for example in examples:
        state_id = int(example["state_id"])
        call_id = int(example["call_id"])
        event_index = int(example["event_index"])
        state = state_by_id[state_id]
        event = state["resolution_events"][event_index]
        assignment = context["call_after_pre"][call_id]

        left = tuple(event["left"])
        right = tuple(event["right"])
        left_class = str(
            safety_class(n, left, assignment, pairs)["classification"]
        )
        right_class = str(
            safety_class(n, right, assignment, pairs)["classification"]
        )
        ordered = (left_class, right_class)
        unordered = tuple(sorted(ordered))
        ordered_pairs[ordered] += 1
        unordered_pairs[unordered] += 1
        occurrence_shapes[tuple(example["endpoint_shape"])] += 1
        event_occurrences[(state_id, event_index)] += 1

        if unordered != MIXED_PAIR:
            violations.append({
                "n": n,
                "state_id": state_id,
                "call_id": call_id,
                "event_index": event_index,
                "literal": int(example["literal"]),
                "resolvent": tuple(example["resolvent"]),
                "ordered_parent_classes": ordered,
            })

    return {
        "n": n,
        "fresh_occurrences": expected_fresh,
        "distinct_origin_events": len(event_occurrences),
        "multi_bad_literal_events": sum(
            1 for multiplicity in event_occurrences.values() if multiplicity > 1
        ),
        "ordered_pairs": tuple(sorted(ordered_pairs.items())),
        "unordered_pairs": tuple(sorted(unordered_pairs.items())),
        "endpoint_shapes": tuple(sorted(occurrence_shapes.items())),
        "violations": tuple(violations),
    }


def self_test() -> None:
    aggregate_occurrences = 0
    aggregate_events = 0
    aggregate_multi = 0
    ordered: Counter[tuple[str, str]] = Counter()
    unordered: Counter[tuple[str, str]] = Counter()
    shapes: Counter[tuple[int, int]] = Counter()
    rows = []

    for n in range(4, 9):
        row = classify_fresh_examples(n)
        assert not row["violations"]
        aggregate_occurrences += int(row["fresh_occurrences"])
        aggregate_events += int(row["distinct_origin_events"])
        aggregate_multi += int(row["multi_bad_literal_events"])
        ordered.update(dict(row["ordered_pairs"]))
        unordered.update(dict(row["unordered_pairs"]))
        shapes.update(dict(row["endpoint_shapes"]))
        rows.append(row)
        print(f"ORDER_SIZE = {n}")
        print(f"  fresh_occurrences = {row['fresh_occurrences']}")
        print(f"  distinct_origin_events = {row['distinct_origin_events']}")
        print(f"  multi_bad_literal_events = {row['multi_bad_literal_events']}")
        print(f"  ordered_pairs = {row['ordered_pairs']}")
        print(f"  unordered_pairs = {row['unordered_pairs']}")
        print(f"  endpoint_shapes = {row['endpoint_shapes']}")
        print(f"  violations = {row['violations']}")

    assert aggregate_occurrences == 77
    assert unordered == Counter({MIXED_PAIR: 77})

    print("JANUS_GT_FRESH_BAD_BRIDGE_PARENT_CLASS_CERTIFICATE = PASS")
    print(f"FRESH_OCCURRENCES = {aggregate_occurrences}")
    print(f"DISTINCT_ORIGIN_EVENTS = {aggregate_events}")
    print(f"MULTI_BAD_LITERAL_EVENTS = {aggregate_multi}")
    print(f"ORDERED_PARENT_PAIRS = {tuple(sorted(ordered.items()))}")
    print(f"UNORDERED_PARENT_PAIRS = {tuple(sorted(unordered.items()))}")
    print(f"ENDPOINT_SHAPES = {tuple(sorted(shapes.items()))}")
    print(
        "claim_boundary = finite parent-class certificate through GT_8; "
        "arbitrary-n GT parent-class reduction remains open"
    )


if __name__ == "__main__":
    self_test()
