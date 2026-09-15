#!/usr/bin/env python3
"""Exact-implementation finite replay for the C024-A resolution-sink family.

This imports the registered Policy-0A primitives instead of reimplementing them.
Finite PASS checks mechanics only; the asymptotic argument lives in
proof_attempts/C024/C024_A_ISSUE_211_RESOLUTION_SINK_COUNTERFAMILY.md.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from janus_tear_policy0a_masked_tseitin import (
    CNF,
    canonical_cnf,
    limited_resolution,
    simplify_one,
    unit_propagate,
    visible_affine_root_decision,
)
from janus_tear_policy0a_source_gt import source_graph_tautology_cnf
from janus_tear_policy0t_trace_certificate import branch_variable


@dataclass(frozen=True)
class PaddedGT:
    n: int
    cnf: CNF
    core_cnf: CNF
    variable_count: int
    core_variables: frozenset[int]
    sink_d: int
    sink_a: int
    B: int
    p: int


def shift_cnf(cnf: CNF, offset: int) -> CNF:
    return canonical_cnf(
        tuple((abs(lit) + offset) if lit > 0 else -(abs(lit) + offset) for lit in clause)
        for clause in cnf
    )


def build_padded_gt(n: int) -> PaddedGT:
    if n < 3:
        raise ValueError("use n >= 3")

    B = 256 * n * n
    p = 64 * n * n

    d = 1
    a = 2
    next_var = 3
    u = list(range(next_var, next_var + p))
    next_var += p
    v = list(range(next_var, next_var + p))
    next_var += p

    source_core, source_variables = source_graph_tautology_cnf(n)
    assert source_variables == n * (n - 1)
    offset = next_var - 1
    core_cnf = shift_cnf(source_core, offset)
    core_variables = frozenset(range(next_var, next_var + source_variables))
    next_var += source_variables

    clauses: list[tuple[int, ...]] = list(core_cnf)

    # Equal frequency boost for every still-unassigned GT variable.
    for core_var in sorted(core_variables):
        for _ in range(B):
            leaf = next_var
            next_var += 1
            clauses.append((core_var, leaf))

    # Earliest resolution pivot. Every d-resolvent contains a and -a.
    for leaf in u:
        clauses.append((d, a, leaf))
    for leaf in v:
        clauses.append((-d, -a, leaf))

    return PaddedGT(
        n=n,
        cnf=canonical_cnf(clauses),
        core_cnf=core_cnf,
        variable_count=next_var - 1,
        core_variables=core_variables,
        sink_d=d,
        sink_a=a,
        B=B,
        p=p,
    )


def core_projection(cnf: CNF, core_variables: frozenset[int]) -> CNF:
    return canonical_cnf(
        clause
        for clause in cnf
        if clause and all(abs(lit) in core_variables for lit in clause)
    )


def self_test() -> None:
    family = build_padded_gt(3)

    affine_answer, affine_equations = visible_affine_root_decision(
        family.cnf,
        family.variable_count,
    )
    assert affine_answer is None
    assert affine_equations == 0

    propagated, contradiction = unit_propagate(family.cnf)
    assert not contradiction
    assert propagated is not None

    core_root, core_contradiction = unit_propagate(family.core_cnf)
    assert not core_contradiction
    assert core_root is not None
    assert core_projection(propagated, family.core_variables) == core_root

    literal_count = sum(len(clause) for clause in propagated)
    attempt_budget = max(64, 4 * literal_count)
    addition_budget = max(8, len(propagated) // 4)
    assert family.p**2 > attempt_budget

    saturated, refuted, attempts, additions = limited_resolution(
        propagated,
        max_width=max(map(len, propagated)) + 1,
        attempt_budget=attempt_budget,
        addition_budget=addition_budget,
    )
    assert not refuted
    assert attempts == attempt_budget
    assert additions == 0
    assert saturated == propagated

    frequencies = Counter(abs(lit) for clause in saturated for lit in clause)
    selected = branch_variable(saturated)
    assert selected in family.core_variables
    assert family.B > 2 * family.p
    assert frequencies[family.sink_d] == 2 * family.p
    assert frequencies[family.sink_a] == 2 * family.p
    assert min(frequencies[var] for var in family.core_variables) >= family.B

    # Both branch values preserve the exact core projection after exhaustive UP.
    for value in (False, True):
        full_child = simplify_one(saturated, selected, value)
        core_child = simplify_one(core_root, selected, value)
        if core_child is None:
            assert full_child is None or unit_propagate(full_child)[1]
            continue
        assert full_child is not None
        full_post, full_bad = unit_propagate(full_child)
        core_post, core_bad = unit_propagate(core_child)
        assert full_bad == core_bad
        if not full_bad:
            assert full_post is not None and core_post is not None
            assert core_projection(full_post, family.core_variables) == core_post

    n = family.n
    V = n * (n - 1)
    L0_upper = 3 * n**3 + 2 * V * family.B + 6 * family.p
    assert family.p**2 > 4 * L0_upper

    print("JANUS_POLICY0A_PADDED_GT_PARITY = PASS")
    print(f"n = {n}")
    print(f"variables = {family.variable_count}")
    print(f"clauses = {len(family.cnf)}")
    print(f"literal_count = {literal_count}")
    print(f"attempt_budget = {attempt_budget}")
    print(f"sink_pair_attempts_available = {family.p**2}")
    print(f"resolution_attempts = {attempts}")
    print(f"resolution_additions = {additions}")
    print(f"branch_variable = {selected}")
    print("claim_boundary = finite implementation-parity replay only")


if __name__ == "__main__":
    self_test()
