from __future__ import annotations

import argparse
import copy
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


def verify_audit_semantic(audit: dict, schema: str, digest: str) -> None:
    if audit.get("schema") != schema or audit.get("semantic_digest_scope") != "audit_payload":
        raise AssertionError("authority audit schema/scope")
    if audit.get("semantic_digest") != digest or dg(audit["audit_payload"]) != digest:
        raise AssertionError("authority audit semantic digest")


def independent_authority(spec: dict, b5c_receipt: dict, b51_receipt: dict, comp: dict, o7: dict, b52_receipt: dict) -> dict:
    a = spec["authority_inputs"]

    if b5c_receipt.get("schema") != "janus.c049_1.b5.general_runtime_terminal_contract_admission_receipt.v1":
        raise AssertionError("B5 contract receipt schema")
    b5c = b5c_receipt["audit_payload"]
    if b5c.get("admission_review_id") != a["b5_contract"]["review_id"]:
        raise AssertionError("B5 contract review")
    if b5c["contract_conclusion"].get("b5_3_generic_no_layout_terminal") is not False:
        raise AssertionError("B5 contract old B5.3 ceiling")

    if b51_receipt.get("schema") != "janus.c049_1.b5_1.generic_corrected_runtime_trace_executor_admission_receipt.v1":
        raise AssertionError("B5.1 receipt schema")
    b51r = b51_receipt["audit_payload"]
    a51 = a["b5_1_runtime_admission"]
    if b51r.get("admission_review_id") != a51["review_id"] or b51r.get("exact_proof_head") != a51["proof_head"]:
        raise AssertionError("B5.1 authority")
    s51 = b51r["semantic_conclusion"]
    if s51.get("generic_corrected_algorithm1_runtime_trace_mapping") != "TRUE_WHEN_RUNTIME_RETURNS_CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.1 closed trace statement")
    if s51.get("generic_no_layout_at_cap") != "FORBIDDEN":
        raise AssertionError("B5.1 negative ceiling")

    ac = a["general_structural_induction_composition"]
    verify_audit_semantic(comp, "janus.c049_1.general_structural_induction_composition_independent_source_audit.v1", ac["audit_semantic_digest"])
    cp = comp["audit_payload"]
    if cp["proof_subject"].get("exact_head") != ac["proof_head"] or cp["proof_subject"].get("review_id") != ac["review_id"]:
        raise AssertionError("general composition authority")
    local = cp["local_composition_audit"]
    if local.get("root_full_set_identity_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("root equality authority")
    if local.get("structural_induction_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("structural induction authority")
    if local.get("lemma_2_7_caller_preconditions_preserved_explicitly") is not True:
        raise AssertionError("caller premise conditional lost")

    ao = a["o7_empty_root_specialization"]
    verify_audit_semantic(o7, "janus.c049_1.general_empty_root_specialization_authority_closure_audit.v1", ao["audit_semantic_digest"])
    op = o7["audit_payload"]
    if op["proof_subject"].get("exact_head") != ao["proof_head"] or op["proof_subject"].get("review_id") != ao["review_id"]:
        raise AssertionError("O7 authority")
    if op["published_source_audit"].get("abstract_biconditional") != "FS_k(V,{0}) nonempty iff there exists a complete linear layout of V with width<=k":
        raise AssertionError("O7 biconditional")
    if op["published_source_audit"].get("engine_root_identity_is_separate") is not True:
        raise AssertionError("O7 engine separation")

    indexed = a["published_indexed_arrangement_binding"]
    if indexed.get("geometry_equality_does_not_deduplicate_occurrences") is not True:
        raise AssertionError("indexed subspace occurrence binding")

    a52 = a["b5_2b_positive_branch_corroboration_only"]
    if b52_receipt.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B receipt schema")
    if b52_receipt.get("semantic_digest") != a52["receipt_semantic_digest"] or dg(b52_receipt["audit_payload"]) != a52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B receipt semantic digest")
    b52 = b52_receipt["audit_payload"]
    if b52.get("admission_review_id") != a52["review_id"] or b52.get("exact_proof_head") != a52["proof_head"]:
        raise AssertionError("B5.2B authority")
    if b52["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B positive branch")

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


def independent_domain(q: dict) -> dict:
    catalog = q["canonical_factor_catalog"]
    ids = [factor["id"] for factor in catalog]
    if len(ids) != len(set(ids)):
        raise AssertionError("factor IDs not unique")
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
        groups.setdefault(key, {"normal_space": factor["normal_space"], "factor_ids": []})["factor_ids"].append(factor["id"])
    geometry_classes = [
        {"normal_space": groups[key]["normal_space"], "factor_ids": sorted(groups[key]["factor_ids"]), "occurrence_count": len(groups[key]["factor_ids"])}
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


def independent_closed_binding(q: dict) -> dict:
    nodes = {node["node_id"]: node for node in q["node_receipts"]}
    root = q["root_id"]
    if root not in nodes:
        raise AssertionError("root receipt")
    internals = [node for node in nodes.values() if node["kind"] == "internal"]
    all_pass = all(node["caller_premise_certificate_if_internal"]["all_pass"] is True for node in internals)
    result = {
        "root_boundary_rref": nodes[root]["B_v_rref"],
        "root_receipt_entry_count": int(nodes[root]["output_entry_count"]),
        "root_covers_all_factors": q["root_covers_all_factors"] is True,
        "all_factor_ids_exactly_once": q["all_factor_ids_exactly_once"] is True,
        "internal_node_count": len(internals),
        "internal_caller_premises_all_pass": all_pass,
        "affine_identity_ledger_matches_catalog": q["affine_offset_identity_ledger"] == [
            {"factor_id": f["id"], "affine_offset": f["affine_offset"]} for f in q["canonical_factor_catalog"]
        ],
    }
    if result["root_boundary_rref"] != []:
        raise AssertionError("root boundary")
    if result["root_receipt_entry_count"] != int(q["root_entry_count_if_closed"]):
        raise AssertionError("root count")
    if not all((result["root_covers_all_factors"], result["all_factor_ids_exactly_once"], result["internal_caller_premises_all_pass"], result["affine_identity_ledger_matches_catalog"])):
        raise AssertionError("closed trace binding")
    return result


def expected_payload(spec: dict, b51: dict, authority: dict) -> dict:
    q = b51["proof_payload"]
    status = q["capability_status"]
    root_count = q.get("root_entry_count_if_closed")
    domain = independent_domain(q)
    closed = independent_closed_binding(q) if status == "CLOSED_COMPLETE_TRACE" else None
    base = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "b5_1_semantic_digest": b51["semantic_digest"],
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
        "closed_trace_binding": closed,
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
            raise AssertionError("invalid OPEN subject")
        base.update({
            "terminal_branch": "NOT_APPLICABLE_OPEN_RUNTIME",
            "composition_chain": {"b5_1_closed_complete_trace": False, "bound_caller_premises": False, "engine_root_equals_fs_k_v_zero": False, "root_full_set_empty": False, "o7_biconditional_bound": True, "indexed_occurrence_domain_bound": True, "contradiction_closed": False},
            "candidate_no_layout_at_cap": False,
            "no_layout_promotion": "FORBIDDEN_OPEN_RUNTIME",
            "candidate_found_layout": False,
        })
    elif status == "CLOSED_COMPLETE_TRACE":
        if root_count is None or q.get("terminal_promotion") != "NONE":
            raise AssertionError("invalid CLOSED subject")
        common = {"b5_1_closed_complete_trace": True, "bound_caller_premises": True, "engine_root_equals_fs_k_v_zero": True, "o7_biconditional_bound": True, "indexed_occurrence_domain_bound": True}
        if int(root_count) == 0:
            base.update({
                "terminal_branch": "NO_LAYOUT_CANDIDATE_PENDING_REVIEW",
                "composition_chain": {**common, "root_full_set_empty": True, "fs_k_v_zero_empty": True, "layout_width_le_k_would_imply_fs_nonempty": True, "contradiction_closed": True, "conclusion": "NO_COMPLETE_PERMUTATION_LAYOUT_OF_ALL_INDEXED_INPUT_FACTOR_OCCURRENCES_HAS_WIDTH_LE_K"},
                "candidate_no_layout_at_cap": True,
                "no_layout_promotion": "FORBIDDEN_PENDING_B5_3_EXACT_HEAD_CI_AND_REVIEW",
                "candidate_found_layout": False,
            })
        else:
            base.update({
                "terminal_branch": "NOT_APPLICABLE_NONEMPTY_ROOT",
                "composition_chain": {**common, "root_full_set_empty": False, "contradiction_closed": False},
                "candidate_no_layout_at_cap": False,
                "no_layout_promotion": "FORBIDDEN_NONEMPTY_ROOT",
                "candidate_found_layout": False,
                "positive_branch": "DEFER_TO_SEPARATELY_ADMITTED_B5_2B",
            })
    else:
        raise AssertionError("unknown B5.1 status")
    base.update({"affine_instance_unsat": "NOT_ESTABLISHED", "c047_result": "NOT_ESTABLISHED_PENDING_B5_4", "strict_boundary": spec["strict_boundary"]})
    return base


def verify(candidate: dict, spec: dict, b51: dict, b5c: dict, b51r: dict, comp: dict, o7: dict, b52r: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.3 spec")
    if b51.get("schema") != B5_1_SCHEMA or b51.get("semantic_digest_scope") != "proof_payload" or b51.get("semantic_digest") != dg(b51["proof_payload"]):
        raise AssertionError("B5.1 artifact")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or candidate.get("semantic_digest") != dg(candidate["proof_payload"]):
        raise AssertionError("B5.3 candidate")
    authority = independent_authority(spec, b5c, b51r, comp, o7, b52r)
    expected = expected_payload(spec, b51, authority)
    if candidate["proof_payload"] != expected:
        raise AssertionError("candidate differs from independent composition")
    return expected


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def repair_audit(audit: dict) -> dict:
    if audit.get("semantic_digest_scope") == "audit_payload":
        audit["semantic_digest"] = dg(audit["audit_payload"])
    return audit


def tamper_suite(empty_candidate: dict, nonempty_candidate: dict, open_candidate: dict, spec: dict, empty_b51: dict, nonempty_b51: dict, open_b51: dict, b5c: dict, b51r: dict, comp: dict, o7: dict, b52r: dict) -> tuple[int, int]:
    attacks = []

    def add(name, candidate, subject, mutation):
        c = copy.deepcopy(candidate); s = copy.deepcopy(subject); bc = copy.deepcopy(b5c); r = copy.deepcopy(b51r); co = copy.deepcopy(comp); oo = copy.deepcopy(o7); r52 = copy.deepcopy(b52r)
        mutation(c, s, bc, r, co, oo, r52)
        repair(c); repair_audit(co); repair_audit(oo)
        if r52.get("semantic_digest_scope") == "audit_payload": r52["semantic_digest"] = dg(r52["audit_payload"])
        attacks.append((name, c, s, bc, r, co, oo, r52))

    add("T01_B5_1_SEMANTIC_BINDING", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"].__setitem__("b5_1_semantic_digest", "0"*64))
    add("T02_B5_1_PROOF_REVIEW", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: r["audit_payload"].__setitem__("admission_review_id", 0))
    add("T03_GENERAL_COMP_REVIEW", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: co["audit_payload"]["proof_subject"].__setitem__("review_id", 0))
    add("T04_GENERAL_COMP_SEMANTIC", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: co["audit_payload"]["local_composition_audit"].__setitem__("root_full_set_identity_for_complete_algorithm1_compatible_trace_supported", False))
    add("T05_O7_REVIEW", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: oo["audit_payload"]["proof_subject"].__setitem__("review_id", 0))
    add("T06_O7_BICONDITIONAL", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: oo["audit_payload"]["published_source_audit"].__setitem__("abstract_biconditional", "ONE_WAY_ONLY"))
    add("T07_ROOT_IDENTITY_WEAKEN", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["composition_chain"].__setitem__("engine_root_equals_fs_k_v_zero", "SUBSET_ONLY"))
    add("T08_O7_ONE_WAY", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["composition_chain"].__setitem__("o7_biconditional_bound", False))
    add("T09_EMPTY_ON_NONEMPTY", nonempty_candidate, nonempty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"].update({"terminal_branch":"NO_LAYOUT_CANDIDATE_PENDING_REVIEW","candidate_no_layout_at_cap":True}))
    add("T10_NO_LAYOUT_ON_OPEN", open_candidate, open_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"].update({"terminal_branch":"NO_LAYOUT_CANDIDATE_PENDING_REVIEW","candidate_no_layout_at_cap":True}))
    add("T11_ENUMERATION_PREMISE", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["proof_policy"].update({"layout_enumeration_used":True,"target_layout_count_used":720}))
    add("T12_ROOT_COUNT_ONLY", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["proof_policy"].update({"root_empty_count_used_as_only_reason":True,"required_authority_bridge":"NONE"}))
    add("T13_DROP_FACTOR", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["layout_domain"]["factor_occurrences"].pop())
    add("T14_AFFINE_AS_WIDTH", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["layout_domain"].update({"affine_offsets_used_in_width_theorem":True,"width_definition":"USES_AFFINE_OFFSETS"}))
    add("T15_AFFINE_UNSAT", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"].__setitem__("affine_instance_unsat","TRUE"))
    add("T16_C047_RESULT", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"].__setitem__("c047_result","UNSAT"))
    add("T17_RUNTIME_COMPLEXITY", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["strict_boundary"].update({"all_input_termination":"ESTABLISHED","polynomial_runtime":"ESTABLISHED"}))
    add("T18_GLOBAL_PROMOTION", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["strict_boundary"].update({"b5_complete":True,"arbitrary_input_global_engine_theorem":True,"p_vs_np":"CLOSED"}))
    add("T19_B5_2B_NEGATIVE_PREMISE", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["authority_bindings"].__setitem__("positive_branch_used_as_negative_proof_premise",True))
    add("T20_SUPERSEDED_B5_2B", empty_candidate, empty_b51, lambda c,s,bc,r,co,oo,r52: c["proof_payload"]["authority_bindings"].__setitem__("superseded_bad_b5_2b_receipt_used",True))

    def collapse_occurrence(c,s,bc,r,co,oo,r52):
        domain = c["proof_payload"]["layout_domain"]
        if domain["factor_occurrence_count"] < 2: raise AssertionError("multiplicity fixture missing")
        domain["factor_occurrences"] = domain["factor_occurrences"][:1]
        domain["factor_occurrence_count"] = 1
        domain["equal_geometry_occurrences_remain_distinct"] = False
    add("T21_COLLAPSE_EQUAL_GEOMETRY_OCCURRENCES", empty_candidate, empty_b51, collapse_occurrence)

    def caller_root(c,s,bc,r,co,oo,r52):
        binding = c["proof_payload"]["closed_trace_binding"]
        binding["internal_caller_premises_all_pass"] = False
        binding["root_boundary_rref"] = [1]
    add("T22_CALLER_OR_ROOT_ZERO", empty_candidate, empty_b51, caller_root)

    rejected = 0
    for name, c, subject, bc, r, co, oo, r52 in attacks:
        try:
            verify(c, spec, subject, bc, r, co, oo, r52)
        except Exception:
            rejected += 1
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--b5-1-artifact", type=Path, required=True)
    p.add_argument("--b5-contract-admission", type=Path, required=True)
    p.add_argument("--b5-1-admission", type=Path, required=True)
    p.add_argument("--composition-audit", type=Path, required=True)
    p.add_argument("--o7-audit", type=Path, required=True)
    p.add_argument("--b5-2b-admission", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--tamper-suite", action="store_true")
    p.add_argument("--nonempty-b5-1", type=Path)
    p.add_argument("--nonempty-candidate", type=Path)
    p.add_argument("--open-b5-1", type=Path)
    p.add_argument("--open-candidate", type=Path)
    a = p.parse_args()
    spec=load(a.spec); b51=load(a.b5_1_artifact); b5c=load(a.b5_contract_admission); b51r=load(a.b5_1_admission); comp=load(a.composition_audit); o7=load(a.o7_audit); b52=load(a.b5_2b_admission); cand=load(a.candidate)
    out = verify(cand,spec,b51,b5c,b51r,comp,o7,b52)
    print("JANUS_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_INDEPENDENT_VERIFIER_V1_1 = PASS")
    print("TERMINAL_BRANCH =", out["terminal_branch"])
    print("INDEXED_SUBSPACE_OCCURRENCE_BINDING = PASS")
    print("FACTOR_OCCURRENCE_COUNT =", out["layout_domain"]["factor_occurrence_count"])
    print("DUPLICATE_GEOMETRY_CLASS_COUNT =", out["layout_domain"]["duplicate_geometry_class_count"])
    print("BOUND_CALLER_PREMISES = PASS" if out["closed_trace_binding"] is not None else "BOUND_CALLER_PREMISES = NOT_APPLICABLE_OPEN")
    print("ROOT_ZERO_BOUNDARY = PASS" if out["closed_trace_binding"] is not None else "ROOT_ZERO_BOUNDARY = NOT_APPLICABLE_OPEN")
    print("GENERAL_ROOT_FULL_SET_IDENTITY = PASS")
    print("O7_BICONDITIONAL = PASS")
    print("LAYOUT_ENUMERATION_USED = FALSE")
    print("B5_2B_POSITIVE_USED_AS_NEGATIVE_PREMISE = FALSE")
    print("AFFINE_INSTANCE_UNSAT = NOT_ESTABLISHED")
    print("C047_RESULT = NOT_ESTABLISHED_PENDING_B5_4")
    print("GENERIC_NO_LAYOUT_AT_CAP_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if a.tamper_suite:
        if not all((a.nonempty_b5_1,a.nonempty_candidate,a.open_b5_1,a.open_candidate)):
            raise AssertionError("tamper suite branch controls missing")
        rejected,total=tamper_suite(cand,load(a.nonempty_candidate),load(a.open_candidate),spec,b51,load(a.nonempty_b5_1),load(a.open_b5_1),b5c,b51r,comp,o7,b52)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
