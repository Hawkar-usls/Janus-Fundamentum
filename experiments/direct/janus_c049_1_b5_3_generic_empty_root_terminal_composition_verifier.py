from __future__ import annotations

import argparse
import copy
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


def verify_audit_semantic(audit: dict, schema: str, digest: str) -> None:
    if audit.get("schema") != schema or audit.get("semantic_digest_scope") != "audit_payload":
        raise AssertionError("authority audit schema/scope")
    if audit.get("semantic_digest") != digest or dg(audit["audit_payload"]) != digest:
        raise AssertionError("authority audit semantic digest")


def verify_authority(spec: dict, b51r: dict, comp: dict, o7: dict, b52r: dict) -> dict:
    authority = spec["authority_inputs"]
    if b51r.get("schema") != "janus.c049_1.b5_1.generic_corrected_runtime_trace_executor_admission_receipt.v1":
        raise AssertionError("B5.1 receipt schema")
    b51 = b51r["audit_payload"]
    a51 = authority["b5_1_runtime_admission"]
    if b51.get("admission_review_id") != a51["review_id"] or b51.get("exact_proof_head") != a51["proof_head"]:
        raise AssertionError("B5.1 review/proof authority")
    sem51 = b51["semantic_conclusion"]
    if sem51.get("generic_corrected_algorithm1_runtime_trace_mapping") != "TRUE_WHEN_RUNTIME_RETURNS_CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.1 closed complete trace admission")
    if sem51.get("generic_no_layout_at_cap") != "FORBIDDEN":
        raise AssertionError("B5.1 terminal ceiling")

    acomp = authority["general_structural_induction_composition"]
    verify_audit_semantic(comp, "janus.c049_1.general_structural_induction_composition_independent_source_audit.v1", acomp["audit_semantic_digest"])
    cp = comp["audit_payload"]
    if cp["proof_subject"].get("exact_head") != acomp["proof_head"] or cp["proof_subject"].get("review_id") != acomp["review_id"]:
        raise AssertionError("general composition authority")
    lc = cp["local_composition_audit"]
    if lc.get("root_full_set_identity_for_complete_algorithm1_compatible_trace_supported") is not True:
        raise AssertionError("F_root identity authority")
    if lc.get("algorithm1_compatible_trace_full_set_identity_supported") is not True:
        raise AssertionError("complete trace full-set identity authority")
    if cp["published_source_audit"].get("root") != "Proposition 5.8 specializes to V_root=V and B_root={0} before the terminal criterion.":
        raise AssertionError("root zero-boundary specialization")

    ao7 = authority["o7_empty_root_specialization"]
    verify_audit_semantic(o7, "janus.c049_1.general_empty_root_specialization_authority_closure_audit.v1", ao7["audit_semantic_digest"])
    op = o7["audit_payload"]
    if op["proof_subject"].get("exact_head") != ao7["proof_head"] or op["proof_subject"].get("review_id") != ao7["review_id"]:
        raise AssertionError("O7 authority")
    if op["published_source_audit"].get("abstract_biconditional") != "FS_k(V,{0}) nonempty iff there exists a complete linear layout of V with width<=k":
        raise AssertionError("O7 biconditional authority")
    if op["published_source_audit"].get("engine_root_identity_is_separate") is not True:
        raise AssertionError("O7 root identity separation")

    a52 = authority["b5_2b_positive_branch_corroboration_only"]
    if b52r.get("schema") != "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1":
        raise AssertionError("B5.2B receipt schema")
    if b52r.get("semantic_digest") != a52["receipt_semantic_digest"] or dg(b52r["audit_payload"]) != a52["receipt_semantic_digest"]:
        raise AssertionError("B5.2B corrected receipt digest")
    b52 = b52r["audit_payload"]
    if b52.get("admission_review_id") != a52["review_id"] or b52.get("exact_proof_head") != a52["proof_head"]:
        raise AssertionError("B5.2B positive review/proof authority")
    if b52["semantic_conclusion"].get("generic_found_layout") != "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY":
        raise AssertionError("B5.2B positive terminal authority")

    return {
        "b5_1_closed_trace_authority": True,
        "general_root_full_set_identity_authority": True,
        "o7_empty_boundary_biconditional_authority": True,
        "positive_branch_corroboration_bound": True,
        "positive_branch_used_as_negative_proof_premise": False,
        "superseded_bad_b5_2b_receipt_used": False,
    }


