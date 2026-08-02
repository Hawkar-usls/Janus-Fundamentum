#!/usr/bin/env python3
"""Search ordinary small CNFs for exact-residual cache hits in Policy-0A.

This is a rarity audit, not the constructive cache-diamond witness.  The latter
lives in janus_tear_policy0a_context_obstruction.py.
"""

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
    attempted = 0
    compared_total = 0
    cache_formulas = 0
    maximum_cache_hits = 0
    first_cache_formula = None
    per_dimension: list[tuple[int, int, int]] = []

    for variable_count, target, attempt_limit in ((4, 600, 12000), (5, 600, 30000)):
        pool = clause_pool(variable_count)
        compared = 0
        local_attempts = 0
        while local_attempts < attempt_limit and compared < target:
            local_attempts += 1
            attempted += 1
            clause_count = rng.randint(5, min(24, len(pool)))
            cnf = canonical_cnf(rng.sample(pool, clause_count))
            if not is_unsat(cnf, variable_count):
                continue
            affine_answer, _ = visible_affine_root_decision(cnf, variable_count)
            if affine_answer is not None:
                continue

            _, result = audit_formula(cnf, variable_count)
            compared += 1
            compared_total += 1
            if result.cache_hits:
                cache_formulas += 1
                maximum_cache_hits = max(maximum_cache_hits, result.cache_hits)
                if first_cache_formula is None:
                    first_cache_formula = cnf

        assert compared >= min(400, target)
        per_dimension.append((variable_count, compared, local_attempts))

    print("JANUS_POLICY0A_CACHE_HIT_SEARCH = PASS")
    print(f"seed = {seed}")
    print(f"attempted_formulas = {attempted}")
    print(f"compared_nonaffine_unsat_formulas = {compared_total}")
    print(f"per_dimension = {tuple(per_dimension)}")
    print(f"formulas_with_cache_hits = {cache_formulas}")
    print(f"maximum_cache_hits = {maximum_cache_hits}")
    print(f"first_cache_formula = {first_cache_formula}")
    print("production_trace_equivalence = PASS")
    print(
        "claim_boundary = random small-CNF rarity audit; explicit cache reuse is tested by the diamond family"
    )


if __name__ == "__main__":
    self_test()
