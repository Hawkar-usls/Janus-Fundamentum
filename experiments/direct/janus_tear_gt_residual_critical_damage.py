#!/usr/bin/env python3
"""Audit assignment-compatible critical orders at every unique GT residual state.

For each Policy-0A state we reconstruct the full assignment accumulated from
branch decisions and recorded unit propagation before the local Resolution pass.
The candidate witness set is the set of critical total orders consistent with
that assignment. We measure how many such orders are falsified by the union of
all resolvents accepted in that state's local pass.

This deliberately weak candidate ignores whether earlier learned clauses already
exclude an order. A state whose pass destroys all assignment-compatible orders
falsifies this raw cardinality measure; survival does not prove the historical
Formula-Caching invariant.
"""

from __future__ import annotations

from collections import Counter
from itertools import permutations

from janus_tear_gt_critical_order_damage import (
    clause_satisfied,
    order_assignment,
    pair_variables,
)
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf


def add_unit_events(assignment: dict[int, bool], events) -> dict[int, bool]:
    result = dict(assignment)
    for event in events:
        if event["kind"] != "unit":
            continue
        literal = int(event["literal"])
        variable = abs(literal)
        value = literal > 0
        assert variable not in result or result[variable] == value
        result[variable] = value
    return result


def compatible(assignment: dict[int, bool], total: dict[int, bool]) -> bool:
    return all(total[variable] == value for variable, value in assignment.items())


def state_assignments(policy: FCTracePolicy, root_call: int):
    result: dict[int, dict[int, bool]] = {}
    seen_calls: set[int] = set()

    def walk_call(call_id: int, incoming: dict[int, bool]) -> None:
        assert call_id not in seen_calls
        seen_calls.add(call_id)
        call = policy.calls[call_id]
        after_pre = add_unit_events(incoming, call.get("pre_units", []))

        if call["terminal"] == "CACHE_HIT":
            return
        if call["terminal"] != "STATE":
            return

        state_id = int(call["state"])
        assert state_id not in result
        result[state_id] = after_pre
        state = policy.states[state_id]
        after_post = add_unit_events(after_pre, state.get("post_units", []))

        for child in state.get("children", []):
            if child["call"] is None:
                continue
            variable = int(state["branch_var"])
            value = bool(child["value"])
            child_assignment = dict(after_post)
            assert variable not in child_assignment
            child_assignment[variable] = value
            walk_call(int(child["call"]), child_assignment)
            if child["result"]:
                break

    walk_call(root_call, {})
    assert len(seen_calls) == len(policy.calls)
    assert len(result) == len(policy.states)
    return result


def self_test() -> None:
    rows = []

    for n in range(4, 8):
        cnf, variable_count = graph_tautology_cnf(n)
        pairs = pair_variables(n)
        critical_assignments = [
            order_assignment(order, pairs)
            for order in permutations(range(n))
        ]

        policy = FCTracePolicy()
        result, root_call = policy.solve(cnf, variable_count)
        assert result.answer is False
        assert root_call is not None
        assert verify_fc_trace(cnf, variable_count, policy, root_call) is False
        assignments = state_assignments(policy, root_call)

        states_with_witnesses = 0
        states_without_witnesses_before_pass = 0
        states_fully_destroyed_by_pass = 0
        states_partially_damaged = 0
        maximum_damage_fraction = (0, 1)
        maximum_damage_state = None
        maximum_witnesses = 0
        total_compatible = 0
        total_union_damage = 0
        survivor_histogram: Counter[int] = Counter()
        assignment_size_histogram: Counter[int] = Counter()

        for state_id, state in policy.states.items():
            entry = assignments[state_id]
            assignment_size_histogram[len(entry)] += 1
            compatible_indices = [
                index
                for index, total in enumerate(critical_assignments)
                if compatible(entry, total)
            ]
            witness_count = len(compatible_indices)
            maximum_witnesses = max(maximum_witnesses, witness_count)
            total_compatible += witness_count

            if witness_count == 0:
                states_without_witnesses_before_pass += 1
                continue
            states_with_witnesses += 1

            events = state.get("resolution_events", [])
            damaged = {
                index
                for index in compatible_indices
                if any(
                    not clause_satisfied(tuple(event["resolvent"]), critical_assignments[index])
                    for event in events
                )
            }
            damage = len(damaged)
            survivors = witness_count - damage
            total_union_damage += damage
            survivor_histogram[survivors] += 1
            states_fully_destroyed_by_pass += survivors == 0
            states_partially_damaged += 0 < damage < witness_count

            if damage * maximum_damage_fraction[1] > maximum_damage_fraction[0] * witness_count:
                maximum_damage_fraction = (damage, witness_count)
                maximum_damage_state = state_id

        rows.append(
            (
                n,
                result.unique_states,
                result.cache_hits,
                states_with_witnesses,
                states_without_witnesses_before_pass,
                states_fully_destroyed_by_pass,
                states_partially_damaged,
                maximum_damage_fraction,
                maximum_damage_state,
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  unique_states = {result.unique_states}")
        print(f"  cache_hits = {result.cache_hits}")
        print(f"  states_with_assignment_compatible_orders = {states_with_witnesses}")
        print(
            "  states_without_assignment_compatible_orders_before_pass = "
            f"{states_without_witnesses_before_pass}"
        )
        print(f"  states_fully_destroyed_by_local_pass = {states_fully_destroyed_by_pass}")
        print(f"  states_partially_damaged = {states_partially_damaged}")
        print(
            "  maximum_union_damage_fraction = "
            f"{maximum_damage_fraction[0]}/{maximum_damage_fraction[1]}"
        )
        print(f"  maximum_damage_state = {maximum_damage_state}")
        print(f"  maximum_assignment_compatible_orders = {maximum_witnesses}")
        print(f"  total_assignment_compatible_order_occurrences = {total_compatible}")
        print(f"  total_union_damage_occurrences = {total_union_damage}")
        print(f"  assignment_size_histogram = {tuple(sorted(assignment_size_histogram.items()))}")
        print(f"  survivor_histogram = {tuple(sorted(survivor_histogram.items()))}")

    print("JANUS_GT_RESIDUAL_CRITICAL_DAMAGE = PASS")
    print(f"rows = {tuple(rows)}")
    print("candidate_measure = critical orders compatible with reconstructed entry assignment")
    print("claim_boundary = finite weak residual witness audit; prior learned-clause compatibility and historical invariant remain unmodeled")


if __name__ == "__main__":
    self_test()
