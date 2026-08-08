from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "janus.c049_1.b5_3.generic_empty_root_terminal_composition_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5_3.generic_empty_root_terminal_composition_spec.v1"
B5_1_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def verify_audit_semantic(audit: dict, expected_schema: str, expected_digest: str) -> None:
    if audit.get("schema") != expected_schema:
        raise AssertionError("authority audit schema mismatch")
    if audit.get("semantic_digest_scope") != "audit_payload":
        raise AssertionError("authority audit digest scope")
    if audit.get("semantic_digest") != expected_digest or dg(audit["audit_payload"]) != expected_digest:
        raise AssertionError("authority audit semantic digest mismatch")


def verify_authority(spec: dict, b5_1_receipt: dict, composition: dict, o7: dict, b5_2b_receipt: dict) -> dict:
    a = spec["authority_inputs"]

    if b5_1_receipt.get("schema") != "janus.c049_1.b5_1.generic_corrected_runtime_trace_executor_admission_receipt.v1":
        raise AssertionError("B5.1 admission receipt schema")
    b51 = b5_1_receipt["audit_payload"]
    if b51.get("admission_review_id") != a["b5_1_runtime_admission"]["review_id"]:
        raise AssertionError("B5.1 review authority")
    if b51.get("exact_proof_head") != a["b5_1_runtime_admission"]["proof_head"]:
        raise AssertionError("B5.1 proof head")
    if b51["semantic_conclusion"].get("generic_corrected_algorithm1_runtime_trace_mapping") != "TRUE_WHEN_RUNTIME_RETURNS_CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.1 admitted closed-trace statement")
    if b51["semantic_conclusion"].get("generic_no_layout_at_cap") != "FORBIDDEN":
        raise AssertionError("B5.1 negative terminal ceiling")

    verify_audit_semantic(
        composition,
        "janus.c049_1.general_structural_induction_composition_independent_source_audit.v1",
        a["general_structural_induction_composition"]["audit_semantic_digest"],
    )
    comp = composition["audit_payload"]
    if comp["proof_subject"].get("exact_head") != a["general_structural_induction_composition"]["proof_head"]:
        raise AssertionError("general composition proof head")
    if comp["proof_subject"].get("review_id") != a["general_structural_induction_composition"]["review_id"]:
        raise AssertionError("general composition review")
    if comp["local_composition_audit"].get("root_full_set_identity_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("general composition root identity")
    if comp["local_composition_audit"].get("structural_induction_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("general composition structural induction")
    if comp["published_source_audit"].get("root") != "Proposition 5.8 specializes to V_root=V and B_root={0} before the terminal criterion.":
        raise AssertionError("general composition root specialization")

    verify_audit_semantic(
        o7,
        "janus.c049_1.general_empty_root_specialization_authority_closure_audit.v1",
        a["o7_empty_root_specialization"]["audit_semantic_digest"],
    )
    o = o7["audit_payload"]
    if o["proof_subject"].get("exact_head") != a["o7_empty_root_specialization"]["proof_head"]:
        raise AssertionError("O7 proof head")
    if o["proof_subject"].get("review_id") != a["o7_empty_root_specialization"]["review_id"]:
        raise AssertionError("O7 review")
    if o["published_source_audit"].get("abstract_biconditional") != "FS_k(V,{0}) nonempty iff there exists a complete linear layout of V with width<=k":
        raise AssertionError("O7 biconditional")
    if o["published_source_audit"].get("engine_root_identity_is_separate") is not True:
        raise AssertionError("O7 engine identity separation")

    if b5_2b_receipt.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B corroborating receipt schema")
    b52 = b5_2b_receipt["audit_payload"]
    expected_b52 = a["b5_2b_positive_branch_corroboration_only"]
    if b52.get("admission_review_id") != expected_b52["review_id"] or b52.get("exact_proof_head") != expected_b52["proof_head"]:
        raise AssertionError("B5.2B positive authority")
    if b5_2b_receipt.get("semantic_digest") != expected_b52["receipt_semantic_digest"] or dg(b52) != expected_b52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B corrected receipt semantic digest")
    if b52["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B positive branch statement")

    return {
        "b5_1_closed_trace_authority": True,
        "general_root_full_set_identity_authority": True,
        "o7_empty_boundary_biconditional_authority": True,
        "positive_branch_corroboration_bound": True,
        "positive_branch_used_as_negative_proof_premise": False,
        "superseded_bad_b5_2b_receipt_used": False,
    }


def build(spec: dict, b5_1: dict, b5_1_receipt: dict, composition: dict, o7: dict, b5_2b_receipt: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.3 spec")
    if b5_1.get("schema") != B5_1_SCHEMA:
        raise AssertionError("B5.1 artifact schema")
    if b5_1.get("semantic_digest_scope") != "proof_payload" or b5_1.get("semantic_digest") != dg(b5_1["proof_payload"]):
        raise AssertionError("B5.1 artifact semantic digest")

    authority = verify_authority(spec, b5_1_receipt, composition, o7, b5_2b_receipt)
    q = b5_1["proof_payload"]
    status = q.get("capability_status")
    root_count = q.get("root_entry_count_if_closed")
    base = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "b5_1_semantic_digest": b5_1["semantic_digest"],
        "ambient_dim": q["ambient_dim"],
        "k": q["k"],
        "canonical_factor_catalog": q["canonical_factor_catalog"],
        "canonical_tree": q["canonical_tree"],
        "root_id": q["root_id"],
        "b5_1_capability_status": status,
        "root_full_set_digest_if_closed": q.get("root_full_set_digest_if_closed"),
        "root_entry_count_if_closed": root_count,
        "authority_bindings": authority,
        "layout_domain": {
            "whole_factor_units": True,
            "exact_factor_catalog_digest": dg(q["canonical_factor_catalog"]),
            "affine_offsets_preserved_as_identity_only": True,
            "affine_offsets_used_in_width_theorem": False,
            "width_definition": "MAX_CUT_DIM_PREFIX_SPAN_INTER_SUFFIX_SPAN",
        },
        "proof_policy": {
            "layout_enumeration_used": False,
            "target_layout_count_used": None,
            "root_empty_count_used_as_only_reason": False,
            "required_authority_bridge": "B5_1_COMPLETE_TRACE_PLUS_GENERAL_COMPOSITION_PLUS_O7",
            "b5_2b_positive_receipt_role": "CORROBORATION_ONLY_NOT_NEGATIVE_PREMISE",
        },
    }

    if status == "OPEN_RUNTIME_CAPABILITY":
        if root_count is not None or q.get("terminal_promotion") != "NONE":
            raise AssertionError("OPEN B5.1 subject has terminal/root result")
        base.update({
            "terminal_branch": "NOT_APPLICABLE_OPEN_RUNTIME",
            "composition_chain": {
                "b5_1_closed_complete_trace": False,
                "engine_root_equals_fs_k_v_zero": False,
                "root_full_set_empty": False,
                "o7_biconditional_bound": True,
                "contradiction_closed": False,
            },
            "candidate_no_layout_at_cap": False,
            "no_layout_promotion": "FORBIDDEN_OPEN_RUNTIME",
            "candidate_found_layout": False,
            "affine_instance_unsat": "NOT_ESTABLISHED",
            "c047_result": "NOT_ESTABLISHED_PENDING_B5_4",
            "strict_boundary": spec["strict_boundary"],
        })
    elif status == "CLOSED_COMPLETE_TRACE":
        if root_count is None or q.get("terminal_promotion") != "NONE":
            raise AssertionError("CLOSED B5.1 subject root/terminal fields")
        if int(root_count) == 0:
            base.update({
                "terminal_branch": "NO_LAYOUT_CANDIDATE_PENDING_REVIEW",
                "composition_chain": {
                    "b5_1_closed_complete_trace": True,
                    "engine_root_equals_fs_k_v_zero": True,
                    "root_full_set_empty": True,
                    "fs_k_v_zero_empty": True,
                    "o7_biconditional_bound": True,
                    "assume_layout_width_le_k_implies_fs_nonempty": True,
                    "contradiction_closed": True,
                    "conclusion": "NO_COMPLETE_WHOLE_FACTOR_LINEAR_LAYOUT_OF_EXACT_INPUT_NORMAL_SPACE_ARRANGEMENT_HAS_WIDTH_LE_K",
                },
                "candidate_no_layout_at_cap": True,
                "no_layout_promotion": "FORBIDDEN_PENDING_B5_3_EXACT_HEAD_CI_AND_REVIEW",
                "candidate_found_layout": False,
                "affine_instance_unsat": "NOT_ESTABLISHED",
                "c047_result": "NOT_ESTABLISHED_PENDING_B5_4",
                "strict_boundary": spec["strict_boundary"],
            })
        else:
            base.update({
                "terminal_branch": "NOT_APPLICABLE_NONEMPTY_ROOT",
                "composition_chain": {
                    "b5_1_closed_complete_trace": True,
                    "engine_root_equals_fs_k_v_zero": True,
                    "root_full_set_empty": False,
                    "o7_biconditional_bound": True,
                    "contradiction_closed": False,
                },
                "candidate_no_layout_at_cap": False,
                "no_layout_promotion": "FORBIDDEN_NONEMPTY_ROOT",
                "candidate_found_layout": False,
                "positive_branch": "DEFER_TO_SEPARATELY_ADMITTED_B5_2B",
                "affine_instance_unsat": "NOT_ESTABLISHED",
                "c047_result": "NOT_ESTABLISHED_PENDING_B5_4",
                "strict_boundary": spec["strict_boundary"],
            })
    else:
        raise AssertionError("unknown B5.1 capability status")

    out = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": base}
    out["semantic_digest"] = dg(base)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--b5-1-artifact", type=Path, required=True)
    p.add_argument("--b5-1-admission", type=Path, required=True)
    p.add_argument("--composition-audit", type=Path, required=True)
    p.add_argument("--o7-audit", type=Path, required=True)
    p.add_argument("--b5-2b-admission", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    artifact = build(load(a.spec), load(a.b5_1_artifact), load(a.b5_1_admission), load(a.composition_audit), load(a.o7_audit), load(a.b5_2b_admission))
    save(artifact, a.output)
    q = artifact["proof_payload"]
    print("JANUS_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION = PASS")
    print("B5_1_CAPABILITY_STATUS =", q["b5_1_capability_status"])
    print("ROOT_ENTRY_COUNT_IF_CLOSED =", q["root_entry_count_if_closed"])
    print("TERMINAL_BRANCH =", q["terminal_branch"])
    print("GENERAL_ROOT_FULL_SET_IDENTITY_AUTHORITY = PASS")
    print("O7_EMPTY_BOUNDARY_BICONDITIONAL_AUTHORITY = PASS")
    print("LAYOUT_ENUMERATION_USED = FALSE")
    print("B5_2B_POSITIVE_RECEIPT_USED_AS_NEGATIVE_PREMISE = FALSE")
    print("CANDIDATE_NO_LAYOUT_AT_CAP =", str(q["candidate_no_layout_at_cap"]).upper())
    print("NO_LAYOUT_PROMOTION =", q["no_layout_promotion"])
    print("AFFINE_INSTANCE_UNSAT = NOT_ESTABLISHED")
    print("C047_RESULT = NOT_ESTABLISHED_PENDING_B5_4")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
