#!/usr/bin/env python3
"""Audit JANUS-FC_local as an explicit residual-judgement DAG.

The certificate is not identified with Resolution.  It consists of unique exact
residual states, ordinary recursive calls, branch edges, local proof events and
cache edges to states completed earlier in depth-first order.

The audit also computes, by dynamic programming, how many recursive call
occurrences would be present if every cache edge were unfolded into another copy
of the referenced completed state.  This measures memoization compression of the
*same execution calculus*; it is not a proof-system separation.
"""

from __future__ import annotations

from dataclasses import dataclass

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_context_obstruction import cache_diamond_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import CNF, K4_EDGES


@dataclass(frozen=True)
class FCMetrics:
    calls: int
    unique_states: int
    cache_edges: int
    branch_edges: int
    unit_events: int
    resolution_events: int
    certificate_records: int
    unfolded_call_occurrences: int
    completion_order: tuple[int, ...]


def audit_fc_dag(cnf: CNF, variable_count: int) -> FCMetrics:
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    completion_order: list[int] = []
    completed: set[int] = set()
    seen_calls: set[int] = set()
    seen_states: set[int] = set()

    def walk_call(call_id: int) -> None:
        assert call_id not in seen_calls
        seen_calls.add(call_id)
        call = policy.calls[call_id]
        terminal = call["terminal"]
        if terminal == "CACHE_HIT":
            target = int(call["cache_target"])
            assert target in completed
            return
        if terminal != "STATE":
            return

        state_id = int(call["state"])
        assert state_id not in seen_states
        seen_states.add(state_id)
        state = policy.states[state_id]
        for child in state.get("children", []):
            if child["call"] is not None:
                walk_call(int(child["call"]))
            if child["result"]:
                break
        completed.add(state_id)
        completion_order.append(state_id)

    walk_call(root_call)
    assert len(seen_calls) == len(policy.calls)
    assert len(seen_states) == len(policy.states)
    assert set(completion_order) == set(policy.states)

    state_cost: dict[int, int] = {}

    def unfold_state(state_id: int) -> int:
        if state_id in state_cost:
            return state_cost[state_id]
        state = policy.states[state_id]
        total = 1
        for child in state.get("children", []):
            if child["call"] is not None:
                total += unfold_call(int(child["call"]))
            if child["result"]:
                break
        state_cost[state_id] = total
        return total

    def unfold_call(call_id: int) -> int:
        call = policy.calls[call_id]
        if call["terminal"] == "CACHE_HIT":
            return unfold_state(int(call["cache_target"]))
        if call["terminal"] == "STATE":
            return unfold_state(int(call["state"]))
        return 1

    unfolded = unfold_call(root_call)

    branch_edges = sum(
        1
        for state in policy.states.values()
        for child in state.get("children", [])
        if child["call"] is not None
    )
    unit_events = sum(
        len(call.get("pre_units", [])) for call in policy.calls.values()
    ) + sum(
        len(state.get("post_units", [])) for state in policy.states.values()
    )
    resolution_events = sum(
        len(state.get("resolution_events", [])) for state in policy.states.values()
    )
    certificate_records = (
        len(policy.calls)
        + len(policy.states)
        + branch_edges
        + unit_events
        + resolution_events
    )

    return FCMetrics(
        calls=len(policy.calls),
        unique_states=len(policy.states),
        cache_edges=result.cache_hits,
        branch_edges=branch_edges,
        unit_events=unit_events,
        resolution_events=resolution_events,
        certificate_records=certificate_records,
        unfolded_call_occurrences=unfolded,
        completion_order=tuple(completion_order),
    )


def self_test() -> None:
    diamond_rows = []
    for selectors in range(0, 8):
        cnf, variable_count = cache_diamond_cnf(selectors)
        metrics = audit_fc_dag(cnf, variable_count)
        assert metrics.cache_edges >= selectors
        assert metrics.unfolded_call_occurrences >= 2 ** (selectors + 1) - 1
        assert metrics.calls <= 4 * selectors + 64
        diamond_rows.append(
            (
                selectors,
                metrics.calls,
                metrics.unique_states,
                metrics.cache_edges,
                metrics.unfolded_call_occurrences,
                metrics.certificate_records,
            )
        )

    maj3_cnf, maj3_variables = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    maj3 = audit_fc_dag(maj3_cnf, maj3_variables)
    assert maj3.calls == 4117
    assert maj3.unique_states == 2427
    assert maj3.cache_edges == 888
    assert maj3.unfolded_call_occurrences >= maj3.calls

    print("JANUS_FC_LOCAL_DAG_AUDIT = PASS")
    print(f"diamond_rows = {tuple(diamond_rows)}")
    print(f"maj3_calls = {maj3.calls}")
    print(f"maj3_unique_states = {maj3.unique_states}")
    print(f"maj3_cache_edges = {maj3.cache_edges}")
    print(f"maj3_branch_edges = {maj3.branch_edges}")
    print(f"maj3_unit_events = {maj3.unit_events}")
    print(f"maj3_resolution_events = {maj3.resolution_events}")
    print(f"maj3_certificate_records = {maj3.certificate_records}")
    print(f"maj3_unfolded_call_occurrences = {maj3.unfolded_call_occurrences}")
    print(f"maj3_completion_states = {len(maj3.completion_order)}")
    print("all_cache_targets_previously_completed = true")
    print("claim_boundary = exact execution-DAG compression; not a Resolution or Formula-Caching lower bound")


if __name__ == "__main__":
    self_test()
