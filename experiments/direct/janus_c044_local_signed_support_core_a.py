#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Any, Iterable
import hashlib
import json

Equation = tuple[int, int]
Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Subspace = tuple[Equation, ...]

SCHEMA = "janus.c044.local_signed_support_vtree.v1"
MAX_SEPARATOR_CAP = 2
SUPPORT_EXPONENT = 2
SUPPORT_MULTIPLIER = 4
WORK_EXPONENT = 8
WORK_MULTIPLIER = 256
CERTIFICATE_EXPONENT = 7
CERTIFICATE_MULTIPLIER = 128

OPEN_LOCAL_SUPPORT = "OPEN_LOCAL_SUPPORT"
OPEN_WORK_BUDGET = "OPEN_WORK_BUDGET"
OPEN_CERTIFICATE_VOLUME = "OPEN_CERTIFICATE_VOLUME"
INVALID_CERTIFICATE = "INVALID_CERTIFICATE"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


@dataclass
class Row:
    mask: int
    rhs: int
    provenance: int = 0

    def xor(self, other: "Row") -> None:
        self.mask ^= other.mask
        self.rhs ^= other.rhs
        self.provenance ^= other.provenance


def rref_system(
    equations: Iterable[Equation],
    dimension: int,
    *,
    provenance: bool = False,
    meter: "Meter | None" = None,
) -> tuple[Subspace | None, list[dict[str, int]], list[Row]]:
    rows = [
        Row(mask, rhs & 1, (1 << index) if provenance else 0)
        for index, (mask, rhs) in enumerate(equations)
    ]
    operations: list[dict[str, int]] = []
    rank = 0
    for variable in range(1, dimension + 1):
        bit = 1 << (variable - 1)
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index].mask & bit),
            None,
        )
        if meter:
            meter.charge("rref_pivot_scan", max(1, len(rows) - rank))
        if pivot is None:
            continue
        if pivot != rank:
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            operations.append({"op": 0, "a": rank, "b": pivot})
            if meter:
                meter.charge("rref_swap")
        for index in range(len(rows)):
            if index != rank and rows[index].mask & bit:
                rows[index].xor(rows[rank])
                operations.append({"op": 1, "dst": index, "src": rank})
                if meter:
                    meter.charge("rref_xor")
        rank += 1

    nonzero: list[Row] = []
    for row in rows:
        if meter:
            meter.charge("rref_row_check")
        if row.mask == 0:
            if row.rhs:
                return None, operations, rows
        else:
            nonzero.append(row)
    nonzero.sort(
        key=lambda row: (
            (row.mask & -row.mask).bit_length(),
            row.mask,
            row.rhs,
            row.provenance,
        )
    )
    return tuple((row.mask, row.rhs) for row in nonzero), operations, nonzero


def intersection(
    left: Subspace,
    right: Subspace,
    dimension: int,
    meter: "Meter | None" = None,
) -> Subspace | None:
    if meter:
        meter.charge("affine_intersection")
    return rref_system(left + right, dimension, meter=meter)[0]


def system_dimension(space: Subspace, dimension: int) -> int:
    return dimension - len(space)


def system_payload(space: Subspace | None) -> list[list[int]] | None:
    if space is None:
        return None
    return [[mask, rhs] for mask, rhs in space]


def parse_system(payload: list[list[Any]]) -> Subspace:
    return tuple((int(mask), int(rhs)) for mask, rhs in payload)


def satisfies_space(space: Subspace, assignment: dict[int, bool]) -> bool:
    packed = sum(1 << (variable - 1) for variable, value in assignment.items() if value)
    return all(((mask & packed).bit_count() & 1) == rhs for mask, rhs in space)


def normalize_cnf(cnf: CNF) -> CNF:
    clauses: list[Clause] = []
    for clause in cnf:
        literals = set(int(literal) for literal in clause)
        if any(-literal in literals for literal in literals):
            continue
        normalized = tuple(sorted(literals, key=lambda literal: (abs(literal), literal < 0)))
        if normalized not in clauses:
            clauses.append(normalized)
    clauses.sort(key=lambda clause: (len(clause), clause))
    return tuple(clauses)


def variables_in_cnf(cnf: CNF) -> set[int]:
    return {abs(literal) for clause in cnf for literal in clause}


