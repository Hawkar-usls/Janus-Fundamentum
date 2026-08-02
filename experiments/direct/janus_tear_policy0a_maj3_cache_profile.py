#!/usr/bin/env python3
"""Profile exact Formula Caching on the structured MAJ3-lifted K4 fixture."""

from __future__ import annotations

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES, Policy0A
from janus_tear_policy0t_no_cache import Policy0T


def self_test() -> None:
    cnf, variable_count = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    quadratic_cap = 4 * variable_count * variable_count

    production = Policy0A().solve(cnf, variable_count)
    assert production.answer is False
    assert not production.cap_exceeded
    assert production.residual_states == 2427
    assert production.residual_states > quadratic_cap

    traced = FCTracePolicy()
    trace_result, root_call = traced.solve(cnf, variable_count)
    assert root_call is not None
    assert trace_result.answer is False
    assert trace_result.unique_states == production.residual_states
    assert trace_result.calls == 4117
    assert trace_result.cache_hits == 888
    assert verify_fc_trace(cnf, variable_count, traced, root_call) is False

    no_cache = Policy0T(occurrence_cap=quadratic_cap).solve(cnf, variable_count)
    assert no_cache.answer is None
    assert no_cache.cap_exceeded
    assert no_cache.recursive_calls == quadratic_cap + 1

    print("JANUS_POLICY0A_MAJ3_CACHE_PROFILE = PASS")
    print(f"variables = {variable_count}")
    print(f"clauses = {len(cnf)}")
    print(f"quadratic_cap = {quadratic_cap}")
    print(f"cached_recursive_calls = {trace_result.calls}")
    print(f"cached_unique_states = {trace_result.unique_states}")
    print(f"exact_cache_hits = {trace_result.cache_hits}")
    print(f"maximum_depth = {trace_result.maximum_depth}")
    print(f"no_cache_cap_crossing_call = {no_cache.recursive_calls}")
    print("serialized_semantics = exact residual equality after unit propagation")
    print("quadratic_unique_state_envelope_survives = false")
    print("claim_boundary = finite structured profile; no asymptotic lower bound for Formula Caching")


if __name__ == "__main__":
    self_test()
