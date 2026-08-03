#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
import hashlib, json

SCHEMA = "janus.c045.joint_basis_decomposition_message_discovery.v1"
PROBE_SCHEMA = "janus.c045.c044_basis_probe.v1"
POLICIES = (
    "CANONICAL_FREE",
    "CLAUSE_EXPOSED_GREEDY",
    "SPARSE_ORIGINAL_GREEDY",
    "REVERSE_ORIGINAL_GREEDY",
)
SELECTOR_WORK_EXPONENT = 5
SELECTOR_WORK_MULTIPLIER = 64
SELECTOR_CERT_EXPONENT = 7
SELECTOR_CERT_MULTIPLIER = 128
OPEN_PORTFOLIO_EXHAUSTED = "OPEN_PORTFOLIO_EXHAUSTED"
OPEN_DISCOVERY_BUDGET = "OPEN_DISCOVERY_BUDGET"
OPEN_CERTIFICATE_VOLUME = "OPEN_CERTIFICATE_VOLUME"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


@dataclass
class SelectorCapability:
    input_length: int
    separator_cap: int = 1
    local_support_cap: int | None = None
    probe_work_cap: int | None = None
    probe_certificate_cap: int | None = None
    selector_work_cap: int | None = None
    selector_certificate_cap: int | None = None

    def __post_init__(self) -> None:
        base = self.input_length + 1
        self.selector_work_polynomial = SELECTOR_WORK_MULTIPLIER * base**SELECTOR_WORK_EXPONENT
        self.selector_certificate_polynomial = SELECTOR_CERT_MULTIPLIER * base**SELECTOR_CERT_EXPONENT
        self.selector_work_limit = min(
            self.selector_work_polynomial,
            self.selector_work_cap if self.selector_work_cap is not None else self.selector_work_polynomial,
        )
        self.selector_certificate_limit = min(
            self.selector_certificate_polynomial,
            self.selector_certificate_cap if self.selector_certificate_cap is not None else self.selector_certificate_polynomial,
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "input_length": self.input_length,
            "candidate_policies": list(POLICIES),
            "separator_cap": self.separator_cap,
            "local_support_cap": None if self.local_support_cap is None else str(self.local_support_cap),
            "probe_work_cap": None if self.probe_work_cap is None else str(self.probe_work_cap),
            "probe_certificate_cap": None if self.probe_certificate_cap is None else str(self.probe_certificate_cap),
            "selector_work_exponent": SELECTOR_WORK_EXPONENT,
            "selector_work_multiplier": SELECTOR_WORK_MULTIPLIER,
            "selector_work_polynomial": str(self.selector_work_polynomial),
            "selector_work_cap": None if self.selector_work_cap is None else str(self.selector_work_cap),
            "selector_work_limit": str(self.selector_work_limit),
            "selector_certificate_exponent": SELECTOR_CERT_EXPONENT,
            "selector_certificate_multiplier": SELECTOR_CERT_MULTIPLIER,
            "selector_certificate_polynomial": str(self.selector_certificate_polynomial),
            "selector_certificate_cap": None if self.selector_certificate_cap is None else str(self.selector_certificate_cap),
            "selector_certificate_limit": str(self.selector_certificate_limit),
        }

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "SelectorCapability":
        if tuple(manifest.get("candidate_policies", ())) != POLICIES:
            raise ValueError("candidate policy mismatch")
        obj = cls(
            int(manifest["input_length"]),
            int(manifest["separator_cap"]),
            None if manifest.get("local_support_cap") is None else int(manifest["local_support_cap"]),
            None if manifest.get("probe_work_cap") is None else int(manifest["probe_work_cap"]),
            None if manifest.get("probe_certificate_cap") is None else int(manifest["probe_certificate_cap"]),
            None if manifest.get("selector_work_cap") is None else int(manifest["selector_work_cap"]),
            None if manifest.get("selector_certificate_cap") is None else int(manifest["selector_certificate_cap"]),
        )
        if obj.manifest() != manifest:
            raise ValueError("selector capability mismatch")
        return obj


class SelectorOpen(RuntimeError):
    def __init__(self, status: str, stage: str, evidence: dict[str, Any] | None = None):
        super().__init__(status)
        self.status = status
        self.stage = stage
        self.evidence = evidence or {}


@dataclass
class SelectorMeter:
    capability: SelectorCapability
    counters: dict[str, int] = field(default_factory=dict)
    total_work_units: int = 0

    def charge(self, category: str, units: int = 1) -> None:
        if units < 0:
            raise ValueError("negative selector charge")
        self.counters[category] = self.counters.get(category, 0) + units
        self.total_work_units += units
        if self.total_work_units > self.capability.selector_work_limit:
            raise SelectorOpen(
                OPEN_DISCOVERY_BUDGET,
                category,
                {"selector_work_units": self.total_work_units, "selector_work_limit": self.capability.selector_work_limit},
            )

    def snapshot(self) -> dict[str, Any]:
        return {"total_work_units": self.total_work_units, "counters": dict(sorted(self.counters.items()))}


