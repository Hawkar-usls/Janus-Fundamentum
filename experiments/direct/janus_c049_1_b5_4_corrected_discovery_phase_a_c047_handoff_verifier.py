from __future__ import annotations

import argparse
import copy
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


def affine_fp(factor: dict) -> dict:
    return {"canonical_affine_equations": [list(eq) for eq in factor["equations"]]}


def canonical_b5_space(rows: list[int], dimension: int) -> list[int]:
    dummy = normalize_factors(
        [{"factor_id": 0, "input_position": 0, "equations": [(int(mask), 0) for mask in rows]}],
        dimension,
    )
    if len(dummy) != 1:
        raise AssertionError("failed to canonicalize B5 normal space")
    return list(normal_space(dummy[0]))


def authority(spec: dict, r52: dict, r53: dict) -> dict:
    a = spec["authority_inputs"]
    e52 = a["b5_2b_positive_terminal"]
    if r52.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B receipt schema")
    if r52.get("semantic_digest") != e52["receipt_semantic_digest"] or dg(r52["audit_payload"]) != e52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B receipt semantic digest")
    if r52["audit_payload"].get("admission_review_id") != e52["review_id"] or r52["audit_payload"].get("exact_proof_head") != e52["proof_head"]:
        raise AssertionError("B5.2B review/proof authority")
    if r52["audit_payload"]["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B admitted positive statement")

    e53 = a["b5_3_negative_terminal_separation"]
    if r53.get("schema") != "janus.c049_1.b5_3.generic_empty_root_terminal_composition_admission_receipt.v1_1":
        raise AssertionError("B5.3 receipt schema")
    if r53.get("semantic_digest") != e53["receipt_semantic_digest"] or dg(r53["audit_payload"]) != e53["receipt_semantic_digest"]:
        raise AssertionError("B5.3 receipt semantic digest")
    if r53["audit_payload"].get("admission_review_id") != e53["review_id"] or r53["audit_payload"].get("exact_proof_head") != e53["proof_head"]:
        raise AssertionError("B5.3 review/proof authority")
    if r53["audit_payload"]["semantic_conclusion"].get("generic_no_layout_at_cap") != "TRUE_WHEN_B5_1_VERIFIED_CLOSED_ROOT_EMPTY_AND_B5_3_AUTHORITY_BRIDGE_PASSES":
        raise AssertionError("B5.3 admitted negative statement")

    return {
        "b5_2b_positive_terminal_authority": True,
        "b5_3_negative_branch_separation_authority": True,
        "b5_3_no_layout_compiled_as_phase_a_transcript": False,
        "phase_a_existing_verified_layout_to_c047_surface_bound": True,
    }


def phase_catalog(phase_input: dict) -> list[dict]:
    dimension = int(phase_input["dimension"])
    factors = normalize_factors(phase_input["factors"], dimension)
    ids = [int(f["factor_id"]) for f in factors]
    if len(ids) != len(set(ids)):
        raise AssertionError("duplicate Phase-A factor ID")
    return [
        {
            "normalized_position": i,
            "factor_id": int(f["factor_id"]),
            "input_position": int(f["input_position"]),
            "normal_space": list(normal_space(f)),
            "affine_fingerprint": affine_fp(f),
            "equations": [list(eq) for eq in f["equations"]],
        }
        for i, f in enumerate(factors)
    ]


