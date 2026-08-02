#!/usr/bin/env python3
"""Independent adversarial audit for the JANUS Tear conjecture.

Software-only scope. No swarm or device access.

The audit independently reconstructs the toroidal Tseitin twins, verifies exact
CNF semantics, tests the SAT-neutral connector attack, distinguishes a two-bit
semantic tear from its proof-bearing certificate, and adds a second family:
a polynomially extractable 2-SAT SCC contradiction tear.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter, deque
from dataclasses import asdict, dataclass
from itertools import product
from typing import Sequence

Vertex = tuple[int, int]
EdgeKey = tuple[str, int, int]
Clause = tuple[int, ...]


@dataclass(frozen=True)
class CNF:
    variable_count: int
    clauses: tuple[Clause, ...]


def torus_size(radius: int) -> int:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    return 8 * radius + 13


def edge_key(orientation: str, x: int, y: int, size: int) -> EdgeKey:
    if orientation not in {"H", "V"}:
        raise ValueError("orientation must be H or V")
    return orientation, x % size, y % size


def all_vertices(size: int) -> list[Vertex]:
    return [(x, y) for x in range(size) for y in range(size)]


def all_edges(size: int) -> list[EdgeKey]:
    return [
        edge_key(orientation, x, y, size)
        for orientation in ("H", "V")
        for x in range(size)
        for y in range(size)
    ]


def incident_edges(vertex: Vertex, size: int) -> tuple[EdgeKey, ...]:
    x, y = vertex
    return (
        edge_key("H", x, y, size),
        edge_key("V", x, y, size),
        edge_key("H", x - 1, y, size),
        edge_key("V", x, y - 1, size),
    )


def edge_endpoints(edge: EdgeKey, size: int) -> tuple[Vertex, Vertex]:
    orientation, x, y = edge
    if orientation == "H":
        return (x, y), ((x + 1) % size, y)
    return (x, y), (x, (y + 1) % size)


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


def charge_patterns(
    radius: int,
) -> tuple[tuple[frozenset[Vertex], ...], tuple[frozenset[Vertex], ...]]:
    size = torus_size(radius)
    second = ((size - 1) // 2, 0)
    sat = (frozenset({(0, 0), second}), frozenset())
    unsat = (frozenset({(0, 0)}), frozenset({(0, 0)}))
    if torus_distance((0, 0), second, size) <= 2 * radius + 2:
        raise AssertionError("charge separation is too small")
    return sat, unsat


def forbidden_assignments(charge: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        bits
        for bits in product((0, 1), repeat=4)
        if sum(bits) % 2 != charge
    )


def build_formula(
    radius: int,
    charges: tuple[frozenset[Vertex], ...],
) -> tuple[CNF, dict[tuple[int, EdgeKey], int]]:
    size = torus_size(radius)
    variable_ids: dict[tuple[int, EdgeKey], int] = {}
    next_variable = 1
    for component in range(2):
        for edge in all_edges(size):
            variable_ids[(component, edge)] = next_variable
            next_variable += 1

    clauses: list[Clause] = []
    for component in range(2):
        for vertex in all_vertices(size):
            edge_ids = [
                variable_ids[(component, edge)]
                for edge in incident_edges(vertex, size)
            ]
            charge = int(vertex in charges[component])
            for forbidden in forbidden_assignments(charge):
                clauses.append(
                    tuple(
                        variable if bit == 0 else -variable
                        for variable, bit in zip(edge_ids, forbidden)
                    )
                )
    return CNF(next_variable - 1, tuple(clauses)), variable_ids


def component_assignment(
    size: int,
    charges: frozenset[Vertex],
) -> dict[EdgeKey, int] | None:
    if len(charges) % 2:
        return None

    root = (0, 0)
    parent: dict[Vertex, Vertex | None] = {root: None}
    parent_edge: dict[Vertex, EdgeKey] = {}
    order: list[Vertex] = []
    queue = deque([root])

    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        x, y = vertex
        neighbors = (
            (((x + 1) % size, y), edge_key("H", x, y, size)),
            (((x - 1) % size, y), edge_key("H", x - 1, y, size)),
            ((x, (y + 1) % size), edge_key("V", x, y, size)),
            ((x, (y - 1) % size), edge_key("V", x, y - 1, size)),
        )
        for neighbor, edge in neighbors:
            if neighbor in parent:
                continue
            parent[neighbor] = vertex
            parent_edge[neighbor] = edge
            queue.append(neighbor)

    values = {edge: 0 for edge in all_edges(size)}
    for vertex in reversed(order[1:]):
        p_edge = parent_edge[vertex]
        value = int(vertex in charges)
        for edge in incident_edges(vertex, size):
            if edge != p_edge:
                value ^= values[edge]
        values[p_edge] = value

    for vertex in all_vertices(size):
        actual = 0
        for edge in incident_edges(vertex, size):
            actual ^= values[edge]
        if actual != int(vertex in charges):
            raise AssertionError("spanning-tree assignment verification failed")
    return values


def formula_assignment(
    radius: int,
    charges: tuple[frozenset[Vertex], ...],
    variable_ids: dict[tuple[int, EdgeKey], int],
) -> dict[int, bool] | None:
    size = torus_size(radius)
    assignment: dict[int, bool] = {}
    for component in range(2):
        local = component_assignment(size, charges[component])
        if local is None:
            return None
        for edge, bit in local.items():
            assignment[variable_ids[(component, edge)]] = bool(bit)
    return assignment


def formula_satisfied(cnf: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment[abs(literal)] == (literal > 0) for literal in clause)
        for clause in cnf.clauses
    )


def visible_charges_for_clause(
    root: Vertex,
    charges: frozenset[Vertex],
    radius: int,
    size: int,
) -> tuple[Vertex, ...]:
    return tuple(
        sorted(
            wrapped_delta(root, charged, size)
            for charged in charges
            if 2 * torus_distance(root, charged, size) <= radius
        )
    )


def visible_charges_for_edge(
    root_edge: EdgeKey,
    charges: frozenset[Vertex],
    radius: int,
    size: int,
) -> tuple[Vertex, ...]:
    start, end = edge_endpoints(root_edge, size)
    visible: list[Vertex] = []
    for charged in charges:
        distance = 1 + 2 * min(
            torus_distance(start, charged, size),
            torus_distance(end, charged, size),
        )
        if distance <= radius:
            visible.append(wrapped_delta(start, charged, size))
    return tuple(sorted(visible))


def local_signature_multiset(
    radius: int,
    charges: tuple[frozenset[Vertex], ...],
) -> Counter:
    size = torus_size(radius)
    signatures: Counter = Counter()
    for component in range(2):
        component_charges = charges[component]
        for edge in all_edges(size):
            signatures[
                ("V", edge[0], visible_charges_for_edge(
                    edge, component_charges, radius, size
                ))
            ] += 1
        for vertex in all_vertices(size):
            charge = int(vertex in component_charges)
            visible = visible_charges_for_clause(
                vertex, component_charges, radius, size
            )
            for forbidden in forbidden_assignments(charge):
                signatures[("C", forbidden, visible)] += 1
    return signatures


def primal_edges_from_cnf(cnf: CNF) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for clause in cnf.clauses:
        variables = sorted({abs(literal) for literal in clause})
        for index, left in enumerate(variables):
            for right in variables[index + 1:]:
                result.add((left, right))
    return result


def connected_primal(cnf: CNF) -> bool:
    adjacency = {variable: set() for variable in range(1, cnf.variable_count + 1)}
    for left, right in primal_edges_from_cnf(cnf):
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = {1}
    queue = deque([1])
    while queue:
        vertex = queue.popleft()
        for neighbor in adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return len(seen) == cnf.variable_count


def bridge_edge(radius: int) -> EdgeKey:
    size = torus_size(radius)
    coordinate = size // 4
    return edge_key("H", coordinate, coordinate, size)


def add_neutral_bridge(
    cnf: CNF,
    variable_ids: dict[tuple[int, EdgeKey], int],
    radius: int,
) -> tuple[CNF, int, int]:
    endpoint = bridge_edge(radius)
    left = variable_ids[(0, endpoint)]
    right = variable_ids[(1, endpoint)]
    z = cnf.variable_count + 1
    w = cnf.variable_count + 2
    clauses = cnf.clauses + (
        (left, z),
        (-left, z),
        (right, w),
        (-right, w),
        (z, w),
    )
    return CNF(cnf.variable_count + 2, clauses), z, w


def semantic_module_tear(
    charges: tuple[frozenset[Vertex], ...],
) -> tuple[int, ...]:
    return tuple(len(component) % 2 for component in charges)


def naive_connected_tear(
    charges: tuple[frozenset[Vertex], ...],
) -> tuple[int]:
    return (sum(len(component) for component in charges) % 2,)


def verify_odd_xor_certificate(
    radius: int,
    cnf: CNF,
    variable_ids: dict[tuple[int, EdgeKey], int],
    charges: tuple[frozenset[Vertex], ...],
    component: int,
) -> bool:
    """Verify a proof-bearing odd-parity tear against the actual CNF subset."""
    if len(charges[component]) % 2 != 1:
        return False

    size = torus_size(radius)
    actual = Counter(cnf.clauses)
    expected: Counter[Clause] = Counter()
    edge_occurrences: Counter[int] = Counter()

    for vertex in all_vertices(size):
        edge_ids = [
            variable_ids[(component, edge)]
            for edge in incident_edges(vertex, size)
        ]
        charge = int(vertex in charges[component])
        for forbidden in forbidden_assignments(charge):
            clause = tuple(
                variable if bit == 0 else -variable
                for variable, bit in zip(edge_ids, forbidden)
            )
            expected[clause] += 1
        for variable in edge_ids:
            edge_occurrences[variable] += 1

    if any(actual[clause] < count for clause, count in expected.items()):
        return False
    if not all(count == 2 for count in edge_occurrences.values()):
        return False
    return True


def verify_connected_twin(radius: int) -> dict[str, object]:
    sat_charges, unsat_charges = charge_patterns(radius)
    sat_base, sat_ids = build_formula(radius, sat_charges)
    unsat_base, unsat_ids = build_formula(radius, unsat_charges)
    sat, sat_z, sat_w = add_neutral_bridge(sat_base, sat_ids, radius)
    unsat, _, _ = add_neutral_bridge(unsat_base, unsat_ids, radius)

    sat_assignment = formula_assignment(radius, sat_charges, sat_ids)
    if sat_assignment is None:
        raise AssertionError("SAT member lacks a base assignment")
    sat_assignment[sat_z] = True
    sat_assignment[sat_w] = True

    if not formula_satisfied(sat, sat_assignment):
        raise AssertionError("SAT witness recovery failed after neutral bridge")
    if formula_assignment(radius, unsat_charges, unsat_ids) is not None:
        raise AssertionError("UNSAT base unexpectedly produced an assignment")
    if not connected_primal(sat) or not connected_primal(unsat):
        raise AssertionError("neutral bridge did not connect the primal graph")
    if local_signature_multiset(radius, sat_charges) != local_signature_multiset(
        radius, unsat_charges
    ):
        raise AssertionError("exact bounded-local signature equality failed")

    sat_naive = naive_connected_tear(sat_charges)
    unsat_naive = naive_connected_tear(unsat_charges)
    sat_hidden = semantic_module_tear(sat_charges)
    unsat_hidden = semantic_module_tear(unsat_charges)

    if sat_naive != unsat_naive or sat_naive != (0,):
        raise AssertionError("expected the connector attack to erase naive parity")
    if sat_hidden == unsat_hidden:
        raise AssertionError("module-aware tear failed to distinguish the twins")
    if not all(
        verify_odd_xor_certificate(
            radius, unsat, unsat_ids, unsat_charges, component
        )
        for component in (0, 1)
    ):
        raise AssertionError("proof-bearing odd parity certificate failed")

    size = torus_size(radius)
    return {
        "radius": radius,
        "torus_side": size,
        "variables_connected": sat.variable_count,
        "clauses_connected": len(sat.clauses),
        "exact_local_multisets_equal": True,
        "primal_connected": True,
        "sat_witness_recovered": True,
        "unsat_odd_module_certificate_verified": True,
        "naive_connected_tear_sat": sat_naive,
        "naive_connected_tear_unsat": unsat_naive,
        "naive_connected_tear_distinguishes": False,
        "module_aware_tear_sat": sat_hidden,
        "module_aware_tear_unsat": unsat_hidden,
        "module_aware_tear_distinguishes": True,
        "semantic_payload_bits": 2,
        "certificate_vertex_equations": 2 * size * size,
        "certificate_clause_references": 16 * size * size,
        "state_merge_count_measured": False,
    }


def literal_node(literal: int) -> int:
    variable = abs(literal) - 1
    return 2 * variable + (0 if literal > 0 else 1)


def negate_node(node: int) -> int:
    return node ^ 1


def node_literal(node: int) -> int:
    variable = node // 2 + 1
    return variable if node % 2 == 0 else -variable


@dataclass
class TwoSatResult:
    status: str
    assignment: dict[int, bool] | None
    contradiction_variable: int | None
    path_positive_to_negative: list[int] | None
    path_negative_to_positive: list[int] | None


def build_implication_graph(
    variable_count: int,
    clauses: Sequence[tuple[int, int]],
) -> tuple[list[list[int]], list[list[int]]]:
    graph = [[] for _ in range(2 * variable_count)]
    reverse = [[] for _ in range(2 * variable_count)]

    for left, right in clauses:
        if not (
            1 <= abs(left) <= variable_count
            and 1 <= abs(right) <= variable_count
        ):
            raise ValueError("2-SAT literal outside variable range")
        edges = (
            (negate_node(literal_node(left)), literal_node(right)),
            (negate_node(literal_node(right)), literal_node(left)),
        )
        for source, target in edges:
            graph[source].append(target)
            reverse[target].append(source)
    return graph, reverse


def kosaraju_scc(graph: list[list[int]], reverse: list[list[int]]) -> list[int]:
    seen = [False] * len(graph)
    order: list[int] = []

    def dfs1(start: int) -> None:
        stack: list[tuple[int, int]] = [(start, 0)]
        seen[start] = True
        while stack:
            vertex, next_index = stack[-1]
            if next_index < len(graph[vertex]):
                neighbor = graph[vertex][next_index]
                stack[-1] = (vertex, next_index + 1)
                if not seen[neighbor]:
                    seen[neighbor] = True
                    stack.append((neighbor, 0))
            else:
                order.append(vertex)
                stack.pop()

    for vertex in range(len(graph)):
        if not seen[vertex]:
            dfs1(vertex)

    component = [-1] * len(graph)

    def dfs2(start: int, component_id: int) -> None:
        stack = [start]
        component[start] = component_id
        while stack:
            vertex = stack.pop()
            for neighbor in reverse[vertex]:
                if component[neighbor] == -1:
                    component[neighbor] = component_id
                    stack.append(neighbor)

    component_id = 0
    for vertex in reversed(order):
        if component[vertex] == -1:
            dfs2(vertex, component_id)
            component_id += 1
    return component


def path_within_component(
    graph: list[list[int]],
    component: list[int],
    source: int,
    target: int,
) -> list[int]:
    required = component[source]
    parent: dict[int, int | None] = {source: None}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        if vertex == target:
            break
        for neighbor in graph[vertex]:
            if component[neighbor] != required or neighbor in parent:
                continue
            parent[neighbor] = vertex
            queue.append(neighbor)
    if target not in parent:
        raise AssertionError("SCC path reconstruction failed")
    path: list[int] = []
    cursor: int | None = target
    while cursor is not None:
        path.append(cursor)
        cursor = parent[cursor]
    path.reverse()
    return path


def solve_2sat(
    variable_count: int,
    clauses: Sequence[tuple[int, int]],
) -> TwoSatResult:
    graph, reverse = build_implication_graph(variable_count, clauses)
    component = kosaraju_scc(graph, reverse)

    for variable in range(1, variable_count + 1):
        positive = literal_node(variable)
        negative = literal_node(-variable)
        if component[positive] == component[negative]:
            return TwoSatResult(
                status="UNSAT",
                assignment=None,
                contradiction_variable=variable,
                path_positive_to_negative=[
                    node_literal(node)
                    for node in path_within_component(
                        graph, component, positive, negative
                    )
                ],
                path_negative_to_positive=[
                    node_literal(node)
                    for node in path_within_component(
                        graph, component, negative, positive
                    )
                ],
            )

    assignment = {
        variable: component[literal_node(variable)]
        > component[literal_node(-variable)]
        for variable in range(1, variable_count + 1)
    }
    if not two_sat_assignment_satisfies(clauses, assignment):
        assignment = {
            variable: not value for variable, value in assignment.items()
        }
    if not two_sat_assignment_satisfies(clauses, assignment):
        raise AssertionError("2-SAT witness recovery failed")
    return TwoSatResult("SAT", assignment, None, None, None)


def two_sat_assignment_satisfies(
    clauses: Sequence[tuple[int, int]],
    assignment: dict[int, bool],
) -> bool:
    def value(literal: int) -> bool:
        result = assignment[abs(literal)]
        return result if literal > 0 else not result

    return all(value(left) or value(right) for left, right in clauses)


def verify_2sat_unsat_tear(
    variable_count: int,
    clauses: Sequence[tuple[int, int]],
    result: TwoSatResult,
) -> bool:
    if (
        result.status != "UNSAT"
        or result.contradiction_variable is None
        or result.path_positive_to_negative is None
        or result.path_negative_to_positive is None
    ):
        return False

    graph, _ = build_implication_graph(variable_count, clauses)
    edge_set = {
        (node_literal(source), node_literal(target))
        for source, neighbors in enumerate(graph)
        for target in neighbors
    }

    def path_valid(path: list[int]) -> bool:
        return all(
            (left, right) in edge_set
            for left, right in zip(path, path[1:])
        )

    variable = result.contradiction_variable
    return (
        result.path_positive_to_negative[0] == variable
        and result.path_positive_to_negative[-1] == -variable
        and result.path_negative_to_positive[0] == -variable
        and result.path_negative_to_positive[-1] == variable
        and path_valid(result.path_positive_to_negative)
        and path_valid(result.path_negative_to_positive)
    )


def brute_force_2sat(
    variable_count: int,
    clauses: Sequence[tuple[int, int]],
) -> tuple[bool, dict[int, bool] | None]:
    for bits in product((False, True), repeat=variable_count):
        assignment = {index + 1: bit for index, bit in enumerate(bits)}
        if two_sat_assignment_satisfies(clauses, assignment):
            return True, assignment
    return False, None


def random_2sat_fuzz(
    seed: int = 9379992,
    cases: int = 300,
) -> dict[str, int]:
    rng = random.Random(seed)
    sat_count = 0
    unsat_count = 0
    for _ in range(cases):
        variable_count = rng.randint(1, 8)
        clause_count = rng.randint(0, 4 * variable_count + 4)
        clauses = []
        for _ in range(clause_count):
            left_var = rng.randint(1, variable_count)
            right_var = rng.randint(1, variable_count)
            left = left_var if rng.random() < 0.5 else -left_var
            right = right_var if rng.random() < 0.5 else -right_var
            clauses.append((left, right))

        exact_sat, _ = brute_force_2sat(variable_count, clauses)
        result = solve_2sat(variable_count, clauses)
        if (result.status == "SAT") != exact_sat:
            raise AssertionError("2-SAT SCC result disagrees with brute force")
        if result.status == "SAT":
            sat_count += 1
            if result.assignment is None or not two_sat_assignment_satisfies(
                clauses, result.assignment
            ):
                raise AssertionError("invalid 2-SAT SAT witness")
        else:
            unsat_count += 1
            if not verify_2sat_unsat_tear(
                variable_count, clauses, result
            ):
                raise AssertionError("invalid 2-SAT contradiction tear")
    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "seed": seed,
    }


def local_sensitivity_test() -> dict[str, bool]:
    """Ensure local-equality PASS is not produced by a broken comparator."""
    radius = 3
    size = torus_size(radius)
    far = ((size - 1) // 2, 0)
    near = (1, 0)
    separated = (frozenset({(0, 0), far}), frozenset())
    split = (frozenset({(0, 0)}), frozenset({(0, 0)}))
    collided = (frozenset({(0, 0), near}), frozenset())
    return {
        "separated_equals_split": (
            local_signature_multiset(radius, separated)
            == local_signature_multiset(radius, split)
        ),
        "collided_differs_from_split": (
            local_signature_multiset(radius, collided)
            != local_signature_multiset(radius, split)
        ),
    }


def run_audit(max_radius: int = 8) -> dict[str, object]:
    if max_radius < 0:
        raise ValueError("max_radius must be nonnegative")

    connected_records = [
        verify_connected_twin(radius)
        for radius in range(max_radius + 1)
    ]
    sensitivity = local_sensitivity_test()
    if sensitivity != {
        "separated_equals_split": True,
        "collided_differs_from_split": True,
    }:
        raise AssertionError("local-signature sensitivity control failed")

    sat_2cnf = ((1, 2), (-1, 2), (1, -2))
    unsat_2cnf = ((1, 1), (-1, -1))
    sat_result = solve_2sat(2, sat_2cnf)
    unsat_result = solve_2sat(1, unsat_2cnf)
    if sat_result.status != "SAT":
        raise AssertionError("crafted SAT 2-CNF rejected")
    if not verify_2sat_unsat_tear(1, unsat_2cnf, unsat_result):
        raise AssertionError("crafted UNSAT 2-CNF tear rejected")

    fuzz = random_2sat_fuzz()

    return {
        "artifact": "JANUS-TEAR-ADVERSARIAL-AUDIT",
        "software_only": True,
        "swarm_touched": False,
        "devices_touched": False,
        "verified_radii": list(range(max_radius + 1)),
        "tseitin_connected_twin_records": connected_records,
        "local_sensitivity_control": sensitivity,
        "two_sat_second_positive_family": {
            "status": "PASS",
            "tear": (
                "two implication paths x -> not x and not x -> x "
                "inside one SCC"
            ),
            "polynomial_extraction": True,
            "polynomial_verification": True,
            "sat_witness_recovery": True,
            "crafted_sat": asdict(sat_result),
            "crafted_unsat": asdict(unsat_result),
            "fuzz": fuzz,
        },
        "attacks": {
            "naive_connected_component_parity": "REJECTED",
            "reason": (
                "The SAT-neutral connector makes the primal graph connected "
                "and both total charge parities equal zero."
            ),
            "module_aware_parity": "CONDITIONAL_PASS",
            "condition": (
                "A decomposition witness or polynomial extractor must identify "
                "the hidden Tseitin modules under arbitrary neutral glue."
            ),
            "tiny_payload_equals_tiny_proof": "REJECTED",
            "reason_proof_size": (
                "The semantic payload is two bits, but the independently checked "
                "derivation references a linear number of equations/clauses."
            ),
            "actual_residual_state_merge_count": "NOT_MEASURED",
            "universal_polynomial_quotient": "NOT_ESTABLISHED",
        },
        "verdict": (
            "The Tear language survives as a proof-learning framework and works "
            "exactly on Tseitin and 2-SAT families. The connector attack sharpens "
            "the missing theorem from 'find parity' to 'discover a sound semantic "
            "module decomposition and witness-recovery map in polynomial total work'."
        ),
    }


def self_test() -> None:
    result = run_audit()
    print("JANUS_TEAR_ADVERSARIAL_AUDIT = PASS")
    print("SOFTWARE_ONLY = true")
    print("SWARM_TOUCHED = false")
    print("DEVICES_TOUCHED = false")
    print("VERIFIED_RADII = 0,1,2,3,4,5,6,7,8")
    print("EXACT_CNF_AND_LOCAL_TWIN_CHECKS = PASS")
    print("SAT_NEUTRAL_CONNECTOR_ATTACK = PASS")
    print("NAIVE_CONNECTED_COMPONENT_TEAR = REJECTED")
    print("MODULE_AWARE_TEAR = CONDITIONAL_PASS")
    print("PROOF_BEARING_TEAR_SIZE = LINEAR_CERTIFICATE")
    print("TWO_SAT_SCC_TEAR = PASS")
    print(
        "TWO_SAT_FUZZ_CASES = "
        f"{result['two_sat_second_positive_family']['fuzz']['cases']}"
    )
    print("UNIVERSAL_POLYNOMIAL_QUOTIENT = OPEN")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max-radius", type=int, default=8)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    result = run_audit(args.max_radius)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
