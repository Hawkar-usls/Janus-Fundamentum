#!/usr/bin/env python3
from __future__ import annotations
from typing import Any

from janus_c047_affine_trellis_core import *
from janus_c048_layout_core import *


def independent_order_probe(
    factors: list[dict[str, Any]],
    dimension: int,
    order_positions: list[int],
    constructor: str,
    *,
    requested_width_cap: int,
    work_cap: int | None,
    certificate_cap: int | None,
) -> dict[str, Any]:
    normalized = normalize_factors(factors, dimension)
    if sorted(order_positions) != list(range(len(normalized))):
        raise ValueError("invalid order")
    L = input_length(normalized, dimension)
    cap = Capability(L, requested_width_cap, work_cap, certificate_cap)
    meter = Meter(cap)
    base = {
        "schema": SCHEMA,
        "dimension": dimension,
        "input_factors": [
            {
                "factor_id": factor["factor_id"],
                "equations": [list(eq) for eq in factor["equations"]],
                "input_position": factor["input_position"],
            }
            for factor in normalized
        ],
        "capability": cap.manifest(),
        "p_vs_np": "OPEN",
    }
    try:
        meter.charge("supplied_order_validation", max(1, len(order_positions)))
        ordered = [normalized[index] for index in order_positions]
        layout = layout_data(normalized, order_positions, dimension)
        widths = list(layout["cut_widths"])
        boundaries = [tuple(boundary) for boundary in layout["boundaries"]]
        meter.max_width = max(widths, default=0)
        for cut, width in enumerate(widths):
            if width > cap.width_limit:
                result = {
                    **base,
                    "status": OPEN_CUT_WIDTH,
                    "reason": "FROZEN_CANDIDATE_EXCEEDS_WIDTH_CAP",
                    "order_policy": constructor,
                    "factor_order": layout["factor_order"],
                    "order_positions": order_positions,
                    "cut_widths": widths,
                    "first_overflow_cut": cut,
                    "overflow_boundary": list(boundaries[cut]),
                    "overflow_width": width,
                }
                result["producer_ledger"] = meter.snapshot()
                result["integrity_sha256"] = digest(result)
                return result

        reachable: dict[int, tuple[LinearSpace, int, dict[str, Any] | None]] = {
            0: ((), 0, None)
        }
        layers: list[dict[str, Any]] = [
            {
                "cut": 0,
                "boundary_basis": list(boundaries[0]),
                "reachable_states": [0],
                "records": {"0": {"prefix_basis": [], "prefix_values": 0, "parent": None}},
            }
        ]
        for layer_index, factor in enumerate(ordered, 1):
            previous_boundary = boundaries[layer_index - 1]
            current_boundary = boundaries[layer_index]
            W = normal_space(factor)
            next_reachable: dict[int, tuple[LinearSpace, int, dict[str, Any]]] = {}
            transitions: list[dict[str, Any]] = []
            for previous_state in sorted(reachable):
                previous_basis, previous_values, _ = reachable[previous_state]
                for current_state in range(1 << len(current_boundary)):
                    meter.transition_tests += 1
                    meter.charge(
                        "transition_test",
                        max(1, len(previous_boundary) + len(current_boundary) + len(W)),
                    )
                    local = extend_avoiding(
                        previous_boundary,
                        previous_state,
                        current_boundary,
                        current_state,
                        factor["equations"],
                        dimension,
                    )
                    if local is None:
                        transitions.append(
                            {"from": previous_state, "to": current_state, "status": "BLOCKED"}
                        )
                        continue
                    transitions.append(
                        {
                            "from": previous_state,
                            "to": current_state,
                            "status": "OPEN_EDGE",
                            "local_basis": local["local_basis"],
                            "local_values": local["local_values"],
                            "factor_values": local["factor_values"],
                            "separating_row": local["separating_row"],
                        }
                    )
                    if current_state in next_reachable:
                        continue
                    total_basis, total_values = combine_functionals(
                        previous_basis,
                        previous_values,
                        W,
                        int(local["factor_values"]),
                        dimension,
                    )
                    if restrict_functional(total_basis, total_values, current_boundary) != current_state:
                        raise AssertionError("current boundary mismatch")
                    parent = {
                        "previous_state": previous_state,
                        "factor_id": factor["factor_id"],
                        "factor_values": local["factor_values"],
                        "separating_row": local["separating_row"],
                    }
                    next_reachable[current_state] = (total_basis, total_values, parent)
            reachable = next_reachable
            meter.states_materialized += len(reachable)
            layers.append(
                {
                    "cut": layer_index,
                    "factor_id": factor["factor_id"],
                    "boundary_basis": list(current_boundary),
                    "reachable_states": sorted(reachable),
                    "records": {
                        str(state): {
                            "prefix_basis": list(record[0]),
                            "prefix_values": record[1],
                            "parent": record[2],
                        }
                        for state, record in sorted(reachable.items())
                    },
                    "transition_records": transitions,
                }
            )

        result: dict[str, Any] = {
            **base,
            "order_policy": constructor,
            "factor_order": layout["factor_order"],
            "order_positions": order_positions,
            "cut_widths": widths,
            "boundaries": [list(boundary) for boundary in boundaries],
            "layers": layers,
        }
        if 0 not in reachable:
            result.update(
                {
                    "status": "UNSAT",
                    "reason": "ROOT_FUNCTIONAL_SET_EMPTY",
                    "root_reachable_states": [],
                }
            )
        else:
            root_basis, root_values, _ = reachable[0]
            point = solve_point(root_basis, root_values, dimension)
            if point is None:
                raise AssertionError("root lift failed")
            if any(point_in_factor(point, factor["equations"]) for factor in normalized):
                raise AssertionError("witness lies in a forbidden factor")
            result.update(
                {
                    "status": "SAT",
                    "reason": "ROOT_FUNCTIONAL_EXISTS",
                    "root_reachable_states": [0],
                    "ambient_witness": str(point),
                    "witness_bits": [(point >> i) & 1 for i in range(dimension)],
                    "root_normal_basis": list(root_basis),
                    "root_functional_values": root_values,
                }
            )
        return fixed_point_certificate(result, cap, meter)
    except OpenResult as error:
        result = {
            **base,
            "status": error.status,
            "reason": error.stage,
            "overflow_evidence": error.evidence,
            "producer_ledger": meter.snapshot(),
        }
        result["integrity_sha256"] = digest(result)
        return result


