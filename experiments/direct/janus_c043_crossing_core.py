#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from janus_c042_affine_core import (
    BudgetExceeded,
    canonical_json,
    digest,
    intersection,
    rref_system,
    system_dimension,
)

Equation = tuple[int, int]
Clause = tuple[int, ...]
CNF = tuple[Clause, ...]
Subspace = tuple[Equation, ...]
Coefficients = dict[Subspace, int]

SCHEMA = "janus.c043.bounded_live_signed_support.v2"
SUPPORT_EXPONENT = 2
SUPPORT_MULTIPLIER = 4
WORK_EXPONENT = 7
WORK_MULTIPLIER = 128
CERTIFICATE_EXPONENT = 6
CERTIFICATE_MULTIPLIER = 64
COEFFICIENT_EXPONENT = 3
COEFFICIENT_MULTIPLIER = 16

OPEN_INTERSECTION_CLOSURE = "OPEN_INTERSECTION_CLOSURE"
OPEN_WORK_BUDGET = "OPEN_WORK_BUDGET"
OPEN_CERTIFICATE_VOLUME = "OPEN_CERTIFICATE_VOLUME"


class CrossingOpen(RuntimeError):
    def __init__(self, status: str, stage: str, evidence: dict[str, Any] | None = None):
        super().__init__(status)
        self.status = status
        self.stage = stage
        self.evidence = evidence or {}


@dataclass
class Capability:
    input_length: int
    support_cap: int | None = None
    work_cap: int | None = None
    certificate_cap: int | None = None
    coefficient_bit_cap: int | None = None

    def __post_init__(self) -> None:
        base = self.input_length + 1
        self.support_polynomial = SUPPORT_MULTIPLIER * base**SUPPORT_EXPONENT
        self.work_polynomial = WORK_MULTIPLIER * base**WORK_EXPONENT
        self.certificate_polynomial = CERTIFICATE_MULTIPLIER * base**CERTIFICATE_EXPONENT
        self.coefficient_polynomial = COEFFICIENT_MULTIPLIER * base**COEFFICIENT_EXPONENT
        self.support_limit = min(self.support_polynomial, self.support_cap if self.support_cap is not None else self.support_polynomial)
        self.work_limit = min(self.work_polynomial, self.work_cap if self.work_cap is not None else self.work_polynomial)
        self.certificate_limit = min(
            self.certificate_polynomial,
            self.certificate_cap if self.certificate_cap is not None else self.certificate_polynomial,
        )
        self.coefficient_bit_limit = min(
            self.coefficient_polynomial,
            self.coefficient_bit_cap if self.coefficient_bit_cap is not None else self.coefficient_polynomial,
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "input_length": self.input_length,
            "support_exponent": SUPPORT_EXPONENT,
            "support_multiplier": SUPPORT_MULTIPLIER,
            "support_polynomial": str(self.support_polynomial),
            "support_cap": None if self.support_cap is None else str(self.support_cap),
            "support_limit": str(self.support_limit),
            "work_exponent": WORK_EXPONENT,
            "work_multiplier": WORK_MULTIPLIER,
            "work_polynomial": str(self.work_polynomial),
            "work_cap": None if self.work_cap is None else str(self.work_cap),
            "work_limit": str(self.work_limit),
            "certificate_exponent": CERTIFICATE_EXPONENT,
            "certificate_multiplier": CERTIFICATE_MULTIPLIER,
            "certificate_polynomial": str(self.certificate_polynomial),
            "certificate_cap": None if self.certificate_cap is None else str(self.certificate_cap),
            "certificate_limit": str(self.certificate_limit),
            "coefficient_exponent": COEFFICIENT_EXPONENT,
            "coefficient_multiplier": COEFFICIENT_MULTIPLIER,
            "coefficient_polynomial": str(self.coefficient_polynomial),
            "coefficient_bit_cap": None if self.coefficient_bit_cap is None else str(self.coefficient_bit_cap),
            "coefficient_bit_limit": str(self.coefficient_bit_limit),
        }

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "Capability":
        capability = cls(
            int(manifest["input_length"]),
            None if manifest.get("support_cap") is None else int(manifest["support_cap"]),
            None if manifest.get("work_cap") is None else int(manifest["work_cap"]),
            None if manifest.get("certificate_cap") is None else int(manifest["certificate_cap"]),
            None
            if manifest.get("coefficient_bit_cap") is None
            else int(manifest["coefficient_bit_cap"]),
        )
        if capability.manifest() != manifest:
            raise ValueError("capability manifest mismatch")
        return capability


