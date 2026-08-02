#!/usr/bin/env python3
"""Differentially compare production Policy0T and the proof-traced core."""

from __future__ import annotations

import random

from janus_tear_policy0t_no_cache import Policy0T
from janus_tear_policy0t_random_translation_fuzz import (
    clause_pool,
    is_unsat,
)
from janus_tear_policy0t_trace_certificate import (
    TracePolicy,
    canonical_cnf,
    verify_trace,
    visible_affine_root_decision,
)


def trace_counters(nodes: dict[int, dict[str, object]]) -> dict[str, int]:
    expanded_states = 0
    branch_edges = 0
    terminal_calls = 0
    maximum_depth = 0
    resolution_attempts = 0
    resolution_additions = 0

    for node in nodes.values():
        maximum_depth = max(maximum_depth, int(node["depth"]))
        # Production Policy0T increments expanded_states immediately before
        # entering limited_resolution.  TracePolicy records resolution_output
        # exactly when that same stage has been entered.
        if "resolution_output" in node:
            expanded_states += 1
            resolution_attempts += int(node["resolution_attempts"])
            resolution_additions += int(node["resolution_additions"])

        terminal = node.get("terminal")
        if terminal in ("BRANCH_UNSAT", "BRANCH_SAT"):
            children = node.get("children", [])
            assert isinstance(children, list)
            branch_edges += sum(
                1
                for child in children
                if isinstance(child, dict) and not child["direct_conflict"]
            )
        else:
            terminal_calls += 1

    return {
        "recursive_calls": len(nodes),
        "expanded_states": expanded_states,
        "branch_edges": branch_edges,
        "terminal_calls": terminal_calls,
        "maximum_branch_depth": maximum_depth,
        "resolution_attempts": resolution_attempts,
        "resolution_additions": resolution_additions,
    }


def audit_formula(cnf, variable_count: int) -> tuple[int, int, int]:
    affine_answer, affine_equations = visible_affine_root_decision(cnf, variable_count)
    assert affine_answer is None
    assert affine_equations == 0

    production = Policy0T().solve(cnf, variable_count)
    assert not production.cap_exceeded

    traced = TracePolicy()
    traced_answer, root_id = traced.search(cnf)
    assert verify_trace(traced.nodes, root_id, cnf) == traced_answer

    counters = trace_counters(traced.nodes)
    assert production.answer == traced_answer
    assert production.affine_equations == 0
    assert production.recursive_calls == counters["recursive_calls"]
    assert production.expanded_states == counters["expanded_states"]
    assert production.branch_edges == counters["branch_edges"]
    assert production.terminal_calls == counters["terminal_calls"]
    assert production.maximum_branch_depth == counters["maximum_branch_depth"]
    assert production.resolution_attempts == counters["resolution_attempts"]
    assert production.resolution_additions == counters["resolution_additions"]

    return (
        production.recursive_calls,
        production.resolution_attempts,
        production.resolution_additions,
    )


def self_test() -> None:
    seed = 221340
    rng = random.Random(seed)
    variable_count = 4
    pool = clause_pool(variable_count)

    attempted = 0
    compared = 0
    maximum_calls = 0
    maximum_attempts = 0
    maximum_additions = 0

    while attempted < 4000 and compared < 500:
        attempted += 1
        clause_count = rng.randint(4, 14)
        cnf = canonical_cnf(rng.sample(pool, clause_count))
        if not is_unsat(cnf, variable_count):
            continue
        affine_answer, _ = visible_affine_root_decision(cnf, variable_count)
        if affine_answer is not None:
            continue

        calls, attempts, additions = audit_formula(cnf, variable_count)
        compared += 1
        maximum_calls = max(maximum_calls, calls)
        maximum_attempts = max(maximum_attempts, attempts)
        maximum_additions = max(maximum_additions, additions)

    assert compared == 500

    print("JANUS_POLICY0T_CORE_EQUIVALENCE_AUDIT = PASS")
    print(f"seed = {seed}")
    print(f"attempted_formulas = {attempted}")
    print(f"compared_nonaffine_unsat_formulas = {compared}")
    print(f"maximum_recursive_calls = {maximum_calls}")
    print(f"maximum_resolution_attempts = {maximum_attempts}")
    print(f"maximum_resolution_additions = {maximum_additions}")
    print("answers_equal = true")
    print("recursive_calls_equal = true")
    print("expanded_states_equal = true")
    print("branch_edges_equal = true")
    print("terminal_calls_equal = true")
    print("maximum_depth_equal = true")
    print("resolution_attempts_equal = true")
    print("resolution_additions_equal = true")
    print("claim_boundary = finite differential audit; source-level equivalence proof remains documented")


if __name__ == "__main__":
    self_test()
