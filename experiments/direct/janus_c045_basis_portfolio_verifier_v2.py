#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

import janus_c045_basis_portfolio_verifier as legacy
from janus_c044_local_signed_support_core import (
    canonical_input,
    encoded_length,
    normalize_cnf,
    parameterize_affine,
    variables_in_affine,
    variables_in_cnf,
)
from janus_c045_basis_portfolio_core import (
    SCHEMA,
    OPEN_PORTFOLIO_EXHAUSTED,
    SelectorCapability,
    SelectorMeter,
    SelectorOpen,
    canonical_json,
    digest,
    finalize_certificate,
    generate_candidate_manifest,
    verify_transform,
)

CNF = tuple[tuple[int, ...], ...]
Equation = tuple[int, int]


def _selection_score(probe: dict[str, Any]) -> tuple[int, int, int, str]:
    return legacy.selection_score(probe)


def _replay_selector_open(
    cnf: CNF,
    affine: tuple[Equation, ...],
    certificate: dict[str, Any],
    *,
    nvars_hint: int,
) -> bool:
    if certificate.get("schema") != SCHEMA:
        return False
    integrity = certificate.get("integrity_sha256")
    if not isinstance(integrity, str):
        return False
    body = dict(certificate)
    body.pop("integrity_sha256", None)
    if digest(body) != integrity:
        return False

    cnf = normalize_cnf(cnf)
    nvars = max(
        nvars_hint,
        max(variables_in_cnf(cnf) | variables_in_affine(affine), default=0),
    )
    input_digest = digest(canonical_input(cnf, affine, nvars))
    if certificate.get("input_digest") != input_digest:
        return False
    if int(certificate.get("nvars", -1)) != nvars:
        return False

    capability = SelectorCapability.from_manifest(certificate["capability"])
    if capability.input_length != encoded_length(cnf, affine, nvars):
        return False
    meter = SelectorMeter(capability)
    base = {
        "schema": SCHEMA,
        "input_digest": input_digest,
        "nvars": nvars,
        "capability": capability.manifest(),
        "p_vs_np": "OPEN",
    }
    try:
        canonical_basis = parameterize_affine(affine, nvars)
        meter.charge("canonical_basis_bytes", len(canonical_json(canonical_basis)))
        if canonical_basis["status"] == "UNSAT":
            finalize_certificate(
                {
                    **base,
                    "status": "UNSAT",
                    "reason": "AFFINE_CONTRADICTION",
                    "canonical_basis": canonical_basis,
                },
                capability,
                meter,
            )
            return False

        manifest = generate_candidate_manifest(cnf, canonical_basis, meter)
        for candidate in manifest["candidates"]:
            if not verify_transform(canonical_basis, candidate):
                return False
        probes: list[dict[str, Any]] = []
        for candidate in manifest["candidates"]:
            meter.charge("candidate_probe_dispatch")
            probes.append(
                legacy.construct_probe_independent(
                    cnf, affine, nvars, candidate, capability
                )
            )

        exact = [probe for probe in probes if probe["status"] in ("SAT", "UNSAT")]
        if exact:
            statuses = {probe["status"] for probe in exact}
            if len(statuses) != 1:
                return False
            selected = min(exact, key=_selection_score)
            expected_body: dict[str, Any] = {
                **base,
                "status": selected["status"],
                "reason": "FROZEN_BASIS_PORTFOLIO_SELECTED",
                "canonical_basis": canonical_basis,
                "candidate_manifest": manifest,
                "candidate_manifest_digest": manifest["manifest_digest"],
                "probes": probes,
                "selected_candidate_index": int(selected["candidate_index"]),
                "selected_candidate_basis_digest": selected["candidate_basis_digest"],
                "selection_score": list(_selection_score(selected)),
            }
            if selected["status"] == "SAT":
                expected_body["witness_mask"] = selected["witness_mask"]
                expected_body["witness"] = selected["witness"]
        else:
            expected_body = {
                **base,
                "status": OPEN_PORTFOLIO_EXHAUSTED,
                "reason": "ALL_FROZEN_BASIS_CANDIDATES_OPEN",
                "canonical_basis": canonical_basis,
                "candidate_manifest": manifest,
                "candidate_manifest_digest": manifest["manifest_digest"],
                "probes": probes,
            }
        finalize_certificate(expected_body, capability, meter)
        return False
    except SelectorOpen as error:
        expected = {
            **base,
            "status": error.status,
            "reason": error.stage,
            "overflow_evidence": error.evidence,
            "selector_ledger": meter.snapshot(),
        }
        expected["integrity_sha256"] = digest(expected)
        return expected == certificate


def verify_basis_portfolio_v2(
    cnf: CNF,
    affine: tuple[Equation, ...],
    certificate: dict[str, Any],
    *,
    nvars_hint: int = 0,
) -> bool:
    try:
        if legacy.verify_basis_portfolio(
            cnf, affine, certificate, nvars_hint=nvars_hint
        ):
            return True
    except SelectorOpen:
        pass
    try:
        return _replay_selector_open(
            cnf, affine, certificate, nvars_hint=nvars_hint
        )
    except (KeyError, TypeError, ValueError, AssertionError):
        return False