def expected_payload(spec: dict, b51: dict, authority: dict) -> dict:
    q = b51["proof_payload"]
    status = q.get("capability_status")
    root_count = q.get("root_entry_count_if_closed")
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
            raise AssertionError("invalid OPEN B5.1 subject")
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
            raise AssertionError("invalid CLOSED B5.1 subject")
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
    return base


def verify(candidate: dict, spec: dict, b51: dict, b51r: dict, comp: dict, o7: dict, b52r: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("B5.3 spec")
    if b51.get("schema") != B5_1_SCHEMA:
        raise AssertionError("B5.1 artifact schema")
    if b51.get("semantic_digest_scope") != "proof_payload" or b51.get("semantic_digest") != dg(b51["proof_payload"]):
        raise AssertionError("B5.1 semantic digest")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("B5.3 candidate schema/scope")
    if candidate.get("semantic_digest") != dg(candidate["proof_payload"]):
        raise AssertionError("B5.3 candidate semantic digest")

    authority = verify_authority(spec, b51r, comp, o7, b52r)
    expected = expected_payload(spec, b51, authority)
    if candidate["proof_payload"] != expected:
        raise AssertionError("B5.3 candidate differs from independently composed expected payload")
    return expected


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def repair_audit(audit: dict) -> dict:
    if audit.get("semantic_digest_scope") == "audit_payload":
        audit["semantic_digest"] = dg(audit["audit_payload"])
    return audit


def tamper_suite(
    empty_candidate: dict,
    nonempty_candidate: dict,
    open_candidate: dict,
    spec: dict,
    empty_b51: dict,
    nonempty_b51: dict,
    open_b51: dict,
    b51r: dict,
    comp: dict,
    o7: dict,
    b52r: dict,
) -> tuple[int, int]:
    attacks: list[tuple[str, dict, dict, dict, dict, dict, dict]] = []

    def add(name: str, candidate: dict, subject: dict, receipt: dict, caudit: dict, oaudit: dict, p52: dict, mutation) -> None:
        c = copy.deepcopy(candidate)
        r = copy.deepcopy(receipt)
        co = copy.deepcopy(caudit)
        oo = copy.deepcopy(oaudit)
        b52 = copy.deepcopy(p52)
        mutation(c, r, co, oo, b52)
        repair(c); repair_audit(co); repair_audit(oo)
        if b52.get("semantic_digest_scope") == "audit_payload":
            b52["semantic_digest"] = dg(b52["audit_payload"])
        attacks.append((name, c, subject, r, co, oo, b52))

    add("T01_B5_1_SEMANTIC_BINDING", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].__setitem__("b5_1_semantic_digest", "0"*64))
    add("T02_B5_1_PROOF_REVIEW", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: r["audit_payload"].__setitem__("admission_review_id", 0))
    add("T03_GENERAL_COMP_REVIEW", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: co["audit_payload"]["proof_subject"].__setitem__("review_id", 0))
    add("T04_GENERAL_COMP_SEMANTIC", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: co["audit_payload"]["local_composition_audit"].__setitem__("root_full_set_identity_for_complete_algorithm1_compatible_trace_supported", False))
    add("T05_O7_REVIEW", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: oo["audit_payload"]["proof_subject"].__setitem__("review_id", 0))
    add("T06_O7_SEMANTIC", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: oo["audit_payload"]["published_source_audit"].__setitem__("abstract_biconditional", "ONE_WAY_ONLY"))
    add("T07_ROOT_IDENTITY_WEAKEN", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["composition_chain"].__setitem__("engine_root_equals_fs_k_v_zero", "SUBSET_ONLY"))
    add("T08_O7_ONE_WAY", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["composition_chain"].__setitem__("o7_biconditional_bound", False))
    add("T09_EMPTY_ON_NONEMPTY", nonempty_candidate, nonempty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].update({"terminal_branch":"NO_LAYOUT_CANDIDATE_PENDING_REVIEW","candidate_no_layout_at_cap":True,"no_layout_promotion":"FORBIDDEN_PENDING_B5_3_EXACT_HEAD_CI_AND_REVIEW"}))
    add("T10_NO_LAYOUT_ON_OPEN", open_candidate, open_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].update({"terminal_branch":"NO_LAYOUT_CANDIDATE_PENDING_REVIEW","candidate_no_layout_at_cap":True}))
    add("T11_ENUMERATION_PREMISE", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["proof_policy"].update({"layout_enumeration_used":True,"target_layout_count_used":720}))
    add("T12_ROOT_COUNT_ONLY", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["proof_policy"].update({"root_empty_count_used_as_only_reason":True,"required_authority_bridge":"NONE"}))
    add("T13_FACTOR_DOMAIN", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["canonical_factor_catalog"].pop())
    add("T14_AFFINE_WIDTH", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["layout_domain"].update({"affine_offsets_preserved_as_identity_only":False,"affine_offsets_used_in_width_theorem":True}))
    add("T15_AFFINE_UNSAT", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].__setitem__("affine_instance_unsat", "TRUE"))
    add("T16_C047_RESULT", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].__setitem__("c047_result", "UNSAT"))
    add("T17_TERMINATION_RUNTIME", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["strict_boundary"].update({"all_input_termination":"TRUE","polynomial_runtime":"TRUE"}))
    add("T18_GLOBAL_PROMOTION", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"]["strict_boundary"].update({"b5_complete":True,"arbitrary_input_global_engine_theorem":True,"p_vs_np":"CLOSED"}))
    add("T19_B5_2B_NEGATIVE_PREMISE", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].update({"authority_bindings":{**c["proof_payload"]["authority_bindings"],"positive_branch_used_as_negative_proof_premise":True}}))
    add("T20_SUPERSEDED_B5_2B_RECEIPT", empty_candidate, empty_b51, b51r, comp, o7, b52r, lambda c,r,co,oo,b52: c["proof_payload"].update({"authority_bindings":{**c["proof_payload"]["authority_bindings"],"superseded_bad_b5_2b_receipt_used":True}}))

    rejected = 0
    for name, candidate, subject, receipt, caudit, oaudit, p52 in attacks:
        try:
            verify(candidate, spec, subject, receipt, caudit, oaudit, p52)
        except Exception:
            rejected += 1
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--b5-1-artifact", type=Path, required=True)
    p.add_argument("--b5-1-admission", type=Path, required=True)
    p.add_argument("--composition-audit", type=Path, required=True)
    p.add_argument("--o7-audit", type=Path, required=True)
    p.add_argument("--b5-2b-admission", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--tamper-suite", action="store_true")
    p.add_argument("--nonempty-b5-1-artifact", type=Path)
    p.add_argument("--nonempty-candidate", type=Path)
    p.add_argument("--open-b5-1-artifact", type=Path)
    p.add_argument("--open-candidate", type=Path)
    a = p.parse_args()

    spec = load(a.spec); b51 = load(a.b5_1_artifact); b51r = load(a.b5_1_admission)
    comp = load(a.composition_audit); o7 = load(a.o7_audit); b52 = load(a.b5_2b_admission); candidate = load(a.candidate)
    expected = verify(candidate, spec, b51, b51r, comp, o7, b52)
    print("JANUS_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_INDEPENDENT_VERIFIER = PASS")
    print("TERMINAL_BRANCH =", expected["terminal_branch"])
    print("B5_1_SEMANTIC_DIGEST = PASS")
    print("GENERAL_COMPOSITION_AUTHORITY = PASS")
    print("O7_BICONDITIONAL_AUTHORITY = PASS")
    print("EXACT_WHOLE_FACTOR_LAYOUT_DOMAIN = PASS")
    print("LAYOUT_ENUMERATION_USED = FALSE")
    print("ROOT_EMPTY_COUNT_USED_AS_ONLY_REASON = FALSE")
    print("B5_2B_POSITIVE_RECEIPT_ROLE = CORROBORATION_ONLY_NOT_NEGATIVE_PREMISE")
    print("CANDIDATE_NO_LAYOUT_AT_CAP =", str(expected["candidate_no_layout_at_cap"]).upper())
    print("NO_LAYOUT_PROMOTION =", expected["no_layout_promotion"])
    print("AFFINE_INSTANCE_UNSAT = NOT_ESTABLISHED")
    print("C047_RESULT = NOT_ESTABLISHED_PENDING_B5_4")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")

    if a.tamper_suite:
        required = [a.nonempty_b5_1_artifact, a.nonempty_candidate, a.open_b5_1_artifact, a.open_candidate]
        if any(x is None for x in required):
            raise AssertionError("tamper suite requires nonempty and OPEN subjects")
        r, t = tamper_suite(
            candidate, load(a.nonempty_candidate), load(a.open_candidate), spec,
            b51, load(a.nonempty_b5_1_artifact), load(a.open_b5_1_artifact), b51r, comp, o7, b52,
        )
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}")


if __name__ == "__main__":
    main()
