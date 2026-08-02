#!/usr/bin/env python3
"""Corrected MAJ3 cache-reason audit.

Direct cache targets and states repeated only because an ancestor cache target is
unfolded are counted separately.  Conflict clauses are compared against both the
decision-only boundary and the full entry assignment, including inherited unit
consequences.
"""

from __future__ import annotations

from collections import defaultdict

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_tear_policy0a_reason_reuse_audit import (
    RecordingTranslator,
    assignment_boundary,
    decision_boundary,
    intersect,
    unfold_fc_calls,
)


def direct_reuse_count(policy: FCTracePolicy) -> int:
    contexts: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for state_id, state in policy.states.items():
        contexts[state_id].append(tuple(state["context"]))
    for call in policy.calls.values():
        if call.get("terminal") == "CACHE_HIT":
            contexts[int(call["cache_target"])].append(tuple(call["context"]))
    return sum(len(items) >= 2 for items in contexts.values())


def self_test() -> None:
    cnf, variable_count = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert result.unique_states == 2427
    assert result.cache_hits == 888
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    direct_reused_states = direct_reuse_count(policy)
    assert direct_reused_states == 438

    nodes, root_node, source_state, contexts = unfold_fc_calls(policy, root_call)
    assert len(nodes) == 15671

    translator = RecordingTranslator(cnf, nodes)
    final_line = translator.translate(root_node)
    axiom_lines, resolution_lines, maximum_width, proof_depth = (
        translator.proof.verify(cnf)
    )
    assert translator.proof.clause(final_line) == ()

    occurrences: dict[int, list[int]] = defaultdict(list)
    for node_id, state_id in source_state.items():
        if state_id is not None:
            occurrences[state_id].append(node_id)
    reused = {state: ids for state, ids in occurrences.items() if len(ids) >= 2}

    identical_reasons = 0
    reusable_full_reasons = 0
    reusable_decision_reasons = 0
    empty_full_boundaries = 0
    empty_decision_boundaries = 0
    inherited_unit_occurrences = 0
    maximum_distinct_reasons = 0
    total_occurrences = 0

    for node_ids in reused.values():
        total_occurrences += len(node_ids)
        clauses = []
        full_boundaries = []
        decision_boundaries = []

        for node_id in node_ids:
            assert translator.return_answers[node_id] is False
            line = translator.return_lines[node_id]
            assert line is not None
            clause = translator.proof.clause(line)
            full_boundary = assignment_boundary(
                translator.entry_assignments[node_id]
            )
            decisions = decision_boundary(contexts[node_id])
            assert set(clause) <= full_boundary
            if not set(clause) <= decisions:
                inherited_unit_occurrences += 1
            clauses.append(clause)
            full_boundaries.append(full_boundary)
            decision_boundaries.append(decisions)

        distinct = set(clauses)
        maximum_distinct_reasons = max(maximum_distinct_reasons, len(distinct))
        if len(distinct) == 1:
            identical_reasons += 1

        common_full = intersect(full_boundaries)
        common_decisions = intersect(decision_boundaries)
        empty_full_boundaries += not common_full
        empty_decision_boundaries += not common_decisions
        reusable_full_reasons += any(
            set(clause) <= common_full for clause in distinct
        )
        reusable_decision_reasons += any(
            set(clause) <= common_decisions for clause in distinct
        )

    assert len(reused) >= direct_reused_states

    print("JANUS_POLICY0A_REASON_REUSE_AUDIT_V2 = PASS")
    print(f"fc_unique_states = {result.unique_states}")
    print(f"fc_cache_hits = {result.cache_hits}")
    print(f"direct_reused_cache_states = {direct_reused_states}")
    print(f"unfolded_reused_states = {len(reused)}")
    print(f"unfolded_reused_state_occurrences = {total_occurrences}")
    print(f"unfolded_trace_nodes = {len(nodes)}")
    print(f"resolution_axiom_lines = {axiom_lines}")
    print(f"resolution_derived_lines = {resolution_lines}")
    print(f"resolution_proof_lines = {len(translator.proof.lines)}")
    print(f"resolution_maximum_width = {maximum_width}")
    print(f"resolution_proof_depth = {proof_depth}")
    print(f"states_with_identical_emitted_reason = {identical_reasons}")
    print(f"states_with_reusable_full_reason = {reusable_full_reasons}")
    print(f"states_with_reusable_decision_reason = {reusable_decision_reasons}")
    print(f"states_with_empty_full_boundary = {empty_full_boundaries}")
    print(f"states_with_empty_decision_boundary = {empty_decision_boundaries}")
    print(f"occurrences_using_inherited_unit_literals = {inherited_unit_occurrences}")
    print(f"maximum_distinct_emitted_reasons_per_state = {maximum_distinct_reasons}")
    print("claim_boundary = finite C022 reason-reuse audit; no general FC-to-Resolution simulation")


if __name__ == "__main__":
    self_test()
