#!/usr/bin/env python3
"""Audit the explicit size/depth bounds in the C022 simulation theorem."""

from __future__ import annotations

from janus_tear_policy0t_recursive_trace_translator import TraceTranslator
from janus_tear_policy0t_recursive_translator_fuzz import CASES
from janus_tear_policy0t_trace_certificate import (
    TracePolicy,
    UNSAT_FORMULA,
    canonical_cnf,
    verify_trace,
    visible_affine_root_decision,
)


def trace_counts(nodes: dict[int, dict[str, object]]) -> tuple[int, int, int, int]:
    local_resolution_events = 0
    propagated_units = 0
    branch_nodes = 0
    opposite_unit_conflicts = 0

    for node in nodes.values():
        local_resolution_events += len(node.get("resolution_events", []))
        if "branch_var" in node:
            branch_nodes += 1
        for key in ("pre_units", "post_units"):
            events = node.get(key, [])
            assert isinstance(events, list)
            for event in events:
                assert isinstance(event, dict)
                if event["kind"] == "unit":
                    propagated_units += 1
                elif event["kind"] == "opposite_units":
                    opposite_unit_conflicts += 1
                else:
                    raise AssertionError(f"unknown unit event: {event['kind']}")

    return (
        local_resolution_events,
        propagated_units,
        branch_nodes,
        opposite_unit_conflicts,
    )


def audit_case(name: str, cnf, variable_count: int) -> None:
    root = canonical_cnf(cnf)
    affine_answer, affine_equations = visible_affine_root_decision(root, variable_count)
    assert affine_answer is None
    assert affine_equations == 0

    policy = TracePolicy()
    answer, root_id = policy.search(root)
    assert answer is False
    assert verify_trace(policy.nodes, root_id, root) is False

    translator = TraceTranslator(root, policy.nodes)
    final_line = translator.translate(root_id)
    axiom_lines, resolution_lines, maximum_width, proof_depth = (
        translator.proof.verify(root)
    )
    assert translator.proof.clause(final_line) == ()

    r, u, b, o = trace_counts(policy.nodes)
    m = len(root)
    predicted_size_bound = m + r + u + b + o
    actual_size = len(translator.proof.lines)
    predicted_depth_bound = 2 * variable_count + 2

    assert axiom_lines == m
    assert resolution_lines <= r + u + b + o
    assert actual_size <= predicted_size_bound
    assert proof_depth <= predicted_depth_bound

    print(f"CASE = {name}")
    print(f"  variables = {variable_count}")
    print(f"  root_clauses_m = {m}")
    print(f"  local_resolution_events_r = {r}")
    print(f"  propagated_units_u = {u}")
    print(f"  branch_nodes_b = {b}")
    print(f"  opposite_unit_conflicts_o = {o}")
    print(f"  proof_lines = {actual_size}")
    print(f"  size_bound_m_plus_r_plus_u_plus_b_plus_o = {predicted_size_bound}")
    print(f"  proof_depth = {proof_depth}")
    print(f"  depth_bound_2N_plus_2 = {predicted_depth_bound}")
    print(f"  maximum_width = {maximum_width}")
    print("  final_clause = EMPTY")


def self_test() -> None:
    audit_case("BASE_NONAFFINE_BRANCH", UNSAT_FORMULA, 4)
    for name, payload in CASES.items():
        audit_case(name, payload["cnf"], int(payload["variables"]))

    print("JANUS_POLICY0T_PROOF_BOUND_AUDIT = PASS")
    print("size_theorem = S <= m+r+u+b+o on all finite fixtures")
    print("depth_theorem = D <= 2N+2 on all finite fixtures")
    print("claim_boundary = finite audit; universal proof is in C022 theorem draft")


if __name__ == "__main__":
    self_test()