def adapter_identity(b5_input: dict, b52: dict, catalog: list[dict], dimension: int, k: int) -> dict:
    if int(b5_input["ambient_dim"]) != dimension or int(b5_input["k"]) != k:
        raise AssertionError("B5/Phase-A parameters")
    if b52.get("schema") != B5_2B_SCHEMA or b52.get("semantic_digest_scope") != "proof_payload" or b52.get("semantic_digest") != dg(b52["proof_payload"]):
        raise AssertionError("B5.2B candidate schema/digest")
    p = b52["proof_payload"]
    if p.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW" or p.get("candidate_found_layout") is not True:
        raise AssertionError("B5.2B positive layout subject")
    if int(p["ambient_dim"]) != dimension or int(p["k"]) != k:
        raise AssertionError("B5.2B/Phase-A parameters")

    by_phase = {x["factor_id"]: x for x in catalog}
    by_b5 = {}
    for factor in b5_input["factors"]:
        fid = int(factor["id"])
        if fid in by_b5:
            raise AssertionError("duplicate B5 factor ID")
        by_b5[fid] = factor
    if set(by_b5) != set(by_phase):
        raise AssertionError("indexed factor ID domain mismatch")

    records = []
    seen = set()
    for layout_position, row in enumerate(p["layout_records"]):
        fid = int(row["factor_id"])
        if fid not in by_phase or fid in seen:
            raise AssertionError("B5.2B order is not an exact known-ID permutation")
        seen.add(fid)
        phase = by_phase[fid]
        fingerprint = phase["affine_fingerprint"]
        if by_b5[fid].get("affine_offset") != fingerprint or row.get("affine_offset") != fingerprint:
            raise AssertionError("affine fingerprint identity")
        if canonical_b5_space(by_b5[fid]["normal_space"], dimension) != phase["normal_space"]:
            raise AssertionError("B5 input/Phase-A normal-space identity")
        if row.get("normal_space") != phase["normal_space"]:
            raise AssertionError("B5.2B layout/Phase-A normal-space identity")
        records.append(
            {
                "layout_position": layout_position,
                "factor_id": fid,
                "phase_a_normalized_position": phase["normalized_position"],
                "phase_a_input_position": phase["input_position"],
                "normal_space": phase["normal_space"],
                "affine_fingerprint": fingerprint,
            }
        )
    if seen != set(by_phase) or [int(x) for x in p["factor_order_ids"]] != [r["factor_id"] for r in records]:
        raise AssertionError("B5.2B factor order/list records identity")
    return {
        "map_records": records,
        "order_positions": [r["phase_a_normalized_position"] for r in records],
        "factor_order_ids": [r["factor_id"] for r in records],
        "affine_identity_digest": dg([[r["factor_id"], r["normal_space"], r["affine_fingerprint"]] for r in records]),
    }


def expected(spec: dict, b5_input: dict, phase_input: dict, b52: dict, r52: dict, r53: dict) -> dict:
    auth = authority(spec, r52, r53)
    dimension = int(phase_input["dimension"]); k = int(phase_input["k"])
    catalog = phase_catalog(phase_input)
    identity = adapter_identity(b5_input, b52, catalog, dimension, k)
    spaces = [tuple(x["normal_space"]) for x in catalog]
    layout = layout_data_from_spaces(spaces, identity["order_positions"], dimension)
    if max(layout["cut_widths"], default=0) > k:
        raise AssertionError("recomputed layout exceeds k")
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
    transcript = make_found_layout_transcript(identity["order_positions"], layout["cut_widths"], layout["cut_bases"], constructor_id=spec["adapter_contract"]["constructor_id"], discovery_claim=True, constructor_trace=trace)
    if not validate_transcript_digest(transcript):
        raise AssertionError("constructor transcript digest")
    caps = phase_input.get("caps", {})
    result = solve_phase_a(
        phase_input["factors"], dimension, k=k, constructor_transcript=transcript,
        discovery_cap=caps.get("discovery_cap"), work_cap=caps.get("work_cap"), certificate_cap=caps.get("certificate_cap"),
        trellis_work_cap=caps.get("trellis_work_cap"), trellis_certificate_cap=caps.get("trellis_certificate_cap"),
    )
    if not verify_phase_a_certificate(result):
        raise AssertionError("Phase-A result certificate")
    if result.get("constructor_terminal") != "FOUND_LAYOUT":
        raise AssertionError("constructor terminal")
    if result.get("verified_layout", {}).get("order_positions") != identity["order_positions"]:
        raise AssertionError("Phase-A order replay")
    if result["verified_layout"].get("cut_widths") != layout["cut_widths"] or result["verified_layout"].get("cut_bases") != layout["cut_bases"]:
        raise AssertionError("Phase-A cut replay")
    nested = result.get("trellis_result")
    status = result["status"]
    if nested is not None and nested.get("status") != status:
        raise AssertionError("outer/nested C047 status")
    payload = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "authority_bindings": auth,
        "dimension": dimension,
        "k": k,
        "phase_a_factor_catalog": catalog,
        "b5_2b_candidate_semantic_digest": b52["semantic_digest"],
        "adapter_identity": identity,
        "phase_a_recomputed_layout": layout,
        "constructor_transcript": transcript,
        "phase_a_result": result,
        "c047_status": status,
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
    return payload


