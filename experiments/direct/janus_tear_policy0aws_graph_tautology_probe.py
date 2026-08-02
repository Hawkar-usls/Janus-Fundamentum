#!/usr/bin/env python3
"""Probe Policy-0A augmented with Formula-Caching Weakening/Subsumption.

A cached UNSAT residual G prunes the current residual F when every clause of G
contains some clause of F.  This is the FCWS cache test: F is at least as strong
as G clause-by-clause.  The solver otherwise keeps Policy-0A's unit propagation,
one-pass budgeted local Resolution and deterministic branching.

The lookup work is charged explicitly.  This finite audit does not transfer the
known FCWS graph-tautology lower bound because the local Resolution pass is an
additional inference resource.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from janus_tear_policy0a_graph_tautology_probe import graph_tautology_cnf
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    Policy0A,
    limited_resolution,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)


@dataclass(frozen=True)
class WSResult:
    answer: bool | None
    cap_exceeded: bool
    unique_states: int
    cache_entries: int
    exact_hits: int
    ws_hits: int
    cache_formula_comparisons: int
    clause_pair_checks: int
    resolution_attempts: int
    resolution_additions: int


class Policy0AWS:
    def __init__(self, state_cap: int | None = None):
        self.state_cap = state_cap

    def solve(self, cnf: CNF, variable_count: int) -> WSResult:
        affine_answer, _ = visible_affine_root_decision(cnf, variable_count)
        if affine_answer is not None:
            return WSResult(
                affine_answer, False, 0, 0, 0, 0, 0, 0, 0, 0
            )

        self.states = 0
        self.cache: list[CNF] = []
        self.exact_index: set[CNF] = set()
        self.exact_hits = 0
        self.ws_hits = 0
        self.formula_comparisons = 0
        self.clause_pair_checks = 0
        self.resolution_attempts = 0
        self.resolution_additions = 0

        try:
            answer = self.search(cnf)
            return self.result(answer, False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> WSResult:
        return WSResult(
            answer=answer,
            cap_exceeded=cap_exceeded,
            unique_states=self.states,
            cache_entries=len(self.cache),
            exact_hits=self.exact_hits,
            ws_hits=self.ws_hits,
            cache_formula_comparisons=self.formula_comparisons,
            clause_pair_checks=self.clause_pair_checks,
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
        )

    def stronger_than_cached(self, current: CNF, cached: CNF) -> bool:
        current_sets = [set(clause) for clause in current]
        for cached_clause in cached:
            cached_set = set(cached_clause)
            found = False
            for current_set in current_sets:
                self.clause_pair_checks += 1
                if current_set <= cached_set:
                    found = True
                    break
            if not found:
                return False
        return True

    def cache_hit(self, cnf: CNF) -> bool:
        if cnf in self.exact_index:
            self.exact_hits += 1
            return True

        # Smaller cached formulas are cheaper and more likely to be dominated.
        for cached in sorted(self.cache, key=lambda item: (len(item), item)):
            self.formula_comparisons += 1
            if self.stronger_than_cached(cnf, cached):
                self.ws_hits += 1
                return True
        return False

    def store_unsat(self, cnf: CNF) -> None:
        if cnf not in self.exact_index:
            self.exact_index.add(cnf)
            self.cache.append(cnf)

    def search(self, cnf: CNF) -> bool:
        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            return False
        assert propagated is not None
        if not propagated:
            return True
        cnf = propagated

        if self.cache_hit(cnf):
            return False

        self.states += 1
        if self.state_cap is not None and self.states > self.state_cap:
            raise RuntimeError("state cap exceeded")

        literal_count = sum(len(clause) for clause in cnf)
        width_limit = max(len(clause) for clause in cnf) + 1
        saturated, refuted, attempts, additions = limited_resolution(
            cnf,
            max_width=width_limit,
            attempt_budget=max(64, 4 * literal_count),
            addition_budget=max(8, len(cnf) // 4),
        )
        self.resolution_attempts += attempts
        self.resolution_additions += additions

        if refuted:
            self.store_unsat(cnf)
            return False

        propagated, contradiction = unit_propagate(saturated)
        if contradiction:
            self.store_unsat(cnf)
            return False
        assert propagated is not None
        if not propagated:
            return True

        frequencies = Counter(
            abs(literal) for clause in propagated for literal in clause
        )
        maximum = max(frequencies.values())
        variable = min(
            candidate
            for candidate, frequency in frequencies.items()
            if frequency == maximum
        )

        for value in (False, True):
            child = simplify_one(propagated, variable, value)
            if child is not None and self.search(child):
                return True

        self.store_unsat(cnf)
        return False


def self_test() -> None:
    rows = []
    state_cap = 1024

    for n in range(3, 9):
        cnf, variable_count = graph_tautology_cnf(n)
        exact = Policy0A(state_cap=state_cap).solve(cnf, variable_count)
        ws = Policy0AWS(state_cap=state_cap).solve(cnf, variable_count)

        assert exact.answer in (False, None)
        assert ws.answer in (False, None)
        if exact.answer is False:
            assert ws.answer is False
        assert ws.unique_states <= exact.residual_states

        rows.append(
            (
                n,
                exact.residual_states,
                ws.unique_states,
                ws.exact_hits,
                ws.ws_hits,
                ws.cache_formula_comparisons,
                ws.clause_pair_checks,
            )
        )

        print(f"ORDER_SIZE = {n}")
        print(f"  exact_states = {exact.residual_states}")
        print(f"  ws_states = {ws.unique_states}")
        print(f"  exact_hits = {ws.exact_hits}")
        print(f"  weakening_subsumption_hits = {ws.ws_hits}")
        print(f"  cache_formula_comparisons = {ws.cache_formula_comparisons}")
        print(f"  clause_pair_checks = {ws.clause_pair_checks}")
        print(f"  cap_exceeded = {str(ws.cap_exceeded).lower()}")

    print("JANUS_POLICY0AWS_GRAPH_TAUTOLOGY_PROBE = PASS")
    print(f"state_cap = {state_cap}")
    print(f"rows = {tuple(rows)}")
    print("cache_rule = exact Formula Caching plus Weakening and Subsumption")
    print("lookup_cost_charged = true")
    print("claim_boundary = finite FCWS-style lookup probe; Policy-0A local Resolution remains outside historical FCWS theorem")


if __name__ == "__main__":
    self_test()
