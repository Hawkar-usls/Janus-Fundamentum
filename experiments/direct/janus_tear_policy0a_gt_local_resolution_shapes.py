#!/usr/bin/env python3
"""Classify Policy-0A local Resolution events on finite graph tautologies."""

from __future__ import annotations

from collections import Counter

from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def variable_pairs(n: int) -> dict[int, tuple[int, int]]:
    mapping: dict[int, tuple[int, int]] = {}
    variable = 1
    for left in range(n):
        for right in range(left + 1, n):
            mapping[variable] = (left, right)
            variable += 1
    return mapping


def self_test() -> None:
    aggregate_widths: Counter[int] = Counter()
    aggregate_supports: Counter[int] = Counter()
    aggregate_parent_widths: Counter[tuple[int, int]] = Counter()
    rows = []

    for n in range(3, 9):
        cnf, variable_count = graph_tautology_cnf(n)
        pairs = variable_pairs(n)
        assert len(pairs) == variable_count

        policy = FCTracePolicy()
        result, root_call = policy.solve(cnf, variable_count)
        assert result.answer is False
        assert root_call is not None
        assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

        width_histogram: Counter[int] = Counter()
        support_histogram: Counter[int] = Counter()
        parent_width_histogram: Counter[tuple[int, int]] = Counter()
        all_resolvents: list[tuple[int, ...]] = []
        states_with_post_units = 0
        post_unit_events = 0
        maximum_events_in_state = 0

        for state in policy.states.values():
            events = state.get("resolution_events", [])
            assert isinstance(events, list)
            maximum_events_in_state = max(maximum_events_in_state, len(events))
            for event in events:
                resolvent = tuple(event["resolvent"])
                left = tuple(event["left"])
                right = tuple(event["right"])
                all_resolvents.append(resolvent)
                width_histogram[len(resolvent)] += 1
                parent_width_histogram[
                    tuple(sorted((len(left), len(right))))
                ] += 1

                vertices: set[int] = set()
                for literal in resolvent:
                    vertices.update(pairs[abs(literal)])
                support_histogram[len(vertices)] += 1

            post_units = state.get("post_units", [])
            assert isinstance(post_units, list)
            if post_units:
                states_with_post_units += 1
                post_unit_events += len(post_units)

        unique_resolvents = set(all_resolvents)
        duplicate_occurrences = len(all_resolvents) - len(unique_resolvents)
        unit_resolvents = sum(len(clause) == 1 for clause in all_resolvents)
        empty_resolvents = sum(len(clause) == 0 for clause in all_resolvents)

        aggregate_widths.update(width_histogram)
        aggregate_supports.update(support_histogram)
        aggregate_parent_widths.update(parent_width_histogram)
        rows.append(
            (
                n,
                result.unique_states,
                result.cache_hits,
                len(all_resolvents),
                len(unique_resolvents),
                duplicate_occurrences,
                unit_resolvents,
                empty_resolvents,
                states_with_post_units,
                post_unit_events,
                maximum_events_in_state,
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  unique_states = {result.unique_states}")
        print(f"  cache_hits = {result.cache_hits}")
        print(f"  resolution_events = {len(all_resolvents)}")
        print(f"  unique_resolvent_clauses = {len(unique_resolvents)}")
        print(f"  duplicate_resolvent_occurrences = {duplicate_occurrences}")
        print(f"  unit_resolvents = {unit_resolvents}")
        print(f"  empty_resolvents = {empty_resolvents}")
        print(f"  states_with_post_resolution_units = {states_with_post_units}")
        print(f"  post_resolution_unit_events = {post_unit_events}")
        print(f"  maximum_resolution_events_in_one_state = {maximum_events_in_state}")
        print(f"  width_histogram = {tuple(sorted(width_histogram.items()))}")
        print(f"  vertex_support_histogram = {tuple(sorted(support_histogram.items()))}")
        print(
            "  parent_width_histogram = "
            f"{tuple(sorted(parent_width_histogram.items()))}"
        )

    assert rows[0][3] > 0
    print("JANUS_POLICY0A_GT_LOCAL_RESOLUTION_SHAPES = PASS")
    print(f"rows = {tuple(rows)}")
    print(f"aggregate_width_histogram = {tuple(sorted(aggregate_widths.items()))}")
    print(f"aggregate_vertex_support_histogram = {tuple(sorted(aggregate_supports.items()))}")
    print(
        "aggregate_parent_width_histogram = "
        f"{tuple(sorted(aggregate_parent_widths.items()))}"
    )
    print("claim_boundary = finite clause-shape census; no robustness theorem for the Formula-Caching lower bound")


if __name__ == "__main__":
    self_test()
