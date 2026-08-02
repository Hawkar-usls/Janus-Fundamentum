#!/usr/bin/env python3
"""Finite accounting audit for contextual circuit-equivalence proofs.

A polynomial-size DAG context can represent exponentially many unfolded gadget
occurrences.  Circuit Frege need not prove each unfolded occurrence separately:
it proves equivalence once per DAG gate and reuses sharing.  This audit records
that accounting distinction.  The universal theorem is proved in
proof_attempts/H111/REFUTATION.md using the Circuit-Frege simulation and
Krajicek's rewrite theorem; this script is only a deterministic fixture.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    op: str
    children: tuple[int, ...]


def shared_binary_tower(depth: int) -> list[Node]:
    if depth < 0:
        raise ValueError("depth must be nonnegative")
    nodes = [Node("PORT", ())]
    for _ in range(depth):
        previous = len(nodes) - 1
        nodes.append(Node("AND", (previous, previous)))
    return nodes


def validate_dag(nodes: list[Node]) -> None:
    if not nodes or nodes[0] != Node("PORT", ()):
        raise ValueError("fixture must start with one gadget port")
    for index, node in enumerate(nodes):
        if node.op == "PORT":
            if node.children:
                raise ValueError("port may not have children")
            continue
        if node.op not in {"AND", "OR", "NOT"}:
            raise ValueError(f"unsupported gate {node.op}")
        expected = 1 if node.op == "NOT" else 2
        if len(node.children) != expected:
            raise ValueError("wrong arity")
        if any(child < 0 or child >= index for child in node.children):
            raise ValueError("context is not acyclic")


def unfolded_port_occurrences(nodes: list[Node], output: int | None = None) -> int:
    validate_dag(nodes)
    target = len(nodes) - 1 if output is None else output
    memo: dict[int, int] = {}

    def count(index: int) -> int:
        if index in memo:
            return memo[index]
        node = nodes[index]
        value = 1 if node.op == "PORT" else sum(count(child) for child in node.children)
        memo[index] = value
        return value

    return count(target)


def circuit_frege_accounting(
    nodes: list[Node],
    local_gadget_equivalence_steps: int = 1,
    congruence_steps_per_gate: int = 3,
) -> int:
    validate_dag(nodes)
    if local_gadget_equivalence_steps < 1 or congruence_steps_per_gate < 1:
        raise ValueError("proof costs must be positive")
    internal = sum(node.op != "PORT" for node in nodes)
    return local_gadget_equivalence_steps + congruence_steps_per_gate * internal


def self_test() -> None:
    depth = 24
    nodes = shared_binary_tower(depth)
    occurrences = unfolded_port_occurrences(nodes)
    proof_steps = circuit_frege_accounting(nodes)

    assert len(nodes) == depth + 1
    assert occurrences == 2**depth
    assert proof_steps == 1 + 3 * depth
    assert proof_steps < depth * depth
    assert occurrences > proof_steps * proof_steps

    print("JANUS_CONTEXTUAL_EF_UPPER_BOUND_AUDIT = PASS")
    print(f"DAG_GATES = {len(nodes)}")
    print(f"UNFOLDED_GADGET_OCCURRENCES = {occurrences}")
    print(f"COMPOSITIONAL_PROOF_STEP_BOUND = {proof_steps}")
    print("SHARING_ACCOUNTED_ONCE_PER_DAG_GATE = true")
    print("CLAIM_BOUNDARY = finite accounting fixture; theorem is in proof artifact")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    parser.error("only --self-test is supported")


if __name__ == "__main__":
    raise SystemExit(main())
