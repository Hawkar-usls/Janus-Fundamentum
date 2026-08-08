from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import janus_c049_1_b5_4_corrected_discovery_c047_rebound as b54base
import janus_c049_1_b5_4_corrected_discovery_c047_rebound_v11 as b54v11
from janus_c049_fpt_integration_core import layout_data_from_spaces, make_found_layout_transcript

SCHEMA = "janus.c049_1.b5.full_input_original_order_lift_c047_rebound_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.full_input_original_order_lift_c047_rebound_spec.v1"
PRE_SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_candidate.v1"
B51_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
B52_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"


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


def valid_artifact(value: dict, schema: str) -> bool:
    return (
        isinstance(value, dict)
        and value.get("schema") == schema
        and value.get("semantic_digest_scope") == "proof_payload"
        and value.get("semantic_digest") == dg(value.get("proof_payload"))
    )


def canonical_original_catalog(pre_payload: dict) -> list[dict]:
    out: list[dict] = []
    for position, rec in enumerate(pre_payload["original_catalog"]):
        if rec.get("occurrence_index") != position:
            raise AssertionError("preprocessing original occurrence index")
        fid = rec.get("factor_id")
        if not isinstance(fid, str) or not fid:
            raise AssertionError("order-lift requires stable nonempty string factor IDs")
        out.append(
            {
                "id": fid,
                "normal_space": [int(x) for x in rec["normal_space"]],
                "affine_offset": copy.deepcopy(rec.get("affine_offset")),
            }
        )
    if len({x["id"] for x in out}) != len(out):
        raise AssertionError("duplicate original factor ID")
    return out


def expected_reduced_catalog(pre_payload: dict) -> list[dict]:
    out: list[dict] = []
    for position, rec in enumerate(pre_payload["discovery_catalog"]):
        if rec.get("occurrence_index") != position:
            raise AssertionError("preprocessing discovery occurrence index")
        out.append(
            {
                "id": str(rec["factor_id"]),
                "normal_space": [int(x) for x in rec["normal_space"]],
                "affine_offset": copy.deepcopy(rec.get("affine_offset")),
            }
        )
    return out


def compare_layouts(reduced_payload: dict, original_layout: dict, dimension: int) -> list[dict]:
    return b54base.compare_b5_phase_a_cuts(reduced_payload, original_layout, dimension)


def compare_original_phase_layout(original_layout: dict, phase_layout: dict, dimension: int) -> list[dict]:
    if len(original_layout["cut_widths"]) != len(phase_layout["cut_widths"]):
        raise AssertionError("original/Phase-A cut count")
    out: list[dict] = []
    for i, (ow, pw, ob, pb) in enumerate(
        zip(original_layout["cut_widths"], phase_layout["cut_widths"], original_layout["cut_bases"], phase_layout["cut_bases"])
    ):
        o = b54base.semantic_space(ob, dimension)
        p = b54base.semantic_space(pb, dimension)
        if int(ow) != int(pw) or o != p:
            raise AssertionError("original/Phase-A cut mismatch")
        out.append(
            {
                "cut": i,
                "width": int(ow),
                "original_boundary_semantic_digest": dg(list(o)),
                "phase_a_boundary_semantic_digest": dg(list(p)),
                "semantic_boundary_equal": True,
            }
        )
    return out


def wrap(spec: dict, payload: dict) -> dict:
    payload["strict_boundary"] = copy.deepcopy(spec["strict_boundary"])
    artifact = {
        "schema": SCHEMA,
        "semantic_digest_scope": "proof_payload",
        "proof_payload": payload,
    }
    artifact["semantic_digest"] = dg(payload)
    return artifact