@dataclass
class CrossingMeter:
    capability: Capability
    counters: dict[str, int] = field(default_factory=dict)
    total_work_units: int = 0
    max_support: int = 0
    max_working_support: int = 0
    max_coefficient_bit_volume: int = 0

    def charge(self, category: str, units: int = 1) -> None:
        if units < 0:
            raise ValueError("negative work charge")
        self.counters[category] = self.counters.get(category, 0) + units
        self.total_work_units += units
        if self.total_work_units > self.capability.work_limit:
            raise CrossingOpen(
                OPEN_WORK_BUDGET,
                category,
                {
                    "work_units": self.total_work_units,
                    "work_limit": self.capability.work_limit,
                },
            )

    def check_support(self, size: int, step: int, working_size: int | None = None) -> None:
        self.max_support = max(self.max_support, size)
        self.max_working_support = max(self.max_working_support, working_size or size)
        self.charge("support_entries", max(1, size))
        if size > self.capability.support_limit:
            raise CrossingOpen(
                OPEN_INTERSECTION_CLOSURE,
                "live_signed_support",
                {
                    "step": step,
                    "attempted_support": size,
                    "support_limit": self.capability.support_limit,
                    "working_support": working_size or size,
                },
            )

    def check_coefficient_volume(self, coefficients: Coefficients, step: int) -> int:
        volume = coefficient_bit_volume(coefficients)
        self.max_coefficient_bit_volume = max(self.max_coefficient_bit_volume, volume)
        self.charge("coefficient_bits", max(1, volume))
        if volume > self.capability.coefficient_bit_limit:
            raise CrossingOpen(
                OPEN_WORK_BUDGET,
                "coefficient_bit_volume",
                {
                    "step": step,
                    "coefficient_bit_volume": volume,
                    "coefficient_bit_limit": self.capability.coefficient_bit_limit,
                },
            )
        return volume

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_work_units": self.total_work_units,
            "counters": dict(sorted(self.counters.items())),
            "max_support": self.max_support,
            "max_working_support": self.max_working_support,
            "max_coefficient_bit_volume": self.max_coefficient_bit_volume,
        }


def system_key(space: Subspace) -> tuple[tuple[int, int], ...]:
    return tuple(space)


def system_payload(space: Subspace | None) -> list[list[int]] | None:
    if space is None:
        return None
    return [[mask, rhs] for mask, rhs in space]


def parse_system(payload: list[list[Any]]) -> Subspace:
    return tuple((int(row[0]), int(row[1])) for row in payload)


def coefficient_bit_volume(coefficients: Coefficients) -> int:
    return sum(1 + max(1, abs(value).bit_length()) for value in coefficients.values())


def coefficient_payload(coefficients: Coefficients, dimension: int) -> list[dict[str, Any]]:
    return [
        {
            "space": system_payload(space),
            "dimension": system_dimension(space, dimension),
            "coefficient": coefficient,
        }
        for space, coefficient in sorted(coefficients.items(), key=lambda item: system_key(item[0]))
    ]


def parse_coefficients(payload: list[dict[str, Any]]) -> Coefficients:
    out: Coefficients = {}
    for item in payload:
        space = parse_system(item["space"])
        coefficient = int(item["coefficient"])
        if coefficient == 0 or space in out:
            raise ValueError("noncanonical coefficient payload")
        out[space] = coefficient
    return out


def count_signed(
    coefficients: Coefficients,
    condition: Subspace,
    dimension: int,
    meter: CrossingMeter,
) -> tuple[int, list[dict[str, Any]]]:
    total = 0
    trace: list[dict[str, Any]] = []
    for space, coefficient in sorted(coefficients.items(), key=lambda item: system_key(item[0])):
        meter.charge("count_terms")
        overlap = intersection(space, condition, dimension, meter)
        points = 0 if overlap is None else 1 << system_dimension(overlap, dimension)
        meter.charge("big_integer_bits", max(1, points.bit_length() + abs(coefficient).bit_length()))
        total += coefficient * points
        trace.append(
            {
                "space": system_payload(space),
                "coefficient": coefficient,
                "intersection": system_payload(overlap),
                "points": str(points),
            }
        )
    return total, trace


def prefix_cell(prefix: Subspace, variable: int, bit: int, dimension: int, meter: CrossingMeter) -> Subspace:
    cell = rref_system(prefix + ((1 << (variable - 1), bit),), dimension, meter)
    if cell is None:
        raise AssertionError("coordinate prefix is inconsistent")
    return cell


def finalize_or_raise(body: dict[str, Any], meter: CrossingMeter) -> dict[str, Any]:
    charged = 0
    stated_size = 0
    for _ in range(16):
        body["producer_ledger"] = meter.snapshot()
        body["certificate_bytes"] = stated_size
        probe = dict(body)
        probe["integrity_sha256"] = "0" * 64
        size = len(canonical_json(probe).encode())
        if size > meter.capability.certificate_limit:
            raise CrossingOpen(
                OPEN_CERTIFICATE_VOLUME,
                "certificate_bytes",
                {
                    "attempted_certificate_bytes": size,
                    "certificate_limit": meter.capability.certificate_limit,
                    "semantic_payload_sha256": digest(body),
                },
            )
        if size > charged:
            meter.charge("certificate_bytes", size - charged)
            charged = size
        if size == stated_size:
            break
        stated_size = size
    body["producer_ledger"] = meter.snapshot()
    body["certificate_bytes"] = stated_size
    body["integrity_sha256"] = digest(body)
    return body


def compact_open_certificate(
    *,
    input_digest: str,
    nvars: int,
    capability: Capability,
    meter: CrossingMeter,
    status: str,
    stage: str,
    evidence: dict[str, Any],
    basis_artifact: dict[str, Any] | None = None,
    raw_factors: list[dict[str, Any]] | None = None,
    transitions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "schema": SCHEMA,
        "status": status,
        "reason": stage,
        "input_digest": input_digest,
        "nvars": nvars,
        "capability": capability.manifest(),
        "producer_ledger": meter.snapshot(),
        "overflow_evidence": evidence,
        "p_vs_np": "OPEN",
    }
    if basis_artifact is not None:
        body["basis_artifact"] = basis_artifact
        body["basis_digest"] = digest(basis_artifact)
    if raw_factors is not None:
        body["raw_factors"] = raw_factors
    if transitions is not None:
        body["completed_transitions"] = transitions
    body["integrity_sha256"] = digest(body)
    return body
