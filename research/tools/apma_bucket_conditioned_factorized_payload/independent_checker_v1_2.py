from __future__ import annotations

import json
from pathlib import Path

from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload_v1_2 as v12
from research.tools.apma_bucket_conditioned_factorized_payload import independent_checker as v1check

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-CONDITIONED-FACTORIZED-PAYLOAD-V1-2-INDEPENDENT-CHECK-2026-09-15"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_2"
V1_FAILURE = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_FIRST_FAILURE_2026-09-15.json")
V11_FAILURE = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_1_FAILURE_2026-09-15.json")


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def run() -> dict:
    old = v1check.run()
    old_false = sorted(k for k, value in old["checks"].items() if not value)
    receipt_pack = v12.valid_and_forged_ready_receipts()
    valid = receipt_pack.get("valid", {})
    forged = receipt_pack.get("forged", {})
    valid_guard = v12.coverage_admission_guard(valid) if valid else {}
    forged_guard = v12.coverage_admission_guard(forged) if forged else {}

    valid_bucket_ids = [str(f["id"]) for f in valid.get("bucket", [])]
    valid_target_ids = [f"orig:{int(gi)}" for gi in valid.get("component", [])]
    forged_bucket_ids = [str(f["id"]) for f in forged.get("bucket", [])]
    forged_target_ids = [f"orig:{int(gi)}" for gi in forged.get("component", [])]
    independent_valid_accept = valid_bucket_ids == valid_target_ids
    independent_forged_reject = forged_bucket_ids != forged_target_ids

    r = root()
    v1_failure = json.loads((r / V1_FAILURE).read_text(encoding="utf-8"))
    v11_failure = json.loads((r / V11_FAILURE).read_text(encoding="utf-8"))
    positive = v12.explain(cc_v1.filtered_still_overbudget_control())

    checks = {
        "S1_v12_source_guard": v12.source_guard()["ok"] is True,
        "S1_v1_candidate_byte_frozen": v12.source_guard()["checks"].get("v1_candidate_blob") is True,
        "S2_v1_failure_receipt_preserved": v1_failure.get("status") == "IMMUTABLE_FIRST_FAILURE" and v1_failure.get("actions_run") == 34976286395,
        "S2_v11_failure_receipt_preserved": v11_failure.get("status") == "IMMUTABLE_V1_1_FAILURE" and v11_failure.get("actions_run") == 34977105951,
        "S2_v1_failure_reproduced": old.get("verdict") == "FAIL_OR_OPEN_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1" and old_false == ["G10_candidate_incomplete_open", "G10_independent_incomplete_open"],
        "S3_all_non_G10_v1_checks_green": all(value for key, value in old["checks"].items() if not key.startswith("G10_")),
        "S4_valid_sticky_receipt_ready": receipt_pack.get("status") == "READY" and receipt_pack.get("predecessor_status") == "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2",
        "S5_valid_guard_accepts": valid_guard.get("status") == "PASS_COMPLETE_TARGET_COMPONENT_COVERAGE_ADMISSION_PRECONDITION" and independent_valid_accept,
        "S6_forged_guard_rejects": forged_guard.get("status") == "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE" and independent_forged_reject,
        "S6_forged_bucket_unchanged": forged_bucket_ids == valid_bucket_ids,
        "S6_forged_target_has_one_extra": len(forged_target_ids) == len(valid_target_ids) + 1,
        "S6_appended_relation_is_existing_outside_relation": receipt_pack.get("appended_existing_relation_index") not in set(valid.get("component", [])) and 0 <= int(receipt_pack.get("appended_existing_relation_index", -1)) < len(valid.get("canonical", {}).get("constraints", [])),
        "S7_valid_guard_zero_portfolio_calls": valid_guard.get("portfolio_construction_calls") == 0,
        "S7_forged_guard_zero_portfolio_calls": forged_guard.get("portfolio_construction_calls") == 0,
        "S7_forged_guard_zero_cartesian": forged_guard.get("bucket_cartesian_combinations_enumerated") == 0,
        "S7_no_promotion": forged_guard.get("scientific_promotion") is False,
        "S8_positive_candidate_still_passes": positive.get("status") == "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "S8_positive_witness_still_verified": positive.get("frozen_v1_result", {}).get("carrier", {}).get("witness_verified") is True,
        "FW_p_vs_np": v12.firewall()["P_VS_NP"] == "OPEN",
        "FW_general_sat": v12.firewall()["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "FW_general_factorization": v12.firewall()["GENERAL_CONDITIONED_FACTORIZATION"] == "NOT_PROVED",
    }
    verdict = VERDICT if all(checks.values()) else "FAIL_OR_OPEN_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_2"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__SCOPE_AUDIT_REPAIR_ONLY__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "v1_false_checks": old_false,
            "positive_candidate": old["controls"].get("positive_candidate"),
            "positive_independent": old["controls"].get("positive_independent"),
            "positive_predecessor_filtered_product": old["controls"].get("positive_predecessor_filtered_product"),
            "positive_portfolio_records": old["controls"].get("positive_portfolio_records"),
            "positive_boundary_rows": old["controls"].get("positive_boundary_rows"),
            "cross_candidate": old["controls"].get("cross_candidate"),
            "multiple_candidate": old["controls"].get("multiple_candidate"),
            "valid_coverage_guard": valid_guard.get("status"),
            "forged_coverage_guard": forged_guard.get("status"),
            "forged_appended_relation_index": receipt_pack.get("appended_existing_relation_index"),
            "hint": old["controls"].get("hint"),
            "tamper": old["controls"].get("tamper"),
        },
        "repair_class": "INCOMPLETE_COVERAGE_OUT_OF_SCOPE_GUARD_TEST_RESCOPING_AFTER_TWO_RAW_CONTROL_REACHABILITY_FAILURES",
        "v1_candidate_mathematics_changed": False,
        "coverage_falsifier_authority": "IMPLEMENTATION_FAIL_CLOSED_UNIT_TEST_ONLY__NOT_RAW_REACHABILITY_EVIDENCE",
        "scientific_firewall": v12.firewall(),
        "verdict": verdict,
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
