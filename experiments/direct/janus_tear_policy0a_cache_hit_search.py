#!/usr/bin/env python3
"""Search small CNFs for genuine exact-residual cache hits in Policy-0A."""

from __future__ import annotations

import random

from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import (
    Policy0A,
    canonical_cnf,
    visible_affine_root_decision,
)
from janus_tear_policy0t_random_translation_fuzz import clause_pool, is_unsat


def state_resolution_counts(policy: FCTracePolicy) -> tuple[int, int]:
    attempts = sum(int(state["resolution_attempts"]) for state in policy.states.values())
    additions = sum(int(state["resolution_additions"]) for state in policy.states.values())
    return attempts, additions


def audit_formula(cnf, variable_count: int):
    production = Policy0A().solve(cnf, variable_count)
    assert production.answer is False
    assert not production.cap_exceeded

    traced = FCTracePolicy()
    result, root_call = traced.solve(cnf, variable_count)
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, traced, root_call) is False
    attempts, additions = state_resolution_counts(traced)

    assert result.answer == production.answer
    assert result.unique_states == production.residual_states
    assert len(traced.completed_memo) == production.memo_entries
    assert attempts == production.resolution_attempts
    assert additions == production.resolution_additions
    return traced, result


def self_test() -> None:
    seed = 231131
    rng = random.Random(seed)
    compared = 0
    attempted = 0
    cache_formulas = 0
    maximum_cache_hits = 0
    maximum_saved_calls = 0
    first_cache_formula = None
    first_cache_contexts = None

    for variable_count, attempt_limit in ((4, 12000), (5, 28000)):
        pool = clause_pool(variable_count)
        local_attempts = 0
        while local_attempts < attempt_limit and compared < 600:
            local_attempts += 1
            attempted += 1
            clause_count = rng.randint(5, min(24, len(pool)))
            cnf = canonical_cnf(rng.sample(pool, clause_count))
            if not is_unsat(cnf, variable_count):
                continue
            affine_answer, _ = visible_affine_root_decision(cnf, variable_count)
            if affine_answer is not None:
                continue

            traced, result = audit_formula(cnf, variable_count)
            compared += 1
            if result.cache_hits:
                cache_formulas += 1
                maximum_cache_hits = max(maximum_cache_hits, result.cache_hits)
                maximum_saved_calls = max(
                    maximum_saved_calls,
                    result.calls - result.unique_states,
                )
                if first_cache_formula is None:
                    first_cache_formula = cnf
                    first_cache_contexts = tuple(
                        (
                            call["context"],
                            call["key"],
                            call["cache_target"],
                        )
                        for call in traced.calls.values()
                        if call.get("terminal") == "CACHE_HIT"
                    )

            if compared >= 600:
                break

    assert compared >= 400
    assert cache_formulas >= 1
    assert first_cache_formula is not None
    assert first_cache_contexts is not None

    print("JANUS_POLICY0A_CACHE_HIT_SEARCH = PASS")
    print(f"seed = {seed}")
    print(f"attempted_formulas = {attempted}")
    print(f"compared_nonaffine_unsat_formulas = {compared}")
    print(f"formulas_with_cache_hits = {cache_formulas}")
    print(f"maximum_cache_hits = {maximum_cache_hits}")
    print(f"maximum_calls_minus_unique_states = {maximum_saved_calls}")
    print(f"first_cache_formula = {first_cache_formula}")
    print(f"first_cache_contexts = {first_cache_contexts}")
    print("production_trace_equivalence = PASS")
    print("claim_boundary = finite search for exact residual reuse; no asymptotic speedup claimed")


if __name__ == "__main__":
    self_test()
