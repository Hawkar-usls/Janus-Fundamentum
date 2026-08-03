#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from janus_c044_local_signed_support_core import (
    Capability, Meter, OpenResult, canonical_input, digest as c044_digest,
    encoded_length, evaluate_affine, evaluate_cnf, fixed_point_certificate,
    lift_coordinate_assignment, normalize_cnf, parameterize_affine,
    translate_factors, variables_in_affine, variables_in_cnf,
)
from janus_c044_local_signed_support_verifier import (
    construct_plan_independent, construct_result_independent, factors_payload,
)
from janus_c045_basis_portfolio_core import (
    SCHEMA, PROBE_SCHEMA, OPEN_PORTFOLIO_EXHAUSTED, OPEN_CERTIFICATE_VOLUME,
    SelectorCapability, SelectorMeter, canonical_json, digest, finalize_certificate,
    generate_candidate_manifest, verify_transform,
)

CNF = tuple[tuple[int, ...], ...]
Equation = tuple[int, int]


def construct_probe_independent(
    cnf: CNF,
    affine: tuple[Equation, ...],
    nvars: int,
    candidate: dict[str, Any],
    selector_capability: SelectorCapability,
) -> dict[str, Any]:
    capability = Capability(
        selector_capability.input_length,
        selector_capability.separator_cap,
        selector_capability.local_support_cap,
        selector_capability.probe_work_cap,
        selector_capability.probe_certificate_cap,
    )
    meter = Meter(capability)
    basis = {
        "status": "SAT",
        "dimension": int(candidate["dimension"]),
        "coordinate_forms": [list(row) for row in candidate["coordinate_forms"]],
        "transform_policy": candidate["policy"],
        "transform_digest": candidate["basis_digest"],
    }
    raw_factors = None
    base = {
        "schema": PROBE_SCHEMA,
        "candidate_index": int(candidate["candidate_index"]),
        "candidate_basis_digest": candidate["basis_digest"],
        "capability": capability.manifest(),
    }
    try:
        factors, raw_factors = translate_factors(cnf, basis, meter)
        active = set().union(*(set(factor.scope) for factor in factors)) if factors else set()
        plan = construct_plan_independent(factors, set(active), set(), capability, meter)
        result = construct_result_independent(plan, {factor.factor_id: factor for factor in factors}, {}, meter)
        body: dict[str, Any] = {
            **base,
            "status": result["status"],
            "reason": "C044_PROBE_CLOSED",
            "basis_artifact": basis,
            "raw_factors": raw_factors,
            "factors": factors_payload(factors),
            "plan": plan,
            "plan_digest": c044_digest(plan),
            "result": result,
        }
        if result["status"] == "SAT":
            coordinate_assignment = {int(v): bool(x) for v, x in result["assignment"].items()}
            witness_mask = lift_coordinate_assignment(coordinate_assignment, basis)
            meter.charge("witness_lift", max(1, nvars + int(basis["dimension"])))
            if not evaluate_affine(affine, witness_mask) or not evaluate_cnf(cnf, witness_mask):
                raise AssertionError("independent candidate witness failed")
            body["witness_mask"] = str(witness_mask)
            body["witness"] = {str(v): bool(witness_mask & (1 << (v - 1))) for v in range(1, nvars + 1)}
        return fixed_point_certificate(body, capability, meter)
    except OpenResult as error:
        body = {
            **base,
            "status": error.status,
            "reason": error.stage,
            "overflow_evidence": error.evidence,
            "basis_artifact": basis,
            "producer_ledger": meter.snapshot(),
        }
        if raw_factors is not None and error.status != OPEN_CERTIFICATE_VOLUME:
            body["raw_factors"] = raw_factors
        body["integrity_sha256"] = c044_digest(body)
        return body


def selection_score(probe: dict[str, Any]) -> tuple[int, int, int, str]:
    ledger = probe["producer_ledger"]
    return (
        int(ledger["max_attempted_live_support"]),
        int(ledger["max_attempted_working_support"]),
        int(ledger["total_work_units"]),
        str(probe["candidate_basis_digest"]),
    )


def verify_basis_portfolio(
    cnf: CNF,
    affine: tuple[Equation, ...],
    certificate: dict[str, Any],
    *,
    nvars_hint: int = 0,
) -> bool:
    try:
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
        input_object = canonical_input(cnf, affine, nvars)
        input_digest = digest(input_object)
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
        canonical_basis = parameterize_affine(affine, nvars)
        meter.charge("canonical_basis_bytes", len(canonical_json(canonical_basis)))
        if canonical_basis["status"] == "UNSAT":
            expected = finalize_certificate(
                {
                    **base,
                    "status": "UNSAT",
                    "reason": "AFFINE_CONTRADICTION",
                    "canonical_basis": canonical_basis,
                },
                capability,
                meter,
            )
            return expected == certificate

        manifest = generate_candidate_manifest(cnf, canonical_basis, meter)
        for candidate in manifest["candidates"]:
            if not verify_transform(canonical_basis, candidate):
                return False
        expected_probes: list[dict[str, Any]] = []
        for candidate in manifest["candidates"]:
            meter.charge("candidate_probe_dispatch")
            expected_probes.append(
                construct_probe_independent(cnf, affine, nvars, candidate, capability)
            )

        exact = [probe for probe in expected_probes if probe["status"] in ("SAT", "UNSAT")]
        if exact:
            statuses = {probe["status"] for probe in exact}
            if len(statuses) != 1:
                return False
            selected = min(exact, key=selection_score)
            expected_body: dict[str, Any] = {
                **base,
                "status": selected["status"],
                "reason": "FROZEN_BASIS_PORTFOLIO_SELECTED",
                "canonical_basis": canonical_basis,
                "candidate_manifest": manifest,
                "candidate_manifest_digest": manifest["manifest_digest"],
                "probes": expected_probes,
                "selected_candidate_index": int(selected["candidate_index"]),
                "selected_candidate_basis_digest": selected["candidate_basis_digest"],
                "selection_score": list(selection_score(selected)),
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
                "probes": expected_probes,
            }
        expected = finalize_certificate(expected_body, capability, meter)
        return expected == certificate
    except (KeyError, TypeError, ValueError, AssertionError, OpenResult):
        return False
