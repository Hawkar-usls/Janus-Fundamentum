"""C023 deterministic SAT, Horn, and affine fixtures."""
from __future__ import annotations
import itertools
import random
from typing import Any
from janus_c023_primitives import *
from janus_c023_affine import *
from janus_c023_solver import *

# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

def random_horn_clause(
    rng: random.Random,
    variables: list[int],
    max_width: int = 4,
) -> Clause:
    width = rng.randint(1, min(max_width, len(variables)))
    chosen = rng.sample(variables, width)
    positive_count = rng.choice([0, 1])
    positive = set(rng.sample(chosen, positive_count))
    clause = canonical_clause(v if v in positive else -v for v in chosen)
    assert clause is not None
    return clause


def random_affine_equations(
    rng: random.Random,
    variables: list[int],
    count: int,
) -> list[Equation]:
    out: list[Equation] = []
    for _ in range(count):
        width = rng.randint(1, min(5, len(variables)))
        chosen = tuple(sorted(rng.sample(variables, width)))
        out.append((chosen, rng.randrange(2)))
    return out


def random_3cnf(rng: random.Random, n: int, m: int) -> CNF:
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        clause = canonical_clause(v if rng.random() < 0.5 else -v for v in chosen)
        assert clause is not None
        clauses.append(clause)
    return canonical_cnf(clauses)


def planted_3cnf(
    rng: random.Random,
    n: int,
    m: int,
) -> tuple[CNF, dict[int, bool]]:
    planted = {v: bool(rng.getrandbits(1)) for v in range(1, n + 1)}
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        lits = [v if rng.random() < 0.5 else -v for v in chosen]
        if not any(planted[abs(lit)] == (lit > 0) for lit in lits):
            v = chosen[0]
            lits[0] = v if planted[v] else -v
        clause = canonical_clause(lits)
        assert clause is not None
        clauses.append(clause)
    formula = canonical_cnf(clauses)
    assert satisfies_cnf(formula, planted)
    return formula, planted


def complete_unsat_3core() -> CNF:
    clauses = []
    for bits in itertools.product([False, True], repeat=3):
        clause = []
        for i, value in enumerate(bits, start=1):
            clause.append(-i if value else i)
        c = canonical_clause(clause)
        assert c is not None
        clauses.append(c)
    formula = canonical_cnf(clauses)
    sat, _, _ = brute_force_mixed([], formula, [1, 2, 3])
    assert not sat
    return formula


def planted_2cnf(
    rng: random.Random,
    n: int,
    m: int,
) -> tuple[CNF, dict[int, bool]]:
    planted = {v: bool(rng.getrandbits(1)) for v in range(1, n + 1)}
    clauses: list[Clause] = []
    for _ in range(m):
        width = rng.choice([1, 2])
        chosen = rng.sample(range(1, n + 1), width)
        lits = [v if rng.random() < 0.5 else -v for v in chosen]
        if not any(planted[abs(lit)] == (lit > 0) for lit in lits):
            v = chosen[0]
            lits[0] = v if planted[v] else -v
        c = canonical_clause(lits)
        assert c is not None
        clauses.append(c)
    formula = canonical_cnf(clauses)
    assert satisfies_cnf(formula, planted)
    return formula, planted


def reduce_3sat_to_horn_xor(formula: CNF, n: int) -> tuple[list[Equation], CNF, list[int]]:
    complements = {v: n + v for v in range(1, n + 1)}
    equations: list[Equation] = [((v, complements[v]), 1) for v in range(1, n + 1)]
    horn_clauses = []
    for clause in formula:
        transformed = []
        for lit in clause:
            if lit > 0:
                transformed.append(-complements[lit])
            else:
                transformed.append(lit)
        c = canonical_clause(transformed)
        assert c is not None
        horn_clauses.append(c)
    horn = canonical_cnf(horn_clauses)
    assert is_horn(horn)
    interface = list(range(1, 2 * n + 1))
    return equations, horn, interface


def verify_3sat_reduction(formula: CNF, n: int) -> bool:
    equations, horn, interface = reduce_3sat_to_horn_xor(formula, n)
    for bits in itertools.product([False, True], repeat=n):
        source = dict(zip(range(1, n + 1), bits))
        extended = dict(source)
        for v in range(1, n + 1):
            extended[n + v] = not source[v]
        if satisfies_cnf(formula, source) != (
            satisfies_affine(equations, extended) and satisfies_cnf(horn, extended)
        ):
            return False
    return True

