#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Equation = tuple[int, int]
Assignment = dict[int, bool]

SCHEMA = "janus.cross_language_negotiation.v1.2"
POLICY = "COMPLETE_HORN_AFFINE_HULL_BASIS_V1"


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def normalize(formula: CNF) -> CNF:
    clauses: list[Clause] = []
    for clause in formula:
        literals = set(clause)
        if any(-literal in literals for literal in literals):
            continue
        canonical = tuple(sorted(literals, key=lambda x: (abs(x), x < 0)))
        if canonical not in clauses:
            clauses.append(canonical)
    clauses.sort(key=lambda clause: (len(clause), clause))
    kept: list[Clause] = []
    for clause in clauses:
        if any(set(previous) <= set(clause) for previous in kept):
            continue
        kept.append(clause)
    return tuple(kept)


def is_horn(formula: CNF) -> bool:
    return all(sum(literal > 0 for literal in clause) <= 1 for clause in formula)


def eval_clause(clause: Clause, assignment: Assignment) -> bool:
    return any(assignment[abs(literal)] == (literal > 0) for literal in clause)


def eval_cnf(formula: CNF, assignment: Assignment) -> bool:
    return all(eval_clause(clause, assignment) for clause in formula)


def eval_row(row: Equation, assignment: Assignment) -> bool:
    mask, rhs = row
    parity = 0
    for variable, value in assignment.items():
        if mask >> (variable - 1) & 1:
            parity ^= int(value)
    return parity == rhs


def eval_affine(rows: tuple[Equation, ...], assignment: Assignment) -> bool:
    return all(eval_row(row, assignment) for row in rows)


class BudgetExceeded(Exception):
    pass


@dataclass
class Meter:
    limit: int
    work_units: int = 0
    horn_calls: int = 0
    horn_clause_scans: int = 0
    equality_pair_queries: int = 0
    basis_extractions: int = 0
    affine_row_xors: int = 0
    self_reduction_tests: int = 0

    def charge(self, amount: int = 1) -> None:
        self.work_units += amount
        if self.work_units > self.limit:
            raise BudgetExceeded


class UnionFind:
    def __init__(self, values: list[int]):
        self.parent = {value: value for value in values}

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> bool:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            return False
        if left_root > right_root:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        return True


def horn_solve(
    formula: CNF,
    variable_count: int,
    units: Assignment,
    meter: Meter,
):
    meter.horn_calls += 1
    meter.charge()
    clauses = list(normalize(formula))
    for variable, value in sorted(units.items()):
        clauses.append((variable,) if value else (-variable,))
    clauses = list(normalize(tuple(clauses)))
    if not is_horn(tuple(clauses)):
        return {"status": "OPEN_LANGUAGE"}

    assignment = {variable: False for variable in range(1, variable_count + 1)}
    trace: list[dict] = []
    changed = True
    while changed:
        changed = False
        for clause_index, clause in enumerate(clauses):
            meter.horn_clause_scans += 1
            meter.charge()
            head = next((literal for literal in clause if literal > 0), None)
            body = [-literal for literal in clause if literal < 0]
            if all(assignment[variable] for variable in body):
                if head is None:
                    return {
                        "status": "UNSAT",
                        "trace": trace + [{"op": "conflict", "clause": clause_index}],
                    }
                if not assignment[head]:
                    assignment[head] = True
                    trace.append({"op": "set", "var": head, "clause": clause_index})
                    changed = True

    if not eval_cnf(tuple(clauses), assignment):
        raise AssertionError("Horn least model does not satisfy the restricted formula")
    return {"status": "SAT", "assignment": assignment, "trace": trace}


def solve_with_literal(
    formula: CNF,
    variable_count: int,
    units: Assignment,
    variable: int,
    value: bool,
    meter: Meter,
):
    if variable in units and units[variable] != value:
        return {
            "status": "UNSAT",
            "trace": [{"op": "unit_conflict", "var": variable}],
        }
    extended = dict(units)
    extended[variable] = value
    return horn_solve(formula, variable_count, extended, meter)


def implication_query(
    formula: CNF,
    variable_count: int,
    units: Assignment,
    antecedent: int,
    consequent: int,
    meter: Meter,
):
    extended = dict(units)
    if antecedent in extended and not extended[antecedent]:
        return {
            "status": "UNSAT",
            "trace": [{"op": "unit_conflict", "var": antecedent}],
        }
    extended[antecedent] = True
    if consequent in extended and extended[consequent]:
        return {
            "status": "UNSAT",
            "trace": [{"op": "unit_conflict", "var": consequent}],
        }
    extended[consequent] = False
    return horn_solve(formula, variable_count, extended, meter)


