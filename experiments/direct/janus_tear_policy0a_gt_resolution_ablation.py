#!/usr/bin/env python3
"""Compare exact caching on graph tautologies with and without local Resolution."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    Policy0A,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)


@dataclass(frozen=True)
class CacheOnlyResult:
    answer: bool | None
    cap_exceeded: bool
    calls: int
    unique_states: int
    cache_hits: int
    maximum_depth: int


class Policy0ACacheOnly:
    def __init__(self, state_cap: int | None = None):
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> CacheOnlyResult:
        affine_answer, _ = visible_affine_root_decision(cnf, variable_count)
        if affine_answer is not None:
            return CacheOnlyResult(affine_answer, False, 0, 0, 0, 0)

        self.calls = 0
        self.states = 0
        self.cache_hits = 0
        self.maximum_depth = 0
        self.memo: dict[CNF, bool] = {}
        try:
            answer = self.search(cnf, 0)
            return self.result(answer, False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> CacheOnlyResult:
        return CacheOnlyResult(
            answer,
            cap_exceeded,
            self.calls,
            self.states,
            self.cache_hits,
            self.maximum_depth,
        )

    def search(self, cnf: CNF, depth: int) -> bool:
        self.calls += 1
        self.maximum_depth = max(self.maximum_depth, depth)
        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            return False
        assert propagated is not None
        if not propagated:
            return True
        cnf = propagated

        if cnf in self.memo:
            self.cache_hits += 1
            return self.memo[cnf]

        self.states += 1
        if self.state_cap is not None and self.states > self.state_cap:
            raise RuntimeError("state cap exceeded")

        frequencies = Counter(
            abs(literal) for clause in cnf for literal in clause
        )
        maximum = max(frequencies.values())
        variable = min(
            candidate
            for candidate, frequency in frequencies.items()
            if frequency == maximum
        )

        for value in (False, True):
            child = simplify_one(cnf, variable, value)
            if child is not None and self.search(child, depth + 1):
                self.memo[cnf] = True
                return True

        self.memo[cnf] = False
        return False


def self_test() -> None:
    state_cap = 8192
    rows = []

    for n in range(3, 10):
        cnf, variable_count = graph_tautology_cnf(n)
        local = Policy0A(state_cap=state_cap).solve(cnf, variable_count)
        cache_only = Policy0ACacheOnly(state_cap=state_cap).solve(
            cnf, variable_count
        )

        assert local.answer in (False, None)
        assert cache_only.answer in (False, None)
        rows.append(
            (
                n,
                local.residual_states,
                cache_only.unique_states,
                cache_only.calls,
                cache_only.cache_hits,
                cache_only.maximum_depth,
                local.resolution_attempts,
                local.resolution_additions,
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  local_resolution_states = {local.residual_states}")
        print(f"  cache_only_states = {cache_only.unique_states}")
        print(f"  cache_only_calls = {cache_only.calls}")
        print(f"  cache_only_hits = {cache_only.cache_hits}")
        print(f"  cache_only_maximum_depth = {cache_only.maximum_depth}")
        print(f"  local_resolution_attempts = {local.resolution_attempts}")
        print(f"  local_resolution_additions = {local.resolution_additions}")
        print(f"  local_cap_exceeded = {str(local.cap_exceeded).lower()}")
        print(f"  cache_only_cap_exceeded = {str(cache_only.cap_exceeded).lower()}")

    print("JANUS_POLICY0A_GT_RESOLUTION_ABLATION = PASS")
    print(f"state_cap = {state_cap}")
    print(f"rows = {tuple(rows)}")
    print("claim_boundary = finite deterministic ablation; no asymptotic robustness theorem")


if __name__ == "__main__":
    self_test()
