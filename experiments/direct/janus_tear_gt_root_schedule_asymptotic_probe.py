#!/usr/bin/env python3
"""Probe the exact deterministic root frozen Resolution schedule through GT_40.

This is a root-only policy probe: no recursive search and no hypothetical child
replay.  For each order it constructs the canonical GT root CNF, executes the
implemented bounded frozen Resolution pass, confirms the uniform 2(n-1)
baseline, and records:

- exact attempt/addition budgets and whether each is saturated;
- first/last accepted event pivot and attempt;
- selected maximum-frequency variable and unordered vertex pair;
- selected fresh-resolvent surplus;
- the full maximum-surplus variable set;
- the top surplus spectrum.

The output is intended to reveal stable or piecewise-stable schedule formulas.
It is finite evidence only and does not assert an asymptotic theorem.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_root_unshielded_handoff_probe import root_stages


def frequencies(cnf):
    return Counter(
        abs(literal)
        for clause in cnf
        for literal in clause
    )


def audit(n: int):
    stages = root_stages(n)
    root = tuple(stages["root"])
    post = tuple(stages["post"])
    events = tuple(stages["events"])
    pairs = stages["pairs"]
    selected = int(stages["selected"])

    root_frequency = frequencies(root)
    post_frequency = frequencies(post)
    baseline = 2 * (n - 1)
    assert set(root_frequency.values()) == {baseline}
    surplus = Counter({
        variable: post_frequency[variable] - baseline
        for variable in post_frequency
    })
    assert min(surplus.values()) >= 0
    maximum_surplus = max(surplus.values())
    maximum_variables = tuple(sorted(
        variable
        for variable, value in surplus.items()
        if value == maximum_surplus
    ))
    assert selected == maximum_variables[0]

    literal_count = sum(len(clause) for clause in root)
    width_limit = max(map(len, root)) + 1
    expected_attempt_budget = max(64, 4 * literal_count)
    expected_addition_budget = max(8, len(root) // 4)
    assert width_limit == n
    assert int(stages["additions"]) == len(events)
    assert int(stages["attempts"]) <= expected_attempt_budget
    assert int(stages["additions"]) <= expected_addition_budget

    spectrum = Counter(surplus.values())
    top_values = tuple(sorted(spectrum.items(), reverse=True)[:12])
    top_variables = tuple(sorted(
        [
            (
                value,
                variable,
                tuple(pairs[variable]),
            )
            for variable, value in surplus.items()
        ],
        reverse=True,
    )[:20])

    pivot_event_counts = Counter(int(event["pivot"]) for event in events)
    first_event = None if not events else events[0]
    last_event = None if not events else events[-1]

    return {
        "n": n,
        "variables": len(root_frequency),
        "root_clauses": len(root),
        "literal_count": literal_count,
        "baseline": baseline,
        "width_limit": width_limit,
        "attempt_budget": expected_attempt_budget,
        "attempts": int(stages["attempts"]),
        "attempt_budget_saturated": int(stages["attempts"]) == expected_attempt_budget,
        "addition_budget": expected_addition_budget,
        "additions": int(stages["additions"]),
        "addition_budget_saturated": int(stages["additions"]) == expected_addition_budget,
        "first_event_pivot": None if first_event is None else int(first_event["pivot"]),
        "first_event_attempt": None if first_event is None else int(first_event["attempt"]),
        "last_event_pivot": None if last_event is None else int(last_event["pivot"]),
        "last_event_attempt": None if last_event is None else int(last_event["attempt"]),
        "pivot_event_counts": tuple(sorted(pivot_event_counts.items())),
        "selected": selected,
        "selected_pair": tuple(pairs[selected]),
        "selected_post_frequency": post_frequency[selected],
        "selected_surplus": surplus[selected],
        "maximum_surplus": maximum_surplus,
        "maximum_variables": maximum_variables,
        "maximum_pairs": tuple(tuple(pairs[variable]) for variable in maximum_variables),
        "surplus_spectrum": tuple(sorted(spectrum.items())),
        "top_surplus_values": top_values,
        "top_variables": top_variables,
    }


def self_test() -> None:
    rows = []
    selected_histogram: Counter[int] = Counter()
    selected_pair_histogram: Counter[tuple[int, int]] = Counter()
    max_set_sizes: Counter[int] = Counter()
    last_pivots: Counter[int] = Counter()
    attempt_saturation: Counter[bool] = Counter()
    addition_saturation: Counter[bool] = Counter()

    for n in range(4, 41):
        data = audit(n)
        selected_histogram[data["selected"]] += 1
        selected_pair_histogram[data["selected_pair"]] += 1
        max_set_sizes[len(data["maximum_variables"])] += 1
        last_pivots[int(data["last_event_pivot"])] += 1
        attempt_saturation[bool(data["attempt_budget_saturated"])] += 1
        addition_saturation[bool(data["addition_budget_saturated"])] += 1
        row = (
            n,
            data["variables"],
            data["root_clauses"],
            data["attempt_budget"],
            data["attempts"],
            data["addition_budget"],
            data["additions"],
            data["last_event_pivot"],
            data["last_event_attempt"],
            data["selected"],
            data["selected_pair"],
            data["selected_surplus"],
            data["maximum_variables"],
            data["top_surplus_values"],
        )
        rows.append(row)
        print(f"ORDER_SIZE = {n}")
        print(f"  variables = {data['variables']}")
        print(f"  root_clauses = {data['root_clauses']}")
        print(f"  baseline = {data['baseline']}")
        print(
            f"  attempts = {data['attempts']} / {data['attempt_budget']} "
            f"saturated={data['attempt_budget_saturated']}"
        )
        print(
            f"  additions = {data['additions']} / {data['addition_budget']} "
            f"saturated={data['addition_budget_saturated']}"
        )
        print(
            f"  event pivots = {data['first_event_pivot']} -> "
            f"{data['last_event_pivot']}"
        )
        print(f"  last_event_attempt = {data['last_event_attempt']}")
        print(
            f"  selected = {data['selected']} pair={data['selected_pair']} "
            f"surplus={data['selected_surplus']}"
        )
        print(f"  maximum_variables = {data['maximum_variables']}")
        print(f"  maximum_pairs = {data['maximum_pairs']}")
        print(f"  top_surplus_values = {data['top_surplus_values']}")
        print(f"  top_variables = {data['top_variables']}")

    print("JANUS_GT_ROOT_SCHEDULE_ASYMPTOTIC_PROBE = PASS")
    print(f"ROWS = {tuple(rows)}")
    print(f"SELECTED_HISTOGRAM = {tuple(sorted(selected_histogram.items()))}")
    print(
        "SELECTED_PAIR_HISTOGRAM = "
        f"{tuple(sorted(selected_pair_histogram.items()))}"
    )
    print(f"MAX_SET_SIZES = {tuple(sorted(max_set_sizes.items()))}")
    print(f"LAST_PIVOTS = {tuple(sorted(last_pivots.items()))}")
    print(f"ATTEMPT_SATURATION = {tuple(sorted(attempt_saturation.items()))}")
    print(f"ADDITION_SATURATION = {tuple(sorted(addition_saturation.items()))}")
    print(
        "claim_boundary = exact root frozen schedule through GT_40; no "
        "asymptotic schedule formula asserted"
    )


if __name__ == "__main__":
    self_test()