def independent_selector_fixed_point(
    body: dict[str, Any],
    certificate_limit: int,
) -> dict[str, Any]:
    stated = 0
    for _ in range(24):
        body["certificate_bytes"] = stated
        probe = dict(body)
        probe["integrity_sha256"] = "0" * 64
        size = len(canonical_json(probe).encode())
        if size > certificate_limit:
            refusal = {
                "schema": SCHEMA_C048,
                "status": OPEN_CERTIFICATE_VOLUME,
                "reason": "selector_certificate_bytes",
                "dimension": body.get("dimension"),
                "input_length": body.get("input_length"),
                "requested_width_cap": body.get("requested_width_cap"),
                "discovery_cap": body.get("discovery_cap"),
                "probe_work_cap": body.get("probe_work_cap"),
                "probe_certificate_cap": body.get("probe_certificate_cap"),
                "selector_certificate_cap": body.get("selector_certificate_cap"),
                "attempted_certificate_bytes": size,
                "certificate_limit": certificate_limit,
                "semantic_payload_sha256": digest(body),
                "p_vs_np": "OPEN",
            }
            refusal["integrity_sha256"] = digest(refusal)
            return refusal
        if size == stated:
            break
        stated = size
    body["certificate_bytes"] = stated
    body["integrity_sha256"] = digest(body)
    return body


