from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

SCHEMA = "janus.c049_1.b5.interface_closure_current_frontier_spec.v1"
STATUS = "SPEC_ONLY_FROZEN_NO_ENGINE_COMPLETION_PROMOTION"
BASE = "e7663ed9be87ebd37bfa51c01501e74c9d5b2603"
NEXT_GATE = "C049.1_B5_ITERATIVE_COMPRESSION_ORCHESTRATOR"

EXPECTED_AUTHORITY = {
    "b5_contract": (4888231726, "6103a509bca3e91b1950a58e90e8274b3cc5e4c7"),
    "b5_1_runtime": (4888268512, "f70d56c84874827fd03cc482e37fd9449a7a8a23"),
    "b5_2a_carrier": (4888326386, "2e076e87029b2bc1ae8e773a6ed16f3897d46b78"),
    "b5_2b_printorder": (4888359197, "5e60eff4a4bd4c87cbf527cd446fc6b23b013774"),
    "b5_3_empty_root": (4888388997, "32177caad196ca4640c090212c41bc132448cc7c"),
    "b5_4_c047_rebound": (4888463198, "93749562d05a7f2af7276aaa77de7c0beb65293c"),
}

EXPECTED_PROOF_HEADS = {
    "b5_contract": "cebbcff9bdbc405834d6e51e0bf5246534e66af5",
    "b5_1_runtime": "dda63620f3053e22469928b9533548c96a0d969d",
    "b5_2a_carrier": "15ea163d918f21be0b7d8479263c1faa3f335614",
    "b5_2b_printorder": "f057b7afe5642dd92ee08d7beb3d534721a13711",
    "b5_3_empty_root": "e98415223c011f69d40d0dc0fbf04aa70215494d",
    "b5_4_c047_rebound": "135740e9ee06030ad0d029cc65cbace95af82cc1",
}

REQUIRED_ORCHESTRATION = {
    "round_zero_or_base_case",
    "round_subject",
    "round_step",
    "scaffold",
    "new_reduced_factor_dimension",
    "runtime",
    "positive_round_transition",
    "negative_round_transition",
    "open_round_transition",
    "final_positive_affine_handoff",
    "factor_identity",
    "accounting",
}

