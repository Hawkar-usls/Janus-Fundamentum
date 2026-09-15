#!/usr/bin/env python3
"""Certify the finite base for the root unsafe-surplus theorem through GT_47.

The asymptotic block argument proves strict selected-versus-unsafe surplus for
n >= 48.  This checker closes the finite remainder using the exact implemented
root Policy-0A stages.

For every immediate-local root component-spanning non-tail bridge occurrence:

- reconstruct its bridge cut;
- verify the two-versus-(n-2) N/T subdivided-star template (except explicit
  GT_4 base cases);
- construct the geometric unsafe class B: comparison variables absent from the
  tracked clause whose endpoints lie inside the large bridge side and avoid
  the distinguished bad head endpoint;
- compare exact post-result frequencies and fresh-resolvent surpluses;
- require a strict selected advantage whenever B is nonempty.

For n >= 6, width-four T/T resolvents cannot span n quotient vertices, so only
fresh width-(n-1) clauses need graph analysis.  This keeps the exact GT_47 gate
small without changing its logical coverage.
"""

from __future__ import annotations

from collections import Counter

from janus_tear_gt_bad_bridge_birth_lifecycle import endpoint_sizes
from janus_tear_gt_bridge_endpoint_profile import bridge_record
from janus_tear_gt_component_tree_clause_audit import clause_component_graph
from janus_tear_gt_rank_safety_dichotomy import safety_class
from janus_tear_gt_root_unshielded_handoff_probe import root_stages


def quotient_map(graph, n: int):
    result = [-1] * n
    for component_index, part in enumerate(graph["parts"]):
        for vertex in part:
            result[int(vertex)] = int(component_index)
    assert all(component >= 0 for component in result)
    return tuple(result)


def side_containing(cut, component_index: int):
    left, right = cut
    if component_index in left:
        return tuple(left), tuple(right)
    assert component_index in right
    return tuple(right), tuple(left)


def audit(n: int):
    stages = root_stages(n)
    root = tuple(stages["root"])
    post = tuple(stages["post"])
    events = tuple(stages["events"])
    pairs = stages["pairs"]
    selected = int(stages["selected"])
    assignment = dict(stages["post_assignment"])
    assert not assignment
    assert not stages["post_events"]

    root_set = set(root)
    fresh_clauses = tuple(clause for clause in post if clause not in root_set)
    fresh_set = set(fresh_clauses)
    event_resolvents = {tuple(event["resolvent"]) for event in events}
    assert fresh_set == event_resolvents

    frequencies = Counter(
        abs(literal)
        for clause in post
        for literal in clause
    )
    baseline = 2 * (n - 1)
    fresh_frequencies = Counter(
        abs(literal)
        for clause in fresh_clauses
        for literal in clause
    )
    assert frequencies[selected] == max(frequencies.values())
    assert frequencies[selected] == baseline + fresh_frequencies[selected]

    counts: Counter[str] = Counter()
    cut_shapes: Counter[tuple[int, int]] = Counter()
    unsafe_sizes: Counter[int] = Counter()
    frequency_gaps: Counter[int] = Counter()
    surplus_gaps: Counter[int] = Counter()
    selected_pairs: Counter[tuple[int, int]] = Counter()
    rows = []

    candidate_clauses = (
        fresh_clauses
        if n <= 5
        else tuple(clause for clause in fresh_clauses if len(clause) == n - 1)
    )

    for clause in candidate_clauses:
        classification = str(
            safety_class(n, clause, assignment, pairs)["classification"]
        )
        if classification != "COMPONENT_SPANNING":
            continue
        graph = clause_component_graph(n, clause, assignment, pairs)
        vertex_component = quotient_map(graph, n)

        for literal in clause:
            literal = int(literal)
            bad_bridge = bridge_record(clause, graph, pairs, literal)
            if bad_bridge is None or bad_bridge["role"] == "TAIL_SINGLETON":
                continue
            sizes = endpoint_sizes(graph, literal, pairs)
            assert int(sizes["tail_size"]) == 1
            assert int(sizes["head_size"]) == 1
            counts["root_unshielded_occurrences"] += 1

            tail_side, head_side = side_containing(
                bad_bridge["cut"], int(sizes["tail_component"])
            )
            shape = (len(tail_side), len(head_side))
            cut_shapes[shape] += 1
            if n >= 5:
                assert shape == (2, n - 2)
                counts["two_by_n_minus_two_templates"] += 1

            head_component = int(sizes["head_component"])
            unsafe_region = set(head_side) - {head_component}
            clause_variables = {abs(candidate) for candidate in clause}
            unsafe_variables = []
            for variable, endpoints in pairs.items():
                if variable in clause_variables:
                    continue
                low, high = endpoints
                endpoint_components = {
                    vertex_component[int(low)],
                    vertex_component[int(high)],
                }
                if endpoint_components.issubset(unsafe_region):
                    unsafe_variables.append(int(variable))

            unsafe_variables = tuple(sorted(unsafe_variables))
            unsafe_sizes[len(unsafe_variables)] += 1
            expected_unsafe_size = 0 if n == 4 else (n - 3) * (n - 4) // 2
            assert len(unsafe_variables) == expected_unsafe_size

            if unsafe_variables:
                maximum_unsafe_frequency = max(
                    frequencies[variable] for variable in unsafe_variables
                )
                maximum_unsafe_surplus = max(
                    fresh_frequencies[variable] for variable in unsafe_variables
                )
                frequency_gap = frequencies[selected] - maximum_unsafe_frequency
                surplus_gap = (
                    fresh_frequencies[selected] - maximum_unsafe_surplus
                )
                assert frequency_gap == surplus_gap
                assert surplus_gap > 0
                counts["nonvacuous_occurrences"] += 1
                frequency_gaps[frequency_gap] += 1
                surplus_gaps[surplus_gap] += 1
            else:
                maximum_unsafe_frequency = None
                maximum_unsafe_surplus = None
                frequency_gap = None
                surplus_gap = None
                counts["vacuous_occurrences"] += 1

            selected_pairs[tuple(pairs[selected])] += 1
            rows.append(
                {
                    "n": n,
                    "clause": clause,
                    "bad_literal": literal,
                    "cut_shape": shape,
                    "selected": selected,
                    "selected_pair": tuple(pairs[selected]),
                    "selected_frequency": frequencies[selected],
                    "selected_surplus": fresh_frequencies[selected],
                    "unsafe_size": len(unsafe_variables),
                    "maximum_unsafe_frequency": maximum_unsafe_frequency,
                    "maximum_unsafe_surplus": maximum_unsafe_surplus,
                    "frequency_gap": frequency_gap,
                    "surplus_gap": surplus_gap,
                }
            )

    assert counts["root_unshielded_occurrences"] > 0
    return {
        "n": n,
        "baseline": baseline,
        "selected": selected,
        "selected_pair": tuple(pairs[selected]),
        "selected_surplus": fresh_frequencies[selected],
        "fresh_clauses": len(fresh_clauses),
        "counts": tuple(sorted(counts.items())),
        "cut_shapes": tuple(sorted(cut_shapes.items())),
        "unsafe_sizes": tuple(sorted(unsafe_sizes.items())),
        "frequency_gaps": tuple(sorted(frequency_gaps.items())),
        "surplus_gaps": tuple(sorted(surplus_gaps.items())),
        "selected_pairs": tuple(sorted(selected_pairs.items())),
        "rows": tuple(rows),
    }


