from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from janus_c047_affine_trellis_core import affine_rref, linear_rref
from janus_c049_fpt_integration_core import IntegrationCapability, layout_data_from_spaces, make_found_layout_transcript
from janus_c049_fpt_integration_solver import solve_phase_a
from janus_c049_fpt_integration_verifier import verify as verify_phase_a

SCHEMA = "janus.c049_1.b5_4.corrected_discovery_c047_rebound_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5_4.corrected_discovery_c047_rebound_spec.v1"
B5_1_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
B5_2B_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"
AFFINE_SCHEMA = "janus.c049_1.c047_affine_equations.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path | None) -> Any:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def canonical_equation_profile(offset: Any, dimension: int) -> tuple[str, tuple[tuple[int, int], ...] | None, str | None]:
    if not isinstance(offset, dict) or offset.get("schema") != AFFINE_SCHEMA:
        return "OPEN_AFFINE_REBOUND_BINDING", None, "MISSING_CANONICAL_AFFINE_PROFILE"
    equations = offset.get("equations")
    if not isinstance(equations, list) or not equations:
        return "OPEN_AFFINE_REBOUND_BINDING", None, "EMPTY_OR_NONLIST_EQUATIONS"
    parsed: list[tuple[int, int]] = []
    limit = 1 << dimension
    for row in equations:
        if not isinstance(row, list) or len(row) != 2:
            return "OPEN_AFFINE_REBOUND_BINDING", None, "BAD_EQUATION_SHAPE"
        mask, beta = row
        if not isinstance(mask, int) or not isinstance(beta, int) or not (0 <= mask < limit) or beta not in (0, 1):
            return "OPEN_AFFINE_REBOUND_BINDING", None, "BAD_EQUATION_VALUE"
        parsed.append((mask, beta))
    reduced = affine_rref(parsed, dimension)
    if reduced is None:
        return "OPEN_NONBIJECTIVE_AFFINE_NORMALIZATION", None, "INCONSISTENT_AFFINE_FACTOR_WOULD_BE_DROPPED"
    return "BOUND", reduced, None


def semantic_space(rows: list[int] | tuple[int, ...], dimension: int) -> tuple[int, ...]:
    return linear_rref([int(x) for x in rows], dimension)


def build_adapter(catalog: list[dict], dimension: int) -> tuple[str, list[dict], list[dict], str | None]:
    phase_a_factors: list[dict] = []
    bijection: list[dict] = []
    seen_ids: set[str] = set()
    for position, factor in enumerate(catalog):
        fid_key = cb(factor["id"]).decode("utf-8")
        if fid_key in seen_ids:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "DUPLICATE_B5_FACTOR_ID"
        seen_ids.add(fid_key)
        status, reduced, reason = canonical_equation_profile(factor.get("affine_offset"), dimension)
        if status != "BOUND" or reduced is None:
            return status, [], [], reason
        normal = semantic_space(factor["normal_space"], dimension)
        affine_normal = linear_rref([mask for mask, _ in reduced], dimension)
        if normal != affine_normal:
            return "OPEN_AFFINE_REBOUND_BINDING", [], [], "AFFINE_NORMAL_SPAN_MISMATCH"
        normalized_equations = [[int(mask), int(beta)] for mask, beta in reduced]
        phase_a_factors.append({"factor_id": position, "equations": normalized_equations})
        bijection.append(
            {
                "b5_factor_id": factor["id"],
                "phase_a_numeric_factor_id": position,
                "phase_a_input_position": position,
                "b5_normal_space_serialized": factor["normal_space"],
                "phase_a_normal_space_rref": list(affine_normal),
                "normal_space_rref": list(normal),
                "normal_space_semantic_digest": dg(list(normal)),
                "semantic_normal_space_equal": True,
                "raw_list_byte_equal": factor["normal_space"] == list(affine_normal),
                "affine_offset_identity_digest": dg(factor.get("affine_offset")),
                "normalized_equations": normalized_equations,
                "normalized_equations_digest": dg(normalized_equations),
            }
        )
    return "BOUND", phase_a_factors, bijection, None


def compare_b5_phase_a_cuts(b52_payload: dict, phase_layout: dict, dimension: int) -> list[dict]:
    b5cuts = b52_payload["cut_certificates"]
    if len(b5cuts) != len(phase_layout["cut_widths"]):
        raise AssertionError("cut count mismatch")
    out = []
    for i, b5cut in enumerate(b5cuts):
        phase_basis = semantic_space(phase_layout["cut_bases"][i], dimension)
        b5_basis = semantic_space(b5cut["boundary_rref"], dimension)
        if int(b5cut["width"]) != int(phase_layout["cut_widths"][i]) or phase_basis != b5_basis:
            raise AssertionError("B5/Phase-A cut mismatch")
        out.append(
            {
                "cut": i,
                "width": int(phase_layout["cut_widths"][i]),
                "b5_boundary_semantic_digest": dg(list(b5_basis)),
                "phase_a_boundary_semantic_digest": dg(list(phase_basis)),
                "semantic_boundary_equal": True,
            }
        )
    return out