def variables_in_affine(affine: tuple[Equation, ...]) -> set[int]:
    variables: set[int] = set()
    for mask, _ in affine:
        while mask:
            bit = mask & -mask
            variables.add(bit.bit_length())
            mask ^= bit
    return variables


def canonical_input(cnf: CNF, affine: tuple[Equation, ...], nvars: int) -> dict[str, Any]:
    return {
        "cnf": [list(clause) for clause in normalize_cnf(cnf)],
        "affine": [[int(mask), int(rhs) & 1] for mask, rhs in affine],
        "nvars": nvars,
    }


def encoded_length(cnf: CNF, affine: tuple[Equation, ...], nvars: int) -> int:
    return max(
        2,
        nvars
        + len(cnf)
        + sum(len(clause) for clause in cnf)
        + len(affine)
        + sum(mask.bit_count() for mask, _ in affine),
    )


def xor_original_rows(provenance: int, affine: tuple[Equation, ...]) -> Equation:
    mask = rhs = 0
    for index, (source_mask, source_rhs) in enumerate(affine):
        if provenance >> index & 1:
            mask ^= source_mask
            rhs ^= source_rhs & 1
    return mask, rhs


def parameterize_affine(
    affine: tuple[Equation, ...],
    nvars: int,
    meter: "Meter | None" = None,
) -> dict[str, Any]:
    rows = [
        Row(mask, rhs & 1, 1 << index)
        for index, (mask, rhs) in enumerate(affine)
    ]
    operations: list[dict[str, int]] = []
    rank = 0
    for variable in range(1, nvars + 1):
        bit = 1 << (variable - 1)
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index].mask & bit),
            None,
        )
        if meter:
            meter.charge("basis_pivot_scan", max(1, len(rows) - rank))
        if pivot is None:
            continue
        if pivot != rank:
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            operations.append({"op": 0, "a": rank, "b": pivot})
            if meter:
                meter.charge("basis_swap")
        for index in range(len(rows)):
            if index != rank and rows[index].mask & bit:
                rows[index].xor(rows[rank])
                operations.append({"op": 1, "dst": index, "src": rank})
                if meter:
                    meter.charge("basis_xor")
        rank += 1

    nonzero: list[Row] = []
    contradiction: dict[str, Any] | None = None
    for row in rows:
        if meter:
            meter.charge("basis_row_check")
        if row.mask == 0:
            if row.rhs:
                contradiction = {
                    "rhs": 1,
                    "provenance": str(row.provenance),
                }
                break
        else:
            nonzero.append(row)
    if contradiction is not None:
        return {
            "status": "UNSAT",
            "operations": operations,
            "rref_rows": [],
            "contradiction": contradiction,
        }

    nonzero.sort(
        key=lambda row: (
            (row.mask & -row.mask).bit_length(),
            row.mask,
            row.rhs,
            row.provenance,
        )
    )
    pivots: dict[int, Row] = {}
    for row in nonzero:
        pivot = (row.mask & -row.mask).bit_length()
        pivots[pivot] = row

    free_variables = [
        variable for variable in range(1, nvars + 1) if variable not in pivots
    ]
    free_index = {
        variable: index + 1 for index, variable in enumerate(free_variables)
    }
    coordinate_forms: list[list[int]] = []
    for variable in range(1, nvars + 1):
        if variable in free_index:
            coordinate_forms.append([1 << (free_index[variable] - 1), 0])
            continue
        row = pivots[variable]
        coordinate_mask = 0
        for free_variable in free_variables:
            if row.mask & (1 << (free_variable - 1)):
                coordinate_mask |= 1 << (free_index[free_variable] - 1)
        coordinate_forms.append([coordinate_mask, row.rhs])

    artifact = {
        "status": "SAT",
        "dimension": len(free_variables),
        "free_variables": free_variables,
        "operations": operations,
        "rref_rows": [
            {
                "mask": row.mask,
                "rhs": row.rhs,
                "provenance": str(row.provenance),
            }
            for row in nonzero
        ],
        "coordinate_forms": coordinate_forms,
    }

    for row in nonzero:
        if xor_original_rows(row.provenance, affine) != (row.mask, row.rhs):
            raise AssertionError("basis provenance mismatch")
    return artifact


def verify_basis(
    affine: tuple[Equation, ...],
    nvars: int,
    artifact: dict[str, Any],
) -> bool:
    replay = parameterize_affine(affine, nvars)
    return replay == artifact


