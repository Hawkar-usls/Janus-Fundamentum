#!/usr/bin/env python3
"""Connect the two H121 toroidal Tseitin components by a SAT-neutral bridge.

The bridge uses fresh variables z,w and clauses
(x or z), (!x or z), (y or w), (!y or w), (z or w).
It is satisfiable for every endpoint assignment by z=w=1, connects the primal
components, and does not alter the original Tseitin satisfiability.

Bridge endpoints are placed farther than the tested local radius from every
charge.  Together with H121's exact local equality, this yields the separated-
feature proof of exact local equality for the connected family.
"""

from __future__ import annotations

import argparse
from collections import deque

from toroidal_tseitin_twins import (
    CNF,
    build_formula,
    charge_patterns,
    edge_endpoints,
    edge_key,
    formula_assignment,
    formula_satisfied,
    local_signature_multiset,
    primal_edges_from_cnf,
    torus_distance,
    torus_size,
)


def bridge_edge(radius: int) -> tuple[str, int, int]:
    size = torus_size(radius)
    coordinate = size // 4
    return edge_key("H", coordinate, coordinate, size)


def bridge_clearance(radius: int, charges: tuple[frozenset[tuple[int, int]], ...]) -> int:
    size = torus_size(radius)
    edge = bridge_edge(radius)
    endpoints = edge_endpoints(edge, size)
    distances = []
    for component in range(2):
        for charged in charges[component]:
            distances.append(
                min(torus_distance(endpoint, charged, size) for endpoint in endpoints)
            )
    return min(distances) if distances else size


def add_neutral_bridge(
    cnf: CNF,
    variable_ids: dict[tuple[int, tuple[str, int, int]], int],
    radius: int,
) -> tuple[CNF, int, int, int, int]:
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
    return CNF(cnf.variable_count + 2, clauses), left, right, z, w


def bridge_is_neutral() -> bool:
    for left in (False, True):
        for right in (False, True):
            z = True
            w = True
            clauses = (
                left or z,
                (not left) or z,
                right or w,
                (not right) or w,
                z or w,
            )
            if not all(clauses):
                return False
    return True


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


def verify_radius(radius: int) -> dict[str, int | bool]:
    sat_charges, unsat_charges = charge_patterns(radius)
    sat_base, sat_ids = build_formula(radius, sat_charges)
    unsat_base, unsat_ids = build_formula(radius, unsat_charges)

    sat, _, _, sat_z, sat_w = add_neutral_bridge(sat_base, sat_ids, radius)
    unsat, _, _, _, _ = add_neutral_bridge(unsat_base, unsat_ids, radius)

    assignment = formula_assignment(radius, sat_charges, sat_ids)
    if assignment is None:
        raise AssertionError("SAT base lost its assignment")
    assignment[sat_z] = True
    assignment[sat_w] = True
    if not formula_satisfied(sat, assignment):
        raise AssertionError("neutral bridge broke the SAT assignment")
    if formula_assignment(radius, unsat_charges, unsat_ids) is not None:
        raise AssertionError("UNSAT Tseitin base unexpectedly became satisfiable")

    if local_signature_multiset(radius, sat_charges) != local_signature_multiset(
        radius, unsat_charges
    ):
        raise AssertionError("H121 base local signatures differ")

    clearance = min(
        bridge_clearance(radius, sat_charges),
        bridge_clearance(radius, unsat_charges),
    )
    if clearance <= 2 * radius + 4:
        raise AssertionError("bridge and charge neighborhoods may overlap")
    if not bridge_is_neutral():
        raise AssertionError("bridge is not assignment-neutral")
    if not connected_primal(sat) or not connected_primal(unsat):
        raise AssertionError("bridged primal graph is disconnected")

    original_edges = primal_edges_from_cnf(sat_base)
    if not original_edges <= primal_edges_from_cnf(sat):
        raise AssertionError("bridge deleted an original primal edge")

    return {
        "radius": radius,
        "torus_side": torus_size(radius),
        "bridge_clearance": clearance,
        "connected": True,
        "sat": True,
        "unsat": True,
        "local_equality_by_separated_features": True,
        "published_treewidth_lower_bound": torus_size(radius) - 1,
    }


def self_test() -> None:
    records = [verify_radius(radius) for radius in range(5)]
    print("JANUS_CONNECTED_TOROIDAL_TSEITIN_TWINS = PASS")
    print("VERIFIED_RADII = 0,1,2,3,4")
    print("PRIMAL_CONNECTED = true")
    print("BRIDGE_SAT_NEUTRAL = true")
    print("EXACT_LOCAL_EQUALITY = separated-feature reduction to H121")
    print(f"LARGEST_TORUS_SIDE = {records[-1]['torus_side']}")
    print(
        "LARGEST_PUBLISHED_TREEWIDTH_LOWER_BOUND = "
        f"{records[-1]['published_treewidth_lower_bound']}"
    )


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
