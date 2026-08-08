from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from janus_c047_affine_trellis_core import normalize_factors
from janus_c049_fpt_integration_core import (
    layout_data_from_spaces,
    make_found_layout_transcript,
    normal_space,
    validate_transcript_digest,
)
from janus_c049_fpt_integration_solver import solve_phase_a
from janus_c049_fpt_integration_verifier import verify_certificate as verify_phase_a_certificate

SCHEMA = "janus.c049_1.b5_4.corrected_discovery_phase_a_c047_handoff_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5_4.corrected_discovery_phase_a_c047_handoff_spec.v1"
B5_2B_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def affine_fingerprint(factor: dict) -> dict:
    return {"canonical_affine_equations": [list(eq) for eq in factor["equations"]]}


def verify_authority(spec: dict, b52_receipt: dict, b53_receipt: dict) -> dict:
    a = spec["authority_inputs"]
    e52 = a["b5_2b_positive_terminal"]
    if b52_receipt.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B admission receipt schema")
    if b52_receipt.get("semantic_digest") != e52["receipt_semantic_digest"] or dg(b52_receipt["audit_payload"]) != e52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B admission receipt semantic digest")
    p52 = b52_receipt["audit_payload"]
    if p52.get("admission_review_id") != e52["review_id"] or p52.get("exact_proof_head") != e52["proof_head"]:
        raise AssertionError("B5.2B review/proof authority")
    if p52["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B positive terminal statement")

    e53 = a["b5_3_negative_terminal_separation"]
    if b53_receipt.get("schema") != "janus.c049_1.b5_3.generic_empty_root_terminal_composition_admission_receipt.v1_1":
        raise AssertionError("B5.3 admission receipt schema")
    if b53_receipt.get("semantic_digest") != e53["receipt_semantic_digest"] or dg(b53_receipt["audit_payload"]) != e53["receipt_semantic_digest"]:
        raise AssertionError("B5.3 admission receipt semantic digest")
    p53 = b53_receipt["audit_payload"]
    if p53.get("admission_review_id") != e53["review_id"] or p53.get("exact_proof_head") != e53["proof_head"]:
        raise AssertionError("B5.3 review/proof authority")
    if p53["semantic_conclusion"].get("generic_no_layout_at_cap") != "TRUE_WHEN_B5_1_VERIFIED_CLOSED_ROOT_EMPTY_AND_B5_3_AUTHORITY_BRIDGE_PASSES":
        raise AssertionError("B5.3 negative terminal statement")

    return {
        "b5_2b_positive_terminal_authority": True,
        "b5_3_negative_branch_separation_authority": True,
        "b5_3_no_layout_compiled_as_phase_a_transcript": False,
        "phase_a_existing_verified_layout_to_c047_surface_bound": True,
    }


def canonical_phase_catalog(phase_input: dict) -> list[dict]:
    dimension = int(phase_input["dimension"])
    normalized = normalize_factors(phase_input["factors"], dimension)
    ids = [int(f["factor_id"]) for f in normalized]
    if len(ids) != len(set(ids)):
        raise AssertionError("Phase-A factor_id must be unique for B5.4")
    return [
        {
            "normalized_position": pos,
            "factor_id": int(factor["factor_id"]),
            "input_position": int(factor["input_position"]),
            "normal_space": list(normal_space(factor)),
            "affine_fingerprint": affine_fingerprint(factor),
            "equations": [list(eq) for eq in factor["equations"]],
        }
        for pos, factor in enumerate(normalized)
    ]


