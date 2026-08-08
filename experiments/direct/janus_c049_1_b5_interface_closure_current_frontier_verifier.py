from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

SPEC_SCHEMA = "janus.c049_1.b5.interface_closure_current_frontier_spec.v1"
FRONTIER_SCHEMA = "janus.c049_1.b5.interface_closure_current_frontier.v1"
BASE = "e7663ed9be87ebd37bfa51c01501e74c9d5b2603"
NEXT_GATE = "C049.1_B5_ITERATIVE_COMPRESSION_ORCHESTRATOR"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def payload(doc: dict[str, Any]) -> dict[str, Any]:
    return doc.get("audit_payload", doc)


def schema_of(doc: dict[str, Any]) -> str | None:
    return doc.get("schema") or payload(doc).get("schema")


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def expected_frontier() -> dict[str, Any]:
    return {
        "schema": FRONTIER_SCHEMA,
        "gate": "C049.1_B5_INTERFACE_CLOSURE_CURRENT_FRONTIER",
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "authority_vector": {
            "b5_1_generic_runtime_trace": "ADMITTED_IF_RUNTIME_RETURNS_CLOSED_COMPLETE_TRACE",
            "b5_2a_algorithm2_provenance": "ADMITTED_FOR_VERIFIED_B5_1_CLOSED_SUBJECTS",
            "b5_2b_generic_found_layout": "ADMITTED_FOR_VERIFIED_POSITIVE_SUBJECTS",
            "b5_3_generic_no_layout_at_cap": "ADMITTED_FOR_VERIFIED_B5_1_CLOSED_EMPTY_ROOT_SUBJECTS",
            "b5_4_phase_a_c047_rebound": "ADMITTED_FOR_VERIFIED_COMPATIBLE_POSITIVE_SUBJECTS"
        },
        "interface_closure": {
            "four_frozen_b5_contract_subgates_available": True,
            "b5_2_realized_by_b5_2a_plus_b5_2b": True,
            "conditional_interface_stack_closed": True,
            "open_preservation": "OPEN_NEVER_PROMOTES",
            "b5_3_no_layout_is_c047_unsat_premise": False
        },
        "remaining_iterative_orchestration_obligations": [
            "ROUND_ZERO_OR_BASE_CASE_EXPLICIT_AND_VERIFIED",
            "EACH_PREFIX_ROUND_BOUND_TO_EXACT_INDEXED_WHOLE_FACTOR_OCCURRENCES",
            "PREVIOUS_VERIFIED_WIDTH_K_LAYOUT_PLUS_NEW_REDUCED_FACTOR",
            "CONSTRUCT_OR_VERIFY_3K_BRANCH_DECOMPOSITION",
            "VERIFY_NEW_REDUCED_FACTOR_DIMENSION_LE_2K_OR_LOCAL_NEGATIVE_CERTIFICATE_OR_OPEN",
            "RUN_B5_1_FOR_EACH_REQUIRED_ROUND",
            "RUN_B5_2A_B5_2B_AND_VERIFY_NEXT_LAYOUT_ON_NONEMPTY_ROOT",
            "RUN_B5_3_AND_STOP_LAYOUT_DISCOVERY_ON_EMPTY_ROOT",
            "PRESERVE_EXACT_OPEN_AND_COMPLETED_EVIDENCE_ON_CAPABILITY_REFUSAL",
            "RUN_B5_4_ONLY_ON_FULL_INPUT_POSITIVE_SUBJECT_WITH_CANONICAL_AFFINE_PROFILE",
            "PRESERVE_FACTOR_ID_AND_AFFINE_OFFSET_WITHOUT_GEOMETRIC_DEDUPLICATION",
            "AGGREGATE_GLOBAL_WORK_AND_CERTIFICATE_LEDGER_OVER_ALL_ROUNDS"
        ],
        "next_gate": NEXT_GATE,
        "strict_boundary": {
            "b5_interface_authority_vector_closed": True,
            "b5_iterative_compression_orchestrator": False,
            "all_input_termination": "NOT_ESTABLISHED",
            "polynomial_runtime": "NOT_ESTABLISHED",
            "b5_complete": False,
            "c049_1_complete": False,
            "arbitrary_input_global_engine_theorem": False,
            "p_vs_np": "OPEN"
        }
    }