def verify(candidate: dict, spec: dict, b5_input: dict, phase_input: dict, b52: dict, r52: dict, r53: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.4 spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or candidate.get("semantic_digest") != dg(candidate["proof_payload"]):
        raise AssertionError("B5.4 candidate schema/digest")
    exp = expected(spec, b5_input, phase_input, b52, r52, r53)
    if candidate["proof_payload"] != exp:
        raise AssertionError("B5.4 candidate differs from independent expected handoff")
    return exp


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(base: dict, spec: dict, b5_input: dict, phase_input: dict, b52: dict, r52: dict, r53: dict, open_candidate: dict | None = None, open_phase_input: dict | None = None) -> tuple[int, int]:
    attacks = []
    def add(name, mutation, source=None, phase=None):
        c = copy.deepcopy(source or base); rr52=copy.deepcopy(r52); rr53=copy.deepcopy(r53); bb52=copy.deepcopy(b52); pp=copy.deepcopy(phase or phase_input); bb5=copy.deepcopy(b5_input)
        mutation(c, rr52, rr53, bb52, pp, bb5); repair(c)
        if rr52.get("semantic_digest_scope") == "audit_payload": rr52["semantic_digest"] = dg(rr52["audit_payload"])
        if rr53.get("semantic_digest_scope") == "audit_payload": rr53["semantic_digest"] = dg(rr53["audit_payload"])
        attacks.append((name,c,bb5,pp,bb52,rr52,rr53))
    p=lambda c:c["proof_payload"]
    add("T01_B52_AUTH",lambda c,a,b,x,ph,bi:a["audit_payload"].__setitem__("admission_review_id",0))
    add("T02_B53_AUTH",lambda c,a,b,x,ph,bi:b["audit_payload"].__setitem__("admission_review_id",0))
    add("T03_PHASE_FROZEN",lambda c,a,b,x,ph,bi:p(c)["handoff_checks"].__setitem__("phase_a_certificate_verifier_pass",False))
    add("T04_FACTOR_POSITION",lambda c,a,b,x,ph,bi:p(c)["adapter_identity"]["map_records"][0].__setitem__("phase_a_normalized_position",999))
    add("T05_AFFINE_SWAP",lambda c,a,b,x,ph,bi:p(c)["adapter_identity"]["map_records"][0].__setitem__("affine_fingerprint",{"canonical_affine_equations":[[1,1]]}))
    add("T06_NORMAL_SPACE",lambda c,a,b,x,ph,bi:p(c)["adapter_identity"]["map_records"][0].__setitem__("normal_space",[]))
    add("T07_FACTOR_ORDER",lambda c,a,b,x,ph,bi:p(c)["adapter_identity"]["factor_order_ids"].append(p(c)["adapter_identity"]["factor_order_ids"][0]))
    add("T08_FORGED_B52_WIDTH",lambda c,a,b,x,ph,bi:x["proof_payload"]["cut_certificates"][0].__setitem__("width",999))
    add("T09_FORGED_B52_BASIS",lambda c,a,b,x,ph,bi:x["proof_payload"]["cut_certificates"][0].__setitem__("boundary_rref",[999]))
    add("T10_TRANSCRIPT_ORDER",lambda c,a,b,x,ph,bi:p(c)["constructor_transcript"]["order_positions"].reverse())
    add("T11_TRANSCRIPT_WIDTH",lambda c,a,b,x,ph,bi:p(c)["constructor_transcript"]["cut_widths"].__setitem__(0,999))
    add("T12_TRANSCRIPT_BASE",lambda c,a,b,x,ph,bi:p(c)["constructor_transcript"]["cut_bases"].__setitem__(0,[999]))
    add("T13_TRANSCRIPT_DIGEST",lambda c,a,b,x,ph,bi:p(c)["constructor_transcript"].__setitem__("transcript_digest","0"*64))
    add("T14_DIRECT_COMPILE",lambda c,a,b,x,ph,bi:p(c)["handoff_checks"].__setitem__("direct_compile_order_probe_called_by_adapter",True))
    add("T15_FORGE_VERIFIED_LAYOUT",lambda c,a,b,x,ph,bi:p(c)["phase_a_result"]["verified_layout"]["order_positions"].reverse())
    add("T16_FORGE_C047_STATUS",lambda c,a,b,x,ph,bi:p(c).__setitem__("c047_status","FORGED"))
    add("T17_FORGE_SAT_WITNESS",lambda c,a,b,x,ph,bi:p(c)["phase_a_result"].__setitem__("ambient_witness",999))
    if open_candidate is not None and open_phase_input is not None:
        add("T18_OPEN_PROMOTION",lambda c,a,b,x,ph,bi:p(c).__setitem__("c047_status","SAT"),source=open_candidate,phase=open_phase_input)
    else:
        add("T18_OPEN_PROMOTION",lambda c,a,b,x,ph,bi:p(c)["handoff_checks"].__setitem__("nested_status_propagated_without_promotion",False))
    add("T19_B53_BARE_NO_LAYOUT",lambda c,a,b,x,ph,bi:p(c)["handoff_checks"].__setitem__("b5_3_bare_no_layout_transcript_created",True))
    add("T20_LOCAL_NO_LAYOUT_CONFUSION",lambda c,a,b,x,ph,bi:p(c)["authority_bindings"].__setitem__("b5_3_no_layout_compiled_as_phase_a_transcript",True))
    add("T21_C047_WITHOUT_PHASE_A",lambda c,a,b,x,ph,bi:p(c)["handoff_checks"].__setitem__("phase_a_solve_reverification",False))
    add("T22_RUNTIME_PROMOTION",lambda c,a,b,x,ph,bi:p(c)["strict_boundary"].update({"all_input_termination":"TRUE","polynomial_runtime":"TRUE"}))
    add("T23_GLOBAL_PROMOTION",lambda c,a,b,x,ph,bi:p(c)["strict_boundary"].update({"arbitrary_input_global_engine_theorem":True,"p_vs_np":"CLOSED"}))
    add("T24_B5_COMPLETE",lambda c,a,b,x,ph,bi:p(c)["strict_boundary"].__setitem__("b5_complete",True))
    rejected=0
    for name,c,bi,ph,x,a,b in attacks:
        try: verify(c,spec,bi,ph,x,a,b)
        except Exception: rejected+=1; continue
        raise AssertionError(name+" survived")
    return rejected,len(attacks)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--spec",type=Path,required=True); p.add_argument("--b5-input",type=Path,required=True); p.add_argument("--phase-a-input",type=Path,required=True)
    p.add_argument("--b5-2b-candidate",type=Path,required=True); p.add_argument("--b5-2b-admission",type=Path,required=True); p.add_argument("--b5-3-admission",type=Path,required=True); p.add_argument("--candidate",type=Path,required=True)
    p.add_argument("--tamper-suite",action="store_true"); p.add_argument("--open-candidate",type=Path); p.add_argument("--open-phase-a-input",type=Path)
    a=p.parse_args(); spec=load(a.spec); bi=load(a.b5_input); ph=load(a.phase_a_input); b52=load(a.b5_2b_candidate); r52=load(a.b5_2b_admission); r53=load(a.b5_3_admission); c=load(a.candidate)
    exp=verify(c,spec,bi,ph,b52,r52,r53)
    print("JANUS_B5_4_CORRECTED_DISCOVERY_PHASE_A_C047_HANDOFF_INDEPENDENT_VERIFIER = PASS")
    print("C047_STATUS =",exp["c047_status"]); print("PHASE_A_FOUND_LAYOUT_TRANSCRIPT = PASS"); print("PHASE_A_LAYOUT_RECOMPUTATION = PASS"); print("PHASE_A_CERTIFICATE_VERIFIER = PASS")
    print("AFFINE_FINGERPRINT_IDENTITY = PASS"); print("DIRECT_COMPILE_ORDER_PROBE_CALLED_BY_ADAPTER = FALSE"); print("B5_3_BARE_NO_LAYOUT_TRANSCRIPT_CREATED = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED"); print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED"); print("B5_COMPLETE = FALSE_PENDING_CONTRACT_COMPLETION_REVIEW"); print("P_VS_NP = OPEN")
    if a.tamper_suite:
        oc=load(a.open_candidate) if a.open_candidate else None; op=load(a.open_phase_a_input) if a.open_phase_a_input else None
        r,t=tamper_suite(c,spec,bi,ph,b52,r52,r53,oc,op); print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}")

if __name__=="__main__": main()
