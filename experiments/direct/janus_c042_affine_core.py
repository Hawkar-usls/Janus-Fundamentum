#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from dataclasses import dataclass, field
from typing import Any

Equation = tuple[int, int]
Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
SCHEMA = "janus.c042.laminar_affine_forbidden_cover.v2"
BUDGET_EXPONENT = 6
BUDGET_MULTIPLIER = 64


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


def normalize_cnf(cnf: CNF) -> CNF:
    out: list[Clause] = []
    for clause in cnf:
        literals = set(clause)
        if any(-lit in literals for lit in literals):
            continue
        normalized = tuple(sorted(literals, key=lambda lit: (abs(lit), lit < 0)))
        if normalized not in out:
            out.append(normalized)
    return tuple(sorted(out, key=lambda clause: (len(clause), clause)))


def variables_in_cnf(cnf: CNF) -> set[int]:
    return {abs(lit) for clause in cnf for lit in clause}


def variables_in_affine(equations: tuple[Equation, ...]) -> set[int]:
    out: set[int] = set()
    for mask, _ in equations:
        while mask:
            bit = mask & -mask
            out.add(bit.bit_length())
            mask ^= bit
    return out


def canonical_input(cnf: CNF, affine: tuple[Equation, ...], nvars: int) -> dict[str, Any]:
    return {
        "cnf": [list(clause) for clause in cnf],
        "affine": [[mask, rhs & 1] for mask, rhs in affine],
        "nvars": nvars,
    }


def encoded_length(cnf: CNF, affine: tuple[Equation, ...], nvars: int) -> int:
    # Standard-model bit-operation envelope: every equation carries n variable bits plus one RHS bit.
    return max(
        2,
        1
        + nvars
        + len(cnf)
        + sum(len(clause) for clause in cnf)
        + len(affine) * (nvars + 1),
    )


class BudgetExceeded(RuntimeError):
    def __init__(self, stage: str):
        super().__init__(stage)
        self.stage = stage


@dataclass
class Ledger:
    input_length: int
    budget_cap: int | None = None
    exponent: int = BUDGET_EXPONENT
    counters: dict[str, int] = field(default_factory=dict)
    total_work_units: int = 0

    def __post_init__(self) -> None:
        self.polynomial_limit = BUDGET_MULTIPLIER * (self.input_length + 1) ** self.exponent
        self.applied_limit = min(
            self.polynomial_limit,
            self.budget_cap if self.budget_cap is not None else self.polynomial_limit,
        )

    def charge(self, category: str, units: int = 1) -> None:
        if units < 0:
            raise ValueError("negative work charge")
        self.counters[category] = self.counters.get(category, 0) + units
        self.total_work_units += units
        if self.total_work_units > self.applied_limit:
            raise BudgetExceeded(category)

    def snapshot(self) -> dict[str, Any]:
        return {
            "input_length": self.input_length,
            "budget_exponent": self.exponent,
            "budget_multiplier": BUDGET_MULTIPLIER,
            "polynomial_limit": str(self.polynomial_limit),
            "applied_limit": str(self.applied_limit),
            "total_work_units": self.total_work_units,
            "counters": dict(sorted(self.counters.items())),
        }


@dataclass
class Row:
    mask: int
    rhs: int
    provenance: int

    def xor(self, other: "Row") -> None:
        self.mask ^= other.mask
        self.rhs ^= other.rhs
        self.provenance ^= other.provenance


def xor_provenance(equations: tuple[Equation, ...], provenance: int) -> Equation:
    mask = rhs = 0
    for index, (row_mask, row_rhs) in enumerate(equations):
        if (provenance >> index) & 1:
            mask ^= row_mask
            rhs ^= row_rhs & 1
    return mask, rhs


