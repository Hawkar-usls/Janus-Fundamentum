#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from janus_c047_affine_trellis_core import (
    Capability as TrellisCapability,
    Meter as TrellisMeter,
    OpenResult as TrellisOpenResult,
    affine_rref,
    canonical_json,
    combine_functionals,
    digest,
    extend_avoiding,
    fixed_point_certificate as trellis_fixed_point_certificate,
    input_length,
    intersection,
    linear_rref,
    normalize_factors,
    point_in_factor,
    restrict_functional,
    solve_point,
    span,
)

SCHEMA = "janus.c049.jko_fpt_layout_integration_phase_a.v1"
CONSTRUCTOR_SCHEMA = "janus.c049.layout_constructor_transcript.v1"
NO_LAYOUT_AT_CAP = "NO_LAYOUT_AT_CAP"
OPEN_FPT_ENGINE_PENDING = "OPEN_FPT_ENGINE_PENDING"
OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT = "OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT"
OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT = "OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT"
OPEN_DISCOVERY_BUDGET = "OPEN_DISCOVERY_BUDGET"
OPEN_WORK_BUDGET = "OPEN_WORK_BUDGET"
OPEN_CERTIFICATE_VOLUME = "OPEN_CERTIFICATE_VOLUME"

DISCOVERY_MULTIPLIER = 128
DISCOVERY_EXPONENT = 6
WORK_MULTIPLIER = 256
WORK_EXPONENT = 7
CERT_MULTIPLIER = 128
CERT_EXPONENT = 6
MAX_K_CAP = 8


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode()).hexdigest()


@dataclass
class IntegrationCapability:
    input_length: int
    requested_k: int
    discovery_cap: int | None = None
    work_cap: int | None = None
    certificate_cap: int | None = None
    trellis_work_cap: int | None = None
    trellis_certificate_cap: int | None = None

    def __post_init__(self) -> None:
        base = self.input_length + 1
        self.k = min(MAX_K_CAP, max(0, int(self.requested_k)))
        self.discovery_polynomial = DISCOVERY_MULTIPLIER * base**DISCOVERY_EXPONENT
        self.work_polynomial = WORK_MULTIPLIER * base**WORK_EXPONENT
        self.certificate_polynomial = CERT_MULTIPLIER * base**CERT_EXPONENT
        self.discovery_limit = min(
            self.discovery_polynomial,
            self.discovery_cap if self.discovery_cap is not None else self.discovery_polynomial,
        )
        self.work_limit = min(
            self.work_polynomial,
            self.work_cap if self.work_cap is not None else self.work_polynomial,
        )
        self.certificate_limit = min(
            self.certificate_polynomial,
            self.certificate_cap if self.certificate_cap is not None else self.certificate_polynomial,
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "input_length": self.input_length,
            "requested_k": self.requested_k,
            "max_k_cap": MAX_K_CAP,
            "effective_k": self.k,
            "discovery_polynomial": str(self.discovery_polynomial),
            "discovery_cap": None if self.discovery_cap is None else str(self.discovery_cap),
            "discovery_limit": str(self.discovery_limit),
            "work_polynomial": str(self.work_polynomial),
            "work_cap": None if self.work_cap is None else str(self.work_cap),
            "work_limit": str(self.work_limit),
            "certificate_polynomial": str(self.certificate_polynomial),
            "certificate_cap": None if self.certificate_cap is None else str(self.certificate_cap),
            "certificate_limit": str(self.certificate_limit),
            "trellis_work_cap": None if self.trellis_work_cap is None else str(self.trellis_work_cap),
            "trellis_certificate_cap": None
            if self.trellis_certificate_cap is None
            else str(self.trellis_certificate_cap),
        }


class IntegrationOpen(Exception):
    def __init__(self, status: str, stage: str, evidence: dict[str, Any]):
        super().__init__(status)
        self.status = status
        self.stage = stage
        self.evidence = evidence


