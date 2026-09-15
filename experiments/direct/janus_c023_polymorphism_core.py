"""C023 Boolean relations, closure fingerprints, and exact compilers."""
from __future__ import annotations
import hashlib
import itertools
import json
from collections import Counter, deque
from dataclasses import dataclass
from typing import Any, Iterable
from janus_c023_primitives import CNF, Clause, canonical_clause, canonical_cnf

TupleB = tuple[int, ...]
OPS = ("ZERO", "ONE", "AND", "OR", "MAJ", "XOR3")

@dataclass(frozen=True)
class Relation:
    name: str
    arity: int
    tuples: frozenset[TupleB]

    def __post_init__(self) -> None:
        expected = 1 << self.arity
        for row in self.tuples:
            if len(row) != self.arity or any(bit not in (0, 1) for bit in row):
                raise ValueError(f"malformed tuple in {self.name}")
        if len(self.tuples) > expected:
            raise ValueError("too many tuples")


@dataclass(frozen=True)
class Constraint:
    relation: Relation
    scope: tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.scope) != self.relation.arity:
            raise ValueError("scope arity mismatch")
        if len(set(self.scope)) != len(self.scope):
            raise ValueError("repeated variables are excluded in this audit")


@dataclass
class DispatchResult:
    status: str
    sat: bool | None
    assignment: dict[int, bool] | None
    component_targets: list[str]
    compiled_constraints: int
    proof_steps: int
    reason: str


def all_tuples(arity: int) -> list[TupleB]:
    return list(itertools.product((0, 1), repeat=arity))


def relation_satisfied(
    relation: Relation,
    scope: tuple[int, ...],
    assignment: dict[int, bool],
) -> bool:
    row = tuple(int(assignment[v]) for v in scope)
    return row in relation.tuples


def instance_satisfied(
    constraints: list[Constraint],
    assignment: dict[int, bool],
) -> bool:
    return all(
        relation_satisfied(c.relation, c.scope, assignment)
        for c in constraints
    )


def instance_variables(constraints: list[Constraint]) -> list[int]:
    return sorted({v for c in constraints for v in c.scope})


def brute_force_instance(
    constraints: list[Constraint],
) -> tuple[bool, dict[int, bool] | None, int]:
    vars_ = instance_variables(constraints)
    checks = 0
    for bits in itertools.product((False, True), repeat=len(vars_)):
        checks += 1
        assignment = dict(zip(vars_, bits))
        if instance_satisfied(constraints, assignment):
            return True, assignment, checks
    return False, None, checks


def op_apply(name: str, rows: tuple[TupleB, ...]) -> TupleB:
    if name == "AND":
        a, b = rows
        return tuple(x & y for x, y in zip(a, b))
    if name == "OR":
        a, b = rows
        return tuple(x | y for x, y in zip(a, b))
    if name == "MAJ":
        a, b, c = rows
        return tuple(int(x + y + z >= 2) for x, y, z in zip(a, b, c))
    if name == "XOR3":
        a, b, c = rows
        return tuple(x ^ y ^ z for x, y, z in zip(a, b, c))
    raise ValueError(name)


def preserved_by(relation: Relation, operation: str) -> bool:
    if not relation.tuples:
        return False
    if operation == "ZERO":
        return (0,) * relation.arity in relation.tuples
    if operation == "ONE":
        return (1,) * relation.arity in relation.tuples

    arity = 2 if operation in ("AND", "OR") else 3
    rows = tuple(relation.tuples)
    for selected in itertools.product(rows, repeat=arity):
        if op_apply(operation, selected) not in relation.tuples:
            return False
    return True


def fingerprint(relation: Relation) -> frozenset[str]:
    return frozenset(op for op in OPS if preserved_by(relation, op))


def tuple_satisfies_clause(row: TupleB, clause: tuple[int, ...]) -> bool:
    for lit in clause:
        value = bool(row[abs(lit) - 1])
        if value == (lit > 0):
            return True
    return False


def relation_from_clauses(
    arity: int,
    clauses: CNF,
    name: str,
) -> Relation:
    accepted = frozenset(
        row
        for row in all_tuples(arity)
        if all(tuple_satisfies_clause(row, clause) for clause in clauses)
    )
    return Relation(name, arity, accepted)


def valid_clause(relation: Relation, clause: tuple[int, ...]) -> bool:
    return all(tuple_satisfies_clause(row, clause) for row in relation.tuples)