def capability_from_args(dimension: int, factors: list[dict], k: int, caps: dict[str, int | None]) -> IntegrationCapability:
    from janus_c047_affine_trellis_core import input_length
    length = input_length(factors, dimension)
    return IntegrationCapability(
        length,
        k,
        discovery_cap=caps.get("discovery_cap"),
        work_cap=caps.get("work_cap"),
        certificate_cap=caps.get("certificate_cap"),
        trellis_work_cap=caps.get("trellis_work_cap"),
        trellis_certificate_cap=caps.get("trellis_certificate_cap"),
    )


def build(spec: dict, raw: dict, b5_1: dict, carrier: dict | None, b52: dict | None, caps: dict[str, int | None]) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.4 spec")
    if b5_1.get("schema") != B5_1_SCHEMA or b5_1.get("semantic_digest_scope") != "proof_payload" or b5_1.get("semantic_digest") != dg(b5_1["proof_payload"]):
        raise AssertionError("B5.1 artifact")
    q = b5_1["proof_payload"]
    dimension, k = int(q["ambient_dim"]), int(q["k"])
    if int(raw["ambient_dim"]) != dimension or int(raw["k"]) != k:
        raise AssertionError("input parameter mismatch")

    base: dict[str, Any] = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "subject": {
            "b5_1_semantic_digest": b5_1["semantic_digest"],
            "b5_2a_carrier_semantic_digest": None if carrier is None else carrier.get("semantic_digest"),
            "b5_2b_semantic_digest": None if b52 is None else b52.get("semantic_digest"),
            "b5_1_capability_status": q["capability_status"],
            "root_entry_count_if_closed": q.get("root_entry_count_if_closed"),
        },
        "ambient_dim": dimension,
        "k": k,
        "canonical_factor_catalog": q["canonical_factor_catalog"],
        "phase_a_capability_request": {key: caps.get(key) for key in sorted(caps)},
        "authority_bindings": {
            "b5_2b_proof_head": spec["authority_inputs"]["b5_2b_positive_terminal_admission"]["proof_head"],
            "b5_2b_review_id": spec["authority_inputs"]["b5_2b_positive_terminal_admission"]["review_id"],
            "b5_2b_admission_semantic_digest": spec["authority_inputs"]["b5_2b_positive_terminal_admission"]["receipt_semantic_digest"],
            "b5_3_proof_head": spec["authority_inputs"]["b5_3_negative_terminal_admission"]["proof_head"],
            "b5_3_review_id": spec["authority_inputs"]["b5_3_negative_terminal_admission"]["review_id"],
            "b5_3_admission_semantic_digest": spec["authority_inputs"]["b5_3_negative_terminal_admission"]["receipt_semantic_digest"],
            "historical_phase_a_subject": spec["authority_inputs"]["historical_phase_a"]["proof_subject"],
        },
        "authority_policy": {
            "b5_2b_positive_terminal_required_for_found_layout_rebound": True,
            "b5_3_negative_terminal_is_branch_separation_only": True,
            "b5_3_no_layout_used_as_c047_unsat_premise": False,
            "historical_phase_a_c047_code_modified": False,
        },
    }

    if q["capability_status"] == "OPEN_RUNTIME_CAPABILITY":
        base.update({
            "rebound_status": "NOT_APPLICABLE_OPEN_RUNTIME",
            "affine_binding_status": "NOT_ATTEMPTED",
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED",
        })
        return wrap(spec, base)

    if q["capability_status"] != "CLOSED_COMPLETE_TRACE":
        raise AssertionError("unknown B5.1 capability status")
    if b52 is None or carrier is None:
        raise AssertionError("CLOSED B5.4 subject requires B5.2A/B5.2B artifacts")
    if b52.get("schema") != B5_2B_SCHEMA or b52.get("semantic_digest_scope") != "proof_payload" or b52.get("semantic_digest") != dg(b52["proof_payload"]):
        raise AssertionError("B5.2B artifact")
    p52 = b52["proof_payload"]
    if p52.get("b5_1_semantic_digest") != b5_1["semantic_digest"] or p52.get("carrier_semantic_digest") != carrier.get("semantic_digest"):
        raise AssertionError("B5.2B subject binding")
    if p52.get("canonical_factor_catalog") != q["canonical_factor_catalog"]:
        raise AssertionError("B5.2B/B5.1 factor identity")

    if p52.get("reconstruction_status") == "NOT_APPLICABLE_EMPTY_ROOT":
        base.update({
            "rebound_status": "NOT_APPLICABLE_NO_FOUND_LAYOUT",
            "affine_binding_status": "NOT_ATTEMPTED",
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED_DEFER_TO_B5_3",
        })
        return wrap(spec, base)
    if p52.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW" or p52.get("candidate_found_layout") is not True:
        raise AssertionError("unexpected B5.2B branch")

    adapter_status, phase_a_factors, bijection, adapter_reason = build_adapter(q["canonical_factor_catalog"], dimension)
    if adapter_status != "BOUND":
        base.update({
            "rebound_status": adapter_status,
            "affine_binding_status": adapter_status,
            "affine_binding_open_reason": adapter_reason,
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED",
        })
        return wrap(spec, base)

    by_id = {cb(rec["b5_factor_id"]).decode("utf-8"): rec for rec in bijection}
    order_ids = p52["factor_order_ids"]
    order_positions: list[int] = []
    for fid in order_ids:
        key = cb(fid).decode("utf-8")
        if key not in by_id:
            raise AssertionError("B5.2B order references unmapped factor")
        order_positions.append(int(by_id[key]["phase_a_input_position"]))
    if sorted(order_positions) != list(range(len(phase_a_factors))):
        raise AssertionError("rebound order is not Phase-A permutation")

    spaces = [tuple(mask for mask, _ in factor["equations"]) for factor in phase_a_factors]
    phase_layout = layout_data_from_spaces(spaces, order_positions, dimension)
    if int(phase_layout["maximum_width"]) != int(p52["maximum_cut_width"]):
        raise AssertionError("maximum width mismatch")
    cut_bridge = compare_b5_phase_a_cuts(p52, phase_layout, dimension)
    transcript = make_found_layout_transcript(
        order_positions,
        phase_layout["cut_widths"],
        phase_layout["cut_bases"],
        constructor_id="B5_2B_CORRECTED_GENERIC_DISCOVERY_REBOUND",
        discovery_claim=True,
        constructor_trace={
            "b5_2b_semantic_digest": b52["semantic_digest"],
            "b5_factor_order_ids": order_ids,
            "factor_bijection_digest": dg(bijection),
            "cut_bridge_digest": dg(cut_bridge),
            "affine_rebound_profile": AFFINE_SCHEMA,
        },
    )
    capability = capability_from_args(dimension, phase_a_factors, k, caps)
    certificate = solve_phase_a(phase_a_factors, dimension, capability, transcript)
    verify_phase_a(phase_a_factors, dimension, certificate)

    base.update({
        "rebound_status": "PHASE_A_C047_REPLAY_COMPLETED" if certificate["status"] in ("SAT", "UNSAT") else "PHASE_A_C047_REPLAY_OPEN",
        "affine_binding_status": "BOUND",
        "affine_binding_open_reason": None,
        "phase_a_factor_bijection": bijection,
        "phase_a_factor_bijection_digest": dg(bijection),
        "phase_a_factors": phase_a_factors,
        "phase_a_factor_catalog_digest": dg(phase_a_factors),
        "phase_a_order_positions": order_positions,
        "phase_a_layout_recomputation": phase_layout,
        "b5_to_phase_a_cut_bridge": cut_bridge,
        "phase_a_transcript": transcript,
        "phase_a_certificate": certificate,
        "historical_phase_a_verifier_pass": True,
        "c047_result": certificate["status"],
        "c047_reason": certificate.get("reason"),
    })
    return wrap(spec, base)


