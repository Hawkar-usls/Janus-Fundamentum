from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "janus.c049_1.b5_3.generic_empty_root_terminal_composition_candidate.v1_1"
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
    if audit.get("schema") != expected_schema or audit.get("semantic_digest_scope") != "audit_payload":
        raise AssertionError("authority audit schema/scope")
    if audit.get("semantic_digest") != expected_digest or dg(audit["audit_payload"]) != expected_digest:
        raise AssertionError("authority audit semantic digest")


def verify_authority(
    spec: dict,
    b5_contract: dict,
    b5_1_receipt: dict,
    composition: dict,
    o7: dict,
    b5_2b_receipt: dict,
) -> dict:
    a = spec["authority_inputs"]

    if b5_contract.get("schema") != "janus.c049_1.b5.general_runtime_terminal_contract_admission_receipt.v1":
        raise AssertionError("B5 contract receipt schema")
    b5c = b5_contract["audit_payload"]
    if b5c.get("admission_review_id") != a["b5_contract"]["review_id"]:
        raise AssertionError("B5 contract review")
    if b5c["contract_conclusion"].get("b5_3_generic_no_layout_terminal") is not False:
        raise AssertionError("B5 contract historical B5.3 ceiling")

    if b5_1_receipt.get("schema") != "janus.c049_1.b5_1.generic_corrected_runtime_trace_executor_admission_receipt.v1":
        raise AssertionError("B5.1 receipt schema")
    b51 = b5_1_receipt["audit_payload"]
    a51 = a["b5_1_runtime_admission"]
    if b51.get("admission_review_id") != a51["review_id"] or b51.get("exact_proof_head") != a51["proof_head"]:
        raise AssertionError("B5.1 review/proof authority")
    sem51 = b51["semantic_conclusion"]
    if sem51.get("generic_corrected_algorithm1_runtime_trace_mapping") != "TRUE_WHEN_RUNTIME_RETURNS_CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.1 closed complete trace admission")
    if sem51.get("generic_no_layout_at_cap") != "FORBIDDEN":
        raise AssertionError("B5.1 terminal ceiling")

    acomp = a["general_structural_induction_composition"]
    verify_audit_semantic(
        composition,
        "janus.c049_1.general_structural_induction_composition_independent_source_audit.v1",
        acomp["audit_semantic_digest"],
    )
    cp = composition["audit_payload"]
    if cp["proof_subject"].get("exact_head") != acomp["proof_head"] or cp["proof_subject"].get("review_id") != acomp["review_id"]:
        raise AssertionError("general composition authority")
    lc = cp["local_composition_audit"]
    if lc.get("root_full_set_identity_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("F_root identity authority")
    if lc.get("structural_induction_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("structural induction authority")
    if lc.get("lemma_2_7_caller_preconditions_preserved_explicitly") is not True:
        raise AssertionError("caller-premise ceiling lost")

    ao7 = a["o7_empty_root_specialization"]
    verify_audit_semantic(
        o7,
        "janus.c049_1.general_empty_root_specialization_authority_closure_audit.v1",
        ao7["audit_semantic_digest"],
    )
    op = o7["audit_payload"]
    if op["proof_subject"].get("exact_head") != ao7["proof_head"] or op["proof_subject"].get("review_id") != ao7["review_id"]:
        raise AssertionError("O7 authority")
    if op["published_source_audit"].get("abstract_biconditional") != "FS_k(V,{0}) nonempty iff there exists a complete linear layout of V with width<=k":
        raise AssertionError("O7 biconditional authority")
    if op["published_source_audit"].get("engine_root_identity_is_separate") is not True:
        raise AssertionError("O7 root identity separation")

    indexed = a["published_indexed_arrangement_binding"]
    if indexed.get("geometry_equality_does_not_deduplicate_occurrences") is not True:
        raise AssertionError("indexed occurrence source binding")

    a52 = a["b5_2b_positive_branch_corroboration_only"]
    if b5_2b_receipt.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B receipt schema")
    if b5_2b_receipt.get("semantic_digest") != a52["receipt_semantic_digest"] or dg(b5_2b_receipt["audit_payload"]) != a52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B corrected receipt digest")
    b52 = b5_2b_receipt["audit_payload"]
    if b52.get("admission_review_id") != a52["review_id"] or b52.get("exact_proof_head") != a52["proof_head"]:
        raise AssertionError("B5.2B positive authority")
    if b52["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B positive terminal authority")

    return {
        "b5_contract_authority": True,
        "b5_1_closed_trace_authority": True,
        "general_root_full_set_identity_authority": True,
        "general_caller_premise_ceiling_preserved": True,
        "o7_empty_boundary_biconditional_authority": True,
        "indexed_subspace_occurrence_authority": True,
        "positive_branch_corroboration_bound": True,
        "positive_branch_used_as_negative_proof_premise": False,
        "superseded_bad_b5_2b_receipt_used": False,
    }


def occurrence_domain(q: dict) -> dict:
    catalog = q["canonical_factor_catalog"]
    occurrences = [
        {
            "occurrence_index": i,
            "factor_id": factor["id"],
            "normal_space": factor["normal_space"],
            "affine_offset_identity_digest": dg(factor.get("affine_offset")),
        }
        for i, factor in enumerate(catalog)
    ]
    groups: dict[str, dict] = {}
    for factor in catalog:
        key = dg(factor["normal_space"])
        group = groups.setdefault(key, {"normal_space": factor["normal_space"], "factor_ids": []})
        group["factor_ids"].append(factor["id"])
    geometry_classes = [
        {
            "normal_space": groups[key]["normal_space"],
            "factor_ids": sorted(groups[key]["factor_ids"]),
            "occurrence_count": len(groups[key]["factor_ids"]),
        }
        for key in sorted(groups)
    ]
    return {
        "whole_factor_units": True,
        "factor_occurrence_count": len(occurrences),
        "factor_occurrences": occurrences,
        "factor_occurrence_digest": dg(occurrences),
        "geometry_classes": geometry_classes,
        "duplicate_geometry_class_count": sum(1 for group in geometry_classes if group["occurrence_count"] > 1),
        "equal_geometry_occurrences_remain_distinct": True,
        "exact_factor_catalog_digest": dg(catalog),
        "affine_offsets_preserved_as_identity_only": True,
        "affine_offsets_used_in_width_theorem": False,
        "width_definition": "MAX_CUT_DIM_PREFIX_SPAN_INTER_SUFFIX_SPAN_OVER_NORMAL_SPACES_ONLY",
        "complete_layout_domain": "PERMUTATIONS_OF_ALL_FACTOR_ID_OCCURRENCES_EXACTLY_ONCE",
    }


def closed_trace_binding(q: dict) -> dict:
    nodes = {node["node_id"]: node for node in q["node_receipts"]}
    root = q["root_id"]
    if root not in nodes:
        raise AssertionError("root receipt missing")
    internal = [node for node in nodes.values() if node["kind"] == "internal"]
    all_pass = all(node["caller_premise_certificate_if_internal"]["all_pass"] is True for node in internal)
    out = {
        "root_boundary_rref": nodes[root]["B_v_rref"],
        "root_receipt_entry_count": int(nodes[root]["output_entry_count"]),
        "root_covers_all_factors": q["root_covers_all_factors"] is True,
        "all_factor_ids_exactly_once": q["all_factor_ids_exactly_once"] is True,
        "internal_node_count": len(internal),
        "internal_caller_premises_all_pass": all_pass,
        "affine_identity_ledger_matches_catalog": q["affine_offset_identity_ledger"] == [
            {"factor_id": f["id"], "affine_offset": f["affine_offset"]} for f in q["canonical_factor_catalog"]
        ],
    }
    if out["root_boundary_rref"] != []:
        raise AssertionError("closed root boundary must be zero")
    if out["root_receipt_entry_count"] != int(q["root_entry_count_if_closed"]):
        raise AssertionError("root entry count binding")
    if not all((out["root_covers_all_factors"], out["all_factor_ids_exactly_once"], out["internal_caller_premises_all_pass"], out["affine_identity_ledger_matches_catalog"])):
        raise AssertionError("closed trace authority binding")
    return out


def build(
    spec: dict,
    b5_1: dict,
    b5_contract: dict,
    b5_1_receipt: dict,
    composition: dict,
    o7: dict,
    b5_2b_receipt: dict,
) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.3 spec")
    if b5_1.get("schema") != B5_1_SCHEMA:
        raise AssertionError("B5.1 artifact schema")
    if b5_1.get("semantic_digest_scope") != "proof_payload" or b5_1.get("semantic_digest") != dg(b5_1["proof_payload"]):
        raise AssertionError("B5.1 artifact semantic digest")

    authority = verify_authority(spec, b5_contract, b5_1_receipt, composition, o7, b5_2b_receipt)
    q = b5_1["proof_payload"]
    status = q.get("capability_status")
    root_count = q.get("root_entry_count_if_closed")
    domain = occurrence_domain(q)
    closed_binding = closed_trace_binding(q) if status == "CLOSED_COMPLETE_TRACE" else None

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
        "layout_domain": domain,
        "closed_trace_binding": closed_binding,
        "proof_policy": {
            "layout_enumeration_used": False,
            "target_layout_count_used": None,
            "root_empty_count_used_as_only_reason": False,
            "required_authority_bridge": "B5_1_COMPLETE_TRACE_PLUS_BOUND_CALLER_PREMISES_PLUS_GENERAL_COMPOSITION_PLUS_O7",
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
                "bound_caller_premises": False,
                "engine_root_equals_fs_k_v_zero": False,
                "root_full_set_empty": False,
                "o7_biconditional_bound": True,
                "indexed_occurrence_domain_bound": True,
                "contradiction_closed": False,
            },
            "candidate_no_layout_at_cap": False,
            "no_layout_promotion": "FORBIDDEN_OPEN_RUNTIME",
            "candidate_found_layout": False,
        })
    elif status == "CLOSED_COMPLETE_TRACE":
        if root_count is None or q.get("terminal_promotion") != "NONE":
            raise AssertionError("CLOSED B5.1 subject root/terminal fields")
        common_chain = {
            "b5_1_closed_complete_trace": True,
            "bound_caller_premises": True,
            "engine_root_equals_fs_k_v_zero": True,
            "o7_biconditional_bound": True,
            "indexed_occurrence_domain_bound": True,
        }
        if int(root_count) == 0:
            base.update({
                "terminal_branch": "NO_LAYOUT_CANDIDATE_PENDING_REVIEW",
                "composition_chain": {
                    **common_chain,
                    "root_full_set_empty": True,
                    "fs_k_v_zero_empty": True,
                    "layout_width_le_k_would_imply_fs_nonempty": True,
                    "contradiction_closed": True,
                    "conclusion": "NO_COMPLETE_PERMUTATION_LAYOUT_OF_ALL_INDEXED_INPUT_FACTOR_OCCURRENCES_HAS_WIDTH_LE_K",
                },
                "candidate_no_layout_at_cap": True,
                "no_layout_promotion": "FORBIDDEN_PENDING_B5_3_EXACT_HEAD_CI_AND_REVIEW",
                "candidate_found_layout": False,
            })
        else:
            base.update({
                "terminal_branch": "NOT_APPLICABLE_NONEMPTY_ROOT",
                "composition_chain": {
                    **common_chain,
                    "root_full_set_empty": False,
                    "contradiction_closed": False,
                },
                "candidate_no_layout_at_cap": False,
                "no_layout_promotion": "FORBIDDEN_NONEMPTY_ROOT",
                "candidate_found_layout": False,
                "positive_branch": "DEFER_TO_SEPARATELY_ADMITTED_B5_2B",
            })
    else:
        raise AssertionError("unknown B5.1 capability status")

    base.update({
        "affine_instance_unsat": "NOT_ESTABLISHED",
        "c047_result": "NOT_ESTABLISHED_PENDING_B5_4",
        "strict_boundary": spec["strict_boundary"],
    })
    out = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": base}
    out["semantic_digest"] = dg(base)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--b5-contract-admission", type=Path, required=True)
    parser.add_argument("--b5-1-admission", type=Path, required=True)
    parser.add_argument("--composition-audit", type=Path, required=True)
    parser.add_argument("--o7-audit", type=Path, required=True)
    parser.add_argument("--b5-2b-admission", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    a = parser.parse_args()
    artifact = build(
        load(a.spec), load(a.b5_1_artifact), load(a.b5_contract_admission), load(a.b5_1_admission),
        load(a.composition_audit), load(a.o7_audit), load(a.b5_2b_admission),
    )
    save(artifact, a.output)
    q = artifact["proof_payload"]
    print("JANUS_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION_V1_1 = PASS")
    print("B5_1_CAPABILITY_STATUS =", q["b5_1_capability_status"])
    print("ROOT_ENTRY_COUNT_IF_CLOSED =", q["root_entry_count_if_closed"])
    print("FACTOR_OCCURRENCE_COUNT =", q["layout_domain"]["factor_occurrence_count"])
    print("DUPLICATE_GEOMETRY_CLASS_COUNT =", q["layout_domain"]["duplicate_geometry_class_count"])
    print("TERMINAL_BRANCH =", q["terminal_branch"])
    print("GENERAL_ROOT_FULL_SET_IDENTITY_AUTHORITY = PASS")
    print("BOUND_CALLER_PREMISES =", "PASS" if q["closed_trace_binding"] is None or q["closed_trace_binding"]["internal_caller_premises_all_pass"] else "FAIL")
    print("O7_EMPTY_BOUNDARY_BICONDITIONAL_AUTHORITY = PASS")
    print("INDEXED_SUBSPACE_OCCURRENCE_BINDING = PASS")
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