def verify_b5_phase_identity(b5_input: dict, b52: dict, phase_catalog: list[dict], dimension: int, k: int) -> dict:
    if int(b5_input["ambient_dim"]) != dimension or int(b5_input["k"]) != k:
        raise AssertionError("B5/Phase-A dimension or k mismatch")
    if b52.get("schema") != B5_2B_SCHEMA or b52.get("semantic_digest_scope") != "proof_payload" or b52.get("semantic_digest") != dg(b52["proof_payload"]):
        raise AssertionError("B5.2B candidate schema/digest")
    p = b52["proof_payload"]
    if p.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW":
        raise AssertionError("B5.4 requires a nonempty B5.2B layout subject")
    if p.get("candidate_found_layout") is not True or p.get("factor_order_ids") is None:
        raise AssertionError("B5.2B layout candidate missing")
    if int(p["ambient_dim"]) != dimension or int(p["k"]) != k:
        raise AssertionError("B5.2B/Phase-A parameter mismatch")

    by_phase = {item["factor_id"]: item for item in phase_catalog}
    b5_raw = b5_input["factors"]
    by_b5 = {}
    for item in b5_raw:
        fid = int(item["id"])
        if fid in by_b5:
            raise AssertionError("duplicate B5 factor id")
        by_b5[fid] = item
    if set(by_b5) != set(by_phase):
        raise AssertionError("B5 and Phase-A indexed factor-id domains differ")

    layout_records = p["layout_records"]
    if len(layout_records) != len(phase_catalog):
        raise AssertionError("B5.2B layout record count")
    seen = set()
    map_records = []
    for position, record in enumerate(layout_records):
        fid = int(record["factor_id"])
        if fid in seen or fid not in by_phase:
            raise AssertionError("B5.2B factor order is not an exact known-ID permutation")
        seen.add(fid)
        phase = by_phase[fid]
        b5_factor = by_b5[fid]
        expected_fp = phase["affine_fingerprint"]
        if b5_factor.get("affine_offset") != expected_fp:
            raise AssertionError("B5 input affine fingerprint differs from normalized Phase-A affine factor")
        if record.get("affine_offset") != expected_fp:
            raise AssertionError("B5.2B layout affine fingerprint differs from normalized Phase-A factor")
        b5_space = list(normal_space({"equations": [(int(mask), 0) for mask in b5_factor["normal_space"]]}))
        if b5_space != phase["normal_space"]:
            raise AssertionError("B5 input normal space differs from Phase-A normalized normal space")
        if record.get("normal_space") != phase["normal_space"]:
            raise AssertionError("B5.2B layout normal space differs from Phase-A normalized normal space")
        map_records.append(
            {
                "layout_position": position,
                "factor_id": fid,
                "phase_a_normalized_position": phase["normalized_position"],
                "phase_a_input_position": phase["input_position"],
                "normal_space": phase["normal_space"],
                "affine_fingerprint": expected_fp,
            }
        )
    if seen != set(by_phase):
        raise AssertionError("B5.2B layout omits factor IDs")
    return {
        "map_records": map_records,
        "order_positions": [record["phase_a_normalized_position"] for record in map_records],
        "factor_order_ids": [record["factor_id"] for record in map_records],
        "affine_identity_digest": dg([
            [record["factor_id"], record["normal_space"], record["affine_fingerprint"]]
            for record in map_records
        ]),
    }