def verify_authority(
    spec: dict[str, Any],
    contract_spec: dict[str, Any],
    contract_receipt: dict[str, Any],
    b51: dict[str, Any],
    b52a: dict[str, Any],
    b52b: dict[str, Any],
    b53: dict[str, Any],
    b54: dict[str, Any],
) -> None:
    require(spec.get("schema") == SPEC_SCHEMA, "closure spec schema")
    require(spec.get("status") == "SPEC_ONLY_FROZEN_NO_ENGINE_COMPLETION_PROMOTION", "closure spec status")
    require(spec.get("base_evidence_head") == BASE, "closure base authority")
    require(spec.get("automatic_merge") is False, "automatic merge")

    ai = spec["authority_inputs"]
    docs = {
        "b5_contract": contract_receipt,
        "b5_1_runtime": b51,
        "b5_2a_carrier": b52a,
        "b5_2b_printorder": b52b,
        "b5_3_empty_root": b53,
        "b5_4_c047_rebound": b54,
    }
    for key, doc in docs.items():
        p = payload(doc)
        require(int(p.get("admission_review_id", -1)) == int(ai[key]["review_id"]), key + " review binding")
        if "exact_proof_head" in p:
            require(p["exact_proof_head"] == ai[key]["proof_head"], key + " proof head")

    require(schema_of(contract_receipt) == "janus.c049_1.b5.general_runtime_terminal_contract_admission_receipt.v1", "contract receipt schema")
    require(schema_of(b51) == "janus.c049_1.b5_1.generic_corrected_runtime_trace_executor_admission_receipt.v1", "B5.1 receipt schema")
    require(schema_of(b52a) == "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier_admission_receipt.v1_1", "B5.2A receipt schema")
    require(schema_of(b52b) == "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_admission_receipt.v1", "B5.2B receipt schema")
    require(schema_of(b53) == "janus.c049_1.b5_3.generic_empty_root_terminal_composition_admission_receipt.v1_1", "B5.3 receipt schema")
    require(payload(b54).get("audit_mode") == "REVIEWER_BOUND_B5_4_NONTRIVIAL_REBOUND_ADMISSION_V1_3", "B5.4 admission mode")
    require(b54.get("semantic_digest") == ai["b5_4_c047_rebound"]["receipt_semantic_digest"], "B5.4 receipt semantic digest")

    pc = payload(contract_receipt)
    require(pc["contract_conclusion"]["b5_complete"] is False, "contract B5 complete promotion")
    require(pc["contract_conclusion"]["p_vs_np"] == "OPEN", "contract P vs NP")

    p51 = payload(b51)
    s51 = p51["semantic_conclusion"]
    require(s51["b5_1_generic_corrected_runtime_trace_executor"] == "ADMITTED_FOR_CLOSED_COMPLETE_TRACE_CONDITIONAL_SCOPE", "B5.1 conditional scope")
    require(s51["all_input_termination"] == "NOT_ESTABLISHED", "B5.1 totality promotion")
    require(s51["polynomial_runtime"] == "NOT_ESTABLISHED", "B5.1 polynomial promotion")
    require(s51["b5_complete"] is False, "B5.1 B5 complete promotion")

    p52a = payload(b52a)
    s52a = p52a["semantic_conclusion"]
    require(s52a["b5_2a_generic_algorithm2_provenance_carrier"] == "ADMITTED_FOR_VERIFIED_B5_1_CLOSED_SUBJECTS", "B5.2A scope")
    require(s52a["factor_order_emitted"] is False, "B5.2A factor order promotion")
    require(s52a["all_input_termination"] == "NOT_ESTABLISHED", "B5.2A totality")
    require(s52a["polynomial_runtime"] == "NOT_ESTABLISHED", "B5.2A polynomial")
    require(s52a["b5_complete"] is False, "B5.2A B5 complete")

    p52b = payload(b52b)
    s52b = p52b["semantic_conclusion"]
    require(s52b["b5_2b_generic_algorithm2_printorder_reconstruction"] == "ADMITTED_FOR_VERIFIED_B5_2A_NONEMPTY_ROOT_SUBJECTS", "B5.2B scope")
    require(s52b["generic_found_layout"] == "TRUE_WHEN_B5_1_CLOSED_ROOT_NONEMPTY_AND_B5_2A_B5_2B_VERIFY", "B5.2B condition")
    require(s52b["all_input_termination"] == "NOT_ESTABLISHED", "B5.2B totality")
    require(s52b["polynomial_runtime"] == "NOT_ESTABLISHED", "B5.2B polynomial")
    require(s52b["b5_complete"] is False, "B5.2B B5 complete")

    p53 = payload(b53)
    require(p53["admitted_statement"]["b5_3_generic_empty_root_terminal_composition"] == "ADMITTED_FOR_VERIFIED_B5_1_CLOSED_EMPTY_ROOT_SUBJECTS", "B5.3 scope")
    require(p53["strict_boundary"]["all_input_termination"] == "NOT_ESTABLISHED", "B5.3 totality")
    require(p53["strict_boundary"]["polynomial_runtime"] == "NOT_ESTABLISHED", "B5.3 polynomial")
    require(p53["strict_boundary"]["b5_complete"] is False, "B5.3 B5 complete")

    p54 = payload(b54)
    require(p54["admitted_statement"]["b5_4_corrected_discovery_to_phase_a_c047_rebound"].startswith("ADMITTED_FOR_VERIFIED_B5_1_CLOSED_NONEMPTY_B5_2B_SUBJECTS"), "B5.4 conditional scope")
    require(p54["verification"]["b5_3_used_as_c047_unsat_premise"] is False, "B5.3 -> C047 UNSAT")
    require(p54["verification"]["historical_phase_a_verifier_return_required_true"] == "PASS", "B5.4 historical verifier")
    require(p54["strict_boundary"]["all_input_termination"] == "NOT_ESTABLISHED", "B5.4 totality")
    require(p54["strict_boundary"]["polynomial_runtime"] == "NOT_ESTABLISHED", "B5.4 polynomial")
    require(p54["strict_boundary"]["b5_complete"] is False, "B5.4 B5 complete")
    require(p54["strict_boundary"]["p_vs_np"] == "OPEN", "B5.4 P vs NP")

    require(contract_spec.get("schema") == "janus.c049_1.b5.general_runtime_terminal_integration_spec.v1", "contract spec schema")
    ic = contract_spec["iterative_compression_contract"]
    for field in (
        "round_zero_or_base_case",
        "round_step",
        "scaffold_obligation",
        "new_reduced_factor_dimension_obligation",
        "round_full_set_obligation",
        "round_transition",
        "round_failure",
    ):
        require(bool(ic.get(field)), "missing iterative-compression contract field: " + field)
    require(contract_spec["resource_and_refusal_contract"]["open_never_implies"] == ["FOUND_LAYOUT", "NO_LAYOUT_AT_CAP", "B5_COMPLETE"], "OPEN refusal contract")
    require(contract_spec["c047_handoff_contract"]["bare_no_layout_transcript_to_phase_a"] == "FORBIDDEN", "bare NO_LAYOUT handoff")

    orchestration = spec["remaining_iterative_orchestration_obligations"]
    required_keys = {
        "round_zero_or_base_case", "round_subject", "round_step", "scaffold",
        "new_reduced_factor_dimension", "runtime", "positive_round_transition",
        "negative_round_transition", "open_round_transition", "final_positive_affine_handoff",
        "factor_identity", "accounting"
    }
    require(set(orchestration) == required_keys, "orchestration obligation coverage")
    require("EACH_PREFIX" in orchestration["round_subject"], "prefix schedule")
    require("3K" in orchestration["scaffold"], "3k scaffold")
    require("2K" in orchestration["new_reduced_factor_dimension"], "2k reduced factor")
    require("B5_1" in orchestration["runtime"], "B5.1 round runtime")
    require("B5_2A_B5_2B" in orchestration["positive_round_transition"], "positive round transition")
    require("B5_3" in orchestration["negative_round_transition"], "negative round transition")
    require("EXACT_OPEN_STATUS" in orchestration["open_round_transition"], "OPEN round transition")
    require("FULL_INPUT" in orchestration["final_positive_affine_handoff"], "full-input C047 handoff")
    require("NO_GEOMETRIC_DEDUPLICATION" in orchestration["factor_identity"], "factor occurrence identity")
    require("FAILED_REFINEMENTS" in orchestration["accounting"], "global accounting")

    nxt = spec["next_implementation_gate"]
    require(nxt["id"] == NEXT_GATE, "next gate")
    require(nxt["status"] == "AUTHORIZED_AFTER_THIS_INTERFACE_CLOSURE_CONTRACT_IS_SEPARATELY_ADMITTED", "next gate admission ceiling")
    require(len(nxt["required_output_classes"]) == 3, "next gate outputs")

    boundary = spec["strict_boundary"]
    require(boundary["b5_interface_authority_vector_closed"] == "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW", "premature interface admission")
    require(boundary["b5_local_conditional_subinterfaces"] == "4_OF_4_LOGICALLY_AVAILABLE_IN_THEIR_ADMITTED_SCOPES", "subinterface count")
    require(boundary["b5_iterative_compression_orchestrator"] is False, "premature orchestrator")
    require(boundary["all_input_termination"] == "NOT_ESTABLISHED", "premature totality")
    require(boundary["polynomial_runtime"] == "NOT_ESTABLISHED", "premature polynomial")
    require(boundary["b5_complete"] is False, "premature B5 complete")
    require(boundary["c049_1_complete"] is False, "premature C049.1 complete")
    require(boundary["arbitrary_input_global_engine_theorem"] is False, "premature global engine")
    require(boundary["p_vs_np"] == "OPEN", "P vs NP promotion")