def translate_clause(
    clause_id: int,
    clause: Clause,
    coordinate_forms: list[tuple[int, int]],
    dimension: int,
    meter: "Meter | None" = None,
) -> dict[str, Any]:
    equations: list[Equation] = []
    for literal in clause:
        if meter:
            meter.charge("clause_coordinate_literal")
        mask, constant = coordinate_forms[abs(literal) - 1]
        false_value = 0 if literal > 0 else 1
        equations.append((mask, false_value ^ constant))
    space = rref_system(equations, dimension, meter=meter)[0]
    return {
        "clause_id": clause_id,
        "clause": list(clause),
        "empty": space is None,
        "space": system_payload(space),
    }


@dataclass(frozen=True)
class Factor:
    factor_id: int
    clause: Clause
    space: Subspace
    scope: tuple[int, ...]


def factor_scope(space: Subspace, dimension: int) -> tuple[int, ...]:
    support = 0
    for mask, _ in space:
        support |= mask
    return tuple(
        variable
        for variable in range(1, dimension + 1)
        if support & (1 << (variable - 1))
    )


def translate_factors(
    cnf: CNF,
    basis: dict[str, Any],
    meter: "Meter | None" = None,
) -> tuple[list[Factor], list[dict[str, Any]]]:
    dimension = int(basis["dimension"])
    coordinate_forms = [
        (int(mask), int(constant)) for mask, constant in basis["coordinate_forms"]
    ]
    raw: list[dict[str, Any]] = []
    factors: list[Factor] = []
    for clause_id, clause in enumerate(cnf):
        record = translate_clause(
            clause_id,
            clause,
            coordinate_forms,
            dimension,
            meter,
        )
        raw.append(record)
        if not record["empty"]:
            space = parse_system(record["space"])
            factors.append(
                Factor(
                    clause_id,
                    clause,
                    space,
                    factor_scope(space, dimension),
                )
            )
    return factors, raw


def remap_space(space: Subspace, scope: tuple[int, ...]) -> Subspace:
    local_index = {variable: index + 1 for index, variable in enumerate(scope)}
    rows: list[Equation] = []
    for mask, rhs in space:
        local_mask = 0
        for variable in scope:
            if mask & (1 << (variable - 1)):
                local_mask |= 1 << (local_index[variable] - 1)
        rows.append((local_mask, rhs))
    remapped = rref_system(rows, len(scope))[0]
    if remapped is None:
        raise AssertionError("consistent factor became empty during remap")
    return remapped


def coefficient_payload(
    coefficients: dict[Subspace, int],
    dimension: int,
) -> list[dict[str, Any]]:
    return [
        {
            "space": system_payload(space),
            "dimension": system_dimension(space, dimension),
            "coefficient": coefficient,
        }
        for space, coefficient in sorted(coefficients.items())
    ]


def parse_coefficients(payload: list[dict[str, Any]]) -> dict[Subspace, int]:
    coefficients: dict[Subspace, int] = {}
    for item in payload:
        space = parse_system(item["space"])
        coefficient = int(item["coefficient"])
        if coefficient == 0 or space in coefficients:
            raise ValueError("noncanonical coefficient payload")
        coefficients[space] = coefficient
    return coefficients


