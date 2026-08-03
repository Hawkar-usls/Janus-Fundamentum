#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from janus_c047_affine_trellis_core import (
    Capability as TrellisCapability,
    Meter as TrellisMeter,
    OpenResult as TrellisOpenResult,
    combine_functionals,
    digest,
    extend_avoiding,
    fixed_point_certificate as trellis_fixed_point_certificate,
    input_length,
    normalize_factors,
    point_in_factor,
    restrict_functional,
    solve_point,
    span,
    intersection,
)
from janus_c049_fpt_integration_core import *


def compile_order_probe(
    factors: list[dict[str, Any]],
    dimension: int,
    order_positions: list[int],
    *,
    requested_width_cap: int,
    work_cap: int | None,
    certificate_cap: int | None,
    order_policy: str,
) -> dict[str, Any]:
    normalized = normalize_factors(factors, dimension)
    if sorted(order_positions) != list(range(len(normalized))):
        raise ValueError("invalid order")
    L = input_length(normalized, dimension)
    cap = TrellisCapability(L, requested_width_cap, work_cap, certificate_cap)
    meter = TrellisMeter(cap)
    base = {
        "schema": "janus.c047.offset_aware_affine_functional_trellis.v1",
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
        meter.charge("verified_constructor_order", max(1, len(order_positions)))
        ordered = [normalized[index] for index in order_positions]
        spaces = [tuple(mask for mask, _ in factor["equations"]) for factor in normalized]
        layout = layout_data_from_spaces(spaces, order_positions, dimension)
        widths = layout["cut_widths"]
        boundaries = [tuple(basis) for basis in layout["cut_bases"]]
        meter.max_width = max(widths, default=0)
        for cut, width in enumerate(widths):
            if width > cap.width_limit:
                body = {
                    **base,
                    "status": "OPEN_CUT_WIDTH",
                    "reason": "VERIFIED_CONSTRUCTOR_LAYOUT_EXCEEDS_WIDTH_CAP",
                    "order_policy": order_policy,
                    "factor_order": [factor["factor_id"] for factor in ordered],
                    "order_positions": list(order_positions),
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
            normal_basis = tuple(mask for mask, _ in factor["equations"])
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
            "order_policy": order_policy,
            "factor_order": [factor["factor_id"] for factor in ordered],
            "order_positions": list(order_positions),
            "cut_widths": widths,
            "boundaries": [list(boundary) for boundary in boundaries],
            "layers": layers,
        }
        if 0 not in reachable:
            body.update({"status": "UNSAT", "reason": "ROOT_FUNCTIONAL_SET_EMPTY", "root_reachable_states": []})
        else:
            root = reachable[0]
            point = solve_point(tuple(root["prefix_basis"]), int(root["prefix_values"]), dimension)
            if point is None or any(point_in_factor(point, factor["equations"]) for factor in normalized):
                raise AssertionError("lifted point invalid")
            body.update(
                {
                    "status": "SAT",
                    "reason": "ROOT_FUNCTIONAL_EXISTS",
                    "root_reachable_states": [0],
                    "ambient_witness": str(point),
                    "witness_bits": [(point >> bit) & 1 for bit in range(dimension)],
                    "root_normal_basis": list(root["prefix_basis"]),
                    "root_functional_values": root["prefix_values"],
                }
            )
        return trellis_fixed_point_certificate(body, cap, meter)
    except TrellisOpenResult as error:
        body = {
            **base,
            "status": error.status,
            "reason": error.stage,
            "overflow_evidence": error.evidence,
            "producer_ledger": meter.snapshot(),
        }
        body["integrity_sha256"] = digest(body)
        return body


def solve_phase_a(
    factors: list[dict[str, Any]],
    dimension: int,
    *,
    k: int,
    constructor_transcript: dict[str, Any] | None = None,
    discovery_cap: int | None = None,
    work_cap: int | None = None,
    certificate_cap: int | None = None,
    trellis_work_cap: int | None = None,
    trellis_certificate_cap: int | None = None,
) -> dict[str, Any]:
    normalized = normalize_factors(factors, dimension)
    L = input_length(normalized, dimension)
    capability = IntegrationCapability(
        L,
        k,
        discovery_cap,
        work_cap,
        certificate_cap,
        trellis_work_cap,
        trellis_certificate_cap,
    )
    meter = IntegrationMeter(capability)
    base = {
        "schema": SCHEMA,
        "phase": "JKO_PREPROCESSING_AND_LAYOUT_REPLAY_CONTRACT",
        "implementation_status": "PUBLISHED_FPT_FULL_SET_ENGINE_NOT_YET_REIMPLEMENTED",
        "dimension": dimension,
        "input_factors": [
            {
                "factor_id": factor["factor_id"],
                "equations": [list(eq) for eq in factor["equations"]],
                "input_position": factor["input_position"],
            }
            for factor in normalized
        ],
        "capability": capability.manifest(),
        "p_vs_np": "OPEN",
    }
    try:
        preprocessing = jko_column_reduction_skeleton(normalized, dimension, capability.k, meter)
        obstruction = preprocessing["first_local_obstruction"]
        if obstruction is not None:
            body = {
                **base,
                "status": NO_LAYOUT_AT_CAP,
                "reason": "JKO_PROPOSITION_2_2_LOCAL_INTERSECTION_GT_2K",
                "preprocessing": preprocessing,
                "no_layout_certificate": obstruction,
                "constructor_terminal": "NO_LAYOUT_AT_CAP",
                "claim_scope": "LINEAR_LAYOUT_WIDTH_AT_MOST_K_DOES_NOT_EXIST",
            }
            return fixed_point_outer_certificate(body, capability, meter)

        spaces = [normal_space(factor) for factor in normalized]
        reduced_spaces = [tuple(space) for space in preprocessing["reduced_spaces"]]

        if constructor_transcript is None:
            order_positions = list(range(len(normalized)))
            meter.charge_discovery("phase_a_baseline_order", max(1, len(order_positions)))
            reduced_layout = layout_data_from_spaces(reduced_spaces, order_positions, dimension, meter)
            original_layout = layout_data_from_spaces(spaces, order_positions, dimension, meter)
            if reduced_layout["cut_widths"] != original_layout["cut_widths"]:
                raise AssertionError("JKO reduction failed cut-width preservation")
            if original_layout["maximum_width"] <= capability.k:
                transcript = make_found_layout_transcript(
                    order_positions,
                    original_layout["cut_widths"],
                    original_layout["cut_bases"],
                    constructor_id="PHASE_A_INPUT_ORDER_WARM_START",
                    discovery_claim=True,
                    constructor_trace={"charged_internal_warm_start": True},
                )
            else:
                body = {
                    **base,
                    "status": OPEN_FPT_ENGINE_PENDING,
                    "reason": "JKO_FULL_SET_ENGINE_PENDING_AFTER_SOUND_PREPROCESSING",
                    "preprocessing": preprocessing,
                    "baseline_layout": original_layout,
                    "constructor_terminal": "OPEN",
                    "surviving_gate": "REIMPLEMENT_B_TRAJECTORY_FULL_SET_ENGINE",
                }
                return fixed_point_outer_certificate(body, capability, meter)
        else:
            transcript = constructor_transcript
            meter.charge_discovery("constructor_transcript_validation", max(1, len(canonical_json(transcript))))
            if not validate_transcript_digest(transcript):
                body = {
                    **base,
                    "status": OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT,
                    "reason": "TRANSCRIPT_DIGEST_OR_SCHEMA_INVALID",
                    "preprocessing": preprocessing,
                    "constructor_transcript": transcript,
                    "constructor_terminal": "OPEN",
                }
                return fixed_point_outer_certificate(body, capability, meter)
            terminal = transcript.get("terminal")
            if terminal == "NO_LAYOUT_AT_CAP":
                body = {
                    **base,
                    "status": OPEN_UNVERIFIED_NO_LAYOUT_TRANSCRIPT,
                    "reason": "BARE_NO_LAYOUT_REQUIRES_FULL_SET_OR_EQUIVALENT_REPLAY",
                    "preprocessing": preprocessing,
                    "constructor_transcript": transcript,
                    "constructor_terminal": "OPEN",
                }
                return fixed_point_outer_certificate(body, capability, meter)
            if terminal != "FOUND_LAYOUT":
                body = {
                    **base,
                    "status": OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT,
                    "reason": "UNSUPPORTED_CONSTRUCTOR_TERMINAL",
                    "preprocessing": preprocessing,
                    "constructor_transcript": transcript,
                    "constructor_terminal": "OPEN",
                }
                return fixed_point_outer_certificate(body, capability, meter)

        order_positions = [int(x) for x in transcript["order_positions"]]
        claimed_widths = [int(x) for x in transcript["cut_widths"]]
        claimed_bases = [[int(x) for x in basis] for basis in transcript["cut_bases"]]
        original_layout = layout_data_from_spaces(spaces, order_positions, dimension, meter)
        reduced_layout = layout_data_from_spaces(reduced_spaces, order_positions, dimension, meter)
        if original_layout["cut_widths"] != reduced_layout["cut_widths"]:
            raise AssertionError("reduced and original layout widths differ")
        if claimed_widths != original_layout["cut_widths"] or claimed_bases != original_layout["cut_bases"]:
            body = {
                **base,
                "status": OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT,
                "reason": "CLAIMED_LAYOUT_OR_CUT_BASES_MISMATCH",
                "preprocessing": preprocessing,
                "constructor_transcript": transcript,
                "recomputed_layout": original_layout,
                "constructor_terminal": "OPEN",
            }
            return fixed_point_outer_certificate(body, capability, meter)
        if original_layout["maximum_width"] > capability.k:
            body = {
                **base,
                "status": OPEN_INVALID_CONSTRUCTOR_TRANSCRIPT,
                "reason": "FOUND_LAYOUT_EXCEEDS_REQUESTED_K",
                "preprocessing": preprocessing,
                "constructor_transcript": transcript,
                "recomputed_layout": original_layout,
                "constructor_terminal": "OPEN",
            }
            return fixed_point_outer_certificate(body, capability, meter)

        trellis = compile_order_probe(
            factors,
            dimension,
            order_positions,
            requested_width_cap=capability.k,
            work_cap=capability.trellis_work_cap,
            certificate_cap=capability.trellis_certificate_cap,
            order_policy=str(transcript["constructor_id"]),
        )
        meter.charge_work("nested_trellis_probe", max(1, int(trellis.get("producer_ledger", {}).get("total_work_units", 1))))
        if trellis.get("status") not in {"SAT", "UNSAT"}:
            body = {
                **base,
                "status": trellis.get("status", OPEN_WORK_BUDGET),
                "reason": "NESTED_C047_DID_NOT_CLOSE",
                "preprocessing": preprocessing,
                "constructor_transcript": transcript,
                "verified_layout": original_layout,
                "trellis_result": trellis,
                "constructor_terminal": "FOUND_LAYOUT",
            }
            return fixed_point_outer_certificate(body, capability, meter)

        body = {
            **base,
            "status": trellis["status"],
            "reason": "FOUND_LAYOUT_VERIFIED_AND_C047_COMPILED",
            "preprocessing": preprocessing,
            "constructor_transcript": transcript,
            "verified_layout": original_layout,
            "constructor_terminal": "FOUND_LAYOUT",
            "discovery_claim": bool(transcript.get("discovery_claim", False)),
            "trellis_result": trellis,
            "ambient_witness": trellis.get("ambient_witness"),
            "claim_boundary": (
                "Phase A proves preprocessing, a local NO_LAYOUT certificate, and exact FOUND_LAYOUT-to-C047 composition. "
                "It does not yet reimplement the published B-trajectory/full-set FPT constructor."
            ),
        }
        return fixed_point_outer_certificate(body, capability, meter)
    except IntegrationOpen as error:
        body = {
            **base,
            "status": error.status,
            "reason": error.stage,
            "overflow_evidence": error.evidence,
            "integration_ledger": meter.snapshot(),
        }
        body["integrity_sha256"] = sha256_obj(body)
        return body