REQUIRED_ANTI_PROMOTION = {
    "NO_B5_COMPLETE_FROM_FOUR_CONDITIONAL_SUBINTERFACES",
    "NO_ALL_INPUT_TERMINATION_FROM_CLOSED_TRACE_SOUNDNESS",
    "NO_POLYNOMIAL_RUNTIME_FROM_FINITE_GREEN_CONTROLS",
    "NO_CONTINUE_AFTER_OPEN_WITHOUT_A_NEW_EXPLICIT_CAPABILITY_REQUEST",
    "NO_STALE_PREFIX_LAYOUT_AS_NEXT_ROUND_WITNESS",
    "NO_FACTOR_OMISSION_DUPLICATION_OR_GEOMETRIC_DEDUPLICATION",
    "NO_AFFINE_OFFSET_LOSS_BETWEEN_ROUNDS",
    "NO_UNVERIFIED_3K_SCAFFOLD",
    "NO_UNVERIFIED_2K_REDUCED_FACTOR_DIMENSION",
    "NO_MISSING_LOCAL_NEGATIVE_CERTIFICATE_PROMOTED_TO_NO_LAYOUT",
    "NO_B5_1_OPEN_PROMOTED_TO_POSITIVE_OR_NEGATIVE_TERMINAL",
    "NO_SKIP_B5_2_REPLAY_ON_POSITIVE_ROUND",
    "NO_SKIP_B5_3_AUTHORITY_ON_EMPTY_ROOT",
    "NO_B5_3_NO_LAYOUT_PROMOTED_TO_C047_UNSAT",
    "NO_SKIP_HISTORICAL_PHASE_A_VERIFIER_ON_B5_4",
    "NO_STRICT_PREFIX_C047_RESULT_PROMOTED_TO_FINAL_FULL_INPUT_RESULT",
    "NO_HIDDEN_FINAL_LAYOUT_OR_SAT_ORACLE",
    "NO_FIXED_FACTOR_COUNT_DIMENSION_K_NODE_ID_OR_HISTORICAL_FIXTURE_AS_ACCEPTANCE_ORACLE",
    "NO_OMITTED_WORK_OR_CERTIFICATE_VOLUME_FROM_GLOBAL_LEDGER",
    "NO_ARBITRARY_INPUT_GLOBAL_ENGINE_OR_P_VS_NP_PROMOTION",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def semantic_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def verify(spec: dict[str, Any]) -> dict[str, Any]:
    assert spec.get("schema") == SCHEMA
    assert spec.get("status") == STATUS
    assert spec.get("base_evidence_head") == BASE
    assert spec.get("automatic_merge") is False

    authority = spec["authority_inputs"]
    for key, (review_id, receipt_blob) in EXPECTED_AUTHORITY.items():
        rec = authority[key]
        assert rec["proof_head"] == EXPECTED_PROOF_HEADS[key]
        assert int(rec["review_id"]) == review_id
        assert rec["receipt_git_blob"] == receipt_blob
    assert authority["b5_contract"]["spec_git_blob"] == "b192f5e3f884551c29d574f568a8b2275ecc92c5"
    assert authority["b5_4_c047_rebound"]["receipt_semantic_digest"] == "14da3e48d8e2adb553414c8ff36b067de043df8f7c813128929beaaf52416ce2"
    assert authority["historical_phase_b_plan"]["subject"] == "8cf39d35fc0fd03191b5ab28905637a5c842b2cf"
    assert authority["historical_phase_b_plan"]["git_blob"] == "a776887c258da5c92414fa3d548beeec6ebcee83"
    assert authority["b4_2_scaffold"]["subject"] == "9bfdef654842fb453f7dd63d34ee23de93266db6"
    assert authority["b4_2_scaffold"]["git_blob"] == "57c16c18a14cecb96264a22fea01cd2c2bdaa857"

    closure = spec["interface_closure"]
    assert set(closure) == {
        "b5_1",
        "b5_2_positive",
        "b5_3_negative",
        "b5_4_affine",
        "open_preservation",
        "negative_affine_separation",
    }
    assert "CLOSED_COMPLETE_TRACE" in closure["b5_1"]
    assert "CLOSED_NONEMPTY" in closure["b5_2_positive"]
    assert "CLOSED_EMPTY_ROOT" in closure["b5_3_negative"]
    assert "SAT_UNSAT_OR_OPEN" in closure["b5_4_affine"]
    assert "REMAINS_OPEN" in closure["open_preservation"]
    assert "NOT_AN_AFFINE_UNSAT_PREMISE" in closure["negative_affine_separation"]

    findings = spec["non_composition_findings"]
    assert findings == {
        "conditional_interfaces_do_not_imply_total_engine": True,
        "closed_trace_soundness_does_not_imply_all_input_termination": True,
        "local_terminal_soundness_does_not_supply_round_scheduler": True,
        "c047_rebound_on_positive_subjects_does_not_supply_iterative_compression": True,
        "green_finite_controls_do_not_prove_polynomial_runtime": True,
    }

    obligations = spec["remaining_iterative_orchestration_obligations"]
    assert set(obligations) == REQUIRED_ORCHESTRATION
    assert "EACH_PREFIX" in obligations["round_subject"]
    assert "3K" in obligations["scaffold"]
    assert "2K" in obligations["new_reduced_factor_dimension"]
    assert "B5_1" in obligations["runtime"]
    assert "B5_2A_B5_2B" in obligations["positive_round_transition"]
    assert "B5_3" in obligations["negative_round_transition"]
    assert "EXACT_OPEN_STATUS" in obligations["open_round_transition"]
    assert "FULL_INPUT" in obligations["final_positive_affine_handoff"]
    assert "NO_GEOMETRIC_DEDUPLICATION" in obligations["factor_identity"]
    assert "FAILED_REFINEMENTS" in obligations["accounting"]

    nxt = spec["next_implementation_gate"]
    assert nxt["id"] == NEXT_GATE
    assert nxt["status"] == "AUTHORIZED_AFTER_THIS_INTERFACE_CLOSURE_CONTRACT_IS_SEPARATELY_ADMITTED"
    assert len(nxt["required_output_classes"]) == 3

    anti = spec["anti_promotion_requirements"]
    assert len(anti) == 20
    assert set(anti) == REQUIRED_ANTI_PROMOTION

    boundary = spec["strict_boundary"]
    assert boundary["b5_interface_authority_vector_closed"] == "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW"
    assert boundary["b5_local_conditional_subinterfaces"] == "4_OF_4_LOGICALLY_AVAILABLE_IN_THEIR_ADMITTED_SCOPES"
    assert boundary["b5_iterative_compression_orchestrator"] is False
    assert boundary["all_input_termination"] == "NOT_ESTABLISHED"
    assert boundary["polynomial_runtime"] == "NOT_ESTABLISHED"
    assert boundary["b5_complete"] is False
    assert boundary["c049_1_complete"] is False
    assert boundary["arbitrary_input_global_engine_theorem"] is False
    assert boundary["p_vs_np"] == "OPEN"

    return {
        "schema": "janus.c049_1.b5.interface_closure_current_frontier_verification.v1",
        "gate": spec["gate"],
        "spec_semantic_digest": semantic_digest(spec),
        "authority_receipts_bound": len(EXPECTED_AUTHORITY),
        "conditional_interface_groups": 4,
        "iterative_orchestration_obligations": len(REQUIRED_ORCHESTRATION),
        "anti_promotion_requirements": len(REQUIRED_ANTI_PROMOTION),
        "next_implementation_gate": NEXT_GATE,
        "b5_complete": False,
        "all_input_termination": "NOT_ESTABLISHED",
        "polynomial_runtime": "NOT_ESTABLISHED",
        "p_vs_np": "OPEN",
    }


def tamper_suite(spec: dict[str, Any]) -> tuple[int, int]:
    attacks: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("T01_B5_COMPLETE", lambda x: x["strict_boundary"].__setitem__("b5_complete", True)),
        ("T02_ALL_INPUT_TERMINATION", lambda x: x["strict_boundary"].__setitem__("all_input_termination", "ESTABLISHED")),
        ("T03_POLYNOMIAL_RUNTIME", lambda x: x["strict_boundary"].__setitem__("polynomial_runtime", "ESTABLISHED")),
        ("T04_P_VS_NP", lambda x: x["strict_boundary"].__setitem__("p_vs_np", "CLOSED")),
        ("T05_B5_1_REVIEW", lambda x: x["authority_inputs"]["b5_1_runtime"].__setitem__("review_id", 1)),
        ("T06_B5_4_RECEIPT", lambda x: x["authority_inputs"]["b5_4_c047_rebound"].__setitem__("receipt_git_blob", "0" * 40)),
        ("T07_DROP_BASE_CASE", lambda x: x["remaining_iterative_orchestration_obligations"].pop("round_zero_or_base_case")),
        ("T08_DROP_PREFIX_SUBJECT", lambda x: x["remaining_iterative_orchestration_obligations"].pop("round_subject")),
        ("T09_DROP_3K", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("scaffold", "UNVERIFIED")),
        ("T10_DROP_2K", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("new_reduced_factor_dimension", "UNVERIFIED")),
        ("T11_CONTINUE_AFTER_OPEN", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("open_round_transition", "CONTINUE")),
        ("T12_STALE_POSITIVE_ROUND", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("positive_round_transition", "REUSE_STALE_LAYOUT")),
        ("T13_SKIP_B5_3", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("negative_round_transition", "ROOT_EMPTY_IMPLIES_NO_LAYOUT")),
        ("T14_PREFIX_C047_FINAL", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("final_positive_affine_handoff", "ALLOW_STRICT_PREFIX_AS_FINAL")),
        ("T15_GEOMETRIC_DEDUP", lambda x: x["remaining_iterative_orchestration_obligations"].__setitem__("factor_identity", "DEDUP_EQUAL_SPACES")),
        ("T16_DROP_ACCOUNTING", lambda x: x["remaining_iterative_orchestration_obligations"].pop("accounting")),
        ("T17_B5_3_TO_C047_UNSAT", lambda x: x["interface_closure"].__setitem__("negative_affine_separation", "B5_3_NO_LAYOUT_IS_C047_UNSAT")),
        ("T18_OPEN_PROMOTION", lambda x: x["interface_closure"].__setitem__("open_preservation", "OPEN_MAY_PROMOTE")),
        ("T19_NEXT_GATE_PRE_ADMITTED", lambda x: x["next_implementation_gate"].__setitem__("status", "ADMITTED")),
        ("T20_AUTO_MERGE", lambda x: x.__setitem__("automatic_merge", True)),
    ]
    rejected = 0
    for name, mutate in attacks:
        attacked = copy.deepcopy(spec)
        mutate(attacked)
        try:
            verify(attacked)
        except Exception:
            rejected += 1
            print(name + " = REJECTED")
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True)
    parser.add_argument("--self-test-tampers", action="store_true")
    args = parser.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    result = verify(spec)
    print("JANUS_B5_INTERFACE_CLOSURE_CURRENT_FRONTIER_INDEPENDENT_VERIFIER = PASS")
    print("AUTHORITY_RECEIPTS_BOUND =", result["authority_receipts_bound"])
    print("CONDITIONAL_INTERFACE_GROUPS =", result["conditional_interface_groups"])
    print("ITERATIVE_ORCHESTRATION_OBLIGATIONS =", result["iterative_orchestration_obligations"])
    print("ANTI_PROMOTION_REQUIREMENTS =", result["anti_promotion_requirements"])
    if args.self_test_tampers:
        rejected, total = tamper_suite(spec)
        print(f"DIGEST_REPAIRED_SEMANTIC_TAMPERS_REJECTED = {rejected}/{total}")
    print("B5_ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