def rank_masks(masks: Iterable[int], dimension: int, meter: SelectorMeter | None = None) -> int:
    rows = [int(mask) for mask in masks]
    rank = 0
    for column in range(dimension):
        bit = 1 << column
        pivot = next((index for index in range(rank, len(rows)) if rows[index] & bit), None)
        if meter:
            meter.charge("rank_scan", max(1, len(rows) - rank))
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index] & bit:
                rows[index] ^= rows[rank]
                if meter:
                    meter.charge("rank_xor")
        rank += 1
    return rank


def inverse_rows(rows: list[int], dimension: int, meter: SelectorMeter | None = None) -> list[int]:
    if len(rows) != dimension:
        raise ValueError("basis row count mismatch")
    augmented = [int(rows[i]) | (1 << (dimension + i)) for i in range(dimension)]
    rank = 0
    for column in range(dimension):
        bit = 1 << column
        pivot = next((index for index in range(rank, dimension) if augmented[index] & bit), None)
        if meter:
            meter.charge("inverse_scan", max(1, dimension - rank))
        if pivot is None:
            raise ValueError("singular basis transform")
        augmented[rank], augmented[pivot] = augmented[pivot], augmented[rank]
        for index in range(dimension):
            if index != rank and augmented[index] & bit:
                augmented[index] ^= augmented[rank]
                if meter:
                    meter.charge("inverse_xor")
        rank += 1
    mask = (1 << dimension) - 1
    for index, row in enumerate(augmented):
        if row & mask != 1 << index:
            raise ValueError("inverse normalization failed")
    return [(row >> dimension) & mask for row in augmented]


def clause_occurrences(cnf: tuple[tuple[int, ...], ...], nvars: int) -> dict[int, int]:
    counts = {variable: 0 for variable in range(1, nvars + 1)}
    for clause in cnf:
        for literal in clause:
            counts[abs(int(literal))] += 1
    return counts


def greedy_selected_variables(
    cnf: tuple[tuple[int, ...], ...],
    canonical_basis: dict[str, Any],
    policy: str,
    meter: SelectorMeter | None = None,
) -> list[int]:
    dimension = int(canonical_basis["dimension"])
    forms = [(int(mask), int(constant)) for mask, constant in canonical_basis["coordinate_forms"]]
    if dimension == 0:
        return []
    occurrences = clause_occurrences(cnf, len(forms))
    variables = [index for index, (mask, _) in enumerate(forms, 1) if mask]
    if policy == "CLAUSE_EXPOSED_GREEDY":
        variables.sort(key=lambda variable: (-occurrences[variable], forms[variable - 1][0].bit_count(), variable))
    elif policy == "SPARSE_ORIGINAL_GREEDY":
        variables.sort(key=lambda variable: (forms[variable - 1][0].bit_count(), -occurrences[variable], variable))
    elif policy == "REVERSE_ORIGINAL_GREEDY":
        variables.sort(reverse=True)
    else:
        raise ValueError("unsupported greedy policy")

    selected: list[int] = []
    masks: list[int] = []
    current_rank = 0
    for variable in variables:
        if meter:
            meter.charge("greedy_candidate")
        trial = masks + [forms[variable - 1][0]]
        new_rank = rank_masks(trial, dimension, meter)
        if new_rank > current_rank:
            selected.append(variable)
            masks.append(forms[variable - 1][0])
            current_rank = new_rank
            if current_rank == dimension:
                break
    if current_rank != dimension:
        raise ValueError("original variable forms do not span coordinate space")
    return selected


