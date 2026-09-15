from __future__ import annotations

import json

from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter_v1_1 as cc_v11
from research.tools.apma_bucket_conditioned_factorized_payload import conditioned_factorized_payload_v1_1 as v11
from research.tools.apma_bucket_conditioned_factorized_payload import independent_checker as v1check

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-CONDITIONED-FACTORIZED-PAYLOAD-V1-1-INDEPENDENT-CHECK-2026-09-15"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_1"


def run() -> dict:
    old = v1check.run()
    old_false = sorted(k for k, value in old["checks"].items() if not value)

    raw = v11.corrected_incomplete_target_coverage_control()
    predecessor = cc_v11.explain(raw)
    ready = cc_v11.first_failed_original_bucket_v11(raw)
    candidate = v11.explain(raw)
    independent = v1check.independent_solve(raw)

    pred_receipt = predecessor.get("carrier", {}).get("receipt", {})
    checks = {
        "R1_v11_source_guard": v11.source_guard()["ok"] is True,
        "R2_v1_first_failure_reproduced_exactly": old.get("verdict") == "FAIL_OR_OPEN_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1" and old_false == ["G10_candidate_incomplete_open", "G10_independent_incomplete_open"],
        "R3_all_non_G10_v1_checks_green": all(value for key, value in old["checks"].items() if not key.startswith("G10_")),
        "R4_corrected_predecessor_still_sticky_open": predecessor.get("status") == "OPEN_COMMON_CORE_FILTERED_BUCKET_STILL_OVER_L2",
        "R5_corrected_predecessor_failed_variable_20": ready.get("status") == "READY" and ready.get("failed_variable") == 20,
        "R6_corrected_predecessor_zero_failed_bucket_enumeration": pred_receipt.get("handoff_failed_bucket_enumerations") == 0,
        "R7_candidate_corrected_incomplete_open": candidate.get("status") == "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE",
        "R8_independent_corrected_incomplete_open": independent.get("status") == "OPEN_INCOMPLETE_TARGET_COMPONENT_COVERAGE",
        "R9_v1_candidate_unchanged_positive_pass": old["controls"].get("positive_candidate") == "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "R10_v1_independent_unchanged_positive_pass": old["controls"].get("positive_independent") == "ADMIT_EXACT_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_PORTFOLIO",
        "R11_v1_cross_control_still_open": old["controls"].get("cross_candidate") == "OPEN_RESIDUAL_CROSS_COUPLING" and old["controls"].get("cross_independent") == "OPEN_RESIDUAL_CROSS_COUPLING",
        "R12_v1_multiple_core_still_open": old["controls"].get("multiple_candidate") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT" and old["controls"].get("multiple_independent") == "OPEN_NONUNIQUE_COMMON_CORE_SUPPORT",
        "R13_hint_and_tamper_still_reject": old["controls"].get("hint") == "REJECT_RAW_INPUT" and old["controls"].get("tamper") == "REJECT_TAMPERED_PROVENANCE",
        "R14_zero_cartesian_preserved": old.get("independent_method", {}).get("cartesian_products_materialized") == 0,
        "FW_p_vs_np": v11.firewall()["P_VS_NP"] == "OPEN",
        "FW_general_sat": v11.firewall()["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "FW_general_factorization": v11.firewall()["GENERAL_CONDITIONED_FACTORIZATION"] == "NOT_PROVED",
    }
    verdict = VERDICT if all(checks.values()) else "FAIL_OR_OPEN_UNIQUE_CORE_CONDITIONED_FACTORIZED_PAYLOAD_V1_1"
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": "INDEPENDENT_CHECKER__CONTROL_REPAIR_ONLY__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "v1_false_checks": old_false,
            "positive_candidate": old["controls"].get("positive_candidate"),
            "positive_independent": old["controls"].get("positive_independent"),
            "positive_predecessor_filtered_product": old["controls"].get("positive_predecessor_filtered_product"),
            "positive_portfolio_records": old["controls"].get("positive_portfolio_records"),
            "positive_boundary_rows": old["controls"].get("positive_boundary_rows"),
            "corrected_predecessor": predecessor.get("status"),
            "corrected_failed_variable": ready.get("failed_variable"),
            "corrected_failed_bucket_enumerations": pred_receipt.get("handoff_failed_bucket_enumerations"),
            "corrected_candidate": candidate.get("status"),
            "corrected_independent": independent.get("status"),
            "cross_candidate": old["controls"].get("cross_candidate"),
            "multiple_candidate": old["controls"].get("multiple_candidate"),
            "hint": old["controls"].get("hint"),
            "tamper": old["controls"].get("tamper"),
        },
        "repair_class": "INCOMPLETE_TARGET_COMPONENT_COVERAGE_NEGATIVE_CONTROL_DESIGN_ONLY",
        "v1_candidate_mathematics_changed": False,
        "scientific_firewall": v11.firewall(),
        "verdict": verdict,
    }


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