def verify_frontier(frontier: dict[str, Any]) -> None:
    require(frontier == expected_frontier(), "frontier differs from independently derived authority state")


def tamper_suite(frontier: dict[str, Any]) -> tuple[int, int]:
    attacks: list[tuple[str, Callable[[dict[str, Any]], None]]] = []

    def add(name: str, fn: Callable[[dict[str, Any]], None]) -> None:
        attacks.append((name, fn))

    add("T01_B51_UNCONDITIONAL", lambda x: x["authority_vector"].__setitem__("b5_1_generic_runtime_trace", "ADMITTED_FOR_ALL_INPUTS"))
    add("T02_B52_UNCONDITIONAL", lambda x: x["authority_vector"].__setitem__("b5_2b_generic_found_layout", "UNCONDITIONAL_FOUND_LAYOUT"))
    add("T03_B53_UNCONDITIONAL", lambda x: x["authority_vector"].__setitem__("b5_3_generic_no_layout_at_cap", "UNCONDITIONAL_NO_LAYOUT"))
    add("T04_B54_UNCONDITIONAL", lambda x: x["authority_vector"].__setitem__("b5_4_phase_a_c047_rebound", "UNCONDITIONAL_SAT_UNSAT"))
    add("T05_B5_COMPLETE", lambda x: x["strict_boundary"].__setitem__("b5_complete", True))
    add("T06_TOTALITY", lambda x: x["strict_boundary"].__setitem__("all_input_termination", "ESTABLISHED"))
    add("T07_POLYNOMIAL", lambda x: x["strict_boundary"].__setitem__("polynomial_runtime", "ESTABLISHED"))
    add("T08_GLOBAL_ENGINE", lambda x: x["strict_boundary"].__setitem__("arbitrary_input_global_engine_theorem", True))
    add("T09_P_VS_NP", lambda x: x["strict_boundary"].__setitem__("p_vs_np", "CLOSED"))
    add("T10_ORCHESTRATOR", lambda x: x["strict_boundary"].__setitem__("b5_iterative_compression_orchestrator", True))
    add("T11_OPEN_PROMOTION", lambda x: x["interface_closure"].__setitem__("open_preservation", "OPEN_MAY_PROMOTE"))
    add("T12_B53_TO_C047_UNSAT", lambda x: x["interface_closure"].__setitem__("b5_3_no_layout_is_c047_unsat_premise", True))
    add("T13_DROP_SCAFFOLD", lambda x: x["remaining_iterative_orchestration_obligations"].remove("CONSTRUCT_OR_VERIFY_3K_BRANCH_DECOMPOSITION"))
    add("T14_DROP_2K", lambda x: x["remaining_iterative_orchestration_obligations"].remove("VERIFY_NEW_REDUCED_FACTOR_DIMENSION_LE_2K_OR_LOCAL_NEGATIVE_CERTIFICATE_OR_OPEN"))
    add("T15_DROP_POSITIVE_REPLAY", lambda x: x["remaining_iterative_orchestration_obligations"].remove("RUN_B5_2A_B5_2B_AND_VERIFY_NEXT_LAYOUT_ON_NONEMPTY_ROOT"))
    add("T16_DROP_NEGATIVE_AUTHORITY", lambda x: x["remaining_iterative_orchestration_obligations"].remove("RUN_B5_3_AND_STOP_LAYOUT_DISCOVERY_ON_EMPTY_ROOT"))
    add("T17_DROP_OPEN_STOP", lambda x: x["remaining_iterative_orchestration_obligations"].remove("PRESERVE_EXACT_OPEN_AND_COMPLETED_EVIDENCE_ON_CAPABILITY_REFUSAL"))
    add("T18_DROP_FACTOR_IDENTITY", lambda x: x["remaining_iterative_orchestration_obligations"].remove("PRESERVE_FACTOR_ID_AND_AFFINE_OFFSET_WITHOUT_GEOMETRIC_DEDUPLICATION"))
    add("T19_DROP_LEDGER", lambda x: x["remaining_iterative_orchestration_obligations"].remove("AGGREGATE_GLOBAL_WORK_AND_CERTIFICATE_LEDGER_OVER_ALL_ROUNDS"))
    add("T20_BAD_NEXT_GATE", lambda x: x.__setitem__("next_gate", "P_VS_NP_CLOSED"))

    rejected = 0
    for name, mutate in attacks:
        attacked = copy.deepcopy(frontier)
        mutate(attacked)
        try:
            verify_frontier(attacked)
        except Exception:
            rejected += 1
            print(name + " = REJECTED")
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--contract-spec", type=Path, required=True)
    ap.add_argument("--frontier", type=Path, required=True)
    ap.add_argument("--b5-contract", type=Path, required=True)
    ap.add_argument("--b5-1", type=Path, required=True)
    ap.add_argument("--b5-2a", type=Path, required=True)
    ap.add_argument("--b5-2b", type=Path, required=True)
    ap.add_argument("--b5-3", type=Path, required=True)
    ap.add_argument("--b5-4", type=Path, required=True)
    ap.add_argument("--tamper-suite", action="store_true")
    args = ap.parse_args()

    spec = load(args.spec)
    frontier = load(args.frontier)
    verify_authority(
        spec,
        load(args.contract_spec),
        load(args.b5_contract),
        load(args.b5_1),
        load(args.b5_2a),
        load(args.b5_2b),
        load(args.b5_3),
        load(args.b5_4),
    )
    verify_frontier(frontier)

    print("JANUS_B5_INTERFACE_CLOSURE_CURRENT_FRONTIER_INDEPENDENT_VERIFIER = PASS")
    print("AUTHORITY_RECEIPTS_REPLAYED = 6/6")
    print("B5_FROZEN_CONTRACT_SUBGATES = 4/4 CONDITIONAL_INTERFACE_AUTHORITY_AVAILABLE")
    print("B5_2_INTERNAL_CHAIN = B5_2A_PLUS_B5_2B_REVIEWER_BOUND")
    print("B5_CONDITIONAL_INTERFACE_STACK_CLOSED = TRUE")
    print("B5_ITERATIVE_COMPRESSION_ORCHESTRATOR = NOT_ESTABLISHED")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("NEXT_GATE = " + NEXT_GATE)
    print("P_VS_NP = OPEN")
    if args.tamper_suite:
        rejected, total = tamper_suite(frontier)
        print(f"ANTI_PROMOTION_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