@dataclass
class Capability:
    input_length: int
    requested_separator_cap: int = 1
    local_support_cap: int | None = None
    work_cap: int | None = None
    certificate_cap: int | None = None

    def __post_init__(self) -> None:
        base = self.input_length + 1
        self.separator_limit = min(
            MAX_SEPARATOR_CAP,
            max(0, int(self.requested_separator_cap)),
        )
        self.support_polynomial = SUPPORT_MULTIPLIER * base**SUPPORT_EXPONENT
        self.work_polynomial = WORK_MULTIPLIER * base**WORK_EXPONENT
        self.certificate_polynomial = (
            CERTIFICATE_MULTIPLIER * base**CERTIFICATE_EXPONENT
        )
        self.local_support_limit = min(
            self.support_polynomial,
            self.local_support_cap
            if self.local_support_cap is not None
            else self.support_polynomial,
        )
        self.work_limit = min(
            self.work_polynomial,
            self.work_cap if self.work_cap is not None else self.work_polynomial,
        )
        self.certificate_limit = min(
            self.certificate_polynomial,
            self.certificate_cap
            if self.certificate_cap is not None
            else self.certificate_polynomial,
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "input_length": self.input_length,
            "max_separator_cap": MAX_SEPARATOR_CAP,
            "requested_separator_cap": self.requested_separator_cap,
            "separator_limit": self.separator_limit,
            "support_exponent": SUPPORT_EXPONENT,
            "support_multiplier": SUPPORT_MULTIPLIER,
            "support_polynomial": str(self.support_polynomial),
            "local_support_cap": (
                None if self.local_support_cap is None else str(self.local_support_cap)
            ),
            "local_support_limit": str(self.local_support_limit),
            "work_exponent": WORK_EXPONENT,
            "work_multiplier": WORK_MULTIPLIER,
            "work_polynomial": str(self.work_polynomial),
            "work_cap": None if self.work_cap is None else str(self.work_cap),
            "work_limit": str(self.work_limit),
            "certificate_exponent": CERTIFICATE_EXPONENT,
            "certificate_multiplier": CERTIFICATE_MULTIPLIER,
            "certificate_polynomial": str(self.certificate_polynomial),
            "certificate_cap": (
                None if self.certificate_cap is None else str(self.certificate_cap)
            ),
            "certificate_limit": str(self.certificate_limit),
        }

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "Capability":
        capability = cls(
            int(manifest["input_length"]),
            int(manifest["requested_separator_cap"]),
            None
            if manifest.get("local_support_cap") is None
            else int(manifest["local_support_cap"]),
            None if manifest.get("work_cap") is None else int(manifest["work_cap"]),
            None
            if manifest.get("certificate_cap") is None
            else int(manifest["certificate_cap"]),
        )
        if capability.manifest() != manifest:
            raise ValueError("capability manifest mismatch")
        return capability


class OpenResult(RuntimeError):
    def __init__(
        self,
        status: str,
        stage: str,
        evidence: dict[str, Any] | None = None,
    ):
        super().__init__(status)
        self.status = status
        self.stage = stage
        self.evidence = evidence or {}


@dataclass
class Meter:
    capability: Capability
    counters: dict[str, int] = field(default_factory=dict)
    total_work_units: int = 0
    max_attempted_live_support: int = 0
    max_attempted_working_support: int = 0
    max_accepted_leaf_support: int = 0
    max_accepted_leaf_working_support: int = 0
    separator_candidates: int = 0
    plan_nodes: int = 0
    result_nodes: int = 0

    def charge(self, category: str, units: int = 1) -> None:
        if units < 0:
            raise ValueError("negative work charge")
        self.counters[category] = self.counters.get(category, 0) + units
        self.total_work_units += units
        if self.total_work_units > self.capability.work_limit:
            raise OpenResult(
                OPEN_WORK_BUDGET,
                category,
                {
                    "work_units": self.total_work_units,
                    "work_limit": self.capability.work_limit,
                },
            )

    def check_support(
        self,
        live: int,
        working: int,
        *,
        accepted_leaf: bool,
        factor_step: int,
    ) -> None:
        self.max_attempted_live_support = max(
            self.max_attempted_live_support,
            live,
        )
        self.max_attempted_working_support = max(
            self.max_attempted_working_support,
            working,
        )
        self.charge("signed_support_entries", max(1, working))
        limit = self.capability.local_support_limit
        if live > limit or working > limit:
            raise OpenResult(
                OPEN_LOCAL_SUPPORT,
                "local_signed_support",
                {
                    "factor_step": factor_step,
                    "attempted_live_support": live,
                    "attempted_working_support": working,
                    "local_support_limit": limit,
                },
            )
        if accepted_leaf:
            self.max_accepted_leaf_support = max(
                self.max_accepted_leaf_support,
                live,
            )
            self.max_accepted_leaf_working_support = max(
                self.max_accepted_leaf_working_support,
                working,
            )

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_work_units": self.total_work_units,
            "counters": dict(sorted(self.counters.items())),
            "max_attempted_live_support": self.max_attempted_live_support,
            "max_attempted_working_support": self.max_attempted_working_support,
            "max_accepted_leaf_support": self.max_accepted_leaf_support,
            "max_accepted_leaf_working_support": (
                self.max_accepted_leaf_working_support
            ),
            "separator_candidates": self.separator_candidates,
            "plan_nodes": self.plan_nodes,
            "result_nodes": self.result_nodes,
        }