@dataclass
class IntegrationMeter:
    capability: IntegrationCapability
    discovery_work: int = 0
    total_work: int = 0
    certificate_bytes_charged: int = 0
    factor_intersections: int = 0
    cut_intersections: int = 0

    def charge_discovery(self, stage: str, amount: int = 1) -> None:
        amount = max(1, int(amount))
        attempted_discovery = self.discovery_work + amount
        attempted_total = self.total_work + amount
        if attempted_discovery > self.capability.discovery_limit:
            raise IntegrationOpen(
                OPEN_DISCOVERY_BUDGET,
                stage,
                {
                    "attempted_discovery_work": attempted_discovery,
                    "discovery_limit": self.capability.discovery_limit,
                },
            )
        if attempted_total > self.capability.work_limit:
            raise IntegrationOpen(
                OPEN_WORK_BUDGET,
                stage,
                {"attempted_work": attempted_total, "work_limit": self.capability.work_limit},
            )
        self.discovery_work = attempted_discovery
        self.total_work = attempted_total

    def charge_work(self, stage: str, amount: int = 1) -> None:
        amount = max(1, int(amount))
        attempted = self.total_work + amount
        if attempted > self.capability.work_limit:
            raise IntegrationOpen(
                OPEN_WORK_BUDGET,
                stage,
                {"attempted_work": attempted, "work_limit": self.capability.work_limit},
            )
        self.total_work = attempted

    def snapshot(self) -> dict[str, Any]:
        return {
            "discovery_work_units": self.discovery_work,
            "total_work_units": self.total_work,
            "factor_intersections": self.factor_intersections,
            "cut_intersections": self.cut_intersections,
            "certificate_bytes_charged": self.certificate_bytes_charged,
        }


def normal_space(factor: dict[str, Any]) -> tuple[int, ...]:
    return tuple(mask for mask, _ in factor["equations"])


def layout_data_from_spaces(
    spaces: list[tuple[int, ...]],
    order_positions: list[int],
    dimension: int,
    meter: IntegrationMeter | None = None,
) -> dict[str, Any]:
    if sorted(order_positions) != list(range(len(spaces))):
        raise ValueError("order is not a permutation")
    ordered = [spaces[index] for index in order_positions]
    prefix = [()]
    for space in ordered:
        if meter is not None:
            meter.charge_work("layout_prefix_span", max(1, len(space)))
        prefix.append(span(prefix[-1], space, dimension=dimension))
    suffix: list[tuple[int, ...]] = [() for _ in range(len(ordered) + 1)]
    for index in range(len(ordered) - 1, -1, -1):
        if meter is not None:
            meter.charge_work("layout_suffix_span", max(1, len(ordered[index])))
        suffix[index] = span(ordered[index], suffix[index + 1], dimension=dimension)
    boundaries: list[tuple[int, ...]] = []
    widths: list[int] = []
    for index in range(len(ordered) + 1):
        if meter is not None:
            meter.charge_work("layout_cut_intersection", max(1, len(prefix[index]) + len(suffix[index])))
            meter.cut_intersections += 1
        boundary = intersection(prefix[index], suffix[index], dimension)
        boundaries.append(boundary)
        widths.append(len(boundary))
    return {
        "order_positions": list(order_positions),
        "cut_widths": widths,
        "cut_bases": [list(boundary) for boundary in boundaries],
        "maximum_width": max(widths, default=0),
        "total_width": sum(widths),
    }


