#!/usr/bin/env python3
"""Construct an explicit exact-cache diamond family for Policy-0A.

Each selector x_i owns many private width-three clauses C.  The formula contains
C, (x_i OR C), and (not x_i OR C).  Either selector value therefore produces the
same canonical residual because C is already present.  Private variables keep
selector frequency dominant, while disjoint width-three clauses make cross
resolvents width six and therefore too wide for the policy's width-five pass.

A fixed non-affine UNSAT core is appended after the selectors.  Policy-0T must
solve both identical children at every selector; Policy-0A solves the first and
hits the exact residual cache on the second.
"""

from __future__ import annotations

from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import Policy0A, canonical_cnf
from janus_tear_policy0t_no_cache import Policy0T
from janus_tear_policy0t_trace_certificate import N_VARS, UNSAT_FORMULA


def shift_clause(clause: tuple[int, ...], offset: int) -> tuple[int, ...]:
    return tuple(
        literal + offset if literal > 0 else literal - offset
        for literal in clause
    )


def cache_diamond_cnf(
    selector_count: int,
    clauses_per_selector: int = 64,
):
    if selector_count < 0:
        raise ValueError("selector_count must be nonnegative")
    if clauses_per_selector < 16:
        raise ValueError("clauses_per_selector must dominate the fixed core")

    clauses: list[tuple[int, ...]] = [
        shift_clause(clause, selector_count) for clause in UNSAT_FORMULA
    ]
    next_variable = selector_count + N_VARS + 1

    for selector in range(1, selector_count + 1):
        for _ in range(clauses_per_selector):
            private_clause = (
                next_variable,
                next_variable + 1,
                next_variable + 2,
            )
            next_variable += 3
            clauses.append(private_clause)
            clauses.append((selector,) + private_clause)
            clauses.append((-selector,) + private_clause)

    return canonical_cnf(clauses), next_variable - 1


def decision_boundary(context: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sorted((-literal for literal in context), key=lambda x: (abs(x), x < 0)))


def audit_case(selector_count: int):
    cnf, variable_count = cache_diamond_cnf(selector_count)

    cached = Policy0A().solve(cnf, variable_count)
    tree = Policy0T().solve(cnf, variable_count)
    traced = FCTracePolicy()
    trace_result, root_call = traced.solve(cnf, variable_count)

    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, traced, root_call) is False
    assert cached.answer is False
    assert tree.answer is False
    assert trace_result.answer is False
    assert not cached.cap_exceeded
    assert not tree.cap_exceeded
    assert cached.residual_states == trace_result.unique_states

    expected_tree_calls = 2 ** (selector_count + 2) - 1
    expected_cache_states = selector_count + 1
    expected_trace_calls = 2 * selector_count + 3
    assert tree.recursive_calls == expected_tree_calls
    assert cached.residual_states == expected_cache_states
    assert trace_result.unique_states == expected_cache_states
    assert trace_result.calls == expected_trace_calls
    assert trace_result.cache_hits == selector_count

    return cnf, variable_count, cached, tree, traced, trace_result


def self_test() -> None:
    rows = []
    for selector_count in range(0, 9):
        cnf, variable_count, cached, tree, traced, trace_result = audit_case(
            selector_count
        )
        rows.append(
            (
                selector_count,
                variable_count,
                len(cnf),
                tree.recursive_calls,
                cached.residual_states,
                trace_result.cache_hits,
            )
        )
        print(f"SELECTORS = {selector_count}")
        print(f"  variables = {variable_count}")
        print(f"  clauses = {len(cnf)}")
        print(f"  no_cache_recursive_calls = {tree.recursive_calls}")
        print(f"  cached_unique_states = {cached.residual_states}")
        print(f"  exact_cache_hits = {trace_result.cache_hits}")

    _, _, _, _, one_trace, _ = audit_case(1)
    cache_calls = [
        call
        for call in one_trace.calls.values()
        if call.get("terminal") == "CACHE_HIT"
    ]
    assert len(cache_calls) == 1
    cache_call = cache_calls[0]
    target_state = one_trace.states[int(cache_call["cache_target"])]
    first_context = tuple(target_state["context"])
    second_context = tuple(cache_call["context"])
    assert first_context == (-1,)
    assert second_context == (1,)
    assert target_state["key"] == cache_call["key"]

    first_boundary = decision_boundary(first_context)
    second_boundary = decision_boundary(second_context)
    assert first_boundary == (1,)
    assert second_boundary == (-1,)
    assert first_boundary != second_boundary

    print("JANUS_POLICY0A_CONTEXT_OBSTRUCTION = PASS")
    print("tree_calls_formula = 2^(selectors+2)-1")
    print("cached_states_formula = selectors+1")
    print("trace_calls_formula = 2*selectors+3")
    print(f"first_context = {first_context}")
    print(f"second_context = {second_context}")
    print(f"first_decision_boundary = {first_boundary}")
    print(f"second_decision_boundary = {second_boundary}")
    print("same_residual_key = true")
    print("single_context_clause_reuse = false")
    print(
        "claim_boundary = explicit syntactic diamond separation between exact cache and no-cache policies; not a general SAT speedup"
    )


if __name__ == "__main__":
    self_test()
