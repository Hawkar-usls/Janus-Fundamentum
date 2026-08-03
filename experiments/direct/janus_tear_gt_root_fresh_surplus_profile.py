#!/usr/bin/env python3
"""Decompose root selected-versus-unsafe frequency gaps into fresh Resolution surplus.

The canonical GT root CNF gives every comparison variable exactly 2(n-1)
occurrences.  This profile independently verifies that baseline, checks the
root post-unit stage is empty, and subtracts the baseline from every exact
selected and unsafe frequency emitted by the unsafe-set margin audit.

The remaining values are counts contributed by fresh frozen-pass resolvents.
No full-saturation assumption is made; the exact implemented attempt/addition
budgets and enumeration order are replayed by root_stages().
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_root_unsafe_selector_margin import audit as margin_audit
from janus_tear_gt_root_unshielded_handoff_probe import root_stages


def variable_frequencies(cnf):
    return Counter(
        abs(literal)
        for clause in cnf
        for literal in clause
    )


def audit(n: int):
    stages = root_stages(n)
    root = tuple(stages["root"])
    post = tuple(stages["post"])
    post_events = tuple(stages["post_events"])
    assert not post_events

    root_frequency = variable_frequencies(root)
    post_frequency = variable_frequencies(post)
    expected_baseline = 2 * (n - 1)
    assert set(root_frequency.values()) == {expected_baseline}
    assert set(root_frequency) == set(post_frequency)

    fresh_clauses = tuple(
        clause
        for clause in post
        if clause not in set(root)
    )
    assert set(post) == set(root) | set(fresh_clauses)
    fresh_frequency = variable_frequencies(fresh_clauses)
    for variable in post_frequency:
        assert post_frequency[variable] == (
            expected_baseline + fresh_frequency[variable]
        )

    margin = margin_audit(n)
    selected = int(margin["selected"])
    selected_surplus = fresh_frequency[selected]

    counts: Counter[str] = Counter()
    selected_surplus_histogram: Counter[int] = Counter()
    unsafe_surplus_histogram: Counter[int] = Counter()
    unsafe_max_surplus_histogram: Counter[int] = Counter()
    surplus_gap_histogram: Counter[int] = Counter()
    unsafe_positive_variables: Counter[int] = Counter()
    unsafe_fresh_clause_counts: Counter[int] = Counter()
    rows = []

    for item in margin["rows"]:
        counts["occurrences"] += 1
        selected_surplus_histogram[selected_surplus] += 1
        unsafe_variables = tuple(int(v) for v in item["unsafe_variables"])
        if not unsafe_variables:
            counts["vacuous_occurrences"] += 1
            rows.append(
                {
                    "n": n,
                    "clause": tuple(item["clause"]),
                    "literal": int(item["literal"]),
                    "selected": selected,
                    "baseline": expected_baseline,
                    "selected_surplus": selected_surplus,
                    "unsafe_variables": (),
                }
            )
            continue

        counts["nonvacuous_occurrences"] += 1
        unsafe_surpluses = tuple(
            fresh_frequency[variable]
            for variable in unsafe_variables
        )
        for variable, surplus in zip(unsafe_variables, unsafe_surpluses):
            unsafe_surplus_histogram[surplus] += 1
            if surplus > 0:
                counts["unsafe_positive_surplus_pairs"] += 1
                unsafe_positive_variables[variable] += 1
                unsafe_fresh_clause_counts[sum(
                    1
                    for clause in fresh_clauses
                    if variable in {abs(literal) for literal in clause}
                )] += 1
            else:
                counts["unsafe_zero_surplus_pairs"] += 1

        maximum_unsafe_surplus = max(unsafe_surpluses)
        unsafe_max_surplus_histogram[maximum_unsafe_surplus] += 1
        surplus_gap = selected_surplus - maximum_unsafe_surplus
        assert surplus_gap == int(item["frequency_gap"])
        assert surplus_gap > 0
        surplus_gap_histogram[surplus_gap] += 1

        rows.append(
            {
                "n": n,
                "clause": tuple(item["clause"]),
                "literal": int(item["literal"]),
                "selected": selected,
                "baseline": expected_baseline,
                "selected_post_frequency": post_frequency[selected],
                "selected_surplus": selected_surplus,
                "unsafe_variables": unsafe_variables,
                "unsafe_surpluses": unsafe_surpluses,
                "maximum_unsafe_surplus": maximum_unsafe_surplus,
                "surplus_gap": surplus_gap,
            }
        )

    return {
        "n": n,
        "variables": len(root_frequency),
        "root_clauses": len(root),
        "fresh_clauses": len(fresh_clauses),
        "resolution_attempts": int(stages["attempts"]),
        "resolution_additions": int(stages["additions"]),
        "baseline": expected_baseline,
        "selected": selected,
        "selected_post_frequency": post_frequency[selected],
        "selected_surplus": selected_surplus,
        "counts": tuple(sorted(counts.items())),
        "selected_surplus_histogram": tuple(sorted(selected_surplus_histogram.items())),
        "unsafe_surplus_histogram": tuple(sorted(unsafe_surplus_histogram.items())),
        "unsafe_max_surplus_histogram": tuple(sorted(unsafe_max_surplus_histogram.items())),
        "surplus_gap_histogram": tuple(sorted(surplus_gap_histogram.items())),
        "unsafe_positive_variables": tuple(sorted(unsafe_positive_variables.items())),
        "unsafe_fresh_clause_counts": tuple(sorted(unsafe_fresh_clause_counts.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_selected_surplus: Counter[int] = Counter()
    aggregate_unsafe_surplus: Counter[int] = Counter()
    aggregate_unsafe_max: Counter[int] = Counter()
    aggregate_gaps: Counter[int] = Counter()
    aggregate_positive_variables: Counter[int] = Counter()
    aggregate_fresh_clause_counts: Counter[int] = Counter()
    per_order = []

    for n in range(4, 13):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_selected_surplus.update(dict(data["selected_surplus_histogram"]))
        aggregate_unsafe_surplus.update(dict(data["unsafe_surplus_histogram"]))
        aggregate_unsafe_max.update(dict(data["unsafe_max_surplus_histogram"]))
        aggregate_gaps.update(dict(data["surplus_gap_histogram"]))
        aggregate_positive_variables.update(dict(data["unsafe_positive_variables"]))
        aggregate_fresh_clause_counts.update(dict(data["unsafe_fresh_clause_counts"]))
        per_order.append(
            (
                n,
                data["baseline"],
                data["fresh_clauses"],
                data["selected"],
                data["selected_post_frequency"],
                data["selected_surplus"],
                data["unsafe_max_surplus_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  variables = {data['variables']}")
        print(f"  root_clauses = {data['root_clauses']}")
        print(f"  fresh_clauses = {data['fresh_clauses']}")
        print(f"  resolution_attempts = {data['resolution_attempts']}")
        print(f"  resolution_additions = {data['resolution_additions']}")
        print(f"  baseline = {data['baseline']}")
        print(f"  selected = {data['selected']}")
        print(f"  selected_post_frequency = {data['selected_post_frequency']}")
        print(f"  selected_surplus = {data['selected_surplus']}")
        print(f"  counts = {data['counts']}")
        print(f"  unsafe_surplus_histogram = {data['unsafe_surplus_histogram']}")
        print(f"  unsafe_max_surplus_histogram = {data['unsafe_max_surplus_histogram']}")
        print(f"  surplus_gap_histogram = {data['surplus_gap_histogram']}")
        print(f"  unsafe_positive_variables = {data['unsafe_positive_variables']}")

    assert aggregate_counts["occurrences"] == 62
    assert aggregate_counts["vacuous_occurrences"] == 4
    assert aggregate_counts["nonvacuous_occurrences"] == 58
    assert sum(aggregate_unsafe_surplus.values()) == 1397
    assert aggregate_unsafe_max == Counter({0: 56, 1: 2})
    assert aggregate_gaps == Counter(
        {
            6: 2,
            7: 2,
            10: 3,
            14: 5,
            18: 6,
            21: 7,
            26: 13,
            31: 18,
            32: 2,
        }
    )

    print("JANUS_GT_ROOT_FRESH_SURPLUS_PROFILE = PASS")
    print(f"PER_ORDER = {tuple(per_order)}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(
        "AGGREGATE_SELECTED_SURPLUS = "
        f"{tuple(sorted(aggregate_selected_surplus.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_SURPLUS = "
        f"{tuple(sorted(aggregate_unsafe_surplus.items()))}"
    )
    print(f"AGGREGATE_UNSAFE_MAX = {tuple(sorted(aggregate_unsafe_max.items()))}")
    print(f"AGGREGATE_GAPS = {tuple(sorted(aggregate_gaps.items()))}")
    print(
        "AGGREGATE_POSITIVE_UNSAFE_VARIABLES = "
        f"{tuple(sorted(aggregate_positive_variables.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_FRESH_CLAUSE_COUNTS = "
        f"{tuple(sorted(aggregate_fresh_clause_counts.items()))}"
    )
    print(
        "finite_result = uniform root baseline cancels exactly; 56 of 58 "
        "nonvacuous occurrences have maximum unsafe fresh surplus zero, and "
        "the remaining two have maximum unsafe surplus one"
    )
    print(
        "claim_boundary = exact frozen-surplus profile through GT_12; "
        "arbitrary-n unsafe-surplus separation remains open"
    )


if __name__ == "__main__":
    self_test()
