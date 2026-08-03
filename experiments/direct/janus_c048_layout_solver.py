#!/usr/bin/env python3
from __future__ import annotations
from typing import Any

from janus_c047_affine_trellis_core import *
from janus_c048_layout_core import *


def compile_order_probe(
    factors: list[dict[str, Any]],
    dimension: int,
    order_positions: list[int],
    constructor: str,
    *,
    requested_width_cap: int,
    work_cap: int | None = None,
    certificate_cap: int | None = None,
) -> dict[str, Any]:
    normalized = normalize_factors(factors, dimension)
    if sorted(order_positions) != list(range(len(normalized))):
        raise ValueError("invalid supplied order")
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
        widths = layout["cut_widths"]
        boundaries = [tuple(boundary) for boundary in layout["boundaries"]]
        meter.max_width = max(widths, default=0)
        for cut, width in enumerate(widths):
            if width > cap.width_limit:
                body = {
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
                body["producer_ledger"] = meter.snapshot()
                body["integrity_sha256"] = digest(body)
                return body

        reachable: dict[int, dict[str, Any]] = {0: {"prefix_basis": (), "prefix_values": 0, "parent": None}}
        layers: list[dict[str, Any]] = [
            {
                "cut": 0,
                "boundary_basis": list(boundaries[0]),
                "reachable_states": [0],
                "records": {"0": {"prefix_basis": [], "prefix_values": 0, "parent": None}},
            }
        ]
        for t, factor in enumerate(ordered, 1):
            previous_boundary = boundaries[t - 1]
            current_boundary = boundaries[t]
            normal_basis = normal_space(factor)
            next_reachable: dict[int, dict[str, Any]] = {}
            transitions: list[dict[str, Any]] = []
            for previous_state in sorted(reachable):
                previous_record = reachable[previous_state]
                for current_state in range(1 << len(current_boundary)):
                    meter.transition_tests += 1
                    meter.charge(
                        "transition_test",
                        max(1, len(previous_boundary) + len(current_boundary) + len(normal_basis)),
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
                        transitions.append({"from": previous_state, "to": current_state, "status": "BLOCKED"})
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
                    combined_basis, combined_values = combine_functionals(
                        tuple(previous_record["prefix_basis"]),
                        int(previous_record["prefix_values"]),
                        normal_basis,
                        int(local["factor_values"]),
                        dimension,
                    )
                    if restrict_functional(combined_basis, combined_values, current_boundary) != current_state:
                        raise AssertionError("combined prefix misses current state")
                    next_reachable[current_state] = {
                        "prefix_basis": combined_basis,
                        "prefix_values": combined_values,
                        "parent": {
                            "previous_state": previous_state,
                            "factor_id": factor["factor_id"],
                            "factor_values": local["factor_values"],
                            "separating_row": local["separating_row"],
                        },
                    }
            reachable = next_reachable
            meter.states_materialized += len(reachable)
            layers.append(
                {
                    "cut": t,
                    "factor_id": factor["factor_id"],
                    "boundary_basis": list(current_boundary),
                    "reachable_states": sorted(reachable),
                    "records": {
                        str(state): {
                            "prefix_basis": list(record["prefix_basis"]),
                            "prefix_values": record["prefix_values"],
                            "parent": record["parent"],
                        }
                        for state, record in sorted(reachable.items())
                    },
                    "transition_records": transitions,
                }
            )

        body: dict[str, Any] = {
            **base,
            "order_policy": constructor,
            "factor_order": layout["factor_order"],
            "order_positions": order_positions,
            "cut_widths": widths,
            "boundaries": [list(boundary) for boundary in boundaries],
            "layers": layers,
        }
        if 0 not in reachable:
            body.update(
                {
                    "status": "UNSAT",
                    "reason": "ROOT_FUNCTIONAL_SET_EMPTY",
                    "root_reachable_states": [],
                }
            )
        else:
            root = reachable[0]
            point = solve_point(tuple(root["prefix_basis"]), int(root["prefix_values"]), dimension)
            if point is None:
                raise AssertionError("root functional failed to lift")
            if any(point_in_factor(point, factor["equations"]) for factor in normalized):
                raise AssertionError("lifted point lies in forbidden factor")
            body.update(
                {
                    "status": "SAT",
                    "reason": "ROOT_FUNCTIONAL_EXISTS",
                    "root_reachable_states": [0],
                    "ambient_witness": str(point),
                    "witness_bits": [(point >> i) & 1 for i in range(dimension)],
                    "root_normal_basis": list(root["prefix_basis"]),
                    "root_functional_values": root["prefix_values"],
                }
            )
        return fixed_point_certificate(body, cap, meter)
    except OpenResult as err:
        body = {
            **base,
            "status": err.status,
            "reason": err.stage,
            "overflow_evidence": err.evidence,
            "producer_ledger": meter.snapshot(),
        }
        body["integrity_sha256"] = digest(body)
        return body


def selector_fixed_point(
    body: dict[str, Any],
    *,
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


def solve_with_layout_portfolio(
    factors: list[dict[str, Any]],
    dimension: int,
    *,
    requested_width_cap: int = 3,
    discovery_cap: int | None = None,
    probe_work_cap: int | None = None,
    probe_certificate_cap: int | None = None,
    selector_certificate_cap: int | None = None,
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
        body = {**base, **manifest_result}
        body["integrity_sha256"] = digest(body)
        return body

    manifest = manifest_result["manifest"]
    frozen_digest_before_probes = manifest["manifest_digest"]
    probes: list[dict[str, Any]] = []
    successful: list[tuple[tuple[Any, ...], dict[str, Any], dict[str, Any]]] = []
    for candidate in manifest["unique_candidates"]:
        probe = compile_order_probe(
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

    if manifest["manifest_digest"] != frozen_digest_before_probes:
        raise AssertionError("candidate manifest changed after probes")

    body: dict[str, Any] = {
        **base,
        "manifest": manifest,
        "manifest_digest_before_probes": frozen_digest_before_probes,
        "probes": probes,
        "probe_count": len(probes),
    }
    if not successful:
        body.update(
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
        body.update(
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
            body["ambient_witness"] = probe["ambient_witness"]
            body["witness_bits"] = probe["witness_bits"]
    return selector_fixed_point(
        body,
        certificate_limit=selector_certificate_limit(L, selector_certificate_cap),
    )
