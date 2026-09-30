"""C023 canonical relation fixtures and 3-SAT reduction."""
from __future__ import annotations
import itertools
import random
from janus_c023_primitives import CNF, canonical_clause, canonical_cnf, satisfies_cnf
from janus_c023_polymorphism_core import *
from janus_c023_polymorphism_dispatch import *

# ---------------------------------------------------------------------------
# Canonical relations and reductions
# ---------------------------------------------------------------------------

TRUE3 = Relation("TRUE3", 3, frozenset(all_tuples(3)))
NAND3 = Relation(
    "NAND3",
    3,
    frozenset(row for row in all_tuples(3) if row != (1, 1, 1)),
)
OR3 = Relation(
    "OR3",
    3,
    frozenset(row for row in all_tuples(3) if row != (0, 0, 0)),
)
NEQ2 = Relation("NEQ2", 2, frozenset({(0, 1), (1, 0)}))
EQ2 = Relation("EQ2", 2, frozenset({(0, 0), (1, 1)}))
IMP2 = Relation(
    "IMP2",
    2,
    frozenset({(0, 0), (0, 1), (1, 1)}),
)
XOR3_EVEN = Relation(
    "XOR3_EVEN",
    3,
    frozenset(row for row in all_tuples(3) if (row[0] ^ row[1] ^ row[2]) == 0),
)


def switch_relation() -> Relation:
    accepted = {
        (0, 0, 0, 1),
        (1, 0, 1, 0),
        (1, 1, 0, 0),
    }
    return Relation("SWITCH_HETEROGENEOUS", 4, frozenset(accepted))


SWITCH4 = switch_relation()


def random_3cnf(
    rng: random.Random,
    n: int,
    m: int,
) -> CNF:
    clauses = []
    for _ in range(m):
        chosen = rng.sample(range(1, n + 1), 3)
        clause = canonical_clause(
            v if rng.random() < 0.5 else -v
            for v in chosen
        )
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
    for bits in all_tuples(3):
        clause = canonical_clause(
            -i if bits[i - 1] else i
            for i in range(1, 4)
        )
        assert clause is not None
        clauses.append(clause)
    return canonical_cnf(clauses)


def reduce_3cnf_to_csp(
    formula: CNF,
    n: int,
) -> list[Constraint]:
    constraints = []
    for v in range(1, n + 1):
        constraints.append(Constraint(NEQ2, (v, n + v)))

    for clause in formula:
        scope = []
        for lit in clause:
            if lit > 0:
                scope.append(n + lit)
            else:
                scope.append(abs(lit))
        constraints.append(Constraint(NAND3, tuple(scope)))
    return constraints


def source_assignment_to_csp(
    assignment: dict[int, bool],
    n: int,
) -> dict[int, bool]:
    extended = dict(assignment)
    for v in range(1, n + 1):
        extended[n + v] = not assignment[v]
    return extended