def build(
    spec: dict,
    raw_original: dict,
    preprocessing: dict,
    reduced_raw: dict | None,
    b51: dict | None,
    carrier: dict | None,
    b52: dict | None,
    caps: dict[str, int | None],
) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("order-lift spec")
    if not valid_artifact(preprocessing, PRE_SCHEMA):
        raise AssertionError("preprocessing artifact")
    pre = preprocessing["proof_payload"]
    d, k = int(pre["ambient_dim"]), int(pre["k"])
    if int(raw_original["ambient_dim"]) != d or int(raw_original["k"]) != k:
        raise AssertionError("original input/preprocessing parameters")

    base = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "ambient_dim": d,
        "k": k,
        "preprocessing_semantic_digest": preprocessing["semantic_digest"],
        "preprocessing_branch": pre["preprocessing_branch"],
        "phase_a_capability_request": {key: caps.get(key) for key in sorted(caps)},
        "authority_policy": {
            "reduced_geometry_is_discovery_only": True,
            "original_geometry_required_for_final_width_and_affine_rebound": True,
            "direct_b5_4_on_reduced_catalog": False,
            "strict_prefix_c047": False,
            "b5_3_no_layout_used_as_c047_unsat_premise": False,
            "historical_phase_a_c047_code_modified": False,
        },
    }

    if pre["preprocessing_branch"] == "LOCAL_NO_LAYOUT_SOURCE_CANDIDATE_PENDING_REVIEW":
        base.update({
            "lift_status": "NOT_APPLICABLE_PREPROCESSING_NO_LAYOUT",
            "reduced_b5_2b_semantic_digest": None,
            "factor_order_ids": None,
            "original_layout_replay": None,
            "reduced_to_original_cut_bridge": None,
            "affine_binding_status": "NOT_ATTEMPTED",
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED_PREPROCESSING_NO_LAYOUT",
        })
        return wrap(spec, base)
    if pre["preprocessing_branch"] == "TRIVIAL_EMPTY_INPUT":
        base.update({
            "lift_status": "NOT_APPLICABLE_EMPTY_INPUT",
            "reduced_b5_2b_semantic_digest": None,
            "factor_order_ids": [],
            "original_layout_replay": None,
            "reduced_to_original_cut_bridge": None,
            "affine_binding_status": "NOT_ATTEMPTED",
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED_EMPTY_INPUT",
        })
        return wrap(spec, base)
    if pre["preprocessing_branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        raise AssertionError("unknown preprocessing branch")

    if reduced_raw is None or b51 is None or carrier is None or b52 is None:
        raise AssertionError("positive lift requires reduced B5 chain")
    if not valid_artifact(b51, B51_SCHEMA) or not valid_artifact(b52, B52_SCHEMA):
        raise AssertionError("reduced B5 artifact digest")
    q51, p52 = b51["proof_payload"], b52["proof_payload"]
    if q51.get("capability_status") == "OPEN_RUNTIME_CAPABILITY":
        base.update({
            "lift_status": "NOT_APPLICABLE_REDUCED_OPEN_RUNTIME",
            "reduced_b5_2b_semantic_digest": None,
            "factor_order_ids": None,
            "original_layout_replay": None,
            "reduced_to_original_cut_bridge": None,
            "affine_binding_status": "NOT_ATTEMPTED",
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED_REDUCED_OPEN",
        })
        return wrap(spec, base)
    if q51.get("capability_status") != "CLOSED_COMPLETE_TRACE":
        raise AssertionError("unexpected reduced B5.1 status")
    if p52.get("reconstruction_status") == "NOT_APPLICABLE_EMPTY_ROOT":
        base.update({
            "lift_status": "NOT_APPLICABLE_REDUCED_NO_LAYOUT",
            "reduced_b5_2b_semantic_digest": b52["semantic_digest"],
            "factor_order_ids": None,
            "original_layout_replay": None,
            "reduced_to_original_cut_bridge": None,
            "affine_binding_status": "NOT_ATTEMPTED",
            "phase_a_factor_bijection": None,
            "phase_a_factors": None,
            "phase_a_order_positions": None,
            "phase_a_transcript": None,
            "phase_a_certificate": None,
            "historical_phase_a_verifier_pass": False,
            "c047_result": "NOT_ESTABLISHED_REDUCED_NO_LAYOUT",
        })
        return wrap(spec, base)
    if p52.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW" or p52.get("candidate_found_layout") is not True:
        raise AssertionError("reduced B5.2B positive status")
    if p52.get("b5_1_semantic_digest") != b51["semantic_digest"] or p52.get("carrier_semantic_digest") != carrier.get("semantic_digest"):
        raise AssertionError("reduced B5.2B subject binding")

    expected_reduced = expected_reduced_catalog(pre)
    if q51.get("canonical_factor_catalog") != expected_reduced:
        raise AssertionError("B5.1 catalog is not exact preprocessing discovery catalog")
    if p52.get("canonical_factor_catalog") != expected_reduced:
        raise AssertionError("B5.2B catalog is not exact preprocessing discovery catalog")
    if int(reduced_raw["ambient_dim"]) != d or int(reduced_raw["k"]) != k:
        raise AssertionError("reduced raw parameters")

    original = canonical_original_catalog(pre)
    if len(original) != len(expected_reduced):
        raise AssertionError("original/reduced occurrence count")
    order_ids = [str(x) for x in p52["factor_order_ids"]]
    all_ids = [x["id"] for x in original]
    if len(order_ids) != len(all_ids) or len(set(order_ids)) != len(order_ids) or sorted(order_ids) != sorted(all_ids):
        raise AssertionError("reduced full-input order is not exact original occurrence permutation")
    by_id = {item["id"]: position for position, item in enumerate(original)}
    order_positions = [by_id[fid] for fid in order_ids]
    original_spaces = [tuple(int(v) for v in item["normal_space"]) for item in original]
    original_layout = layout_data_from_spaces(original_spaces, order_positions, d)
    if int(original_layout["maximum_width"]) > k:
        raise AssertionError("lifted original order exceeds k")
    cut_bridge = compare_layouts(p52, original_layout, d)
    original_layout_records = [
        {
            "position": position,
            "factor_id": fid,
            "normal_space": copy.deepcopy(original[by_id[fid]]["normal_space"]),
            "affine_offset": copy.deepcopy(original[by_id[fid]]["affine_offset"]),
        }
        for position, fid in enumerate(order_ids)
    ]

    base.update({
        "reduced_b5_2b_semantic_digest": b52["semantic_digest"],
        "factor_order_ids": order_ids,
        "original_layout_records": original_layout_records,
        "original_layout_replay": original_layout,
        "original_layout_semantic_digest": dg(original_layout),
        "reduced_to_original_cut_bridge": cut_bridge,
        "reduced_to_original_cut_bridge_digest": dg(cut_bridge),
    })

    adapter_status, phase_a_factors, bijection, adapter_reason = b54base.build_adapter(original, d)
    if adapter_status != "BOUND":
        base.update({
            "lift_status": adapter_status,
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

    phase_by_id = {str(rec["b5_factor_id"]): rec for rec in bijection}
    phase_order_positions = [int(phase_by_id[fid]["phase_a_input_position"]) for fid in order_ids]
    if phase_order_positions != order_positions:
        raise AssertionError("original/Phase-A numeric occurrence order mismatch")
    phase_spaces = [tuple(mask for mask, _ in factor["equations"]) for factor in phase_a_factors]
    phase_layout = layout_data_from_spaces(phase_spaces, phase_order_positions, d)
    original_phase_bridge = compare_original_phase_layout(original_layout, phase_layout, d)
    transcript = make_found_layout_transcript(
        phase_order_positions,
        phase_layout["cut_widths"],
        phase_layout["cut_bases"],
        constructor_id="B5_FULL_INPUT_ORIGINAL_ORDER_LIFT",
        discovery_claim=True,
        constructor_trace={
            "preprocessing_semantic_digest": preprocessing["semantic_digest"],
            "reduced_b5_2b_semantic_digest": b52["semantic_digest"],
            "factor_order_ids": order_ids,
            "original_layout_semantic_digest": dg(original_layout),
            "reduced_to_original_cut_bridge_digest": dg(cut_bridge),
            "original_to_phase_a_cut_bridge_digest": dg(original_phase_bridge),
        },
    )
    capability = b54base.capability_from_args(d, phase_a_factors, k, caps)
    certificate = b54v11.solve_phase_a_keyword_adapter(phase_a_factors, d, capability, transcript)
    b54v11.strict_historical_verify(phase_a_factors, d, certificate)
    c047_result = str(certificate["status"])

    base.update({
        "lift_status": "ORIGINAL_ORDER_LIFT_AND_PHASE_A_C047_COMPLETED" if c047_result in {"SAT", "UNSAT"} else "ORIGINAL_ORDER_LIFT_PHASE_A_C047_OPEN",
        "affine_binding_status": "BOUND",
        "affine_binding_open_reason": None,
        "phase_a_factor_bijection": bijection,
        "phase_a_factor_bijection_digest": dg(bijection),
        "phase_a_factors": phase_a_factors,
        "phase_a_factor_catalog_digest": dg(phase_a_factors),
        "phase_a_order_positions": phase_order_positions,
        "phase_a_layout_recomputation": phase_layout,
        "original_to_phase_a_cut_bridge": original_phase_bridge,
        "phase_a_transcript": transcript,
        "phase_a_certificate": certificate,
        "historical_phase_a_verifier_pass": True,
        "c047_result": c047_result,
        "c047_reason": certificate.get("reason"),
    })
    return wrap(spec, base)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--original-input", type=Path, required=True)
    parser.add_argument("--preprocessing", type=Path, required=True)
    parser.add_argument("--reduced-input", type=Path)
    parser.add_argument("--b5-1-artifact", type=Path)
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
    artifact = build(
        load(args.spec),
        load(args.original_input),
        load(args.preprocessing),
        load(args.reduced_input),
        load(args.b5_1_artifact),
        load(args.carrier),
        load(args.b5_2b_artifact),
        caps,
    )
    save(artifact, args.output)
    p = artifact["proof_payload"]
    print("JANUS_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND = PASS")
    print("LIFT_STATUS =", p["lift_status"])
    print("ORIGINAL_MAX_WIDTH =", None if p.get("original_layout_replay") is None else p["original_layout_replay"]["maximum_width"])
    print("AFFINE_BINDING_STATUS =", p["affine_binding_status"])
    print("C047_RESULT =", p["c047_result"])
    print("HISTORICAL_PHASE_A_VERIFIER_PASS =", str(p["historical_phase_a_verifier_pass"]).upper())
    print("DIRECT_B5_4_ON_REDUCED_CATALOG = FALSE")
    print("STRICT_PREFIX_C047 = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