def reconstruct_selector(
    factors: list[dict[str, Any]],
    dimension: int,
    *,
    requested_width_cap: int,
    discovery_cap: int | None,
    probe_work_cap: int | None,
    probe_certificate_cap: int | None,
    selector_certificate_cap: int | None,
) -> dict[str, Any]:
    normalized = normalize_factors(factors, dimension)
    L = input_length(normalized, dimension)
    manifest_result = generate_candidate_manifest(
        factors,
        dimension,
        discovery_cap=discovery_cap,
    )
    base = {
        "schema": SCHEMA_C048,
        "dimension": dimension,
        "input_factors": [
            {
                "factor_id": factor["factor_id"],
                "equations": [list(eq) for eq in factor["equations"]],
                "input_position": factor["input_position"],
            }
            for factor in normalized
        ],
        "input_length": L,
        "requested_width_cap": requested_width_cap,
        "discovery_cap": discovery_cap,
        "probe_work_cap": probe_work_cap,
        "probe_certificate_cap": probe_certificate_cap,
        "selector_certificate_cap": selector_certificate_cap,
        "p_vs_np": "OPEN",
    }
    if manifest_result["status"] != "MANIFEST_FROZEN":
        result = {**base, **manifest_result}
        result["integrity_sha256"] = digest(result)
        return result

    manifest = manifest_result["manifest"]
    manifest_digest = manifest["manifest_digest"]
    probes: list[dict[str, Any]] = []
    successful: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any]]] = []
    for candidate in manifest["unique_candidates"]:
        probe = independent_order_probe(
            factors,
            dimension,
            list(candidate["order_positions"]),
            candidate["constructor"],
            requested_width_cap=requested_width_cap,
            work_cap=probe_work_cap,
            certificate_cap=probe_certificate_cap,
        )
        probes.append(
            {
                "candidate_id": candidate["candidate_id"],
                "layout_digest": candidate["layout_digest"],
                "constructor": candidate["constructor"],
                "probe": probe,
            }
        )
        if probe["status"] in ("SAT", "UNSAT"):
            cost = (
                max(probe["cut_widths"], default=0),
                sum(probe["cut_widths"]),
                int(probe["producer_ledger"]["total_work_units"]),
                candidate["layout_digest"],
            )
            successful.append((cost, candidate, probe))

    result: dict[str, Any] = {
        **base,
        "manifest": manifest,
        "manifest_digest_before_probes": manifest_digest,
        "probes": probes,
        "probe_count": len(probes),
    }
    if not successful:
        result.update(
            {
                "status": OPEN_PORTFOLIO_EXHAUSTED,
                "reason": "NO_FROZEN_LAYOUT_CLOSED_WITHIN_CAPABILITY",
                "selected_candidate_id": None,
                "selected_probe_digest": None,
            }
        )
    else:
        successful.sort(key=lambda item: item[0])
        cost, candidate, probe = successful[0]
        result.update(
            {
                "status": probe["status"],
                "reason": "FROZEN_LAYOUT_SELECTED",
                "selected_candidate_id": candidate["candidate_id"],
                "selected_layout_digest": candidate["layout_digest"],
                "selected_cost": list(cost[:-1]) + [cost[-1]],
                "selected_probe_digest": probe["integrity_sha256"],
                "selected_probe": probe,
            }
        )
        if probe["status"] == "SAT":
            result["ambient_witness"] = probe["ambient_witness"]
            result["witness_bits"] = probe["witness_bits"]
    return independent_selector_fixed_point(
        result,
        selector_certificate_limit(L, selector_certificate_cap),
    )


def verify(
    factors: list[dict[str, Any]],
    dimension: int,
    certificate: dict[str, Any],
) -> bool:
    try:
        if certificate.get("schema") != SCHEMA_C048:
            return False
        integrity = certificate.get("integrity_sha256")
        body = dict(certificate)
        body.pop("integrity_sha256", None)
        if integrity != digest(body):
            return False
        expected = reconstruct_selector(
            factors,
            dimension,
            requested_width_cap=int(certificate.get("requested_width_cap", 3)),
            discovery_cap=certificate.get("discovery_cap"),
            probe_work_cap=certificate.get("probe_work_cap"),
            probe_certificate_cap=certificate.get("probe_certificate_cap"),
            selector_certificate_cap=certificate.get("selector_certificate_cap"),
        )
        return expected == certificate
    except (KeyError, TypeError, ValueError, AssertionError):
        return False
