#!/usr/bin/env python3
"""Strengthen the finite canonical root-shield certificate through GT_8.

For every non-tail bridge occurrence reported by the root non-minimality shield
audit, verify the exact structural pattern suggested by the trace:

- the root non-minimality axiom is completely untouched by restriction;
- the tail Hasse component is a singleton;
- the head Hasse component has size at least two;
- every other vertex in that head component contributes one quotient-parallel
  shield literal, so parallel multiplicity equals head size minus one.

This is finite evidence for the remaining arbitrary-n birth lemma, not its
proof.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_root_nonminimality_bridge_shield import audit


def self_test() -> None:
    counts: Counter[str] = Counter()
    head_size_histogram: Counter[int] = Counter()
    parallel_histogram: Counter[int] = Counter()
    rows = []

    for n in range(4, 9):
        data = audit(n)
        examples = tuple(data["examples"])
        expected = dict(data["counts"])["non_tail_bridge_occurrences"]
        assert len(examples) == expected

        for record in examples:
            counts["non_tail_bridge_occurrences"] += 1
            assert tuple(record["root_residual"]) == tuple(record["root_non_minimality"])
            counts["untouched_root_axioms"] += 1

            tail_size = int(record["tail_component_size"])
            head_size = int(record["head_component_size"])
            parallel_count = len(tuple(record["parallel_literals"]))

            assert tail_size == 1
            assert head_size >= 2
            assert parallel_count == head_size - 1

            counts["singleton_tail"] += 1
            counts["merged_head"] += 1
            counts["exact_parallel_multiplicity"] += 1
            head_size_histogram[head_size] += 1
            parallel_histogram[parallel_count] += 1

        rows.append({
            "n": n,
            "occurrences": expected,
            "head_sizes": dict(data["head_component_sizes"]),
            "parallel_multiplicity": dict(data["parallel_multiplicity"]),
        })

    assert counts == Counter({
        "non_tail_bridge_occurrences": 62,
        "untouched_root_axioms": 62,
        "singleton_tail": 62,
        "merged_head": 62,
        "exact_parallel_multiplicity": 62,
    })
    assert head_size_histogram == Counter({2: 12, 3: 21, 4: 17, 5: 12})
    assert parallel_histogram == Counter({1: 12, 2: 21, 3: 17, 4: 12})

    print("JANUS_GT_ROOT_SHIELD_STRENGTH_CERTIFICATE = PASS")
    for row in rows:
        print(f"ROW = {row}")
    print(f"COUNTS = {dict(counts)}")
    print(f"HEAD_SIZE_HISTOGRAM = {dict(sorted(head_size_histogram.items()))}")
    print(f"PARALLEL_HISTOGRAM = {dict(sorted(parallel_histogram.items()))}")
    print(
        "claim_boundary = exhaustive finite strengthening through GT_8; "
        "the arbitrary-n singleton-tail/merged-head birth lemma remains open"
    )


if __name__ == "__main__":
    self_test()