def wrap(spec: dict, payload: dict) -> dict:
    payload["strict_boundary"] = spec["strict_boundary"]
    payload["scope_ceiling"] = {
        "c047_result_admitted": False,
        "affine_instance_sat_or_unsat_admitted": False,
        "all_input_termination": "NOT_ESTABLISHED",
        "polynomial_runtime": "NOT_ESTABLISHED",
        "b5_complete": False,
        "arbitrary_input_global_engine_theorem": False,
        "p_vs_np": "OPEN",
        "formal_admission": "BLOCKED_PENDING_REVIEW",
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    artifact["semantic_digest"] = dg(payload)
    return artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--carrier", type=Path)
    parser.add_argument("--b5-2b-artifact", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--discovery-cap", type=int)
    parser.add_argument("--work-cap", type=int)
    parser.add_argument("--certificate-cap", type=int)
    parser.add_argument("--trellis-work-cap", type=int)
    parser.add_argument("--trellis-certificate-cap", type=int)
    args = parser.parse_args()
    caps = {
        "discovery_cap": args.discovery_cap,
        "work_cap": args.work_cap,
        "certificate_cap": args.certificate_cap,
        "trellis_work_cap": args.trellis_work_cap,
        "trellis_certificate_cap": args.trellis_certificate_cap,
    }
    artifact = build(load(args.spec), load(args.input), load(args.b5_1_artifact), load(args.carrier), load(args.b5_2b_artifact), caps)
    save(artifact, args.output)
    p = artifact["proof_payload"]
    print("JANUS_B5_4_CORRECTED_DISCOVERY_C047_REBOUND = PASS")
    print("REBOUND_STATUS =", p["rebound_status"])
    print("AFFINE_BINDING_STATUS =", p["affine_binding_status"])
    print("C047_RESULT =", p["c047_result"])
    print("HISTORICAL_PHASE_A_VERIFIER_PASS =", str(p["historical_phase_a_verifier_pass"]).upper())
    print("B5_3_NO_LAYOUT_USED_AS_C047_UNSAT_PREMISE = FALSE")
    print("AFFINE_INSTANCE_SAT_OR_UNSAT_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