def extract_affine_consequence_basis(
    formula: CNF,
    variable_count: int,
    units: Assignment,
    meter: Meter,
):
    meter.basis_extractions += 1
    root = horn_solve(formula, variable_count, units, meter)
    if root["status"] == "UNSAT":
        return {
            "status": "UNSAT",
            "native_proof": root,
            "rows": [],
            "row_events": [],
        }

    fixed: dict[int, bool] = {}
    nonconstant: list[int] = []
    literal_events: list[dict] = []
    for variable in range(1, variable_count + 1):
        zero = solve_with_literal(
            formula, variable_count, units, variable, False, meter
        )
        one = solve_with_literal(
            formula, variable_count, units, variable, True, meter
        )
        if zero["status"] == "UNSAT":
            fixed[variable] = True
            literal_events.append(
                {
                    "kind": "ENTAILED_LITERAL",
                    "var": variable,
                    "value": True,
                    "opposite_assumption": False,
                    "native_proof": zero,
                }
            )
        elif one["status"] == "UNSAT":
            fixed[variable] = False
            literal_events.append(
                {
                    "kind": "ENTAILED_LITERAL",
                    "var": variable,
                    "value": False,
                    "opposite_assumption": True,
                    "native_proof": one,
                }
            )
        else:
            nonconstant.append(variable)

    union_find = UnionFind(nonconstant)
    equality_events: list[dict] = []
    for left_index, left in enumerate(nonconstant):
        for right in nonconstant[left_index + 1 :]:
            meter.equality_pair_queries += 1
            left_to_right = implication_query(
                formula, variable_count, units, left, right, meter
            )
            right_to_left = implication_query(
                formula, variable_count, units, right, left, meter
            )
            if (
                left_to_right["status"] == "UNSAT"
                and right_to_left["status"] == "UNSAT"
                and union_find.union(left, right)
            ):
                equality_events.append(
                    {
                        "kind": "ENTAILED_EQUALITY_ALIAS",
                        "left": left,
                        "right": right,
                        "rhs": 0,
                        "native_proofs": [left_to_right, right_to_left],
                    }
                )

    rows: list[Equation] = []
    row_events: list[dict] = []
    by_variable = {event["var"]: event for event in literal_events}
    for variable, value in sorted(fixed.items()):
        rows.append((1 << (variable - 1), int(value)))
        row_events.append(by_variable[variable])
    for event in equality_events:
        rows.append(
            (
                (1 << (event["left"] - 1)) | (1 << (event["right"] - 1)),
                0,
            )
        )
        row_events.append(event)

    return {
        "status": "SAT",
        "rows": rows,
        "row_events": row_events,
        "fixed": fixed,
        "nonconstant": nonconstant,
        "literal_events": literal_events,
        "equality_events": equality_events,
    }


def build_augmented_elimination(
    rows: list[Equation], variable_count: int, meter: Meter | None = None
):
    basis: dict[int, tuple[int, int]] = {}
    for row_index, (mask, rhs) in enumerate(rows):
        vector = mask | (rhs << variable_count)
        provenance = 1 << row_index
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = (vector, provenance)
                break
            vector ^= basis[pivot][0]
            provenance ^= basis[pivot][1]
            if meter is not None:
                meter.affine_row_xors += 1
                meter.charge()
    return basis


def reduce_augmented_row(
    row: Equation,
    variable_count: int,
    basis: dict[int, tuple[int, int]],
    meter: Meter | None = None,
):
    vector = row[0] | (row[1] << variable_count)
    provenance = 0
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in basis:
            return vector, provenance
        vector ^= basis[pivot][0]
        provenance ^= basis[pivot][1]
        if meter is not None:
            meter.affine_row_xors += 1
            meter.charge()
    return 0, provenance


def row_entailment_decision(
    formula: CNF,
    variable_count: int,
    units: Assignment,
    row: Equation,
    meter: Meter,
):
    certificate = extract_affine_consequence_basis(
        formula, variable_count, units, meter
    )
    if certificate["status"] == "UNSAT":
        return True, certificate, 0
    elimination = build_augmented_elimination(
        certificate["rows"], variable_count, meter
    )
    residual, provenance = reduce_augmented_row(
        row, variable_count, elimination, meter
    )
    return residual == 0, certificate, provenance


def recover_horn_countermodel(
    formula: CNF,
    variable_count: int,
    row: Equation,
    meter: Meter,
):
    entailed, _, _ = row_entailment_decision(
        formula, variable_count, {}, row, meter
    )
    if entailed:
        raise ValueError("countermodel requested for an entailed row")

    units: Assignment = {}
    decisions: list[dict] = []
    for variable in range(1, variable_count + 1):
        chosen = None
        for value in (False, True):
            meter.self_reduction_tests += 1
            extended = dict(units)
            extended[variable] = value
            branch_entails, _, _ = row_entailment_decision(
                formula, variable_count, extended, row, meter
            )
            decisions.append(
                {
                    "var": variable,
                    "value": value,
                    "branch_entails_row": branch_entails,
                }
            )
            if not branch_entails:
                chosen = value
                break
        if chosen is None:
            raise AssertionError("both branches entailed a row not entailed by parent")
        units[variable] = chosen

    if not eval_cnf(formula, units):
        raise AssertionError("recovered separator is not a Horn model")
    if eval_row(row, units):
        raise AssertionError("recovered separator does not violate the affine row")
    return units, decisions