def jko_column_reduction_skeleton(
    normalized_factors: list[dict[str, Any]],
    dimension: int,
    k: int,
    meter: IntegrationMeter,
) -> dict[str, Any]:
    spaces = [normal_space(factor) for factor in normalized_factors]
    records: list[dict[str, Any]] = []
    first_obstruction: dict[str, Any] | None = None
    for index, space in enumerate(spaces):
        meter.charge_discovery("jko_other_span", max(1, sum(len(s) for j, s in enumerate(spaces) if j != index)))
        other_span = span(*(spaces[:index] + spaces[index + 1 :]), dimension=dimension) if len(spaces) > 1 else ()
        meter.charge_discovery("jko_factor_intersection", max(1, len(space) + len(other_span)))
        meter.factor_intersections += 1
        reduced = intersection(space, other_span, dimension)
        record = {
            "normalized_position": index,
            "factor_id": normalized_factors[index]["factor_id"],
            "original_normal_basis": list(space),
            "other_span_basis": list(other_span),
            "reduced_normal_basis": list(reduced),
            "reduced_dimension": len(reduced),
            "obstruction_threshold": 2 * k,
        }
        records.append(record)
        if first_obstruction is None and len(reduced) > 2 * k:
            first_obstruction = {
                "normalized_position": index,
                "factor_id": normalized_factors[index]["factor_id"],
                "reduced_dimension": len(reduced),
                "threshold": 2 * k,
                "reduced_normal_basis": list(reduced),
                "original_normal_basis": list(space),
                "other_span_basis": list(other_span),
                "theorem": "JKO_PROPOSITION_2_2_LOCAL_INTERSECTION_GT_2K",
            }
    reduced_spaces = [tuple(record["reduced_normal_basis"]) for record in records]
    return {
        "theorem_source": "Jeong-Kim-Oum arXiv:1507.02184v4, Lemma 5.2 and Proposition 2.2",
        "parameter_k": k,
        "records": records,
        "reduced_spaces": [list(space) for space in reduced_spaces],
        "first_local_obstruction": first_obstruction,
        "preprocessing_digest": sha256_obj(
            {
                "parameter_k": k,
                "records": records,
                "first_local_obstruction": first_obstruction,
            }
        ),
    }


def fixed_point_outer_certificate(
    body: dict[str, Any], capability: IntegrationCapability, meter: IntegrationMeter
) -> dict[str, Any]:
    charged = 0
    stated = 0
    for _ in range(24):
        body["integration_ledger"] = meter.snapshot()
        body["certificate_bytes"] = stated
        probe = dict(body)
        probe["integrity_sha256"] = "0" * 64
        size = len(canonical_json(probe).encode())
        if size > capability.certificate_limit:
            raise IntegrationOpen(
                OPEN_CERTIFICATE_VOLUME,
                "outer_certificate_bytes",
                {
                    "attempted_certificate_bytes": size,
                    "certificate_limit": capability.certificate_limit,
                    "semantic_payload_sha256": sha256_obj(body),
                },
            )
        if size > charged:
            meter.charge_work("outer_certificate_bytes", size - charged)
            meter.certificate_bytes_charged += size - charged
            charged = size
        if size == stated:
            break
        stated = size
    body["integration_ledger"] = meter.snapshot()
    body["certificate_bytes"] = stated
    body["integrity_sha256"] = sha256_obj(body)
    return body


def make_found_layout_transcript(
    order_positions: list[int],
    cut_widths: list[int],
    cut_bases: list[list[int]],
    *,
    constructor_id: str,
    discovery_claim: bool,
    constructor_trace: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = {
        "schema": CONSTRUCTOR_SCHEMA,
        "terminal": "FOUND_LAYOUT",
        "constructor_id": constructor_id,
        "discovery_claim": bool(discovery_claim),
        "order_positions": list(order_positions),
        "cut_widths": list(cut_widths),
        "cut_bases": [list(basis) for basis in cut_bases],
        "constructor_trace": constructor_trace or {},
    }
    body["transcript_digest"] = sha256_obj(body)
    return body


def validate_transcript_digest(transcript: dict[str, Any]) -> bool:
    if transcript.get("schema") != CONSTRUCTOR_SCHEMA:
        return False
    digest_value = transcript.get("transcript_digest")
    if not isinstance(digest_value, str):
        return False
    body = dict(transcript)
    body.pop("transcript_digest", None)
    return sha256_obj(body) == digest_value
