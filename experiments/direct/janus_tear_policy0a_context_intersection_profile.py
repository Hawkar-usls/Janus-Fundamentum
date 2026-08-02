#!/usr/bin/env python3
"""Profile common decision boundaries of reused exact residual states.

For a context Delta, B(Delta) is the clause consisting of complements of its
decision literals.  A single context-independent conflict clause reusable at all
visits to one residual must be a subclause of the intersection of all B(Delta).
An empty intersection does not prove a Resolution lower bound, but it blocks the
naive strategy of attaching one nonempty decision-boundary clause to the cache
state.
"""

from __future__ import annotations

from collections import defaultdict

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_context_obstruction import cache_diamond_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES


def boundary(context: tuple[int, ...]) -> frozenset[int]:
    return frozenset(-literal for literal in context)


def profile(cnf, variable_count: int):
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    contexts_by_state: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    for state_id, state in policy.states.items():
        contexts_by_state[state_id].append(tuple(state["context"]))
    for call in policy.calls.values():
        if call.get("terminal") == "CACHE_HIT":
            contexts_by_state[int(call["cache_target"])].append(tuple(call["context"]))

    reused = {
        state_id: contexts
        for state_id, contexts in contexts_by_state.items()
        if len(contexts) >= 2
    }
    intersections: dict[int, frozenset[int]] = {}
    contradictory_pairs = 0
    for state_id, contexts in reused.items():
        common = boundary(contexts[0])
        for context in contexts[1:]:
            common = common & boundary(context)
        intersections[state_id] = common

        context_sets = [set(context) for context in contexts]
        if any(
            any(-literal in right for literal in left)
            for index, left in enumerate(context_sets)
            for right in context_sets[index + 1 :]
        ):
            contradictory_pairs += 1

    sizes = [len(common) for common in intersections.values()]
    return {
        "result": result,
        "reused_states": len(reused),
        "empty_intersections": sum(size == 0 for size in sizes),
        "minimum_intersection": min(sizes, default=0),
        "maximum_intersection": max(sizes, default=0),
        "total_intersection_literals": sum(sizes),
        "maximum_contexts_per_state": max((len(v) for v in reused.values()), default=0),
        "states_with_opposite_decision_contexts": contradictory_pairs,
    }


def self_test() -> None:
    diamond_cnf, diamond_vars = cache_diamond_cnf(1)
    diamond = profile(diamond_cnf, diamond_vars)
    assert diamond["reused_states"] >= 1
    assert diamond["empty_intersections"] >= 1

    maj3_cnf, maj3_vars = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    maj3 = profile(maj3_cnf, maj3_vars)
    result = maj3["result"]
    assert result.unique_states == 2427
    assert result.cache_hits == 888
    assert maj3["reused_states"] >= 1

    print("JANUS_POLICY0A_CONTEXT_INTERSECTION_PROFILE = PASS")
    print(f"diamond_reused_states = {diamond['reused_states']}")
    print(f"diamond_empty_intersections = {diamond['empty_intersections']}")
    print(f"maj3_unique_states = {result.unique_states}")
    print(f"maj3_cache_hits = {result.cache_hits}")
    print(f"maj3_reused_states = {maj3['reused_states']}")
    print(f"maj3_empty_intersections = {maj3['empty_intersections']}")
    print(f"maj3_minimum_common_boundary = {maj3['minimum_intersection']}")
    print(f"maj3_maximum_common_boundary = {maj3['maximum_intersection']}")
    print(f"maj3_total_common_boundary_literals = {maj3['total_intersection_literals']}")
    print(f"maj3_maximum_contexts_per_state = {maj3['maximum_contexts_per_state']}")
    print(
        "maj3_states_with_opposite_decision_contexts = "
        f"{maj3['states_with_opposite_decision_contexts']}"
    )
    print("claim_boundary = context-clause obstruction only; no Resolution or FC lower bound")


if __name__ == "__main__":
    self_test()
