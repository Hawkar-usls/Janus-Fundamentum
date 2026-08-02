#!/usr/bin/env python3
"""Charge Policy-0A recursive calls, memo hits, and branch edges.

Unique residual CNFs are not a complete work measure.  This audit keeps the
original Policy-0A transition rule but counts every recursive invocation and
every incoming branch edge, including calls that terminate at a memo hit.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import (
    CNF,
    K33_EDGES,
    K4_EDGES,
    Policy0A,
    limited_resolution,
    masked_tseitin_cnf,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)


@dataclass
class AccountingResult:
    answer: bool | None
    cap_exceeded: bool
    unique_residual_states: int
    memo_entries: int
    recursive_calls: int
    memo_hits: int
    branch_edges: int
    terminal_calls: int
    resolution_attempts: int
    resolution_additions: int
    affine_equations: int


class AccountingPolicy0A(Policy0A):
    def solve(self, cnf: CNF, variable_count: int) -> AccountingResult:
        self.states = 0
        self.memo: dict[CNF, bool] = {}
        self.resolution_attempts = 0
        self.resolution_additions = 0
        self.recursive_calls = 0
        self.memo_hits = 0
        self.branch_edges = 0
        self.terminal_calls = 0

        affine_answer, equation_count = visible_affine_root_decision(cnf, variable_count)
        self.affine_equation_count = equation_count
        if affine_answer is not None:
            return self.accounting_result(affine_answer, False)

        try:
            answer = self.search(cnf)
            return self.accounting_result(answer, False)
        except RuntimeError:
            return self.accounting_result(None, True)

    def accounting_result(
        self,
        answer: bool | None,
        cap_exceeded: bool,
    ) -> AccountingResult:
        return AccountingResult(
            answer=answer,
            cap_exceeded=cap_exceeded,
            unique_residual_states=self.states,
            memo_entries=len(self.memo),
            recursive_calls=self.recursive_calls,
            memo_hits=self.memo_hits,
            branch_edges=self.branch_edges,
            terminal_calls=self.terminal_calls,
            resolution_attempts=self.resolution_attempts,
            resolution_additions=self.resolution_additions,
            affine_equations=self.affine_equation_count,
        )

    def search(self, cnf: CNF) -> bool:
        self.recursive_calls += 1

        propagated, contradiction = unit_propagate(cnf)
        if contradiction:
            self.terminal_calls += 1
            return False
        assert propagated is not None
        if not propagated:
            self.terminal_calls += 1
            return True
        cnf = propagated

        if cnf in self.memo:
            self.memo_hits += 1
            return self.memo[cnf]

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
            self.memo[cnf] = False
            self.terminal_calls += 1
            return False

        propagated, contradiction = unit_propagate(saturated)
        if contradiction:
            self.memo[cnf] = False
            self.terminal_calls += 1
            return False
        assert propagated is not None
        if not propagated:
            self.memo[cnf] = True
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
            if self.search(child):
                self.memo[cnf] = True
                return True

        self.memo[cnf] = False
        return False


def print_result(name: str, result: AccountingResult) -> None:
    print(f"CASE = {name}")
    print(f"  answer = {result.answer}")
    print(f"  cap_exceeded = {str(result.cap_exceeded).lower()}")
    print(f"  unique_residual_states = {result.unique_residual_states}")
    print(f"  memo_entries = {result.memo_entries}")
    print(f"  recursive_calls = {result.recursive_calls}")
    print(f"  memo_hits = {result.memo_hits}")
    print(f"  branch_edges = {result.branch_edges}")
    print(f"  terminal_calls = {result.terminal_calls}")
    print(f"  resolution_attempts = {result.resolution_attempts}")
    print(f"  resolution_additions = {result.resolution_additions}")


def self_test() -> None:
    triangular_k4, triangular_variables = masked_tseitin_cnf(4, K4_EDGES)
    triangular = AccountingPolicy0A().solve(triangular_k4, triangular_variables)
    print_result("TRIANGULAR_MASKED_K4", triangular)
    assert triangular.answer is False
    assert not triangular.cap_exceeded
    assert triangular.unique_residual_states == 3842
    assert triangular.recursive_calls == triangular.branch_edges + 1
    assert triangular.recursive_calls >= triangular.unique_residual_states

    maj3_k4, maj3_variables = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    maj3 = AccountingPolicy0A().solve(maj3_k4, maj3_variables)
    print_result("MAJ3_LIFTED_K4", maj3)
    assert maj3.answer is False
    assert not maj3.cap_exceeded
    assert maj3.unique_residual_states == 2427
    assert maj3.recursive_calls == maj3.branch_edges + 1
    assert maj3.recursive_calls >= maj3.unique_residual_states

    maj3_k33, maj3_k33_variables = maj3_lifted_tseitin_cnf(6, K33_EDGES)
    cap = 4 * maj3_k33_variables**2
    capped = AccountingPolicy0A(state_cap=cap).solve(
        maj3_k33,
        maj3_k33_variables,
    )
    print_result("MAJ3_LIFTED_K33_QUADRATIC_CAP", capped)
    assert capped.answer is None
    assert capped.cap_exceeded
    assert capped.unique_residual_states == cap + 1
    assert capped.recursive_calls == capped.branch_edges + 1

    print("JANUS_TEAR_POLICY0A_WORK_ACCOUNTING_SELF_TEST = PASS")


if __name__ == "__main__":
    self_test()