def rref_with_provenance(
    equations: tuple[Equation, ...], dimension: int, ledger: Ledger
) -> tuple[tuple[tuple[int, int, int], ...], bool, int | None]:
    ledger.charge("elimination_calls")
    rows = [Row(mask, rhs & 1, 1 << index) for index, (mask, rhs) in enumerate(equations)]
    rank = 0
    for variable in range(1, dimension + 1):
        bit = 1 << (variable - 1)
        pivot = None
        for index in range(rank, len(rows)):
            ledger.charge("elimination_row_scans")
            if rows[index].mask & bit:
                pivot = index
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        ledger.charge("row_swaps")
        for index in range(len(rows)):
            ledger.charge("elimination_row_scans")
            if index != rank and rows[index].mask & bit:
                rows[index].xor(rows[rank])
                ledger.charge("row_xors")
        rank += 1
    output: list[tuple[int, int, int]] = []
    conflict: int | None = None
    for row in rows:
        ledger.charge("elimination_output_scans")
        if row.mask == 0:
            if row.rhs:
                conflict = row.provenance
                break
        else:
            output.append((row.mask, row.rhs, row.provenance))
    if conflict is not None:
        return (), False, conflict
    output.sort(key=lambda row: ((row[0] & -row[0]).bit_length(), row[0], row[1]))
    return tuple(output), True, None


def rref_system(equations: tuple[Equation, ...], dimension: int, ledger: Ledger) -> tuple[Equation, ...] | None:
    rows, consistent, _ = rref_with_provenance(equations, dimension, ledger)
    if not consistent:
        return None
    return tuple((mask, rhs) for mask, rhs, _ in rows)


def system_dimension(system: tuple[Equation, ...], ambient_dimension: int) -> int:
    return ambient_dimension - len(system)


def evaluate_equations(equations: tuple[Equation, ...], assignment_mask: int) -> bool:
    return all(((mask & assignment_mask).bit_count() & 1) == (rhs & 1) for mask, rhs in equations)


def solve_system(system: tuple[Equation, ...], dimension: int, ledger: Ledger) -> int | None:
    canonical = rref_system(system, dimension, ledger)
    if canonical is None:
        return None
    assignment = 0
    for mask, rhs in reversed(canonical):
        pivot = mask & -mask
        value = rhs ^ ((mask ^ pivot) & assignment).bit_count() & 1
        if value:
            assignment |= pivot
        ledger.charge("back_substitution_bits", max(1, mask.bit_count()))
    return assignment


def intersection(
    left: tuple[Equation, ...], right: tuple[Equation, ...], dimension: int, ledger: Ledger
) -> tuple[Equation, ...] | None:
    ledger.charge("intersection_calls")
    return rref_system(left + right, dimension, ledger)


def entails(system: tuple[Equation, ...], equation: Equation, dimension: int, ledger: Ledger) -> bool:
    ledger.charge("entailment_calls")
    mask, rhs = equation
    return rref_system(system + ((mask, rhs ^ 1),), dimension, ledger) is None


def subset(
    left: tuple[Equation, ...], right: tuple[Equation, ...], dimension: int, ledger: Ledger
) -> bool:
    ledger.charge("inclusion_calls")
    return all(entails(left, equation, dimension, ledger) for equation in right)


def relation(
    left: tuple[Equation, ...], right: tuple[Equation, ...], dimension: int, ledger: Ledger
) -> str:
    overlap = intersection(left, right, dimension, ledger)
    if overlap is None:
        return "DISJOINT"
    left_in_right = subset(left, right, dimension, ledger)
    right_in_left = subset(right, left, dimension, ledger)
    if left_in_right and right_in_left:
        return "EQUAL"
    if left_in_right:
        return "LEFT_SUBSET_RIGHT"
    if right_in_left:
        return "RIGHT_SUBSET_LEFT"
    return "CROSSING"


