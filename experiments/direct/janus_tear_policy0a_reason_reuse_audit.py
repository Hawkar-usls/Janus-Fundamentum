#!/usr/bin/env python3
"""Audit whether C022 conflict clauses can be reused across Policy-0A cache hits.

The exact Formula-Caching DAG for MAJ3-K4 is unfolded into an ordinary tree by
replacing each cache hit with a fresh copy of the referenced completed state.
The C022 trace-to-Resolution translator then emits a conflict clause for every
UNSAT occurrence.  Occurrences originating from the same cache state are grouped
and tested for a common emitted reason valid under all their decision contexts.

This is a finite reason-reuse audit.  It does not prove a simulation or a lower
bound for Formula Caching.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_tear_policy0t_recursive_trace_translator import TraceTranslator


def decision_boundary(context: tuple[int, ...]) -> frozenset[int]:
    return frozenset(-literal for literal in context)


def unfold_fc_calls(policy: FCTracePolicy, root_call: int):
    nodes: dict[int, dict[str, object]] = {}
    source_state: dict[int, int | None] = {}
    contexts: dict[int, tuple[int, ...]] = {}
    next_node = 0

    def clone_call(
        call_id: int,
        context: tuple[int, ...],
        depth: int,
    ) -> int:
        nonlocal next_node
        call = policy.calls[call_id]
        node_id = next_node
        next_node += 1
        node: dict[str, object] = {
            "id": node_id,
            "input": call["input"],
            "depth": depth,
            "pre_units": call["pre_units"],
            "pre_result": call["pre_result"],
        }
        nodes[node_id] = node
        contexts[node_id] = context

        terminal = call["terminal"]
        if terminal == "PRE_UNIT_CONTRADICTION":
            node["terminal"] = "UNIT_CONTRADICTION"
            node["result"] = False
            source_state[node_id] = None
            return node_id
        if terminal == "SAT_EMPTY":
            node["terminal"] = "SAT_EMPTY"
            node["result"] = True
            source_state[node_id] = None
            return node_id

        if terminal == "CACHE_HIT":
            state_id = int(call["cache_target"])
        else:
            assert terminal == "STATE"
            state_id = int(call["state"])
        source_state[node_id] = state_id
        state = policy.states[state_id]

        for field in (
            "resolution_output",
            "resolution_refuted",
            "resolution_attempts",
            "resolution_additions",
            "resolution_events",
            "width_limit",
            "attempt_budget",
            "addition_budget",
        ):
            node[field] = state[field]

        if state["resolution_refuted"]:
            node["terminal"] = "RESOLUTION_CONTRADICTION"
            node["result"] = False
            return node_id

        node["post_units"] = state["post_units"]
        node["post_result"] = state["post_result"]
        if state["terminal"] == "POST_UNIT_CONTRADICTION":
            node["terminal"] = "POST_UNIT_CONTRADICTION"
            node["result"] = False
            return node_id
        if state["terminal"] == "SAT_EMPTY":
            node["terminal"] = "SAT_EMPTY"
            node["result"] = True
            return node_id

        variable = int(state["branch_var"])
        node["branch_var"] = variable
        children: list[dict[str, Any]] = []
        node["children"] = children
        for child in state["children"]:
            value = bool(child["value"])
            literal = variable if value else -variable
            if child["call"] is None:
                children.append(
                    {
                        "value": value,
                        "child": None,
                        "result": False,
                        "direct_conflict": True,
                    }
                )
            else:
                child_node = clone_call(
                    int(child["call"]),
                    context + (literal,),
                    depth + 1,
                )
                children.append(
                    {
                        "value": value,
                        "child": child_node,
                        "result": bool(child["result"]),
                        "direct_conflict": False,
                    }
                )
            if child["result"]:
                break

        node["terminal"] = state["terminal"]
        node["result"] = state["result"]
        return node_id

    root_node = clone_call(root_call, (), 0)
    return nodes, root_node, source_state, contexts


class RecordingTranslator(TraceTranslator):
    def __init__(self, root, nodes):
        super().__init__(root, nodes)
        self.return_lines: dict[int, int | None] = {}
        self.return_answers: dict[int, bool] = {}

    def translate_node(self, node_id, records, assignment):
        answer, line = super().translate_node(node_id, records, assignment)
        self.return_answers[node_id] = answer
        self.return_lines[node_id] = line
        return answer, line


def self_test() -> None:
    cnf, variable_count = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert result.unique_states == 2427
    assert result.cache_hits == 888
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    nodes, root_node, source_state, contexts = unfold_fc_calls(policy, root_call)
    assert len(nodes) == 15671

    translator = RecordingTranslator(cnf, nodes)
    final_line = translator.translate(root_node)
    axiom_lines, resolution_lines, maximum_width, proof_depth = (
        translator.proof.verify(cnf)
    )
    assert translator.proof.clause(final_line) == ()
    assert len(translator.return_lines) == len(nodes)

    occurrences: dict[int, list[int]] = defaultdict(list)
    for node_id, state_id in source_state.items():
        if state_id is not None:
            occurrences[state_id].append(node_id)

    reused = {state: ids for state, ids in occurrences.items() if len(ids) >= 2}
    states_with_one_emitted_reason = 0
    states_with_some_globally_reusable_emitted_reason = 0
    states_with_empty_common_boundary = 0
    maximum_distinct_reasons = 0
    total_occurrences = 0

    for state_id, node_ids in reused.items():
        total_occurrences += len(node_ids)
        clauses = []
        boundaries = []
        for node_id in node_ids:
            assert translator.return_answers[node_id] is False
            line = translator.return_lines[node_id]
            assert line is not None
            clause = translator.proof.clause(line)
            current_boundary = decision_boundary(contexts[node_id])
            assert set(clause) <= current_boundary
            clauses.append(clause)
            boundaries.append(current_boundary)

        distinct = set(clauses)
        maximum_distinct_reasons = max(maximum_distinct_reasons, len(distinct))
        if len(distinct) == 1:
            states_with_one_emitted_reason += 1

        common = boundaries[0]
        for current in boundaries[1:]:
            common = common & current
        if not common:
            states_with_empty_common_boundary += 1

        if any(set(clause) <= common for clause in distinct):
            states_with_some_globally_reusable_emitted_reason += 1

    assert len(reused) == 438
    assert states_with_empty_common_boundary == 4

    print("JANUS_POLICY0A_REASON_REUSE_AUDIT = PASS")
    print(f"fc_unique_states = {result.unique_states}")
    print(f"fc_cache_hits = {result.cache_hits}")
    print(f"unfolded_trace_nodes = {len(nodes)}")
    print(f"resolution_axiom_lines = {axiom_lines}")
    print(f"resolution_derived_lines = {resolution_lines}")
    print(f"resolution_proof_lines = {len(translator.proof.lines)}")
    print(f"resolution_maximum_width = {maximum_width}")
    print(f"resolution_proof_depth = {proof_depth}")
    print(f"reused_cache_states = {len(reused)}")
    print(f"reused_state_occurrences = {total_occurrences}")
    print(f"states_with_identical_emitted_reason = {states_with_one_emitted_reason}")
    print(
        "states_with_some_reusable_emitted_reason = "
        f"{states_with_some_globally_reusable_emitted_reason}"
    )
    print(f"states_with_empty_common_boundary = {states_with_empty_common_boundary}")
    print(f"maximum_distinct_emitted_reasons_per_state = {maximum_distinct_reasons}")
    print("claim_boundary = finite C022-reason reuse audit; no general FC-to-Resolution simulation")


if __name__ == "__main__":
    self_test()
