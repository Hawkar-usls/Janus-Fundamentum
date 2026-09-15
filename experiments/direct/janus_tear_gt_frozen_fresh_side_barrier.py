#!/usr/bin/env python3
"""Bridge the abstract frozen fresh-side lemma to exact Policy-0A traces.

The abstract lemma is set-theoretic: if an entry key K has no same-cut pair,
then every same-cut pair in R=K union F contains a fresh side from F.  Frozen
one-pass semantics then prevents that side from being reused in the same pass.

This checker verifies the implementation assumptions through GT_8 up to novelty
n-2:

- every recorded Resolution event chooses both parents from the exact entry key;
- no raw same-cut pair occurs in an entry key;
- every raw same-cut output pair contains at least one clause absent from the
  entry key;
- no output-fresh clause is used as a parent by another event in the same pass.

The abstract proof does not depend on the finite run.  This file is an
implementation-conformance certificate.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_component_tree_clause_audit import execution_context
from janus_tear_gt_double_bridge_transition_birth import enumerate_double_bridges

Clause = tuple[int, ...]


def same_cut_pairs(n: int, clauses, assignment, pairs):
    return tuple(
        record
        for record in enumerate_double_bridges(
            n, tuple(clauses), assignment, pairs
        )
        if record["left_bridge"]["cut"]
        == record["right_bridge"]["cut"]
    )


def audit(n: int):
    context = execution_context(n)
    policy = context["policy"]
    pairs = context["pairs"]
    levels = context["levels"]
    target = n - 2

    counts: Counter[str] = Counter()
    fresh_side_histogram: Counter[int] = Counter()
    origin_shapes: Counter[tuple[bool, bool]] = Counter()
    examples = []

    for state in policy.states.values():
        state_id = int(state["id"])
        call_id = int(state["entry_call"])
        novelty = int(levels[call_id])
        if novelty > target:
            continue

        counts["states"] += 1
        assignment = context["call_after_pre"][call_id]
        key = tuple(tuple(clause) for clause in state["key"])
        key_set = set(key)
        output = tuple(tuple(clause) for clause in state["resolution_output"])
        output_set = set(output)
        fresh_set = output_set - key_set

        assert key_set <= output_set
        counts["entry_clause_occurrences"] += len(key)
        counts["output_clause_occurrences"] += len(output)
        counts["fresh_output_clause_occurrences"] += len(fresh_set)

        event_parent_clauses: set[Clause] = set()
        for event in state.get("resolution_events", ()):
            counts["resolution_events"] += 1
            left = tuple(event["left"])
            right = tuple(event["right"])
            resolvent = tuple(event["resolvent"])
            assert left in key_set
            assert right in key_set
            assert resolvent in output_set
            event_parent_clauses.add(left)
            event_parent_clauses.add(right)

        assert not (event_parent_clauses & fresh_set)

        key_same_cut = same_cut_pairs(n, key, assignment, pairs)
        counts["entry_key_same_cut_occurrences"] += len(key_same_cut)
        assert not key_same_cut

        raw_same_cut = same_cut_pairs(n, output, assignment, pairs)
        counts["raw_output_same_cut_occurrences"] += len(raw_same_cut)
        for record in raw_same_cut:
            left = tuple(record["left"])
            right = tuple(record["right"])
            left_fresh = left in fresh_set
            right_fresh = right in fresh_set
            fresh_sides = int(left_fresh) + int(right_fresh)
            assert fresh_sides >= 1
            fresh_side_histogram[fresh_sides] += 1
            origin_shapes[(left_fresh, right_fresh)] += 1
            if len(examples) < 20:
                examples.append({
                    "n": n,
                    "state_id": state_id,
                    "call_id": call_id,
                    "novelty": novelty,
                    "pivot": int(record["pivot"]),
                    "left": left,
                    "right": right,
                    "left_fresh": left_fresh,
                    "right_fresh": right_fresh,
                    "roles": tuple(sorted((
                        str(record["left_bridge"]["role"]),
                        str(record["right_bridge"]["role"]),
                    ))),
                    "cut": record["left_bridge"]["cut"],
                })

    return {
        "n": n,
        "target": target,
        "counts": tuple(sorted(counts.items())),
        "fresh_side_histogram": tuple(sorted(fresh_side_histogram.items())),
        "origin_shapes": tuple(sorted(origin_shapes.items(), key=repr)),
        "examples": tuple(examples),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_fresh_sides: Counter[int] = Counter()
    aggregate_shapes: Counter[tuple[bool, bool]] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_fresh_sides.update(dict(data["fresh_side_histogram"]))
        aggregate_shapes.update(dict(data["origin_shapes"]))
        rows.append((
            n,
            data["target"],
            data["counts"],
            data["fresh_side_histogram"],
            data["origin_shapes"],
        ))
        print(f"ORDER_SIZE = {n}")
        print(f"  target = {data['target']}")
        print(f"  counts = {data['counts']}")
        print(f"  fresh_side_histogram = {data['fresh_side_histogram']}")
        print(f"  origin_shapes = {data['origin_shapes']}")
        print(f"  examples = {data['examples']}")

    assert aggregate_counts["states"] == 615
    assert aggregate_counts["entry_key_same_cut_occurrences"] == 0
    assert aggregate_counts["raw_output_same_cut_occurrences"] == 2
    assert aggregate_fresh_sides == Counter({1: 1, 2: 1})
    assert sum(aggregate_shapes.values()) == 2

    print("JANUS_GT_FROZEN_FRESH_SIDE_BARRIER = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_FRESH_SIDE_HISTOGRAM = {tuple(sorted(aggregate_fresh_sides.items()))}")
    print(f"AGGREGATE_ORIGIN_SHAPES = {tuple(sorted(aggregate_shapes.items(), key=repr))}")
    print(
        "claim_boundary = implementation conformance through GT_8 for the "
        "arbitrary-n set-theoretic frozen fresh-side barrier"
    )


if __name__ == "__main__":
    self_test()
