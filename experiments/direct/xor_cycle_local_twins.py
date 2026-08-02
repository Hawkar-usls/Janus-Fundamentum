#!/usr/bin/env python3
"""Construct exact local SAT/UNSAT twins from signed XOR cycles.

For every radius R, build two 2-CNF formulas on two equal cycles.  The SAT
formula places two inequality edges in one cycle and none in the other.  The
UNSAT formula places one inequality edge in each cycle.  The two marked edges
are far enough apart that the exact multiset of rooted signed incidence balls
through radius R is identical, while satisfiability depends on parity inside
each connected component.

The formulas already have primal treewidth two.  Consequently an identity
compiler followed by an ordinary global dynamic program distinguishes them.
This is a counterexample to the claim that local-type inventory alone controls
global low-treewidth decision behavior.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Hashable


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


EdgeLabel = str
Color = Hashable


def equality_clauses(left: int, right: int) -> tuple[tuple[int, int], ...]:
    return ((-left, right), (left, -right))


def inequality_clauses(left: int, right: int) -> tuple[tuple[int, int], ...]:
    return ((left, right), (-left, -right))


def build_two_cycle_formula(
    cycle_length: int,
    negative_positions: tuple[frozenset[int], frozenset[int]],
) -> CNF:
    if cycle_length < 4:
        raise ValueError("cycle length must be at least four")
    clauses: list[tuple[int, ...]] = []
    offset = 0
    for marked in negative_positions:
        if any(position < 0 or position >= cycle_length for position in marked):
            raise ValueError("marked edge outside cycle")
        variables = list(range(offset + 1, offset + cycle_length + 1))
        offset += cycle_length
        for index, left in enumerate(variables):
            right = variables[(index + 1) % cycle_length]
            clauses.extend(
                inequality_clauses(left, right)
                if index in marked
                else equality_clauses(left, right)
            )
    return CNF(offset, tuple(clauses))


def local_twin_pair(radius: int) -> tuple[CNF, CNF, int]:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    cycle_length = 8 * radius + 12
    sat = build_two_cycle_formula(
        cycle_length,
        (frozenset({0, cycle_length // 2}), frozenset()),
    )
    unsat = build_two_cycle_formula(
        cycle_length,
        (frozenset({0}), frozenset({0})),
    )
    return sat, unsat, cycle_length


def incidence_graph(cnf: CNF) -> tuple[dict[str, dict[str, EdgeLabel]], dict[str, str]]:
    adjacency: dict[str, dict[str, EdgeLabel]] = {}
    labels: dict[str, str] = {}
    for variable in range(1, cnf.variable_count + 1):
        node = f"v{variable}"
        adjacency[node] = {}
        labels[node] = "V"
    for clause_index, clause in enumerate(cnf.clauses):
        clause_node = f"c{clause_index}"
        adjacency[clause_node] = {}
        labels[clause_node] = "C"
        for literal in clause:
            variable_node = f"v{abs(literal)}"
            sign = "+" if literal > 0 else "-"
            adjacency[clause_node][variable_node] = sign
            adjacency[variable_node][clause_node] = sign
    return adjacency, labels


def rooted_ball(
    adjacency: dict[str, dict[str, EdgeLabel]],
    labels: dict[str, str],
    root: str,
    radius: int,
) -> tuple[dict[str, dict[str, EdgeLabel]], dict[str, tuple[str, int, bool]]]:
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

    subgraph = {
        node: {
            neighbor: sign
            for neighbor, sign in adjacency[node].items()
            if neighbor in distance
        }
        for node in distance
    }
    base_labels = {
        node: (labels[node], distance[node], node == root) for node in distance
    }
    return subgraph, base_labels


def refine_colors(
    subgraph: dict[str, dict[str, EdgeLabel]], colors: dict[str, Color]
) -> dict[str, int]:
    while True:
        descriptors = {
            node: (
                colors[node],
                tuple(
                    sorted(
                        (sign, colors[neighbor])
                        for neighbor, sign in subgraph[node].items()
                    )
                ),
            )
            for node in subgraph
        }
        palette = {
            descriptor: index
            for index, descriptor in enumerate(
                sorted(set(descriptors.values()), key=repr)
            )
        }
        updated = {node: palette[descriptor] for node, descriptor in descriptors.items()}

        old_cells = sorted(
            sorted(node for node in subgraph if colors[node] == color)
            for color in set(colors.values())
        )
        new_cells = sorted(
            sorted(node for node in subgraph if updated[node] == color)
            for color in set(updated.values())
        )
        if old_cells == new_cells:
            return updated
        colors = updated


def exact_canonical_signature(
    subgraph: dict[str, dict[str, EdgeLabel]],
    base_labels: dict[str, tuple[str, int, bool]],
) -> tuple:
    initial_palette = {
        label: index
        for index, label in enumerate(sorted(set(base_labels.values()), key=repr))
    }
    initial = {node: initial_palette[label] for node, label in base_labels.items()}

    def search(colors: dict[str, Color]) -> tuple:
        refined = refine_colors(subgraph, colors)
        cells: dict[int, list[str]] = {}
        for node, color in refined.items():
            cells.setdefault(color, []).append(node)

        if all(len(cell) == 1 for cell in cells.values()):
            order = [cells[color][0] for color in sorted(cells)]
            labels = tuple(base_labels[node] for node in order)
            edges: list[str] = []
            for position, left in enumerate(order):
                for right in order[position + 1 :]:
                    edges.append(subgraph[left].get(right, "0"))
            return labels, tuple(edges)

        _, cell = min(
            (
                (color, members)
                for color, members in cells.items()
                if len(members) > 1
            ),
            key=lambda item: (len(item[1]), item[0]),
        )
        candidates = []
        for chosen in cell:
            individualized = {
                node: (refined[node], node == chosen) for node in subgraph
            }
            palette = {
                label: index
                for index, label in enumerate(
                    sorted(set(individualized.values()), key=repr)
                )
            }
            candidates.append(
                search(
                    {
                        node: palette[label]
                        for node, label in individualized.items()
                    }
                )
            )
        return min(candidates)

    return search(initial)


def exact_signature_multiset(cnf: CNF, radius: int) -> Counter:
    adjacency, labels = incidence_graph(cnf)
    signatures = Counter()
    for root in adjacency:
        signatures[
            exact_canonical_signature(*rooted_ball(adjacency, labels, root, radius))
        ] += 1
    return signatures


def component_parity(negative_positions: frozenset[int]) -> int:
    return len(negative_positions) % 2


def satisfying_assignment(
    cycle_length: int,
    negative_positions: tuple[frozenset[int], frozenset[int]],
) -> dict[int, bool] | None:
    values: dict[int, bool] = {}
    offset = 0
    for marked in negative_positions:
        if component_parity(marked):
            return None
        current = False
        values[offset + 1] = current
        for edge in range(cycle_length - 1):
            if edge in marked:
                current = not current
            values[offset + edge + 2] = current
        closing_value = not current if cycle_length - 1 in marked else current
        if closing_value != values[offset + 1]:
            raise AssertionError("even parity propagation failed")
        offset += cycle_length
    return values


def formula_satisfied(cnf: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment[abs(literal)] == (literal > 0) for literal in clause)
        for clause in cnf.clauses
    )


def primal_cycle_audit(cnf: CNF, cycle_length: int) -> None:
    adjacency = {variable: set() for variable in range(1, cnf.variable_count + 1)}
    for clause in cnf.clauses:
        variables = sorted({abs(literal) for literal in clause})
        if len(variables) != 2:
            raise AssertionError("formula is not binary")
        left, right = variables
        adjacency[left].add(right)
        adjacency[right].add(left)
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise AssertionError("primal graph is not two-regular")

    unseen = set(adjacency)
    component_sizes = []
    while unseen:
        start = next(iter(unseen))
        stack = [start]
        seen = {start}
        while stack:
            node = stack.pop()
            for neighbor in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        unseen -= seen
        component_sizes.append(len(seen))
    if sorted(component_sizes) != [cycle_length, cycle_length]:
        raise AssertionError(f"unexpected primal components: {component_sizes}")


def verify_radius(radius: int) -> dict[str, int | bool]:
    sat, unsat, cycle_length = local_twin_pair(radius)
    sat_assignment = satisfying_assignment(
        cycle_length,
        (frozenset({0, cycle_length // 2}), frozenset()),
    )
    unsat_assignment = satisfying_assignment(
        cycle_length,
        (frozenset({0}), frozenset({0})),
    )
    if sat_assignment is None or not formula_satisfied(sat, sat_assignment):
        raise AssertionError("SAT member lacks the promised witness")
    if unsat_assignment is not None:
        raise AssertionError("UNSAT member passed the cycle-parity test")

    if exact_signature_multiset(sat, radius) != exact_signature_multiset(unsat, radius):
        raise AssertionError(f"local signatures differ at radius {radius}")

    primal_cycle_audit(sat, cycle_length)
    primal_cycle_audit(unsat, cycle_length)
    return {
        "radius": radius,
        "cycle_length": cycle_length,
        "variables": sat.variable_count,
        "clauses": len(sat.clauses),
        "local_multisets_equal": True,
        "sat": True,
        "unsat": True,
        "primal_treewidth_upper_bound": 2,
    }


def self_test() -> None:
    records = [verify_radius(radius) for radius in range(5)]
    print("JANUS_XOR_CYCLE_LOCAL_TWINS = PASS")
    print("VERIFIED_RADII = 0,1,2,3,4")
    print("SAT_PARITY_PATTERN = 2,0")
    print("UNSAT_PARITY_PATTERN = 1,1")
    print("EXACT_LOCAL_MULTISET_EQUALITY = true")
    print("PRIMAL_TREEWIDTH_UPPER_BOUND = 2")
    print(f"LARGEST_FIXTURE_VARIABLES = {records[-1]['variables']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--radius", type=int)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.radius is not None:
        print(verify_radius(args.radius))
        return 0
    parser.error("use --self-test or --radius R")


if __name__ == "__main__":
    raise SystemExit(main())
