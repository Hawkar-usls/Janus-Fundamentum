#!/usr/bin/env python3
"""No-cache successor of JANUS Tear Policy-0A.

Policy-0T keeps the same visible affine root shortcut, unit propagation,
polynomially budgeted one-pass resolution, branching rule, and value order, but
removes exact residual memoization.  Every recursive occurrence is charged.

The finite audit does not prove the asymptotic lifting theorem.  It provides the
fully specified tree policy to which a DPLL/Resolution certificate can be
attached without a formula-caching inference rule.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    K4_EDGES,
    limited_resolution,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
    visible_tseitin_cnf,
)


@dataclass
class TreePolicyResult:
    answer: bool | None
    cap_exceeded: bool
    recursive_calls: int
    expanded_states: int
    branch_edges: int
    terminal_calls: int
    resolution_attempts: int
    resolution_additions: int
    affine_equations: int
    maximum_branch_depth: int


class Policy0T:
    def __init__(self, occurrence_cap: int | None = None):
        self.occurrence_cap = occurrence_cap

    def solve(self, cnf: CNF, variable_count: int) -> TreePolicyResult:
        self.recursive_calls = 0
        self.expanded_states = 0
        self.branch_edges = 0
        self.terminal_calls = 0
        self.resolution_attempts = 0
        self.resolution_additions = 0
        self.maximum_branch_depth = 0

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.result(affine_answer, False)

        try:
            answer = self.search(cnf, depth=0)
            return self.result(answer, False)
        except RuntimeError:
            return self.result(None, True)

    def result(self, answer: bool | None, cap_exceeded: bool) -> TreePolicyResult:
        return TreePolicyResult(
            answer=answer,
            cap_exceeded=cap_exceeded,
            recursive_calls=self.recursive_calls,
            expanded_states=self.expanded_states,
            branch_edges=self.branch_edges,
            terminal_calls=self.terminal_calls,
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
            affine_equations=self.affine_equation_count,
            maximum_branch_depth=self.maximum_branch_depth,
        )

    def charge_call(self, depth: int) -> None:
        self.recursive_calls += 1
        self.maximum_branch_depth = max(self.maximum_branch_depth, depth)
        if self.occurrence_cap is not None and self.recursive_calls > self.occurrence_cap:
            raise RuntimeError("recursive occurrence cap exceeded")

    def search(self, cnf: CNF, depth: int) -> bool:
        self.charge_call(depth)

        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            self.terminal_calls += 1
            return False
        assert propagated is not None
        if not propagated:
            self.terminal_calls += 1
            return True

        self.expanded_states += 1
        literal_count = sum(len(clause) for clause in propagated)
        width_limit = max(len(clause) for clause in propagated) + 1
        saturated, refuted, attempts, additions = limited_resolution(
            propagated,
            max_width=width_limit,
            attempt_budget=max(64, 4 * literal_count),
            addition_budget=max(8, len(propagated) // 4),
        )
        self.resolution_attempts += attempts
        self.resolution_additions += additions

        if refuted:
            self.terminal_calls += 1
            return False

        propagated, contradiction = unit_propagate(saturated)
        if contradiction:
            self.terminal_calls += 1
            return False
        assert propagated is not None
        if not propagated:
            self.terminal_calls += 1
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
            if child is None:
                self.terminal_calls += 1
                continue
            self.branch_edges += 1
            if self.search(child, depth + 1):
                return True

        return False


def print_result(name: str, result: TreePolicyResult) -> None:
    print(f"CASE = {name}")
    print(f"  answer = {result.answer}")
    print(f"  cap_exceeded = {str(result.cap_exceeded).lower()}")
    print(f"  recursive_calls = {result.recursive_calls}")
    print(f"  expanded_states = {result.expanded_states}")
    print(f"  branch_edges = {result.branch_edges}")
    print(f"  terminal_calls = {result.terminal_calls}")
    print(f"  maximum_branch_depth = {result.maximum_branch_depth}")
    print(f"  affine_equations = {result.affine_equations}")
    print(f"  resolution_attempts = {result.resolution_attempts}")
    print(f"  resolution_additions = {result.resolution_additions}")


def self_test() -> None:
    visible, visible_variables = visible_tseitin_cnf(4, K4_EDGES)
    visible_result = Policy0T().solve(visible, visible_variables)
    print_result("VISIBLE_K4", visible_result)
    assert visible_result.answer is False
    assert not visible_result.cap_exceeded
    assert visible_result.recursive_calls == 0
    assert visible_result.affine_equations == 4

    lifted, lifted_variables = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    cap = 4 * lifted_variables**2
    lifted_result = Policy0T(occurrence_cap=cap).solve(lifted, lifted_variables)
    print_result("MAJ3_LIFTED_K4_QUADRATIC_OCCURRENCE_CAP", lifted_result)
    assert lifted_variables == 18
    assert lifted_result.answer is None
    assert lifted_result.cap_exceeded
    assert lifted_result.recursive_calls == cap + 1
    assert lifted_result.maximum_branch_depth <= lifted_variables

    print("JANUS_TEAR_POLICY0T_NO_CACHE_SELF_TEST = PASS")


if __name__ == "__main__":
    self_test()