def self_test() -> None:
    aggregate_counts: Counter[str] = Counter()
    aggregate_shapes: Counter[tuple[int, int]] = Counter()
    aggregate_unsafe_sizes: Counter[int] = Counter()
    aggregate_gaps: Counter[int] = Counter()
    selected_by_order = []
    minimum_positive_gap = None

    for n in range(4, 48):
        data = audit(n)
        aggregate_counts.update(dict(data["counts"]))
        aggregate_shapes.update(dict(data["cut_shapes"]))
        aggregate_unsafe_sizes.update(dict(data["unsafe_sizes"]))
        aggregate_gaps.update(dict(data["surplus_gaps"]))
        selected_by_order.append(
            (
                n,
                data["selected"],
                data["selected_pair"],
                data["selected_surplus"],
                data["counts"],
                data["surplus_gaps"],
            )
        )
        for gap, _count in data["surplus_gaps"]:
            minimum_positive_gap = (
                gap
                if minimum_positive_gap is None
                else min(minimum_positive_gap, gap)
            )
        print(f"ORDER_SIZE = {n}")
        print(f"  selected = {data['selected']} / pair {data['selected_pair']}")
        print(f"  selected_surplus = {data['selected_surplus']}")
        print(f"  fresh_clauses = {data['fresh_clauses']}")
        print(f"  counts = {data['counts']}")
        print(f"  cut_shapes = {data['cut_shapes']}")
        print(f"  unsafe_sizes = {data['unsafe_sizes']}")
        print(f"  surplus_gaps = {data['surplus_gaps']}")

    assert aggregate_counts["root_unshielded_occurrences"] > 0
    assert aggregate_counts["nonvacuous_occurrences"] > 0
    assert minimum_positive_gap is not None and minimum_positive_gap > 0

    print("JANUS_GT_ROOT_SURPLUS_GAP_FINITE_BASE = PASS")
    print("FINITE_BASE_RANGE = GT_4_THROUGH_GT_47")
    print(f"MINIMUM_POSITIVE_GAP = {minimum_positive_gap}")
    print(f"AGGREGATE_COUNTS = {tuple(sorted(aggregate_counts.items()))}")
    print(f"AGGREGATE_CUT_SHAPES = {tuple(sorted(aggregate_shapes.items()))}")
    print(
        "AGGREGATE_UNSAFE_SIZES = "
        f"{tuple(sorted(aggregate_unsafe_sizes.items()))}"
    )
    print(f"AGGREGATE_GAPS = {tuple(sorted(aggregate_gaps.items()))}")
    print(f"SELECTED_BY_ORDER = {tuple(selected_by_order)}")
    print(
        "finite_result = every root geometric unsafe class has strictly lower "
        "fresh-resolvent surplus than the exact selected maximum through GT_47"
    )
    print(
        "claim_boundary = exact finite base for the asymptotic block theorem; "
        "independent CI admission required before promoting full arbitrary-n "
        "root surplus separation"
    )


if __name__ == "__main__":
    self_test()
