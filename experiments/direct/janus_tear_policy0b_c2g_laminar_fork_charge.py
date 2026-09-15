#!/usr/bin/env python3
"""Provider replay for C025-C2G v1.2 laminar fork-charge mechanics.

Finite replay only.  It imports the already-frozen Policy-0B.1 provider
primitive so the nested-fork witness uses the exact same preprocessing rules.
"""
from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from itertools import product
from pathlib import Path

BASE_PATH = Path(__file__).with_name("janus_tear_policy0b1_total_machine.py")
spec = importlib.util.spec_from_file_location("policy0b1", BASE_PATH)
assert spec and spec.loader
policy0b1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy0b1)

Clause = tuple[int, ...]


def falsifying_req(clause: Clause) -> dict[int, int]:
    req: dict[int, int] = {}
    for lit in clause:
        var = abs(lit)
        value = 0 if lit > 0 else 1
        if var in req and req[var] != value:
            raise ValueError("tautological clause")
        req[var] = value
    return req


def cubes_disjoint(c: Clause, d: Clause) -> bool:
    rc, rd = falsifying_req(c), falsifying_req(d)
    return any(var in rd and rd[var] != value for var, value in rc.items())


def cube_subset(c: Clause, d: Clause) -> bool:
    """Q(c) subseteq Q(d) iff literals(d) subseteq literals(c)."""
    return set(d) <= set(c)


def laminar_pair(c: Clause, d: Clause) -> bool:
    return cubes_disjoint(c, d) or cube_subset(c, d) or cube_subset(d, c)


def prefix_clause(bits: tuple[int, ...]) -> Clause:
    # Clause falsified exactly when prefix variables take `bits`.
    return tuple(i + 1 if bit == 0 else -(i + 1) for i, bit in enumerate(bits))


def laminar_prefix_family(w: int) -> list[Clause]:
    family: list[Clause] = []
    for depth in range(w + 1):
        for bits in product((0, 1), repeat=depth):
            family.append(prefix_clause(bits))
    return family


def test_laminar_relations_and_count() -> None:
    assert cubes_disjoint((1, 2), (-1, 3))
    assert not cubes_disjoint((1,), (1, 2))
    assert cube_subset((1, 2), (1,))
    assert not cube_subset((1,), (1, 2))
    assert not laminar_pair((1, 2), (2, 3))  # crossing overlap

    for w in range(1, 8):
        family = laminar_prefix_family(w)
        assert len(set(family)) == len(family)
        for i, c in enumerate(family):
            for d in family[i + 1 :]:
                assert laminar_pair(c, d)
        assert len(family) == 2 ** (w + 1) - 1
        assert len(family) <= (w + 1) * 2**w


def parity_constraint(vars_: tuple[int, ...], bit: int) -> list[Clause]:
    clauses: list[Clause] = []
    for values in product((0, 1), repeat=len(vars_)):
        if sum(values) % 2 == bit:
            continue
        # Unique clause falsified by this forbidden row assignment.
        clauses.append(
            tuple(var if value == 0 else -var for var, value in zip(vars_, values))
        )
    return clauses


def k4_tseitin_odd_cnf():
    # Edge ids: AB=1, AC=2, AD=3, BC=4, BD=5, CD=6.
    incidence = {
        "A": (1, 2, 3),
        "B": (1, 4, 5),
        "C": (2, 4, 6),
        "D": (3, 5, 6),
    }
    charge = {"A": 1, "B": 0, "C": 0, "D": 0}
    clauses: list[Clause] = []
    for vertex in ("A", "B", "C", "D"):
        clauses.extend(parity_constraint(incidence[vertex], charge[vertex]))
    return policy0b1.canonical_cnf(clauses)


def eval_cnf(cnf, assignment):
    return all(
        any(assignment[abs(l)] if l > 0 else 1 - assignment[abs(l)] for l in clause)
        for clause in cnf
    )


@dataclass(frozen=True)
class TraceNode:
    status: str
    var: int | None = None
    children: tuple["TraceNode", ...] = ()


def exact_trace(active, rho: dict[int, int]) -> TraceNode:
    conflict, residual, propagated, _ = policy0b1.preprocess(active, rho)
    if conflict:
        return TraceNode("UNSAT")
    if not residual:
        return TraceNode("SAT")
    remaining = sorted(
        {
            abs(l)
            for clause in residual
            for l in clause
            if abs(l) not in propagated
        }
    )
    assert remaining
    var = remaining[0]

    rho0 = dict(propagated)
    rho0[var] = 0
    child0 = exact_trace(residual, rho0)
    if child0.status == "SAT":
        return TraceNode("SAT", var, (child0,))

    rho1 = dict(propagated)
    rho1[var] = 1
    child1 = exact_trace(residual, rho1)
    if child1.status == "SAT":
        return TraceNode("SAT", var, (child0, child1))
    return TraceNode("UNSAT", var, (child0, child1))


def count_binary_forks(node: TraceNode) -> int:
    return (1 if len(node.children) == 2 else 0) + sum(
        count_binary_forks(child) for child in node.children
    )


def test_k4_nested_fork() -> None:
    cnf = k4_tseitin_odd_cnf()
    assert len(cnf) == 16
    assert sum(map(len, cnf)) == 48

    # Independent finite UNSAT check.
    for bits in product((0, 1), repeat=6):
        assert not eval_cnf(cnf, dict(zip(range(1, 7), bits)))

    root_conflict, root_residual, root_rho, _ = policy0b1.preprocess(cnf, {})
    assert not root_conflict
    root_remaining = sorted(
        {abs(l) for c in root_residual for l in c if abs(l) not in root_rho}
    )
    assert root_remaining[0] == 1

    rho0 = dict(root_rho)
    rho0[1] = 0
    child_conflict, child_residual, child_rho, _ = policy0b1.preprocess(root_residual, rho0)
    assert not child_conflict
    child_remaining = sorted(
        {abs(l) for c in child_residual for l in c if abs(l) not in child_rho}
    )
    assert child_remaining[0] == 2

    trace = exact_trace(cnf, {})
    assert trace.status == "UNSAT"
    assert trace.var == 1 and len(trace.children) == 2
    false_subtree = trace.children[0]
    assert false_subtree.status == "UNSAT"
    assert false_subtree.var == 2 and len(false_subtree.children) == 2
    assert count_binary_forks(trace) >= 2


def main() -> None:
    test_laminar_relations_and_count()
    test_k4_nested_fork()
    print("C025_C2G_V1_1_PAIRWISE_DISJOINT_NESTED_FORK_RULE = REFUTED_FINITE_K4_WITNESS")
    print("C025_C2G_V1_2_LAMINAR_RELATION_CHECK = PASS")
    print("C025_C2G_V1_2_LAMINAR_PREFIX_FAMILY_COUNT = PASS")
    print("C025_C2G_V1_2_K4_ROOT_FORK_VAR = 1")
    print("C025_C2G_V1_2_K4_NESTED_FALSE_SUBTREE_FORK_VAR = 2")
    print("C025_C2G_V1_2_LAMINAR_WIDTH_COUNT_THEOREM = ANALYTICAL_SUFFICIENT_CONDITION")
    print("C025_C2G_V1_2_UNIVERSAL_SHORT_LAMINAR_REASON = OPEN")
    print("C025_C2G_V1_2_CLAIM_CEILING = FINITE_MECHANICS_ONLY")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