def build(spec: dict, b5_input: dict, phase_input: dict, b52: dict, b52_receipt: dict, b53_receipt: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.4 spec")
    authority = verify_authority(spec, b52_receipt, b53_receipt)
    dimension = int(phase_input["dimension"])
    k = int(phase_input["k"])
    phase_catalog = canonical_phase_catalog(phase_input)
    identity = verify_b5_phase_identity(b5_input, b52, phase_catalog, dimension, k)

    spaces = [tuple(item["normal_space"]) for item in phase_catalog]
    recomputed_layout = layout_data_from_spaces(spaces, identity["order_positions"], dimension)
    if max(recomputed_layout["cut_widths"], default=0) > k:
        raise AssertionError("Phase-A recomputed B5.2B layout exceeds k")

    trace = {
        "source_gate": "C049.1_B5.2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION",
        "b5_2b_admission_receipt_semantic_digest": spec["authority_inputs"]["b5_2b_positive_terminal"]["receipt_semantic_digest"],
        "b5_2b_candidate_semantic_digest": b52["semantic_digest"],
        "factor_order_ids": identity["factor_order_ids"],
        "factor_order_ids_digest": dg(identity["factor_order_ids"]),
        "factor_id_to_phase_a_position": identity["map_records"],
        "affine_identity_digest": identity["affine_identity_digest"],
        "b5_3_branch_separation_receipt_semantic_digest": spec["authority_inputs"]["b5_3_negative_terminal_separation"]["receipt_semantic_digest"],
        "b5_3_no_layout_compiled_as_phase_a_transcript": False,
        "b5_2b_cut_certificates_trusted": False,
        "phase_a_layout_recomputed_before_transcript": True,
    }
    transcript = make_found_layout_transcript(
        identity["order_positions"],
        recomputed_layout["cut_widths"],
        recomputed_layout["cut_bases"],
        constructor_id=spec["adapter_contract"]["constructor_id"],
        discovery_claim=True,
        constructor_trace=trace,
    )
    if not validate_transcript_digest(transcript):
        raise AssertionError("canonical Phase-A constructor transcript digest")

    caps = phase_input.get("caps", {})
    result = solve_phase_a(
        phase_input["factors"],
        dimension,
        k=k,
        constructor_transcript=transcript,
        discovery_cap=caps.get("discovery_cap"),
        work_cap=caps.get("work_cap"),
        certificate_cap=caps.get("certificate_cap"),
        trellis_work_cap=caps.get("trellis_work_cap"),
        trellis_certificate_cap=caps.get("trellis_certificate_cap"),
    )
    if not verify_phase_a_certificate(result):
        raise AssertionError("Phase-A certificate verification failed after B5.4 handoff")

    phase_status = result["status"]
    if result.get("constructor_terminal") != "FOUND_LAYOUT":
        raise AssertionError("Phase-A did not preserve FOUND_LAYOUT constructor terminal")
    if result.get("verified_layout", {}).get("order_positions") != identity["order_positions"]:
        raise AssertionError("Phase-A verified layout order differs from adapter order")
    if result["verified_layout"].get("cut_widths") != recomputed_layout["cut_widths"]:
        raise AssertionError("Phase-A verified cut widths differ from adapter recomputation")
    if result["verified_layout"].get("cut_bases") != recomputed_layout["cut_bases"]:
        raise AssertionError("Phase-A verified cut bases differ from adapter recomputation")

    nested = result.get("trellis_result")
    c047_status = phase_status
    if nested is not None:
        if nested.get("status") != phase_status:
            raise AssertionError("Phase-A outer/nested C047 status mismatch")
        c047_status = nested["status"]

    payload = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "authority_bindings": authority,
        "dimension": dimension,
        "k": k,
        "phase_a_factor_catalog": phase_catalog,
        "b5_2b_candidate_semantic_digest": b52["semantic_digest"],
        "adapter_identity": identity,
        "phase_a_recomputed_layout": recomputed_layout,
        "constructor_transcript": transcript,
        "phase_a_result": result,
        "c047_status": c047_status,
        "handoff_checks": {
            "b5_2b_independent_verifier_required_in_ci": True,
            "normal_space_identity": True,
            "affine_fingerprint_identity": True,
            "factor_id_position_map_exact": True,
            "b5_2b_cut_certificates_trusted": False,
            "phase_a_layout_recomputed": True,
            "canonical_found_layout_transcript": True,
            "phase_a_solve_reverification": True,
            "phase_a_certificate_verifier_pass": True,
            "direct_compile_order_probe_called_by_adapter": False,
            "b5_3_bare_no_layout_transcript_created": False,
            "nested_status_propagated_without_promotion": True,
        },
        "strict_boundary": spec["strict_boundary"],
    }
    out = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    out["semantic_digest"] = dg(payload)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--b5-input", type=Path, required=True)
    p.add_argument("--phase-a-input", type=Path, required=True)
    p.add_argument("--b5-2b-candidate", type=Path, required=True)
    p.add_argument("--b5-2b-admission", type=Path, required=True)
    p.add_argument("--b5-3-admission", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    artifact = build(load(a.spec), load(a.b5_input), load(a.phase_a_input), load(a.b5_2b_candidate), load(a.b5_2b_admission), load(a.b5_3_admission))
    save(artifact, a.output)
    q = artifact["proof_payload"]
    print("JANUS_B5_4_CORRECTED_DISCOVERY_PHASE_A_C047_HANDOFF = PASS")
    print("C047_STATUS =", q["c047_status"])
    print("FACTOR_ORDER_IDS =", json.dumps(q["adapter_identity"]["factor_order_ids"], separators=(",", ":")))
    print("ORDER_POSITIONS =", json.dumps(q["adapter_identity"]["order_positions"], separators=(",", ":")))
    print("PHASE_A_MAX_LAYOUT_WIDTH =", max(q["phase_a_recomputed_layout"]["cut_widths"], default=0))
    print("PHASE_A_CERTIFICATE_VERIFIER = PASS")
    print("DIRECT_COMPILE_ORDER_PROBE_CALLED_BY_ADAPTER = FALSE")
    print("B5_3_BARE_NO_LAYOUT_TRANSCRIPT_CREATED = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE_PENDING_CONTRACT_COMPLETION_REVIEW")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
