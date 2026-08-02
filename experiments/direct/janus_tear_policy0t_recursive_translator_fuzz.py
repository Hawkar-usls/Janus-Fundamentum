#!/usr/bin/env python3
"""Adversarial finite suite for the Policy-0T recursive trace translator."""

from __future__ import annotations

from janus_tear_policy0t_recursive_trace_translator import TraceTranslator
from janus_tear_policy0t_trace_certificate import (
    TracePolicy,
    canonical_cnf,
    verify_trace,
    visible_affine_root_decision,
)


CASES = {
    "OPPOSITE_ROOT_UNITS": {
        "variables": 4,
        "cnf": ((1,), (-1,), (2, 3, 4)),
        "root_terminal": "UNIT_CONTRADICTION",
        "minimum_depth": 0,
    },
    "MULTI_BATCH_UNIT_CONTRADICTION": {
        "variables": 4,
        "cnf": ((1,), (-1, 2), (-2, 3), (-3,), (2, 3, 4)),
        "root_terminal": "UNIT_CONTRADICTION",
        "minimum_depth": 0,
    },
    "POST_RESOLUTION_UNIT_CONTRADICTION": {
        "variables": 4,
        "cnf": ((1, 2), (1, -2), (-1, 2), (-1, -2), (3, 4)),
        "root_terminal": "POST_UNIT_CONTRADICTION",
        "minimum_depth": 0,
    },
    "DEPTH_TWO_BRANCH_TREE": {
        "variables": 5,
        "cnf": (
            (-3, 4, -5),
            (-2, -3, -4),
            (-2, -3, 5),
            (-2, 3, -4),
            (-2, 4, 5),
            (-1, 3, 4),
            (1, -4, 5),
            (1, -2, -5),
            (2, -3, -4),
            (2, -3, 4),
            (2, 3, -5),
            (2, 3, 5),
        ),
        "root_terminal": "BRANCH_UNSAT",
        "minimum_depth": 2,
    },
}


def audit_case(name: str, payload: dict[str, object]) -> None:
    variables = int(payload["variables"])
    root = canonical_cnf(payload["cnf"])
    affine_answer, affine_equations = visible_affine_root_decision(root, variables)
    assert affine_answer is None
    assert affine_equations == 0

    policy = TracePolicy()
    answer, root_id = policy.search(root)
    assert answer is False
    assert verify_trace(policy.nodes, root_id, root) is False
    assert policy.nodes[root_id]["terminal"] == payload["root_terminal"]

    translator = TraceTranslator(root, policy.nodes)
    final_line = translator.translate(root_id)
    axiom_lines, resolution_lines, maximum_width, proof_depth = (
        translator.proof.verify(root)
    )
    maximum_trace_depth = max(int(node["depth"]) for node in policy.nodes.values())

    assert translator.proof.clause(final_line) == ()
    assert maximum_trace_depth >= int(payload["minimum_depth"])

    print(f"CASE = {name}")
    print(f"  variables = {variables}")
    print(f"  clauses = {len(root)}")
    print(f"  trace_nodes = {len(policy.nodes)}")
    print(f"  maximum_trace_depth = {maximum_trace_depth}")
    print(f"  root_terminal = {policy.nodes[root_id]['terminal']}")
    print(f"  axiom_lines = {axiom_lines}")
    print(f"  resolution_lines = {resolution_lines}")
    print(f"  proof_lines = {len(translator.proof.lines)}")
    print(f"  maximum_width = {maximum_width}")
    print(f"  proof_depth = {proof_depth}")
    print("  final_clause = EMPTY")


def self_test() -> None:
    for name, payload in CASES.items():
        audit_case(name, payload)
    print("JANUS_POLICY0T_RECURSIVE_TRANSLATOR_FUZZ = PASS")
    print("claim_boundary = four finite adversarial classes; universal H134 induction remains open")


if __name__ == "__main__":
    self_test()
