#!/usr/bin/env python3
"""Exact rooted-neighborhood signatures for tiny signed CNF incidence graphs.

This is a diagnostic for H106/H114/H115.  It checks fixed-radius local views;
it does not claim that matching local signatures alone proves indistinguishability
for every transduction or that the supplied fixtures form a SAT/UNSAT lower-bound
family.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


def incidence_graph(cnf: CNF) -> dict[str, dict[str, str]]:
    adjacency: dict[str, dict[str, str]] = {}
    for variable in range(1, cnf.variable_count + 1):
        adjacency[f"v{variable}"] = {}
    for clause_index, clause in enumerate(cnf.clauses):
        clause_node = f"c{clause_index}"
        adjacency[clause_node] = {}
        for literal in clause:
            variable_node = f"v{abs(literal)}"
            sign = "+" if literal > 0 else "-"
            adjacency[clause_node][variable_node] = sign
            adjacency[variable_node][clause_node] = sign
    return adjacency


def node_type(node: str) -> str:
    return "V" if node.startswith("v") else "C"


def rooted_signature(
    adjacency: dict[str, dict[str, str]], root: str, radius: int
) -> tuple:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    distance = {root: 0}
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if distance[node] == radius:
            continue
        for neighbor in adjacency[node]:
            if neighbor not in distance:
                distance[neighbor] = distance[node] + 1
                queue.append(neighbor)

    colors = {node: node_type(node) for node in distance}
    for _ in range(radius + 1):
        updated = {}
        for node in distance:
            neighborhood = sorted(
                (edge_sign, colors[neighbor])
                for neighbor, edge_sign in adjacency[node].items()
                if neighbor in distance
            )
            updated[node] = (colors[node], tuple(neighborhood))
        canonical = {value: index for index, value in enumerate(sorted(set(updated.values()), key=repr))}
        colors = {node: str(canonical[value]) for node, value in updated.items()}

    layer_summary = Counter(
        (distance[node], node_type(node), colors[node]) for node in distance
    )
    root_edges = tuple(
        sorted(
            (sign, node_type(neighbor), distance.get(neighbor))
            for neighbor, sign in adjacency[root].items()
            if neighbor in distance
        )
    )
    return (
        node_type(root),
        colors[root],
        tuple(sorted(layer_summary.items())),
        root_edges,
    )


def signature_multiset(cnf: CNF, radius: int) -> Counter:
    adjacency = incidence_graph(cnf)
    return Counter(rooted_signature(adjacency, node, radius) for node in adjacency)


def rename_variables(cnf: CNF, permutation: tuple[int, ...]) -> CNF:
    if sorted(permutation) != list(range(1, cnf.variable_count + 1)):
        raise ValueError("invalid permutation")
    mapping = {index + 1: permutation[index] for index in range(cnf.variable_count)}
    return CNF(
        cnf.variable_count,
        tuple(
            tuple(mapping[abs(literal)] if literal > 0 else -mapping[abs(literal)] for literal in clause)
            for clause in cnf.clauses
        ),
    )


def self_test() -> None:
    base = CNF(3, ((1, -2), (2, 3), (-1, -3)))
    renamed = rename_variables(base, (3, 1, 2))
    for radius in range(3):
        assert signature_multiset(base, radius) == signature_multiset(renamed, radius)

    sign_changed = CNF(3, ((1, 2), (2, 3), (-1, -3)))
    assert signature_multiset(base, 1) != signature_multiset(sign_changed, 1)

    print("JANUS_LOCAL_NEIGHBORHOOD_AUDIT = PASS")
    print("VARIABLE_RENAMING_INVARIANCE = VERIFIED_FOR_FIXTURE")
    print("SIGNED_EDGE_SENSITIVITY = VERIFIED_FOR_FIXTURE")


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
