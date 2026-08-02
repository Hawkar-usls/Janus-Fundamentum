#!/usr/bin/env python3
"""Emit and independently verify exact Formula-Caching traces for Policy-0A.

A cache hit is not treated as free Resolution DAG sharing.  The certificate
records a completed residual-CNF judgement and allows reuse only when the
canonical residual key is byte-for-byte identical and the referenced state was
completed earlier in the depth-first execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from janus_tear_policy0a_masked_tseitin import (
    CNF,
    Policy0A,
    canonical_cnf,
    simplify_one,
    visible_affine_root_decision,
)
from janus_tear_policy0t_trace_certificate import (
    branch_variable,
    resolution_trace,
    unit_trace,
)


@dataclass(frozen=True)
class FCResult:
    answer: bool | None
    affine_answer: bool | None
    affine_equations: int
    calls: int
    unique_states: int
    cache_hits: int
    maximum_depth: int


class FCTracePolicy:
    """Instrumented copy of the exact Policy-0A search core."""

    def __init__(self, state_cap: int | None = None) -> None:
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> tuple[FCResult, int | None]:
        self.calls: dict[int, dict[str, Any]] = {}
        self.states: dict[int, dict[str, Any]] = {}
        self.completed_memo: dict[CNF, tuple[bool, int]] = {}
        self.next_call_id = 0
        self.next_state_id = 0
        self.cache_hits = 0
        self.maximum_depth = 0
        self.unique_states = 0

        root = canonical_cnf(cnf)
        affine_answer, affine_equations = visible_affine_root_decision(
            root, variable_count
        )
        if affine_answer is not None:
            return (
                FCResult(
                    answer=affine_answer,
                    affine_answer=affine_answer,
                    affine_equations=affine_equations,
                    calls=0,
                    unique_states=0,
                    cache_hits=0,
                    maximum_depth=0,
                ),
                None,
            )

        try:
            answer, root_call = self.search(root, depth=0, context=())
        except RuntimeError:
            answer = None
            root_call = 0 if self.calls else None

        return (
            FCResult(
                answer=answer,
                affine_answer=None,
                affine_equations=affine_equations,
                calls=len(self.calls),
                unique_states=self.unique_states,
                cache_hits=self.cache_hits,
                maximum_depth=self.maximum_depth,
            ),
            root_call,
        )

    def new_call(self, payload: dict[str, Any]) -> int:
        call_id = self.next_call_id
        self.next_call_id += 1
        payload["id"] = call_id
        self.calls[call_id] = payload
        return call_id

    def search(
        self,
        cnf: CNF,
        depth: int,
        context: tuple[int, ...],
    ) -> tuple[bool, int]:
        self.maximum_depth = max(self.maximum_depth, depth)
        call_id = self.new_call(
            {
                "input": cnf,
                "depth": depth,
                "context": context,
            }
        )
        call = self.calls[call_id]

        propagated, contradiction, pre_events = unit_trace(cnf)
        call["pre_units"] = pre_events
        call["pre_result"] = propagated
        if contradiction:
            call["terminal"] = "PRE_UNIT_CONTRADICTION"
            call["result"] = False
            return False, call_id
        assert propagated is not None
        if not propagated:
            call["terminal"] = "SAT_EMPTY"
            call["result"] = True
            return True, call_id

        key = propagated
        call["key"] = key
        cached = self.completed_memo.get(key)
        if cached is not None:
            cached_answer, cached_state = cached
            self.cache_hits += 1
            call["terminal"] = "CACHE_HIT"
            call["cache_target"] = cached_state
            call["result"] = cached_answer
            return cached_answer, call_id

        state_id = self.next_state_id
        self.next_state_id += 1
        self.unique_states += 1
        if self.state_cap is not None and self.unique_states > self.state_cap:
            raise RuntimeError("state cap exceeded")
        call["state"] = state_id
        state: dict[str, Any] = {
            "id": state_id,
            "key": key,
            "entry_call": call_id,
            "depth": depth,
            "context": context,
        }
        self.states[state_id] = state

        literal_count = sum(len(clause) for clause in key)
        width_limit = max(map(len, key)) + 1
        attempt_budget = max(64, 4 * literal_count)
        addition_budget = max(8, len(key) // 4)
        saturated, refuted, attempts, additions, resolution_events = resolution_trace(
            key,
            width_limit,
            attempt_budget,
            addition_budget,
        )
        state.update(
            {
                "resolution_output": saturated,
                "resolution_refuted": refuted,
                "resolution_attempts": attempts,
                "resolution_additions": additions,
                "resolution_events": resolution_events,
                "width_limit": width_limit,
                "attempt_budget": attempt_budget,
                "addition_budget": addition_budget,
            }
        )

        if refuted:
            state["terminal"] = "RESOLUTION_CONTRADICTION"
            state["result"] = False
            self.completed_memo[key] = (False, state_id)
            call["terminal"] = "STATE"
            call["result"] = False
            return False, call_id

        post, contradiction, post_events = unit_trace(saturated)
        state["post_units"] = post_events
        state["post_result"] = post
        if contradiction:
            state["terminal"] = "POST_UNIT_CONTRADICTION"
            state["result"] = False
            self.completed_memo[key] = (False, state_id)
            call["terminal"] = "STATE"
            call["result"] = False
            return False, call_id
        assert post is not None
        if not post:
            state["terminal"] = "SAT_EMPTY"
            state["result"] = True
            self.completed_memo[key] = (True, state_id)
            call["terminal"] = "STATE"
            call["result"] = True
            return True, call_id

        variable = branch_variable(post)
        state["branch_var"] = variable
        children: list[dict[str, Any]] = []
        state["children"] = children
        answer = False
        for value in (False, True):
            literal = variable if value else -variable
            child_cnf = simplify_one(post, variable, value)
            if child_cnf is None:
                children.append(
                    {
                        "value": value,
                        "literal": literal,
                        "direct_conflict": True,
                        "call": None,
                        "result": False,
                    }
                )
                continue
            child_answer, child_call = self.search(
                child_cnf,
                depth + 1,
                context + (literal,),
            )
            children.append(
                {
                    "value": value,
                    "literal": literal,
                    "direct_conflict": False,
                    "call": child_call,
                    "result": child_answer,
                }
            )
            if child_answer:
                answer = True
                break

        state["terminal"] = "BRANCH_SAT" if answer else "BRANCH_UNSAT"
        state["result"] = answer
        self.completed_memo[key] = (answer, state_id)
        call["terminal"] = "STATE"
        call["result"] = answer
        return answer, call_id


def verify_fc_trace(
    root_cnf: CNF,
    variable_count: int,
    policy: FCTracePolicy,
    root_call: int,
) -> bool:
    """Replay the cache discipline without trusting the producer's memo table."""

    root = canonical_cnf(root_cnf)
    affine_answer, _ = visible_affine_root_decision(root, variable_count)
    assert affine_answer is None

    seen_calls: set[int] = set()
    seen_states: set[int] = set()
    completed: dict[CNF, tuple[bool, int]] = {}

    def verify_call(
        call_id: int,
        expected_input: CNF,
        expected_depth: int,
        expected_context: tuple[int, ...],
    ) -> bool:
        assert call_id not in seen_calls
        seen_calls.add(call_id)
        call = policy.calls[call_id]
        assert call["input"] == expected_input
        assert call["depth"] == expected_depth
        assert call["context"] == expected_context

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
        assert state_id not in seen_states
        seen_states.add(state_id)
        state = policy.states[state_id]
        assert state["key"] == key
        assert state["entry_call"] == call_id
        assert state["depth"] == expected_depth
        assert state["context"] == expected_context

        saturated, refuted, attempts, additions, resolution_events = resolution_trace(
            key,
            int(state["width_limit"]),
            int(state["attempt_budget"]),
            int(state["addition_budget"]),
        )
        assert state["resolution_output"] == saturated
        assert state["resolution_refuted"] == refuted
        assert state["resolution_attempts"] == attempts
        assert state["resolution_additions"] == additions
        assert state["resolution_events"] == resolution_events

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
                    child_answers: list[bool] = []
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
                                expected_depth + 1,
                                expected_context + (literal,),
                            )
                        assert child["result"] == child_answer
                        child_answers.append(child_answer)
                        if child_answer:
                            break
                    answer = any(child_answers)
                    assert state["terminal"] == (
                        "BRANCH_SAT" if answer else "BRANCH_UNSAT"
                    )

        assert state["result"] == answer
        completed[key] = (answer, state_id)
        assert call["result"] == answer
        return answer

    answer = verify_call(root_call, root, 0, ())
    assert len(seen_calls) == len(policy.calls)
    assert len(seen_states) == len(policy.states)
    return answer


def self_test() -> None:
    from janus_tear_policy0t_trace_certificate import N_VARS, UNSAT_FORMULA

    cnf = canonical_cnf(UNSAT_FORMULA)
    production = Policy0A().solve(cnf, N_VARS)
    traced = FCTracePolicy()
    result, root_call = traced.solve(cnf, N_VARS)
    assert root_call is not None
    assert verify_fc_trace(cnf, N_VARS, traced, root_call) is False
    assert production.answer == result.answer is False
    assert production.residual_states == result.unique_states

    print("JANUS_POLICY0A_FC_TRACE = PASS")
    print(f"calls = {result.calls}")
    print(f"unique_states = {result.unique_states}")
    print(f"cache_hits = {result.cache_hits}")
    print(f"maximum_depth = {result.maximum_depth}")
    print("root_answer = UNSAT")
    print("claim_boundary = exact finite FC trace calculus; no proof-system simulation claimed")


if __name__ == "__main__":
    self_test()
