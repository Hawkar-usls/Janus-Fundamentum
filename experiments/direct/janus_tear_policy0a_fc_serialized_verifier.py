#!/usr/bin/env python3
"""Replay a serialized Policy-0A Formula-Caching certificate.

The checker receives only primitive call/state records.  It does not trust the
producer memo table and does not call verify_fc_trace.  Cache reuse is legal
only after the referenced exact residual has completed earlier in DFS order.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from janus_tear_policy0a_context_obstruction import cache_diamond_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    canonical_cnf,
    simplify_one,
    visible_affine_root_decision,
)
from janus_tear_policy0t_trace_certificate import (
    branch_variable,
    resolution_trace,
    unit_trace,
)


def serialize(policy: FCTracePolicy, root_call: int) -> dict[str, Any]:
    return {
        "root_call": root_call,
        "calls": deepcopy(policy.calls),
        "states": deepcopy(policy.states),
    }


def replay_serialized(root_cnf: CNF, variable_count: int, cert: dict[str, Any]) -> bool:
    root = canonical_cnf(root_cnf)
    affine_answer, _ = visible_affine_root_decision(root, variable_count)
    assert affine_answer is None

    calls = cert["calls"]
    states = cert["states"]
    assert isinstance(calls, dict)
    assert isinstance(states, dict)

    seen_calls: set[int] = set()
    seen_states: set[int] = set()
    completed: dict[CNF, tuple[bool, int]] = {}

    def verify_call(
        call_id: int,
        expected_input: CNF,
        depth: int,
        context: tuple[int, ...],
    ) -> bool:
        assert call_id in calls and call_id not in seen_calls
        seen_calls.add(call_id)
        call = calls[call_id]
        assert call["input"] == expected_input
        assert call["depth"] == depth
        assert call["context"] == context

        propagated, contradiction, pre_events = unit_trace(expected_input)
        assert call["pre_units"] == pre_events
        assert call["pre_result"] == propagated
        if contradiction:
            assert call["terminal"] == "PRE_UNIT_CONTRADICTION"
            assert call["result"] is False
            return False
        assert propagated is not None
        if not propagated:
            assert call["terminal"] == "SAT_EMPTY"
            assert call["result"] is True
            return True

        key = propagated
        assert call["key"] == key
        if call["terminal"] == "CACHE_HIT":
            assert key in completed
            answer, target = completed[key]
            assert call["cache_target"] == target
            assert call["result"] == answer
            return answer

        assert call["terminal"] == "STATE"
        state_id = int(call["state"])
        assert state_id in states and state_id not in seen_states
        seen_states.add(state_id)
        state = states[state_id]
        assert state["key"] == key
        assert state["entry_call"] == call_id
        assert state["depth"] == depth
        assert state["context"] == context

        saturated, refuted, attempts, additions, events = resolution_trace(
            key,
            int(state["width_limit"]),
            int(state["attempt_budget"]),
            int(state["addition_budget"]),
        )
        assert state["resolution_output"] == saturated
        assert state["resolution_refuted"] == refuted
        assert state["resolution_attempts"] == attempts
        assert state["resolution_additions"] == additions
        assert state["resolution_events"] == events

        if refuted:
            assert state["terminal"] == "RESOLUTION_CONTRADICTION"
            answer = False
        else:
            post, contradiction, post_events = unit_trace(saturated)
            assert state["post_units"] == post_events
            assert state["post_result"] == post
            if contradiction:
                assert state["terminal"] == "POST_UNIT_CONTRADICTION"
                answer = False
            else:
                assert post is not None
                if not post:
                    assert state["terminal"] == "SAT_EMPTY"
                    answer = True
                else:
                    variable = branch_variable(post)
                    assert state["branch_var"] == variable
                    children = state["children"]
                    assert isinstance(children, list)
                    answers: list[bool] = []
                    for child in children:
                        value = bool(child["value"])
                        literal = variable if value else -variable
                        assert child["literal"] == literal
                        child_cnf = simplify_one(post, variable, value)
                        if child_cnf is None:
                            assert child["direct_conflict"] is True
                            assert child["call"] is None
                            child_answer = False
                        else:
                            assert child["direct_conflict"] is False
                            child_answer = verify_call(
                                int(child["call"]),
                                child_cnf,
                                depth + 1,
                                context + (literal,),
                            )
                        assert child["result"] == child_answer
                        answers.append(child_answer)
                        if child_answer:
                            break
                    answer = any(answers)
                    assert state["terminal"] == (
                        "BRANCH_SAT" if answer else "BRANCH_UNSAT"
                    )

        assert state["result"] == answer
        assert call["result"] == answer
        completed[key] = (answer, state_id)
        return answer

    answer = verify_call(int(cert["root_call"]), root, 0, ())
    assert len(seen_calls) == len(calls)
    assert len(seen_states) == len(states)
    return answer


def rejected(root: CNF, variable_count: int, cert: dict[str, Any]) -> bool:
    try:
        replay_serialized(root, variable_count, cert)
    except (AssertionError, KeyError, TypeError, ValueError):
        return True
    return False


def self_test() -> None:
    cnf, variable_count = cache_diamond_cnf(1)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert result.cache_hits >= 1

    cert = serialize(policy, root_call)
    assert replay_serialized(cnf, variable_count, cert) is False

    cache_call_id = next(
        call_id
        for call_id, call in cert["calls"].items()
        if call.get("terminal") == "CACHE_HIT"
    )

    corrupt_target = deepcopy(cert)
    corrupt_target["calls"][cache_call_id]["cache_target"] = 10**9
    assert rejected(cnf, variable_count, corrupt_target)

    corrupt_result = deepcopy(cert)
    corrupt_result["calls"][cache_call_id]["result"] = True
    assert rejected(cnf, variable_count, corrupt_result)

    corrupt_key = deepcopy(cert)
    corrupt_key["calls"][cache_call_id]["key"] = ()
    assert rejected(cnf, variable_count, corrupt_key)

    corrupt_context = deepcopy(cert)
    corrupt_context["calls"][cache_call_id]["context"] = (999,)
    assert rejected(cnf, variable_count, corrupt_context)

    print("JANUS_POLICY0A_FC_SERIALIZED_VERIFIER = PASS")
    print(f"calls = {result.calls}")
    print(f"unique_states = {result.unique_states}")
    print(f"cache_hits = {result.cache_hits}")
    print("corrupt_cache_target_rejected = true")
    print("corrupt_cached_result_rejected = true")
    print("corrupt_residual_key_rejected = true")
    print("corrupt_context_rejected = true")
    print("claim_boundary = serialized exact-cache certificate only; no asymptotic proof-system comparison")


if __name__ == "__main__":
    self_test()
