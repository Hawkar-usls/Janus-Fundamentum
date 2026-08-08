from __future__ import annotations

from typing import Any

import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier as base

load = base.load
dg = base.dg
cb = base.cb

SCHEMA = base.SCHEMA


def fail_fast_candidate_consistency(
    candidate: dict,
    spec: dict,
    raw_original: dict,
    preprocessing: dict,
    reduced_raw: dict | None,
    b51: dict | None,
    carrier: dict | None,
    b52: dict | None,
    prep_spec: dict,
    b51_spec: dict,
    b52a_spec: dict,
    b52b_spec: dict,
    caps: dict[str, int | None],
) -> None:
    """Reject candidate-local contradictions before expensive upstream replay.

    This is rejection-only hardening. Passing this preflight never admits a
    candidate: base.verify(...) still performs the full independent
    preprocessing/B5.1/B5.2A/B5.2B/original-cut/historical-Phase-A replay.
    """
    if candidate.get("schema") != SCHEMA:
        raise AssertionError("v1.2 fail-fast candidate schema")
    if candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("v1.2 fail-fast digest scope")
    p = candidate.get("proof_payload")
    if not isinstance(p, dict) or candidate.get("semantic_digest") != dg(p):
        raise AssertionError("v1.2 fail-fast candidate digest")
    if not isinstance(spec, dict) or p.get("strict_boundary") != spec.get("strict_boundary"):
        raise AssertionError("v1.2 fail-fast strict boundary")

    expected_policy = {
        "reduced_geometry_is_discovery_only": True,
        "original_geometry_required_for_final_width_and_affine_rebound": True,
        "direct_b5_4_on_reduced_catalog": False,
        "strict_prefix_c047": False,
        "b5_3_no_layout_used_as_c047_unsat_premise": False,
        "historical_phase_a_c047_code_modified": False,
    }
    if p.get("authority_policy") != expected_policy:
        raise AssertionError("v1.2 fail-fast authority policy")
    if p.get("phase_a_capability_request") != {key: caps.get(key) for key in sorted(caps)}:
        raise AssertionError("v1.2 fail-fast capability request")

    if not isinstance(preprocessing, dict):
        raise AssertionError("v1.2 fail-fast preprocessing object")
    if p.get("preprocessing_semantic_digest") != preprocessing.get("semantic_digest"):
        raise AssertionError("v1.2 fail-fast preprocessing subject digest")
    pre = preprocessing.get("proof_payload")
    if not isinstance(pre, dict):
        raise AssertionError("v1.2 fail-fast preprocessing payload")
    branch = pre.get("preprocessing_branch")
    if p.get("preprocessing_branch") != branch:
        raise AssertionError("v1.2 fail-fast preprocessing branch")

    if branch not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        return
    if b52 is None or not isinstance(b52, dict):
        return
    p52 = b52.get("proof_payload")
    if not isinstance(p52, dict):
        return
    if b51 is None or not isinstance(b51, dict):
        return
    q51 = b51.get("proof_payload")
    if not isinstance(q51, dict) or q51.get("capability_status") != "CLOSED_COMPLETE_TRACE":
        return
    if p52.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW" or p52.get("candidate_found_layout") is not True:
        return

    if p.get("reduced_b5_2b_semantic_digest") != b52.get("semantic_digest"):
        raise AssertionError("v1.2 fail-fast reduced B5.2B subject digest")

    order_ids = [str(x) for x in p52.get("factor_order_ids", [])]
    if p.get("factor_order_ids") != order_ids:
        raise AssertionError("v1.2 fail-fast factor order")
    catalog = base.original_catalog(pre)
    ids = [x["id"] for x in catalog]
    if len(order_ids) != len(ids) or len(set(order_ids)) != len(order_ids) or sorted(order_ids) != sorted(ids):
        raise AssertionError("v1.2 fail-fast full occurrence permutation")
    by_id = {x["id"]: i for i, x in enumerate(catalog)}
    positions = [by_id[x] for x in order_ids]

    d = int(pre["ambient_dim"])
    layout = base.layout_data_from_spaces([tuple(x["normal_space"]) for x in catalog], positions, d)
    if p.get("original_layout_replay") != layout or p.get("original_layout_semantic_digest") != dg(layout):
        raise AssertionError("v1.2 fail-fast original layout replay")
    expected_records = [
        {
            "position": j,
            "factor_id": fid,
            "normal_space": catalog[by_id[fid]]["normal_space"],
            "affine_offset": catalog[by_id[fid]]["affine_offset"],
        }
        for j, fid in enumerate(order_ids)
    ]
    if p.get("original_layout_records") != expected_records:
        raise AssertionError("v1.2 fail-fast original layout records")

    bridge = base.verify_reduced_original_cuts(p52, layout, d)
    if p.get("reduced_to_original_cut_bridge") != bridge or p.get("reduced_to_original_cut_bridge_digest") != dg(bridge):
        raise AssertionError("v1.2 fail-fast reduced/original cut bridge")

    status, phase_factors, mapping, reason = base.affine_adapter(catalog, d)
    if status != "BOUND":
        if (
            p.get("lift_status") != status
            or p.get("affine_binding_status") != status
            or p.get("affine_binding_open_reason") != reason
            or p.get("c047_result") != "NOT_ESTABLISHED"
        ):
            raise AssertionError("v1.2 fail-fast affine OPEN branch")
        return

    phase_by_id = {str(x["b5_factor_id"]): x for x in mapping}
    phase_positions = [int(phase_by_id[fid]["phase_a_input_position"]) for fid in order_ids]
    if phase_positions != positions:
        raise AssertionError("v1.2 fail-fast numeric occurrence order")
    phase_layout = base.layout_data_from_spaces(
        [tuple(mask for mask, _ in f["equations"]) for f in phase_factors],
        phase_positions,
        d,
    )
    phase_bridge = []
    for i, (ow, pw, ob, pb) in enumerate(
        zip(layout["cut_widths"], phase_layout["cut_widths"], layout["cut_bases"], phase_layout["cut_bases"])
    ):
        os = base.semantic_space(ob, d)
        ps = base.semantic_space(pb, d)
        if int(ow) != int(pw) or os != ps:
            raise AssertionError("v1.2 fail-fast original/Phase-A cut")
        phase_bridge.append(
            {
                "cut": i,
                "width": int(ow),
                "original_boundary_semantic_digest": dg(list(os)),
                "phase_a_boundary_semantic_digest": dg(list(ps)),
                "semantic_boundary_equal": True,
            }
        )
    transcript = base.make_found_layout_transcript(
        phase_positions,
        phase_layout["cut_widths"],
        phase_layout["cut_bases"],
        constructor_id="B5_FULL_INPUT_ORIGINAL_ORDER_LIFT",
        discovery_claim=True,
        constructor_trace={
            "preprocessing_semantic_digest": preprocessing["semantic_digest"],
            "reduced_b5_2b_semantic_digest": b52["semantic_digest"],
            "factor_order_ids": order_ids,
            "original_layout_semantic_digest": dg(layout),
            "reduced_to_original_cut_bridge_digest": dg(bridge),
            "original_to_phase_a_cut_bridge_digest": dg(phase_bridge),
        },
    )

    if p.get("phase_a_factor_bijection") != mapping or p.get("phase_a_factor_bijection_digest") != dg(mapping):
        raise AssertionError("v1.2 fail-fast Phase-A mapping")
    if p.get("phase_a_factors") != phase_factors or p.get("phase_a_factor_catalog_digest") != dg(phase_factors):
        raise AssertionError("v1.2 fail-fast Phase-A factors")
    if p.get("phase_a_order_positions") != phase_positions or p.get("phase_a_layout_recomputation") != phase_layout:
        raise AssertionError("v1.2 fail-fast Phase-A layout")
    if p.get("original_to_phase_a_cut_bridge") != phase_bridge or p.get("phase_a_transcript") != transcript:
        raise AssertionError("v1.2 fail-fast Phase-A bridge/transcript")

    certificate = p.get("phase_a_certificate")
    if not isinstance(certificate, dict):
        raise AssertionError("v1.2 fail-fast historical certificate")
    result = str(certificate.get("status"))
    if p.get("c047_result") != result:
        raise AssertionError("v1.2 fail-fast C047 result/certificate disagreement")
    expected_status = (
        "ORIGINAL_ORDER_LIFT_AND_PHASE_A_C047_COMPLETED"
        if result in {"SAT", "UNSAT"}
        else "ORIGINAL_ORDER_LIFT_PHASE_A_C047_OPEN"
    )
    if p.get("lift_status") != expected_status:
        raise AssertionError("v1.2 fail-fast terminal status")
    if p.get("affine_binding_status") != "BOUND" or p.get("historical_phase_a_verifier_pass") is not True:
        raise AssertionError("v1.2 fail-fast historical verifier flag")


def verify(
    candidate: dict,
    spec: dict,
    raw_original: dict,
    preprocessing: dict,
    reduced_raw: dict | None,
    b51: dict | None,
    carrier: dict | None,
    b52: dict | None,
    prep_spec: dict,
    b51_spec: dict,
    b52a_spec: dict,
    b52b_spec: dict,
    caps: dict[str, int | None],
) -> dict:
    fail_fast_candidate_consistency(
        candidate,
        spec,
        raw_original,
        preprocessing,
        reduced_raw,
        b51,
        carrier,
        b52,
        prep_spec,
        b51_spec,
        b52a_spec,
        b52b_spec,
        caps,
    )
    return base.verify(
        candidate,
        spec,
        raw_original,
        preprocessing,
        reduced_raw,
        b51,
        carrier,
        b52,
        prep_spec,
        b51_spec,
        b52a_spec,
        b52b_spec,
        caps,
    )
