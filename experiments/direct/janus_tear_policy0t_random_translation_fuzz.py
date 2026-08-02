#!/usr/bin/env python3
"""Deterministically fuzz the C022 trace-to-Resolution theorem on small CNFs."""

from __future__ import annotations

import random
from itertools import combinations, product

from janus_tear_policy0t_proof_bound_audit import trace_counts
from janus_tear_policy0t_recursive_trace_translator import TraceTranslator
from janus_tear_policy0t_trace_certificate import (
    TracePolicy,
    canonical_cnf,
    verify_trace,
    visible_affine_root_decision,
)

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def clause_pool(variable_count: int, maximum_width: int = 3) -> tuple[Clause, ...]:
    clauses: set[Clause] = set()
    variables = range(1, variable_count + 1)
    for width in range(1, min(maximum_width, variable_count) + 1):
        for scope in combinations(variables, width):
            for signs in product((False, True), repeat=width):
                clause = tuple(
                    -variable if negative else variable
                    for variable, negative in zip(scope, signs, strict=True)
                )
                clauses.add(clause)
    return tuple(sorted(clauses, key=lambda clause: (len(clause), clause)))


def satisfies(cnf: CNF, assignment: tuple[bool, ...]) -> bool:
    return all(
        any(
            (literal > 0 and assignment[literal - 1])
            or (literal < 0 and not assignment[-literal - 1])
            for literal in clause
        )
        for clause in cnf
    )


def is_unsat(cnf: CNF, variable_count: int) -> bool:
    return not any(
        satisfies(cnf, assignment)
        for assignment in product((False, True), repeat=variable_count)
    )


def audit_formula(cnf: CNF, variable_count: int) -> tuple[int, int, int]:
    affine_answer, affine_equations = visible_affine_root_decision(cnf, variable_count)
    assert affine_answer is None
    assert affine_equations == 0

    policy = TracePolicy()
    answer, root_id = policy.search(cnf)
    assert answer is False
    assert verify_trace(policy.nodes, root_id, cnf) is False

    translator = TraceTranslator(cnf, policy.nodes)
    final_line = translator.translate(root_id)
    _, resolution_lines, _, proof_depth = translator.proof.verify(cnf)
    assert translator.proof.clause(final_line) == ()

    r, u, b, o = trace_counts(policy.nodes)
    size_bound = len(cnf) + r + u + b + o
    assert len(translator.proof.lines) <= size_bound
    assert resolution_lines <= r + u + b + o
    assert proof_depth <= 2 * variable_count + 2

    maximum_trace_depth = max(int(node["depth"]) for node in policy.nodes.values())
    return len(policy.nodes), len(translator.proof.lines), maximum_trace_depth


def self_test() -> None:
    seed = 220134
    rng = random.Random(seed)
    variable_count = 4
    pool = clause_pool(variable_count)

    attempted = 0
    unsat_seen = 0
    nonaffine_translated = 0
    maximum_trace_nodes = 0
    maximum_proof_lines = 0
    maximum_trace_depth = 0

    while attempted < 3000 and nonaffine_translated < 500:
        attempted += 1
        clause_count = rng.randint(4, 14)
        cnf = canonical_cnf(rng.sample(pool, clause_count))
        if not is_unsat(cnf, variable_count):
            continue
        unsat_seen += 1

        affine_answer, _ = visible_affine_root_decision(cnf, variable_count)
        if affine_answer is not None:
            continue

        trace_nodes, proof_lines, trace_depth = audit_formula(cnf, variable_count)
        nonaffine_translated += 1
        maximum_trace_nodes = max(maximum_trace_nodes, trace_nodes)
        maximum_proof_lines = max(maximum_proof_lines, proof_lines)
        maximum_trace_depth = max(maximum_trace_depth, trace_depth)

    assert nonaffine_translated >= 300

    print("JANUS_POLICY0T_RANDOM_TRANSLATION_FUZZ = PASS")
    print(f"seed = {seed}")
    print(f"attempted_formulas = {attempted}")
    print(f"unsat_formulas_seen = {unsat_seen}")
    print(f"nonaffine_formulas_translated = {nonaffine_translated}")
    print(f"maximum_trace_nodes = {maximum_trace_nodes}")
    print(f"maximum_proof_lines = {maximum_proof_lines}")
    print(f"maximum_trace_depth = {maximum_trace_depth}")
    print("all_final_clauses = EMPTY")
    print("all_size_bounds = PASS")
    print("all_depth_bounds = PASS")
    print("claim_boundary = deterministic finite fuzz; universal theorem still needs proof review")


if __name__ == "__main__":
    self_test()