def transform_basis_from_variables(
    canonical_basis: dict[str, Any],
    selected_variables: list[int],
    policy: str,
    meter: SelectorMeter | None = None,
) -> dict[str, Any]:
    dimension = int(canonical_basis["dimension"])
    forms = [(int(mask), int(constant)) for mask, constant in canonical_basis["coordinate_forms"]]
    if dimension == 0:
        return {
            "policy": policy,
            "dimension": 0,
            "selected_variables": [],
            "selected_rows": [],
            "selected_constants": [],
            "inverse_rows": [],
            "coordinate_forms": [list(form) for form in forms],
        }
    if len(selected_variables) != dimension or len(set(selected_variables)) != dimension:
        raise ValueError("selected basis variable count mismatch")
    selected_rows = [forms[variable - 1][0] for variable in selected_variables]
    selected_constants = [forms[variable - 1][1] for variable in selected_variables]
    inverse = inverse_rows(selected_rows, dimension, meter)
    constants_mask = sum((constant & 1) << index for index, constant in enumerate(selected_constants))
    transformed: list[list[int]] = []
    for source_mask, source_constant in forms:
        new_mask = 0
        for bit in range(dimension):
            if source_mask >> bit & 1:
                new_mask ^= inverse[bit]
                if meter:
                    meter.charge("basis_form_xor")
        new_constant = source_constant ^ ((new_mask & constants_mask).bit_count() & 1)
        transformed.append([new_mask, new_constant])
        if meter:
            meter.charge("basis_form_emit")
    artifact = {
        "policy": policy,
        "dimension": dimension,
        "selected_variables": selected_variables,
        "selected_rows": selected_rows,
        "selected_constants": selected_constants,
        "inverse_rows": inverse,
        "coordinate_forms": transformed,
    }
    for coordinate, variable in enumerate(selected_variables, 1):
        if transformed[variable - 1] != [1 << (coordinate - 1), 0]:
            raise AssertionError("selected original variable is not a new coordinate")
    return artifact


def verify_transform(canonical_basis: dict[str, Any], artifact: dict[str, Any]) -> bool:
    try:
        replay = transform_basis_from_variables(
            canonical_basis,
            [int(v) for v in artifact["selected_variables"]],
            str(artifact["policy"]),
            None,
        )
        expected = dict(replay)
        if "candidate_index" in artifact:
            expected["candidate_index"] = int(artifact["candidate_index"])
        if "basis_digest" in artifact:
            expected["basis_digest"] = artifact["basis_digest"]
            probe = dict(artifact)
            probe.pop("basis_digest", None)
            if digest(probe) != artifact["basis_digest"]:
                return False
        return expected == artifact
    except (KeyError, TypeError, ValueError, AssertionError):
        return False


def generate_candidate_manifest(
    cnf: tuple[tuple[int, ...], ...],
    canonical_basis: dict[str, Any],
    meter: SelectorMeter | None = None,
) -> dict[str, Any]:
    dimension = int(canonical_basis["dimension"])
    raw_candidates: list[dict[str, Any]] = []
    canonical_selected = [int(v) for v in canonical_basis.get("free_variables", [])]
    canonical_transform = transform_basis_from_variables(canonical_basis, canonical_selected, "CANONICAL_FREE", meter)
    raw_candidates.append(canonical_transform)
    for policy in POLICIES[1:]:
        selected = greedy_selected_variables(cnf, canonical_basis, policy, meter)
        raw_candidates.append(transform_basis_from_variables(canonical_basis, selected, policy, meter))

    unique: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    aliases: list[dict[str, Any]] = []
    for candidate in raw_candidates:
        key = digest(candidate["coordinate_forms"])
        if key in seen:
            aliases.append({"policy": candidate["policy"], "candidate_index": seen[key]})
            continue
        index = len(unique)
        seen[key] = index
        candidate = dict(candidate)
        candidate["candidate_index"] = index
        candidate["basis_digest"] = digest(candidate)
        unique.append(candidate)
    manifest = {
        "policies": list(POLICIES),
        "dimension": dimension,
        "candidates": unique,
        "aliases": aliases,
    }
    manifest["manifest_digest"] = digest(manifest)
    return manifest


def finalize_certificate(body: dict[str, Any], capability: SelectorCapability, meter: SelectorMeter) -> dict[str, Any]:
    # Certificate size is self-referential because the charged ledger and the
    # stated byte count are themselves serialized. Iterate to a fixed point,
    # charging every newly exposed byte exactly once.
    charged = 0
    stated_size = 0
    for _ in range(32):
        body["selector_ledger"] = meter.snapshot()
        body["certificate_bytes"] = stated_size
        probe = dict(body)
        probe["integrity_sha256"] = "0" * 64
        size = len(canonical_json(probe).encode())
        if size > capability.selector_certificate_limit:
            raise SelectorOpen(
                OPEN_CERTIFICATE_VOLUME,
                "selector_certificate_bytes",
                {
                    "attempted_certificate_bytes": size,
                    "selector_certificate_limit": capability.selector_certificate_limit,
                },
            )
        if size > charged:
            meter.charge("certificate_bytes", size - charged)
            charged = size
        if size == stated_size:
            break
        stated_size = size
    else:
        raise AssertionError("selector certificate size failed to stabilize")
    body["selector_ledger"] = meter.snapshot()
    body["certificate_bytes"] = stated_size
    body["integrity_sha256"] = digest(body)
    return body
