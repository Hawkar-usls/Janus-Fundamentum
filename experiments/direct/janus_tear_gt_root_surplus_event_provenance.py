#!/usr/bin/env python3
"""Profile the exact root Resolution events paying selected and unsafe surplus.

At the canonical GT root, every variable has uniform baseline 2(n-1).  Each
post-frequency surplus unit is therefore one accepted fresh frozen-pass
resolvent containing that variable.

For GT_4..GT_12 this audit classifies every accepted event by direct root parent
families (NONMINIMALITY or TRANSITIVITY), pivot, attempt index, and resolvent
width.  It then emits the complete event provenance paying:

- the selected maximum-frequency variable's surplus;
- every actual unsafe variable's positive surplus.

The purpose is to expose a repeatable frozen-enumeration template rather than
infer one from aggregate frequency values.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_root_unsafe_selector_margin import audit as margin_audit
from janus_tear_gt_root_unshielded_handoff_probe import root_stages
from janus_tear_gt_same_cut_parent_ancestry import root_minimum_labels


def parent_family(clause, minimum_labels):
    return (
        "NONMINIMALITY"
        if tuple(clause) in minimum_labels
        else "TRANSITIVITY"
    )


def audit(n: int):
    stages = root_stages(n)
    root = tuple(stages["root"])
    pairs = stages["pairs"]
    events = tuple(stages["events"])
    minimum_labels = root_minimum_labels(n, pairs)
    assert set(minimum_labels).issubset(set(root))
    margin = margin_audit(n)
    selected = int(margin["selected"])

    unsafe_variables = tuple(sorted({
        int(variable)
        for row in margin["rows"]
        for variable in row["unsafe_variables"]
    }))

    event_family_histogram: Counter[tuple[str, str]] = Counter()
    event_width_histogram: Counter[int] = Counter()
    event_pivot_histogram: Counter[int] = Counter()
    selected_family_histogram: Counter[tuple[str, str]] = Counter()
    selected_width_histogram: Counter[int] = Counter()
    selected_pivot_histogram: Counter[int] = Counter()
    unsafe_family_histogram: Counter[tuple[str, str]] = Counter()
    unsafe_width_histogram: Counter[int] = Counter()
    unsafe_pivot_histogram: Counter[int] = Counter()
    unsafe_variable_event_counts: Counter[int] = Counter()
    selected_records = []
    unsafe_records = []

    for event_index, event in enumerate(events):
        left = tuple(event["left"])
        right = tuple(event["right"])
        resolvent = tuple(event["resolvent"])
        family = tuple(sorted((
            parent_family(left, minimum_labels),
            parent_family(right, minimum_labels),
        )))
        pivot = int(event["pivot"])
        width = len(resolvent)
        variables = {abs(literal) for literal in resolvent}

        event_family_histogram[family] += 1
        event_width_histogram[width] += 1
        event_pivot_histogram[pivot] += 1

        record = {
            "event_index": event_index,
            "attempt": int(event["attempt"]),
            "pivot": pivot,
            "family": family,
            "left": left,
            "right": right,
            "resolvent": resolvent,
            "width": width,
        }

        if selected in variables:
            selected_family_histogram[family] += 1
            selected_width_histogram[width] += 1
            selected_pivot_histogram[pivot] += 1
            selected_records.append(record)

        hit_unsafe = tuple(
            variable for variable in unsafe_variables if variable in variables
        )
        if hit_unsafe:
            unsafe_family_histogram[family] += len(hit_unsafe)
            unsafe_width_histogram[width] += len(hit_unsafe)
            unsafe_pivot_histogram[pivot] += len(hit_unsafe)
            for variable in hit_unsafe:
                unsafe_variable_event_counts[variable] += 1
            unsafe_records.append({**record, "unsafe_variables": hit_unsafe})

    post = tuple(stages["post"])
    root_set = set(root)
    fresh = tuple(clause for clause in post if clause not in root_set)
    assert len(fresh) == len(events) == int(stages["additions"])
    selected_surplus = sum(
        1 for clause in fresh if selected in {abs(literal) for literal in clause}
    )
    assert selected_surplus == len(selected_records)

    return {
        "n": n,
        "selected": selected,
        "selected_surplus": selected_surplus,
        "unsafe_variables": unsafe_variables,
        "events": len(events),
        "attempts": int(stages["attempts"]),
        "event_family_histogram": tuple(sorted(event_family_histogram.items(), key=repr)),
        "event_width_histogram": tuple(sorted(event_width_histogram.items())),
        "event_pivot_histogram": tuple(sorted(event_pivot_histogram.items())),
        "selected_family_histogram": tuple(sorted(selected_family_histogram.items(), key=repr)),
        "selected_width_histogram": tuple(sorted(selected_width_histogram.items())),
        "selected_pivot_histogram": tuple(sorted(selected_pivot_histogram.items())),
        "unsafe_family_histogram": tuple(sorted(unsafe_family_histogram.items(), key=repr)),
        "unsafe_width_histogram": tuple(sorted(unsafe_width_histogram.items())),
        "unsafe_pivot_histogram": tuple(sorted(unsafe_pivot_histogram.items())),
        "unsafe_variable_event_counts": tuple(sorted(unsafe_variable_event_counts.items())),
        "selected_records": tuple(selected_records),
        "unsafe_records": tuple(unsafe_records),
    }


def self_test() -> None:
    aggregate_selected_families: Counter[tuple[str, str]] = Counter()
    aggregate_unsafe_families: Counter[tuple[str, str]] = Counter()
    aggregate_selected_widths: Counter[int] = Counter()
    aggregate_unsafe_widths: Counter[int] = Counter()
    aggregate_selected_pivots: Counter[int] = Counter()
    aggregate_unsafe_pivots: Counter[int] = Counter()
    aggregate_unsafe_variable_events: Counter[int] = Counter()
    per_order = []
    all_unsafe_records = []

    for n in range(4, 13):
        data = audit(n)
        aggregate_selected_families.update(dict(data["selected_family_histogram"]))
        aggregate_unsafe_families.update(dict(data["unsafe_family_histogram"]))
        aggregate_selected_widths.update(dict(data["selected_width_histogram"]))
        aggregate_unsafe_widths.update(dict(data["unsafe_width_histogram"]))
        aggregate_selected_pivots.update(dict(data["selected_pivot_histogram"]))
        aggregate_unsafe_pivots.update(dict(data["unsafe_pivot_histogram"]))
        aggregate_unsafe_variable_events.update(dict(data["unsafe_variable_event_counts"]))
        all_unsafe_records.extend({"n": n, **record} for record in data["unsafe_records"])
        per_order.append(
            (
                n,
                data["selected"],
                data["selected_surplus"],
                data["events"],
                data["selected_family_histogram"],
                data["unsafe_family_histogram"],
            )
        )
        print(f"ORDER_SIZE = {n}")
        print(f"  selected = {data['selected']}")
        print(f"  selected_surplus = {data['selected_surplus']}")
        print(f"  events = {data['events']} / attempts {data['attempts']}")
        print(f"  event_family_histogram = {data['event_family_histogram']}")
        print(f"  selected_family_histogram = {data['selected_family_histogram']}")
        print(f"  selected_width_histogram = {data['selected_width_histogram']}")
        print(f"  selected_pivot_histogram = {data['selected_pivot_histogram']}")
        print(f"  unsafe_family_histogram = {data['unsafe_family_histogram']}")
        print(f"  unsafe_width_histogram = {data['unsafe_width_histogram']}")
        print(f"  unsafe_pivot_histogram = {data['unsafe_pivot_histogram']}")
        print(f"  unsafe_variable_event_counts = {data['unsafe_variable_event_counts']}")
        print(f"  unsafe_records = {data['unsafe_records']}")

    print("JANUS_GT_ROOT_SURPLUS_EVENT_PROVENANCE = PASS")
    print(f"PER_ORDER = {tuple(per_order)}")
    print(
        "AGGREGATE_SELECTED_FAMILIES = "
        f"{tuple(sorted(aggregate_selected_families.items(), key=repr))}"
    )
    print(
        "AGGREGATE_UNSAFE_FAMILIES = "
        f"{tuple(sorted(aggregate_unsafe_families.items(), key=repr))}"
    )
    print(
        "AGGREGATE_SELECTED_WIDTHS = "
        f"{tuple(sorted(aggregate_selected_widths.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_WIDTHS = "
        f"{tuple(sorted(aggregate_unsafe_widths.items()))}"
    )
    print(
        "AGGREGATE_SELECTED_PIVOTS = "
        f"{tuple(sorted(aggregate_selected_pivots.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_PIVOTS = "
        f"{tuple(sorted(aggregate_unsafe_pivots.items()))}"
    )
    print(
        "AGGREGATE_UNSAFE_VARIABLE_EVENTS = "
        f"{tuple(sorted(aggregate_unsafe_variable_events.items()))}"
    )
    print(f"ALL_UNSAFE_EVENT_RECORDS = {tuple(all_unsafe_records)}")
    print(
        "claim_boundary = exact accepted-event provenance through GT_12; "
        "arbitrary-n frozen-enumeration surplus theorem remains open"
    )


if __name__ == "__main__":
    self_test()
