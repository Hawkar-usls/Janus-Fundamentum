#!/usr/bin/env python3
"""Exact high-treewidth local SAT/UNSAT twins from toroidal Tseitin formulas.

For every fixed incidence radius R, build two formulas on two disjoint copies of
an m x m toroidal grid, m = 8R + 13.  Edge variables satisfy one parity equation
at every grid vertex.

SAT member charge counts by connected component:   (2, 0)
UNSAT member charge counts by connected component: (1, 1)

A connected Tseitin system is satisfiable exactly when its total charge is even.
The two marked vertices are farther apart than any radius-R incidence view, so
the complete translation-normalized local signature multisets are identical.
The primal graph is the disjoint union of two line graphs of the toroidal grid.
Known treewidth transfer bounds therefore give treewidth at least m - 1.

The executable checks exact CNF semantics, an explicit SAT assignment, the odd
charge obstruction, the local signature equality, and the line-graph identity.
The published treewidth theorems remain external mathematical dependencies.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[tuple[int, ...], ...]


Vertex = tuple[int, int]
EdgeKey = tuple[str, int, int]
NodeKey = tuple


def torus_size(radius: int) -> int:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    return 8 * radius + 13


def add(vertex: Vertex, delta: Vertex, size: int) -> Vertex:
    return ((vertex[0] + delta[0]) % size, (vertex[1] + delta[1]) % size)


def wrapped_delta(source: Vertex, target: Vertex, size: int) -> Vertex:
    def one(value: int) -> int:
        value %= size
        if value > size // 2:
            value -= size
        return value

    return one(target[0] - source[0]), one(target[1] - source[1])


def torus_distance(left: Vertex, right: Vertex, size: int) -> int:
    dx, dy = wrapped_delta(left, right, size)
    return abs(dx) + abs(dy)


def edge_key(orientation: str, x: int, y: int, size: int) -> EdgeKey:
    if orientation not in {"H", "V"}:
        raise ValueError("orientation must be H or V")
    return orientation, x % size, y % size


def incident_edges(vertex: Vertex, size: int) -> tuple[EdgeKey, ...]:
    x, y = vertex
    # Fixed translation-invariant order: east, north, west, south.
    return (
        edge_key("H", x, y, size),
        edge_key("V", x, y, size),
        edge_key("H", x - 1, y, size),
        edge_key("V", x, y - 1, size),
    )


def edge_endpoints(edge: EdgeKey, size: int) -> tuple[Vertex, Vertex]:
    orientation, x, y = edge
    start = (x, y)
    if orientation == "H":
        return start, ((x + 1) % size, y)
    return start, (x, (y + 1) % size)


def all_vertices(size: int) -> list[Vertex]:
    return [(x, y) for x in range(size) for y in range(size)]


def all_edges(size: int) -> list[EdgeKey]:
    return [
        edge_key(orientation, x, y, size)
        for orientation in ("H", "V")
        for x in range(size)
        for y in range(size)
    ]


def charge_patterns(radius: int) -> tuple[tuple[frozenset[Vertex], ...], tuple[frozenset[Vertex], ...]]:
    size = torus_size(radius)
    second = ((size - 1) // 2, 0)
    sat = (frozenset({(0, 0), second}), frozenset())
    unsat = (frozenset({(0, 0)}), frozenset({(0, 0)}))
    if torus_distance((0, 0), second, size) <= 2 * radius + 2:
        raise AssertionError("charge separation is too small")
    return sat, unsat


def forbidden_assignments(charge: int) -> tuple[tuple[int, ...], ...]:
    return tuple(bits for bits in product((0, 1), repeat=4) if sum(bits) % 2 != charge)


def build_formula(radius: int, charges: tuple[frozenset[Vertex], ...]) -> tuple[CNF, dict[tuple[int, EdgeKey], int]]:
    size = torus_size(radius)
    variable_ids: dict[tuple[int, EdgeKey], int] = {}
    next_variable = 1
    for component in range(2):
        for edge in all_edges(size):
            variable_ids[(component, edge)] = next_variable
            next_variable += 1

    clauses: list[tuple[int, ...]] = []
    for component in range(2):
        for vertex in all_vertices(size):
            edge_ids = [variable_ids[(component, edge)] for edge in incident_edges(vertex, size)]
            charge = 1 if vertex in charges[component] else 0
            for forbidden in forbidden_assignments(charge):
                # Exclude exactly the forbidden local assignment.
                clause = tuple(
                    variable if bit == 0 else -variable
                    for variable, bit in zip(edge_ids, forbidden)
                )
                clauses.append(clause)
    return CNF(next_variable - 1, tuple(clauses)), variable_ids


def component_assignment(size: int, charges: frozenset[Vertex]) -> dict[EdgeKey, int] | None:
    if len(charges) % 2:
        return None

    vertices = all_vertices(size)
    root = (0, 0)
    parent: dict[Vertex, Vertex | None] = {root: None}
    parent_edge: dict[Vertex, EdgeKey] = {}
    order: list[Vertex] = []
    queue = deque([root])
    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        x, y = vertex
        neighbors = [
            (((x + 1) % size, y), edge_key("H", x, y, size)),
            (((x - 1) % size, y), edge_key("H", x - 1, y, size)),
            ((x, (y + 1) % size), edge_key("V", x, y, size)),
            ((x, (y - 1) % size), edge_key("V", x, y - 1, size)),
        ]
        for neighbor, edge in neighbors:
            if neighbor in parent:
                continue
            parent[neighbor] = vertex
            parent_edge[neighbor] = edge
            queue.append(neighbor)

    values = {edge: 0 for edge in all_edges(size)}
    for vertex in reversed(order[1:]):
        p_edge = parent_edge[vertex]
        xor_without_parent = 0
        for edge in incident_edges(vertex, size):
            if edge != p_edge:
                xor_without_parent ^= values[edge]
        values[p_edge] = xor_without_parent ^ (1 if vertex in charges else 0)

    root_xor = 0
    for edge in incident_edges(root, size):
        root_xor ^= values[edge]
    if root_xor != (1 if root in charges else 0):
        raise AssertionError("even-charge spanning-tree construction failed")
    return values


def formula_assignment(radius: int, charges: tuple[frozenset[Vertex], ...], variable_ids: dict[tuple[int, EdgeKey], int]) -> dict[int, bool] | None:
    size = torus_size(radius)
    result: dict[int, bool] = {}
    for component in range(2):
        local = component_assignment(size, charges[component])
        if local is None:
            return None
        for edge, bit in local.items():
            result[variable_ids[(component, edge)]] = bool(bit)
    return result


def formula_satisfied(cnf: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment[abs(literal)] == (literal > 0) for literal in clause)
        for clause in cnf.clauses
    )


def visible_charges_for_clause(root: Vertex, charges: frozenset[Vertex], radius: int, size: int) -> tuple[Vertex, ...]:
    visible = []
    for charged in charges:
        if 2 * torus_distance(root, charged, size) <= radius:
            visible.append(wrapped_delta(root, charged, size))
    return tuple(sorted(visible))


def visible_charges_for_edge(root_edge: EdgeKey, charges: frozenset[Vertex], radius: int, size: int) -> tuple[Vertex, ...]:
    start, end = edge_endpoints(root_edge, size)
    visible = []
    for charged in charges:
        distance = 1 + 2 * min(
            torus_distance(start, charged, size),
            torus_distance(end, charged, size),
        )
        if distance <= radius:
            visible.append(wrapped_delta(start, charged, size))
    return tuple(sorted(visible))


def local_signature_multiset(radius: int, charges: tuple[frozenset[Vertex], ...]) -> Counter:
    """Return a translation-normalized signature finer than rooted-ball isomorphism.

    The uncharged torus CNF is translation invariant.  A radius-R incidence ball
    is therefore determined by the root subtype and the translated charged
    vertices whose clause gadgets occur in that ball.  Charge separation ensures
    that no signature contains two charges in the SAT member.
    """

    size = torus_size(radius)
    signatures: Counter = Counter()
    for component in range(2):
        component_charges = charges[component]
        for edge in all_edges(size):
            orientation, _, _ = edge
            signature = (
                "V",
                orientation,
                visible_charges_for_edge(edge, component_charges, radius, size),
            )
            signatures[signature] += 1

        for vertex in all_vertices(size):
            charge = 1 if vertex in component_charges else 0
            visible = visible_charges_for_clause(vertex, component_charges, radius, size)
            for forbidden in forbidden_assignments(charge):
                signature = ("C", forbidden, visible)
                signatures[signature] += 1
    return signatures


def primal_edges_from_cnf(cnf: CNF) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for clause in cnf.clauses:
        variables = sorted({abs(literal) for literal in clause})
        for left_index, left in enumerate(variables):
            for right in variables[left_index + 1 :]:
                edges.add((left, right))
    return edges


def line_graph_edges(size: int, variable_ids: dict[tuple[int, EdgeKey], int]) -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for component in range(2):
        for vertex in all_vertices(size):
            identifiers = sorted(variable_ids[(component, edge)] for edge in incident_edges(vertex, size))
            for left_index, left in enumerate(identifiers):
                for right in identifiers[left_index + 1 :]:
                    edges.add((left, right))
    return edges


def verify_radius(radius: int) -> dict[str, int | bool]:
    size = torus_size(radius)
    sat_charges, unsat_charges = charge_patterns(radius)
    sat_cnf, sat_ids = build_formula(radius, sat_charges)
    unsat_cnf, unsat_ids = build_formula(radius, unsat_charges)

    sat_assignment = formula_assignment(radius, sat_charges, sat_ids)
    if sat_assignment is None or not formula_satisfied(sat_cnf, sat_assignment):
        raise AssertionError("SAT member lacks the promised exact assignment")
    if formula_assignment(radius, unsat_charges, unsat_ids) is not None:
        raise AssertionError("odd-charge UNSAT member unexpectedly has an assignment")

    if local_signature_multiset(radius, sat_charges) != local_signature_multiset(radius, unsat_charges):
        raise AssertionError(f"local signature multisets differ at radius {radius}")

    if primal_edges_from_cnf(sat_cnf) != line_graph_edges(size, sat_ids):
        raise AssertionError("SAT primal graph is not the expected line graph")
    if primal_edges_from_cnf(unsat_cnf) != line_graph_edges(size, unsat_ids):
        raise AssertionError("UNSAT primal graph is not the expected line graph")

    return {
        "radius": radius,
        "torus_side": size,
        "variables": sat_cnf.variable_count,
        "clauses": len(sat_cnf.clauses),
        "local_multisets_equal": True,
        "sat_component_charges": (2, 0),
        "unsat_component_charges": (1, 1),
        "primal_is_two_line_graphs": True,
        "published_treewidth_lower_bound": size - 1,
    }


def self_test() -> None:
    records = [verify_radius(radius) for radius in range(5)]
    print("JANUS_TOROIDAL_TSEITIN_LOCAL_TWINS = PASS")
    print("VERIFIED_RADII = 0,1,2,3,4")
    print("SAT_COMPONENT_CHARGES = 2,0")
    print("UNSAT_COMPONENT_CHARGES = 1,1")
    print("EXACT_TRANSLATION_NORMALIZED_LOCAL_EQUALITY = true")
    print("PRIMAL_GRAPH = TWO_COPIES_OF_LINE_GRAPH_TOROIDAL_GRID")
    print(f"LARGEST_TORUS_SIDE = {records[-1]['torus_side']}")
    print(f"LARGEST_PUBLISHED_TREEWIDTH_LOWER_BOUND = {records[-1]['published_treewidth_lower_bound']}")


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