def compile_horn_relation(relation: Relation) -> CNF:
    if not relation.tuples:
        return ((),)
    clauses: list[Clause] = []
    for states in itertools.product((-1, 0, 1), repeat=relation.arity):
        if all(state == 0 for state in states):
            continue
        raw = []
        positives = 0
        for i, state in enumerate(states, start=1):
            if state == 1:
                positives += 1
                raw.append(i)
            elif state == -1:
                raw.append(-i)
        if positives > 1:
            continue
        clause = canonical_clause(raw)
        assert clause is not None
        if valid_clause(relation, clause):
            clauses.append(clause)
    formula = canonical_cnf(clauses)
    rebuilt = relation_from_clauses(relation.arity, formula, relation.name + "_HORN")
    if rebuilt.tuples != relation.tuples:
        raise AssertionError(f"Horn compiler incomplete for {relation.name}")
    return formula


def compile_dual_horn_relation(relation: Relation) -> CNF:
    if not relation.tuples:
        return ((),)
    clauses: list[Clause] = []
    for states in itertools.product((-1, 0, 1), repeat=relation.arity):
        if all(state == 0 for state in states):
            continue
        raw = []
        negatives = 0
        for i, state in enumerate(states, start=1):
            if state == 1:
                raw.append(i)
            elif state == -1:
                negatives += 1
                raw.append(-i)
        if negatives > 1:
            continue
        clause = canonical_clause(raw)
        assert clause is not None
        if valid_clause(relation, clause):
            clauses.append(clause)
    formula = canonical_cnf(clauses)
    rebuilt = relation_from_clauses(relation.arity, formula, relation.name + "_DUAL")
    if rebuilt.tuples != relation.tuples:
        raise AssertionError(f"dual-Horn compiler incomplete for {relation.name}")
    return formula


def compile_bijunctive_relation(relation: Relation) -> CNF:
    if not relation.tuples:
        return ((),)
    literals = [lit for i in range(1, relation.arity + 1) for lit in (i, -i)]
    clauses: list[Clause] = []
    for width in (1, 2):
        for chosen in itertools.combinations(literals, width):
            if len({abs(lit) for lit in chosen}) != width:
                continue
            clause = canonical_clause(chosen)
            if clause is None:
                continue
            if valid_clause(relation, clause):
                clauses.append(clause)
    formula = canonical_cnf(clauses)
    rebuilt = relation_from_clauses(relation.arity, formula, relation.name + "_2CNF")
    if rebuilt.tuples != relation.tuples:
        raise AssertionError(f"2-CNF compiler incomplete for {relation.name}")
    return formula


def parity(row: TupleB, mask: int) -> int:
    value = 0
    for i, bit in enumerate(row):
        if (mask >> i) & 1:
            value ^= bit
    return value


def compile_affine_relation(relation: Relation) -> list[tuple[tuple[int, ...], int]]:
    if not relation.tuples:
        return [((), 1)]
    equations = []
    rows = tuple(relation.tuples)
    for mask in range(1 << relation.arity):
        values = {parity(row, mask) for row in rows}
        if len(values) == 1:
            rhs = next(iter(values))
            variables = tuple(i + 1 for i in range(relation.arity) if (mask >> i) & 1)
            equations.append((variables, rhs))

    accepted = set()
    for row in all_tuples(relation.arity):
        ok = True
        for vars_, rhs in equations:
            value = 0
            for v in vars_:
                value ^= row[v - 1]
            if value != rhs:
                ok = False
                break
        if ok:
            accepted.add(row)
    if accepted != set(relation.tuples):
        raise AssertionError(f"affine compiler incomplete for {relation.name}")
    return equations


def map_local_clause(clause: Clause, scope: tuple[int, ...]) -> Clause:
    mapped = []
    for lit in clause:
        var = scope[abs(lit) - 1]
        mapped.append(var if lit > 0 else -var)
    result = canonical_clause(mapped)
    if result is None:
        raise AssertionError("unexpected tautology after scope mapping")
    return result


def components(constraints: list[Constraint]) -> list[list[Constraint]]:
    if not constraints:
        return []
    by_var: dict[int, list[int]] = {}
    for i, constraint in enumerate(constraints):
        for v in constraint.scope:
            by_var.setdefault(v, []).append(i)

    unseen = set(range(len(constraints)))
    output = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        indices = []
        while queue:
            i = queue.popleft()
            indices.append(i)
            for v in constraints[i].scope:
                for j in by_var[v]:
                    if j in unseen:
                        unseen.remove(j)
                        queue.append(j)
        output.append([constraints[i] for i in indices])
    return output
