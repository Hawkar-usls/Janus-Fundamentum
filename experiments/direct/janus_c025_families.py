"""C025 frozen formula families and Resolution certificates."""
from __future__ import annotations
import itertools
import random
from dataclasses import dataclass
from typing import Any
from janus_c025_core import *


def absorption_family(n: int) -> tuple[CNF, list[int], list[int], list[int]]:
    x = list(range(1, n + 1))
    y = list(range(n + 1, 2 * n + 1))
    z = list(range(2 * n + 1, 3 * n + 1))
    clauses = []
    for xv, yv, zv in zip(x, y, z):
        clauses.append((xv, yv))
        clauses.append((-xv, yv))
        clauses.append((xv, yv, zv))
    return canonical_cnf(clauses), x, y, z


def equality_family(n: int) -> tuple[CNF, list[int], list[int]]:
    x = list(range(1, n + 1))
    y = list(range(n + 1, 2 * n + 1))
    clauses = []
    for xv, yv in zip(x, y):
        clauses.append((-xv, yv))
        clauses.append((xv, -yv))
    return canonical_cnf(clauses), x, y


def implication_chain(n: int) -> CNF:
    clauses = [(1,)]
    for variable in range(1, n):
        clauses.append((-variable, variable + 1))
    return canonical_cnf(clauses)


def random_3cnf(rng: random.Random, n: int, m: int) -> CNF:
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        clause = canonical_clause(variable if rng.random() < 0.5 else -variable for variable in chosen)
        assert clause is not None
        clauses.append(clause)
    return canonical_cnf(clauses)


def planted_3cnf(rng: random.Random, n: int, m: int) -> tuple[CNF, dict[int, bool]]:
    planted = {v: bool(rng.getrandbits(1)) for v in range(1, n + 1)}
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        literals = [v if rng.random() < 0.5 else -v for v in chosen]
        if not any(planted[abs(lit)] == (lit > 0) for lit in literals):
            v = chosen[0]
            literals[0] = v if planted[v] else -v
        clause = canonical_clause(literals)
        assert clause is not None
        clauses.append(clause)
    formula = canonical_cnf(clauses)
    assert satisfies(formula, planted)
    return formula, planted


def complete_unsat_3core() -> CNF:
    clauses = []
    for bits in itertools.product((False, True), repeat=3):
        clause = canonical_clause(-index if bits[index - 1] else index for index in range(1, 4))
        assert clause is not None
        clauses.append(clause)
    return canonical_cnf(clauses)


@dataclass(frozen=True)
class ResolutionStep:
    derived: Clause
    left_index: int
    right_index: int
    pivot: int


@dataclass
class ResolutionProof:
    initial: CNF
    steps: list[ResolutionStep]
    empty_index: int | None
    pair_attempts: int


def resolve_pair(left: Clause, right: Clause, pivot: int) -> Clause | None:
    if pivot not in left or -pivot not in right:
        return None
    raw = [lit for lit in left if lit != pivot]
    raw.extend(lit for lit in right if lit != -pivot)
    return canonical_clause(raw)


def generate_resolution_refutation(formula: CNF, clause_budget: int = 5000) -> ResolutionProof:
    clauses = list(canonical_cnf(formula))
    index_of = {clause: i for i, clause in enumerate(clauses)}
    steps: list[ResolutionStep] = []
    attempts = 0
    cursor = 0
    while cursor < len(clauses):
        left = clauses[cursor]
        for right_index in range(cursor):
            right = clauses[right_index]
            for literal in left:
                pivot = abs(literal)
                if literal > 0 and -pivot in right:
                    oriented_left, oriented_right = left, right
                    left_index, r_index = cursor, right_index
                elif literal < 0 and pivot in right:
                    oriented_left, oriented_right = right, left
                    left_index, r_index = right_index, cursor
                else:
                    continue
                attempts += 1
                resolvent = resolve_pair(oriented_left, oriented_right, pivot)
                if resolvent is None or resolvent in index_of:
                    continue
                if len(clauses) >= clause_budget:
                    return ResolutionProof(canonical_cnf(formula), steps, None, attempts)
                new_index = len(clauses)
                clauses.append(resolvent)
                index_of[resolvent] = new_index
                steps.append(ResolutionStep(resolvent, left_index, r_index, pivot))
                if resolvent == ():
                    proof = ResolutionProof(canonical_cnf(formula), steps, new_index, attempts)
                    if not verify_resolution_proof(proof):
                        raise AssertionError("generated resolution proof failed")
                    return proof
        cursor += 1
    return ResolutionProof(canonical_cnf(formula), steps, None, attempts)


def verify_resolution_proof(proof: ResolutionProof) -> bool:
    clauses = list(proof.initial)
    for step in proof.steps:
        if not (0 <= step.left_index < len(clauses)) or not (0 <= step.right_index < len(clauses)):
            return False
        expected = resolve_pair(clauses[step.left_index], clauses[step.right_index], step.pivot)
        if expected != step.derived:
            return False
        clauses.append(step.derived)
    if proof.empty_index is None:
        return () not in clauses
    return 0 <= proof.empty_index < len(clauses) and clauses[proof.empty_index] == ()
