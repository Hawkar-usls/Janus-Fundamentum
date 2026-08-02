#!/usr/bin/env python3
"""Exact bounded-width resolution audit for a small Tseitin contradiction."""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
from itertools import product

Clause = frozenset[int]

VERTICES = (0, 1, 2, 3)
EDGES = (
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
)
CHARGES = {0: 1, 1: 0, 2: 0, 3: 0}


def tseitin_cnf() -> set[Clause]:
    edge_variable = {
        tuple(sorted(edge)): index + 1 for index, edge in enumerate(EDGES)
    }
    clauses: set[Clause] = set()

    for vertex in VERTICES:
        incident = [
            edge_variable[tuple(sorted((vertex, neighbour)))]
            for neighbour in VERTICES
            if neighbour != vertex
        ]
        charge = CHARGES[vertex]
        for bits in product((0, 1), repeat=len(incident)):
            if sum(bits) % 2 == charge:
                continue
            clause = frozenset(
                variable if bit == 0 else -variable
                for variable, bit in zip(incident, bits, strict=True)
            )
            clauses.add(clause)

    return clauses


def bounded_resolution_closure(
    axioms: set[Clause], max_width: int
) -> tuple[bool, int]:
    known = {clause for clause in axioms if len(clause) <= max_width}
    positive: dict[int, set[Clause]] = defaultdict(set)
    negative: dict[int, set[Clause]] = defaultdict(set)

    for clause in known:
        for literal in clause:
            (positive if literal > 0 else negative)[abs(literal)].add(clause)

    queue = deque(known)
    while queue:
        clause = queue.popleft()
        if not clause:
            return True, len(known)

        for literal in tuple(clause):
            opposite_clauses = (
                negative[abs(literal)] if literal > 0 else positive[abs(literal)]
            )
            for other in tuple(opposite_clauses):
                resolvent = (clause - {literal}) | (other - {-literal})
                if len(resolvent) > max_width:
                    continue
                if any(-entry in resolvent for entry in resolvent):
                    continue
                frozen = frozenset(resolvent)
                if frozen in known:
                    continue

                known.add(frozen)
                queue.append(frozen)
                for entry in frozen:
                    (positive if entry > 0 else negative)[abs(entry)].add(frozen)

    return False, len(known)


def run() -> None:
    axioms = tseitin_cnf()
    width_three_refutes, width_three_clauses = bounded_resolution_closure(axioms, 3)
    width_four_refutes, width_four_clauses = bounded_resolution_closure(axioms, 4)

    assert len(axioms) == 16
    assert all(len(clause) == 3 for clause in axioms)
    assert not width_three_refutes
    assert width_four_refutes

    print("JANUS_TEAR_RESOLUTION_WIDTH_AUDIT = PASS")
    print(f"variables = {len(EDGES)}")
    print(f"axiom_clauses = {len(axioms)}")
    print(f"width_3_refutes = {str(width_three_refutes).lower()}")
    print(f"width_3_closure_clauses = {width_three_clauses}")
    print(f"width_4_refutes = {str(width_four_refutes).lower()}")
    print(f"width_4_closure_clauses = {width_four_clauses}")
    print("minimum_refutation_width = 4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.parse_args()
    run()