def parameterize_affine(
    affine: tuple[Equation, ...], nvars: int, ledger: Ledger
) -> dict[str, Any]:
    rows, consistent, conflict = rref_with_provenance(affine, nvars, ledger)
    if not consistent:
        return {
            "status": "UNSAT",
            "conflict_provenance": str(conflict),
        }
    canonical = tuple((mask, rhs) for mask, rhs, _ in rows)
    pivots = {(mask & -mask).bit_length(): (mask, rhs) for mask, rhs in canonical}
    free_variables = [variable for variable in range(1, nvars + 1) if variable not in pivots]

    def extend(seed_mask: int, homogeneous: bool) -> int:
        assignment = seed_mask
        for pivot_variable in sorted(pivots, reverse=True):
            mask, rhs = pivots[pivot_variable]
            pivot = 1 << (pivot_variable - 1)
            value = (0 if homogeneous else rhs) ^ (((mask ^ pivot) & assignment).bit_count() & 1)
            if value:
                assignment |= pivot
            else:
                assignment &= ~pivot
            ledger.charge("basis_back_substitution_bits", max(1, mask.bit_count()))
        return assignment

    particular = extend(0, False)
    basis = [extend(1 << (variable - 1), True) for variable in free_variables]
    coordinate_forms: list[tuple[int, int]] = []
    for variable in range(1, nvars + 1):
        coordinate_mask = 0
        for index, vector in enumerate(basis):
            ledger.charge("coordinate_form_bits")
            if vector & (1 << (variable - 1)):
                coordinate_mask |= 1 << index
        coordinate_forms.append((coordinate_mask, int(bool(particular & (1 << (variable - 1))))))
    return {
        "status": "SAT",
        "dimension": len(free_variables),
        "rref": [[mask, rhs, str(provenance)] for mask, rhs, provenance in rows],
        "free_variables": free_variables,
        "particular_mask": str(particular),
        "basis_masks": [str(vector) for vector in basis],
        "coordinate_forms": [[mask, constant] for mask, constant in coordinate_forms],
    }


def translate_clause(
    clause_id: int,
    clause: Clause,
    coordinate_forms: list[tuple[int, int]],
    dimension: int,
    ledger: Ledger,
) -> dict[str, Any]:
    literal_equations: list[Equation] = []
    for literal in clause:
        ledger.charge("coordinate_translation_literals")
        coordinate_mask, constant = coordinate_forms[abs(literal) - 1]
        required_value = 0 if literal > 0 else 1
        literal_equations.append((coordinate_mask, required_value ^ constant))
    rows, consistent, conflict = rref_with_provenance(tuple(literal_equations), dimension, ledger)
    return {
        "clause_id": clause_id,
        "clause": list(clause),
        "literal_equations": [[mask, rhs] for mask, rhs in literal_equations],
        "empty": not consistent,
        "conflict_provenance": None if consistent else str(conflict),
        "system": [] if not consistent else [[mask, rhs, str(provenance)] for mask, rhs, provenance in rows],
    }


def canonical_factor_system(factor: dict[str, Any]) -> tuple[Equation, ...]:
    return tuple((int(row[0]), int(row[1])) for row in factor["system"])


def assignment_dict(mask: int, dimension: int) -> dict[str, bool]:
    return {str(variable): bool(mask & (1 << (variable - 1))) for variable in range(1, dimension + 1)}


def lift_coordinate_mask(lambda_mask: int, basis_artifact: dict[str, Any], nvars: int) -> int:
    assignment = int(basis_artifact["particular_mask"])
    for index, vector_text in enumerate(basis_artifact["basis_masks"]):
        if lambda_mask & (1 << index):
            assignment ^= int(vector_text)
    return assignment & ((1 << nvars) - 1 if nvars else 0)


def evaluate_cnf(cnf: CNF, assignment_mask: int) -> bool:
    for clause in cnf:
        if not any(bool(assignment_mask & (1 << (abs(literal) - 1))) == (literal > 0) for literal in clause):
            return False
    return True


def make_open_budget(
    input_digest: str, nvars: int, ledger: Ledger, stage: str, budget_cap: int | None
) -> dict[str, Any]:
    body = {
        "schema": SCHEMA,
        "status": "OPEN_BUDGET",
        "reason": stage,
        "input_digest": input_digest,
        "nvars": nvars,
        "capability": {
            "budget_exponent": BUDGET_EXPONENT,
            "budget_multiplier": BUDGET_MULTIPLIER,
            "budget_cap": None if budget_cap is None else str(budget_cap),
        },
        "producer_ledger": ledger.snapshot(),
        "p_vs_np": "OPEN",
    }
    body["integrity_sha256"] = digest(body)
    return body


def finalize_certificate(body: dict[str, Any], ledger: Ledger) -> dict[str, Any]:
    charged = 0
    for _ in range(8):
        body["producer_ledger"] = ledger.snapshot()
        probe = dict(body)
        probe["integrity_sha256"] = "0" * 64
        size = len(canonical_json(probe).encode())
        if size <= charged:
            break
        ledger.charge("certificate_bytes", size - charged)
        charged = size
    body["producer_ledger"] = ledger.snapshot()
    body["integrity_sha256"] = digest(body)
    return body
